#!/usr/bin/env node
/**
 * Build the offline comparison reader from a frozen correction manifest.
 * Usage: node scripts/build_viewer.mjs [--repo PATH] [--run PATH] [--output PATH] [--check]
 * No outputs are synthesized. Missing sources abort before index.html is written.
 */
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { Marked, Renderer } from './vendor/marked/marked.esm.mjs';

const DEFAULT_REPO = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const DEFAULT_RUN = 'evaluations/runs/2026-11-05-v0.6.0';
const REPOSITORY = 'https://github.com/hostkimjang/korean-dev-writing-skills';
const BLOB_ROOT = REPOSITORY + '/blob/main/';
const TREE_ROOT = REPOSITORY + '/tree/main/';
const CONDITIONS = ['baseline', 'previous', 'latest'];
const css = String.raw`
:root{
  color-scheme:light;
  --ink:#1d332c;
  --muted:#52665d;
  --line:#d6ded8;
  --paper:#fff;
  --bg:#f4f5ef;
  --green:#125c48;
  --soft:#e8f1e9;
  --mono:ui-monospace,SFMono-Regular,Consolas,monospace;
  --radius:13px}
*{
  box-sizing:border-box}
html{
  scroll-behavior:smooth}
body{
  margin:0;
  background:var(--bg);
  color:var(--ink);
  font-family:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",system-ui,sans-serif;
  font-size:15px;
  line-height:1.7;
  word-break:keep-all;
  overflow-wrap:anywhere}
a{
  color:#135b8b;
  text-underline-offset:3px}
a:hover{
  text-decoration-thickness:2px}
button,select{
  font:inherit}
button{
  cursor:pointer}
button,a,select,summary{
  touch-action:manipulation}
:focus-visible{
  outline:3px solid #d37822;
  outline-offset:4px}
[hidden]{
  display:none!important}
.sr-only{
  position:absolute;
  width:1px;
  height:1px;
  padding:0;
  margin:-1px;
  overflow:hidden;
  clip:rect(0,0,0,0);
  white-space:nowrap;
  border:0}
.skip{
  position:absolute;
  top:-80px;
  left:20px;
  z-index:10;
  background:var(--ink);
  color:white;
  padding:12px 20px}
.skip:focus{
  top:10px}
.shell{
  width:min(1480px,calc(100% - 64px));
  margin-inline:auto}
.masthead{
  border-bottom:1px solid var(--line);
  background:rgba(255,255,255,.55)}
.masthead .shell{
  display:flex;
  justify-content:space-between;
  align-items:center;
  gap:18px;
  min-height:60px;
  font-size:13px}
.brand{
  font-weight:750;
  letter-spacing:-.02em}
.run-label{
  color:var(--muted)}
.hero{
  padding:46px 0 30px;
  max-width:1000px}
.eyebrow{
  font-size:12px;
  letter-spacing:.07em;
  font-weight:750;
  margin:0 0 7px;
  color:var(--muted)}
.hero .eyebrow{
  color:var(--green)}
h1,h2,h3,h4,p{
  margin-top:0}
h1{
  font-size:clamp(27px,3vw,42px);
  letter-spacing:-.055em;
  line-height:1.3;
  margin-bottom:18px}
.lead{
  font-size:17px;
  max-width:940px;
  line-height:1.8;
  margin-bottom:12px}
.hero-note{
  color:var(--muted);
  font-size:14px;
  margin-bottom:0}
.hero-note strong{
  color:var(--ink)}
.toolbar{
  margin:0 0 24px}
.case-tabs{
  display:grid;
  grid-template-columns:repeat(3,minmax(0,1fr));
  gap:12px}
.case-tab{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:16px;
  padding:19px 22px;
  text-align:left;
  border:1px solid var(--line);
  border-radius:var(--radius);
  background:#fff;
  color:var(--ink);
  min-height:100px}
.case-tab:hover{
  border-color:#5e8b77}
.case-tab[aria-selected=true]{
  border:2px solid var(--green);
  padding:18px 21px;
  background:var(--soft);
  box-shadow:0 3px 0 #d4e5d7}
.tab-title{
  font-weight:750;
  font-size:17px;
  display:block}
.tab-sub{
  color:var(--muted);
  font-size:12px;
  display:block;
  margin-top:4px}
.tab-metric{
  font-size:25px;
  font-weight:750;
  font-variant-numeric:tabular-nums;
  white-space:nowrap;
  letter-spacing:-.04em}
.tab-metric small{
  font-size:12px;
  font-weight:500;
  letter-spacing:0}
.controls{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:14px;
  margin-top:19px}
.controls p{
  font-size:13px;
  color:var(--muted);
  margin:0}
.view-control{
  display:flex;
  align-items:center;
  gap:10px;
  flex-shrink:0}
.view-control label{
  font-size:13px;
  font-weight:650}
select{
  border:1px solid #a9b9ae;
  border-radius:7px;
  background:white;
  color:var(--ink);
  padding:7px 34px 7px 11px;
  min-height:40px}
.case-heading{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:18px;
  margin:30px 0 18px}
.case-heading h2{
  font-size:26px;
  letter-spacing:-.04em;
  margin-bottom:6px;
  line-height:1.4}
.case-heading p:last-child{
  color:var(--muted);
  font-size:14px;
  margin:0}
.input-download{
  flex-shrink:0;
  border:1px solid #b1c1b5;
  border-radius:8px;
  padding:9px 14px;
  color:var(--ink);
  background:transparent;
  font-size:13px}
.input-download:hover{
  background:var(--soft)}
.observations{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:14px}
.observation{
  padding:20px 22px;
  border:1px solid var(--line);
  border-radius:var(--radius);
  background:#fbfcf8}
.observation h3{
  font-size:14px;
  color:var(--green);
  margin-bottom:9px}
.observation p{
  font-size:14px;
  line-height:1.85;
  margin:0}
.assessment{
  font-size:13px;
  color:var(--muted);
  padding:14px 3px 0;
  margin:0 0 18px}
.assessment strong{
  color:var(--ink)}
code{
  font-family:var(--mono);
  font-size:.9em;
  background:#edf0ea;
  border-radius:4px;
  padding:2px 4px;
  word-break:break-word}
.excerpts,.record,.method{
  border:1px solid var(--line);
  border-radius:var(--radius);
  background:#fff;
  margin-bottom:20px;
  overflow:hidden}
summary{
  cursor:pointer;
  font-size:14px;
  font-weight:700;
  padding:15px 20px}
summary::marker{
  color:var(--green)}
summary span{
  font-weight:400;
  color:var(--muted);
  font-size:12px;
  margin-left:12px}
.excerpts[open] summary,.record[open] summary,.method[open] summary{
  border-bottom:1px solid var(--line)}
.excerpt{
  padding:22px 24px;
  border-bottom:1px solid var(--line)}
.excerpt h4{
  font-size:16px;
  margin-bottom:16px}
.excerpt-grid{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:26px}
.excerpt .eyebrow{
  font-size:11px}
.applied-text{
  color:var(--green)}
.location{
  font-size:12px;
  color:var(--muted);
  line-height:1.6;
  min-height:40px;
  margin-bottom:10px}
blockquote{
  margin:0;
  padding:12px 17px;
  border-left:3px solid #c3d0c4;
  background:#f5f7f2;
  font-size:14px}
blockquote p:last-child{
  margin:0}
.excerpt-note{
  font-size:13px;
  color:var(--muted);
  margin:16px 0 0}
.tradeoff{
  padding:19px 24px;
  background:#faf8f0}
.tradeoff h4{
  font-size:13px;
  margin:0 0 7px}
.tradeoff p{
  font-size:13px;
  color:#625f46;
  margin:0}
.reader-intro{
  display:flex;
  justify-content:space-between;
  gap:16px;
  align-items:baseline;
  padding:0 3px;
  margin:25px 0 12px}
.reader-intro h3{
  font-size:16px;
  margin:0}
.reader-intro p{
  font-size:12px;
  color:var(--muted);
  margin:0}
.reader{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:20px;
  align-items:start}
.paper{
  border:1px solid #cbd5cd;
  border-radius:var(--radius);
  background:white;
  max-height:78vh;
  overflow:auto;
  scrollbar-gutter:stable;
  scroll-margin-top:20px;
  box-shadow:0 4px 16px #22352a05}
.paper.revised{
  border-color:#94b7a1}
.paper-header{
  display:flex;
  justify-content:space-between;
  gap:15px;
  align-items:center;
  position:sticky;
  top:0;
  z-index:1;
  padding:17px 22px;
  background:#f7f8f5;
  border-bottom:1px solid var(--line)}
.paper.revised .paper-header{
  background:#edf5ec}
.paper-header h3{
  font-size:15px;
  margin:0 0 2px}
.paper-header p{
  font-size:12px;
  color:var(--muted);
  margin:0;
  font-variant-numeric:tabular-nums}
.paper-header p span{
  margin:0 4px}
.download{
  white-space:nowrap;
  border:1px solid #b0c0b3;
  border-radius:7px;
  padding:6px 11px;
  background:white;
  color:var(--ink);
  font-size:12px}
.download:hover{
  background:#e3eee4}
.download span{
  margin-left:3px}
.source-document{
  padding:30px 28px 22px;
  line-height:1.9;
  font-size:14px;
  word-break:normal;
  overflow-wrap:anywhere}
.source-document h1{
  font-size:24px;
  line-height:1.45;
  letter-spacing:-.035em;
  margin:0 0 22px;
  padding-bottom:18px;
  border-bottom:1px solid var(--line)}
.source-document h2{
  font-size:19px;
  letter-spacing:-.025em;
  line-height:1.5;
  margin:34px 0 14px}
.source-document h3{
  font-size:16px;
  line-height:1.55;
  margin:24px 0 12px}
.source-document p{
  margin:0 0 15px}
.source-document li{
  padding-left:2px;
  margin:5px 0}
.source-document ul,.source-document ol{
  padding-left:23px;
  margin:0 0 18px}
.source-document table{
  font-size:12px;
  line-height:1.75;
  table-layout:fixed;
  width:100%;
  border-collapse:collapse;
  margin:18px 0 22px}
.source-document th,.source-document td{
  border:1px solid #dce3dc;
  padding:10px 9px;
  vertical-align:top;
  text-align:left;
  overflow-wrap:anywhere}
.source-document th{
  background:#f2f5ef;
  font-weight:650}
.source-document tr:nth-child(even) td{
  background:#fcfdfa}
.source-document pre{
  background:#20392f;
  color:#edf4eb;
  border-radius:8px;
  padding:16px;
  overflow:auto;
  font-size:12px;
  line-height:1.8;
  margin:16px 0 20px;
  word-break:normal;
  white-space:pre}
.source-document pre code{
  padding:0;
  background:transparent;
  color:inherit;
  border-radius:0;
  font-size:inherit;
  word-break:normal}
.paper-footer{
  border-top:1px solid var(--line);
  padding:17px 28px 22px;
  color:var(--muted);
  font-size:11px}
.paper-footer p{
  margin:0 0 5px}
.paper-footer code{
  font-size:10px;
  background:none;
  padding:0;
  overflow-wrap:anywhere}
.record{
  margin-top:20px}
.record>p,.record>.table-wrap{
  margin:16px 22px}
.small{
  font-size:12px;
  color:var(--muted)}
.table-wrap{
  overflow-x:auto}
.table-wrap table{
  border-collapse:collapse;
  width:100%;
  font-size:13px}
.table-wrap th,.table-wrap td{
  padding:8px 12px;
  border-bottom:1px solid var(--line);
  text-align:left}
.table-wrap thead th{
  background:#f1f5ee}
.table-wrap tbody th{
  font-weight:500}
.endnotes{
  margin:30px 0 45px}
.method-body{
  padding:18px 24px 24px;
  font-size:13px;
  color:var(--muted)}
.method-body p{
  margin-bottom:14px}
.method-body ul{
  padding-left:20px}
.method-body li{
  margin:8px 0}
.method-body p:last-child{
  margin-bottom:0}
.foot{
  display:flex;
  justify-content:space-between;
  gap:20px;
  color:var(--muted);
  font-size:12px;
  border-top:1px solid var(--line);
  padding:20px 0 30px}
.foot p{
  margin:0}
.js .case-panel{
  margin-top:0}
.no-js{
  padding:14px 20px;
  border:1px solid var(--line);
  border-radius:8px;
  background:white;
  margin:10px 0 20px}
.js[data-view=baseline] .paper.revised,.js[data-view=revised] .paper.baseline{
  display:none}
.js[data-view=baseline] .reader,.js[data-view=revised] .reader{
  grid-template-columns:minmax(0,980px);
  justify-content:center}
.case-panel+.case-panel{
  margin-top:70px}
.status{
  min-height:1px}
.no-script-only{
  display:block}
.js .no-script-only{
  display:none}
body:not(.js) .download,body:not(.js) .input-download,body:not(.js) .view-control,body:not(.js) .case-tabs{
  display:none}

@media(max-width:1050px){
  .shell{
  width:calc(100% - 36px)}
.case-tab{
  padding:16px;
  gap:9px}
.case-tab[aria-selected=true]{
  padding:15px}
.tab-title{
  font-size:16px}
.tab-metric{
  font-size:22px}
.tab-sub{
  font-size:11px}
.source-document{
  padding:24px 19px}
.paper-header{
  padding:14px 17px}
.hero{
  padding-top:32px}
.controls{
  align-items:flex-start}
.controls p{
  max-width:58%}
}

@media(max-width:760px){
  .shell{
  width:calc(100% - 28px)}
.masthead .shell{
  min-height:52px;
  font-size:11px;
  gap:8px}
.hero{
  padding:30px 0 24px}
.lead{
  font-size:15px}
.hero-note{
  font-size:13px}
.case-tabs{
  gap:7px}
.case-tab{
  display:block;
  padding:12px 10px;
  min-height:110px}
.case-tab[aria-selected=true]{
  padding:11px 9px}
.tab-title{
  font-size:14px}
.tab-sub{
  font-size:10px;
  margin-top:5px}
.tab-metric{
  font-size:21px;
  display:block;
  margin-top:5px}
.tab-metric small{
  font-size:10px}
.controls{
  display:block;
  margin-top:15px}
.controls p{
  max-width:none;
  font-size:12px;
  margin-bottom:13px}
.view-control{
  justify-content:space-between}
.view-control select{
  min-width:185px}
.case-heading{
  align-items:flex-start;
  margin-top:25px;
  flex-wrap:wrap;
  gap:12px}
.case-heading h2{
  font-size:23px}
.input-download{
  font-size:12px;
  padding:7px 12px}
.observations{
  grid-template-columns:1fr;
  gap:9px}
.observation{
  padding:17px 18px}
.observation p{
  font-size:13px}
.assessment{
  font-size:12px;
  padding-top:12px}
.excerpts summary span{
  display:block;
  margin:4px 0 0 18px;
  font-size:11px}
.excerpt{
  padding:18px}
.excerpt-grid{
  grid-template-columns:1fr;
  gap:18px}
.location{
  min-height:0}
.excerpt-note{
  font-size:12px}
.reader-intro{
  display:block;
  margin-top:22px}
.reader-intro p{
  margin-top:5px;
  font-size:11px}
.reader{
  grid-template-columns:1fr;
  gap:18px}
.paper{
  max-height:none;
  overflow:visible;
  scrollbar-gutter:auto}
.paper-header{
  position:static;
  border-radius:var(--radius) var(--radius) 0 0}
.source-document{
  padding:24px 18px;
  line-height:1.85;
  font-size:14px}
.source-document h1{
  font-size:22px}
.source-document h2{
  font-size:18px}
.source-document table{
  font-size:11px;
  line-height:1.7}
.source-document th,.source-document td{
  padding:8px 6px}
.source-document pre{
  font-size:11px;
  padding:12px}
.foot{
  display:block}
.foot p+p{
  margin-top:8px}
.record>p,.record>.table-wrap{
  margin:13px 18px}
.method-body{
  padding:16px 18px}
.endnotes{
  margin-bottom:20px}
}

@media(prefers-reduced-motion:reduce){
  html{
  scroll-behavior:auto}
}

@media print{
  body{
  background:white;
  font-size:11pt}
.shell{
  width:100%}
.masthead,.toolbar,.input-download,.download,.reader-intro p,.record,.endnotes,.foot,.excerpts{
  display:none!important}
.hero{
  padding:0 0 12px}
.hero h1{
  font-size:24pt}
.case-panel[hidden]{
  display:none!important}
.reader{
  display:block}
.paper{
  max-height:none;
  overflow:visible;
  border:0;
  box-shadow:none;
  break-before:page}
.paper-header{
  position:static;
  background:transparent!important;
  padding:0 0 10px}
.source-document{
  padding:0;
  font-size:10pt}
.source-document table{
  font-size:8pt}
.paper-footer{
  padding:12px 0}
.source-document h2,.source-document h3{
  break-after:avoid}
.source-document pre,.source-document tr{
  break-inside:avoid}
.observations{
  display:block}
.observation{
  border:0;
  padding:5px 0}
.assessment{
  padding:4px 0}
}

.case-tabs{
  grid-template-columns:repeat(5,minmax(0,1fr));
  gap:10px}
.case-tab{
  min-height:93px;
  padding:16px 18px;
  gap:10px}
.case-tab[aria-selected=true]{
  padding:15px 17px}
.tab-title{
  font-size:15px;
  line-height:1.5}
.tab-number{
  font-family:var(--mono);
  font-size:12px;
  color:var(--muted);
  align-self:flex-start;
  padding-top:2px}
.tab-sub{
  font-size:11px;
  line-height:1.7}
.controls{
  align-items:flex-start;
  flex-wrap:wrap}
.controls>p{
  flex:1 1 280px;
  max-width:510px}
.control-group{
  display:flex;
  gap:13px;
  flex-wrap:wrap;
  justify-content:flex-end}
.view-control{
  align-items:center}
.hero-note+.hero-note{
  margin-top:8px}
.report-links{
  display:flex;
  flex-wrap:wrap;
  gap:8px 20px;
  margin:19px 0 0;
  font-size:13px}
.case-heading{
  align-items:flex-start}
.case-heading h2{
  margin-bottom:8px}
.comparison-description{
  max-width:850px}
.observation ul{
  font-size:14px;
  line-height:1.85;
  padding-left:20px;
  margin:0}
.observation li+li{
  margin-top:7px}
.observation p+p{
  margin-top:10px}
.observation-summary{
  font-size:14px;
  line-height:1.85;
  padding:0 3px;
  margin-bottom:16px}
.observation-summary p:last-child{
  margin-bottom:0}
.observation-notice{
  background:#fbfcf8;
  border:1px solid var(--line);
  border-radius:var(--radius);
  padding:17px 20px;
  color:var(--muted);
  font-size:14px;
  margin-bottom:18px}
.observation-notice p:last-child{
  margin-bottom:0}
.scope-note{
  font-size:12px;
  color:var(--muted);
  margin:0 3px 16px}
.comparison-scope{
  margin-bottom:0}
.observations:empty{
  display:none}
.observation-details{
  padding:18px 22px;
  font-size:13px}
.observation-details p:last-child{
  margin-bottom:0}
.observation-details ul{
  padding-left:21px}
.finding-list{
  margin:0}
.finding-list dt{
  font-weight:650;
  margin-top:9px}
.finding-list dd{
  margin:4px 0 12px 15px}
.finding-list dd p{
  margin:0}
.excerpt blockquote{
  white-space:normal}
.excerpt blockquote pre{
  white-space:pre-wrap}
.excerpt:last-child{
  border-bottom:0}
.excerpt-note p{
  margin-bottom:0}
.paper{
  min-width:0}
.reader-intro{
  flex-wrap:wrap}
.reader-intro p{
  font-size:12px}
.paper-footer a{
  font-size:11px}
.paper-footer .path{
  font-family:var(--mono);
  overflow-wrap:anywhere}
.document-meta{
  display:flex;
  flex-wrap:wrap;
  gap:3px 8px}
.source-document table{
  table-layout:auto}
.source-document td,.source-document th{
  min-width:65px}
.source-document hr{
  border:0;
  border-top:1px solid var(--line);
  margin:25px 0}
.source-document h4{
  font-size:15px;
  margin:22px 0 10px}
.source-document blockquote{
  margin:16px 0}
.source-document img{
  max-width:100%}
.source-document pre{
  max-width:100%}
.source-document .footnotes{
  border-top:1px solid var(--line);
  font-size:12px;
  margin-top:28px;
  padding-top:5px}
.source-document .footnotes h2{
  font-size:14px;
  margin:15px 0 10px}
.source-document .footnotes p{
  margin-bottom:7px}
.footnote-ref{
  font-size:.75em;
  line-height:0}
.footnote-ref a{
  text-decoration:none;
  padding:2px}
.footnote-backlinks{
  font-size:11px}
.footnote-backlinks a+a{
  margin-left:10px}
.source-document a{
  overflow-wrap:anywhere}
.input-record{
  margin:16px 0 20px}
.input-record .input-body{
  padding:0 22px 22px}
.raw-input{
  font-family:var(--mono);
  font-size:12px;
  line-height:1.75;
  white-space:pre-wrap;
  overflow-wrap:anywhere;
  word-break:normal;
  background:#f5f7f2;
  border:1px solid var(--line);
  border-radius:8px;
  padding:18px;
  margin:16px 0;
  max-height:60vh;
  overflow:auto}
.record th,.record td{
  vertical-align:top}
.record caption{
  text-align:left;
  color:var(--muted);
  font-size:12px;
  padding:0 0 10px}
.source-files{
  list-style:none;
  padding:0!important}
.source-files li{
  padding:11px 0;
  border-bottom:1px solid var(--line)}
.source-files code{
  display:block;
  background:none;
  padding:2px 0;
  font-size:10px;
  overflow-wrap:anywhere}
.source-files a{
  overflow-wrap:anywhere}
.method-body dl{
  margin:0}
.no-js .small{
  margin:0}
.foot a{
  white-space:nowrap}
.js[data-comparison=baseline] .paper.previous,.js[data-comparison=previous] .paper.baseline{
  display:none}
.js[data-view=latest] .paper.baseline,.js[data-view=latest] .paper.previous{
  display:none}
.js[data-view=latest] .reader{
  grid-template-columns:minmax(0,980px);
  justify-content:center}
.js .case-panel+.case-panel{
  margin-top:0}
body:not(.js) .reader{
  grid-template-columns:1fr}
body:not(.js) .control-group{
  display:none}
.paper:focus-visible{
  outline-offset:2px}

@media(max-width:1100px){
  .case-tabs{
  grid-template-columns:repeat(3,minmax(0,1fr))}
.controls{
  display:block}
.controls>p{
  max-width:none;
  margin-bottom:12px}
.control-group{
  justify-content:flex-start}
.case-tab{
  padding:14px}
.case-tab[aria-selected=true]{
  padding:13px}
.tab-title{
  font-size:14px}
.tab-number{
  display:none}
}

@media(max-width:760px){
  .case-tabs{
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:8px}
.case-tab{
  min-height:83px;
  padding:12px 13px}
.case-tab[aria-selected=true]{
  padding:11px 12px}
.tab-title{
  font-size:14px}
.tab-sub{
  font-size:10px;
  margin-top:4px}
.control-group{
  display:grid;
  grid-template-columns:1fr;
  gap:10px}
.view-control{
  display:grid;
  grid-template-columns:76px minmax(0,1fr);
  gap:10px}
.view-control select{
  min-width:0;
  width:100%;
  font-size:13px}
.controls>p{
  margin-bottom:14px;
  font-size:12px}
.report-links{
  font-size:12px;
  gap:8px 16px}
.observation ul{
  font-size:13px}
.observation-summary,.observation-notice{
  font-size:13px}
.scope-note{
  font-size:11px}
.paper-header{
  gap:9px}
.paper-header h3{
  font-size:14px}
.paper-header p{
  font-size:11px}
.download{
  padding:7px 9px;
  min-height:38px}
.reader-intro p{
  font-size:11px}
.input-record .input-body{
  padding:0 18px 18px}
.raw-input{
  padding:14px;
  font-size:11px;
  max-height:none}
.source-document table{
  table-layout:fixed}
.source-document td,.source-document th{
  min-width:0}
.paper-footer{
  padding:16px 18px}
.source-document .footnotes{
  font-size:12px}
.source-files code{
  font-size:9px}
}

@media print{
  .input-record,.observation-notice,.report-links,.scope-note{
  display:none!important}
.js[data-comparison=baseline] .paper.previous,.js[data-comparison=previous] .paper.baseline,.js[data-view=latest] .paper.baseline,.js[data-view=latest] .paper.previous,.js[data-view=baseline] .paper.latest{
  display:none!important}
.paper{
  max-height:none}
.source-document a{
  color:inherit}
.footnote-ref a{
  text-decoration:none}
}

/* Keep the case picker compact without clipping titles or reducing touch targets. */
.case-tab{
  min-height:62px;
  padding:10px 12px;
  gap:8px;
  align-items:flex-start}

.case-tab[aria-selected=true]{
  padding:9px 11px}

.tab-title{
  font-size:14px;
  line-height:1.45}

.tab-sub{
  font-size:11px;
  margin-top:3px}

.document-toc{
  padding:0 22px;
  border-bottom:1px solid var(--line);
  background:#fbfcf8;
  font-size:13px}

.document-toc summary{
  padding:12px 0;
  font-size:13px}

.document-toc summary span{
  font-size:11px}

.document-toc ol{
  list-style:none;
  margin:0;
  padding:0 0 14px;
  columns:2;
  column-gap:22px}

.document-toc li{
  break-inside:avoid;
  margin:0 0 7px;
  line-height:1.6}

.document-toc .toc-depth-3{
  padding-left:12px;
  font-size:12px}

.document-toc a{
  display:inline-block;
  padding:2px 0}

.source-document{
  min-width:0}

.source-document [id]{
  scroll-margin-top:100px}

.document-table{
  max-width:100%;
  overflow-x:auto;
  overscroll-behavior-inline:contain;
  margin:18px 0 22px}

.source-document .document-table table{
  width:auto;
  max-width:none;
  table-layout:auto;
  margin:0;
  font-size:14px;
  line-height:1.75}

.source-document .document-table th,.source-document .document-table td{
  min-width:8ch;
  max-width:46ch;
  overflow-wrap:break-word}

.js[data-view=baseline] .paper,.js[data-view=latest] .paper,body:not(.js) .paper{
  max-height:none;
  overflow:visible;
  scrollbar-gutter:auto}

.js[data-view=baseline] .paper-header,.js[data-view=latest] .paper-header,body:not(.js) .paper-header{
  position:static}

.js[data-view=baseline] .source-document [id],.js[data-view=latest] .source-document [id]{
  scroll-margin-top:20px}

@media(max-width:760px){
.case-tab{
  min-height:64px;
  padding:10px 11px}

.case-tab[aria-selected=true]{
  padding:9px 10px}

.tab-sub{
  font-size:11px}

.document-toc{
  padding:0 18px}

.document-toc ol{
  columns:1}

.source-document .document-table table{
  font-size:14px;
  table-layout:auto}

.source-document [id]{
  scroll-margin-top:20px}

}

@media print{
.document-toc{
  display:none}

.document-table{
  overflow:visible}

.source-document .document-table table{
  width:100%;
  font-size:9pt}

}
`;

