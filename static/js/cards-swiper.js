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
    clearResidualStyles();
  }

  function shouldUseSwiper() {
    return window.innerWidth <= MOBILE_BP;
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

  function clearResidualStyles() {
    const root = getRoot();
    if (root) {
      Array.from(root.classList).forEach(function (className) {
        if (className.indexOf('swiper-') === 0 && className !== 'swiper') {
          root.classList.remove(className);
        }
      });
    }
    const wrapper = document.querySelector('.cards-swiper .swiper-wrapper');
    if (wrapper) wrapper.removeAttribute('style');
    const slides = document.querySelectorAll('.cards-swiper .swiper-slide');
    slides.forEach(function (slide) {
      slide.removeAttribute('style');
      Array.from(slide.classList).forEach(function (className) {
        if (className.indexOf('swiper-slide-') === 0) slide.classList.remove(className);
      });
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

    try {
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
      root.classList.remove('cards-swiper--fallback');
      root.classList.add('cards-swiper--ready');
      syncSlideVisibility(swiperInstance);
    } catch (error) {
      swiperInstance = null;
      enableNativeFallback();
      console.warn('Cards carousel switched to native scrolling.', error);
    }
  }

  function destroySwiper() {
    const root = getRoot();
    if (swiperInstance) {
      swiperInstance.destroy(true, true);
      swiperInstance = null;
    }
    if (root) root.classList.remove('cards-swiper--ready', 'cards-swiper--fallback');

    clearResidualStyles();
  }

  function handleResize() {
    if (shouldUseSwiper()) {
      initSwiper();
    } else {
      destroySwiper();
    }
  }

  // Init whether the script runs before or after DOMContentLoaded (Safari/BFCache safe).
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', handleResize, { once: true });
  } else {
    handleResize();
  }
  window.addEventListener('pageshow', handleResize);

  // Re-check on resize (debounced)
  let resizeTimer;
  window.addEventListener('resize', function () {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(handleResize, 150);
  });
})();
