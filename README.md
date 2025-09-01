# JT Express Chat — MVP (Flask)

> **🌐 Produção:** https://chat-humano-jt-express.onrender.com  
> **API base:** https://chat-humano-jt-express.onrender.com/api

[![Website status](https://img.shields.io/website?url=https%3A%2F%2Fchat-humano-jt-express.onrender.com)](https://chat-humano-jt-express.onrender.com)

<p align="center">
  <img src="assets\print-tela-chat.png" alt="JT Express Chat — Screenshot" width="900">
</p>


## 🎯 Contexto, Problema & Porquê

Este repositório nasce após observar **falhas de comunicação** no atendimento da J&T Express — tempos de resposta altos, canais pouco efetivos e ausência de chat ao vivo. A partir de uma análise de reclamações públicas e do diagnóstico elaborado no projeto de extensão, identificamos que **grande parte das queixas está ligada a comunicação/atendimento**, com **tempo de resposta por e-mail chegando a ~48h**. Para validar rapidamente uma alternativa mais responsiva, construímos um **MVP de chat com atendimento direto** e coleta de métricas operacionais. Objetivo: reduzir o tempo de resposta para a ordem de **minutos** e medir impacto em satisfação/eficiência antes de investir em uma solução mais complexa. :contentReference[oaicite:0]{index=0}

### Por que um MVP?
- **Aprender rápido** com uso real e métricas (sessions, mensagens, duração, SLA, satisfação).
- **Baixa fricção** para adotar/testar (rodar localmente com SQLite; deploy simples no Render).
- **Base extensível** para evoluir (migrar SQLite→Postgres, adicionar autenticação, dashboards, IA, etc.).

### Bases técnicas do MVP
- **Backend:** Flask 3 + Flask-CORS  
- **Dados:** Flask-SQLAlchemy; **SQLite** por padrão (config. via `SQLITE_PATH`) e **Postgres** opcional (`DATABASE_URL`).  
- **Endpoints REST (prefixo `/api`):**  
  - `POST /chat/session` (cria sessão, captura IP/UA)  
  - `POST /chat/message` (envio de mensagens por sessão)  
  - `POST /chat/end` (encerra sessão com `satisfaction_rating`)  
- **Métricas registradas:** contagem de sessões/mensagens, duração média de sessão, tempo médio de resposta, satisfação média, problemas comuns (JSON).  
- **Frontend estático:** servido de `src/static/` (fallback `index.html`).  
- **Deploy:** Render com `gunicorn src.main:app`; variáveis de ambiente (`SECRET_KEY`, `SQLITE_PATH` ou `DATABASE_URL`).  

> Em resumo: este **MVP** materializa a hipótese de que um canal síncrono e humano, com instrumentação mínima, **reduz atrito e tempo de resposta**, oferecendo evidências para decisões de produto/atendimento.


## ✨ Recursos

- **Flask 3** + **Flask-CORS**
- **Flask-SQLAlchemy** (SQLite por padrão; suporte a Postgres)
- API REST:
  - Criar sessão → `/api/chat/session`
  - Enviar mensagem → `/api/chat/message`
  - Encerrar sessão (com rating) → `/api/chat/end`
- Servir SPA/HTML de `src/static/` (fallback para `index.html`)
- Pronto para **Render** (Start com `gunicorn src.main:app`)

---

## 🧱 Stack

- **Backend:** Python, Flask, Flask-CORS, Flask-SQLAlchemy, SQLAlchemy  
- **Banco:** SQLite (dev e/ou produção com Persistent Disk) **ou** Postgres  
- **Servidor de produção:** gunicorn

---


## 🧭 Arquitetura

```mermaid
flowchart LR
  U[Usuário] --> B[Browser]
  B -->|HTTP| F[Flask (Gunicorn)]
  F --> R[/Rotas /api/chat/*/]
  F --> S[/Static / (index.html)/]
  F --> D[(SQLite / Postgres)]
  H[Render.com] --- F
```

## 🗂️ Estrutura do projeto

```
.
├─ README.md
├─ requirements.txt
├─ render.yaml                # (opcional) Infra as Code p/ Render
├─ .env.example               # modelo de variáveis de ambiente (não obrigatório)
└─ src/
   ├─ main.py                 # app Flask, blueprints, CORS, DB e static
   ├─ static/                 # frontend (index.html, favicon, etc.)
   ├─ database/
   │  └─ app.db               # SQLite local (gerado em dev)
   ├─ models/
   │  ├─ chat.py              # ChatSession, ChatMessage, ChatAnalytics
   │  └─ user.py              # User
   └─ routes/
      ├─ chat.py              # rotas de chat
      └─ user.py              # rotas de usuário
```

---

## ✅ Pré-requisitos

- **Python 3.11+**  
- **pip** e **venv**  
- (produção) **gunicorn** — já listado em `requirements.txt`

---

## ▶️ Rodando localmente

```bash
# 1) criar e ativar venv
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 2) instalar dependências
pip install -r requirements.txt

# 3) (opcional) definir SECRET_KEY via .env ou ambiente
# Em dev funciona sem, mas é recomendado usar um valor forte.

# 4) subir em modo dev
python src/main.py

# Acesse: http://localhost:5000
```

> Em dev, o app usa **SQLite** em `src/database/app.db` automaticamente (cria se não existir).

---

## 🔐 Variáveis de ambiente

O app lê variáveis nesta ordem (ver `src/main.py`):

1. `DATABASE_URL` — **Postgres**  
   `postgresql+psycopg2://usuario:senha@host:5432/banco`
2. `SQLITE_PATH` — caminho do **SQLite**  
   Ex.: `/var/data/app.db`
3. *Fallback* → `src/database/app.db` (se nada for informado)

Sempre defina:
- `SECRET_KEY` — **obrigatório em produção** (cookie signing, segurança)

Exemplo de `.env` local (opcional — **não** comitar):
```dotenv
SECRET_KEY=troque-esta-chave
# DATABASE_URL=postgresql+psycopg2://usuario:senha@host:5432/banco
# SQLITE_PATH=/caminho/absoluto/para/app.db
```

---

## 🧪 Testando a API (cURL)

### 1) Criar sessão
```bash
curl -X POST http://localhost:5000/api/chat/session   -H "Content-Type: application/json"   -d '{}'
```

### 2) Enviar mensagem
```bash
curl -X POST http://localhost:5000/api/chat/message   -H "Content-Type: application/json"   -d '{
    "session_id": "ID_DA_SESSAO",
    "author": "user",
    "content": "Olá, tudo bem?"
  }'
```

### 3) Encerrar sessão (com rating 1–5)
```bash
curl -X POST http://localhost:5000/api/chat/end   -H "Content-Type: application/json"   -d '{
    "session_id": "ID_DA_SESSAO",
    "rating": 5
  }'
```

> **Obs.:** As rotas de usuário estão em `src/routes/user.py` (ex.: listar/criar usuários).

---

## 🚀 Deploy no Render (Python nativo)

### A) Usando o painel (sem `render.yaml`)
1. **New → Web Service** → selecione seu repositório  
2. **Runtime:** Python  
3. **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Start Command:**
   ```bash
   gunicorn src.main:app
   ```
5. **Environment Variables:**
   - `SECRET_KEY` = valor forte
   - **SQLite com disco persistente:**
     - Adicione um **Persistent Disk** (ex.: 1 GB, mount `/var/data`)
     - `SQLITE_PATH=/var/data/app.db`
   - **Ou Postgres:**
     - Crie um Postgres no Render
     - `DATABASE_URL` = string de conexão
6. Deploy → o Render entrega uma URL pública **HTTPS**

### B) Usando `render.yaml` (Infra as Code)

Exemplo para **SQLite + Persistent Disk**:

```yaml
services:
  - type: web
    name: jt-express-chat-mvp
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn src.main:app
    envVars:
      - key: SECRET_KEY
        sync: false
      - key: SQLITE_PATH
        value: /var/data/app.db
    healthCheckPath: /
    autoDeploy: true
    plan: free
    disk:
      name: data
      mountPath: /var/data
      sizeGB: 1
```

> Para **Postgres**, remova a seção `disk` e configure `DATABASE_URL` no painel do Render.

---

## 🗃️ Modelos (resumo)

- **ChatSession**: `session_id`, `user_ip`, `user_agent`, `started_at`, `ended_at`, `status`, `satisfaction_rating`
- **ChatMessage**: FK `session_id`, `author`, `content`, `timestamp`
- **ChatAnalytics**: métricas diárias (`total_sessions`, `total_messages`, `avg_session_duration`, `avg_response_time`, `satisfaction_avg`, `common_issues` JSON)
- **User**: `username`, `email`

---

## 🐞 Troubleshooting

- **502 no Render** + log `gunicorn: command not found` →  
  adicionar `gunicorn` ao `requirements.txt` e fazer novo deploy.
- **Erro com SQLite no Render** →  
  usar `SQLITE_PATH=/var/data/app.db` + **Persistent Disk** habilitado.
- **Porta errada** →  
  em produção use **gunicorn** (não `app.run`); o Render detecta a porta automaticamente.

---

## 📚 Aprendizados & Próximos passos

**O que aprendemos neste MVP:**
- A importância de **variáveis de ambiente** (ex.: `SECRET_KEY`) para segurança e portabilidade.
- Por que usar **gunicorn** em produção (processo robusto vs. `app.run`).
- **SQLite** acelera o desenvolvimento, mas em PaaS é preciso **disco persistente** ou **Postgres** para não perder dados a cada deploy.
- A estrutura com **Blueprints + SQLAlchemy** facilita crescer a base de código (models, rotas e camadas bem separadas).
- A entrega de **estáticos** com fallback para `index.html` simplifica testes ponta a ponta.

**Próximos passos sugeridos:**
- Adicionar **Flask-Migrate (Alembic)** para versionar o schema do banco.
- Escrever **testes automatizados** (pytest) e configurar **CI**.
- Restringir **CORS** para domínios confiáveis em produção.
- Incluir **tratamento de erros** padronizado e validação de payloads (ex.: `pydantic`/`marshmallow`).
- Instrumentar **logs e métricas** (ex.: Prometheus/Grafana, Sentry) para visibilidade em produção.

---

## 📄 Licença

Defina a licença do projeto (ex.: MIT).

---

## 🤝 Contribuição

- Issues/PRs são bem-vindos.
- Padrão de commit sugerido: frases no **presente** e objetivas.