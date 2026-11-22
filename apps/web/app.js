/* Atlas local: dados, fontes, identidade visual e Leaflet servidos sem CDN. */
'use strict';
const $ = id => document.getElementById(id);
const state = {network: null, base: null, selected: null, direction: 'all', request: 0, loading: false, wasRunning: false};
const number = value => new Intl.NumberFormat('pt-BR').format(value);
const date = value => {
  if (!value) return 'Não informada';
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? String(value) : new Intl.DateTimeFormat('pt-BR', {dateStyle: 'short', timeStyle: 'short', timeZone: 'America/Fortaleza'}).format(parsed);
};
const sourceDate = value => {
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? String(value) : new Intl.DateTimeFormat('pt-BR', {dateStyle: 'short', timeZone: 'UTC'}).format(parsed);
};
const normalized = value => String(value || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
function element(tag, text, className) {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (className) node.className = className;
  return node;
}
function error(message) {
  $('global-error').textContent = message || '';
  $('global-error').hidden = !message;
}
async function api(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `Falha na consulta (${response.status})`);
  return data;
}
const pages = {
  atual: ['A cidade em movimento.', 'Explore os trajetos, consulte as linhas e conheça as fontes.'],
  proposta: ['Uma rede. Novas conexões.', 'Explore o estudo de uma rede integrada para João Pessoa.'],
};
function navigate() {
  if (location.hash === '#coletor') { location.href='/admin#observed'; return; }
  const view = Object.prototype.hasOwnProperty.call(pages, location.hash.slice(1)) ? location.hash.slice(1) : 'atual';
  for (const key of Object.keys(pages)) $(`view-${key}`).hidden = key !== view;
  document.querySelectorAll('[data-view]').forEach(link => {
    const active = link.dataset.view === view;
    link.classList.toggle('active', active);
    if (active) link.setAttribute('aria-current', 'page'); else link.removeAttribute('aria-current');
  });
  [$('page-title').textContent, $('page-description').textContent] = pages[view];
  document.title = `${view === 'atual' ? 'Rede atual' : view === 'proposta' ? 'Rede proposta' : 'Coletor SEMOB'} · Mobilidade JP`;
  if (view === 'proposta') window.loadProposal?.();
  if (view === 'atual') requestAnimationFrame(drawMap);
}
function featureCode(feature) { return String(feature.properties.line_code || feature.properties.CODIGO_LIN || ''); }
function lineFeatures() { return (state.network?.geojson.features || []).filter(feature => featureCode(feature) === state.selected); }
function visibleFeatures() {
  if (!state.selected) return state.network?.geojson.features || [];
  const features = lineFeatures();
  return state.direction === 'all' ? features : features.filter((_, index) => String(index) === state.direction);
}
async function loadNetwork(source) {
  const request = ++state.request;
  state.loading = true;
  error();
  $('network-notice').textContent = 'Carregando a base local…';
  try {
    const network = await api(`/api/network?source=${encodeURIComponent(source)}`);
    if (request !== state.request) return;
    state.network = network;
    state.selected = null;
    state.direction = 'all';
    $('search').value = '';
    $('source-label').textContent = network.label;
    $('source-date').textContent = `Última coleta: ${date(network.retrieved_at)}`;
    $('line-count').textContent = number(network.lines.length);
    $('route-count').textContent = number(network.geojson.features.length);
    $('stop-count').textContent = network.stops.features.length ? number(network.stops.features.length) : '—';
    $('show-stops').checked = false;
    $('show-stops').disabled = !network.stops.features.length;
    $('network-notice').textContent = network.warnings.join(' ') + (source === 'semob' ? ` Base local: ${network.lines.length} linhas com dados, catálogo consultado: ${network.catalog_count}.` : ' Horários e sequência de ruas estão disponíveis somente nas linhas coletadas da SEMOB.');
  } catch (exc) {
    if (request !== state.request) return;
    state.network = null;
    state.selected = null;
    state.direction = 'all';
    $('source-label').textContent = source === 'semob' ? 'SEMOB · sem coleta local' : 'Base indisponível';
    $('source-date').textContent = '';
    ['line-count', 'route-count', 'stop-count'].forEach(id => $(id).textContent = '—');
    $('network-notice').textContent = exc.message;
    $('show-stops').checked = false;
    $('show-stops').disabled = true;
  } finally {
    if (request === state.request) {
      state.loading = false;
      renderLines(); updateDirections(); renderDetail(); drawMap();
    }
  }
}
function renderLines() {
  const query = normalized($('search').value).trim();
  const lines = (state.network?.lines || []).filter(line => {
    const codeMatch = /^\d+$/.test(query) && line.code.replace(/^0+/, '') === query.replace(/^0+/, '');
    const text = [line.code, line.name, ...(line.names || []), ...line.itineraries.flatMap(item => item.streets)].join(' ');
    return !query || codeMatch || normalized(text).includes(query);
  });
  $('results-count').textContent = `${number(lines.length)} ${lines.length === 1 ? 'resultado' : 'resultados'}`;
  $('lines').replaceChildren();
  for (const line of lines) {
    const button = element('button', undefined, 'line-item' + (line.code === state.selected ? ' selected' : ''));
    button.type = 'button';
    button.setAttribute('aria-pressed', String(line.code === state.selected));
    const label = element('span', line.name, 'line-name');
    const count = state.network.geojson.features.filter(feature => featureCode(feature) === line.code).length;
    label.append(element('small', `${count} traçados${line.errors.length ? ' · coleta parcial' : ''}${line.in_latest_catalog === false ? ' · fora do catálogo consultado' : ''}`));
    button.append(element('span', line.code, 'line-code'), label);
    button.addEventListener('click', () => selectLine(line.code));
    $('lines').append(button);
  }
  if (!lines.length) {
    $('lines').append(element('p', state.network ? 'Nenhuma linha encontrada. Tente outro código, nome ou rua coletada.' : 'Faça uma coleta no painel administrativo ou escolha a referência histórica.', 'empty-state'));
  }
}
function selectLine(code) {
  state.selected = code; state.direction = 'all';
  renderLines(); updateDirections(); renderDetail(); drawMap();
}
function updateDirections() {
  const select = $('direction');
  select.replaceChildren(new Option('Todos os traçados', 'all'));
  lineFeatures().forEach((feature, index) => {
    const p = feature.properties;
    const name = p.ITINERARIO ? `${p.ITINERARIO} · ${p.ROUTE_LONG || p.LINHA || ''}` : `${p.direction_code ?? index} · ${p.direction_name || p.route_name || 'Variante'}`;
    select.add(new Option(name, String(index)));
  });
  select.value = state.direction;
  select.disabled = !state.selected || !lineFeatures().length;
  const line = state.network?.lines.find(item => item.code === state.selected);
  $('map-title').textContent = line ? `${line.code} · ${line.name}` : 'Visão geral dos trajetos';
  $('map-legend').textContent = line ? 'Ida em vermelho · volta em ocre, quando identificadas' : 'Traçados da base selecionada';
}
function renderDetail() {
  const root = $('line-detail'); root.replaceChildren();
  const line = state.network?.lines.find(item => item.code === state.selected);
  if (!line) {
    root.append(element('p', 'Selecione uma linha para consultar seus sentidos, itinerário e horários disponíveis.', 'empty-state')); return;
  }
  const header = element('div', undefined, 'detail-heading');
  const heading = element('div');
  heading.append(element('h2', `${line.code} · ${line.name}`));
  heading.append(element('p', `Coletado em ${date(line.retrieved_at)} · ${state.network.label}`));
  heading.append(element('p', `Atualização declarada pela fonte: ${line.source_updated_at.length ? line.source_updated_at.map(sourceDate).join(' / ') : 'não informada nesta base'}`));
  if (line.operator) heading.append(element('p', `Operador declarado: ${line.operator}`));
  if (line.names?.length > 1) heading.append(element('p', `Variantes na base: ${line.names.join(' / ')}`));
  const source = element('a', 'Consultar fonte', 'secondary');
  source.href = line.itinerary_url || 'https://s3.amazonaws.com/bus4.jpa.mapa/index.html';
  source.target = '_blank'; source.rel = 'noopener';
  header.append(heading, source); root.append(header);
  if (line.errors.length) root.append(element('p', 'Coleta parcial: ' + line.errors.map(item => `${({itineraries: 'itinerário', schedules: 'horários', geojson: 'geometria'})[item.field] || item.field}: ${item.message}`).join(' · '), 'notice error'));
  if (line.in_latest_catalog === false) root.append(element('p', 'Esta linha foi preservada de uma coleta anterior e não aparece no catálogo mais recente consultado. Confirme sua situação na fonte.', 'notice'));
  if (state.selected && !lineFeatures().length) root.append(element('p', 'Sem geometria disponível para esta linha. Os demais dados coletados continuam abaixo.', 'notice'));
  const grid = element('div', undefined, 'detail-grid');
  const itineraries = element('section'); itineraries.append(element('h3', 'Itinerário por sentido'));
  for (const [index, itinerary] of line.itineraries.entries()) {
    const item = element('details', undefined, 'itinerary'); item.open = index === 0;
    item.append(element('summary', `${itinerary.direction} · ${itinerary.variant}`));
    const streets = element('ol'); itinerary.streets.forEach(street => streets.append(element('li', street)));
    item.append(streets); itineraries.append(item);
  }
  if (!line.itineraries.length) itineraries.append(element('p', 'A sequência textual de ruas não está disponível nesta base. Consulte a fonte ou faça uma coleta da SEMOB.', 'muted'));
  const schedules = element('section'); schedules.append(element('h3', 'Horários publicados'));
  for (const schedule of line.schedules) {
    const block = element('div', undefined, 'schedule-block');
    block.append(element('h4', `${schedule.day}${schedule.declared_trips !== null ? ' · ' + schedule.declared_trips + ' viagens declaradas' : ''}`));
    const times = element('div', undefined, 'times');
    schedule.departures.forEach(time => times.append(element('span', time)));
    if (!schedule.departures.length) times.append(element('p', 'Nenhuma partida publicada neste quadro.', 'muted'));
    block.append(times); schedules.append(block);
  }
  schedules.append(element('p', line.schedules.length ? 'Dias e sentidos sem quadro publicado não permitem concluir ausência de serviço. Confira a informação na fonte.' : 'Não há horários disponíveis nesta base. Faça uma coleta da SEMOB ou consulte a página oficial.', 'muted'));
  grid.append(itineraries, schedules); root.append(grid);
}

