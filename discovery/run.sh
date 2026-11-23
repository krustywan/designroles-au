python3 -c "
import os, fetch_logos as F
os.makedirs(F.OUT, exist_ok=True)
print('RESULT', F.one(('Qantas Group','qantas.com')))
"
mkdir -p discovery/out/q && cp logos/qantas.com.* discovery/out/q/ 2>/dev/null; ls discovery/out/q
