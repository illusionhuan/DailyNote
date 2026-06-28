---
title: 每日测试
date: 2026-06-28
type: "quiz"
top_img: /DailyNote/images/landscape3.jpg
aside: false
---

<div id="quiz-container">
  <div id="quiz-select" class="quiz-screen">
    <div class="quiz-tabs">
      <button class="quiz-tab quiz-tab-active" data-tab="bank">题库</button>
      <button class="quiz-tab" data-tab="notebook">错题本 <span id="quiz-notebook-badge" class="quiz-tab-badge" style="display:none">0</span></button>
    </div>
    <div id="quiz-tab-bank" class="quiz-tab-panel">
      <div class="quiz-select-header">
        <h2>选择题库</h2>
        <p>根据文章内容出题，检验你的学习成果</p>
      </div>
      <div id="quiz-cards" class="quiz-cards"></div>
    </div>
    <div id="quiz-tab-notebook" class="quiz-tab-panel" style="display:none">
      <div class="quiz-select-header">
        <h2>错题本</h2>
        <p>答错的题目会自动收录，掌握后可移除</p>
      </div>
      <div id="quiz-notebook-list" class="quiz-notebook-list"></div>
    </div>
  </div>
  <div id="quiz-questions" class="quiz-screen" style="display:none">
    <div class="quiz-header">
      <button id="quiz-back-btn" class="quiz-back-btn">← 返回列表</button>
      <div class="quiz-progress-wrap">
        <div class="quiz-progress-bar">
          <div id="quiz-progress-fill" class="quiz-progress-fill"></div>
        </div>
        <span id="quiz-progress-text" class="quiz-progress-text">0/0</span>
      </div>
    </div>
    <div class="quiz-body">
      <div id="quiz-article-link" class="quiz-article-link"></div>
      <div id="quiz-question-text" class="quiz-question-text"></div>
      <div id="quiz-options" class="quiz-options"></div>
      <div id="quiz-feedback" class="quiz-feedback" style="display:none"></div>
    </div>
    <div class="quiz-nav">
      <button id="quiz-prev-btn" class="quiz-nav-btn">上一题</button>
      <button id="quiz-next-btn" class="quiz-nav-btn quiz-nav-btn-primary">下一题</button>
    </div>
  </div>
  <div id="quiz-result" class="quiz-screen" style="display:none">
    <div class="quiz-result-card">
      <div class="quiz-result-icon" id="quiz-result-icon"></div>
      <h2 id="quiz-result-title" class="quiz-result-title"></h2>
      <div class="quiz-result-score">
        <span id="quiz-result-correct" class="quiz-result-num"></span>
        <span class="quiz-result-sep">/</span>
        <span id="quiz-result-total" class="quiz-result-num"></span>
      </div>
      <div class="quiz-result-rate-wrap">
        <div class="quiz-result-rate-bar">
          <div id="quiz-result-rate-fill" class="quiz-result-rate-fill"></div>
        </div>
        <span id="quiz-result-rate" class="quiz-result-rate"></span>
      </div>
      <p id="quiz-result-comment" class="quiz-result-comment"></p>
      <div class="quiz-result-actions">
        <button id="quiz-retry-btn" class="quiz-result-btn">重新答题</button>
        <button id="quiz-home-btn" class="quiz-result-btn quiz-result-btn-outline">返回列表</button>
      </div>
    </div>
  </div>
</div>

