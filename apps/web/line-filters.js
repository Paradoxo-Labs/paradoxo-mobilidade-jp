/* Filtros de consulta: eixos documentados no estudo, numeração e vínculos cadastrados. */
(() => {
  const fold = (value) =>
    String(value || '')
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '')
      .toUpperCase()
      .replace(/[^A-Z0-9]/g, '');
  const corridors = [
    {
      id: '0',
      label: '0 · Roger / Jaguaribe / Centro',
      points: ['centro', 'jaguaribe', 'roger', 'lagoa'],
      streets: ['PARQUESOLONDELUCENA', 'PARQUESOLOMDELUCENA'],
    },
    {
      id: '1',
      label: '1 · Cruz das Armas',
      points: ['cruz'],
      streets: ['CRUZDASARMAS'],
    },
    {
      id: '2',
      label: '2 · Dois de Fevereiro / Rangel',
      points: ['rangel'],
      streets: ['2DEFEVEREIRO', 'DOISDEFEVEREIRO'],
    },
    {
      id: '3',
      label: '3 · Dom Pedro II',
      points: ['pedro', 'ufpb_dp2'],
      streets: ['DOMPEDROII', 'DOMPEDROSEGUNDO'],
    },
    {
      id: '4',
      label: '4 · Beira-Rio',
      points: ['beira'],
      streets: ['BEIRARIO', 'JOSEAMERICODEALMEIDA'],
    },
    {
      id: '5',
      label: '5 · Epitácio Pessoa / Ruy Carneiro',
      points: ['epitacio', 'ruy'],
      streets: ['EPITACIOPESSOA', 'RUYCARNEIRO', 'RUICARNEIRO'],
    },
    {
      id: '6',
      label: '6 · Mandacaru / Tancredo Neves',
      points: ['mandacaru', 'ipes'],
      streets: ['MANDACARU', 'TANCREDONEVES'],
    },
    {
      id: '7',
      label: '7 · Via Oeste',
      points: ['via_oeste'],
      streets: ['VIAOESTE'],
    },
    {
      id: '8',
      label: '8 · BR-230 / orbital',
      points: ['br230'],
      streets: ['BR230'],
    },
  ];
  const aliases = {
    lagoa_ida: 'lagoa',
    lagoa_volta: 'lagoa',
    estacao_ida: 'universidade',
    estacao_volta: 'universidade',
  };
  function references(line) {
    return [
      ...(line.points || []),
      ...(line.sentidos || []).flatMap((p) => [
        ...(p.waypoints || []),
        ...(p.station_ids || []),
        ...(p.control_points || []).map((c) => c.station_id).filter(Boolean),
      ]),
    ].filter((value) => typeof value === 'string');
  }
  function describe(line, places = {}) {
    const refs = references(line),
      streets = (line.sentidos || [])
        .flatMap((p) => p.street_sequence || [])
        .map(fold);
    const axes = corridors
      .filter(
        (axis) =>
          axis.points.some((key) =>
            refs.some((ref) => ref === key || ref.startsWith(key + '_')),
          ) ||
          axis.streets.some((name) =>
            streets.some((street) => street.includes(name)),
          ),
      )
      .map((axis) => axis.id);
    const number = /-([0-9]+)$/.exec(line.code || '');
    const family = number ? String(Math.floor(Number(number[1]) / 100)) : null;
    const terminals = [
      ...new Set(
        refs
          .map((ref) => aliases[ref] || ref)
          .filter(
            (key) =>
              places[key] &&
              !places[key].archived &&
              (places[key].kind === 'terminal' || places[key].terminal),
          ),
      ),
    ];
    return { corridors: axes, family, terminals };
  }
  function matches(line, places, filters = {}) {
    const d = describe(line, places);
    return (
      (!filters.corridor ||
        filters.corridor === 'all' ||
        (filters.corridor === 'none'
          ? !d.corridors.length
          : d.corridors.includes(filters.corridor))) &&
      (!filters.family ||
        filters.family === 'all' ||
        (filters.family === 'none'
          ? d.family === null
          : d.family === filters.family)) &&
      (!filters.terminal ||
        filters.terminal === 'all' ||
        (filters.terminal === 'none'
          ? !d.terminals.length
          : d.terminals.includes(filters.terminal)))
    );
  }
  function populate({ corridor, family, terminal }, lines, places) {
    corridor.replaceChildren(
      new Option('Todos os corredores', 'all'),
      ...corridors.map((c) => new Option(c.label, c.id)),
      new Option('Sem corredor identificado', 'none'),
    );
    const families = [
      ...new Set(
        lines
          .map((line) => describe(line, places).family)
          .filter((v) => v !== null),
      ),
    ].sort((a, b) => Number(a) - Number(b));
    family.replaceChildren(
      new Option('Todas as famílias', 'all'),
      ...families.map((f) => new Option(`Família ${f} · ${f}xx`, f)),
      new Option('Sem numeração', 'none'),
    );
    terminal.replaceChildren(
      new Option('Todos os terminais', 'all'),
      ...Object.entries(places)
        .filter(([, p]) => !p.archived && (p.kind === 'terminal' || p.terminal))
        .sort((a, b) => a[1].label.localeCompare(b[1].label, 'pt-BR'))
        .map(([id, p]) => new Option(p.label, id)),
      new Option('Sem terminal vinculado', 'none'),
    );
  }
  window.ProposalFilters = { corridors, describe, matches, populate };
})();
