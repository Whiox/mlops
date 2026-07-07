
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import Select
from sqlalchemy.orm import Session

from database import get_db

from chat.schemas import MessageSc, ChatCreateSc, ChatPrevSc
from chat.models import Chat, Message
from chat.chain import get_llm, Model

from auth.models import User
from auth.depends import get_current_user


router = APIRouter()


@router.get("/chats", response_model = list[ChatPrevSc])
def get_chats(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = Select(Chat).where(Chat.user == user)
    chats = db.scalars(query).all()

    return chats


@router.post("/chats", response_model = ChatPrevSc)
def create_chat(
    payload: ChatCreateSc,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chat = Chat(
        title = payload.title,
        user = user,
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


@router.get("/chat/{chat_id}", response_model = list[MessageSc])
def get_chat(
    chat_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = Select(Chat).where((Chat.id == chat_id) & (Chat.user == user))
    chat = db.scalar(query)
    if not chat:
        raise HTTPException(404, detail="Chat not found")

    query = Select(Message).where(Message.chat_id == chat.id).order_by(Message.id.asc())
    messages = db.scalars(query).all()

    return messages


# @router.post("/generate/{chat_id}", response_model = MessageSc)
# def generate(
#     chat_id: int,
#     message: MessageSc,
#     user: User = Depends(get_current_user),
#     db: Session = Depends(get_db),
#     model: Model = Depends(get_llm),
# ):
#     query = Select(Chat).where((Chat.id == chat_id) & (Chat.user == user))
#     chat = db.scalar(query)
#     if not chat:
#         raise HTTPException(404, detail="Chat not found")
#
#
#     query = Select(Message).where(Message.chat_id == chat_id).order_by(Message.id.asc())
#     messages = list(db.scalars(query).all())
#
#
#     if message.is_assistant is True and messages and messages[-1].is_assistant is True:
#         formated_context = model.create_chat_context(messages[:-1])
#         generation = model.generate(formated_context)
#
#         last_message = MessageSc(
#             text = generation,
#             is_user = False,
#             is_assistant = True,
#         )
#
#         db.delete(messages[-1])
#         db.commit()
#
#     elif message.is_user is True:
#         user_message = Message(
#             text = message.text,
#             is_user = True,
#             is_assistant = False,
#             chat = chat
#         )
#
#         formated_context = model.create_chat_context(messages + [user_message])
#
#         generation = model.generate(formated_context)
#
#         last_message = MessageSc(
#             text = generation,
#             is_user = False,
#             is_assistant = True,
#         )
#
#         db.add(user_message)
#         db.commit()
#         db.refresh(user_message)
#
#     else:
#         raise HTTPException(400, detail="Nothing to do")
#
#
#     ass_message = Message(
#         text = last_message.text,
#         is_user = False,
#         is_assistant = True,
#         chat = chat,
#     )
#
#     db.add(ass_message)
#     db.commit()
#     db.refresh(ass_message)
#
#     return last_message


@router.post("/generate/{chat_id}/stream")
def stream_generate(
    chat_id: int,
    message: MessageSc,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    model: Model = Depends(get_llm),
):
    query = Select(Chat).where((Chat.id == chat_id) & (Chat.user == user))
    chat = db.scalar(query)

    if not chat:
        raise HTTPException(404, detail="Chat not found")

    query = Select(Message).where(Message.chat_id == chat_id).order_by(Message.id.asc())
    messages = list(db.scalars(query).all())

    user_message = Message(
        text=message.text,
        is_user=True,
        is_assistant=False,
        chat=chat,
    )

    context = model.create_chat_context(messages + [user_message])

    def token_stream():
        full_text = ""

        for token in model.stream_generate(context):
            full_text += token
            yield token

        db.add(user_message)
        db.add(
            Message(
                text = full_text,
                is_user = False,
                is_assistant = True,
                chat = chat,
            )
        )
        db.commit()

    return StreamingResponse(
        token_stream(),
        media_type="text/plain",
    )
