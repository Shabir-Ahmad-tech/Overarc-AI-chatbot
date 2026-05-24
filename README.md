# 🚀 Overarc Agency — AI Chatbot Builder Toolkit

## 🏢 Who We Are

**Overarc Agency** is an AI automation agency. We build custom AI chatbots for businesses that:
- Answer customer questions **24/7**
- Capture **leads** (name + phone numbers) automatically  
- Book **appointments** without human involvement
- Work on websites, WhatsApp, Instagram, and as standalone links

## 📦 What's in this Toolkit?

This folder contains **our complete system** for building, managing, and selling AI chatbots to clients. Every file here is designed to help you deliver a premium product fast.

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

### STEP 2: Run the System
Double-click **`Launch_App.bat`** OR open terminal and type:
```
cd "d:\04_Coding_and_AI\05. Antigravity\Overarc-AI-chatbot"
venv\Scripts\python server.py
```

You'll see:
```
Starting Overarc Python Backend on port 5000...
Access the site at: http://localhost:5000
```

### STEP 3: Open in Browser
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

## ➕ How to Add a NEW Client to Your Agency

### Method 1: Edit JSON (Manual — 2 Minutes)

1. Open **`businesses.json`** 
2. Copy one existing entry and paste it
3. Change the `"id"` to something unique (e.g., `"my-client"`)
4. Change all the business info (name, services, FAQs, etc.)
5. Save the file
6. Restart the server (Ctrl+C then `python server.py` again)
7. Done! Your client's bot is live at: `/chat/my-client`

### Method 2: Admin Dashboard (No Coding)

1. Go to `http://localhost:5000/dashboard/YOUR_CLIENT_ID`
2. Enter password: `admin123`
3. Go to "Customize Bot" tab
4. Edit everything: name, greeting, brand color, AI instructions, FAQs, services
5. Click "Save" — bot is updated instantly!

---

## 💰 HOW TO SELL BOTS & MAKE MONEY (Agency Model)

### Our Pricing Tiers (Already on the Agency Website):

| Package | PKR | USD | What Client Gets |
|---------|-----|-----|------------------|
| 🟢 **Starter** | PKR 42,000 | **$150** | 24/7 FAQ bot + lead capture + admin panel |
| 🔵 **Pro** | PKR 70,000 | **$250** | Everything + appointment booking + embed code |
| 🔴 **Premium** | PKR 112,000 | **$400** | Everything + custom branding + 6 months support |
| 💎 **Monthly** | PKR 8,400 | **$30/mo** | Hosting + updates + support (passive income) |

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
   Password: admin123

💻 EMBED CODE (for your website):
   <script src="http://localhost:5000/widget.js?botId=[their-botId]"></script>

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
| `server.py` | ⚙️ Backend engine — runs all APIs |
| `.env` | 🔑 Store your API keys here (SECRET!) |
| `businesses.json` | 📋 All your clients' bot configurations |
| `leads.json` | 📩 Captured customer leads (auto-saved) |
| `appointments.json` | 📅 Booked appointments (auto-saved) |
| `public/index.html` | 🌐 Your agency marketing website |
| `public/smartbot-demo.html` | 🎮 Live demo for client pitches |
| `public/chat.html` | 💬 Standalone chat page per client |
| `public/widget.js` | 🔌 1-line embed widget for websites |
| `public/smartbot-dashboard.html` | 📊 Admin panel for clients |
| `schema.sql` | 🗄️ Database schema (for Supabase) |

---

## ❓ Agency FAQ

**Q: How much does it cost ME to run this?**
A: Almost nothing! AI costs ~$0.01 per 100 conversations. If you get 1,000 conversations/month across all clients, that's only $0.10.

**Q: What if my client doesn't have a website?**
A: No problem. Give them the standalone link (e.g., `/chat/clinic`) — they share it on WhatsApp/Instagram.

**Q: Can I customize the AI model?**
A: Yes. In `server.py`, change `google/gemini-2.5-flash` to any model (GPT-4, Claude, etc.)

**Q: How do I deploy this for real clients?**
A: For now it runs on your computer. When you're ready for live deployment, I'll help you put it on **Render** or **Railway** (free hosting).

**Q: Can I change the admin password?**
A: Yes. Open `.env` and change `ADMIN_PASSWORD=admin123` to your own password.

---

## 🚀 Quick Start Recap for Overarc Agency

```
STEP 1: Get API key from https://openrouter.ai/keys
STEP 2: Paste it in .env file
STEP 3: Run: venv\Scripts\python server.py
STEP 4: Open http://localhost:5000
STEP 5: Show 3 demo bots to clients
STEP 6: Close deals at $150-$400 per bot
STEP 7: Collect $30/month recurring from each client 💰
```

---

*Built by **Overarc Agency** | AI Chatbot Builders | Version 1.0 | May 2026*
