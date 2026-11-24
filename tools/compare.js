// Capture original vs clone at given viewport, freezing sliders/tickers identically in both, then build side-by-side.
const { chromium } = require('playwright-core'); const {execSync}=require('child_process');
const V=__dirname+'/../visual-comparison';
const jobs=JSON.parse(process.argv[2]);
async function shot(b,url,out,w,h,full){
  const p=await b.newPage({viewport:{width:w,height:h}});
  await p.goto(url,{waitUntil:'networkidle',timeout:120000}).catch(e=>console.log('goto',url,e.message));
  await p.evaluate(async()=>{for(let y=0;y<document.body.scrollHeight;y+=500){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,80))}window.scrollTo(0,0)});
  await p.waitForTimeout(2500);
  await p.evaluate(()=>{ // freeze: stop timers, show first slide only, stop ticker animation
    let id=setTimeout(()=>{},0); while(id--) {clearTimeout(id);clearInterval(id);}
    document.querySelectorAll('.et_pb_slider').forEach(sl=>{sl.querySelectorAll('.et_pb_slide').forEach((s,i)=>{s.style.opacity=i?0:1;s.style.display=i?'none':'block';s.classList.toggle('et-pb-active-slide',!i);s.style.zIndex=i?0:2});});
    const st=document.createElement('style');st.textContent='*,*:before,*:after{animation-play-state:paused!important;transition:none!important}.dtq-news-wrap{transform:none!important;animation:none!important;left:0!important}';document.head.appendChild(st);
    document.querySelectorAll('.et_animated').forEach(e=>{e.style.opacity=1;e.style.animation='none'});
  });
  await p.waitForTimeout(500);
  await p.screenshot({path:out,fullPage:!!full}); await p.close();
}
(async()=>{
  const b=await chromium.launch({executablePath:'/usr/bin/google-chrome',args:['--no-sandbox']});
  for(const j of jobs){
    const o=`${V}/original-${j.name}.png`, c=`${V}/clone-${j.name}.png`;
    await shot(b,'https://gate2024.iisc.ac.in'+j.path,o,j.w,j.h,j.full);
    await shot(b,'http://localhost:8080'+j.path,c,j.w,j.h,j.full);
    console.log(execSync(`python3 ${__dirname}/sbs.py "${o}" "${c}" "${V}/compare-${j.name}.png" 2>/dev/null`).toString().trim());
    console.log('done',j.name);
  }
  await b.close();
})();
