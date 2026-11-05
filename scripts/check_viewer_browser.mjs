#!/usr/bin/env node
/** Actual Chromium checks for the generated offline comparison reader.
 * Usage: node scripts/check_viewer_browser.mjs [--repo PATH] [--run PATH] [--html PATH]
 * Install Playwright separately, or set PLAYWRIGHT_MODULE_PATH to its index.mjs.
 * A missing browser is an error, never a successful or simulated browser check.
 */
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { fileURLToPath, pathToFileURL } from 'node:url';

let repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
let htmlArgument;
let run;
const args = process.argv.slice(2);
for (let i=0;i<args.length;i++) {
  if (args[i] === '--repo' && args[i+1]) repo = path.resolve(args[++i]);
  else if (args[i] === '--html' && args[i+1]) htmlArgument = args[++i];
  else if (args[i] === '--run' && args[i+1]) run = args[++i];
  else throw new Error('Usage: check_viewer_browser.mjs [--repo PATH] [--run PATH] [--html PATH]');
}
const htmlPath = path.resolve(htmlArgument || path.join(repo,'docs/comparisons/index.html'));
const html = fs.readFileSync(htmlPath,'utf8');
const payload = /<script id="comparison-data" type="application\/json">([\s\S]*?)<\/script>/.exec(html);
assert(payload,'Missing comparison payload');
const data = JSON.parse(payload[1]);
if (run) {
  const manifest = JSON.parse(fs.readFileSync(path.join(repo,run,'manifest.json'),'utf8'));
  assert.equal(data.runId,manifest.run_id);
  assert.equal(data.skillVersion,manifest.skill_version);
}
const documentCount = data.cases.reduce((total,entry)=>total+Object.keys(entry.documents).length,0);
let chromium;
try {
  const module = process.env.PLAYWRIGHT_MODULE_PATH
    ? await import(pathToFileURL(path.resolve(process.env.PLAYWRIGHT_MODULE_PATH)).href)
    : await import('playwright');
  chromium = module.chromium;
} catch (error) {
  throw new Error('Playwright could not be loaded. Install playwright@1.62.1 or set PLAYWRIGHT_MODULE_PATH to its index.mjs. No browser checks ran.',{cause:error});
}
let browser;
try {
  browser = await chromium.launch({headless:true});
} catch (error) {
  throw new Error('Chromium could not be launched. Install its binary with the Playwright CLI before this check. No browser checks ran.',{cause:error});
}
const results = [];
const errors = [];
const temporary = fs.mkdtempSync(path.join(os.tmpdir(),'korean-dev-writing-browser-'));
const fileUrl = pathToFileURL(htmlPath).href;
const viewports = [{width:1440,height:1000},{width:800,height:900},{width:390,height:844},{width:320,height:740}];

