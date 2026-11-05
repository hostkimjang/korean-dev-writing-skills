#!/usr/bin/env node
/** Verify the generated reader's provenance, fragments and client behavior.
 * Usage: node scripts/check_viewer.mjs [--repo PATH] [--run PATH] [--html PATH]
 * A Node VM with DOM doubles checks behavior; this does not render a browser.
 * Python 3's standard HTML parser is used for structural inspection.
 */
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import { execFileSync } from 'node:child_process';
import { createHash } from 'node:crypto';
import assert from 'node:assert/strict';
import os from 'node:os';
import { fileURLToPath } from 'node:url';
import { buildViewer, renderMarkdown } from './build_viewer.mjs';

const options = process.argv.slice(2);
let repo = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
let htmlArgument;
let runArgument;
const positional = [];
for (let i=0;i<options.length;i++) {
  if (options[i] === '--repo' && options[i+1]) repo = path.resolve(options[++i]);
  else if (options[i] === '--run' && options[i+1]) runArgument = options[++i];
  else if (options[i] === '--html' && options[i+1]) htmlArgument = options[++i];
  else if (!options[i].startsWith('-') && positional.length < 2) positional.push(options[i]);
  else throw new Error('Usage: check_viewer.mjs [--repo PATH] [--run PATH] [--html PATH]');
}
if (positional[1]) repo = path.resolve(positional[1]);
const htmlPath = path.resolve(htmlArgument || positional[0] || path.join(repo,'docs/comparisons/index.html'));
const html = fs.readFileSync(htmlPath, 'utf8');
const parsed = JSON.parse(execFileSync(process.env.PYTHON || 'python3', ['-c', String.raw`
import json,sys
from html.parser import HTMLParser
class Read(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.nodes=[];self.stack=[]
    def handle_starttag(self,tag,attrs):
        i=len(self.nodes)
        self.nodes.append(dict(tag=tag,attrs=dict(attrs),parent=self.stack[-1] if self.stack else None,parts=[]))
        if self.stack: self.nodes[self.stack[-1]]['parts'].append(i)
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}: self.stack.append(i)
    def handle_endtag(self,tag):
        for i in range(len(self.stack)-1,-1,-1):
            if self.nodes[self.stack[i]]['tag']==tag:
                self.stack=self.stack[:i];break
    def handle_data(self,data):
        if self.stack:self.nodes[self.stack[-1]]['parts'].append(data)
p=Read();p.feed(open(sys.argv[1],encoding='utf-8').read());print(json.dumps(p.nodes))
`, htmlPath], {maxBuffer: 12 * 1024 * 1024}));
const clientScripts = parsed.filter(n => n.tag === 'script' && !n.attrs.type);
assert.equal(clientScripts.length, 1, 'Exactly one executable inline client script');
const clientScript = clientScripts[0].parts.join('');
const dataNode = parsed.find(n => n.attrs.id === 'comparison-data');
const data = JSON.parse(dataNode.parts.join(''));
const run = runArgument || 'evaluations/runs/' + data.runId;
const manifest = JSON.parse(fs.readFileSync(path.join(repo,run,'manifest.json'),'utf8'));
const expectedCases = [...(manifest.cases || []),...(manifest.transfer_cases || [])];
const expectedDocumentCount = expectedCases.reduce((count,entry) => count + ['baseline','previous','latest'].filter(condition=>entry[condition]).length,0);
const expectedDownloadCount = expectedCases.length + expectedDocumentCount;
assert.equal(data.runId,manifest.run_id,'HTML run matches selected manifest');
assert.equal(data.skillVersion,manifest.skill_version,'HTML version matches selected manifest');
assert.deepEqual(data.cases.map(entry=>entry.id),expectedCases.map(entry=>entry.id),'HTML case order matches manifest');
assert(data.cases.every((entry,i)=>entry.previousLabel===expectedCases[i].previous_label),'Previous conditions match manifest');
buildViewer(repo,{run,output:htmlPath,check:true});
const styleText = parsed.filter(n => n.tag === 'style').map(n => n.parts.join('')).join('\n');
const results = [];
const issues = [];
const check = (label, callback) => { callback(); results.push(label); };

