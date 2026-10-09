/* MediaGrab front-end */
'use strict';

/* ---------------------------------------------------------------- icons */
const ICONS = {
  search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
  list: '<path d="M12 3v12m0 0-4-4m4 4 4-4"/><path d="M5 21h14"/>',
  gear: '<circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.7 1.7 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.7 1.7 0 0 0-1.8-.3 1.7 1.7 0 0 0-1 1.5V21a2 2 0 1 1-4 0v-.1a1.7 1.7 0 0 0-1.1-1.5 1.7 1.7 0 0 0-1.8.3l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1a1.7 1.7 0 0 0 .3-1.8 1.7 1.7 0 0 0-1.5-1H3a2 2 0 1 1 0-4h.1a1.7 1.7 0 0 0 1.5-1.1 1.7 1.7 0 0 0-.3-1.8l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1a1.7 1.7 0 0 0 1.8.3H9a1.7 1.7 0 0 0 1-1.5V3a2 2 0 1 1 4 0v.1a1.7 1.7 0 0 0 1 1.5 1.7 1.7 0 0 0 1.8-.3l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.7 1.7 0 0 0-.3 1.8V9a1.7 1.7 0 0 0 1.5 1H21a2 2 0 1 1 0 4h-.1a1.7 1.7 0 0 0-1.5 1z"/>',
  moon: '<path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/>',
  sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M2 12h2M20 12h2M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
  auto: '<circle cx="12" cy="12" r="9"/><path d="M12 3a9 9 0 0 1 0 18z" fill="currentColor"/>',
  link: '<path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/>',
  paste: '<rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>',
  download: '<path d="M12 3v12m0 0-4.5-4.5M12 15l4.5-4.5"/><path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2"/>',
  video: '<rect x="2" y="5" width="15" height="14" rx="3"/><path d="m17 10 5-3v10l-5-3"/>',
  music: '<path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>',
  image: '<rect x="3" y="3" width="18" height="18" rx="3"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.5-3.5L7 22"/>',
  cc: '<rect x="2" y="5" width="20" height="14" rx="3"/><path d="M10 10.5a2.5 2.5 0 1 0 0 3M17 10.5a2.5 2.5 0 1 0 0 3"/>',
  check: '<path d="m5 12 5 5L20 7"/>',
  x: '<path d="M18 6 6 18M6 6l12 12"/>',
  pause: '<rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/>',
  play: '<path d="M7 4v16l13-8z"/>',
  retry: '<path d="M3 12a9 9 0 0 1 15.5-6.3L21 8"/><path d="M21 3v5h-5"/><path d="M21 12a9 9 0 0 1-15.5 6.3L3 16"/><path d="M3 21v-5h5"/>',
  folder: '<path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
  open: '<path d="M15 3h6v6M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
  trash: '<path d="M3 6h18M8 6V4h8v2M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>',
  eye: '<path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
  cal: '<rect x="3" y="4" width="18" height="18" rx="3"/><path d="M16 2v4M8 2v4M3 10h18"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  alert: '<path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 16v-4M12 8h.01"/>',
  zap: '<path d="M13 2 3 14h9l-1 8 10-12h-9z"/>',
  layers: '<path d="m12 2 10 5-10 5L2 7z"/><path d="m2 17 10 5 10-5M2 12l10 5 10-5"/>',
  shield: '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
  globe: '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18"/>',
  cookie: '<path d="M12 2a10 10 0 1 0 10 10 4 4 0 0 1-5-5 4 4 0 0 1-5-5z"/><path d="M8.5 8.5h.01M16 15.5h.01M12 12h.01M11 17h.01M7 14h.01"/>',
  sparkles: '<path d="M12 3l1.8 4.7L18.5 9.5l-4.7 1.8L12 16l-1.8-4.7L5.5 9.5l4.7-1.8z"/><path d="M19 15l.9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9z"/>',
  scissors: '<circle cx="6" cy="6" r="3"/><circle cx="6" cy="18" r="3"/><path d="M20 4 8.1 15.9M14.5 14.5 20 20M8.1 8.1 12 12"/>',
  infinity: '<path d="M12 12c-2-2.7-4-4-6-4a4 4 0 0 0 0 8c2 0 4-1.3 6-4zm0 0c2 2.7 4 4 6 4a4 4 0 0 0 0-8c-2 0-4 1.3-6 4z"/>',
  batch: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
  refresh: '<path d="M21 12a9 9 0 1 1-3-6.7L21 8"/><path d="M21 3v5h-5"/>',
  cpu: '<rect x="5" y="5" width="14" height="14" rx="2"/><path d="M9 9h6v6H9zM9 1v4M15 1v4M9 19v4M15 19v4M1 9h4M1 15h4M19 9h4M19 15h4"/>',
};
const icon = (name) => `<i data-i="${name}">${ICONS[name] ? `<svg viewBox="0 0 24 24">${ICONS[name]}</svg>` : ''}</i>`;
function hydrateIcons(root = document) {
  root.querySelectorAll('i[data-i]:empty').forEach((el) => { const n = el.dataset.i; if (ICONS[n]) el.innerHTML = `<svg viewBox="0 0 24 24">${ICONS[n]}</svg>`; });
}

/* ---------------------------------------------------------------- helpers */
const $ = (s, r = document) => r.querySelector(s);
function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === 'class') el.className = v;
    else if (k === 'html') el.innerHTML = v;
    else if (k.startsWith('on')) el.addEventListener(k.slice(2), v);
    else if (k === 'style' && typeof v === 'object') Object.assign(el.style, v);
    else el.setAttribute(k, v === true ? '' : v);
  }
  for (const kid of kids.flat(9)) {
    if (kid == null || kid === false) continue;
    el.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
  }
  return el;
}
const I = (name) => h('i', { 'data-i': name, html: ICONS[name] ? `<svg viewBox="0 0 24 24">${ICONS[name]}</svg>` : '' });

async function api(path, opts = {}) {
  const o = { method: opts.method || (opts.body !== undefined ? 'POST' : 'GET'), headers: {} };
  if (opts.body instanceof FormData) o.body = opts.body;
  else if (opts.body !== undefined) { o.body = JSON.stringify(opts.body); o.headers['Content-Type'] = 'application/json'; }
  let r;
  try { r = await fetch(path, o); } catch (e) { throw new Error('MediaGrab isn’t responding. Is the app still running?'); }
  let data = {};
  try { data = await r.json(); } catch (e) { /* not json */ }
  if (!r.ok || data.ok === false) throw new Error(data.error || `Request failed (${r.status})`);
  return data;
}

