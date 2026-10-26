/** Browser integration checks using Deno + the existing Chromium CDP.
 * No imports, dependencies, package installation or global changes.
 * Start the isolated headless browser and local server as described in docs/PRUEBAS.md.
 */
const base = Deno.args[0] || 'http://127.0.0.1:4850/';
const debug = Deno.args[1] || 'http://127.0.0.1:9228';
const prefix = Deno.args[2] || 'browser';
if (!/^[a-z0-9-]+$/.test(prefix) || new URL(base).hostname!=='127.0.0.1' || new URL(debug).hostname!=='127.0.0.1') throw Error('Use a simple report name and loopback test endpoints.');
const report = {base, date: new Date().toISOString(), checks: [], matrix: [], contrast: [], screenshots: [], errors: []};
let seq = 0;
let loadReady;
const pending = new Map();
const tabs = await (await fetch(`${debug}/json/list`)).json();
const target = tabs.find(t => t.type === 'page');
if (!target) throw Error('No page target; launch Chromium with about:blank.');
const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {socket.onopen = resolve; socket.onerror = reject;});
socket.onmessage = e => {
  const msg = JSON.parse(e.data);
  if (msg.method === 'Page.loadEventFired') { loadReady?.(); loadReady = undefined; }
  if (msg.id) {
    const task = pending.get(msg.id);
    clearTimeout(task?.timer);
    pending.delete(msg.id);
    if (msg.error) task?.reject(Error(JSON.stringify(msg.error)));
    else task?.resolve(msg.result);
  }
  if (msg.method === 'Runtime.exceptionThrown') report.errors.push(msg.params.exceptionDetails.text + ': ' + (msg.params.exceptionDetails.exception?.description || ''));
  if (msg.method === 'Network.responseReceived' && msg.params.response.status >= 400) report.errors.push(`${msg.params.response.status} ${msg.params.response.url}`);
  if (msg.method === 'Network.loadingFailed' && !msg.params.canceled) report.errors.push(`${msg.params.errorText} (${msg.params.type})`);
};
function cdp(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++seq;
    const timer=setTimeout(()=>{pending.delete(id);reject(Error(`CDP timeout: ${method}`));},30000);
    pending.set(id, {resolve, reject, timer});
    socket.send(JSON.stringify({id, method, params}));
  });
}
async function evaluate(expression) {
  const r = await cdp('Runtime.evaluate', {expression, returnByValue:true, awaitPromise:true});
  if (r.exceptionDetails) throw Error(r.exceptionDetails.exception?.description || r.exceptionDetails.text);
  return r.result.value;
}
async function waitFor(expression, ms=12000) {
  const start = Date.now();
  while (Date.now() - start < ms) {
    try { if (await evaluate(expression)) return true; } catch { /* navigation context may be replacing the document */ }
    await new Promise(r=>setTimeout(r,100));
  }
  throw Error(`Timed out: ${expression}`);
}
function check(name, value, details) {
  report.checks.push({name, pass: Boolean(value), ...(details === undefined ? {} : {details})});
  console.log(`${value ? 'PASS' : 'FAIL'} ${name}${details === undefined ? '' : ': '+JSON.stringify(details)}`);
}
async function navigate(path) {
  const url = new URL(path, base).href;
  const loaded = new Promise((resolve, reject) => {const timer=setTimeout(()=>reject(Error("Navigation timeout")),30000);loadReady=()=>{clearTimeout(timer);resolve();};});
  await cdp('Page.navigate', {url});
  await loaded;
  await waitFor(`location.href === ${JSON.stringify(url)} && document.readyState === 'complete' && !!document.querySelector('.uso-skip-link')`);
  await evaluate('window.MathJax?.startup?.promise?.then(()=>true) ?? true');
  await evaluate('document.fonts.ready.then(()=>true)');
}
async function theme(mode) {
  if (!(await evaluate(`document.body.classList.contains('quarto-${mode}')`))) {
    await click('.quarto-color-scheme-toggle');
  }
  await waitFor(`document.body.classList.contains('quarto-${mode}')`);
  await waitFor(`getComputedStyle(document.documentElement).getPropertyValue('--uso-bg').trim() === '${mode === 'dark' ? '#111827' : '#f4f6fa'}'`);
  await evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))');
}
async function click(selector) {
  const p=await evaluate(`(()=>{const el=document.querySelector(${JSON.stringify(selector)});el.scrollIntoView({block:'center'});const r=el.getBoundingClientRect();return {x:r.x+r.width/2,y:r.y+r.height/2}})()`);
  await cdp('Input.dispatchMouseEvent', {type:'mousePressed', ...p, button:'left', clickCount:1});
  await cdp('Input.dispatchMouseEvent', {type:'mouseReleased', ...p, button:'left', clickCount:1});
}
async function key(key, code=key) {
  await cdp('Input.dispatchKeyEvent',{type:'keyDown',key,code,text:key==='Enter'?'\r':undefined,windowsVirtualKeyCode: key==='Tab'?9:key==='Enter'?13:key===' '?32:undefined});
  await cdp('Input.dispatchKeyEvent',{type:'keyUp',key,code});
}
async function screenshot(name) {
  const shot = await cdp('Page.captureScreenshot', {format:'png',captureBeyondViewport:false});
  const bytes = Uint8Array.from(atob(shot.data), c=>c.charCodeAt(0));
  await Deno.writeFile(`artifacts/v0.2/screenshots/${prefix}-${name}.png`,bytes);
  report.screenshots.push(`${prefix}-${name}.png`);
}
await Deno.mkdir('artifacts/v0.2/screenshots',{recursive:true});
await cdp('Page.enable');
await cdp('Runtime.enable');
await cdp('Network.enable');
await cdp('Network.setCacheDisabled',{cacheDisabled:true});
await cdp('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:'dark'},{name:'prefers-reduced-motion',value:'reduce'}]});
// Clear only this disposable test origin, never the user's browser state.
await cdp('Storage.clearDataForOrigin',{origin:new URL(base).origin,storageTypes:'local_storage'});
await cdp('Emulation.setDeviceMetricsOverride',{width:1440,height:1000,deviceScaleFactor:1,mobile:false});
await navigate('index.html');
check('system dark preference on first visit', await evaluate("document.body.classList.contains('quarto-dark')"));
await evaluate("document.querySelector('.uso-skip-link').focus()");
await key('Enter');
check('skip link focuses main content',await evaluate("document.activeElement.id==='quarto-document-content'"));
check('reduced motion preference applies',await evaluate("matchMedia('(prefers-reduced-motion: reduce)').matches && parseFloat(getComputedStyle(document.querySelector('.navbar-toggler')).transitionDuration)<=.00002"));
await theme('light');
await navigate('unidades/fundamentos.html');
check('explicit light preference persists across nested navigation',await evaluate("document.body.classList.contains('quarto-light')"));
const reloaded = new Promise((resolve, reject) => {const timer=setTimeout(()=>reject(Error("Reload timeout")),30000);loadReady=()=>{clearTimeout(timer);resolve();};});
await cdp('Page.reload');
await reloaded;
await waitFor("document.readyState === 'complete' && !!document.querySelector('.uso-skip-link')");
check('explicit preference survives reload',await evaluate("document.body.classList.contains('quarto-light')"));
await waitFor('!!document.querySelector("mjx-container")',20000).catch(e=>report.errors.push(e.message));
check('MathJax typesets formula on nested page',await evaluate('document.querySelectorAll("mjx-container").length > 0'));
check('nested page has native sidebar, TOC and previous/next',await evaluate('!!document.querySelector("#quarto-sidebar") && !!document.querySelector("#TOC") && document.querySelectorAll(".nav-page a").length===2'));
await navigate('laboratorio.html');
await evaluate("document.querySelector('#uso-slope').value='1.7';document.querySelector('#uso-slope').dispatchEvent(new Event('input',{bubbles:true}));document.querySelector('#uso-reference').checked=false;document.querySelector('#uso-reference').dispatchEvent(new Event('change',{bubbles:true}));document.querySelector('#uso-notes').value='Conservar apuntes';window.usoTestLine=document.querySelector('[data-line]');");
const before=await evaluate("({path:usoTestLine.getAttribute('d'),stroke:getComputedStyle(usoTestLine).stroke})");
await theme('dark');
const after=await evaluate("({value:document.querySelector('#uso-slope').value,reference:document.querySelector('#uso-reference').checked,notes:document.querySelector('#uso-notes').value,same:usoTestLine===document.querySelector('[data-line]'),path:usoTestLine.getAttribute('d'),stroke:getComputedStyle(usoTestLine).stroke,result:document.querySelector('[data-result]').textContent})");
check('theme switch preserves SVG node, values and notes',after.same&&after.value==='1.7'&&!after.reference&&after.notes==='Conservar apuntes'&&after.path===before.path,after);
check('SVG responds to theme with computed color',before.stroke!==after.stroke,{light:before.stroke,dark:after.stroke});
await evaluate("document.querySelector('#uso-answer').value='5'");
await click('[data-uso-form] button');
check('incorrect answer has associated error and receives focus',await evaluate("document.querySelector('#uso-answer').getAttribute('aria-invalid')==='true'&&document.activeElement.id==='uso-answer'&&document.querySelector('[data-feedback]').textContent.includes('Revisa')"));
await evaluate("document.querySelector('#uso-answer').value='3'");
await click('[data-uso-form] button');
check('correct answer displays confirmation',await evaluate("document.querySelector('#uso-answer').getAttribute('aria-invalid')==='false'&&document.querySelector('[data-feedback]').textContent.includes('correcta')"));
await click('[data-reset]');
check('reset restores controls and SVG',await evaluate("document.querySelector('#uso-slope').value==='1'&&document.querySelector('#uso-reference').checked&&document.querySelector('[data-line]').getAttribute('d')==='M 56 235 L 464 151'"));
// Actual computed button styles catch selector conflicts with button.uso-button.
await cdp('Input.dispatchMouseEvent',{type:'mouseMoved',x:5,y:5});
const secondary=await evaluate(`(()=>{
  const button=document.querySelector('[data-reset]'),style=getComputedStyle(button);
  const probe=document.createElement('span');probe.style.color='var(--uso-emphasis-ink)';probe.style.backgroundColor='var(--uso-surface)';document.body.append(probe);
  const expected=getComputedStyle(probe);const result={color:style.color,background:style.backgroundColor,expectedColor:expected.color,expectedBackground:expected.backgroundColor};probe.remove();return result;
})()`);
check('secondary button retains semantic teal style',secondary.color===secondary.expectedColor&&secondary.background===secondary.expectedBackground,secondary);
// Native keyboard behavior and visible focus, using actual input events.
await evaluate("document.querySelector('.quarto-color-scheme-toggle').focus()");
const keyboardMode=await evaluate("document.body.classList.contains('quarto-dark')");
await key(' ' ,'Space');
check('theme toggle operable with Space',await evaluate("document.body.classList.contains('quarto-dark')")!==keyboardMode);
const focus=await evaluate("({style:getComputedStyle(document.activeElement).outlineStyle,width:getComputedStyle(document.activeElement).outlineWidth})");
check('keyboard focus has visible outline',focus.style==='solid'&&parseFloat(focus.width)>=2,focus);
await evaluate("document.querySelector('#uso-slope').focus()");
await key('ArrowRight');
check('range control operable with arrow key',await evaluate("document.querySelector('#uso-slope').value==='1.1'"));
await navigate('componentes.html');
await evaluate("document.querySelector('details.uso-solution > summary').focus()");
await key('Enter');
check('native details opens with keyboard',await evaluate("document.querySelector('details.uso-solution').open"));
await theme('dark');
check('theme change preserves open solution',await evaluate("document.querySelector('details.uso-solution').open"));
// Search from root and nested context, loading the real generated index.
await navigate('unidades/fundamentos.html');
await click('#quarto-search');
await waitFor("!!document.querySelector('.aa-Input')");
await cdp('Input.insertText',{text:'pendiente'});
await waitFor("document.querySelectorAll('.aa-Item').length>0").catch(e=>report.errors.push(e.message));
check('native Quarto search returns results from nested page',await evaluate("document.querySelectorAll('.aa-Item').length>0"));
await key('Escape');
const paths=['index.html','unidades/fundamentos.html','componentes.html','laboratorio.html','sistema.html'];
for (const width of (prefix.endsWith('subpath') ? [390,1440] : [320,390,768,1440])) {
  await cdp('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});
  for (const path of paths) {
    await navigate(path);
    for (const mode of ['light','dark']) {
      await theme(mode);
      const state=await evaluate(`(()=>{
        const toggle=document.querySelector('.quarto-color-scheme-toggle');const r=toggle.getBoundingClientRect();const search=document.querySelector('#quarto-search').getBoundingClientRect();
        const styles=[...document.querySelectorAll('link[rel="stylesheet"]')].filter(l=>l.href.includes('bootstrap-'));
        const ids=[...document.body.querySelectorAll('[id]')].map(el=>el.id);
        return {duplicateBodyIds:ids.length-new Set(ids).size,width:innerWidth,documentWidth:document.documentElement.scrollWidth,toggle:{x:r.x,y:r.y,width:r.width,height:r.height,visible:r.x>=0&&r.right<=innerWidth&&r.y>=0&&r.bottom<65,right:innerWidth-r.right<80,sameRow:Math.abs(r.y-search.y)<5},theme:document.body.className,stylesLoaded:styles.every(l=>!!l.sheet),math:document.querySelectorAll('mjx-container').length};
      })()`);
      report.matrix.push({width,path,mode,...state});
      check(`reflow, theme control and CSS ${path} ${width} ${mode}`, state.duplicateBodyIds===0&&state.documentWidth<=width&&state.toggle.visible&&state.toggle.right&&state.toggle.sameRow&&state.toggle.width>=44&&state.toggle.height>=44&&state.stylesLoaded,state);
      await screenshot(`${path.replaceAll('/','-').replace('.html','')}-${width}-${mode}`);
    }
  }
  await navigate('unidades/fundamentos.html');
  if (width<992) {
    await click('.navbar-toggler');
    await waitFor("document.querySelector('.navbar-collapse').classList.contains('show')");
    check(`mobile navbar opens ${width}`,await evaluate("document.querySelector('.navbar-collapse').classList.contains('show')"));
    await screenshot(`navigation-${width}-dark`);
    await click('.navbar-toggler');
    await waitFor("!document.querySelector('.navbar-collapse.show') && !document.querySelector('.collapsing')");
    await click('.quarto-btn-toggle');
    await waitFor("document.querySelector('#quarto-sidebar').classList.contains('show')");
    check(`mobile units sidebar opens ${width}`,await evaluate("document.querySelector('#quarto-sidebar').classList.contains('show')"));
    await screenshot(`units-${width}-dark`);
    await click('.quarto-btn-toggle');
    await waitFor("!document.querySelector('#quarto-sidebar.show') && !document.querySelector('.collapsing')");
    await click('.uso-mobile-toc > summary');
    check(`mobile page TOC opens ${width}`,await evaluate("document.querySelector('.uso-mobile-toc').open && document.querySelector('#TOC-body a').getBoundingClientRect().height>0"));
    await screenshot(`toc-${width}-dark`);
  }
}
// Pairwise contrast of effective semantic tokens on the actual compiled themes.
await navigate('laboratorio.html');
for (const mode of ['light','dark']) {
  await theme(mode);
  const pairs=await evaluate(`(()=>{
    const token=n=>getComputedStyle(document.documentElement).getPropertyValue('--uso-'+n).trim();
    const rgb=c=>{const el=document.createElement('span');el.style.color=c;document.body.append(el);const v=getComputedStyle(el).color.match(/[\\d.]+/g).slice(0,3).map(Number);el.remove();return v;};
    const lum=c=>rgb(c).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
    const ratio=(a,b)=>{const x=lum(token(a)),y=lum(token(b));return (Math.max(x,y)+.05)/(Math.min(x,y)+.05)};
    const results=[];
    for(const fg of ['text','heading','muted','link','primary','emphasis','success','warning','danger'])for(const bg of ['bg','surface','surface-alt'])results.push({fg,bg,ratio:ratio(fg,bg),minimum:fg==='emphasis'&&bg==='surface-alt'?3:4.5});
    for(const bg of ['primary','primary-hover'])results.push({fg:'on-primary',bg,ratio:ratio('on-primary',bg),minimum:4.5});
    for(const fg of ['control-border','focus'])for(const bg of ['surface','bg','surface-alt'])results.push({fg,bg,ratio:ratio(fg,bg),minimum:3});
    for(const bg of ['emphasis-soft','primary-soft'])for(const fg of ['text','heading','link','emphasis-ink'])results.push({fg,bg,ratio:ratio(fg,bg),minimum:4.5});
    return results;
  })()`);
  report.contrast.push({mode,pairs});
  check(`semantic contrast pairs ${mode}`,pairs.every(p=>p.ratio>=p.minimum),pairs.filter(p=>p.ratio<p.minimum));
}
// Zoom equivalent reflow: 1280 viewport at 400% = 320 CSS px. Matrix covers
// that width; true browser zoom and assistive technology remain manual checks.
check('no network or JavaScript errors',report.errors.length===0,report.errors);
report.summary={passed:report.checks.filter(c=>c.pass).length,failed:report.checks.filter(c=>!c.pass).length,matrixCases:report.matrix.length,screenshots:report.screenshots.length};
await Deno.writeTextFile(`artifacts/v0.2/${prefix}-results.json`,JSON.stringify(report,null,2)+'\n');
console.log(JSON.stringify(report.summary));
socket.close();
Deno.exit(report.summary.failed?1:0);
