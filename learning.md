# Dutch Learning App - Session Learnings

## Irregular Verb Conjugation

### Problem
The regular conjugation algorithm was treating strong/irregular Dutch verbs as regular, producing incorrect past tenses and past participles. For example:
- "blijken" was generating "blijkte/geblijkt" instead of "bleek/gebleken"
- "kruipen" was generating "kruipte/gekruipt" instead of "kroop/gekropen"

### Scope
62 verbs were affected across several categories:
- Direct irregular verbs (e.g. blijken, liegen, vragen)
- Inseparable prefix verbs (e.g. begrijpen, overwegen, ondernemen)
- Separable verbs whose base is irregular (e.g. opbergen, afwijken, opstijgen)

### Dutch Strong Verb Classes Identified
| Class | Pattern | Examples |
|-------|---------|----------|
| ij -> ee | rijzen -> rees/gerezen | blijken, lijken, prijzen, strijken, wijken, zwijgen |
| ie -> oo | liegen -> loog/gelogen | vliegen, vriezen, schieten, kiezen |
| ui -> oo | kruipen -> kroop/gekropen | duiken, fluiten, ruiken, schuiven, sluiten, zuigen |
| i -> o | blinken -> blonk/geblonken | drinken, klinken, krimpen, springen, stinken, zinken, zwellen |
| e -> a/o | bergen -> borg/geborgen | delven, sterven, zwerven, werpen, heffen |
| ee -> a | treden -> trad/getreden | meten, lezen, vergeten, genezen |
| a -> oe | varen -> voer/gevaren | dragen, graven, slaan |
| aa -> ie | raden -> ried/geraden | slapen, laten, vallen, houden |
| Mixed | various | bakken/gebakken, lachen/gelachen, vragen/gevraagd |

### Key Insight - Separable + Irregular Interaction
When a separable verb has an irregular base, the conjugator already handled this correctly via `split_separable()` + lookup in `IRREGULAR_VERBS`. So adding the base verb to the dictionary automatically fixed all its separable compounds (e.g. adding `bergen` fixed `opbergen`, adding `stijgen` fixed `opstijgen`).

### Key Insight - Inseparable Prefix Verbs
Verbs with inseparable prefixes (be-, er-, ge-, her-, ont-, ver-, over-) need their own full entry in the irregular dict because:
- They don't get `ge-` in the perfect (begrijpen -> begrepen, not gebegrepen)
- Their past tense is one word (begreep, not greep be)
- The conjugator treats them as a single unit, not prefix + base

### Verification Approach
Created `check_irregular.py` with a comprehensive reference list of ~150 Dutch strong verbs. Cross-referenced against the generated `verbs.json` to find mismatches. This script can be re-run whenever new verbs are added to catch any missed irregulars.

### Total Irregular Verbs in Dictionary
~80 verbs now covered in `IRREGULAR_VERBS`, handling the vast majority of strong verbs in the dataset.
