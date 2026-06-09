from contextlib import asynccontextmanager

import anyio

from fastapi import FastAPI, Path, Body, HTTPException, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from openai import OpenAI

from database_async import get_async_session
from llama import llm, SYSTEM_PROMPT
from orm import Item
from schema import ItemCreateRequest, ItemResponse, ItemUpdateRequest, OpenAIResponse
from config import settings


@asynccontextmanager
async def lifespan(app):
    limiter = anyio.to_thread.current_default_thread_limiter()
    limiter.total_tokens = 200  # 스레드 풀의 개수 조정
    yield


app = FastAPI(lifespan=lifespan)

client = OpenAI(api_key=settings.openai_api_key)

@app.post(
    "/gpt",
    summary="ChatGPT API 호출",
)
def call_gpt_handler(
    user_input: str = Body(..., embed=True),
):
    result = client.responses.parse(
        model="gpt-4.1-mini",
        input=user_input,
        text_format=OpenAIResponse,
    )

    if result.output_parsed.confidence < 0.5:
        return {"msg": "충분한 답변을 제공할 수 없습니다."}
    return {"answer": result.output_parsed}

@app.post(
    "/chats",
    summary="Llama 응답 생성 API",
)
def create_chat_handler(
    user_input: str = Body(..., embed=True),
):
    def token_generator():
        result = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            max_tokens=256,
            temperature=0.7,
            stream=True,
        )
        for chunk in result:
            token = chunk["choices"][0]["delta"].get("content")
            if token:
                yield token
    
    return StreamingResponse(
        token_generator(),
        media_type="text/event-stream",
    )

# 상품 관리 API

@app.get(
    "/items",
    summary="전체 상품 목록 조회 API",
    response_model=list[ItemResponse],
)
async def get_items_handler(
    session = Depends(get_async_session),
):
    stmt = select(Item)
    result = await session.execute(stmt)
    items = result.scalars().all()
    return items

@app.get(
    "/items/{item_id}",
    summary="단일 상품 조회 API",
    response_model=ItemResponse,
)
async def get_item_handler(
    item_id: int = Path(..., ge=1, description="상품 고유번호"),
    session = Depends(get_async_session),
):
    stmt = select(Item).where(Item.id == item_id)
    result = await session.execute(stmt)
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
async def create_item_handler(
    body: ItemCreateRequest,
    session = Depends(get_async_session),
):
    new_item = Item(name=body.name, price=body.price)
    session.add(new_item)
    await session.commit()
    return new_item

@app.patch(
    "/items/{item_id}",
    summary="상품 수정 API",
    response_model=ItemResponse,
)
async def update_item_handler(
    item_id: int,
    body: ItemUpdateRequest,
    session = Depends(get_async_session),
):
    stmt = select(Item).where(Item.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar()
    if item is None:
        raise HTTPException(
            status_code=404, detail="Item Not Found"
        )
    
    if body.name is not None:
        item.name = body.name
    if body.price is not None:
        item.price = body.price

    await session.commit()
    return item

@app.delete(
    "/items/{item_id}",
    summary="상품 삭제 API",
    status_code=204,  # 204 NO CONTENT
    response_model=None,
)
async def delete_item_handler(
    item_id: int,
    session = Depends(get_async_session),
):
    stmt = select(Item).where(Item.id == item_id)
    result = await session.execute(stmt)
    item = result.scalar()
    if item is None:
        raise HTTPException(
            status_code=404, detail="Item Not Found"
        )
    
    await session.delete(item)
    await session.commit()
