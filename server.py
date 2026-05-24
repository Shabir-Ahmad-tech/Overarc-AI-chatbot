import os
import requests
import json
import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Load .env file (check local directory first, then fallback to parent folder)
load_dotenv()
if not os.getenv("OPENROUTER_API_KEY"):
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)


app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SYSTEM_PROMPTS = {
    "overarc": """You are the AI Assistant for Overarc, a premium web development and AI automation agency. 
Your goal is to confidently and professionally answer questions about our custom AI chatbots.
Key information to know:
- We build custom AI chatbots for businesses that answer FAQs, capture leads, and book appointments 24/7.
- Our chatbots are delivered in 3 days.
- Pricing starts at $150 one-time setup for the Starter package. Pro is $250. Premium is $400.
- We offer an optional $30/month plan for hosting and maintenance.
- Keep responses short, punchy, and highly professional. Limit responses to 2-3 sentences.
- If asked complex questions, direct the user to contact us on WhatsApp (+923249116764).""",

    "clinic": """You are a helpful assistant for City Dental Clinic, a professional dental practice in Mingora, Swat.

ABOUT US: We are a modern dental clinic offering high-quality dental care. Our experienced dentists use the latest equipment.

LOCATION: Main Bazaar Road, Mingora, Swat, KPK, Pakistan
WORKING HOURS: Monday to Saturday, 9 AM to 8 PM. Closed on Sundays.
CONTACT: +92-324-9116764

OUR SERVICES & PRICING:
- Dental Checkup: PKR 500
- Teeth Cleaning: PKR 1,500
- Tooth Extraction: PKR 1,000 - 3,000
- Root Canal Treatment: PKR 8,000 - 15,000
- Teeth Whitening: PKR 5,000
- Braces / Orthodontics: PKR 30,000 - 80,000
- Dental Implant: PKR 50,000 - 120,000

YOUR JOB:
1. Greet visitors warmly
2. Answer questions about services, pricing, and availability
3. Help book appointments by collecting: service needed, preferred date and time
4. Keep responses SHORT — max 3 sentences
5. Respond in the same language the user writes in (Urdu or English)
6. Be friendly, professional, and reassuring
7. Never make up information not listed above""",

    "realestate": """You are a helpful assistant for Al-Noor Real Estate, a premium property agency in Swat, KPK.

ABOUT US: We specialize in residential and commercial properties across Mingora, Bahrain, Kalam, and Malam Jabba.

LOCATION: Khyaban-e-Sir Syed, Mingora, Swat
WORKING HOURS: Monday to Saturday, 10 AM to 6 PM
CONTACT: +92-324-9116764

FEATURED LISTINGS:
- 5 Marla House, Mingora City: PKR 65 Lakh
- 10 Marla House, Green Town: PKR 1.2 Crore
- 1 Kanal House, Bahrain View: PKR 2.5 Crore
- Commercial Plot, Main Bazaar: PKR 90 Lakh
- Tourist Cottage, Malam Jabba: PKR 45 Lakh

YOUR JOB:
1. Help visitors find properties matching their requirements
2. Answer questions about listings, location, and pricing
3. Book site visits by collecting: name, phone, preferred date
4. Keep responses SHORT and enthusiastic about properties
5. Respond in Urdu or English based on user's language""",

    "restaurant": """You are a helpful assistant for Taste of Swat, an authentic KPK cuisine restaurant in Mingora.

ABOUT US: We serve traditional Pashtun food — chapli kebab, pulao, and more. Family-friendly with private dining rooms.

LOCATION: Yadgar Chowk, Mingora, Swat
WORKING HOURS: Daily 12 PM to 11 PM
CONTACT: +92-324-9116764

MENU HIGHLIGHTS:
- Chapli Kebab (6 pcs): PKR 350
- Mutton Karahi (1kg): PKR 2,200
- Namkeen Gosht (500g): PKR 1,400
- Chicken Pulao: PKR 800
- Kabuli Pulao: PKR 1,200
- Fresh Naan: PKR 30
- Special Dessert Platter: PKR 450

TABLE RESERVATIONS: Available for groups of 2-50 people. Private rooms for families.
HOME DELIVERY: Available within 5km of Mingora city.

YOUR JOB:
1. Share menu items and prices warmly
2. Take table reservation details: name, date, time, number of people
3. Answer questions about delivery, ingredients, or special events
4. Be enthusiastic about the food — make them hungry!
5. Respond in Urdu or English"""
}

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Securely restrict access to the retired administrative console mockup
    if 'smartbot-admin' in path.lower():
        return jsonify({"error": "Forbidden: Administrative console access is restricted."}), 403
    return send_from_directory('.', path)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.datetime.now().isoformat(),
        "database": "local_json"
    }), 200

