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
    packages = {"requests": "requests", "bs4": "beautifulsoup4", "colorama": "colorama"}
    for mod, pkg in packages.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True)
auto_setup()
from bs4 import BeautifulSoup

# ── CONFIG ────────────────────────────────
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), 'config'))
    import settings
    GMAIL_APP_PASS = settings.GMAIL_APP_PASS
    DB_FILE = settings.DB_FILE
    CREATOR_FB = settings.CREATOR_FACEBOOK
    CREATOR_MSG = settings.CREATOR_MESSENGER
    BIN_API = settings.BIN_API_URL
except:
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

def user_exists(email):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT verified FROM users WHERE email=?", (email,))
    result = c.fetchone()
    conn.close()
    return result is not None

# ── EMAIL ──────────────────────────────────
def send_verification_code(email, code):
    try:
        msg = MIMEMultipart()
        msg['From'] = GMAIL_APP_PASS.split()[0] + "@gmail.com" if GMAIL_APP_PASS else "noreply@gmail.com"
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
        server.login(GMAIL_APP_PASS, GMAIL_APP_PASS)
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

def check_animation(text1, text2, duration=2):
    os.system('clear')
    h = shutil.get_terminal_size().lines
    print("\n" * (h // 2 - 2))
    print(f"{C}{BOLD}{'✓'.center(tw())}{RES}")
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
    creator_text = "Created by Saeka Tojirp"
    print(f"\n{DIM}{creator_text}{RES}")
    if username:
        print(f"{C}{BOLD}Hi! {username}{RES}")
    print()

# ── LOADING SCREEN ────────────────────────
def loading_screen():
    packages = {"requests": "requests", "bs4": "beautifulsoup4", "colorama": "colorama"}
    missing = []
    for mod, pkg in packages.items():
        try:
            importlib.import_module(mod)
        except ImportError:
            missing.append(pkg)
    
    duration = 60 if missing else 10
    
    greetings = [
        ("English", "Welcome!"),
        ("Spanish", "¡Bienvenido!"),
        ("French", "Bienvenue!"),
        ("German", "Willkommen!"),
        ("Italian", "Benvenuto!"),
        ("Japanese", "ようこそ"),
        ("Korean", "환영합니다"),
        ("Filipino", "Maligayang Pagdating!"),
    ]
    
    if missing:
        for pkg in missing:
            subprocess.run([sys.executable, "-m", "pip", "install", pkg], capture_output=True)
    
    frames = ['◜', '◠', '◝', '◞', '◡', '◟']
    end = time.time() + duration
    i = 0
    g = 0
    greet_timer = time.time()
    
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
        time.sleep(0.1)
        i += 1

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
        print(f"  {R}Email is required.{RES}")
        time.sleep(1.5)
        return
    password = input(f"  {W}Password: {RES}").strip()
    if len(password) < 6:
        print(f"  {R}Password must be at least 6 characters.{RES}")
        time.sleep(1.5)
        return
    
    if not register_user(email, password):
        print(f"  {R}Email already registered.{RES}")
        time.sleep(1.5)
        return
    
    code = str(random.randint(100000, 999999))
    stop_event = threading.Event()
    t = threading.Thread(target=lambda: process_spinner("Sending verification code to your Gmail account...", stop_event))
    t.start()
    sent = send_verification_code(email, code)
    stop_event.set()
    t.join()
    
    if sent:
        os.system('clear')
        banner()
        print(f"  {W}Email: {email}{RES}")
        print(f"  {W}Password: {'*' * len(password)}{RES}")
        print(f"  {G}✓ Verification code sent to {email}{RES}")
        time.sleep(2)
        os.system('clear')
        banner()
        print(f"  {W}Email: {email}{RES}")
        print(f"  {W}Password: {'*' * len(password)}{RES}")
        user_code = input(f"  {W}Enter code: {RES}").strip()
        if user_code == code:
            set_verified(email)
            centered_spinner("Verification is in Process. Please do not Close this Terminal.", 10)
            check_animation("", "VERIFICATION SUCCESSFUL!", 2)
            main_menu(email)
        else:
            print(f"  {R}Incorrect code.{RES}")
            time.sleep(1.5)
    else:
        print(f"  {R}Failed to send email. Check your Gmail SMTP settings.{RES}")
        time.sleep(2)

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
    stop_event.set()
    t.join()
    
    if valid:
        check_animation("", "VERIFICATION SUCCESSFUL!", 2)
        main_menu(email)
    else:
        print(f"  {R}Account not found or not verified.{RES}")
        time.sleep(1.5)

# ── MAIN MENU ─────────────────────────────
def main_menu(username=""):
    options = [
        "FACEBOOK SPAM SHARE",
        "FACEBOOK SPAM REPORTER",
        "FACEBOOK OSINT",
        "HTTP TOOLS",
        "CC BIN INFO",
        "FREENET PH METHODS",
        "USEFUL TOOLS",
        "CREDITS",
        "END SESSION"
    ]
    while True:
        choice = arrow_menu(options, username)
        
        if choice == 1:
            facebook_spam_share()
        elif choice == 2:
            facebook_spam_reporter()
        elif choice == 3:
            facebook_osint()
        elif choice == 4:
            http_tools()
        elif choice == 5:
            cc_bin_info()
        elif choice in (6, 7):
            restricted_access()
        elif choice == 8:
            credits()
        elif choice == 9:
            end_session()
        input()

# ── FEATURES ──────────────────────────────

def facebook_spam_share():
    os.system('clear')
    banner()
    link = input(f"  {W}ENTER POST LINK: {RES}").strip()
    if not link:
        return
    # Placeholder
    os.system('clear')
    centered_spinner("PROCESSING SHARE REQUEST...", 1)
    print(f"  {Y}Spam share requires access token setup.{RES}")
    print(f"  {DIM}This feature needs Graph API access token.{RES}")

def facebook_spam_reporter():
    os.system('clear')
    banner()
    link = input(f"  {W}ENTER ACCOUNT PROFILE LINK: {RES}").strip()
    if not link:
        return
    os.system('clear')
    spinner("Reporting account", 1)
    print(f"  {Y}Reporter requires access token setup.{RES}")

def facebook_osint():
    os.system('clear')
    banner()
    link = input(f"  {W}ENTER FACEBOOK PROFILE LINK: {RES}").strip()
    if not link:
        return
    centered_spinner("SCANNING PROFILE...", 2)
    os.system('clear')
    banner()
    print(f"  {G}OSINT Report:{RES}")
    print(f"  {DIM}Profile scanned. Results would appear here.{RES}")

def http_tools():
    os.system('clear')
    banner()
    url = input(f"  {W}ENTER SITE URL: {RES}").strip()
    if not url:
        return
    centered_spinner("SCANNING SITE...", 2)
    os.system('clear')
    banner()
    print(f"  {G}HTTP REPORT:{RES}")
    print(f"  {DIM}Site scanned. Results would appear here.{RES}")

def cc_bin_info():
    os.system('clear')
    banner()
    bin_num = input(f"  {W}ENTER BIN (First 6 digits): {RES}").strip()
    if not bin_num or len(bin_num) < 6:
        return
    spinner("Looking up BIN", 1)
    try:
        r = requests.get(BIN_API.format(bin_num[:6]))
        if r.status_code == 200:
            data = r.json()
            os.system('clear')
            banner()
            print(f"  {G}BIN Found: {bin_num[:6]}{RES}")
            print(f"  {DIM}{'─'*50}{RES}")
            print(f"  Country: {data.get('country', {}).get('name', 'N/A')}")
            print(f"  Bank: {data.get('bank', {}).get('name', 'N/A')}")
            print(f"  Brand: {data.get('brand', 'N/A')}")
            print(f"  Type: {data.get('type', 'N/A')}")
            print(f"  Level: {data.get('scheme', 'N/A')}")
            print(f"  Currency: {data.get('country', {}).get('currency', 'N/A')}")
            print(f"  {DIM}{'─'*50}{RES}")
        else:
            print(f"  {R}BIN Not Found.{RES}")
    except:
        print(f"  {R}Connection error.{RES}")

def restricted_access():
    os.system('clear')
    w = tw()
    title = "NOT AVAILABLE"
    body = "This feature is not available on your account status."
    action = "SUBSCRIBE FOR FULL ACCESS"
    contact = CREATOR_FB
    contacts = [CREATOR_FB, CREATOR_MSG]
    ci = 0
    timer = time.time()
    
    while True:
        os.system('clear')
        print("\n" * 4)
        print(f"{Y}{BOLD}{title.center(w)}{RES}")
        print()
        print(f"{W}{body.center(w)}{RES}")
        print()
        print(f"{G}{BOLD}{action.center(w)}{RES}")
        print()
        if time.time() - timer >= 5:
            ci = (ci + 1) % len(contacts)
            timer = time.time()
        print(f"{C}{BOLD}Contact: {contacts[ci]}{RES}".center(w + len(contacts[ci]) - len(contact)))
        print()
        print(f"{DIM}Press ENTER to continue...{RES}")
        # Non-blocking check for Enter
        import select
        if select.select([sys.stdin], [], [], 1)[0]:
            sys.stdin.readline()
            break

def credits():
    os.system('clear')
    w = tw()
    print("\n" * 3)
    print(f"{C}{BOLD}CREDITS{RES}".center(w + 8))
    print()
    print(f"{W}This tool was developed with dedication and passion{RES}".center(w + 50))
    print(f"{W}for the community. Every feature was built from{RES}".center(w + 50))
    print(f"{W}the ground up to provide powerful capabilities{RES}".center(w + 50))
    print(f"{W}in a single, unified platform.{RES}".center(w + 50))
    print()
    print(f"{W}Thank you for using this tool.{RES}".center(w + 30))
    print()
    print(f"{G}{BOLD}CREATED BY{RES}".center(w + 10))
    print(f"{Y}{BOLD}SAEKA TOJIRP{RES}".center(w + 14))
    print()
    print(f"{C}Contact: {CREATOR_FB}{RES}".center(w + len(CREATOR_FB) + 9))
    print(f"{C}         {CREATOR_MSG}{RES}".center(w + len(CREATOR_MSG) + 9))

def end_session():
    colors = [R, G, B, M, C, Y]
    frames = ['◜', '◠', '◝', '◞', '◡', '◟']
    end = time.time() + 3
    i = 0
    c = 0
    while time.time() < end:
        os.system('clear')
        h = shutil.get_terminal_size().lines
        print("\n" * (h // 2 - 3))
        color = colors[c % len(colors)]
        print(f"{color}{BOLD}THANK YOU FOR USING SAEKAX TOOL{RES}".center(tw() + 30))
        print()
        print(f"{color}{frames[i%6]}{RES}".center(tw()))
        print()
        print(f"{color}TERMINATING SESSION...{RES}".center(tw() + 20))
        time.sleep(0.15)
        i += 1
        if i % 6 == 0:
            c += 1
    os.system('clear')
    sys.exit(0)

# ── INITIAL SCREEN ────────────────────────
def auth_screen():
    options = ["SIGNUP", "LOGIN"]
    selected = 0
    while True:
        os.system('clear')
        h = shutil.get_terminal_size().lines
        w = tw()
        print("\n" * (h // 2 - 5))
        print(f"{BOLD}{C}HOLA! HEY THERE{RES}".center(w + 30))
        print()
        for i, option in enumerate(options):
            if i == selected:
                print(f"{G}{BOLD}▸ {option}{RES}".center(w + 4))
            else:
                print(f"{DIM}  {option}{RES}".center(w + 4))
        print()
        # Rainbow footer
        colors = [R, G, B, M, C, Y]
        footer = "Created by Saeka Tojirp"
        for i, char in enumerate(footer):
            sys.stdout.write(f"{colors[i % len(colors)]}{BOLD}{char}{RES}")
        sys.stdout.write("\n")
        sys.stdout.flush()
        
        key = get_key()
        if key == 'UP' and selected > 0:
            selected -= 1
        elif key == 'DOWN' and selected < len(options) - 1:
            selected += 1
        elif key == 'ENTER':
            if selected == 0:
                signup()
            else:
                login()
            break

# ── MAIN ───────────────────────────────────
def main():
    init_db()
    loading_screen()
    auth_screen()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        os.system('clear')
        sys.exit(0)
