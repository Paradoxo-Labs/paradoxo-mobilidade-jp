const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const { parseHTML } = require('linkedom');
const html = fs.readFileSync(require('node:path').join(__dirname, '..', 'mapa-rede-joao-pessoa-revisada.html'), 'utf8');
const { window, document } = parseHTML('<html><body>' + html + '</body></html>');
const svg = document.querySelector('svg');
const select = document.querySelector('select');
const data = JSON.parse(document.getElementById('mgb-geodados').textContent);
assert.deepEqual(data.routes.map(route => route.code), ['BRS-100', 'BRS-200', 'BRS-300', 'BRS-500', 'BRS-501', 'BRS-800', 'T-410', 'T-610', 'TRV-321', 'TRV-322', 'TRV-721', 'I-331', 'I-332', 'I-333', 'I-334', 'I-731', 'R-241', 'R-242', 'R-343', 'L-251', 'L-351', 'L-751', 'M-961']);
const expanded = data.routes.find(route => route.code === 'TRV-322');
const stops = code => data.routes.find(route => route.code === code).points;
assert.deepEqual(stops('TRV-321').slice(-3), ['manaira', 'shopping', 'bessa']);
assert.deepEqual(stops('T-610').slice(0, 4), ['bessa', 'shopping', 'ipes', 'mandacaru']);
assert.deepEqual(stops('BRS-800'), ['aeroporto', 'oitizeiro', 'cristo', 'universidade', 'shopping', 'bessa']);
assert.deepEqual(stops('R-242').slice(1, 5), ['agua_fria', 'jardim_sp', 'edmilson', 'colibris']);
assert.deepEqual(stops('I-731'), ['val', 'geisel', 'cristo']);
assert.deepEqual(stops('L-251'), ['cristo', 'rangel', 'vale_palmeiras', 'cristo']);
assert.deepEqual(stops('I-331'), ['hub', 'josefa', 'val1', 'val']);
assert.deepEqual(stops('I-332'), ['hub', 'garrafao', 'trauminha', 'porfirio', 'severino_dias', 'maria_ines', 'sibipiruna', 'paratibe', 'felix_cahino', 'humberto', 'jacaranda', 'mucu', 'clodoaldo', 'severina', 'balbina', 'joao_maria', 'parque', 'val']);
assert.deepEqual(stops('M-961'), ['hub', 'jacarape_acesso', 'jacaranda', 'pb008', 'jacuma']);
assert.deepEqual(stops('L-751').slice(0, 4), ['val', 'oliveiras', 'maria_ana', 'cedros']);
assert.deepEqual(stops('L-351').slice(2, 6), ['diogenes', 'corujinha', 'josefa_sul', 'euclides']);
assert.deepEqual(stops('R-343').slice(-8), ['alfredo_inicio', 'alfredo_meio', 'anizio', 'josefa_sul', 'corujinha', 'trauminha', 'detran', 'hub']);
assert.deepEqual(stops('I-334').slice(-6), ['josefa', 'anizio', 'alfredo_meio', 'alfredo_inicio', 'hilton_leste', 'hub']);
assert.ok(data.routes.every(route => route.traces.every(trace => trace.length > 15)));
assert.deepEqual(expanded.points.filter(point => ['hub', 'convencoes', 'boulevard', 'penha', 'estacao', 'cristo', 'coqueiral', 'josefa', 'mangabeira_67'].includes(point)), ['hub', 'convencoes', 'boulevard', 'penha', 'estacao', 'cristo', 'hub']);
assert.ok(data.places.cristo.label.includes('Almeidão'));
assert.ok(select.querySelector('[value="all"]').hasAttribute('selected'));
let width, height, resize;
let selected = 'all';
Object.defineProperties(svg, {clientWidth:{get:()=>width}, clientHeight:{get:()=>height}});
Object.defineProperty(select, 'value', {get:()=>selected});
window.Element.prototype.getComputedTextLength = function () { return this.textContent.length * 6; };
const main = Array.from(document.querySelectorAll('script')).at(-1).textContent.replace('  function draw() {', '  window.parallelTraces = parallelTraces;\n  function draw() {');
const d3 = fs.readFileSync(__dirname + '/d3.js', 'utf8');
const context = vm.createContext({window, document, ResizeObserver:class{observe(){resize=this.cb;}constructor(cb){this.cb=cb;}}});
function run() {
  vm.runInContext(d3 + '\nwindow.d3 = d3;\n' + main, context);
  const scenario = window.parallelTraces([
    {order: 0, points: [[0, 0], [40, 0]]},
    {order: 1, points: [[40, .15], [20, .15], [0, .15]]},
    {order: 2, points: [[20, -15], [20, 15]]},
  ], .4);
  assert.ok(Math.abs(scenario[0].points[6][1] + 1.525) < .1);
  assert.ok(Math.abs(scenario[1].points[6][1] - 1.525) < .1);
  assert.ok(scenario[2].points.every(([x]) => x === 20));
  for (const w of [320, 736]) {
    width = w;
    height = w === 320 ? 465 : 540;
    for (const [key, comparison] of Object.entries(data.comparisons)) {
      selected = key;
      select.dispatchEvent(new window.Event('change'));
      resize();
      const paths = Array.from(svg.querySelectorAll('.mgb-comparison path'));
      assert.equal(paths.length, 2);
      assert.notEqual(paths[0].getAttribute('d'), paths[1].getAttribute('d'));
      assert.equal(svg.querySelectorAll('.mgb-reference-stop').length, comparison.stops.length);
      assert.ok(document.querySelector('.mgb-legend').textContent.includes('Proposta atualizada'));
      if (w === 736) fs.writeFileSync(__dirname + '/verificar-' + key + '.svg', svg.outerHTML);
    }
    selected = 'recorte';
    select.dispatchEvent(new window.Event('change'));
    resize();
    assert.equal(select.querySelectorAll('option').length, 30);
    assert.equal(svg.querySelectorAll('.mgb-neighborhood').length, 64);
    const focusedCodes = Array.from(svg.querySelectorAll('[data-code]'), element => element.getAttribute('data-code'));
    assert.deepEqual(focusedCodes, ['TRV-322', 'I-331', 'I-332', 'I-333', 'I-334', 'R-343', 'L-351']);
    assert.ok(document.querySelector('.mgb-route').textContent.includes('7 linhas no mapa'));
    assert.ok(!document.querySelector('.mgb-legend').textContent.includes('BRS'));
    assert.equal(document.querySelectorAll('.mgb-legend .mgb-swatch').length, 7);
    assert.equal(new Set(Array.from(svg.querySelectorAll('[data-code]'), el => el.querySelector('path').getAttribute('stroke'))).size, 7);
    if(w === 736) fs.writeFileSync(__dirname + '/check.svg', svg.outerHTML);
    selected = 'all';
    select.dispatchEvent(new window.Event('change'));
    assert.equal(svg.querySelectorAll('[data-code]').length, 23);
    assert.equal(new Set(Array.from(svg.querySelectorAll('[data-code]'), el => el.querySelector('path').getAttribute('stroke'))).size, 23);
    assert.ok(Array.from(svg.querySelectorAll('path')).every(path => !path.getAttribute('d')?.includes('NaN')));
    assert.ok(svg.textContent.includes('T. Mangabeira'));
    const allColors = new Map(Array.from(svg.querySelectorAll('[data-code]'), el => [el.getAttribute('data-code'), el.querySelector('path').getAttribute('stroke')]));
    for (const [group, n] of [['brs', 6], ['cristo', 7], ['valentina', 6]]) {
      selected = group;
      select.dispatchEvent(new window.Event('change'));
      assert.equal(svg.querySelectorAll('[data-code]').length, n);
    }
    for (const route of data.routes) {
      selected = route.code;
      select.dispatchEvent(new window.Event('change'));
      assert.equal(svg.querySelectorAll('[data-code]').length, 1);
      assert.ok(svg.querySelector(`[data-code="${route.code}"]`));
      assert.equal(svg.querySelector('[data-code] path').getAttribute('stroke'), allColors.get(route.code));
      assert.ok(document.querySelector('.mgb-route').textContent.includes(route.code));
      assert.ok(svg.querySelector('desc').textContent.includes(route.itinerary));
    }
    console.log(`${w}px: 23 linhas, filtros, comparações de Paratibe e Parque do Sol e todas as seleções conferidos`);
  }
}
try {
  run();
} catch(error) {
  console.error(error.constructor.name, error.message);
  console.error(error.stack.split('\n').filter(line => line.startsWith('    at')).slice(0,7).join('\n'));
  process.exitCode = 1;
}
