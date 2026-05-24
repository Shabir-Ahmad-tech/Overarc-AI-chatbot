# 🚀 Overarc Agency — AI Chatbot Builder Toolkit (SmartBot)

## 🏢 Who We Are

**Overarc Agency** is an AI automation agency. We build custom AI chatbots for businesses that:
- Answer customer questions **24/7**
- Capture **leads** (name + phone numbers) automatically  
- Book **appointments** without human involvement
- Work on websites, WhatsApp, Instagram, and as standalone links
- Use **RAG (Retrieval-Augmented Generation)** to answer from uploaded business documents

---

## 📦 What's in this Toolkit?

This folder contains **our complete system** for building, managing, and selling AI chatbots to clients. Every file here is designed to help you deliver a premium product fast.

**Latest Version: 2.0** — Now includes:
- ✅ **RAG System** — Upload PDFs or paste text, AI auto-extracts services/FAQs/policies
- ✅ **JWT Authentication** — Secure per-client login for admin dashboards
- ✅ **Supabase PostgreSQL + pgvector** — Enterprise-grade database with vector search
- ✅ **Rate Limiting** — 30 requests/minute/IP on chat endpoint
- ✅ **Password Strength Validation** — No more weak passwords
- ✅ **Client Password Change** — Clients can change their own passwords
- ✅ **Super Admin** — Create new clients via API with strong password enforcement
- ✅ **Email Notifications** — Resend.com integration for lead & booking alerts
- ✅ **Comprehensive Security** — Input validation, CORS restriction, bcrypt password hashing, JWT tokens

---

## 🛠️ HOW TO SETUP (5 Minutes)

### STEP 1: Get a FREE AI API Key
We use **OpenRouter** (cheapest option — ~$0.01 per 100 conversations):

1. Go to **https://openrouter.ai/keys**
2. Sign up with Google (FREE)
3. Click **"Create Key"** — copy the key starting with `sk-or-v1-...`
4. Open the file **`.env`** and paste it here:
   ```
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   ```

### STEP 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Requirements installed:**
- `flask` — Web framework
- `requests` — HTTP client for OpenRouter API
- `python-dotenv` — Environment variable loading
- `flask-cors` — Cross-origin resource sharing
- `pyjwt` — JWT token generation/verification
- `bcrypt` — Password hashing
- `flask-limiter` — Rate limiting
- `openai` — OpenAI SDK (utility)
- `pypdf2` — PDF text extraction (for RAG document upload)

### STEP 3: Configure Environment
Open **`.env`** and set these values:

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | ✅ YES | Your OpenRouter API key |
| `SUPER_ADMIN_KEY` | ✅ YES | Strong random key for creating new clients |
| `JWT_SECRET` | ✅ YES | Secret for signing JWT tokens |
| `SUPABASE_URL` | ❌ No | Supabase project URL (optional, uses local JSON if blank) |
| `SUPABASE_KEY` | ❌ No | Supabase anon/service key |
| `RESEND_API_KEY` | ❌ No | Resend.com API key for email alerts |
| `ADMIN_PASSWORD` | ❌ No | Dashboard password (default: admin123) |

### STEP 4: Run the System
```bash
cd "d:\04_Coding_and_AI\05. Antigravity\Overarc-AI-chatbot"
venv\Scripts\python server.py
```

You'll see:
```
Starting Overarc Python Backend on port 5000...
Access the site at: http://localhost:5000
[SECURITY] Debug mode: OFF
[SECURITY] CORS restricted to: https://overarc.co, http://localhost:5000
[SECURITY] Rate limit on /api/chat: 30 requests/minute/IP
[SECURITY] JWT tokens expire after: 24 hours
[RAG] Embedding model: perplexity/pplx-embed-v1-0.6b (via OpenRouter)
```

### STEP 5: Open in Browser
Go to **http://localhost:5000** — you'll see your agency website!

---

## 👀 Your 3 Demo Bots (Show to Clients)

We've pre-built **3 demo bots** to showcase to potential clients:

