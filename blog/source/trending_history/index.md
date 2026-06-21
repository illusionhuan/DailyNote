---
title: 热文归档
date: 2026-06-21
type: "trending_history"
top_img: /DailyNote/images/landscape6.jpg
---

<div id="history-container">
  <div class="history-sidebar">
    <h3 class="history-sidebar-title">选择日期</h3>
    <div id="history-dates" class="history-dates">
      <p>加载中...</p>
    </div>
  </div>
  <div class="history-main">
    <div class="history-header">
      <h2 id="history-date-title" class="history-date-title">热文归档</h2>
      <p id="history-updated" class="history-updated"></p>
    </div>
    <div id="history-list" class="history-list">
      <p class="history-hint">← 请选择日期查看往期热文</p>
    </div>
  </div>
</div>

<script>
(function() {
  var BASE = '/DailyNote/data/trending_history/';
  var manifestUrl = BASE + 'manifest.json';
  var currentLoaded = null;

  fetch(manifestUrl)
    .then(function(res) { return res.json(); })
    .then(function(data) {
      var dates = data.dates || [];
      if (dates.length === 0) {
        document.getElementById('history-dates').innerHTML = '<p class="history-empty">暂无历史数据</p>';
        return;
      }
      renderDates(dates);
      loadDate(dates[0]);
    })
    .catch(function() {
      document.getElementById('history-dates').innerHTML = '<p class="history-empty">暂无历史数据</p>';
    });

  function renderDates(dates) {
    var html = '';
    dates.forEach(function(date) {
      html += '<div class="history-date-item" data-date="' + date + '">';
      html += '<span class="history-date-text">' + formatDate(date) + '</span>';
      html += '<span class="history-date-weekday">' + getWeekday(date) + '</span>';
      html += '</div>';
    });
    document.getElementById('history-dates').innerHTML = html;

    document.getElementById('history-dates').addEventListener('click', function(e) {
      var item = e.target.closest('.history-date-item');
      if (!item) return;
      var date = item.getAttribute('data-date');
      loadDate(date);
    });
  }

  function loadDate(date) {
    if (currentLoaded === date) return;
    currentLoaded = date;

    // 高亮当前选中日期
    var items = document.querySelectorAll('.history-date-item');
    items.forEach(function(el) {
      el.classList.toggle('active', el.getAttribute('data-date') === date);
    });

    document.getElementById('history-date-title').textContent = formatDate(date) + ' 热文';
    document.getElementById('history-list').innerHTML = '<p>加载中...</p>';

    fetch(BASE + date + '.json')
      .then(function(res) { return res.json(); })
      .then(function(data) {
        document.getElementById('history-updated').textContent = '抓取时间：' + new Date(data.updated_at).toLocaleString('zh-CN');
        renderArticles(data.articles);
      })
      .catch(function() {
        document.getElementById('history-list').innerHTML = '<p class="history-empty">该日期数据加载失败</p>';
      });
  }

  function renderArticles(articles) {
    if (!articles || articles.length === 0) {
      document.getElementById('history-list').innerHTML = '<p class="history-empty">暂无文章</p>';
      return;
    }
    var html = '';
    articles.forEach(function(article, i) {
      var sourceName = {'juejin': '掘金'}[article.source] || article.source;
      html += '<div class="history-card">';
      html += '<span class="history-rank">#' + (i + 1) + '</span>';
      html += '<span class="history-source source-' + article.source + '">' + sourceName + '</span>';
      html += '<a href="' + article.url + '" target="_blank" rel="noopener" class="history-title">' + article.title + '</a>';
      if (article.summary) {
        html += '<p class="history-summary">' + article.summary.substring(0, 120) + '...</p>';
      }
      html += '<div class="history-meta">';
      if (article.score) html += '<span class="history-score">&#9650; ' + article.score + '</span>';
      if (article.comments) html += '<span class="history-comments">&#128172; ' + article.comments + '</span>';
      if (article.author) html += '<span class="history-author">' + article.author + '</span>';
      html += '</div>';
      html += '</div>';
    });
    document.getElementById('history-list').innerHTML = html;
  }

  function formatDate(dateStr) {
    var parts = dateStr.split('-');
    return parts[0] + ' 年 ' + parseInt(parts[1]) + ' 月 ' + parseInt(parts[2]) + ' 日';
  }

  function getWeekday(dateStr) {
    var days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];
    var d = new Date(dateStr + 'T00:00:00');
    return days[d.getDay()];
  }
})();
</script>

