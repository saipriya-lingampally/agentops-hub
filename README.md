\# 🚀 AgentOps Hub



Event-driven AI orchestration platform built with FastAPI, Redis Streams, background workers, and Next.js.



This project demonstrates scalable distributed system design using:



\- FastAPI (API layer)

\- Redis Streams (event backbone)

\- Background workers (consumer groups)

\- Server-Sent Events (real-time streaming)

\- Next.js frontend

\- Docker Compose multi-service architecture



---



\## 🧠 Architecture



Client (Next.js UI)

&nbsp;       ↓

FastAPI → Redis Stream (agent\_events)

&nbsp;       ↓

Worker (xreadgroup consumer)

&nbsp;       ↓

Publishes:

RUN\_STARTED

STEP

TOOL\_CALLED

FINAL\_OUTPUT

RUN\_COMPLETED

&nbsp;       ↓

Frontend listens via SSE



---



\## ⚙️ Tech Stack



Backend:

\- Python 3.11

\- FastAPI

\- Redis Streams

\- Uvicorn



Frontend:

\- Next.js

\- React

\- SSE (EventSource)



Infrastructure:

\- Docker

\- Docker Compose



---



\## 🚀 How To Run



Start backend + Redis + worker:



docker compose up -d --build



Check API:



curl http://localhost:8000/health



Start frontend:



cd web

npm install

npm run dev



Open:



http://localhost:3000



---



\## 🔥 Example Goal



Write a polite apology email for delivery delay and offer 20% discount.



System Streams:



RUN\_STARTED

STEP

TOOL\_CALLED

FINAL\_OUTPUT

RUN\_COMPLETED



---



\## 💡 Why This Project Is Strong



✔ Event-driven architecture  

✔ Distributed system design  

✔ Redis consumer groups  

✔ Real-time UI updates  

✔ Dockerized microservices  

✔ Production-style backend workflow  



---



\## 👩‍💻 Author



Saipriya Lingampally  

AI / Backend / Distributed Systems Engineer



