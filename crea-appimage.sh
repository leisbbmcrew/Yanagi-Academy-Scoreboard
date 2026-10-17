#!/bin/sh
# Crea YanagiServer-x86_64.AppImage. Da lanciare su un PC Linux con python3 e connessione (scarica appimagetool).
# Metti nella stessa cartella: server.py locale.js scarica-bandiere.py gare.html index.html pdg.html sw.js
set -e; cd "$(dirname "$0")"
A=YanagiServer.AppDir; rm -rf "$A"; mkdir -p "$A/usr/share/yanagi"
cp server.py locale.js *.html sw.js "$A/usr/share/yanagi/" 2>/dev/null || true
[ -d flags ] && cp -r flags "$A/usr/share/yanagi/" || echo "Nota: cartella flags assente, lancia prima scarica-bandiere.py (serve internet)"
python3 - "$A/yanagi.png" <<'PY'
import sys,zlib,struct
w=h=64;raw=b''.join(b'\0'+bytes([200,30,30,255])*w for _ in range(h))
c=lambda t,d:struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
open(sys.argv[1],'wb').write(b'\x89PNG\r\n\x1a\n'+c(b'IHDR',struct.pack('>IIBBBBB',w,h,8,6,0,0,0))+c(b'IDAT',zlib.compress(raw))+c(b'IEND',b''))
PY
cat > "$A/yanagi.desktop" <<'D'
[Desktop Entry]
Type=Application
Name=Server Yanagi Academy
Exec=AppRun
Icon=yanagi
Terminal=true
Categories=Utility;
D
cat > "$A/AppRun" <<'R'
#!/bin/sh
D="$(dirname "$(readlink -f "$0")")/usr/share/yanagi"
DATI="${XDG_DOCUMENTS_DIR:-$HOME}/dati-evento.json"
echo "1 = dati DEFINITIVI (salvati in $DATI)   2 = dati TEMPORANEI (cancellati alla chiusura)"
printf "Scegli 1 o 2: "; read s
if [ "$s" = 2 ]; then exec python3 "$D/server.py" --cartella "$D" --temp; else exec python3 "$D/server.py" --cartella "$D" --dati "$DATI"; fi
R
chmod +x "$A/AppRun"
[ -x ./appimagetool ] || { echo "Scarico appimagetool..."; curl -L -o appimagetool https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage; chmod +x appimagetool; }
ARCH=x86_64 ./appimagetool "$A" YanagiServer-x86_64.AppImage
echo "Fatto: YanagiServer-x86_64.AppImage (richiede python3 sul PC che lo esegue)"
