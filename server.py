#!/usr/bin/env python3
"""Server locale Yanagi Academy: sostituisce Firebase su una rete senza internet.
Serve le pagine (gare.html, index.html, pdg.html...) e conserva i dati dell'evento.
Uso: python3 server.py [--porta 8080] [--dati dati-evento.json] [--temp] [--cartella .]"""
import argparse, json, os, queue, signal, socket, threading, time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

DOCS, LOCK, WATCH, DIRTY, CFG = {}, threading.Lock(), [], [False], {'temp': False, 'port': 8080, 'conn': 0}

def parent(p): return p.rsplit('/', 1)[0] if '/' in p else ''

def notify(p, d, c=None):
    for path, q in list(WATCH):
        if path == p: q.put({'t': 'doc', 'w': p, 'p': p, 'd': d, 'c': c})
        elif path == parent(p): q.put({'t': 'ch', 'w': path, 'id': p.rsplit('/', 1)[1], 'd': d, 'c': c})

def save(path):
    while True:
        time.sleep(2)
        if DIRTY[0]:
            DIRTY[0] = False
            with LOCK: txt = json.dumps(DOCS, ensure_ascii=False)
            tmp = path + '.tmp'
            with open(tmp, 'w', encoding='utf-8') as f: f.write(txt)
            os.replace(tmp, path)

class H(SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Private-Network', 'true')
        self.send_header('Access-Control-Allow-Headers', 'content-type')
        self.send_header('Cache-Control', 'public, max-age=86400' if self.path.startswith('/flags/') else 'no-store')
        super().end_headers()
    def send_error(self, code, message=None, explain=None):
        if code == 404 and not self.path.startswith('/api/'): print('  [!] File non trovato:', self.path.split('?')[0], '- cercato in:', os.getcwd())
        super().send_error(code, message, explain)
    def do_OPTIONS(self): self.send_response(204); self.end_headers()
    def js(self, o, code=200):
        b = json.dumps(o, ensure_ascii=False).encode()
        self.send_response(code); self.send_header('Content-Type', 'application/json'); self.send_header('Content-Length', str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_POST(self):
        r = json.loads(self.rfile.read(int(self.headers.get('Content-Length', 0))) or b'{}')
        u = urlparse(self.path).path; p = r.get('p', '')
        if u == '/api/modo': CFG['temp'] = bool(r.get('temp')); return self.js({'ok': 1, 'temp': CFG['temp']})
        if not p.startswith('ev/'): return self.js({'err': 'percorso non valido'}, 400)
        with LOCK:
            if u == '/api/set':
                d = r.get('d') or {}
                if r.get('merge') and isinstance(DOCS.get(p), dict): d = {**DOCS[p], **d}
                DOCS[p] = d
            elif u == '/api/del': DOCS.pop(p, None); d = None
            else: return self.js({'err': 'sconosciuto'}, 404)
            DIRTY[0] = True; notify(p, d, r.get('c'))
        self.js({'ok': 1})
    def do_GET(self):
        u = urlparse(self.path); q = parse_qs(u.query); p = (q.get('p') or [''])[0]
        if u.path == '/api/ping': return self.js({'ok': 1, 'docs': len(DOCS), 'temp': CFG['temp'], 'port': CFG['port'], 'ips': ips(), 'conn': CFG['conn']})
        if u.path == '/api/get':
            with LOCK: return self.js([{'id': k.rsplit('/', 1)[1], 'd': v} for k, v in DOCS.items() if parent(k) == p])
        if u.path == '/api/watch':
            ps = q.get('p') or ['']; qq = queue.Queue(); items = [(x, qq) for x in ps]
            with LOCK:
                WATCH.extend(items); CFG['conn'] += 1
                firsts = [{'t': 'init', 'w': x, 'p': x, 'docs': [{'id': k.rsplit('/', 1)[1], 'd': v} for k, v in DOCS.items() if parent(k) == x], 'd': DOCS.get(x)} for x in ps]
            self.send_response(200); self.send_header('Content-Type', 'text/event-stream'); self.end_headers()
            try:
                for f in firsts: self.wfile.write(('data: ' + json.dumps(f, ensure_ascii=False) + '\n\n').encode())
                self.wfile.flush()
                while True:
                    try: m = qq.get(timeout=15); self.wfile.write(('data: ' + json.dumps(m, ensure_ascii=False) + '\n\n').encode())
                    except queue.Empty: self.wfile.write(b': ping\n\n')
                    self.wfile.flush()
            except Exception: pass
            finally:
                with LOCK:
                    CFG['conn'] -= 1
                    for it in items:
                        if it in WATCH: WATCH.remove(it)
            return
        super().do_GET()

def ips():
    out = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('10.255.255.255', 1)); out.add(s.getsockname()[0]); s.close()
    except Exception: pass
    try: out.update(i[4][0] for i in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET))
    except Exception: pass
    return sorted(i for i in out if not i.startswith('127.'))

if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--porta', type=int, default=8080); a.add_argument('--dati', default='dati-evento.json')
    a.add_argument('--temp', action='store_true', help='dati temporanei: cancellati alla chiusura')
    a.add_argument('--cartella', default=os.path.dirname(os.path.abspath(__file__)))
    o = a.parse_args(); os.chdir(o.cartella)
    CFG['temp'] = o.temp; CFG['port'] = o.porta
    if os.path.exists(o.dati) and not o.temp:
        with open(o.dati, encoding='utf-8') as f: DOCS.update(json.load(f))
    threading.Thread(target=save, args=(o.dati,), daemon=True).start()
    srv = ThreadingHTTPServer(('0.0.0.0', o.porta), H); srv.daemon_threads = True
    print('Cartella delle pagine:', os.getcwd())
    manca = [f for f in ('gare.html', 'index.html', 'pdg.html', 'premiazioni.html', 'locale.js') if not os.path.exists(f)]
    if manca: print('  [!] ATTENZIONE: nella cartella mancano:', ', '.join(manca), '- copiali accanto a server.py')
    print('Server Yanagi Academy attivo. Dati:', ('TEMPORANEI (file cancellato alla chiusura): ' if o.temp else '') + os.path.abspath(o.dati))
    for i in ips(): print('  Apri dagli altri dispositivi:  http://%s:%d/gare.html' % (i, o.porta))
    print('  Su questo dispositivo:         http://localhost:%d/gare.html\nCtrl+C per chiudere.' % o.porta)
    signal.signal(signal.SIGTERM, lambda *x: (_ for _ in ()).throw(KeyboardInterrupt()))
    try: srv.serve_forever()
    except KeyboardInterrupt: pass
    finally:
        if CFG['temp']:
            try: os.remove(o.dati)
            except Exception: pass
        else:
            with open(o.dati, 'w', encoding='utf-8') as f: json.dump(DOCS, f, ensure_ascii=False)
