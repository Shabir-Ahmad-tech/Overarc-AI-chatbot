# 📋 Overarc SmartBot — Complete Project Report

> **Generated:** May 24, 2026  
> **Project:** Overarc Agency AI Chatbot Builder Toolkit  
> **Version:** 2.0  
> **Tech Stack:** Python (Flask) + HTML/CSS/JS + OpenRouter AI + Supabase PostgreSQL

---

## 1. 🎯 PROJECT OVERVIEW

**Overarc SmartBot** is a complete **white-label AI chatbot SaaS platform** built for **Overarc Agency** — an AI automation agency based in Pakistan. The system allows the agency to build, manage, and sell custom AI chatbots to businesses with zero coding per client.

### Core Business Model
- Build **ONE** product → Customize per client → Deliver in **3 days**
- Pricing: **$150 - $400** one-time setup + **$30/month** recurring hosting
- Target clients: Local Pakistani businesses (clinics, restaurants, real estate) + International clients via Fiverr/Upwork

### Key Differentiators
- ✅ **RAG System** — Upload PDFs/text, AI learns from documents automatically
- ✅ **Multi-tenant** — One codebase serves unlimited clients
- ✅ **Standalone links** — Works even for clients without websites
- ✅ **24/7 operation** — AI answers questions, captures leads, books appointments
- ✅ **Full security** — JWT auth, bcrypt passwords, rate limiting, input validation

---

## 2. 📂 COMPLETE FILE STRUCTURE

```
Overarc-AI-chatbot/
│
├── server.py                          # ⚙️ BACKEND ENGINE (2078 lines) — Flask API
├── .env                               # 🔑 Environment configuration (SECRET)
├── businesses.json                    # 📋 Client bot configurations (143 lines)
├── requirements.txt                   # 📦 Python dependencies (9 packages)
├── schema.sql                         # 🗄️ Core database schema (Supabase)
├── supabase_migration.sql             # 🗄️ RAG vector database schema (76 lines)
├── .gitignore                         # 🚫 Git ignore rules
├── README.md                          # 📘 Documentation (updated)
├── PROJECT_REPORT.md                  # 📋 This file
│
├── AI-chatbot.md                      # 📘 Business blueprint (582 lines)
├── HOW_TO_SELL_CLIENTS.md             # 💼 Sales guide (224 lines)
├── refrence.md                        # 📚 Industry reference (746 lines)
│
├── public/
│   ├── index.html                     # 🌐 Agency marketing website
│   ├── chat.html                      # 💬 Standalone chat page (476 lines)
│   ├── smartbot-dashboard.html        # 📊 Admin dashboard
│   ├── smartbot-demo.html             # 🎮 Live demo sandbox
│   ├── widget.js                      # 🔌 Embeddable chat widget
│   └── Icons/                         # 🖼️ Brand graphics
│       ├── Hero.png
│       └── Transparent.png
│
├── leads.json                         # 📩 Captured leads (auto-generated)
├── appointments.json                  # 📅 Booked appointments (auto-generated)
├── chat_logs.json                     # 💬 Chat logs (auto-generated)
├── document_chunks_{bot_id}.json      # 📄 RAG chunks per bot (auto-generated)
├── documents_{bot_id}.json            # 📚 Document metadata per bot (auto-generated)
│
└── venv/                              # 🐍 Python virtual environment (IGNORED)
```

---