const fmt = {
  bytes(n) {
    if (n == null || !isFinite(n) || n <= 0) return '';
    const u = ['B', 'KB', 'MB', 'GB', 'TB']; let i = 0;
    while (n >= 1024 && i < u.length - 1) { n /= 1024; i++; }
    return `${n >= 100 || i === 0 ? Math.round(n) : n.toFixed(1)} ${u[i]}`;
  },
  dur(s) {
    if (s == null || !isFinite(s)) return '';
    s = Math.round(s); const hh = Math.floor(s / 3600), mm = Math.floor(s % 3600 / 60), ss = s % 60;
    return hh ? `${hh}:${String(mm).padStart(2, '0')}:${String(ss).padStart(2, '0')}` : `${mm}:${String(ss).padStart(2, '0')}`;
  },
  eta(s) {
    if (s == null || !isFinite(s)) return '';
    if (s < 60) return `${Math.max(1, Math.round(s))}s left`;
    if (s < 3600) return `${Math.round(s / 60)} min left`;
    return `${Math.floor(s / 3600)}h ${Math.round(s % 3600 / 60)}m left`;
  },
  num(n) {
    if (n == null) return '';
    if (n >= 1e9) return (n / 1e9).toFixed(1).replace(/\.0$/, '') + 'B';
    if (n >= 1e6) return (n / 1e6).toFixed(1).replace(/\.0$/, '') + 'M';
    if (n >= 1e3) return (n / 1e3).toFixed(1).replace(/\.0$/, '') + 'K';
    return String(n);
  },
  date(d) {
    if (!d || d.length !== 8) return '';
    const dt = new Date(+d.slice(0, 4), +d.slice(4, 6) - 1, +d.slice(6, 8));
    return dt.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
  },
  ago(t) {
    if (!t) return '';
    const s = Date.now() / 1000 - t;
    if (s < 60) return 'just now';
    if (s < 3600) return `${Math.round(s / 60)} min ago`;
    if (s < 86400) return `${Math.round(s / 3600)} h ago`;
    return new Date(t * 1000).toLocaleDateString();
  },
};
const thumbUrl = (u) => (u ? `/api/thumb?u=${encodeURIComponent(u)}` : '');
function img(src, alt = '') {
  if (!src) return h('div', { class: 'ph' }, I('image'));
  const el = h('img', { src: thumbUrl(src), alt, loading: 'lazy', decoding: 'async' });
  el.onerror = () => el.replaceWith(h('div', { class: 'ph' }, I('image')));
  return el;
}
function parseTime(v) {
  v = String(v || '').trim();
  if (!v) return null;
  if (/^\d+(\.\d+)?$/.test(v)) return parseFloat(v);
  const p = v.split(':').map(Number);
  if (p.some(isNaN)) return NaN;
  return p.reduce((a, b) => a * 60 + b, 0);
}

function toast(msg, opts = {}) {
  const t = h('div', { class: 'toast' + (opts.error ? ' err' : '') }, I(opts.error ? 'alert' : 'check'), h('div', { class: 't' }, msg),
    opts.action ? h('button', { onclick: () => { opts.action.fn(); close(); } }, opts.action.label) : null);
  $('#toasts').append(t);
  const close = () => { t.classList.add('out'); setTimeout(() => t.remove(), 260); };
  setTimeout(close, opts.ms || (opts.error ? 6000 : 3800));
}

/* ---------------------------------------------------------------- state */
const APP = { settings: {}, tools: {}, version: '', result: null, analyzing: false, error: null, sel: null, jobs: [], filter: 'all', batch: false, lastUrl: '' };
const SITES = [['YouTube', '#ff0033'], ['TikTok', '#25f4ee'], ['Instagram', '#e1306c'], ['X / Twitter', '#8899a6'], ['Facebook', '#1877f2'], ['Vimeo', '#1ab7ea'], ['Reddit', '#ff4500'], ['Twitch', '#9146ff'], ['SoundCloud', '#ff5500'], ['Pinterest', '#e60023'], ['Dailymotion', '#0a6cf5'], ['+1800 more', '#a64dff']];
const QUALITY_PRESETS = [['best', 'Best available'], ['2160', '4K (2160p)'], ['1440', '1440p'], ['1080', '1080p'], ['720', '720p'], ['480', '480p'], ['360', '360p'], ['audio', 'Audio only (MP3)']];

/* ---------------------------------------------------------------- navigation */
function go(view) {
  document.querySelectorAll('.view').forEach((v) => v.classList.toggle('active', v.id === 'view-' + view));
  document.querySelectorAll('#nav button').forEach((b) => b.classList.toggle('active', b.dataset.go === view));
  APP.view = view;
  if (view === 'queue') renderQueue(true);
  if (view === 'settings') renderSettings();
  if (view === 'download') setTimeout(() => $('#url')?.focus(), 30);
  try { sessionStorage.setItem('mg-view', view); } catch (e) { /* ignore */ }
  window.scrollTo({ top: 0 });
}
document.addEventListener('click', (e) => { const g = e.target.closest('[data-go]'); if (g) go(g.dataset.go); });

/* theme */
function applyTheme(t) {
  if (t === 'auto') delete document.documentElement.dataset.theme; else document.documentElement.dataset.theme = t;
  try { localStorage.setItem('mg-theme', t); } catch (e) { /* ignore */ }
  $('#themeBtn').innerHTML = icon(t === 'dark' ? 'moon' : t === 'light' ? 'sun' : 'auto');
  $('#themeBtn').title = `Theme: ${t}`;
}
$('#themeBtn').onclick = () => {
  let cur = 'auto'; try { cur = localStorage.getItem('mg-theme') || 'auto'; } catch (e) { /* ignore */ }
  applyTheme({ auto: 'dark', dark: 'light', light: 'auto' }[cur]);
};

/* ---------------------------------------------------------------- download view */
function renderDownloadShell() {
  const v = $('#view-download');
  v.innerHTML = '';
  const input = h('input', { id: 'url', type: 'text', placeholder: 'Paste a link from YouTube, TikTok, Instagram, X…', autocomplete: 'off', spellcheck: 'false',
    onkeydown: (e) => { if (e.key === 'Enter') analyze(); } });
  const single = h('div', { class: 'omnibox', id: 'omni' },
    h('span', { class: 'lead' }, I('link')), input,
    h('button', { class: 'btn ghost', title: 'Paste from clipboard', onclick: pasteAndGo }, I('paste'), h('span', { class: 'hide-sm' }, 'Paste')),
    h('button', { class: 'btn primary', id: 'goBtn', onclick: () => analyze() }, I('search'), 'Analyze'));
  const ta = h('textarea', { id: 'batchText', placeholder: 'Paste many links — one per line (videos, playlists, posts…)', spellcheck: 'false', oninput: updateBatchCount });
  const qsel = h('select', { class: 'input', id: 'batchQ' }, QUALITY_PRESETS.map(([v2, l]) => h('option', { value: v2 }, l)));
  qsel.value = APP.settings.default_quality || 'best';
  const batch = h('div', { class: 'omnibox batch', id: 'batchBox', hidden: true }, ta,
    h('div', { style: { display: 'flex', gap: '8px', width: '100%', alignItems: 'center', padding: '0 4px 4px', flexWrap: 'wrap' } },
      h('span', { class: 'opt-label' }, 'Quality'), qsel, h('span', { style: { flex: 1 } }),
      h('button', { class: 'btn primary', id: 'batchGo', onclick: batchDownload }, I('download'), h('span', { id: 'batchLbl' }, 'Add to downloads'))));
  v.append(
    h('div', { class: 'hero' },
      h('h1', {}, 'Download ', h('span', { class: 'g' }, 'anything'), ', any length.'),
      h('p', {}, 'Videos up to 8K, music, thumbnails and photos from YouTube, TikTok, Instagram, X, Facebook and 1800+ sites — saved straight to your PC.')),
    single, batch,
    h('div', { class: 'under-box' },
      h('span', {}, 'Tip: press ', h('span', { class: 'kbd' }, 'Ctrl'), ' + ', h('span', { class: 'kbd' }, 'V'), ' anywhere, or drop a link on the page'),
      h('button', { class: 'linkish', id: 'batchToggle', onclick: toggleBatch }, I('batch'), ' Many links at once')),
    h('div', { id: 'result', class: 'result' }),
    h('div', { id: 'landing' },
      h('div', { class: 'sites' }, SITES.map(([n, c]) => h('span', { class: 'site-chip' }, h('span', { class: 'dot', style: { background: c } }), n))),
      h('div', { class: 'features' },
        feat('infinity', 'Any length', 'Hours-long videos download in resumable chunks. Pause, close the app, come back — it continues.'),
        feat('sparkles', 'Every quality', 'Pick 144p up to 8K / HDR / 60fps, or MP3, M4A, Opus and WAV audio.'),
        feat('image', 'Photos & thumbnails', 'Instagram carousels, X images, Pinterest pins and full-size YouTube thumbnails.'),
        feat('layers', 'Playlists & batches', 'Grab a whole playlist or channel, or paste many links at once.'))));
  renderResult();
}
function feat(ic, t, d) { return h('div', { class: 'feat' }, h('div', { class: 'fi' }, I(ic)), h('b', {}, t), h('p', {}, d)); }

