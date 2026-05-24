import os
import re
import requests
import json
import datetime
import functools
import secrets
import io
import uuid
from flask import Flask, request, jsonify, send_from_directory, g
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import bcrypt
import jwt
import csv

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    print("[WARNING] APScheduler not installed. Keep-alive ping will be disabled.")

# =============================================================================
# RAG-specific imports
# =============================================================================
try:
    from PyPDF2 import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PdfReader = None
    PDF_SUPPORT = False
    print("[WARNING] PyPDF2 not installed. PDF upload will be unavailable.")

# =============================================================================
# SECURITY FIX 1: Load environment variables
# =============================================================================
load_dotenv()
if not os.getenv("OPENROUTER_API_KEY"):
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
    load_dotenv(dotenv_path=dotenv_path)

app = Flask(__name__, static_folder='public', static_url_path='')

# =============================================================================
# SECURITY FIX 2: Restrict CORS to specific origins only
# =============================================================================
CORS(app, resources={r"/api/*": {"origins": "*"}})

# =============================================================================
# SECURITY FIX 3: Rate Limiting for /api/chat
# =============================================================================
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[]
)

# =============================================================================
# Configuration loaded from environment
# =============================================================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "perplexity/pplx-embed-v1-0.6b")
BUSINESSES_FILE = os.path.join(os.path.dirname(__file__), 'businesses.json')
SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "").strip()
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_KEY)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123").strip()
SUPER_ADMIN_KEY = os.getenv("SUPER_ADMIN_KEY", "").strip()
if not SUPER_ADMIN_KEY:
    raise RuntimeError("SUPER_ADMIN_KEY environment variable is not set. Add it to your .env file.")

# =============================================================================
# SECURITY FIX 4: JWT Secret
# =============================================================================
JWT_SECRET = os.getenv("JWT_SECRET", "").strip()
if not JWT_SECRET:
    raise RuntimeError("JWT_SECRET environment variable is not set.")

JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# =============================================================================
# SECURITY FIX 5: Input validation constants
# =============================================================================
FIELD_LIMITS = {
    "name": 100,
    "customer_name": 100,
    "phone": 30,
    "customer_phone": 30,
    "message": 2000,
    "bot": 50,
    "bot_id": 50,
    "botId": 50,
    "id": 50,
    "password": 128,
    "session_id": 100,
    "role": 20,
    "content": 2000,
    "service": 200,
    "preferred_date": 50,
    "preferred_time": 50,
    "status": 50,
    "topic": 500,
    "business": 200,
    "email": 200,
    "emoji": 50,
    "color": 50,
    "dark_color": 50,
    "whatsapp": 50,
    "greeting": 500,
    "system_prompt": 10000,
    "working_hours": 500,
    "location": 500,
    "default": 500,
    "source_name": 200,
    "policies": 5000,
    "extracted_hours": 500,
    "suggested_greeting": 500
}

# =============================================================================
# SECURITY FIX 6: Bot ID sanitizer
# =============================================================================
def sanitize_bot_id(bot_id):
    """Sanitize bot_id — only allow alphanumeric and hyphens."""
    if not isinstance(bot_id, str):
        return ""
    return re.sub(r'[^a-zA-Z0-9\-]', '', bot_id).strip().lower()

# =============================================================================
# SECURITY FIX 7: Input validation helper
# =============================================================================
def validate_field_lengths(data, max_length=None):
    """Validate that all string fields in data do not exceed character limits."""
    if not isinstance(data, dict):
        return True, ""
    for key, value in data.items():
        if isinstance(value, str):
            limit = FIELD_LIMITS.get(key, FIELD_LIMITS["default"])
            if max_length is not None:
                limit = min(limit, max_length)
            if len(value) > limit:
                return False, f"Field '{key}' exceeds maximum length of {limit} characters."
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    valid, err = validate_field_lengths(item, max_length)
                    if not valid:
                        return False, err
    return True, ""

# =============================================================================
# Password strength validation
# =============================================================================
COMMON_PASSWORDS = {
    "123456", "password", "12345678", "qwerty", "123456789",
    "12345", "1234", "111111", "1234567", "sunshine",
    "qwerty123", "0", "admin", "letmein", "123123",
    "dragon", "baseball", "abc123", "monkey", "password123"
}

def validate_password_strength(password):
    """Validate password strength. Returns (is_valid, error_message)."""
    if not isinstance(password, str) or not password:
        return False, "Password is required."
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number."
    if password.lower() in COMMON_PASSWORDS:
        return False, "This password is too common. Please choose a stronger password."
    return True, ""

# =============================================================================
# SECURITY FIX 8: JWT Authentication decorator
# =============================================================================
def jwt_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authentication required. Provide a valid Bearer token."}), 401
        token = auth_header.split(" ", 1)[1] if " " in auth_header else ""
        if not token:
            return jsonify({"error": "Authentication token is missing."}), 401
        try:
            payload = jwt.decode(
                token,
                JWT_SECRET,
                algorithms=[JWT_ALGORITHM],
                options={
                    "require": ["exp", "bot_id"],
                    "verify_exp": True
                }
            )
            g.bot_id = payload.get("bot_id", "")
            g.token_payload = payload
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired. Please login again."}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": f"Invalid authentication token: {str(e)}"}), 401
        return f(*args, **kwargs)
    return decorated_function

# =============================================================================
# Global error handlers
# =============================================================================
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found."}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed."}), 405

@app.errorhandler(429)
def ratelimit_handler(error):
    return jsonify({"error": "Too many requests. Please slow down."}), 429

@app.errorhandler(500)
def internal_error(error):
    print(f"[ERROR] Internal server error: {error}")
    return jsonify({"error": "An internal server error occurred."}), 500

@app.errorhandler(Exception)
def unhandled_exception(error):
    print(f"[ERROR] Unhandled exception: {error}")
    return jsonify({"error": "An unexpected error occurred."}), 500

# Log the database status on start
if USE_SUPABASE:
    print(f"[DATABASE] Core: Supabase PostgreSQL (URL: {SUPABASE_URL})")
else:
    print("[DATABASE] Core: Local JSON fallback (businesses.json & leads.json)")

# =============================================================================
# Email notification function
# =============================================================================
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

# =============================================================================
# Database helpers
# =============================================================================
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
            return {biz["id"]: biz for biz in records}
        except Exception as e:
            print(f"[WARNING] Supabase error load_businesses: {e}. Falling back to local businesses.json")
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
            url = f"{SUPABASE_URL}/rest/v1/businesses"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            }
            payload = list(data.values())
            res = requests.post(url, headers=headers, json=payload)
            res.raise_for_status()
            return True
        except Exception as e:
            print(f"[WARNING] Supabase error save_businesses: {e}. Falling back to local businesses.json")
    try:
        with open(BUSINESSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error writing businesses.json: {e}")
    return False

def update_single_business(bot_id, business_data):
    """Update a single business record in the database (Supabase or local JSON)."""
    if USE_SUPABASE:
        try:
            url = f"{SUPABASE_URL}/rest/v1/businesses?id=eq.{bot_id}"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            }
            res = requests.patch(url, headers=headers, json=business_data)
            res.raise_for_status()
            return True
        except Exception as e:
            print(f"[WARNING] Supabase error update_single_business: {e}. Falling back to local businesses.json")
    businesses = {}
    if os.path.exists(BUSINESSES_FILE):
        try:
            with open(BUSINESSES_FILE, 'r', encoding='utf-8') as f:
                businesses = json.load(f)
        except Exception as e:
            print(f"Error reading businesses.json: {e}")
            return False
    if bot_id not in businesses:
        businesses[bot_id] = {"id": bot_id}
    businesses[bot_id].update(business_data)
    try:
        with open(BUSINESSES_FILE, 'w', encoding='utf-8') as f:
            json.dump(businesses, f, indent=2)
        return True
    except Exception as e:
        print(f"Error writing businesses.json: {e}")
        return False

# =============================================================================
# RAG — Embedding function using OpenRouter (perplexity/pplx-embed-v1-0.6b)
# =============================================================================

