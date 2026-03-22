const Quiz = (() => {
  const PERSONS = ['ik', 'jij', 'u', 'hij/zij', 'wij', 'jullie', 'zij_plural'];
  const TENSES = ['present', 'past'];

  let session = null; // { mode, questions, currentIndex, results, endless }

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
              <span>Dutch → English</span>
            </label>
            <label class="checkbox-card">
              <input type="checkbox" name="quiz-type" value="english-to-dutch">
              <span>English → Dutch</span>
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

    const lengthVal = document.querySelector('input[name="session-length"]:checked')?.value || '10';
    const endless = lengthVal === 'endless';
    const count = endless ? 10 : parseInt(lengthVal); // For endless, generate 10 at a time

    const questions = generateQuestions(selectedTypes, count);
    if (questions.length === 0) {
      alert('Not enough words to quiz. Add more words in the Manager!');
      return;
    }

    session = {
      types: selectedTypes,
      questions,
      currentIndex: 0,
      results: [],
      endless,
      totalAnswered: 0,
      totalCorrect: 0
    };

    renderQuestion();
  }

  function generateQuestions(types, count) {
    const questions = [];
    const allWordIds = [];

    // Collect eligible word IDs per type
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

    // Build candidate questions
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
        // Create a question for a random person+tense combo
        const person = PERSONS[Math.floor(Math.random() * PERSONS.length)];
        const tense = TENSES[Math.floor(Math.random() * TENSES.length)];
        candidates.push({ type: 'conjugation', wordId: v.id, word: v, person, tense });
      }
    }

    if (candidates.length === 0) return [];

    // Prioritize by spaced repetition
    const wordIds = [...new Set(candidates.map(c => c.wordId))];
    const prioritized = SpacedRepetition.getNextWords(wordIds, wordIds.length);

    // Sort candidates by priority order
    const priorityMap = {};
    prioritized.forEach((id, i) => priorityMap[id] = i);
    candidates.sort((a, b) => (priorityMap[a.wordId] ?? 999) - (priorityMap[b.wordId] ?? 999));

    // Pick top N, but add some randomness within priority tiers
    const selected = candidates.slice(0, count * 2);
    shuffleArray(selected);
    return selected.slice(0, count);
  }

  function renderQuestion() {
    if (!session) return;

    if (session.currentIndex >= session.questions.length) {
      if (session.endless) {
        // Generate more questions
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

    let questionHtml = '';

    switch (q.type) {
      case 'dutch-to-english':
        questionHtml = `
          <p class="quiz-prompt">What is the English translation of:</p>
          <p class="quiz-word">${esc(q.word.word)}</p>
          <input type="text" id="quiz-answer" class="quiz-input" placeholder="Type the English translation..." autofocus
            onkeydown="if(event.key==='Enter')Quiz.submitAnswer()">
        `;
        break;

      case 'english-to-dutch':
        questionHtml = `
          <p class="quiz-prompt">What is the Dutch translation of:</p>
          <p class="quiz-word">${esc(q.word.translation)}</p>
          <input type="text" id="quiz-answer" class="quiz-input" placeholder="Type the Dutch word..." autofocus
            onkeydown="if(event.key==='Enter')Quiz.submitAnswer()">
        `;
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
        questionHtml = `
          <p class="quiz-prompt">Conjugate <strong>${esc(q.word.word)}</strong> (${esc(q.word.translation)})</p>
          <p class="quiz-word">${personDisplay(q.person)} ___</p>
          <p class="quiz-hint">${q.tense} tense</p>
          <input type="text" id="quiz-answer" class="quiz-input" placeholder="Type the conjugation..." autofocus
            onkeydown="if(event.key==='Enter')Quiz.submitAnswer()">
        `;
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
          ${q.type !== 'de-het' ? '<button class="btn btn-primary" onclick="Quiz.submitAnswer()">Check</button>' : ''}
        </div>
      </div>
    `;

    document.getElementById('quiz-answer')?.focus();
  }

  function submitAnswer() {
    const input = document.getElementById('quiz-answer');
    if (!input) return;
    const answer = input.value.trim();
    if (!answer) return;

    const q = session.questions[session.currentIndex];
    let correct = false;
    let correctAnswer = '';

    switch (q.type) {
      case 'dutch-to-english':
        correctAnswer = q.word.translation;
        correct = answer.toLowerCase() === correctAnswer.toLowerCase();
        break;
      case 'english-to-dutch':
        correctAnswer = q.word.word;
        correct = answer.toLowerCase() === correctAnswer.toLowerCase();
        break;
      case 'conjugation':
        correctAnswer = q.word.conjugations[q.tense]?.[q.person] || '';
        correct = answer.toLowerCase() === correctAnswer.toLowerCase();
        break;
    }

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

    // If wrong and not endless, re-add a similar question later
    if (!correct) {
      const retry = { ...q };
      if (q.type === 'conjugation') {
        retry.person = PERSONS[Math.floor(Math.random() * PERSONS.length)];
        retry.tense = TENSES[Math.floor(Math.random() * TENSES.length)];
      }
      // Insert retry 3-5 questions later
      const insertAt = Math.min(session.currentIndex + 3 + Math.floor(Math.random() * 3), session.questions.length);
      session.questions.splice(insertAt, 0, retry);
    }

    showFeedback(correct, userAnswer, correctAnswer, q);
  }

  function showFeedback(correct, userAnswer, correctAnswer, q) {
    const container = document.getElementById('quiz-content');
    const feedbackClass = correct ? 'feedback-correct' : 'feedback-wrong';
    const icon = correct ? '✓' : '✗';

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

    // Auto-focus the continue button
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
      // Deduplicate by wordId
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
      'dutch-to-english': 'NL → EN',
      'english-to-dutch': 'EN → NL',
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

  return { init, start, submitAnswer, submitDeHet, nextQuestion, endSession, renderSetup };
})();
