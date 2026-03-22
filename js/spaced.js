const SpacedRepetition = (() => {
  const STORAGE_KEY = 'dutch_learning_spaced';
  const DEFAULT_INTERVAL = 1;       // minutes (first review very soon)
  const DEFAULT_EASE = 2.5;
  const MIN_EASE = 1.3;
  const INTERVALS = [1, 10, 1440, 4320, 10080, 20160, 43200]; // minutes: 1m, 10m, 1d, 3d, 7d, 14d, 30d

  function loadData() {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : {};
  }

  function saveData(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }

  function getWordData(wordId) {
    const data = loadData();
    return data[wordId] || null;
  }

  function recordAnswer(wordId, correct) {
    const data = loadData();
    const now = Date.now();

    if (!data[wordId]) {
      data[wordId] = {
        lastSeen: now,
        intervalIndex: 0,
        easeFactor: DEFAULT_EASE,
        correctStreak: 0,
        totalCorrect: 0,
        totalAttempts: 0
      };
    }

    const w = data[wordId];
    w.totalAttempts++;
    w.lastSeen = now;

    if (correct) {
      w.correctStreak++;
      w.totalCorrect++;
      w.easeFactor = Math.min(w.easeFactor + 0.1, 3.0);
      w.intervalIndex = Math.min(w.intervalIndex + 1, INTERVALS.length - 1);
    } else {
      w.correctStreak = 0;
      w.easeFactor = Math.max(w.easeFactor - 0.2, MIN_EASE);
      w.intervalIndex = 0; // Reset to shortest interval
    }

    saveData(data);
  }

  // Returns a priority score — higher means more urgent to review
  function getPriority(wordId) {
    const entry = getWordData(wordId);
    if (!entry) return 1000; // Never seen — highest priority

    const now = Date.now();
    const elapsed = (now - entry.lastSeen) / 60000; // minutes
    const interval = INTERVALS[entry.intervalIndex] * entry.easeFactor;

    // How overdue is this word? >1 means overdue
    const overdueRatio = elapsed / interval;

    if (overdueRatio >= 1) {
      return 100 + overdueRatio * 10; // Overdue words get high priority
    }

    return overdueRatio; // Not yet due — low priority
  }

  // Get word IDs sorted by review priority (most urgent first)
  function getNextWords(wordIds, count) {
    const scored = wordIds.map(id => ({ id, priority: getPriority(id) }));
    scored.sort((a, b) => b.priority - a.priority);
    return scored.slice(0, count).map(s => s.id);
  }

  function removeWord(wordId) {
    const data = loadData();
    delete data[wordId];
    saveData(data);
  }

  function getStats(wordId) {
    const entry = getWordData(wordId);
    if (!entry) return { seen: false };
    return {
      seen: true,
      totalAttempts: entry.totalAttempts,
      totalCorrect: entry.totalCorrect,
      accuracy: entry.totalAttempts > 0 ? Math.round(entry.totalCorrect / entry.totalAttempts * 100) : 0,
      correctStreak: entry.correctStreak,
      lastSeen: new Date(entry.lastSeen)
    };
  }

  return { recordAnswer, getPriority, getNextWords, removeWord, getStats, getWordData };
})();
