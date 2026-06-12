import json
import redis

from llama_cpp import Llama


redis_client = redis.from_url(
    "redis://redis:6379", decode_responses=True
)

llm = Llama(
    model_path="./models/Llama-3.2-1B-Instruct-Q4_K_M.gguf",
    n_ctx=4096,
    n_threads=2,
    verbose=False,
    chat_format="llama-3",
)

SYSTEM_PROMPT = (
    "You are a concise assistant. "
    "Always reply in the same language as the user's input. "
    "Do not change the language. "
    "Do not mix languages."
)

def run():
    while True:
        # 1) Task Dequeue
        _, task = redis_client.brpop("inference_queue", timeout=0)
        task_data: dict = json.loads(task)

        user_input = task_data["user_input"]
        channel_id = task_data["channel"]

        # 2) 추론
        response_generator = llm.create_chat_completion(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input},
            ],
            max_tokens=256,
            temperature=0.7,
            stream=True
        )
        for chunk in response_generator:
            token = chunk["choices"][0]["delta"].get("content")
            if token:
                redis_client.publish(channel_id, token)
        
        redis_client.publish(channel_id, "[DONE]")


if __name__ == "__main__":
    run()