try {
  const context = await browser.newContext({viewport:viewports[0],reducedMotion:'reduce',locale:'ko-KR',acceptDownloads:true});
  await context.setOffline(true);
  const page = await context.newPage();
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(fileUrl);
  await page.locator('body.js').waitFor();
  assert.equal(await page.locator('.source-document').count(),documentCount);
  assert.equal(await page.locator('.case-panel:visible').count(),1);
  assert.equal(await page.locator('#comparison-mode').inputValue(),'previous');
  results.push('The offline file initializes in Chromium with all source documents and the previous-version default');

  // Exercise the real CSS cascade, scroll containers and viewport geometry.
  let checkedStates = 0;
  for (const viewport of viewports) {
    await page.setViewportSize(viewport);
    for (const entry of data.cases) {
      await page.locator('#tab-'+entry.id).click();
      const baselineOption = page.locator('#comparison-mode option[value="baseline"]');
      assert.equal(await baselineOption.isDisabled(),!entry.documents.baseline);
      for (const comparison of entry.documents.baseline ? ['previous','baseline'] : ['previous']) {
        await page.locator('#comparison-mode').selectOption(comparison);
        for (const view of ['both','baseline','latest']) {
          await page.locator('#view-mode').selectOption(view);
          const expected = view === 'both' ? [comparison,'latest'] : view === 'baseline' ? [comparison] : ['latest'];
          const state = await page.evaluate(() => {
            const visible = element => element.getClientRects().length > 0 && getComputedStyle(element).visibility !== 'hidden';
            const papers = [...document.querySelectorAll('.paper')].filter(visible);
            return {
              conditions:papers.map(paper=>paper.dataset.document),
              panels:[...document.querySelectorAll('.case-panel')].filter(visible).map(panel=>panel.id),
              horizontalOverflow:document.documentElement.scrollWidth-document.documentElement.clientWidth,
              papers:papers.map(paper=>{
                const style=getComputedStyle(paper);
                const original=paper.scrollTop;
                paper.scrollTop=100;
                const internalScroll=paper.scrollTop;
                paper.scrollTop=original;
                return {overflowY:style.overflowY,maxHeight:style.maxHeight,internalScroll};
              }),
              tables:[...document.querySelectorAll('.source-document table')].filter(visible).map(table=>({
                wrapped:table.parentElement.classList.contains('document-table'),
                overflowX:getComputedStyle(table.parentElement).overflowX,
                fontSize:parseFloat(getComputedStyle(table).fontSize),
                tableLayout:getComputedStyle(table).tableLayout,
              })),
            };
          });
          const label = [viewport.width,entry.id,comparison,view].join('/');
          assert.deepEqual(state.conditions,expected,label+': visible conditions');
          assert.deepEqual(state.panels,['panel-'+entry.id],label+': one selected case');
          assert(state.horizontalOverflow<=1,label+': page has horizontal overflow');
          if (view !== 'both' || viewport.width <= 760) {
            for (const paper of state.papers) {
              assert.equal(paper.maxHeight,'none',label+': no height cap during single/mobile reading');
              assert.equal(paper.overflowY,'visible',label+': document flows with the page');
              assert.equal(paper.internalScroll,0,label+': no nested vertical scrollbar');
            }
          }
          for (const table of state.tables) {
            assert(table.wrapped && table.overflowX === 'auto',label+': scrollable table wrapper');
            assert(table.fontSize>=13,label+': readable table font');
            assert.equal(table.tableLayout,'auto',label+': natural column sizes');
          }
          checkedStates++;
        }
      }
    }
    const maxTabHeight = await page.locator('.case-tab').evaluateAll(tabs=>Math.max(...tabs.map(tab=>tab.getBoundingClientRect().height)));
    assert(maxTabHeight<=112,'Case picker unexpectedly tall at '+viewport.width+'px');
  }
  results.push(checkedStates+' real viewport/case/condition states: correct visibility, single-document page scrolling, readable tables, compact tabs and no page overflow');

  await page.setViewportSize(viewports[0]);
  const firstTab = page.locator('[data-case-tab]').first();
  await firstTab.focus();
  await page.keyboard.press('End');
  assert.equal(await page.evaluate(()=>document.activeElement.dataset.caseTab),data.cases.at(-1).id);
  await page.keyboard.press('ArrowRight');
  assert.equal(await page.evaluate(()=>document.activeElement.dataset.caseTab),data.cases[0].id);
  assert.equal(await page.locator('[data-case-tab][tabindex="0"]').count(),1);
  results.push('Native keyboard tab navigation wraps and maintains one focused tab stop');

  const targets = await page.evaluate(() => ['baseline','previous','latest'].map(condition=>{
    const papers=[...document.querySelectorAll('[data-document="'+condition+'"]')]
      .filter(paper=>paper.querySelector('.source-document h2[id]'))
      .sort((a,b)=>b.textContent.length-a.textContent.length);
    const target=papers[0]?.querySelector('.source-document h2[id]:last-of-type') || papers[0]?.querySelector('.source-document h2[id]');
    return target ? {id:target.id,caseId:target.closest('.case-panel').id.slice('panel-'.length),condition} : null;
  }).filter(Boolean));
  assert.equal(targets.length,3,'Need a heading fragment for all three conditions');
  async function assertFragment(target) {
    await page.waitForFunction(id=>{
      const target=document.getElementById(id);
      if(!target?.getClientRects().length || document.activeElement!==target)return false;
      const rect=target.getBoundingClientRect();
      return rect.top>=-1 && rect.bottom<=innerHeight+1;
    },target.id);
    const actual = await page.evaluate(id=>{
      const target=document.getElementById(id);
      const paper=target.closest('.paper');
      const header=paper.querySelector('.paper-header');
      return {
        caseId:document.querySelector('[data-case-tab][aria-selected="true"]').dataset.caseTab,
        condition:paper.dataset.document,
        hash:decodeURIComponent(location.hash.slice(1)),
        top:target.getBoundingClientRect().top,
        headerBottom:getComputedStyle(header).position==='sticky'?header.getBoundingClientRect().bottom:0,
      };
    },target.id);
    assert.equal(actual.caseId,target.caseId);
    assert.equal(actual.condition,target.condition);
    assert.equal(actual.hash,target.id);
    assert(actual.top>=actual.headerBottom-1,'Fragment hidden behind sticky document header');
  }
  for (const target of targets) {
    await page.goto('about:blank');
    await page.goto(fileUrl+'#'+encodeURIComponent(target.id));
    await assertFragment(target);
    await page.locator('#tab-'+data.cases[0].id).click();
    await page.locator('#view-mode').selectOption(target.condition==='latest'?'baseline':'latest');
    await page.evaluate(id=>{location.hash=encodeURIComponent(id);},target.id);
    await assertFragment(target);
  }
  const latestTarget=targets.find(target=>target.condition==='latest');
  await page.locator('#tab-'+latestTarget.caseId).click();
  await page.locator('#view-mode').selectOption('latest');
  const tocLink=page.locator('#panel-'+latestTarget.caseId+' .paper.latest .document-toc a').last();
  const tocId=(await tocLink.getAttribute('href')).slice(1);
  await tocLink.click();
  await assertFragment({...latestTarget,id:tocId});
  results.push('Direct loads, hidden-case hash changes and native ToC clicks reveal and scroll to the correct document heading');

  const note = await page.evaluate(() => {
    const reference = document.querySelector('.paper.latest [role="doc-noteref"]');
    return reference ? {referenceId:reference.id,noteId:reference.getAttribute('href').slice(1),caseId:reference.closest('.case-panel').id.slice('panel-'.length),condition:'latest'} : null;
  });
  assert(note,'Missing footnote fixture');
  await page.locator('#tab-'+note.caseId).click();
  await page.locator('#view-mode').selectOption('latest');
  await page.locator('[id="'+note.referenceId+'"]').click();
  await assertFragment({...note,id:note.noteId});
  await page.locator('[id="'+note.noteId+'"] .footnote-backlinks a').first().click();
  await assertFragment({...note,id:note.referenceId});
  results.push('Native footnote and backlink clicks keep their document selected and return focus to the referenced text');

  // A real short table must keep its natural width in the wider single-document mode.
  const shortTable=await page.evaluate(()=>{
    const table=[...document.querySelectorAll('.source-document table')].find(table=>table.querySelector('th')?.textContent.includes('--level'));
    return table ? {caseId:table.closest('.case-panel').id.slice('panel-'.length),condition:table.closest('.paper').dataset.document} : null;
  });
  assert(shortTable,'Missing --level table fixture');
  await page.locator('#tab-'+shortTable.caseId).click();
  if(shortTable.condition!=='latest')await page.locator('#comparison-mode').selectOption(shortTable.condition);
  await page.locator('#view-mode').selectOption(shortTable.condition==='latest'?'latest':'baseline');
  const shortGeometry=await page.evaluate(()=>{
    const table=[...document.querySelectorAll('.source-document table')].find(table=>table.getClientRects().length&&table.querySelector('th')?.textContent.includes('--level'));
    return {table:table.getBoundingClientRect().width,container:table.parentElement.getBoundingClientRect().width};
  });
  assert(shortGeometry.table<shortGeometry.container*0.85,'Short table should not stretch across the whole reading column');
  results.push('The actual two-column --level table stays compact in single-document reading');

  // Exercise native download handling; exhaustive payload-byte checks live in the VM checker.
  const downloadCase=data.cases.find(entry=>entry.documents.baseline);
  await page.locator('#tab-'+downloadCase.id).click();
  await page.locator('#view-mode').selectOption('both');
  for(const condition of ['input','baseline','previous','latest']){
    if(condition==='baseline'||condition==='previous')await page.locator('#comparison-mode').selectOption(condition);
    const downloadPromise=page.waitForEvent('download');
    await page.locator('#panel-'+downloadCase.id+' [data-source="'+condition+'"]').click();
    const download=await downloadPromise;
    const destination=path.join(temporary,condition+'.md');
    await download.saveAs(destination);
    const source=condition==='input'?downloadCase.input:downloadCase.documents[condition];
    assert(fs.readFileSync(destination).equals(fs.readFileSync(path.join(repo,source.path))),condition+': native download bytes');
  }
  results.push('Native Chromium downloads preserve source bytes for input, baseline, previous and latest documents');

  const noJs=await browser.newContext({javaScriptEnabled:false,viewport:viewports[2]});
  await noJs.setOffline(true);
  const fallback=await noJs.newPage();
  await fallback.goto(fileUrl);
  assert.equal(await fallback.locator('.paper:visible').count(),documentCount);
  assert(await fallback.evaluate(()=>document.documentElement.scrollWidth<=document.documentElement.clientWidth+1));
  assert(await fallback.locator('.paper').evaluateAll(papers=>papers.every(paper=>getComputedStyle(paper).maxHeight==='none')));
  results.push('With JavaScript disabled, every source document remains readable in the page flow on a narrow viewport');
  await noJs.close();
  await context.close();
  assert.deepEqual(errors,[],'Uncaught browser script errors');
  console.log(JSON.stringify({runId:data.runId,html:htmlPath,browser:'Chromium '+browser.version(),viewports,checks:results.length,results,limitations:['Checks exercise real browser geometry and native interactions; no human reading study or screenshot-based visual review is implied.']},null,2));
} finally {
  await browser.close();
  fs.rmSync(temporary,{recursive:true,force:true});
}