<style>
/* 布局：左侧日期列表 + 右侧文章列表 */
#history-container {
  display: flex;
  gap: 24px;
  min-height: 60vh;
}

/* 左侧日期栏 */
.history-sidebar {
  flex: 0 0 200px;
  position: sticky;
  top: 80px;
  align-self: flex-start;
  max-height: calc(100vh - 120px);
  overflow-y: auto;
}

.history-sidebar-title {
  font-size: 16px;
  font-weight: 600;
  color: #555;
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 2px solid #7CABBA;
}

.history-dates {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-date-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
  font-size: 14px;
  color: #555;
}

.history-date-item:hover {
  background: rgba(124, 171, 186, 0.1);
}

.history-date-item.active {
  background: linear-gradient(135deg, #7CABBA 0%, #5A8C9C 100%);
  color: #fff;
  font-weight: 600;
}

.history-date-item.active .history-date-weekday {
  color: rgba(255, 255, 255, 0.8);
}

.history-date-weekday {
  font-size: 12px;
  color: #999;
}

/* 右侧文章区 */
.history-main {
  flex: 1;
  min-width: 0;
}

.history-header {
  margin-bottom: 20px;
}

.history-date-title {
  font-size: 22px;
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
}

.history-updated {
  color: #999;
  font-size: 13px;
}

.history-hint, .history-empty {
  color: #999;
  font-size: 15px;
  text-align: center;
  padding: 40px 0;
}

/* 文章卡片（复用 trending 页面风格） */
.history-card {
  position: relative;
  padding: 16px;
  margin-bottom: 12px;
  border: 1px solid #eee;
  border-radius: 8px;
  transition: box-shadow 0.2s;
}

.history-card:hover {
  box-shadow: 0 2px 12px rgba(124, 171, 186, 0.18);
}

.history-rank {
  position: absolute;
  top: 12px;
  right: 12px;
  font-size: 24px;
  font-weight: bold;
  color: #ddd;
}

.history-source {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  color: #fff;
  margin-bottom: 8px;
}

.source-juejin { background: linear-gradient(135deg, #1e90ff 0%, #0066dd 100%); }

.history-title {
  font-size: 16px;
  font-weight: 600;
  display: block;
  margin-bottom: 6px;
}

.history-summary {
  color: #666;
  font-size: 14px;
  margin: 6px 0;
  line-height: 1.6;
}

.history-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #999;
  margin-top: 8px;
}

/* 暗色模式 */
[data-theme="dark"] .history-sidebar-title { color: #ccc; border-color: #5A8C9C; }
[data-theme="dark"] .history-date-item { color: #bbb; }
[data-theme="dark"] .history-date-item:hover { background: rgba(124, 171, 186, 0.15); }
[data-theme="dark"] .history-date-title { color: #e0e0e0; }
[data-theme="dark"] .history-card { border-color: #333; }
[data-theme="dark"] .history-card:hover { box-shadow: 0 2px 12px rgba(74, 122, 138, 0.2); }
[data-theme="dark"] .history-summary { color: #aaa; }

/* 响应式：移动端改为上下布局 */
@media (max-width: 768px) {
  #history-container {
    flex-direction: column;
  }
  .history-sidebar {
    flex: none;
    position: static;
    max-height: none;
    margin-bottom: 16px;
  }
  .history-dates {
    flex-direction: row;
    flex-wrap: wrap;
    gap: 6px;
  }
  .history-date-item {
    padding: 6px 10px;
    font-size: 13px;
    border-radius: 16px;
  }
  .history-date-weekday { display: none; }
}
</style>
