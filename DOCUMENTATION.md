# Overarc SmartBot — Complete Documentation

> Version 1.0 | Updated: May 2026 | Built by Overarc Agency, Mingora, Swat, KPK, Pakistan

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Complete API Reference](#2-complete-api-reference)
3. [Setup Guide](#3-setup-guide)
4. [Client Onboarding SOP](#4-client-onboarding-sop)
5. [Troubleshooting Guide](#5-troubleshooting-guide)
6. [Business Operations Guide](#6-business-operations-guide)

---

## 1. System Overview

### What Overarc SmartBot Is

Overarc SmartBot is a **multi-tenant AI chatbot SaaS platform** that allows a single operator (Overarc Agency) to deploy customized AI chatbots for multiple clients. Each client gets:

- A standalone chat page (sharable on WhatsApp/Instagram)
- An embeddable widget (paste one line on their website)
- A private admin dashboard (manage leads, settings, knowledge base)
- A RAG-powered AI brain trained on their business documents

### Architecture

```
Client Website                     Overarc Backend (Flask)
  <script widget.js>   ──────────▶   /api/chat          (AI response)
                                      /api/leads         (lead capture)
                                      /api/appointments  (booking)
                                      /api/settings      (config)
                                      /api/documents     (RAG upload)
                                          │
                              ┌───────────┴────────────┐
                              ▼                        ▼
                          OpenRouter API           Supabase DB
                       (Gemini 2.5 Flash +       (PostgreSQL +
                        pplx-embed-v1-0.6b)       pgvector RAG)
                              │                        │
                              ▼                        ▼
                         AI Response              Leads / Appts /
                          (streamed)              Document Chunks
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python + Flask |
| AI | Gemini 2.5 Flash via OpenRouter |
| Embeddings | perplexity/pplx-embed-v1-0.6b via OpenRouter |
| Database | Supabase (PostgreSQL + pgvector) |
| Auth | JWT (HS256, 24h expiry) + bcrypt passwords |
| Email | Resend.com API |
| Deployment | Render.com (gunicorn) |
| Frontend | Vanilla HTML/CSS/JS |

### Demo Bots

| Bot ID | Business | Color |
|--------|----------|-------|
| `clinic` | City Dental Clinic | #10B981 (green) |
| `realestate` | Al-Noor Real Estate | #A855F7 (purple) |
| `restaurant` | Taste of Swat | #EF4444 (red) |

---

## 2. Complete API Reference

### Base URL
- Local: `http://localhost:5000`
- Production: `https://overarc.co`

### Authentication Types

| Type | Header | Used For |
|------|--------|----------|
| None | — | Public endpoints |
| JWT Bearer | `Authorization: Bearer <token>` | Client endpoints |
| Admin Key | `X-Admin-Key: <your_key>` | Admin-only endpoints |

---

### `GET /api/health`

**Auth:** None  
**Description:** Health check endpoint. Also used for keep-alive pings.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2026-05-24T10:00:00",
  "database": "supabase"
}
```

---

### `POST /api/auth/login`

**Auth:** None  
**Description:** Authenticate a client and get a JWT token.

**Request Body:**
```json
{
  "botId": "clinic",
  "password": "your_password"
}
```

**Response (200):**
```json
{
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "bot_id": "clinic",
  "expires_at": "2026-05-25T10:00:00+00:00"
}
```

**Errors:** `401` Invalid credentials · `400` Missing fields

**Example curl:**
```bash
curl -X POST https://overarc.co/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"botId":"clinic","password":"yourpassword123"}'
```

---

### `POST /api/chat`

**Auth:** None (rate-limited: 30/min/IP)  
**Description:** Send a message and receive an AI response.

**Request Body:**
```json
{
  "bot": "clinic",
  "message": "What are your working hours?",
  "history": [
    {"role": "user", "content": "Hello"},
    {"role": "assistant", "content": "Hi! How can I help?"}
  ]
}
```

**Response:**
```json
{ "reply": "We are open Monday to Saturday, 9 AM to 8 PM." }
```

**Subscription States:**
- `active` → normal AI response
- `trial` (within 14 days) → normal AI response
- `trial` (expired) → `"This service is currently unavailable."`
- `suspended` → `"This service is currently unavailable."`

---

### `POST /api/leads`

**Auth:** None  
**Description:** Save a captured lead (called by the chatbot widget).

**Request Body:**
```json
{
  "bot": "clinic",
  "name": "Ahmed Khan",
  "phone": "+923001234567",
  "message": "Interested in teeth whitening"
}
```

**Response:** `{"success": true}`

---

### `GET /api/leads`

**Auth:** JWT Bearer  
**Description:** Get all leads for the authenticated bot.

**Query Params:** `?botId=clinic`

**Response:** Array of lead objects.

**Example curl:**
```bash
curl https://overarc.co/api/leads?botId=clinic \
  -H "Authorization: Bearer <your_token>"
```

---

### `GET /api/leads/export`

**Auth:** JWT Bearer  
**Description:** Download all leads as a CSV file.

**Query Params:** `?botId=clinic`

**Response:** `text/csv` file download  
**Filename:** `leads_clinic_2026-05-24.csv`

---

### `POST /api/appointments`

**Auth:** None  
**Description:** Save an appointment booking.

**Request Body:**
```json
{
  "bot": "clinic",
  "customer_name": "Sara Ahmed",
  "customer_phone": "+923009876543",
  "service": "Teeth Cleaning",
  "preferred_date": "2026-05-28",
  "preferred_time": "11:00 AM"
}
```

---

### `GET /api/appointments`

**Auth:** JWT Bearer · **Query:** `?botId=clinic`

---

### `GET /api/appointments/export`

**Auth:** JWT Bearer · **Query:** `?botId=clinic`  
Downloads appointments as CSV.

---

### `GET /api/settings`

**Auth:** JWT Bearer · **Query:** `?botId=clinic`  
Returns full business config (without password_hash).

---

### `POST /api/settings`

**Auth:** JWT Bearer  
**Description:** Update bot configuration.

**Request Body:** (all fields optional except `id`)
```json
{
  "id": "clinic",
  "name": "City Dental Clinic",
  "greeting": "Hello! Welcome...",
  "system_prompt": "You are...",
  "color": "#10B981",
  "working_hours": "9 AM - 8 PM",
  "location": "Mingora, Swat",
  "whatsapp": "+923249116764",
  "faqs": [{"q": "What are your hours?", "a": "9-8 PM"}],
  "services": [{"name": "Checkup", "price": "PKR 500"}]
}
```

---

### `POST /api/documents/upload`

**Auth:** JWT Bearer  
**Description:** Upload a PDF or paste text for RAG processing.

**Request:** `multipart/form-data`  
- `file` — PDF file (optional)  
- `text` — Raw text string (optional)  
One of the two must be provided.

**Response:**
```json
{
  "success": true,
  "chunks_stored": 14,
  "summary_text": "Found 8 services, 5 FAQs — all saved!",
  "extraction": { "detected_type": "clinic_services", "extracted_services": [...], "confidence": 0.9 },
  "pending_approval": true
}
```

---

### `GET /api/documents`

**Auth:** JWT Bearer  
Returns list of all uploaded documents for the bot.

---

### `DELETE /api/documents/<doc_id>`

**Auth:** JWT Bearer  
Deletes a document and all its vector chunks.

---

### `GET /api/documents/preview`

**Auth:** JWT Bearer · **Query:** `?source_name=filename.pdf`  
Returns a 3000-character preview of the extracted text.

---

### `POST /api/documents/apply-extraction`

**Auth:** JWT Bearer  
**Description:** Accept/reject AI-extracted data.

```json
{
  "action": "accept",
  "extraction": { "extracted_services": [...], "extracted_faqs": [...] }
}
```

`action` values: `"accept"` (apply all) · `"review"` (return data) · `"skip"` (do nothing)

---

### `POST /api/crawl`

**Auth:** JWT Bearer  
**Description:** Crawl a website URL and auto-extract business info.

```json
{ "url": "https://yourbusiness.com" }
```

---

### `POST /api/admin/create-client`

**Auth:** `X-Admin-Key` header  
**Description:** Create a new bot/client.

```json
{
  "botId": "new-business",
  "businessName": "New Business Co",
  "password": "Pass1234!",
  "email": "owner@business.com",
  "whatsapp": "+923001234567",
  "color": "#6366f1",
  "working_hours": "9AM-6PM",
  "location": "Mingora",
  "services": [{"name": "Consulting", "price": "PKR 5000"}],
  "faqs": [{"q": "Hours?", "a": "9-6 PM"}]
}
```

**Response:**
```json
{
  "success": true,
  "botId": "new-business",
  "loginUrl": "https://overarc.co/dashboard/new-business"
}
```

**Example curl:**
```bash
curl -X POST https://overarc.co/api/admin/create-client \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: YOUR_SUPER_ADMIN_KEY" \
  -d '{"botId":"test-biz","businessName":"Test Business","password":"Test1234","email":"test@test.com"}'
```

---

### `POST /api/admin/set-status`

**Auth:** `X-Admin-Key` header  
**Description:** Set subscription status for a bot.

```json
{ "botId": "clinic", "status": "suspended" }
```

`status` values: `"active"` · `"trial"` · `"suspended"`

---

### `POST /api/client/change-password`

**Auth:** JWT Bearer  
**Description:** Change the authenticated client's dashboard password.

```json
{
  "currentPassword": "OldPass123",
  "newPassword": "NewPass456"
}
```

---

## 3. Setup Guide

### Step 1: Get OpenRouter API Key

1. Go to [openrouter.ai](https://openrouter.ai)
2. Click "Sign In" → Create account
3. Go to **Settings → API Keys**
4. Click **"Create Key"** → Copy the key
5. Add credits (start with $5)

---

### Step 2: Set Up Supabase

1. Go to [supabase.com](https://supabase.com) → **New Project**
2. Choose a region closest to Pakistan (Frankfurt is usually good)
3. Wait for the project to initialize (~2 minutes)
4. Go to **Settings → API** → Copy:
   - **Project URL** → this is your `SUPABASE_URL`
   - **anon public** key → this is your `SUPABASE_KEY`
5. Go to **SQL Editor** → Click **"New query"**
6. Paste the contents of `schema.sql` → **Run**
7. Paste the contents of `supabase_migration.sql` → **Run**

---

### Step 3: Configure .env File

Copy `.env.example` to `.env` and fill in all values:

```bash
cp .env.example .env
```

Generate a JWT secret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Generate a Super Admin Key:
```bash
python -c "import secrets; print(secrets.token_hex(24))"
```

---

### Step 4: Install Dependencies & Run Locally

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python server.py
```

Open `http://localhost:5000` in your browser.

---

### Step 5: Deploy to Render

1. Push your code to GitHub (make sure `.env` is in `.gitignore`)
2. Go to [render.com](https://render.com) → **New → Web Service**
3. Connect your GitHub repo
4. Render will auto-detect the `render.yaml` configuration
5. Add all environment variables in the Render dashboard under **Environment**:
   - `OPENROUTER_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `RESEND_API_KEY`
   - `JWT_SECRET`
   - `SUPER_ADMIN_KEY`
   - `ADMIN_PASSWORD`
6. Click **Deploy**

---

### Step 6: Connect Custom Domain (overarc.co)

1. In Render dashboard → go to your service → **Settings → Custom Domains**
2. Click **"Add Custom Domain"** → enter `overarc.co`
3. Copy the CNAME value Render gives you
4. In your domain registrar (Namecheap/GoDaddy/etc.):
   - Add a CNAME record: `@` → the value Render gave you
   - Or: `www` → the value Render gave you
5. Wait 5-30 minutes for DNS propagation
6. Update CORS in `server.py` if you add subdomains

---

## 4. Client Onboarding SOP

### Step-by-Step Process for a New Paying Client

#### 1. Collect Client Info

Send this Google Form or WhatsApp message to collect:

```
Please send me the following info for your chatbot setup:

1. Business Name:
2. Services & Prices (list up to 10):
3. Top 5-10 FAQs your customers ask:
4. Working Hours:
5. Location / Address:
6. WhatsApp Number:
7. Email for lead notifications:
8. Brand color (send hex code or just say your logo color):
```

---

#### 2. Create the Client Bot

**Option A — Use the Onboarding Page (Easiest):**
1. Open `https://overarc.co/onboarding`
2. Fill in all fields
3. Enter your SUPER_ADMIN_KEY
4. Click "Create & Deploy Bot"
5. Screenshot the delivery card

**Option B — Use curl (Fastest):**
```bash
curl -X POST https://overarc.co/api/admin/create-client \
  -H "Content-Type: application/json" \
  -H "X-Admin-Key: YOUR_KEY_HERE" \
  -d '{
    "botId": "business-name",
    "businessName": "Business Name",
    "password": "StrongPass1",
    "email": "client@email.com",
    "whatsapp": "+923001234567",
    "color": "#10B981",
    "working_hours": "9AM-8PM Mon-Sat",
    "location": "Mingora, Swat",
    "services": [{"name": "Service 1", "price": "PKR 500"}],
    "faqs": [{"q": "Are you open on Sundays?", "a": "No, we are closed on Sundays."}]
  }'
```

---

#### 3. Send Delivery Message to Client

Copy this template and fill in the blanks:

```
Assalam-o-Alaikum [Client Name]! 🎉

Your AI chatbot is ready! Here are your 3 links:

1️⃣ CHAT LINK (share on WhatsApp/Instagram):
   https://overarc.co/chat/[BOT-ID]
   ➡️ Customers can chat with your AI 24/7

2️⃣ DASHBOARD (view leads & appointments):
   https://overarc.co/dashboard/[BOT-ID]
   Password: [THEIR-PASSWORD]
   ➡️ Login to see all captured leads

3️⃣ WEBSITE EMBED CODE:
   <script src="https://overarc.co/widget.js?botId=[BOT-ID]"></script>
   ➡️ Paste before </body> on your website

Please test it and send feedback!
After approval, please send the remaining payment. Thank you! 🙏
```

---

#### 4. Post-Delivery Checklist

- [ ] Test the chat link yourself — ask about services, hours, booking
- [ ] Verify lead capture works (check dashboard)
- [ ] Ask client to test and approve
- [ ] Request testimonial: "Can you share a quick review?"
- [ ] Ask for referral: "Know any other business owner who'd benefit?"
- [ ] Offer monthly plan: "$30/month for hosting + updates"

---

## 5. Troubleshooting Guide

### Bot Not Responding

1. Check `OPENROUTER_API_KEY` is set in `.env`
2. Check OpenRouter dashboard for credits remaining
3. Check server logs: `python server.py` → look for `[ERROR]` lines
4. Try: `curl http://localhost:5000/api/health`

### Leads Not Saving

1. If using Supabase: check `SUPABASE_URL` and `SUPABASE_KEY` are correct
2. Check the `leads` table exists in Supabase SQL editor
3. Check for Row Level Security (RLS) — disable it on the `leads` table for the service key
4. Fallback: leads are saved to `leads.json` locally if Supabase fails

### Dashboard Login Failing

1. Make sure the botId exists in `businesses.json`
2. Make sure `password_hash` is set for that bot
3. Check `JWT_SECRET` is set and not empty in `.env`
4. Try creating a new password hash: `python -c "import bcrypt; print(bcrypt.hashpw(b'yourpassword', bcrypt.gensalt()).decode())"`

### RAG Not Finding Relevant Chunks

1. Check `OPENROUTER_API_KEY` works for embeddings
2. The embedding model (`perplexity/pplx-embed-v1-0.6b`) must be available on your plan
3. Lower the similarity threshold from 0.75 to 0.6 in `search_relevant_chunks()`
4. Check that `document_chunks` table exists in Supabase

### Render Deployment Issues

1. Check that `render.yaml` is in the root of your repo
2. Check all environment variables are set in Render dashboard
3. Check build logs for pip install errors
4. Make sure `gunicorn` is in `requirements.txt`
5. Free tier may take 30-60 seconds to wake up on first request

### Supabase Connection Errors

1. Check `SUPABASE_URL` format: must be `https://xxxxx.supabase.co` (no trailing slash)
2. Check `SUPABASE_KEY` is the **anon public** key, not the service role key
3. Check that pgvector extension is enabled: go to Supabase → Database → Extensions → enable `vector`
4. Check Row Level Security: for the `businesses` table, you may need to add a policy allowing SELECT

---

## 6. Business Operations Guide

### Pricing Guide

| Package | Price | What's Included |
|---------|-------|----------------|
| Starter | $150 (PKR 42,000) | Chatbot + lead capture + dashboard |
| Pro | $250 (PKR 70,000) | + Appointment booking |
| Premium | $400 (PKR 112,000) | + Custom branding + RAG knowledge base |
| Monthly | $30/month | Hosting + maintenance + updates |

**Payment flow:** 50% upfront → deliver → 50% on approval.

---

### How to Handle Support Requests

1. Client messages about bot not working → check the logs first
2. Client wants to change FAQ → log into their dashboard → Bot Settings → edit FAQs → Save
3. Client wants new service added → add it in Bot Settings → Services
4. Client's bot gets too many messages → rate limiting is already active (30/min/IP)
5. Client wants to suspend temporarily → use set-status:
   ```bash
   curl -X POST https://overarc.co/api/admin/set-status \
     -H "X-Admin-Key: YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{"botId": "their-bot-id", "status": "suspended"}'
   ```

---

### Monthly Maintenance Checklist

- [ ] Check OpenRouter API credit balance
- [ ] Check Supabase storage usage (free tier: 500MB)
- [ ] Check Render service logs for errors
- [ ] Review leads count per client (send monthly report)
- [ ] Ask clients if they want any changes to services/FAQs
- [ ] Check if any client's trial is expiring (set status to `active` after payment)

---

### Subscription Management

| Command | Effect |
|---------|--------|
| `status: "active"` | Bot works normally |
| `status: "trial"` | Works for 14 days from `created_at`, then auto-suspends |
| `status: "suspended"` | Bot replies: "This service is currently unavailable." |

**Activate after payment:**
```bash
curl -X POST https://overarc.co/api/admin/set-status \
  -H "X-Admin-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"botId": "client-bot-id", "status": "active"}'
```

---

*Overarc Agency — AI Chatbot Builders | Mingora, Swat, KPK, Pakistan*  
*WhatsApp: +92-324-9116764 | overarc.co*
