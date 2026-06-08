from contextlib import asynccontextmanager

import anyio

from fastapi import FastAPI, Path, Body, HTTPException, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy import select

from database import get_session
from llama import llm, SYSTEM_PROMPT
from orm import Item
from schema import ItemCreateRequest, ItemResponse, ItemUpdateRequest


@asynccontextmanager
async def lifespan(app):
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 200  # 스레드 풀의 개수 조정
    yield

app = FastAPI(lifespan=lifespan)

@app.post(
    "/chats",
    summary="Llama 응답 생성 API",
)
def create_chat_handler(
    user_input: str = Body(..., embed=True),
):
    result = llm.create_chat_completion(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input},
        ],
        max_tokens=256,
        temperature=0.7,
    )
    answer = result["choices"][0]["message"]["content"]
    return {"answer": answer}

# 상품 관리 API

@app.get(
    "/items",
    summary="전체 상품 목록 조회 API",
    response_model=list[ItemResponse],
)
async def get_items_handler(
    session = Depends(get_session),
):
    stmt = select(Item)
    result = await run_in_threadpool(session.execute, stmt)
    items = result.scalars().all()
    return items

@app.get(
    "/items/{item_id}",
    summary="단일 상품 조회 API",
    response_model=ItemResponse,
)
def get_item_handler(
    item_id: int = Path(..., ge=1, description="상품 고유번호"),
):
    with SessionFactory() as session:
        stmt = select(Item).where(Item.id == item_id)
        result = session.execute(stmt)
        item: Item | None = result.scalar()
        if item is None:
            raise HTTPException(
                status_code=404, detail="Item Not Found"
            )
        return item


@app.post(
    "/items",
    summary="새로운 상품 등록 API",
    status_code=201,  # 201 CREATED
    response_model=ItemResponse,
)
def create_item_handler(body: ItemCreateRequest):
    with SessionFactory() as session:
        new_item = Item(name=body.name, price=body.price)
        session.add(new_item)
        session.commit()
        return new_item

@app.patch(
    "/items/{item_id}",
    summary="상품 수정 API",
    response_model=ItemResponse,
)
def update_item_handler(
    item_id: int,
    body: ItemUpdateRequest,
):
    with SessionFactory() as session:
        stmt = select(Item).where(Item.id == item_id)
        result = session.execute(stmt)
        item = result.scalar()
        if item is None:
            raise HTTPException(
                status_code=404, detail="Item Not Found"
            )
        
        if body.name is not None:
            item.name = body.name
        if body.price is not None:
            item.price = body.price

        session.commit()
        return item

@app.delete(
    "/items/{item_id}",
    summary="상품 삭제 API",
    status_code=204,  # 204 NO CONTENT
    response_model=None,
)
def delete_item_handler(item_id: int):
    with SessionFactory() as session:
        stmt = select(Item).where(Item.id == item_id)
        result = session.execute(stmt)
        item = result.scalar()
        if item is None:
            raise HTTPException(
                status_code=404, detail="Item Not Found"
            )

        session.delete(item)
        session.commit()