function makeDom(initialHash = '') {
  let document;
  const events = new Map();
  const location = {hash: initialHash};
  const urlBlobs = new Map();
  const downloads = [];
  const timers = [];
  const historyCalls = [];
  let sequence = 0;
  class Element {
    constructor(node = {tag:'a',attrs:{},parts:[]}) {
      this.tagName = node.tag;
      this.attributes = {...node.attrs};
      this.parts = [...node.parts];
      this.dataset = {};
      for (const [key,value] of Object.entries(node.attrs)) {
        if (key.startsWith('data-')) this.dataset[key.slice(5).replace(/-([a-z])/g, (_,c) => c.toUpperCase())] = value;
      }
      this.listeners = new Map();
      this.children = [];
      this.parentElement = null;
      this.hidden = Object.hasOwn(node.attrs,'hidden');
      this.tabIndex = Number(node.attrs.tabindex ?? -1);
      this.classList = {
        add: name => {this.attributes.class = [...new Set((this.attributes.class || '').split(/\s+/).filter(Boolean).concat(name))].join(' ');},
        contains: name => (this.attributes.class || '').split(/\s+/).includes(name)
      };
    }
    get id() { return this.attributes.id; }
    get textContent() { return this.replacementText ?? this.parts.map(p => typeof p === 'number' ? elements[p].textContent : p).join(''); }
    set textContent(value) { this.replacementText = String(value); }
    get options() { return this.children.filter(n => n.tagName === 'option'); }
    get selectedOptions() { return this.options.filter(n => n.attributes.value === this.value); }
    get value() { return this.assignedValue ?? this.options.find(n=>Object.hasOwn(n.attributes,'selected'))?.attributes.value ?? this.options[0]?.attributes.value ?? this.attributes.value; }
    set value(value) { this.assignedValue = value; }
    get disabled() { return Object.hasOwn(this.attributes, 'disabled'); }
    set disabled(value) { if (value) this.attributes.disabled = ''; else delete this.attributes.disabled; }
    getAttribute(name) {
      if (name === 'hidden') return this.hidden ? '' : null;
      if (name.startsWith('data-')) return this.dataset[name.slice(5).replace(/-([a-z])/g,(_,c)=>c.toUpperCase())] ?? null;
      return this.attributes[name] ?? null;
    }
    setAttribute(name,value) { this.attributes[name] = String(value); }
    addEventListener(type, callback) { this.listeners.set(type, (this.listeners.get(type) || []).concat(callback)); }
    emit(type,values = {}) {
      const event = {target:this,defaultPrevented:false,preventDefault(){this.defaultPrevented=true;},...values};
      for (const callback of this.listeners.get(type) || []) callback(event);
      return event;
    }
    focus() { document.activeElement = this; }
    scrollIntoView(options) { this.lastScrollRequest = options; }
    closest(selector) { for(let node=this;node;node=node.parentElement)if(matches(node,selector))return node;return null; }
    append(child) { child.parentElement = this;this.children.push(child); }
    remove() { this.parentElement.children = this.parentElement.children.filter(c=>c!==this);this.parentElement=null; }
    click() {
      if (this.tagName === 'a' && this.download) downloads.push({filename:this.download,href:this.href,blob:urlBlobs.get(this.href),attached:!!this.parentElement});
      this.emit('click');
    }
  }
  const elements = parsed.map(n=>new Element(n));
  elements.forEach((element,i)=>{
    if (parsed[i].parent !== null) {
      element.parentElement = elements[parsed[i].parent];
      element.parentElement.children.push(element);
    }
  });
  document = {
    body: elements.find(n=>n.tagName==='body'), activeElement:null,
    getElementById:id=>elements.find(n=>n.id===id) || null,
    querySelectorAll:selector=>elements.filter(n=>matches(n,selector)),
    querySelector:selector=>elements.find(n=>matches(n,selector)) || null,
    createElement:tag=>new Element({tag,attrs:{},parts:[]})
  };
  const window = {
    addEventListener(type,callback){events.set(type,(events.get(type)||[]).concat(callback));}
  };
  const context = vm.createContext({document,window,location,Blob,Uint8Array,atob,
    history:{replaceState(a,b,hash){historyCalls.push(hash);location.hash=hash;}},
    URL:{createObjectURL(blob){const url='blob:review-'+(++sequence);urlBlobs.set(url,blob);return url;},revokeObjectURL(url){urlBlobs.delete(url);}},
    setTimeout(callback,delay){timers.push({callback,delay});},
    requestAnimationFrame(callback){callback(0);return 1;}
  });
  vm.runInContext(clientScript,context,{timeout:1000,filename:'index.html:actual-client-script'});
  return {document,elements,location,downloads,timers,urlBlobs,historyCalls,
    hashchange(hash){location.hash=hash;for(const callback of events.get('hashchange')||[])callback();}
  };
}

