const Progress = (() => {
  let currentFilter = 'all'; // all, mastered, learning, new

  function init() {
    render();
  }

  function render() {
    const container = document.getElementById('progress-content');

    const allWords = [
      ...Store.getAll('nouns').map(w => ({ ...w, wordType: 'noun' })),
      ...Store.getAll('verbs').map(w => ({ ...w, wordType: 'verb' })),
      ...Store.getAll('adjectives').map(w => ({ ...w, wordType: 'adjective' }))
    ];

    // Categorize words by mastery level
    const mastered = []; // 5+ correct streak, 80%+ accuracy
    const learning = []; // seen but not mastered
    const unseen = [];   // never quizzed

    for (const word of allWords) {
      const stats = SpacedRepetition.getStats(word.id);
      if (!stats.seen) {
        unseen.push({ word, stats });
      } else if (stats.correctStreak >= 5 && stats.accuracy >= 80) {
        mastered.push({ word, stats });
      } else {
        learning.push({ word, stats });
      }
    }

    const total = allWords.length;
    const masteredPct = total > 0 ? Math.round(mastered.length / total * 100) : 0;
    const learningPct = total > 0 ? Math.round(learning.length / total * 100) : 0;
    const unseenPct = total > 0 ? Math.round(unseen.length / total * 100) : 0;

    // Overall accuracy
    let totalAttempts = 0, totalCorrect = 0;
    for (const word of allWords) {
      const stats = SpacedRepetition.getStats(word.id);
      if (stats.seen) {
        totalAttempts += stats.totalAttempts;
        totalCorrect += Math.round(stats.accuracy * stats.totalAttempts / 100);
      }
    }
    const overallAccuracy = totalAttempts > 0 ? Math.round(totalCorrect / totalAttempts * 100) : 0;

    // Determine which list to show
    let displayList = [];
    let listTitle = '';
    switch (currentFilter) {
      case 'mastered':
        displayList = mastered;
        listTitle = `Mastered Words (${mastered.length})`;
        break;
      case 'learning':
        displayList = learning;
        listTitle = `Learning (${learning.length})`;
        break;
      case 'new':
        displayList = unseen;
        listTitle = `Not Yet Seen (${unseen.length})`;
        break;
      default:
        displayList = [...mastered, ...learning];
        listTitle = `All Practiced Words (${mastered.length + learning.length})`;
        break;
    }

    // Sort: mastered first, then by accuracy desc
    displayList.sort((a, b) => {
      if (a.stats.seen && !b.stats.seen) return -1;
      if (!a.stats.seen && b.stats.seen) return 1;
      return (b.stats.accuracy || 0) - (a.stats.accuracy || 0);
    });

    container.innerHTML = `
      <div class="progress-dashboard">
        <h2>Your Progress</h2>

        <div class="progress-stats">
          <div class="stat-card">
            <span class="stat-value">${total}</span>
            <span class="stat-label">Total Words</span>
          </div>
          <div class="stat-card">
            <span class="stat-value" style="color: var(--success)">${mastered.length}</span>
            <span class="stat-label">Mastered</span>
          </div>
          <div class="stat-card">
            <span class="stat-value" style="color: #f39c12">${learning.length}</span>
            <span class="stat-label">Learning</span>
          </div>
          <div class="stat-card">
            <span class="stat-value" style="color: var(--text-muted)">${unseen.length}</span>
            <span class="stat-label">Not Seen</span>
          </div>
          <div class="stat-card">
            <span class="stat-value">${overallAccuracy}%</span>
            <span class="stat-label">Accuracy</span>
          </div>
        </div>

        <div class="progress-bar-container">
          <div class="progress-bar-label">
            <span>Overall Progress</span>
            <span>${masteredPct}% mastered</span>
          </div>
          <div class="progress-bar-track">
            <div style="display: flex; height: 100%;">
              <div class="progress-bar-fill mastered" style="width: ${masteredPct}%"></div>
              <div class="progress-bar-fill learning" style="width: ${learningPct}%"></div>
            </div>
          </div>
          <div style="display: flex; gap: 1rem; margin-top: 0.5rem; font-size: 0.75rem; color: var(--text-muted);">
            <span style="color: var(--success);">&#9632; Mastered ${masteredPct}%</span>
            <span style="color: #f39c12;">&#9632; Learning ${learningPct}%</span>
            <span>&#9632; New ${unseenPct}%</span>
          </div>
        </div>

        ${renderTypeBreakdown(allWords)}

        <div class="mastered-list">
          <h3>Word List</h3>
          <div class="mastery-filter">
            <button class="btn btn-sm ${currentFilter === 'all' ? 'btn-primary' : ''}" onclick="Progress.setFilter('all')">All Practiced</button>
            <button class="btn btn-sm ${currentFilter === 'mastered' ? 'btn-primary' : ''}" onclick="Progress.setFilter('mastered')">Mastered</button>
            <button class="btn btn-sm ${currentFilter === 'learning' ? 'btn-primary' : ''}" onclick="Progress.setFilter('learning')">Learning</button>
            <button class="btn btn-sm ${currentFilter === 'new' ? 'btn-primary' : ''}" onclick="Progress.setFilter('new')">Not Seen</button>
          </div>

          ${displayList.length > 0 ? `
            <table class="word-table">
              <thead><tr>
                <th>Word</th>
                <th>Translation</th>
                <th>Type</th>
                <th>Accuracy</th>
                <th>Streak</th>
                <th>Status</th>
              </tr></thead>
              <tbody>${displayList.slice(0, 100).map(({ word: w, stats: s }) => {
                const status = !s.seen ? 'new' : (s.correctStreak >= 5 && s.accuracy >= 80) ? 'mastered' : 'learning';
                const statusBadge = status === 'mastered'
                  ? '<span class="badge badge-ok">Mastered</span>'
                  : status === 'learning'
                  ? '<span class="badge" style="background:rgba(243,156,18,0.2);color:#f39c12;">Learning</span>'
                  : '<span class="badge" style="background:rgba(138,138,154,0.2);color:var(--text-muted);">New</span>';
                return `<tr>
                  <td>${esc(w.word)}</td>
                  <td>${esc(w.translation)}</td>
                  <td>${w.wordType}</td>
                  <td>${s.seen ? s.accuracy + '%' : '-'}</td>
                  <td>${s.seen ? s.correctStreak : '-'}</td>
                  <td>${statusBadge}</td>
                </tr>`;
              }).join('')}</tbody>
            </table>
            ${displayList.length > 100 ? `<p style="color: var(--text-muted); margin-top: 0.5rem; font-size: 0.85rem;">Showing first 100 of ${displayList.length} words</p>` : ''}
          ` : `<p class="empty-msg">No words in this category yet. Start quizzing!</p>`}
        </div>
      </div>
    `;
  }

  function renderTypeBreakdown(allWords) {
    const types = ['noun', 'verb', 'adjective'];
    const rows = types.map(type => {
      const words = allWords.filter(w => w.wordType === type);
      const total = words.length;
      let mastered = 0, learning = 0;
      for (const w of words) {
        const s = SpacedRepetition.getStats(w.id);
        if (s.seen) {
          if (s.correctStreak >= 5 && s.accuracy >= 80) mastered++;
          else learning++;
        }
      }
      const pct = total > 0 ? Math.round(mastered / total * 100) : 0;
      const learnPct = total > 0 ? Math.round(learning / total * 100) : 0;
      const label = type.charAt(0).toUpperCase() + type.slice(1) + 's';
      return `
        <div class="progress-bar-container" style="padding: 0.75rem 1.25rem;">
          <div class="progress-bar-label">
            <span>${label}</span>
            <span>${mastered} / ${total} mastered</span>
          </div>
          <div class="progress-bar-track" style="height: 8px;">
            <div style="display: flex; height: 100%;">
              <div class="progress-bar-fill mastered" style="width: ${pct}%"></div>
              <div class="progress-bar-fill learning" style="width: ${learnPct}%"></div>
            </div>
          </div>
        </div>
      `;
    });
    return rows.join('');
  }

  function setFilter(filter) {
    currentFilter = filter;
    render();
  }

  function esc(s) {
    if (!s) return '';
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  return { init, render, setFilter };
})();