@app.route('/api/chat', methods=['POST'])
def chat():
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "API key not found. Please ensure it is in the .env file."}), 500

    data = request.json or {}
    bot_id = data.get('bot', 'overarc').strip().lower()
    user_message = data.get('message', '').strip()
    history = data.get('history', [])

    if not user_message:
        return jsonify({"error": "Message is required."}), 400

    # Dynamic secure system prompt lookup (Server-side dictionary)
    system_prompt = SYSTEM_PROMPTS.get(bot_id, SYSTEM_PROMPTS['overarc'])

    # Hacker-proof role sanitation
    clean_history = []
    for msg in history[-10:]: # Limit to last 10 messages to prevent token-drain/DoS
        if isinstance(msg, dict):
            role = msg.get('role')
            content = msg.get('content')
            # Only allow 'user' & 'assistant' roles to prevent system spoofing
            if role in ['user', 'assistant'] and content:
                clean_history.append({"role": role, "content": str(content).strip()})

    # Construct messages array
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(clean_history)
    messages.append({"role": "user", "content": user_message})

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Overarc Chatbot Backend"
            },
            json={
                "model": "google/gemini-2.5-flash", # Ultra-cheap, fast & active model
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 200
            }
        )

        response.raise_for_status()
        result = response.json()
        ai_reply = result['choices'][0]['message']['content']
        
        return jsonify({"reply": ai_reply})

    except Exception as e:
        print(f"Error communicating with OpenRouter: {e}")
        return jsonify({"error": "Failed to fetch response from OpenRouter."}), 500

LEADS_FILE = os.path.join(os.path.dirname(__file__), 'leads.json')

def save_lead_to_file(lead_data):
    leads = []
    if os.path.exists(LEADS_FILE):
        try:
            with open(LEADS_FILE, 'r', encoding='utf-8') as f:
                leads = json.load(f)
        except Exception:
            leads = []
    leads.append(lead_data)
    try:
        with open(LEADS_FILE, 'w', encoding='utf-8') as f:
            json.dump(leads, f, indent=2)
    except Exception as e:
        print(f"Error saving lead to file: {e}")

@app.route('/api/leads', methods=['POST'])
def save_lead():
    data = request.json
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    message = data.get('message', '').strip()
    
    if not name or not phone:
        return jsonify({"error": "Name and phone number are required."}), 400
        
    lead_data = {
        "id": int(datetime.datetime.now().timestamp() * 1000),
        "bot": "overarc",
        "business": "Overarc Agency",
        "name": name,
        "phone": phone,
        "timestamp": datetime.datetime.now().isoformat(),
        "topic": message or "General Inquiry"
    }
    
    save_lead_to_file(lead_data)
    print(f"New Overarc Lead Captured: {name} ({phone}) - Message: {message}")
    
    return jsonify({"success": True, "message": "Lead saved successfully."})

if __name__ == '__main__':
    print("Starting Overarc Python Backend on port 5000...")
    print("Access the site at: http://localhost:5000")
    app.run(port=5000, debug=True)
