import { useState } from 'react'
import { useNavigate } from "react-router-dom";

import "./auth.css";


const API_URL = import.meta.env.VITE_REACT_API_URL;


function Auth() {
    const navigate = useNavigate();

    const [mode, setMode] = useState("login");

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");


    async function handleSubmit(event) {
        event.preventDefault();

        setError("")

        let path = mode === "login" ? "login" : "registration"

        const response = await fetch(
            `${API_URL}/auth/${path}`,
            {
                method: "POST",
                headers:
                    {
                        "Content-Type": "application/json",
                    },
                body: JSON.stringify(
                    {
                        username,
                        password,
                    }
                ),
            },
        );

        const data = await response.json();

        if (data.status === "error") {
            setError(data.error);
            return;
        }

        localStorage.setItem("access_token", data.token);
        navigate("/")
    }

    let submitButtonPlaceholder = mode === "login" ? "Войти" : "Создать аккаунт"

    return (
        <div id="auth-page__centred">
            <form id="auth-page__form" onSubmit={handleSubmit}>
                <h2 id="auth-page__title">
                    {mode === "login" ? "Войдите в аккаунт" : "Создайте аккаунт"}
                </h2>

                <input
                    className="auth-page__input"
                    value={username}
                    onChange={
                        (event) => setUsername(event.target.value)
                    }
                    placeholder="Логин"
                />

                <input
                    className="auth-page__input"
                    value={password}
                    onChange={
                        (event) => setPassword(event.target.value)
                    }
                    placeholder="Пароль"
                />

                <button id="auth-page__submit" type="submit">{submitButtonPlaceholder}</button>

                {error && <p>{error}</p>}

                <div id="auth-page__method__box">
                    <button
                        className="auth-page__method__button"
                        type="button"
                        onClick={() => setMode("login")}
                    >
                        Вход
                    </button>
                    <button
                        className="auth-page__method__button"
                        type="button"
                        onClick={() => setMode("registration")}
                    >
                        Регистрация
                    </button>
                </div>
            </form>
        </div>
    )
}


export default Auth
