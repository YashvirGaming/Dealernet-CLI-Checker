<h1 id="dealernet-cli-checker">Dealernet-CLI-Checker</h1>

<p>Premium OB2 → Python conversion of the Dealernet login flow. Fast, colorful CLI with live CPM, proxy rotation, and clean hit logging.</p>

---

<img width="1094" height="590" alt="image" src="https://github.com/user-attachments/assets/20bf675d-c889-41f6-b591-c4a0ccb4173e" />


<p>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.9%2B-blue">
  <img alt="httpx" src="https://img.shields.io/badge/httpx-async%2Fsync%20HTTP-brightgreen">
  <img alt="OS" src="https://img.shields.io/badge/OS-Windows-lightgrey">
  <img alt="License" src="https://img.shields.io/badge/License-MIT-purple">
</p>

<hr/>

<h2 id="features">✨ Features</h2>
<ul>
  <li>Premium CLI with centered ART + subtitle and bright emoji logs</li>
  <li>Drag-and-drop <strong>combos</strong> and <strong>proxies</strong> (no auto-strip of lines)</li>
  <li>Proxy parsing: <code>ip:port</code>, <code>ip:port:user:pass</code> &rarr; <code>user:pass@ip:port</code>, <code>user:pass@ip:port</code></li>
  <li>Protocols: <code>http</code> / <code>https</code> / <code>socks4</code> / <code>socks5</code> (supports <code>(scheme)</code> or <code>scheme://</code> hints)</li>
  <li>Smart proxy rotation + per-proxy cooldown on failures</li>
  <li>Multithreaded (1–100) with a <strong>live CPM bar</strong></li>
  <li>OB2-accurate XML payload with Base64 credentials</li>
  <li>Precise keycheck: <code>&lt;Autentificado&gt;True&lt;/Autentificado&gt;</code> = HIT</li>
  <li>Fail detection on <code>&lt;response&gt;&lt;ERROR&gt;</code> / <code>&lt;CODERROR&gt;1&lt;/CODERROR&gt;</code> with first <code>&lt;ERRMSG&gt;</code> displayed</li>
  <li>Retry policy only for transient issues: network errors, <code>408</code>/<code>409</code>/<code>429</code>, and <code>5xx</code> (capped attempts)</li>
  <li>Bright per-combo logs: <strong>[CHECKING]</strong>, <strong>[HIT]</strong>, <strong>[FAIL]</strong>, <strong>[RETRY]</strong> (with reason)</li>
  <li>Supports multiple proxy files; preserves input lines (trims only trailing newline)</li>
  <li>Writes hits to <code>Results/Hits.txt</code> with capture</li>
</ul>

<hr/>

<h2 id="how-it-works">🧩 How it works</h2>
<ul>
  <li>Payload built as:</li>
</ul>
<pre><code>&lt;cuenta&gt;{USER}&lt;/cuenta&gt;&lt;clave&gt;{PASS}&lt;/clave&gt;
→ Base64 → injected into XML
→ POST https://suite.dealernet.cl/srv-sawfw-login.aspx
</code></pre>
<ul>
  <li><strong>Hit:</strong> XML contains <code>&lt;Autentificado&gt;True&lt;/Autentificado&gt;</code></li>
  <li><strong>Fail:</strong> XML contains <code>&lt;response&gt;&lt;ERROR&gt;</code> or <code>&lt;CODERROR&gt;1&lt;/CODERROR&gt;</code> (first <code>&lt;ERRMSG&gt;</code> shown)</li>
  <li><strong>Retry:</strong> transient network/server conditions only</li>
</ul>

<hr/>

<h2 id="requirements">📦 Requirements</h2>
<pre><code>httpx&gt;=0.27.0
colorama&gt;=0.4.6
</code></pre>

<p><strong>Install:</strong></p>
<pre><code class="language-bash">pip install -r requirements.txt
</code></pre>

<hr/>

<h2 id="run">▶️ Run</h2>
<p><strong>Python:</strong></p>
<pre><code class="language-bash">python dealernet_checker.py
</code></pre>

<p><strong>Simple launcher (optional):</strong></p>
<pre><code class="language-bat">@echo off
python dealernet_checker.py
pause
</code></pre>

<hr/>

<h2 id="build">🏗️ Build (Nuitka)</h2>
<p><strong>Builder (with icon):</strong></p>
<pre><code class="language-bat">@echo off
set "SCRIPT=dealernet_checker.py"
set "OUT=Dealernet_CLI_Checker.exe"
set "ICON=icon.ico"

python -m pip install -U pip wheel setuptools nuitka
python -m nuitka --standalone --onefile --windows-icon-from-ico=%ICON% --jobs=12 --output-filename="%OUT%" "%SCRIPT%"
pause
</code></pre>

<p><strong>GUI / no console (optional):</strong></p>
<pre><code class="language-bat">python -m nuitka --standalone --onefile --windows-disable-console --windows-icon-from-ico=%ICON% --jobs=12 -o "%OUT%" "%SCRIPT%"
</code></pre>

<hr/>

<h2 id="inputs">📥 Input formats</h2>
<p><strong>Combos</strong></p>
<pre><code>email@example.com:password123
</code></pre>

<p><strong>Proxies</strong> (any of these)</p>
<pre><code>1.2.3.4:8080
1.2.3.4:8080:user:pass
user:pass@1.2.3.4:8080
(http) 1.2.3.4:8080
https://1.2.3.4:8080
socks4://1.2.3.4:9050
(socks5) user:pass@1.2.3.4:1080
</code></pre>
<p>Drop one or multiple <code>.txt</code> files when prompted. Lines are preserved (only trailing newlines removed).</p>

<hr/>

<h2 id="output">📂 Output</h2>
<pre><code>Results/Hits.txt   -&gt;  email:pass | Autentificado=True
</code></pre>

<hr/>

<h2 id="tunables">⚙️ Tunables (inside script)</h2>
<pre><code>MAX_RETRIES = 2
PROXY_COOLDOWN = 20   # seconds
</code></pre>
<p>Threads are prompted at start (1–100).</p>

<hr/>

<h2 id="troubleshooting">🧯 Troubleshooting</h2>
<ul>
  <li><strong>Many retries:</strong> use higher-quality/rotating proxies; increase <code>PROXY_COOLDOWN</code>.</li>
  <li><strong>Low CPM:</strong> raise thread count; ensure proxies aren’t rate-limited.</li>
  <li><strong>All fails:</strong> check printed <code>&lt;ERRMSG&gt;</code>; verify payload and credentials.</li>
  <li><strong>Unicode issues:</strong> save input files as UTF-8.</li>
</ul>

<hr/>

<h2 id="disclaimer">⚠️ Disclaimer</h2>
<p>This project is for educational and testing purposes only. Use responsibly and only against systems you are authorized to test.</p>

<p>Made with ♥ by <strong>Yashvir Gaming</strong> · Telegram: <a href="https://t.me/therealyashvirgaming" target="_blank">https://t.me/therealyashvirgaming</a></p>
