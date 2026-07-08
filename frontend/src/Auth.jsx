import { useState } from 'react'


const API_URL = import.meta.env.VITE_REACT_API_URL;


function Auth() {
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
    }

    let submitButtonPlaceholder = mode === "login" ? "Войти" : "Создать аккаунт"

    return (
        <form onSubmit={handleSubmit}>
            <input
                value={username}
                onChange={
                    (event) => setUsername(event.target.value)
                }
                placeholder="Логин"
            />

            <input
                value={password}
                onChange={
                    (event) => setPassword(event.target.value)
                }
                placeholder="Пароль"
            />

            <button type="submit">{submitButtonPlaceholder}</button>

            {error && <p>{error}</p>}

            <div>
                <button type="button" onClick={() => setMode("login")}>
                    Вход
                </button>
                <button type="button" onClick={() => setMode("registration")}>
                    Регистрация
                </button>
            </div>
        </form>
    )
}


export default Auth
