/**
 * Arena gallery — one full-width court photo at a time.
 */
(function () {
  'use strict';

  let arenaSwiper = null;

  function initArenaSwiper() {
    const element = document.querySelector('.arena-swiper');
    if (!element || arenaSwiper || typeof window.Swiper === 'undefined') return;

    arenaSwiper = new window.Swiper(element, {
      slidesPerView: 1,
      spaceBetween: 0,
      speed: 560,
      loop: false,
      grabCursor: true,
      keyboard: {
        enabled: true,
        onlyInViewport: true,
      },
      navigation: {
        prevEl: element.querySelector('.arena-nav--prev'),
        nextEl: element.querySelector('.arena-nav--next'),
      },
      pagination: {
        el: element.querySelector('.arena-pagination'),
        clickable: true,
      },
      a11y: {
        enabled: true,
        prevSlideMessage: 'Previous court photo',
        nextSlideMessage: 'Next court photo',
        paginationBulletMessage: 'Open court photo {{index}}',
      },
    });
  }

  document.addEventListener('DOMContentLoaded', initArenaSwiper);
  window.addEventListener('pageshow', initArenaSwiper);
})();
