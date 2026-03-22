"""
Dutch verb conjugation engine.
Handles regular verbs automatically; irregular verbs are specified manually.
"""

def get_stem(infinitive):
    """Get the verb stem from the infinitive."""
    if infinitive.endswith('en'):
        stem = infinitive[:-2]
    elif infinitive.endswith('n'):
        stem = infinitive[:-1]
    else:
        return infinitive

    # Dutch spelling rules: double vowel in open syllable
    # If stem ends in double vowel + consonant pattern, it might need adjustment
    # E.g., 'maken' -> 'maak' (not 'mak')
    # E.g., 'lopen' -> 'loop' (not 'lop')
    # But 'werken' -> 'werk'

    return stem


def apply_spelling_rules(stem, infinitive):
    """
    Apply Dutch spelling rules to get the correct stem.
    In Dutch, long vowels in closed syllables need doubling.
    """
    if len(stem) < 2:
        return stem

    # If the infinitive has a single vowel between consonants (CVC pattern in stem),
    # but the infinitive spelling shows it's a long vowel (open syllable in infinitive),
    # we need to double the vowel in the stem.
    # E.g., 'ma-ken' has open syllable 'ma' -> stem needs 'aa' -> 'maak'
    # E.g., 'lo-pen' has open syllable 'lo' -> stem needs 'oo' -> 'loop'

    vowels = 'aeiou'

    # Check if stem ends with consonant and has single vowel before it
    if len(stem) >= 2 and stem[-1] not in vowels:
        # Find the last vowel cluster
        i = len(stem) - 2
        while i >= 0 and stem[i] not in vowels:
            i -= 1

        if i >= 0 and stem[i] in vowels:
            # Check if it's a single vowel (not already doubled)
            if i == 0 or stem[i-1] not in vowels:
                # Check if in the infinitive this was an open syllable
                # (the vowel is followed by a single consonant then 'en')
                inf_vowel_pos = i
                consonants_after = 0
                for j in range(i+1, len(stem)):
                    if stem[j] not in vowels:
                        consonants_after += 1

                if consonants_after == 1:
                    # This was likely an open syllable in the infinitive
                    # Double the vowel
                    vowel = stem[i]
                    stem = stem[:i] + vowel + stem[i:]

    # Handle 'z' -> 's' and 'v' -> 'f' at end of stem
    if stem.endswith('z'):
        stem = stem[:-1] + 's'
    if stem.endswith('v'):
        stem = stem[:-1] + 'f'

    return stem


def conjugate_regular(infinitive):
    """
    Conjugate a regular Dutch verb.
    Returns conjugation dict with present, past, and perfect.
    """
    raw_stem = get_stem(infinitive)
    stem = apply_spelling_rules(raw_stem, infinitive)

    # Present tense
    present = {
        'ik': stem,
        'jij': stem + 't',
        'u': stem + 't',
        'hij/zij': stem + 't',
        'wij': infinitive,
        'jullie': infinitive,
        'zij_plural': infinitive
    }

    # Fix: if stem already ends in 't', don't add another
    if stem.endswith('t'):
        present['jij'] = stem
        present['u'] = stem
        present['hij/zij'] = stem

    # Past tense: 't kofschip rule
    # If stem ends in t, k, f, s, ch, p -> add 'te/ten'
    # Otherwise -> add 'de/den'
    tkofschip = ('t', 'k', 'f', 's', 'p')

    if stem.endswith('ch') or stem[-1] in tkofschip:
        past_singular = stem + 'te'
        past_plural = stem + 'ten'
    else:
        past_singular = stem + 'de'
        past_plural = stem + 'den'

    past = {
        'ik': past_singular,
        'jij': past_singular,
        'u': past_singular,
        'hij/zij': past_singular,
        'wij': past_plural,
        'jullie': past_plural,
        'zij_plural': past_plural
    }

    # Perfect participle
    # ge + stem + t/d (same t kofschip rule)
    prefix = 'ge'

    # Inseparable prefixes don't get 'ge-'
    inseparable = ('be', 'er', 'ge', 'her', 'ont', 'ver')
    for p in inseparable:
        if infinitive.startswith(p) and len(infinitive) > len(p) + 2:
            prefix = ''
            break

    if stem.endswith('ch') or stem[-1] in tkofschip:
        perfect = prefix + stem + 't'
    else:
        perfect = prefix + stem + 'd'

    # Fix double 'ge' for verbs starting with 'ge'
    if perfect.startswith('gege'):
        perfect = perfect[2:]

    return {
        'present': present,
        'past': past,
        'perfect': perfect
    }


