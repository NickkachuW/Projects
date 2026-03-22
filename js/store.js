const Store = (() => {
  const STORAGE_KEY = 'dutch_learning_data';
  const TYPES = ['nouns', 'verbs', 'adjectives'];

  function loadAll() {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
    // First run — seed from bundled data
    const data = JSON.parse(JSON.stringify(SEED_DATA));
    saveAll(data);
    return data;
  }

  function saveAll(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }

  function getAll(type) {
    return loadAll()[type] || [];
  }

  function nextId(type) {
    const prefix = type[0]; // n, v, a
    const items = getAll(type);
    let max = 0;
    for (const item of items) {
      const num = parseInt(item.id.replace(/\D/g, ''), 10);
      if (num > max) max = num;
    }
    return prefix + (max + 1);
  }

  function add(type, item) {
    const data = loadAll();
    item.id = nextId(type);
    data[type].push(item);
    saveAll(data);
    return item;
  }

  function update(type, id, changes) {
    const data = loadAll();
    const list = data[type];
    const idx = list.findIndex(w => w.id === id);
    if (idx === -1) return null;
    Object.assign(list[idx], changes);
    saveAll(data);
    return list[idx];
  }

  function remove(type, id) {
    const data = loadAll();
    data[type] = data[type].filter(w => w.id !== id);
    saveAll(data);
    // Also remove spaced repetition data for this word
    SpacedRepetition.removeWord(id);
  }

  function getById(type, id) {
    return getAll(type).find(w => w.id === id) || null;
  }

  function exportData() {
    return JSON.stringify(loadAll(), null, 2);
  }

  function importData(jsonString) {
    const data = JSON.parse(jsonString);
    for (const type of TYPES) {
      if (!Array.isArray(data[type])) throw new Error(`Missing or invalid "${type}" array`);
    }
    saveAll(data);
  }

  function resetToSeed() {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem('dutch_learning_spaced');
    return loadAll();
  }

  return { getAll, getById, add, update, remove, exportData, importData, resetToSeed, TYPES };
})();