const escapeHtml = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const number = value => Number(value).toLocaleString('ko-KR');
const repoLink = (relative, isTree = false) => (isTree ? TREE_ROOT : BLOB_ROOT) + relative.split('/').map(encodeURIComponent).join('/');
const jsonForHtml = value => JSON.stringify(value).replace(/</g, '\\u003c').replace(/>/g, '\\u003e').replace(/&/g, '\\u0026').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029');

function safeHref(href, sourcePath = '') {
  const value = String(href || '').trim();
  if (/^(https?:|mailto:|#)/i.test(value)) return value;
  if (/^[a-z][a-z0-9+.-]*:/i.test(value) || value.startsWith('//')) return null;
  const relative = path.posix.normalize(path.posix.join(path.posix.dirname(sourcePath || 'README.md'), value));
  if (relative.startsWith('../')) return null;
  return repoLink(relative);
}

/** Render Markdown at build time. No Markdown runtime or remote resources enter the HTML. */
export function renderMarkdown(raw, prefix = 'document', sourcePath = '', { headings = [] } = {}) {
  const definitions = new Map();
  const referenceOrder = [];
  const slugCounts = new Map();
  const slug = value => {
    const base = value.toLowerCase().replace(/<[^>]*>/g, '').replace(/[^\p{L}\p{N}_-]+/gu, '-').replace(/^-|-$/g, '') || 'section';
    const count = (slugCounts.get(base) || 0) + 1;
    slugCounts.set(base, count);
    return prefix + '-' + base + (count > 1 ? '-' + count : '');
  };
  const markdown = new Marked({
    gfm: true,
    breaks: false,
    renderer: {
      html(token) { return escapeHtml(token.text); },
      heading(token) {
        const text = token.tokens.map(function plain(part) {
          return part.tokens ? part.tokens.map(plain).join('') : part.text || part.raw || '';
        }).join('');
        const id = slug(text);
        headings.push({ id, depth: token.depth, text });
        return '<h' + token.depth + ' id="' + escapeHtml(id) + '" tabindex="-1">' + this.parser.parseInline(token.tokens) + '</h' + token.depth + '>\n';
      },
      table(token) {
        const renderer = new Renderer();
        renderer.parser = this.parser;
        return '<div class="document-table" role="region" tabindex="0" aria-label="가로로 스크롤할 수 있는 표">' + renderer.table(token) + '</div>\n';
      },
      link(token) {
        let href = safeHref(token.href, sourcePath);
        if (href && href.startsWith('#')) href = '#' + prefix + '-' + href.slice(1);
        const label = this.parser.parseInline(token.tokens);
        if (!href) return label;
        return '<a href="' + escapeHtml(href) + '"' + (token.title ? ' title="' + escapeHtml(token.title) + '"' : '') + '>' + label + '</a>';
      },
      image(token) {
        const href = safeHref(token.href, sourcePath);
        const label = '이미지: ' + (token.text || token.href || '');
        return href ? '<a href="' + escapeHtml(href) + '">' + escapeHtml(label) + '</a>' : escapeHtml(label);
      }
    },
    extensions: [
      {
        name: 'footnoteDefinition',
        level: 'block',
        start(source) { return source.match(/^ {0,3}\[\^[^\]\n]+\]:/m)?.index; },
        tokenizer(source) {
          const first = /^ {0,3}\[\^([^\]\n]+)\]:[ \t]*([^\n]*)(?:\n|$)/.exec(source);
          if (!first) return;
          let consumed = first[0].length;
          let text = first[2];
          let remaining = source.slice(consumed);
          while (remaining) {
            const continued = /^(?:(?: {4}|\t)([^\n]*)(?:\n|$)|\n(?=(?: {4}|\t)))/.exec(remaining);
            if (!continued) break;
            text += '\n' + (continued[1] || '');
            consumed += continued[0].length;
            remaining = source.slice(consumed);
          }
          const label = first[1].trim().toLowerCase();
          if (!definitions.has(label)) definitions.set(label, { label, text, references: [] });
          return { type: 'footnoteDefinition', raw: source.slice(0, consumed) };
        },
        renderer() { return ''; }
      },
      {
        name: 'footnoteReference',
        level: 'inline',
        start(source) { return source.indexOf('[^'); },
        tokenizer(source) {
          const match = /^\[\^([^\]\n]+)\]/.exec(source);
          if (match) return { type: 'footnoteReference', raw: match[0], label: match[1].trim().toLowerCase() };
        },
        renderer(token) {
          const note = definitions.get(token.label);
          if (!note) return escapeHtml(token.raw);
          if (!note.number) { note.number = referenceOrder.length + 1; referenceOrder.push(note); }
          const referenceId = prefix + '-fnref-' + note.number + '-' + (note.references.length + 1);
          note.references.push(referenceId);
          return '<sup class="footnote-ref"><a id="' + escapeHtml(referenceId) + '" href="#' + escapeHtml(prefix + '-fn-' + note.number) + '" role="doc-noteref" aria-label="각주 ' + note.number + '">' + note.number + '</a></sup>';
        }
      }
    ]
  });
  let html = markdown.parse(raw);
  for (const note of definitions.values()) {
    if (!note.number) { note.number = referenceOrder.length + 1; referenceOrder.push(note); }
  }
  if (referenceOrder.length) {
    const notes = referenceOrder.map(note => {
      const content = markdown.parse(note.text);
      const backlinks = note.references.map((referenceId, index) => '<a href="#' + escapeHtml(referenceId) + '" aria-label="각주 ' + note.number + '의 본문 참조 ' + (index + 1) + '로 돌아가기">본문으로 ↩' + (note.references.length > 1 ? ' ' + (index + 1) : '') + '</a>').join(' ');
      return '<li id="' + escapeHtml(prefix + '-fn-' + note.number) + '" tabindex="-1">' + content + (backlinks ? '<p class="footnote-backlinks">' + backlinks + '</p>' : '') + '</li>';
    }).join('\n');
    html += '<section class="footnotes" role="doc-endnotes" aria-label="각주"><h2>각주</h2><ol>' + notes + '</ol></section>\n';
  }
  return html;
}

