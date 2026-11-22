"""Regras territoriais da revisão; referências são corredores, não paradas aprovadas."""
import unicodedata

def fold(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text.upper()) if not unicodedata.combining(c))

# Ponto do mercado fornecido pelo usuário. O terreno adjacente não tem planta de acesso.
OITIZEIRO_MARKET = [-34.893325, -7.163894]
LAGOA_PLATFORM = [-34.8796961, -7.1184807]  # OSM 3962688662, plataforma 4 / SEMOB
CRISTO_TERMINAL = [-34.87198, -7.16650]  # extremidades coincidentes das atuais 204 e 208


ROAD_HINTS = {k: 'JOSÉ AMÉRICO DE ALMEIDA' for k in ['beira', 'beira_back', 'beira_oeste', 'beira_oeste_back']}


def configure(network, waypoints):
    from collections import defaultdict
    streets = defaultdict(set)
    for (node, _), edge in network.edges.items():
        streets[fold(edge['name'])].add(node)
    network.corridor_nodes = streets

    def street(key, name, near):
        candidates = {node for title, nodes in streets.items() if fold(name) in title for node in nodes}
        if not candidates:
            raise ValueError(f'Corredor não encontrado: {name}')
        point = min((network.positions[n] for n in candidates), key=lambda p: ((p[0]-near[0])**2+(p[1]-near[1])**2))
        waypoints[key] = point
        ROAD_HINTS[key] = name

    references = [
        ('beira_meio', 'JOSÉ AMÉRICO DE ALMEIDA', [-34.840, -7.126]),
        ('beira_altiplano', 'JOSÉ AMÉRICO DE ALMEIDA', [-34.835, -7.126]),
        ('bessa_afonso', 'AFONSO PENA', [-34.8415, -7.0655]),
        ('bessa_afonso_sul', 'AFONSO PENA', [-34.835, -7.0712]),
        ('praia_interior_sape', 'SAPÉ', [-34.838, -7.103]),
        ('praia_interior_brandao', 'FRANCISCO BRANDÃO', [-34.840, -7.104]),
        ('praia_interior_morais', 'MANOEL MORAIS', [-34.835, -7.110]),
        ('colibris_leste', 'DOS COLIBRIS', [-34.8490, -7.1663]),
        ('colibris_dentro', 'FERNANDO TORRES', [-34.8500, -7.1680]),
        ('colibris_central', 'DOS COLIBRIS', [-34.8501, -7.1657]),
        ('colibris_fernando', 'FERNANDO TORRES', [-34.8511, -7.1667]),
        ('ja_paulo', 'PAULO GOMES DE ALMEIDA', [-34.861, -7.173]),
        ('ja_climaco', 'CLIMACO', [-34.8607, -7.1748]),
        ('ja_aristoteles', 'ARISTOTELES', [-34.8557, -7.1785]),
        ('ja_aristoteles_sul', 'ARISTOTELES', [-34.8555, -7.1800]),
        ('ja_otavio', 'OTÁVIO FÉLIX', [-34.856, -7.176]),
        ('ifpb', 'PRIMEIRO DE MAIO', [-34.8727, -7.1348]),
        ('fraternidade', 'FRATERNIDADE', [-34.883, -7.154]),
        ('heronides', 'HERONIDES', [-34.872, -7.155]),
        ('carlos_luz', 'CARLOS LUZ', [-34.871, -7.159]),
        ('ranieri', 'RANIERI', [-34.8664, -7.1664]),
        ('rangel_norte', '14 DE JULHO', [-34.872, -7.141]),
    ]
    for key, name, near in references:
        street(key, name, near)
    waypoints.update(oitizeiro=[-34.8932842, -7.1649318], oitizeiro_back=[-34.8932842, -7.1649318], cristo=CRISTO_TERMINAL)
    for key in ['br230_shopping_sul', 'br230_norte']:
        candidates = {n for (n, _), e in network.edges.items() if 'BR-230' in e.get('ref', '') and e['highway'] in {'trunk', 'motorway'}}
        waypoints[key] = min((network.positions[n] for n in candidates), key=lambda p: (p[0]-waypoints[key][0])**2+(p[1]-waypoints[key][1])**2)


