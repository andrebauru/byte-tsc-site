// Dependency-free integration tests with an isolated DOM/storage harness.
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const source = fs.readFileSync(require('node:path').join(__dirname, '../assets/js/lang.js'), 'utf8');
let count = 0;
function test(name, fn) { fn(); console.log('ok ' + name); count++; }
function boot({root = false, saved, legacy, locales = ['ja'], hash = '', blocked = false} = {}) {
  const storage = new Map(saved ? [['rbm-pref-lang', saved]] : []);
  if (legacy) storage.set('bytetsc-pref-lang', legacy);
  const events = {};
  const nodes = ['ja', 'en', 'pt'].map(lang => ({
    attrs: {'data-lang': lang}, events: {},
    getAttribute(k) { return this.attrs[k]; },
    setAttribute(k,v) { this.attrs[k] = v; },
    addEventListener(k, f) { (this.events[k] ||= []).push(f); },
    click() { this.events.click.forEach(f => f.call(this)); }
  }));
  const classes = new Set();
  const button = {attrs:{}, setAttribute(k,v){this.attrs[k]=v;}, addEventListener(k,f){this[k]=f;}};
  const location = {hash, search:'?q=1', replace(v){this.destination=v;}};
  const window = {location, RBM: {}, localStorage: {
    getItem(k){if(blocked) throw Error(); return storage.get(k);},
    setItem(k,v){if(blocked) throw Error(); storage.set(k,v);}
  }, addEventListener(k,f){(events[k] ||= []).push(f);}, matchMedia(){return {matches:true,addListener(){}};}};
  const document = {readyState:'complete', documentElement: {lang:root?'ja':'en', getAttribute(k){return {'data-root-page':String(root),'data-alt-ja':'/','data-alt-en':'/en/','data-alt-pt':'/pt/'}[k];}},
    querySelectorAll(){return [{querySelectorAll(){return nodes;}}];},
    querySelector(s){return s === '.menu-toggle' ? button : {};},
    body:{classList:{add(v){classes.add(v);},toggle(v){if(classes.has(v)){classes.delete(v); return false;} classes.add(v); return true;}}}
  };
  vm.runInNewContext(source, {window, document, navigator:{languages:locales}});
  return {window, location, storage, nodes, classes, button,
    hash(v){location.hash=v; (events.hashchange||[]).forEach(f=>f());}};
}
test('root detects EN with query and anchor',()=>assert.equal(boot({root:true,locales:['fr','en-US'],hash:'#faq'}).location.destination,'/en/?q=1#faq'));
test('root detects PT',()=>assert.equal(boot({root:true,locales:['pt-BR']}).location.destination,'/pt/?q=1'));
test('saved manual preference wins',()=>assert.equal(boot({root:true,saved:'pt',locales:['en']}).location.destination,'/pt/?q=1'));
test('saved Japanese overrides English',()=>assert.equal(boot({root:true,saved:'ja',locales:['en']}).location.destination,undefined));
test('unsupported languages fall back to Japanese',()=>assert.equal(boot({root:true,locales:['fr']}).location.destination,undefined));
test('invalid saved preference is ignored',()=>assert.equal(boot({root:true,saved:'xx',locales:['en']}).location.destination,'/en/?q=1'));
test('blocked storage does not break detection',()=>assert.equal(boot({root:true,blocked:true,locales:['pt']}).location.destination,'/pt/?q=1'));
test('localized pages never redirect',()=>assert.equal(boot({saved:'pt',locales:['pt']}).location.destination,undefined));
test('manual choice persists and wins on reload',()=>{const x=boot();x.nodes[2].click();assert.equal(boot({root:true,saved:x.storage.get('rbm-pref-lang'),locales:['en']}).location.destination,'/pt/?q=1');});
test('switch preserves initial anchor',()=>assert.equal(boot({hash:'#faq'}).nodes[2].attrs.href,'/pt/#faq'));
test('same-page anchor changes update language links',()=>{const x=boot();x.hash('#development');assert.equal(x.nodes[2].attrs.href,'/pt/#development');});
test('click refreshes anchor even before hashchange',()=>{const x=boot();x.location.hash='#project';x.nodes[2].click();assert.equal(x.nodes[2].attrs.href,'/pt/#project');});
test('active language has accessible marker',()=>assert.equal(boot().nodes[1].attrs['aria-current'],'true'));
test('mobile menu state and aria-expanded stay synchronized',()=>{const x=boot();assert(x.classes.has('nav-closed'));assert.equal(x.button.attrs['aria-expanded'],'false');x.button.click();assert(!x.classes.has('nav-closed'));assert.equal(x.button.attrs['aria-expanded'],'true');x.button.click();assert(x.classes.has('nav-closed'));assert.equal(x.button.attrs['aria-expanded'],'false');});
test('legacy preference migrates on the same origin',()=>{const x=boot({root:true,legacy:'pt',locales:['en']});assert.equal(x.location.destination,'/pt/?q=1');assert.equal(x.storage.get('rbm-pref-lang'),'pt');});
test('new preference wins over legacy preference',()=>assert.equal(boot({root:true,saved:'ja',legacy:'pt',locales:['en']}).location.destination,undefined));
test('invalid legacy preference is ignored',()=>assert.equal(boot({root:true,legacy:'xx',locales:['en']}).location.destination,'/en/?q=1'));
console.log(`All ${count} DOM integration tests passed.`);
