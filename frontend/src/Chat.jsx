import { useEffect, useState } from 'react'
import { useNavigate } from "react-router-dom";

import "./chat.css";


const API_URL = import.meta.env.VITE_REACT_API_URL;


function authHeaders() {
    const token = localStorage.getItem("access_token");

    return {
        Authorization: `Bearer ${token}`,
    };
}


async function checkToken() {
    const response = await fetch(
        `${API_URL}/auth/check_token`,
        {
            method: "GET",
            headers: {
                ...authHeaders(),
            },
        },
    );

    return response.ok;
}


async function fetchChats() {
    const response = await fetch(
        `${API_URL}/chat/chats`,
        {
            method: "GET",
            headers: {
                ...authHeaders(),
            },
        },
    );

    return await response.json()
}


async function createChat(title) {
    const response = await fetch(
        `${API_URL}/chat/create`,
        {
            method: "POST",
            headers: {
                ...authHeaders(),
                "Content-Type": "application/json",
            },
            body: JSON.stringify(
                {
                title,
                }
            ),
        },
    );

    return response.json()
}


async function fetchMessages(chatId){
    const response = await fetch(
        `${API_URL}/chat/chat/${chatId}`,
        {
            method: "GET",
            headers: {
                ...authHeaders(),
            },
        },
    );

    return response.json()
}


async function streamMessage(chatId, text, onToken) {
    const response = await fetch(
        `${API_URL}/chat/generate/${chatId}/stream`,
        {
            method: "POST",
            headers: {
                ...authHeaders(),
                "Content-Type": "application/json",
            },
            body: JSON.stringify(
                {
                    text: text,
                    is_user: true,
                    is_assistant: false,
                }
            ),
        },
    );

    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8");

    while (true) {
        const { value, done } = await reader.read();

        if (done) {
            break
        }

        const chunk = decoder.decode(value, { stream: true });
        onToken(chunk);
    }
}


function Chat() {
    const navigate = useNavigate();

    const [chats, setChats] = useState([]);
    const [newChatName, setNewChatName] = useState("");

    const [selectedChat, setSelectedChat] = useState(null);
    const [messages, setmessages] = useState([]);

    const [messageToSend, setMessageToSend] = useState("")


    useEffect(() => {
        async function loadPage() {
            const isValidToken = await checkToken();

            if (!isValidToken) {
                localStorage.removeItem("access_token");
                navigate("/auth");
                return;
            }

            const currentChats = await fetchChats();
            setChats(currentChats);
            setChats(currentChats.reverse())
        }

        loadPage();
    }, [navigate]);

    async function handleNewChat(event) {
        event.preventDefault()

        const title = newChatName.trim()

        if (!title) {
            return;
        }

        const newChat = await createChat(title);
        setChats([...chats, newChat]);
        setNewChatName("")
    }

    async function handleChatChoice(chat) {
        const chat_messages = await fetchMessages(chat.id);

        setSelectedChat(chat);
        setmessages(chat_messages)
    }

    async function handleSendMessage(event){
        event.preventDefault();

        if (!selectedChat) {
            return;
        }

        const text = messageToSend.trim();

        if (!text) {
            return;
        }

        setMessageToSend("");

        const userMessage = {
            text: text,
            is_user: true,
            is_assistant: false,
        };

        const assistantMessage = {
            text: "",
            is_user: false,
            is_assistant: true,
        }

        setmessages((messages) => [
            ...messages,
            userMessage,
            assistantMessage,
        ]);

        await streamMessage(selectedChat.id, text, (token) => {
            setmessages((messages) => {
                const updatedMessage = [...messages];
                const lastIndex = updatedMessage.length - 1;
                const lastMessage = updatedMessage[lastIndex];

                updatedMessage[lastIndex] = {
                    ...lastMessage,
                    text: lastMessage.text + token
                };

                return updatedMessage;
            });
        });
    }

    return (
        <main>
            <section id="chat-page__sidebar">
                <h1>MLops чат</h1>

                <div id="chat-page__sidebar__chats">
                    <ul id="chat-page__sidebar__ul">
                        {chats.map((chat) => (
                        <li key={chat.id} className="chat-page__sidebar__li">
                            <button
                                className="chat-page__sidebar__li__button"
                                title={chat.title}
                                type="button"
                                onClick={async () => handleChatChoice(chat)}
                            >
                                {chat.title}
                            </button>
                        </li>
                    ))}
                    </ul>
                </div>

                <form onSubmit={handleNewChat}>
                <h2>Создать чат</h2>

                <input id="chat-page__sidebar__newchat"
                    value={newChatName}
                    onChange={
                        (event) => setNewChatName(event.target.value)
                    }
                    placeholder="Название"
                />
            </form>
            </section>

            <section id="chat-page__chat">
                <ul id="chat-page__chat__ul">
                    {messages.map((message, index) => (
                        <li className="chat-page__chat__li">
                            <div className={
                                message.is_user
                                    ? "chat-page__chat__div chat-page__chat__div_user"
                                    : "chat-page__chat__div chat-page__chat__div_assistant"
                            }>
                                {message.text}
                            </div>
                        </li>
                    ))}
                </ul>

                <form id="chat-page__chat__form" onSubmit={handleSendMessage}>
                    <div id="chat-page__chat__inputzone">
                        <textarea id="chat-page__chat__textarea"
                            value={messageToSend}
                            onChange={
                                (event) => setMessageToSend(event.target.value)
                            }
                            placeholder="Привет, Мир!"
                        />
                        <button
                            id="chat-page__chat__send"
                            type="submit"
                            disabled={!selectedChat || !messageToSend.trim()}
                        >
                            <svg
                                width="18"
                                height="18"
                                viewBox="0 0 16 16"
                                fill="none"
                                aria-hidden="true"
                            >
                                <path
                                    d="M6 8L2 8L2 6L8 5.24536e-07L14 6L14 8L10 8L10 16L6 16L6 8Z"
                                    fill="#eae8e8"
                                />
                            </svg>
                        </button>
                    </div>
                </form>
            </section>
        </main>
    )
}

export default Chat
