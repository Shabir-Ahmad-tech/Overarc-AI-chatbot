# AI Chatbot Business Blueprint
## Complete Build + Client Acquisition Guide
### For: Google Antigravity / AI IDE Agent

---

## SECTION 1 — WHAT TO BUILD (Give this to your AI)

### Product Name
**"SmartBot" — Embeddable AI Business Assistant**

### What It Is
A white-label AI chatbot web app that any business can use.
You build ONE product. You customize it per client. You deliver it in 3 days.

### Why Embeddable Website Chatbot (Not WhatsApp)
- Works for ALL clients — local + international
- No Meta Business API approval needed (WhatsApp bots need this — takes weeks)
- Client just pastes ONE line of code on their website OR you give them a standalone hosted link
- You control the backend, client pays you monthly (recurring revenue)
- Works on mobile and desktop automatically

---

## SECTION 2 — FULL TECHNICAL SPECIFICATION (For Your AI to Build)

### Tech Stack
```
Frontend:     Next.js 14 (App Router) + Tailwind CSS
Backend:      Next.js API Routes (serverless)
AI:           OpenAI GPT-4o-mini API (cheapest, fastest, good enough)
Database:     Supabase (free tier — stores leads, appointments, chat logs)
Auth:         None needed for client-facing bot
Deployment:   Vercel (free tier, one-click deploy)
Embed:        Single <script> tag injection
```

### Core Features to Build

#### 1. Chat Interface
- Floating chat bubble (bottom-right corner)
- Opens into a clean chat window
- Business logo + name at top
- Typing indicator (animated dots)
- Mobile responsive
- Custom color theme per client (set via config)

#### 2. AI Brain
- System prompt dynamically loaded from Supabase per business
- Knows: business name, services, pricing, hours, location, FAQs
- Handles: greetings, questions, objections, bookings, lead capture
- Falls back to: "Let me connect you with our team" when unsure
- Language: supports both English and Urdu (detect from user input)

#### 3. Lead Capture Flow
- After 2nd message, bot asks: "Can I get your name and number to follow up?"
- Saves to Supabase leads table
- Sends email notification to business owner (via Resend.com free tier)

#### 4. Appointment Booking Flow
- Bot asks: preferred service, date, time
- Saves to Supabase appointments table
- Sends confirmation message to user
- Sends email to business owner with booking details

#### 5. Admin Dashboard (Simple)
- Protected by a password (simple env variable, no full auth needed)
- Shows: all leads captured, all appointments booked, chat logs
- Business owner can update: FAQs, services, pricing (no-code, form-based)
- Export leads as CSV button

#### 6. Embed System
- Each business gets unique botId (UUID)
- Embed code:
```html
<script src="https://yourapp.vercel.app/embed.js?botId=UNIQUE_ID"></script>
```
- Also provide standalone link: `https://yourapp.vercel.app/chat/UNIQUE_ID`
  (For clients with no website — they share this link on WhatsApp/Instagram)

---

## SECTION 3 — DATABASE SCHEMA (Tell AI to build exactly this)

### Supabase Tables

```sql
-- Businesses table
businesses (
  id UUID PRIMARY KEY,
  name TEXT,
  industry TEXT,           -- clinic / restaurant / real_estate / other
  logo_url TEXT,
  primary_color TEXT,      -- hex color e.g. #2563eb
  whatsapp_number TEXT,
  email TEXT,
  system_prompt TEXT,      -- full AI instructions for this business
  faqs JSONB,              -- [{ question, answer }]
  services JSONB,          -- [{ name, price, duration }]
  working_hours TEXT,
  location TEXT,
  created_at TIMESTAMP
)

-- Leads table
leads (
  id UUID PRIMARY KEY,
  business_id UUID REFERENCES businesses(id),
  name TEXT,
  phone TEXT,
  email TEXT,
  message TEXT,            -- what they were asking about
  created_at TIMESTAMP
)

-- Appointments table
appointments (
  id UUID PRIMARY KEY,
  business_id UUID REFERENCES businesses(id),
  customer_name TEXT,
  customer_phone TEXT,
  service TEXT,
  preferred_date TEXT,
  preferred_time TEXT,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMP
)

-- Chat logs table
chat_logs (
  id UUID PRIMARY KEY,
  business_id UUID REFERENCES businesses(id),
  session_id TEXT,
  role TEXT,               -- 'user' or 'assistant'
  content TEXT,
  created_at TIMESTAMP
)
```

---

## SECTION 4 — AI SYSTEM PROMPT TEMPLATE (Auto-fill per client)

