/**
 * 风景图片轮播
 * 通过 Butterfly 的 inject 机制注入到每个页面
 * 首页：替换全屏 header 背景为多图淡入淡出轮播
 * 归档页：为 header 添加轮播背景，并让内容区上移覆盖部分 header
 */
(function () {
  var header = document.getElementById('page-header');
  if (!header) return;

  var isHome = header.classList.contains('full_page');
  var isArchive = /^\/blog\/archives\//.test(window.location.pathname);
  if (!isHome && !isArchive) return;

  // 轮播图片列表
  var images = [
    '/blog/images/landscape1.jpg',
    '/blog/images/landscape2.jpg',
    '/blog/images/landscape3.jpg',
    '/blog/images/landscape4.jpg',
    '/blog/images/landscape5.jpg'
  ];

  // 归档页标记（用于 CSS 样式适配）
  if (isArchive) {
    header.classList.add('carousel-archive');
    var page = document.getElementById('page');
    if (page) page.classList.add('carousel-archive-layout');
  }

  // 创建轮播容器，插入到 header 最前面
  var container = document.createElement('div');
  container.className = 'carousel-container';
  header.insertBefore(container, header.firstChild);

  // 为每张图片创建一个 slide 层（绝对定位叠加，通过 opacity 切换）
  var slides = images.map(function (src, i) {
    var div = document.createElement('div');
    div.className = 'carousel-slide' + (i === 0 ? ' active' : '');
    div.style.backgroundImage = 'url(' + src + ')';
    container.appendChild(div);
    return div;
  });

  // 首页：将下拉箭头移入轮播容器
  if (isHome) {
    var scrollDown = document.getElementById('scroll-down');
    if (scrollDown) container.appendChild(scrollDown);
  }

  // 定时切换：每隔 5 秒淡入下一张图片
  var current = 0;
  setInterval(function () {
    slides[current].classList.remove('active');
    current = (current + 1) % slides.length;
    slides[current].classList.add('active');
  }, 5000);
})();
