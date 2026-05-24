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


app = Flask(__name__, static_folder='public', static_url_path='')
CORS(app)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

BUSINESSES_FILE = os.path.join(os.path.dirname(__file__), 'businesses.json')

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)

# Admin password from env, fallback to 'admin123'
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123").strip()

# Log the database status on start
if USE_SUPABASE:
    print(f"[DATABASE] Core: Supabase PostgreSQL (URL: {SUPABASE_URL})")
else:
    print("[DATABASE] Core: Local JSON fallback (businesses.json & leads.json)")

def send_resend_email(to_email, subject, html_body):
    if not RESEND_API_KEY:
        return False
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "from": "Overarc SmartBot <onboarding@resend.dev>",
                "to": to_email,
                "subject": subject,
                "html": html_body
            }
        )
        if response.status_code in [200, 201]:
            print(f"[EMAIL] Resend Email Alert Sent successfully to {to_email}!")
            return True
        else:
            print(f"[WARNING] Resend API returned error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[WARNING] Failed to send Resend email: {e}")
    return False

def load_businesses():
    if USE_SUPABASE:
        try:
            url = f"{SUPABASE_URL}/rest/v1/businesses"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            records = res.json()
            # Convert list into id-keyed dict for seamless downstream compatibility
            return {biz["id"]: biz for biz in records}
        except Exception as e:
            print(f"[WARNING] Supabase error load_businesses: {e}. Falling back to local businesses.json")
            
    # Fallback to local businesses.json
    if os.path.exists(BUSINESSES_FILE):
        try:
            with open(BUSINESSES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading businesses.json: {e}")
    return {}

def save_businesses(data):
    if USE_SUPABASE:
        try:
            # Postgrest upsert inserts or merges records
            url = f"{SUPABASE_URL}/rest/v1/businesses"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            }
            # Upsert all businesses in the dictionary
            payload = list(data.values())
            res = requests.post(url, headers=headers, json=payload)
            res.raise_for_status()
            return True
        except Exception as e:
            print(f"[WARNING] Supabase error save_businesses: {e}. Falling back to local businesses.json")

    # Fallback to local businesses.json
    try:
        with open(BUSINESSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error writing businesses.json: {e}")
    return False

@app.route('/')
def serve_index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Securely restrict access to the retired administrative console mockup
    if 'smartbot-admin' in path.lower():
        return jsonify({"error": "Forbidden: Administrative console access is restricted."}), 403
    return send_from_directory('public', path)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.datetime.now().isoformat(),
        "database": "supabase" if USE_SUPABASE else "local_json"
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

    # Dynamic secure system prompt lookup from JSON or Supabase
    businesses = load_businesses()
    if bot_id in businesses:
        biz = businesses[bot_id]
        system_prompt = biz.get('system_prompt', '')
        
        # Dynamic injection of Menu/Services list into prompt template
        services = biz.get('services', [])
        if services:
            services_text = "\n".join([f"- {s.get('name')}: {s.get('price')}" for s in services])
            system_prompt = system_prompt.replace("{SERVICES_LIST}", services_text)
            
        # Dynamic injection of FAQs list into prompt template
        faqs = biz.get('faqs', [])
        if faqs:
            faqs_text = "\n".join([f"Q: {f.get('q')}\nA: {f.get('a')}" for f in faqs])
            system_prompt = system_prompt.replace("{FAQS_LIST}", faqs_text)
    else:
        system_prompt = """You are the AI Assistant for Overarc, a premium web development and AI automation agency. 
Your goal is to confidently and professionally answer questions about our custom AI chatbots.
Key information to know:
- We build custom AI chatbots for businesses that answer FAQs, capture leads, and book appointments 24/7.
- Our chatbots are delivered in 3 days.
- Pricing starts at $150 one-time setup for the Starter package. Pro is $250. Premium is $400.
- We offer an optional $30/month plan for hosting and maintenance.
- Keep responses short, punchy, and highly professional. Limit responses to 2-3 sentences.
- If asked complex questions, direct the user to contact us on WhatsApp (+923249116764)."""

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

def save_lead_to_db(lead_data):
    if USE_SUPABASE:
        try:
            url = f"{SUPABASE_URL}/rest/v1/leads"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            res = requests.post(url, headers=headers, json=lead_data)
            res.raise_for_status()
            return True
        except Exception as e:
            print(f"[WARNING] Supabase error save_lead_to_db: {e}. Falling back to local leads.json")
            
    # Fallback to local leads.json
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
        return True
    except Exception as e:
        print(f"Error saving lead to file: {e}")
    return False

@app.route('/api/leads', methods=['POST'])
def save_lead():
    data = request.json or {}
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    message = data.get('message', '').strip()
    bot = data.get('bot', 'overarc').strip().lower()
    
    if not name or not phone:
        return jsonify({"error": "Name and phone number are required."}), 400
        
    # Dynamically map business name from JSON or Supabase
    businesses = load_businesses()
    business_name = "Overarc Agency"
    business_email = "hello@overarc.co"
    if bot in businesses:
        biz = businesses[bot]
        business_name = biz.get('name', 'Overarc Agency')
        # Check if the business has configured an email address (otherwise fallback to general hello@overarc.co)
        business_email = biz.get('email', 'hello@overarc.co')
        
    lead_data = {
        "bot": bot,
        "business": business_name,
        "name": name,
        "phone": phone,
        "timestamp": datetime.datetime.now().isoformat(),
        "topic": message or "General Inquiry"
    }
    
    # Save lead
    save_lead_to_db(lead_data)
    print(f"New Lead Captured [{business_name}]: {name} ({phone}) - Topic: {message}")
    
    # 📬 Resend Email Alert triggering!
    if RESEND_API_KEY:
        email_html = f"""
        <h3>⚡ New Lead Captured on Overarc SmartBot</h3>
        <p><strong>Business Client:</strong> {business_name} ({bot})</p>
        <hr/>
        <p><strong>Customer Name:</strong> {name}</p>
        <p><strong>Phone Number:</strong> {phone}</p>
        <p><strong>Inquiry Message:</strong> {message or 'General Inquiry'}</p>
        <hr/>
        <p><em>This lead has been auto-captured and saved to your Overarc administrative dashboard.</em></p>
        """
        send_resend_email(
            to_email=business_email,
            subject=f"⚡ New Lead Captured: {name} ({business_name})",
            html_body=email_html
        )
        
    return jsonify({"success": True, "message": "Lead saved successfully."})

@app.route('/api/leads', methods=['GET'])
def get_leads():
    bot_id = request.args.get('botId', '').strip().lower()
    if not bot_id:
        return jsonify({"error": "botId is required"}), 400
        
    if USE_SUPABASE:
        try:
            url = f"{SUPABASE_URL}/rest/v1/leads?bot=eq.{bot_id}"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            return jsonify(res.json())
        except Exception as e:
            print(f"[WARNING] Supabase error get_leads: {e}. Falling back to local leads.json")
            
    # Fallback to local leads.json
    leads = []
    if os.path.exists(LEADS_FILE):
        try:
            with open(LEADS_FILE, 'r', encoding='utf-8') as f:
                leads = json.load(f)
        except Exception:
            leads = []
            
    # Filter leads belonging to the target business
    filtered_leads = [l for l in leads if l.get('bot', 'overarc') == bot_id]
    return jsonify(filtered_leads)

@app.route('/chat/<bot_id>', methods=['GET'])
def serve_chat(bot_id):
    """Standalone chat page for clients without websites"""
    return send_from_directory('public', 'chat.html')

@app.route('/dashboard/<bot_id>', methods=['GET'])
def serve_dashboard(bot_id):
    # Host route to serve settings dashboard panel
    return send_from_directory('public', 'smartbot-dashboard.html')

@app.route('/api/settings', methods=['GET'])
def get_settings():
    bot_id = request.args.get('botId', '').strip().lower()
    if not bot_id:
        return jsonify({"error": "botId is required"}), 400
        
    businesses = load_businesses()
    if bot_id not in businesses:
        return jsonify({"error": "Business profile not found"}), 404
        
    return jsonify(businesses[bot_id])

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.json or {}
    bot_id = data.get('id', '').strip().lower()
    if not bot_id:
        return jsonify({"error": "Business ID is required"}), 400
        
    businesses = load_businesses()
    if bot_id not in businesses:
        return jsonify({"error": "Business profile not found"}), 404
        
    # Safely merge updates
    biz = businesses[bot_id]
    biz['name'] = data.get('name', biz.get('name')).strip()
    biz['emoji'] = data.get('emoji', biz.get('emoji')).strip()
    biz['color'] = data.get('color', biz.get('color')).strip()
    biz['dark_color'] = data.get('dark_color', biz.get('dark_color')).strip()
    biz['whatsapp'] = data.get('whatsapp', biz.get('whatsapp')).strip()
    biz['greeting'] = data.get('greeting', biz.get('greeting')).strip()
    biz['system_prompt'] = data.get('system_prompt', biz.get('system_prompt')).strip()
    biz['working_hours'] = data.get('working_hours', biz.get('working_hours')).strip()
    biz['location'] = data.get('location', biz.get('location')).strip()
    
    if 'faqs' in data:
        biz['faqs'] = data['faqs']
    if 'services' in data:
        biz['services'] = data['services']
        
    save_businesses(businesses)
    return jsonify({"success": True, "message": "Settings updated successfully."})


APPOINTMENTS_FILE = os.path.join(os.path.dirname(__file__), 'appointments.json')

def save_appointment_to_db(appt_data):
    if USE_SUPABASE:
        try:
            url = f"{SUPABASE_URL}/rest/v1/appointments"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            res = requests.post(url, headers=headers, json=appt_data)
            res.raise_for_status()
            return True
        except Exception as e:
            print(f"[WARNING] Supabase error save_appointment: {e}. Falling back to local JSON")
    appts = []
    if os.path.exists(APPOINTMENTS_FILE):
        try:
            with open(APPOINTMENTS_FILE, 'r', encoding='utf-8') as f:
                appts = json.load(f)
        except Exception:
            appts = []
    appts.append(appt_data)
    try:
        with open(APPOINTMENTS_FILE, 'w', encoding='utf-8') as f:
            json.dump(appts, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving appointment: {e}")
    return False

@app.route('/api/appointments', methods=['POST'])
def save_appointment():
    data = request.json or {}
    bot = data.get('bot', 'overarc').strip().lower()
    customer_name = data.get('customer_name', '').strip()
    customer_phone = data.get('customer_phone', '').strip()
    service = data.get('service', '').strip()
    preferred_date = data.get('preferred_date', '').strip()
    preferred_time = data.get('preferred_time', '').strip()
    
    if not customer_name or not customer_phone:
        return jsonify({"error": "Customer name and phone are required."}), 400

    appt_data = {
        "bot": bot,
        "customer_name": customer_name,
        "customer_phone": customer_phone,
        "service": service,
        "preferred_date": preferred_date,
        "preferred_time": preferred_time,
        "status": "pending",
        "timestamp": datetime.datetime.now().isoformat()
    }
    save_appointment_to_db(appt_data)
    print(f"[APPOINTMENT] New booking for [{bot}]: {customer_name} - {service} on {preferred_date} at {preferred_time}")

    # Email notification if configured
    if RESEND_API_KEY:
        businesses = load_businesses()
        business_email = "hello@overarc.co"
        business_name = "Overarc Agency"
        if bot in businesses:
            biz = businesses[bot]
            business_name = biz.get('name', 'Overarc Agency')
            business_email = biz.get('email', 'hello@overarc.co')
        email_html = f"""
        <h3>📅 New Appointment Booking</h3>
        <p><strong>Business:</strong> {business_name}</p>
        <hr/>
        <p><strong>Customer:</strong> {customer_name}</p>
        <p><strong>Phone:</strong> {customer_phone}</p>
        <p><strong>Service:</strong> {service}</p>
        <p><strong>Date:</strong> {preferred_date}</p>
        <p><strong>Time:</strong> {preferred_time}</p>
        <hr/>
        <p><em>Auto-captured by Overarc SmartBot.</em></p>
        """
        send_resend_email(
            to_email=business_email,
            subject=f"📅 New Appointment: {customer_name} - {service}",
            html_body=email_html
        )
    
    return jsonify({"success": True, "message": "Appointment booked successfully."})

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    bot_id = request.args.get('botId', '').strip().lower()
    if not bot_id:
        return jsonify({"error": "botId is required"}), 400

    if USE_SUPABASE:
        try:
            url = f"{SUPABASE_URL}/rest/v1/appointments?bot=eq.{bot_id}"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            return jsonify(res.json())
        except Exception as e:
            print(f"[WARNING] Supabase error get_appointments: {e}")

    appts = []
    if os.path.exists(APPOINTMENTS_FILE):
        try:
            with open(APPOINTMENTS_FILE, 'r', encoding='utf-8') as f:
                appts = json.load(f)
        except Exception:
            appts = []
    filtered = [a for a in appts if a.get('bot', 'overarc') == bot_id]
    return jsonify(filtered)


CHAT_LOGS_FILE = os.path.join(os.path.dirname(__file__), 'chat_logs.json')

@app.route('/api/chat-logs', methods=['POST'])
def save_chat_log():
    data = request.json or {}
    bot = data.get('bot', 'overarc').strip().lower()
    session_id = data.get('session_id', '')
    role = data.get('role', 'user')
    content = data.get('content', '').strip()
    
    if not content:
        return jsonify({"error": "Content is required."}), 400

    log_entry = {
        "bot": bot,
        "session_id": session_id,
        "role": role,
        "content": content,
        "timestamp": datetime.datetime.now().isoformat()
    }

    if USE_SUPABASE:
        try:
            url = f"{SUPABASE_URL}/rest/v1/chat_logs"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            res = requests.post(url, headers=headers, json=log_entry)
            res.raise_for_status()
            return jsonify({"success": True})
        except Exception as e:
            print(f"[WARNING] Supabase error save_chat_log: {e}")

    logs = []
    if os.path.exists(CHAT_LOGS_FILE):
        try:
            with open(CHAT_LOGS_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.append(log_entry)
    try:
        with open(CHAT_LOGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2)
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error saving chat log: {e}")
        return jsonify({"error": "Failed to save."}), 500


@app.route('/api/auth/check', methods=['POST'])
def check_auth():
    """Check admin password against env variable"""
    data = request.json or {}
    password = data.get('password', '').strip()
    if password == ADMIN_PASSWORD:
        return jsonify({"authorized": True})
    return jsonify({"authorized": False}), 401


@app.route('/api/widget-config', methods=['GET'])
def get_widget_config():
    bot_id = request.args.get('botId', '').strip().lower()
    if not bot_id:
        return jsonify({"error": "botId is required"}), 400
        
    businesses = load_businesses()
    if bot_id not in businesses:
        return jsonify({"error": "Business not found"}), 404
        
    biz = businesses[bot_id]
    return jsonify({
        "name": biz.get("name"),
        "emoji": biz.get("emoji"),
        "color": biz.get("color"),
        "dark_color": biz.get("dark_color"),
        "greeting": biz.get("greeting"),
        "quick_replies": biz.get("quick_replies", [])
    })

if __name__ == '__main__':
    print("Starting Overarc Python Backend on port 5000...")
    print("Access the site at: http://localhost:5000")
    app.run(port=5000, debug=True)
