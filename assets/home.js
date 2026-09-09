(function () {
  'use strict';

  var navbar = document.getElementById('navbar');
  var revealElements = document.querySelectorAll('.reveal');

  function onScroll() {
    if (window.scrollY > 20) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry, index) {
          if (entry.isIntersecting) {
            var delay = entry.target.dataset.delay || (index * 80);
            setTimeout(function () {
              entry.target.classList.add('visible');
            }, delay);
            observer.unobserve(entry.target);
          }
        });
      },
      {
        threshold: 0.12,
        rootMargin: '0px 0px -60px 0px'
      }
    );

    revealElements.forEach(function (el) {
      observer.observe(el);
    });
  } else {
    revealElements.forEach(function (el) {
      el.classList.add('visible');
    });
  }

  var navLinks = document.querySelectorAll('a[href^="#"]');
  navLinks.forEach(function (link) {
    link.addEventListener('click', function (e) {
      var targetId = link.getAttribute('href');
      if (targetId.length > 1) {
        var target = document.querySelector(targetId);
        if (target) {
          e.preventDefault();
          var offset = target.getBoundingClientRect().top + window.scrollY - 40;
          window.scrollTo({
            top: offset,
            behavior: 'smooth'
          });
        }
      }
    });
  });
})();
