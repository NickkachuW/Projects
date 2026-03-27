"""
Dutch verb conjugation engine.
Handles regular verbs automatically; irregular verbs are specified manually.
Supports scheidbare werkwoorden (separable verbs).
"""

# Separable prefixes in Dutch, ordered longest-first to avoid false matches
SEPARABLE_PREFIXES = [
    'terug', 'samen', 'tegen', 'tussen',
    'achter', 'binnen', 'boven', 'buiten', 'onder', 'over', 'voort', 'voorbij',
    'aan', 'af', 'bij', 'door', 'in', 'mee', 'na', 'neer', 'om', 'op', 'over',
    'toe', 'uit', 'vast', 'voor', 'weg',
]

# Inseparable prefixes — these NEVER split
INSEPARABLE_PREFIXES = ('be', 'er', 'ge', 'her', 'ont', 'ver')

# Some prefixes can be BOTH separable and inseparable depending on the verb
# e.g. "overleggen" (inseparable: to consult) vs "overlopen" (separable: to overflow)
# We handle known ambiguous cases with a manual override list
FORCE_INSEPARABLE = {
    'overleggen', 'ondergaan', 'ondernemen', 'ondervinden', 'onderzoeken',
    'onderscheiden', 'ondersteunen', 'onderbreken', 'onderhouden', 'onderdrukken',
    'ondervragen', 'ondertekenen', 'onderschatten', 'onderverdelen',
    'doorgronden', 'doorstaan', 'doorkruisen',
    'omhelzen', 'omringen', 'omschrijven', 'omvatten',
    'voorkomen', 'voorzien', 'voorspellen', 'voorkomen',
    'overtuigen', 'overwegen', 'overleven', 'overwinnen', 'overschrijden',
    'overtreden', 'overtreffen', 'overheersen',
    'achtervolgen', 'achterhalen',
}

FORCE_SEPARABLE = {
    'aankomen', 'aanbieden', 'aanbrengen', 'aandoen', 'aandringen', 'aangaan',
    'aangeven', 'aanhouden', 'aankijken', 'aanleggen', 'aannemen', 'aanpassen',
    'aanraken', 'aansluiten', 'aanspreken', 'aantasten', 'aantonen', 'aanwijzen',
    'aanzetten', 'afbreken', 'afdoen', 'afgaan', 'afhangen', 'afkomen', 'afleggen',
    'afleiden', 'aflopen', 'afmaken', 'afnemen', 'afschaffen', 'afsluiten',
    'afspelen', 'afspreken', 'afwijken', 'afwijzen', 'afzetten',
    'bijdragen', 'bijhouden', 'bijstaan', 'bijkomen',
    'doorbreken', 'doorbrengen', 'doorgaan', 'doorlopen', 'doormaken', 'doorvoeren',
    'doorwerken', 'doorzetten',
    'ingaan', 'ingrijpen', 'inrichten', 'instellen', 'invoeren', 'inzien',
    'inzetten', 'inleiden', 'innemen', 'inschrijven', 'inspelen', 'instappen',
    'meebrengen', 'meedelen', 'meekomen', 'meemaken', 'meenemen', 'meewerken',
    'meevallen',
    'nagaan', 'nakijken', 'nalaten', 'nastreven',
    'neerkomen', 'neerleggen', 'neerzetten',
    'omgaan', 'omkomen', 'omzetten', 'omdraaien',
    'opgaan', 'opgeven', 'opkomen', 'opletten', 'opleveren', 'oplopen',
    'opmerken', 'opnemen', 'oprichten', 'oproepen', 'opruimen', 'opslaan',
    'opstaan', 'opstellen', 'optreden', 'opvallen', 'opvatten', 'opvoeden',
    'opvangen', 'opzoeken',
    'terugkeren', 'terugkomen', 'terugvinden', 'teruggaan', 'terugbrengen',
    'toelaten', 'toepassen', 'toevoegen', 'toenemen', 'toekomen', 'toekennen',
    'uitgaan', 'uitgeven', 'uitkomen', 'uitmaken', 'uitnodigen', 'uitoefenen',
    'uitspreken', 'uitstellen', 'uitvoeren', 'uitwerken', 'uitwijzen', 'uitzetten',
    'uitbreiden', 'uitleggen', 'uitlopen', 'uitpakken', 'uitschakelen', 'uitsluiten',
    'uitsteken', 'uittrekken', 'uitvallen', 'uitvinden', 'uitwisselen', 'uitzien',
    'vaststellen', 'vasthouden', 'vastleggen', 'vastzetten',
    'voordoen', 'voorleggen', 'voornemen', 'voorstellen', 'voortbrengen',
    'voortduren', 'voortzetten',
    'weggaan', 'weglopen', 'wegnemen', 'wegvallen',
    'samenkomen', 'samenwerken', 'samenstellen', 'samenvallen', 'samenhangen',
    'tegenspreken', 'tegenkomen', 'tegenhouden', 'tegenvallen',
}


def is_separable(infinitive):
    """Check if a verb is separable (scheidbaar werkwoord)."""
    if infinitive in FORCE_INSEPARABLE:
        return False
    if infinitive in FORCE_SEPARABLE:
        return True

    # Check if it starts with an inseparable prefix
    for prefix in INSEPARABLE_PREFIXES:
        if infinitive.startswith(prefix) and len(infinitive) > len(prefix) + 2:
            return False

    # Check if it starts with a separable prefix
    for prefix in SEPARABLE_PREFIXES:
        if infinitive.startswith(prefix):
            remainder = infinitive[len(prefix):]
            # The remainder should be a valid verb (ends in -en or -n)
            if len(remainder) >= 3 and (remainder.endswith('en') or remainder.endswith('n')):
                return True

    return False


def split_separable(infinitive):
    """Split a separable verb into (prefix, base_verb). Returns (None, infinitive) if not separable."""
    if not is_separable(infinitive):
        return None, infinitive

    # Try longest prefix first
    for prefix in sorted(SEPARABLE_PREFIXES, key=len, reverse=True):
        if infinitive.startswith(prefix):
            remainder = infinitive[len(prefix):]
            if len(remainder) >= 3 and (remainder.endswith('en') or remainder.endswith('n')):
                return prefix, remainder

    return None, infinitive


def get_stem(infinitive):
    """Get the verb stem from the infinitive."""
    if infinitive.endswith('en'):
        stem = infinitive[:-2]
    elif infinitive.endswith('n'):
        stem = infinitive[:-1]
    else:
        return infinitive

    # Reduce double final consonants: "bell" -> "bel", "stell" -> "stel"
    # In Dutch, double consonants at the end of a word are reduced to single
    # (they were doubled to keep the preceding vowel short in the infinitive)
    if len(stem) >= 3 and stem[-1] == stem[-2] and stem[-1] not in 'aeiou':
        stem = stem[:-1]

    return stem


