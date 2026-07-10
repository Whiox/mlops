# MLOps Chat

Учебный проект веб-чата с локальной LLM-моделью через Ollama.

Проект сделан для практики fullstack-разработки, Docker, FastAPI, React и работы с локальными языковыми моделями. После завершения разработки проект планируется заархивировать.

## Возможности

- регистрация и вход пользователя;
- проверка токена при входе в чат;
- создание отдельных чатов;
- хранение истории сообщений;
- отправка контекста диалога в локальную LLM;
- потоковая генерация ответа модели;
- запуск backend, frontend и Ollama через Docker Compose;
- настройка портов, модели и адресов сервисов через `.env`.

## Стек

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- LangChain
- Ollama

### Frontend

- React
- Vite
- React Router
- CSS
- Nginx для production-сборки

### Инфраструктура

- Docker
- Docker Compose
- Ollama
- GGUF-модель, подключаемая через Ollama

## Структура проекта

```text
.
├── backend/                 # FastAPI-приложение
│   ├── auth/                # регистрация, логин, проверка токена
│   ├── chat/                # чаты, сообщения, генерация ответа
│   ├── main.py              # точка входа FastAPI
│   └── Dockerfile-backend
├── frontend/                # React-приложение
│   ├── src/
│   │   ├── Auth.jsx         # страница авторизации
│   │   ├── Chat.jsx         # страница чата
│   │   └── main.jsx         # маршрутизация
│   ├── nginx.conf
│   └── Dockerfile-frontend
├── docker-compose.yml
├── .example.env
└── README.md
```

## Как это работает

Frontend отправляет запросы в FastAPI backend. Backend проверяет токен пользователя, загружает историю выбранного чата из базы данных и формирует контекст для модели.

Модель вызывается через `ChatOllama`. Ответ возвращается не одним большим JSON, а потоково через `StreamingResponse`, поэтому frontend может показывать текст постепенно, по мере генерации токенов.

## Подготовка

Создайте Docker-сеть для Ollama:

```bash
docker network create ollama-network
```

Создайте `.env` на основе примера:

```bash
cp .example.env .env
```

Пример основных переменных:

```env
OLLAMA_MODEL_NAME=llama-8b
OLLAMA_URL=http://ollama-instance:11434

UVICORN_PORT=10081
REACT_PORT=10173

VITE_REACT_API_URL=http://localhost:10081
```

Для запуска на сервере `VITE_REACT_API_URL` должен указывать на публичный адрес backend, а не на `localhost`.

## Запуск

Запуск backend и frontend:

```bash
docker compose up --build
```

Если нужно поднять Ollama вместе с проектом:

```env
COMPOSE_PROFILES=ollama
```

И затем:

```bash
docker compose up --build
```

После запуска:

- frontend: `http://localhost:10173`
- backend: `http://localhost:10081`

## Ollama

Backend обращается к Ollama по адресу из переменной:

```env
OLLAMA_URL=http://ollama-instance:11434
```

Имя модели задается отдельно:

```env
OLLAMA_MODEL_NAME=llama-8b
```

На сервере можно использовать один общий контейнер Ollama для нескольких проектов, подключив их к одной Docker-сети.

## API

Основные группы маршрутов:

```text
/auth/registration       # регистрация
/auth/login              # вход
/auth/check_token        # проверка токена

/chat/chats              # список чатов
/chat/create             # создание чата
/chat/chat/{chat_id}     # сообщения выбранного чата
/chat/generate/{chat_id}/stream
                          # потоковая генерация ответа
```

## Статус проекта

Проект учебный и не рассчитан на production-использование.
