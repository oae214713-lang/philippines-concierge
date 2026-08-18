#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys
import subprocess
import threading
import re
import time

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class SPAHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Resolve requested path
        path = self.translate_path(self.path)
        if not os.path.exists(path) and "." not in self.path.split("/")[-1]:
            self.path = "/index.html"
        return super().do_GET()

    def log_message(self, format, *args):
        sys.stderr.write(f"[Web Server] {self.address_string()} - {format % args}\n")

def run_server():
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), SPAHandler) as httpd:
        print(f"[Web Server] Serving {DIRECTORY} on port {PORT}...")
        httpd.serve_forever()

def main():
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1)

    cloudflared_path = "/home/tearhock/.local/bin/cloudflared"
    cmd = [cloudflared_path, "tunnel", "--url", f"http://127.0.0.1:{PORT}"]

    print("[Cloudflare] Starting tunnel...")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    tunnel_url = None
    url_pattern = re.compile(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com")

    for line in iter(process.stdout.readline, ""):
        sys.stdout.write(line)
        sys.stdout.flush()
        if not tunnel_url:
            match = url_pattern.search(line)
            if match:
                tunnel_url = match.group(0)
                print("\n" + "=" * 60)
                print(f"🎉 САЙТ ОПУБЛИКОВАН В ИНТЕРНЕТЕ!")
                print(f"🔗 ССЫЛКА ДЛЯ ДРУГА: {tunnel_url}")
                print("=" * 60 + "\n")
                
                # Write link file to both Desktop locations
                for desktop_path in ["/home/tearhock/Рабочий стол", "/home/tearhock/Desktop"]:
                    if os.path.exists(desktop_path):
                        try:
                            with open(os.path.join(desktop_path, "ССЫЛКА_ДЛЯ_ДРУГА.txt"), "w", encoding="utf-8") as f:
                                f.write(f"Ссылка на сайт:\n{tunnel_url}\n\nСайт активен, пока работает туннель Cloudflare.\n")
                        except Exception:
                            pass

    process.wait()

if __name__ == "__main__":
    main()
