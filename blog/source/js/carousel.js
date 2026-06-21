/**
 * 风景图片轮播
 * 通过 Butterfly 的 inject 机制注入到每个页面
 * 首页：替换全屏 header 背景为多图淡入淡出轮播
 * 其他页面：为 header 添加轮播背景
 */
(function () {
  var header = document.getElementById('page-header');
  if (!header) return;

  var isHome = header.classList.contains('full_page');
  var isPost = header.classList.contains('post-bg');
  var isPage = header.classList.contains('not-home-page');
  if (!isHome && !isPost && !isPage) return;

  // 轮播图片列表（全部 7 张风景图）
  var images = [
    '/DailyNote/images/landscape1.jpg',
    '/DailyNote/images/landscape2.jpg',
    '/DailyNote/images/landscape3.jpg',
    '/DailyNote/images/landscape4.jpg',
    '/DailyNote/images/landscape5.jpg',
    '/DailyNote/images/landscape6.jpg',
    '/DailyNote/images/landscape7.jpg'
  ];

  // 非首页页面标记（用于 CSS 样式适配）
  if (isPost || isPage) {
    header.classList.add('carousel-page');
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
