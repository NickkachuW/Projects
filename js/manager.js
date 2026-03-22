const Manager = (() => {
  const PERSONS = ['ik', 'jij', 'u', 'hij/zij', 'wij', 'jullie', 'zij_plural'];
  const TENSES = ['present', 'past'];
  let currentTab = 'nouns';
  let searchQuery = '';

  function init() {
    render();
  }

  function render() {
    const container = document.getElementById('manager-content');
    container.innerHTML = `
      <div class="manager-tabs">
        ${['nouns', 'verbs', 'adjectives'].map(t => `
          <button class="tab-btn ${currentTab === t ? 'active' : ''}" onclick="Manager.switchTab('${t}')">${capitalize(t)}</button>
        `).join('')}
      </div>
      <div class="manager-toolbar">
        <input type="text" id="search-input" placeholder="Search..." value="${searchQuery}" oninput="Manager.onSearch(this.value)">
        <button class="btn btn-primary" onclick="Manager.showAddForm()">+ Add ${capitalize(currentTab.slice(0, -1))}</button>
      </div>
      <div id="word-list"></div>
      <div id="word-form-modal" class="modal hidden"></div>
    `;
    renderList();
  }

  function switchTab(tab) {
    currentTab = tab;
    searchQuery = '';
    render();
  }

  function onSearch(query) {
    searchQuery = query.toLowerCase();
    renderList();
  }

  function renderList() {
    const items = Store.getAll(currentTab).filter(w =>
      !searchQuery ||
      w.word.toLowerCase().includes(searchQuery) ||
      w.translation.toLowerCase().includes(searchQuery)
    );

    const listEl = document.getElementById('word-list');

    if (items.length === 0) {
      listEl.innerHTML = '<p class="empty-msg">No words found. Add some!</p>';
      return;
    }

    if (currentTab === 'nouns') {
      listEl.innerHTML = renderNounTable(items);
    } else if (currentTab === 'verbs') {
      listEl.innerHTML = renderVerbTable(items);
    } else {
      listEl.innerHTML = renderAdjectiveTable(items);
    }
  }

  function renderNounTable(items) {
    return `<table class="word-table">
      <thead><tr><th>Article</th><th>Dutch</th><th>English</th><th>Actions</th></tr></thead>
      <tbody>${items.map(w => `
        <tr>
          <td><span class="article ${w.article || 'none'}">${w.article || '—'}</span></td>
          <td>${esc(w.word)}</td>
          <td>${esc(w.translation)}</td>
          <td class="actions">
            <button class="btn btn-sm" onclick="Manager.editWord('${w.id}')">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="Manager.deleteWord('${w.id}')">Delete</button>
          </td>
        </tr>
      `).join('')}</tbody>
    </table>`;
  }

  function renderVerbTable(items) {
    return `<table class="word-table">
      <thead><tr><th>Dutch</th><th>English</th><th>Conjugated</th><th>Actions</th></tr></thead>
      <tbody>${items.map(w => {
        const hasConj = w.conjugations && w.conjugations.present && w.conjugations.present.ik;
        return `
        <tr>
          <td>${esc(w.word)}</td>
          <td>${esc(w.translation)}</td>
          <td>${hasConj ? '<span class="badge badge-ok">Yes</span>' : '<span class="badge badge-missing">No</span>'}</td>
          <td class="actions">
            <button class="btn btn-sm" onclick="Manager.editWord('${w.id}')">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="Manager.deleteWord('${w.id}')">Delete</button>
          </td>
        </tr>`;
      }).join('')}</tbody>
    </table>`;
  }

  function renderAdjectiveTable(items) {
    return `<table class="word-table">
      <thead><tr><th>Dutch</th><th>English</th><th>Actions</th></tr></thead>
      <tbody>${items.map(w => `
        <tr>
          <td>${esc(w.word)}</td>
          <td>${esc(w.translation)}</td>
          <td class="actions">
            <button class="btn btn-sm" onclick="Manager.editWord('${w.id}')">Edit</button>
            <button class="btn btn-sm btn-danger" onclick="Manager.deleteWord('${w.id}')">Delete</button>
          </td>
        </tr>
      `).join('')}</tbody>
    </table>`;
  }

  function showAddForm() {
    showForm(null);
  }

  function editWord(id) {
    const word = Store.getById(currentTab, id);
    if (word) showForm(word);
  }

  function showForm(existing) {
    const modal = document.getElementById('word-form-modal');
    const isEdit = !!existing;
    const title = isEdit ? `Edit ${capitalize(currentTab.slice(0, -1))}` : `Add ${capitalize(currentTab.slice(0, -1))}`;

    let formFields = '';

    if (currentTab === 'nouns') {
      formFields = `
        <div class="form-group">
          <label>Dutch word</label>
          <input type="text" id="form-word" value="${esc(existing?.word || '')}">
        </div>
        <div class="form-group">
          <label>English translation</label>
          <input type="text" id="form-translation" value="${esc(existing?.translation || '')}">
        </div>
        <div class="form-group">
          <label>Article</label>
          <div class="article-picker">
            <button class="btn article-btn ${existing?.article === 'de' ? 'active' : ''}" onclick="Manager.pickArticle('de')" id="art-de">de</button>
            <button class="btn article-btn ${existing?.article === 'het' ? 'active' : ''}" onclick="Manager.pickArticle('het')" id="art-het">het</button>
          </div>
        </div>
      `;
    } else if (currentTab === 'verbs') {
      const conj = existing?.conjugations || { present: {}, past: {}, perfect: '' };
      formFields = `
        <div class="form-group">
          <label>Dutch infinitive</label>
          <input type="text" id="form-word" value="${esc(existing?.word || '')}">
        </div>
        <div class="form-group">
          <label>English translation</label>
          <input type="text" id="form-translation" value="${esc(existing?.translation || '')}">
        </div>
        <div class="form-group">
          <label>Conjugations</label>
          <div class="conj-grid">
            <table class="conj-table">
              <thead><tr><th>Person</th><th>Present</th><th>Past</th></tr></thead>
              <tbody>
                ${PERSONS.map(p => `
                  <tr>
                    <td class="person-label">${personDisplay(p)}</td>
                    <td><input type="text" class="conj-input" data-tense="present" data-person="${p}" value="${esc(conj.present?.[p] || '')}"></td>
                    <td><input type="text" class="conj-input" data-tense="past" data-person="${p}" value="${esc(conj.past?.[p] || '')}"></td>
                  </tr>
                `).join('')}
              </tbody>
            </table>
          </div>
        </div>
        <div class="form-group">
          <label>Perfect participle (voltooid deelwoord)</label>
          <input type="text" id="form-perfect" value="${esc(conj.perfect || '')}">
        </div>
      `;
    } else {
      formFields = `
        <div class="form-group">
          <label>Dutch word</label>
          <input type="text" id="form-word" value="${esc(existing?.word || '')}">
        </div>
        <div class="form-group">
          <label>English translation</label>
          <input type="text" id="form-translation" value="${esc(existing?.translation || '')}">
        </div>
      `;
    }

    modal.innerHTML = `
      <div class="modal-backdrop" onclick="Manager.closeForm()"></div>
      <div class="modal-content">
        <h3>${title}</h3>
        ${formFields}
        <div class="form-actions">
          <button class="btn" onclick="Manager.closeForm()">Cancel</button>
          <button class="btn btn-primary" onclick="Manager.saveForm('${existing?.id || ''}')">${isEdit ? 'Save' : 'Add'}</button>
        </div>
      </div>
    `;
    modal.classList.remove('hidden');
    modal.querySelector('#form-word')?.focus();
  }

  let selectedArticle = null;

  function pickArticle(art) {
    selectedArticle = art;
    document.getElementById('art-de').classList.toggle('active', art === 'de');
    document.getElementById('art-het').classList.toggle('active', art === 'het');
  }

  function saveForm(existingId) {
    const word = document.getElementById('form-word')?.value.trim();
    const translation = document.getElementById('form-translation')?.value.trim();

    if (!word || !translation) {
      alert('Please fill in both the Dutch word and English translation.');
      return;
    }

    if (currentTab === 'nouns') {
      const article = selectedArticle || (existingId ? Store.getById('nouns', existingId)?.article : null);
      const item = { word, translation, article };
      if (existingId) {
        Store.update('nouns', existingId, item);
      } else {
        Store.add('nouns', item);
      }
    } else if (currentTab === 'verbs') {
      const conjugations = { present: {}, past: {}, perfect: '' };
      document.querySelectorAll('.conj-input').forEach(input => {
        const tense = input.dataset.tense;
        const person = input.dataset.person;
        conjugations[tense][person] = input.value.trim();
      });
      conjugations.perfect = document.getElementById('form-perfect')?.value.trim() || '';
      const item = { word, translation, conjugations };
      if (existingId) {
        Store.update('verbs', existingId, item);
      } else {
        Store.add('verbs', item);
      }
    } else {
      const item = { word, translation };
      if (existingId) {
        Store.update('adjectives', existingId, item);
      } else {
        Store.add('adjectives', item);
      }
    }

    selectedArticle = null;
    closeForm();
    renderList();
  }

  function closeForm() {
    const modal = document.getElementById('word-form-modal');
    modal.classList.add('hidden');
    modal.innerHTML = '';
    selectedArticle = null;
  }

  function deleteWord(id) {
    if (!confirm('Delete this word?')) return;
    Store.remove(currentTab, id);
    renderList();
  }

  function personDisplay(p) {
    if (p === 'zij_plural') return 'zij (plural)';
    return p;
  }

  function capitalize(s) {
    return s.charAt(0).toUpperCase() + s.slice(1);
  }

  function esc(s) {
    if (!s) return '';
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  return { init, render, switchTab, onSearch, showAddForm, editWord, showForm, pickArticle, saveForm, closeForm, deleteWord };
})();
