#!/usr/bin/env python3
"""Scarica le bandiere (SVG) nella cartella flags/4x3 accanto a questo file, per usarle senza internet.
Da lanciare UNA volta, con internet attivo:  python scarica-bandiere.py   (su Windows: py scarica-bandiere.py)"""
import os, sys, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
BASE = os.environ.get('BANDIERE_URL', 'https://cdn.jsdelivr.net/gh/lipis/flag-icons@7.3.2/flags/4x3/')
COD = ("ad ae af ag ai al am ao aq ar as at au aw ax az ba bb bd be bf bg bh bi bj bl bm bn bo bq br bs bt bv bw by bz ca cc cd cf cg ch ci ck cl cm cn co cr cu cv cw cx cy cz de dj dk dm do dz ec ee eg eh er es et fi fj fk fm fo fr ga gb gd ge gf gg gh gi gl gm gn gp gq gr gs gt gu gw gy hk hm hn hr ht hu id ie il im in io iq ir is it je jm jo jp ke kg kh ki km kn kp kr kw ky kz la lb lc li lk lr ls lt lu lv ly ma mc md me mf mg mh mk ml mm mn mo mp mq mr ms mt mu mv mw mx my mz na nc ne nf ng ni nl no np nr nu nz om pa pe pf pg ph pk pl pm pn pr ps pt pw py qa re ro rs ru rw sa sb sc sd se sg sh si sj sk sl sm sn so sr ss st sv sx sy sz tc td tf tg th tj tk tl tm tn to tr tt tv tw tz ua ug um us uy uz va vc ve vg vi vn vu wf ws xk ye yt za zm zw").split()
DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'flags', '4x3'); os.makedirs(DEST, exist_ok=True)
def prendi(c):
    f = os.path.join(DEST, c + '.svg')
    if os.path.exists(f) and os.path.getsize(f) > 50: return 'ok'
    try:
        with urllib.request.urlopen(BASE + c + '.svg', timeout=10) as r: d = r.read()
        if len(d) < 50: return 'manca'
        with open(f, 'wb') as o: o.write(d)
        return 'ok'
    except urllib.error.HTTPError: return 'manca'
    except Exception: return 'rete'
r0 = prendi(COD[0])
if r0 == 'rete': print('Internet non raggiungibile: riprova con la connessione attiva.'); sys.exit(1)
with ThreadPoolExecutor(12) as ex: ris = [r0] + list(ex.map(prendi, COD[1:]))
print('Bandiere scaricate: %d su %d (%d non disponibili, %d errori di rete).' % (ris.count('ok'), len(COD), ris.count('manca'), ris.count('rete')))
print('Cartella:', DEST); sys.exit(0 if ris.count('rete') == 0 else 1)
