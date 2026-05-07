#!/usr/bin/env python3
# ============================================
# SAEKAX TOOL v1.0 — COMPLETE ALL-IN-ONE
# Created by Saeka Tojirp
# GitHub: github.com/saekacutie/sakea
# ============================================

import re, os, sys, time, shutil, subprocess, importlib, json, sqlite3, hashlib, random, socket, ssl, smtplib, ipaddress, threading, requests
from datetime import datetime
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── AUTO-SETUP ────────────────────────────
def auto_setup():
    packages = {"requests": "requests", "bs4": "beautifulsoup4", "colorama": "colorama", "playwright": "playwright"}
    for mod, pkg in packages.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True)
    try:
        from playwright.sync_api import sync_playwright
    except:
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], capture_output=True)
auto_setup()
from bs4 import BeautifulSoup

# ── CONFIG ────────────────────────────────
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))
    import settings
    GMAIL_USER = settings.GMAIL_USER
    GMAIL_APP_PASS = settings.GMAIL_APP_PASS
    DB_FILE = settings.DB_FILE
    CREATOR_FB = settings.CREATOR_FACEBOOK
    CREATOR_MSG = settings.CREATOR_MESSENGER
    BIN_API = settings.BIN_API_URL
except:
    GMAIL_USER = "bidosijanjan@gmail.com"
    GMAIL_APP_PASS = "xkfu xnin jift cxax"
    DB_FILE = "data/users.db"
    CREATOR_FB = "Facebook.com/saekacutiee"
    CREATOR_MSG = "m.me/saekacutiee"
    BIN_API = "https://lookup.binlist.net/{}"

# ── CONSTANTS ─────────────────────────────
R = '\033[91m'; G = '\033[92m'; Y = '\033[93m'; B = '\033[94m'
M = '\033[95m'; C = '\033[96m'; W = '\033[97m'
BOLD = '\033[1m'; DIM = '\033[2m'; RES = '\033[0m'

def tw(): return shutil.get_terminal_size().columns if hasattr(shutil, 'get_terminal_size') else 60

