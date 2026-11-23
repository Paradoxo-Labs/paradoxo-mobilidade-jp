'use strict';
Object.assign(S, {
  placeEditing: null,
  placeDirty: false,
  placeMode: 'position',
  batchSelection: null,
  batchReview: null,
});
const placeKinds = {
  terminal: 'Terminal',
  station: 'Estação',
  stop: 'Parada',
  reference: 'Referência territorial',
};
function activePlaces() {
  return Object.entries(S.overview.places).filter(([, p]) => !p.archived);
}
function placePosition(p, direction) {
  return p.accesses?.[direction] || p.route_position || p.position;
}
function placeIcon(p, text) {
  return L.divIcon({
    className: 'place-handle ' + (p.kind || 'reference'),
    html: esc(
      text || (p.kind === 'terminal' ? 'T' : p.kind === 'station' ? 'E' : 'P'),
    ),
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });
}
function renderPlaces(selected = S.placeEditing) {
  S.placeMode = 'position';
  const items = Object.entries(S.overview.places);
  if (selected && !S.overview.places[selected]) selected = null;
  S.placeEditing = selected;
  S.placeDirty = false;
  const place = clone(
    selected
      ? S.overview.places[selected]
      : {
          label: '',
          kind: 'station',
          position: [-34.88, -7.15],
          route_position: [-34.88, -7.15],
          accesses: {},
          note: '',
          archived: false,
        },
  );
  S.placeForm = place;
  $('#admin-body').innerHTML =
    header(
      'INFRAESTRUTURA / CADASTRO COMPARTILHADO',
      'Estações e terminais',
      'Cadastre a posição no terreno e os acessos na rua. As alterações ficam em edição até a publicação conjunta.',
      '<button data-net-action="new-place">+ Nova estação / terminal</button><button data-nav="batch" class="primary">Revisar publicação</button>',
    ) +
    `<p class="note">${S.overview.places_dirty ? 'Há referências alteradas ainda não publicadas.' : 'Cadastro igual à publicação ativa.'} Revisão ${S.overview.places_revision}. Mover uma referência não recalcula as linhas automaticamente.</p><div class="infrastructure-grid"><aside class="surface stack"><label>Pesquisar referência<input id="place-search" type="search" placeholder="Nome, terminal ou estação"></label><label class="check"><input type="checkbox" id="show-archived-places"> Mostrar arquivadas</label><div id="places-list" class="places-list"></div></aside><section class="surface stack"><h3>${selected ? 'Editar referência' : 'Nova referência'}</h3><form id="place-form" class="stack"><label>Nome<input name="label" required maxlength="160" value="${esc(place.label)}"></label><div class="form-grid"><label>Tipo<select name="kind">${Object.entries(
      placeKinds,
    )
      .map(
        ([k, v]) =>
          `<option value="${k}" ${place.kind === k ? 'selected' : ''}>${v}</option>`,
      )
      .join(
        '',
      )}</select></label><label class="check"><input type="checkbox" name="archived" ${place.archived ? 'checked' : ''}> Arquivada</label></div><label>Observações<textarea name="note" maxlength="2000">${esc(place.note || '')}</textarea></label><div class="map-tools"><button type="button" data-place-mode="position">Ponto no terreno</button><button type="button" data-place-mode="route_position">Conexão viária</button><select id="place-access-mode" aria-label="Acesso para editar"><option value="">Escolher acesso</option></select><button type="button" data-net-action="access-mode">Posicionar acesso</button></div><p id="place-map-hint" class="muted">Clique no mapa ou arraste o marcador para posicionar o ponto no terreno.</p><div id="places-map" class="map small-map" aria-label="Localização e acessos da referência"></div><div class="form-grid"><label>Latitude do terreno<input name="lat" type="number" step="any" required value="${place.position[1]}"></label><label>Longitude do terreno<input name="lon" type="number" step="any" required value="${place.position[0]}"></label><label>Latitude da conexão<input name="route_lat" type="number" step="any" required value="${place.route_position[1]}"></label><label>Longitude da conexão<input name="route_lon" type="number" step="any" required value="${place.route_position[0]}"></label></div><h3>Acessos por sentido</h3><div id="place-accesses" class="stack"></div><div class="row"><label>Chave do sentido<input id="new-access-key" placeholder="ida, volta, circuito ou variante-3" maxlength="40"></label><button type="button" data-net-action="add-access">+ Acesso</button></div><div class="actions"><button class="primary" type="submit">Salvar referência em edição</button><button type="button" data-nav="batch">Revisar publicação conjunta</button></div></form></section></div>`;
  const drawList = () => {
    const q = $('#place-search').value.toLocaleLowerCase('pt-BR');
    $('#places-list').innerHTML =
      items
        .filter(
          ([, p]) =>
            (!p.archived || $('#show-archived-places').checked) &&
            p.label.toLocaleLowerCase('pt-BR').includes(q),
        )
        .sort((a, b) => a[1].label.localeCompare(b[1].label))
        .map(
          ([key, p]) =>
            `<button data-edit-place="${esc(key)}" aria-pressed="${key === selected}"><strong>${esc(p.label)}</strong><small>${placeKinds[p.kind] || 'Referência'}${p.archived ? ' · arquivada' : ''}${JSON.stringify(p) !== JSON.stringify(S.overview.published_places[key]) ? ' · em edição' : ''}</small></button>`,
        )
        .join('') || '<p>Nenhuma referência encontrada.</p>';
  };
  $('#place-search').oninput = drawList;
  $('#show-archived-places').onchange = drawList;
  drawList();
  drawPlaceAccesses();
  const map = makeMap('places-map', []);
  const markers = L.layerGroup().addTo(map);
  const redraw = () => {
    markers.clearLayers();
    const p = S.placeForm;
    for (const [key, pos] of [
      ['position', p.position],
      ['route_position', p.route_position],
      ...Object.entries(p.accesses),
    ]) {
      L.marker([pos[1], pos[0]], {
        icon: placeIcon(
          p,
          key === 'position'
            ? 'T'
            : key === 'route_position'
              ? 'V'
              : key.slice(0, 2).toUpperCase(),
        ),
        draggable: true,
      })
        .bindTooltip(
          textNode(
            key === 'position'
              ? 'Ponto no terreno'
              : key === 'route_position'
                ? 'Conexão viária'
                : 'Acesso ' + key,
          ),
        )
        .on('dragend', (e) => {
          const ll = e.target.getLatLng();
          setPlacePosition(key, [ll.lng, ll.lat]);
          redraw();
        })
        .addTo(markers);
    }
  };
  S.redrawPlaceMarkers = redraw;
  map.setView([place.position[1], place.position[0]], 16, { animate: false });
  redraw();
  map.on('click', (e) => {
    setPlacePosition(S.placeMode, [e.latlng.lng, e.latlng.lat]);
    redraw();
  });
  $('#place-form').oninput = () => {
    const f = $('#place-form').elements;
    S.placeDirty = true;
    place.label = f.label.value;
    place.kind = f.kind.value;
    place.note = f.note.value;
    place.archived = f.archived.checked;
    for (const [key, lat, lon] of [
      ['position', 'lat', 'lon'],
      ['route_position', 'route_lat', 'route_lon'],
    ]) {
      if (
        f[lat].value !== '' &&
        f[lon].value !== '' &&
        Number.isFinite(Number(f[lat].value)) &&
        Number.isFinite(Number(f[lon].value))
      )
        place[key] = [Number(f[lon].value), Number(f[lat].value)];
    }
    redraw();
  };
  $('#place-form').onsubmit = (e) => {
    e.preventDefault();
    run(async () => {
      const nav = S.navRequest;
      const form = e.currentTarget,
        button = form.querySelector('[type=submit]');
      button.disabled = true;
      const submitted = clone(S.placeForm);
      try {
        const result = await api('places/save', {
          id: selected,
          revision: S.overview.places_revision,
          place: submitted,
        });
        const overview = await api('overview');
        if (S.screen !== 'places' || S.navRequest !== nav || !form.isConnected)
          return;
        selected = result.id;
        S.placeEditing = result.id;
        S.overview = overview;
        if (JSON.stringify(S.placeForm) !== JSON.stringify(submitted)) {
          S.placeDirty = true;
          message(
            'Referência salva; há novas alterações no formulário. Salve novamente para incluí-las.',
          );
          return;
        }
        S.placeDirty = false;
        cleanup();
        renderPlaces(result.id);
        message(
          'Referência salva em edição. Publique em conjunto para atualizar o atlas.',
        );
      } finally {
        if (button.isConnected) button.disabled = false;
      }
    });
  };
}
function setPlacePosition(key, pos) {
  if (['position', 'route_position'].includes(key)) {
    S.placeForm[key] = pos;
    const form = $('#place-form').elements,
      prefix = key === 'position' ? '' : 'route_';
    form[prefix + 'lat'].value = pos[1].toFixed(7);
    form[prefix + 'lon'].value = pos[0].toFixed(7);
  } else {
    S.placeForm.accesses[key] = pos;
    drawPlaceAccesses();
  }
  S.placeDirty = true;
}
function drawPlaceAccesses() {
  $('#place-accesses').innerHTML =
    Object.entries(S.placeForm.accesses)
      .map(
        ([key, p]) =>
          `<div class="spread"><span><strong>${esc(key)}</strong> · ${p[1].toFixed(6)}, ${p[0].toFixed(6)}</span><button type="button" data-remove-access="${esc(key)}">Remover</button></div>`,
      )
      .join('') ||
    '<p class="muted">Sem acesso específico. Será usada a conexão viária.</p>';
  $('#place-access-mode').innerHTML =
    '<option value="">Escolher acesso</option>' +
    Object.keys(S.placeForm.accesses)
      .map(
        (k) =>
          `<option value="${esc(k)}" ${S.placeMode === k ? 'selected' : ''}>${esc(k)}</option>`,
      )
      .join('');
}
function renderList() {
  renderLegacyList();
  const o = S.overview;
  const drafts = o.drafts.filter(
    (d) => !o.lines.some((l) => l.id === d.line_id),
  );
  for (const d of drafts) {
    const button = $(`[data-open-draft="${d.id}"]`);
    if (button)
      button.insertAdjacentHTML(
        'afterend',
        lineStateButton(d.line_id, !!o.line_states[d.line_id]?.archived) +
          `<button data-discard-line="${d.line_id}">Descartar rascunho</button>`,
      );
  }
  const inactive = o.inactive_lines.filter(
    (l) => !drafts.some((d) => d.line_id === l.id),
  );
  if (inactive.length)
    $('#admin-body').insertAdjacentHTML(
      'beforeend',
      `<section class="surface stack" data-filter-group><h3>Fora da publicação ativa</h3>${inactive.map((l) => `<div class="spread rule" data-filter-line="${l.id}"><div><strong>${esc(l.code)} · ${esc(l.name)}</strong><p class="muted">${o.line_states[l.id]?.archived ? 'Arquivada' : 'Disponível para republicação'} · histórico preservado</p></div><div class="actions">${lineStateButton(l.id, !!o.line_states[l.id]?.archived)}<button data-edit="${l.id}">Abrir versão em rascunho</button></div></div>`).join('')}</section>`,
    );
  const decorate = () => {
    $$('#line-table tr').forEach((row) => {
      const edit = row.querySelector('[data-edit]');
      if (!edit || row.querySelector('[data-manage-line]')) return;
      const lid = edit.dataset.edit,
        state = o.line_states[lid];
      if (state?.archived)
        row.cells[2].insertAdjacentHTML(
          'afterbegin',
          '<strong class="danger">Retirada pendente</strong>',
        );
      row
        .querySelector('.actions')
        .insertAdjacentHTML(
          'beforeend',
          lineStateButton(lid, !!state?.archived),
        );
      if (o.drafts.some((d) => d.line_id === lid))
        row
          .querySelector('.actions')
          .insertAdjacentHTML(
            'beforeend',
            `<button data-discard-line="${lid}">Descartar rascunho</button>`,
          );
    });
    $$('[data-filter-line]').forEach((card) => {
      const l = S.listRecords.get(card.dataset.filterLine);
      card.hidden = !l || !S.listLineMatches(l);
    });
    $$('[data-filter-group]').forEach(
      (group) =>
        (group.hidden = Array.from(
          group.querySelectorAll('[data-filter-line]'),
        ).every((card) => card.hidden)),
    );
  };
  $('#line-table').addEventListener('lines-rendered', decorate);
  decorate();
  $('#admin-body .heading .actions').insertAdjacentHTML(
    'afterbegin',
    '<button data-nav="batch">Preparar publicação conjunta</button>',
  );
}