function conditionsFor(entry) { return CONDITIONS.filter(condition => entry.documents[condition]); }
function conditionLabel(entry, condition) {
  return condition === 'baseline' ? '스킬 미적용 참고 원문' : condition === 'previous' ? '이전 문서 · ' + entry.previousLabel : '현재 문서 · v' + entry.latestVersion;
}
function renderStructured(value, prefix) {
  if (value == null) return '';
  if (typeof value === 'string') return renderMarkdown(value, prefix);
  if (Array.isArray(value)) return '<ul>' + value.map((item, i) => '<li>' + renderStructured(item, prefix + '-' + i) + '</li>').join('') + '</ul>';
  if (typeof value === 'object') {
    const labels = {summary:'요약',finding:'검토 내용',text:'내용',note:'설명',evidence:'근거',baseline:'미적용',previous:'이전',latest:'현재',status:'상태',severity:'중요도',source:'자료',label:'항목',condition:'조건',quote:'인용',location:'위치',details:'상세',preserved:'보존한 조건',concerns:'추가 확인 범위'};
    return '<dl class="finding-list">' + Object.entries(value).map(([key,item],i) => '<dt>' + escapeHtml(labels[key] || key) + '</dt><dd>' + renderStructured(item,prefix + '-' + i) + '</dd>').join('') + '</dl>';
  }
  return '<p>' + escapeHtml(value) + '</p>';
}
function observationHtml(entry) {
  const observation = entry.observations;
  const parts = ['<div class="observation-summary">' + renderStructured(observation.summary,entry.id + '-summary') + '</div>'];
  const cards = [];
  if (observation.strengths.length) cards.push('<section class="observation"><h3>수정하고 확인한 내용</h3>' + renderStructured(observation.strengths,entry.id + '-strengths') + '</section>');
  if (observation.limitations.length) cards.push('<section class="observation"><h3>추가 확인 범위</h3>' + renderStructured(observation.limitations,entry.id + '-limitations') + '</section>');
  if (cards.length) parts.push('<div class="observations">' + cards.join('') + '</div>');
  if (observation.factual_findings && (!Array.isArray(observation.factual_findings) || observation.factual_findings.length)) {
    parts.push('<details class="record"><summary>사실·조건 검토</summary><div class="observation-details">' + renderStructured(observation.factual_findings,entry.id + '-facts') + '<p><a href="' + repoLink(entry.reviewReport) + '">보존 검토 기록</a></p></div></details>');
  }
  const changedExcerpts = entry.changed ? observation.excerpts.filter(excerpt => excerpt.previous !== excerpt.latest) : [];
  if (changedExcerpts.length) {
    const excerpts = changedExcerpts.map((excerpt,i) => {
      const prefix = entry.id + '-excerpt-' + i;
      return '<section class="excerpt"><h4>' + escapeHtml(excerpt.label || '실제 수정 문장 ' + (i+1)) + '</h4><div class="excerpt-grid"><div><p class="eyebrow">이전 문서 · ' + escapeHtml(entry.previousLabel) + '</p><blockquote>' + renderMarkdown(excerpt.previous,prefix + '-previous') + '</blockquote></div><div><p class="eyebrow applied-text">현재 문서 · v' + escapeHtml(entry.latestVersion) + '</p><blockquote>' + renderMarkdown(excerpt.latest,prefix + '-latest') + '</blockquote></div></div>' + (excerpt.note ? '<div class="excerpt-note">' + renderStructured(excerpt.note,prefix + '-note') + '</div>' : '') + '</section>';
    }).join('');
    parts.push('<details class="excerpts"><summary>실제 수정 문장 확인하기 <span>' + changedExcerpts.length + '곳 · 이전과 현재</span></summary>' + excerpts + '</details>');
  }
  return parts.join('\n');
}
function documentHtml(entry,condition) {
  const doc = entry.documents[condition];
  const label = conditionLabel(entry,condition);
  // Include the comparison version so links cannot silently target another release.
  const id = entry.id + '-v' + entry.latestVersion.replace(/\./g, '-') + '-' + condition;
  const headings = [];
  const body = renderMarkdown(doc.raw,id,doc.path,{headings});
  const sections = headings.filter(heading => heading.depth === 2 || heading.depth === 3);
  const toc = sections.length >= 4 ? '<nav class="document-toc" aria-label="' + escapeHtml(entry.title + ' ' + label + ' 목차') + '"><details open><summary>이 문서 목차 <span>' + sections.length + '개 절</span></summary><ol>' + sections.map(heading => '<li class="toc-depth-' + heading.depth + '"><a href="#' + escapeHtml(heading.id) + '">' + escapeHtml(heading.text) + '</a></li>').join('') + '</ol></details></nav>' : '';
  return [
    '<article class="paper ' + condition + (condition === 'latest' ? ' revised' : '') + '" aria-labelledby="heading-' + id + '" tabindex="0" data-document="' + condition + '">',
    '<header class="paper-header"><div><h3 id="heading-' + id + '">' + escapeHtml(label) + '</h3><p class="document-meta"><span>' + number(doc.characters) + '자</span><span>·</span><span>' + (condition === 'latest' ? (entry.changed ? '이번 버전 수정본' : '이전 원문 유지') : '보존한 이전 원문') + '</span></p></div><button type="button" class="download" data-case="' + entry.id + '" data-source="' + condition + '" aria-label="' + escapeHtml(entry.title + ' ' + label + ' Markdown 원문 저장') + '">원문 저장 <span aria-hidden="true">↓</span></button></header>',
    toc,
    '<div class="source-document">' + body + '</div>',
    '<footer class="paper-footer"><p><a href="' + repoLink(doc.path) + '">저장소 원문 보기</a>' + (condition === 'latest' ? ' · <a href="' + repoLink(entry.examplePath) + '">완성 예제로 읽기</a>' : '') + ' · UTF-8 ' + number(doc.bytes) + '바이트</p><p class="path">' + escapeHtml(doc.path) + '</p><p>SHA-256 <code>' + doc.sha256 + '</code></p></footer></article>'
  ].join('\n');
}
function caseHtml(entry,i,total) {
  const rows = [['공통 원자료·요청',entry.input],...conditionsFor(entry).map(condition => [conditionLabel(entry,condition),entry.documents[condition]])].map(([label,source]) => '<tr><th scope="row">' + escapeHtml(label) + '</th><td>' + number(source.characters) + '</td><td>' + number(source.bytes) + '</td><td><a href="' + repoLink(source.path) + '">' + escapeHtml(source.path) + '</a></td></tr>').join('');
  return [
    '<section class="case-panel" id="panel-' + entry.id + '" role="tabpanel" aria-labelledby="tab-' + entry.id + '" tabindex="-1">',
    '<div class="case-heading"><div><p class="eyebrow">사례 ' + String(i+1).padStart(2,'0') + ' / ' + String(total).padStart(2,'0') + '</p><h2 id="heading-' + entry.id + '">' + escapeHtml(entry.title) + '</h2><p class="comparison-description"><a href="' + repoLink(entry.examplePath) + '">현재 문서 바로 읽기</a> · <a href="' + repoLink(entry.reviewReport) + '">보존 검토 기록</a></p></div><button class="input-download" type="button" data-case="' + entry.id + '" data-source="input" aria-label="' + escapeHtml(entry.title + ' 공통 입력 저장') + '">공통 입력 저장 ↓</button></div>',
    observationHtml(entry),
    '<details class="record input-record"><summary>공통 원자료·요청 읽기 <span>' + number(entry.input.characters) + '자</span></summary><div class="input-body"><pre class="raw-input" tabindex="0" aria-label="' + escapeHtml(entry.title + ' 공통 입력 원문') + '">' + escapeHtml(entry.input.raw) + '</pre><p class="small"><a href="' + repoLink(entry.input.path) + '">입력 원문</a> · <a href="' + repoLink(entry.sourcePath) + '">문서용 원자료</a></p></div></details>',
    '<div class="reader-intro"><h3>전체 문서 읽기</h3><p data-reader-description="' + entry.id + '">이전 문서 ' + escapeHtml(entry.previousLabel) + ' ↔ 현재 문서 v' + escapeHtml(entry.latestVersion) + ' · 각 본문을 독립적으로 스크롤합니다.</p></div>',
    '<div class="reader">' + conditionsFor(entry).map(condition => documentHtml(entry,condition)).join('\n') + '</div>',
    '<details class="record"><summary>이 사례의 원문과 문자 수</summary><div class="table-wrap"><table><caption>공백·개행·Markdown 문법을 포함한 Unicode 코드 포인트 수입니다.</caption><thead><tr><th scope="col">조건</th><th scope="col">문자 수</th><th scope="col">바이트 수</th><th scope="col">원문 경로</th></tr></thead><tbody>' + rows + '</tbody></table></div></details>',
    '</section>'
  ].join('\n');
}
function viewerRuntime() {
  'use strict';
  const data = JSON.parse(document.getElementById('comparison-data').textContent);
  const tabs = Array.from(document.querySelectorAll('[data-case-tab]'));
  const panels = Array.from(document.querySelectorAll('.case-panel'));
  const status = document.getElementById('status');
  const comparisonMode = document.getElementById('comparison-mode');
  const viewMode = document.getElementById('view-mode');
  const baselineOption = Array.from(comparisonMode.options).find(option => option.value === 'baseline');
  const previousOption = Array.from(comparisonMode.options).find(option => option.value === 'previous');
  let selected = data.cases[0];
  function effectiveComparison(entry) { return comparisonMode.value === 'baseline' && entry.documents.baseline ? 'baseline' : 'previous'; }
  function comparisonLabel(entry) { return effectiveComparison(entry) === 'previous' ? '이전 문서 ' + entry.previousLabel : '스킬 미적용'; }
  function updateDescriptions(announce = true) {
    baselineOption.disabled = !selected.documents.baseline;
    comparisonMode.value = effectiveComparison(selected);
    document.body.dataset.comparison = comparisonMode.value;
    document.body.dataset.view = viewMode.value;
    const left = comparisonLabel(selected);
    const current = '현재 문서 v' + data.skillVersion;
    previousOption.textContent = '이전 문서 ' + selected.previousLabel + ' ↔ ' + current;
    baselineOption.textContent = selected.documents.baseline ? '미적용 참고 원문 ↔ ' + current : '미적용 참고 원문 없음';
    viewMode.options[1].textContent = left + '만';
    data.cases.forEach(entry => {
      const label = viewMode.value === 'latest' ? current : comparisonLabel(entry);
      document.querySelector('[data-reader-description="' + entry.id + '"]').textContent = viewMode.value === 'both'
        ? comparisonLabel(entry) + ' ↔ ' + current + ' · 넓은 화면에서는 각 본문을 독립적으로 스크롤합니다.'
        : label + ' 단독 읽기 · 페이지를 스크롤해 끝까지 읽습니다.';
    });
    if (announce) status.textContent = selected.title + ': ' + (viewMode.value === 'both' ? left + '과 ' + current + ', 나란히 보기' : viewMode.selectedOptions[0].textContent + ' 단독 읽기') + '입니다.';
  }
  function selectCase(id,focus = false,updateHash = true) {
    selected = data.cases.find(item => item.id === id) || data.cases[0];
    tabs.forEach(tab => {
      const active = tab.dataset.caseTab === selected.id;
      tab.setAttribute('aria-selected',String(active));
      tab.tabIndex = active ? 0 : -1;
      if (active && focus) tab.focus();
    });
    panels.forEach(panel => { panel.hidden = panel.id !== 'panel-' + selected.id; });
    updateDescriptions();
    if (updateHash) { try { history.replaceState(null,'','#' + selected.id); } catch {} }
  }
  tabs.forEach((tab,i) => {
    tab.addEventListener('click',() => selectCase(tab.dataset.caseTab));
    tab.addEventListener('keydown',event => {
      let next = null;
      if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (i+1) % tabs.length;
      if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (i-1+tabs.length) % tabs.length;
      if (event.key === 'Home') next = 0;
      if (event.key === 'End') next = tabs.length-1;
      if (next !== null) { event.preventDefault(); selectCase(tabs[next].dataset.caseTab,true); }
    });
  });
  comparisonMode.addEventListener('change',() => updateDescriptions());
  viewMode.addEventListener('change',() => updateDescriptions());
  document.querySelectorAll('[data-source]').forEach(button => button.addEventListener('click',() => {
    const entry = data.cases.find(item => item.id === button.dataset.case);
    const key = button.dataset.source;
    const source = key === 'input' ? entry.input : entry.documents[key];
    const prefix = key === 'previous' ? entry.previousLabel : key === 'latest' ? 'v' + entry.latestVersion + '-revised' : key;
    const filename = prefix + '-' + entry.file;
    const bytes = Uint8Array.from(atob(source.bytesBase64),character => character.charCodeAt(0));
    const url = URL.createObjectURL(new Blob([bytes],{type:'text/markdown;charset=utf-8'}));
    const anchor = document.createElement('a');
    anchor.href = url; anchor.download = filename; document.body.append(anchor); anchor.click(); anchor.remove();
    setTimeout(() => URL.revokeObjectURL(url),10000);
    status.textContent = filename + ' 원문 저장을 요청했습니다.';
  }));
  function selectedHash() { try { return decodeURIComponent(location.hash.slice(1)); } catch { return ''; } }
  function caseIdForHash(hash) {
    if (data.cases.some(entry => entry.id === hash)) return hash;
    const panel = document.getElementById(hash)?.closest('.case-panel');
    return data.cases.find(entry => 'panel-' + entry.id === panel?.id)?.id;
  }
  function selectHash(hash) {
    const id = caseIdForHash(hash);
    if (!id) return false;
    const condition = document.getElementById(hash)?.closest('[data-document]')?.dataset.document;
    if (condition === 'baseline' || condition === 'previous') {
      comparisonMode.value = condition;
      if (viewMode.value === 'latest') viewMode.value = 'both';
    } else if (condition === 'latest' && viewMode.value === 'baseline') viewMode.value = 'both';
    selectCase(id,false,false);
    // A fragment may have belonged to a hidden panel when native navigation ran.
    // Reveal the case/condition first, then place its heading below the paper header.
    const target = document.getElementById(hash);
    if (target) requestAnimationFrame(() => {
      target.scrollIntoView({block:'start',behavior:'instant'});
      target.focus({preventScroll:true});
    });
    return true;
  }
  window.addEventListener('hashchange',() => selectHash(selectedHash()));
  document.body.classList.add('js');
  if (!selectHash(selectedHash())) selectCase(data.cases[0].id,false,false);
}
const clientScript = '(' + viewerRuntime.toString() + ')();';

