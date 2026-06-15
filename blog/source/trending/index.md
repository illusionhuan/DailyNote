---
title: 热文榜
date: 2026-06-08
type: "trending"
---

<!-- 热文聚合页面：从 trending.json 加载数据，支持按平台筛选 -->
<!-- 数据来源：Python 脚本定时抓取 Hacker News / GitHub / 掘金 / V2EX / SegmentFault -->

<div id="trending-container">
  <div class="trending-header">
    <p class="trending-updated" id="trending-updated"></p>
    <!-- 平台筛选按钮 -->
    <div class="trending-filters" id="trending-filters">
      <button class="filter-btn active" data-source="all">全部</button>
      <button class="filter-btn" data-source="hacker_news">Hacker News</button>
      <button class="filter-btn" data-source="github">GitHub</button>
      <button class="filter-btn" data-source="juejin">掘金</button>
      <button class="filter-btn" data-source="v2ex">V2EX</button>
      <button class="filter-btn" data-source="segmentfault">SegmentFault</button>
    </div>
  </div>
  <div class="trending-list" id="trending-list">
    <p>加载中...</p>
  </div>
</div>

<script>
// 加载热文数据（由 Python 脚本生成）
fetch('/_data/trending.json')
  .then(res => res.json())
  .then(data => {
    // 显示最后更新时间
    document.getElementById('trending-updated').textContent = '更新时间：' + new Date(data.updated_at).toLocaleString('zh-CN');
    renderArticles(data.articles, 'all');
    setupFilters(data.articles);
  })
  .catch(() => {
    document.getElementById('trending-list').innerHTML = '<p>热文数据加载中，请稍后刷新...</p>';
  });

/**
 * 渲染文章列表
 * @param {Array} articles - 文章数组
 * @param {string} source - 筛选的平台标识（'all' 显示全部）
 */
function renderArticles(articles, source) {
  var filtered = source === 'all' ? articles : articles.filter(function(a) { return a.source === source; });
  var html = '';
  filtered.forEach(function(article, i) {
    // 平台标识到中文名的映射
    var sourceName = {
      'hacker_news': 'Hacker News',
      'github': 'GitHub',
      'juejin': '掘金',
      'v2ex': 'V2EX',
      'segmentfault': 'SegmentFault'
    }[article.source] || article.source;

    html += '<div class="trending-card">';
    html += '<span class="trending-rank">#' + (i + 1) + '</span>';
    html += '<span class="trending-source source-' + article.source + '">' + sourceName + '</span>';
    html += '<a href="' + article.url + '" target="_blank" rel="noopener" class="trending-title">' + article.title + '</a>';
    if (article.summary) {
      html += '<p class="trending-summary">' + article.summary.substring(0, 120) + '...</p>';
    }
    html += '<div class="trending-meta">';
    if (article.score) html += '<span class="trending-score">&#9650; ' + article.score + '</span>';
    if (article.comments) html += '<span class="trending-comments">&#128172; ' + article.comments + '</span>';
    if (article.author) html += '<span class="trending-author">' + article.author + '</span>';
    html += '</div>';
    html += '</div>';
  });
  document.getElementById('trending-list').innerHTML = html || '<p>暂无该平台热文</p>';
}

/**
 * 绑定筛选按钮点击事件
 * 点击后重新渲染对应平台的文章
 */
function setupFilters(articles) {
  document.querySelectorAll('.filter-btn').forEach(function(btn) {
    btn.addEventListener('click', function() {
      document.querySelectorAll('.filter-btn').forEach(function(b) { b.classList.remove('active'); });
      this.classList.add('active');
      renderArticles(articles, this.dataset.source);
    });
  });
}
</script>

<style>
/* 热文榜页面样式 */
.trending-header { margin-bottom: 20px; }
.trending-updated { color: #999; font-size: 14px; margin-bottom: 12px; }
.trending-filters { display: flex; flex-wrap: wrap; gap: 8px; }
.filter-btn {
  padding: 6px 16px; border: 1px solid #ddd; border-radius: 20px;
  background: transparent; cursor: pointer; font-size: 14px; transition: all 0.2s;
}
.filter-btn:hover, .filter-btn.active {
  background: linear-gradient(135deg, #7CABBA 0%, #5A8C9C 100%);
  color: #fff; border-color: #7CABBA;
}
.trending-card {
  position: relative; padding: 16px; margin-bottom: 12px;
  border: 1px solid #eee; border-radius: 8px; transition: box-shadow 0.2s;
}
.trending-card:hover { box-shadow: 0 2px 12px rgba(124, 171, 186, 0.18); }
.trending-rank {
  position: absolute; top: 12px; right: 12px;
  font-size: 24px; font-weight: bold; color: #ddd;
}
/* 各平台标签颜色 (渐变) */
.trending-source {
  display: inline-block; padding: 2px 8px; border-radius: 4px;
  font-size: 12px; color: #fff; margin-bottom: 8px;
}
.source-hacker_news { background: linear-gradient(135deg, #ff7711 0%, #e55c00 100%); }
.source-github { background: linear-gradient(135deg, #3a3f44 0%, #24292e 100%); }
.source-juejin { background: linear-gradient(135deg, #1e90ff 0%, #0066dd 100%); }
.source-v2ex { background: linear-gradient(135deg, #444 0%, #2a2a2a 100%); }
.source-segmentfault { background: linear-gradient(135deg, #00a86b 0%, #007a4e 100%); }
.trending-title { font-size: 16px; font-weight: 600; display: block; margin-bottom: 6px; }
.trending-summary { color: #666; font-size: 14px; margin: 6px 0; line-height: 1.6; }
.trending-meta { display: flex; gap: 16px; font-size: 13px; color: #999; margin-top: 8px; }
/* 暗色模式适配 */
[data-theme="dark"] .trending-card { border-color: #333; }
[data-theme="dark"] .trending-card:hover { box-shadow: 0 2px 12px rgba(74, 122, 138, 0.2); }
[data-theme="dark"] .filter-btn { border-color: #555; color: #ccc; }
[data-theme="dark"] .filter-btn:hover, [data-theme="dark"] .filter-btn.active {
  background: linear-gradient(135deg, #4A7A8A 0%, #3A6A7A 100%);
  border-color: #4A7A8A;
}
[data-theme="dark"] .trending-summary { color: #aaa; }
</style>
