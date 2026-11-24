#!/usr/bin/env node
// Zero-dependency static server for the GATE 2024 clone.  Usage: node server.js [port]
const http = require('http'), fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, 'site');
const PORT = +(process.argv[2] || process.env.PORT || 8080);
const TYPES = {'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'application/javascript; charset=utf-8','.json':'application/json','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.gif':'image/gif','.svg':'image/svg+xml','.webp':'image/webp','.ico':'image/x-icon','.woff':'font/woff','.woff2':'font/woff2','.ttf':'font/ttf','.eot':'application/vnd.ms-fontobject','.otf':'font/otf','.pdf':'application/pdf','.docx':'application/vnd.openxmlformats-officedocument.wordprocessingml.document','.txt':'text/plain; charset=utf-8','.xml':'application/xml'};
function typeOf(f){ // wget-style names like "style.css@ver=1.2.css" or "x.js@ver=3"
  let ext = path.extname(f).toLowerCase();
  if (!TYPES[ext]) { const m = f.match(/\.(css|js|png|jpe?g|gif|svg|woff2?|ttf|eot|otf|webp)@/i); if (m) ext = '.' + m[1].toLowerCase(); }
  return TYPES[ext] || 'application/octet-stream';
}
http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split('?')[0].split('#')[0]);
  // tolerate un-rewritten "?ver=" requests made by scripts: try wget's "@" naming
  const q = req.url.includes('?') ? req.url.slice(req.url.indexOf('?') + 1) : '';
  let f = path.normalize(path.join(ROOT, p));
  if (!f.startsWith(ROOT)) { res.writeHead(403); return res.end('Forbidden'); }
  try { if (fs.statSync(f).isDirectory()) { if (!p.endsWith('/')) { res.writeHead(301, {Location: p + '/' + (q ? '?' + q : '')}); return res.end(); } f = path.join(f, 'index.html'); } } catch (e) {
    const alt = q ? f + '@' + q : null;
    if (alt && fs.existsSync(alt)) f = alt;
  }
  fs.readFile(f, (err, data) => {
    if (err) { res.writeHead(404, {'Content-Type': 'text/html; charset=utf-8'}); return res.end(fs.existsSync(path.join(ROOT,'404.html')) ? fs.readFileSync(path.join(ROOT,'404.html')) : '<h1>404 Not Found</h1>'); }
    res.writeHead(200, {'Content-Type': typeOf(f), 'Cache-Control': 'no-cache'});
    res.end(data);
  });
}).listen(PORT, () => console.log(`GATE 2024 clone running at http://localhost:${PORT}/`));
