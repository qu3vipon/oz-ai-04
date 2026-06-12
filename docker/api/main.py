import uuid
import json

from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse

from redis import asyncio as aredis


app = FastAPI()

redis_client = aredis.from_url(
    "redis://redis:6379", decode_responses=True
)

@app.post("/chats")
async def generate_chat_handler(
    user_input: str = Body(..., embed=True)
):
    # 1) 작업 정의
    channel_id = str(uuid.uuid4())
    task = {
        "user_input": user_input,
        "channel": channel_id
    }

    # 2) 채널 구독(Pub/Sub)
    pubsub = redis_client.pubsub()
    await pubsub.subscribe(channel_id)

    # 3) 작업 enqueue(Queue)
    await redis_client.lpush("inference_queue", json.dumps(task))

    # 4) 결과 수신(Pub/Sub)
    async def token_generator():
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            token = message["data"]
            if token == "[DONE]":
                break

            yield token
        
        await pubsub.unsubscribe(channel_id)
        await pubsub.close()

    # 5) 클라이언트 응답
    return StreamingResponse(
        token_generator(),
        media_type="text/event-stream",
    )