| Bot ID | Business | Try It | Best For Showing To... |
|--------|----------|--------|----------------------|
| `clinic` | 🏥 City Dental Clinic | /chat/clinic | Clinics, Dentists, Doctors, Hospitals |
| `realestate` | 🏠 Al-Noor Real Estate | /chat/realestate | Real Estate Agents, Property Dealers |
| `restaurant` | 🍽️ Taste of Swat | /chat/restaurant | Restaurants, Cafes, Bakeries, Hotels |

---

## 🗺️ All Pages at a Glance

| Page | URL | Purpose |
|------|-----|---------|
| 🏠 **Agency Website** | http://localhost:5000/ | Your agency's marketing site — send clients here |
| 🎮 **Live Demo** | http://localhost:5000/smartbot-demo.html | Clients can try all 3 bots in one place |
| 💬 **Clinic Bot** | http://localhost:5000/chat/clinic | Standalone chat link — share on WhatsApp/Instagram |
| 💬 **Real Estate Bot** | http://localhost:5000/chat/realestate | Standalone chat link |
| 💬 **Restaurant Bot** | http://localhost:5000/chat/restaurant | Standalone chat link |
| 📊 **Admin Dashboard** | http://localhost:5000/dashboard/clinic | View captured leads + edit bot settings |
| 🔌 **Embed Code** | `<script src=".../widget.js?botId=clinic">` | Paste on any website to add chatbot |

> **Default Admin Password: `admin123`** (Change in `.env` file before going live!)

---

## 🔐 Authentication System

Each client bot now has **its own login credentials** with secure authentication:

### How It Works
1. Each bot in `businesses.json` has a `password_hash` field (bcrypt hashed)
2. Clients log in at their dashboard URL with their bot ID and password
3. Server returns a **JWT token** (valid for 24 hours)
4. All dashboard API calls require this token in the `Authorization: Bearer <token>` header

### Client Features
- **Login**: Authenticate with bot ID + password
- **Change Password**: Clients can update their own password from the dashboard
- **Token Management**: Tokens auto-expire after 24 hours

### Super Admin API
Create new clients programmatically via:
```
POST /api/admin/create-client
Headers: X-Admin-Key: <YOUR_SUPER_ADMIN_KEY>
Body: { "botId": "...", "businessName": "...", "password": "...", "email": "..." }
```

Password requirements: minimum 8 characters, must contain a number, cannot be a common password.

---

## 🧠 RAG System (Retrieval-Augmented Generation)

The biggest new feature! Your chatbots can now learn from uploaded business documents.

### What RAG Does
1. **Upload** a PDF document or paste text in the admin dashboard
2. The system **chunks** the text into segments (~500 chars each with 50 char overlap)
3. **Generates embeddings** using `perplexity/pplx-embed-v1-0.6b` via OpenRouter (1536-dimension vectors)
4. **Stores** chunks in Supabase `document_chunks` table with pgvector indexing OR local JSON files
5. **AI analyzes** the document to auto-extract: services, FAQs, business policies, working hours, greeting message
6. When a user asks a question, the system **searches** for the most relevant chunks using cosine similarity
7. **Injects** the relevant context into the AI's system prompt for accurate answers

### RAG Key Components
| Component | Description |
|-----------|-------------|
| `chunk_text()` | Splits text into overlapping segments with smart sentence-boundary detection |
| `get_embedding()` | Generates 1536-dim vectors via OpenRouter embeddings API |
| `search_relevant_chunks()` | Cosine similarity search with configurable threshold (default: 0.75) and top-k (default: 3) |
| `analyze_document_with_ai()` | Uses Gemini 2.5 Flash to extract structured business data from documents |
| `store_document_chunks()` | Persists chunks with embeddings to Supabase or local JSON |
| `match_documents()` | Supabase pgvector function for efficient HNSW-indexed similarity search |

