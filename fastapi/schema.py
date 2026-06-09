from pydantic import BaseModel, Field


# Item 생성 요청 데이터 구조
class ItemCreateRequest(BaseModel):
    name: str
    price: int

# Item 수정 요청 데이터 구조
class ItemUpdateRequest(BaseModel):
    name: str | None = None
    price: int | None = None

# Item 응답 데이터 구조
class ItemResponse(BaseModel):
    id: int
    name: str
    price: int

class OpenAIResponse(BaseModel):
    result: str = Field(description="최종 답변")
    confidence: float = Field(description="0~1 사이의 답변 신뢰도")