export function buildViewer(repo = DEFAULT_REPO,{run = DEFAULT_RUN, check = false, output} = {}) {
  repo = path.resolve(repo);
  if (typeof run !== 'string' || !run || path.isAbsolute(run) || run.includes('\\')) throw new Error('--run must be a repository-relative run directory.');
  const RUN_PATH = path.posix.normalize(run).replace(/\/$/, '');
  const sourceFiles = new Map();
  function readSource(relative) {
    if (!relative || typeof relative !== 'string' || path.isAbsolute(relative) || path.posix.normalize(relative).startsWith('../')) throw new Error('Invalid repository source path: ' + relative);
    const absolute = path.resolve(repo,relative);
    if (!absolute.startsWith(path.resolve(repo) + path.sep)) throw new Error('Source is outside repository: ' + relative);
    let bytes;
    try { bytes = fs.readFileSync(absolute); } catch(error) { if (error.code === 'ENOENT') throw new Error('Missing required source; HTML was not changed: ' + relative); throw error; }
    const raw = bytes.toString('utf8');
    if (!Buffer.from(raw,'utf8').equals(bytes)) throw new Error('Source is not valid UTF-8: ' + relative);
    const hash = sha256(bytes);
    sourceFiles.set(relative,{path:relative,sha256:hash});
    return {path:relative,raw,sha256:hash,characters:[...raw].length,bytes:bytes.length,bytesBase64:bytes.toString('base64')};
  }
  const manifestPath = RUN_PATH + '/manifest.json';
  const manifest = JSON.parse(readSource(manifestPath).raw);
  if (manifest.run_id !== path.posix.basename(RUN_PATH)) throw new Error('Run directory and manifest run_id differ.');
  const SKILL_VERSION = manifest.skill_version;
  if (!/^\d+\.\d+\.\d+$/.test(SKILL_VERSION)) throw new Error('Manifest must declare a semantic skill_version.');
  const manifestCases = [...(manifest.cases || []),...(manifest.transfer_cases || [])];
  if (!manifestCases.length) throw new Error('Manifest must contain comparison cases.');
  const previousLabels = new Set(manifestCases.map(item => item.previous_label));
  const PREVIOUS_LABEL = manifest.previous_version ? 'v' + manifest.previous_version : manifestCases[0].previous_label;
  if (previousLabels.size !== 1 || !/^v\d+\.\d+\.\d+$/.test(PREVIOUS_LABEL) || !previousLabels.has(PREVIOUS_LABEL)) throw new Error('Comparison cases and previous_version must agree.');
  const date = manifest.date || manifest.run_id.slice(0,10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(date)) throw new Error('Manifest date must be YYYY-MM-DD.');
  const reportPath = manifest.report_path || 'docs/repairs-v' + SKILL_VERSION + '.md';
  if (manifest.skill_snapshot_path !== RUN_PATH + '/snapshots/v' + SKILL_VERSION) throw new Error('Unexpected skill snapshot path.');
  const expectedSnapshotFiles = ['LICENSE','SKILL.md','agents/openai.yaml','references/before-after-guide.md','references/document-types.md','references/reading-flow.md'];
  if (JSON.stringify(Object.keys(manifest.skill_files || {}).sort()) !== JSON.stringify(expectedSnapshotFiles.sort())) throw new Error('Expected the six named frozen skill files.');
  for (const [relative,expected] of Object.entries(manifest.skill_files)) {
    const snapshot = readSource(manifest.skill_snapshot_path + '/' + relative);
    if (snapshot.sha256 !== expected) throw new Error('Frozen skill snapshot SHA-256 mismatch: ' + snapshot.path);
  }
  const hashes = {};
  for (const name of ['frozen_files','artifact_hashes']) {
    const values = manifest[name] || {};
    if (!values || typeof values !== 'object' || Array.isArray(values)) throw new Error(name + ' must be a path-to-SHA-256 object.');
    for (const [relative,digest] of Object.entries(values)) {
      if (hashes[relative] && hashes[relative] !== digest) throw new Error('Conflicting recorded SHA-256: ' + relative);
      hashes[relative] = digest;
    }
  }
  const observationPath = RUN_PATH + '/observations.json';
  const observationData = JSON.parse(readSource(observationPath).raw);
  if (!observationData.cases || typeof observationData.cases !== 'object' || Array.isArray(observationData.cases)) throw new Error('observations.json must contain a cases object.');
  const seen = new Set();
  const seenFiles = new Set();
  const cases = manifestCases.map(item => {
    for (const required of ['id','title','file','source','input','previous','latest','previous_label']) {
      if (typeof item[required] !== 'string' || !item[required]) throw new Error('Missing string field ' + required + ': ' + item.id);
    }
    if (!/^[a-zA-Z0-9_-]+$/.test(item.id) || seen.has(item.id)) throw new Error('Invalid or duplicate case id: ' + item.id);
    seen.add(item.id);
    if (path.posix.basename(item.file) !== item.file || !item.file.endsWith('.md') || seenFiles.has(item.file)) throw new Error('Invalid or duplicate example filename: ' + item.file);
    seenFiles.add(item.file);
    if (item.previous_label !== PREVIOUS_LABEL) throw new Error('Expected previous_label=' + PREVIOUS_LABEL + ': ' + item.id);
    if (!item.latest.startsWith(RUN_PATH + '/outputs/revised/')) throw new Error('Latest must be a final outputs/revised document: ' + item.id);
    if (!hashes[item.latest]) throw new Error('Final document has no recorded SHA-256: ' + item.latest);
    const observation = observationData.cases[item.id];
    if (!observation || typeof observation !== 'object' || Array.isArray(observation) || typeof observation.summary !== 'string' || !observation.summary.trim()) throw new Error('Missing observations summary: ' + item.id);
    for (const field of ['strengths','limitations','excerpts']) if (!Array.isArray(observation[field])) throw new Error('Expected observations.' + field + ' array: ' + item.id);
    if (!Object.hasOwn(observation,'factual_findings')) throw new Error('Missing factual_findings: ' + item.id);
    const input = readSource(item.input);
    const documents = Object.fromEntries(CONDITIONS.filter(condition => item[condition]).map(condition => [condition,readSource(item[condition])]));
    const factualSource = readSource(item.source);
    for (const source of [input,factualSource,...Object.values(documents)]) if (hashes[source.path] && hashes[source.path] !== source.sha256) throw new Error('Recorded source SHA-256 mismatch: ' + source.path);
    if (item.review_report) readSource(item.review_report);
    for (const [index,excerpt] of observation.excerpts.entries()) for (const condition of ['previous','latest']) {
      if (typeof excerpt[condition] !== 'string' || !excerpt[condition] || !documents[condition].raw.includes(excerpt[condition])) throw new Error('Excerpt is not an exact substring: ' + item.id + '/' + condition + '/' + index);
    }
    return {id:item.id,title:item.title,file:item.file,changed:documents.previous.sha256 !== documents.latest.sha256,revisionKind:item.revision_kind || null,previousLabel:item.previous_label,latestVersion:manifest.skill_version,sourcePath:item.source,input,documents,observations:observation,reviewReport:item.review_report || reportPath,examplePath:item.example || 'docs/examples/' + item.file};
  });
  if (Object.keys(observationData.cases).length !== cases.length || Object.keys(observationData.cases).some(id => !seen.has(id))) throw new Error('Observation case ids must match manifest cases exactly.');
  for (const source of sourceFiles.values()) {
    if (hashes[source.path] && hashes[source.path] !== source.sha256) throw new Error('Recorded source SHA-256 mismatch: ' + source.path);
  }
  const changedCount = cases.filter(entry => entry.changed).length;
  const retainedCount = cases.length - changedCount;
  const data = {
    changedCount,retainedCount,version:5,runId:manifest.run_id,skillVersion:manifest.skill_version,previousVersion:PREVIOUS_LABEL.slice(1),date,skillSnapshotPath:manifest.skill_snapshot_path,
    workflow:'revision-and-retention-of-' + PREVIOUS_LABEL + '-documents',defaultComparison:'previous',latestCondition:'latest',
    semanticReviewConditions:['latest'],baselineReview:'historical-reference-only',humanReaderMeasurements:false,
    revisionWorkflow:manifest.revision_workflow || null,observationsPath:observationPath,
    examplesPath:'docs/examples/README.md',repairsPath:reportPath,
    sourceFiles:[...sourceFiles.values()],cases
  };
  const documentCount = cases.reduce((total,entry) => total + conditionsFor(entry).length,0);
  const baselineCount = cases.filter(entry => entry.documents.baseline).length;
  const tabs = cases.map((entry,i) => '<button type="button" role="tab" class="case-tab" id="tab-' + entry.id + '" data-case-tab="' + entry.id + '" aria-controls="panel-' + entry.id + '" aria-selected="' + (i===0 ? 'true':'false') + '" tabindex="' + (i===0 ? '0':'-1') + '"><span><span class="tab-title">' + escapeHtml(entry.title) + '</span><span class="tab-sub">이전과 현재' + (entry.documents.baseline ? ' · 미적용 참고 원문':' · 2개 문서') + '</span></span><span class="tab-number" aria-hidden="true">' + String(i+1).padStart(2,'0') + '</span></button>').join('\n');
  const sourceList = data.sourceFiles.map(source => '<li><a href="' + repoLink(source.path) + '">' + escapeHtml(source.path) + '</a><code>SHA-256 ' + source.sha256 + '</code></li>').join('\n');
  const html = [
    '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; script-src \'unsafe-inline\'; img-src data:; connect-src \'none\'; base-uri \'none\'; form-action \'none\'; object-src \'none\'"><title>v' + SKILL_VERSION + ' 문서 비교 | Korean Dev Writing</title><style>' + css + '</style></head>',
    '<body data-view="both" data-comparison="previous"><a class="skip" href="#reader-start">문서 비교로 건너뛰기</a><header class="masthead"><div class="shell"><span class="brand">KOREAN DEV WRITING</span><span class="run-label">v' + SKILL_VERSION + ' · ' + date + '</span></div></header><main class="shell">',
    '<section class="hero"><p class="eyebrow">현재 문서 ' + cases.length + '개 · 수정 ' + changedCount + '개 · 원문 유지 ' + retainedCount + '개</p><h1>바뀐 부분과 그대로 둔 내용을<br>문서로 확인하세요</h1><p class="lead">' + PREVIOUS_LABEL + ' 문서와 v' + SKILL_VERSION + ' 현재 문서를 비교합니다. 이번 버전에서 ' + changedCount + '개를 수정했고, ' + retainedCount + '개는 이전 원문 그대로 포함했습니다. 각 사례의 수정 관찰과 보존 검토 기록을 함께 확인할 수 있습니다.</p><nav class="report-links" aria-label="완성 문서와 수정 결과"><a href="' + repoLink(data.examplesPath) + '">현재 문서 바로 읽기</a><a href="' + repoLink(data.repairsPath) + '">수정 결과 보고서</a><a href="' + repoLink('docs/evaluation.md') + '">전체 결과 요약</a><a href="#method">작성과 확인 방법</a></nav></section>',
    '<div id="reader-start" tabindex="-1"></div><section class="toolbar" aria-label="비교 문서 선택"><div class="case-tabs" role="tablist" aria-label="문서 사례">' + tabs + '</div><div class="controls"><p>기본은 이전 문서와 현재 문서의 비교입니다. 원문이 있는 ' + baselineCount + '개 사례에서는 미적용 문서를 함께 볼 수 있습니다.</p><div class="control-group"><div class="view-control"><label for="comparison-mode">비교 기준</label><select id="comparison-mode"><option value="previous" selected>이전 문서 ' + PREVIOUS_LABEL + ' ↔ 현재 문서 v' + SKILL_VERSION + '</option><option value="baseline">미적용 참고 원문 ↔ 현재 문서 v' + SKILL_VERSION + '</option></select></div><div class="view-control"><label for="view-mode">보기</label><select id="view-mode"><option value="both" selected>나란히 보기</option><option value="baseline">이전 문서 ' + PREVIOUS_LABEL + '만</option><option value="latest">현재 문서 v' + SKILL_VERSION + '만</option></select></div></div></div></section>',
    '<p class="sr-only status" id="status" role="status" aria-live="polite" aria-atomic="true"></p><noscript><div class="no-js">JavaScript가 꺼져 있어 모든 사례와 원문을 순서대로 표시합니다. 각 문서의 저장소 링크에서 원문을 확인할 수 있습니다.</div></noscript>',
    cases.map((entry,i) => caseHtml(entry,i,cases.length)).join('\n'),
    '<section class="endnotes" id="method"><details class="method"><summary>작성과 확인 방법</summary><div class="method-body"><p>' + PREVIOUS_LABEL + ' 원문과 같은 원자료를 기준으로 v' + SKILL_VERSION + ' 문서를 정리했습니다. ' + changedCount + '개는 수정했고, ' + retainedCount + '개는 이전 원문의 바이트를 그대로 유지했습니다. 이번에 확인한 범위와 이전 검토를 이어받은 범위는 사례별 관찰, 실행 manifest, 수정 결과 보고서에 기록했습니다. 수정 이력은 별도로 보존했고 완성 예제는 현재 문서의 바이트를 그대로 복사했습니다.</p><p>조건을 가린 단회 생성 비교가 아닙니다. 미적용 문서는 과거의 참고 원문입니다. 위의 수정 관찰과 발췌는 ' + PREVIOUS_LABEL + '과 v' + SKILL_VERSION + '을 비교하며, 왼쪽 문서를 바꿔도 관찰 내용은 그대로입니다.</p><p>검토 결과는 사실·조건 보존과 문서 구성에 관한 판단입니다. 실제 독자의 이해도·기억·읽는 시간·피로를 측정하지 않았습니다. 사례는 공개용 가상 자료입니다. 문자 수는 공백·개행·Markdown 문법을 포함한 Unicode 코드 포인트 수이며, 길이 자체를 품질 점수로 사용하지 않습니다.</p><p>본문 ' + documentCount + '개와 입력 ' + cases.length + '개는 HTML 안에 포함되어 인터넷 없이 읽고 내려받을 수 있습니다. 원문 저장은 UTF-8 바이트와 마지막 개행까지 보존합니다. 아래 출처 목록은 빌드할 때 실제 읽은 파일을 기록합니다.</p><p><a href="' + repoLink(manifestPath) + '">실행 manifest</a> · <a href="' + repoLink(RUN_PATH + '/protocol.md') + '">교정 절차와 수정 이력</a> · <a href="' + repoLink(observationPath) + '">수정 관찰</a> · <a href="' + repoLink('docs/evaluation-' + PREVIOUS_LABEL + '.md') + '">' + PREVIOUS_LABEL + ' 평가 보존본</a></p></div></details><details class="method"><summary>자료와 SHA-256 <span>' + data.sourceFiles.length + '개 파일</span></summary><div class="method-body"><ul class="source-files">' + sourceList + '</ul></div></details></section>',
    '<footer class="foot"><p>v' + SKILL_VERSION + ' 현재 문서 · ' + cases.length + '개 사례 · 본문 ' + documentCount + '개</p><p><a href="' + REPOSITORY + '">GitHub 저장소</a> · <a href="' + repoLink(RUN_PATH,true) + '">이번 수정 기록</a></p></footer></main>',
    '<script id="comparison-data" type="application/json">' + jsonForHtml(data) + '</script><script>' + clientScript + '</script></body></html>'
  ].join('\n');
  const destination = output ? path.resolve(repo,output) : path.join(repo,'docs/comparisons/index.html');
  const generated = Buffer.from(html,'utf8');
  if (check) {
    if (!fs.existsSync(destination)) throw new Error('Missing generated viewer: ' + destination + '. Run the builder without --check.');
    if (!fs.readFileSync(destination).equals(generated)) throw new Error('Stale generated viewer: ' + destination + '. Regenerate from ' + RUN_PATH + '.');
  } else {
    fs.mkdirSync(path.dirname(destination),{recursive:true});
    fs.writeFileSync(destination,generated);
  }
  return {destination,checkedOnly:check,cases:cases.length,documents:documentCount,inputs:cases.length,downloads:documentCount+cases.length,sourceFiles:data.sourceFiles.length,observationsIncluded:true,bytes:Buffer.byteLength(html)};
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const options = process.argv.slice(2);
  let repo = DEFAULT_REPO;
  let check = false;
  let run = DEFAULT_RUN;
  let output;
  try {
    for (let i=0;i<options.length;i++) {
      if (options[i] === '--check') check = true;
      else if (options[i] === '--repo' && options[i+1]) repo = path.resolve(options[++i]);
      else if (options[i] === '--run' && options[i+1]) run = options[++i];
      else if (options[i] === '--output' && options[i+1]) output = options[++i];
      else throw new Error('Usage: build_viewer.mjs [--repo PATH] [--run PATH] [--output PATH] [--check]');
    }
    console.log(JSON.stringify(buildViewer(repo,{run,check,output}),null,2));
  } catch(error) { console.error(error.message); process.exitCode = 1; }
}