function toggleBatch() {
  APP.batch = !APP.batch;
  $('#omni').hidden = APP.batch;
  $('#batchBox').hidden = !APP.batch;
  $('#batchToggle').innerHTML = APP.batch ? `${icon('link')} One link` : `${icon('batch')} Many links at once`;
  (APP.batch ? $('#batchText') : $('#url')).focus();
}
function batchLinks() {
  return [...new Set(($('#batchText').value.match(/(https?:\/\/[^\s<>"']+|(?:www\.)?[a-z0-9-]+\.[a-z]{2,}\/[^\s<>"']+)/gi) || []).map((s) => s.trim()))];
}
function updateBatchCount() {
  const n = batchLinks().length;
  $('#batchLbl').textContent = n ? `Add ${n} link${n > 1 ? 's' : ''} to downloads` : 'Add to downloads';
}
async function batchDownload() {
  const links = batchLinks();
  if (!links.length) return toast('Paste at least one link.', { error: true });
  const q = $('#batchQ').value;
  const specs = links.map((url) => ({ url, mode: q === 'audio' ? 'audio' : 'video', quality: q === 'audio' ? undefined : q, audio: 'mp3-320', title: url,
    label: q === 'audio' ? 'MP3 320' : (q === 'best' ? 'Best quality' : q + 'p') }));
  try {
    await api('/api/download', { body: { specs } });
    $('#batchText').value = ''; updateBatchCount();
    toast(`${links.length} download${links.length > 1 ? 's' : ''} added`, { action: { label: 'View', fn: () => go('queue') } });
    pollSoon();
  } catch (e) { toast(e.message, { error: true }); }
}

async function pasteAndGo() {
  try {
    const t = (await navigator.clipboard.readText()).trim();
    if (!t) return toast('Your clipboard is empty.', { error: true });
    if (APP.batch) { $('#batchText').value += (($('#batchText').value && !$('#batchText').value.endsWith('\n')) ? '\n' : '') + t; updateBatchCount(); return; }
    $('#url').value = t; analyze();
  } catch (e) { $('#url').focus(); toast('Press Ctrl+V to paste the link.', { error: true }); }
}

async function analyze(urlArg, fresh) {
  const url = (urlArg || $('#url').value || '').trim();
  if (!url) { $('#url').focus(); return; }
  if (APP.batch) toggleBatch();
  $('#url').value = url;
  APP.analyzing = true; APP.error = null; APP.result = null; APP.lastUrl = url;
  const btn = $('#goBtn'); btn.disabled = true; btn.innerHTML = '<span class="spin"></span> Analyzing';
  renderResult();
  const token = (APP.token = Symbol('a'));
  try {
    const r = await api('/api/analyze', { body: { url, fresh: !!fresh } });
    if (token !== APP.token) return;
    APP.result = r.result;
    APP.sel = initSel(r.result);
  } catch (e) {
    if (token !== APP.token) return;
    APP.error = e.message;
  } finally {
    if (token === APP.token) {
      APP.analyzing = false; btn.disabled = false; btn.innerHTML = `${icon('search')} Analyze`;
      renderResult();
    }
  }
}

function initSel(r) {
  const s = APP.settings;
  const dq = s.default_quality || 'best';
  let quality = r.qualities?.[0]?.id || 'best';
  if (/^\d+$/.test(dq) && r.qualities?.length) {
    const fit = r.qualities.find((q) => q.height <= +dq);
    quality = fit ? fit.id : r.qualities[r.qualities.length - 1].id;
  }
  let tab = 'video';
  if (r.kind === 'images') tab = 'images';
  else if (r.kind === 'audio' || dq === 'audio') tab = r.audio?.length ? 'audio' : 'video';
  if (tab === 'video' && !r.qualities?.length && r.images?.length) tab = 'images';
  return {
    tab, quality, audio: 'mp3-320', container: s.container || 'mp4', subs: new Set(), trim: false, start: '', end: '',
    thumbs: new Set(r.thumbnails?.length ? [Math.max(0, r.thumbnails.findIndex((t) => t.ext === 'jpg'))] : []), bad: new Set(), imgs: new Set((r.images || []).map((_, i) => i)),
    pl: new Set((r.entries || []).map((_, i) => i)), plq: dq,
  };
}

function renderResult() {
  const box = $('#result'); if (!box) return;
  box.innerHTML = '';
  $('#landing').hidden = !!(APP.analyzing || APP.result || APP.error);
  if (APP.analyzing) {
    box.append(h('div', { class: 'card skel' },
      h('div', { class: 'sk', style: { aspectRatio: '16/9' } }),
      h('div', {}, h('div', { class: 'sk', style: { height: '22px', width: '80%' } }), h('div', { class: 'sk', style: { height: '14px', width: '45%', marginTop: '10px' } }),
        h('div', { class: 'steps', style: { marginTop: '18px' } }, h('span', { class: 'spin' }), h('span', { id: 'stepTxt' }, 'Reading the link…')),
        h('div', { style: { display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '10px', marginTop: '18px' } },
          [0, 1, 2].map(() => h('div', { class: 'sk', style: { height: '78px' } }))))));
    const msgs = ['Reading the link…', 'Finding every quality…', 'Checking audio & subtitles…', 'Collecting thumbnails & images…', 'Large playlists can take a little longer…'];
    let i = 0; const tok = APP.token;
    const tick = () => { if (APP.token !== tok || !APP.analyzing) return; const el = $('#stepTxt'); if (el) el.textContent = msgs[Math.min(++i, msgs.length - 1)]; setTimeout(tick, 2600); };
    setTimeout(tick, 2600);
    return;
  }
  if (APP.error) {
    box.append(h('div', { class: 'notice' }, I('alert'), h('div', {}, h('b', {}, 'Couldn’t read this link'), h('p', {}, APP.error),
      h('div', { class: 'act' }, h('button', { class: 'btn sm', onclick: () => analyze(APP.lastUrl, true) }, I('retry'), 'Try again'),
        /cookie|logged in|age-restricted/i.test(APP.error) ? h('button', { class: 'btn sm', onclick: () => go('settings') }, I('cookie'), 'Open Settings') : null))));
    return;
  }
  const r = APP.result; if (!r) return;
  box.append(r.kind === 'playlist' ? playlistCard(r) : mediaCard(r));
  hydrateIcons(box);
}

function metaBlock(r) {
  return h('div', { class: 'meta' },
    h('div', { style: { display: 'flex', gap: '6px', marginBottom: '8px', flexWrap: 'wrap' } }, h('span', { class: 'pill' }, I('globe'), r.site || 'Web'),
      r.kind === 'playlist' ? h('span', { class: 'pill' }, I('layers'), `${r.entries.length} items`) : null),
    h('h2', {}, r.title),
    h('div', { class: 'sub' },
      r.uploader ? h('span', {}, I('user'), r.uploader) : null,
      r.view_count ? h('span', {}, I('eye'), fmt.num(r.view_count) + ' views') : null,
      r.upload_date ? h('span', {}, I('cal'), fmt.date(r.upload_date)) : null,
      r.duration ? h('span', {}, I('clock'), fmt.dur(r.duration)) : null));
}

function mediaCard(r) {
  const S = APP.sel;
  const portrait = /tiktok|instagram|snapchat/i.test(r.site) && r.kind !== 'images';
  const side = h('div', { class: 'side' },
    h('div', { class: 'thumb' + (portrait ? ' portrait' : '') }, img(r.thumbnail, r.title),
      r.duration ? h('span', { class: 'dur' }, fmt.dur(r.duration)) : null, r.is_live ? h('span', { class: 'live' }, 'LIVE') : null),
    metaBlock(r),
    h('button', { class: 'btn ghost sm', style: { alignSelf: 'flex-start' }, onclick: () => analyze(r.url, true) }, I('refresh'), 'Re-analyze'));
  const tabs = [];
  if (r.qualities?.length) tabs.push(['video', 'video', 'Video', r.qualities.length]);
  if (r.audio?.length) tabs.push(['audio', 'music', 'Audio', null]);
  if (r.images?.length) tabs.push(['images', 'image', r.images.some((x) => x.video) ? 'Media' : 'Images', r.images.length]);
  if (r.thumbnails?.length) tabs.push(['thumbs', 'image', 'Thumbnail', r.thumbnails.length - S.bad.size]);
  if (r.subtitles?.length && r.qualities?.length) tabs.push(['subs', 'cc', 'Subtitles', r.subtitles.length]);
  if (!tabs.some((t) => t[0] === S.tab)) S.tab = tabs[0]?.[0];
  const main = h('div', { class: 'main' });
  if (r.warnings?.length) main.append(h('div', { class: 'notice warn', style: { marginBottom: '14px' } }, I('alert'), h('div', {}, h('p', {}, r.warnings.join(' ')))));
  if (!tabs.length) {
    main.append(h('div', { class: 'notice warn' }, I('info'), h('div', {}, h('b', {}, 'Nothing downloadable found'), h('p', {}, 'This page has no video or images MediaGrab can save. If it needs a login, add cookies in Settings.'))));
  } else {
    main.append(h('div', { class: 'tabs' }, tabs.map(([id, ic, label, n]) => h('button', { class: S.tab === id ? 'active' : '', onclick: () => { S.tab = id; renderResult(); } },
      I(ic), label, n ? h('span', { class: 'count' }, n) : null))));
    main.append(tabBody(r, S));
  }
  return h('div', { class: 'card media' }, side, main);
}

function qopt(sel, onclick, ...body) {
  return h('button', { class: 'qopt' + (sel ? ' sel' : ''), onclick }, h('span', { class: 'check' }, sel ? I('check') : null), ...body);
}

function tabBody(r, S) {
  const wrap = h('div', { style: { display: 'flex', flexDirection: 'column', flex: 1 } });
  const rer = () => renderResult();
  if (S.tab === 'video') {
    wrap.append(h('div', { class: 'qgrid' }, r.qualities.map((q) => qopt(S.quality === q.id, () => { S.quality = q.id; rer(); },
      h('div', { class: 'q' }, q.label, q.badge ? h('span', { class: 'tag' + (q.height < 720 ? ' plain' : '') }, q.badge) : null),
      h('div', { class: 'd' }, [q.fps > 30 ? `${q.fps}fps` : null, q.hdr ? 'HDR' : null, (q.vcodec || '').toUpperCase().replace('AVC1', 'H.264').replace('VP09', 'VP9').replace('AV01', 'AV1')].filter(Boolean).join(' · ') || 'Video'),
      h('div', { class: 'sz' }, q.size ? '≈ ' + fmt.bytes(q.size) : 'Size varies')))));
    const subsAvail = r.subtitles?.length;
    if (!(r.gallery && S.quality === 'original')) wrap.append(h('div', { class: 'opts' },
      h('div', {}, h('span', { class: 'opt-label' }, 'Format'),
        h('div', { class: 'seg' }, ['mp4', 'mkv'].map((c) => h('button', { class: S.container === c ? 'on' : '', onclick: () => { S.container = c; rer(); } }, c.toUpperCase())))),
      h('div', { class: 'trim' }, h('span', { class: 'opt-label' }, 'Trim'),
        h('button', { class: 'switch' + (S.trim ? ' on' : ''), title: 'Download only part of the video', onclick: () => { S.trim = !S.trim; rer(); } }),
        S.trim ? [h('input', { class: 'input', placeholder: 'Start 0:00', value: S.start, oninput: (e) => { S.start = e.target.value; } }), '→',
          h('input', { class: 'input', placeholder: `End ${fmt.dur(r.duration) || 'end'}`, value: S.end, oninput: (e) => { S.end = e.target.value; } })] : null),
      subsAvail ? h('div', {}, h('span', { class: 'opt-label' }, 'Subtitles'), h('span', { style: { color: 'var(--text-2)', fontSize: '13px' } }, S.subs.size ? [...S.subs].join(', ') : 'none'),
        ' ', h('button', { class: 'linkish', onclick: () => { S.tab = 'subs'; rer(); } }, 'choose')) : null));
    const q = r.qualities.find((x) => x.id === S.quality) || r.qualities[0];
    wrap.append(cta(r.gallery && S.quality === 'original' ? 'Download video' : `Download ${q ? q.label : ''} ${S.container.toUpperCase()}`, () => startVideo(r, S),
      q?.size ? `About ${fmt.bytes(q.size)}${r.duration > 3600 ? ' · long video: safe to pause & resume' : ''}` : ''));
  } else if (S.tab === 'audio') {
    wrap.append(h('div', { class: 'qgrid' }, r.audio.map((a) => qopt(S.audio === a.id, () => { S.audio = a.id; rer(); },
      h('div', { class: 'q' }, a.label, a.id.startsWith('mp3') ? h('span', { class: 'tag plain' }, a.id.split('-')[1]) : null),
      h('div', { class: 'd' }, a.desc), h('div', { class: 'sz' }, a.size ? '≈ ' + fmt.bytes(a.size) : '')))));
    const a = r.audio.find((x) => x.id === S.audio);
    wrap.append(cta(`Download ${a ? a.label : 'audio'}${S.audio.includes('-') ? ' ' + S.audio.split('-')[1] + 'k' : ''}`, () => startAudio(r, S), 'Cover art and title are added automatically'));
  } else if (S.tab === 'thumbs') {
    wrap.append(h('div', { class: 'grid-bar' }, h('span', { style: { color: 'var(--text-2)' } }, 'Pick the sizes you want — the biggest is the original.')),
      h('div', { class: 'igrid', style: { gridTemplateColumns: 'repeat(auto-fill,minmax(180px,1fr))' } }, r.thumbnails.map((t, i) => {
        if (S.bad.has(i)) return null;
        const on = S.thumbs.has(i);
        const pic = img(t.url);
        // some sizes a site lists don't actually exist — hide them instead of showing a blank tile
        if (pic.tagName === 'IMG') pic.addEventListener('error', () => {
          S.bad.add(i); S.thumbs.delete(i);
          if (!S.thumbs.size) { const next = r.thumbnails.findIndex((_, j) => !S.bad.has(j)); if (next >= 0) S.thumbs.add(next); }
          rer();
        });
        return h('div', { class: 'iitem' + (on ? ' sel' : ''), style: { aspectRatio: '16/9' }, onclick: () => { on ? S.thumbs.delete(i) : S.thumbs.add(i); rer(); } },
          pic, h('span', { class: 'box' }, on ? I('check') : null), h('span', { class: 'cap' }, h('span', {}, t.label), h('span', {}, t.ext.toUpperCase())));
      })));
    wrap.append(cta(S.thumbs.size ? `Download ${S.thumbs.size} thumbnail${S.thumbs.size > 1 ? 's' : ''}` : 'Select a thumbnail', () => startThumbs(r, S), '', !S.thumbs.size));
  } else if (S.tab === 'images') {
    const all = S.imgs.size === r.images.length;
    wrap.append(h('div', { class: 'grid-bar' },
      h('button', { class: 'btn sm', onclick: () => { S.imgs = all ? new Set() : new Set(r.images.map((_, i) => i)); rer(); } }, h('span', { class: 'cbox' + (all ? ' on' : '') }, all ? I('check') : null), all ? 'Unselect all' : 'Select all'),
      h('span', { style: { color: 'var(--muted)', fontSize: '13px' } }, `${S.imgs.size} of ${r.images.length} selected · saved in original quality`)),
    h('div', { class: 'igrid' }, r.images.map((m, i) => {
      const on = S.imgs.has(i);
      return h('div', { class: 'iitem' + (on ? ' sel' : ''), onclick: () => { on ? S.imgs.delete(i) : S.imgs.add(i); rer(); } },
        img(m.display || (m.video ? r.thumbnail : '')), h('span', { class: 'box' }, on ? I('check') : null),
        m.video ? h('span', { class: 'vid' }, I('video'), 'Video') : null,
        h('span', { class: 'cap' }, h('span', {}, `#${i + 1}`), h('span', {}, m.width ? `${m.width}×${m.height}` : (m.ext || '').toUpperCase())));
    })));
    wrap.append(cta(S.imgs.size ? `Download ${S.imgs.size} item${S.imgs.size > 1 ? 's' : ''}` : 'Select items', () => startImages(r, S), '', !S.imgs.size));
  } else if (S.tab === 'subs') {
    wrap.append(h('p', { style: { margin: '0 0 12px', color: 'var(--text-2)' } }, 'Choose subtitle languages to save with the video (as .srt files, or embedded — see Settings).'),
      h('div', { class: 'chips' }, r.subtitles.map((s) => h('button', { class: 'chip' + (S.subs.has(s.lang) ? ' on' : ''), onclick: () => { S.subs.has(s.lang) ? S.subs.delete(s.lang) : S.subs.add(s.lang); rer(); } }, s.name))));
    wrap.append(cta('Back to video', () => { S.tab = 'video'; rer(); }, S.subs.size ? `${S.subs.size} language${S.subs.size > 1 ? 's' : ''} selected` : '', false, 'video'));
  }
  return wrap;
}

function cta(label, fn, hint, disabled, ic = 'download') {
  return h('div', { class: 'cta' }, h('button', { class: 'btn primary big', disabled: !!disabled, onclick: fn }, I(ic), label), hint ? h('span', { class: 'hint' }, hint) : null);
}

async function queue(specs, what) {
  try {
    const r = await api('/api/download', { body: { specs } });
    toast(`${what} added to downloads`, { action: { label: 'View', fn: () => go('queue') } });
    pollSoon();
    return r;
  } catch (e) { toast(e.message, { error: true }); }
}
const baseSpec = (r) => ({ url: r.webpage_url || r.url, title: r.title, thumbnail: r.thumbnail, site: r.site });

function startVideo(r, S) {
  if (S.quality === 'original' && r.gallery) {
    return queue([{ ...baseSpec(r), mode: 'gallery', indices: [], count: 1, label: 'Original video' }], 'Video');
  }
  const spec = { ...baseSpec(r), mode: 'video', quality: S.quality, container: S.container, subs: [...S.subs], portrait: r.portrait ?? null };
  const q = r.qualities.find((x) => x.id === S.quality);
  spec.label = `${q ? q.label : 'Best'} ${S.container.toUpperCase()}`;
  if (S.trim) {
    const a = parseTime(S.start), b = parseTime(S.end);
    if (Number.isNaN(a) || Number.isNaN(b)) return toast('Use times like 1:30 or 1:02:30.', { error: true });
    if (a != null && b != null && b <= a) return toast('The end time must be after the start.', { error: true });
    spec.trim = { start: a, end: b };
    spec.label += ` · ${fmt.dur(a || 0)}–${b != null ? fmt.dur(b) : 'end'}`;
  }
  queue([spec], 'Video');
}
function startAudio(r, S) {
  const a = r.audio.find((x) => x.id === S.audio);
  queue([{ ...baseSpec(r), mode: 'audio', audio: S.audio, label: `${a ? a.label : 'Audio'}${S.audio.includes('-') ? ' ' + S.audio.split('-')[1] : ''}` }], 'Audio');
}
function safeName(s) { return String(s || 'file').replace(/[<>:"/\\|?*\x00-\x1f]/g, '_').replace(/\s+/g, ' ').trim().slice(0, 90) || 'file'; }
function startThumbs(r, S) {
  const files = [...S.thumbs].sort().map((i) => { const t = r.thumbnails[i]; return { url: t.url, name: `${safeName(r.title)} - thumbnail ${t.width ? t.width + 'x' + t.height : 'original'}.${t.ext}` }; });
  queue([{ ...baseSpec(r), mode: 'files', files, referer: r.webpage_url, label: `${files.length} thumbnail${files.length > 1 ? 's' : ''}` }], files.length > 1 ? 'Thumbnails' : 'Thumbnail');
}
function startImages(r, S) {
  const idx = [...S.imgs].sort((a, b) => a - b);
  const n = idx.length;
  const label = `${n} item${n > 1 ? 's' : ''}`;
  if (r.gallery) {
    queue([{ ...baseSpec(r), mode: 'gallery', indices: idx.length === r.images.length ? [] : idx.map((i) => r.images[i].index), count: n, label }], n > 1 ? 'Images' : 'Image');
  } else {
    const files = idx.map((i) => ({ url: r.images[i].url, name: '' }));
    queue([{ ...baseSpec(r), mode: 'files', files, referer: r.webpage_url, label }], n > 1 ? 'Images' : 'Image');
  }
}

function playlistCard(r) {
  const S = APP.sel;
  const rer = () => renderResult();
  const all = S.pl.size === r.entries.length;
  const total = [...S.pl].reduce((a, i) => a + (r.entries[i]?.duration || 0), 0);
  const qsel = h('select', { class: 'input', onchange: (e) => { S.plq = e.target.value; } }, QUALITY_PRESETS.map(([v, l]) => h('option', { value: v }, l)));
  qsel.value = S.plq;
  return h('div', { class: 'card', style: { overflow: 'hidden', animation: 'rise .35s ease' } },
    h('div', { class: 'playlist-head' }, h('div', { class: 'thumb' }, img(r.thumbnail, r.title)), metaBlock(r)),
    h('div', { class: 'playlist-body' },
      h('div', { class: 'grid-bar' },
        h('button', { class: 'btn sm', onclick: () => { S.pl = all ? new Set() : new Set(r.entries.map((_, i) => i)); rer(); } }, h('span', { class: 'cbox' + (all ? ' on' : '') }, all ? I('check') : null), all ? 'Unselect all' : 'Select all'),
        h('span', { style: { color: 'var(--muted)', fontSize: '13px' } }, `${S.pl.size} of ${r.entries.length} selected${total ? ' · ' + fmt.dur(total) + ' total' : ''}`)),
      h('div', { class: 'plist' }, r.entries.map((e, i) => {
        const on = S.pl.has(i);
        return h('div', { class: 'prow', onclick: () => { on ? S.pl.delete(i) : S.pl.add(i); rer(); } },
          h('span', { class: 'cbox' + (on ? ' on' : '') }, on ? I('check') : null), h('span', { class: 'n' }, e.index),
          h('div', { class: 'pt' }, img(e.thumbnail)), h('div', { class: 'tt' }, h('b', {}, e.title), e.uploader ? h('small', {}, e.uploader) : null),
          h('span', { class: 'dd' }, fmt.dur(e.duration)));
      })),
      h('div', { class: 'cta' }, h('span', { class: 'opt-label' }, 'Quality'), qsel,
        h('button', { class: 'btn primary big', disabled: !S.pl.size, onclick: () => startPlaylist(r, S) }, I('download'), `Download ${S.pl.size} item${S.pl.size === 1 ? '' : 's'}`),
        h('span', { class: 'hint' }, 'Saved into a folder named after the playlist'))));
}
function startPlaylist(r, S) {
  const q = S.plq;
  const specs = [...S.pl].sort((a, b) => a - b).map((i) => {
    const e = r.entries[i];
    return { url: e.url, title: e.title, thumbnail: e.thumbnail, site: r.site, folder: r.title, mode: q === 'audio' ? 'audio' : 'video',
      quality: q === 'audio' ? undefined : q, audio: 'mp3-320', label: q === 'audio' ? 'MP3 320' : (q === 'best' ? 'Best quality' : q + 'p') };
  });
  queue(specs, `${specs.length} item${specs.length > 1 ? 's' : ''}`);
}

/* ---------------------------------------------------------------- queue view */
const STATUS_TXT = { queued: 'Waiting', starting: 'Starting', downloading: 'Downloading', processing: 'Processing', retrying: 'Retrying', paused: 'Paused', done: 'Completed', error: 'Failed', cancelled: 'Cancelled' };
const ACTIVE = ['downloading', 'processing', 'starting', 'retrying'];

function renderQueue(full) {
  const v = $('#view-queue');
  if (full || !$('#jobList')) {
    v.innerHTML = '';
    v.append(
      h('div', { class: 'page-head' }, h('div', {}, h('h1', {}, 'Downloads'), h('p', {}, 'Everything you’ve grabbed. Downloads keep going in the background and resume after a restart.')),
        h('div', { style: { display: 'flex', gap: '8px' } }, h('button', { class: 'btn', onclick: () => api('/api/open', { body: { what: 'downloads' } }).catch((e) => toast(e.message, { error: true })) }, I('folder'), 'Open folder'),
          h('button', { class: 'btn primary', onclick: () => go('download') }, I('download'), 'New download'))),
      h('div', { class: 'stats', id: 'qstats' }),
      h('div', { class: 'toolbar' },
        h('div', { class: 'seg', id: 'qfilter' }, [['all', 'All'], ['active', 'Active'], ['done', 'Completed'], ['failed', 'Failed']].map(([k, l]) =>
          h('button', { class: APP.filter === k ? 'on' : '', 'data-f': k, onclick: () => { APP.filter = k; renderQueue(true); } }, l))),
        h('span', { class: 'grow' }),
        h('button', { class: 'btn sm', onclick: () => bulk('pause-all') }, I('pause'), 'Pause all'),
        h('button', { class: 'btn sm', onclick: () => bulk('resume-all') }, I('play'), 'Resume all'),
        h('button', { class: 'btn sm ghost', onclick: () => bulk('clear-finished') }, I('check'), 'Clear completed'),
        h('button', { class: 'btn sm ghost', onclick: () => bulk('clear-failed') }, I('trash'), 'Clear failed')),
      h('div', { class: 'jobs', id: 'jobList' }));
    APP.jobEls = new Map();
  }
  updateQueue();
}
async function bulk(action) {
  try { const r = await api('/api/jobs/bulk', { body: { action } }); if (r.removed != null) toast(r.removed ? `Removed ${r.removed} from the list` : 'Nothing to clear'); await poll(); } catch (e) { toast(e.message, { error: true }); }
}
function filtered() {
  const f = APP.filter;
  return APP.jobs.filter((j) => f === 'all' || (f === 'active' && (ACTIVE.includes(j.status) || j.status === 'queued' || j.status === 'paused'))
    || (f === 'done' && j.status === 'done') || (f === 'failed' && (j.status === 'error' || j.status === 'cancelled')));
}
function updateQueue() {
  const list = $('#jobList'); if (!list) return;
  const jobs = filtered();
  const act = APP.jobs.filter((j) => ACTIVE.includes(j.status)).length;
  const q = APP.jobs.filter((j) => j.status === 'queued').length;
  const done = APP.jobs.filter((j) => j.status === 'done');
  const speed = APP.jobs.reduce((a, j) => a + (ACTIVE.includes(j.status) ? (j.speed || 0) : 0), 0);
  $('#qstats').replaceChildren(stat('Active', act), stat('Waiting', q), stat('Completed', done.length),
    stat('Saved', fmt.bytes(done.reduce((a, j) => a + (j.size || 0), 0)) || '0 B'), stat('Speed', speed ? fmt.bytes(speed) + '/s' : '—'));
  if (!jobs.length) {
    APP.jobEls = new Map();
    list.replaceChildren(h('div', { class: 'empty' }, h('div', { class: 'ei' }, I('download')),
      h('b', {}, APP.jobs.length ? 'Nothing here' : 'No downloads yet'),
      h('div', {}, APP.jobs.length ? 'Try another filter.' : 'Paste a link on the Download page to get started.'),
      APP.jobs.length ? null : h('button', { class: 'btn primary', style: { marginTop: '16px' }, onclick: () => go('download') }, I('link'), 'Paste a link')));
    return;
  }
  const want = new Set(jobs.map((j) => j.id));
  for (const [id, el] of APP.jobEls) if (!want.has(id)) { el.remove(); APP.jobEls.delete(id); }
  if (list.querySelector('.empty')) list.innerHTML = '';
  let prev = null;
  for (const j of jobs) {
    let el = APP.jobEls.get(j.id);
    const sig = j.status + '|' + (j.thumbnail || '') + '|' + j.title + '|' + (j.error || '') + '|' + (j.note || '');
    if (!el || el.dataset.sig !== sig) {
      const fresh = jobEl(j); fresh.dataset.sig = sig;
      if (el) el.replaceWith(fresh); el = fresh; APP.jobEls.set(j.id, el);
    }
    updateJobProgress(el, j);
    const want2 = prev ? prev.nextSibling : list.firstChild;
    if (want2 !== el) list.insertBefore(el, want2);
    prev = el;
  }
}
function stat(l, v) { return h('div', { class: 'stat' }, h('small', {}, l), h('b', {}, v)); }

function jobEl(j) {
  const st = j.status;
  const act = (ic, title, fn, cls = '') => h('button', { class: 'icon-btn ' + cls, title, onclick: fn }, I(ic));
  const ctl = (a) => async () => { try { await api(`/api/jobs/${j.id}/${a}`, { body: {} }); poll(); } catch (e) { toast(e.message, { error: true }); } };
  const open = (what) => async () => { try { await api('/api/open', { body: { id: j.id, what } }); } catch (e) { toast(e.message, { error: true }); } };
  const actions = [];
  if (st === 'done') { actions.push(act('play', 'Open file', open('file'), 'go'), act('folder', 'Show in folder', open('folder')), act('retry', 'Download again', ctl('retry'))); }
  if (ACTIVE.includes(st) || st === 'queued') actions.push(act('pause', 'Pause', ctl('pause')), act('x', 'Cancel', ctl('cancel'), 'red'));
  if (st === 'paused') actions.push(act('play', 'Resume', ctl('resume'), 'go'), act('x', 'Cancel', ctl('cancel'), 'red'));
  if (st === 'error' || st === 'cancelled') actions.push(act('retry', 'Try again', ctl(st === 'error' ? 'resume' : 'retry'), 'go'));
  if (!ACTIVE.includes(st)) actions.push(act('trash', 'Remove from list', ctl('remove'), 'red'));
  const modeIc = { video: 'video', audio: 'music', files: 'image', gallery: 'image' }[j.mode] || 'download';
  return h('div', { class: 'job ' + st },
    h('div', { class: 'jt' }, j.thumbnail ? img(j.thumbnail) : I(modeIc), h('div', { class: 'ok' }, I('check'))),
    h('div', { class: 'jb' },
      h('div', { class: 'jtitle', title: j.title }, j.title),
      h('div', { class: 'jmeta' }, h('span', { class: 'status ' + st }, STATUS_TXT[st] || st), j.site ? h('span', {}, j.site) : null, j.label ? h('span', {}, j.label) : null,
        st === 'done' && j.size ? h('span', {}, fmt.bytes(j.size)) : null, st === 'done' && j.files?.length > 1 ? h('span', {}, `${j.files.length} files`) : null,
        st === 'done' ? h('span', {}, fmt.ago(j.finished)) : null),
      st === 'done' || st === 'error' || st === 'cancelled' ? null : h('div', { class: 'bar' }, h('div', { style: { width: '0%' } })),
      st === 'done' || st === 'error' || st === 'cancelled' ? null : h('div', { class: 'jline' }, h('span', { class: 'l' }), h('span', { class: 'r' })),
      j.error ? h('div', { class: 'jerr' }, j.error) : null,
      j.note ? h('div', { class: 'jnote' }, j.note) : null),
    h('div', { class: 'ja' }, actions));
}
function updateJobProgress(el, j) {
  const bar = el.querySelector('.bar'); if (!bar) return;
  const st = j.status;
  const pct = j.percent;
  bar.classList.toggle('indet', (st === 'downloading' && pct == null) || st === 'starting');
  bar.classList.toggle('proc', st === 'processing');
  bar.classList.toggle('paused', st === 'paused' || st === 'queued');
  bar.firstChild.style.width = (pct != null ? pct : st === 'processing' ? 100 : 0) + '%';
  const left = el.querySelector('.jline .l'), right = el.querySelector('.jline .r');
  let l = j.stage_label || STATUS_TXT[st] || '';
  if (st === 'queued') l = 'Waiting for a free slot…';
  if (st === 'paused') l = 'Paused — resumes from where it stopped';
  const bits = [];
  if (st === 'downloading') {
    if (pct != null) bits.push(pct.toFixed(pct < 10 ? 1 : 0) + '%');
    if (j.total) bits.push(`${fmt.bytes(j.downloaded)} of ${fmt.bytes(j.total)}`); else if (j.downloaded) bits.push(fmt.bytes(j.downloaded));
    if (j.speed) bits.push(fmt.bytes(j.speed) + '/s');
    if (j.eta) bits.push(fmt.eta(j.eta));
  }
  left.textContent = l; right.textContent = bits.join(' · ');
}

/* ---------------------------------------------------------------- polling */
let pollTimer = null;
async function poll() {
  clearTimeout(pollTimer);
  try {
    const r = await api('/api/jobs');
    APP.jobs = r.jobs;
    const busy = APP.jobs.filter((j) => ACTIVE.includes(j.status) || j.status === 'queued').length;
    const b = $('#qbadge'); b.hidden = !busy; b.textContent = busy; b.classList.toggle('pulse', busy > 0);
    for (const j of APP.jobs) {
      const old = APP.seen?.get(j.id);
      if (old && old !== 'done' && j.status === 'done') toast(`Saved: ${j.title.slice(0, 60)}`, { action: { label: 'Open', fn: () => api('/api/open', { body: { id: j.id, what: 'file' } }) } });
      if (old && old !== 'error' && j.status === 'error') toast(`Failed: ${j.title.slice(0, 50)}`, { error: true, action: { label: 'Details', fn: () => go('queue') } });
    }
    APP.seen = new Map(APP.jobs.map((j) => [j.id, j.status]));
    if (APP.view === 'queue') updateQueue();
    document.title = busy ? `(${busy}) MediaGrab` : 'MediaGrab';
    pollTimer = setTimeout(poll, busy ? 900 : 4000);
  } catch (e) {
    pollTimer = setTimeout(poll, 5000);
  }
}
function pollSoon() { clearTimeout(pollTimer); pollTimer = setTimeout(poll, 250); }

/* ---------------------------------------------------------------- settings */
async function saveSetting(patch, quiet) {
  try { const r = await api('/api/settings', { body: patch }); APP.settings = r.settings; if (!quiet) toast('Saved'); return true; } catch (e) { toast(e.message, { error: true }); return false; }
}
function sw(key, onChange) {
  const b = h('button', { class: 'switch' + (APP.settings[key] ? ' on' : ''), onclick: async () => {
    const val = !APP.settings[key];
    if (await saveSetting({ [key]: val }, true)) { b.classList.toggle('on', val); onChange && onChange(val); }
  } });
  return b;
}
function row(title, desc, control) { return h('div', { class: 'row' }, h('div', { class: 'rl' }, h('b', {}, title), desc ? h('small', {}, desc) : null), control); }
function debounce(fn, ms = 600) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }
function textSetting(key, placeholder, width = '220px') {
  const save = debounce((v) => saveSetting({ [key]: v }), 700);
  return h('input', { class: 'input', style: { width }, value: APP.settings[key] ?? '', placeholder, oninput: (e) => save(e.target.value) });
}
function selSetting(key, options) {
  const s = h('select', { class: 'input', onchange: (e) => saveSetting({ [key]: e.target.value }) }, options.map(([v, l]) => h('option', { value: v }, l)));
  s.value = String(APP.settings[key] ?? '');
  return s;
}

async function renderSettings() {
  const v = $('#view-settings');
  try { const st = await api('/api/state'); APP.settings = st.settings; APP.tools = st.tools; APP.version = st.version; } catch (e) { /* keep last */ }
  const S = APP.settings, T = APP.tools;
  const pathCode = h('code', { title: S.download_dir }, S.download_dir);
  const cookieInfo = h('small', {}, S.cookies_file ? 'Using your cookies.txt file' : S.cookies_browser ? `Using cookies from ${S.cookies_browser}` : 'Off — public content only');
  const fileIn = h('input', { type: 'file', accept: '.txt', hidden: true, onchange: async (e) => {
    const f = e.target.files[0]; if (!f) return;
    const fd = new FormData(); fd.append('file', f);
    try { const r = await api('/api/cookies', { body: fd }); APP.settings = r.settings; toast('Cookies file loaded'); renderSettings(); } catch (err) { toast(err.message, { error: true }); }
  } });
  v.replaceChildren(
    h('div', { class: 'page-head' }, h('div', {}, h('h1', {}, 'Settings'), h('p', {}, 'Changes save automatically.'))),
    h('div', { class: 'sgrid' },
      h('div', { class: 'card scard wide' }, h('h3', {}, I('folder'), 'Save location'), h('p', {}, 'Where your downloads go.'),
        h('div', { class: 'path' }, pathCode,
          h('button', { class: 'btn', onclick: async () => { try { const r = await api('/api/pick-folder', { body: {} }); if (r.picked) { APP.settings = r.settings; pathCode.textContent = r.settings.download_dir; toast('Download folder changed'); } } catch (e) { toast(e.message, { error: true }); } } }, I('folder'), 'Change…'),
          h('button', { class: 'btn ghost', onclick: () => api('/api/open', { body: { what: 'downloads' } }) }, I('open'), 'Open')),
        row('Sort into site folders', 'YouTube, TikTok, Instagram… each get their own folder', sw('subfolder_by_site')),
        row('Playlist folders', 'Playlist downloads go into a folder named after the playlist', sw('playlist_subfolder')),
        row('File name pattern', h('span', {}, 'yt-dlp template — e.g. ', h('code', {}, '%(uploader)s - %(title)s.%(ext)s')), textSetting('filename', '%(title)s [%(id)s].%(ext)s', '300px'))),
      h('div', { class: 'card scard' }, h('h3', {}, I('video'), 'Video'), h('p', {}, 'Defaults for new downloads.'),
        row('Default quality', 'Pre-selected after analyzing', selSetting('default_quality', QUALITY_PRESETS)),
        row('Container', 'MP4 plays everywhere · MKV keeps every codec', selSetting('container', [['mp4', 'MP4'], ['mkv', 'MKV']])),
        row('Max compatibility', 'Prefer H.264 + AAC when there’s a choice, so files play on any TV/phone', sw('compat')),
        row('Embed thumbnail', 'Cover image inside the video/MP3', sw('embed_thumbnail')),
        row('Embed info & chapters', 'Title, artist, date, chapters', sw('embed_metadata')),
        row('Embed subtitles', 'Put chosen subtitles inside the video instead of .srt files', sw('embed_subs'))),
      h('div', { class: 'card scard' }, h('h3', {}, I('zap'), 'Speed & reliability'), h('p', {}, 'Tuned for very long videos and shaky connections.'),
        row('Simultaneous downloads', 'How many run at the same time', selSetting('concurrency', [1, 2, 3, 4, 5, 6].map((n) => [String(n), String(n)]))),
        row('Parallel chunks', 'Faster for streams split into pieces (HLS/DASH)', selSetting('fragments', [1, 2, 4, 8, 16].map((n) => [String(n), String(n)]))),
        row('Auto-retry', 'Retries after a lost connection (resumes, doesn’t restart)', selSetting('auto_retry', [0, 1, 3, 5, 10].map((n) => [String(n), n ? n + ' times' : 'Off']))),
        row('Speed limit', 'e.g. 5M = 5 MB/s · empty = unlimited', textSetting('rate_limit', 'Unlimited', '120px'))),
      h('div', { class: 'card scard' }, h('h3', {}, I('cookie'), 'Login cookies'),
        h('p', {}, 'Needed for private, age-restricted or login-only content (often Instagram & Facebook). Your cookies never leave this PC.'),
        row('Use cookies from browser', cookieInfo, selSetting('cookies_browser', [['', 'Off'], ['firefox', 'Firefox (recommended)'], ['chrome', 'Chrome'], ['edge', 'Edge'], ['brave', 'Brave'], ['opera', 'Opera'], ['vivaldi', 'Vivaldi']])),
        row('cookies.txt file', 'Works with every browser — export with a “Get cookies.txt” extension', h('div', { style: { display: 'flex', gap: '6px' } }, fileIn,
          h('button', { class: 'btn sm', onclick: () => fileIn.click() }, 'Load…'),
          S.cookies_file ? h('button', { class: 'btn sm ghost danger', onclick: async () => { const r = await api('/api/cookies', { method: 'DELETE' }); APP.settings = r.settings; renderSettings(); } }, 'Remove') : null)),
        h('div', { class: 'notice info', style: { marginTop: '8px' } }, I('info'), h('div', {}, h('p', {}, 'Chrome and Edge lock their cookies while open. If it fails, close the browser first, use Firefox, or load a cookies.txt file.')))),
      h('div', { class: 'card scard' }, h('h3', {}, I('globe'), 'Network'), h('p', {}, 'Optional.'),
        row('Proxy', 'http://host:port or socks5://host:port', textSetting('proxy', 'None', '220px'))),
      h('div', { class: 'card scard wide' }, h('h3', {}, I('cpu'), 'Download engine'),
        h('p', {}, 'Sites change often. If a download suddenly stops working, update the engine — it fixes most problems.'),
        h('div', { class: 'engine' },
          eng('yt-dlp', T.yt_dlp), eng('gallery-dl', T.gallery_dl), eng('FFmpeg', T.ffmpeg ? 'Installed' : 'Missing', T.ffmpeg),
          eng('JS runtime (YouTube)', T.deno ? 'Deno ready' : 'Missing', T.deno), eng('MediaGrab', APP.version)),
        h('div', { style: { display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' } },
          h('button', { class: 'btn primary', id: 'updBtn', onclick: updateEngines }, I('refresh'), 'Update engines'),
          h('span', { class: 'hint', id: 'updMsg', style: { color: 'var(--muted)', fontSize: '13px' } }),
          !T.ffmpeg ? h('button', { class: 'btn', id: 'ffBtn', onclick: installFfmpeg }, I('download'), 'Install FFmpeg') : null,
          !T.ffmpeg ? h('span', { style: { color: 'var(--err)', fontSize: '13px' } }, 'FFmpeg is needed for HD video (1080p+) and MP3.') : null),
        h('pre', { class: 'log', id: 'updLog', hidden: true }))));
  hydrateIcons(v);
}
function eng(name, val, good = true) { return h('div', { class: 'eng' }, h('small', {}, name), h('b', {}, h('span', { class: good && val ? 'okd' : 'bad' }), val || 'Not found')); }
async function installFfmpeg() {
  const btn = $('#ffBtn'); btn.disabled = true; btn.innerHTML = '<span class="spin"></span> Installing FFmpeg…';
  $('#updMsg').textContent = 'Downloading FFmpeg with Windows’ package manager — this can take a few minutes.';
  try {
    await api('/api/install-ffmpeg', { body: {} });
    for (;;) {
      await new Promise((r) => setTimeout(r, 3000));
      const r = await api('/api/install-ffmpeg');
      if (!r.install.running) {
        APP.tools = r.tools;
        $('#updLog').hidden = !r.install.log; $('#updLog').textContent = r.install.log || '';
        toast(r.install.ok ? 'FFmpeg installed — HD video and MP3 are ready' : 'FFmpeg install failed — see the log', { error: !r.install.ok });
        if (r.install.ok) setTimeout(renderSettings, 1200);
        break;
      }
    }
  } catch (e) { toast(e.message, { error: true }); }
  btn.disabled = false; btn.innerHTML = `${icon('download')} Install FFmpeg`; $('#updMsg').textContent = '';
}

async function updateEngines() {
  const btn = $('#updBtn'); btn.disabled = true; btn.innerHTML = '<span class="spin"></span> Updating…';
  $('#updMsg').textContent = 'This takes up to a minute.';
  try {
    await api('/api/update-engines', { body: {} });
    for (;;) {
      await new Promise((r) => setTimeout(r, 2000));
      const r = await api('/api/update-engines');
      if (!r.update.running) {
        APP.tools = r.tools;
        $('#updLog').hidden = false; $('#updLog').textContent = r.update.log || '';
        toast(r.update.ok ? 'Engines are up to date' : 'Update failed — see the log', { error: !r.update.ok });
        if (r.update.ok) setTimeout(renderSettings, 1500);
        break;
      }
    }
  } catch (e) { toast(e.message, { error: true }); }
  btn.disabled = false; btn.innerHTML = `${icon('refresh')} Update engines`; $('#updMsg').textContent = '';
}

/* ---------------------------------------------------------------- paste & drop anywhere */
const looksLikeUrl = (t) => /^(https?:\/\/|www\.)\S+$/i.test(t.trim()) || /^[a-z0-9-]+(\.[a-z0-9-]+)+\/\S*$/i.test(t.trim());
document.addEventListener('paste', (e) => {
  const tgt = e.target;
  if (tgt && (tgt.tagName === 'INPUT' || tgt.tagName === 'TEXTAREA')) {
    if (tgt.id === 'url') setTimeout(() => { if (looksLikeUrl(tgt.value)) analyze(); }, 30);
    return;
  }
  const t = (e.clipboardData?.getData('text') || '').trim();
  if (!t) return;
  e.preventDefault();
  const links = t.split(/\s+/).filter(looksLikeUrl);
  if (links.length > 1) { if (APP.view !== 'download') go('download'); if (!APP.batch) toggleBatch(); $('#batchText').value = links.join('\n'); updateBatchCount(); return; }
  if (!looksLikeUrl(t)) return;
  if (APP.view !== 'download') go('download');
  if (APP.batch) toggleBatch();
  $('#url').value = t; analyze();
});
let dragN = 0;
window.addEventListener('dragenter', (e) => { if ([...(e.dataTransfer?.types || [])].some((t) => t === 'text/uri-list' || t === 'text/plain')) { dragN++; $('#dropHint').classList.add('on'); } });
window.addEventListener('dragleave', () => { dragN = Math.max(0, dragN - 1); if (!dragN) $('#dropHint').classList.remove('on'); });
window.addEventListener('dragover', (e) => e.preventDefault());
window.addEventListener('drop', (e) => {
  e.preventDefault(); dragN = 0; $('#dropHint').classList.remove('on');
  const t = (e.dataTransfer.getData('text/uri-list') || e.dataTransfer.getData('text/plain') || '').split('\n').find((x) => x && !x.startsWith('#'));
  if (t && looksLikeUrl(t)) { go('download'); if (APP.batch) toggleBatch(); $('#url').value = t.trim(); analyze(); }
});

/* ---------------------------------------------------------------- boot */
(async function boot() {
  let t = 'auto'; try { t = localStorage.getItem('mg-theme') || 'auto'; } catch (e) { /* ignore */ }
  applyTheme(t);
  hydrateIcons();
  try { const st = await api('/api/state'); APP.settings = st.settings; APP.tools = st.tools; APP.version = st.version; } catch (e) { toast(e.message, { error: true }); }
  renderDownloadShell();
  let view = 'download'; try { view = sessionStorage.getItem('mg-view') || 'download'; } catch (e) { /* ignore */ }
  go(view);
  poll();
})();
