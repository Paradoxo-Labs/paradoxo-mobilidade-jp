'use strict';
S.dragSpan = 350;
S.dragRoadCache = new Map();
function routeDragSidebar() {
  return `<h3>Arraste a própria rota</h3><p>Segure a linha e leve para outra rua. O marcador só encaixa nas ruas disponíveis.</p><div id="drag-street-status" class="route-status" role="status">Carregando ruas para edição…</div><label>Alcance de cada lado<select id="drag-span"><option value="350" ${S.dragSpan === 350 ? 'selected' : ''}>Curto · 350 m</option><option value="700" ${S.dragSpan === 700 ? 'selected' : ''}>Médio · 700 m</option><option value="1200" ${S.dragSpan === 1200 ? 'selected' : ''}>Longo · 1,2 km</option></select></label><p class="muted">Ao soltar, confira a prévia e aplique. O restante do percurso é mantido. Em ruas compartilhadas pelo circuito, escolha a passagem.</p>${S.preview?.drag_street ? `<div class="note"><strong>Rua escolhida</strong><p>${esc(S.preview.drag_street)}</p></div>` : ''}<button data-route-advanced="true">Ferramentas avançadas</button><p class="muted">Referências, cortes e trechos preservados continuam disponíveis nas ferramentas avançadas.</p>`;
}
function lineProjection(p, a, b) {
  const dx = b.x - a.x,
    dy = b.y - a.y,
    l = dx * dx + dy * dy;
  const fraction = l
    ? Math.max(0, Math.min(1, ((p.x - a.x) * dx + (p.y - a.y) * dy) / l))
    : 0;
  const point = L.point(a.x + fraction * dx, a.y + fraction * dy);
  return { point, fraction, distance: point.distanceTo(p) };
}
function routeGrabCandidates(map, coords, p) {
  if (coords.length < 2) return [];
  const all = [];
  for (let i = 0; i < coords.length - 1; i++) {
    const a = map.latLngToContainerPoint([coords[i][1], coords[i][0]]),
      b = map.latLngToContainerPoint([coords[i + 1][1], coords[i + 1][0]]);
    if (a.distanceTo(b) < 0.05) continue;
    const hit = lineProjection(p, a, b);
    if (hit.distance <= 13) all.push({ ...hit, index: i });
  }
  if (!all.length) return [];
  const best = Math.min(...all.map((x) => x.distance)),
    near = all.filter((x) => x.distance <= best + 2);
  const groups = [];
  for (const item of near) {
    const group = groups.at(-1);
    if (group && item.index <= group.at(-1).index + 1) group.push(item);
    else groups.push([item]);
  }
  const firstDirection = [
    coords[1][0] - coords[0][0],
    coords[1][1] - coords[0][1],
  ];
  const lastDirection = [
    coords.at(-1)[0] - coords.at(-2)[0],
    coords.at(-1)[1] - coords.at(-2)[1],
  ];
  const seamContinues =
    firstDirection[0] * lastDirection[0] +
      firstDirection[1] * lastDirection[1] >=
    0;
  if (
    groups.length > 1 &&
    seamContinues &&
    same(coords[0], coords.at(-1)) &&
    groups[0][0].index === 0 &&
    groups.at(-1).at(-1).index === coords.length - 2
  )
    groups[0] = groups.pop().concat(groups[0]);
  return groups.map((group) => ({
    ...group.reduce((a, b) => (a.distance <= b.distance ? a : b)),
    indices: group.map((x) => x.index),
  }));
}
function routeDirection(coords, index) {
  const a = coords[index],
    b = coords[index + 1],
    dx = (b[0] - a[0]) * 110440,
    dy = (b[1] - a[1]) * 110580;
  return Math.abs(dy) > Math.abs(dx)
    ? dy > 0
      ? '↑ norte'
      : '↓ sul'
    : dx > 0
      ? '→ leste'
      : '← oeste';
}
function installRouteDragging(map, feature) {
  if (feature.geometry.coordinates.length < 2 || S.advancedEditor) return;
  const coords = feature.geometry.coordinates,
    pathId = feature.properties.path_id,
    did = S.draft.id;
  const container = map.getContainer();
  container.classList.add('route-drag-enabled');
  let destroyed = false,
    roads = [],
    loading = false,
    pendingLoad = false,
    loadedKey = null,
    loadTimer,
    drag = null,
    hover = null,
    ghost = null,
    chosen = null;
  const status = (text, error = false) => {
    const n = $('#drag-street-status');
    if (!destroyed && n) {
      n.textContent = text;
      n.classList.toggle('error', error);
    }
  };
  const ready = () =>
    !destroyed &&
    S.screen === 'editor' &&
    S.maps.includes(map) &&
    S.draft?.id === did &&
    current()?.properties.path_id === pathId;
  const active = () => ready() && S.mode === 'drag';
  map.loadDragRoads = async () => {
    if (!ready()) return;
    if (loading) {
      pendingLoad = true;
      return;
    }
    if (!S.router.ready) {
      status('Preparando a malha de ruas…');
      return;
    }
    if (map.getZoom() < 14) {
      roads = [];
      status('Aproxime o mapa para arrastar a linha pelas ruas.');
      return;
    }
    const b = map.getBounds().pad(0.03),
      bbox = [b.getWest(), b.getSouth(), b.getEast(), b.getNorth()]
        .map((x) => x.toFixed(5))
        .join(',');
    const key = [
      pathId,
      S.payload.line.routing_policy || S.payload.line.code,
      bbox,
      S.router.fingerprint,
    ].join('|');
    if (key === loadedKey) {
      if (!drag)
        status(
          S.mode === 'drag'
            ? 'Segure um trecho da linha e arraste para outra rua.'
            : 'Modo de navegação. Ative “Arrastar rota” para editar.',
        );
      return;
    }
    const cached = S.dragRoadCache.get(key);
    if (cached) {
      roads = cached;
      loadedKey = key;
      status('Segure um trecho da linha e arraste para outra rua.');
      return;
    }
    loading = true;
    roads = [];
    status('Carregando ruas para encaixar o arraste…');
    try {
      const result = await api(
        `drafts/${did}/drag-roads?path_id=${encodeURIComponent(pathId)}&bbox=${encodeURIComponent(bbox)}`,
      );
      if (!ready()) return;
      if (!result.ready) return;
      if (result.truncated) {
        status(
          'Aproxime mais o mapa para carregar todas as ruas deste trecho.',
        );
        return;
      }
      roads = result.features;
      loadedKey = key;
      S.dragRoadCache.set(key, roads);
      if (S.dragRoadCache.size > 8)
        S.dragRoadCache.delete(S.dragRoadCache.keys().next().value);
      status('Segure um trecho da linha e arraste para outra rua.');
    } catch (e) {
      if (ready()) status(e.message, true);
    } finally {
      loading = false;
      if (pendingLoad && ready()) {
        pendingLoad = false;
        map.loadDragRoads();
      }
    }
  };
  const scheduleLoad = () => {
    clearTimeout(loadTimer);
    loadTimer = setTimeout(() => map.loadDragRoads(), 180);
  };
  map.on('moveend', scheduleLoad);
  map.loadDragRoads();
  const span = $('#drag-span');
  if (span) span.onchange = (e) => (S.dragSpan = Number(e.target.value));
  function nearestStreet(p) {
    const size = map.getSize();
    if (p.x < 0 || p.y < 0 || p.x > size.x || p.y > size.y) return null;
    let best = null;
    for (const f of roads) {
      const [a, b] = f.geometry.coordinates;
      const hit = lineProjection(
        p,
        map.latLngToContainerPoint([a[1], a[0]]),
        map.latLngToContainerPoint([b[1], b[0]]),
      );
      if (best && best.distance <= hit.distance) continue;
      best = {
        ...hit,
        edge: f.properties.edge,
        name: f.properties.name,
        position: [
          a[0] + hit.fraction * (b[0] - a[0]),
          a[1] + hit.fraction * (b[1] - a[1]),
        ],
      };
    }
    if (!best) return null;
    const ll = map.containerPointToLatLng(p),
      gap = Math.hypot(
        (best.position[0] - ll.lng) * 110440,
        (best.position[1] - ll.lat) * 110580,
      );
    return gap <= 21 && best.distance <= 20 ? best : null;
  }
  const isUI = (e) =>
    !!e.target.closest('.leaflet-control,.leaflet-popup,.leaflet-marker-icon');
  function removeHover() {
    if (hover) {
      hover.remove();
      hover = null;
    }
    container.classList.remove('route-can-grab');
  }
  function onMove(e) {
    if (!active()) return;
    const p = map.mouseEventToContainerPoint(e);
    if (drag) {
      if (e.pointerId !== drag.pointerId) return;
      e.preventDefault();
      e.stopPropagation();
      drag.moved = drag.moved || p.distanceTo(drag.origin) > 4;
      const street = nearestStreet(p);
      drag.street = street;
      drag.raw = map.containerPointToLatLng(p);
      if (street) {
        if (!ghost)
          ghost = L.circleMarker([street.position[1], street.position[0]], {
            radius: 8,
            weight: 3,
            color: '#08756c',
            fillColor: '#fff',
            fillOpacity: 1,
            interactive: false,
          }).addTo(map);
        else
          ghost
            .setLatLng([street.position[1], street.position[0]])
            .setStyle({ color: '#08756c' });
        status(street.name + ' · solte para recalcular neste trecho.');
      } else {
        if (ghost) ghost.setStyle({ color: '#c71020' });
        status(
          'Fora das ruas: leve o ponteiro até uma rua disponível. Soltar aqui cancela o arraste.',
          true,
        );
      }
      return;
    }
    if (isUI(e) || S.preview || map.getZoom() < 14) {
      removeHover();
      return;
    }
    const hits = routeGrabCandidates(map, coords, p);
    if (!hits.length) {
      removeHover();
      return;
    }
    const hit = hits[0],
      ll = map.containerPointToLatLng(hit.point);
    if (!hover)
      hover = L.circleMarker(ll, {
        radius: 6,
        weight: 2,
        color: '#c71020',
        fillColor: '#fff',
        fillOpacity: 1,
        interactive: false,
      }).addTo(map);
    else hover.setLatLng(ll);
    container.classList.add('route-can-grab');
  }
  function onDown(e) {
    if (!active() || isUI(e) || e.button !== 0 || drag) return;
    const p = map.mouseEventToContainerPoint(e),
      hits = routeGrabCandidates(map, coords, p);
    if (!hits.length) return;
    if (S.preview) {
      message(
        'Aplique ou descarte a prévia antes de arrastar outro trecho.',
        true,
      );
      return;
    }
    if (map.getZoom() < 14) {
      status('Aproxime o mapa para escolher a rua de destino.');
      return;
    }
    if (!roads.length) {
      status('Aguarde o carregamento das ruas antes de arrastar.');
      map.loadDragRoads();
      return;
    }
    e.preventDefault();
    e.stopImmediatePropagation();
    let hit = hits[0];
    if (hits.length > 1) {
      const selection =
        chosen !== null &&
        hits.find((h) => h.indices.some((i) => Math.abs(i - chosen) < 3));
      if (selection) hit = selection;
      else {
        const popup = L.popup()
          .setLatLng(map.containerPointToLatLng(p))
          .setContent(
            `<div class="stack"><strong>Qual passagem deseja mover?</strong>${hits.map((h, i) => `<button data-drag-passage="${h.index}">Passagem ${i + 1} · ${routeDirection(coords, h.index)}</button>`).join('')}</div>`,
          )
          .openOn(map);
        popup
          .getElement()
          .querySelectorAll('[data-drag-passage]')
          .forEach(
            (button) =>
              (button.onclick = () => {
                chosen = Number(button.dataset.dragPassage);
                map.closePopup();
                status(
                  'Passagem escolhida. Segure a linha novamente e arraste para a rua desejada.',
                );
              }),
          );
        return;
      }
    }
    S.routeRequest++;
    drag = {
      pointerId: e.pointerId,
      origin: p,
      hit,
      street: null,
      raw: null,
      moved: false,
      wasDragging: map.dragging.enabled(),
      wasZoom: map.scrollWheelZoom.enabled(),
    };
    map.dragging.disable();
    map.scrollWheelZoom.disable();
    removeHover();
    container.classList.add('route-is-dragging');
    try {
      container.setPointerCapture(e.pointerId);
    } catch {}
    status(
      'Arraste até uma rua. O marcador encaixa apenas na malha disponível.',
    );
  }
  function resetGesture() {
    const previous = drag;
    drag = null;
    if (previous) {
      try {
        container.releasePointerCapture(previous.pointerId);
      } catch {}
      if (!destroyed) {
        if (previous.wasDragging) map.dragging.enable();
        if (previous.wasZoom) map.scrollWheelZoom.enable();
      }
    }
    container.classList.remove('route-is-dragging');
    if (ghost) {
      ghost.remove();
      ghost = null;
    }
    return previous;
  }
  function onUp(e) {
    if (!drag || e.pointerId !== drag.pointerId) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    const d = resetGesture();
    if (!d.moved) return;
    if (!d.street) {
      status(
        'Arraste cancelado: solte sobre uma rua. O percurso não foi alterado.',
        true,
      );
      return;
    }
    run(async () => {
      const request = ++S.routeRequest,
        nav = S.navRequest,
        original = JSON.stringify(coords);
      status('Recalculando a rota pela rua escolhida…');
      try {
        await saveDraft();
        if (
          !ready() ||
          request !== S.routeRequest ||
          nav !== S.navRequest ||
          JSON.stringify(points()) !== original
        )
          return;
        const result = await api(`drafts/${did}/route-drag`, {
          revision: S.draft.revision,
          path_id: pathId,
          segment_index: d.hit.index,
          fraction: d.hit.fraction,
          drop_position: [d.raw.lng, d.raw.lat],
          edge: d.street.edge,
          span_m: S.dragSpan,
        });
        if (
          !ready() ||
          request !== S.routeRequest ||
          nav !== S.navRequest ||
          S.dirty ||
          result.revision !== S.draft.revision
        )
          return;
        S.preview = result;
        S.via = [];
        S.segment = null;
        chosen = null;
        renderEditorAgain();
        message(
          'Prévia pela ' +
            result.drag_street +
            '. Confira e aplique para salvar o novo trecho.',
        );
      } catch (error) {
        if (ready() && request === S.routeRequest) {
          status(error.message, true);
          throw error;
        }
      }
    });
  }
  function cancel(e) {
    if (drag && (!e || e.pointerId === drag.pointerId)) {
      resetGesture();
      status('Arraste cancelado. O percurso foi mantido.');
    }
  }
  container.addEventListener('pointerdown', onDown, true);
  container.addEventListener('pointermove', onMove, true);
  container.addEventListener('pointerup', onUp, true);
  container.addEventListener('pointercancel', cancel, true);
  const leave = () => {
    if (!drag) removeHover();
  };
  container.addEventListener('pointerleave', leave);
  const escape = (e) => {
    if (e.key === 'Escape') cancel();
  };
  document.addEventListener('keydown', escape);
  map.on('unload', () => {
    destroyed = true;
    clearTimeout(loadTimer);
    resetGesture();
    container.removeEventListener('pointerdown', onDown, true);
    container.removeEventListener('pointermove', onMove, true);
    container.removeEventListener('pointerup', onUp, true);
    container.removeEventListener('pointercancel', cancel, true);
    container.removeEventListener('pointerleave', leave);
    document.removeEventListener('keydown', escape);
  });
}
document.addEventListener('click', (e) => {
  const b = e.target.closest('[data-route-advanced]');
  if (!b) return;
  S.advancedEditor = b.dataset.routeAdvanced === 'true';
  S.mode = S.advancedEditor ? 'from' : 'drag';
  S.via = [];
  renderEditorAgain();
});
