---
title: 热文榜
date: 2026-06-08
type: "trending"
top_img: /images/landscape7.jpg
---

<!-- 热文聚合页面：从 trending.json 加载数据，展示中文技术热文 -->

<div id="trending-container">
  <div class="trending-header">
    <p class="trending-updated" id="trending-updated"></p>
  </div>
  <div class="trending-list" id="trending-list">
    <p>加载中...</p>
  </div>
</div>

<script>
fetch('../data/trending.json')
  .then(function(res) { return res.json(); })
  .then(function(data) {
    document.getElementById('trending-updated').textContent = '更新时间：' + new Date(data.updated_at).toLocaleString('zh-CN');
    renderArticles(data.articles);
  })
  .catch(function() {
    document.getElementById('trending-list').innerHTML = '<p>热文数据加载中，请稍后刷新...</p>';
  });

function renderArticles(articles) {
  var html = '';
  articles.forEach(function(article, i) {
    var sourceName = {
      'juejin': '掘金'
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
  document.getElementById('trending-list').innerHTML = html || '<p>暂无热文数据</p>';
}
</script>

<style>
.trending-header { margin-bottom: 20px; }
.trending-updated { color: #999; font-size: 14px; margin-bottom: 12px; }
.trending-card {
  position: relative; padding: 16px; margin-bottom: 12px;
  border: 1px solid #eee; border-radius: 8px; transition: box-shadow 0.2s;
}
.trending-card:hover { box-shadow: 0 2px 12px rgba(124, 171, 186, 0.18); }
.trending-rank {
  position: absolute; top: 12px; right: 12px;
  font-size: 24px; font-weight: bold; color: #ddd;
}
.trending-source {
  display: inline-block; padding: 2px 8px; border-radius: 4px;
  font-size: 12px; color: #fff; margin-bottom: 8px;
}
.source-juejin { background: linear-gradient(135deg, #1e90ff 0%, #0066dd 100%); }
.trending-title { font-size: 16px; font-weight: 600; display: block; margin-bottom: 6px; }
.trending-summary { color: #666; font-size: 14px; margin: 6px 0; line-height: 1.6; }
.trending-meta { display: flex; gap: 16px; font-size: 13px; color: #999; margin-top: 8px; }
[data-theme="dark"] .trending-card { border-color: #333; }
[data-theme="dark"] .trending-card:hover { box-shadow: 0 2px 12px rgba(74, 122, 138, 0.2); }
[data-theme="dark"] .trending-summary { color: #aaa; }
</style>
