"""Generate irregular verb entries and add them to conjugator.py"""
import sys
sys.path.insert(0, '.')
from check_irregular import STRONG
from conjugator import IRREGULAR_VERBS

PERSONS = ['ik', 'jij', 'u', 'hij/zij', 'wij', 'jullie', 'zij_plural']

def make_entry(word, past_ik, perfect):
    """Generate a full irregular verb dict entry."""
    # Derive present tense
    if word.endswith('en'):
        raw = word[:-2]
    elif word.endswith('n'):
        raw = word[:-1]
    else:
        raw = word

    # Handle double consonant reduction
    if len(raw) >= 3 and raw[-1] == raw[-2] and raw[-1] not in 'aeiou':
        stem = raw[:-1]
    else:
        stem = raw

    # Apply vowel doubling for single-syllable stems
    vowels = 'aeiou'
    has_double_cons = len(raw) >= 2 and raw[-1] == raw[-2] and raw[-1] not in vowels

    if not has_double_cons and len(stem) >= 2 and stem[-1] not in vowels:
        i = len(stem) - 2
        while i >= 0 and stem[i] not in vowels:
            i -= 1
        if i >= 0 and stem[i] in vowels:
            if i == 0 or stem[i-1] not in vowels:
                # Check no earlier vowels (monosyllabic)
                insep = ('be', 'er', 'ge', 'her', 'ont', 'ver')
                check_from = 0
                for pfx in insep:
                    if stem.startswith(pfx) and any(c in vowels for c in stem[len(pfx):]):
                        check_from = len(pfx)
                        break
                has_earlier = any(c in vowels for c in stem[check_from:i])
                cons_after = sum(1 for c in stem[i+1:] if c not in vowels)
                if cons_after == 1 and not has_earlier:
                    stem = stem[:i] + stem[i] + stem[i:]

    # z->s, v->f
    if stem.endswith('z'): stem = stem[:-1] + 's'
    if stem.endswith('v'): stem = stem[:-1] + 'f'

    # Present
    jij_form = stem + 't' if not stem.endswith('t') else stem
    present = {p: (stem if p == 'ik' else jij_form if p in ('jij','u','hij/zij') else word) for p in PERSONS}

    # Past - derive plural from singular
    if past_ik.endswith('d') or past_ik.endswith('t'):
        past_plural = past_ik + 'en'
    elif past_ik[-1] == past_ik[-2:][0] if len(past_ik) >= 2 else False:
        past_plural = past_ik + 'en'
    else:
        past_plural = past_ik + 'en'

    past = {p: (past_ik if p in ('ik','jij','u','hij/zij') else past_plural) for p in PERSONS}

    return {
        'present': present,
        'past': past,
        'perfect': perfect
    }

# Generate entries for verbs not yet in IRREGULAR_VERBS
new_entries = {}
for word in sorted(STRONG.keys()):
    if word not in IRREGULAR_VERBS:
        past_ik, perfect = STRONG[word]
        new_entries[word] = make_entry(word, past_ik, perfect)

# Output as Python code
for word, entry in sorted(new_entries.items()):
    pr = entry['present']
    pa = entry['past']
    pf = entry['perfect']
    print(f"    '{word}': {{")
    print(f"        'present': {{'ik': '{pr['ik']}', 'jij': '{pr['jij']}', 'u': '{pr['u']}', 'hij/zij': '{pr['hij/zij']}', 'wij': '{pr['wij']}', 'jullie': '{pr['jullie']}', 'zij_plural': '{pr['zij_plural']}'}},")
    print(f"        'past': {{'ik': '{pa['ik']}', 'jij': '{pa['jij']}', 'u': '{pa['u']}', 'hij/zij': '{pa['hij/zij']}', 'wij': '{pa['wij']}', 'jullie': '{pa['jullie']}', 'zij_plural': '{pa['zij_plural']}'}},")
    print(f"        'perfect': '{pf}'")
    print(f"    }},")
