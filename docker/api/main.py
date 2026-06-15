import uuid
import json

from fastapi import FastAPI, Body, Depends, HTTPException
from fastapi.responses import StreamingResponse
from redis import asyncio as aredis
from sqlalchemy import select

from models import Chat, Message
from database import get_session


app = FastAPI()

redis_client = aredis.from_url("redis://redis:6379", decode_responses=True)

@app.post(
    "/chats",
    summary="대화 생성 API",
)
async def create_chat_handler(
    name: str = Body(..., embed=True),
    session = Depends(get_session),
):
    new_chat = Chat(name=name)
    session.add(new_chat)
    await session.commit()
    return new_chat

@app.get(
    "/chats/{chat_uuid}/messages",
    summary="대화 내역 조회 API",
)
async def get_messages_handler(
    chat_uuid: str,
    session = Depends(get_session)
):
    # chat_uuid 올바른지 검증
    stmt = select(Chat).where(Chat.uuid == chat_uuid)
    result = await session.execute(stmt)
    chat = result.scalar()

    if chat is None:
        raise HTTPException(
            status_code=404, detail="대화방이 존재하지 않습니다."
        )

    # chat_uuid 기준 -> messages 조회
    stmt = (
        select(Message)
        .where(Message.chat_uuid == chat.uuid)
        .order_by(Message.id)  # id 기준 오름차순 정렬
    )
    result = await session.execute(stmt)
    messages = result.scalars().all()
    return messages

@app.post(
    "/chats/{chat_uuid}/messages",
    summary="메시지 생성 API",
)
async def generate_message_handler(
    chat_uuid: str,
    user_input: str = Body(..., embed=True),
    session = Depends(get_session),
):
    stmt = select(Chat).where(Chat.uuid == chat_uuid)
    result = await session.execute(stmt)
    chat = result.scalar()

    if chat is None:
        raise HTTPException(
            status_code=404, detail="대화방이 존재하지 않습니다."
        )

    # Message 조회
    stmt = (
        select(Message)
        .where(Message.chat_uuid == chat.uuid)
        .order_by(Message.id)  # id 기준 오름차순 정렬
    )
    result = await session.execute(stmt)
    messages = result.scalars().all()

    # 컨텍스트 최적화(요약 & 정리) 필요
    context = [
        {"role": msg.role, "content": msg.content} for msg in messages
    ]

    # 1) 작업 정의
    channel_id = chat.uuid
    task = {
        "context": context,
        "channel": channel_id
    }

    # 2) 채널 구독(Pub/Sub)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel_id)

    # 3) 작업 enqueue(Queue)
    await redis_client.lpush("inference_queue", json.dumps(task))

    # 4) 결과 수신(Pub/Sub)
    async def token_generator():
        tokens = []

        try:
            async for message in pubsub.listen():
                if message["type"] != "message":
                    continue

                token = message["data"]
                if token == "[DONE]":
                    break

                tokens.append(token)
                yield token
        finally:
            await pubsub.unsubscribe(channel_id)
            await pubsub.close()

            assistant_content = "".join(tokens)

            user_message = Message(
                chat_uuid=chat.uuid,
                role="user",
                content=user_input
            )
            assistant_message = Message(
                chat_uuid=chat.uuid,
                role="assistant",
                content=assistant_content
            )
            session.add_all([user_message, assistant_message])
            await session.commit()

    # 5) 클라이언트 응답
    return StreamingResponse(
        token_generator(),
        media_type="text/event-stream",
    )