### RAG API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/documents/upload` | POST | Upload PDF or paste text for RAG processing (JWT required) |
| `/api/documents/analyze` | POST | Re-analyze an already-uploaded document (JWT required) |
| `/api/documents/apply-extraction` | POST | Accept/reject AI-extracted services, FAQs, policies (JWT required) |
| `/api/documents` | GET | List all uploaded documents for a bot (JWT required) |
| `/api/documents/preview` | GET | Preview document text content (JWT required) |
| `/api/documents/<doc_id>` | DELETE | Delete a document and its chunks (JWT required) |

### Database Setup for RAG
Run the SQL in **`supabase_migration.sql`** in your Supabase SQL editor:
1. Enables `pgvector` extension
2. Creates `document_chunks` table with VECTOR(1536) column
3. Creates HNSW index for fast similarity search
4. Creates `match_documents()` function for cosine similarity queries
5. Creates `documents` metadata table

---

## 📊 API Endpoints Reference

### Chat & Business
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/chat` | POST | Rate-limited (30/min) | Send a message to the AI chatbot |
| `/api/health` | GET | None | Health check with database status |
| `/api/widget-config` | GET | None | Get widget configuration for embed |

### Authentication
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/auth/login` | POST | None | Login with bot ID + password, get JWT |
| `/api/auth/check` | POST | None | Check admin password |
| `/api/client/change-password` | POST | JWT | Change client password |

### Leads & Appointments
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/leads` | POST | None | Save a new lead (name + phone) |
| `/api/leads` | GET | JWT | Get all leads for a bot |
| `/api/appointments` | POST | None | Book an appointment |
| `/api/appointments` | GET | JWT | Get all appointments for a bot |
| `/api/chat-logs` | POST | None | Log a chat message |

### Settings & Admin
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/settings` | GET | JWT | Get bot settings |
| `/api/settings` | POST | JWT | Update bot settings |
| `/api/admin/create-client` | POST | Super Admin Key | Create a new client bot |

---

## ➕ How to Add a NEW Client to Your Agency

### Method 1: Super Admin API (Recommended — Secure)
```bash
curl -X POST http://localhost:5000/api/admin/create-client \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: YOUR_SUPER_ADMIN_KEY" \
  -d '{
    "botId": "my-client",
    "businessName": "My Client Business",
    "password": "StrongPass123",
    "email": "client@email.com",
    "emoji": "🏪",
    "whatsapp": "+923001234567"
  }'
```

### Method 2: Edit JSON (Manual — 2 Minutes)
1. Open **`businesses.json`** 
2. Copy one existing entry and paste it
3. Change the `"id"` to something unique (e.g., `"my-client"`)
4. Add a bcrypt `password_hash` field
5. Change all the business info (name, services, FAQs, etc.)
6. Save the file
7. Restart the server (Ctrl+C then `python server.py` again)

### Method 3: Admin Dashboard (No Coding)
1. Go to `http://localhost:5000/dashboard/YOUR_CLIENT_ID`
2. Enter password: `admin123`
3. Go to "Customize Bot" tab
4. Edit everything: name, greeting, brand color, AI instructions, FAQs, services
5. Click "Save" — bot is updated instantly!

### Method 4: Upload Documents (RAG — Smartest)
1. Go to the admin dashboard for your client
2. Click "Documents" tab
3. Upload a PDF with their services/FAQs/policies
4. AI auto-extracts structured data
5. Review and accept the extraction
6. Done! The bot now answers from the document

---

## 💰 HOW TO SELL BOTS & MAKE MONEY (Agency Model)

### Our Pricing Tiers (Already on the Agency Website):

| Package | PKR | USD | What Client Gets |
|---------|-----|-----|------------------|
| 🟢 **Starter** | PKR 42,000 | **$150** | 24/7 FAQ bot + lead capture + admin panel |
| 🔵 **Pro** | PKR 70,000 | **$250** | Everything + appointment booking + embed code |
| 🔴 **Premium** | PKR 112,000 | **$400** | Everything + custom branding + 6 months support |
| 💎 **Monthly** | PKR 8,400 | **$30/mo** | Hosting + updates + support (passive income) |

> **New Value Proposition with RAG:** You can now offer "Upload your business documents and get an instant AI assistant" — this is your premium upsell! Clients can upload their menu, price list, policy documents, or brochure and the AI instantly learns everything.

