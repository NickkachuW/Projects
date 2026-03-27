"""Check all verbs for incorrect conjugations against known strong verb list."""
import sys, json
sys.path.insert(0, '.')
from conjugator import IRREGULAR_VERBS, is_separable, split_separable, INSEPARABLE_PREFIXES

# Comprehensive Dutch strong/irregular verbs: word -> (past_ik, perfect)
STRONG = {
    'bijten': ('beet', 'gebeten'), 'blijken': ('bleek', 'gebleken'),
    'blijven': ('bleef', 'gebleven'), 'drijven': ('dreef', 'gedreven'),
    'glijden': ('gleed', 'gegleden'), 'grijpen': ('greep', 'gegrepen'),
    'hijsen': ('hees', 'gehesen'), 'kijken': ('keek', 'gekeken'),
    'krijgen': ('kreeg', 'gekregen'), 'lijden': ('leed', 'geleden'),
    'lijken': ('leek', 'geleken'), 'mijden': ('meed', 'gemeden'),
    'prijzen': ('prees', 'geprezen'), 'rijden': ('reed', 'gereden'),
    'rijzen': ('rees', 'gerezen'), 'scheiden': ('scheidde', 'gescheiden'),
    'schrijven': ('schreef', 'geschreven'), 'snijden': ('sneed', 'gesneden'),
    'spijten': ('speet', 'gespeten'), 'stijgen': ('steeg', 'gestegen'),
    'strijden': ('streed', 'gestreden'), 'strijken': ('streek', 'gestreken'),
    'wijken': ('week', 'geweken'), 'wijzen': ('wees', 'gewezen'),
    'wrijven': ('wreef', 'gewreven'), 'zwijgen': ('zweeg', 'gezwegen'),
    # ie -> oo
    'bedriegen': ('bedroog', 'bedrogen'), 'bieden': ('bood', 'geboden'),
    'gieten': ('goot', 'gegoten'), 'kiezen': ('koos', 'gekozen'),
    'liegen': ('loog', 'gelogen'), 'schieten': ('schoot', 'geschoten'),
    'verbieden': ('verbood', 'verboden'), 'verliezen': ('verloor', 'verloren'),
    'vliegen': ('vloog', 'gevlogen'), 'vriezen': ('vroor', 'gevroren'),
    'genieten': ('genoot', 'genoten'),
    # ui -> oo
    'buigen': ('boog', 'gebogen'), 'duiken': ('dook', 'gedoken'),
    'fluiten': ('floot', 'gefloten'), 'kruipen': ('kroop', 'gekropen'),
    'ruiken': ('rook', 'geroken'), 'schuiven': ('schoof', 'geschoven'),
    'sluiten': ('sloot', 'gesloten'), 'spuiten': ('spoot', 'gespoten'),
    'zuigen': ('zoog', 'gezogen'),
    # i -> o
    'binden': ('bond', 'gebonden'), 'blinken': ('blonk', 'geblonken'),
    'drinken': ('dronk', 'gedronken'), 'dringen': ('drong', 'gedrongen'),
    'dwingen': ('dwong', 'gedwongen'), 'klimmen': ('klom', 'geklommen'),
    'klinken': ('klonk', 'geklonken'), 'krimpen': ('kromp', 'gekrompen'),
    'schelden': ('schold', 'gescholden'), 'schrikken': ('schrok', 'geschrokken'),
    'smelten': ('smolt', 'gesmolten'), 'spinnen': ('spon', 'gesponnen'),
    'springen': ('sprong', 'gesprongen'), 'stinken': ('stonk', 'gestonken'),
    'treffen': ('trof', 'getroffen'), 'trekken': ('trok', 'getrokken'),
    'vinden': ('vond', 'gevonden'), 'winnen': ('won', 'gewonnen'),
    'wringen': ('wrong', 'gewrongen'), 'zenden': ('zond', 'gezonden'),
    'zinken': ('zonk', 'gezonken'), 'zwellen': ('zwol', 'gezwollen'),
    'zwemmen': ('zwom', 'gezwommen'), 'zingen': ('zong', 'gezongen'),
    # e -> a -> o
    'bergen': ('borg', 'geborgen'), 'breken': ('brak', 'gebroken'),
    'delven': ('dolf', 'gedolven'), 'gelden': ('gold', 'gegolden'),
    'helpen': ('hielp', 'geholpen'), 'nemen': ('nam', 'genomen'),
    'scheppen': ('schiep', 'geschapen'), 'schenken': ('schonk', 'geschonken'),
    'spreken': ('sprak', 'gesproken'), 'steken': ('stak', 'gestoken'),
    'sterven': ('stierf', 'gestorven'), 'werpen': ('wierp', 'geworpen'),
    'zwerven': ('zwierf', 'gezworven'), 'verwerven': ('verwierf', 'verworven'),
    # a -> oe
    'dragen': ('droeg', 'gedragen'), 'graven': ('groef', 'gegraven'),
    'slaan': ('sloeg', 'geslagen'), 'varen': ('voer', 'gevaren'),
    # ee -> a -> e
    'eten': ('at', 'gegeten'), 'genezen': ('genas', 'genezen'),
    'geven': ('gaf', 'gegeven'), 'lezen': ('las', 'gelezen'),
    'meten': ('mat', 'gemeten'), 'treden': ('trad', 'getreden'),
    'vergeten': ('vergat', 'vergeten'),
    # oo -> ie
    'lopen': ('liep', 'gelopen'), 'roepen': ('riep', 'geroepen'),
    # aa
    'blazen': ('blies', 'geblazen'), 'houden': ('hield', 'gehouden'),
    'laten': ('liet', 'gelaten'), 'raden': ('ried', 'geraden'),
    'slapen': ('sliep', 'geslapen'), 'vallen': ('viel', 'gevallen'),
    # special
    'bakken': ('bakte', 'gebakken'), 'barsten': ('barstte', 'gebarsten'),
    'bidden': ('bad', 'gebeden'), 'braden': ('braadde', 'gebraden'),
    'brengen': ('bracht', 'gebracht'), 'denken': ('dacht', 'gedacht'),
    'doen': ('deed', 'gedaan'), 'gaan': ('ging', 'gegaan'),
    'hangen': ('hing', 'gehangen'), 'hebben': ('had', 'gehad'),
    'heffen': ('hief', 'geheven'), 'komen': ('kwam', 'gekomen'),
    'kopen': ('kocht', 'gekocht'), 'laden': ('laadde', 'geladen'),
    'lachen': ('lachte', 'gelachen'), 'scheiden': ('scheidde', 'gescheiden'),
    'schudden': ('schudde', 'geschud'), 'staan': ('stond', 'gestaan'),
    'vouwen': ('vouwde', 'gevouwen'), 'vragen': ('vroeg', 'gevraagd'),
    'wegen': ('woog', 'gewogen'), 'weten': ('wist', 'geweten'),
    'zeggen': ('zei', 'gezegd'), 'zijn': ('was', 'geweest'),
    'zitten': ('zat', 'gezeten'), 'zoeken': ('zocht', 'gezocht'),
    'vangen': ('ving', 'gevangen'), 'wassen': ('waste', 'gewassen'),
    # inseparable prefix
    'beginnen': ('begon', 'begonnen'), 'begrijpen': ('begreep', 'begrepen'),
    'behouden': ('behield', 'behouden'), 'beschrijven': ('beschreef', 'beschreven'),
    'besluiten': ('besloot', 'besloten'), 'bespreken': ('besprak', 'besproken'),
    'bestrijden': ('bestreed', 'bestreden'), 'betreden': ('betrad', 'betreden'),
    'bevallen': ('beviel', 'bevallen'), 'bevelen': ('beval', 'bevolen'),
    'bevinden': ('bevond', 'bevonden'), 'bevriezen': ('bevroor', 'bevroren'),
    'bewegen': ('bewoog', 'bewogen'), 'bewijzen': ('bewees', 'bewezen'),
    'bezoeken': ('bezocht', 'bezocht'), 'bedwingen': ('bedwong', 'bedwongen'),
    'bederven': ('bedierf', 'bedorven'), 'bedrijven': ('bedreef', 'bedreven'),
    'geschieden': ('geschiedde', 'geschied'),
    'onthouden': ('onthield', 'onthouden'), 'ontvangen': ('ontving', 'ontvangen'),
    'ontbreken': ('ontbrak', 'ontbroken'),
    'onderscheiden': ('onderscheidde', 'onderscheiden'),
    'ondervinden': ('ondervond', 'ondervonden'),
    'verbinden': ('verbond', 'verbonden'), 'verdwijnen': ('verdween', 'verdwenen'),
    'vergelijken': ('vergeleek', 'vergeleken'), 'vergeten': ('vergat', 'vergeten'),
    'verliezen': ('verloor', 'verloren'), 'vernemen': ('vernam', 'vernomen'),
    'verschijnen': ('verscheen', 'verschenen'), 'verstaan': ('verstond', 'verstaan'),
    'vermijden': ('vermeed', 'vermeden'), 'verbieden': ('verbood', 'verboden'),
    'overwegen': ('overwoog', 'overwogen'), 'overwinnen': ('overwon', 'overwonnen'),
    'overleven': ('overleefde', 'overleefd'),
    'overlijden': ('overleed', 'overleden'),
    'ondernemen': ('ondernam', 'ondernomen'),
    'betrappen': ('betrapte', 'betrapt'),
    'erkennen': ('erkende', 'erkend'),
    'herkennen': ('herkende', 'herkend'),
}