# Irregular verbs - manually specified
IRREGULAR_VERBS = {
    'zijn': {
        'present': {'ik': 'ben', 'jij': 'bent', 'u': 'bent', 'hij/zij': 'is', 'wij': 'zijn', 'jullie': 'zijn', 'zij_plural': 'zijn'},
        'past': {'ik': 'was', 'jij': 'was', 'u': 'was', 'hij/zij': 'was', 'wij': 'waren', 'jullie': 'waren', 'zij_plural': 'waren'},
        'perfect': 'geweest'
    },
    'hebben': {
        'present': {'ik': 'heb', 'jij': 'hebt', 'u': 'hebt', 'hij/zij': 'heeft', 'wij': 'hebben', 'jullie': 'hebben', 'zij_plural': 'hebben'},
        'past': {'ik': 'had', 'jij': 'had', 'u': 'had', 'hij/zij': 'had', 'wij': 'hadden', 'jullie': 'hadden', 'zij_plural': 'hadden'},
        'perfect': 'gehad'
    },
    'worden': {
        'present': {'ik': 'word', 'jij': 'wordt', 'u': 'wordt', 'hij/zij': 'wordt', 'wij': 'worden', 'jullie': 'worden', 'zij_plural': 'worden'},
        'past': {'ik': 'werd', 'jij': 'werd', 'u': 'werd', 'hij/zij': 'werd', 'wij': 'werden', 'jullie': 'werden', 'zij_plural': 'werden'},
        'perfect': 'geworden'
    },
    'kunnen': {
        'present': {'ik': 'kan', 'jij': 'kunt', 'u': 'kunt', 'hij/zij': 'kan', 'wij': 'kunnen', 'jullie': 'kunnen', 'zij_plural': 'kunnen'},
        'past': {'ik': 'kon', 'jij': 'kon', 'u': 'kon', 'hij/zij': 'kon', 'wij': 'konden', 'jullie': 'konden', 'zij_plural': 'konden'},
        'perfect': 'gekund'
    },
    'zullen': {
        'present': {'ik': 'zal', 'jij': 'zult', 'u': 'zult', 'hij/zij': 'zal', 'wij': 'zullen', 'jullie': 'zullen', 'zij_plural': 'zullen'},
        'past': {'ik': 'zou', 'jij': 'zou', 'u': 'zou', 'hij/zij': 'zou', 'wij': 'zouden', 'jullie': 'zouden', 'zij_plural': 'zouden'},
        'perfect': ''
    },
    'moeten': {
        'present': {'ik': 'moet', 'jij': 'moet', 'u': 'moet', 'hij/zij': 'moet', 'wij': 'moeten', 'jullie': 'moeten', 'zij_plural': 'moeten'},
        'past': {'ik': 'moest', 'jij': 'moest', 'u': 'moest', 'hij/zij': 'moest', 'wij': 'moesten', 'jullie': 'moesten', 'zij_plural': 'moesten'},
        'perfect': 'gemoeten'
    },
    'mogen': {
        'present': {'ik': 'mag', 'jij': 'mag', 'u': 'mag', 'hij/zij': 'mag', 'wij': 'mogen', 'jullie': 'mogen', 'zij_plural': 'mogen'},
        'past': {'ik': 'mocht', 'jij': 'mocht', 'u': 'mocht', 'hij/zij': 'mocht', 'wij': 'mochten', 'jullie': 'mochten', 'zij_plural': 'mochten'},
        'perfect': 'gemoogd'
    },
    'willen': {
        'present': {'ik': 'wil', 'jij': 'wilt', 'u': 'wilt', 'hij/zij': 'wil', 'wij': 'willen', 'jullie': 'willen', 'zij_plural': 'willen'},
        'past': {'ik': 'wilde', 'jij': 'wilde', 'u': 'wilde', 'hij/zij': 'wilde', 'wij': 'wilden', 'jullie': 'wilden', 'zij_plural': 'wilden'},
        'perfect': 'gewild'
    },
    'doen': {
        'present': {'ik': 'doe', 'jij': 'doet', 'u': 'doet', 'hij/zij': 'doet', 'wij': 'doen', 'jullie': 'doen', 'zij_plural': 'doen'},
        'past': {'ik': 'deed', 'jij': 'deed', 'u': 'deed', 'hij/zij': 'deed', 'wij': 'deden', 'jullie': 'deden', 'zij_plural': 'deden'},
        'perfect': 'gedaan'
    },
    'gaan': {
        'present': {'ik': 'ga', 'jij': 'gaat', 'u': 'gaat', 'hij/zij': 'gaat', 'wij': 'gaan', 'jullie': 'gaan', 'zij_plural': 'gaan'},
        'past': {'ik': 'ging', 'jij': 'ging', 'u': 'ging', 'hij/zij': 'ging', 'wij': 'gingen', 'jullie': 'gingen', 'zij_plural': 'gingen'},
        'perfect': 'gegaan'
    },
    'komen': {
        'present': {'ik': 'kom', 'jij': 'komt', 'u': 'komt', 'hij/zij': 'komt', 'wij': 'komen', 'jullie': 'komen', 'zij_plural': 'komen'},
        'past': {'ik': 'kwam', 'jij': 'kwam', 'u': 'kwam', 'hij/zij': 'kwam', 'wij': 'kwamen', 'jullie': 'kwamen', 'zij_plural': 'kwamen'},
        'perfect': 'gekomen'
    },
    'zien': {
        'present': {'ik': 'zie', 'jij': 'ziet', 'u': 'ziet', 'hij/zij': 'ziet', 'wij': 'zien', 'jullie': 'zien', 'zij_plural': 'zien'},
        'past': {'ik': 'zag', 'jij': 'zag', 'u': 'zag', 'hij/zij': 'zag', 'wij': 'zagen', 'jullie': 'zagen', 'zij_plural': 'zagen'},
        'perfect': 'gezien'
    },
    'staan': {
        'present': {'ik': 'sta', 'jij': 'staat', 'u': 'staat', 'hij/zij': 'staat', 'wij': 'staan', 'jullie': 'staan', 'zij_plural': 'staan'},
        'past': {'ik': 'stond', 'jij': 'stond', 'u': 'stond', 'hij/zij': 'stond', 'wij': 'stonden', 'jullie': 'stonden', 'zij_plural': 'stonden'},
        'perfect': 'gestaan'
    },
    'geven': {
        'present': {'ik': 'geef', 'jij': 'geeft', 'u': 'geeft', 'hij/zij': 'geeft', 'wij': 'geven', 'jullie': 'geven', 'zij_plural': 'geven'},
        'past': {'ik': 'gaf', 'jij': 'gaf', 'u': 'gaf', 'hij/zij': 'gaf', 'wij': 'gaven', 'jullie': 'gaven', 'zij_plural': 'gaven'},
        'perfect': 'gegeven'
    },
    'nemen': {
        'present': {'ik': 'neem', 'jij': 'neemt', 'u': 'neemt', 'hij/zij': 'neemt', 'wij': 'nemen', 'jullie': 'nemen', 'zij_plural': 'nemen'},
        'past': {'ik': 'nam', 'jij': 'nam', 'u': 'nam', 'hij/zij': 'nam', 'wij': 'namen', 'jullie': 'namen', 'zij_plural': 'namen'},
        'perfect': 'genomen'
    },
    'vinden': {
        'present': {'ik': 'vind', 'jij': 'vindt', 'u': 'vindt', 'hij/zij': 'vindt', 'wij': 'vinden', 'jullie': 'vinden', 'zij_plural': 'vinden'},
        'past': {'ik': 'vond', 'jij': 'vond', 'u': 'vond', 'hij/zij': 'vond', 'wij': 'vonden', 'jullie': 'vonden', 'zij_plural': 'vonden'},
        'perfect': 'gevonden'
    },
    'zeggen': {
        'present': {'ik': 'zeg', 'jij': 'zegt', 'u': 'zegt', 'hij/zij': 'zegt', 'wij': 'zeggen', 'jullie': 'zeggen', 'zij_plural': 'zeggen'},
        'past': {'ik': 'zei', 'jij': 'zei', 'u': 'zei', 'hij/zij': 'zei', 'wij': 'zeiden', 'jullie': 'zeiden', 'zij_plural': 'zeiden'},
        'perfect': 'gezegd'
    },
    'denken': {
        'present': {'ik': 'denk', 'jij': 'denkt', 'u': 'denkt', 'hij/zij': 'denkt', 'wij': 'denken', 'jullie': 'denken', 'zij_plural': 'denken'},
        'past': {'ik': 'dacht', 'jij': 'dacht', 'u': 'dacht', 'hij/zij': 'dacht', 'wij': 'dachten', 'jullie': 'dachten', 'zij_plural': 'dachten'},
        'perfect': 'gedacht'
    },
    'weten': {
        'present': {'ik': 'weet', 'jij': 'weet', 'u': 'weet', 'hij/zij': 'weet', 'wij': 'weten', 'jullie': 'weten', 'zij_plural': 'weten'},
        'past': {'ik': 'wist', 'jij': 'wist', 'u': 'wist', 'hij/zij': 'wist', 'wij': 'wisten', 'jullie': 'wisten', 'zij_plural': 'wisten'},
        'perfect': 'geweten'
    },
    'maken': {
        'present': {'ik': 'maak', 'jij': 'maakt', 'u': 'maakt', 'hij/zij': 'maakt', 'wij': 'maken', 'jullie': 'maken', 'zij_plural': 'maken'},
        'past': {'ik': 'maakte', 'jij': 'maakte', 'u': 'maakte', 'hij/zij': 'maakte', 'wij': 'maakten', 'jullie': 'maakten', 'zij_plural': 'maakten'},
        'perfect': 'gemaakt'
    },
    'schrijven': {
        'present': {'ik': 'schrijf', 'jij': 'schrijft', 'u': 'schrijft', 'hij/zij': 'schrijft', 'wij': 'schrijven', 'jullie': 'schrijven', 'zij_plural': 'schrijven'},
        'past': {'ik': 'schreef', 'jij': 'schreef', 'u': 'schreef', 'hij/zij': 'schreef', 'wij': 'schreven', 'jullie': 'schreven', 'zij_plural': 'schreven'},
        'perfect': 'geschreven'
    },
    'lezen': {
        'present': {'ik': 'lees', 'jij': 'leest', 'u': 'leest', 'hij/zij': 'leest', 'wij': 'lezen', 'jullie': 'lezen', 'zij_plural': 'lezen'},
        'past': {'ik': 'las', 'jij': 'las', 'u': 'las', 'hij/zij': 'las', 'wij': 'lazen', 'jullie': 'lazen', 'zij_plural': 'lazen'},
        'perfect': 'gelezen'
    },
    'spreken': {
        'present': {'ik': 'spreek', 'jij': 'spreekt', 'u': 'spreekt', 'hij/zij': 'spreekt', 'wij': 'spreken', 'jullie': 'spreken', 'zij_plural': 'spreken'},
        'past': {'ik': 'sprak', 'jij': 'sprak', 'u': 'sprak', 'hij/zij': 'sprak', 'wij': 'spraken', 'jullie': 'spraken', 'zij_plural': 'spraken'},
        'perfect': 'gesproken'
    },
    'lopen': {
        'present': {'ik': 'loop', 'jij': 'loopt', 'u': 'loopt', 'hij/zij': 'loopt', 'wij': 'lopen', 'jullie': 'lopen', 'zij_plural': 'lopen'},
        'past': {'ik': 'liep', 'jij': 'liep', 'u': 'liep', 'hij/zij': 'liep', 'wij': 'liepen', 'jullie': 'liepen', 'zij_plural': 'liepen'},
        'perfect': 'gelopen'
    },
    'zitten': {
        'present': {'ik': 'zit', 'jij': 'zit', 'u': 'zit', 'hij/zij': 'zit', 'wij': 'zitten', 'jullie': 'zitten', 'zij_plural': 'zitten'},
        'past': {'ik': 'zat', 'jij': 'zat', 'u': 'zat', 'hij/zij': 'zat', 'wij': 'zaten', 'jullie': 'zaten', 'zij_plural': 'zaten'},
        'perfect': 'gezeten'
    },
    'liggen': {
        'present': {'ik': 'lig', 'jij': 'ligt', 'u': 'ligt', 'hij/zij': 'ligt', 'wij': 'liggen', 'jullie': 'liggen', 'zij_plural': 'liggen'},
        'past': {'ik': 'lag', 'jij': 'lag', 'u': 'lag', 'hij/zij': 'lag', 'wij': 'lagen', 'jullie': 'lagen', 'zij_plural': 'lagen'},
        'perfect': 'gelegen'
    },
    'houden': {
        'present': {'ik': 'houd', 'jij': 'houdt', 'u': 'houdt', 'hij/zij': 'houdt', 'wij': 'houden', 'jullie': 'houden', 'zij_plural': 'houden'},
        'past': {'ik': 'hield', 'jij': 'hield', 'u': 'hield', 'hij/zij': 'hield', 'wij': 'hielden', 'jullie': 'hielden', 'zij_plural': 'hielden'},
        'perfect': 'gehouden'
    },
    'brengen': {
        'present': {'ik': 'breng', 'jij': 'brengt', 'u': 'brengt', 'hij/zij': 'brengt', 'wij': 'brengen', 'jullie': 'brengen', 'zij_plural': 'brengen'},
        'past': {'ik': 'bracht', 'jij': 'bracht', 'u': 'bracht', 'hij/zij': 'bracht', 'wij': 'brachten', 'jullie': 'brachten', 'zij_plural': 'brachten'},
        'perfect': 'gebracht'
    },
    'kopen': {
        'present': {'ik': 'koop', 'jij': 'koopt', 'u': 'koopt', 'hij/zij': 'koopt', 'wij': 'kopen', 'jullie': 'kopen', 'zij_plural': 'kopen'},
        'past': {'ik': 'kocht', 'jij': 'kocht', 'u': 'kocht', 'hij/zij': 'kocht', 'wij': 'kochten', 'jullie': 'kochten', 'zij_plural': 'kochten'},
        'perfect': 'gekocht'
    },
    'eten': {
        'present': {'ik': 'eet', 'jij': 'eet', 'u': 'eet', 'hij/zij': 'eet', 'wij': 'eten', 'jullie': 'eten', 'zij_plural': 'eten'},
        'past': {'ik': 'at', 'jij': 'at', 'u': 'at', 'hij/zij': 'at', 'wij': 'aten', 'jullie': 'aten', 'zij_plural': 'aten'},
        'perfect': 'gegeten'
    },
    'drinken': {
        'present': {'ik': 'drink', 'jij': 'drinkt', 'u': 'drinkt', 'hij/zij': 'drinkt', 'wij': 'drinken', 'jullie': 'drinken', 'zij_plural': 'drinken'},
        'past': {'ik': 'dronk', 'jij': 'dronk', 'u': 'dronk', 'hij/zij': 'dronk', 'wij': 'dronken', 'jullie': 'dronken', 'zij_plural': 'dronken'},
        'perfect': 'gedronken'
    },
    'slapen': {
        'present': {'ik': 'slaap', 'jij': 'slaapt', 'u': 'slaapt', 'hij/zij': 'slaapt', 'wij': 'slapen', 'jullie': 'slapen', 'zij_plural': 'slapen'},
        'past': {'ik': 'sliep', 'jij': 'sliep', 'u': 'sliep', 'hij/zij': 'sliep', 'wij': 'sliepen', 'jullie': 'sliepen', 'zij_plural': 'sliepen'},
        'perfect': 'geslapen'
    },
    'rijden': {
        'present': {'ik': 'rijd', 'jij': 'rijdt', 'u': 'rijdt', 'hij/zij': 'rijdt', 'wij': 'rijden', 'jullie': 'rijden', 'zij_plural': 'rijden'},
        'past': {'ik': 'reed', 'jij': 'reed', 'u': 'reed', 'hij/zij': 'reed', 'wij': 'reden', 'jullie': 'reden', 'zij_plural': 'reden'},
        'perfect': 'gereden'
    },
    'vallen': {
        'present': {'ik': 'val', 'jij': 'valt', 'u': 'valt', 'hij/zij': 'valt', 'wij': 'vallen', 'jullie': 'vallen', 'zij_plural': 'vallen'},
        'past': {'ik': 'viel', 'jij': 'viel', 'u': 'viel', 'hij/zij': 'viel', 'wij': 'vielen', 'jullie': 'vielen', 'zij_plural': 'vielen'},
        'perfect': 'gevallen'
    },
    'trekken': {
        'present': {'ik': 'trek', 'jij': 'trekt', 'u': 'trekt', 'hij/zij': 'trekt', 'wij': 'trekken', 'jullie': 'trekken', 'zij_plural': 'trekken'},
        'past': {'ik': 'trok', 'jij': 'trok', 'u': 'trok', 'hij/zij': 'trok', 'wij': 'trokken', 'jullie': 'trokken', 'zij_plural': 'trokken'},
        'perfect': 'getrokken'
    },
    'sterven': {
        'present': {'ik': 'sterf', 'jij': 'sterft', 'u': 'sterft', 'hij/zij': 'sterft', 'wij': 'sterven', 'jullie': 'sterven', 'zij_plural': 'sterven'},
        'past': {'ik': 'stierf', 'jij': 'stierf', 'u': 'stierf', 'hij/zij': 'stierf', 'wij': 'stierven', 'jullie': 'stierven', 'zij_plural': 'stierven'},
        'perfect': 'gestorven'
    },
    'helpen': {
        'present': {'ik': 'help', 'jij': 'helpt', 'u': 'helpt', 'hij/zij': 'helpt', 'wij': 'helpen', 'jullie': 'helpen', 'zij_plural': 'helpen'},
        'past': {'ik': 'hielp', 'jij': 'hielp', 'u': 'hielp', 'hij/zij': 'hielp', 'wij': 'hielpen', 'jullie': 'hielpen', 'zij_plural': 'hielpen'},
        'perfect': 'geholpen'
    },
    'laten': {
        'present': {'ik': 'laat', 'jij': 'laat', 'u': 'laat', 'hij/zij': 'laat', 'wij': 'laten', 'jullie': 'laten', 'zij_plural': 'laten'},
        'past': {'ik': 'liet', 'jij': 'liet', 'u': 'liet', 'hij/zij': 'liet', 'wij': 'lieten', 'jullie': 'lieten', 'zij_plural': 'lieten'},
        'perfect': 'gelaten'
    },
    'roepen': {
        'present': {'ik': 'roep', 'jij': 'roept', 'u': 'roept', 'hij/zij': 'roept', 'wij': 'roepen', 'jullie': 'roepen', 'zij_plural': 'roepen'},
        'past': {'ik': 'riep', 'jij': 'riep', 'u': 'riep', 'hij/zij': 'riep', 'wij': 'riepen', 'jullie': 'riepen', 'zij_plural': 'riepen'},
        'perfect': 'geroepen'
    },
    'wijzen': {
        'present': {'ik': 'wijs', 'jij': 'wijst', 'u': 'wijst', 'hij/zij': 'wijst', 'wij': 'wijzen', 'jullie': 'wijzen', 'zij_plural': 'wijzen'},
        'past': {'ik': 'wees', 'jij': 'wees', 'u': 'wees', 'hij/zij': 'wees', 'wij': 'wezen', 'jullie': 'wezen', 'zij_plural': 'wezen'},
        'perfect': 'gewezen'
    },
    'slaan': {
        'present': {'ik': 'sla', 'jij': 'slaat', 'u': 'slaat', 'hij/zij': 'slaat', 'wij': 'slaan', 'jullie': 'slaan', 'zij_plural': 'slaan'},
        'past': {'ik': 'sloeg', 'jij': 'sloeg', 'u': 'sloeg', 'hij/zij': 'sloeg', 'wij': 'sloegen', 'jullie': 'sloegen', 'zij_plural': 'sloegen'},
        'perfect': 'geslagen'
    },
    'dragen': {
        'present': {'ik': 'draag', 'jij': 'draagt', 'u': 'draagt', 'hij/zij': 'draagt', 'wij': 'dragen', 'jullie': 'dragen', 'zij_plural': 'dragen'},
        'past': {'ik': 'droeg', 'jij': 'droeg', 'u': 'droeg', 'hij/zij': 'droeg', 'wij': 'droegen', 'jullie': 'droegen', 'zij_plural': 'droegen'},
        'perfect': 'gedragen'
    },
    'groeien': {
        'present': {'ik': 'groei', 'jij': 'groeit', 'u': 'groeit', 'hij/zij': 'groeit', 'wij': 'groeien', 'jullie': 'groeien', 'zij_plural': 'groeien'},
        'past': {'ik': 'groeide', 'jij': 'groeide', 'u': 'groeide', 'hij/zij': 'groeide', 'wij': 'groeiden', 'jullie': 'groeiden', 'zij_plural': 'groeiden'},
        'perfect': 'gegroeid'
    },
    'wassen': {
        'present': {'ik': 'was', 'jij': 'wast', 'u': 'wast', 'hij/zij': 'wast', 'wij': 'wassen', 'jullie': 'wassen', 'zij_plural': 'wassen'},
        'past': {'ik': 'waste', 'jij': 'waste', 'u': 'waste', 'hij/zij': 'waste', 'wij': 'wasten', 'jullie': 'wasten', 'zij_plural': 'wasten'},
        'perfect': 'gewassen'
    },
    'winnen': {
        'present': {'ik': 'win', 'jij': 'wint', 'u': 'wint', 'hij/zij': 'wint', 'wij': 'winnen', 'jullie': 'winnen', 'zij_plural': 'winnen'},
        'past': {'ik': 'won', 'jij': 'won', 'u': 'won', 'hij/zij': 'won', 'wij': 'wonnen', 'jullie': 'wonnen', 'zij_plural': 'wonnen'},
        'perfect': 'gewonnen'
    },
    'breken': {
        'present': {'ik': 'breek', 'jij': 'breekt', 'u': 'breekt', 'hij/zij': 'breekt', 'wij': 'breken', 'jullie': 'breken', 'zij_plural': 'breken'},
        'past': {'ik': 'brak', 'jij': 'brak', 'u': 'brak', 'hij/zij': 'brak', 'wij': 'braken', 'jullie': 'braken', 'zij_plural': 'braken'},
        'perfect': 'gebroken'
    },
    'kiezen': {
        'present': {'ik': 'kies', 'jij': 'kiest', 'u': 'kiest', 'hij/zij': 'kiest', 'wij': 'kiezen', 'jullie': 'kiezen', 'zij_plural': 'kiezen'},
        'past': {'ik': 'koos', 'jij': 'koos', 'u': 'koos', 'hij/zij': 'koos', 'wij': 'kozen', 'jullie': 'kozen', 'zij_plural': 'kozen'},
        'perfect': 'gekozen'
    },
    'sluiten': {
        'present': {'ik': 'sluit', 'jij': 'sluit', 'u': 'sluit', 'hij/zij': 'sluit', 'wij': 'sluiten', 'jullie': 'sluiten', 'zij_plural': 'sluiten'},
        'past': {'ik': 'sloot', 'jij': 'sloot', 'u': 'sloot', 'hij/zij': 'sloot', 'wij': 'sloten', 'jullie': 'sloten', 'zij_plural': 'sloten'},
        'perfect': 'gesloten'
    },
    'bijten': {
        'present': {'ik': 'bijt', 'jij': 'bijt', 'u': 'bijt', 'hij/zij': 'bijt', 'wij': 'bijten', 'jullie': 'bijten', 'zij_plural': 'bijten'},
        'past': {'ik': 'beet', 'jij': 'beet', 'u': 'beet', 'hij/zij': 'beet', 'wij': 'beten', 'jullie': 'beten', 'zij_plural': 'beten'},
        'perfect': 'gebeten'
    },
    'bewegen': {
        'present': {'ik': 'beweeg', 'jij': 'beweegt', 'u': 'beweegt', 'hij/zij': 'beweegt', 'wij': 'bewegen', 'jullie': 'bewegen', 'zij_plural': 'bewegen'},
        'past': {'ik': 'bewoog', 'jij': 'bewoog', 'u': 'bewoog', 'hij/zij': 'bewoog', 'wij': 'bewogen', 'jullie': 'bewogen', 'zij_plural': 'bewogen'},
        'perfect': 'bewogen'
    },
    'kijken': {
        'present': {'ik': 'kijk', 'jij': 'kijkt', 'u': 'kijkt', 'hij/zij': 'kijkt', 'wij': 'kijken', 'jullie': 'kijken', 'zij_plural': 'kijken'},
        'past': {'ik': 'keek', 'jij': 'keek', 'u': 'keek', 'hij/zij': 'keek', 'wij': 'keken', 'jullie': 'keken', 'zij_plural': 'keken'},
        'perfect': 'gekeken'
    },
    'beginnen': {
        'present': {'ik': 'begin', 'jij': 'begint', 'u': 'begint', 'hij/zij': 'begint', 'wij': 'beginnen', 'jullie': 'beginnen', 'zij_plural': 'beginnen'},
        'past': {'ik': 'begon', 'jij': 'begon', 'u': 'begon', 'hij/zij': 'begon', 'wij': 'begonnen', 'jullie': 'begonnen', 'zij_plural': 'begonnen'},
        'perfect': 'begonnen'
    },
    'vergeten': {
        'present': {'ik': 'vergeet', 'jij': 'vergeet', 'u': 'vergeet', 'hij/zij': 'vergeet', 'wij': 'vergeten', 'jullie': 'vergeten', 'zij_plural': 'vergeten'},
        'past': {'ik': 'vergat', 'jij': 'vergat', 'u': 'vergat', 'hij/zij': 'vergat', 'wij': 'vergaten', 'jullie': 'vergaten', 'zij_plural': 'vergaten'},
        'perfect': 'vergeten'
    },
    'hangen': {
        'present': {'ik': 'hang', 'jij': 'hangt', 'u': 'hangt', 'hij/zij': 'hangt', 'wij': 'hangen', 'jullie': 'hangen', 'zij_plural': 'hangen'},
        'past': {'ik': 'hing', 'jij': 'hing', 'u': 'hing', 'hij/zij': 'hing', 'wij': 'hingen', 'jullie': 'hingen', 'zij_plural': 'hingen'},
        'perfect': 'gehangen'
    },
    'vliegen': {
        'present': {'ik': 'vlieg', 'jij': 'vliegt', 'u': 'vliegt', 'hij/zij': 'vliegt', 'wij': 'vliegen', 'jullie': 'vliegen', 'zij_plural': 'vliegen'},
        'past': {'ik': 'vloog', 'jij': 'vloog', 'u': 'vloog', 'hij/zij': 'vloog', 'wij': 'vlogen', 'jullie': 'vlogen', 'zij_plural': 'vlogen'},
        'perfect': 'gevlogen'
    },
    'zwemmen': {
        'present': {'ik': 'zwem', 'jij': 'zwemt', 'u': 'zwemt', 'hij/zij': 'zwemt', 'wij': 'zwemmen', 'jullie': 'zwemmen', 'zij_plural': 'zwemmen'},
        'past': {'ik': 'zwom', 'jij': 'zwom', 'u': 'zwom', 'hij/zij': 'zwom', 'wij': 'zwommen', 'jullie': 'zwommen', 'zij_plural': 'zwommen'},
        'perfect': 'gezwommen'
    },
    'steken': {
        'present': {'ik': 'steek', 'jij': 'steekt', 'u': 'steekt', 'hij/zij': 'steekt', 'wij': 'steken', 'jullie': 'steken', 'zij_plural': 'steken'},
        'past': {'ik': 'stak', 'jij': 'stak', 'u': 'stak', 'hij/zij': 'stak', 'wij': 'staken', 'jullie': 'staken', 'zij_plural': 'staken'},
        'perfect': 'gestoken'
    },
    'graven': {
        'present': {'ik': 'graaf', 'jij': 'graaft', 'u': 'graaft', 'hij/zij': 'graaft', 'wij': 'graven', 'jullie': 'graven', 'zij_plural': 'graven'},
        'past': {'ik': 'groef', 'jij': 'groef', 'u': 'groef', 'hij/zij': 'groef', 'wij': 'groeven', 'jullie': 'groeven', 'zij_plural': 'groeven'},
        'perfect': 'gegraven'
    },
    'scheppen': {
        'present': {'ik': 'schep', 'jij': 'schept', 'u': 'schept', 'hij/zij': 'schept', 'wij': 'scheppen', 'jullie': 'scheppen', 'zij_plural': 'scheppen'},
        'past': {'ik': 'schiep', 'jij': 'schiep', 'u': 'schiep', 'hij/zij': 'schiep', 'wij': 'schiepen', 'jullie': 'schiepen', 'zij_plural': 'schiepen'},
        'perfect': 'geschapen'
    },
    'zoeken': {
        'present': {'ik': 'zoek', 'jij': 'zoekt', 'u': 'zoekt', 'hij/zij': 'zoekt', 'wij': 'zoeken', 'jullie': 'zoeken', 'zij_plural': 'zoeken'},
        'past': {'ik': 'zocht', 'jij': 'zocht', 'u': 'zocht', 'hij/zij': 'zocht', 'wij': 'zochten', 'jullie': 'zochten', 'zij_plural': 'zochten'},
        'perfect': 'gezocht'
    },
    'bieden': {
        'present': {'ik': 'bied', 'jij': 'biedt', 'u': 'biedt', 'hij/zij': 'biedt', 'wij': 'bieden', 'jullie': 'bieden', 'zij_plural': 'bieden'},
        'past': {'ik': 'bood', 'jij': 'bood', 'u': 'bood', 'hij/zij': 'bood', 'wij': 'boden', 'jullie': 'boden', 'zij_plural': 'boden'},
        'perfect': 'geboden'
    },
    'buigen': {
        'present': {'ik': 'buig', 'jij': 'buigt', 'u': 'buigt', 'hij/zij': 'buigt', 'wij': 'buigen', 'jullie': 'buigen', 'zij_plural': 'buigen'},
        'past': {'ik': 'boog', 'jij': 'boog', 'u': 'boog', 'hij/zij': 'boog', 'wij': 'bogen', 'jullie': 'bogen', 'zij_plural': 'bogen'},
        'perfect': 'gebogen'
    },
    'gieten': {
        'present': {'ik': 'giet', 'jij': 'giet', 'u': 'giet', 'hij/zij': 'giet', 'wij': 'gieten', 'jullie': 'gieten', 'zij_plural': 'gieten'},
        'past': {'ik': 'goot', 'jij': 'goot', 'u': 'goot', 'hij/zij': 'goot', 'wij': 'goten', 'jullie': 'goten', 'zij_plural': 'goten'},
        'perfect': 'gegoten'
    },
    'schieten': {
        'present': {'ik': 'schiet', 'jij': 'schiet', 'u': 'schiet', 'hij/zij': 'schiet', 'wij': 'schieten', 'jullie': 'schieten', 'zij_plural': 'schieten'},
        'past': {'ik': 'schoot', 'jij': 'schoot', 'u': 'schoot', 'hij/zij': 'schoot', 'wij': 'schoten', 'jullie': 'schoten', 'zij_plural': 'schoten'},
        'perfect': 'geschoten'
    },
    'verbieden': {
        'present': {'ik': 'verbied', 'jij': 'verbiedt', 'u': 'verbiedt', 'hij/zij': 'verbiedt', 'wij': 'verbieden', 'jullie': 'verbieden', 'zij_plural': 'verbieden'},
        'past': {'ik': 'verbood', 'jij': 'verbood', 'u': 'verbood', 'hij/zij': 'verbood', 'wij': 'verboden', 'jullie': 'verboden', 'zij_plural': 'verboden'},
        'perfect': 'verboden'
    },
    'drijven': {
        'present': {'ik': 'drijf', 'jij': 'drijft', 'u': 'drijft', 'hij/zij': 'drijft', 'wij': 'drijven', 'jullie': 'drijven', 'zij_plural': 'drijven'},
        'past': {'ik': 'dreef', 'jij': 'dreef', 'u': 'dreef', 'hij/zij': 'dreef', 'wij': 'dreven', 'jullie': 'dreven', 'zij_plural': 'dreven'},
        'perfect': 'gedreven'
    },
    'grijpen': {
        'present': {'ik': 'grijp', 'jij': 'grijpt', 'u': 'grijpt', 'hij/zij': 'grijpt', 'wij': 'grijpen', 'jullie': 'grijpen', 'zij_plural': 'grijpen'},
        'past': {'ik': 'greep', 'jij': 'greep', 'u': 'greep', 'hij/zij': 'greep', 'wij': 'grepen', 'jullie': 'grepen', 'zij_plural': 'grepen'},
        'perfect': 'gegrepen'
    },
    'krijgen': {
        'present': {'ik': 'krijg', 'jij': 'krijgt', 'u': 'krijgt', 'hij/zij': 'krijgt', 'wij': 'krijgen', 'jullie': 'krijgen', 'zij_plural': 'krijgen'},
        'past': {'ik': 'kreeg', 'jij': 'kreeg', 'u': 'kreeg', 'hij/zij': 'kreeg', 'wij': 'kregen', 'jullie': 'kregen', 'zij_plural': 'kregen'},
        'perfect': 'gekregen'
    },
    'blijven': {
        'present': {'ik': 'blijf', 'jij': 'blijft', 'u': 'blijft', 'hij/zij': 'blijft', 'wij': 'blijven', 'jullie': 'blijven', 'zij_plural': 'blijven'},
        'past': {'ik': 'bleef', 'jij': 'bleef', 'u': 'bleef', 'hij/zij': 'bleef', 'wij': 'bleven', 'jullie': 'bleven', 'zij_plural': 'bleven'},
        'perfect': 'gebleven'
    },
    'verdwijnen': {
        'present': {'ik': 'verdwijn', 'jij': 'verdwijnt', 'u': 'verdwijnt', 'hij/zij': 'verdwijnt', 'wij': 'verdwijnen', 'jullie': 'verdwijnen', 'zij_plural': 'verdwijnen'},
        'past': {'ik': 'verdween', 'jij': 'verdween', 'u': 'verdween', 'hij/zij': 'verdween', 'wij': 'verdwenen', 'jullie': 'verdwenen', 'zij_plural': 'verdwenen'},
        'perfect': 'verdwenen'
    },
    'verschijnen': {
        'present': {'ik': 'verschijn', 'jij': 'verschijnt', 'u': 'verschijnt', 'hij/zij': 'verschijnt', 'wij': 'verschijnen', 'jullie': 'verschijnen', 'zij_plural': 'verschijnen'},
        'past': {'ik': 'verscheen', 'jij': 'verscheen', 'u': 'verscheen', 'hij/zij': 'verscheen', 'wij': 'verschenen', 'jullie': 'verschenen', 'zij_plural': 'verschenen'},
        'perfect': 'verschenen'
    },
    'sterven': {
        'present': {'ik': 'sterf', 'jij': 'sterft', 'u': 'sterft', 'hij/zij': 'sterft', 'wij': 'sterven', 'jullie': 'sterven', 'zij_plural': 'sterven'},
        'past': {'ik': 'stierf', 'jij': 'stierf', 'u': 'stierf', 'hij/zij': 'stierf', 'wij': 'stierven', 'jullie': 'stierven', 'zij_plural': 'stierven'},
        'perfect': 'gestorven'
    },
    'werpen': {
        'present': {'ik': 'werp', 'jij': 'werpt', 'u': 'werpt', 'hij/zij': 'werpt', 'wij': 'werpen', 'jullie': 'werpen', 'zij_plural': 'werpen'},
        'past': {'ik': 'wierp', 'jij': 'wierp', 'u': 'wierp', 'hij/zij': 'wierp', 'wij': 'wierpen', 'jullie': 'wierpen', 'zij_plural': 'wierpen'},
        'perfect': 'geworpen'
    },
    'zingen': {
        'present': {'ik': 'zing', 'jij': 'zingt', 'u': 'zingt', 'hij/zij': 'zingt', 'wij': 'zingen', 'jullie': 'zingen', 'zij_plural': 'zingen'},
        'past': {'ik': 'zong', 'jij': 'zong', 'u': 'zong', 'hij/zij': 'zong', 'wij': 'zongen', 'jullie': 'zongen', 'zij_plural': 'zongen'},
        'perfect': 'gezongen'
    },
    'springen': {
        'present': {'ik': 'spring', 'jij': 'springt', 'u': 'springt', 'hij/zij': 'springt', 'wij': 'springen', 'jullie': 'springen', 'zij_plural': 'springen'},
        'past': {'ik': 'sprong', 'jij': 'sprong', 'u': 'sprong', 'hij/zij': 'sprong', 'wij': 'sprongen', 'jullie': 'sprongen', 'zij_plural': 'sprongen'},
        'perfect': 'gesprongen'
    },
    'dwingen': {
        'present': {'ik': 'dwing', 'jij': 'dwingt', 'u': 'dwingt', 'hij/zij': 'dwingt', 'wij': 'dwingen', 'jullie': 'dwingen', 'zij_plural': 'dwingen'},
        'past': {'ik': 'dwong', 'jij': 'dwong', 'u': 'dwong', 'hij/zij': 'dwong', 'wij': 'dwongen', 'jullie': 'dwongen', 'zij_plural': 'dwongen'},
        'perfect': 'gedwongen'
    },
    'dringen': {
        'present': {'ik': 'dring', 'jij': 'dringt', 'u': 'dringt', 'hij/zij': 'dringt', 'wij': 'dringen', 'jullie': 'dringen', 'zij_plural': 'dringen'},
        'past': {'ik': 'drong', 'jij': 'drong', 'u': 'drong', 'hij/zij': 'drong', 'wij': 'drongen', 'jullie': 'drongen', 'zij_plural': 'drongen'},
        'perfect': 'gedrongen'
    },
    'binden': {
        'present': {'ik': 'bind', 'jij': 'bindt', 'u': 'bindt', 'hij/zij': 'bindt', 'wij': 'binden', 'jullie': 'binden', 'zij_plural': 'binden'},
        'past': {'ik': 'bond', 'jij': 'bond', 'u': 'bond', 'hij/zij': 'bond', 'wij': 'bonden', 'jullie': 'bonden', 'zij_plural': 'bonden'},
        'perfect': 'gebonden'
    },
    'schrappen': {
        'present': {'ik': 'schrap', 'jij': 'schrapt', 'u': 'schrapt', 'hij/zij': 'schrapt', 'wij': 'schrappen', 'jullie': 'schrappen', 'zij_plural': 'schrappen'},
        'past': {'ik': 'schrapte', 'jij': 'schrapte', 'u': 'schrapte', 'hij/zij': 'schrapte', 'wij': 'schrapten', 'jullie': 'schrapten', 'zij_plural': 'schrapten'},
        'perfect': 'geschrapt'
    },
    'blazen': {
        'present': {'ik': 'blaas', 'jij': 'blaast', 'u': 'blaast', 'hij/zij': 'blaast', 'wij': 'blazen', 'jullie': 'blazen', 'zij_plural': 'blazen'},
        'past': {'ik': 'blies', 'jij': 'blies', 'u': 'blies', 'hij/zij': 'blies', 'wij': 'bliezen', 'jullie': 'bliezen', 'zij_plural': 'bliezen'},
        'perfect': 'geblazen'
    },
    'wegen': {
        'present': {'ik': 'weeg', 'jij': 'weegt', 'u': 'weegt', 'hij/zij': 'weegt', 'wij': 'wegen', 'jullie': 'wegen', 'zij_plural': 'wegen'},
        'past': {'ik': 'woog', 'jij': 'woog', 'u': 'woog', 'hij/zij': 'woog', 'wij': 'wogen', 'jullie': 'wogen', 'zij_plural': 'wogen'},
        'perfect': 'gewogen'
    },
    'bedriegen': {
        'present': {'ik': 'bedrieg', 'jij': 'bedriegt', 'u': 'bedriegt', 'hij/zij': 'bedriegt', 'wij': 'bedriegen', 'jullie': 'bedriegen', 'zij_plural': 'bedriegen'},
        'past': {'ik': 'bedroog', 'jij': 'bedroog', 'u': 'bedroog', 'hij/zij': 'bedroog', 'wij': 'bedrogen', 'jullie': 'bedrogen', 'zij_plural': 'bedrogen'},
        'perfect': 'bedrogen'
    },
    'genezen': {
        'present': {'ik': 'genees', 'jij': 'geneest', 'u': 'geneest', 'hij/zij': 'geneest', 'wij': 'genezen', 'jullie': 'genezen', 'zij_plural': 'genezen'},
        'past': {'ik': 'genas', 'jij': 'genas', 'u': 'genas', 'hij/zij': 'genas', 'wij': 'genazen', 'jullie': 'genazen', 'zij_plural': 'genazen'},
        'perfect': 'genezen'
    },
    'bevelen': {
        'present': {'ik': 'beveel', 'jij': 'beveelt', 'u': 'beveelt', 'hij/zij': 'beveelt', 'wij': 'bevelen', 'jullie': 'bevelen', 'zij_plural': 'bevelen'},
        'past': {'ik': 'beval', 'jij': 'beval', 'u': 'beval', 'hij/zij': 'beval', 'wij': 'bevalen', 'jullie': 'bevalen', 'zij_plural': 'bevalen'},
        'perfect': 'bevolen'
    },
    'stelen': {
        'present': {'ik': 'steel', 'jij': 'steelt', 'u': 'steelt', 'hij/zij': 'steelt', 'wij': 'stelen', 'jullie': 'stelen', 'zij_plural': 'stelen'},
        'past': {'ik': 'stal', 'jij': 'stal', 'u': 'stal', 'hij/zij': 'stal', 'wij': 'stalen', 'jullie': 'stalen', 'zij_plural': 'stalen'},
        'perfect': 'gestolen'
    },
    'zweren': {
        'present': {'ik': 'zweer', 'jij': 'zweert', 'u': 'zweert', 'hij/zij': 'zweert', 'wij': 'zweren', 'jullie': 'zweren', 'zij_plural': 'zweren'},
        'past': {'ik': 'zwoer', 'jij': 'zwoer', 'u': 'zwoer', 'hij/zij': 'zwoer', 'wij': 'zwoeren', 'jullie': 'zwoeren', 'zij_plural': 'zwoeren'},
        'perfect': 'gezworen'
    },
    'treffen': {
        'present': {'ik': 'tref', 'jij': 'treft', 'u': 'treft', 'hij/zij': 'treft', 'wij': 'treffen', 'jullie': 'treffen', 'zij_plural': 'treffen'},
        'past': {'ik': 'trof', 'jij': 'trof', 'u': 'trof', 'hij/zij': 'trof', 'wij': 'troffen', 'jullie': 'troffen', 'zij_plural': 'troffen'},
        'perfect': 'getroffen'
    },
    'schenken': {
        'present': {'ik': 'schenk', 'jij': 'schenkt', 'u': 'schenkt', 'hij/zij': 'schenkt', 'wij': 'schenken', 'jullie': 'schenken', 'zij_plural': 'schenken'},
        'past': {'ik': 'schonk', 'jij': 'schonk', 'u': 'schonk', 'hij/zij': 'schonk', 'wij': 'schonken', 'jullie': 'schonken', 'zij_plural': 'schonken'},
        'perfect': 'geschonken'
    },
    'klimmen': {
        'present': {'ik': 'klim', 'jij': 'klimt', 'u': 'klimt', 'hij/zij': 'klimt', 'wij': 'klimmen', 'jullie': 'klimmen', 'zij_plural': 'klimmen'},
        'past': {'ik': 'klom', 'jij': 'klom', 'u': 'klom', 'hij/zij': 'klom', 'wij': 'klommen', 'jullie': 'klommen', 'zij_plural': 'klommen'},
        'perfect': 'geklommen'
    },
    'draagen': {
        'present': {'ik': 'draag', 'jij': 'draagt', 'u': 'draagt', 'hij/zij': 'draagt', 'wij': 'dragen', 'jullie': 'dragen', 'zij_plural': 'dragen'},
        'past': {'ik': 'droeg', 'jij': 'droeg', 'u': 'droeg', 'hij/zij': 'droeg', 'wij': 'droegen', 'jullie': 'droegen', 'zij_plural': 'droegen'},
        'perfect': 'gedragen'
    },
    'meten': {
        'present': {'ik': 'meet', 'jij': 'meet', 'u': 'meet', 'hij/zij': 'meet', 'wij': 'meten', 'jullie': 'meten', 'zij_plural': 'meten'},
        'past': {'ik': 'mat', 'jij': 'mat', 'u': 'mat', 'hij/zij': 'mat', 'wij': 'maten', 'jullie': 'maten', 'zij_plural': 'maten'},
        'perfect': 'gemeten'
    },
    'draalen': {
        'present': {'ik': 'draai', 'jij': 'draait', 'u': 'draait', 'hij/zij': 'draait', 'wij': 'draaien', 'jullie': 'draaien', 'zij_plural': 'draaien'},
        'past': {'ik': 'draaide', 'jij': 'draaide', 'u': 'draaide', 'hij/zij': 'draaide', 'wij': 'draaiden', 'jullie': 'draaiden', 'zij_plural': 'draaiden'},
        'perfect': 'gedraaid'
    },
    'draaien': {
        'present': {'ik': 'draai', 'jij': 'draait', 'u': 'draait', 'hij/zij': 'draait', 'wij': 'draaien', 'jullie': 'draaien', 'zij_plural': 'draaien'},
        'past': {'ik': 'draaide', 'jij': 'draaide', 'u': 'draaide', 'hij/zij': 'draaide', 'wij': 'draaiden', 'jullie': 'draaiden', 'zij_plural': 'draaiden'},
        'perfect': 'gedraaid'
    },
    'wrijven': {
        'present': {'ik': 'wrijf', 'jij': 'wrijft', 'u': 'wrijft', 'hij/zij': 'wrijft', 'wij': 'wrijven', 'jullie': 'wrijven', 'zij_plural': 'wrijven'},
        'past': {'ik': 'wreef', 'jij': 'wreef', 'u': 'wreef', 'hij/zij': 'wreef', 'wij': 'wreven', 'jullie': 'wreven', 'zij_plural': 'wreven'},
        'perfect': 'gewreven'
    },
    'snijden': {
        'present': {'ik': 'snijd', 'jij': 'snijdt', 'u': 'snijdt', 'hij/zij': 'snijdt', 'wij': 'snijden', 'jullie': 'snijden', 'zij_plural': 'snijden'},
        'past': {'ik': 'sneed', 'jij': 'sneed', 'u': 'sneed', 'hij/zij': 'sneed', 'wij': 'sneden', 'jullie': 'sneden', 'zij_plural': 'sneden'},
        'perfect': 'gesneden'
    },
    'lijden': {
        'present': {'ik': 'lijd', 'jij': 'lijdt', 'u': 'lijdt', 'hij/zij': 'lijdt', 'wij': 'lijden', 'jullie': 'lijden', 'zij_plural': 'lijden'},
        'past': {'ik': 'leed', 'jij': 'leed', 'u': 'leed', 'hij/zij': 'leed', 'wij': 'leden', 'jullie': 'leden', 'zij_plural': 'leden'},
        'perfect': 'geleden'
    },
    'genoten': {
        'present': {'ik': 'geniet', 'jij': 'geniet', 'u': 'geniet', 'hij/zij': 'geniet', 'wij': 'genieten', 'jullie': 'genieten', 'zij_plural': 'genieten'},
        'past': {'ik': 'genoot', 'jij': 'genoot', 'u': 'genoot', 'hij/zij': 'genoot', 'wij': 'genoten', 'jullie': 'genoten', 'zij_plural': 'genoten'},
        'perfect': 'genoten'
    },
    'genieten': {
        'present': {'ik': 'geniet', 'jij': 'geniet', 'u': 'geniet', 'hij/zij': 'geniet', 'wij': 'genieten', 'jullie': 'genieten', 'zij_plural': 'genieten'},
        'past': {'ik': 'genoot', 'jij': 'genoot', 'u': 'genoot', 'hij/zij': 'genoot', 'wij': 'genoten', 'jullie': 'genoten', 'zij_plural': 'genoten'},
        'perfect': 'genoten'
    },
    'smelten': {
        'present': {'ik': 'smelt', 'jij': 'smelt', 'u': 'smelt', 'hij/zij': 'smelt', 'wij': 'smelten', 'jullie': 'smelten', 'zij_plural': 'smelten'},
        'past': {'ik': 'smolt', 'jij': 'smolt', 'u': 'smolt', 'hij/zij': 'smolt', 'wij': 'smolten', 'jullie': 'smolten', 'zij_plural': 'smolten'},
        'perfect': 'gesmolten'
    },
    'schelden': {
        'present': {'ik': 'scheld', 'jij': 'scheldt', 'u': 'scheldt', 'hij/zij': 'scheldt', 'wij': 'schelden', 'jullie': 'schelden', 'zij_plural': 'schelden'},
        'past': {'ik': 'schold', 'jij': 'schold', 'u': 'schold', 'hij/zij': 'schold', 'wij': 'scholden', 'jullie': 'scholden', 'zij_plural': 'scholden'},
        'perfect': 'gescholden'
    },
    'zenden': {
        'present': {'ik': 'zend', 'jij': 'zendt', 'u': 'zendt', 'hij/zij': 'zendt', 'wij': 'zenden', 'jullie': 'zenden', 'zij_plural': 'zenden'},
        'past': {'ik': 'zond', 'jij': 'zond', 'u': 'zond', 'hij/zij': 'zond', 'wij': 'zonden', 'jullie': 'zonden', 'zij_plural': 'zonden'},
        'perfect': 'gezonden'
    },
    'braden': {
        'present': {'ik': 'braad', 'jij': 'braadt', 'u': 'braadt', 'hij/zij': 'braadt', 'wij': 'braden', 'jullie': 'braden', 'zij_plural': 'braden'},
        'past': {'ik': 'braadde', 'jij': 'braadde', 'u': 'braadde', 'hij/zij': 'braadde', 'wij': 'braadden', 'jullie': 'braadden', 'zij_plural': 'braadden'},
        'perfect': 'gebraden'
    },
    'laden': {
        'present': {'ik': 'laad', 'jij': 'laadt', 'u': 'laadt', 'hij/zij': 'laadt', 'wij': 'laden', 'jullie': 'laden', 'zij_plural': 'laden'},
        'past': {'ik': 'laadde', 'jij': 'laadde', 'u': 'laadde', 'hij/zij': 'laadde', 'wij': 'laadden', 'jullie': 'laadden', 'zij_plural': 'laadden'},
        'perfect': 'geladen'
    },
}


def conjugate(infinitive):
    """Get conjugation for a verb - irregular if known, otherwise regular."""
    if infinitive in IRREGULAR_VERBS:
        return IRREGULAR_VERBS[infinitive]
    return conjugate_regular(infinitive)
