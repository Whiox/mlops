
from typing import List

from sqlalchemy import String, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key = True)
    title: Mapped[str] = mapped_column(String(32))

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
    )

    user: Mapped["User"] = relationship(
        back_populates = "chats"
    )

    messages: Mapped[List["Message"]] = relationship(
        back_populates = "chat",
        foreign_keys = "Message.chat_id",
    )

    first_message_id: Mapped[int | None] = mapped_column(
        ForeignKey("messages.id"),
        nullable = True,
    )

    first_message: Mapped["Message | None"] = relationship(
        foreign_keys=[first_message_id],
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(primary_key = True)
    text: Mapped[str] = mapped_column(Text)

    is_user: Mapped[bool] = mapped_column(
        Boolean,
        default = False,
    )

    is_assistant: Mapped[bool] = mapped_column(
        Boolean,
        default = False,
    )

    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id"),
    )

    chat: Mapped["Chat"] = relationship(
        back_populates = "messages",
        foreign_keys = [chat_id],
    )
