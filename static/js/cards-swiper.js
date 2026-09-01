/**
 * Cards Swiper — mobile-only carousel
 * Stacked cards effect with swipe
 */
(function () {
  'use strict';

  const MOBILE_BP = 768;
  let swiperInstance = null;

  function getRoot() {
    return document.querySelector('.cards-swiper');
  }

  function enableNativeFallback() {
    const root = getRoot();
    if (!root) return;
    root.classList.remove('cards-swiper--ready');
    root.classList.add('cards-swiper--fallback');
  }

  function shouldUseSwiper() {
    return window.innerWidth < MOBILE_BP;
  }

  function syncSlideVisibility(swiper) {
    if (!swiper || !swiper.slides) return;
    swiper.slides.forEach(function (slide, index) {
      if (index === swiper.activeIndex) {
        slide.style.opacity = '1';
        slide.style.visibility = 'visible';
        slide.style.pointerEvents = 'auto';
      } else {
        slide.style.opacity = '0';
        slide.style.visibility = 'hidden';
        slide.style.pointerEvents = 'none';
      }
    });
  }

  function initSwiper() {
    if (swiperInstance) return;
    const root = getRoot();
    if (!root) return;
    if (typeof window.Swiper !== 'function') {
      enableNativeFallback();
      return;
    }

    root.classList.remove('cards-swiper--fallback');
    root.classList.add('cards-swiper--ready');
    swiperInstance = new window.Swiper(root, {
      effect: 'cards',
      grabCursor: true,
      speed: 500,
      cardsEffect: {
        perSlideOffset: 8,
        perSlideRotate: 3,
        rotate: true,
        slideShadows: false,
      },
      pagination: {
        el: '.cards-pagination',
        clickable: true,
      },
      on: {
        init: syncSlideVisibility,
        slideChange: syncSlideVisibility,
        resize: syncSlideVisibility,
      },
    });
  }

  function destroySwiper() {
    const root = getRoot();
    if (swiperInstance) {
      swiperInstance.destroy(true, true);
      swiperInstance = null;
    }
    if (root) root.classList.remove('cards-swiper--ready', 'cards-swiper--fallback');

    // Clean up residual inline styles left by Swiper
    var wrapper = document.querySelector('.cards-swiper .swiper-wrapper');
    if (wrapper) wrapper.removeAttribute('style');
    var slides = document.querySelectorAll('.cards-swiper .swiper-slide');
    slides.forEach(function (s) { s.removeAttribute('style'); });
  }

  function handleResize() {
    if (shouldUseSwiper()) {
      initSwiper();
    } else {
      destroySwiper();
    }
  }

  // Init on load
  document.addEventListener('DOMContentLoaded', handleResize);
  window.addEventListener('pageshow', handleResize);

  // Re-check on resize (debounced)
  let resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(handleResize, 150);
  });
})();