function lineStateButton(lid, archived) {
  return `<button data-manage-line="${lid}" data-line-action="${archived ? 'restore' : 'archive'}">${archived ? 'Reativar' : 'Arquivar / retirar'}</button>`;
}
function editorExtensions() {
  const f = current(),
    ps = points(),
    p = f.properties;
  const controls = p.control_points || [],
    stations = p.station_ids || [];
  return `<section class="stack rule"><h3>Seleção e cortes</h3>${ps.length ? `<div class="form-grid"><label>Índice A<input type="number" id="segment-from" min="0" max="${ps.length - 2}" value="${S.segment?.from ?? 0}"></label><label>Índice B<input type="number" id="segment-to" min="1" max="${ps.length - 1}" value="${S.segment?.to ?? ps.length - 1}"></label></div><button data-net-action="fit-selection">Mostrar seleção e ↔</button><button data-net-action="direct-route" data-needs-router>Reconectar A → B pelas ruas</button><p class="muted">Reconecta sem passagens intermediárias. Use para retirar uma ida e retorno desnecessária.</p><div class="actions"><button data-net-action="trim-before">Cortar antes de A</button><button data-net-action="trim-after">Cortar depois de B</button></div>` : '<p class="muted">Disponível após calcular um percurso.</p>'}</section><section class="stack rule"><h3>Referências permanentes</h3><div id="permanent-controls">${controls.map((c, i) => `<div class="permanent-row" draggable="true" data-control-row="${i}"><label>${i + 1}. Nome<input data-control-label="${i}" maxlength="160" value="${esc(c.label)}"></label><small>${c.position[1].toFixed(5)}, ${c.position[0].toFixed(5)}${c.station_id ? ' · acesso de estação' : ''}</small><div class="actions"><button data-control-move="${i}" data-delta="-1" ${i === 0 ? 'disabled' : ''}>↑</button><button data-control-move="${i}" data-delta="1" ${i === controls.length - 1 ? 'disabled' : ''}>↓</button><button data-control-delete="${i}">Remover</button></div></div>`).join('') || '<p class="muted">Nenhuma referência permanente neste sentido.</p>'}</div><button data-mode="permanent">+ Referência no mapa</button><button data-net-action="capture-controls">Guardar A, passagens e B</button><button data-net-action="import-controls">Importar referências do estudo</button><button data-net-action="recalculate-controls" data-needs-router>Recalcular pelas referências</button><p class="muted">Nomes e ordem são salvos no rascunho. Mover referências não muda o percurso até aplicar o recálculo.</p></section><section class="stack rule"><h3>Estações neste sentido</h3><select id="path-station" aria-label="Estação para vincular"><option value="">Escolher estação / terminal</option>${activePlaces()
    .filter(([k, v]) => v.kind !== 'reference' && !stations.includes(k))
    .map(([k, v]) => `<option value="${esc(k)}">${esc(v.label)}</option>`)
    .join(
      '',
    )}</select><button data-net-action="link-station">+ Vincular e adicionar acesso</button>${stations.map((key, i) => `<div class="stack"><strong>${i + 1}. ${esc(S.overview.places[key]?.label || key)}</strong><div class="actions"><button data-station-move="${i}" data-delta="-1" ${i === 0 ? 'disabled' : ''}>↑</button><button data-station-move="${i}" data-delta="1" ${i === stations.length - 1 ? 'disabled' : ''}>↓</button><button data-unlink-station="${i}">Desvincular</button></div></div>`).join('')}<button data-nav="places">Gerenciar estações e acessos</button></section>`;
}
function bindEditorExtensions() {
  for (const key of ['from', 'to']) {
    const input = $('#segment-' + key);
    if (input)
      input.onchange = () =>
        run(async () => {
          const v = Number(input.value),
            segment = { ...S.segment, [key]: v };
          if (
            !Number.isInteger(v) ||
            segment.from < 0 ||
            segment.to >= points().length ||
            segment.from >= segment.to
          )
            throw new Error('Use índices válidos, com A antes de B.');
          S.segment = segment;
          S.via = [];
          S.preview = null;
          renderEditorAgain();
        });
  }
  $$('[data-control-label]').forEach(
    (input) =>
      (input.oninput = () =>
        mutate(
          () =>
            (current().properties.control_points[
              Number(input.dataset.controlLabel)
            ].label = input.value),
        )),
  );
  let dragging = null;
  $$('[data-control-row]').forEach((row) => {
    row.ondragstart = (e) => {
      if (e.target.tagName === 'INPUT') {
        e.preventDefault();
        return;
      }
      dragging = Number(row.dataset.controlRow);
      e.dataTransfer.setData('text/plain', String(dragging));
    };
    row.ondragover = (e) => e.preventDefault();
    row.ondrop = (e) => {
      e.preventDefault();
      const to = Number(row.dataset.controlRow);
      if (dragging === null) return;
      mutate(() => {
        const list = current().properties.control_points,
          [c] = list.splice(dragging, 1);
        list.splice(to, 0, c);
      });
      dragging = null;
      renderEditorAgain();
    };
    row.ondragend = () => (dragging = null);
  });
}
function addPermanent(pos, label, stationId) {
  const list = current().properties.control_points || [];
  if (list.length >= 100)
    throw new Error('Limite de 100 referências por sentido.');
  mutate(() => {
    current().properties.control_points ||= [];
    current().properties.control_points.push({
      id: id(),
      label: label || 'Referência ' + (list.length + 1),
      position: pos,
      ...(stationId ? { station_id: stationId } : {}),
    });
  });
  renderEditorAgain();
}
function drawEditorExtensions(map) {
  const p = current().properties;
  for (const key of p.station_ids || []) {
    const place = S.overview.places[key];
    if (place)
      L.marker([place.position[1], place.position[0]], {
        icon: placeIcon(place),
      })
        .bindTooltip(textNode(place.label))
        .addTo(map);
  }
  if (!S.advancedEditor) return;
  (p.control_points || []).forEach((c, i) => {
    L.marker([c.position[1], c.position[0]], {
      icon: L.divIcon({
        className: 'control-handle',
        html: String(i + 1),
        iconSize: [24, 24],
        iconAnchor: [12, 12],
      }),
      draggable: true,
    })
      .bindTooltip(textNode(c.label + ' · referência permanente'))
      .on('dragend', (e) => {
        const ll = e.target.getLatLng();
        mutate(() => {
          c.position = [ll.lng, ll.lat];
          delete c.station_id;
        });
        renderEditorAgain();
        message(
          'Referência permanente movida. Recalcule e aplique para alterar a rota.',
        );
      })
      .addTo(map);
  });
}
function nearestCoordinateIndex(coords, pos) {
  let best = 0,
    d = Infinity;
  coords.forEach((c, i) => {
    const v = Math.hypot(c[0] - pos[0], c[1] - pos[1]);
    if (v < d) {
      best = i;
      d = v;
    }
  });
  return best;
}
function distanceToRoute(pos, coords) {
  const c = coords[nearestCoordinateIndex(coords, pos)];
  return c
    ? Math.hypot((c[0] - pos[0]) * 110440, (c[1] - pos[1]) * 110580)
    : Infinity;
}
function offerOverlappingVertices(map, ll, coords, best, endpoint) {
  const samePoint = coords
    .map((c, i) => (same(c, coords[best]) ? i : -1))
    .filter((i) => i >= 0);
  if (samePoint.length < 2) return false;
  const buttons = samePoint
    .map(
      (i) =>
        `<button data-route-index="${i}" data-endpoint="${endpoint}">Passagem no índice ${i}${i === 0 ? ' · início' : i === coords.length - 1 ? ' · fim' : ''}</button>`,
    )
    .join('');
  L.popup()
    .setLatLng(ll)
    .setContent(
      `<div class="stack"><strong>A rota passa aqui mais de uma vez.</strong>${buttons}</div>`,
    )
    .openOn(map);
  return true;
}
async function previewTrim(side) {
  await saveDraft();
  const request = ++S.routeRequest,
    did = S.draft.id,
    path = current().properties.path_id,
    revision = S.draft.revision;
  const result = await api(`drafts/${did}/route-trim`, {
    revision,
    path_id: path,
    index: side === 'before' ? S.segment.from : S.segment.to,
    side,
  });
  if (
    request !== S.routeRequest ||
    S.screen !== 'editor' ||
    S.draft.id !== did ||
    current().properties.path_id !== path ||
    S.draft.revision !== revision ||
    S.dirty
  )
    return;
  S.preview = result;
  renderEditorAgain();
  message('Prévia do corte pronta. Confira e aplique para alterar o rascunho.');
}
function renderBatch() {
  S.batchRequest++;
  const o = S.overview;
  const options = o.drafts.filter((d) => !o.line_states[d.line_id]?.archived);
  const removals = o.lines.filter((l) => o.line_states[l.id]?.archived);
  S.batchReview = null;
  $('#admin-body').innerHTML =
    header(
      'PUBLICAÇÃO / COMPOSIÇÃO DA REDE',
      'Publicação conjunta',
      'Selecione versões salvas, retiradas e referências. A revisão verifica a composição final antes de trocar a rede no atlas.',
    ) +
    `<form id="batch-form" class="surface stack"><h3>Linhas em edição</h3>${options.map((d) => `<label class="check"><input type="checkbox" name="draft" value="${d.id}"><span><strong>${esc(d.payload.line.code || 'Sem código')} · ${esc(d.payload.line.name)}</strong><small>${stamp(d.updated)} · revisão ${d.revision}${d.saved_version ? ' · possui versão salva' : ' · precisa salvar versão'}</small></span><button type="button" data-open-draft="${d.id}">Abrir</button></label>`).join('') || '<p>Nenhum rascunho disponível.</p>'}<h3>Retiradas da rede publicada</h3>${removals.map((l) => `<label class="check"><input type="checkbox" name="remove" value="${l.id}">${esc(l.code)} · ${esc(l.name)}</label>`).join('') || '<p class="muted">Nenhuma retirada marcada. Use “Arquivar / retirar” na lista de linhas.</p>'}<h3>Estações e terminais</h3><label class="check"><input type="checkbox" name="places" ${o.places_dirty ? 'checked' : ''}> Incluir o cadastro compartilhado em edição ${o.places_dirty ? '· há alterações' : '· sem alterações'}</label><p class="muted">Novas estações vinculadas às linhas precisam entrar na mesma publicação. Referências arquivadas não podem permanecer vinculadas à rede final.</p><button type="submit" class="primary">Revisar composição selecionada</button></form><div id="batch-result"></div>`;
  if (S.batchSelection) {
    for (const input of $$('#batch-form input'))
      input.checked =
        input.name === 'places'
          ? S.batchSelection.include_places
          : (input.name === 'draft'
              ? S.batchSelection.draft_ids
              : S.batchSelection.remove_ids
            ).includes(input.value);
  }
  $('#batch-form').onsubmit = (e) => {
    e.preventDefault();
    run(async () => {
      const body = {
        draft_ids: $$('#batch-form [name=draft]:checked').map((n) => n.value),
        remove_ids: $$('#batch-form [name=remove]:checked').map((n) => n.value),
        include_places: $('#batch-form [name=places]').checked,
      };
      S.batchSelection = body;
      const revision = ++S.batchRequest;
      const r = await api('batch/review', body);
      if (S.screen !== 'batch' || revision !== S.batchRequest) return;
      S.batchReview = r;
      renderBatchReview(r);
    });
  };
  $('#batch-form').onchange = () => {
    S.batchRequest++;
    S.batchReview = null;
    $('#batch-result').innerHTML = '';
  };
}
S.batchRequest = 0;
function renderBatchReview(r) {
  cleanup();
  $('#batch-result').innerHTML =
    `<section class="surface stack"><h2>Revisão da publicação ${r.release_number + 1}</h2><p>${r.changes.length} linhas alteradas · ${r.removals.length} retiradas · ${r.places_changed.length} referências alteradas · ${r.line_count} linhas na rede final.</p><div class="review-grid"><div class="stack"><div id="batch-map" class="map small-map" aria-label="Composição final da rede"></div><h3>Alterações selecionadas</h3>${r.changes.map((c) => `<p><strong>${esc(c.code)}</strong> · V${c.version || '?'} · revisão ${c.revision}</p>`).join('')}${r.removals.map((c) => `<p class="danger">Retirar ${esc(c.code)}</p>`).join('')}${r.places_changed.map((key) => `<p>${r.places[key]?.archived ? 'Arquivar referência' : 'Atualizar referência'}: ${esc(r.places[key]?.label || key)}</p>`).join('')}</div><aside class="stack"><h3>Conferência</h3>${r.errors.map((e) => `<div class="issue error">${esc(e)}</div>`).join('') || '<div class="issue">✓ Composição válida para publicação.</div>'}${r.warnings.map((w) => `<div class="issue">△ ${esc(w)}</div>`).join('')}<label class="check"><input id="batch-ack" type="checkbox"> Conferi as alterações, retiradas e pendências. Publicar como estudo.</label><button data-net-action="publish-batch" id="batch-publish" class="primary" disabled>Publicar conjunto no atlas</button><p class="muted">Tudo é publicado na mesma transação. A publicação anterior pode ser restaurada, incluindo as estações.</p></aside></div></section>`;
  // Descarte mapas de revisões anteriores, preservando somente a seleção do formulário.
  const map = makeMap('batch-map', r.features);
  for (const p of Object.values(r.places).filter(
    (p) => !p.archived && p.kind !== 'reference',
  ))
    L.marker([p.position[1], p.position[0]], { icon: placeIcon(p) })
      .bindTooltip(textNode(p.label))
      .addTo(map);
  $('#batch-ack').onchange = (e) =>
    ($('#batch-publish').disabled = !e.target.checked || r.errors.length > 0);
}
document.addEventListener('click', (e) => {
  const b = e.target.closest('button');
  if (!b) return;
  run(async () => {
    if (b.dataset.editPlace) {
      if (
        S.placeDirty &&
        !(await confirmAction(
          'Trocar a referência?',
          'As mudanças deste formulário ainda não foram salvas. Descartá-las?',
        ))
      )
        return;
      cleanup();
      renderPlaces(b.dataset.editPlace);
      return;
    }
    if (b.dataset.placeMode) {
      S.placeMode = b.dataset.placeMode;
      $('#place-map-hint').textContent =
        'Clique no mapa para posicionar ' +
        (S.placeMode === 'position'
          ? 'o ponto no terreno.'
          : 'a conexão viária.');
      return;
    }
    if (b.dataset.removeAccess) {
      delete S.placeForm.accesses[b.dataset.removeAccess];
      if (S.placeMode === b.dataset.removeAccess) S.placeMode = 'position';
      S.placeDirty = true;
      drawPlaceAccesses();
      S.redrawPlaceMarkers();
      return;
    }
    if (b.dataset.manageLine || b.dataset.discardLine) {
      const lid = b.dataset.manageLine || b.dataset.discardLine,
        action = b.dataset.lineAction || 'discard-draft',
        state = S.overview.line_states[lid],
        draft = S.overview.drafts.find((d) => d.line_id === lid),
        published = S.overview.lines.some((l) => l.id === lid);
      const text =
        action === 'archive'
          ? published
            ? 'A linha continuará no atlas até você confirmar sua retirada na publicação conjunta. Seus dados e versões serão preservados.'
            : 'A linha sairá das opções de publicação, mantendo seu rascunho e histórico.'
          : action === 'restore'
            ? 'A linha voltará a ficar disponível para edição e publicação. O atlas não muda agora.'
            : 'O rascunho será descartado. Versões já salvas e a publicação atual serão preservadas; alterações sem versão salva serão perdidas.';
      if (
        !(await confirmAction(
          action === 'archive'
            ? 'Arquivar / preparar retirada?'
            : action === 'restore'
              ? 'Reativar linha?'
              : 'Descartar rascunho?',
          text,
        ))
      )
        return;
      if (action === 'discard-draft' && S.draft?.line_id === lid && S.dirty)
        await saveDraft();
      await api('lines/manage', {
        line_id: lid,
        action,
        revision: state?.revision || 0,
        draft_revision:
          S.draft?.line_id === lid ? S.draft.revision : draft?.revision,
      });
      if (action === 'discard-draft' && S.draft?.line_id === lid) {
        localStorage.removeItem(recoveryKey());
        S.draft = null;
        S.payload = null;
        S.dirty = false;
      }
      await go('list');
      message(
        action === 'archive' && published
          ? 'Retirada preparada. Revise e publique o conjunto para atualizar o atlas.'
          : 'Gerenciamento atualizado. A publicação não foi alterada.',
      );
      return;
    }
    if (b.dataset.routeIndex !== undefined) {
      const index = Number(b.dataset.routeIndex),
        next = { ...S.segment, [b.dataset.endpoint]: index };
      if (next.from >= next.to)
        throw new Error(
          'Escolha uma passagem com A antes de B no sentido do percurso.',
        );
      S.segment = next;
      S.via = [];
      S.preview = null;
      S.mode = 'navigate';
      renderEditorAgain();
      return;
    }
    if (b.dataset.controlDelete !== undefined) {
      mutate(() =>
        current().properties.control_points.splice(
          Number(b.dataset.controlDelete),
          1,
        ),
      );
      renderEditorAgain();
      return;
    }
    if (
      b.dataset.controlMove !== undefined ||
      b.dataset.stationMove !== undefined
    ) {
      const controls = b.dataset.controlMove !== undefined,
        index = Number(
          controls ? b.dataset.controlMove : b.dataset.stationMove,
        ),
        delta = Number(b.dataset.delta),
        list = controls
          ? current().properties.control_points
          : current().properties.station_ids;
      if (index + delta < 0 || index + delta >= list.length) return;
      mutate(() => {
        [list[index], list[index + delta]] = [list[index + delta], list[index]];
      });
      renderEditorAgain();
      return;
    }
    if (b.dataset.unlinkStation !== undefined) {
      mutate(() => {
        const p = current().properties,
          [key] = p.station_ids.splice(Number(b.dataset.unlinkStation), 1);
        p.control_points = (p.control_points || []).filter(
          (c) => c.station_id !== key,
        );
      });
      renderEditorAgain();
      return;
    }
    switch (b.dataset.netAction) {
      case 'new-place':
        if (
          S.placeDirty &&
          !(await confirmAction(
            'Criar outra referência?',
            'Descartar as mudanças deste formulário?',
          ))
        )
          return;
        S.placeMode = 'position';
        cleanup();
        renderPlaces(null);
        break;
      case 'add-access': {
        const key = $('#new-access-key').value.trim();
        if (
          !/^[a-z0-9-]{1,40}$/.test(key) ||
          ['position', 'route_position'].includes(key)
        )
          throw new Error(
            'Use uma chave de sentido: ida, volta, circuito ou variante-3.',
          );
        if (S.placeForm.accesses[key])
          throw new Error('Este acesso já existe. Selecione-o para mover.');
        if (Object.keys(S.placeForm.accesses).length >= 12)
          throw new Error('Limite de 12 acessos por referência.');
        S.placeForm.accesses[key] = clone(S.placeForm.route_position);
        S.placeMode = key;
        S.placeDirty = true;
        drawPlaceAccesses();
        S.redrawPlaceMarkers();
        $('#new-access-key').value = '';
        $('#place-map-hint').textContent =
          'Clique no mapa para posicionar o acesso ' + key + '.';
        break;
      }
      case 'access-mode':
        if (!$('#place-access-mode').value)
          throw new Error('Adicione ou escolha um acesso primeiro.');
        S.placeMode = $('#place-access-mode').value;
        $('#place-map-hint').textContent =
          'Clique no mapa para posicionar o acesso ' + S.placeMode + '.';
        break;
      case 'fit-selection': {
        if (!S.segment) throw new Error('Selecione A e B primeiro.');
        const ps = points().slice(S.segment.from, S.segment.to + 1);
        S.maps.at(-1).fitBounds(
          ps.map((p) => [p[1], p[0]]),
          { padding: [50, 50], maxZoom: 19, animate: false },
        );
        break;
      }
      case 'direct-route':
        await calculatePreview(true);
        break;
      case 'trim-before':
        await previewTrim('before');
        break;
      case 'trim-after':
        await previewTrim('after');
        break;
      case 'capture-controls': {
        if (!S.segment)
          throw new Error('Selecione um intervalo do percurso primeiro.');
        const selected = [
          points()[S.segment.from],
          ...S.via,
          points()[S.segment.to],
        ];
        if (
          (current().properties.control_points?.length || 0) + selected.length >
          100
        )
          throw new Error('Limite de 100 referências por sentido.');
        mutate(() => {
          const p = current().properties;
          p.control_points ||= [];
          selected.forEach((pos, i) =>
            p.control_points.push({
              id: id(),
              label:
                i === 0
                  ? 'Início A'
                  : i === selected.length - 1
                    ? 'Fim B'
                    : 'Passagem ' + i,
              position: clone(pos),
            }),
          );
        });
        renderEditorAgain();
        break;
      }
      case 'import-controls': {
        const currentPath = current().properties.path_id,
          did = S.draft.id;
        const response = await fetch('/api/proposal');
        if (!response.ok)
          throw new Error(
            'Não foi possível consultar as referências do estudo.',
          );
        const proposal = await response.json();
        if (
          S.screen !== 'editor' ||
          S.draft.id !== did ||
          current().properties.path_id !== currentPath
        )
          return;
        const refs = (current().properties.waypoints || [])
          .map((key) => ({
            key,
            position:
              S.overview.places[key]?.route_position || proposal.waypoints[key],
          }))
          .filter((p) => p.position);
        if (!refs.length)
          throw new Error(
            'Este percurso não possui referências importáveis. Adicione no mapa ou guarde A e B.',
          );
        if (
          !(await confirmAction(
            'Importar referências do estudo?',
            'A lista de referências permanentes deste sentido será substituída. A geometria não muda.',
          ))
        )
          return;
        mutate(
          () =>
            (current().properties.control_points = refs.map((p) => ({
              id: id(),
              label:
                S.overview.places[p.key]?.label || p.key.replaceAll('_', ' '),
              position: clone(p.position),
            }))),
        );
        renderEditorAgain();
        break;
      }
      case 'recalculate-controls': {
        const controls = current().properties.control_points || [];
        if (controls.length < 2)
          throw new Error(
            'Guarde ao menos duas referências, na ordem desejada para o percurso inteiro.',
          );
        if (
          !(await confirmAction(
            'Recalcular o sentido inteiro?',
            'Será criada uma prévia passando pelas referências permanentes na ordem da lista. O percurso só muda depois de aplicar.',
          ))
        )
          return;
        await calculateNew(controls.map((c) => c.position));
        break;
      }
      case 'link-station': {
        const key = $('#path-station').value,
          p = S.overview.places[key];
        if (!p) throw new Error('Escolha uma estação ou terminal.');
        if ((current().properties.control_points?.length || 0) >= 100)
          throw new Error('Limite de 100 referências por sentido.');
        mutate(() => {
          const path = current().properties;
          path.station_ids ||= [];
          if (!path.station_ids.includes(key)) path.station_ids.push(key);
          path.control_points ||= [];
          path.control_points.push({
            id: id(),
            label: p.label,
            position: clone(placePosition(p, path.sentido)),
            station_id: key,
          });
        });
        renderEditorAgain();
        break;
      }
      case 'publish-batch': {
        const report = S.batchReview;
        if (!report || !$('#batch-ack')?.checked || report.errors.length)
          throw new Error('Revise e confirme a composição antes de publicar.');
        if (
          !(await confirmAction(
            'Publicar este conjunto?',
            `${report.changes.length} linhas, ${report.removals.length} retiradas e ${report.places_changed.length} referências alteradas serão aplicadas ao atlas. A publicação anterior ficará no histórico.`,
          ))
        )
          return;
        b.disabled = true;
        try {
          const result = await api('batch/publish', {
            ...S.batchSelection,
            review_token: report.review_token,
            acknowledge_warnings: true,
          });
          S.batchSelection = null;
          S.batchReview = null;
          await go('history');
          message('Publicação conjunta ' + result.number + ' ativa no atlas.');
        } finally {
          if (b.isConnected) b.disabled = false;
        }
        break;
      }
    }
  });
});
