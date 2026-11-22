/* Visualização da revisão ativa; o estudo importado permanece preservado como histórico. */
(() => {
  const classes = {
    brs: {name: 'BRS', color: '#c71020'}, troncal: {name: 'Troncal', color: '#294e80'},
    transversal: {name: 'Transversal', color: '#915c9c'}, integracional: {name: 'Integracional', color: '#08756c'},
    regional: {name: 'Regional', color: '#b47316'}, local: {name: 'Local', color: '#785c42'}, metropolitana: {name: 'Metropolitana', color: '#5150ae'},
  };
  let data, map, loading, selected = null, direction = 'all';
  const filtered = () => data.catalog.linhas.filter(line => {
    const group = $('proposal-class').value;
    const query = normalized($('proposal-search').value);
    return (group === 'all' || line.type === group) && normalized(`${line.code} ${line.name} ${line.itinerary}`).includes(query);
  });
  const features = () => data.geojson.features.filter(f => selected ? f.properties.codigo === selected : filtered().some(line => line.code === f.properties.codigo)).filter(f => direction === 'all' || f.properties.sentido === direction);
  function select(code) {
    selected = code; direction = 'all'; $('proposal-comparison').value = '';
    render();
  }
  function legend(comparison = false) {
    $('proposal-legend').replaceChildren();
    const groups = comparison ? [{name: 'Revisão anterior · tracejada', color: '#6b6b6b'}, {name: 'Proposta atualizada', color: '#c71020'}] : Object.entries(classes).filter(([key]) => filtered().some(line => line.type === key)).map(([, value]) => value);
    for (const group of groups) {
      const item = element('span'); const swatch = element('i', '', 'swatch'); swatch.style.background = group.color;
      item.append(swatch, document.createTextNode(group.name)); $('proposal-legend').append(item);
    }
  }
  function render() {
    if (!data || !map) return;
    const lines = filtered();
    $('proposal-count').textContent = `${lines.length} serviços`;
    $('proposal-lines').replaceChildren();
    for (const line of lines) {
      const button = element('button', undefined, 'line-item' + (selected === line.code ? ' selected' : ''));
      button.type = 'button'; button.setAttribute('aria-pressed', String(selected === line.code));
      const code = element('span', line.code, 'line-code'); code.style.setProperty('--route-color', classes[line.type].color);
      const name = element('span', line.name, 'line-name');
      name.append(element('small', `${classes[line.type].name} · ${line.sentidos.length} ${line.sentidos.length === 1 ? 'traçado' : 'sentidos'}`));
      button.append(code, name); button.addEventListener('click', () => select(line.code)); $('proposal-lines').append(button);
    }
    if (!lines.length) $('proposal-lines').append(element('p', 'Nenhum serviço encontrado para esse filtro.', 'empty-state'));
    const line = data.catalog.linhas.find(line => line.code === selected);
    $('proposal-map-title').textContent = line ? `${line.code} / ${line.name}` : 'Conexões propostas';
    const directionSelect = $('proposal-direction'); directionSelect.replaceChildren(new Option('Todos os sentidos', 'all'));
    for (const entry of line?.sentidos || []) directionSelect.add(new Option(['circuito', 'circular'].includes(entry.sentido) ? 'Circuito' : entry.sentido === 'ida' ? 'Ida' : 'Volta', entry.sentido));
    directionSelect.value = direction; directionSelect.disabled = !line;
    map.render(features(), {selected: Boolean(line), color: feature => classes[feature.properties.classe]?.color || '#c71020'});
    renderPoints(line); legend(); detail(line);
  }
  function renderPoints(line) {
    const names = {hub: 'Mangabeira', metro: 'Varadouro / TIV', bessa: 'Bessa', oitizeiro: 'Oitizeiro / novo mercado', cristo: 'Cristo', val: 'Valentina', universidade: 'Est. Cidade Universitária', lagoa: 'Terminal da Lagoa'};
    const markers = $('proposal-terminals').checked ? Object.entries(names).filter(([key]) => data.catalog.lugares[key]).map(([key, short]) => ({...data.catalog.lugares[key], terminal: true, short, label: data.catalog.lugares[key].label + ' · integração proposta'})) : [];
    if (line && $('proposal-points').checked) {
      const keys = new Set(line.sentidos.filter(s => direction === 'all' || s.sentido === direction).flatMap(s => s.waypoints));
      for (const key of keys) {
        const position = data.waypoints[key];
        if (position) markers.push({position, label: data.catalog.lugares[key]?.label || key.replaceAll('_', ' ')});
      }
    }
    map.markers(markers);
  }
  function detail(line) {
    const root = $('proposal-detail'); root.replaceChildren();
    if (!line) { root.append(element('p', 'Escolha um serviço para explorar o itinerário, os sentidos e as conexões propostas.', 'empty-state')); return; }
    const heading = element('div', undefined, 'detail-heading');
    const title = element('div'); title.append(element('p', classes[line.type].name + ' / SERVIÇO PROPOSTO', 'eyebrow'), element('h2', `${line.code} · ${line.name}`));
    heading.append(title, element('span', 'REVISÃO / 21.11.2026', 'revision')); root.append(heading);
    const grid = element('div', undefined, 'detail-grid');
    const itinerary = element('section'); itinerary.append(element('h3', 'Itinerário proposto'), element('p', line.itinerary, 'route-itinerary'));
    if (line.note) itinerary.append(element('p', line.note, 'muted'));
    const paths = element('section'); paths.append(element('h3', 'Traçados por sentido'));
    for (const entry of line.sentidos) {
      const item = element('div', undefined, 'path-summary');
      const km = new Intl.NumberFormat('pt-BR', {maximumFractionDigits: 2}).format(entry.distancia_km);
      item.append(element('strong', `${entry.sentido.toUpperCase()} / ${km} km`), element('span', `${entry.waypoints.length} referências de roteamento`)); paths.append(item);
      if (entry.observed_streets_percent !== undefined) item.append(element('span', `${entry.observed_streets_percent.toLocaleString('pt-BR')}% do traçado em ruas com referência na rede observada`));
      if (entry.central_pattern) item.append(element('p', 'Varadouro: acesso do TIV e passagem pela Lagoa conforme o padrão SEMOB da 0301, neste sentido.', 'muted'));
      if (entry.street_sequence?.length) {
        const streets = element('details', undefined, 'itinerary');
        streets.append(element('summary', 'Ver sequência de vias da revisão'));
        const list = element('ol'); entry.street_sequence.forEach(street => list.append(element('li', street)));
        streets.append(list); item.append(streets);
      }
    }
    paths.append(element('p', 'Extensões aproximadas. Continuidade dos corredores em vias públicas, com referências da rede observada; isso não mede demanda ou frequência. Referências não equivalem a paradas. Conversões, gabarito e acessos de novos terminais ainda exigem validação.', 'muted'));
    grid.append(itinerary, paths); root.append(grid);
  }
  window.loadProposal = async () => {
    if (map) { map.map.invalidateSize({animate: false}); return; }
    if (loading) return loading;
    loading = (async () => {
      try {
        const [proposal, resources] = await Promise.all([api('/api/proposal'), mapResources]); data = proposal;
        for (const [value, group] of Object.entries(classes)) $('proposal-class').add(new Option(group.name, value));
        map = new TransitMap('proposal-map', resources, $('proposal-base'), select);
        render();
      } catch (exc) { error(`Não foi possível abrir a proposta: ${exc.message}`); loading = null; }
    })();
    return loading;
  };
  for (const id of ['proposal-search', 'proposal-class']) $(id).addEventListener(id === 'proposal-search' ? 'input' : 'change', () => { selected = null; direction = 'all'; $('proposal-comparison').value = ''; render(); });
  $('proposal-all').addEventListener('click', () => { $('proposal-search').value = ''; $('proposal-class').value = 'all'; select(null); });
  $('proposal-direction').addEventListener('change', () => { direction = $('proposal-direction').value; render(); });
  for (const id of ['proposal-terminals', 'proposal-points']) $(id).addEventListener('change', () => { if (data) renderPoints(data.catalog.linhas.find(line => line.code === selected)); });
  $('proposal-fit').addEventListener('click', () => map?.fit());
  $('proposal-fullscreen').addEventListener('click', async () => {
    try { if (document.fullscreenElement) await document.exitFullscreen(); else await $('proposal-canvas').requestFullscreen(); }
    catch { error('O navegador não disponibilizou o modo de tela cheia. O mapa continua disponível nesta página.'); }
  });
  document.addEventListener('fullscreenchange', () => { $('proposal-fullscreen').textContent = document.fullscreenElement ? 'Sair da tela cheia' : 'Tela cheia'; map?.map.invalidateSize({animate: false}); });
  $('proposal-comparison').addEventListener('change', () => {
    const key = $('proposal-comparison').value;
    if (!data) return;
    if (!key) { render(); return; }
    $('proposal-search').value = ''; $('proposal-class').value = 'all'; selected = 'I-332'; direction = 'all'; render();
    map.render([], {fit: false}); map.compare(data.comparisons[key]); legend(true);
    $('proposal-map-title').textContent = `I-332 / ${data.comparisons[key].name} · antes e depois`;
    map.markers((data.comparisons[key].stops || []).map(position => ({position, label: 'Parada de referência histórica'})));
  });
  if (!$('view-proposta').hidden) window.loadProposal();
})();
