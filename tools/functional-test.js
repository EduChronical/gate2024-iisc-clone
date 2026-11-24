// Functional checks: dropdowns, mobile menu, search overlay + page, notifications panel, downloads.
const { chromium } = require('playwright-core');
const BASE=(process.argv[2]||'http://localhost:8080').replace(/\/$/,'');
const V=__dirname+'/../visual-comparison/';
const results=[]; const ok=(n,c,d='')=>{results.push({test:n,pass:!!c,detail:d});};
(async()=>{
  const b=await chromium.launch({executablePath:process.env.CHROME||'/usr/bin/google-chrome',args:['--no-sandbox']});
  // desktop
  let p=await b.newPage({viewport:{width:1440,height:900}}); const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>m.type()==='error'&&errs.push(m.text()));
  await p.goto(BASE+'/',{waitUntil:'networkidle'});
  await p.hover('#menu-global-navigation > li.menu-item-has-children >> nth=0'); await p.waitForTimeout(600);
  const sub=await p.locator('#menu-global-navigation > li.menu-item-has-children >> nth=0 >> .sub-menu').isVisible();
  ok('Desktop dropdown "Gate Papers" opens on hover',sub);
  await p.screenshot({path:V+'func-desktop-dropdown.png'});
  await p.click('#menu-global-navigation > li.menu-item-has-children >> nth=0 >> .sub-menu a >> nth=0'); await p.waitForLoadState('networkidle');
  ok('Dropdown link navigates',p.url().includes('/papers-and-syllabus/'),p.url());
  ok('Active menu state on internal page',await p.locator('#menu-global-navigation .current-menu-item, #menu-global-navigation .current-menu-ancestor, #menu-global-navigation .current_page_item').count()>0);
  await p.goto(BASE+'/',{waitUntil:'networkidle'});
  await p.click('.gc-desk-tools .gc-search-btn'); await p.fill('.gc-search input','brochure'); await p.waitForTimeout(300);
  const nres=await p.locator('.gc-search .gc-results a').count(); ok('Search overlay returns results for "brochure"',nres>0,nres+' results');
  const dl=await p.locator('.gc-search .gc-results a[href$=".pdf"]').count(); ok('Search finds downloadable PDFs',dl>0,dl+' pdf hits');
  await p.screenshot({path:V+'func-search-overlay.png'});
  await p.keyboard.press('Escape'); ok('Esc closes search',await p.locator('.gc-search').isHidden());
  await p.keyboard.press('/'); ok('"/" shortcut opens search',await p.locator('.gc-search').isVisible()); await p.keyboard.press('Escape');
  await p.click('.gc-desk-tools .gc-bell-btn'); await p.waitForTimeout(200);
  const nn=await p.locator('#gc-notifications li a[data-u]').count(); ok('Notifications panel lists announcements',nn>0,nn+' items');
  const badge1=await p.locator('.gc-desk-tools .gc-badge').textContent();
  await p.screenshot({path:V+'func-notifications.png'});
  await p.click('#gc-notifications .gc-x >> nth=0'); const nn2=await p.locator('#gc-notifications li a[data-u]').count(); ok('Dismiss removes a notification',nn2===nn-1,`${nn} -> ${nn2}`);
  await p.click('#gc-notifications [data-all]'); const hidden=await p.locator('.gc-desk-tools .gc-badge').isHidden(); ok('Mark all read clears badge',hidden,'badge was '+badge1);
  await p.click('#gc-notifications li a[data-u] >> nth=0'); await p.waitForLoadState('networkidle'); ok('Notification link opens post',!p.url().endsWith(':8080/'),p.url());
  // ticker + view all
  await p.goto(BASE+'/',{waitUntil:'networkidle'});
  ok('Homepage notifications ticker present',await p.locator('.dtq-news-wrap li').count()>0);
  // search page
  await p.goto(BASE+'/search/?s=cut-off',{waitUntil:'networkidle'}); const sp=await p.locator('.gc-page-results a').count(); ok('Search page (/search/?s=cut-off) renders results',sp>0,sp+' results');
  // download links
  await p.goto(BASE+'/papers-and-syllabus/',{waitUntil:'networkidle'});
  const hrefs=await p.$$eval('a[href$=".pdf"]',as=>as.map(a=>a.href)); let bad=0; for(const h of hrefs){const r=await p.request.get(h);if(r.status()!==200)bad++}
  ok('PDF download links on papers-and-syllabus return 200',hrefs.length>0&&bad===0,`${hrefs.length} links, ${bad} bad`);
  ok('No page errors on desktop flows',errs.length===0,errs.slice(0,3).join(' | '));
  await p.close();
  // mobile
  p=await b.newPage({viewport:{width:390,height:844}}); await p.goto(BASE+'/',{waitUntil:'networkidle'});
  await p.click('.et-l--header .mobile_nav'); await p.waitForTimeout(800);
  const mm=await p.locator('.et-l--header .et_mobile_menu').isVisible(); ok('Mobile hamburger opens menu',mm);
  await p.screenshot({path:V+'func-mobile-menu.png'});
  await p.click('.gc-mobile-tools .gc-search-btn'); await p.fill('.gc-search input','exam cities'); await p.waitForTimeout(300);
  ok('Mobile search works',await p.locator('.gc-search .gc-results a').count()>0); await p.screenshot({path:V+'func-mobile-search.png'});
  await p.close();
  // tablet
  p=await b.newPage({viewport:{width:768,height:1024}}); await p.goto(BASE+'/',{waitUntil:'networkidle'});
  await p.click('.et-l--header .mobile_nav'); await p.waitForTimeout(800); ok('Tablet hamburger opens menu',await p.locator('.et-l--header .et_mobile_menu').isVisible());
  await p.close(); await b.close();
  for(const r of results) console.log((r.pass?'PASS':'FAIL')+'  '+r.test+(r.detail?'  ('+r.detail+')':''));
  console.log(`${results.filter(r=>r.pass).length}/${results.length} passed`);
})();
