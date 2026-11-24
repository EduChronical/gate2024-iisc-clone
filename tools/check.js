// Crawl every page of the running clone: console/page errors, failed local requests, broken internal links.
const { chromium } = require('playwright-core');
const BASE = (process.argv[2] || 'http://localhost:8080').replace(/\/$/, '');
const EXE = process.env.CHROME || '/usr/bin/google-chrome';
(async () => {
  const b = await chromium.launch({ executablePath: EXE, args: ['--no-sandbox'] });
  const ctx = await b.newContext({ viewport: { width: 1440, height: 900 } });
  const seen = new Set(), queue = ['/'], problems = [], linkStatus = {};
  let pagesChecked = 0;
  while (queue.length) {
    const path = queue.shift(); if (seen.has(path)) continue; seen.add(path);
    const p = await ctx.newPage(); const errs = [];
    p.on('pageerror', e => errs.push('pageerror: ' + e.message));
    p.on('console', m => { if (m.type() === 'error') errs.push('console: ' + m.text()); });
    p.on('requestfailed', r => { if (r.url().startsWith(BASE)) errs.push('requestfailed: ' + r.url()); });
    p.on('response', r => { if (r.url().startsWith(BASE) && r.status() >= 400) errs.push('HTTP ' + r.status() + ': ' + r.url()); });
    const resp = await p.goto(BASE + path, { waitUntil: 'networkidle', timeout: 60000 }).catch(e => (errs.push('goto: ' + e.message), null));
    if (resp && resp.status() >= 400) errs.push('page status ' + resp.status());
    pagesChecked++;
    const links = await p.$$eval('a[href]', as => as.map(a => a.href));
    for (const l of links) {
      if (!l.startsWith(BASE)) continue;
      const u = new URL(l); const clean = u.pathname;
      if (/\.(pdf|docx?|jpe?g|png)$/i.test(clean)) { linkStatus[clean] = linkStatus[clean] || { from: path }; continue; }
      if (!seen.has(clean) && !queue.includes(clean)) queue.push(clean);
    }
    if (errs.length) problems.push({ path, errs: [...new Set(errs)] });
    await p.close();
  }
  for (const f of Object.keys(linkStatus)) {
    const r = await ctx.request.get(BASE + f); linkStatus[f].status = r.status();
    if (r.status() >= 400) problems.push({ path: linkStatus[f].from, errs: ['broken download ' + f + ' ' + r.status()] });
  }
  console.log(JSON.stringify({ pagesChecked, pages: [...seen], downloadsChecked: Object.keys(linkStatus).length, problems }, null, 1));
  await b.close();
})();
