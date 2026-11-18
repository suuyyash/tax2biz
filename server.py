#!/usr/bin/env python3
"""
Tax2Biz — Local Development & API Server
Serves static web files and provides a live Trademark Search REST API
powered by the TradeMarx Official IP India API.

GET /api/trademark-search?q=<wordmark>&class=<class>&match_type=<type>
"""

import http.server
import socketserver
import urllib.parse
import urllib.request
import json
import hashlib
import random
import time
import os
import sys

PORT = 8000

# Nice Class Titles Mapping
NICE_CLASS_TITLES = {
    1: "Chemicals & Resins",
    2: "Paints & Varnishes",
    3: "Cosmetics & Cleaning",
    4: "Industrial Oils & Fuels",
    5: "Pharmaceuticals & Health",
    6: "Common Metals & Hardware",
    7: "Machines & Power Tools",
    8: "Hand Tools & Cutlery",
    9: "Software, Apps & Electronics",
    10: "Medical Devices",
    11: "Environmental & Lighting",
    12: "Vehicles & Automotive",
    13: "Firearms & Explosives",
    14: "Jewelry & Horology",
    15: "Musical Instruments",
    16: "Paper & Stationery",
    17: "Rubber & Plastics",
    18: "Leather & Luggage",
    19: "Non-Metallic Building",
    20: "Furniture & Containers",
    21: "Household Utensils",
    22: "Ropes & Sacks",
    23: "Yarns & Threads",
    24: "Textiles & Fabrics",
    25: "Apparel & Footwear",
    26: "Lace & Haberdashery",
    27: "Carpets & Mats",
    28: "Games, Toys & Sports",
    29: "Dairy, Meat & Oils",
    30: "Food, Tea, Coffee & Spices",
    31: "Agricultural & Seeds",
    32: "Beverages & Mineral Water",
    33: "Alcoholic Beverages",
    34: "Tobacco & Smokers' Articles",
    35: "Business, Retail & E-Commerce",
    36: "Fintech, Banking & Insurance",
    37: "Construction & Repair",
    38: "Telecommunications",
    39: "Transport & Logistics",
    40: "Material Treatment",
    41: "Education & Entertainment",
    42: "Tech, Cloud & SaaS",
    43: "Restaurants & Hotels",
    44: "Medical & Healthcare",
    45: "Legal & IP Services",
    99: "Multi-Class Application"
}

def get_api_key():
    """Retrieve the TradeMarx API key securely from .env or environment."""
    key = os.environ.get('TRADEMARX_API_KEY')
    if key and key.strip():
        return key.strip()

    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('TRADEMARX_API_KEY='):
                        return line.split('=', 1)[1].strip()
        except Exception:
            pass
    return None