# ── DATABASE SETUP ─────────────────────────
def init_db():
    Path(os.path.dirname(DB_FILE)).mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        verified INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS fb_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        cookie TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(email, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(email, password):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=? AND verified=1", (email, hash_password(password)))
    result = c.fetchone()
    conn.close()
    return result is not None

def set_verified(email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE users SET verified=1 WHERE email=?", (email,))
    conn.commit()
    conn.close()

def save_fb_account(name, cookie):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO fb_accounts (name, cookie) VALUES (?, ?)", (name, cookie))
    conn.commit()
    conn.close()

def get_all_fb_accounts():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name, cookie FROM fb_accounts")
    rows = c.fetchall()
    conn.close()
    return [{"id": r[0], "name": r[1], "cookie": r[2]} for r in rows]

# ── EMAIL ──────────────────────────────────
def send_verification_code(email, code):
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_USER
        msg['To'] = email
        msg['Subject'] = "Your Verification Code - SAEKAX TOOL"
        username = email.split('@')[0]
        body = f"""Hi {username},

Thank you for signing up! Use the code below to complete your verification.

Verification Code: {code}

If you did not request this, please ignore this email.

Thank you,
Saeka Tojirp"""
        msg.attach(MIMEText(body, 'plain'))
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_APP_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except:
        return False

# ── ANIMATIONS ────────────────────────────
def spinner(text="Loading", sec=1.2):
    frames = ['◜', '◠', '◝', '◞', '◡', '◟']
    end = time.time() + sec; i = 0
    while time.time() < end:
        sys.stdout.write(f"\r  {C}{frames[i%6]} {RES}{text}...")
        sys.stdout.flush(); time.sleep(0.08); i += 1
    sys.stdout.write("\r" + " " * 50 + "\r")

def centered_spinner(text, duration):
    frames = ['◜', '◠', '◝', '◞', '◡', '◟']
    h = shutil.get_terminal_size().lines
    end = time.time() + duration; i = 0
    while time.time() < end:
        os.system('clear')
        print("\n" * (h // 2 - 2))
        print(f"{C}{BOLD}{frames[i%6].center(tw())}{RES}")
        print(f"{W}{BOLD}{text.center(tw())}{RES}")
        time.sleep(0.1); i += 1

def process_spinner(text, stop_event):
    frames = ['◜', '◠', '◝', '◞', '◡', '◟']; i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r  {C}{frames[i%6]} {RES}{text}...")
        sys.stdout.flush(); time.sleep(0.08); i += 1

def check_animation(text2, duration=2):
    os.system('clear')
    h = shutil.get_terminal_size().lines
    print("\n" * (h // 2 - 2))
    print(f"{G}{BOLD}{'✓'.center(tw())}{RES}")
    print(f"{G}{BOLD}{text2.center(tw())}{RES}")
    time.sleep(duration)

def banner(username=""):
    os.system('clear')
    title_lines = [
        "███████╗ █████╗ ███████╗██╗  ██╗ █████╗ ██╗  ██╗",
        "██╔════╝██╔══██╗██╔════╝██║ ██╔╝██╔══██╗╚██╗██╔╝",
        "███████╗███████║█████╗  █████╔╝ ███████║ ╚███╔╝ ",
        "╚════██║██╔══██║██╔══╝  ██╔═██╗ ██╔══██║ ██╔██╗ ",
        "███████║██║  ██║███████╗██║  ██╗██║  ██║██╔╝ ██╗",
        "╚══════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝",
    ]
    colors = [R, G, B, M, C, Y]
    for i, line in enumerate(title_lines):
        color = colors[i % len(colors)]
        print(f"{BOLD}{color}{line}{RES}")
        time.sleep(0.05)
    print(f"\n{DIM}Created by Saeka Tojirp{RES}")
    if username:
        print(f"{C}{BOLD}Hi! {username}{RES}")
    print()

# ── LOADING SCREEN ────────────────────────
def loading_screen():
    missing = []
    for mod in ["requests", "bs4", "colorama", "playwright"]:
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(mod)
    duration = 60 if missing else 10
    greetings = [
        ("English", "Welcome!"), ("Spanish", "¡Bienvenido!"), ("French", "Bienvenue!"),
        ("German", "Willkommen!"), ("Italian", "Benvenuto!"), ("Japanese", "ようこそ"),
        ("Korean", "환영합니다"), ("Filipino", "Maligayang Pagdating!"),
    ]
    if missing:
        for pkg in missing:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True)
    frames = ['◜', '◠', '◝', '◞', '◡', '◟']
    end = time.time() + duration; i = 0; g = 0; greet_timer = time.time()
    while time.time() < end:
        os.system('clear')
        h = shutil.get_terminal_size().lines
        print("\n" * (h // 2 - 3))
        print(f"{C}{BOLD}{frames[i%6].center(tw())}{RES}")
        print()
        if time.time() - greet_timer >= 5:
            g = (g + 1) % len(greetings)
            greet_timer = time.time()
        print(f"{W}{BOLD}{greetings[g][1].center(tw())}{RES}")
        time.sleep(0.1); i += 1

# ── ARROW MENU ────────────────────────────
def arrow_menu(options, username=""):
    selected = 0
    while True:
        os.system('clear')
        banner(username)
        for i, option in enumerate(options):
            if i == selected:
                print(f"  {G}{BOLD}▸ {option}{RES}")
            else:
                print(f"  {DIM}  {option}{RES}")
        key = get_key()
        if key == 'UP' and selected > 0:
            selected -= 1
        elif key == 'DOWN' and selected < len(options) - 1:
            selected += 1
        elif key == 'ENTER':
            return selected + 1

def get_key():
    import tty, termios
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch2 = sys.stdin.read(2)
            if ch2 == '[A': return 'UP'
            elif ch2 == '[B': return 'DOWN'
        elif ch == '\r': return 'ENTER'
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return None

# ── SIGNUP ─────────────────────────────────
def signup():
    os.system('clear')
    banner()
    email = input(f"  {W}Email: {RES}").strip()
    if not email: return
    password = input(f"  {W}Password: {RES}").strip()
    if len(password) < 6:
        print(f"  {R}Password must be at least 6 characters.{RES}")
        time.sleep(1.5); return
    if not register_user(email, password):
        print(f"  {R}Email already registered.{RES}")
        time.sleep(1.5); return
    code = str(random.randint(100000, 999999))
    stop_event = threading.Event()
    t = threading.Thread(target=lambda: process_spinner("Sending verification code to your Gmail account...", stop_event))
    t.start()
    sent = send_verification_code(email, code)
    stop_event.set(); t.join()
    if sent:
        os.system('clear'); banner()
        print(f"  {W}Email: {email}{RES}")
        print(f"  {W}Password: {'*' * len(password)}{RES}")
        print(f"  {G}✓ Verification code sent to {email}{RES}")
        time.sleep(2)
        os.system('clear'); banner()
        print(f"  {W}Email: {email}{RES}")
        print(f"  {W}Password: {'*' * len(password)}{RES}")
        user_code = input(f"  {W}Enter code: {RES}").strip()
        if user_code == code:
            set_verified(email)
            centered_spinner("Verification is in Process. Please do not Close this Terminal.", 10)
            check_animation("VERIFICATION SUCCESSFUL!", 2)
            main_menu(email)
        else:
            print(f"  {R}Incorrect code.{RES}"); time.sleep(1.5)
    else:
        print(f"  {R}Failed to send email. Check your Gmail SMTP settings.{RES}"); time.sleep(2)

# ── LOGIN ──────────────────────────────────
def login():
    os.system('clear')
    banner()
    email = input(f"  {W}Email: {RES}").strip()
    password = input(f"  {W}Password: {RES}").strip()
    stop_event = threading.Event()
    t = threading.Thread(target=lambda: process_spinner("CHECKING IF ACCOUNT IS ACTIVE...", stop_event))
    t.start()
    valid = verify_user(email, password)
    stop_event.set(); t.join()
    if valid:
        check_animation("VERIFICATION SUCCESSFUL!", 2)
        main_menu(email)
    else:
        print(f"  {R}Account not found or not verified.{RES}"); time.sleep(1.5)

# ── MAIN MENU ─────────────────────────────
def main_menu(username=""):
    options = [
        "FACEBOOK SPAM SHARE",
        "FACEBOOK SPAM REPORTER",
        "SAVE FACEBOOK ACCOUNT",
        "HTTP TOOLS",
        "CC BIN INFO",
        "FREENET PH METHODS",
        "USEFUL TOOLS",
        "CREDITS",
        "END SESSION"
    ]
    while True:
        choice = arrow_menu(options, username)
        if choice == 1: facebook_spam_share()
        elif choice == 2: facebook_spam_reporter()
        elif choice == 3: save_fb_menu()
        elif choice == 4: http_tools()
        elif choice == 5: cc_bin_info()
        elif choice in (6, 7): restricted_access()
        elif choice == 8: credits()
        elif choice == 9: end_session()

# ── SAVE FB ACCOUNT ────────────────────
def save_fb_menu():
    os.system('clear')
    banner()
    print(f"  {W}SAVE FACEBOOK ACCOUNT{RES}\n")
    name = input(f"  {W}Account Name: {RES}").strip()
    if not name: return
    print(f"\n  {DIM}Paste your Facebook cookie from browser DevTools:{RES}")
    print(f"  {DIM}Example: c_user=123456; xs=abc123def{RES}")
    cookie = input(f"  {W}Cookie: {RES}").strip()
    if not cookie: return
    save_fb_account(name, cookie)
    print(f"\n  {G}[OK] Account saved: {name}{RES}")
    time.sleep(1.5)

# ── FACEBOOK SPAM REPORTER ──────────────
def facebook_spam_reporter():
    os.system('clear')
    banner()
    accounts = get_all_fb_accounts()
    if not accounts:
        print(f"  {R}No Facebook accounts saved.{RES}")
        print(f"  {DIM}Use SAVE FACEBOOK ACCOUNT first.{RES}")
        input(f"\n  {DIM}Press ENTER to continue...{RES}"); return
    print(f"  {W}Select account:{RES}")
    for i, acc in enumerate(accounts):
        print(f"  {G}[{i+1}]{RES} {acc['name']}")
    print(f"  {G}[0]{RES} Back")
    try:
        choice = int(input(f"\n  {W}Choice: {RES}"))
        if choice == 0: return
        selected = accounts[choice - 1]
    except: return
    link = input(f"  {W}ENTER ACCOUNT PROFILE LINK: {RES}").strip()
    if not link: return
    user_id = None
    try:
        r = requests.get(link, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        match = re.search(r'"userID":"(\d+)"', r.text)
        if match: user_id = match.group(1)
        else:
            match = re.search(r'entity_id=(\d+)', r.text)
            if match: user_id = match.group(1)
    except: pass
    if not user_id:
        print(f"  {R}Could not extract profile ID.{RES}")
        input(f"\n  {DIM}Press ENTER to continue...{RES}"); return
    print(f"\n  {G}Target ID: {user_id}{RES}")
    print(f"  {Y}Starting report loop...{RES}\n")
    cookie = selected['cookie']
    categories = ["impersonation", "harassment", "spam", "fake_account"]
    count = 0
    while True:
        fake_ip = f"{random.randint(1,255)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,255)}"
        headers = {
            "User-Agent": random.choice(["Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"]),
            "Cookie": cookie,
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Forwarded-For": fake_ip
        }
        cat = random.choice(categories)
        count += 1
        try:
            r = requests.post("https://www.facebook.com/ajax/report/social.php", headers=headers, data={"report_type": cat, "content_owner_id_new": user_id, "reportable_ent_token": user_id}, timeout=10)
            status = "SUCCESS" if r.status_code == 200 else "FAILED"
            color = G if r.status_code == 200 else R
            print(f"  [{color}{count}{RES}] [{fake_ip}] [{status}] {cat}")
        except:
            print(f"  [{R}{count}{RES}] [{fake_ip}] Connection error")
        time.sleep(random.uniform(1, 4))

# ── FACEBOOK SPAM SHARE ──────────────────
def facebook_spam_share():
    os.system('clear')
    banner()
    accounts = get_all_fb_accounts()
    if not accounts:
        print(f"  {R}No Facebook accounts saved.{RES}")
        print(f"  {DIM}Use SAVE FACEBOOK ACCOUNT first.{RES}")
        input(f"\n  {DIM}Press ENTER to continue...{RES}"); return
    print(f"  {W}Select account:{RES}")
    for i, acc in enumerate(accounts):
        print(f"  {G}[{i+1}]{RES} {acc['name']}")
    print(f"  {G}[0]{RES} Back")
    try:
        choice = int(input(f"\n  {W}Choice: {RES}"))
        if choice == 0: return
        selected = accounts[choice - 1]
    except: return
    link = input(f"  {W}ENTER POST LINK: {RES}").strip()
    if not link: return
    duration = input(f"  {W}SPAM SHARE DURATION (sec/min/hour): {RES}").strip()
    rate = int(input(f"  {W}Shares per second: {RES}") or "1")
    safe = input(f"  {W}ENABLE SAFE MODE (on/off): {RES}").strip().lower() == "on"
    dur_sec = 60
    if "min" in duration: dur_sec = int(duration.replace("min","")) * 60
    elif "hour" in duration: dur_sec = int(duration.replace("hour","")) * 3600
    elif duration.isdigit(): dur_sec = int(duration)
    post_id = None
    try:
        match = re.search(r'posts/(\d+)', link)
        if match: post_id = match.group(1)
        else:
            match = re.search(r'story_fbid=(\d+)', link)
            if match: post_id = match.group(1)
    except: pass
    if not post_id:
        print(f"  {R}Could not extract post ID.{RES}")
        input(f"\n  {DIM}Press ENTER to continue...{RES}"); return
    print(f"\n  {G}Post ID: {post_id}{RES}\n  {Y}Starting share loop...{RES}\n")
    cookie = selected['cookie']
    count = 0
    start_time = time.time()
    while time.time() - start_time < dur_sec:
        try:
            r = requests.post("https://www.facebook.com/ajax/share/dialog", headers={"User-Agent": "Mozilla/5.0", "Cookie": cookie, "Content-Type": "application/x-www-form-urlencoded"}, data={"shareable_id": post_id, "nctr[_mod]": "pagelet_composer"}, timeout=10)
            if r.status_code == 200:
                count += 1
                print(f"  [{G}✓{RES}] Shared ({count})")
            else:
                print(f"  [{R}✗{RES}] Failed (HTTP {r.status_code})")
        except:
            print(f"  [{R}✗{RES}] Connection error")
        if safe: time.sleep(random.uniform(3, 8))
        else: time.sleep(1 / rate)
    print(f"\n  {G}[DONE]{RES} Total shares: {count}")
    input(f"\n  {DIM}Press ENTER to continue...{RES}")

# ── HTTP TOOLS ──────────────────────────
def http_tools():
    os.system('clear')
    banner()
    url = input(f"  {W}ENTER SITE URL: {RES}").strip()
    if not url: return
    centered_spinner("SCANNING SITE...", 2)
    try:
        if not url.startswith('http'): url = 'https://' + url
        r = requests.get(url, timeout=10)
        hostname = url.replace("https://","").replace("http://","").split("/")[0]
        ip = socket.gethostbyname(hostname)
        os.system('clear'); banner()
        print(f"  {G}HTTP REPORT:{RES}\n  URL: {url}\n  Resolved IP: {ip}\n  Status: {r.status_code}\n  Server: {r.headers.get('Server','N/A')}\n  CDN: {'Cloudflare' if 'cloudflare' in str(r.headers).lower() else 'None'}")
    except:
        print(f"  {R}Site not reachable.{RES}")
    input(f"\n  {DIM}Press ENTER to continue...{RES}")

# ── CC BIN INFO ─────────────────────────
def cc_bin_info():
    os.system('clear')
    banner()
    bin_num = input(f"  {W}ENTER BIN (First 6 digits): {RES}").strip()
    if not bin_num: return
    spinner("Looking up BIN", 1)
    try:
        r = requests.get(BIN_API.format(bin_num[:6]), headers={"Accept": "application/json"})
        if r.status_code == 200:
            data = r.json()
            country = data.get('country',{})
            bank = data.get('bank',{})
            if not country.get('name') and not data.get('brand'):
                print(f"  {R}BIN Not Found.{RES}")
                input(f"\n  {DIM}Press ENTER to continue...{RES}"); return
            os.system('clear'); banner()
            print(f"  {G}BIN Found: {bin_num[:6]}{RES}\n  {DIM}{'─'*50}{RES}\n  Country: {country.get('name','N/A')} {country.get('emoji','')}\n  Bank: {bank.get('name','N/A')}\n  Brand: {data.get('brand','N/A')}\n  Type: {data.get('type','N/A')}\n  Currency: {country.get('currency','N/A')}\n  {DIM}{'─'*50}{RES}")
        else:
            print(f"  {R}BIN Not Found.{RES}")
    except:
        print(f"  {R}Connection error.{RES}")
    input(f"\n  {DIM}Press ENTER to continue...{RES}")

# ── RESTRICTED ACCESS ───────────────────
def restricted_access():
    contacts = [CREATOR_FB, CREATOR_MSG]
    ci = 0; timer = time.time()
    while True:
        os.system('clear')
        w = tw()
        print("\n" * 4)
        print(f"{Y}{BOLD}NOT AVAILABLE{RES}".center(w + 15))
        print(f"{W}This feature is not available on your account status.{RES}".center(w + 50))
        print(f"{G}{BOLD}SUBSCRIBE FOR FULL ACCESS{RES}".center(w + 25))
        if time.time() - timer >= 5: ci = (ci + 1) % 2; timer = time.time()
        print(f"{C}Contact: {contacts[ci]}{RES}".center(w + len(contacts[ci]) + 9))
        import select
        if select.select([sys.stdin], [], [], 1)[0]:
            sys.stdin.readline(); break

# ── CREDITS ─────────────────────────────
def credits():
    os.system('clear')
    w = tw()
    print("\n" * 3)
    print(f"{C}{BOLD}CREDITS{RES}".center(w + 8))
    print(f"{W}This tool was developed with dedication and passion{RES}".center(w + 50))
    print(f"{W}Thank you for using this tool.{RES}".center(w + 30))
    print(f"{G}{BOLD}CREATED BY{RES}".center(w + 10))
    print(f"{Y}{BOLD}SAEKA TOJIRP{RES}".center(w + 14))
    print(f"{C}Contact: {CREATOR_FB}{RES}".center(w + len(CREATOR_FB) + 9))
    input(f"\n  {DIM}Press ENTER to continue...{RES}")

# ── END SESSION ─────────────────────────
def end_session():
    colors = [R, G, B, M, C, Y]; frames = ['◜', '◠', '◝', '◞', '◡', '◟']
    end = time.time() + 3; i = 0; c = 0
    while time.time() < end:
        os.system('clear')
        h = shutil.get_terminal_size().lines
        print("\n" * (h // 2 - 3))
        color = colors[c % len(colors)]
        print(f"{color}{BOLD}THANK YOU FOR USING SAEKAX TOOL{RES}".center(tw() + 30))
        print(f"{color}{frames[i%6]}{RES}".center(tw()))
        print(f"{color}TERMINATING SESSION...{RES}".center(tw() + 20))
        time.sleep(0.15); i += 1
        if i % 6 == 0: c += 1
    os.system('clear'); sys.exit(0)

# ── AUTH SCREEN ──────────────────────────
def auth_screen():
    options = ["SIGNUP", "LOGIN"]
    selected = 0
    while True:
        os.system('clear')
        h = shutil.get_terminal_size().lines
        w = tw()
        print("\n" * (h // 2 - 5))
        print(f"{BOLD}{C}HOLA! HEY THERE{RES}".center(w + 30))
        for i, option in enumerate(options):
            if i == selected:
                print(f"{G}{BOLD}▸ {option}{RES}".center(w + 4))
            else:
                print(f"{DIM}  {option}{RES}".center(w + 4))
        colors = [R, G, B, M, C, Y]
        footer = "Created by Saeka Tojirp"
        for i, char in enumerate(footer):
            sys.stdout.write(f"{colors[i % len(colors)]}{BOLD}{char}{RES}")
        sys.stdout.write("\n"); sys.stdout.flush()
        key = get_key()
        if key == 'UP' and selected > 0: selected -= 1
        elif key == 'DOWN' and selected < 1: selected += 1
        elif key == 'ENTER':
            if selected == 0: signup()
            else: login()
            break

# ── MAIN ───────────────────────────────────
def main():
    init_db()
    loading_screen()
    auth_screen()

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: os.system('clear'); sys.exit(0)
