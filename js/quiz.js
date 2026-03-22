const Quiz = (() => {
  const PERSONS = ['ik', 'jij', 'u', 'hij/zij', 'wij', 'jullie', 'zij_plural'];
  const TENSES = ['present', 'past'];

  let session = null; // { mode, questions, currentIndex, results, endless, multipleChoice }

  function init() {
    renderSetup();
  }

  function renderSetup() {
    const container = document.getElementById('quiz-content');
    container.innerHTML = `
      <div class="quiz-setup">
        <h2>Start a Quiz</h2>
        <div class="form-group">
          <label>Quiz Type</label>
          <div class="quiz-type-grid">
            <label class="checkbox-card">
              <input type="checkbox" name="quiz-type" value="dutch-to-english" checked>
              <span>Dutch &rarr; English</span>
            </label>
            <label class="checkbox-card">
              <input type="checkbox" name="quiz-type" value="english-to-dutch">
              <span>English &rarr; Dutch</span>
            </label>
            <label class="checkbox-card">
              <input type="checkbox" name="quiz-type" value="de-het">
              <span>De or Het</span>
            </label>
            <label class="checkbox-card">
              <input type="checkbox" name="quiz-type" value="conjugation">
              <span>Conjugation</span>
            </label>
          </div>
        </div>
        <div class="form-group">
          <label>Answer Mode</label>
          <div class="quiz-type-grid">
            <label class="checkbox-card">
              <input type="radio" name="answer-mode" value="multiple-choice" checked>
              <span>Multiple Choice</span>
            </label>
            <label class="checkbox-card">
              <input type="radio" name="answer-mode" value="typed">
              <span>Type Answer</span>
            </label>
            <label class="checkbox-card">
              <input type="radio" name="answer-mode" value="mixed">
              <span>Mix Both</span>
            </label>
          </div>
        </div>
        <div class="form-group">
          <label>Session Length</label>
          <div class="quiz-type-grid">
            <label class="checkbox-card">
              <input type="radio" name="session-length" value="10" checked>
              <span>10 questions</span>
            </label>
            <label class="checkbox-card">
              <input type="radio" name="session-length" value="20">
              <span>20 questions</span>
            </label>
            <label class="checkbox-card">
              <input type="radio" name="session-length" value="50">
              <span>50 questions</span>
            </label>
            <label class="checkbox-card">
              <input type="radio" name="session-length" value="endless">
              <span>Endless</span>
            </label>
          </div>
        </div>
        <button class="btn btn-primary btn-lg" onclick="Quiz.start()">Start Quiz</button>
      </div>
    `;
  }

  function start() {
    const selectedTypes = [...document.querySelectorAll('input[name="quiz-type"]:checked')].map(el => el.value);
    if (selectedTypes.length === 0) {
      alert('Select at least one quiz type.');
      return;
    }

    const answerMode = document.querySelector('input[name="answer-mode"]:checked')?.value || 'multiple-choice';
    const lengthVal = document.querySelector('input[name="session-length"]:checked')?.value || '10';
    const endless = lengthVal === 'endless';
    const count = endless ? 10 : parseInt(lengthVal);

    const questions = generateQuestions(selectedTypes, count);
    if (questions.length === 0) {
      alert('Not enough words to quiz. Add more words in the Manager!');
      return;
    }

    session = {
      types: selectedTypes,
      answerMode,
      questions,
      currentIndex: 0,
      results: [],
      endless,
      totalAnswered: 0,
      totalCorrect: 0
    };

    renderQuestion();
  }

  // Should this question use multiple choice?
  function useMultipleChoice(q) {
    if (session.answerMode === 'multiple-choice') return true;
    if (session.answerMode === 'typed') return false;
    // mixed: randomly pick, but de-het is always buttons anyway
    if (q.type === 'de-het') return true;
    return Math.random() < 0.5;
  }

  // Get wrong options for multiple choice
  function getDistractors(q, count) {
    const distractors = [];
    let pool = [];

    if (q.type === 'dutch-to-english') {
      // Get other translations as wrong answers
      const allWords = [...Store.getAll('nouns'), ...Store.getAll('verbs'), ...Store.getAll('adjectives')];
      pool = allWords.filter(w => w.id !== q.wordId).map(w => w.translation);
    } else if (q.type === 'english-to-dutch') {
      const allWords = [...Store.getAll('nouns'), ...Store.getAll('verbs'), ...Store.getAll('adjectives')];
      pool = allWords.filter(w => w.id !== q.wordId).map(w => w.word);
    } else if (q.type === 'conjugation') {
      // Get other conjugations of different verbs
      const verbs = Store.getAll('verbs').filter(v =>
        v.id !== q.wordId && v.conjugations && v.conjugations[q.tense] && v.conjugations[q.tense][q.person]
      );
      pool = verbs.map(v => v.conjugations[q.tense][q.person]).filter(c => c);
    }

    // Shuffle and pick unique distractors
    shuffleArray(pool);
    const correctAnswer = getCorrectAnswer(q).toLowerCase();

    for (const item of pool) {
      if (distractors.length >= count) break;
      const itemLower = item.toLowerCase();
      if (itemLower !== correctAnswer && !distractors.some(d => d.toLowerCase() === itemLower)) {
        distractors.push(item);
      }
    }

    return distractors;
  }

  function getCorrectAnswer(q) {
    switch (q.type) {
      case 'dutch-to-english': return q.word.translation;
      case 'english-to-dutch': return q.word.word;
      case 'de-het': return q.word.article;
      case 'conjugation': return q.word.conjugations[q.tense]?.[q.person] || '';
      default: return '';
    }
  }

  function generateQuestions(types, count) {
    const questions = [];
    const allWordIds = [];

    const pools = {};

    if (types.includes('dutch-to-english') || types.includes('english-to-dutch')) {
      const nouns = Store.getAll('nouns');
      const verbs = Store.getAll('verbs');
      const adjectives = Store.getAll('adjectives');
      pools.translation = [...nouns, ...verbs, ...adjectives];
    }

    if (types.includes('de-het')) {
      pools.dehet = Store.getAll('nouns').filter(n => n.article);
    }

    if (types.includes('conjugation')) {
      pools.conjugation = Store.getAll('verbs').filter(v =>
        v.conjugations && v.conjugations.present && v.conjugations.present.ik
      );
    }

    const candidates = [];

    if (types.includes('dutch-to-english') && pools.translation) {
      for (const w of pools.translation) {
        candidates.push({ type: 'dutch-to-english', wordId: w.id, word: w });
      }
    }
    if (types.includes('english-to-dutch') && pools.translation) {
      for (const w of pools.translation) {
        candidates.push({ type: 'english-to-dutch', wordId: w.id, word: w });
      }
    }
    if (types.includes('de-het') && pools.dehet) {
      for (const w of pools.dehet) {
        candidates.push({ type: 'de-het', wordId: w.id, word: w });
      }
    }
    if (types.includes('conjugation') && pools.conjugation) {
      for (const v of pools.conjugation) {
        const person = PERSONS[Math.floor(Math.random() * PERSONS.length)];
        const tense = TENSES[Math.floor(Math.random() * TENSES.length)];
        candidates.push({ type: 'conjugation', wordId: v.id, word: v, person, tense });
      }
    }

    if (candidates.length === 0) return [];

    // Add randomness: shuffle first, then use spaced repetition to bias toward priority words
    shuffleArray(candidates);

    const wordIds = [...new Set(candidates.map(c => c.wordId))];
    const prioritized = SpacedRepetition.getNextWords(wordIds, wordIds.length);

    // Build a priority score with randomness added
    const priorityMap = {};
    prioritized.forEach((id, i) => {
      // Add random jitter so same-priority words get mixed up
      priorityMap[id] = i + Math.random() * Math.min(count, 20);
    });
    candidates.sort((a, b) => (priorityMap[a.wordId] ?? 999) - (priorityMap[b.wordId] ?? 999));

    // Pick top candidates
    const selected = candidates.slice(0, count);

    // Final shuffle so the order within a session is random
    shuffleArray(selected);

    // Mark unseen words so we can show a learn card first
    for (const q of selected) {
      const stats = SpacedRepetition.getWordData(q.wordId);
      q.isNew = !stats;
    }

    return selected;
  }

  function renderQuestion() {
    if (!session) return;

    if (session.currentIndex >= session.questions.length) {
      if (session.endless) {
        const more = generateQuestions(session.types, 10);
        if (more.length === 0) {
          renderSummary();
          return;
        }
        session.questions.push(...more);
      } else {
        renderSummary();
        return;
      }
    }

    const q = session.questions[session.currentIndex];
    const container = document.getElementById('quiz-content');
    const progress = session.endless
      ? `Question ${session.totalAnswered + 1}`
      : `Question ${session.currentIndex + 1} / ${session.questions.length}`;

    // Show learn card for new words before quizzing
    if (q.isNew && !q._learned) {
      renderLearnCard(q, progress);
      return;
    }

    const mc = useMultipleChoice(q);
    let questionHtml = '';

    switch (q.type) {
      case 'dutch-to-english':
        if (mc) {
          questionHtml = renderMCQuestion(
            'What is the English translation of:',
            q.word.word,
            null,
            q
          );
        } else {
          questionHtml = `
            <p class="quiz-prompt">What is the English translation of:</p>
            <p class="quiz-word">${esc(q.word.word)}</p>
            <input type="text" id="quiz-answer" class="quiz-input" placeholder="Type the English translation..." autofocus
              onkeydown="if(event.key==='Enter')Quiz.submitAnswer()">
          `;
        }
        break;

      case 'english-to-dutch':
        if (mc) {
          questionHtml = renderMCQuestion(
            'What is the Dutch translation of:',
            q.word.translation,
            null,
            q
          );
        } else {
          questionHtml = `
            <p class="quiz-prompt">What is the Dutch translation of:</p>
            <p class="quiz-word">${esc(q.word.translation)}</p>
            <input type="text" id="quiz-answer" class="quiz-input" placeholder="Type the Dutch word..." autofocus
              onkeydown="if(event.key==='Enter')Quiz.submitAnswer()">
          `;
        }
        break;

      case 'de-het':
        questionHtml = `
          <p class="quiz-prompt">Is it <strong>de</strong> or <strong>het</strong>?</p>
          <p class="quiz-word">${esc(q.word.word)}</p>
          <p class="quiz-hint">(${esc(q.word.translation)})</p>
          <div class="dehet-buttons">
            <button class="btn btn-lg dehet-btn" onclick="Quiz.submitDeHet('de')">de</button>
            <button class="btn btn-lg dehet-btn" onclick="Quiz.submitDeHet('het')">het</button>
          </div>
        `;
        break;

      case 'conjugation':
        if (mc) {
          questionHtml = renderMCQuestion(
            `Conjugate <strong>${esc(q.word.word)}</strong> (${esc(q.word.translation)})`,
            `${personDisplay(q.person)} ___`,
            q.tense + ' tense',
            q
          );
        } else {
          questionHtml = `
            <p class="quiz-prompt">Conjugate <strong>${esc(q.word.word)}</strong> (${esc(q.word.translation)})</p>
            <p class="quiz-word">${personDisplay(q.person)} ___</p>
            <p class="quiz-hint">${q.tense} tense</p>
            <input type="text" id="quiz-answer" class="quiz-input" placeholder="Type the conjugation..." autofocus
              onkeydown="if(event.key==='Enter')Quiz.submitAnswer()">
          `;
        }
        break;
    }

    container.innerHTML = `
      <div class="quiz-session">
        <div class="quiz-header">
          <span class="quiz-progress">${progress}</span>
          <span class="quiz-score">${session.totalCorrect} / ${session.totalAnswered} correct</span>
          ${session.endless ? '<button class="btn btn-sm" onclick="Quiz.endSession()">Stop</button>' : ''}
        </div>
        <div class="quiz-card">
          ${questionHtml}
          ${q.type !== 'de-het' && !mc ? '<button class="btn btn-primary" onclick="Quiz.submitAnswer()">Check</button>' : ''}
        </div>
      </div>
    `;

    document.getElementById('quiz-answer')?.focus();
  }

  function renderLearnCard(q, progress) {
    const container = document.getElementById('quiz-content');
    const w = q.word;

    let infoHtml = '';

    // Determine word type from ID prefix
    const wordType = w.id.startsWith('n') ? 'noun' : w.id.startsWith('v') ? 'verb' : 'adjective';

    if (wordType === 'noun') {
      infoHtml = `
        <p class="learn-label">Noun</p>
        <p class="learn-word"><span class="learn-article">${esc(w.article || '')}</span> ${esc(w.word)}</p>
        <p class="learn-translation">${esc(w.translation)}</p>
      `;
    } else if (wordType === 'verb') {
      const conj = w.conjugations || {};
      const present = conj.present || {};
      const past = conj.past || {};

      // Show a compact conjugation preview
      const previewPersons = ['ik', 'jij', 'hij/zij', 'wij'];
      let conjRows = previewPersons.map(p => {
        const pLabel = p === 'zij_plural' ? 'zij (pl.)' : p;
        return `<tr>
          <td class="person-label">${esc(pLabel)}</td>
          <td>${esc(present[p] || '-')}</td>
          <td>${esc(past[p] || '-')}</td>
        </tr>`;
      }).join('');

      infoHtml = `
        <p class="learn-label">Verb</p>
        <p class="learn-word">${esc(w.word)}</p>
        <p class="learn-translation">${esc(w.translation)}</p>
        <table class="learn-conj-table">
          <thead><tr><th></th><th>Present</th><th>Past</th></tr></thead>
          <tbody>${conjRows}</tbody>
        </table>
        ${conj.perfect ? `<p class="learn-perfect">Perfect: <strong>${esc(conj.perfect)}</strong></p>` : ''}
      `;
    } else {
      infoHtml = `
        <p class="learn-label">Adjective</p>
        <p class="learn-word">${esc(w.word)}</p>
        <p class="learn-translation">${esc(w.translation)}</p>
      `;
    }

    container.innerHTML = `
      <div class="quiz-session">
        <div class="quiz-header">
          <span class="quiz-progress">${progress}</span>
          <span class="quiz-score">${session.totalCorrect} / ${session.totalAnswered} correct</span>
          ${session.endless ? '<button class="btn btn-sm" onclick="Quiz.endSession()">Stop</button>' : ''}
        </div>
        <div class="quiz-card learn-card">
          <p class="learn-new-badge">New Word</p>
          ${infoHtml}
          <button class="btn btn-primary" onclick="Quiz.dismissLearnCard()" autofocus>Got it, quiz me!</button>
        </div>
      </div>
    `;

    container.querySelector('.btn-primary')?.focus();
  }

  function dismissLearnCard() {
    const q = session.questions[session.currentIndex];
    q._learned = true;
    renderQuestion();
  }

  function renderMCQuestion(prompt, word, hint, q) {
    const correctAnswer = getCorrectAnswer(q);
    const distractors = getDistractors(q, 3);
    const options = [correctAnswer, ...distractors];
    shuffleArray(options);

    // Store correct index for keyboard shortcuts
    q._mcOptions = options;
    q._mcCorrect = correctAnswer;

    return `
      <p class="quiz-prompt">${prompt}</p>
      <p class="quiz-word">${esc(word)}</p>
      ${hint ? `<p class="quiz-hint">${esc(hint)}</p>` : ''}
      <div class="mc-options">
        ${options.map((opt, i) => `
          <button class="btn mc-btn" onclick="Quiz.submitMC(${i})" data-index="${i}">
            <span class="mc-key">${i + 1}</span>
            ${esc(opt)}
          </button>
        `).join('')}
      </div>
    `;
  }

  function submitMC(index) {
    const q = session.questions[session.currentIndex];
    if (!q._mcOptions) return;

    const userAnswer = q._mcOptions[index];
    const correctAnswer = q._mcCorrect;
    const correct = checkAnswer(userAnswer, correctAnswer);

    // Highlight the buttons
    const buttons = document.querySelectorAll('.mc-btn');
    buttons.forEach((btn, i) => {
      btn.disabled = true;
      if (q._mcOptions[i] === correctAnswer) {
        btn.classList.add('mc-correct');
      } else if (i === index && !correct) {
        btn.classList.add('mc-wrong');
      }
    });

    // Short delay then show feedback
    setTimeout(() => {
      processResult(q, correct, userAnswer, correctAnswer);
    }, 600);
  }

  // Handle keyboard shortcuts 1-4 for MC
  document.addEventListener('keydown', (e) => {
    if (!session) return;
    const q = session.questions?.[session.currentIndex];
    if (!q?._mcOptions) return;

    const key = parseInt(e.key);
    if (key >= 1 && key <= 4 && key <= q._mcOptions.length) {
      // Check buttons aren't already disabled (already answered)
      const btn = document.querySelector(`.mc-btn[data-index="${key - 1}"]`);
      if (btn && !btn.disabled) {
        submitMC(key - 1);
      }
    }
  });

  function checkAnswer(userAnswer, correctAnswer) {
    const user = userAnswer.toLowerCase().trim();
    const correct = correctAnswer.toLowerCase().trim();

    // Exact match
    if (user === correct) return true;

    // For translations with multiple meanings like "arm; poor" or "house, home"
    // Accept if the user typed any one of them
    const meanings = correct.split(/[;,]/).map(m => m.trim().toLowerCase());
    if (meanings.includes(user)) return true;

    // Also check if user's answer is contained in any meaning
    for (const meaning of meanings) {
      if (meaning === user) return true;
    }

    return false;
  }

  function submitAnswer() {
    const input = document.getElementById('quiz-answer');
    if (!input) return;
    const answer = input.value.trim();
    if (!answer) return;

    const q = session.questions[session.currentIndex];
    const correctAnswer = getCorrectAnswer(q);
    const correct = checkAnswer(answer, correctAnswer);

    processResult(q, correct, answer, correctAnswer);
  }

  function submitDeHet(answer) {
    const q = session.questions[session.currentIndex];
    const correctAnswer = q.word.article;
    const correct = answer === correctAnswer;
    processResult(q, correct, answer, correctAnswer);
  }

  function processResult(q, correct, userAnswer, correctAnswer) {
    session.totalAnswered++;
    if (correct) session.totalCorrect++;

    session.results.push({ question: q, correct, userAnswer, correctAnswer });
    SpacedRepetition.recordAnswer(q.wordId, correct);

    // If wrong, re-add a similar question later
    if (!correct) {
      const retry = { ...q };
      delete retry._mcOptions;
      delete retry._mcCorrect;
      if (q.type === 'conjugation') {
        retry.person = PERSONS[Math.floor(Math.random() * PERSONS.length)];
        retry.tense = TENSES[Math.floor(Math.random() * TENSES.length)];
      }
      const insertAt = Math.min(session.currentIndex + 3 + Math.floor(Math.random() * 3), session.questions.length);
      session.questions.splice(insertAt, 0, retry);
    }

    showFeedback(correct, userAnswer, correctAnswer, q);
  }

  function showFeedback(correct, userAnswer, correctAnswer, q) {
    const container = document.getElementById('quiz-content');
    const feedbackClass = correct ? 'feedback-correct' : 'feedback-wrong';
    const icon = correct ? '&#10003;' : '&#10007;';

    let detail = '';
    if (!correct) {
      if (q.type === 'de-het') {
        detail = `<p>It's <strong>${correctAnswer} ${esc(q.word.word)}</strong></p>`;
      } else if (q.type === 'conjugation') {
        detail = `<p>Correct: <strong>${esc(correctAnswer)}</strong></p>
                  <p>${personDisplay(q.person)} ${esc(correctAnswer)} (${q.tense})</p>`;
      } else {
        detail = `<p>Correct answer: <strong>${esc(correctAnswer)}</strong></p>`;
      }
    }

    container.innerHTML = `
      <div class="quiz-session">
        <div class="quiz-header">
          <span class="quiz-score">${session.totalCorrect} / ${session.totalAnswered} correct</span>
        </div>
        <div class="quiz-card ${feedbackClass}">
          <p class="feedback-icon">${icon}</p>
          <p class="feedback-text">${correct ? 'Correct!' : 'Wrong!'}</p>
          ${detail}
          <button class="btn btn-primary" onclick="Quiz.nextQuestion()" autofocus>Continue</button>
        </div>
      </div>
    `;

    container.querySelector('.btn-primary')?.focus();
  }

  function nextQuestion() {
    session.currentIndex++;
    renderQuestion();
  }

  function endSession() {
    renderSummary();
  }

  function renderSummary() {
    const container = document.getElementById('quiz-content');
    const pct = session.totalAnswered > 0 ? Math.round(session.totalCorrect / session.totalAnswered * 100) : 0;

    const mistakes = session.results.filter(r => !r.correct);
    let mistakesList = '';
    if (mistakes.length > 0) {
      const seen = new Set();
      const unique = mistakes.filter(m => {
        if (seen.has(m.question.wordId + m.question.type)) return false;
        seen.add(m.question.wordId + m.question.type);
        return true;
      });

      mistakesList = `
        <h3>Words to Review</h3>
        <table class="word-table">
          <thead><tr><th>Type</th><th>Word</th><th>Your Answer</th><th>Correct</th></tr></thead>
          <tbody>${unique.map(m => `
            <tr>
              <td>${quizTypeLabel(m.question.type)}</td>
              <td>${esc(m.question.word.word)}</td>
              <td class="wrong-answer">${esc(m.userAnswer)}</td>
              <td>${esc(m.correctAnswer)}</td>
            </tr>
          `).join('')}</tbody>
        </table>
      `;
    }

    container.innerHTML = `
      <div class="quiz-summary">
        <h2>Quiz Complete!</h2>
        <div class="score-display">
          <span class="score-number">${pct}%</span>
          <span class="score-detail">${session.totalCorrect} correct out of ${session.totalAnswered}</span>
        </div>
        ${mistakesList}
        <div class="summary-actions">
          <button class="btn btn-primary btn-lg" onclick="Quiz.init()">New Quiz</button>
        </div>
      </div>
    `;

    session = null;
  }

  function quizTypeLabel(type) {
    const labels = {
      'dutch-to-english': 'NL &rarr; EN',
      'english-to-dutch': 'EN &rarr; NL',
      'de-het': 'De/Het',
      'conjugation': 'Conjugation'
    };
    return labels[type] || type;
  }

  function personDisplay(p) {
    if (p === 'zij_plural') return 'zij (plural)';
    return p;
  }

  function esc(s) {
    if (!s) return '';
    return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  function shuffleArray(arr) {
    for (let i = arr.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [arr[i], arr[j]] = [arr[j], arr[i]];
    }
  }

  return { init, start, submitAnswer, submitDeHet, submitMC, nextQuestion, endSession, dismissLearnCard, renderSetup };
})();