```
You are a helpful assistant for {BUSINESS_NAME}, a {INDUSTRY} business.

ABOUT US:
{BUSINESS_DESCRIPTION}

LOCATION: {LOCATION}
WORKING HOURS: {WORKING_HOURS}
CONTACT: {WHATSAPP_NUMBER}

OUR SERVICES & PRICING:
{SERVICES_LIST}

COMMON QUESTIONS & ANSWERS:
{FAQS_LIST}

YOUR JOB:
1. Greet visitors warmly
2. Answer questions about our services, pricing, and availability
3. Capture name + phone number of interested visitors
4. Help book appointments by collecting: service needed, preferred date and time
5. If you cannot answer something, say: "Let me connect you with our team directly." and provide the WhatsApp number
6. Keep responses SHORT — max 3 sentences
7. Respond in the same language the user writes in (Urdu or English)
8. Never make up prices or services not listed above
9. Always be polite and professional

IMPORTANT: You represent {BUSINESS_NAME}. Do not mention OpenAI or that you are an AI unless directly asked.
```

---

## SECTION 5 — PAGES TO BUILD

```
/ (home)              → Not needed, redirect to /chat/[botId]
/chat/[botId]         → Standalone chat page (for clients without websites)
/admin/[botId]        → Password-protected admin dashboard
/admin/[botId]/leads  → View + export leads
/admin/[botId]/bookings → View appointments
/admin/[botId]/settings → Update business info, FAQs, services
/api/chat             → POST endpoint, takes botId + messages, returns AI response
/api/leads            → POST endpoint, saves lead to Supabase
/api/appointments     → POST endpoint, saves booking to Supabase
/embed.js             → JavaScript snippet that injects chat bubble into any website
```

---

## SECTION 6 — PRICING TIERS (Your Service Packages)

### Package 1 — Starter ($150 / PKR 42,000)
- 1 chatbot setup
- FAQ answering + lead capture
- Admin dashboard
- Standalone chat link
- 1 month free support

### Package 2 — Pro ($250 / PKR 70,000)
- Everything in Starter
- Appointment booking system
- Embed code for their website
- Urdu + English support
- 3 months support

### Package 3 — Premium ($400 / PKR 112,000)
- Everything in Pro
- Custom branding + colors
- Monthly leads report (PDF)
- Priority support 6 months
- Free tweaks anytime

### Recurring Maintenance (Optional upsell)
- $30/month: hosting + support + updates
- This is your passive income — push this on EVERY client

---

## SECTION 7 — HOW TO FIND CLIENTS

### Local Pakistani Clients (Mingora/Swat/KPK)

**Step 1 — Build 3 Demo Bots First (before outreach)**
Build these specific demos:
- Demo 1: "City Dental Clinic" — appointment booking bot
- Demo 2: "Al-Noor Real Estate" — property inquiry bot
- Demo 3: "Taste of Swat Restaurant" — menu + reservation bot

Record a 60-second Loom video of each one working.

**Step 2 — WhatsApp Outreach Script**
Target: Clinics, pharmacies, real estate offices, restaurants, clothing stores

Message (send in Urdu or English based on who they are):

```
Assalam o Alaikum [Name/Sir/Ma'am],

I noticed your business [NAME] doesn't have an AI assistant yet.
I've built one for similar businesses — it answers customer questions
24/7, captures leads, and books appointments automatically.

Here's a 60-second demo I made for a clinic similar to yours:
[LOOM LINK]

I can build the same for your business in 3 days.
First one is free — I only ask for a testimonial.

Interested?
```

**Step 3 — Where to Find Their Numbers**
- Google Maps → search "clinics in Mingora" → click each → get WhatsApp number
- Facebook business pages in your city
- Instagram local business pages
- Physical walk-in (most powerful — show demo on your phone)

**Step 4 — Follow-up**
- Day 1: Send message
- Day 3: One follow-up only: "Just checking if you got a chance to see the demo?"
- Day 5: Move on, contact next business
- Never chase more than twice

---

### International Clients (Fiverr + Upwork)

**Fiverr Gig Title:**
"I will build an AI chatbot for your business that captures leads and books appointments"

**Fiverr Gig Description:**
```
Tired of missing customer inquiries? I'll build you a smart AI chatbot
that works 24/7 — answering questions, capturing leads, and booking
appointments automatically.

What you get:
✅ Custom AI trained on YOUR business info
✅ Lead capture with email notifications
✅ Appointment booking system
✅ Admin dashboard to view all leads + bookings
✅ Works on your website OR as a standalone link
✅ English + any language support
✅ Delivered in 3 days

Perfect for: Clinics, Law Firms, Real Estate, Restaurants,
E-commerce, Coaches, Service Businesses

Basic: $150 — FAQ + Lead Capture
Standard: $250 — + Appointment Booking
Premium: $400 — + Full custom branding + 6mo support
```