with open('../data/verbs.json', 'r', encoding='utf-8') as f:
    verbs = json.load(f)

wrong = []
for v in verbs:
    word = v['word']
    conj = v['conjugations']
    act_past = conj.get('past', {}).get('ik', '')
    act_perfect = conj.get('perfect', '')

    # Direct match
    if word in STRONG:
        exp_past, exp_perfect = STRONG[word]
        if act_past != exp_past or act_perfect != exp_perfect:
            wrong.append((word, act_past, exp_past, act_perfect, exp_perfect))
        continue

    # Separable verb with strong base
    if is_separable(word):
        prefix, base = split_separable(word)
        if base in STRONG:
            exp_past_base, exp_perfect_base = STRONG[base]
            exp_past = exp_past_base + ' ' + prefix
            # Perfect: depends on whether base has ge- or inseparable prefix
            if exp_perfect_base.startswith('ge'):
                exp_perfect = prefix + exp_perfect_base
            elif any(base.startswith(p) for p in INSEPARABLE_PREFIXES if len(base) > len(p) + 2):
                exp_perfect = prefix + exp_perfect_base
            else:
                exp_perfect = prefix + 'ge' + exp_perfect_base
            if act_past != exp_past or act_perfect != exp_perfect:
                wrong.append((word, act_past, exp_past, act_perfect, exp_perfect))

print(f"Verbs with incorrect conjugation: {len(wrong)}")
for w, ap, ep, aperf, eperf in sorted(wrong):
    issues = []
    if ap != ep: issues.append(f"past: {ap} -> {ep}")
    if aperf != eperf: issues.append(f"perf: {aperf} -> {eperf}")
    print(f"  {w}: {' | '.join(issues)}")
