// Smoke test: runs the planner <script> from the BUILT index.html (which has the
// travel matrix injected) against a stub DOM. Run build_index.py first.
const fs = require('fs');
const src = fs.readFileSync(__dirname + '/index.html', 'utf8');
const blocks = [...src.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(x => x[1]);
const m = [null, blocks.find(s => s.includes('glenPlanV1'))];
if (!m[1]) { console.error('FAIL: no planner script block'); process.exit(1); }

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
// Pretend the weather script already loaded a forecast for Saturday
global.window = { print() {}, __wx: { '2026-07-18': { hi: 81, lo: 62, kind: 'rain', e: '🌧️' } } };

// Seed: items 0 & 63 in Fri/Morning + Laser Tag (9) in Fri/Evening; custom text plus
// takeout McDonald's (105+1000) in Sat/Evening; Monday gets Funspot (81) in Midday plus
// garbage tokens (out-of-range id, NaN, takeout-flagged non-food 1063, broken URI) that
// must be dropped silently. Sunday stays empty.
// Monday seq: Bear Mail (51, camp) -> McDonald's (105, not takeout) -> Wake Up (52, camp)
// -> Funspot (81) -> Diana's (66). McD out-and-back must read "easy dad run!"; the
// camp->Funspot leg is a huge detour vs Diana's but departs camp, so no verdict allowed.
store['glenPlanV1'] =
  '0,63|||9;|||~' + encodeURIComponent('Pool, time; fun|x') + ',1105;|||;999,abc,1063,51|105|52,81,~%|66';

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
check('Saturday loaded custom + takeout entries', satEntries === 2);
check('Monday kept 5 valid entries, dropped 4 garbage tokens', monEntries === 5);
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

// Travel connectors: Fri has camp event (0) -> Story Land (63) -> ... -> Laser Tag (9, camp)
function collect(node, cls, out) {
  (node.children || []).forEach(c => {
    if ((c.className || '').includes(cls)) out.push(c.textContent);
    collect(c, cls, out);
  });
  return out;
}
const friTravel = collect(days[0], 'pl-travel', []);
check('Friday shows camp -> Story Land leg', friTravel.some(t => /~\d+ min from camp/.test(t)));
check('camp legs use calibrated guide times', friTravel.some(t => t.includes('~3 min from camp')));
check('Friday shows back-to-camp leg', friTravel.some(t => /~\d+ min back to camp/.test(t)));
check('narrative includes hop times', dyn.includes('🚗 ~'));

// On-the-way badges: Fri seq camp -> Story Land -> back to camp gives a detour verdict
function findEls(node, cls, out) {
  (node.children || []).forEach(c => {
    if ((c.className || '').includes(cls)) out.push(c);
    findEls(c, cls, out);
  });
  return out;
}
const badges = findEls(ids['pl-days'], 'pl-otw', []);
check('detour badges render', badges.length > 0 &&
  badges.every(b => / (on the way!|slight detour|out of the way!|easy dad run! 🥡)$/.test(b.textContent)));
check('food out-and-back reads easy dad run', badges.some(b => b.textContent.includes('easy dad run!')));
check('out-and-back never says out of the way', (() => {
  const monBadges = findEls(ids['pl-days'].children[3], 'pl-otw', []);
  // McD sits between two camp stops; its connector badge must not be a routing verdict
  return !monBadges.some(b => b.textContent.includes('out of the way') &&
    findEls(ids['pl-days'].children[3], 'pl-travel', []).indexOf(b) === 0);
})());
check('legs departing camp never judged out of the way', (() => {
  const monTravel = findEls(ids['pl-days'].children[3], 'pl-travel', []);
  const fromCampLegs = monTravel.filter(t => t.textContent.includes('from camp'));
  return fromCampLegs.length > 0 && fromCampLegs.every(t =>
    findEls(t, 'pl-otw', []).every(b => !b.textContent.includes('out of the way')));
})());
check('mid-route detours still get called out', (() => {
  // McD -> back to camp -> Funspot: the return-to-camp leg is a genuine mid-route detour
  const monBadges = findEls(ids['pl-days'].children[3], 'pl-otw', []);
  return monBadges.some(b => b.textContent.includes('out of the way'));
})());

// Focus mode: switch to Attractions tab, click Friday Morning slot (anchor = Story Land)
ids['pl-tabs'].children[4].listeners.click[0]();
const drops = findEls(ids['pl-days'].children[0], 'pl-drop', []);
drops[0].listeners.click[0]();
const dots = findEls(ids['pl-chips'], 'pl-dot', []);
check('focus mode colors palette chips', dots.length > 10);
check('focus note is visible with anchor name', ids['pl-focus'].hidden === false);
check('new attractions present (Attitash chip)',
  findEls(ids['pl-chips'], 'pl-chip', []).some(c => collect(c, 'nm', []).join('').includes('Attitash')));

// Takeout: Sat evening has McDonald's as a dad-run (1105)
const satCard = ids['pl-days'].children[1];
check('takeout entry gets send-dad checkbox', findEls(satCard, 'pl-togo', []).length > 0);
check('takeout connector shows each-way run', collect(satCard, 'pl-travel', []).some(t => t.includes("Dad's run") && t.includes('each way')));
check('regular food entries also get the checkbox', findEls(ids['pl-days'], 'pl-togo', []).length >= 1);
const dyn2 = ids['dyn-days'].innerHTML;
check('narrative sends dad for takeout', dyn2.includes('while <b>Dad</b> grabs <b>McDonald') && dyn2.includes('each way'));
check('share URL preserves takeout flag', new URL(global.__copied).searchParams.get('p').includes('1105'));

// Weather weaving: Saturday header + narrative pick up the stubbed forecast
check('builder day header shows forecast chip', collect(satCard, 'pl-wx', []).some(t => t.includes('81°/62°')));
check('dynamic plan title shows forecast chip', ids['dyn-days'].innerHTML.includes('🌧️ 81°/62°'));
check('planner exposes refresh hook for weather', typeof global.window.__plRefresh === 'function');
process.exit(fail);
