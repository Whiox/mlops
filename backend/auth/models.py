
from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(32))

    password: Mapped[str] = mapped_column(String(256))
    token: Mapped[str] = mapped_column(String(256))

    chats: Mapped[List["Chat"]] = relationship(
        back_populates = "user",
    )
