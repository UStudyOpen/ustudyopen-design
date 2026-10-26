// Focused cascade/regression audit. Uses the browser tooling already installed.
// Serve course docs on 4860 and the prototype _site on 4861, then run with Node.
import assert from 'node:assert/strict';
import {mkdirSync, readFileSync, writeFileSync, readdirSync} from 'node:fs';
const {chromium} = await import(process.env.PLAYWRIGHT_MODULE ?? '/usr/lib/chatgpt/resources/cua_node/lib/node_modules/playwright-core/index.mjs');
const stage = process.argv[2] ?? 'after';
assert.ok(['before', 'after'].includes(stage));
const output = 'artifacts/inline-code';
mkdirSync(output, {recursive:true});
const report = {stage, cases:[], errors:[]};
const browser = await chromium.launch({headless:true, chromiumSandbox:true,
  executablePath:process.env.BROWSER_EXECUTABLE ?? '/opt/brave.com/brave/brave'});
try {
  const page = await browser.newPage({reducedMotion:'reduce'});
  page.on('pageerror', e=>report.errors.push(e.message));
  page.on('response', r=>{if(r.status()>=400)report.errors.push(`${r.status()} ${r.url()}`);});
  page.on('requestfailed', r=>report.errors.push(`${r.failure()?.errorText} ${r.url()}`));
  const routes = [
    ['schema','http://127.0.0.1:4860/index.html','.schema-box'],
    ['attributes','http://127.0.0.1:4860/fundamentos/relaciones-nombradas.html','main p:has(> code:text-is("rut"))'],
    ['prototype','http://127.0.0.1:4861/componentes.html','#uso-inline-code-example']
  ];
  for(const [name,url,selector] of routes) {
    for(const width of [320,390,768,1440]) {
      await page.setViewportSize({width,height:1000});
      await page.goto(url);
      await page.evaluate(async()=>{await document.fonts.ready;await window.MathJax?.startup?.promise;});
      // Before the gallery sample is added, provide identical illustrative markup.
      // The course examples above are always the actual, unchanged rendered QMD.
      if(name==='prototype' && !await page.locator(selector).count()) {
        await page.locator('#código-y-tablas').evaluate(e=>{
          const p=document.createElement('p');p.id='uso-inline-code-example';
          p.innerHTML='Atributos de una relación: <code>rut</code>, <code>nombre</code>, <code>carrera</code>, <code>codigo</code>, <code>creditos</code> y <code>semestre</code>.';
          e.append(p);
        });
      }
      // Synthetic edge cases expose accidental global/code-block/link overrides.
      await page.locator('main.content').evaluate(e=>{
        const fixture=document.createElement('div');fixture.id='inline-code-regression';
        fixture.innerHTML='<ul><li>Inline <code>atributo</code><pre><code>plain block</code></pre><pre class="sourceCode"><code class="sourceCode sql"><span class="kw">SELECT</span> nombre</code></pre></li></ul><table><tbody><tr><td><code>columna</code></td></tr></tbody></table><p><a href="#">Enlace <code>link</code></a> <code class="sourceCode">highlighted inline</code> <span class="badge bg-primary">Badge</span> <span class="concept-tag">Concepto</span> <span class="uso-status uso-status--lista">Lista</span></p><nav><p><code>navigation</code></p></nav>';
        e.append(fixture);
      });
      for(const theme of ['light','dark']) {
        if(!await page.locator('body').evaluate((e,t)=>e.classList.contains(`quarto-${t}`),theme))
          await page.locator('.quarto-color-scheme-toggle').click();
        await page.waitForFunction(t=>document.body.classList.contains(`quarto-${t}`) &&
          getComputedStyle(document.documentElement).getPropertyValue('--uso-bg').trim()===(t==='dark'?'#111827':'#f4f6fa'),theme);
        if(stage==='after')await page.waitForFunction(t=>getComputedStyle(document.documentElement).getPropertyValue('--uso-inline-code-bg').trim()===(t==='dark'?'#475569':'#e2e8f0'),theme);
        await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
        const result=await page.locator(selector).evaluate(root=>{
          const rgba=s=>s.match(/[\d.]+/g).map(Number);
          const composite=(a,b)=>a.slice(0,3).map((v,i)=>v*(a[3]??1)+b[i]*(1-(a[3]??1)));
          const bg=e=>!e ? [255,255,255] : composite(rgba(getComputedStyle(e).backgroundColor),bg(e.parentElement));
          const lum=c=>c.map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;}).reduce((s,v,i)=>s+v*[.2126,.7152,.0722][i],0);
          const ratio=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
          const style=e=>{const s=getComputedStyle(e);return {color:s.color,background:s.backgroundColor,border:s.border,shadow:s.boxShadow,
            fontSize:s.fontSize,padding:s.padding,radius:s.borderRadius,lineHeight:s.lineHeight};};
          const codes=[...root.querySelectorAll('code')].map(e=>{
            const r=e.getBoundingClientRect();return {text:e.textContent,style:style(e),effectiveBackground:bg(e),
              contrast:ratio(rgba(getComputedStyle(e).color).slice(0,3),bg(e)),
              containerContrast:ratio(bg(e),bg(e.parentElement)),geometry:{width:r.width,height:r.height},
              inViewport:r.left>=0&&r.right<=innerWidth};
          });
          const rules=[];const sample=root.querySelector('code');
          const visit=rs=>{for(const r of rs){if(r.cssRules)visit(r.cssRules);else if(r.selectorText && sample.matches(r.selectorText) && (r.style.background||r.style.backgroundColor||r.style.color||r.style.boxShadow))rules.push({selector:r.selectorText,css:r.style.cssText});}};
          for(const sheet of document.styleSheets){if(!sheet.disabled)try{visit(sheet.cssRules);}catch{}}
          const unaffected=[...document.querySelectorAll('main pre, main pre code, main pre code span, .concept-tag, .uso-status, .badge, #inline-code-regression a, #inline-code-regression a code, #inline-code-regression code.sourceCode, #inline-code-regression nav code')].map(e=>({tag:e.tagName,text:e.textContent,style:style(e)}));
          const inlineFixture=[...document.querySelectorAll('#inline-code-regression li > code, #inline-code-regression td > code')].map(e=>({style:style(e),contrast:ratio(rgba(getComputedStyle(e).color).slice(0,3),bg(e))}));
          return {codes,rules,unaffected,inlineFixture};
        });
        const item={name,width,theme,...result};report.cases.push(item);
        assert.ok(result.codes.length>0,'actual attribute codes found');
        assert.ok(result.codes.every(c=>c.inViewport),'chips fit mobile and desktop');
        if(stage==='after') {
          const before=JSON.parse(readFileSync(`${output}/before.json`)).cases.find(c=>c.name===name&&c.width===width&&c.theme===theme);
          assert.deepEqual(result.unaffected,before.unaffected,'blocks, highlighted code, links, badges, concepts, status and navigation unchanged');
          assert.deepEqual(result.codes.map(c=>c.geometry),before.codes.map(c=>c.geometry),'chip dimensions unchanged');
          for(const c of [...result.codes,...result.inlineFixture])assert.ok(c.contrast>=4.5,`${name} ${theme}: AA contrast ${c.contrast}`);
          for(const c of result.codes) {
            assert.equal(c.style.background,theme==='dark'?'rgb(71, 85, 105)':'rgb(226, 232, 240)');
            assert.equal(c.style.shadow,'none');
          }
          if(theme==='dark')assert.ok(result.codes.every(c=>c.containerContrast>=1.5),'slate surface distinct from container');
        }
        if([390,1440].includes(width))await page.locator(selector).screenshot({path:`${output}/${stage}-${name}-${theme}-${width}.png`});
      }
    }
  }
  if(stage==='after') {
    report.course=[];
    const root='../base-de-datos/docs/';
    const routes=readdirSync(root,{recursive:true}).filter(p=>p.endsWith('.html'));
    assert.equal(routes.length,27,'all course pages preserved');
    for(const route of routes) {
      await page.goto(`http://127.0.0.1:4860/${route}`);
      // Closed native details can return cached styles from the preceding theme.
      // Reveal solutions so the browser paints the code being measured.
      await page.locator('main details').evaluateAll(es=>es.forEach(e=>{e.open=true;}));
      for(const theme of ['light','dark']) {
        if(!await page.locator('body').evaluate((e,t)=>e.classList.contains(`quarto-${t}`),theme))
          await page.locator('.quarto-color-scheme-toggle').click();
        await page.waitForFunction(t=>getComputedStyle(document.documentElement).getPropertyValue('--uso-bg').trim()===(t==='dark'?'#111827':'#f4f6fa'),theme);
        await page.waitForFunction(t=>document.body.classList.contains(`quarto-${t}`) && getComputedStyle(document.documentElement).getPropertyValue('--uso-inline-code-bg').trim()===(t==='dark'?'#475569':'#e2e8f0'),theme);
        await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
        // Wait for the actual painted component after switching Quarto sheets.
        await page.waitForFunction(t=>[...document.querySelectorAll('main :is(p,li,td) > code:not(.sourceCode)')].every(e=>{
          const s=getComputedStyle(e);return s.backgroundColor===(t==='dark'?'rgb(71, 85, 105)':'rgb(226, 232, 240)') &&
            s.color===(t==='dark'?'rgb(232, 238, 247)':'rgb(36, 50, 71)');
        }),theme);
        const samples=await page.locator('main :is(p,li,td) > code:not(.sourceCode)').evaluateAll(es=>es.map(e=>{
          const s=getComputedStyle(e);
          const lum=c=>c.match(/[\d.]+/g).slice(0,3).map(Number).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4;}).reduce((v,x,i)=>v+x*[.2126,.7152,.0722][i],0);
          const a=lum(s.color),b=lum(s.backgroundColor);
          return {text:e.textContent,background:s.backgroundColor,contrast:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
        }));
        for(const s of samples) {
          assert.equal(s.background,theme==='dark'?'rgb(71, 85, 105)':'rgb(226, 232, 240)',route);
          assert.ok(s.contrast>=4.5,`${route}: inline code contrast ${s.contrast}`);
        }
        report.course.push({route,theme,samples:samples.length,minimum:samples.length?Math.min(...samples.map(s=>s.contrast)):null});
      }
    }
  }
  assert.deepEqual(report.errors,[],'no network or JavaScript errors');
  report.passed=true;
} catch(e) {
  report.passed=false;report.failure=e.stack;process.exitCode=1;
} finally {
  await browser.close();
  writeFileSync(`${output}/${stage}.json`,JSON.stringify(report,null,2)+'\n');
  console.log(JSON.stringify({stage,passed:report.passed,cases:report.cases.length,errors:report.errors,failure:report.failure}));
}
