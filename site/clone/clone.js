/* GATE 2024 clone: client-side search, notifications panel, link hygiene. No dependencies. */
(function(){
  'use strict';
  var ROOT = window.CLONE_ROOT || '/';
  var IDX = window.CLONE_INDEX || {pages:[],downloads:[],notifications:[]};
  var READ_KEY = 'gate2024-clone-read', DISMISS_KEY = 'gate2024-clone-dismissed';
  function $(s,c){return (c||document).querySelector(s)}
  function el(tag,attrs,html){var e=document.createElement(tag);for(var k in attrs||{})e.setAttribute(k,attrs[k]);if(html!=null)e.innerHTML=html;return e}
  function href(u){return /^https?:/.test(u)?u:ROOT+u.replace(/^\//,'')}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]})}
  function load(k){try{return JSON.parse(localStorage.getItem(k))||[]}catch(e){return[]}}
  function save(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}

  /* ---------- search ---------- */
  function terms(q){return q.toLowerCase().split(/\s+/).filter(function(t){return t.length>0})}
  function score(text,ts){var s=0,l=text.toLowerCase();for(var i=0;i<ts.length;i++){var c=l.split(ts[i]).length-1;if(!c)return 0;s+=c}return s}
  function hl(text,ts){var out=esc(text);ts.forEach(function(t){if(t.length<2)return;out=out.replace(new RegExp('('+t.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+')','gi'),'<mark>$1</mark>')});return out}
  function snippet(body,ts){var l=body.toLowerCase(),i=l.indexOf(ts[0]);if(i<0)return body.slice(0,160);var s=Math.max(0,i-70);if(s){var sp=body.indexOf(' ',s);if(sp>-1&&sp<i)s=sp+1}var e=body.lastIndexOf(' ',s+200);if(e<=i)e=s+200;return(s?'… ':'')+body.slice(s,e)+'…'}
  function search(q){
    var ts=terms(q);if(!ts.length)return null;
    var pages=IDX.pages.map(function(p){var st=score(p.t,ts)*10,sb=score(p.t+' '+p.b,ts);return{p:p,s:st+sb}}).filter(function(x){return x.s>0}).sort(function(a,b){return b.s-a.s}).slice(0,25);
    var dls=IDX.downloads.filter(function(d){return score(d.t+' '+d.u+' '+d.pt,ts)>0}).slice(0,15);
    var nts=IDX.notifications.filter(function(n){return score(n.t,ts)>0}).slice(0,10);
    return{ts:ts,pages:pages,dls:dls,nts:nts};
  }
  function render(r,box){
    if(!r){box.innerHTML='<div class="gc-hint">Search pages, announcements, important dates and downloads. Try <em>brochure</em>, <em>cut-off</em>, <em>eligibility</em> or <em>exam cities</em>. <span class="gc-kbd">Esc</span> to close.</div>';return}
    var h='';
    if(r.nts.length){h+='<h4>Notifications</h4>';r.nts.forEach(function(n){h+='<a href="'+esc(href(n.u))+'"><b>'+hl(n.t,r.ts)+'</b><span>'+esc(n.d)+'</span></a>'})}
    if(r.pages.length){h+='<h4>Pages</h4>';r.pages.forEach(function(x){h+='<a href="'+esc(href(x.p.u))+'"><b>'+hl(x.p.t,r.ts)+'</b><span>'+hl(snippet(x.p.b,r.ts),r.ts)+'</span></a>'})}
    if(r.dls.length){h+='<h4>Downloads</h4>';r.dls.forEach(function(d){h+='<a href="'+esc(href(d.u))+'" target="_blank" rel="noopener"><b>'+hl(d.t,r.ts)+'</b><span>'+esc(d.u.split('/').pop())+' · from '+esc(d.pt)+'</span></a>'})}
    box.innerHTML=h||'<div class="gc-hint">No results for “'+esc(r.ts.join(' '))+'”.</div>';
  }
  var overlay;
  function openSearch(prefill){
    if(!overlay){
      overlay=el('div',{'class':'gc-search',role:'dialog','aria-modal':'true','aria-label':'Search GATE 2024',hidden:''});
      overlay.innerHTML='<div class="gc-search-box"><form role="search"><input type="search" name="s" placeholder="Search GATE 2024…" aria-label="Search GATE 2024" autocomplete="off"><button type="button" class="gc-close" aria-label="Close search">&times;</button></form><div class="gc-results" aria-live="polite"></div></div>';
      document.body.appendChild(overlay);
      var inp=$('input',overlay),res=$('.gc-results',overlay);
      inp.addEventListener('input',function(){render(search(inp.value),res)});
      $('form',overlay).addEventListener('submit',function(e){e.preventDefault();var a=$('a.gc-active',res)||$('a',res);if(a)location.href=a.href});
      inp.addEventListener('keydown',function(e){if(e.key!=='ArrowDown'&&e.key!=='ArrowUp')return;e.preventDefault();var as=[].slice.call(res.querySelectorAll('a')),i=as.indexOf($('a.gc-active',res));if(i>=0)as[i].classList.remove('gc-active');i=e.key==='ArrowDown'?Math.min(as.length-1,i+1):Math.max(0,i-1);if(as[i]){as[i].classList.add('gc-active');as[i].scrollIntoView({block:'nearest'})}});
      $('.gc-close',overlay).addEventListener('click',closeSearch);
      overlay.addEventListener('click',function(e){if(e.target===overlay)closeSearch()});
    }
    overlay.hidden=false;var inp=$('input',overlay);inp.value=prefill||'';render(search(inp.value),$('.gc-results',overlay));setTimeout(function(){inp.focus()},20);
  }
  function closeSearch(){if(overlay&&!overlay.hidden){overlay.hidden=true;var a=document.activeElement;if(a&&overlay.contains(a))a.blur()}}
  window.gcOpenSearch=openSearch;

  /* ---------- notifications ---------- */
  var panel,badge;
  function visibleNotes(){var d=load(DISMISS_KEY);return IDX.notifications.filter(function(n){return d.indexOf(n.u)<0})}
  function unread(){var r=load(READ_KEY);return visibleNotes().filter(function(n){return r.indexOf(n.u)<0})}
  function refreshBadge(){var n=unread().length;document.querySelectorAll('.gc-badge').forEach(function(b){b.textContent=n>9?'9+':n;b.hidden=!n})}
  function renderPanel(){
    var r=load(READ_KEY),items=visibleNotes(),ul=$('ul',panel);
    ul.innerHTML=items.length?items.map(function(n){return '<li class="'+(r.indexOf(n.u)<0?'gc-unread':'')+'"><a href="'+esc(href(n.u))+'" data-u="'+esc(n.u)+'">'+esc(n.t)+'<small>'+esc(n.d)+'</small></a><button class="gc-x" data-u="'+esc(n.u)+'" aria-label="Dismiss notification" title="Dismiss">&times;</button></li>'}).join(''):'<li class="gc-empty">You’re all caught up. <a href="#" data-restore style="display:inline;padding:0;color:#005059;text-decoration:underline">Restore dismissed</a></li>';
  }
  function togglePanel(btn){
    if(!panel){
      panel=el('div',{'class':'gc-panel',id:'gc-notifications',role:'dialog','aria-label':'Notifications',hidden:''});
      panel.innerHTML='<header><h3>Notifications</h3><button type="button" data-all>Mark all as read</button></header><ul></ul><div class="gc-foot"><a href="'+href('/category/notifications/')+'">View all notifications</a><button type="button" data-close>Close</button></div>';
      document.body.appendChild(panel);
      panel.addEventListener('click',function(e){
        var t=e.target;
        if(t.matches('[data-all]')){save(READ_KEY,IDX.notifications.map(function(n){return n.u}));renderPanel();refreshBadge()}
        else if(t.matches('[data-close]'))panel.hidden=true;
        else if(t.matches('.gc-x')){var d=load(DISMISS_KEY);d.push(t.getAttribute('data-u'));save(DISMISS_KEY,d);renderPanel();refreshBadge()}
        else if(t.matches('[data-restore]')){e.preventDefault();save(DISMISS_KEY,[]);renderPanel();refreshBadge()}
        else{var a=t.closest('a[data-u]');if(a){var r=load(READ_KEY);r.push(a.getAttribute('data-u'));save(READ_KEY,r)}}
      });
    }
    panel.hidden=!panel.hidden;
    if(!panel.hidden){renderPanel();var rc=btn.getBoundingClientRect();panel.style.top=Math.max(8,rc.bottom+10)+'px';var right=Math.max(12,window.innerWidth-rc.right-20);panel.style.right=Math.min(right,window.innerWidth-panel.offsetWidth-12)+'px';}
  }

  /* ---------- header tools ---------- */
  function toolButtons(){
    var f=document.createDocumentFragment();
    var s=el('li',{'class':'gc-tool'},'<button type="button" class="gc-btn gc-search-btn" aria-label="Search" title="Search (/)"><i class="fa-solid fa-magnifying-glass"></i></button>');
    var n=el('li',{'class':'gc-tool'},'<button type="button" class="gc-btn gc-bell-btn" aria-label="Notifications" aria-controls="gc-notifications" title="Notifications"><i class="fa-solid fa-bell"></i></button><span class="gc-badge" hidden></span>');
    f.appendChild(s);f.appendChild(n);return f;
  }
  function installTools(){
    // desktop: compact tool buttons in the top-right of the white branding band (keeps the original nav row untouched)
    var sec=$('.et-l--header .et_pb_section');
    if(sec){var d=el('ul',{'class':'gc-desk-tools et_pb_social_media_follow'});d.appendChild(toolButtons());sec.style.position='relative';sec.appendChild(d)}
    // tablet/mobile: the theme collapses the menu, so add the tools beside the hamburger
    var mob=$('.et-l--header .et_mobile_nav_menu');
    if(mob){var w=el('ul',{'class':'gc-mobile-tools et_pb_social_media_follow'});w.appendChild(toolButtons());mob.parentNode.style.position='relative';mob.parentNode.appendChild(w)}
    document.addEventListener('click',function(e){
      var b=e.target.closest('.gc-search-btn');if(b){e.preventDefault();openSearch();return}
      var n=e.target.closest('.gc-bell-btn');if(n){e.preventDefault();togglePanel(n);return}
      if(panel&&!panel.hidden&&e.composedPath().indexOf(panel)<0&&document.contains(e.target))panel.hidden=true;
    });
    document.addEventListener('keydown',function(e){
      if(e.key==='Escape'){closeSearch();if(panel)panel.hidden=true}
      if(e.key==='/'&&!/input|textarea|select/i.test(document.activeElement.tagName)){e.preventDefault();openSearch()}
    });
    refreshBadge();
  }

  /* ---------- WordPress search forms & the /search/ page ---------- */
  function wireForms(){
    document.querySelectorAll('form[role="search"]:not(.gc-search-box form)').forEach(function(f){
      f.addEventListener('submit',function(e){var i=f.querySelector('input[name="s"]');if(!i)return;e.preventDefault();location.href=href('/search/')+'?s='+encodeURIComponent(i.value)});
    });
    var q=new URLSearchParams(location.search).get('s')||new URLSearchParams(location.search).get('q');
    if(/\/search\/(index\.html)?$/.test(location.pathname)){
      var form=$('#et-main-area form[role="search"]');var wrap=el('div',{'class':'gc-page-results'},'<div class="gc-results" aria-live="polite"></div>');
      if(form){form.parentNode.insertBefore(wrap,form.nextSibling);var inp=form.querySelector('input[name="s"]');if(inp){inp.value=q||'';inp.addEventListener('input',function(){render(search(inp.value),$('.gc-results',wrap))})}}
      else{($('#et-main-area')||document.body).appendChild(wrap)}
      render(search(q||''),$('.gc-results',wrap));
    } else if(q){openSearch(q)}
  }

  /* ---------- links: placeholder parent items & external links ---------- */
  function links(){
    document.querySelectorAll('a[href$="#"],a[href="#"]').forEach(function(a){if(a.closest('.menu-item-has-children'))a.addEventListener('click',function(e){e.preventDefault()})});
    document.querySelectorAll('a[href^="http"]').forEach(function(a){if(!a.target)a.target='_blank';a.rel='noopener'});
    document.querySelectorAll('a[href$=".pdf"],a[href$=".docx"]').forEach(function(a){if(!/^http/.test(a.getAttribute('href'))){a.target='_blank';a.rel='noopener'}});
  }

  function init(){installTools();wireForms();links()}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
})();
/* Ninja Tables provenance note (tables are restored locally because the live table service returns 403) */
(function(){
  var ROOT=window.CLONE_ROOT||'/';
  function note(){
    var parents=document.querySelectorAll('[id^="footable_parent_"]'); if(!parents.length) return;
    fetch(ROOT+'clone/tables/meta.json').then(function(r){return r.json()}).then(function(meta){
      parents.forEach(function(p){
        var id=p.id.replace('footable_parent_',''); if(meta[id]!=='brochure'||p.querySelector('.gc-table-note'))return;
        var n=document.createElement('p'); n.className='gc-table-note';
        n.innerHTML='Table restored in this clone from the official <a href="'+ROOT+'wp-content/uploads/2023/09/GATE2024InformationBrochureSep27.pdf" target="_blank" rel="noopener">GATE 2024 Information Brochure</a> and site text (the live site’s table service is unavailable).';
        p.appendChild(n);
      });
    }).catch(function(){});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',note);else note();
})();
