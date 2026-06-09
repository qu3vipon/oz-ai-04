from pydantic_settings import BaseSettings


# 프로젝트 내의 설정값을 관리하는 클래스
class Settings(BaseSettings):
    openai_api_key: str

    class Config:
        env_file = ".env"

settings = Settings()