def apply_spelling_rules(stem, infinitive):
    """
    Apply Dutch spelling rules to get the correct stem.
    In Dutch, long vowels in closed syllables need doubling.
    Key insight: check the ORIGINAL infinitive to determine if a vowel is long or short.
    - Single consonant before 'en' = long vowel (open syllable): ma-ken → maak
    - Double consonant before 'en' = short vowel (closed syllable): bel-len → bel
    """
    if len(stem) < 2:
        return stem

    vowels = 'aeiou'

    # Determine from the infinitive whether the vowel before the ending is long or short.
    # Strip the -en/-n ending to get the raw infinitive stem (before our consonant reduction)
    if infinitive.endswith('en'):
        raw_inf_stem = infinitive[:-2]
    elif infinitive.endswith('n'):
        raw_inf_stem = infinitive[:-1]
    else:
        raw_inf_stem = infinitive

    # Check if raw_inf_stem ends with double consonant → short vowel, do NOT double
    has_double_consonant = (len(raw_inf_stem) >= 2
                           and raw_inf_stem[-1] == raw_inf_stem[-2]
                           and raw_inf_stem[-1] not in vowels)

    if not has_double_consonant:
        # Check if stem ends with consonant and has single vowel before it
        if len(stem) >= 2 and stem[-1] not in vowels:
            # Find the last vowel
            i = len(stem) - 2
            while i >= 0 and stem[i] not in vowels:
                i -= 1

            if i >= 0 and stem[i] in vowels:
                # Check if it's a single vowel (not already doubled)
                if i == 0 or stem[i-1] not in vowels:
                    # Only double for monosyllabic base stems.
                    # Polysyllabic stems like "nodig" should NOT get doubling.
                    # But for inseparable prefix verbs (betalen→betal), ignore the
                    # prefix vowel — check only the base verb portion.
                    check_from = 0
                    for pfx in INSEPARABLE_PREFIXES:
                        if stem.startswith(pfx):
                            remainder_root = stem[len(pfx):]
                            # Only treat as prefix if remainder has a vowel
                            if any(c in vowels for c in remainder_root):
                                check_from = len(pfx)
                                break
                    has_earlier_vowel = any(c in vowels for c in stem[check_from:i])

                    # Count consonants after the vowel in the stem
                    consonants_after = 0
                    for j in range(i+1, len(stem)):
                        if stem[j] not in vowels:
                            consonants_after += 1

                    if consonants_after == 1 and not has_earlier_vowel:
                        # Open syllable in infinitive → long vowel → double it
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
    Returns conjugation dict with present, past, perfect, and separable flag.
    Handles scheidbare werkwoorden (separable verbs).
    """
    sep_prefix, base_verb = split_separable(infinitive)
    is_sep = sep_prefix is not None

    # Conjugate the base verb (without the separable prefix)
    verb_to_conjugate = base_verb if is_sep else infinitive
    raw_stem = get_stem(verb_to_conjugate)
    stem = apply_spelling_rules(raw_stem, verb_to_conjugate)

    # Present tense
    if is_sep:
        # Separable: "ik bel op", "jij belt op"
        present = {
            'ik': stem + ' ' + sep_prefix,
            'jij': stem + 't ' + sep_prefix,
            'u': stem + 't ' + sep_prefix,
            'hij/zij': stem + 't ' + sep_prefix,
            'wij': base_verb + ' ' + sep_prefix,
            'jullie': base_verb + ' ' + sep_prefix,
            'zij_plural': base_verb + ' ' + sep_prefix,
        }
        if stem.endswith('t'):
            present['jij'] = stem + ' ' + sep_prefix
            present['u'] = stem + ' ' + sep_prefix
            present['hij/zij'] = stem + ' ' + sep_prefix
    else:
        present = {
            'ik': stem,
            'jij': stem + 't',
            'u': stem + 't',
            'hij/zij': stem + 't',
            'wij': infinitive,
            'jullie': infinitive,
            'zij_plural': infinitive
        }
        if stem.endswith('t'):
            present['jij'] = stem
            present['u'] = stem
            present['hij/zij'] = stem

    # Past tense: 't kofschip rule
    tkofschip = ('t', 'k', 'f', 's', 'p')

    if stem.endswith('ch') or stem[-1] in tkofschip:
        past_singular = stem + 'te'
        past_plural = stem + 'ten'
    else:
        past_singular = stem + 'de'
        past_plural = stem + 'den'

    if is_sep:
        past = {
            'ik': past_singular + ' ' + sep_prefix,
            'jij': past_singular + ' ' + sep_prefix,
            'u': past_singular + ' ' + sep_prefix,
            'hij/zij': past_singular + ' ' + sep_prefix,
            'wij': past_plural + ' ' + sep_prefix,
            'jullie': past_plural + ' ' + sep_prefix,
            'zij_plural': past_plural + ' ' + sep_prefix,
        }
    else:
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
    # Rule: ge + stem + t (if 't kofschip) or + d (otherwise)
    # But don't double: if stem already ends in 'd', don't add another 'd'
    # Same for 't' — if stem ends in 't', don't add another 't'
    def make_perfect_suffix(stem):
        if stem.endswith('ch') or stem[-1] in tkofschip:
            return stem if stem.endswith('t') else stem + 't'
        else:
            return stem if stem.endswith('d') else stem + 'd'

    if is_sep:
        # Separable: prefix + ge + stem + t/d → "opgebeld", "aangekomen"
        perfect = sep_prefix + 'ge' + make_perfect_suffix(stem)
    else:
        prefix = 'ge'
        # Inseparable prefixes don't get 'ge-'
        # The remainder must look like a real verb: ≥4 chars, ends in -en,
        # and has a vowel before the -en ending (so "llen" from "bellen" is rejected)
        insep_vowels = 'aeiou'
        for p in INSEPARABLE_PREFIXES:
            if infinitive.startswith(p):
                remainder = infinitive[len(p):]
                root = remainder[:-2] if remainder.endswith('en') else remainder[:-1] if remainder.endswith('n') else ''
                if len(remainder) >= 4 and remainder.endswith('en') and any(c in insep_vowels for c in root):
                    prefix = ''
                    break

        perfect = prefix + make_perfect_suffix(stem)

        # Fix double 'ge' for verbs starting with 'ge'
        if perfect.startswith('gege'):
            perfect = perfect[2:]

    result = {
        'present': present,
        'past': past,
        'perfect': perfect
    }

    if is_sep:
        result['separable'] = True
        result['prefix'] = sep_prefix

    return result


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
    'bezoeken': {
        'present': {'ik': 'bezoek', 'jij': 'bezoekt', 'u': 'bezoekt', 'hij/zij': 'bezoekt', 'wij': 'bezoeken', 'jullie': 'bezoeken', 'zij_plural': 'bezoeken'},
        'past': {'ik': 'bezocht', 'jij': 'bezocht', 'u': 'bezocht', 'hij/zij': 'bezocht', 'wij': 'bezochten', 'jullie': 'bezochten', 'zij_plural': 'bezochten'},
        'perfect': 'bezocht'
    },
    'beschrijven': {
        'present': {'ik': 'beschrijf', 'jij': 'beschrijft', 'u': 'beschrijft', 'hij/zij': 'beschrijft', 'wij': 'beschrijven', 'jullie': 'beschrijven', 'zij_plural': 'beschrijven'},
        'past': {'ik': 'beschreef', 'jij': 'beschreef', 'u': 'beschreef', 'hij/zij': 'beschreef', 'wij': 'beschreven', 'jullie': 'beschreven', 'zij_plural': 'beschreven'},
        'perfect': 'beschreven'
    },
    'besluiten': {
        'present': {'ik': 'besluit', 'jij': 'besluit', 'u': 'besluit', 'hij/zij': 'besluit', 'wij': 'besluiten', 'jullie': 'besluiten', 'zij_plural': 'besluiten'},
        'past': {'ik': 'besloot', 'jij': 'besloot', 'u': 'besloot', 'hij/zij': 'besloot', 'wij': 'besloten', 'jullie': 'besloten', 'zij_plural': 'besloten'},
        'perfect': 'besloten'
    },
    'bespreken': {
        'present': {'ik': 'bespreek', 'jij': 'bespreekt', 'u': 'bespreekt', 'hij/zij': 'bespreekt', 'wij': 'bespreken', 'jullie': 'bespreken', 'zij_plural': 'bespreken'},
        'past': {'ik': 'besprak', 'jij': 'besprak', 'u': 'besprak', 'hij/zij': 'besprak', 'wij': 'bespraken', 'jullie': 'bespraken', 'zij_plural': 'bespraken'},
        'perfect': 'besproken'
    },
    'bestrijden': {
        'present': {'ik': 'bestrijd', 'jij': 'bestrijdt', 'u': 'bestrijdt', 'hij/zij': 'bestrijdt', 'wij': 'bestrijden', 'jullie': 'bestrijden', 'zij_plural': 'bestrijden'},
        'past': {'ik': 'bestreed', 'jij': 'bestreed', 'u': 'bestreed', 'hij/zij': 'bestreed', 'wij': 'bestreden', 'jullie': 'bestreden', 'zij_plural': 'bestreden'},
        'perfect': 'bestreden'
    },
    'bedrijven': {
        'present': {'ik': 'bedrijf', 'jij': 'bedrijft', 'u': 'bedrijft', 'hij/zij': 'bedrijft', 'wij': 'bedrijven', 'jullie': 'bedrijven', 'zij_plural': 'bedrijven'},
        'past': {'ik': 'bedreef', 'jij': 'bedreef', 'u': 'bedreef', 'hij/zij': 'bedreef', 'wij': 'bedreven', 'jullie': 'bedreven', 'zij_plural': 'bedreven'},
        'perfect': 'bedreven'
    },
    'bederven': {
        'present': {'ik': 'bederf', 'jij': 'bederft', 'u': 'bederft', 'hij/zij': 'bederft', 'wij': 'bederven', 'jullie': 'bederven', 'zij_plural': 'bederven'},
        'past': {'ik': 'bedierf', 'jij': 'bedierf', 'u': 'bedierf', 'hij/zij': 'bedierf', 'wij': 'bedierven', 'jullie': 'bedierven', 'zij_plural': 'bedierven'},
        'perfect': 'bedorven'
    },
    'bedwingen': {
        'present': {'ik': 'bedwing', 'jij': 'bedwingt', 'u': 'bedwingt', 'hij/zij': 'bedwingt', 'wij': 'bedwingen', 'jullie': 'bedwingen', 'zij_plural': 'bedwingen'},
        'past': {'ik': 'bedwong', 'jij': 'bedwong', 'u': 'bedwong', 'hij/zij': 'bedwong', 'wij': 'bedwongen', 'jullie': 'bedwongen', 'zij_plural': 'bedwongen'},
        'perfect': 'bedwongen'
    },
    'bevallen': {
        'present': {'ik': 'beval', 'jij': 'bevalt', 'u': 'bevalt', 'hij/zij': 'bevalt', 'wij': 'bevallen', 'jullie': 'bevallen', 'zij_plural': 'bevallen'},
        'past': {'ik': 'beviel', 'jij': 'beviel', 'u': 'beviel', 'hij/zij': 'beviel', 'wij': 'bevielen', 'jullie': 'bevielen', 'zij_plural': 'bevielen'},
        'perfect': 'bevallen'
    },
    'bewijzen': {
        'present': {'ik': 'bewijs', 'jij': 'bewijst', 'u': 'bewijst', 'hij/zij': 'bewijst', 'wij': 'bewijzen', 'jullie': 'bewijzen', 'zij_plural': 'bewijzen'},
        'past': {'ik': 'bewees', 'jij': 'bewees', 'u': 'bewees', 'hij/zij': 'bewees', 'wij': 'bewezen', 'jullie': 'bewezen', 'zij_plural': 'bewezen'},
        'perfect': 'bewezen'
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
    'verliezen': {
        'present': {'ik': 'verlies', 'jij': 'verliest', 'u': 'verliest', 'hij/zij': 'verliest', 'wij': 'verliezen', 'jullie': 'verliezen', 'zij_plural': 'verliezen'},
        'past': {'ik': 'verloor', 'jij': 'verloor', 'u': 'verloor', 'hij/zij': 'verloor', 'wij': 'verloren', 'jullie': 'verloren', 'zij_plural': 'verloren'},
        'perfect': 'verloren'
    },
    'ontbreken': {
        'present': {'ik': 'ontbreek', 'jij': 'ontbreekt', 'u': 'ontbreekt', 'hij/zij': 'ontbreekt', 'wij': 'ontbreken', 'jullie': 'ontbreken', 'zij_plural': 'ontbreken'},
        'past': {'ik': 'ontbrak', 'jij': 'ontbrak', 'u': 'ontbrak', 'hij/zij': 'ontbrak', 'wij': 'ontbraken', 'jullie': 'ontbraken', 'zij_plural': 'ontbraken'},
        'perfect': 'ontbroken'
    },
    'ontvangen': {
        'present': {'ik': 'ontvang', 'jij': 'ontvangt', 'u': 'ontvangt', 'hij/zij': 'ontvangt', 'wij': 'ontvangen', 'jullie': 'ontvangen', 'zij_plural': 'ontvangen'},
        'past': {'ik': 'ontving', 'jij': 'ontving', 'u': 'ontving', 'hij/zij': 'ontving', 'wij': 'ontvingen', 'jullie': 'ontvingen', 'zij_plural': 'ontvingen'},
        'perfect': 'ontvangen'
    },
    'verbinden': {
        'present': {'ik': 'verbind', 'jij': 'verbindt', 'u': 'verbindt', 'hij/zij': 'verbindt', 'wij': 'verbinden', 'jullie': 'verbinden', 'zij_plural': 'verbinden'},
        'past': {'ik': 'verbond', 'jij': 'verbond', 'u': 'verbond', 'hij/zij': 'verbond', 'wij': 'verbonden', 'jullie': 'verbonden', 'zij_plural': 'verbonden'},
        'perfect': 'verbonden'
    },
    'vergelijken': {
        'present': {'ik': 'vergelijk', 'jij': 'vergelijkt', 'u': 'vergelijkt', 'hij/zij': 'vergelijkt', 'wij': 'vergelijken', 'jullie': 'vergelijken', 'zij_plural': 'vergelijken'},
        'past': {'ik': 'vergeleek', 'jij': 'vergeleek', 'u': 'vergeleek', 'hij/zij': 'vergeleek', 'wij': 'vergeleken', 'jullie': 'vergeleken', 'zij_plural': 'vergeleken'},
        'perfect': 'vergeleken'
    },
    'vernemen': {
        'present': {'ik': 'verneem', 'jij': 'verneemt', 'u': 'verneemt', 'hij/zij': 'verneemt', 'wij': 'vernemen', 'jullie': 'vernemen', 'zij_plural': 'vernemen'},
        'past': {'ik': 'vernam', 'jij': 'vernam', 'u': 'vernam', 'hij/zij': 'vernam', 'wij': 'vernamen', 'jullie': 'vernamen', 'zij_plural': 'vernamen'},
        'perfect': 'vernomen'
    },
    'verstaan': {
        'present': {'ik': 'versta', 'jij': 'verstaat', 'u': 'verstaat', 'hij/zij': 'verstaat', 'wij': 'verstaan', 'jullie': 'verstaan', 'zij_plural': 'verstaan'},
        'past': {'ik': 'verstond', 'jij': 'verstond', 'u': 'verstond', 'hij/zij': 'verstond', 'wij': 'verstonden', 'jullie': 'verstonden', 'zij_plural': 'verstonden'},
        'perfect': 'verstaan'
    },
    'scheiden': {
        'present': {'ik': 'scheid', 'jij': 'scheidt', 'u': 'scheidt', 'hij/zij': 'scheidt', 'wij': 'scheiden', 'jullie': 'scheiden', 'zij_plural': 'scheiden'},
        'past': {'ik': 'scheidde', 'jij': 'scheidde', 'u': 'scheidde', 'hij/zij': 'scheidde', 'wij': 'scheidden', 'jullie': 'scheidden', 'zij_plural': 'scheidden'},
        'perfect': 'gescheiden'
    },
    'bakken': {
        'present': {'ik': 'bak', 'jij': 'bakt', 'u': 'bakt', 'hij/zij': 'bakt', 'wij': 'bakken', 'jullie': 'bakken', 'zij_plural': 'bakken'},
        'past': {'ik': 'bakte', 'jij': 'bakte', 'u': 'bakte', 'hij/zij': 'bakte', 'wij': 'bakten', 'jullie': 'bakten', 'zij_plural': 'bakten'},
        'perfect': 'gebakken'
    },
    'barsten': {
        'present': {'ik': 'barst', 'jij': 'barst', 'u': 'barst', 'hij/zij': 'barst', 'wij': 'barsten', 'jullie': 'barsten', 'zij_plural': 'barsten'},
        'past': {'ik': 'barstte', 'jij': 'barstte', 'u': 'barstte', 'hij/zij': 'barstte', 'wij': 'barstten', 'jullie': 'barstten', 'zij_plural': 'barstten'},
        'perfect': 'gebarsten'
    },
    'bergen': {
        'present': {'ik': 'berg', 'jij': 'bergt', 'u': 'bergt', 'hij/zij': 'bergt', 'wij': 'bergen', 'jullie': 'bergen', 'zij_plural': 'bergen'},
        'past': {'ik': 'borg', 'jij': 'borg', 'u': 'borg', 'hij/zij': 'borg', 'wij': 'borgen', 'jullie': 'borgen', 'zij_plural': 'borgen'},
        'perfect': 'geborgen'
    },
    'blinken': {
        'present': {'ik': 'blink', 'jij': 'blinkt', 'u': 'blinkt', 'hij/zij': 'blinkt', 'wij': 'blinken', 'jullie': 'blinken', 'zij_plural': 'blinken'},
        'past': {'ik': 'blonk', 'jij': 'blonk', 'u': 'blonk', 'hij/zij': 'blonk', 'wij': 'blonken', 'jullie': 'blonken', 'zij_plural': 'blonken'},
        'perfect': 'geblonken'
    },
    'delven': {
        'present': {'ik': 'delf', 'jij': 'delft', 'u': 'delft', 'hij/zij': 'delft', 'wij': 'delven', 'jullie': 'delven', 'zij_plural': 'delven'},
        'past': {'ik': 'dolf', 'jij': 'dolf', 'u': 'dolf', 'hij/zij': 'dolf', 'wij': 'dolven', 'jullie': 'dolven', 'zij_plural': 'dolven'},
        'perfect': 'gedolven'
    },
    'duiken': {
        'present': {'ik': 'duik', 'jij': 'duikt', 'u': 'duikt', 'hij/zij': 'duikt', 'wij': 'duiken', 'jullie': 'duiken', 'zij_plural': 'duiken'},
        'past': {'ik': 'dook', 'jij': 'dook', 'u': 'dook', 'hij/zij': 'dook', 'wij': 'doken', 'jullie': 'doken', 'zij_plural': 'doken'},
        'perfect': 'gedoken'
    },
    'fluiten': {
        'present': {'ik': 'fluit', 'jij': 'fluit', 'u': 'fluit', 'hij/zij': 'fluit', 'wij': 'fluiten', 'jullie': 'fluiten', 'zij_plural': 'fluiten'},
        'past': {'ik': 'floot', 'jij': 'floot', 'u': 'floot', 'hij/zij': 'floot', 'wij': 'floten', 'jullie': 'floten', 'zij_plural': 'floten'},
        'perfect': 'gefloten'
    },
    'heffen': {
        'present': {'ik': 'hef', 'jij': 'heft', 'u': 'heft', 'hij/zij': 'heft', 'wij': 'heffen', 'jullie': 'heffen', 'zij_plural': 'heffen'},
        'past': {'ik': 'hief', 'jij': 'hief', 'u': 'hief', 'hij/zij': 'hief', 'wij': 'hieven', 'jullie': 'hieven', 'zij_plural': 'hieven'},
        'perfect': 'geheven'
    },
    'klinken': {
        'present': {'ik': 'klink', 'jij': 'klinkt', 'u': 'klinkt', 'hij/zij': 'klinkt', 'wij': 'klinken', 'jullie': 'klinken', 'zij_plural': 'klinken'},
        'past': {'ik': 'klonk', 'jij': 'klonk', 'u': 'klonk', 'hij/zij': 'klonk', 'wij': 'klonken', 'jullie': 'klonken', 'zij_plural': 'klonken'},
        'perfect': 'geklonken'
    },
    'kruipen': {
        'present': {'ik': 'kruip', 'jij': 'kruipt', 'u': 'kruipt', 'hij/zij': 'kruipt', 'wij': 'kruipen', 'jullie': 'kruipen', 'zij_plural': 'kruipen'},
        'past': {'ik': 'kroop', 'jij': 'kroop', 'u': 'kroop', 'hij/zij': 'kroop', 'wij': 'kropen', 'jullie': 'kropen', 'zij_plural': 'kropen'},
        'perfect': 'gekropen'
    },
    'lijken': {
        'present': {'ik': 'lijk', 'jij': 'lijkt', 'u': 'lijkt', 'hij/zij': 'lijkt', 'wij': 'lijken', 'jullie': 'lijken', 'zij_plural': 'lijken'},
        'past': {'ik': 'leek', 'jij': 'leek', 'u': 'leek', 'hij/zij': 'leek', 'wij': 'leken', 'jullie': 'leken', 'zij_plural': 'leken'},
        'perfect': 'geleken'
    },
    'rijzen': {
        'present': {'ik': 'rijs', 'jij': 'rijst', 'u': 'rijst', 'hij/zij': 'rijst', 'wij': 'rijzen', 'jullie': 'rijzen', 'zij_plural': 'rijzen'},
        'past': {'ik': 'rees', 'jij': 'rees', 'u': 'rees', 'hij/zij': 'rees', 'wij': 'rezen', 'jullie': 'rezen', 'zij_plural': 'rezen'},
        'perfect': 'gerezen'
    },
    'ruiken': {
        'present': {'ik': 'ruik', 'jij': 'ruikt', 'u': 'ruikt', 'hij/zij': 'ruikt', 'wij': 'ruiken', 'jullie': 'ruiken', 'zij_plural': 'ruiken'},
        'past': {'ik': 'rook', 'jij': 'rook', 'u': 'rook', 'hij/zij': 'rook', 'wij': 'roken', 'jullie': 'roken', 'zij_plural': 'roken'},
        'perfect': 'geroken'
    },
    'schrikken': {
        'present': {'ik': 'schrik', 'jij': 'schrikt', 'u': 'schrikt', 'hij/zij': 'schrikt', 'wij': 'schrikken', 'jullie': 'schrikken', 'zij_plural': 'schrikken'},
        'past': {'ik': 'schrok', 'jij': 'schrok', 'u': 'schrok', 'hij/zij': 'schrok', 'wij': 'schrokken', 'jullie': 'schrokken', 'zij_plural': 'schrokken'},
        'perfect': 'geschrokken'
    },
    'spijten': {
        'present': {'ik': 'spijt', 'jij': 'spijt', 'u': 'spijt', 'hij/zij': 'spijt', 'wij': 'spijten', 'jullie': 'spijten', 'zij_plural': 'spijten'},
        'past': {'ik': 'speet', 'jij': 'speet', 'u': 'speet', 'hij/zij': 'speet', 'wij': 'speten', 'jullie': 'speten', 'zij_plural': 'speten'},
        'perfect': 'gespeten'
    },
    'stinken': {
        'present': {'ik': 'stink', 'jij': 'stinkt', 'u': 'stinkt', 'hij/zij': 'stinkt', 'wij': 'stinken', 'jullie': 'stinken', 'zij_plural': 'stinken'},
        'past': {'ik': 'stonk', 'jij': 'stonk', 'u': 'stonk', 'hij/zij': 'stonk', 'wij': 'stonken', 'jullie': 'stonken', 'zij_plural': 'stonken'},
        'perfect': 'gestonken'
    },
    'vangen': {
        'present': {'ik': 'vang', 'jij': 'vangt', 'u': 'vangt', 'hij/zij': 'vangt', 'wij': 'vangen', 'jullie': 'vangen', 'zij_plural': 'vangen'},
        'past': {'ik': 'ving', 'jij': 'ving', 'u': 'ving', 'hij/zij': 'ving', 'wij': 'vingen', 'jullie': 'vingen', 'zij_plural': 'vingen'},
        'perfect': 'gevangen'
    },
    'vouwen': {
        'present': {'ik': 'vouw', 'jij': 'vouwt', 'u': 'vouwt', 'hij/zij': 'vouwt', 'wij': 'vouwen', 'jullie': 'vouwen', 'zij_plural': 'vouwen'},
        'past': {'ik': 'vouwde', 'jij': 'vouwde', 'u': 'vouwde', 'hij/zij': 'vouwde', 'wij': 'vouwden', 'jullie': 'vouwden', 'zij_plural': 'vouwden'},
        'perfect': 'gevouwen'
    },
    'zinken': {
        'present': {'ik': 'zink', 'jij': 'zinkt', 'u': 'zinkt', 'hij/zij': 'zinkt', 'wij': 'zinken', 'jullie': 'zinken', 'zij_plural': 'zinken'},
        'past': {'ik': 'zonk', 'jij': 'zonk', 'u': 'zonk', 'hij/zij': 'zonk', 'wij': 'zonken', 'jullie': 'zonken', 'zij_plural': 'zonken'},
        'perfect': 'gezonken'
    },
    'zuigen': {
        'present': {'ik': 'zuig', 'jij': 'zuigt', 'u': 'zuigt', 'hij/zij': 'zuigt', 'wij': 'zuigen', 'jullie': 'zuigen', 'zij_plural': 'zuigen'},
        'past': {'ik': 'zoog', 'jij': 'zoog', 'u': 'zoog', 'hij/zij': 'zoog', 'wij': 'zogen', 'jullie': 'zogen', 'zij_plural': 'zogen'},
        'perfect': 'gezogen'
    },
    'zwellen': {
        'present': {'ik': 'zwel', 'jij': 'zwelt', 'u': 'zwelt', 'hij/zij': 'zwelt', 'wij': 'zwellen', 'jullie': 'zwellen', 'zij_plural': 'zwellen'},
        'past': {'ik': 'zwol', 'jij': 'zwol', 'u': 'zwol', 'hij/zij': 'zwol', 'wij': 'zwollen', 'jullie': 'zwollen', 'zij_plural': 'zwollen'},
        'perfect': 'gezwollen'
    },
    'zwerven': {
        'present': {'ik': 'zwerf', 'jij': 'zwerft', 'u': 'zwerft', 'hij/zij': 'zwerft', 'wij': 'zwerven', 'jullie': 'zwerven', 'zij_plural': 'zwerven'},
        'past': {'ik': 'zwierf', 'jij': 'zwierf', 'u': 'zwierf', 'hij/zij': 'zwierf', 'wij': 'zwierven', 'jullie': 'zwierven', 'zij_plural': 'zwierven'},
        'perfect': 'gezworven'
    },
    'zwijgen': {
        'present': {'ik': 'zwijg', 'jij': 'zwijgt', 'u': 'zwijgt', 'hij/zij': 'zwijgt', 'wij': 'zwijgen', 'jullie': 'zwijgen', 'zij_plural': 'zwijgen'},
        'past': {'ik': 'zweeg', 'jij': 'zweeg', 'u': 'zweeg', 'hij/zij': 'zweeg', 'wij': 'zwegen', 'jullie': 'zwegen', 'zij_plural': 'zwegen'},
        'perfect': 'gezwegen'
    },
    'begrijpen': {
        'present': {'ik': 'begrijp', 'jij': 'begrijpt', 'u': 'begrijpt', 'hij/zij': 'begrijpt', 'wij': 'begrijpen', 'jullie': 'begrijpen', 'zij_plural': 'begrijpen'},
        'past': {'ik': 'begreep', 'jij': 'begreep', 'u': 'begreep', 'hij/zij': 'begreep', 'wij': 'begrepen', 'jullie': 'begrepen', 'zij_plural': 'begrepen'},
        'perfect': 'begrepen'
    },
    'behouden': {
        'present': {'ik': 'behoud', 'jij': 'behoudt', 'u': 'behoudt', 'hij/zij': 'behoudt', 'wij': 'behouden', 'jullie': 'behouden', 'zij_plural': 'behouden'},
        'past': {'ik': 'behield', 'jij': 'behield', 'u': 'behield', 'hij/zij': 'behield', 'wij': 'behielden', 'jullie': 'behielden', 'zij_plural': 'behielden'},
        'perfect': 'behouden'
    },
    'bevinden': {
        'present': {'ik': 'bevind', 'jij': 'bevindt', 'u': 'bevindt', 'hij/zij': 'bevindt', 'wij': 'bevinden', 'jullie': 'bevinden', 'zij_plural': 'bevinden'},
        'past': {'ik': 'bevond', 'jij': 'bevond', 'u': 'bevond', 'hij/zij': 'bevond', 'wij': 'bevonden', 'jullie': 'bevonden', 'zij_plural': 'bevonden'},
        'perfect': 'bevonden'
    },
    'blijken': {
        'present': {'ik': 'blijk', 'jij': 'blijkt', 'u': 'blijkt', 'hij/zij': 'blijkt', 'wij': 'blijken', 'jullie': 'blijken', 'zij_plural': 'blijken'},
        'past': {'ik': 'bleek', 'jij': 'bleek', 'u': 'bleek', 'hij/zij': 'bleek', 'wij': 'bleken', 'jullie': 'bleken', 'zij_plural': 'bleken'},
        'perfect': 'gebleken'
    },
    'hijsen': {
        'present': {'ik': 'hijs', 'jij': 'hijst', 'u': 'hijst', 'hij/zij': 'hijst', 'wij': 'hijsen', 'jullie': 'hijsen', 'zij_plural': 'hijsen'},
        'past': {'ik': 'hees', 'jij': 'hees', 'u': 'hees', 'hij/zij': 'hees', 'wij': 'hesen', 'jullie': 'hesen', 'zij_plural': 'hesen'},
        'perfect': 'gehesen'
    },
    'krimpen': {
        'present': {'ik': 'krimp', 'jij': 'krimpt', 'u': 'krimpt', 'hij/zij': 'krimpt', 'wij': 'krimpen', 'jullie': 'krimpen', 'zij_plural': 'krimpen'},
        'past': {'ik': 'kromp', 'jij': 'kromp', 'u': 'kromp', 'hij/zij': 'kromp', 'wij': 'krompen', 'jullie': 'krompen', 'zij_plural': 'krompen'},
        'perfect': 'gekrompen'
    },
    'lachen': {
        'present': {'ik': 'lach', 'jij': 'lacht', 'u': 'lacht', 'hij/zij': 'lacht', 'wij': 'lachen', 'jullie': 'lachen', 'zij_plural': 'lachen'},
        'past': {'ik': 'lachte', 'jij': 'lachte', 'u': 'lachte', 'hij/zij': 'lachte', 'wij': 'lachten', 'jullie': 'lachten', 'zij_plural': 'lachten'},
        'perfect': 'gelachen'
    },
    'liegen': {
        'present': {'ik': 'lieg', 'jij': 'liegt', 'u': 'liegt', 'hij/zij': 'liegt', 'wij': 'liegen', 'jullie': 'liegen', 'zij_plural': 'liegen'},
        'past': {'ik': 'loog', 'jij': 'loog', 'u': 'loog', 'hij/zij': 'loog', 'wij': 'logen', 'jullie': 'logen', 'zij_plural': 'logen'},
        'perfect': 'gelogen'
    },
    'mijden': {
        'present': {'ik': 'mijd', 'jij': 'mijdt', 'u': 'mijdt', 'hij/zij': 'mijdt', 'wij': 'mijden', 'jullie': 'mijden', 'zij_plural': 'mijden'},
        'past': {'ik': 'meed', 'jij': 'meed', 'u': 'meed', 'hij/zij': 'meed', 'wij': 'meden', 'jullie': 'meden', 'zij_plural': 'meden'},
        'perfect': 'gemeden'
    },
    'ondernemen': {
        'present': {'ik': 'onderneem', 'jij': 'onderneemt', 'u': 'onderneemt', 'hij/zij': 'onderneemt', 'wij': 'ondernemen', 'jullie': 'ondernemen', 'zij_plural': 'ondernemen'},
        'past': {'ik': 'ondernam', 'jij': 'ondernam', 'u': 'ondernam', 'hij/zij': 'ondernam', 'wij': 'ondernamen', 'jullie': 'ondernamen', 'zij_plural': 'ondernamen'},
        'perfect': 'ondernomen'
    },
    'onderscheiden': {
        'present': {'ik': 'onderscheid', 'jij': 'onderscheidt', 'u': 'onderscheidt', 'hij/zij': 'onderscheidt', 'wij': 'onderscheiden', 'jullie': 'onderscheiden', 'zij_plural': 'onderscheiden'},
        'past': {'ik': 'onderscheidde', 'jij': 'onderscheidde', 'u': 'onderscheidde', 'hij/zij': 'onderscheidde', 'wij': 'onderscheidden', 'jullie': 'onderscheidden', 'zij_plural': 'onderscheidden'},
        'perfect': 'onderscheiden'
    },
    'ondervinden': {
        'present': {'ik': 'ondervind', 'jij': 'ondervindt', 'u': 'ondervindt', 'hij/zij': 'ondervindt', 'wij': 'ondervinden', 'jullie': 'ondervinden', 'zij_plural': 'ondervinden'},
        'past': {'ik': 'ondervond', 'jij': 'ondervond', 'u': 'ondervond', 'hij/zij': 'ondervond', 'wij': 'ondervonden', 'jullie': 'ondervonden', 'zij_plural': 'ondervonden'},
        'perfect': 'ondervonden'
    },
    'onthouden': {
        'present': {'ik': 'onthoud', 'jij': 'onthoudt', 'u': 'onthoudt', 'hij/zij': 'onthoudt', 'wij': 'onthouden', 'jullie': 'onthouden', 'zij_plural': 'onthouden'},
        'past': {'ik': 'onthield', 'jij': 'onthield', 'u': 'onthield', 'hij/zij': 'onthield', 'wij': 'onthielden', 'jullie': 'onthielden', 'zij_plural': 'onthielden'},
        'perfect': 'onthouden'
    },
    'overlijden': {
        'present': {'ik': 'overlijd', 'jij': 'overlijdt', 'u': 'overlijdt', 'hij/zij': 'overlijdt', 'wij': 'overlijden', 'jullie': 'overlijden', 'zij_plural': 'overlijden'},
        'past': {'ik': 'overleed', 'jij': 'overleed', 'u': 'overleed', 'hij/zij': 'overleed', 'wij': 'overleden', 'jullie': 'overleden', 'zij_plural': 'overleden'},
        'perfect': 'overleden'
    },
    'overwegen': {
        'present': {'ik': 'overweeg', 'jij': 'overweegt', 'u': 'overweegt', 'hij/zij': 'overweegt', 'wij': 'overwegen', 'jullie': 'overwegen', 'zij_plural': 'overwegen'},
        'past': {'ik': 'overwoog', 'jij': 'overwoog', 'u': 'overwoog', 'hij/zij': 'overwoog', 'wij': 'overwogen', 'jullie': 'overwogen', 'zij_plural': 'overwogen'},
        'perfect': 'overwogen'
    },
    'overwinnen': {
        'present': {'ik': 'overwin', 'jij': 'overwint', 'u': 'overwint', 'hij/zij': 'overwint', 'wij': 'overwinnen', 'jullie': 'overwinnen', 'zij_plural': 'overwinnen'},
        'past': {'ik': 'overwon', 'jij': 'overwon', 'u': 'overwon', 'hij/zij': 'overwon', 'wij': 'overwonnen', 'jullie': 'overwonnen', 'zij_plural': 'overwonnen'},
        'perfect': 'overwonnen'
    },
    'prijzen': {
        'present': {'ik': 'prijs', 'jij': 'prijst', 'u': 'prijst', 'hij/zij': 'prijst', 'wij': 'prijzen', 'jullie': 'prijzen', 'zij_plural': 'prijzen'},
        'past': {'ik': 'prees', 'jij': 'prees', 'u': 'prees', 'hij/zij': 'prees', 'wij': 'prezen', 'jullie': 'prezen', 'zij_plural': 'prezen'},
        'perfect': 'geprezen'
    },
    'raden': {
        'present': {'ik': 'raad', 'jij': 'raadt', 'u': 'raadt', 'hij/zij': 'raadt', 'wij': 'raden', 'jullie': 'raden', 'zij_plural': 'raden'},
        'past': {'ik': 'ried', 'jij': 'ried', 'u': 'ried', 'hij/zij': 'ried', 'wij': 'rieden', 'jullie': 'rieden', 'zij_plural': 'rieden'},
        'perfect': 'geraden'
    },
    'schuiven': {
        'present': {'ik': 'schuif', 'jij': 'schuift', 'u': 'schuift', 'hij/zij': 'schuift', 'wij': 'schuiven', 'jullie': 'schuiven', 'zij_plural': 'schuiven'},
        'past': {'ik': 'schoof', 'jij': 'schoof', 'u': 'schoof', 'hij/zij': 'schoof', 'wij': 'schoven', 'jullie': 'schoven', 'zij_plural': 'schoven'},
        'perfect': 'geschoven'
    },
    'spuiten': {
        'present': {'ik': 'spuit', 'jij': 'spuit', 'u': 'spuit', 'hij/zij': 'spuit', 'wij': 'spuiten', 'jullie': 'spuiten', 'zij_plural': 'spuiten'},
        'past': {'ik': 'spoot', 'jij': 'spoot', 'u': 'spoot', 'hij/zij': 'spoot', 'wij': 'spoten', 'jullie': 'spoten', 'zij_plural': 'spoten'},
        'perfect': 'gespoten'
    },
    'stijgen': {
        'present': {'ik': 'stijg', 'jij': 'stijgt', 'u': 'stijgt', 'hij/zij': 'stijgt', 'wij': 'stijgen', 'jullie': 'stijgen', 'zij_plural': 'stijgen'},
        'past': {'ik': 'steeg', 'jij': 'steeg', 'u': 'steeg', 'hij/zij': 'steeg', 'wij': 'stegen', 'jullie': 'stegen', 'zij_plural': 'stegen'},
        'perfect': 'gestegen'
    },
    'strijken': {
        'present': {'ik': 'strijk', 'jij': 'strijkt', 'u': 'strijkt', 'hij/zij': 'strijkt', 'wij': 'strijken', 'jullie': 'strijken', 'zij_plural': 'strijken'},
        'past': {'ik': 'streek', 'jij': 'streek', 'u': 'streek', 'hij/zij': 'streek', 'wij': 'streken', 'jullie': 'streken', 'zij_plural': 'streken'},
        'perfect': 'gestreken'
    },
    'treden': {
        'present': {'ik': 'treed', 'jij': 'treedt', 'u': 'treedt', 'hij/zij': 'treedt', 'wij': 'treden', 'jullie': 'treden', 'zij_plural': 'treden'},
        'past': {'ik': 'trad', 'jij': 'trad', 'u': 'trad', 'hij/zij': 'trad', 'wij': 'traden', 'jullie': 'traden', 'zij_plural': 'traden'},
        'perfect': 'getreden'
    },
    'varen': {
        'present': {'ik': 'vaar', 'jij': 'vaart', 'u': 'vaart', 'hij/zij': 'vaart', 'wij': 'varen', 'jullie': 'varen', 'zij_plural': 'varen'},
        'past': {'ik': 'voer', 'jij': 'voer', 'u': 'voer', 'hij/zij': 'voer', 'wij': 'voeren', 'jullie': 'voeren', 'zij_plural': 'voeren'},
        'perfect': 'gevaren'
    },
    'verwerven': {
        'present': {'ik': 'verwerf', 'jij': 'verwerft', 'u': 'verwerft', 'hij/zij': 'verwerft', 'wij': 'verwerven', 'jullie': 'verwerven', 'zij_plural': 'verwerven'},
        'past': {'ik': 'verwierf', 'jij': 'verwierf', 'u': 'verwierf', 'hij/zij': 'verwierf', 'wij': 'verwierven', 'jullie': 'verwierven', 'zij_plural': 'verwierven'},
        'perfect': 'verworven'
    },
    'vragen': {
        'present': {'ik': 'vraag', 'jij': 'vraagt', 'u': 'vraagt', 'hij/zij': 'vraagt', 'wij': 'vragen', 'jullie': 'vragen', 'zij_plural': 'vragen'},
        'past': {'ik': 'vroeg', 'jij': 'vroeg', 'u': 'vroeg', 'hij/zij': 'vroeg', 'wij': 'vroegen', 'jullie': 'vroegen', 'zij_plural': 'vroegen'},
        'perfect': 'gevraagd'
    },
    'vriezen': {
        'present': {'ik': 'vries', 'jij': 'vriest', 'u': 'vriest', 'hij/zij': 'vriest', 'wij': 'vriezen', 'jullie': 'vriezen', 'zij_plural': 'vriezen'},
        'past': {'ik': 'vroor', 'jij': 'vroor', 'u': 'vroor', 'hij/zij': 'vroor', 'wij': 'vroren', 'jullie': 'vroren', 'zij_plural': 'vroren'},
        'perfect': 'gevroren'
    },
    'wijken': {
        'present': {'ik': 'wijk', 'jij': 'wijkt', 'u': 'wijkt', 'hij/zij': 'wijkt', 'wij': 'wijken', 'jullie': 'wijken', 'zij_plural': 'wijken'},
        'past': {'ik': 'week', 'jij': 'week', 'u': 'week', 'hij/zij': 'week', 'wij': 'weken', 'jullie': 'weken', 'zij_plural': 'weken'},
        'perfect': 'geweken'
    },
    'wringen': {
        'present': {'ik': 'wring', 'jij': 'wringt', 'u': 'wringt', 'hij/zij': 'wringt', 'wij': 'wringen', 'jullie': 'wringen', 'zij_plural': 'wringen'},
        'past': {'ik': 'wrong', 'jij': 'wrong', 'u': 'wrong', 'hij/zij': 'wrong', 'wij': 'wrongen', 'jullie': 'wrongen', 'zij_plural': 'wrongen'},
        'perfect': 'gewrongen'
    },
    'overleven': {
        'present': {'ik': 'overleef', 'jij': 'overleeft', 'u': 'overleeft', 'hij/zij': 'overleeft', 'wij': 'overleven', 'jullie': 'overleven', 'zij_plural': 'overleven'},
        'past': {'ik': 'overleefde', 'jij': 'overleefde', 'u': 'overleefde', 'hij/zij': 'overleefde', 'wij': 'overleefden', 'jullie': 'overleefden', 'zij_plural': 'overleefden'},
        'perfect': 'overleefd'
    },
    'glijden': {
        'present': {'ik': 'glijd', 'jij': 'glijdt', 'u': 'glijdt', 'hij/zij': 'glijdt', 'wij': 'glijden', 'jullie': 'glijden', 'zij_plural': 'glijden'},
        'past': {'ik': 'gleed', 'jij': 'gleed', 'u': 'gleed', 'hij/zij': 'gleed', 'wij': 'gleden', 'jullie': 'gleden', 'zij_plural': 'gleden'},
        'perfect': 'gegleden'
    },
    'vermijden': {
        'present': {'ik': 'vermijd', 'jij': 'vermijdt', 'u': 'vermijdt', 'hij/zij': 'vermijdt', 'wij': 'vermijden', 'jullie': 'vermijden', 'zij_plural': 'vermijden'},
        'past': {'ik': 'vermeed', 'jij': 'vermeed', 'u': 'vermeed', 'hij/zij': 'vermeed', 'wij': 'vermeden', 'jullie': 'vermeden', 'zij_plural': 'vermeden'},
        'perfect': 'vermeden'
    },
    'strijden': {
        'present': {'ik': 'strijd', 'jij': 'strijdt', 'u': 'strijdt', 'hij/zij': 'strijdt', 'wij': 'strijden', 'jullie': 'strijden', 'zij_plural': 'strijden'},
        'past': {'ik': 'streed', 'jij': 'streed', 'u': 'streed', 'hij/zij': 'streed', 'wij': 'streden', 'jullie': 'streden', 'zij_plural': 'streden'},
        'perfect': 'gestreden'
    },
    'bidden': {
        'present': {'ik': 'bid', 'jij': 'bidt', 'u': 'bidt', 'hij/zij': 'bidt', 'wij': 'bidden', 'jullie': 'bidden', 'zij_plural': 'bidden'},
        'past': {'ik': 'bad', 'jij': 'bad', 'u': 'bad', 'hij/zij': 'bad', 'wij': 'baden', 'jullie': 'baden', 'zij_plural': 'baden'},
        'perfect': 'gebeden'
    },
    'schudden': {
        'present': {'ik': 'schud', 'jij': 'schudt', 'u': 'schudt', 'hij/zij': 'schudt', 'wij': 'schudden', 'jullie': 'schudden', 'zij_plural': 'schudden'},
        'past': {'ik': 'schudde', 'jij': 'schudde', 'u': 'schudde', 'hij/zij': 'schudde', 'wij': 'schudden', 'jullie': 'schudden', 'zij_plural': 'schudden'},
        'perfect': 'geschud'
    },
    'betreden': {
        'present': {'ik': 'betreed', 'jij': 'betreedt', 'u': 'betreedt', 'hij/zij': 'betreedt', 'wij': 'betreden', 'jullie': 'betreden', 'zij_plural': 'betreden'},
        'past': {'ik': 'betrad', 'jij': 'betrad', 'u': 'betrad', 'hij/zij': 'betrad', 'wij': 'betraden', 'jullie': 'betraden', 'zij_plural': 'betraden'},
        'perfect': 'betreden'
    },
    'bevriezen': {
        'present': {'ik': 'bevries', 'jij': 'bevriest', 'u': 'bevriest', 'hij/zij': 'bevriest', 'wij': 'bevriezen', 'jullie': 'bevriezen', 'zij_plural': 'bevriezen'},
        'past': {'ik': 'bevroor', 'jij': 'bevroor', 'u': 'bevroor', 'hij/zij': 'bevroor', 'wij': 'bevroren', 'jullie': 'bevroren', 'zij_plural': 'bevroren'},
        'perfect': 'bevroren'
    },
    'gelden': {
        'present': {'ik': 'geld', 'jij': 'geldt', 'u': 'geldt', 'hij/zij': 'geldt', 'wij': 'gelden', 'jullie': 'gelden', 'zij_plural': 'gelden'},
        'past': {'ik': 'gold', 'jij': 'gold', 'u': 'gold', 'hij/zij': 'gold', 'wij': 'golden', 'jullie': 'golden', 'zij_plural': 'golden'},
        'perfect': 'gegolden'
    },
}


def conjugate(infinitive):
    """
    Get conjugation for a verb.
    Handles: irregular verbs, separable verbs with irregular bases, and regular verbs.
    """
    # Direct irregular match
    if infinitive in IRREGULAR_VERBS:
        result = IRREGULAR_VERBS[infinitive]
        # Check if this irregular verb is also separable
        sep_prefix, base = split_separable(infinitive)
        if sep_prefix and 'separable' not in result:
            result['separable'] = True
            result['prefix'] = sep_prefix
        return result

    # Separable verb with irregular base?
    # e.g., "aankomen" -> prefix="aan", base="komen" (irregular)
    sep_prefix, base_verb = split_separable(infinitive)
    if sep_prefix and base_verb in IRREGULAR_VERBS:
        base_conj = IRREGULAR_VERBS[base_verb]
        # Build separable conjugation from the irregular base
        present = {}
        past = {}
        for person in base_conj['present']:
            present[person] = base_conj['present'][person] + ' ' + sep_prefix
        for person in base_conj['past']:
            past[person] = base_conj['past'][person] + ' ' + sep_prefix

        # Perfect: prefix + base_perfect (with 'ge' handling)
        # - If base already has 'ge': aan + gekomen = aangekomen
        # - If base has inseparable prefix (no 'ge'): aan + bevolen = aanbevolen
        # - Otherwise: op + ge + beld = opgebeld
        base_perfect = base_conj['perfect']
        if base_perfect.startswith('ge'):
            perfect = sep_prefix + base_perfect  # aan + gekomen = aangekomen
        elif any(base_verb.startswith(p) for p in INSEPARABLE_PREFIXES if len(base_verb) > len(p) + 2):
            perfect = sep_prefix + base_perfect  # aan + bevolen = aanbevolen (no extra ge)
        else:
            perfect = sep_prefix + 'ge' + base_perfect

        return {
            'present': present,
            'past': past,
            'perfect': perfect,
            'separable': True,
            'prefix': sep_prefix
        }

    # Regular verb (possibly separable - handled inside conjugate_regular)
    return conjugate_regular(infinitive)