## 3. 🏗️ ARCHITECTURE

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Browser)                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────┐ │
│  │ index.html│  │chat.html │  │dashboard │  │  widget.js │ │
│  │(Agency    │  │(Chat     │  │(Admin    │  │(Embeddable │ │
│  │ Website)  │  │Interface)│  │Panel)    │  │ Widget)    │ │
│  └──────────┘  └──────────┘  └──────────┘  └────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │ HTTP/JSON
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (Flask — server.py)                │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                 API Endpoints (20+)                  │   │
│  │  /api/chat  /api/leads  /api/appointments           │   │
│  │  /api/auth/login  /api/settings  /api/documents/*   │   │
│  │  /api/health  /api/widget-config  /api/chat-logs    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Core Systems                            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────┐│   │
│  │  │RAG Engine│ │Auth      │ │Lead      │ │Appt.   ││   │
│  │  │(Embed +  │ │(JWT +    │ │Capture + │ │Booking ││   │
│  │  │ Vector   │ │bcrypt)   │ │Email     │ │System  ││   │
│  │  │ Search)  │ │          │ │Notify    │ │        ││   │
│  │  └──────────┘ └──────────┘ └──────────┘ └────────┘│   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        ▼                  ▼                  ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  OpenRouter  │  │   Supabase   │  │ Local JSON   │
│  AI API      │  │  PostgreSQL  │  │ Files (Dev   │
│  (Chat +     │  │  + pgvector  │  │ Fallback)    │
│  Embeddings) │  │  (Optional)  │  │              │
└──────────────┘  └──────────────┘  └──────────────┘
```

### Data Flow (Chat Request)

```
1. User sends message → POST /api/chat { bot, message, history }
2. Server loads business config from DB (Supabase or JSON)
3. Server generates embedding of user message via OpenRouter
4. Server searches vector DB for relevant document chunks (RAG)
5. Server builds system prompt + RAG context + message history
6. Server sends to OpenRouter (Gemini 2.5 Flash)
7. AI response returned to user
8. Chat log saved to DB
```

---

## 4. 🛠️ TECHNOLOGIES & CONCEPTS USED (Full Reference)

### 4.1 🤖 AI & Language Models

| Technology | Model / Service | Purpose | How It's Used |
|-----------|----------------|---------|---------------|
| **OpenRouter API** | Gateway to 200+ AI models | Provides unified API access to multiple LLMs without separate accounts | Every chat request hits `https://openrouter.ai/api/v1/chat/completions` |
| **Gemini 2.5 Flash** | `google/gemini-2.5-flash` | Primary chat AI model | Powers all chatbot conversations; generates human-like responses in English/Urdu |
| **Perplexity Embedding** | `perplexity/pplx-embed-v1-0.6b` | Text embedding model (RAG) | Converts document chunks into 1536-dimension vectors for similarity search |
| **OpenAI SDK** | `openai` Python package | Utility SDK (installed, not directly used) | Available for future model integration |

**Why These Models?**
- **Gemini 2.5 Flash** → Cheapest option on OpenRouter (~$0.01/100 conversations), fast, supports Urdu
- **pplx-embed-v1-0.6b** → Free embedding model via OpenRouter, 1536-dim output (compatible with pgvector)

### 4.2 🔍 RAG (Retrieval-Augmented Generation) — Deep Dive

**What is RAG?**
RAG = **Retrieval-Augmented Generation**. Instead of relying solely on the AI's training data, RAG retrieves relevant information from uploaded documents and injects it into the AI's context at query time. This means:
- The AI answers from **your actual business documents**, not generic knowledge
- No fine-tuning needed — just upload PDFs or paste text
- Information stays **up-to-date** — just re-upload changed documents

**RAG Components in This System:**

| Component | Function | Code |
|-----------|----------|------|
| **Text Chunking** | Splits documents into ~500-char segments with 50-char overlap | `chunk_text()` in server.py |
| **Embedding Generation** | Converts text chunks to 1536-dimension vectors | `get_embedding()` in server.py |
| **Vector Storage** | Stores embeddings for fast similarity search | Supabase `document_chunks` table OR local JSON |
| **Vector Index** | HNSW index for sub-second similarity search | `idx_document_chunks_embedding` (HNSW, m=16, ef_construction=200) |
| **Similarity Search** | Cosine similarity search with threshold filtering | `search_relevant_chunks()` or `match_documents()` SQL function |
| **Document Analysis** | AI extracts structured data from uploaded docs | `analyze_document_with_ai()` using Gemini 2.5 Flash |
| **Context Injection** | Injects relevant chunks into system prompt | RAG context appended to system_prompt before AI call |

**RAG Processing Pipeline (Step-by-Step):**
```
[1] User uploads PDF/pastes text
[2] Text extracted (PyPDF2 for PDFs)
[3] Text split into chunks (500 chars, 50 overlap)
[4] Each chunk embedded → 1536-dim vector
[5] Chunks stored in vector DB with metadata
[6] AI analyzes document → extracts services/FAQs/policies
[7] User asks a question
[8] Question embedded → same embedding model
[9] Vector DB searched for similar chunks (cosine similarity)
[10] Top-3 most relevant chunks retrieved
[11] Chunks injected into AI system prompt
[12] AI answers with document context
```

### 4.3 🔐 Security Technologies

| Technology | Purpose | Implementation Detail |
|-----------|---------|----------------------|
| **JWT (JSON Web Tokens)** | Stateless authentication | PyJWT library, HS256 algorithm, 24-hour expiry, includes bot_id + jti claims |
| **bcrypt** | Password hashing | Salt rounds via `bcrypt.gensalt()`, stored as hash in DB |
| **Flask-CORS** | Cross-Origin Resource Sharing | Restricted to `https://overarc.co` and `http://localhost:5000` |
| **Flask-Limiter** | Rate limiting | 30 requests/minute/IP on `/api/chat` |
| **Input Validation** | Field length enforcement | `validate_field_lengths()` with 25+ field-specific limits |
| **Regex Sanitization** | Bot ID injection prevention | `sanitize_bot_id()` — only allows `[a-zA-Z0-9\-]` |

### 4.4 🗄️ Database Technologies

| Technology | Version/Type | Purpose |
|-----------|-------------|---------|
| **Supabase PostgreSQL** | PostgreSQL 15+ | Primary production database (multi-tenant) |
| **pgvector** | Extension for PostgreSQL | Vector similarity search for RAG embeddings |
| **JSONB** | PostgreSQL data type | Stores FAQs, services, extraction summaries (schemaless) |
| **HNSW Index** | Hierarchical Navigable Small World | Fast approximate nearest neighbor search on 1536-dim vectors |
| **Local JSON Files** | Plain .json files | Development fallback (zero-config, no database needed) |

**Database Tables Structure:**
```
Core Tables (schema.sql):
├── businesses      → Multi-tenant bot configs (PK: id/varchar)
├── leads           → Captured customer leads (FK: bot → businesses)
├── appointments    → Booked appointments (FK: bot → businesses)
└── chat_logs       → Conversation history (FK: bot → businesses)

RAG Tables (supabase_migration.sql):
├── document_chunks → Text chunks + VECTOR(1536) embeddings + HNSW index
└── documents       → Document metadata + extraction summaries (JSONB)
```

### 4.5 📡 API & Communication Technologies

| Technology | Purpose |
|-----------|---------|
| **REST API** | All communication between frontend and backend |
| **HTTP/JSON** | Data interchange format |
| **Bearer Token Auth** | JWT tokens sent via `Authorization: Bearer <token>` header |
| **Rate Limiting** | HTTP 429 responses when exceeded |

### 4.6 🌐 Frontend Technologies

| Technology | Purpose |
|-----------|---------|
| **HTML5** | Page structure for chat, dashboard, marketing site |
| **CSS3** | Styling with custom properties, dark theme, responsive design |
| **JavaScript (Vanilla)** | Chat logic, API calls, widget injection, dashboard interactivity |
| **Google Fonts (Inter, Space Grotesk)** | Typography |
| **Lucide Icons** | SVG icon library for UI elements |
| **Embed Widget** | `<script>` tag injection for third-party websites |

### 4.7 📧 Email & Notification Technologies

| Technology | Purpose |
|-----------|---------|
| **Resend.com API** | Sends email notifications for new leads and appointments |
| **HTML Email Templates** | Formatted email bodies with lead/appointment details |

### 4.8 🐍 Python Ecosystem & Libraries

| Library | Version | Purpose | Key Functions Used |
|---------|---------|---------|-------------------|
| **Flask** | Latest | Web framework, routing, request handling | `Flask()`, `@app.route()`, `send_from_directory()` |
| **Requests** | Latest | HTTP client for API calls | `requests.post()`, `requests.get()`, `requests.patch()`, `requests.delete()` |
| **python-dotenv** | Latest | Environment variable loading | `load_dotenv()` |
| **Flask-CORS** | Latest | Cross-origin headers | `CORS(app, origins=[...])` |
| **PyJWT** | Latest | JWT token generation and verification | `jwt.encode()`, `jwt.decode()` |
| **bcrypt** | Latest | Password hashing and verification | `bcrypt.hashpw()`, `bcrypt.checkpw()` |
| **Flask-Limiter** | Latest | Rate limiting middleware | `Limiter(app)`, `@limiter.limit("30 per minute")` |
| **PyPDF2** | Latest | PDF text extraction for RAG | `PdfReader()`, `page.extract_text()` |
| **OpenAI** | Latest | OpenAI SDK (utility/fallback) | Installed for future compatibility |

### 4.9 ☁️ Infrastructure & Hosting Technologies

| Technology | Purpose | Current Status |
|-----------|---------|---------------|
| **Localhost (port 5000)** | Development server | Running locally via Flask |
| **Render/Railway/Fly.io** | Production hosting (recommended) | Not yet deployed |
| **Supabase Cloud** | Database hosting (recommended) | Optional — use Supabase free tier |
| **Git** | Version control | `.gitignore` configured for security |

### 4.10 🧠 Key Concepts & Algorithms

| Concept | Description | Where Used |
|---------|-------------|------------|
| **Cosine Similarity** | Measures angle between two vectors (range: -1 to 1) | `search_relevant_chunks()` — finds relevant document chunks |
| **HNSW Algorithm** | Hierarchical Navigable Small World — approximate nearest neighbor search | `idx_document_chunks_embedding` — fast vector search at scale |
| **Text Chunking** | Splitting documents into overlapping segments for better retrieval | `chunk_text()` — 500-char chunks with 50-char overlap |
| **Multi-Tenancy** | Single codebase serving multiple isolated clients | Each bot has unique `bot_id`, separate config, separate data |
| **JWT (JSON Web Token)** | Compact, URL-safe token format for claims transfer | `auth_login()` — generates tokens with bot_id, iat, exp, jti |
| **HS256 (HMAC-SHA256)** | Symmetric key algorithm for JWT signing | `jwt.encode()` / `jwt.decode()` with JWT_SECRET |
| **bcrypt Salt Rounds** | Adaptive cryptographic hashing with cost factor | `bcrypt.gensalt()` — password storage |
| **Prompt Injection (RAG)** | Injecting retrieved context into AI system prompt | `/api/chat` — appends `RELEVANT BUSINESS INFORMATION` context |
| **Fallback Chain** | Graceful degradation when primary service fails | Supabase → Local JSON for every database operation |

### 4.11 💼 Business & Sales Technologies

| Tool | Purpose | Cost |
|------|---------|------|
| **OpenRouter** | AI provider (chat + embeddings) | ~$0.01/100 conversations |
| **Supabase** | Database (optional) | Free tier available |
| **Resend.com** | Email notifications | Free tier (100 emails/day) |
| **Fiverr** | International client acquisition | 20% commission |
| **Upwork** | International client acquisition | Free to join |
| **Google Maps** | Local client discovery | Free |
| **WhatsApp** | Client communication & sales | Free |
| **Loom** | Demo video recording | Free |

---

## 5. 🔌 API ENDPOINTS REFERENCE

### Chat & Business Endpoints
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/chat` | POST | Rate-limited (30/min) | Send message to AI chatbot, returns AI reply |
| `/api/health` | GET | None | Server health check, returns DB status |
| `/api/widget-config` | GET | None | Get bot config for embed widget (name, emoji, color, greeting) |

### Authentication Endpoints
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/login` | POST | None | Login with botId + password, returns JWT token |
| `/api/auth/check` | POST | None | Check admin/master password |
| `/api/client/change-password` | POST | JWT | Change password for authenticated client |

### Lead & Appointment Endpoints
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/leads` | POST | None | Save a lead (name + phone + message + bot) |
| `/api/leads` | GET | JWT | Get all leads for a bot |
| `/api/appointments` | POST | None | Book an appointment |
| `/api/appointments` | GET | JWT | Get all appointments for a bot |
| `/api/chat-logs` | POST | None | Log a chat message |

### Settings Endpoints
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/settings` | GET | JWT | Get bot settings (name, emoji, color, prompt, etc.) |
| `/api/settings` | POST | JWT | Update bot settings |

### Admin Endpoints
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/admin/create-client` | POST | Super Admin Key | Create new client bot with password |

### RAG Document Endpoints
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/documents/upload` | POST | JWT | Upload PDF or paste text for RAG processing |
| `/api/documents/analyze` | POST | JWT | Re-analyze an already-uploaded document |
| `/api/documents/apply-extraction` | POST | JWT | Accept/reject AI-extracted data |
| `/api/documents` | GET | JWT | List all uploaded documents for a bot |
| `/api/documents/preview` | GET | JWT | Preview document text content |
| `/api/documents/<doc_id>` | DELETE | JWT | Delete a document and its chunks |

### Static File Routes
| Route | Description |
|-------|-------------|
| `/` | Agency marketing website |
| `/chat/<bot_id>` | Standalone chat page |
| `/dashboard/<bot_id>` | Admin dashboard |
| `/<filename>` | Any file in public/ directory |

---

## 6. 🧠 RAG SYSTEM (RETRIEVAL-AUGMENTED GENERATION) — DETAILED

### What It Does
The RAG system allows chatbots to **learn from uploaded business documents** (PDFs or pasted text) and answer questions based on that information.

### Complete Processing Pipeline

```
Document Upload
      ↓
[1] Text Extraction (PyPDF2 for PDFs, direct for text)
      ↓
[2] Text Chunking (chunk_text function)
    • 500 chars per chunk
    • 50 char overlap between chunks
    • Smart sentence-boundary detection
      ↓
[3] Embedding Generation (get_embedding function)
    • Model: perplexity/pplx-embed-v1-0.6b
    • Output: 1536-dimension vector
    • Via OpenRouter API
      ↓
[4] Store Chunks (store_document_chunks function)
    • Option A: Supabase document_chunks table (VECTOR column)
    • Option B: Local JSON file (document_chunks_{bot_id}.json)
      ↓
[5] AI Document Analysis (analyze_document_with_ai function)
    • Uses Gemini 2.5 Flash
    • Extracts: services, FAQs, policies, hours, greeting
    • Returns structured JSON
      ↓
[6] Store Metadata (store_document_metadata function)
    • Stores extraction summary
    • Tracks source name, type, chunk count
      ↓
[7] Query Time — User asks a question
    • Generate embedding of user's question
    • Search vector DB via cosine similarity
    • Threshold: 0.75 (configurable)
    • Top-K: 3 results
    • Inject relevant chunks into system prompt
      ↓
[8] AI answers with document context
```

### Vector Search Implementation

**Supabase (Production):**
- Uses pgvector extension with VECTOR(1536) column
- HNSW index for fast approximate nearest neighbor search
- `match_documents()` PostgreSQL function for cosine similarity
- Parameters: `m = 16`, `ef_construction = 200`

**Local JSON (Development):**
- Brute-force cosine similarity calculation
- Custom `cosine_similarity()` function
- Filters by threshold, sorts by similarity, returns top-K

### Document Auto-Extraction

When a document is uploaded, the AI (Gemini 2.5 Flash) analyzes it and extracts:

```json
{
  "detected_type": "restaurant_menu | clinic_services | policy_document | general_info",
  "extracted_services": [
    { "name": "Service Name", "price": "PKR 500" }
  ],
  "extracted_faqs": [
    { "q": "Question", "a": "Answer" }
  ],
  "extracted_policies": [
    "Policy statement 1"
  ],
  "extracted_hours": "9 AM to 8 PM",
  "confidence": 0.85,
  "suggested_greeting": "Welcome to our clinic!"
}
```

---

## 7. 🔐 SECURITY & AUTHENTICATION

### Security Layers

| Layer | Implementation | Detail |
|-------|---------------|--------|
| **Input Validation** | `validate_field_lengths()` | All fields have max character limits (e.g., name: 100, message: 2000) |
| **Bot ID Sanitization** | `sanitize_bot_id()` | Only allows `[a-zA-Z0-9\-]` — prevents injection |
| **CORS** | Flask-CORS | Restricted to `https://overarc.co` and `http://localhost:5000` |
| **Rate Limiting** | Flask-Limiter | 30 requests/minute/IP on `/api/chat` |
| **JWT Authentication** | PyJWT | 24-hour expiry tokens, required for dashboard APIs |
| **Password Hashing** | bcrypt | All stored passwords have bcrypt salt rounds |
| **Password Strength** | Custom validator | Min 8 chars, must contain number, not in common passwords list (20+ blacklisted) |
| **Super Admin Key** | Custom header | `X-Admin-Key` required for client creation |
| **Error Handling** | Global handlers | 404, 405, 429, 500, unhandled exceptions all handled |

### Authentication Flow

```
Client Dashboard Login
      ↓
[1] User enters botId + password
[2] Server loads business config from DB
[3] Server verifies password against bcrypt hash
[4] Server generates JWT with:
    • bot_id, iat, exp (24h), jti (random)
[5] Client stores JWT in browser
[6] All subsequent API calls include:
    Authorization: Bearer <token>
[7] Server verifies JWT signature + expiry + bot_id match
```

### Common Passwords Blacklist
The system checks against 20+ common passwords including: `123456`, `password`, `admin`, `qwerty`, `letmein`, `dragon`, `baseball`, etc.

---

## 8. 🗄️ DATABASE ARCHITECTURE

### Option 1: Supabase PostgreSQL (Production)

**Core Schema** (`schema.sql`):
```sql
-- Multi-tenant business configs
businesses (id PK, name, industry, emoji, color, dark_color, whatsapp,
           greeting, system_prompt, faqs JSONB, services JSONB,
           working_hours, location, created_at)

-- Captured leads
leads (id PK, bot FK→businesses, business, name, phone, topic, timestamp)

-- Appointment bookings
appointments (id PK, bot FK→businesses, customer_name, customer_phone,
             service, preferred_date, preferred_time, status, timestamp)

-- Chat conversation logs
chat_logs (id PK, bot FK→businesses, session_id, role, content, timestamp)
```

**RAG Schema** (`supabase_migration.sql`):
```sql
-- Document chunks with vector embeddings
document_chunks (id UUID PK, bot_id TEXT, content TEXT,
                embedding VECTOR(1536), source_name TEXT, created_at)
-- HNSW index: idx_document_chunks_embedding
-- Function: match_documents(query_embedding, match_bot_id, match_threshold, match_count)

-- Document metadata
documents (id UUID PK, bot_id TEXT, source_name TEXT, source_type TEXT,
          chunk_count INT, extraction_summary JSONB, created_at)
```

### Option 2: Local JSON Files (Development)

| File | Purpose |
|------|---------|
| `businesses.json` | All bot configurations (3 demo bots included) |
| `leads.json` | Captured leads with bot, name, phone, topic |
| `appointments.json` | Booked appointments with status tracking |
| `chat_logs.json` | Full chat history per session |
| `document_chunks_{bot_id}.json` | RAG chunks with embeddings per bot |
| `documents_{bot_id}.json` | Document metadata per bot |

---

## 9. 💼 BUSINESS MODEL

### Pricing Tiers

| Tier | Price (USD) | Price (PKR) | Features |
|------|-------------|-------------|----------|
| 🟢 **Starter** | $150 | PKR 42,000 | 24/7 FAQ bot + lead capture + admin dashboard |
| 🔵 **Pro** | $250 | PKR 70,000 | Everything + appointment booking + website embed code |
| 🔴 **Premium** | $400 | PKR 112,000 | Everything + custom branding + 6 months support |
| 💎 **Monthly** | $30/mo | PKR 8,400/mo | Hosting + updates + support (recurring) |

### Revenue Targets

| Metric | Target |
|--------|--------|
| Time to build per client | 3 days |
| Minimum price | $150 |
| Month 1 goal | 2 clients = $300 |
| Month 3 goal | 5 clients + 3 retainers = $1,250+/month |
| Messages per week | 20 local + 10 Fiverr proposals |
| Follow-ups per lead | Max 2 |

### Client Acquisition Channels
1. **Local (Pakistan)** — WhatsApp outreach to Mingora/Swat businesses
2. **Fiverr** — Gig: "I will build an AI chatbot for your business..."
3. **Upwork** — Profile: "AI Chatbot Developer | 3-Day Delivery"
4. **Google Maps** — Find business numbers
5. **Physical walk-ins** — Show demo on phone

---

## 10. ⚙️ TECHNICAL DETAILS

### Tech Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Backend** | Python Flask | HTTP server + API endpoints |
| **Frontend** | HTML + CSS + JavaScript | Chat UI, Dashboard, Marketing Site |
| **AI Provider** | OpenRouter API | Access to Gemini 2.5 Flash + Embedding models |
| **AI Model** | google/gemini-2.5-flash | Default chat model (swap to GPT-4, Claude, etc.) |
| **Embedding Model** | perplexity/pplx-embed-v1-0.6b | 1536-dim vector embeddings |
| **Database (Prod)** | Supabase PostgreSQL + pgvector | Multi-tenant + vector search |
| **Database (Dev)** | Local JSON files | Zero-config fallback |
| **Auth** | JWT (PyJWT) + bcrypt | Secure token-based auth |
| **Rate Limiting** | Flask-Limiter | 30 req/min/IP |
| **Email** | Resend.com API | Lead & booking notifications |
| **PDF** | PyPDF2 | Document text extraction |

### Python Dependencies
```
flask          → Web framework
requests       → HTTP client for OpenRouter API
python-dotenv  → .env file loading
flask-cors     → CORS headers
pyjwt          → JWT token generation
bcrypt         → Password hashing
flask-limiter  → Rate limiting
openai         → OpenAI SDK (utility)
pypdf2         → PDF text extraction
```

### 3 Demo Bot Configurations

| Field | Clinic (clinic) | Real Estate (realestate) | Restaurant (restaurant) |
|-------|-----------------|-------------------------|------------------------|
| Name | City Dental Clinic | Al-Noor Real Estate | Taste of Swat |
| Emoji | 🏥 | 🏡 | 🍽️ |
| Color | #10B981 | #A855F7 | #E8471C |
| Dark Color | #059669 | #7E22CE | #C2410C |
| WhatsApp | +923249116764 | +923249116764 | +923249116764 |
| Hours | Mon-Sat 9AM-8PM | 9AM-6PM | 12PM-12AM |
| Location | Mingora, Swat | Kanju, Swat | G.T. Road, Mingora |

---

## 11. 🔄 DATA FLOWS

### Lead Capture Flow
```
User sends message #2 → AI asks for name & phone
User provides name + phone → POST /api/leads
Lead saved to DB (Supabase or JSON)
Email notification sent via Resend (if configured)
Lead visible in admin dashboard
```

### Appointment Booking Flow
```
User asks to book → AI collects: service, date, time
User provides details → POST /api/appointments
Appointment saved with status: "pending"
Email notification sent via Resend
Appointment visible in admin dashboard
```

### Chat Flow
```
User opens chat page → GET /api/widget-config
Page renders with bot name, color, greeting
User sends message → POST /api/chat
System prompt built from business config
RAG context injected (if relevant documents exist)
AI responds via OpenRouter
Response displayed in chat
Chat log saved via POST /api/chat-logs
```

---

## 12. 📝 ENVIRONMENT VARIABLES

```env
# === REQUIRED ===
OPENROUTER_API_KEY=sk-or-v1-...    # OpenRouter API key
SUPER_ADMIN_KEY=<strong-random-key> # For creating clients via API
JWT_SECRET=<32-byte-hex-secret>    # JWT signing secret

# === OPTIONAL (leave blank for local JSON fallback) ===
SUPABASE_URL=                      # Supabase project URL
SUPABASE_KEY=                      # Supabase anon/service key
RESEND_API_KEY=                    # Resend.com API key for emails

# === OPTIONAL ===
ADMIN_PASSWORD=admin123            # Dashboard master password
```

---

## 13. 🚀 GETTING STARTED (5 Minutes)

```bash
# 1. Get API key from https://openrouter.ai/keys

# 2. Configure environment
#    Edit .env → Set OPENROUTER_API_KEY, SUPER_ADMIN_KEY, JWT_SECRET

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
venv\Scripts\python server.py

# 5. Open in browser
#    http://localhost:5000
```

---

## 14. 💡 KEY FILES SUMMARY

| File | Lines | Purpose |
|------|-------|---------|
| `server.py` | 2,078 | Complete Flask backend with all API endpoints |
| `businesses.json` | 143 | 3 demo bot configurations |
| `public/chat.html` | 476 | Standalone chat page with dark theme |
| `AI-chatbot.md` | 582 | Business blueprint & original spec |
| `HOW_TO_SELL_CLIENTS.md` | 224 | Step-by-step sales workflow |
| `refrence.md` | 746 | Industry best practices reference |
| `schema.sql` | 108 | Core database schema |
| `supabase_migration.sql` | 76 | RAG vector database migration |
| `requirements.txt` | 9 | Python dependencies |
| `.env` | 35 | Environment configuration |

---

## 15. 🎯 FUTURE ENHANCEMENTS

Based on the reference guide and industry best practices, potential future additions:

1. **Multi-Channel Support** — WhatsApp Business API, Instagram DM, Facebook Messenger
2. **Live Chat Handoff** — Human takeover when AI can't handle a query
3. **Voice AI** — ElevenLabs + Twilio for AI phone calls
4. **Analytics Dashboard** — Conversation metrics, conversion tracking
5. **Automation Workflows** — n8n/Make.com integration (Google Calendar, CRM sync)
6. **Multi-Agent System** — Separate agents for sales, support, booking
7. **Website Crawler** — Auto-import business info from existing websites
8. **Payment Integration** — Stripe/PayPal for in-chat payments
9. **Mobile Apps** — Native iOS/Android widgets
10. **User Memory** — Return user recognition with conversation history

---

## 16. 📈 PROJECT STATS

| Metric | Value |
|--------|-------|
| Backend Code | 2,078 lines (Python) |
| Chat Frontend | 476 lines (HTML/CSS/JS) |
| Total Documentation | ~1,700+ lines across 4 guide files |
| API Endpoints | 16+ |
| Database Tables | 6 (3 core + 3 RAG) |
| Demo Bots | 3 (clinic, real estate, restaurant) |
| AI Models Used | 2 (Gemini 2.5 Flash + pplx-embed-v1-0.6b) |
| Security Layers | 10+ |
| Language Support | English + Urdu (auto-detect) |

---

*Report generated for Overarc Agency | SmartBot v2.0 | May 2026*