// Generic selector subset used by this HTML's display rules and client queries.
// It does not implement layout or browser style calculation.
function matchesSimple(node, selector) {
  if (!node) return false;
  selector = selector.replace(/:not\(([^()]+)\)/g, (_,negative)=>matchesSimple(node,negative)?':never':'');
  if (/:/.test(selector)) return false;
  const tag = /^([a-z][\w-]*)/i.exec(selector)?.[1];
  if (tag && tag !== node.tagName) return false;
  for(const match of selector.matchAll(/#([\w-]+)/g)) if(node.id!==match[1])return false;
  for(const match of selector.matchAll(/\.([\w-]+)/g)) if(!node.classList.contains(match[1]))return false;
  for(const match of selector.matchAll(/\[([\w-]+)(?:=(["']?)([^\]"']*)\2)?\]/g)) {
    const value=node.getAttribute(match[1]);
    if(value===null || (match[3]!==undefined && value!==match[3]))return false;
  }
  return true;
}
function matches(node, selector) {
  const bits=selector.trim().split(/\s+/);
  if(bits.some(s=>s==='>'||s==='+'))return false;
  if(!matchesSimple(node,bits.pop()))return false;
  while(bits.length){const needed=bits.pop();node=node.parentElement;while(node&&!matchesSimple(node,needed))node=node.parentElement;if(!node)return false;}
  return true;
}
function parseCss(source, media=[], rules=[]) {
  let offset=0;
  while(offset<source.length){
    const open=source.indexOf('{',offset);if(open<0)break;
    const selector=source.slice(offset,open).trim();
    let close=open+1,depth=1;
    while(depth&&close<source.length){if(source[close]==='{')depth++;if(source[close]==='}')depth--;close++;}
    const body=source.slice(open+1,close-1);
    if(selector.startsWith('@media'))parseCss(body,[...media,selector.slice(6).trim()],rules);
    else if(!selector.startsWith('@'))rules.push({selector,body,media,index:rules.length});
    offset=close;
  }
  return rules;
}
const cssRules=parseCss(styleText);
function appliesMedia(rule,width,medium) {
  return rule.media.every(condition=>{
    if(condition==='print')return medium==='print';
    if(condition==='screen')return medium==='screen';
    if(condition.includes('prefers-reduced-motion'))return false;
    const max=/max-width:\s*(\d+)px/.exec(condition);
    if(max)return width<=Number(max[1]);
    throw new Error('Unsupported media condition '+condition);
  });
}
function display(node,width,medium) {
  const matchesForProperty=[];
  for(const rule of cssRules){
    if(!appliesMedia(rule,width,medium))continue;
    for(const selector of rule.selector.split(',')){
      if(!matches(node,selector))continue;
      const match=/(?:^|;)\s*display\s*:\s*([^;]+)/.exec(rule.body);if(!match)continue;
      const specificity=(selector.match(/#/g)||[]).length*100+(selector.match(/\.|\[|:(?!not\()/g)||[]).length*10+(selector.match(/(?:^|\s)(?:body|html|[a-z]+)(?=[.#:\[\s]|$)/g)||[]).length;
      matchesForProperty.push({value:match[1].replace(/!important/g,'').trim(),priority:/!important/.test(match[1])?1:0,specificity,index:rule.index});
    }
  }
  matchesForProperty.sort((a,b)=>a.priority-b.priority||a.specificity-b.specificity||a.index-b.index);
  return matchesForProperty.at(-1)?.value || 'block';
}
function isVisible(node,width,medium){for(let n=node;n;n=n.parentElement)if(n.hidden||display(n,width,medium)==='none')return false;return true;}
function selectedId(dom){return dom.document.querySelectorAll('[data-case-tab]').find(n=>n.getAttribute('aria-selected')==='true')?.dataset.caseTab;}
function assertSelection(dom,id){
  assert.equal(selectedId(dom),id);
  const tabs=dom.document.querySelectorAll('[data-case-tab]');
  assert.equal(tabs.filter(n=>n.getAttribute('aria-selected')==='true').length,1);
  assert.deepEqual(tabs.filter(n=>n.tabIndex===0).map(n=>n.dataset.caseTab),[id]);
  assert.deepEqual(dom.document.querySelectorAll('.case-panel').filter(n=>!n.hidden).map(n=>n.id),['panel-'+id]);
}

check('Changed and retained counts come from actual previous/latest bytes, and retained cases omit change excerpts',()=>{
  const changed=data.cases.filter(entry=>entry.documents.previous.sha256!==entry.documents.latest.sha256);
  assert.equal(data.changedCount,changed.length);
  assert.equal(data.retainedCount,data.cases.length-changed.length);
  assert(data.cases.every(entry=>entry.changed===(entry.documents.previous.sha256!==entry.documents.latest.sha256)));
  const dom=makeDom();
  for(const entry of data.cases.filter(entry=>!entry.changed)){
    const panel=dom.document.getElementById('panel-'+entry.id);
    assert(!dom.elements.some(node=>node.classList.contains('excerpts')&&node.closest('.case-panel')===panel));
  }
});
check('Case, full-document, input and download counts match the selected manifest',()=>{
  assert.equal(data.cases.length,expectedCases.length);
  assert.equal(parsed.filter(n=>n.attrs['data-document']).length,expectedDocumentCount);
  assert.equal(parsed.filter(n=>(n.attrs.class||'').split(' ').includes('raw-input')).length,expectedCases.length);
  assert.equal(parsed.filter(n=>n.attrs['data-source']).length,expectedDownloadCount);
});
check('All HTML IDs are unique and every local fragment / ARIA target resolves',()=>{
  const ids=parsed.map(n=>n.attrs.id).filter(Boolean);assert.equal(ids.length,new Set(ids).size);
  for(const node of parsed){
    if(node.attrs.href?.startsWith('#'))assert(ids.includes(decodeURIComponent(node.attrs.href.slice(1))),node.attrs.href);
    for(const attr of ['aria-controls','aria-labelledby'])for(const id of (node.attrs[attr]||'').split(/\s+/).filter(Boolean))assert(ids.includes(id),attr+': '+id);
  }
});
check('Each footnote reference and backlink stays inside the same document',()=>{
  const dom=makeDom();
  const paperFor=node=>{while(node&&!node.getAttribute('data-document'))node=node.parentElement;return node;};
  const refs=dom.elements.filter(n=>n.getAttribute('role')==='doc-noteref');
  assert(refs.length>0);
  for(const ref of refs){
    const target=dom.document.getElementById(ref.getAttribute('href').slice(1));
    assert.equal(paperFor(ref),paperFor(target));
    assert(dom.elements.some(n=>n.tagName==='a'&&n.getAttribute('href')==='#'+ref.id&&paperFor(n)===paperFor(ref)));
  }
});
check('Initialization, valid case hashes, invalid hashes, and malformed URI hashes',()=>{
  for(const hash of ['', '#missing_case','#%E0%A4%A'])assertSelection(makeDom(hash),data.cases[0].id);
  for(const entry of data.cases)assertSelection(makeDom('#'+entry.id),entry.id);
});
check('All tab click handlers update selection, roving tabindex, hidden panels and case hash',()=>{
  const dom=makeDom();
  for(const tab of dom.document.querySelectorAll('[data-case-tab]')){tab.click();assertSelection(dom,tab.dataset.caseTab);assert.equal(dom.location.hash,'#'+tab.dataset.caseTab);}
});
check('Arrow keys wrap, Home/End select endpoints, focus follows selection, unrelated keys are untouched',()=>{
  const dom=makeDom();const tabs=dom.document.querySelectorAll('[data-case-tab]');
  for(let i=0;i<tabs.length;i++)for(const [key,index] of [['ArrowRight',(i+1)%tabs.length],['ArrowDown',(i+1)%tabs.length],['ArrowLeft',(i+tabs.length-1)%tabs.length],['ArrowUp',(i+tabs.length-1)%tabs.length],['Home',0],['End',tabs.length-1]]){
    tabs[i].click();const event=tabs[i].emit('keydown',{key});assert(event.defaultPrevented);assertSelection(dom,tabs[index].dataset.caseTab);assert.equal(dom.document.activeElement,tabs[index]);
  }
  const before=selectedId(dom);assert.equal(tabs[0].emit('keydown',{key:'a'}).defaultPrevented,false);assert.equal(selectedId(dom),before);
});
check('Comparison/view changes preserve the chosen case and update labels and status for every case',()=>{
  const dom=makeDom();const comparison=dom.document.getElementById('comparison-mode');const view=dom.document.getElementById('view-mode');
  for(const entry of data.cases){
    dom.document.getElementById('tab-'+entry.id).click();
    for(const compare of ['baseline','previous'])for(const mode of ['both','baseline','latest']){
      comparison.value=compare;comparison.emit('change');view.value=mode;view.emit('change');assertSelection(dom,entry.id);
      const effective = compare === 'baseline' && entry.documents.baseline ? 'baseline' : 'previous';
      assert.equal(dom.document.body.dataset.comparison,effective);assert.equal(dom.document.body.dataset.view,mode);
      assert(comparison.options.find(option => option.value === 'previous').textContent.includes(entry.previousLabel));
      assert.equal(comparison.options.find(option => option.value === 'baseline').disabled,!entry.documents.baseline);
      assert(view.options[1].textContent.includes(effective==='previous'?entry.previousLabel:'스킬 미적용'));
      assert(dom.document.getElementById('status').textContent.includes(entry.title));
      for(const other of data.cases){
        const description=dom.document.querySelector('[data-reader-description="'+other.id+'"]').textContent;
        const otherEffective=effective==='baseline'&&other.documents.baseline?'baseline':'previous';
        assert(description.includes(mode==='latest'?'v'+data.skillVersion:otherEffective==='previous'?other.previousLabel:'스킬 미적용'));
        assert.equal(description.includes('독립적으로 스크롤'),mode==='both');
        assert.equal(description.includes('페이지를 스크롤'),mode!=='both');
      }
    }
  }
});
check('CSS display-rule analysis: correct visible conditions for all cases, six selections, three widths and screen/print',()=>{
  const dom=makeDom();const comparison=dom.document.getElementById('comparison-mode');const view=dom.document.getElementById('view-mode');
  for(const entry of data.cases){
    dom.document.getElementById('tab-'+entry.id).click();
    for(const compare of ['baseline','previous'])for(const mode of ['both','baseline','latest']){
      comparison.value=compare;comparison.emit('change');view.value=mode;view.emit('change');
      const effective=compare==='baseline'&&entry.documents.baseline?'baseline':'previous';
      const expected=mode==='both'?[effective,'latest']:mode==='baseline'?[effective]:['latest'];
      for(const width of [375,800,1280])for(const medium of ['screen','print']){
        const papers=dom.document.querySelectorAll('.paper').filter(n=>isVisible(n,width,medium));
        assert.deepEqual(papers.map(n=>n.dataset.document),expected,[entry.id,compare,mode,width,medium].join('/'));
      }
    }
  }
});
check('No-JavaScript display-rule analysis keeps every document available',()=>{
  const dom=makeDom();dom.document.body.attributes.class='';
  for(const panel of dom.document.querySelectorAll('.case-panel'))panel.hidden=false;
  for(const width of [375,800,1280])assert.equal(dom.document.querySelectorAll('.paper').filter(n=>isVisible(n,width,'screen')).length,expectedDocumentCount);
});
check('Hashchange switches valid cases and does not disrupt the current case for a clicked footnote',()=>{
  const dom=makeDom();
  for(const entry of data.cases){dom.hashchange('#'+entry.id);assertSelection(dom,entry.id);}
  const ref=dom.elements.find(node=>node.getAttribute('role')==='doc-noteref');
  dom.hashchange(ref.getAttribute('href'));
  assertSelection(dom,ref.closest('.case-panel').id.slice('panel-'.length));
});
check('Default is previous; selecting a case without a historical baseline disables and normalizes the comparison',()=>{
  const dom=makeDom();const comparison=dom.document.getElementById('comparison-mode');
  assert.equal(data.defaultComparison,'previous');assert.equal(comparison.value,'previous');
  assert.equal(dom.document.body.dataset.comparison,'previous');
  const eligible=data.cases.find(entry=>entry.documents.baseline);
  for(const entry of data.cases.filter(entry=>!entry.documents.baseline)){
    dom.document.getElementById('tab-'+eligible.id).click();comparison.value='baseline';comparison.emit('change');
    assert.equal(comparison.value,'baseline');
    dom.document.getElementById('tab-'+entry.id).click();assertSelection(dom,entry.id);
    assert.equal(comparison.value,'previous');assert.equal(dom.document.body.dataset.comparison,'previous');
    assert.equal(comparison.options.find(option=>option.value==='baseline').disabled,true);
    assert(!dom.document.querySelectorAll('.paper').some(paper=>paper.closest('.case-panel')?.id==='panel-'+entry.id&&paper.dataset.document==='baseline'));
  }
});
check('All listed source SHA-256 values and recorded source count match actual files',()=>{
  assert(data.sourceFiles.length>0);
  assert.equal(data.sourceFiles.length,new Set(data.sourceFiles.map(item=>item.path)).size);
  for(const source of data.sourceFiles)assert.equal(createHash('sha256').update(fs.readFileSync(path.join(repo,source.path))).digest('hex'),source.sha256,source.path);
  assert(html.includes(data.sourceFiles.length+'개 파일'));
});
check('Top-level links lead to final examples and the repair report; empty limitations cards are omitted',()=>{
  assert(parsed.some(node=>node.attrs.href?.endsWith('/docs/examples/README.md')));
  assert(parsed.some(node=>node.attrs.href?.endsWith('/'+data.repairsPath)));
  const dom=makeDom();
  for(const entry of data.cases.filter(item=>!item.observations.limitations.length)){
    const panel=dom.document.getElementById('panel-'+entry.id);
    assert(!dom.elements.some(node=>node.tagName==='h3'&&node.textContent==='추가 확인 범위'&&node.closest('.case-panel')===panel));
  }
});
const downloadsDom=makeDom();
for(const button of downloadsDom.document.querySelectorAll('[data-source]')){
  button.click();
  const download=downloadsDom.downloads.at(-1);
  const entry=data.cases.find(c=>c.id===button.dataset.case);
  const source=button.dataset.source==='input'?entry.input:entry.documents[button.dataset.source];
  const original=fs.readFileSync(path.join(repo,source.path));
  const downloaded=Buffer.from(await download.blob.arrayBuffer());
  assert(download.attached,'Download anchor is attached at click');
  assert(downloaded.equals(original),'Downloaded bytes differ: '+source.path);
  assert.equal(createHash('sha256').update(downloaded).digest('hex'),source.sha256);
  assert.equal(downloaded.byteLength,source.bytes);
  assert.equal([...downloaded.toString('utf8')].length,source.characters);
  assert.equal(download.blob.type,'text/markdown;charset=utf-8');
  assert(download.filename.endsWith(entry.file));
}
assert.equal(downloadsDom.downloads.length,expectedDownloadCount);
assert.equal(downloadsDom.timers.length,expectedDownloadCount);
for(const timer of downloadsDom.timers){assert.equal(timer.delay,10000);timer.callback();}
assert.equal(downloadsDom.urlBlobs.size,0);
results.push('All ' + expectedDownloadCount + ' download handlers produce Blob bytes matching source files and SHA-256; anchors attach/remove; URLs revoke after scheduled delay');

check('Regression: opening/reloading footnote and backlink fragments selects their case; hashchange preserves each fragment',()=>{
  const fragments=parsed.filter(n=>n.attrs.role==='doc-noteref').flatMap(n=>[n.attrs.href,'#'+n.attrs.id]);
  assert(fragments.length>0);
  for(const fragment of fragments){
    const dom=makeDom(fragment);const target=dom.document.getElementById(fragment.slice(1));
    const owner=target.closest('.case-panel');
    assertSelection(dom,owner.id.slice('panel-'.length));assert(isVisible(target,1280,'screen'),fragment);
    assert.equal(dom.location.hash,fragment);
    dom.document.getElementById('tab-'+data.cases[0].id).click();
    dom.hashchange(fragment);assertSelection(dom,owner.id.slice('panel-'.length));assert(isVisible(target,1280,'screen'),fragment);
    assert.equal(dom.location.hash,fragment);
  }
});
check('Document headings and ToCs use case/version/condition prefixes and resolve inside their own document',()=>{
  const dom=makeDom();
  const tocs=dom.elements.filter(node=>node.classList.contains('document-toc'));
  assert(tocs.length>0,'Long source documents need a section ToC');
  for(const toc of tocs){
    const paper=toc.closest('[data-document]');
    const panel=paper.closest('.case-panel');
    const prefix=panel.id.slice('panel-'.length)+'-v'+data.skillVersion.replace(/\./g,'-')+'-'+paper.dataset.document+'-';
    const links=dom.elements.filter(node=>node.tagName==='a'&&node.closest('.document-toc')===toc);
    assert(links.length>=4);
    for(const link of links){
      const id=decodeURIComponent(link.getAttribute('href').slice(1));
      const target=dom.document.getElementById(id);
      assert(id.startsWith(prefix),id);
      assert.equal(target.closest('[data-document]'),paper);
      assert(['h2','h3'].includes(target.tagName));
      assert.equal(target.textContent,link.textContent,'ToC preserves the actual section title');
    }
  }
});
check('Heading fragments reveal the correct case and condition, then request scrolling without replacing the fragment',()=>{
  const dom=makeDom();
  const comparison=dom.document.getElementById('comparison-mode');
  const view=dom.document.getElementById('view-mode');
  const headings=dom.elements.filter(node=>node.tagName==='h2'&&node.id&&node.closest('.source-document'));
  assert(headings.length>0);
  for(const heading of headings){
    const paper=heading.closest('[data-document]');
    const owner=paper.closest('.case-panel');
    comparison.value='baseline';comparison.emit('change');
    view.value=paper.dataset.document==='latest'?'baseline':'latest';view.emit('change');
    const hash='#'+encodeURIComponent(heading.id);
    dom.hashchange(hash);
    assertSelection(dom,owner.id.slice('panel-'.length));
    assert(isVisible(heading,1280,'screen'),hash);
    assert.equal(dom.location.hash,hash);
    assert.equal(heading.lastScrollRequest.block,'start');
    assert.equal(dom.document.activeElement,heading);
  }
  for(const paper of dom.document.querySelectorAll('.paper')){
    const heading=dom.elements.find(node=>node.tagName==='h2'&&node.closest('[data-document]')===paper&&node.id);
    if(!heading)continue;
    const opened=makeDom('#'+encodeURIComponent(heading.id));
    assertSelection(opened,paper.closest('.case-panel').id.slice('panel-'.length));
    assert(isVisible(opened.document.getElementById(heading.id),1280,'screen'));
  }
});
check('Every source table has a keyboard-focusable horizontal scroll container',()=>{
  const dom=makeDom();
  const tables=dom.elements.filter(node=>node.tagName==='table'&&node.closest('.source-document'));
  assert(tables.length>0);
  for(const table of tables){
    assert(table.parentElement.classList.contains('document-table'));
    assert.equal(table.parentElement.tabIndex,0);
    assert.equal(table.parentElement.getAttribute('role'),'region');
    assert(table.parentElement.getAttribute('aria-label'));
  }
});
check('Formatted, duplicate, and non-ASCII heading fragments retain stable, distinct IDs',()=>{
  const headings=[];
  const output=renderMarkdown('# 제목\n\n## `코드`와 **강조**\n\n[이동](#코드와-강조)\n\n## 중복\n\n## 중복\n','fixture-v1-2-3-latest','README.md',{headings});
  assert.deepEqual(headings.map(item=>item.id),['fixture-v1-2-3-latest-제목','fixture-v1-2-3-latest-코드와-강조','fixture-v1-2-3-latest-중복','fixture-v1-2-3-latest-중복-2']);
  assert(output.includes('href="#fixture-v1-2-3-latest-코드와-강조"'));
});
check('Check mode rejects a missing or stale viewer without writing either output',()=>{
  const temporary=fs.mkdtempSync(path.join(os.tmpdir(),'korean-dev-writing-viewer-'));
  try{
    const output=path.join(temporary,'index.html');
    assert.throws(()=>buildViewer(repo,{run,output,check:true}),/Missing generated viewer/);
    assert(!fs.existsSync(output));
    fs.writeFileSync(output,'stale viewer\n');
    assert.throws(()=>buildViewer(repo,{run,output,check:true}),/Stale generated viewer/);
    assert.equal(fs.readFileSync(output,'utf8'),'stale viewer\n');
  }finally{fs.rmSync(temporary,{recursive:true,force:true});}
});
const summary={runId:data.runId,skillVersion:data.skillVersion,html:htmlPath,htmlSha256:createHash('sha256').update(html).digest('hex'),observationsIncluded:!!data.observationsPath,cases:data.cases.length,documents:expectedDocumentCount,downloads:expectedDownloadCount,checks:results.length,results,issues,limitations:['Node VM with DOM doubles; no real browser, layout, native focus/scroll, screen reader, download dialog, or print rendering was exercised.','CSS inspection evaluates display rules, media predicates, specificity, and ancestor visibility only; it does not measure overflow.']};
console.log(JSON.stringify(summary,null,2));
