# 🏢 Overarc Agency — Complete Client Workflow Guide

## The Problem You're Solving

Business owners MISS customer inquiries at night, on holidays, or when they're busy.
Your chatbot captures those leads automatically — they never miss a customer again.

---

## 📸 REAL EXAMPLE: A Client Comes to You

Let's say **Dr. Khan** (a dentist in Mingora) wants a chatbot for his clinic.

Here's exactly what you do:

---

## STEP 1: Collect Client Info (5 mins on WhatsApp)

Ask Dr. Khan these 5 questions:

```
1. Business Name? → "Khan Dental Clinic"
2. What services & prices? → "Checkup PKR 500, Cleaning PKR 1500, etc."
3. What are common customer questions? → "Timings? Location? Price? Appointment?"
4. Working hours & location? → "9AM-8PM, Mingora Road"
5. WhatsApp number? → "0300-1234567"
```

---

## STEP 2: Add the Client to Your System (2 mins)

### Method A: Using the Admin Dashboard (EASIEST — No Coding!)

1. Open your browser → go to:
   ```
   http://localhost:5000/dashboard/khans-clinic
   ```
   
2. Log in with password: `admin123`

3. Click **"Customize Bot"** tab

4. Fill in:
   - **Business Name**: Khan Dental Clinic
   - **Avatar Emoji**: 🦷
   - **WhatsApp**: 0300-1234567
   - **Greeting**: "Welcome to Khan Dental Clinic! How can I help you today?"  
   - **Brand Color**: Pick a color (e.g., #22C55E green)
   - **System Prompt** (the AI's brain — write this in simple English):
     ```
     You are a helpful assistant for Khan Dental Clinic, a dental clinic in Mingora, Swat.
     
     LOCATION: Mingora Road, Swat
     WORKING HOURS: 9 AM to 8 PM, Monday-Saturday
     CONTACT: 0300-1234567
     
     OUR SERVICES:
     - Dental Checkup: PKR 500
     - Teeth Cleaning: PKR 1,500
     - Tooth Extraction: PKR 1,000-3,000
     - Root Canal: PKR 8,000-15,000
     
     YOUR JOB:
     - Greet visitors warmly
     - Answer questions about services and prices
     - Collect name + phone number for appointments
     - Keep responses short (max 3 sentences)
     ```
   
5. Add **FAQs** (click "Add FAQ Question Pair"):
   - Q: "What are your hours?" → A: "9 AM to 8 PM, Monday to Saturday"
   - Q: "Where are you located?" → A: "Mingora Road, Swat"

6. Add **Services** (click "Add Menu/Service Item"):
   - Dental Checkup → PKR 500
   - Teeth Cleaning → PKR 1,500

7. Click **"Save Customizations"**

### ✅ DONE! Your client's bot is now LIVE at:
```
http://localhost:5000/chat/khans-clinic
```

---

## STEP 3: Give the Client Their 3 Things

Send Dr. Khan this message on WhatsApp:

```
Assalam-o-Alaikum Dr. Khan! 🦷

Your AI chatbot for Khan Dental Clinic is ready! 🎉

Here are your 3 things:

1️⃣ STANDALONE CHAT LINK (share on WhatsApp/Instagram/Facebook):
   http://localhost:5000/chat/khans-clinic
   
   ➡️ Post this link on your WhatsApp status and Instagram bio
   ➡️ When someone clicks it, they can talk to your AI assistant
   ➡️ It works 24/7 — even when you're sleeping!

2️⃣ ADMIN DASHBOARD (see who messaged you):
   http://localhost:5000/dashboard/khans-clinic
   Password: admin123
   
   ➡️ Here you can see ALL leads captured (name + phone numbers)
   ➡️ You can also edit your bot's info anytime

3️⃣ WEBSITE EMBED CODE (if you have a website):
   Copy this and paste it before </body> on your website:
   <script src="http://localhost:5000/widget.js?botId=khans-clinic"></script>
   
   ➡️ A floating chat bubble will appear on your website

Please test it out and let me know if you want any changes.
Once approved, send the remaining payment.

Thank you for choosing Overarc Agency! 🙏
```

---

## WHAT THE CLIENT WILL SEE

### When they click the chat link:
They see a full-screen chat window with:
- Their clinic name at the top
- A greeting message
- Quick reply buttons (Services, Hours, Location)
- The AI answers all questions automatically
- After a few messages, it asks for name + phone (lead capture)

### When they open the dashboard:
They see:
- How many leads were captured
- A table with all customer names + phone numbers
- Settings to edit their bot's info
- Embed code to copy
- CSV export button to download leads

---

## STEP 4: GET PAID 💰

### Your Pricing:

| Package | Price | What Client Gets |
|---------|-------|------------------|
| 🟢 Starter | **$150** (PKR 42,000) | Chatbot + lead capture + dashboard |
| 🔵 Pro | **$250** (PKR 70,000) | Everything + appointment booking |
| 🔴 Premium | **$400** (PKR 112,000) | Everything + custom branding |
| 💎 Monthly | **$30/mo** (PKR 8,400) | Hosting + support (ASK EVERY CLIENT!) |

**Payment flow:** 50% upfront to start, 50% on delivery.

---

## WHAT TO SAY TO CLIENTS (Scripts)

### Urdu WhatsApp Script (Local Businesses):

> *"Assalam-o-Alaikum! 🤝*  
> *Main **Overarc Agency** se AI chatbot banata hoon.*  
> *Yeh chatbot aapki business ke liye 24/7 customers ke questions jawab deta hai, unka naam aur phone number save karta hai, aur appointments book karta hai.*  
> *Agar koi raat 2 baje aapke clinic ke baare mein poochhay, to AI jawab day ga aur appointment book kar day ga — jab aap so rahay hotay hain!*  
> *Main 3 din mein ready kar deta hoon. Pehle demo FREE hai. Interested?*  

### English Fiverr Gig:

> *"I will build an AI chatbot for your business that captures leads and books appointments 24/7"*

---

## WHAT TO DO AFTER THEY SAY YES

```
1. Get their business info (name, services, FAQs, hours, location)
2. Go to http://localhost:5000/dashboard/THEIR-ID
3. Fill in all their info in "Customize Bot" tab
4. Click Save
5. Send them the 3 things (chat link, dashboard, embed code)
6. Ask for testimonial
7. Ask for referral: "Do you know any other business owner?"
8. Offer monthly maintenance for $30/month
```

---

## REPEAT FOR EVERY CLIENT

Every new client = a new botId.

For example:
- `khans-clinic` → http://localhost:5000/chat/khans-clinic
- `ali-restaurant` → http://localhost:5000/chat/ali-restaurant
- `ahmad-realestate` → http://localhost:5000/chat/ahmad-realestate

Each one gets their OWN dashboard at:
- http://localhost:5000/dashboard/khans-clinic
- http://localhost:5000/dashboard/ali-restaurant
- http://localhost:5000/dashboard/ahmad-realestate

---

## QUICK REFERENCE

| Action | What to Do |
|--------|-----------|
| Get client info | Ask on WhatsApp (5 questions) |
| Add to system | Go to /dashboard/THEIR-ID → Customize Bot tab |
| Get chat link | http://localhost:5000/chat/THEIR-ID |
| Get dashboard | http://localhost:5000/dashboard/THEIR-ID |
| Get embed code | Copy from dashboard Overview tab |
| Get paid | 50% upfront, 50% on delivery |
| Monthly income | Ask every client for $30/month hosting |

---

*Overarc Agency — AI Chatbot Builders | May 2026*