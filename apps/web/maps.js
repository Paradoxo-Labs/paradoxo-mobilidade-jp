'use strict';
window.mapResources = Promise.all([
  fetch('/api/base').then(r => { if (!r.ok) throw new Error('Cartografia local indisponível'); return r.json(); }),
  fetch('/api/map-sources').then(r => { if (!r.ok) throw new Error('Fontes cartográficas indisponíveis'); return r.json(); }),
]).then(([base, sources]) => ({base, sources: sources.sources}));

window.TransitMap = class {
  constructor(id, resources, select, onSelect) {
    this.map = L.map(id, {zoomControl: false, minZoom: 8, maxZoom: 19, zoomSnap: .25});
    this.map.createPane('localBase');
    this.map.getPane('localBase').style.zIndex = 350;
    this.map.getPane('localBase').style.pointerEvents = 'none';
    this.map.setView([-7.14, -34.86], 12);
    this.map.attributionControl.addAttribution('Filipeia · IBGE · © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>');
    L.control.scale({imperial: false, position: 'bottomleft'}).addTo(this.map);
    L.control.zoom({position: 'bottomright'}).addTo(this.map);
    this.routes = L.featureGroup().addTo(this.map);
    this.points = L.layerGroup().addTo(this.map);
    this.context = L.layerGroup().addTo(this.map);
    this.comparison = L.featureGroup().addTo(this.map);
    this.onSelect = onSelect;
    this.resources = resources;
    this.select = select;
    for (const source of resources.sources) select.add(new Option(source.label, source.id));
    select.addEventListener('change', () => this.setBase(select.value));
    this.local = L.layerGroup();
    const add = (features, style) => L.geoJSON({type: 'FeatureCollection', features: features.filter(Boolean)}, {style, interactive: false, pane: 'localBase'}).addTo(this.local);
    add(resources.base.land, {fillColor: '#eeeee7', fillOpacity: 1, color: '#bbbcb4', weight: .8});
    add(resources.base.neighborhoods, {fillColor: '#f5f4ef', fillOpacity: .75, color: '#d0cec4', weight: .6});
    add(resources.base.rivers, {fillColor: '#c5dce0', fillOpacity: 1, color: '#a9cbd1', weight: .5});
    add(resources.base.roads, {color: '#c6bfb4', weight: 1.3, fill: false});
    this.setBase('streets');
    this.observer = new ResizeObserver(() => this.map.invalidateSize({animate: false}));
    this.observer.observe(document.getElementById(id));
  }
  setBase(id) {
    if (this.tiles) { this.tiles.remove(); this.tiles = null; }
    this.local.remove();
    const source = this.resources.sources.find(item => item.id === id) || this.resources.sources[0];
    this.map.setMaxZoom(source.maxZoom || 19);
    this.select.value = source.id;
    const note = document.getElementById(this.map.getContainer().id === 'proposal-map' ? 'proposal-map-note' : 'current-map-note');
    note.textContent = source.id === 'local' ? 'Cartografia local · Filipeia / IBGE · sem internet' : `${source.label} · requer internet`;
    if (source.id === 'local') { this.local.addTo(this.map); return; }
    const tiles = this.tiles = L.tileLayer(source.url, {attribution: source.attribution, maxZoom: source.maxZoom, referrerPolicy: 'strict-origin-when-cross-origin'}).addTo(this.map);
    let failed = false;
    tiles.on('tileerror', () => {
      if (!failed && this.tiles === tiles) {
        failed = true; this.setBase('local');
        note.textContent = 'Fundo online indisponível · cartografia local preservada';
      }
    });
  }
  tooltip(text) { const label = document.createElement('span'); label.textContent = text; return label; }
  render(features, {color = () => '#c71020', selected = false, fit = true} = {}) {
    this.routes.clearLayers(); this.comparison.clearLayers();
    if (selected) L.geoJSON({type: 'FeatureCollection', features}, {style: {color: '#fff', weight: 8, opacity: .95}, interactive: false}).addTo(this.routes);
    L.geoJSON({type: 'FeatureCollection', features}, {
      style: f => ({color: color(f), weight: selected ? 4 : 2.5, opacity: selected ? 1 : .8, lineCap: 'round'}),
      onEachFeature: (feature, layer) => {
        const p = feature.properties;
        const code = String(p.codigo || p.line_code || p.CODIGO_LIN || '');
        const label = `${code} · ${p.nome || p.LINHA || p.route_name || ''} · ${p.sentido || p.ITINERARIO || p.direction_name || ''}`;
        layer.bindTooltip(this.tooltip(label), {sticky: true});
        layer.on('click', () => this.onSelect?.(code));
        layer.on('add', () => {
          const el = layer.getElement();
          if (el) {
            el.setAttribute('data-code', code); el.setAttribute('tabindex', '0'); el.setAttribute('role', 'button'); el.setAttribute('aria-label', label);
            el.addEventListener('keydown', event => { if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); this.onSelect?.(code); } });
          }
        });
      },
    }).addTo(this.routes);
    if (fit) this.fit();
  }
  fit() {
    this.map.invalidateSize({animate: false});
    const bounds = this.comparison.getLayers().length ? this.comparison.getBounds() : this.routes.getBounds();
    if (bounds.isValid()) this.map.fitBounds(bounds, {padding: [38, 38], maxZoom: 16, animate: false});
  }
  markers(items) {
    this.points.clearLayers();
    for (const item of items) {
      const point = L.circleMarker([item.position[1], item.position[0]], {radius: item.terminal ? 6 : item.kind === 'station' ? 5 : 3, color: '#111112', weight: 2, fillColor: item.terminal || item.kind === 'station' ? '#fff' : '#ed2633', fillOpacity: 1, className: 'transit-reference'});
      point.bindTooltip(this.tooltip(item.short || item.label), {permanent: Boolean(item.terminal || item.kind === 'station'), direction: 'top', className: 'terminal-label', offset: [0, -6]});
      if (item.terminal || item.kind === 'station') point.bindPopup(this.tooltip(item.label));
      point.addTo(this.points);
    }
  }
  compare(data) {
    this.comparison.clearLayers();
    for (const [field, color, dashArray] of [['before', '#6b6b6b', '8 6'], ['after', '#c71020', null]]) {
      L.polyline(data[field].map(([x, y]) => [y, x]), {color, weight: 5, dashArray}).bindTooltip(this.tooltip(field === 'before' ? 'Revisão anterior' : 'Proposta atualizada')).addTo(this.comparison);
    }
    this.fit();
  }
};
