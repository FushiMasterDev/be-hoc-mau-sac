"""Generate audio/*.mp3 for the quiz with Google Translate's Vietnamese voice.

Run after editing questions in index.html:  python3 gen_audio.py
"""
import os, re, ssl, urllib.parse, urllib.request

# python.org builds on macOS ship without CA certs; fall back to the system bundle.
CTX = ssl.create_default_context(cafile="/etc/ssl/cert.pem" if os.path.exists("/etc/ssl/cert.pem") else None)
ROOT = os.path.dirname(os.path.abspath(__file__))
html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()

texts = {}
rows = re.findall(r'q: "([^"]+)",\s*options: \[([^\]]+)\]', html)
assert len(rows) == 10, f"expected 10 questions, found {len(rows)}"
for i, (q, opts) in enumerate(rows, 1):
    # keep in sync with questionText() in index.html
    texts[f"q{i}"] = f"{q} {', '.join(re.findall(r'"([^"]+)"', opts))}"

# keep in sync with resultMessage() in index.html
for s in range(11):
    msg = ("Tuyệt vời! Bé biết hết các màu rồi!" if s == 10 else
           "Bé làm tốt lắm! Chơi lại để được 10 điểm nhé!" if s >= 6 else
           "Cố lên nào! Mình cùng chơi lại nhé!")
    texts[f"r{s}"] = f"Bé được {s} điểm. {msg}"

os.makedirs(os.path.join(ROOT, "audio"), exist_ok=True)
for name, text in texts.items():
    assert len(text) <= 200, f"{name}: Google TTS limit is 200 chars"
    url = "https://translate.google.com/translate_tts?" + urllib.parse.urlencode(
        {"ie": "UTF-8", "tl": "vi", "client": "tw-ob", "q": text})
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
        assert r.headers.get_content_type() == "audio/mpeg", f"{name}: got {r.headers.get_content_type()}"
        data = r.read()
    open(os.path.join(ROOT, "audio", f"{name}.mp3"), "wb").write(data)
    print(f"{name} {len(data):>6}B  {text}")