### 🎯 Client Outreach Scripts

#### 📱 WhatsApp — Local Pakistani Businesses (Mingora, Swat, KPK):

> *"Assalam-o-Alaikum! 🤝*  
> *Main **Overarc Agency** se AI chatbots banata hoon.*  
> *Ye chatbot aapki business ke liye 24/7 customers ke questions answer karta hai, leads capture karta hai, aur appointments book karta hai.*  
> *Example: Agar koi raat 2 baje aapke clinic ke baare mein poochta hai, to AI jawab dega aur appointment book kar dega — aap so rahe hote hain!*  
> *Main 3 din mein bana kar deta hoon. Pehle demo FREE hai. Interested hai?*  

#### 🌍 Fiverr Gig Title:
> *"I will build an AI chatbot for your business that captures leads and books appointments"*

#### 🌍 Upwork Profile Headline:
> *"AI Chatbot Developer | Lead Capture + Appointment Booking Bots | 3-Day Delivery"*

### 📍 Where to Find Local Clients:
- **Google Maps** → Search "clinics in Mingora" → Get their WhatsApp numbers
- **Facebook Business Pages** → Local businesses in Swat/KPK
- **Physical Walk-ins** → Show demo on your phone (most powerful!)

---

## 📤 How to Deliver to a Client

After building, send them this message:

```
Hi [Client Name],

Your AI assistant from Overarc Agency is ready! 🚀

Here's your delivery package:

🔗 STANDALONE LINK (share on WhatsApp/Instagram):
   http://localhost:5000/chat/[their-botId]

📊 ADMIN DASHBOARD (manage leads & settings):
   http://localhost:5000/dashboard/[their-botId]
   Login with your bot ID and password

💻 EMBED CODE (for your website):
   <script src="http://localhost:5000/widget.js?botId=[their-botId]"></script>

📄 DOCUMENT UPLOAD (to train your bot):
   Upload PDFs or paste text in the dashboard → Documents tab
   The AI will learn from your business documents instantly!

Please test it and let me know if you want any changes.
Once approved, kindly send the remaining payment.

Thank you for choosing Overarc Agency! 🙏
```

### 🔁 After Delivery — Get Recurring Income:
Immediately ask:
> *"Would you like me to handle hosting & updates for just PKR 8,400/month? That keeps your bot running 24/7 and I handle everything."*

---

## 🗂️ Files Overview (Agency Toolkit)

| File | What It's For |
|------|--------------|
| `server.py` | ⚙️ Backend engine — runs all APIs (2078 lines) |
| `.env` | 🔑 Store your API keys here (SECRET!) |
| `businesses.json` | 📋 All your clients' bot configurations |
| `leads.json` | 📩 Captured customer leads (auto-saved, IGNORED by git) |
| `appointments.json` | 📅 Booked appointments (auto-saved) |
| `chat_logs.json` | 💬 Chat conversation logs (auto-saved) |
| `document_chunks_*.json` | 📄 RAG document chunks per bot (auto-saved) |
| `documents_*.json` | 📚 Document metadata per bot (auto-saved) |
| `requirements.txt` | 📦 Python dependencies list |
| `schema.sql` | 🗄️ Core database schema (Supabase) |
| `supabase_migration.sql` | 🗄️ RAG database schema (Supabase + pgvector) |
| `public/index.html` | 🌐 Your agency marketing website |
| `public/smartbot-demo.html` | 🎮 Live demo for client pitches |
| `public/chat.html` | 💬 Standalone chat page (476 lines) |
| `public/widget.js` | 🔌 1-line embed widget for websites |
| `public/smartbot-dashboard.html` | 📊 Admin panel for clients |
| `public/Icons/` | 🖼️ Static assets & brand graphics |
| `AI-chatbot.md` | 📘 Business blueprint & design guidelines (582 lines) |
| `HOW_TO_SELL_CLIENTS.md` | 💼 Complete client workflow & sales guide (224 lines) |
| `refrence.md` | 📚 Industry reference & best practices (746 lines) |

