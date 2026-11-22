'use strict';
const $ = (s) => document.querySelector(s),
  $$ = (s) => Array.from(document.querySelectorAll(s));
const esc = (v) =>
  String(v ?? '').replace(
    /[&<>"']/g,
    (c) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[
        c
      ],
  );
const clone = (v) => JSON.parse(JSON.stringify(v));
const id = () => crypto.randomUUID();
const labels = {
  brs: 'BRS',
  troncal: 'Troncal',
  transversal: 'Transversal',
  integracional: 'Integracional',
  regional: 'Regional',
  local: 'Local',
  metropolitana: 'Metropolitana',
};
const stamp = (v) =>
  v
    ? new Intl.DateTimeFormat('pt-BR', {
        dateStyle: 'short',
        timeStyle: 'short',
        timeZone: 'America/Fortaleza',
      }).format(new Date(v))
    : '—';
const km = (v) =>
  Number(v || 0).toLocaleString('pt-BR', { maximumFractionDigits: 2 });
const S = {
  user: null,
  csrf: null,
  screen: 'list',
  overview: null,
  draft: null,
  payload: null,
  path: 0,
  dirty: false,
  savePromise: null,
  timer: null,
  undo: [],
  redo: [],
  preview: null,
  via: [],
  draw: [],
  segment: null,
  mode: 'drag',
  advancedEditor: false,
  router: { ready: false },
  maps: [],
  resources: null,
  observed: null,
  review: null,
  baseline: null,
  view: null,
  focus: false,
  recovery: null,
  routeRequest: 0,
  navRequest: 0,
  compareRequest: 0,
};
let routerTimer, jobTimer;
async function api(path, body) {
  const r = await fetch('/api/admin/' + path, {
    method: body === undefined ? 'GET' : 'POST',
    headers:
      body === undefined
        ? {}
        : { 'Content-Type': 'application/json', 'X-CSRF-Token': S.csrf || '' },
    body: body === undefined ? undefined : JSON.stringify(body),
  });
  const data = await r.json();
  if (!r.ok) {
    if (r.status === 401 && S.user) {
      S.user = null;
      renderAuth(true);
      message(
        'Sua sessão expirou. Entre novamente; o rascunho recuperável foi mantido.',
        true,
      );
    }
    const e = new Error(data.error || 'Falha na operação.');
    e.status = r.status;
    e.data = data;
    throw e;
  }
  return data;
}
function message(text, error = false) {
  const node = S.user ? $('#message') : $('#auth-error');
  if (!node) return;
  node.textContent = text;
  node.hidden = !text;
  node.classList.toggle('error', error);
}
function saveStatus(text) {
  $('#save-state').textContent = text;
}
function current() {
  return S.payload?.features[S.path];
}
function points() {
  return current()?.geometry.coordinates || [];
}
function recoveryKey() {
  return `px-draft:${S.user}:${S.draft?.id}`;
}
function protect() {
  try {
    localStorage.setItem(
      recoveryKey(),
      JSON.stringify({
        revision: S.draft.revision,
        payload: S.payload,
        time: Date.now(),
      }),
    );
  } catch {
    message(
      'Não foi possível manter a cópia de recuperação neste navegador. Salve o rascunho no servidor.',
      true,
    );
  }
}
function changed() {
  S.dirty = true;
  S.preview = null;
  protect();
  saveStatus('Alterações locais · salvando…');
  clearTimeout(S.timer);
  S.timer = setTimeout(
    () => saveDraft().catch((e) => message(e.message, true)),
    700,
  );
}
function mutate(action) {
  S.undo.push(clone(S.payload));
  if (S.undo.length > 40) S.undo.shift();
  S.redo = [];
  action();
  changed();
}
async function saveDraft() {
  clearTimeout(S.timer);
  if (S.savePromise) {
    await S.savePromise;
    if (S.dirty) return saveDraft();
    return S.draft;
  }
  if (!S.dirty) return S.draft;
  const did = S.draft.id;
  const serialized = JSON.stringify(S.payload);
  const revision = S.draft.revision;
  S.savePromise = (async () => {
    try {
      const result = await api(`drafts/${did}/update`, {
        revision,
        payload: JSON.parse(serialized),
      });
      if (S.draft.id !== did) return result;
      const same = JSON.stringify(S.payload) === serialized;
      S.draft = result;
      if (same) {
        S.payload = result.payload;
        S.dirty = false;
        localStorage.removeItem(recoveryKey());
      } else protect();
      saveStatus(
        same
          ? 'Rascunho salvo · ' + stamp(result.updated)
          : 'Novas alterações locais',
      );
      return result;
    } catch (e) {
      saveStatus(
        e.status === 409
          ? 'Conflito · versão local preservada'
          : 'Falha ao salvar · cópia local preservada',
      );
      throw e;
    } finally {
      S.savePromise = null;
    }
  })();
  return S.savePromise;
}
async function confirmAction(title, text) {
  const d = $('#confirm-dialog');
  $('#confirm-title').textContent = title;
  $('#confirm-text').textContent = text;
  return new Promise((resolve) => {
    const finish = (value) => {
      d.close();
      d.removeEventListener('click', click);
      d.removeEventListener('cancel', cancel);
      resolve(value);
    };
    const click = (e) => {
      const b = e.target.closest('[data-confirm]');
      if (b) finish(b.dataset.confirm === 'ok');
    };
    const cancel = (e) => {
      e.preventDefault();
      finish(false);
    };
    d.addEventListener('click', click);
    d.addEventListener('cancel', cancel);
    d.showModal();
  });
}
function renderAuth(configured) {
  clearInterval(routerTimer);
  clearInterval(jobTimer);
  cleanup();
  $('#admin-app').hidden = true;
  $('#auth').hidden = false;
  $('#auth').innerHTML =
    `<div class="auth-brand"><img src="/assets/paradoxo-logo.webp" alt="Paradoxo Labs"><span class="mono">MOBILIDADE JP<br>ADMINISTRAÇÃO LOCAL</span></div><form id="auth-form" class="surface stack"><span class="eyebrow">${configured ? 'ACESSO RESTRITO' : 'PRIMEIRO ACESSO'}</span><h1>${configured ? 'Entrar no painel' : 'Cadastrar administrador'}</h1>${configured ? '' : `<p class="muted">Leia o código de primeiro acesso no terminal do Docker. Ele deixa de funcionar após o cadastro.</p><code>docker compose exec atlas python3 apps/admin/manage.py setup-token</code><label>Código de primeiro acesso<input name="token" required autocomplete="off"></label>`}<label>Usuário<input name="username" required autocomplete="username" minlength="3" maxlength="50"></label><label>Senha<input type="password" name="password" required minlength="${configured ? 1 : 12}" maxlength="200" autocomplete="${configured ? 'current-password' : 'new-password'}"></label>${configured ? '' : '<label>Repita a senha<input type="password" name="confirmation" required minlength="12" autocomplete="new-password"></label>'}<p id="auth-error" class="auth-error" role="alert" hidden></p><button class="primary" type="submit">${configured ? 'Entrar' : 'Cadastrar e entrar'}</button><a class="muted" href="/">Voltar ao atlas de consulta</a></form>`;
  $('#auth-form').onsubmit = async (e) => {
    e.preventDefault();
    const b = e.currentTarget.querySelector('button');
    b.disabled = true;
    try {
      const fields = Object.fromEntries(new FormData(e.currentTarget));
      if (!configured && fields.password !== fields.confirmation)
        throw new Error('As senhas não coincidem.');
      const r = await api(configured ? 'login' : 'setup', fields);
      S.user = r.user;
      S.csrf = r.csrf;
      await start();
    } catch (e) {
      message(e.message, true);
    } finally {
      b.disabled = false;
    }
  };
}
async function start() {
  S.overview = await api('overview');
  $('#auth').hidden = true;
  $('#admin-app').hidden = false;
  S.resources = await Promise.all([
    fetch('/api/base').then((r) => r.json()),
    fetch('/api/map-sources').then((r) => r.json()),
  ]).then(([base, sources]) => ({ base, sources: sources.sources }));
  warmRouter();
  await go(location.hash === '#observed' ? 'observed' : 'list');
}
async function warmRouter() {
  clearInterval(routerTimer);
  const update = async () => {
    try {
      S.router = await api('router');
      updateRouterStatus();
      if (S.router.ready) clearInterval(routerTimer);
    } catch (e) {
      if (e.status !== 401) message(e.message, true);
    }
  };
  await update();
  if (!S.router.ready) routerTimer = setInterval(update, 4000);
}
function updateRouterStatus() {
  if (S.router.ready)
    S.maps.forEach((m) => {
      m.loadRoads?.();
      m.loadDragRoads?.();
    });
  const n = $('#router-status');
  if (n)
    n.textContent = S.router.ready
      ? 'Malha local pronta'
      : S.router.loading
        ? 'Preparando malha local…'
        : S.router.error || 'Malha local indisponível';
  $$('[data-needs-router]').forEach((b) => (b.disabled = !S.router.ready));
}
function cleanup() {
  const maps = S.maps;
  S.maps = [];
  for (const m of maps) {
    m.off('moveend');
    if (S.screen === 'editor')
      S.view = { center: m.getCenter(), zoom: m.getZoom() };
    m.remove();
  }
  S.maps = [];
  clearInterval(jobTimer);
}
function header(eyebrow, title, subtitle, actions = '') {
  return `<div class="heading"><div><span class="eyebrow">${eyebrow}</span><h1>${title}</h1><p class="muted">${subtitle}</p></div><div class="actions">${actions}</div></div>`;
}
function classOptions(value) {
  return Object.entries(labels)
    .map(
      ([k, v]) =>
        `<option value="${k}" ${value === k ? 'selected' : ''}>${v}</option>`,
    )
    .join('');
}
function placeOptions(value) {
  return (
    '<option value="">Escolher referência</option>' +
    Object.entries(S.overview.places)
      .filter(([k, v]) => !v.archived || k === value)
      .sort((a, b) => a[1].label.localeCompare(b[1].label))
      .map(
        ([k, v]) =>
          `<option value="${esc(k)}" ${k === value ? 'selected' : ''}>${esc(v.label)}</option>`,
      )
      .join('')
  );
}
async function go(screen) {
  if (S.screen === 'places' && S.placeDirty) {
    if (
      !(await confirmAction(
        'Sair sem salvar a referência?',
        'As mudanças deste formulário serão descartadas.',
      ))
    )
      return;
    S.placeDirty = false;
  }
  const request = ++S.navRequest;
  S.routeRequest++;
  if (S.draft && S.dirty) await saveDraft();
  if (request !== S.navRequest) return;
  cleanup();
  S.screen = screen;
  $('#message').hidden = true;
  $$('[data-nav]').forEach((b) =>
    b.classList.toggle(
      'active',
      b.dataset.nav ===
        (screen === 'places'
          ? 'places'
          : screen === 'batch'
            ? 'batch'
            : screen === 'observed'
              ? 'observed'
              : screen === 'history'
                ? 'history'
                : 'list'),
    ),
  );
  if (screen === 'list') {
    const overview = await api('overview');
    if (request !== S.navRequest) return;
    S.overview = overview;
    renderList();
  } else if (screen === 'places' || screen === 'batch') {
    const overview = await api('overview');
    if (request !== S.navRequest) return;
    S.overview = overview;
    if (screen === 'places') renderPlaces();
    else renderBatch();
  } else if (screen === 'create') renderCreate();
  else if (screen === 'editor') renderEditor();
  else if (screen === 'compare') {
    await loadBaseline();
    await loadObserved();
    if (request !== S.navRequest) return;
    S.compareSource = 'published';
    renderCompare();
  } else if (screen === 'save') renderSave();
  else if (screen === 'review') {
    const review = await api(`drafts/${S.draft.id}/review`);
    if (request !== S.navRequest) return;
    S.review = review;
    renderReview();
  } else if (screen === 'history') {
    const overview = await api('overview');
    if (request !== S.navRequest) return;
    S.overview = overview;
    renderHistory();
  } else if (screen === 'observed') {
    const overview = await api('overview');
    await loadObserved();
    if (request !== S.navRequest) return;
    S.overview = overview;
    renderObserved();
  }
}

function renderLegacyList() {
  const published = S.overview.lines;
  const newDrafts = S.overview.drafts.filter(
    (d) => !published.some((l) => l.id === d.line_id),
  );
  $('#admin-body').innerHTML =
    header(
      'PLANEJAMENTO / CATÁLOGO',
      'Linhas da proposta',
      `Publicação ${S.overview.release.number} · ${published.length} serviços · ${S.overview.drafts.length} rascunhos`,
      `<button data-action="new" class="primary">+ Criar linha</button>`,
    ) +
    `<div class="row"><label style="flex:1">Encontrar linha<input id="line-search" type="search" placeholder="Código, nome, bairro ou terminal"></label><label>Classe<select id="class-filter"><option value="all">Todas</option>${classOptions('')}</select></label></div><div class="surface table-wrap"><table><thead><tr><th>Linha</th><th>Percurso</th><th>Estado</th><th>Ações</th></tr></thead><tbody id="line-table"></tbody></table></div>${newDrafts.length ? '<section class="surface stack"><h3>Linhas novas em rascunho</h3>' + newDrafts.map((d) => `<div class="spread"><div><span class="mono">${esc(d.payload.line.code || 'Sem código')}</span> · ${esc(d.payload.line.name || 'Sem nome')}<p class="muted">${stamp(d.updated)} · não publicada</p></div><button data-open-draft="${d.id}">Retomar rascunho</button></div>`).join('') + '</section>' : ''}<p class="note">O atlas usa somente a publicação ativa. Edições e novas linhas ficam separadas em rascunhos.</p>`;
  const draw = () => {
    const query = $('#line-search')
      .value.normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toLowerCase();
    const type = $('#class-filter').value;
    $('#line-table').innerHTML = published
      .filter(
        (l) =>
          (type === 'all' || l.type === type) &&
          `${l.code} ${l.name} ${l.itinerary}`
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, '')
            .toLowerCase()
            .includes(query),
      )
      .map(
        (l) =>
          `<tr><td class="code">${esc(l.code)}</td><td><span class="line-title">${esc(l.name)}</span><small>${esc(l.itinerary)}</small></td><td>${l.draft ? 'Rascunho disponível' : 'Publicada'}<small>V${l.version}</small></td><td><div class="actions"><button data-edit="${l.id}">${l.draft ? 'Retomar' : 'Editar'}</button><button data-duplicate="${l.id}">Duplicar</button></div></td></tr>`,
      )
      .join('');
  };
  $('#line-search').oninput = draw;
  $('#class-filter').onchange = draw;
  draw();
}
function renderCreate(source = null) {
  const line = source || {
    code: '',
    name: '',
    type: 'integracional',
    kind: 'bidirectional',
    points: [],
  };
  $('#admin-body').innerHTML =
    header(
      'NOVA LINHA / IDENTIFICAÇÃO',
      'Começar um percurso',
      'Cadastre a linha e construa seus sentidos no editor.',
    ) +
    `<form id="create-form" class="surface stack"><label>Como começar<select name="source"><option value="">Começar em branco</option>${S.overview.lines.map((l) => `<option value="${l.id}" ${source?.id === l.id ? 'selected' : ''}>Duplicar ${esc(l.code)} · ${esc(l.name)}</option>`).join('')}</select></label><div class="form-grid"><label>Código de estudo<input name="code" value="${esc(source ? source.code + '' : line.code)}" placeholder="I-132" required maxlength="30"></label><label>Classe<select name="type">${classOptions(line.type)}</select></label></div><label>Nome<input name="name" required maxlength="300" value="${esc(source ? 'Alternativa · ' + source.name : '')}"></label><div class="form-grid"><label>Origem<select name="origin">${placeOptions(line.points[0])}</select></label><label>Destino<select name="destination">${placeOptions(line.points.at(-1))}</select></label></div><label>Organização<select name="kind"><option value="bidirectional" ${line.kind === 'bidirectional' ? 'selected' : ''}>Bidirecional · ida e volta</option><option value="circular" ${line.kind === 'circular' ? 'selected' : ''}>Circular · circuito</option><option value="oneway" ${line.kind === 'oneway' ? 'selected' : ''}>Unidirecional · ida</option></select></label><label>Objetivo da linha<textarea name="itinerary" placeholder="Bairros, ligações e cobertura pretendida">${esc(source?.itinerary || '')}</textarea></label><div class="note">O código deve estar disponível. Ao duplicar, os percursos de origem são copiados para um novo rascunho, preservando a linha existente.</div><div class="spread rule"><button type="button" data-nav="list">Voltar às linhas</button><button class="primary" type="submit">Criar rascunho e abrir editor →</button></div></form>`;
  $('#create-form').onsubmit = async (e) => {
    e.preventDefault();
    await run(async () => {
      const b = Object.fromEntries(new FormData(e.currentTarget));
      if (S.overview.lines.some((l) => l.code === b.code.trim().toUpperCase()))
        throw new Error(
          'O código já está publicado. Abra a linha existente ou escolha outro código.',
        );
      let body = {
        code: b.code,
        name: b.name,
        type: b.type,
        kind: b.kind,
        points: [b.origin, b.destination].filter(Boolean),
        itinerary: b.itinerary,
      };
      if (b.source) body.line_id = b.source;
      else
        body.payload = {
          line: {
            ...body,
            points: [b.origin, b.destination].filter(Boolean),
            itinerary: b.itinerary,
            note: '',
          },
          features: emptyFeatures(b.kind),
        };
      const d = await api('drafts', body);
      await openDraft(d.id);
    });
  };
}
function emptyFeatures(kind) {
  return (
    kind === 'bidirectional'
      ? ['ida', 'volta']
      : kind === 'circular'
        ? ['circuito']
        : ['ida']
  ).map((k) => ({
    type: 'Feature',
    properties: {
      sentido: k,
      path_id: id(),
      label: k === 'circuito' ? 'Circuito' : k === 'ida' ? 'Ida' : 'Volta',
      locked_sections: [],
      source: 'edicao-administrativa',
    },
    geometry: { type: 'LineString', coordinates: [] },
  }));
}
async function openDraft(did) {
  if (S.draft && S.dirty) await saveDraft();
  S.draft = await api('drafts/' + did);
  S.payload = clone(S.draft.payload);
  S.path = 0;
  S.preview = null;
  S.via = [];
  S.draw = [];
  S.segment = null;
  S.mode = 'drag';
  S.advancedEditor = false;
  S.undo = [];
  S.redo = [];
  S.dirty = false;
  S.view = null;
  S.recovery = null;
  try {
    const r = JSON.parse(localStorage.getItem(recoveryKey()) || 'null');
    if (r && JSON.stringify(r.payload) !== JSON.stringify(S.payload))
      S.recovery = r;
  } catch {}
  await go('editor');
}
function chooseSegment() {
  const ps = points();
  if (ps.length < 2) return null;
  const locks = current().properties.locked_sections || [];
  let ranges = [];
  for (const l of locks) {
    const i = ps.findIndex(
      (p, k) =>
        same(p, l.coordinates[0]) &&
        JSON.stringify(ps.slice(k, k + l.coordinates.length)) ===
          JSON.stringify(l.coordinates),
    );
    if (i >= 0) ranges.push([i, i + l.coordinates.length - 1]);
  }
  ranges.sort((a, b) => a[0] - b[0]);
  let start = 0;
  for (const [a, b] of ranges) {
    if (a - start > 1) return { from: start, to: a };
    start = Math.max(start, b);
  }
  return ps.length - 1 - start > 1
    ? { from: start, to: ps.length - 1 }
    : { from: 0, to: ps.length - 1 };
}
function same(a, b) {
  return a && b && a[0] === b[0] && a[1] === b[1];
}
function editorFields() {
  const l = S.payload.line;
  return `<details class="editor-metadata"><summary>Identificação, terminais e observações da linha</summary><div class="form-grid"><label>Código<input data-field="code" value="${esc(l.code)}"></label><label>Nome<input data-field="name" value="${esc(l.name)}"></label><label>Classe<select data-field="type">${classOptions(l.type)}</select></label><label>Organização<select data-field="kind"><option value="bidirectional" ${l.kind === 'bidirectional' ? 'selected' : ''}>Bidirecional</option><option value="circular" ${l.kind === 'circular' ? 'selected' : ''}>Circular</option><option value="oneway" ${l.kind === 'oneway' ? 'selected' : ''}>Unidirecional</option></select></label><label>Origem<select data-place="origin">${placeOptions(l.points[0])}</select></label><label>Destino<select data-place="destination">${placeOptions(l.points.at(-1))}</select></label><label>Itinerário<textarea data-field="itinerary">${esc(l.itinerary)}</textarea></label><label>Observações<textarea data-field="note">${esc(l.note)}</textarea></label></div></details>`;
}
function renderEditor() {
  if (!S.payload) return;
  const f = current();
  if (!f) {
    mutate(() =>
      S.payload.features.push(...emptyFeatures(S.payload.line.kind)),
    );
    S.path = 0;
    return renderEditor();
  }
  if (!S.segment) S.segment = chooseSegment();
  const ps = points();
  if (!ps.length && !S.draw.length) {
    const places = S.payload.line.points;
    const a = S.overview.places[places[0]],
      b = S.overview.places[places.at(-1)];
    if (a && b && places[0] !== places.at(-1)) {
      S.draw = [a.route_position || a.position, b.route_position || b.position];
      if (f.properties.sentido === 'volta') S.draw.reverse();
    }
  }
  $('#admin-body').classList.toggle('focus-map', S.focus);
  $('#admin-body').innerHTML =
    header(
      'EDITOR / CENÁRIO BASE',
      `${esc(S.payload.line.code || 'Nova linha')} · Editar percurso`,
      `${esc(S.payload.line.name)} · rascunho separado da publicação`,
      `<button data-nav="save">Salvar versão</button><button class="primary" data-nav="review">Revisar publicação</button>`,
    ) +
    (S.recovery
      ? `<div class="recovery"><strong>Há alterações recuperáveis neste navegador.</strong><p>O servidor tem revisão ${S.draft.revision}; a cópia local partiu da revisão ${S.recovery.revision}. Confira antes de recuperar.</p><div class="actions"><button data-action="recover">Recuperar como rascunho atual</button><button data-action="discard-recovery">Descartar cópia local</button></div></div>`
      : '') +
    `<div class="editor">${editorFields()}<div class="editor-head"><div class="directions">${S.payload.features.map((v, i) => `<button data-path="${i}" aria-pressed="${i === S.path}">${esc(v.properties.label || v.properties.sentido)}</button>`).join('')}<button data-action="add-path">+ Sentido / variante</button></div><div class="actions"><button data-action="undo" ${S.undo.length ? '' : 'disabled'}>↶ Desfazer</button><button data-action="redo" ${S.redo.length ? '' : 'disabled'}>↷ Refazer</button><button data-nav="compare">Comparar</button><button data-action="focus">${S.focus ? 'Recolher' : 'Ampliar mapa'}</button></div></div><div class="editor-grid"><aside class="points"><h3>${ps.length ? 'Trecho em edição' : 'Construir percurso'}</h3><p class="muted">${ps.length ? 'Selecione início e fim na linha. Arraste as referências vermelhas para outra rua.' : 'Clique no mapa para adicionar passagens. Arraste e reordene as referências.'}</p><div class="stack" id="point-list"></div>${ps.length ? `<div class="pair"><span>Início / fim</span><span>${S.segment?.from ?? '—'} → ${S.segment?.to ?? '—'}</span></div><button data-mode="from">Selecionar início A</button><button data-mode="to">Selecionar fim B</button><button data-mode="via">+ Passagem no trecho</button>` : `<button data-mode="draw">+ Referência no mapa</button><button class="primary" data-action="calculate-new" data-needs-router>Calcular percurso</button><button data-action="clear-draw">Limpar referências</button>`}<p class="muted">Referências não equivalem a paradas.</p>${editorExtensions()}<button data-action="import-observed">Consultar rede SEMOB</button>${f.properties.sentido === 'volta' ? '<button data-action="from-ida" data-needs-router>Recalcular volta a partir da ida</button>' : ''}</aside><div class="mapcol"><div class="map-tools"><button data-mode="drag" aria-pressed="${S.mode === 'drag'}">Arrastar rota</button><button data-mode="navigate" aria-pressed="${S.mode === 'navigate'}">Navegar</button><button data-mode="via" aria-pressed="${S.mode === 'via'}">Seleção avançada</button><button data-action="lock">Preservar seleção</button><select id="editor-base" aria-label="Mapa base"></select></div><div id="editor-map" class="map" aria-label="Editor de rotas por arrastar e soltar"></div></div><aside class="context"><div class="stack"><span class="eyebrow">PRÉVIA DO TRECHO</span><h3>${esc(f.properties.label || f.properties.sentido)}</h3><label>Nome do sentido / variante<input id="path-label" maxlength="160" value="${esc(f.properties.label || f.properties.sentido)}"></label><div id="preview-status" class="route-status">${S.preview ? `Antes: ${km(S.preview.old_km || 0)} km · alternativa: ${km(S.preview.new_km || S.preview.distance_km)} km` : 'Sem prévia pendente. O percurso exibido é o rascunho.'}</div><button class="primary" data-action="calculate" data-needs-router ${ps.length ? '' : 'hidden'}>Calcular alternativa</button><button data-action="apply" ${S.preview ? '' : 'disabled'}>Aplicar alternativa</button><button data-action="discard" ${S.preview ? '' : 'disabled'}>Descartar prévia</button>${S.preview ? `<p class="muted">${S.preview.snap_offsets_m ? 'Encaixes na via: ' + S.preview.snap_offsets_m.map((v) => v + ' m').join(' / ') : ''}</p><details><summary>Vias da alternativa</summary><ol>${S.preview.streets.map((s) => `<li>${esc(s)}</li>`).join('')}</ol></details>` : ''}</div><div class="stack"><span class="eyebrow">TRECHOS PRESERVADOS</span>${(f.properties.locked_sections || []).map((l, i) => `<div class="lock"><span>▣ ${esc(l.label || 'Trecho preservado')}</span><button data-unlock="${i}">Desbloquear trecho</button></div>`).join('') || '<p class="muted">Nenhum bloqueio neste sentido.</p>'}<p class="note">O cálculo não modifica os trechos preservados. Conversões e gabarito ainda exigem validação operacional.</p></div><div class="stack"><span class="eyebrow">MALHA VIÁRIA</span>${S.payload.line.routing_policy ? `<p class="muted">Regras viárias da referência ${esc(S.payload.line.routing_policy)} preservadas.</p>` : ''}<p id="router-status" class="muted"></p>${S.router.error ? '<button data-action="warm-router">Tentar preparar malha</button>' : ''}<button class="danger" data-action="delete-path">Remover este sentido</button></div></aside></div><div class="editor-foot"><span>${esc(f.properties.label || f.properties.sentido)} / ${km(f.properties.distancia_km)} km</span><span>Arraste → calcule → confira → aplique → salve</span><span>© OpenStreetMap contributors · Filipeia / IBGE</span></div></div>`;
  $$('[data-field]').forEach((input) =>
    input.addEventListener('input', () => {
      mutate(() => (S.payload.line[input.dataset.field] = input.value));
    }),
  );
  $$('[data-place]').forEach(
    (input) =>
      (input.onchange = () => {
        mutate(() => {
          const a = $('[data-place=origin]').value,
            b = $('[data-place=destination]').value;
          S.payload.line.points = [a, b].filter(Boolean);
        });
      }),
  );
  $('#path-label').oninput = (e) =>
    mutate(() => (current().properties.label = e.target.value));
  if (ps.length && !S.advancedEditor) {
    $('.editor-grid .points').innerHTML = routeDragSidebar();
    $('[data-action=calculate]').hidden = true;
    $('[data-action=lock]').hidden = true;
  } else {
    drawPointList();
    bindEditorExtensions();
  }
  drawEditor();
  updateRouterStatus();
  saveStatus(
    S.dirty
      ? 'Alterações locais · salvando…'
      : 'Rascunho salvo · ' + stamp(S.draft.updated),
  );
}
function drawPointList() {
  const refs = points().length ? S.via : S.draw;
  $('#point-list').innerHTML = refs.length
    ? refs
        .map(
          (p, i) =>
            `<div class="point" draggable="true" data-point="${i}"><span><span class="mono">${String(i + 1).padStart(2, '0')}</span> ${p[1].toFixed(5)}, ${p[0].toFixed(5)}<small>Arraste no mapa ou reordene aqui</small></span><button data-remove-point="${i}" aria-label="Remover referência ${i + 1}">×</button></div>`,
        )
        .join('')
    : '<p class="muted">Clique no mapa ou arraste o ponto central do trecho para criar uma passagem.</p>';
  let dragged;
  $$('[data-point]').forEach((row) => {
    row.ondragstart = (e) => {
      dragged = Number(row.dataset.point);
      e.dataTransfer.setData('text/plain', String(dragged));
      row.classList.add('dragging');
    };
    row.ondragend = () => row.classList.remove('dragging');
    row.ondragover = (e) => e.preventDefault();
    row.ondrop = (e) => {
      e.preventDefault();
      const target = Number(row.dataset.point);
      if (!Number.isInteger(dragged)) return;
      const [p] = refs.splice(dragged, 1);
      refs.splice(target, 0, p);
      S.preview = null;
      renderEditorAgain();
    };
  });
}
function geometryFeature(geometry, properties = {}) {
  return { type: 'Feature', properties, geometry };
}
function textNode(value) {
  const node = document.createElement('span');
  node.textContent = value;
  return node;
}
function makeMap(container, features, baseId = null, fit = true) {
  const map = L.map(container, {
    zoomControl: true,
    minZoom: 9,
    maxZoom: 19,
  }).setView([-7.145, -34.87], 12);
  S.maps.push(map);
  map.createPane('adminBase');
  map.getPane('adminBase').style.zIndex = 350;
  map.createPane('adminRoads');
  map.getPane('adminRoads').style.zIndex = 390;
  let roadsLayer = null,
    roadsTimer;
  map.loadRoads = async () => {
    if (!S.router.ready || map.getZoom() < 13 || !S.maps.includes(map)) return;
    const b = map.getBounds();
    const bbox = [b.getWest(), b.getSouth(), b.getEast(), b.getNorth()]
      .map((v) => v.toFixed(3))
      .join(',');
    if (map.roadsKey === bbox) return;
    map.roadsKey = bbox;
    try {
      const data = await api('roads?bbox=' + encodeURIComponent(bbox));
      if (!S.maps.includes(map)) return;
      if (roadsLayer) roadsLayer.remove();
      roadsLayer = L.geoJSON(data, {
        pane: 'adminRoads',
        style: { color: '#b4ada0', weight: 1, opacity: 0.8 },
        onEachFeature: (f, l) => l.bindTooltip(textNode(f.properties.name)),
      }).addTo(map);
    } catch {
      map.roadsKey = null;
    }
  };
  map.on('moveend', () => {
    clearTimeout(roadsTimer);
    roadsTimer = setTimeout(() => map.loadRoads(), 400);
  });
  map.on('unload', () => clearTimeout(roadsTimer));
  const local = L.layerGroup();
  for (const [name, style] of [
    [
      'land',
      { fillColor: '#eeeee7', fillOpacity: 1, color: '#bbbcb4', weight: 0.8 },
    ],
    [
      'neighborhoods',
      {
        fillColor: '#f5f4ef',
        fillOpacity: 0.75,
        color: '#d0cec4',
        weight: 0.6,
      },
    ],
    ['rivers', { color: '#a9cbd1', fillColor: '#c5dce0', weight: 0.7 }],
    ['roads', { color: '#c6bfb4', weight: 1.3, fill: false }],
  ])
    L.geoJSON(
      {
        type: 'FeatureCollection',
        features: S.resources.base[name].filter(Boolean),
      },
      { style, interactive: false, pane: 'adminBase' },
    ).addTo(local);
  local.addTo(map);
  map.attributionControl.addAttribution(
    'Filipeia · IBGE · © <a href="https://www.openstreetmap.org/copyright">OpenStreetMap contributors</a>',
  );
  let tile = null;
  const setBase = (value) => {
    if (tile) {
      tile.remove();
      tile = null;
    }
    local.remove();
    if (value === 'local') {
      local.addTo(map);
      return;
    }
    const src = S.resources.sources.find((s) => s.id === value);
    if (!src) {
      local.addTo(map);
      return;
    }
    tile = L.tileLayer(src.url, {
      maxZoom: src.maxZoom,
      attribution: src.attribution,
      referrerPolicy: 'strict-origin-when-cross-origin',
    }).addTo(map);
    tile.once('tileerror', () => {
      setBase('local');
      if (baseId) document.getElementById(baseId).value = 'local';
    });
  };
  if (baseId) {
    const select = document.getElementById(baseId);
    select.innerHTML =
      '<option value="local">Local · sem internet</option>' +
      S.resources.sources
        .filter((s) => s.id !== 'local')
        .map((s) => `<option value="${s.id}">${esc(s.label)}</option>`)
        .join('');
    select.onchange = () => setBase(select.value);
  }
  const layer = L.geoJSON(
    {
      type: 'FeatureCollection',
      features: features.filter((f) => f.geometry.coordinates.length >= 2),
    },
    {
      style: (f) => ({
        color: f.properties.sentido === 'volta' ? '#77736b' : '#08756c',
        weight: 4,
        opacity: 1,
        dashArray: f.properties.sentido === 'volta' ? '6 5' : null,
      }),
    },
  ).addTo(map);
  if (fit && layer.getLayers().length)
    map.fitBounds(layer.getBounds(), {
      padding: [35, 35],
      maxZoom: 16,
      animate: false,
    });
  map.loadRoads();
  return map;
}
function nearestIndex(map, latlng, coords) {
  const p = map.latLngToLayerPoint(latlng);
  let best = 0,
    min = Infinity;
  coords.forEach((c, i) => {
    const q = map.latLngToLayerPoint([c[1], c[0]]);
    const d = p.distanceTo(q);
    if (d < min) {
      min = d;
      best = i;
    }
  });
  return best;
}
function drawEditor() {
  const ps = points(),
    f = current();
  const map = makeMap('editor-map', [f], 'editor-base', !S.view);
  if (S.view) map.setView(S.view.center, S.view.zoom, { animate: false });
  map.on('moveend', () => {
    if (S.screen === 'editor' && S.maps.includes(map))
      S.view = { center: map.getCenter(), zoom: map.getZoom() };
  });
  if (S.preview)
    L.geoJSON(geometryFeature(S.preview.geometry), {
      style: { color: '#c71020', weight: 5 },
    }).addTo(map);
  if (ps.length && S.segment && S.advancedEditor) {
    const { from, to } = S.segment;
    const range = ps.slice(from, to + 1);
    L.polyline(
      range.map((p) => [p[1], p[0]]),
      { color: '#c71020', weight: 6, opacity: 0.55 },
    ).addTo(map);
    for (const [i, label] of [
      [from, 'A'],
      [to, 'B'],
    ])
      L.marker([ps[i][1], ps[i][0]], {
        icon: L.divIcon({
          className: 'route-handle',
          html: label,
          iconSize: [26, 26],
          iconAnchor: [13, 13],
        }),
      })
        .bindTooltip(
          textNode(label === 'A' ? 'Início do trecho' : 'Fim do trecho'),
        )
        .addTo(map);
    if (!S.via.length) {
      const mid = ps[Math.floor((from + to) / 2)];
      L.marker([mid[1], mid[0]], {
        draggable: true,
        icon: L.divIcon({
          className: 'route-handle',
          html: '↔',
          iconSize: [26, 26],
          iconAnchor: [13, 13],
        }),
      })
        .bindTooltip(textNode('Arraste para outra rua'))
        .on('dragend', (e) => {
          const p = e.target.getLatLng();
          S.via = [[p.lng, p.lat]];
          run(() => calculatePreview());
        })
        .addTo(map);
    }
  }
  const refs = ps.length ? (S.advancedEditor ? S.via : []) : S.draw;
  refs.forEach((p, i) =>
    L.marker([p[1], p[0]], {
      draggable: true,
      icon: L.divIcon({
        className: 'route-handle',
        html: String(i + 1),
        iconSize: [26, 26],
        iconAnchor: [13, 13],
      }),
    })
      .bindTooltip(textNode('Referência ' + (i + 1)))
      .on('dragend', (e) => {
        const ll = e.target.getLatLng();
        refs[i] = [ll.lng, ll.lat];
        S.preview = null;
        if (ps.length) run(() => calculatePreview());
        else renderEditorAgain();
      })
      .addTo(map),
  );
  if (!ps.length && refs.length > 1)
    map.fitBounds(
      refs.map((p) => [p[1], p[0]]),
      { padding: [40, 40], maxZoom: 16, animate: false },
    );
  drawEditorExtensions(map);
  installRouteDragging(map, f);
  map.on('click', (e) => {
    if (S.mode === 'permanent') {
      addPermanent([e.latlng.lng, e.latlng.lat]);
      return;
    }
    if (S.mode === 'from' || S.mode === 'to') {
      if (ps.length < 2) return;
      const i = nearestIndex(map, e.latlng, ps);
      if (offerOverlappingVertices(map, e.latlng, ps, i, S.mode)) return;
      const next = { ...S.segment, [S.mode]: i };
      if (next.from >= next.to) {
        message('O início deve vir antes do fim no sentido da linha.', true);
        return;
      }
      S.segment = next;
      S.via = [];
      S.preview = null;
      S.mode = 'navigate';
      renderEditorAgain();
    } else if (S.mode === 'draw' || S.mode === 'via') {
      const p = [e.latlng.lng, e.latlng.lat];
      if (ps.length) {
        S.via.push(p);
        S.preview = null;
        renderEditorAgain();
      } else {
        S.draw.push(p);
        renderEditorAgain();
      }
    }
  });
}
function renderEditorAgain() {
  S.navRequest++;
  S.routeRequest++;
  cleanup();
  S.screen = 'editor';
  renderEditor();
}
async function calculatePreview(direct = false) {
  await saveDraft();
  const request = ++S.routeRequest;
  if (!S.router.ready)
    throw new Error(S.router.error || 'A malha local está sendo preparada.');
  if (!S.segment || (!S.via.length && !direct))
    throw new Error(
      'Selecione o trecho e adicione ou arraste uma referência intermediária.',
    );
  const did = S.draft.id,
    pathId = current().properties.path_id;
  const from = S.segment.from,
    to = S.segment.to;
  message('Calculando o trecho nas ruas públicas…');
  const result = await api(`drafts/${did}/route-preview`, {
    revision: S.draft.revision,
    path_id: pathId,
    from,
    to,
    via: direct ? [] : S.via,
    direct,
  });
  if (
    request !== S.routeRequest ||
    S.screen !== 'editor' ||
    S.dirty ||
    S.draft.id !== did ||
    current().properties.path_id !== pathId ||
    S.draft.revision !== result.revision
  )
    return;
  S.preview = { ...result, passage_controls: direct ? [] : clone(S.via) };
  renderEditorAgain();
  message(
    'Alternativa calculada. Confira as vias e aplique para alterar o rascunho.',
  );
}
async function calculateNew(refs = S.draw) {
  await saveDraft();
  const request = ++S.routeRequest;
  if (refs.length < 2)
    throw new Error('Escolha ao menos origem e destino no mapa.');
  const pathId = current().properties.path_id;
  message('Calculando percurso viário…');
  const result = await api('route-create', {
    points: refs,
    draft_id: S.draft.id,
    revision: S.draft.revision,
    path_id: pathId,
  });
  if (
    request !== S.routeRequest ||
    S.screen !== 'editor' ||
    S.dirty ||
    S.draft.revision !== result.revision ||
    current().properties.path_id !== pathId
  )
    return;
  S.preview = {
    ...result,
    new_km: result.distance_km,
    old_km: current().properties.distancia_km || 0,
    creating: true,
    controls: clone(refs),
  };
  renderEditorAgain();
  message('Percurso calculado. Aplique a prévia para gravá-lo no rascunho.');
}
async function loadBaseline() {
  const r = await api(`drafts/${S.draft.id}/review`);
  S.baseline = r.baseline;
}
function renderCompare() {
  const before = S.baseline;
  const next = clone(S.payload);
  if (S.preview) next.features[S.path].geometry = S.preview.geometry;
  $('#admin-body').innerHTML =
    header(
      'COMPARAÇÃO / ANTES DE SALVAR',
      'Conferir a alteração',
      S.preview
        ? 'Prévia ainda não aplicada ao rascunho.'
        : 'Rascunho atual versus publicação ativa.',
      `<button data-nav="editor">Voltar ao editor</button>`,
    ) +
    `<label>Referência da comparação<select id="compare-source"><option value="published">Publicação atual desta linha</option><optgroup label="Versões salvas">${(S.draft.versions || []).map((v) => `<option value="version:${v.id}" ${S.compareSource === 'version:' + v.id ? 'selected' : ''}>V${v.number} · ${stamp(v.created)}</option>`).join('')}</optgroup><optgroup label="Rede observada SEMOB">${(S.observed?.lines || []).map((l) => `<option value="semob:${l.code}" ${S.compareSource === 'semob:' + l.code ? 'selected' : ''}>${esc(l.code)} · ${esc(l.name)}</option>`).join('')}</optgroup></select></label><div class="compare-grid"><section class="surface stack"><h3>${esc(S.compareSource?.startsWith('semob:') ? 'Referência SEMOB' : S.compareSource?.startsWith('version:') ? 'Versão salva' : 'Publicação atual')}</h3><div id="before-map" class="map compare-map"></div></section><section class="surface stack"><h3>${S.preview ? 'Prévia não aplicada' : 'Rascunho'}</h3><div id="after-map" class="map compare-map"></div></section></div><section class="surface table-wrap"><table><thead><tr><th>Sentido</th><th>Publicado</th><th>Rascunho / prévia</th></tr></thead><tbody>${next.features
      .map((f) => {
        const p = f.properties;
        const old = before?.features.find(
          (v) => v.properties.sentido === p.sentido,
        );
        return `<tr><td>${esc(p.label || p.sentido)}</td><td>${old ? km(old.properties.distancia_km) + ' km' : 'Linha nova'}</td><td>${km(measure(f.geometry.coordinates))} km</td></tr>`;
      })
      .join(
        '',
      )}</tbody></table><div class="actions rule"><button data-nav="editor">Continuar editando</button><button class="primary" data-nav="save">Salvar versão</button></div></section>`;
  $('#compare-source').onchange = (e) =>
    run(async () => {
      const source = e.target.value;
      const request = ++S.compareRequest;
      const nav = S.navRequest;
      let baseline;
      message('Carregando a referência de comparação…');
      if (source === 'published')
        baseline = (await api(`drafts/${S.draft.id}/review`)).baseline;
      else if (source.startsWith('version:'))
        baseline = (await api('versions/' + source.slice(8))).payload;
      else {
        const code = source.slice(6);
        const features = (S.observed?.geojson.features || [])
          .filter(
            (f) =>
              String(f.properties.line_code || f.properties.CODIGO_LIN) ===
                code && f.geometry.type === 'LineString',
          )
          .map((f) => ({
            type: 'Feature',
            geometry: clone(f.geometry),
            properties: {
              sentido: String(f.properties.ITINERARIO || 'ida').toLowerCase(),
              distancia_km: measure(f.geometry.coordinates),
            },
          }));
        baseline = { line: { code }, features };
      }
      if (
        request !== S.compareRequest ||
        nav !== S.navRequest ||
        S.screen !== 'compare'
      )
        return;
      S.compareSource = source;
      S.baseline = baseline;
      cleanup();
      renderCompare();
      message(
        source.startsWith('semob:')
          ? 'Referência coletada em ' +
              stamp(S.observed.retrieved_at) +
              '. O rascunho não foi alterado.'
          : 'Referência de comparação atualizada.',
      );
    });
  const a = makeMap('before-map', before?.features || []);
  const b = makeMap('after-map', next.features);
  const all = [...(before?.features || []), ...next.features].filter(
    (f) => f.geometry.coordinates.length > 1,
  );
  if (all.length) {
    const bounds = L.geoJSON({
      type: 'FeatureCollection',
      features: all,
    }).getBounds();
    a.fitBounds(bounds, { padding: [25, 25], animate: false });
    b.fitBounds(bounds, { padding: [25, 25], animate: false });
  }
  let syncing = false;
  for (const [x, y] of [
    [a, b],
    [b, a],
  ])
    x.on('moveend', () => {
      if (syncing || !S.maps.includes(x) || !S.maps.includes(y)) return;
      syncing = true;
      y.setView(x.getCenter(), x.getZoom(), { animate: false });
      syncing = false;
    });
}
function measure(ps) {
  return ps
    .slice(1)
    .reduce(
      (n, p, i) =>
        n +
        Math.hypot((p[0] - ps[i][0]) * 110440, (p[1] - ps[i][1]) * 110580) /
          1000,
      0,
    );
}
function renderSave() {
  $('#admin-body').innerHTML =
    header(
      'VERSÕES / MARCO DE TRABALHO',
      'Salvar uma versão',
      'Reúna identificação, ida, volta, referências e trechos preservados.',
      `<button data-nav="editor">Voltar ao editor</button>`,
    ) +
    `<div class="review-grid"><form id="save-version-form" class="surface stack"><h3>${esc(S.payload.line.code)} · ${esc(S.payload.line.name)}</h3>${S.payload.features.map((f) => `<div class="pair"><span>${esc(f.properties.label || f.properties.sentido)}</span><span>${km(measure(f.geometry.coordinates))} km</span></div>`).join('')}<label>Descrição da versão <span class="muted">Opcional</span><textarea name="note" placeholder="Ex.: ajuste do trecho por Novais"></textarea></label>${S.preview ? '<p class="note">Aplique ou descarte a prévia no editor antes de salvar uma versão.</p>' : ''}<button class="primary" ${S.preview ? 'disabled' : ''} type="submit">Salvar versão</button><p class="muted">Salvar não altera a publicação no atlas.</p></form><aside class="surface stack"><h3>Histórico da linha</h3>${(S.draft.versions || []).map((v) => `<div class="stack rule"><strong>V${v.number} · ${stamp(v.created)}</strong><p class="muted">${esc(v.note || 'Sem descrição')}</p><button data-restore-version="${v.id}">Recuperar no rascunho</button></div>`).join('') || '<p class="muted">Ainda não há versões salvas.</p>'}</aside></div>`;
  $('#save-version-form').onsubmit = (e) => {
    e.preventDefault();
    const note = new FormData(e.currentTarget).get('note');
    run(async () => {
      await saveDraft();
      S.draft = await api(`drafts/${S.draft.id}/save-version`, {
        revision: S.draft.revision,
        note,
      });
      await go('review');
      message('Versão salva. Confira a revisão antes de publicar.');
    });
  };
}
function renderReview() {
  const r = S.review;
  $('#admin-body').innerHTML =
    header(
      'REVISÃO / PUBLICAÇÃO NO ESTUDO',
      'Revisar antes de publicar',
      'Uma linha alterada · demais linhas preservadas.',
      `<button data-nav="editor">Voltar ao editor</button>`,
    ) +
    `<div class="review-grid"><div class="stack"><section class="surface stack"><h3>${esc(r.payload.line.code)} · ${esc(r.payload.line.name)}</h3><p>${esc(r.payload.line.itinerary)}</p><div id="review-map" class="map small-map"></div><div class="summary-grid">${r.payload.features.map((f) => `<div><span class="mono">${esc(f.properties.label || f.properties.sentido)}</span><strong>${km(f.properties.distancia_km)} km</strong></div>`).join('')}</div><div class="legend"><span>Ida / circuito</span><span class="before">Volta</span></div><button data-nav="compare">Abrir comparação detalhada</button><button data-nav="batch">Publicar junto de outras linhas e estações</button></section><section class="surface stack"><h3>Conferência</h3>${r.errors.map((e) => `<div class="issue error">✕ ${esc(e)}</div>`).join('') || '<div class="issue">✓ Identificação e geometrias obrigatórias presentes.</div>'}${r.warnings.map((w) => `<div class="issue">△ ${esc(w)}</div>`).join('')}</section></div><aside class="surface publish-box stack"><span class="eyebrow">VERSÃO DO CENÁRIO</span><h3>Publicar no atlas</h3><div class="pair"><span>Origem</span><span>${r.saved_number ? 'V' + r.saved_number : 'Sem versão salva'}</span></div><div class="pair"><span>Publicação ativa</span><span>${r.release_number}</span></div><div class="pair"><span>Impedimentos</span><span>${r.errors.length}</span></div><div class="pair"><span>Pendências declaradas</span><span>${r.warnings.length}</span></div><label class="check"><input id="publish-ack" type="checkbox"> Publicar como estudo, mantendo as pendências identificadas.</label><button data-action="publish" id="publish-button" class="primary" disabled>Publicar versão no estudo</button>${r.errors.length ? '<button data-nav="save">Salvar / corrigir versão</button>' : ''}<p class="muted">A publicação é atômica. A versão anterior permanece recuperável no histórico.</p></aside></div>`;
  makeMap('review-map', r.payload.features);
  $('#publish-ack').onchange = (e) =>
    ($('#publish-button').disabled = !e.target.checked || r.errors.length > 0);
}
function renderHistory() {
  $('#admin-body').innerHTML =
    header(
      'HISTÓRICO / REDE PUBLICADA',
      'Publicações do cenário',
      'Restaurar cria uma nova publicação; o histórico anterior permanece disponível.',
    ) +
    `<div class="surface stack">${S.overview.releases.map((r) => `<div class="spread rule"><div><h3>Publicação ${r.number} ${r.id === S.overview.release.id ? '· ativa' : ''}</h3><p>${esc(r.note)}</p><p class="muted">${stamp(r.created)}</p></div>${r.id !== S.overview.release.id ? `<button data-restore-release="${r.id}">Restaurar esta publicação</button>` : ''}</div>`).join('')}</div>`;
}
async function loadObserved() {
  const r = await fetch('/api/network?source=semob');
  S.observed = r.ok ? await r.json() : null;
}
function renderObserved() {
  $('#admin-body').innerHTML =
    header(
      'FONTE OFICIAL / ADMINISTRAÇÃO',
      'Rede atual e coletor',
      S.observed
        ? `${S.observed.lines.length} linhas locais · última coleta ${stamp(S.observed.retrieved_at)}`
        : 'Nenhuma coleta local disponível.',
      `<button class="primary" data-action="collect">Coletar catálogo completo</button>`,
    ) +
    `<section class="surface stack"><div id="collection-status" role="status">Consultando coleta…</div><progress id="collection-progress" hidden></progress><h3>Histórico das execuções</h3>${
      S.overview.jobs
        .map((j) => {
          let d;
          try {
            d = JSON.parse(j.detail);
          } catch {
            d = {};
          }
          return `<div class="job"><strong>${esc({ complete: 'Concluída', failed: 'Falha', interrupted: 'Interrompida pelo reinício', running: 'Em andamento' }[j.state] || j.state)}</strong> · ${stamp(j.created)}<p>${esc(d.message || '')}</p>${d.error ? `<p class="danger">${esc(d.error)}</p>` : ''}</div>`;
        })
        .join('') ||
      '<p class="muted">Execuções anteriores ao painel continuam nos manifests da coleta, fora deste histórico administrativo.</p>'
    }<p class="note">Coleta é uma ação administrativa. Falhas preservam os dados anteriores; geometria ausente não significa linha extinta. A proposta publicada não é recalculada pela coleta.</p></section><section class="surface stack"><h3>Linhas coletadas</h3><label>Pesquisar<input type="search" id="observed-search" placeholder="Código ou nome"></label><div class="table-wrap"><table><thead><tr><th>Código</th><th>Linha</th><th>Geometrias</th><th>Ação</th></tr></thead><tbody id="observed-lines"></tbody></table></div></section>`;
  const draw = () => {
    const q = $('#observed-search').value.toLowerCase();
    $('#observed-lines').innerHTML = (S.observed?.lines || [])
      .filter((l) => `${l.code} ${l.name}`.toLowerCase().includes(q))
      .map(
        (l) =>
          `<tr><td class="code">${esc(l.code)}</td><td>${esc(l.name)}<small>${esc(l.errors.length ? 'Coleta parcial' : 'Dados coletados')}</small></td><td>${S.observed.geojson.features.filter((f) => String(f.properties.line_code || f.properties.CODIGO_LIN) === l.code).length}</td><td><button data-import-line="${esc(l.code)}">Criar proposta</button></td></tr>`,
      )
      .join('');
  };
  $('#observed-search').oninput = draw;
  draw();
  pollCollection();
  jobTimer = setInterval(pollCollection, 2500);
}
async function pollCollection() {
  try {
    const r = await fetch('/api/status');
    const data = await r.json();
    const n = $('#collection-status');
    if (!n) return;
    n.textContent = data.job.error || data.job.message;
    if (S.collectionRunning && !data.job.running) {
      S.collectionRunning = false;
      await go('observed');
      message('Execução encerrada. Dados e histórico atualizados.');
      return;
    }
    S.collectionRunning = data.job.running;
    const p = $('#collection-progress');
    p.hidden = !data.job.running;
    p.max = data.job.total || 1;
    p.value = data.job.done;
    const b = $('[data-action=collect]');
    if (b) b.disabled = data.job.running;
  } catch (e) {
    message('Não foi possível consultar o andamento da coleta.', true);
  }
}
async function importLine(code) {
  const line = S.observed.lines.find((l) => l.code === code);
  const fs = S.observed.geojson.features.filter(
    (f) => String(f.properties.line_code || f.properties.CODIGO_LIN) === code,
  );
  if (!fs.length)
    throw new Error(
      'A SEMOB não forneceu geometria para esta linha. Crie o desenho em branco.',
    );
  const used = new Set();
  const features = fs
    .filter((f) => f.geometry.type === 'LineString')
    .map((f, i) => {
      let sentido =
        String(f.properties.ITINERARIO || '').toLowerCase() === 'volta'
          ? 'volta'
          : 'ida';
      if (used.has(sentido)) sentido += '-' + (i + 1);
      used.add(sentido);
      return {
        type: 'Feature',
        properties: {
          sentido,
          label:
            String(f.properties.ITINERARIO || 'Variante') + ' · ' + (i + 1),
          path_id: id(),
          source: 'SEMOB ' + code + ' / ' + S.observed.retrieved_at,
          reference_lines: [code],
          locked_sections: [],
        },
        geometry: clone(f.geometry),
      };
    });
  if (!features.length)
    throw new Error(
      'A fonte tem apenas geometrias multipartes. Selecione um percurso contínuo para importar.',
    );
  const d = await api('drafts', {
    payload: {
      line: {
        code: '',
        name: 'Proposta · ' + line.name,
        type: 'integracional',
        kind: used.has('ida') && used.has('volta') ? 'bidirectional' : 'oneway',
        note:
          'Referência SEMOB ' +
          code +
          ' coletada em ' +
          S.observed.retrieved_at,
        points: [],
      },
      features,
    },
  });
  await openDraft(d.id);
  message(
    'Percursos importados para um rascunho. Informe um código de estudo disponível.',
  );
}
async function run(fn) {
  try {
    await fn();
  } catch (e) {
    message(e.message, true);
  }
}
$('#logout').onclick = () =>
  run(async () => {
    if (S.dirty) await saveDraft();
    await api('logout', {});
    S.user = null;
    S.csrf = null;
    renderAuth(true);
  });
