#!/usr/bin/env python3
"""Loopback-only exact allowlist, GET/HEAD only, no source HTML execution."""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
import json, os, re, urllib.parse
BASE=Path(__file__).resolve().parent
ALLOWED=json.loads((BASE/'allowlist.json').read_text())
STATIC={'/':('index.html','text/html; charset=utf-8'),'/index.html':('index.html','text/html; charset=utf-8'),'/app.css':('app.css','text/css; charset=utf-8'),'/app.js':('app.js','text/javascript; charset=utf-8'),'/catalog.json':('catalog.json','application/json; charset=utf-8')}
class Handler(BaseHTTPRequestHandler):
 def do_HEAD(self):self.respond(True)
 def do_GET(self):self.respond(False)
 def respond(self,head):
  if self.headers.get('Host')!=f'127.0.0.1:{self.server.server_port}':self.send_error(403);return
  origin=self.headers.get('Origin')
  if origin and origin!=f'http://127.0.0.1:{self.server.server_port}':self.send_error(403);return
  route=urllib.parse.urlsplit(self.path).path
  if route in STATIC:
   n,mime=STATIC[route];p=BASE/n
  elif re.fullmatch(r'/asset/[0-9a-f]{24}',route) and route[7:] in ALLOWED:
   rec=ALLOWED[route[7:]];p=Path(rec['path'])
   if not p.is_file() or str(p.resolve())!=rec['path']:self.send_error(404);return
   if p.stat().st_size!=rec['bytes'] or p.stat().st_mtime_ns!=rec['mtime_ns']:self.send_error(409,'Source changed; regenerate catalogue');return
   mime={'.mp4':'video/mp4','.png':'image/png','.jpg':'image/jpeg','.json':'application/json'}.get(p.suffix,'text/plain; charset=utf-8')
  else:self.send_error(404);return
  size=p.stat().st_size;start=0;end=size-1;status=200
  rng=self.headers.get('Range')
  if rng:
   m=re.fullmatch(r'bytes=(\d*)-(\d*)',rng)
   if not m or not any(m.groups()):self.send_error(416);return
   if m[1]:start=int(m[1]);end=min(int(m[2]),size-1) if m[2] else size-1
   else:start=max(0,size-int(m[2]))
   if start>end or start>=size:self.send_error(416);return
   status=206
  self.send_response(status);self.send_header('Content-Type',mime);self.send_header('Content-Length',str(end-start+1));self.send_header('Accept-Ranges','bytes');self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.send_header('Cross-Origin-Resource-Policy','same-origin');self.send_header('Referrer-Policy','no-referrer')
  self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; media-src 'self'; img-src 'self'; connect-src 'self'; object-src 'none'; frame-src 'none'; base-uri 'none'; frame-ancestors 'none'")
  if status==206:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers()
  if head:return
  try:
   with p.open('rb') as f:
    f.seek(start);left=end-start+1
    while left:
     chunk=f.read(min(left,128*1024))
     if not chunk:break
     self.wfile.write(chunk);left-=len(chunk)
  except (BrokenPipeError,ConnectionResetError):pass
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',int(os.environ.get('CATALOG_PORT','0'))),Handler)
runtime={'pid':os.getpid(),'url':f'http://127.0.0.1:{server.server_port}/','bind':'127.0.0.1','command':'python3 serve.py','root':str(BASE),'allowlist_files':len(ALLOWED)}
(BASE/'runtime.json').write_text(json.dumps(runtime,ensure_ascii=False,indent=2))
print(json.dumps(runtime,ensure_ascii=False),flush=True)
server.serve_forever()