---

## 🔒 Security Features

| Feature | Description |
|---------|-------------|
| **CORS Restriction** | Only allows requests from `https://overarc.co` and `http://localhost:5000` |
| **Rate Limiting** | 30 requests per minute per IP on `/api/chat` |
| **Input Validation** | All fields have maximum character limits; SQL injection prevented |
| **Bot ID Sanitization** | Only alphanumeric and hyphens allowed |
| **JWT Authentication** | 24-hour expiry tokens, required for all dashboard API calls |
| **bcrypt Password Hashing** | All passwords stored as bcrypt hashes |
| **Password Strength** | Minimum 8 chars, must include a number, common password check |
| **Super Admin Authentication** | Requires `X-Admin-Key` header for client creation |
| **Error Handling** | Global error handlers for 404, 405, 429, 500 |
| **Debug Mode** | Explicitly disabled in production |

---

## 🗄️ Database Architecture

### Option 1: Supabase (Production — Recommended)
The full schema is in **`schema.sql`** with these tables:
- **businesses** — Multi-tenant bot configurations (id, name, system_prompt, faqs, services, etc.)
- **leads** — Captured customer leads (bot, name, phone, topic, timestamp)
- **appointments** — Booked appointments (bot, customer_name, phone, service, date, time, status)
- **chat_logs** — Chat conversation history (bot, session_id, role, content, timestamp)

### Option 2: Local JSON Files (Development — No Setup)
Auto-created when Supabase is not configured:
- `businesses.json` — Business configurations
- `leads.json` — Captured leads
- `appointments.json` — Booked appointments
- `chat_logs.json` — Chat history
- `document_chunks_{bot_id}.json` — RAG document chunks per bot
- `documents_{bot_id}.json` — Document metadata per bot

### RAG Vector Database
The **`supabase_migration.sql`** adds:
- `document_chunks` table with `VECTOR(1536)` column for embeddings
- HNSW index for fast similarity search
- `match_documents()` function for cosine similarity queries
- `documents` metadata table

---

## 🧪 Quick Start Recap for Overarc Agency

```
STEP 1:  Get API key from https://openrouter.ai/keys
STEP 2:  Paste it in .env file + set SUPER_ADMIN_KEY + JWT_SECRET
STEP 3:  Install: pip install -r requirements.txt
STEP 4:  Run: venv\Scripts\python server.py
STEP 5:  Open http://localhost:5000
STEP 6:  Show 3 demo bots to clients
STEP 7:  Close deals at $150-$400 per bot
STEP 8:  Collect $30/month recurring from each client 💰
```

---

## ❓ FAQ

**Q: How much does it cost ME to run this?**
A: Almost nothing! AI costs ~$0.01 per 100 conversations via OpenRouter. If you get 1,000 conversations/month across all clients, that's only $0.10.

**Q: What if my client doesn't have a website?**
A: No problem. Give them the standalone link (e.g., `/chat/clinic`) — they share it on WhatsApp/Instagram.

**Q: Can I customize the AI model?**
A: Yes. In `server.py`, change `google/gemini-2.5-flash` to any OpenRouter-supported model (GPT-4, Claude, etc.)

**Q: How do I deploy this for real clients?**
A: For now it runs on your computer. When you're ready for live deployment, put it on **Render**, **Railway**, or **Fly.io** (free hosting options available).

**Q: Can I change the admin password?**
A: Yes. Open `.env` and change `ADMIN_PASSWORD=admin123` to your own password.

**Q: What files should NOT be committed to Git?**
A: `.env`, `leads.json`, `venv/`, `__pycache__/`, `*.pyc`, `*.db` — all covered in `.gitignore`

**Q: How does the RAG system work?**
A: The system converts business documents (PDFs or text) into vector embeddings, stores them in a vector database (Supabase pgvector or local JSON), and when a user asks a question, it finds the most relevant document chunks and injects them into the AI's system prompt for accurate, context-aware answers.

---

*Built by **Overarc Agency** | AI Chatbot Builders | Version 2.0 | May 2026*