document.addEventListener('click', (e) => {
  const b = e.target.closest('button');
  if (!b || b.closest('#auth') || b.hasAttribute('data-confirm')) return;
  run(async () => {
    if (b.dataset.nav) {
      await go(b.dataset.nav);
      return;
    }
    if (b.dataset.edit) {
      const d = await api('drafts', { line_id: b.dataset.edit, edit: true });
      await openDraft(d.id);
      return;
    }
    if (b.dataset.duplicate) {
      await go('create');
      renderCreate(S.overview.lines.find((l) => l.id === b.dataset.duplicate));
      return;
    }
    if (b.dataset.openDraft) {
      await openDraft(b.dataset.openDraft);
      return;
    }
    if (b.dataset.path !== undefined) {
      await saveDraft();
      S.path = Number(b.dataset.path);
      S.preview = null;
      S.via = [];
      S.draw = [];
      S.segment = null;
      S.mode = 'drag';
      S.advancedEditor = false;
      renderEditorAgain();
      return;
    }
    if (b.dataset.mode) {
      const oldAdvanced = S.advancedEditor;
      if (b.dataset.mode === 'drag') S.advancedEditor = false;
      if (['via', 'from', 'to', 'permanent'].includes(b.dataset.mode))
        S.advancedEditor = true;
      S.mode = b.dataset.mode;
      if (oldAdvanced !== S.advancedEditor) renderEditorAgain();
      $$('[data-mode]').forEach((v) =>
        v.setAttribute('aria-pressed', String(v.dataset.mode === S.mode)),
      );
      message(
        {
          from: 'Clique na linha próximo ao início desejado.',
          to: 'Clique na linha próximo ao fim desejado.',
          via: 'Clique na rua desejada para incluir uma passagem.',
          draw: 'Clique no mapa para adicionar referências.',
          navigate: 'Modo de navegação.',
          drag: 'Segure a linha e arraste até uma rua. Aproxime o mapa para ver as ruas.',
          permanent:
            'Clique no mapa para guardar uma referência permanente neste sentido.',
        }[S.mode],
      );
      return;
    }
    if (b.dataset.removePoint !== undefined) {
      (points().length ? S.via : S.draw).splice(
        Number(b.dataset.removePoint),
        1,
      );
      S.preview = null;
      renderEditorAgain();
      return;
    }
    if (b.dataset.unlock !== undefined) {
      if (
        await confirmAction(
          'Desbloquear trecho?',
          'O trecho deixará de ser preservado nos próximos cálculos deste sentido.',
        )
      ) {
        mutate(() =>
          current().properties.locked_sections.splice(
            Number(b.dataset.unlock),
            1,
          ),
        );
        renderEditorAgain();
      }
      return;
    }
    if (b.dataset.restoreVersion) {
      if (
        await confirmAction(
          'Recuperar versão no rascunho?',
          'A publicação atual não muda. A versão selecionada substituirá o conteúdo deste rascunho.',
        )
      ) {
        await saveDraft();
        const d = await api(`drafts/${S.draft.id}/restore-version`, {
          revision: S.draft.revision,
          version_id: b.dataset.restoreVersion,
        });
        await openDraft(d.id);
      }
      return;
    }
    if (b.dataset.restoreRelease) {
      if (
        await confirmAction(
          'Restaurar publicação?',
          'O atlas passará a usar esta composição da rede. Uma nova publicação registrará a restauração.',
        )
      ) {
        await api('restore-release', {
          release_id: b.dataset.restoreRelease,
          expected_release: S.overview.release.id,
        });
        await go('history');
        message('Publicação restaurada.');
      }
      return;
    }
    if (b.dataset.importLine) {
      await importLine(b.dataset.importLine);
      return;
    }
    switch (b.dataset.action) {
      case 'new':
        await go('create');
        break;
      case 'warm-router':
        await warmRouter();
        break;
      case 'focus':
        S.focus = !S.focus;
        renderEditorAgain();
        break;
      case 'undo':
      case 'redo': {
        const source = b.dataset.action === 'undo' ? S.undo : S.redo,
          dest = b.dataset.action === 'undo' ? S.redo : S.undo;
        if (!source.length) break;
        dest.push(clone(S.payload));
        S.payload = source.pop();
        S.path = Math.min(S.path, S.payload.features.length - 1);
        S.segment = null;
        S.via = [];
        changed();
        renderEditorAgain();
        break;
      }
      case 'calculate':
        await calculatePreview();
        break;
      case 'calculate-new':
        await calculateNew();
        break;
      case 'apply': {
        if (!S.preview) break;
        const preview = clone(S.preview);
        mutate(() => {
          const f = current();
          f.geometry = preview.geometry;
          f.properties.distancia_km = preview.distance_km;
          f.properties.street_sequence = preview.creating
            ? preview.streets
            : [];
          f.properties.editor_last_segment_streets = preview.streets;
          f.properties.source = 'edicao-administrativa';
          if (preview.drag_target)
            f.properties.editor_last_drag = {
              source: preview.drag_source,
              target: preview.drag_target,
              street: preview.drag_street,
            };
          f.properties.router_fingerprint = preview.router_fingerprint;
          f.properties.manual = false;
          delete f.properties.observed_streets_percent;
          delete f.properties.central_pattern;
          if (preview.controls) {
            f.properties.editor_controls = preview.controls;
            const controls = f.properties.control_points || [];
            const used = new Set();
            f.properties.control_points = preview.controls.map((p, i) => {
              const match = controls.find(
                (c) => same(c.position, p) && !used.has(c.id),
              );
              const control = match || {
                id: id(),
                label: 'Referência ' + (i + 1),
                position: p,
              };
              used.add(control.id);
              return control;
            });
          } else if (preview.passage_controls?.length) {
            f.properties.control_points ||= [];
            for (const p of preview.passage_controls) {
              if (!f.properties.control_points.some((c) => same(c.position, p)))
                f.properties.control_points.push({
                  id: id(),
                  label: 'Passagem ' + (f.properties.control_points.length + 1),
                  position: p,
                });
            }
            f.properties.control_points.sort(
              (a, b) =>
                nearestCoordinateIndex(f.geometry.coordinates, a.position) -
                nearestCoordinateIndex(f.geometry.coordinates, b.position),
            );
          }
          if (preview.trimmed) {
            f.properties.control_points = (
              f.properties.control_points || []
            ).filter(
              (c) => distanceToRoute(c.position, f.geometry.coordinates) < 80,
            );
          }
        });
        S.via = [];
        S.draw = [];
        S.segment = null;
        renderEditorAgain();
        message(
          'Alternativa aplicada ao rascunho. Confira e salve uma versão.',
        );
        break;
      }
      case 'discard':
        S.preview = null;
        S.via = [];
        renderEditorAgain();
        break;
      case 'clear-draw':
        S.draw = [];
        S.preview = null;
        renderEditorAgain();
        break;
      case 'lock': {
        if (!S.segment) throw new Error('Selecione um trecho no percurso.');
        const { from, to } = S.segment;
        mutate(() =>
          current().properties.locked_sections.push({
            id: id(),
            label: 'Trecho preservado pelo administrador',
            coordinates: clone(points().slice(from, to + 1)),
          }),
        );
        renderEditorAgain();
        break;
      }
      case 'add-path': {
        const existing = new Set(
          S.payload.features.map((f) => f.properties.sentido),
        );
        let key = !existing.has('ida')
          ? 'ida'
          : !existing.has('volta')
            ? 'volta'
            : !existing.has('circuito') && S.payload.line.kind === 'circular'
              ? 'circuito'
              : 'variante-' + (existing.size + 1);
        mutate(() =>
          S.payload.features.push({
            type: 'Feature',
            properties: {
              sentido: key,
              label: key === 'ida' ? 'Ida' : key === 'volta' ? 'Volta' : key,
              path_id: id(),
              locked_sections: [],
            },
            geometry: { type: 'LineString', coordinates: [] },
          }),
        );
        S.path = S.payload.features.length - 1;
        S.segment = null;
        S.draw = [];
        S.via = [];
        renderEditorAgain();
        break;
      }
      case 'delete-path':
        if (
          await confirmAction(
            'Remover este sentido?',
            'Você pode desfazer. Uma linha bidirecional exige ida e volta para publicar.',
          )
        ) {
          mutate(() => S.payload.features.splice(S.path, 1));
          S.path = 0;
          S.segment = null;
          renderEditorAgain();
        }
        break;
      case 'from-ida': {
        const ida = S.payload.features.find(
          (f) => f.properties.sentido === 'ida',
        );
        if (!ida || ida.geometry.coordinates.length < 2)
          throw new Error(
            'Conclua a ida antes de gerar a referência da volta.',
          );
        const ps =
          (ida.properties.control_points?.length >= 2
            ? ida.properties.control_points.map((c) => c.position)
            : null) ||
          ida.properties.editor_controls ||
          ida.geometry.coordinates.filter(
            (_, i, all) =>
              i === 0 ||
              i === all.length - 1 ||
              i % Math.max(1, Math.floor(all.length / 7)) === 0,
          );
        await calculateNew(clone(ps).reverse());
        break;
      }
      case 'import-observed':
        await go('observed');
        message(
          'Escolha uma linha coletada para criar uma proposta a partir de seus sentidos. O rascunho anterior permanece salvo.',
        );
        break;
      case 'recover': {
        if (
          S.recovery.revision !== S.draft.revision &&
          !(await confirmAction(
            'Recuperar conteúdo local?',
            'O servidor tem uma revisão diferente. O conteúdo local substituirá o rascunho atual após sua confirmação.',
          ))
        )
          break;
        const payload = clone(S.recovery.payload);
        mutate(() => (S.payload = payload));
        S.recovery = null;
        renderEditorAgain();
        break;
      }
      case 'discard-recovery':
        localStorage.removeItem(recoveryKey());
        S.recovery = null;
        renderEditorAgain();
        break;
      case 'publish': {
        if (S.preview)
          throw new Error('Aplique ou descarte a prévia antes de publicar.');
        const r = S.review;
        const result = await api(`drafts/${S.draft.id}/publish`, {
          revision: r.revision,
          release_id: r.release_id,
          version_id: r.version_id,
          acknowledge_warnings: $('#publish-ack').checked,
        });
        await openDraft(S.draft.id);
        await go('history');
        message('Publicação ' + result.number + ' ativa no atlas.');
        break;
      }
      case 'collect':
        await api('collect', { codes: [] });
        message('Coleta do catálogo completo iniciada.');
        await pollCollection();
        break;
    }
  });
});
window.addEventListener('beforeunload', (e) => {
  if (S.dirty || S.placeDirty) {
    if (S.dirty) protect();
    e.preventDefault();
    e.returnValue = '';
  }
});
(async () => {
  try {
    const session = await api('session');
    if (session.user) {
      S.user = session.user;
      S.csrf = session.csrf;
      await start();
    } else renderAuth(session.configured);
  } catch (e) {
    $('#auth').hidden = false;
    $('#auth').textContent = 'Não foi possível iniciar o painel: ' + e.message;
  }
})();
