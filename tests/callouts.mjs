import {connect} from './cdp.mjs';
const [base='http://127.0.0.1:4850/', phase='after', debug='http://127.0.0.1:9228'] = Deno.args;
if (!['before','after'].includes(phase)) throw Error('phase must be before or after');
const {cdp,evaluate,waitFor,theme,click,key,errors,close}=await connect(debug);
const report={phase,base,date:new Date().toISOString(),checks:[],styles:[],screenshots:[]};
function check(name,pass,details){report.checks.push({name,pass:!!pass,details});console.log(`${pass?'PASS':'FAIL'} ${name}`);}
await Deno.mkdir('artifacts/v0.2/comparison',{recursive:true});
await cdp('Emulation.setEmulatedMedia',{features:[{name:'prefers-reduced-motion',value:'reduce'}]});
for (const width of [1440,390,320]) {
  await cdp('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});
  await cdp('Page.navigate',{url:new URL('componentes.html',base).href});
  await waitFor("document.readyState==='complete' && !!document.querySelector('.uso-skip-link')");
  await evaluate('window.MathJax?.startup?.promise?.then(()=>true) ?? true');
  await evaluate('document.fonts.ready.then(()=>true)');
  for(const mode of ['light','dark']) {
    await theme(mode);
    await evaluate("document.querySelector('.callout-note').scrollIntoView({block:'center'})");
    const shot=await cdp('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
    const file=`artifacts/v0.2/comparison/${phase}-${width}-${mode}.png`;
    await Deno.writeFile(file,Uint8Array.from(atob(shot.data),c=>c.charCodeAt(0)));
    report.screenshots.push(file);
    const styles=await evaluate(`(()=>{
      const rgb=c=>c.match(/[\\d.]+/g).slice(0,3).map(Number);
      const lum=c=>rgb(c).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
      const contrast=(a,b)=>{const x=lum(a),y=lum(b);return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};
      return [...document.querySelectorAll('div.callout')].map(el=>{
        const header=el.querySelector('.callout-header'),icon=el.querySelector('.callout-icon'),toggle=el.querySelector('.callout-toggle');
        const s=getComputedStyle(el),h=getComputedStyle(header),i=icon&&getComputedStyle(icon,'::before'),t=toggle&&getComputedStyle(toggle,'::before');
        const title=getComputedStyle(el.querySelector('.callout-title-container'));
        const body=el.querySelector('.callout-body'),b=body&&getComputedStyle(body);
        const link=el.querySelector('.callout-body a'),l=link&&getComputedStyle(link);
        return {type:[...el.classList].find(c=>/^callout-(note|tip|important|caution|warning)$/.test(c)),title:header.textContent.trim(),expanded:header.getAttribute('aria-expanded'),header:h.backgroundColor,text:title.color,opacity:h.opacity,body:s.backgroundColor,border:s.borderLeftColor,outline:s.borderRightColor,icon:i&&{background:i.backgroundColor,image:i.backgroundImage,mask:i.maskImage},toggle:t&&{background:t.backgroundColor,mask:t.maskImage},ratios:{title:contrast(title.color,h.backgroundColor),body:contrast(b.color,s.backgroundColor),link:l&&contrast(l.color,s.backgroundColor),borderBody:contrast(s.borderLeftColor,s.backgroundColor),borderHeader:contrast(s.borderLeftColor,h.backgroundColor),outlineHeader:contrast(s.borderTopColor,h.backgroundColor),outlineBody:contrast(s.borderRightColor,s.backgroundColor),borderOutside:contrast(s.borderLeftColor,getComputedStyle(document.querySelector('main')).backgroundColor==='rgba(0, 0, 0, 0)'?s.backgroundColor:getComputedStyle(document.querySelector('main')).backgroundColor),icon:i&&i.backgroundColor!=='rgba(0, 0, 0, 0)'?contrast(i.backgroundColor,h.backgroundColor):null,toggle:t&&t.backgroundColor!=='rgba(0, 0, 0, 0)'?contrast(t.backgroundColor,h.backgroundColor):null}};
      });
    })()`);
    report.styles.push({width,mode,callouts:styles});
    if(phase==='after') {
      check(`native callout coverage ${width} ${mode}`,styles.length===15&&new Set(styles.map(s=>s.type)).size===5,styles.length);
      check(`computed callout contrast ${width} ${mode}`,styles.every(s=>s.opacity==='1'&&s.ratios.title>=4.5&&s.ratios.body>=4.5&&(!s.ratios.link||s.ratios.link>=4.5)&&s.ratios.borderBody>=3&&s.ratios.borderHeader>=3&&s.ratios.borderOutside>=3&&s.ratios.outlineHeader>=3&&s.ratios.outlineBody>=3&&s.ratios.icon>=3&&s.icon.mask!=='none'&&s.icon.image==='none'&&(!s.toggle||(s.ratios.toggle>=3&&s.toggle.mask!=='none'))),styles);
      check(`no page overflow ${width} ${mode}`,await evaluate('document.documentElement.scrollWidth<=innerWidth'));
      for(const type of ['note','tip','important','caution','warning']) {
        const selector=`.callout-${type} .callout-header[aria-expanded="false"]`;
        await evaluate(`document.querySelector(${JSON.stringify(selector)}).focus()`);
        await key('Enter');
        const focused=await evaluate(`(()=>{const s=getComputedStyle(document.activeElement);return {style:s.outlineStyle,width:s.outlineWidth,color:s.outlineColor,background:s.backgroundColor}})()`);
        await waitFor(`document.querySelector('[data-fixture="${type}-closed"] .callout-header').getAttribute('aria-expanded')==='true' && !!document.querySelector('[data-fixture="${type}-closed"] .callout-collapse.show') && !document.querySelector('.collapsing')`);
        // There is also an initially open fixture; assert the exact focused header.
        check(`opens ${type} with Enter ${width} ${mode}`,await evaluate("document.activeElement.getAttribute('aria-expanded')==='true'"));
        check(`focus visible ${type} ${width} ${mode}`,focused.style==='solid'&&parseFloat(focused.width)>=2,focused);
        await key(' ');
        await waitFor("document.activeElement.getAttribute('aria-expanded')==='false' && !document.querySelector('.collapsing')");
        // Test the initially open instance separately by pointer, checking native ARIA.
        const openSelector=`.callout-${type} .callout-header[aria-expanded="true"]`;
        await click(openSelector);
        await waitFor(`document.querySelectorAll('.callout-${type} .callout-header[aria-expanded="true"]').length===0 && !document.querySelector('.collapsing')`);
        check(`closes initially open ${type} by pointer ${width} ${mode}`, await evaluate(`!document.querySelector('[data-fixture="${type}-open"] .callout-collapse.show')`));
        // Restore the originally open fixture by its stable fixture attribute.
        await click(`[data-fixture="${type}-open"] .callout-header`);
        await waitFor(`document.querySelector('[data-fixture="${type}-open"] .callout-header').getAttribute('aria-expanded')==='true' && !document.querySelector('.collapsing')`);
        if(width!==320) {
          await evaluate(`document.querySelector('[data-fixture="${type}-closed"]').scrollIntoView({block:'center'})`);
          const stateShot=await cdp('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
          const stateFile=`artifacts/v0.2/comparison/states-${type}-${width}-${mode}.png`;
          await Deno.writeFile(stateFile,Uint8Array.from(atob(stateShot.data),c=>c.charCodeAt(0)));
          report.screenshots.push(stateFile);
        }

      }
    }
  }
}
if(phase==='after') check('no network or JavaScript errors',errors.length===0,errors);
report.summary={passed:report.checks.filter(c=>c.pass).length,failed:report.checks.filter(c=>!c.pass).length,screenshots:report.screenshots.length};
await Deno.writeTextFile(`artifacts/v0.2/callouts-${phase}.json`,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report.summary));close();Deno.exit(report.summary.failed?1:0);
