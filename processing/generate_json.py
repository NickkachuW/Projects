"""
Combines all word data files and the conjugator to produce
the final nouns.json, verbs.json, and adjectives.json files.
Also updates seed.js with the full dataset.
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from conjugator import conjugate
from data_A_D import WORDS as WORDS_AD
from data_E_K import WORDS as WORDS_EK
from data_L_R import WORDS as WORDS_LR
from data_S_Z import WORDS as WORDS_SZ
from data_A_D_extra import WORDS as WORDS_AD2
from data_E_K_extra import WORDS as WORDS_EK2
from data_L_R_extra import WORDS as WORDS_LR2
from data_S_Z_extra import WORDS as WORDS_SZ2

# Merge all word dictionaries
ALL_WORDS = {}
ALL_WORDS.update(WORDS_AD)
ALL_WORDS.update(WORDS_EK)
ALL_WORDS.update(WORDS_LR)
ALL_WORDS.update(WORDS_SZ)
ALL_WORDS.update(WORDS_AD2)
ALL_WORDS.update(WORDS_EK2)
ALL_WORDS.update(WORDS_LR2)
ALL_WORDS.update(WORDS_SZ2)

print(f"Total words loaded: {len(ALL_WORDS)}")

nouns = []
verbs = []
adjectives = []

noun_id = 0
verb_id = 0
adj_id = 0

for word in sorted(ALL_WORDS.keys()):
    word_type, translation, article = ALL_WORDS[word]

    if word_type == "noun":
        noun_id += 1
        nouns.append({
            "id": f"n{noun_id}",
            "word": word,
            "translation": translation,
            "article": article
        })
    elif word_type == "verb":
        verb_id += 1
        conj = conjugate(word)
        verbs.append({
            "id": f"v{verb_id}",
            "word": word,
            "translation": translation,
            "conjugations": conj
        })
    elif word_type == "adjective":
        adj_id += 1
        adjectives.append({
            "id": f"a{adj_id}",
            "word": word,
            "translation": translation
        })

print(f"Nouns: {len(nouns)}")
print(f"Verbs: {len(verbs)}")
print(f"Adjectives: {len(adjectives)}")

# Write JSON files
base_dir = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(base_dir, "data", "nouns.json"), "w", encoding="utf-8") as f:
    json.dump(nouns, f, indent=2, ensure_ascii=False)

with open(os.path.join(base_dir, "data", "verbs.json"), "w", encoding="utf-8") as f:
    json.dump(verbs, f, indent=2, ensure_ascii=False)

with open(os.path.join(base_dir, "data", "adjectives.json"), "w", encoding="utf-8") as f:
    json.dump(adjectives, f, indent=2, ensure_ascii=False)

# Update seed.js with the full dataset
seed_content = f"const SEED_DATA = {json.dumps({'nouns': nouns, 'verbs': verbs, 'adjectives': adjectives}, indent=2, ensure_ascii=False)};\n"

with open(os.path.join(base_dir, "seed.js"), "w", encoding="utf-8") as f:
    f.write(seed_content)

print("Done! Files written:")
print(f"  data/nouns.json ({len(nouns)} nouns)")
print(f"  data/verbs.json ({len(verbs)} verbs)")
print(f"  data/adjectives.json ({len(adjectives)} adjectives)")
print(f"  seed.js (updated with full dataset)")