**Upwork Profile Headline:**
"AI Chatbot Developer | Lead Capture + Appointment Booking Bots | 3-Day Delivery"

**First 5 Upwork Proposals — Target These Job Types:**
- "Need a chatbot for my clinic/dental office"
- "Looking for AI assistant for my website"
- "Need automated lead capture system"
- "Chatbot for customer support"
- "AI appointment booking system"

---

## SECTION 8 — HOW TO CLOSE A CLIENT

### The Discovery Call (20 minutes max)

Ask ONLY these 5 questions:
1. "What do customers ask you most often?"
2. "Do you currently miss inquiries after business hours?"
3. "Do you want it to book appointments or just answer questions?"
4. "Do you have a website, or should I give you a standalone link?"
5. "What's your budget range?"

Then say:
```
"Based on what you told me, I can build you a bot that handles [X and Y].
It'll answer questions 24/7, capture leads directly to you, and
[book appointments / show pricing / handle inquiries].

I can deliver it in 3 days. My [Starter/Pro] package covers everything
you need — that's [$150/$250]. I take 50% upfront to start,
50% when you approve the final version.

Should I send you the invoice?"
```

**Stop talking after that. Wait for their answer.**

### Handling Objections

| Objection | Your Response |
|---|---|
| "It's expensive" | "Understood. If it captures just 2 extra clients per month, it pays for itself. Want to try the Starter at $150?" |
| "I need to think" | "Of course. I'll send you the demo link to share with your team. I have one slot open this week — if you decide by [day], I can start immediately." |
| "Does it really work?" | "Here's a live demo I built for a similar business: [link]. You can test it right now." |
| "I don't have a website" | "No problem — I give you a standalone link you can share on WhatsApp and Instagram. No website needed." |

---

## SECTION 9 — HOW TO DELIVER THE RESULT

### Day 1 (After Payment Received)
- Send client a simple Google Form or WhatsApp message asking:
  - Business name, logo, colors
  - Services + prices
  - Top 10 FAQs
  - Working hours + location
  - WhatsApp number for escalations
  - Email for lead notifications

### Day 2 (Build)
- Feed their info into your Antigravity setup
- Generate the full app
- Customize system prompt with their data
- Deploy to Vercel
- Test every flow: FAQ, lead capture, booking

### Day 3 (Deliver)
Send client a message with:
```
Hi [Name],

Your AI assistant is ready! Here's everything:

🔗 Chat Link: https://yourapp.vercel.app/chat/[their-botId]
   (Share this on WhatsApp, Instagram, or your website)

📊 Admin Dashboard: https://yourapp.vercel.app/admin/[their-botId]
   Password: [their-password]

💻 Embed Code (paste before </body> on your website):
   <script src="https://yourapp.vercel.app/embed.js?botId=[their-botId]"></script>

📹 Quick video showing how to use the dashboard: [Loom link]

Please test it and let me know if you want any changes.
Once you approve, kindly send the remaining payment.

Thank you!
```

### After Delivery
- Ask immediately: "Can you give me a short testimonial I can use?"
- Ask: "Do you know any other business owner who could benefit from this?"
- Offer maintenance: "For $30/month I'll handle all updates and keep it running smoothly"

---

## SECTION 10 — TOOLS YOU NEED (All Free to Start)

| Tool | Purpose | Cost |
|---|---|---|
| Google Antigravity | Build the app | Free |
| Vercel | Deploy/host the app | Free |
| Supabase | Database | Free |
| OpenAI API | AI brain | Pay per use (~$0.01/conversation) |
| Resend.com | Email notifications | Free (100/day) |
| Loom | Demo videos | Free |
| Fiverr | International clients | Free (20% commission) |
| Upwork | International clients | Free to join |
| Google Maps | Find local clients | Free |

**Total startup cost: $0 + OpenAI API credits (~$5 to start)**

---

## SECTION 11 — EXACT PROMPT TO GIVE YOUR AI

Copy and paste this into Antigravity:

```
Build a complete white-label AI chatbot SaaS application with the following specifications:

TECH STACK: Next.js 14 (App Router), Tailwind CSS, Supabase, OpenAI API (gpt-4o-mini), Vercel deployment, Resend for emails.

BUILD EXACTLY:
1. A floating chat bubble widget that opens a chat window (bottom-right, mobile responsive)
2. AI responses powered by OpenAI, using a dynamic system prompt loaded from Supabase based on botId
3. Lead capture after 2nd message (name + phone → save to Supabase leads table + email via Resend)
4. Appointment booking flow (service, date, time → save to Supabase appointments table + email via Resend)
5. Admin dashboard at /admin/[botId] protected by env variable password showing: all leads, all bookings, chat logs, and editable business settings (name, FAQs, services, hours, colors)
6. Standalone chat page at /chat/[botId]
7. Embeddable script at /embed.js?botId=X that injects the chat bubble into any website
8. API routes: /api/chat (POST), /api/leads (POST), /api/appointments (POST)

DATABASE: Use exact Supabase schema provided — tables: businesses, leads, appointments, chat_logs

SYSTEM PROMPT: Load from businesses.system_prompt in Supabase, inject businesses.faqs and businesses.services dynamically

UI STYLE: Clean, modern, professional. White background, subtle shadows, smooth animations. Chat bubble uses businesses.primary_color. Business logo in chat header.

LANGUAGE: Support English and Urdu. Detect from user input and respond in same language.

INCLUDE: Full README with setup instructions, environment variables list, Supabase schema SQL, and how to add a new business.

Make it production-ready, well-commented, and deployable to Vercel in one click.
```

---

## SECTION 12 — REPOSITORY SETUP & GIT CONFIGURATION (.gitignore)

To maintain a professional, secure, and clean codebase, configuring Git properly is essential. A `.gitignore` file prevents sensitive API credentials, local test data, database files, and massive system environment folders (like `venv/` or `node_modules/`) from being accidentally pushed to GitHub.

### 1. Recommended Project Directory Structure

```
Overarc-AI-chatbot/
│
├── .env                  # Private configurations & API keys (IGNORED)
├── .gitignore            # Git configuration rules
├── AI-chatbot.md         # Business blueprint & design guidelines
├── requirements.txt      # Python dependencies
├── server.py             # Flask backend API
├── index.html            # Main landing page for Overarc Agency
├── smartbot-demo.html    # Interactive demo sandbox for clients
├── leads.json            # Captured leads local database (IGNORED)
│
├── Icons/                # Static assets & brand graphics
│   ├── Hero.png
│   └── Transparent.png
│
└── venv/                 # Python Virtual Environment folder (IGNORED)
```

### 2. Standard `.gitignore` File Contents

Create a file named `.gitignore` in the root of your project directory and add the following contents:

```gitignore
# =========================================================================
# Overarc AI Chatbot - Professional Git Ignore Configuration
# =========================================================================

# --- Environment Configuration ---
# Never commit sensitive credentials, API keys, or private environment files
.env
.env.local
.env.*.local
*.env

# --- Python Virtual Environments ---
# Ignore local virtual environment directories used for development
venv/
.venv/
env/
ENV/
ActiveState.venv/

# --- Python Compilation & Cache ---
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so

# --- Local Data & Databases ---
# Ignore locally captured leads data and database instances
leads.json
*.db
*.sqlite
*.sqlite3

# --- Web & Frontend Build Caches (for Next.js / Node.js migration) ---
node_modules/
.next/
out/
build/
dist/
.docusaurus/
.cache/

# --- Operating System & Editor Files ---
# OS files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Editor and IDE configurations
.vscode/
.idea/
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?

# --- Log Files ---
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
```

### 3. How to Clean Up Already Tracked Files

If you accidentally tracked the `venv/` folder or `.env` file before creating `.gitignore`, run the following commands in your terminal to untrack them without deleting them locally:

```bash
# Untrack .env file
git rm --cached .env

# Untrack leads.json file (if created)
git rm --cached leads.json

# Untrack the entire venv folder (might take a moment)
git rm --cached -r venv/

# Commit the changes and your new .gitignore
git add .gitignore
git commit -m "chore: implement professional gitignore and untrack virtual env"
```

---


## QUICK REFERENCE — YOUR NUMBERS

| Metric | Target |
|---|---|
| Time to build per client | 3 days |
| Minimum price | $150 |
| First month goal | 2 clients = $300 |
| Month 3 goal | 5 clients + 3 retainers = $1,250+ |
| Messages to send per week | 20 local + 10 Fiverr proposals |
| Follow-ups per lead | Max 2 |
| Demo bots to build first | 3 (clinic, real estate, restaurant) |

---

*Built for: [Your Name] | Version 1.0 | May 2026*