def route_keys(code, direction, keys):
    if code in {'BRS-500', 'T-610', 'TRV-321'}:
        keys = keys[:1] + ['bessa_afonso', 'bessa_afonso_sul'] + keys[1:] if keys[0] == 'bessa' else keys[:-1] + ['bessa_afonso_sul', 'bessa_afonso', keys[-1]]
    if code == 'BRS-501':
        outward = ['bessa', 'bessa_afonso', 'bessa_afonso_sul', 'aeroc', 'praia_interior_sape', 'praia_interior_brandao', 'praia_interior_morais', 'ruy', 'metro']
        return outward if direction == 'ida' else ['metro', 'ruy_back', 'praia_interior_morais', 'praia_interior_brandao', 'praia_interior_sape', 'aeroc', 'bessa_afonso_sul', 'bessa_afonso', 'bessa']
    if code == 'BRS-800':
        return (['aeroporto', 'oitizeiro', 'cristo', 'estacao_ida', 'br230_shopping_sul', 'shopping', 'br230_norte', 'bessa'] if direction == 'ida' else
                ['bessa', 'shopping', 'br230_shopping_sul', 'estacao_volta', 'cristo', 'oitizeiro_back', 'aeroporto'])
    if code == 'T-410':
        outward = ['hub', 'mariz', 'portal_arterial', 'altiplano_arterial', 'beira_altiplano', 'beira_meio', 'beira', 'beira_oeste', 'metro']
        return outward if direction == 'ida' else ['metro', 'beira_oeste_back', 'beira_back', 'beira_meio', 'beira_altiplano', 'altiplano_arterial', 'portal_arterial', 'mariz', 'hub']
    if code == 'T-610':
        return [k for k in keys if not k.startswith('br230') and k != 'retao_oeste']
    if code == 'TRV-321':
        return [({'leocadio': 'aeroc', 'leocadio_back': 'aeroc'}.get(k, k)) for k in keys]
    if code == 'TRV-721':
        return [k for k in keys if k not in {'perimetral_leste', 'perimetral_leste_back'}]
    if code == 'I-332':
        return [k for k in keys if k not in {'clodoaldo', 'severina', 'balbina', 'joao_maria', 'parque'}]
    if code in {'R-241', 'R-242'}:
        outward = ['cristo', 'ranieri', 'ja_paulo', 'ja_climaco', 'ja_aristoteles', 'ja_aristoteles_sul', 'ja_otavio', 'jose_estevao', 'geni', 'colibris_dentro', 'colibris_fernando', 'colibris_central', 'colibris_leste', 'jardim_sp', 'agua_fria', 'cristo']
        return outward if code == 'R-241' else outward[::-1]
    if code == 'L-251':
        return ['cristo', 'vale_sul', 'vale_palmeiras', 'vale_murilo', 'fraternidade', 'heronides', 'rangel', 'rangel_norte', 'ifpb', 'rangel_norte', 'rangel_back', 'carlos_luz', 'ranieri', 'cristo']
    if code == 'L-751':
        return ['val', 'parque', 'joao_maria', 'balbina', 'severina', 'clodoaldo'] + keys[1:]
    return keys


NOTES = {
    'BRS-501': 'Eixo interior de Manaíra por Sapé, Francisco Brandão e Manoel Morais, distinguindo-se da BRS-500.',
    'BRS-800': 'Após Cidade Universitária, ligação pela BR-230, sem incursão no Castelo Branco.',
    'T-410': 'Corredor da Beira-Rio contínuo até o Altiplano; sem UFPB ou Epitácio Pessoa.',
    'T-610': 'Ligação urbana por Bessa, Shopping, Ipês, Mandacaru e Roger; sem BR-230.',
    'TRV-321': 'Manaíra Shopping com retorno ao eixo próximo à praia / Jardim Oceania e Bessa; sem BR-230.',
    'TRV-721': 'Perimetral Sul e BR-101, sem desvio pelo interior do Planalto da Boa Esperança.',
    'I-332': 'Muçumagro ligado diretamente ao terminal Valentina; atendimento interno do Parque do Sol transferido à L-751.',
    'R-241': 'José Américo com referências da atual 107; entrada e saída pela área central do Colibris.',
    'R-242': 'Circuito complementar pela área central do Colibris e ruas do José Américo usadas pela atual 107.',
    'L-251': 'Cobertura ampliada de Cristo, Vale das Palmeiras, Rangel e IFPB/Jaguaribe, tomando as atuais 204, 208 e 203 como referência. A antiga 201 não está disponível nas bases locais.',
    'L-751': 'Assume o atendimento interno do Parque do Sol e mantém Muçumagro, Barra de Gramame e Praia do Sol.',
    'M-961': 'Traçados originais do estudo restaurados integralmente nos dois sentidos.',
}


