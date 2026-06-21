---
title: 分类
date: 2026-06-21
type: "page"
top_img: /DailyNote/images/landscape2.jpg
---

<div class="classify-tabs">
  <button class="classify-tab active" data-tab="categories">分类</button>
  <button class="classify-tab" data-tab="tags">标签</button>
</div>
<div class="classify-content" id="classify-categories">
  <div class="category-cards-grid" id="category-grid"></div>
</div>
<div class="classify-content" id="classify-tags" style="display:none">
  <div class="tag-cloud-list" id="tag-cloud-custom"></div>
</div>

<script>
(function () {
  // Tab 切换
  var tabs = document.querySelectorAll('.classify-tab');
  tabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      tabs.forEach(function (t) { t.classList.remove('active'); });
      tab.classList.add('active');
      document.getElementById('classify-categories').style.display = tab.dataset.tab === 'categories' ? '' : 'none';
      document.getElementById('classify-tags').style.display = tab.dataset.tab === 'tags' ? '' : 'none';
    });
  });

  // 分类图标映射
  var iconMap = { '前端': '💻', '后端': '⚙️', 'AI': '🤖', '算法': '🧮', '数据库': '🗄️', '运维': '🛠️', '设计': '🎨', '工具': '🔧', '随笔': '✍️' };
  function getIcon(name) {
    for (var k in iconMap) { if (name.indexOf(k) !== -1) return iconMap[k]; }
    return '📁';
  }

  // 从分类页面抓取数据
  fetch('/DailyNote/categories/')
    .then(function (r) { return r.text(); })
    .then(function (html) {
      var doc = new DOMParser().parseFromString(html, 'text/html');
      var items = doc.querySelectorAll('.category-lists .category-list > .category-list-item');
      var grid = document.getElementById('category-grid');
      if (!items.length) { grid.innerHTML = '<p style="color:#999">暂无分类</p>'; return; }
      items.forEach(function (item) {
        var link = item.querySelector('a');
        var count = item.querySelector('.category-list-count');
        if (!link) return;
        var name = link.textContent.trim();
        var href = link.getAttribute('href');
        var cnt = count ? count.textContent.trim() : '0';
        var card = document.createElement('a');
        card.className = 'category-card';
        card.href = href;
        card.innerHTML = '<div class="category-card-icon">' + getIcon(name) + '</div>' +
          '<div class="category-card-name">' + name + '</div>' +
          '<div class="category-card-count"><span>' + cnt + '</span> 篇</div>';
        grid.appendChild(card);
      });
    });

  // 主题色系配色（浅色背景，适合深色文字）
  var tagColors = [
    '#D0E8F0', '#C0DEE8', '#B0D4E0', '#A0CAD8',
    '#D8ECF2', '#C8E2EC', '#B8D8E4', '#E0F0F5'
  ];

  // 从标签页面抓取数据
  fetch('/DailyNote/tags/')
    .then(function (r) { return r.text(); })
    .then(function (html) {
      var doc = new DOMParser().parseFromString(html, 'text/html');
      var links = doc.querySelectorAll('.tag-cloud-list a');
      var cloud = document.getElementById('tag-cloud-custom');
      if (!links.length) { cloud.innerHTML = '<p style="color:#999">暂无标签</p>'; return; }
      links.forEach(function (a, i) {
        var tag = document.createElement('a');
        tag.href = a.getAttribute('href');
        tag.textContent = a.textContent;
        // 保留原始字号差异，使用主题色系循环配色
        tag.style.fontSize = a.style.fontSize;
        tag.style.backgroundColor = tagColors[i % tagColors.length];
        cloud.appendChild(tag);
      });
    });
})();
</script>

<style>
.classify-tabs {
  display: flex; gap: 12px; margin-bottom: 28px;
  border-bottom: 2px solid #eee; padding-bottom: 0;
}
.classify-tab {
  padding: 10px 28px; font-size: 15px; font-weight: 600;
  background: none; border: none; cursor: pointer;
  color: #999; border-bottom: 3px solid transparent;
  margin-bottom: -2px; transition: color 0.2s, border-color 0.2s;
}
.classify-tab.active { color: #7CABBA; border-bottom-color: #7CABBA; }
.classify-tab:hover { color: #5A8C9C; }

/* 标签云 */
#tag-cloud-custom {
  display: flex; flex-wrap: wrap; gap: 12px;
  justify-content: flex-start; padding: 10px 0;
}
#tag-cloud-custom a {
  display: inline-block; padding: 6px 18px;
  border-radius: 20px; color: #2C5F6E;
  text-decoration: none; line-height: 1.6; font-weight: 600;
  transition: transform 0.2s, box-shadow 0.2s, filter 0.2s;
}
#tag-cloud-custom a:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  filter: brightness(1.1);
  text-decoration: none;
}

/* 暗色模式 */
[data-theme="dark"] .classify-tabs { border-bottom-color: #333; }
[data-theme="dark"] .classify-tab { color: #666; }
[data-theme="dark"] .classify-tab.active { color: #9CC5D0; border-bottom-color: #9CC5D0; }
[data-theme="dark"] .classify-tab:hover { color: #7CABBA; }
[data-theme="dark"] #tag-cloud-custom a {
  color: #D0E8F0;
  filter: brightness(0.75);
}
</style>