def get_embedding(text):
    """
    Generate a 1536-dimensional embedding vector for the given text using
    OpenRouter's perplexity/pplx-embed-v1-0.6b model.
    
    Args:
        text: The input text to embed (string)
    
    Returns:
        A list of 1536 floats representing the embedding vector,
        or None if the request fails.
    """
    if not OPENROUTER_API_KEY:
        print("[RAG ERROR] OPENROUTER_API_KEY not set — cannot generate embeddings.")
        return None
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/embeddings",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "Overarc Chatbot Backend"
            },
            json={
                "model": EMBEDDING_MODEL,
                "input": text
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        embedding = result['data'][0]['embedding']
        return embedding
    except Exception as e:
        print(f"[RAG ERROR] Embedding generation failed: {e}")
        return None


def chunk_text(text, chunk_size=500, overlap=50):
    """
    Split text into overlapping chunks for embedding and retrieval.
    
    Args:
        text: The full text to chunk (string)
        chunk_size: Maximum characters per chunk (default: 500)
        overlap: Character overlap between adjacent chunks (default: 50)
    
    Returns:
        List of chunk strings
    """
    if not text:
        return []
    
    # Clean whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    chunks = []
    start = 0
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        if end >= text_len:
            # Last chunk — take the remainder
            chunks.append(text[start:].strip())
            break
        
        # Try to break at a sentence boundary or space for cleaner chunks
        search_end = min(end + overlap, text_len)
        # Look for sentence-ending punctuation within overlap region
        split_point = -1
        for sep in ['\n\n', '\n', '. ', '! ', '? ', ', ', ' ']:
            pos = text.rfind(sep, start, search_end)
            if pos > start:
                split_point = pos + len(sep)
                break
        
        if split_point > start:
            chunks.append(text[start:split_point].strip())
            start = split_point
        else:
            # No good break point — just cut at chunk_size
            chunks.append(text[start:end].strip())
            start = end
    
    return chunks


def analyze_document_with_ai(text, bot_id):
    """
    Use OpenRouter (Gemini 2.5 Flash) to analyze a document and extract
    structured business data: services, FAQs, policies, hours, etc.
    
    Args:
        text: The full extracted document text
        bot_id: The business bot ID (for context)
    
    Returns:
        Dictionary with extracted fields and confidence score
    """
    if not OPENROUTER_API_KEY:
        return {
            "detected_type": "general_info",
            "extracted_services": [],
            "extracted_faqs": [],
            "extracted_policies": [],
            "extracted_hours": "",
            "confidence": 0.0,
            "suggested_greeting": ""
        }
    
    prompt = f"""You are an AI document analyzer for a business chatbot configuration system.
Analyze the following document text and extract structured information.

Return ONLY valid JSON (no markdown, no code fences) with this exact structure:
{{
  "detected_type": "restaurant_menu" | "clinic_services" | "policy_document" | "general_info",
  "extracted_services": [{{"name": "Service Name", "price": "Price or 'N/A'"}}],
  "extracted_faqs": [{{"q": "Question", "a": "Answer"}}],
  "extracted_policies": ["Policy statement 1", "Policy statement 2"],
  "extracted_hours": "Business hours string or empty",
  "confidence": 0.0-1.0,
  "suggested_greeting": "Suggested greeting message or empty"
}}

Rules:
- Extract services/menu items with prices if found. Price can be 'N/A' if not mentioned.
- Extract FAQs only if clear question-answer patterns are detected.
- Extract business policies (cancellation, refund, terms, etc.) as policy statements.
- Extract business hours if mentioned anywhere.
- Set confidence based on how clearly the document type can be identified.
- Suggest a greeting only if the document clearly indicates one.

Document text for bot_id "{bot_id}":
{text[:8000]}
"""
    
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
                "model": "google/gemini-2.5-flash",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
                "max_tokens": 2000
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        content = result['choices'][0]['message']['content'].strip()
        
        # Strip markdown code fences if present
        content = re.sub(r'^```(?:json)?\s*', '', content)
        content = re.sub(r'\s*```$', '', content)
        
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        print(f"[RAG ERROR] Document analysis failed: {e}")
        return {
            "detected_type": "general_info",
            "extracted_services": [],
            "extracted_faqs": [],
            "extracted_policies": [],
            "extracted_hours": "",
            "confidence": 0.0,
            "suggested_greeting": ""
        }


def store_document_chunks(bot_id, chunks, source_name, embeddings=None):
    """
    Store document chunks with embeddings in Supabase document_chunks table.
    Falls back to local JSON storage if Supabase is not configured.
    
    Args:
        bot_id: The business bot ID
        chunks: List of text chunks
        source_name: Original filename or source label
        embeddings: Optional list of embedding vectors (if None, generates them)
    
    Returns:
        Number of chunks successfully stored
    """
    if USE_SUPABASE:
        try:
            stored_count = 0
            for i, chunk in enumerate(chunks):
                embedding = embeddings[i] if embeddings else get_embedding(chunk)
                if embedding is None:
                    print(f"[RAG WARNING] Skipping chunk {i} — embedding failed.")
                    continue
                
                payload = {
                    "bot_id": bot_id,
                    "content": chunk,
                    "embedding": json.dumps(embedding),  # Supabase accepts JSON arrays
                    "source_name": source_name
                }
                
                url = f"{SUPABASE_URL}/rest/v1/document_chunks"
                headers = {
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json"
                }
                res = requests.post(url, headers=headers, json=payload)
                res.raise_for_status()
                stored_count += 1
            
            return stored_count
        except Exception as e:
            print(f"[WARNING] Supabase error store_document_chunks: {e}. Falling back to local JSON.")
    
    # Local fallback: store in a JSON file
    chunks_file = os.path.join(os.path.dirname(__file__), f'document_chunks_{bot_id}.json')
    existing = []
    if os.path.exists(chunks_file):
        try:
            with open(chunks_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except Exception:
            existing = []
    
    stored_count = 0
    for i, chunk in enumerate(chunks):
        embedding = embeddings[i] if embeddings else get_embedding(chunk)
        if embedding is None:
            continue
        existing.append({
            "id": str(uuid.uuid4()),
            "bot_id": bot_id,
            "content": chunk,
            "embedding": embedding,
            "source_name": source_name,
            "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        })
        stored_count += 1
    
    try:
        with open(chunks_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2)
    except Exception as e:
        print(f"Error writing document chunks to file: {e}")
    
    return stored_count


def store_document_metadata(bot_id, source_name, source_type, chunk_count, extraction_summary):
    """
    Store document metadata in Supabase documents table.
    Falls back to local JSON.
    """
    if USE_SUPABASE:
        try:
            payload = {
                "bot_id": bot_id,
                "source_name": source_name,
                "source_type": source_type,
                "chunk_count": chunk_count,
                "extraction_summary": json.dumps(extraction_summary)
            }
            url = f"{SUPABASE_URL}/rest/v1/documents"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            res = requests.post(url, headers=headers, json=payload)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            print(f"[WARNING] Supabase error store_document_metadata: {e}. Falling back to local JSON.")
    
    # Local fallback
    meta_file = os.path.join(os.path.dirname(__file__), f'documents_{bot_id}.json')
    existing = []
    if os.path.exists(meta_file):
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                existing = json.load(f)
        except Exception:
            existing = []
    
    record = {
        "id": str(uuid.uuid4()),
        "bot_id": bot_id,
        "source_name": source_name,
        "source_type": source_type,
        "chunk_count": chunk_count,
        "extraction_summary": extraction_summary,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
    existing.append(record)
    
    try:
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=2)
    except Exception as e:
        print(f"Error writing document metadata: {e}")
    
    return record


def search_relevant_chunks(bot_id, query_embedding, threshold=0.75, top_k=3):
    """
    Search for the most relevant document chunks for a given bot using
    cosine similarity via Supabase's match_documents function.
    
    Falls back to brute-force local search if Supabase is not configured.
    
    Args:
        bot_id: The business bot ID
        query_embedding: The embedding vector of the user's query
        threshold: Minimum cosine similarity threshold (default: 0.75)
        top_k: Maximum number of chunks to return (default: 3)
    
    Returns:
        List of dicts with keys: content, source_name, similarity
    """
    if USE_SUPABASE:
        try:
            url = f"{SUPABASE_URL}/rest/v1/rpc/match_documents"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json"
            }
            payload = {
                "query_embedding": query_embedding,
                "match_bot_id": bot_id,
                "match_threshold": threshold,
                "match_count": top_k
            }
            res = requests.post(url, headers=headers, json=payload)
            res.raise_for_status()
            results = res.json()
            return [
                {
                    "content": r["content"],
                    "source_name": r["source_name"],
                    "similarity": r["similarity"]
                }
                for r in results
            ]
        except Exception as e:
            print(f"[RAG WARNING] Supabase match_documents failed: {e}. Falling back to local search.")
    
    # Local fallback: brute-force cosine similarity on local JSON file
    chunks_file = os.path.join(os.path.dirname(__file__), f'document_chunks_{bot_id}.json')
    if not os.path.exists(chunks_file):
        return []
    
    try:
        with open(chunks_file, 'r', encoding='utf-8') as f:
            chunks = json.load(f)
    except Exception:
        return []
    
    if not chunks or not query_embedding:
        return []
    
    import math
    
    def cosine_similarity(a, b):
        """Compute cosine similarity between two vectors."""
        if len(a) != len(b):
            return 0.0
        dot = sum(ai * bi for ai, bi in zip(a, b))
        norm_a = math.sqrt(sum(ai * ai for ai in a))
        norm_b = math.sqrt(sum(bi * bi for bi in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
    
    scored = []
    for chunk in chunks:
        emb = chunk.get("embedding")
        if not emb:
            continue
        sim = cosine_similarity(query_embedding, emb)
        if sim >= threshold:
            scored.append({
                "content": chunk["content"],
                "source_name": chunk.get("source_name", "unknown"),
                "similarity": sim
            })
    
    scored.sort(key=lambda x: x["similarity"], reverse=True)
    return scored[:top_k]


def extract_text_from_pdf(file_storage):
    """
    Extract text from an uploaded PDF file using PyPDF2.
    
    Args:
        file_storage: A Werkzeug FileStorage object from Flask
    
    Returns:
        Extracted text as string, or None if extraction fails
    """
    if not PDF_SUPPORT:
        print("[RAG ERROR] PyPDF2 not installed. Cannot extract PDF text.")
        return None
    
    try:
        pdf_file = io.BytesIO(file_storage.read())
        reader = PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip()
    except Exception as e:
        print(f"[RAG ERROR] PDF text extraction failed: {e}")
        return None

# =============================================================================
# Static file routes
# =============================================================================
@app.route('/')
def serve_index():
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if 'smartbot-admin' in path.lower():
        return jsonify({"error": "Forbidden: Administrative console access is restricted."}), 403
    return send_from_directory('public', path)

# =============================================================================
# Health check
# =============================================================================
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "timestamp": datetime.datetime.now().isoformat(),
        "database": "supabase" if USE_SUPABASE else "local_json"
    }), 200

# =============================================================================
# Auth endpoints
# =============================================================================
@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    data = request.json or {}
    valid, err = validate_field_lengths(data)
    if not valid:
        return jsonify({"error": err}), 400
    bot_id = sanitize_bot_id(data.get('botId', '').strip().lower())
    password = data.get('password', '')
    if not bot_id:
        return jsonify({"error": "botId is required."}), 400
    if not password:
        return jsonify({"error": "Password is required."}), 400
    businesses = load_businesses()
    if bot_id not in businesses:
        return jsonify({"error": "Invalid botId or password."}), 401
    biz = businesses[bot_id]
    stored_hash = biz.get('password_hash', '')
    if not stored_hash:
        return jsonify({"error": "Invalid botId or password."}), 401
    try:
        password_match = bcrypt.checkpw(
            password.encode('utf-8'),
            stored_hash.encode('utf-8')
        )
    except Exception as e:
        print(f"[WARNING] bcrypt check failed: {e}")
        return jsonify({"error": "Invalid botId or password."}), 401
    if not password_match:
        return jsonify({"error": "Invalid botId or password."}), 401
    now = datetime.datetime.now(datetime.timezone.utc)
    expiry = now + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
    token_payload = {
        "bot_id": bot_id,
        "iat": int(now.timestamp()),
        "exp": int(expiry.timestamp()),
        "jti": secrets.token_hex(16)
    }
    token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return jsonify({
        "token": token,
        "bot_id": bot_id,
        "expires_at": expiry.isoformat()
    }), 200

@app.route('/api/auth/check', methods=['POST'])
def check_auth():
    data = request.json or {}
    valid, err = validate_field_lengths(data)
    if not valid:
        return jsonify({"error": err}), 400
    password = data.get('password', '').strip()
    if password == ADMIN_PASSWORD:
        return jsonify({"authorized": True})
    return jsonify({"authorized": False}), 401

# =============================================================================
# /api/chat — Modified with RAG Retrieval
# =============================================================================
@app.route('/api/chat', methods=['POST'])
@limiter.limit("30 per minute")
def chat():
    if not OPENROUTER_API_KEY:
        return jsonify({"error": "API key not found. Please ensure it is in the .env file."}), 500

    data = request.json or {}
    valid, err = validate_field_lengths(data)
    if not valid:
        return jsonify({"error": err}), 400

    bot_id = sanitize_bot_id(data.get('bot', 'overarc').strip().lower())
    user_message = data.get('message', '').strip()
    history = data.get('history', [])

    if not user_message:
        return jsonify({"error": "Message is required."}), 400

    if len(user_message) > FIELD_LIMITS["content"]:
        return jsonify({"error": f"Message exceeds maximum length of {FIELD_LIMITS['content']} characters."}), 400

    # Load business config
    businesses = load_businesses()
    if bot_id in businesses:
        biz = businesses[bot_id]

        # =================================================================
        # SUBSCRIPTION STATUS CHECK
        # =================================================================
        status = biz.get('status', 'active')
        if status == 'suspended':
            return jsonify({"reply": "This service is currently unavailable. Please contact the business directly."})
        elif status == 'trial':
            # Trial period: 14 days from created_at
            created_at_str = biz.get('created_at', '')
            if created_at_str:
                try:
                    created_at = datetime.datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=datetime.timezone.utc)
                    now_utc = datetime.datetime.now(datetime.timezone.utc)
                    trial_end = created_at + datetime.timedelta(days=14)
                    if now_utc > trial_end:
                        return jsonify({"reply": "This service is currently unavailable. Please contact the business directly."})
                except Exception:
                    pass  # If we can't parse date, allow it

        system_prompt = biz.get('system_prompt', '')
        
        services = biz.get('services', [])
        if services:
            services_text = "\n".join([f"- {s.get('name')}: {s.get('price')}" for s in services])
            system_prompt = system_prompt.replace("{SERVICES_LIST}", services_text)
            
        faqs = biz.get('faqs', [])
        if faqs:
            faqs_text = "\n".join([f"Q: {f.get('q')}\nA: {f.get('a')}" for f in faqs])
            system_prompt = system_prompt.replace("{FAQS_LIST}", faqs_text)
    else:
        system_prompt = """You are the AI Assistant for Overarc, a premium web development and AI automation agency. 
Your goal is to confidently and professionally answer questions about our custom AI chatbots and services.
Key information to know:
- We build custom AI chatbots for businesses that answer FAQs, capture leads, and book appointments 24/7.
- Our chatbots are delivered in 3 days.
- Pricing is $150 for Starter, $250 for Pro, and $400 for Premium. (Prices are one-time setup).
- We offer an optional $30/month plan for hosting, updates & priority support.
- Keep responses short, punchy, and highly professional. Limit responses to 2-3 sentences.
- If asked complex questions, direct the user to contact us on WhatsApp (+923249116764) or email shabir@overarc.co.
- IMPORTANT STRICT RULE: If the user asks ANY question that is NOT about Overarc, our chatbots, our services, or web development, politely decline to answer. Say something like: "I'm a specialized assistant for Overarc and can only answer questions related to our web development and AI chatbot services. How can I help you with those?" Never write code, solve math problems, or discuss general topics."""

    # =============================================================================
    # RAG RETRIEVAL: Embed the user's message and search for relevant chunks
    # =============================================================================
    try:
        user_embedding = get_embedding(user_message)
        if user_embedding:
            relevant_chunks = search_relevant_chunks(bot_id, user_embedding, threshold=0.75, top_k=3)
            if relevant_chunks:
                chunks_text = "\n\n".join([
                    f"[Source: {c['source_name']}] (relevance: {c['similarity']:.2f})\n{c['content']}"
                    for c in relevant_chunks
                ])
                # Inject RAG context into the system prompt
                rag_context = f"\n\nRELEVANT BUSINESS INFORMATION:\n{chunks_text}\n\nUse this information to answer the customer."
                system_prompt += rag_context
                print(f"[RAG] Injected {len(relevant_chunks)} relevant chunks into system prompt for bot '{bot_id}'")
            else:
                print(f"[RAG] No chunks found above threshold for bot '{bot_id}' — using JSON config only")
        else:
            print(f"[RAG] Could not generate embedding for user message — skipping RAG retrieval")
    except Exception as e:
        print(f"[RAG ERROR] Retrieval failed: {e} — falling back to standard chat")

    # Build messages array
    clean_history = []
    for msg in history[-10:]:
        if isinstance(msg, dict):
            role = msg.get('role')
            content = msg.get('content')
            if role in ['user', 'assistant'] and content:
                if len(content) > FIELD_LIMITS["content"]:
                    continue
                clean_history.append({"role": role, "content": str(content).strip()})

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
                "model": "google/gemini-2.5-flash",
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

# =============================================================================
# Lead saving helper
# =============================================================================
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

# =============================================================================
# /api/leads POST
# =============================================================================
@app.route('/api/leads', methods=['POST'])
def save_lead():
    data = request.json or {}
    valid, err = validate_field_lengths(data)
    if not valid:
        return jsonify({"error": err}), 400
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    message = data.get('message', '').strip()
    bot = sanitize_bot_id(data.get('bot', 'overarc').strip().lower())
    if not name or not phone:
        return jsonify({"error": "Name and phone number are required."}), 400
    if len(name) > FIELD_LIMITS["name"]:
        return jsonify({"error": f"Name exceeds maximum length of {FIELD_LIMITS['name']} characters."}), 400
    if len(phone) > FIELD_LIMITS["phone"]:
        return jsonify({"error": f"Phone number exceeds maximum length of {FIELD_LIMITS['phone']} characters."}), 400
    businesses = load_businesses()
    business_name = "Overarc Agency"
    business_email = "shabir@overarc.co"
    if bot in businesses:
        biz = businesses[bot]
        business_name = biz.get('name', 'Overarc Agency')
        business_email = biz.get('email', 'shabir@overarc.co')
    lead_data = {
        "bot": bot,
        "business": business_name,
        "name": name,
        "phone": phone,
        "timestamp": datetime.datetime.now().isoformat(),
        "topic": message or "General Inquiry"
    }
    save_lead_to_db(lead_data)
    print(f"New Lead Captured [{business_name}]: {name} ({phone}) - Topic: {message}")
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
@jwt_required
def get_leads():
    bot_id = sanitize_bot_id(request.args.get('botId', '').strip().lower())
    if not bot_id:
        return jsonify({"error": "botId is required"}), 400
    token_bot_id = g.bot_id
    if token_bot_id and token_bot_id != bot_id:
        return jsonify({"error": "Access denied. Token does not match requested bot."}), 403
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
    leads = []
    if os.path.exists(LEADS_FILE):
        try:
            with open(LEADS_FILE, 'r', encoding='utf-8') as f:
                leads = json.load(f)
        except Exception:
            leads = []
    filtered_leads = [l for l in leads if l.get('bot', 'overarc') == bot_id]
    return jsonify(filtered_leads)

# =============================================================================
# Chat page and dashboard routes
# =============================================================================
@app.route('/chat/<bot_id>', methods=['GET'])
def serve_chat(bot_id):
    return send_from_directory('public', 'chat.html')

@app.route('/dashboard/<bot_id>', methods=['GET'])
def serve_dashboard(bot_id):
    return send_from_directory('public', 'smartbot-dashboard.html')

# =============================================================================
# Settings endpoints
# =============================================================================
@app.route('/api/settings', methods=['GET'])
@jwt_required
def get_settings():
    bot_id = sanitize_bot_id(request.args.get('botId', '').strip().lower())
    if not bot_id:
        return jsonify({"error": "botId is required"}), 400
    token_bot_id = g.bot_id
    if token_bot_id and token_bot_id != bot_id:
        return jsonify({"error": "Access denied. Token does not match requested bot."}), 403
    businesses = load_businesses()
    if bot_id not in businesses:
        return jsonify({"error": "Business profile not found"}), 404
    biz = dict(businesses[bot_id])
    biz.pop('password_hash', None)
    return jsonify(biz)

@app.route('/api/settings', methods=['POST'])
@jwt_required
def update_settings():
    data = request.json or {}
    valid, err = validate_field_lengths(data)
    if not valid:
        return jsonify({"error": err}), 400
    bot_id = sanitize_bot_id(data.get('id', '').strip().lower())
    if not bot_id:
        return jsonify({"error": "Business ID is required"}), 400
    token_bot_id = g.bot_id
    if token_bot_id and token_bot_id != bot_id:
        return jsonify({"error": "Access denied. Token does not match requested bot."}), 403
    businesses = load_businesses()
    if bot_id not in businesses:
        return jsonify({"error": "Business profile not found"}), 404
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

# =============================================================================
# Appointment endpoints
# =============================================================================
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
    valid, err = validate_field_lengths(data)
    if not valid:
        return jsonify({"error": err}), 400
    bot = sanitize_bot_id(data.get('bot', 'overarc').strip().lower())
    customer_name = data.get('customer_name', '').strip()
    customer_phone = data.get('customer_phone', '').strip()
    service = data.get('service', '').strip()
    preferred_date = data.get('preferred_date', '').strip()
    preferred_time = data.get('preferred_time', '').strip()
    if not customer_name or not customer_phone:
        return jsonify({"error": "Customer name and phone are required."}), 400
    if len(customer_name) > FIELD_LIMITS["customer_name"]:
        return jsonify({"error": f"Customer name exceeds maximum length of {FIELD_LIMITS['customer_name']} characters."}), 400
    if len(customer_phone) > FIELD_LIMITS["customer_phone"]:
        return jsonify({"error": f"Phone number exceeds maximum length of {FIELD_LIMITS['customer_phone']} characters."}), 400
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
    if RESEND_API_KEY:
        businesses = load_businesses()
        business_email = "shabir@overarc.co"
        business_name = "Overarc Agency"
        if bot in businesses:
            biz = businesses[bot]
            business_name = biz.get('name', 'Overarc Agency')
            business_email = biz.get('email', 'shabir@overarc.co')
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
@jwt_required
def get_appointments():
    bot_id = sanitize_bot_id(request.args.get('botId', '').strip().lower())
    if not bot_id:
        return jsonify({"error": "botId is required"}), 400
    token_bot_id = g.bot_id
    if token_bot_id and token_bot_id != bot_id:
        return jsonify({"error": "Access denied. Token does not match requested bot."}), 403
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

# =============================================================================
# Chat logs endpoint
# =============================================================================
CHAT_LOGS_FILE = os.path.join(os.path.dirname(__file__), 'chat_logs.json')

@app.route('/api/chat-logs', methods=['POST'])
def save_chat_log():
    data = request.json or {}
    valid, err = validate_field_lengths(data)
    if not valid:
        return jsonify({"error": err}), 400
    bot = sanitize_bot_id(data.get('bot', 'overarc').strip().lower())
    session_id = data.get('session_id', '')
    role = data.get('role', 'user')
    content = data.get('content', '').strip()
    if not content:
        return jsonify({"error": "Content is required."}), 400
    if len(content) > FIELD_LIMITS["content"]:
        return jsonify({"error": f"Content exceeds maximum length of {FIELD_LIMITS['content']} characters."}), 400
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

# =============================================================================
# Widget config endpoint
# =============================================================================
@app.route('/api/widget-config', methods=['GET'])
def get_widget_config():
    bot_id = sanitize_bot_id(request.args.get('botId', '').strip().lower())
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

# =============================================================================
# Admin create client endpoint
# =============================================================================
@app.route('/api/admin/create-client', methods=['POST'])
def admin_create_client():
    admin_key = request.headers.get("X-Admin-Key", "").strip()
    if not admin_key or admin_key != SUPER_ADMIN_KEY:
        return jsonify({"error": "Unauthorized. Valid admin key required."}), 401
    data = request.json or {}
    valid, err = validate_field_lengths(data)
    if not valid:
        return jsonify({"error": err}), 400
    bot_id = sanitize_bot_id(data.get('botId', '').strip().lower())
    business_name = data.get('businessName', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip()
    if not bot_id:
        return jsonify({"error": "botId is required."}), 400
    if not business_name:
        return jsonify({"error": "businessName is required."}), 400
    if not password:
        return jsonify({"error": "Password is required."}), 400
    pw_valid, pw_error = validate_password_strength(password)
    if not pw_valid:
        return jsonify({"error": pw_error}), 400
    businesses = load_businesses()
    if bot_id in businesses:
        return jsonify({"error": f"A business with botId '{bot_id}' already exists."}), 409
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        password_hash = hashed.decode('utf-8')
    except Exception as e:
        print(f"[ERROR] bcrypt hashing failed: {e}")
        return jsonify({"error": "Failed to hash password."}), 500
    new_business = {
        "id": bot_id,
        "name": business_name,
        "password_hash": password_hash,
        "email": email,
        "emoji": data.get('emoji', '🤖'),
        "color": data.get('color', '#10B981'),
        "dark_color": data.get('dark_color', '#059669'),
        "whatsapp": data.get('whatsapp', ''),
        "greeting": data.get('greeting', f'Hello! Welcome to {business_name}. How can I help you today?'),
        "system_prompt": data.get('system_prompt', f"You are a helpful assistant for {business_name}.\n\nYOUR JOB:\n1. Greet visitors warmly\n2. Answer questions about services, pricing, and availability\n3. Capture name + phone number of interested visitors\n4. Keep responses SHORT — max 3 sentences\n5. Respond in the same language the user writes in\n6. STRICT RULE: If the user asks ANY question not related to {business_name} or its services, politely decline to answer. Say something like: \"I'm a specialized assistant for {business_name}. I can only help with our services. How can I assist you today?\""),
        "working_hours": data.get('working_hours', ''),
        "location": data.get('location', ''),
        "faqs": data.get('faqs', []),
        "services": data.get('services', []),
        "quick_replies": data.get('quick_replies', [
            "Book appointment",
            "Services & prices",
            "Working hours",
            "Location"
        ])
    }
    new_business.pop('password', None)
    businesses[bot_id] = new_business
    if not save_businesses(businesses):
        return jsonify({"error": "Failed to save business record."}), 500
    login_url = f"{request.host_url}dashboard/{bot_id}"
    print(f"[ADMIN] New client created: {business_name} (botId: {bot_id})")
    return jsonify({
        "success": True,
        "botId": bot_id,
        "loginUrl": login_url
    }), 201

# =============================================================================
# Client change password endpoint
# =============================================================================
@app.route('/api/client/change-password', methods=['POST'])
@jwt_required
def client_change_password():
    data = request.json or {}
    valid, err = validate_field_lengths(data)
    if not valid:
        return jsonify({"error": err}), 400
    bot_id = g.bot_id
    current_password = data.get('currentPassword', '')
    new_password = data.get('newPassword', '')
    if not current_password:
        return jsonify({"error": "currentPassword is required."}), 400
    if not new_password:
        return jsonify({"error": "newPassword is required."}), 400
    businesses = load_businesses()
    if bot_id not in businesses:
        return jsonify({"error": "Business profile not found."}), 404
    biz = businesses[bot_id]
    stored_hash = biz.get('password_hash', '')
    if not stored_hash:
        return jsonify({"error": "No password set for this account."}), 500
    try:
        password_match = bcrypt.checkpw(
            current_password.encode('utf-8'),
            stored_hash.encode('utf-8')
        )
    except Exception as e:
        print(f"[WARNING] bcrypt check failed during password change: {e}")
        return jsonify({"error": "Current password is incorrect."}), 401
    if not password_match:
        return jsonify({"error": "Current password is incorrect."}), 401
    pw_valid, pw_error = validate_password_strength(new_password)
    if not pw_valid:
        return jsonify({"error": pw_error}), 400
    try:
        new_hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        new_password_hash = new_hashed.decode('utf-8')
    except Exception as e:
        print(f"[ERROR] bcrypt hashing failed during password change: {e}")
        return jsonify({"error": "Failed to hash new password."}), 500
    success = update_single_business(bot_id, {"password_hash": new_password_hash})
    if not success:
        return jsonify({"error": "Failed to update password."}), 500
    now = datetime.datetime.now(datetime.timezone.utc)
    expiry = now + datetime.timedelta(hours=JWT_EXPIRATION_HOURS)
    token_payload = {
        "bot_id": bot_id,
        "iat": int(now.timestamp()),
        "exp": int(expiry.timestamp()),
        "jti": secrets.token_hex(16)
    }
    new_token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    print(f"[SECURITY] Password changed for client: {bot_id}")
    return jsonify({
        "success": True,
        "message": "Password changed successfully.",
        "token": new_token,
        "expires_at": expiry.isoformat()
    }), 200

# =============================================================================
# =============================================================================
# RAG ENDPOINTS — Document Upload & Management
# =============================================================================
# =============================================================================

# ---------------------------------------------------------------------------
# POST /api/documents/upload — Upload a document (PDF or raw text) for RAG
# Requires JWT authentication
# ---------------------------------------------------------------------------
@app.route('/api/documents/upload', methods=['POST'])
@jwt_required
def document_upload():
    """
    Upload a document for RAG processing.
    
    Accepts either:
    - A PDF file via multipart/form-data (field name: 'file')
    - Raw pasted text via multipart/form-data (field name: 'text')
    
    For PDFs: extracts text using PyPDF2
    For text: uses the text as-is
    
    Then:
    1. Chunks the text into ~500 char segments with 50 char overlap
    2. Generates embeddings for each chunk using perplexity/pplx-embed-v1-0.6b
    3. Stores chunks in Supabase document_chunks table
    4. Auto-analyzes the document to extract services, FAQs, policies, hours
    5. Stores document metadata in Supabase documents table
    6. Returns a JSON summary of what was extracted
    
    Returns the extraction summary so the dashboard can prompt the user
    to accept/reject the extracted data.
    """
    bot_id = g.bot_id
    
    # Check if we got a file or text
    uploaded_file = request.files.get('file')
    pasted_text = request.form.get('text', '').strip()
    
    if not uploaded_file and not pasted_text:
        return jsonify({"error": "No file or text provided. Upload a PDF file or paste text."}), 400
    
    source_name = "pasted_text"
    text = None
    
    if uploaded_file and uploaded_file.filename:
        filename = uploaded_file.filename
        source_name = filename
        
        # Check file extension
        if filename.lower().endswith('.pdf'):
            if not PDF_SUPPORT:
                return jsonify({"error": "PDF support is not available. PyPDF2 is not installed. Install it with: pip install pypdf2"}), 500
            text = extract_text_from_pdf(uploaded_file)
            if not text:
                return jsonify({"error": "Failed to extract text from the PDF. The file may be empty, corrupted, or image-based (OCR not supported)."}), 400
        else:
            return jsonify({"error": "Unsupported file format. Please upload a PDF file."}), 400
    elif pasted_text:
        source_name = pasted_text[:50].strip().replace('\n', ' ')
        text = pasted_text
    
    if not text:
        return jsonify({"error": "No text content found to process."}), 400
    
    # Validate text length
    if len(text) > 50000:
        return jsonify({"error": "Document is too large. Maximum 50,000 characters supported."}), 400
    
    # Step 1: Chunk the text
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    if not chunks:
        return jsonify({"error": "No text chunks could be generated from the document."}), 400
    
    print(f"[RAG] Processing document '{source_name}' for bot '{bot_id}': {len(chunks)} chunks generated")
    
    # Step 2: Generate embeddings and store chunks
    embeddings = []
    for chunk in chunks:
        emb = get_embedding(chunk)
        if emb:
            embeddings.append(emb)
        else:
            print(f"[RAG WARNING] Failed to generate embedding for a chunk — skipping")
    
    if not embeddings:
        return jsonify({"error": "Failed to generate embeddings for the document. Check your OpenRouter API key and model availability."}), 500
    
    # Only store chunks that have embeddings
    valid_chunks = chunks[:len(embeddings)]
    stored_count = store_document_chunks(bot_id, valid_chunks, source_name, embeddings)
    
    if stored_count == 0:
        return jsonify({"error": "Failed to store document chunks in the database."}), 500
    
    # Step 3: Auto-analyze the document
    analysis = analyze_document_with_ai(text, bot_id)
    
    # Step 4: Store document metadata
    doc_record = store_document_metadata(
        bot_id=bot_id,
        source_name=source_name,
        source_type="pdf" if (uploaded_file and uploaded_file.filename and uploaded_file.filename.lower().endswith('.pdf')) else "text",
        chunk_count=stored_count,
        extraction_summary=analysis
    )
    
    print(f"[RAG] Document '{source_name}' processed: {stored_count} chunks stored, analysis confidence={analysis.get('confidence', 0):.2f}")
    
    # Build a human-readable summary
    services_found = len(analysis.get('extracted_services', []))
    faqs_found = len(analysis.get('extracted_faqs', []))
    policies_found = len(analysis.get('extracted_policies', []))
    hours_found = bool(analysis.get('extracted_hours', ''))
    greeting_found = bool(analysis.get('suggested_greeting', ''))
    
    summary_parts = []
    if services_found:
        summary_parts.append(f"{services_found} service items")
    if faqs_found:
        summary_parts.append(f"{faqs_found} FAQs")
    if policies_found:
        summary_parts.append(f"{policies_found} business policies")
    if hours_found:
        summary_parts.append("business hours")
    if greeting_found:
        summary_parts.append("a suggested greeting")
    
    summary_text = f"Found {', '.join(summary_parts)} — all saved!" if summary_parts else "Document processed. No structured data was automatically detected."
    
    return jsonify({
        "success": True,
        "message": "Document uploaded and processed successfully.",
        "document": doc_record,
        "chunks_stored": stored_count,
        "summary_text": summary_text,
        "extraction": analysis,
        "pending_approval": bool(services_found or faqs_found or policies_found or hours_found or greeting_found)
    }), 200


# ---------------------------------------------------------------------------
# POST /api/documents/analyze — Re-analyze an already-uploaded document
# Requires JWT authentication
# ---------------------------------------------------------------------------
@app.route('/api/documents/analyze', methods=['POST'])
@jwt_required
def reanalyze_document():
    """
    Re-run the AI analysis on an already-uploaded document.
    
    This is useful if the document was already uploaded but the user
    wants to re-extract structured data after making changes to their
    bot config.
    
    Body: { "source_name": "..." }
    Reconstructs text from stored chunks and re-analyzes.
    """
    bot_id = g.bot_id
    data = request.json or {}
    source_name = data.get('source_name', '').strip()
    
    if not source_name:
        return jsonify({"error": "source_name is required."}), 400
    
    # Retrieve the chunks for this source
    if USE_SUPABASE:
        try:
            url = f"{SUPABASE_URL}/rest/v1/document_chunks?bot_id=eq.{bot_id}&source_name=eq.{source_name}"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            chunks_data = res.json()
        except Exception as e:
            print(f"[RAG ERROR] Failed to fetch chunks for re-analysis: {e}")
            return jsonify({"error": "Failed to retrieve document chunks for re-analysis."}), 500
    else:
        chunks_file = os.path.join(os.path.dirname(__file__), f'document_chunks_{bot_id}.json')
        if not os.path.exists(chunks_file):
            return jsonify({"error": "No document chunks found."}), 404
        try:
            with open(chunks_file, 'r', encoding='utf-8') as f:
                all_chunks = json.load(f)
            chunks_data = [c for c in all_chunks if c.get('source_name') == source_name]
        except Exception:
            return jsonify({"error": "Failed to read local document chunks."}), 500
    
    if not chunks_data:
        return jsonify({"error": f"No document found with source name '{source_name}'."}), 404
    
    # Reconstruct text from chunks
    text = " ".join([c.get('content', '') for c in chunks_data])
    
    # Re-analyze
    analysis = analyze_document_with_ai(text, bot_id)
    
    # Update the extraction summary in the documents table
    if USE_SUPABASE:
        try:
            update_url = f"{SUPABASE_URL}/rest/v1/documents?bot_id=eq.{bot_id}&source_name=eq.{source_name}"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": "application/json",
                "Prefer": "resolution=merge-duplicates"
            }
            requests.patch(update_url, headers=headers, json={"extraction_summary": json.dumps(analysis)})
        except Exception as e:
            print(f"[RAG WARNING] Failed to update extraction summary: {e}")
    
    services_found = len(analysis.get('extracted_services', []))
    faqs_found = len(analysis.get('extracted_faqs', []))
    
    return jsonify({
        "success": True,
        "message": "Re-analysis complete.",
        "extraction": analysis,
        "pending_approval": bool(services_found or faqs_found)
    }), 200


# ---------------------------------------------------------------------------
# POST /api/documents/apply-extraction — Accept/reject extracted data
# Requires JWT authentication
# ---------------------------------------------------------------------------
@app.route('/api/documents/apply-extraction', methods=['POST'])
@jwt_required
def apply_extraction():
    """
    Apply (or reject) the AI-extracted structured data to the bot's config.
    
    Body: {
        "action": "accept" | "review" | "skip",
        "extraction": { ... }   // the extraction object from the upload response
    }
    
    - "accept": Merges extracted services, FAQs, policies, hours into the business config
    - "review": Returns the extraction data so the user can manually edit before saving
    - "skip": Does nothing — user declined the extraction
    """
    bot_id = g.bot_id
    data = request.json or {}
    action = data.get('action', 'skip').strip().lower()
    extraction = data.get('extraction', {})
    
    if action == 'skip':
        return jsonify({"success": True, "message": "Extraction skipped. No changes made."}), 200
    
    if action == 'review':
        return jsonify({
            "success": True,
            "message": "Extraction data returned for review.",
            "extraction": extraction
        }), 200
    
    if action not in ('accept', 'merge'):
        return jsonify({"error": "Invalid action. Use 'accept', 'review', or 'skip'."}), 400
    
    # Load current business config
    businesses = load_businesses()
    if bot_id not in businesses:
        return jsonify({"error": "Business profile not found."}), 404
    
    biz = businesses[bot_id]
    changes_made = []
    
    # Merge services
    extracted_services = extraction.get('extracted_services', [])
    if extracted_services and isinstance(extracted_services, list):
        existing_services = biz.get('services', [])
        existing_names = {s.get('name', '').strip().lower() for s in existing_services if s.get('name')}
        new_services = []
        for svc in extracted_services:
            name = svc.get('name', '').strip()
            if name and name.lower() not in existing_names:
                new_services.append({"name": name, "price": svc.get('price', 'N/A')})
                existing_names.add(name.lower())
        if new_services:
            biz['services'] = existing_services + new_services
            changes_made.append(f"{len(new_services)} new services")
    
    # Merge FAQs
    extracted_faqs = extraction.get('extracted_faqs', [])
    if extracted_faqs and isinstance(extracted_faqs, list):
        existing_faqs = biz.get('faqs', [])
        existing_questions = {f.get('q', '').strip().lower() for f in existing_faqs if f.get('q')}
        new_faqs = []
        for faq in extracted_faqs:
            q = faq.get('q', '').strip()
            if q and q.lower() not in existing_questions:
                new_faqs.append({"q": q, "a": faq.get('a', '')})
                existing_questions.add(q.lower())
        if new_faqs:
            biz['faqs'] = existing_faqs + new_faqs
            changes_made.append(f"{len(new_faqs)} new FAQs")
    
    # Merge policies (stored in system_prompt or as a separate field)
    extracted_policies = extraction.get('extracted_policies', [])
    if extracted_policies and isinstance(extracted_policies, list):
        # Store policies as a JSON string in a 'policies' field
        existing_policies = biz.get('policies', [])
        if isinstance(existing_policies, str):
            try:
                existing_policies = json.loads(existing_policies)
            except (json.JSONDecodeError, TypeError):
                existing_policies = []
        existing_policy_set = set(p.strip().lower() for p in existing_policies if isinstance(p, str))
        new_policies = []
        for p in extracted_policies:
            if isinstance(p, str) and p.strip().lower() not in existing_policy_set:
                new_policies.append(p.strip())
                existing_policy_set.add(p.strip().lower())
        if new_policies:
            biz['policies'] = existing_policies + new_policies
            changes_made.append(f"{len(new_policies)} new policies")
    
    # Update working hours
    extracted_hours = extraction.get('extracted_hours', '').strip()
    if extracted_hours:
        existing_hours = biz.get('working_hours', '').strip()
        if extracted_hours.lower() != existing_hours.lower():
            biz['working_hours'] = extracted_hours
            changes_made.append("working hours updated")
    
    # Update greeting
    suggested_greeting = extraction.get('suggested_greeting', '').strip()
    if suggested_greeting:
        existing_greeting = biz.get('greeting', '').strip()
        if suggested_greeting.lower() != existing_greeting.lower():
            biz['greeting'] = suggested_greeting
            changes_made.append("greeting updated")
    
    if not changes_made:
        return jsonify({
            "success": True,
            "message": "All extracted data was already present in your configuration. No changes needed."
        }), 200
    
    # Save the updated config
    if not save_businesses(businesses):
        return jsonify({"error": "Failed to save business configuration."}), 500
    
    return jsonify({
        "success": True,
        "message": f"Applied {len(changes_made)} changes to your bot configuration: {', '.join(changes_made)}.",
        "changes": changes_made
    }), 200


# ---------------------------------------------------------------------------
# GET /api/documents — List all uploaded documents for this bot
# Requires JWT authentication
# ---------------------------------------------------------------------------
@app.route('/api/documents', methods=['GET'])
@jwt_required
def list_documents():
    """
    List all uploaded documents for the authenticated bot.
    Returns metadata including source name, type, chunk count, and extraction summary.
    """
    bot_id = g.bot_id
    
    if USE_SUPABASE:
        try:
            url = f"{SUPABASE_URL}/rest/v1/documents?bot_id=eq.{bot_id}&order=created_at.desc"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            docs = res.json()
            # Parse the extraction_summary from string if needed
            for doc in docs:
                if isinstance(doc.get('extraction_summary'), str):
                    try:
                        doc['extraction_summary'] = json.loads(doc['extraction_summary'])
                    except (json.JSONDecodeError, TypeError):
                        doc['extraction_summary'] = {}
            return jsonify(docs), 200
        except Exception as e:
            print(f"[RAG WARNING] Supabase list_documents failed: {e}. Falling back to local JSON.")
    
    # Local fallback
    meta_file = os.path.join(os.path.dirname(__file__), f'documents_{bot_id}.json')
    if os.path.exists(meta_file):
        try:
            with open(meta_file, 'r', encoding='utf-8') as f:
                docs = json.load(f)
            docs.sort(key=lambda d: d.get('created_at', ''), reverse=True)
            return jsonify(docs), 200
        except Exception as e:
            print(f"[RAG ERROR] Failed to read local documents: {e}")
    
    return jsonify([]), 200


# ---------------------------------------------------------------------------
# GET /api/documents/preview — Show extracted text preview for a document
# Requires JWT authentication
# ---------------------------------------------------------------------------
@app.route('/api/documents/preview', methods=['GET'])
@jwt_required
def preview_document():
    """
    Preview the extracted text content of a document by source_name.
    
    Query params:
        source_name: The original filename or source label
    """
    bot_id = g.bot_id
    source_name = request.args.get('source_name', '').strip()
    
    if not source_name:
        return jsonify({"error": "source_name query parameter is required."}), 400
    
    if USE_SUPABASE:
        try:
            url = f"{SUPABASE_URL}/rest/v1/document_chunks?bot_id=eq.{bot_id}&source_name=eq.{source_name}&select=content,created_at"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            chunks = res.json()
        except Exception as e:
            print(f"[RAG ERROR] Failed to fetch chunks for preview: {e}")
            return jsonify({"error": "Failed to retrieve document chunks."}), 500
    else:
        chunks_file = os.path.join(os.path.dirname(__file__), f'document_chunks_{bot_id}.json')
        if not os.path.exists(chunks_file):
            return jsonify({"error": "No document chunks found."}), 404
        try:
            with open(chunks_file, 'r', encoding='utf-8') as f:
                all_chunks = json.load(f)
            chunks = [c for c in all_chunks if c.get('source_name') == source_name]
        except Exception:
            return jsonify({"error": "Failed to read local document chunks."}), 500
    
    if not chunks:
        return jsonify({"error": f"No document found with source name '{source_name}'."}), 404
    
    # Combine all chunk content for preview
    full_text = " ".join([c.get('content', '') for c in chunks])
    preview_text = full_text[:3000]  # Limit preview to first 3000 chars
    
    return jsonify({
        "source_name": source_name,
        "total_chunks": len(chunks),
        "total_characters": len(full_text),
        "preview": preview_text
    }), 200


# ---------------------------------------------------------------------------
# DELETE /api/documents/<doc_id> — Delete a document and its chunks
# Requires JWT authentication
# ---------------------------------------------------------------------------
@app.route('/api/documents/<doc_id>', methods=['DELETE'])
@jwt_required
def delete_document(doc_id):
    """
    Delete a document and all its associated chunks from the database.
    
    Args:
        doc_id: The UUID of the document to delete
    """
    bot_id = g.bot_id
    
    if not doc_id:
        return jsonify({"error": "Document ID is required."}), 400
    
    # Sanitize doc_id — only allow UUID format
    if not re.match(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', doc_id):
        return jsonify({"error": "Invalid document ID format."}), 400
    
    if USE_SUPABASE:
        try:
            # First, get the document metadata to find the source_name
            get_url = f"{SUPABASE_URL}/rest/v1/documents?id=eq.{doc_id}&select=source_name,bot_id"
            headers = {
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
            res = requests.get(get_url, headers=headers)
            res.raise_for_status()
            docs = res.json()
            
            if not docs:
                return jsonify({"error": "Document not found."}), 404
            
            doc = docs[0]
            if doc.get('bot_id') != bot_id:
                return jsonify({"error": "Access denied. This document does not belong to your bot."}), 403
            
            source_name = doc.get('source_name', '')
            
            # Delete the document metadata
            del_url = f"{SUPABASE_URL}/rest/v1/documents?id=eq.{doc_id}"
            del_res = requests.delete(del_url, headers=headers)
            del_res.raise_for_status()
            
            # Delete associated chunks
            if source_name:
                chunks_url = f"{SUPABASE_URL}/rest/v1/document_chunks?bot_id=eq.{bot_id}&source_name=eq.{source_name}"
                chunks_del = requests.delete(chunks_url, headers=headers)
                chunks_del.raise_for_status()
                deleted_chunks = True
            else:
                deleted_chunks = False
            
            return jsonify({
                "success": True,
                "message": f"Document '{doc.get('source_name', 'unknown')}' and its chunks have been deleted."
            }), 200
            
        except Exception as e:
            print(f"[RAG ERROR] Failed to delete document: {e}")
            return jsonify({"error": "Failed to delete document from database."}), 500
    
    # Local fallback
    meta_file = os.path.join(os.path.dirname(__file__), f'documents_{bot_id}.json')
    chunks_file = os.path.join(os.path.dirname(__file__), f'document_chunks_{bot_id}.json')
    
    if not os.path.exists(meta_file):
        return jsonify({"error": "Document not found."}), 404
    
    try:
        with open(meta_file, 'r', encoding='utf-8') as f:
            docs = json.load(f)
        
        doc_idx = None
        source_name = None
        for i, d in enumerate(docs):
            if d.get('id') == doc_id:
                doc_idx = i
                source_name = d.get('source_name', '')
                break
        
        if doc_idx is None:
            return jsonify({"error": "Document not found."}), 404
        
        # Remove from docs list
        docs.pop(doc_idx)
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(docs, f, indent=2)
        
        # Remove chunks for this source
        if source_name and os.path.exists(chunks_file):
            with open(chunks_file, 'r', encoding='utf-8') as f:
                all_chunks = json.load(f)
            all_chunks = [c for c in all_chunks if c.get('source_name') != source_name]
            with open(chunks_file, 'w', encoding='utf-8') as f:
                json.dump(all_chunks, f, indent=2)
        
        return jsonify({
            "success": True,
            "message": f"Document '{source_name}' and its chunks have been deleted."
        }), 200
        
    except Exception as e:
        print(f"[RAG ERROR] Failed to delete document: {e}")
        return jsonify({"error": "Failed to delete document."}), 500


# =============================================================================
# Onboarding page route
# =============================================================================
@app.route('/onboarding')
def serve_onboarding():
    return send_from_directory('public', 'onboarding.html')


# =============================================================================
# POST /api/admin/set-status — Admin-only subscription management
# =============================================================================
@app.route('/api/admin/set-status', methods=['POST'])
def admin_set_status():
    """Set the subscription status for a bot.
    Protected by X-Admin-Key header.
    Body: { botId, status }  status ∈ { 'active', 'trial', 'suspended' }
    """
    admin_key = request.headers.get("X-Admin-Key", "").strip()
    if not admin_key or admin_key != SUPER_ADMIN_KEY:
        return jsonify({"error": "Unauthorized. Valid admin key required."}), 401
    data = request.json or {}
    bot_id = sanitize_bot_id(data.get('botId', '').strip().lower())
    new_status = data.get('status', '').strip().lower()
    if not bot_id:
        return jsonify({"error": "botId is required."}), 400
    if new_status not in ('active', 'trial', 'suspended'):
        return jsonify({"error": "status must be 'active', 'trial', or 'suspended'."}), 400
    businesses = load_businesses()
    if bot_id not in businesses:
        return jsonify({"error": f"Business '{bot_id}' not found."}), 404
    success = update_single_business(bot_id, {"status": new_status})
    if not success:
        return jsonify({"error": "Failed to update status."}), 500
    print(f"[ADMIN] Status updated for '{bot_id}': {new_status}")
    return jsonify({"success": True, "botId": bot_id, "status": new_status}), 200


# =============================================================================
# GET /api/leads/export — CSV export for leads
# =============================================================================
@app.route('/api/leads/export', methods=['GET'])
@jwt_required
def export_leads():
    """Export all leads for a bot as a CSV file download."""
    from flask import Response
    import io as _io
    bot_id = sanitize_bot_id(request.args.get('botId', '').strip().lower())
    if not bot_id:
        return jsonify({"error": "botId is required"}), 400
    token_bot_id = g.bot_id
    if token_bot_id and token_bot_id != bot_id:
        return jsonify({"error": "Access denied."}), 403

    # Fetch leads
    leads = []
    if USE_SUPABASE:
        try:
            url = f"{SUPABASE_URL}/rest/v1/leads?bot=eq.{bot_id}"
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            leads = res.json()
        except Exception as e:
            print(f"[WARNING] Supabase leads export failed: {e}")
    if not leads and os.path.exists(LEADS_FILE):
        try:
            with open(LEADS_FILE, 'r', encoding='utf-8') as f:
                all_leads = json.load(f)
            leads = [l for l in all_leads if l.get('bot', '') == bot_id]
        except Exception:
            leads = []

    output = _io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Name', 'Phone', 'Topic', 'Date', 'Time'])
    for lead in leads:
        ts = lead.get('timestamp', '')
        date_part, time_part = (ts.split('T') if 'T' in ts else [ts, ''])
        writer.writerow([
            lead.get('name', ''),
            lead.get('phone', ''),
            lead.get('topic', ''),
            date_part,
            time_part[:8] if time_part else ''
        ])
    today = datetime.date.today().strftime('%Y-%m-%d')
    filename = f"leads_{bot_id}_{today}.csv"
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


# =============================================================================
# GET /api/appointments/export — CSV export for appointments
# =============================================================================
@app.route('/api/appointments/export', methods=['GET'])
@jwt_required
def export_appointments():
    """Export all appointments for a bot as a CSV file download."""
    from flask import Response
    import io as _io
    bot_id = sanitize_bot_id(request.args.get('botId', '').strip().lower())
    if not bot_id:
        return jsonify({"error": "botId is required"}), 400
    token_bot_id = g.bot_id
    if token_bot_id and token_bot_id != bot_id:
        return jsonify({"error": "Access denied."}), 403

    appts = []
    if USE_SUPABASE:
        try:
            url = f"{SUPABASE_URL}/rest/v1/appointments?bot=eq.{bot_id}"
            headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            appts = res.json()
        except Exception as e:
            print(f"[WARNING] Supabase appointments export failed: {e}")
    if not appts and os.path.exists(APPOINTMENTS_FILE):
        try:
            with open(APPOINTMENTS_FILE, 'r', encoding='utf-8') as f:
                all_appts = json.load(f)
            appts = [a for a in all_appts if a.get('bot', '') == bot_id]
        except Exception:
            appts = []

    output = _io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Customer Name', 'Phone', 'Service', 'Date', 'Time', 'Status'])
    for appt in appts:
        writer.writerow([
            appt.get('customer_name', ''),
            appt.get('customer_phone', ''),
            appt.get('service', ''),
            appt.get('preferred_date', ''),
            appt.get('preferred_time', ''),
            appt.get('status', 'pending')
        ])
    today = datetime.date.today().strftime('%Y-%m-%d')
    filename = f"appointments_{bot_id}_{today}.csv"
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename="{filename}"'}
    )


# =============================================================================
# POST /api/crawl — Website URL crawler for auto-configuration
# =============================================================================
@app.route('/api/crawl', methods=['POST'])
@jwt_required
def crawl_website():
    """
    Crawl a URL, extract page text, and run AI analysis.
    Body: { url, bot_id (optional — defaults to JWT bot_id) }
    Returns the same extraction summary as /api/documents/upload.
    """
    bot_id = g.bot_id
    data = request.json or {}
    url = data.get('url', '').strip()
    if not url:
        return jsonify({"error": "url is required."}), 400
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url

    try:
        resp = requests.get(url, timeout=15, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; OverarcBot/1.0)'
        })
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        return jsonify({"error": f"Failed to fetch URL: {str(e)}"}), 400

    # Strip HTML tags
    clean = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<style[^>]*>.*?</style>', ' ', clean, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<[^>]+>', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()

    if len(clean) > 50000:
        clean = clean[:50000]

    if not clean:
        return jsonify({"error": "No text content found on the page."}), 400

    # Chunk + embed + store
    chunks = chunk_text(clean, chunk_size=500, overlap=50)
    source_name = url[:100]
    embeddings = []
    for chunk in chunks[:50]:  # Limit to first 50 chunks for web pages
        emb = get_embedding(chunk)
        if emb:
            embeddings.append(emb)
    valid_chunks = chunks[:len(embeddings)]
    stored_count = store_document_chunks(bot_id, valid_chunks, source_name, embeddings)

    # AI analysis
    analysis = analyze_document_with_ai(clean, bot_id)

    # Store metadata
    doc_record = store_document_metadata(
        bot_id=bot_id,
        source_name=source_name,
        source_type='url',
        chunk_count=stored_count,
        extraction_summary=analysis
    )

    services_found = len(analysis.get('extracted_services', []))
    faqs_found = len(analysis.get('extracted_faqs', []))
    policies_found = len(analysis.get('extracted_policies', []))
    summary_parts = []
    if services_found: summary_parts.append(f"{services_found} service items")
    if faqs_found: summary_parts.append(f"{faqs_found} FAQs")
    if policies_found: summary_parts.append(f"{policies_found} business policies")
    summary_text = f"Found {', '.join(summary_parts)} — all saved!" if summary_parts else "Page crawled. No structured data detected."

    return jsonify({
        "success": True,
        "url": url,
        "chunks_stored": stored_count,
        "summary_text": summary_text,
        "extraction": analysis,
        "document": doc_record,
        "pending_approval": bool(services_found or faqs_found or policies_found)
    }), 200


# =============================================================================
# Application entry point
# =============================================================================

# Keep-alive scheduler (prevents Render free tier from sleeping)
def _keep_alive():
    """Ping /api/health every 14 minutes to prevent Render sleep."""
    try:
        requests.get("http://localhost:{}/api/health".format(
            os.environ.get('PORT', 5000)
        ), timeout=10)
        print("[KEEP-ALIVE] Pinged /api/health")
    except Exception:
        pass  # Silently ignore failures

if APSCHEDULER_AVAILABLE and os.environ.get('PORT'):  # PORT set = running in production
    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(_keep_alive, 'interval', minutes=14)
    _scheduler.start()
    print("[KEEP-ALIVE] Scheduler started — pinging every 14 minutes")


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Overarc Python Backend on port {port}...")
    print(f"Access the site at: http://localhost:{port}")
    print("[SECURITY] Debug mode: OFF")
    print("[SECURITY] CORS restricted to: https://overarc.co, http://localhost:5000")
    print(f"[SECURITY] Rate limit on /api/chat: 30 requests/minute/IP")
    print(f"[SECURITY] JWT tokens expire after: {JWT_EXPIRATION_HOURS} hours")
    # RAG status
    if USE_SUPABASE:
        print(f"[RAG] Database: Supabase + pgvector enabled")
    else:
        print("[RAG] Database: Local JSON files (chunks stored per-bot)")
    print(f"[RAG] Embedding model: {EMBEDDING_MODEL} (via OpenRouter)")
    print(f"[RAG] PDF support: {'Yes (PyPDF2)' if PDF_SUPPORT else 'No (install pypdf2)'}")
    app.run(host='0.0.0.0', port=port, debug=False)