def forbidden(code, edge, midpoint):
    name, ref = edge['name'].upper(), edge.get('ref', '')
    highway = 'BR-230' in ref or 'BR-230' in name or 'BR 230' in name
    if code in {'T-610', 'TRV-321'} and highway:
        return True
    if code == 'T-410' and -34.869 < midpoint[0] < -34.835 and -7.131 < midpoint[1] < -7.122 and 'JOSÉ AMÉRICO DE ALMEIDA' not in name and edge.get('highway') not in {'primary_link', 'secondary_link'}:
        return True
    if code == 'T-410' and ('EPITÁCIO' in name or 'PADRE ZÉ' in name or 'UFPB' in name or highway):
        return True
    if code == 'BRS-800' and not highway and edge.get('highway') in {'residential', 'living_street', 'service'} and -34.850 < midpoint[0] < -34.835 and -7.138 < midpoint[1] < -7.122:
        return True  # interior de Castelo Branco, a leste da BR-230
    if code == 'TRV-721' and -34.872 < midpoint[0] < -34.852 and -7.204 < midpoint[1] < -7.193:
        return edge.get('highway') in {'residential', 'living_street', 'service'}
    return False

ITINERARIES = {
    'BRS-501': 'T. Bessa → Jardim Oceania → Manaíra interior (Sapé / Francisco Brandão / Manoel Morais) → Ruy Carneiro → Terminal de Passageiros da Lagoa → TIV Varadouro',
    'BRS-800': 'Aeroporto → T. Oitizeiro (novo mercado) → Terminal Cristo atual → Estação Cidade Universitária → BR-230 → Manaíra Shopping → T. Bessa',
    'T-410': 'T. Mangabeira → Portal do Sol → Altiplano → Beira-Rio → Terminal de Passageiros da Lagoa → TIV Varadouro',
    'T-610': 'T. Bessa → Manaíra Shopping → Tancredo Neves / Ipês → Mandacaru → Padre Zé → Roger → Terminal de Passageiros da Lagoa → TIV Varadouro',
    'TRV-321': 'T. Mangabeira → Portal do Sol → Altiplano → Cabo Branco → Tambaú → Manaíra → Manaíra Shopping → Jardim Oceania próximo à praia → T. Bessa',
    'I-332': 'T. Mangabeira → Garrafão → Trauminha → Francisco Porfírio Ribeiro → Paratibe → Félix Cahino → Humberto Maul → Jacarandá → Muçumagro → NTI Valentina',
    'R-241': 'Terminal Cristo atual → José Américo (ruas da atual 107) → Fernando Torres / centro do Colibris → Jardim São Paulo → Água Fria → Terminal Cristo',
    'R-242': 'Terminal Cristo atual → Água Fria → Jardim São Paulo → centro do Colibris / Fernando Torres → José Américo (ruas da atual 107) → Terminal Cristo',
    'L-251': 'Terminal Cristo atual → Vale das Palmeiras → Fraternidade → Rangel → IFPB / Primeiro de Maio (Jaguaribe) → Rangel → Presidente Carlos Luz → Ranieri Mazilli → Terminal Cristo',
    'L-751': 'NTI Valentina → Parque do Sol (atendimento interno) → Oliveiras / Maria Ana Nunes / Cedros → Muçumagro → Barra de Gramame → Praia do Sol → NTI Valentina',
}

NAMES = {
    'I-332': 'Valentina via Paratibe e Muçumagro',
    'L-251': 'Cristo–Rangel–IFPB / Vale das Palmeiras',
    'L-751': 'Valentina–Parque do Sol–Barra de Gramame / Praia do Sol',
}
