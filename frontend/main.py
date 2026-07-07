
import os
from dotenv import load_dotenv

load_dotenv()

import requests
import streamlit as st


API_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")


def request_json(method: str, path: str, **kwargs):
    response = requests.request(
        method,
        f"{API_URL}{path}",
        timeout=600,
        **kwargs,
    )

    response.raise_for_status()
    return response.json()


def auth_headers():
    return {
        "Authorization": f"Bearer {st.session_state.token}",
    }


def login(username: str, password: str):
    return request_json(
        "POST",
        "/auth/login",
        json={
            "username": username,
            "password": password,
        },
    )


def register(username: str, password: str):
    return request_json(
        "POST",
        "/auth/registration",
        json={
            "username": username,
            "password": password,
        },
    )


def get_chats():
    return request_json(
        "GET",
        "/chat/chats",
        headers=auth_headers(),
    )


def create_chat(title: str):
    return request_json(
        "POST",
        "/chat/chats",
        headers=auth_headers(),
        json={
            "title": title,
        },
    )


def get_chat_messages(chat_id: int):
    return request_json(
        "GET",
        f"/chat/chat/{chat_id}",
        headers=auth_headers(),
    )


def generate_message(chat_id: int, message: dict):
    return request_json(
        "POST",
        f"/chat/generate/{chat_id}",
        headers=auth_headers(),
        json=message,
    )


def generate_message_stream(chat_id: int, message: dict):
    with requests.post(
        f"{API_URL}/chat/generate/{chat_id}/stream",
        headers=auth_headers(),
        json=message,
        stream=True,
        timeout=600,
    ) as response:
        response.raise_for_status()

        for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
            if chunk:
                yield chunk


def init_state():
    defaults = {
        "token": None,
        "chats": [],
        "current_chat_id": None,
        "messages_by_chat": {},
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_state():
    st.session_state.token = None
    st.session_state.chats = []
    st.session_state.current_chat_id = None
    st.session_state.messages_by_chat = {}


def message_role(message: dict):
    if message.get("is_assistant"):
        return "assistant"

    return "user"


def current_chat():
    for chat in st.session_state.chats:
        if chat["id"] == st.session_state.current_chat_id:
            return chat

    return None


def load_messages(chat_id: int):
    st.session_state.messages_by_chat[chat_id] = get_chat_messages(chat_id)


def load_chats():
    st.session_state.chats = get_chats()
    chat_ids = {chat["id"] for chat in st.session_state.chats}

    if st.session_state.current_chat_id not in chat_ids:
        st.session_state.current_chat_id = None

    if st.session_state.current_chat_id is None and st.session_state.chats:
        st.session_state.current_chat_id = st.session_state.chats[0]["id"]

    if st.session_state.current_chat_id is not None:
        load_messages(st.session_state.current_chat_id)


def select_chat(chat_id: int):
    st.session_state.current_chat_id = chat_id
    load_messages(chat_id)


def current_messages():
    chat_id = st.session_state.current_chat_id

    if chat_id is None:
        return []

    return st.session_state.messages_by_chat.setdefault(chat_id, [])


def show_auth():
    st.title("MLOps Chat")

    tab_login, tab_register = st.tabs(["Вход", "Регистрация"])

    with tab_login:
        with st.form("login_form"):
            username = st.text_input("Логин", key="login_username")
            password = st.text_input("Пароль", type="password", key="login_password")
            submitted = st.form_submit_button("Войти", type="primary")

        if submitted:
            data = login(username, password)

            if data["status"] == "ok":
                st.session_state.token = data["token"]
                load_chats()
                st.rerun()

            st.error(data["error"])

    with tab_register:
        with st.form("register_form"):
            username = st.text_input("Логин", key="register_username")
            password = st.text_input("Пароль", type="password", key="register_password")
            submitted = st.form_submit_button("Зарегистрироваться", type="primary")

        if submitted:
            data = register(username, password)

            if data["status"] == "ok":
                st.session_state.token = data["token"]
                load_chats()
                st.rerun()

            st.error(data["error"])


def show_sidebar():
    with st.sidebar:
        st.header("Чаты")

        if st.button("Обновить", use_container_width=True):
            load_chats()
            st.rerun()

        with st.form("create_chat_form"):
            title = st.text_input("Новый чат", max_chars=32)
            submitted = st.form_submit_button("Создать", type="primary")

        if submitted:
            if not title.strip():
                st.warning("Название чата не должно быть пустым")
            else:
                chat = create_chat(title.strip())
                st.session_state.current_chat_id = chat["id"]
                st.session_state.messages_by_chat[chat["id"]] = []
                load_chats()
                st.rerun()

        st.divider()

        if not st.session_state.chats:
            load_chats()

        for chat in st.session_state.chats:
            selected = chat["id"] == st.session_state.current_chat_id

            if st.button(
                chat["title"],
                key=f"chat_{chat['id']}",
                type="primary" if selected else "secondary",
                use_container_width=True,
            ):
                select_chat(chat["id"])
                st.rerun()

        st.divider()

        if st.button("Выйти", use_container_width=True):
            reset_state()
            st.rerun()


def show_chat():
    chat = current_chat()

    if chat is None:
        st.info("Выбери или создай чат")
        return

    st.subheader(chat["title"])

    messages = current_messages()

    for message in messages:
        with st.chat_message(message_role(message)):
            st.write(message["text"])

    if st.button("↻ Перегенерировать последний ответ"):
        with st.spinner("Перегенерирую ответ..."):
            generate_message(
                chat["id"],
                {
                    "text": "",
                    "is_user": False,
                    "is_assistant": True,
                },
            )
        load_messages(chat["id"])
        st.rerun()

    prompt = st.chat_input("Напиши сообщение")

    if prompt:
        user_message = {
            "text": prompt.strip(),
            "is_user": True,
            "is_assistant": False,
        }

        with st.spinner("Генерирую ответ..."):
            with st.chat_message("assistant"):
                placeholder = st.empty()
                full_text = ""

                for token in generate_message_stream(chat["id"], user_message):
                    full_text += token
                    placeholder.write(full_text)

        load_messages(chat["id"])
        st.rerun()


def show_request_error(error: requests.RequestException):
    if isinstance(error, requests.Timeout):
        st.error("Backend не ответил вовремя. Проверь FastAPI на http://127.0.0.1:8000")
        return

    if isinstance(error, requests.ConnectionError):
        st.error("Backend недоступен. Проверь, что FastAPI запущен на http://127.0.0.1:8000")
        return

    if isinstance(error, requests.HTTPError) and error.response is not None:
        try:
            detail = error.response.json()
        except ValueError:
            detail = error.response.text

        st.error(f"Ошибка backend {error.response.status_code}: {detail}")
        return

    st.error(f"Ошибка запроса: {error}")


init_state()

try:
    if st.session_state.token:
        show_sidebar()
        show_chat()
    else:
        show_auth()
except requests.RequestException as error:
    show_request_error(error)
