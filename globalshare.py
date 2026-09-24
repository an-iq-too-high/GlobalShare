import os
import sys
import platform
import subprocess
import socket
import time
from http.server import SimpleHTTPRequestHandler, HTTPServer
import urllib.parse
import threading

PORT = 9595
G, B, C, Y, R, X, W = "\033[92m", "\033[94m", "\033[96m", "\033[93m", "\033[91m", "\033[0m", "\033[1m"

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def resolve_system_specs():
    sys_os = "Android" if (platform.system() == "Linux" and "ANDROID_ROOT" in os.environ) else platform.system()
    sys_arch = platform.machine() or "arm64"
    
    bat_status = "PC"
    if sys_os == "Android":
        try:
            import json
            bat_status = f"{json.loads(subprocess.check_output(['termux-battery-status'], stderr=subprocess.DEVNULL).decode('utf-8'))['percentage']}%"
        except:
            p = "/sys/class/power_supply/battery/capacity"
            if os.path.exists(p):
                with open(p, "r") as f: bat_status = f"{f.read().strip()}%"

    ram_status = "[N/A]"
    if os.path.exists("/proc/meminfo"):
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if "MemTotal" in line:
                    nums = "".join(c for c in line if c.isdigit())
                    if nums: ram_status = f"{round(int(nums) / (1024**2), 1)} GB"
                    break

    if sys_os == "Android":
        storage_root = "/storage/emulated/0"
    elif sys_os == "Windows":
        storage_root = "C:\\"
    else:
        storage_root = os.path.expanduser("~")

    return {"os": sys_os, "arch": sys_arch, "ram": ram_status, "bat": bat_status, "root": storage_root}

class GlobalShareHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return  # Keeps the dashboard completely clean

    def do_GET(self):
        specs = resolve_system_specs()
        root_path = specs["root"]
        
        safe_url = urllib.parse.unquote(self.path).replace('..', '')
        if safe_url.startswith('/'): safe_url = safe_url[1:]
        
        target_path = os.path.join(root_path, safe_url)
        
        if not os.path.exists(target_path):
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Error 404: Storage asset location not found.")
            return

        if os.path.isdir(target_path):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            
            html = f'<html><head><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>GlobalShare Console</title></head><body style="font-family:monospace; padding:20px; background:#111; color:#eee;">'
            html += f'<h2 style="color:#00ffff;">📂 SYSTEM ROOT CONSOLE: {root_path}</h2>'
            html += f'<h3>📍 CURRENT PATH: /{safe_url}</h3><hr style="border:1px solid #333;"><ul style="list-style-type:none; padding:0; line-height:2.2;">'
            
            if safe_url:
                up_link = "/" + os.path.dirname(safe_url)
                html += f'<li>📁 <a href="{up_link}" style="color:#ffcc00; text-decoration:none;">.. (Go Up a Directory)</a></li>'
            
            try:
                for item in sorted(os.listdir(target_path)):
                    item_url = os.path.join("/", safe_url, item)
                    full_item_path = os.path.join(target_path, item)
                    if os.path.isdir(full_item_path):
                        html += f'<li>📁 <a href="{item_url}" style="color:#ffcc00; text-decoration:none;">{item}/</a></li>'
                    else:
                        html += f'<li>📄 <a href="{item_url}" style="color:#00ff00; text-decoration:none;" download>{item}</a></li>'
            except Exception as e:
                html += f'<li>⚠️ <span style="color:#ff0000;">System Access Locked ({str(e)})</span></li>'
                
            html += '</ul></body></html>'
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.end_headers()
            try:
                with open(target_path, 'rb') as f:
                    self.wfile.write(f.read())
            except:
                pass

def run_http_server():
    server = HTTPServer(('0.0.0.0', PORT), GlobalShareHandler)
    server.serve_forever()

def start_engine():
    specs = resolve_system_specs()
    local_ip = get_local_ip()
    
    os.system('clear')
    print(f"{C}{W}======================================\n    📡 GLOBALSHARE SERVER INTERFACE \n======================================{X}")
    print(f"{B}💻 OS: {specs['os']}   🏗️  Arch: {specs['arch']}{X}")
    print(f"{B}📊 RAM: {specs['ram']}   🔋 Battery: {specs['bat']}{X}")
    print(f"{G}📂 HOVERING STORAGE ROOT: {specs['root']}{X}")
    print(f"{C}======================================{X}")
    print(f"\n {W}LOCAL Wi-Fi IP:  http://{local_ip}:{PORT}{X}")
    print(f" LOCAL LOOPBACK:  http://127.0.0.1:{PORT}")
    print(f"\n{Y}🛠️  Opening Worldwide Tunnel Over Serveo Core...{X}")

    threading.Thread(target=run_http_server, daemon=True).start()

    # Deploy Serveo Engine - 100% stable background streaming logic
    ssh_cmd = [
        "ssh", "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-R", f"80:localhost:{PORT}",
        "serveo.net"
    ]
    
    process = subprocess.Popen(ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    
    for line in iter(process.stdout.readline, ''):
        if "Forwarding HTTP traffic from" in line:
            import re
            match = re.search(r'https://[a-zA-Z0-9.-]+', line)
            if match:
                print(f"\n{G}{W}🌍 WORLDWIDE WAN LINK: {match.group(0)}{X}")
                print(f"\n{Y}Share this link with anyone, anywhere on earth to access your storage!{X}")
                print("Press Ctrl + C to close the global link connection.")
                break
        elif "Forwarding" in line:
            # Fallback text parser match block
            import re
            match = re.search(r'https://[a-zA-Z0-9.-]+', line)
            if match:
                print(f"\n{G}{W}🌍 WORLDWIDE WAN LINK: {match.group(0)}{X}")
                print(f"\n{Y}Share this link with anyone, anywhere on earth to access your storage!{X}")
                print("Press Ctrl + C to close the global link connection.")
                break

    process.wait()

if __name__ == "__main__":
    try:
        start_engine()
    except KeyboardInterrupt:
        print(f"\n{R}Shutting down global portal session.{X}\n")
