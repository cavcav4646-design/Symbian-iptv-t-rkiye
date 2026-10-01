from flask import Flask, Response, request
import requests

app = Flask(__name__)

# Hedef M3U Listesi
M3U_URL = "https://tinyurl.com/ByteFixRepairs2026"

@app.route('/')
def index():
    return "Symbian TS Proxy Aktif! /playlist.ts adresini kullanın."

@app.route('/playlist.ts')
def playlist_ts():
    try:
        headers = {'User-Agent': 'VLC/3.0.16 LibVLC/3.0.16'}
        r = requests.get(M3U_URL, headers=headers, timeout=10)
        r.encoding = 'utf-8'
        lines = r.text.splitlines()
        
        new_lines = []
        server_host = request.host
        
        for line in lines:
            if line.startswith('http://') or line.startswith('https://'):
                # CorePlayer'ın doğrudan ts akışı olarak tetiklemesi için yönlendirme
                proxy_link = f"http://{server_host}/stream.ts?url={line}"
                new_lines.append(proxy_link)
            else:
                new_lines.append(line)
                
        output = "\n".join(new_lines)
        # CorePlayer'ın doğrudan tanıması için mpegurl/ts MIME tipi
        return Response(output, mimetype='audio/x-mpegurl')
    except Exception as e:
        return f"Liste indirilemedi: {str(e)}", 500

@app.route('/stream.ts')
def stream_ts():
    target_url = request.args.get('url')
    if not target_url:
        return "URL belirtilmedi", 400
        
    def generate():
        try:
            s = requests.get(target_url, stream=True, timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
            for chunk in s.iter_content(chunk_size=1024):
                if chunk:
                    yield chunk
        except Exception:
            return

    return Response(generate(), mimetype='video/mp2t')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
