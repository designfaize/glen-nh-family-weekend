// Smoke test: runs the planner <script> from planner_snippet.html against a stub DOM.
const fs = require('fs');
const src = fs.readFileSync(__dirname + '/planner_snippet.html', 'utf8');
const m = src.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error('FAIL: no script block'); process.exit(1); }

function el(tag) {
  return {
    tag, children: [], listeners: {}, dataset: {}, style: { cssText: '' },
    classList: { add() {}, remove() {} },
    hidden: false, draggable: false, value: '', _text: '', className: '',
    set textContent(v) { this._text = String(v); this.children = []; },
    get textContent() { return this._text; },
    set innerHTML(v) { this._html = String(v); this.children = []; },
    get innerHTML() { return this._html || ''; },
    appendChild(c) { this.children.push(c); return c; },
    removeChild(c) { this.children = this.children.filter(x => x !== c); },
    setAttribute() {}, select() {},
    addEventListener(t, f) { (this.listeners[t] = this.listeners[t] || []).push(f); },
  };
}
const ids = {};
global.document = {
  getElementById(id) { return ids[id] || (ids[id] = el('div#' + id)); },
  createElement(t) { return el(t); },
  createTextNode(t) { return { text: t }; },
  body: el('body'),
};
global.location = { search: '', pathname: '/glen/', origin: 'https://example.com' };
global.history = { replaceState() {} };
const store = {};
global.localStorage = {
  getItem: k => (k in store ? store[k] : null),
  setItem: (k, v) => { store[k] = v; },
  removeItem: k => { delete store[k]; },
};
Object.defineProperty(globalThis, 'navigator', {
  value: { clipboard: { writeText(u) { global.__copied = u; return { then(ok) { ok(); } }; } } },
  configurable: true,
});
global.document.execCommand = () => { global.__copied = global.document.body.children.at(-1).value; return true; };
global.prompt = () => {};
global.confirm = () => true;
global.window = { print() {} };

// Seed: items 0 & 63 in Fri/Morning + Laser Tag (9) in Fri/Evening; custom text with
// delimiters in Sat/Evening; Monday gets Funspot (81) in Midday plus garbage tokens
// (out-of-range id, NaN, broken URI) that must be dropped silently. Sunday stays empty.
store['glenPlanV1'] =
  '0,63|||9;|||~' + encodeURIComponent('Pool, time; fun|x') + ';|||;999,abc|81|~%|';

eval(m[1]);

function count(node, cls) {
  let n = 0;
  (node.children || []).forEach(c => {
    if ((c.className || '').includes(cls)) n++;
    n += count(c, cls);
  });
  return n;
}
const days = ids['pl-days'].children;
const friEntries = count(days[0], 'pl-entry');
const satEntries = count(days[1], 'pl-entry');
const monEntries = count(days[3], 'pl-entry');
const chips = ids['pl-chips'].children.length;

ids['pl-share'].listeners['click'][0]();
const p = new URL(global.__copied).searchParams.get('p');

let fail = 0;
function check(label, cond) { console.log((cond ? 'PASS' : 'FAIL') + ': ' + label); if (!cond) fail = 1; }
check('Friday loaded 3 entries from storage', friEntries === 3);
check('Saturday loaded 1 custom entry', satEntries === 1);
check('Monday kept Funspot, dropped 3 garbage tokens', monEntries === 1);
check('Friday palette rendered chips (10 expected)', chips === 10);
check('share URL round-trips custom text', typeof p === 'string' && p.includes('~Pool%2C%20time%3B%20fun%7Cx'));
check('share URL keeps numeric ids', typeof p === 'string' && p.indexOf('0,63') === 0);

const dyn = ids['dyn-days'].innerHTML;
check('dynamic plan keeps Friday check-in', dyn.includes('Check in at <b>Jellystone</b>'));
check('dynamic plan keeps Monday rollout', dyn.includes('Roll out south'));
check('Funspot detour callout renders', dyn.includes('35–40 minutes of total detour time'));
check('selected sidebar event gets a star', dyn.includes('<span class="star">★</span> Laser Tag'));
check('empty Sunday shows builder hint', dyn.includes('drag activities into Sunday below'));
check('custom entry is HTML-escaped in plan', !dyn.includes('<script') && dyn.includes('Pool, time; fun|x'));
process.exit(fail);
