// ActualWork — Main JS
// Minimal JavaScript for navigation toggle and lazy video loading.

(function () {
  'use strict';

  // Mobile nav toggle
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.querySelector('.site-nav');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      nav.classList.toggle('open');
      var expanded = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!expanded));
    });
  }

  // Lazy-load YouTube iframes when they scroll into view
  var lazyVideos = document.querySelectorAll('.video-lazy');
  if (lazyVideos.length > 0 && 'IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var el = entry.target;
          var iframe = document.createElement('iframe');
          iframe.src = el.getAttribute('data-src');
          iframe.setAttribute('allowfullscreen', '');
          iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture');
          iframe.title = el.getAttribute('data-title') || 'Video';
          el.innerHTML = '';
          el.appendChild(iframe);
          el.classList.remove('video-lazy');
          observer.unobserve(el);
        }
      });
    }, { rootMargin: '200px' });

    lazyVideos.forEach(function (v) {
      observer.observe(v);
    });
  } else {
    // Fallback: load all videos immediately
    lazyVideos.forEach(function (el) {
      var iframe = document.createElement('iframe');
      iframe.src = el.getAttribute('data-src');
      iframe.setAttribute('allowfullscreen', '');
      iframe.setAttribute('allow', 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture');
      iframe.title = el.getAttribute('data-title') || 'Video';
      el.innerHTML = '';
      el.appendChild(iframe);
      el.classList.remove('video-lazy');
    });
  }
})();
