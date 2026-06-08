from sqlalchemy import Integer, String
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped


# 테이블 클래스의 부모 클래스
class Base(DeclarativeBase):
    pass

class Item(Base):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(128))
    price: Mapped[int] = mapped_column(Integer)