def fetch_from_trademarx(query, target_class='all'):
    """Fetch live trademark records from TradeMarx Public API."""
    api_key = get_api_key()
    if not api_key:
        return None

    clean_q = query.strip()
    url = f"https://admin.trademarx.in/api/public/v1/trademarks/search?name={urllib.parse.quote(clean_q)}"
    if target_class and str(target_class).lower() != 'all':
        try:
            c_int = int(target_class)
            url += f"&class={c_int}"
        except ValueError:
            pass

    req = urllib.request.Request(
        url,
        headers={
            'X-API-Key': api_key,
            'User-Agent': 'Tax2Biz/1.0 (https://tax2biz.com)',
            'Accept': 'application/json'
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode('utf-8'))
                if isinstance(data, list):
                    return data
    except Exception as e:
        print(f"[TradeMarx API Error] {e}", file=sys.stderr)
        return None
    return None

def fetch_trademarx_status(app_no):
    """Fetch live single trademark status from TradeMarx API."""
    api_key = get_api_key()
    if not api_key:
        return None
    url = f"https://admin.trademarx.in/api/public/v1/trademarks/{urllib.parse.quote(str(app_no).strip())}/status"
    req = urllib.request.Request(
        url,
        headers={
            'X-API-Key': api_key,
            'User-Agent': 'Tax2Biz/1.0 (https://tax2biz.com)',
            'Accept': 'application/json'
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as resp:
            if resp.status == 200:
                return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"[TradeMarx Status Error] {e}", file=sys.stderr)
        return None
    return None

def format_date(d_str):
    """Convert YYYY-MM-DD into DD/MM/YYYY."""
    if not d_str:
        return 'On Record'
    parts = d_str.strip().split('-')
    if len(parts) == 3:
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    return d_str

def calculate_valid_upto(d_str):
    """Compute 10-year validity under Section 25 of Trade Marks Act 1999."""
    if not d_str:
        return 'Under Review'
    parts = d_str.strip().split('-')
    if len(parts) == 3:
        try:
            exp_year = int(parts[0]) + 10
            return f"{parts[2]}/{parts[1]}/{exp_year}"
        except Exception:
            return 'Under Review'
    return 'Under Review'

def process_trademarx_response(query, target_class, raw_records):
    """Map raw TradeMarx response into Tax2Biz frontend schema."""
    clean_q = query.strip().upper()
    mapped_records = []

    for item in raw_records:
        c_num = item.get('tmClass') or 0
        c_title = NICE_CLASS_TITLES.get(c_num, f"Class {c_num}")
        
        status_raw = item.get('trademarkStatus') or 'Registered'
        s_lower = status_raw.lower()
        
        status_class = 'tm-status-registered'
        if any(w in s_lower for w in ['object', 'advertis', 'accept']):
            status_class = 'tm-status-objected'
        elif any(w in s_lower for w in ['abandon', 'refus', 'remov', 'withdraw']):
            status_class = 'tm-status-abandoned'
        elif any(w in s_lower for w in ['exam', 'formalit', 'new', 'pending', 'ready']):
            status_class = 'tm-status-pending'
        elif any(w in s_lower for w in ['oppo']):
            status_class = 'tm-status-opposed'

        app_date_raw = item.get('applicationDate') or ''
        filing_date = format_date(app_date_raw)
        valid_upto = calculate_valid_upto(app_date_raw)

        mapped_records.append({
            'appNo': str(item.get('applicationNo') or ''),
            'wordmark': (item.get('name') or clean_q).upper(),
            'classNum': c_num,
            'classLabel': f"Class {c_num} – {c_title}",
            'status': status_raw,
            'statusClass': status_class,
            'proprietor': item.get('proprietorName') or 'Proprietor on Record',
            'filingDate': filing_date,
            'validUpto': valid_upto,
            'journalNo': 'Official Trade Marks Journal',
            'goods': item.get('details') or f"Goods & services registered under Nice Class {c_num}.",
            'sourceUrl': item.get('url') or '',
            'isLiveTradeMarx': True
        })

    # Evaluate conflict risk
    has_exact = any(r['wordmark'] == clean_q for r in mapped_records)
    total_count = len(mapped_records)

    if total_count == 0:
        availability_state = 'available'
        availability_pct = 98
    elif has_exact:
        availability_state = 'high_conflict'
        availability_pct = 22
    else:
        availability_state = 'moderate'
        availability_pct = max(35, 88 - (total_count * 3))

    return {
        'status': 'success',
        'query': clean_q,
        'targetClass': target_class,
        'source': 'trademarx_live_api',
        'attribution': 'Trademark data powered by TradeMarx',
        'attributionUrl': 'https://trademarx.in/?utm_source=api&utm_medium=attribution&utm_content=55940401',
        'availabilityPercentage': availability_pct,
        'availabilityState': availability_state,
        'totalRecords': total_count,
        'records': mapped_records,
        'ipindiaDirectUrl': f"https://ipindiaonline.gov.in/eregister/eregister.aspx?wordmark={urllib.parse.quote(clean_q)}"
    }


LEADS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'leads.json')

def load_leads():
    if os.path.exists(LEADS_FILE):
        try:
            with open(LEADS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_leads(leads):
    try:
        with open(LEADS_FILE, 'w', encoding='utf-8') as f:
            json.dump(leads, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"[Lead Save Error] {e}", file=sys.stderr)
        return False

class Tax2BizRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Enable CORS for local API access
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-API-Key')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_POST(self):
            parsed = urllib.parse.urlparse(self.path)
            content_length = int(self.headers.get('Content-Length', 0))
            raw_body = self.rfile.read(content_length).decode('utf-8') if content_length > 0 else '{}'
            try:
                payload = json.loads(raw_body)
            except Exception:
                payload = {}
    
            if parsed.path == '/api/leads':
                lead_id = payload.get('leadId') or f"LEAD-{int(time.time()*1000)}-{random.randint(100, 999)}"
                name = payload.get('name', '').strip()
                email = payload.get('email', '').strip()
                phone = payload.get('phone', '').strip()
                state = payload.get('state', '').strip()
                company_name = payload.get('companyName', '').strip()
                service = payload.get('service', 'Private Limited Company Registration')
                package = payload.get('package', 'Standard')
                amount = payload.get('amount', 0)
                status = payload.get('paymentStatus', 'UNPAID_LEAD')
    
                leads = load_leads()
                existing = next((l for l in leads if l.get('leadId') == lead_id), None)
                now_iso = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    
                if existing:
                    existing.update({
                        'name': name or existing.get('name'),
                        'email': email or existing.get('email'),
                        'phone': phone or existing.get('phone'),
                        'state': state or existing.get('state'),
                        'companyName': company_name or existing.get('companyName'),
                        'service': service,
                        'package': package,
                        'amount': amount,
                        'paymentStatus': status,
                        'updatedAt': now_iso
                    })
                else:
                    lead_record = {
                        'leadId': lead_id,
                        'name': name,
                        'email': email,
                        'phone': phone,
                        'state': state,
                        'companyName': company_name,
                        'service': service,
                        'package': package,
                        'amount': amount,
                        'paymentStatus': status,
                        'createdAt': now_iso,
                        'updatedAt': now_iso,
                        'source': 'landing_page_form'
                    }
                    leads.insert(0, lead_record)
    
                save_leads(leads)
                resp_data = {
                    'status': 'success',
                    'message': 'Lead recorded successfully',
                    'leadId': lead_id,
                    'paymentStatus': status
                }
    
            elif parsed.path == '/api/payment-complete':
                lead_id = payload.get('leadId')
                payment_id = payload.get('paymentId') or f"PAY-{int(time.time()*1000)}"
                method = payload.get('method', 'UPI')
                now_iso = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    
                leads = load_leads()
                lead = next((l for l in leads if l.get('leadId') == lead_id), None)
                if lead:
                    lead['paymentStatus'] = 'PAID'
                    lead['paymentId'] = payment_id
                    lead['paymentMethod'] = method
                    lead['paidAt'] = now_iso
                    save_leads(leads)
                    resp_data = {
                        'status': 'success',
                        'message': 'Professional fees payment successfully recorded!',
                        'leadId': lead_id,
                        'paymentId': payment_id,
                        'orderId': f"T2B-PVT-{lead_id[-6:]}"
                    }
                else:
                    resp_data = {
                        'status': 'error',
                        'message': f"Lead #{lead_id} not found to record payment"
                    }
            else:
                resp_data = {'status': 'error', 'message': 'Endpoint not found'}
    
            body = json.dumps(resp_data, indent=2).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
    
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == '/api/trademark-details':
            params = urllib.parse.parse_qs(parsed.query)
            app_no = params.get('appNo', [''])[0].strip()
            if not app_no:
                resp_data = {'status': 'error', 'message': 'Query parameter "appNo" is required'}
            else:
                live_item = fetch_trademarx_status(app_no)
                if live_item:
                    c_num = live_item.get('tmClass') or 0
                    c_title = NICE_CLASS_TITLES.get(c_num, f"Class {c_num}")
                    status_raw = live_item.get('trademarkStatus') or 'Registered'
                    s_lower = status_raw.lower()
                    status_class = 'tm-status-registered'
                    if any(w in s_lower for w in ['object', 'advertis', 'accept']):
                        status_class = 'tm-status-objected'
                    elif any(w in s_lower for w in ['abandon', 'refus', 'remov']):
                        status_class = 'tm-status-abandoned'
                    elif any(w in s_lower for w in ['exam', 'formalit', 'new', 'pending', 'ready']):
                        status_class = 'tm-status-pending'
                    elif any(w in s_lower for w in ['oppo']):
                        status_class = 'tm-status-opposed'

                    app_date = format_date(live_item.get('applicationDate') or '')
                    valid_upto = calculate_valid_upto(live_item.get('applicationDate') or '')

                    resp_data = {
                        'status': 'success',
                        'record': {
                            'appNo': str(live_item.get('applicationNo') or app_no),
                            'wordmark': (live_item.get('name') or '').upper(),
                            'classNum': c_num,
                            'classLabel': f"Class {c_num} – {c_title}",
                            'status': status_raw,
                            'statusClass': status_class,
                            'proprietor': live_item.get('proprietorName') or 'Proprietor on Record',
                            'filingDate': app_date,
                            'validUpto': valid_upto,
                            'journalNo': 'Trade Marks Journal',
                            'goods': live_item.get('details') or f"Goods & services registered under Nice Class {c_num}.",
                            'type': live_item.get('type') or 'Wordmark',
                            'imgUrl': live_item.get('imgUrl') or '',
                            'source': 'TradeMarx Official IP India API',
                            'attribution': 'Trademark data powered by TradeMarx'
                        }
                    }
                else:
                    resp_data = {'status': 'error', 'message': f'Application #{app_no} not found or network error'}

            body = json.dumps(resp_data, indent=2).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        elif parsed.path == '/api/leads':
            leads = load_leads()
            resp_data = {'status': 'success', 'count': len(leads), 'leads': leads}
            body = json.dumps(resp_data, indent=2).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        elif parsed.path == '/api/trademark-search':
            params = urllib.parse.parse_qs(parsed.query)
            q = params.get('q', [''])[0].strip()
            target_class = params.get('class', ['all'])[0].strip()

            if not q:
                resp_data = {'status': 'error', 'message': 'Query parameter "q" is required'}
            else:
                # 1. Fetch live from TradeMarx
                live_data = fetch_from_trademarx(q, target_class)
                if live_data is not None:
                    resp_data = process_trademarx_response(q, target_class, live_data)
                else:
                    # Fallback if TradeMarx request is blocked or offline
                    resp_data = {
                        'status': 'fallback',
                        'query': q,
                        'targetClass': target_class,
                        'source': 'local_engine',
                        'message': 'TradeMarx live API call unavailable; running local clearance engine.'
                    }
            
            body = json.dumps(resp_data, indent=2).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # Default static file handler
        return super().do_GET()

def run_server():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Tax2BizRequestHandler) as httpd:
        print(f"Tax2Biz server running at http://localhost:{PORT}")
        print(f"Live TradeMarx Trademark API enabled at http://localhost:{PORT}/api/trademark-search?q=XYZ")
        httpd.serve_forever()

if __name__ == '__main__':
    run_server()
