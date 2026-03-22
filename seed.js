const SEED_DATA = {
  nouns: [
    { id: "n1", word: "huis", translation: "house", article: "het" },
    { id: "n2", word: "boek", translation: "book", article: "het" },
    { id: "n3", word: "man", translation: "man", article: "de" },
    { id: "n4", word: "vrouw", translation: "woman", article: "de" },
    { id: "n5", word: "kind", translation: "child", article: "het" },
    { id: "n6", word: "school", translation: "school", article: "de" },
    { id: "n7", word: "water", translation: "water", article: "het" },
    { id: "n8", word: "stad", translation: "city", article: "de" },
    { id: "n9", word: "auto", translation: "car", article: "de" },
    { id: "n10", word: "dag", translation: "day", article: "de" }
  ],
  verbs: [
    {
      id: "v1", word: "zijn", translation: "to be",
      conjugations: {
        present: { ik: "ben", jij: "bent", u: "bent", "hij/zij": "is", wij: "zijn", jullie: "zijn", zij_plural: "zijn" },
        past: { ik: "was", jij: "was", u: "was", "hij/zij": "was", wij: "waren", jullie: "waren", zij_plural: "waren" },
        perfect: "geweest"
      }
    },
    {
      id: "v2", word: "hebben", translation: "to have",
      conjugations: {
        present: { ik: "heb", jij: "hebt", u: "hebt", "hij/zij": "heeft", wij: "hebben", jullie: "hebben", zij_plural: "hebben" },
        past: { ik: "had", jij: "had", u: "had", "hij/zij": "had", wij: "hadden", jullie: "hadden", zij_plural: "hadden" },
        perfect: "gehad"
      }
    },
    {
      id: "v3", word: "doen", translation: "to do",
      conjugations: {
        present: { ik: "doe", jij: "doet", u: "doet", "hij/zij": "doet", wij: "doen", jullie: "doen", zij_plural: "doen" },
        past: { ik: "deed", jij: "deed", u: "deed", "hij/zij": "deed", wij: "deden", jullie: "deden", zij_plural: "deden" },
        perfect: "gedaan"
      }
    },
    {
      id: "v4", word: "gaan", translation: "to go",
      conjugations: {
        present: { ik: "ga", jij: "gaat", u: "gaat", "hij/zij": "gaat", wij: "gaan", jullie: "gaan", zij_plural: "gaan" },
        past: { ik: "ging", jij: "ging", u: "ging", "hij/zij": "ging", wij: "gingen", jullie: "gingen", zij_plural: "gingen" },
        perfect: "gegaan"
      }
    },
    {
      id: "v5", word: "komen", translation: "to come",
      conjugations: {
        present: { ik: "kom", jij: "komt", u: "komt", "hij/zij": "komt", wij: "komen", jullie: "komen", zij_plural: "komen" },
        past: { ik: "kwam", jij: "kwam", u: "kwam", "hij/zij": "kwam", wij: "kwamen", jullie: "kwamen", zij_plural: "kwamen" },
        perfect: "gekomen"
      }
    },
    {
      id: "v6", word: "zien", translation: "to see",
      conjugations: {
        present: { ik: "zie", jij: "ziet", u: "ziet", "hij/zij": "ziet", wij: "zien", jullie: "zien", zij_plural: "zien" },
        past: { ik: "zag", jij: "zag", u: "zag", "hij/zij": "zag", wij: "zagen", jullie: "zagen", zij_plural: "zagen" },
        perfect: "gezien"
      }
    },
    {
      id: "v7", word: "willen", translation: "to want",
      conjugations: {
        present: { ik: "wil", jij: "wilt", u: "wilt", "hij/zij": "wil", wij: "willen", jullie: "willen", zij_plural: "willen" },
        past: { ik: "wilde", jij: "wilde", u: "wilde", "hij/zij": "wilde", wij: "wilden", jullie: "wilden", zij_plural: "wilden" },
        perfect: "gewild"
      }
    },
    {
      id: "v8", word: "maken", translation: "to make",
      conjugations: {
        present: { ik: "maak", jij: "maakt", u: "maakt", "hij/zij": "maakt", wij: "maken", jullie: "maken", zij_plural: "maken" },
        past: { ik: "maakte", jij: "maakte", u: "maakte", "hij/zij": "maakte", wij: "maakten", jullie: "maakten", zij_plural: "maakten" },
        perfect: "gemaakt"
      }
    },
    {
      id: "v9", word: "eten", translation: "to eat",
      conjugations: {
        present: { ik: "eet", jij: "eet", u: "eet", "hij/zij": "eet", wij: "eten", jullie: "eten", zij_plural: "eten" },
        past: { ik: "at", jij: "at", u: "at", "hij/zij": "at", wij: "aten", jullie: "aten", zij_plural: "aten" },
        perfect: "gegeten"
      }
    },
    {
      id: "v10", word: "werken", translation: "to work",
      conjugations: {
        present: { ik: "werk", jij: "werkt", u: "werkt", "hij/zij": "werkt", wij: "werken", jullie: "werken", zij_plural: "werken" },
        past: { ik: "werkte", jij: "werkte", u: "werkte", "hij/zij": "werkte", wij: "werkten", jullie: "werkten", zij_plural: "werkten" },
        perfect: "gewerkt"
      }
    }
  ],
  adjectives: [
    { id: "a1", word: "groot", translation: "big" },
    { id: "a2", word: "klein", translation: "small" },
    { id: "a3", word: "goed", translation: "good" },
    { id: "a4", word: "slecht", translation: "bad" },
    { id: "a5", word: "oud", translation: "old" },
    { id: "a6", word: "nieuw", translation: "new" },
    { id: "a7", word: "mooi", translation: "beautiful" },
    { id: "a8", word: "lelijk", translation: "ugly" },
    { id: "a9", word: "snel", translation: "fast" },
    { id: "a10", word: "langzaam", translation: "slow" }
  ]
};
