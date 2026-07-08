import {useEffect, useState} from 'react'

import "./chat.css";


const API_URL = import.meta.env.VITE_REACT_API_URL;
const token = localStorage.getItem("access_token");


async function fetchChats() {
    const response = await fetch(
        `${API_URL}/chat/chats`,
        {
            method: "GET",
            headers: {
                Authorization: `Bearer ${token}`
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
                Authorization: `Bearer ${token}`,
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
                Authorization: `Bearer ${token}`,
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
                Authorization: `Bearer ${token}`,
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
    const [chats, setChats] = useState([]);
    const [newChatName, setNewChatName] = useState("");

    const [selectedChat, setSelectedChat] = useState(null);
    const [messages, setmessages] = useState([]);

    const [messageToSend, setMessageToSend] = useState("")


    useEffect(() => {
        async function loadChats() {
            const currentChats = await fetchChats();
            setChats(currentChats);
        }

        loadChats();
    }, []);

    async function handleNewChat() {
        const newChat = await createChat(newChatName);
        setChats([...chats, newChat]);
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
                <h1>Чаты</h1>

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

                <form>
                <h2>Создать чат</h2>

                <input
                    value={newChatName}
                    onChange={
                        (event) => setNewChatName(event.target.value)
                    }
                    placeholder="Новый чат"
                />

                <button type="button" onClick={handleNewChat}>
                    Создать
                </button>
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
                        <button type="submit">
                            o
                        </button>
                    </div>
                </form>
            </section>
        </main>
    )
}

export default Chat