let currentMap;
function drawMap() {
  if (!state.base || $('view-atual').hidden) return;
  if (!currentMap) currentMap = new TransitMap('network-map', state.resources, $('current-base'), selectLine);
  const features = visibleFeatures();
  currentMap.render(features, {selected: Boolean(state.selected), color: feature => String(feature.properties.ITINERARIO || '').toUpperCase().includes('VOLTA') || String(feature.properties.direction_code) === '1' ? '#bc742b' : '#c71020'});
  const stops = $('show-stops').checked && state.network ? state.network.stops.features.map(f => ({position: f.geometry.coordinates, label: `${f.properties.stop_name} · ${f.properties.address || ''}`})) : [];
  currentMap.markers(stops);
}

$('source').addEventListener('change', () => loadNetwork($('source').value));
$('search').addEventListener('input', renderLines);
$('show-all').addEventListener('click', () => { state.selected = null; state.direction = 'all'; $('search').value = ''; renderLines(); updateDirections(); renderDetail(); drawMap(); });
$('direction').addEventListener('change', () => { state.direction = $('direction').value; drawMap(); });
$('show-stops').addEventListener('change', drawMap);
$('reset-map').addEventListener('click', drawMap);
$('zoom-in').addEventListener('click', () => currentMap?.map.zoomIn());
$('zoom-out').addEventListener('click', () => currentMap?.map.zoomOut());
window.addEventListener('hashchange', navigate);
navigate();
(async () => {
  try { state.resources = await mapResources; state.base = state.resources.base; const status = await api('/api/status'); const source = status.semob_available ? 'semob' : 'historical'; $('source').value = source; await loadNetwork(source); }
  catch (exc) { error(`Não foi possível iniciar o atlas: ${exc.message}. Confira se o servidor local está em execução.`); }
})();