<style>
/* ===== Tab 切换 ===== */
.quiz-tabs {
  display: flex;
  justify-content: center;
  gap: 0;
  margin-bottom: 28px;
  border-bottom: 2px solid rgba(124, 171, 186, 0.15);
}
.quiz-tab {
  background: none;
  border: none;
  padding: 10px 28px;
  font-size: 1rem;
  font-weight: 600;
  color: var(--second-font-color, #888);
  cursor: pointer;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  transition: all 0.25s;
  position: relative;
}
.quiz-tab:hover {
  color: #7CABBA;
}
.quiz-tab-active {
  color: #7CABBA;
  border-bottom-color: #7CABBA;
}
.quiz-tab-badge {
  display: inline-block;
  background: #ef5350;
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 1px 7px;
  border-radius: 10px;
  margin-left: 4px;
  vertical-align: middle;
  min-width: 18px;
  text-align: center;
}

/* ===== 选择界面 ===== */
.quiz-select-header {
  text-align: center;
  margin-bottom: 30px;
}
.quiz-select-header h2 {
  font-size: 1.6rem;
  color: var(--font-color, #333);
  margin-bottom: 8px;
}
.quiz-select-header p {
  color: var(--second-font-color, #888);
  font-size: 0.95rem;
}
.quiz-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  max-width: 900px;
  margin: 0 auto;
}
.quiz-card {
  background: var(--card-bg, #fff);
  border: 1px solid rgba(124, 171, 186, 0.2);
  border-radius: 12px;
  padding: 24px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
  position: relative;
  overflow: hidden;
}
.quiz-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(124, 171, 186, 0.2);
  border-color: #7CABBA;
}
.quiz-card-category {
  display: inline-block;
  padding: 2px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #fff;
  margin-bottom: 12px;
  background: linear-gradient(135deg, #7CABBA, #5A8C9C);
}
.quiz-card-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--font-color, #333);
  margin-bottom: 10px;
}
.quiz-card-count {
  color: var(--second-font-color, #888);
  font-size: 0.85rem;
}
.quiz-card-count::before {
  content: "\1F4DD ";
}

/* ===== 错题本列表 ===== */
.quiz-notebook-list {
  max-width: 800px;
  margin: 0 auto;
}
.quiz-notebook-empty {
  text-align: center;
  color: var(--second-font-color, #999);
  padding: 40px 20px;
  font-size: 0.95rem;
}
.quiz-notebook-empty::before {
  content: "\1F389 ";
}
.quiz-notebook-item {
  background: var(--card-bg, #fff);
  border: 1px solid rgba(124, 171, 186, 0.15);
  border-radius: 10px;
  padding: 18px 20px;
  margin-bottom: 12px;
  transition: all 0.2s;
}
.quiz-notebook-item:hover {
  border-color: rgba(124, 171, 186, 0.4);
}
.quiz-notebook-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  flex-wrap: wrap;
}
.quiz-notebook-cat {
  display: inline-block;
  padding: 1px 10px;
  border-radius: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #7CABBA, #5A8C9C);
}
.quiz-notebook-title {
  font-size: 0.8rem;
  color: var(--second-font-color, #999);
}
.quiz-notebook-q {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--font-color, #333);
  margin-bottom: 10px;
  line-height: 1.5;
}
.quiz-notebook-answers {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 10px;
}
.quiz-notebook-ans {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.85rem;
  padding: 6px 10px;
  border-radius: 6px;
  line-height: 1.4;
}
.quiz-notebook-ans-wrong {
  background: rgba(239, 83, 80, 0.08);
  color: #c62828;
}
.quiz-notebook-ans-correct {
  background: rgba(76, 175, 80, 0.08);
  color: #2e7d32;
}
.quiz-notebook-ans-label {
  font-weight: 700;
  flex-shrink: 0;
  width: 20px;
}
.quiz-notebook-explanation {
  font-size: 0.83rem;
  color: var(--second-font-color, #888);
  line-height: 1.5;
  margin-bottom: 12px;
  padding-left: 12px;
  border-left: 3px solid rgba(124, 171, 186, 0.3);
}
.quiz-notebook-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}
.quiz-notebook-btn {
  padding: 5px 14px;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid;
}
.quiz-notebook-btn-master {
  background: rgba(76, 175, 80, 0.1);
  border-color: rgba(76, 175, 80, 0.3);
  color: #2e7d32;
}
.quiz-notebook-btn-master:hover {
  background: rgba(76, 175, 80, 0.2);
}
.quiz-notebook-btn-retry {
  background: rgba(124, 171, 186, 0.1);
  border-color: rgba(124, 171, 186, 0.3);
  color: #5A8C9C;
}
.quiz-notebook-btn-retry:hover {
  background: rgba(124, 171, 186, 0.2);
}

/* ===== 答题界面 ===== */
.quiz-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}
.quiz-back-btn {
  background: none;
  border: 1px solid var(--second-font-color, #aaa);
  color: var(--second-font-color, #888);
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
  white-space: nowrap;
}
.quiz-back-btn:hover {
  border-color: #7CABBA;
  color: #7CABBA;
}
.quiz-progress-wrap {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}
.quiz-progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(124, 171, 186, 0.15);
  border-radius: 4px;
  overflow: hidden;
}
.quiz-progress-fill {
  height: 100%;
  width: 0%;
  background: linear-gradient(90deg, #7CABBA, #5A8C9C);
  border-radius: 4px;
  transition: width 0.4s ease;
}
.quiz-progress-text {
  font-size: 0.85rem;
  color: var(--second-font-color, #888);
  white-space: nowrap;
}

.quiz-article-link {
  margin-bottom: 16px;
}
.quiz-article-link a {
  color: #7CABBA;
  font-size: 0.85rem;
  text-decoration: none;
  border-bottom: 1px dashed #7CABBA;
  padding-bottom: 1px;
}
.quiz-article-link a:hover {
  color: #5A8C9C;
  border-color: #5A8C9C;
}
.quiz-article-link a::before {
  content: "\1F4D6 ";
}

.quiz-question-text {
  font-size: 1.15rem;
  font-weight: 600;
  color: var(--font-color, #333);
  line-height: 1.6;
  margin-bottom: 20px;
  padding: 16px 20px;
  background: var(--card-bg, #fff);
  border-radius: 10px;
  border-left: 4px solid #7CABBA;
}
.quiz-question-index {
  color: #7CABBA;
  font-weight: 700;
}

.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.quiz-option {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  background: var(--card-bg, #fff);
  border: 2px solid rgba(124, 171, 186, 0.15);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.25s ease;
  font-size: 0.95rem;
  color: var(--font-color, #333);
}
.quiz-option:hover:not(.quiz-option-disabled) {
  border-color: #7CABBA;
  background: rgba(124, 171, 186, 0.05);
}
.quiz-option-label {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(124, 171, 186, 0.1);
  color: #7CABBA;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.85rem;
  flex-shrink: 0;
  transition: all 0.25s;
}
.quiz-option-text {
  flex: 1;
  line-height: 1.5;
}
.quiz-option-correct {
  border-color: #4caf50 !important;
  background: rgba(76, 175, 80, 0.08) !important;
}
.quiz-option-correct .quiz-option-label {
  background: #4caf50;
  color: #fff;
}
.quiz-option-wrong {
  border-color: #ef5350 !important;
  background: rgba(239, 83, 80, 0.08) !important;
}
.quiz-option-wrong .quiz-option-label {
  background: #ef5350;
  color: #fff;
}
.quiz-option-disabled {
  cursor: default;
  opacity: 0.7;
}
.quiz-option-correct.quiz-option-disabled,
.quiz-option-wrong.quiz-option-disabled {
  opacity: 1;
}

.quiz-feedback {
  margin-top: 16px;
  padding: 14px 18px;
  border-radius: 10px;
  font-size: 0.9rem;
  line-height: 1.6;
}
.quiz-feedback-correct {
  background: rgba(76, 175, 80, 0.1);
  border: 1px solid rgba(76, 175, 80, 0.3);
  color: #2e7d32;
}
.quiz-feedback-wrong {
  background: rgba(239, 83, 80, 0.1);
  border: 1px solid rgba(239, 83, 80, 0.3);
  color: #c62828;
}
.quiz-feedback-label {
  font-weight: 700;
  margin-right: 6px;
}

.quiz-nav {
  display: flex;
  justify-content: space-between;
  margin-top: 24px;
  gap: 12px;
}
.quiz-nav-btn {
  padding: 10px 24px;
  border: 2px solid #7CABBA;
  background: transparent;
  color: #7CABBA;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.25s;
}
.quiz-nav-btn:hover {
  background: rgba(124, 171, 186, 0.1);
}
.quiz-nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.quiz-nav-btn-primary {
  background: linear-gradient(135deg, #7CABBA, #5A8C9C);
  color: #fff;
  border-color: transparent;
}
.quiz-nav-btn-primary:hover {
  background: linear-gradient(135deg, #5A8C9C, #4a7a8a);
}
.quiz-nav-btn-primary:disabled {
  background: linear-gradient(135deg, #7CABBA, #5A8C9C);
}

/* ===== 结果界面 ===== */
.quiz-result-card {
  max-width: 500px;
  margin: 0 auto;
  text-align: center;
  background: var(--card-bg, #fff);
  border-radius: 16px;
  padding: 40px 30px;
  border: 1px solid rgba(124, 171, 186, 0.2);
}
.quiz-result-icon {
  font-size: 3rem;
  margin-bottom: 12px;
}
.quiz-result-title {
  font-size: 1.4rem;
  color: var(--font-color, #333);
  margin-bottom: 20px;
}
.quiz-result-score {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 4px;
  margin-bottom: 16px;
}
.quiz-result-num {
  font-size: 2.8rem;
  font-weight: 800;
  color: #7CABBA;
}
.quiz-result-sep {
  font-size: 2rem;
  color: var(--second-font-color, #aaa);
  margin: 0 2px;
}
.quiz-result-rate-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  max-width: 300px;
  margin: 0 auto 20px;
}
.quiz-result-rate-bar {
  flex: 1;
  height: 10px;
  background: rgba(124, 171, 186, 0.15);
  border-radius: 5px;
  overflow: hidden;
}
.quiz-result-rate-fill {
  height: 100%;
  width: 0%;
  border-radius: 5px;
  transition: width 1s ease;
}
.quiz-result-rate {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--font-color, #333);
  white-space: nowrap;
}
.quiz-result-comment {
  color: var(--second-font-color, #888);
  font-size: 0.95rem;
  line-height: 1.6;
  margin-bottom: 28px;
}
.quiz-result-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}
.quiz-result-btn {
  padding: 10px 24px;
  border: 2px solid #7CABBA;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: all 0.25s;
  background: linear-gradient(135deg, #7CABBA, #5A8C9C);
  color: #fff;
}
.quiz-result-btn:hover {
  background: linear-gradient(135deg, #5A8C9C, #4a7a8a);
  border-color: transparent;
}
.quiz-result-btn-outline {
  background: transparent;
  color: #7CABBA;
}
.quiz-result-btn-outline:hover {
  background: rgba(124, 171, 186, 0.1);
}

/* ===== 暗色模式 ===== */
[data-theme="dark"] .quiz-card {
  background: #1e1e1e;
  border-color: rgba(124, 171, 186, 0.15);
}
[data-theme="dark"] .quiz-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}
[data-theme="dark"] .quiz-notebook-item {
  background: #1e1e1e;
  border-color: rgba(124, 171, 186, 0.1);
}
[data-theme="dark"] .quiz-question-text {
  background: #1e1e1e;
}
[data-theme="dark"] .quiz-option {
  background: #1e1e1e;
  border-color: rgba(124, 171, 186, 0.1);
}
[data-theme="dark"] .quiz-option:hover:not(.quiz-option-disabled) {
  background: rgba(124, 171, 186, 0.08);
}
[data-theme="dark"] .quiz-option-correct {
  background: rgba(76, 175, 80, 0.12) !important;
}
[data-theme="dark"] .quiz-option-wrong {
  background: rgba(239, 83, 80, 0.12) !important;
}
[data-theme="dark"] .quiz-feedback-correct {
  background: rgba(76, 175, 80, 0.12);
  color: #66bb6a;
}
[data-theme="dark"] .quiz-feedback-wrong {
  background: rgba(239, 83, 80, 0.12);
  color: #ef5350;
}
[data-theme="dark"] .quiz-result-card {
  background: #1e1e1e;
}
[data-theme="dark"] .quiz-back-btn {
  border-color: #555;
  color: #999;
}
[data-theme="dark"] .quiz-notebook-ans-wrong {
  background: rgba(239, 83, 80, 0.12);
  color: #ef5350;
}
[data-theme="dark"] .quiz-notebook-ans-correct {
  background: rgba(76, 175, 80, 0.12);
  color: #66bb6a;
}
[data-theme="dark"] .quiz-tab {
  color: #999;
}
[data-theme="dark"] .quiz-tab-active {
  color: #7CABBA;
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .quiz-cards {
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
  }
  .quiz-card {
    padding: 18px 14px;
  }
  .quiz-question-text {
    font-size: 1.05rem;
    padding: 14px 16px;
  }
  .quiz-option {
    padding: 12px 14px;
  }
  .quiz-tab {
    padding: 10px 18px;
    font-size: 0.9rem;
  }
}
@media (max-width: 480px) {
  .quiz-cards {
    grid-template-columns: 1fr;
  }
  .quiz-header {
    flex-direction: column;
    align-items: stretch;
  }
  .quiz-back-btn {
    align-self: flex-start;
  }
  .quiz-nav-btn {
    padding: 10px 16px;
    font-size: 0.85rem;
  }
  .quiz-result-actions {
    flex-direction: column;
  }
  .quiz-notebook-actions {
    flex-direction: column;
  }
  .quiz-notebook-btn {
    text-align: center;
  }
}
</style>

<script>
(function() {
  var BASE = '/DailyNote/data/quiz.json';
  var LABELS = ['A', 'B', 'C', 'D'];

  function esc(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
  var STORAGE_KEY = 'quiz_wrong_answers';
  var quizData = null;
  var currentQuiz = null;
  var currentIdx = 0;
  var answers = [];
  var answered = false;
  var quizFromNotebook = false; // 是否从错题本进入答题

  // ===== DOM 引用 =====
  var $select = document.getElementById('quiz-select');
  var $questions = document.getElementById('quiz-questions');
  var $result = document.getElementById('quiz-result');
  var $cards = document.getElementById('quiz-cards');
  var $progressFill = document.getElementById('quiz-progress-fill');
  var $progressText = document.getElementById('quiz-progress-text');
  var $articleLink = document.getElementById('quiz-article-link');
  var $questionText = document.getElementById('quiz-question-text');
  var $options = document.getElementById('quiz-options');
  var $feedback = document.getElementById('quiz-feedback');
  var $prevBtn = document.getElementById('quiz-prev-btn');
  var $nextBtn = document.getElementById('quiz-next-btn');
  var $backBtn = document.getElementById('quiz-back-btn');
  var $resultIcon = document.getElementById('quiz-result-icon');
  var $resultTitle = document.getElementById('quiz-result-title');
  var $resultCorrect = document.getElementById('quiz-result-correct');
  var $resultTotal = document.getElementById('quiz-result-total');
  var $resultRateFill = document.getElementById('quiz-result-rate-fill');
  var $resultRate = document.getElementById('quiz-result-rate');
  var $resultComment = document.getElementById('quiz-result-comment');
  var $retryBtn = document.getElementById('quiz-retry-btn');
  var $homeBtn = document.getElementById('quiz-home-btn');
  var $notebookBadge = document.getElementById('quiz-notebook-badge');
  var $notebookList = document.getElementById('quiz-notebook-list');

  // ===== localStorage 操作 =====
  function getWrongAnswers() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];
    } catch(e) {
      return [];
    }
  }

  function saveWrongAnswers(list) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
    updateBadge();
  }

  function addWrongAnswer(quizId, questionIdx, wrongIdx) {
    var list = getWrongAnswers();
    // 去重：同一题只存一条
    var exists = list.findIndex(function(item) {
      return item.quizId === quizId && item.questionIdx === questionIdx;
    });
    if (exists !== -1) {
      // 更新错误选项（可能换了另一个错误答案）
      list[exists].wrongIdx = wrongIdx;
      list[exists].timestamp = Date.now();
    } else {
      list.push({
        quizId: quizId,
        questionIdx: questionIdx,
        wrongIdx: wrongIdx,
        timestamp: Date.now()
      });
    }
    saveWrongAnswers(list);
  }

  function removeWrongAnswer(quizId, questionIdx) {
    var list = getWrongAnswers().filter(function(item) {
      return !(item.quizId === quizId && item.questionIdx === questionIdx);
    });
    saveWrongAnswers(list);
  }

  function updateBadge() {
    var count = getWrongAnswers().length;
    if (count > 0) {
      $notebookBadge.textContent = count;
      $notebookBadge.style.display = '';
    } else {
      $notebookBadge.style.display = 'none';
    }
  }

  // ===== Tab 切换 =====
  var $tabs = document.querySelectorAll('.quiz-tab');
  var $tabBank = document.getElementById('quiz-tab-bank');
  var $tabNotebook = document.getElementById('quiz-tab-notebook');

  $tabs.forEach(function(tab) {
    tab.addEventListener('click', function() {
      $tabs.forEach(function(t) { t.classList.remove('quiz-tab-active'); });
      tab.classList.add('quiz-tab-active');
      var name = tab.getAttribute('data-tab');
      $tabBank.style.display = name === 'bank' ? '' : 'none';
      $tabNotebook.style.display = name === 'notebook' ? '' : 'none';
      if (name === 'notebook') renderNotebook();
    });
  });

  // ===== 加载数据 =====
  fetch(BASE).then(function(r) { return r.json(); }).then(function(data) {
    quizData = data;
    renderCards();
    updateBadge();
    var hash = location.hash.replace('#', '');
    if (hash) {
      var found = quizData.quizzes.find(function(q) { return q.id === hash; });
      if (found) startQuiz(found);
    }
  }).catch(function() {
    $cards.innerHTML = '<p style="text-align:center;color:#999">题库加载失败，请刷新重试</p>';
  });

  // ===== 渲染题库卡片 =====
  function renderCards() {
    var html = '';
    quizData.quizzes.forEach(function(quiz) {
      html += '<div class="quiz-card" data-id="' + quiz.id + '">'
        + '<span class="quiz-card-category">' + (quiz.category || '综合') + '</span>'
        + '<div class="quiz-card-title">' + quiz.title + '</div>'
        + '<div class="quiz-card-count">' + quiz.questions.length + ' 道题</div>'
        + '</div>';
    });
    $cards.innerHTML = html;
    $cards.addEventListener('click', function(e) {
      var card = e.target.closest('.quiz-card');
      if (!card) return;
      var id = card.getAttribute('data-id');
      var quiz = quizData.quizzes.find(function(q) { return q.id === id; });
      if (quiz) startQuiz(quiz);
    });
  }

  // ===== 渲染错题本 =====
  function renderNotebook() {
    var wrongList = getWrongAnswers();
    if (wrongList.length === 0) {
      $notebookList.innerHTML = '<div class="quiz-notebook-empty">还没有错题，继续加油！</div>';
      return;
    }
    var html = '';
    // 按时间倒序
    wrongList.sort(function(a, b) { return b.timestamp - a.timestamp; });
    wrongList.forEach(function(item) {
      var quiz = quizData.quizzes.find(function(q) { return q.id === item.quizId; });
      if (!quiz) return;
      var q = quiz.questions[item.questionIdx];
      if (!q) return;
      var wrongLabel = LABELS[item.wrongIdx] + '. ' + esc(q.options[item.wrongIdx]);
      var correctLabel = LABELS[q.answer] + '. ' + esc(q.options[q.answer]);
      html += '<div class="quiz-notebook-item" data-quiz="' + item.quizId + '" data-idx="' + item.questionIdx + '">'
        + '<div class="quiz-notebook-meta">'
        + '<span class="quiz-notebook-cat">' + (quiz.category || '综合') + '</span>'
        + '<span class="quiz-notebook-title">' + quiz.title + '</span>'
        + '</div>'
        + '<div class="quiz-notebook-q">' + esc(q.question) + '</div>'
        + '<div class="quiz-notebook-answers">'
        + '<div class="quiz-notebook-ans quiz-notebook-ans-wrong"><span class="quiz-notebook-ans-label">✗</span>' + wrongLabel + '</div>'
        + '<div class="quiz-notebook-ans quiz-notebook-ans-correct"><span class="quiz-notebook-ans-label">✓</span>' + correctLabel + '</div>'
        + '</div>'
        + (q.explanation ? '<div class="quiz-notebook-explanation">' + esc(q.explanation) + '</div>' : '')
        + '<div class="quiz-notebook-actions">'
        + '<button class="quiz-notebook-btn quiz-notebook-btn-retry" data-action="retry">重练此题</button>'
        + '<button class="quiz-notebook-btn quiz-notebook-btn-master" data-action="master">已掌握，移出</button>'
        + '</div>'
        + '</div>';
    });
    $notebookList.innerHTML = html;
  }

  // 错题本点击事件
  $notebookList.addEventListener('click', function(e) {
    var btn = e.target.closest('.quiz-notebook-btn');
    if (!btn) return;
    var item = btn.closest('.quiz-notebook-item');
    var quizId = item.getAttribute('data-quiz');
    var idx = parseInt(item.getAttribute('data-idx'));
    var action = btn.getAttribute('data-action');

    if (action === 'master') {
      removeWrongAnswer(quizId, idx);
      item.style.opacity = '0';
      item.style.transform = 'translateX(20px)';
      setTimeout(function() { renderNotebook(); }, 250);
    } else if (action === 'retry') {
      var quiz = quizData.quizzes.find(function(q) { return q.id === quizId; });
      if (quiz) {
        // 从错题本进入，标记来源
        quizFromNotebook = true;
        startSingleQuestion(quiz, idx);
      }
    }
  });

  // ===== 开始答题 =====
  function startQuiz(quiz) {
    currentQuiz = quiz;
    currentIdx = 0;
    quizFromNotebook = false;
    answers = new Array(quiz.questions.length).fill(-1);
    answered = false;
    location.hash = quiz.id;
    showScreen('questions');
    renderQuestion();
  }

  // 从错题本重练单题
  function startSingleQuestion(quiz, idx) {
    currentQuiz = quiz;
    currentIdx = idx;
    answers = new Array(quiz.questions.length).fill(-1);
    answered = false;
    showScreen('questions');
    renderQuestion();
  }

  function showScreen(name) {
    $select.style.display = name === 'select' ? '' : 'none';
    $questions.style.display = name === 'questions' ? '' : 'none';
    $result.style.display = name === 'result' ? '' : 'none';
  }

  // ===== 渲染题目 =====
  function renderQuestion() {
    var q = currentQuiz.questions[currentIdx];
    var total = currentQuiz.questions.length;
    var answeredCount = answers.filter(function(a) { return a !== -1; }).length;

    $progressFill.style.width = (answeredCount / total * 100) + '%';
    $progressText.textContent = answeredCount + '/' + total;

    if (currentQuiz.article_url && currentIdx === 0 && !quizFromNotebook) {
      $articleLink.innerHTML = '<a href="' + currentQuiz.article_url + '" target="_blank">先阅读原文</a>';
    } else {
      $articleLink.innerHTML = '';
    }

    $questionText.innerHTML = '<span class="quiz-question-index">第 ' + (currentIdx + 1) + ' 题</span><br>' + esc(q.question);

    var optHtml = '';
    q.options.forEach(function(opt, i) {
      var cls = 'quiz-option';
      if (answers[currentIdx] !== -1) {
        cls += ' quiz-option-disabled';
        if (i === q.answer) cls += ' quiz-option-correct';
        else if (i === answers[currentIdx] && i !== q.answer) cls += ' quiz-option-wrong';
      }
      optHtml += '<div class="' + cls + '" data-idx="' + i + '">'
        + '<span class="quiz-option-label">' + LABELS[i] + '</span>'
        + '<span class="quiz-option-text">' + esc(opt) + '</span>'
        + '</div>';
    });
    $options.innerHTML = optHtml;

    answered = answers[currentIdx] !== -1;
    if (answered) {
      showFeedback(currentIdx);
    } else {
      $feedback.style.display = 'none';
    }

    $prevBtn.disabled = currentIdx === 0;
    if (quizFromNotebook) {
      // 从错题本进入：只答一题，答完显示"返回错题本"
      $nextBtn.textContent = answers[currentIdx] !== -1 ? '返回错题本' : '下一题';
      $nextBtn.disabled = answers[currentIdx] === -1;
    } else {
      if (currentIdx === total - 1 && answeredCount === total) {
        $nextBtn.textContent = '查看结果';
      } else {
        $nextBtn.textContent = '下一题';
      }
      $nextBtn.disabled = currentIdx === total - 1 && answeredCount < total;
    }
  }

  function showFeedback(idx) {
    var q = currentQuiz.questions[idx];
    var isCorrect = answers[idx] === q.answer;
    $feedback.style.display = '';
    $feedback.className = 'quiz-feedback ' + (isCorrect ? 'quiz-feedback-correct' : 'quiz-feedback-wrong');
    $feedback.innerHTML = '<span class="quiz-feedback-label">' + (isCorrect ? '✓ 回答正确！' : '✗ 回答错误') + '</span>'
      + (q.explanation ? '<br>' + esc(q.explanation) : '');
  }

  // ===== 选项点击 =====
  $options.addEventListener('click', function(e) {
    var opt = e.target.closest('.quiz-option');
    if (!opt || answered) return;
    var idx = parseInt(opt.getAttribute('data-idx'));
    answers[currentIdx] = idx;
    answered = true;

    // 答错了自动收录到错题本
    if (idx !== currentQuiz.questions[currentIdx].answer) {
      addWrongAnswer(currentQuiz.id, currentIdx, idx);
    } else {
      // 答对了如果之前在错题本里，自动移除
      removeWrongAnswer(currentQuiz.id, currentIdx);
    }

    renderQuestion();
  });

  // ===== 导航 =====
  $prevBtn.addEventListener('click', function() {
    if (currentIdx > 0) {
      currentIdx--;
      answered = answers[currentIdx] !== -1;
      renderQuestion();
    }
  });

  $nextBtn.addEventListener('click', function() {
    if (quizFromNotebook) {
      // 从错题本来的，返回错题本
      quizFromNotebook = false;
      showScreen('select');
      // 切换到错题本 tab
      $tabs.forEach(function(t) { t.classList.remove('quiz-tab-active'); });
      document.querySelector('[data-tab="notebook"]').classList.add('quiz-tab-active');
      $tabBank.style.display = 'none';
      $tabNotebook.style.display = '';
      renderNotebook();
      return;
    }
    var total = currentQuiz.questions.length;
    var answeredCount = answers.filter(function(a) { return a !== -1; }).length;
    if (currentIdx < total - 1) {
      currentIdx++;
      renderQuestion();
    } else if (answeredCount === total) {
      showResult();
    }
  });

  $backBtn.addEventListener('click', function() {
    currentQuiz = null;
    quizFromNotebook = false;
    location.hash = '';
    showScreen('select');
    renderNotebook();
  });

  // ===== 结果 =====
  function showResult() {
    var total = currentQuiz.questions.length;
    var correct = 0;
    answers.forEach(function(a, i) {
      if (a === currentQuiz.questions[i].answer) correct++;
    });
    var rate = Math.round(correct / total * 100);

    showScreen('result');
    $resultCorrect.textContent = correct;
    $resultTotal.textContent = total;
    $resultRate.textContent = rate + '%';

    setTimeout(function() {
      $resultRateFill.style.width = rate + '%';
    }, 100);

    var color, icon, title, comment;
    if (rate === 100) {
      color = '#4caf50'; icon = '🎉'; title = '满分！'; comment = '完美掌握，太强了！';
    } else if (rate >= 80) {
      color = '#7CABBA'; icon = '💪'; title = '表现优秀'; comment = '掌握得不错，再巩固一下细节就完美了。';
    } else if (rate >= 60) {
      color = '#ff9800'; icon = '📚'; title = '继续努力'; comment = '基础还行，建议回顾文章中的重点内容。';
    } else {
      color = '#ef5350'; icon = '💡'; title = '需要加油'; comment = '建议重新阅读原文，巩固基础知识后再试一次。';
    }
    $resultIcon.textContent = icon;
    $resultTitle.textContent = title;
    $resultComment.textContent = comment;
    $resultRateFill.style.background = color;
  }

  $retryBtn.addEventListener('click', function() {
    startQuiz(currentQuiz);
  });

  $homeBtn.addEventListener('click', function() {
    currentQuiz = null;
    location.hash = '';
    showScreen('select');
    $resultRateFill.style.width = '0%';
    renderNotebook();
  });
})();
</script>
