(() => {
  let initialized = false;

  const initHeroBackground = () => {
    if (initialized) return;

    const root = document.querySelector('.hero-bg-swiper');
    if (!root) return;
    initialized = true;

    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const slides = [...root.querySelectorAll('.hero-bg-slide')];

    const startFallback = () => {
      let activeIndex = 0;
      Array.from(root.classList).forEach((className) => {
        if (className.indexOf('swiper-') === 0 && className !== 'swiper') {
          root.classList.remove(className);
        }
      });
      const wrapper = root.querySelector('.swiper-wrapper');
      if (wrapper) wrapper.removeAttribute('style');
      slides.forEach((slide) => {
        slide.removeAttribute('style');
        Array.from(slide.classList).forEach((className) => {
          if (className.indexOf('swiper-slide-') === 0) slide.classList.remove(className);
        });
      });
      root.classList.add('hero-bg-swiper--fallback');

      const setActiveSlide = (index) => {
        slides.forEach((slide, slideIndex) => {
          slide.classList.toggle('is-fallback-active', slideIndex === index);
        });
      };

      setActiveSlide(activeIndex);
      if (!reduceMotion && slides.length > 1) {
        window.setInterval(() => {
          if (document.hidden) return;
          activeIndex = (activeIndex + 1) % slides.length;
          setActiveSlide(activeIndex);
        }, 5200);
      }
    };

    if (typeof window.Swiper !== 'function') {
      startFallback();
      return;
    }

    let swiper;
    try {
      swiper = new window.Swiper(root, {
        effect: 'fade',
        fadeEffect: { crossFade: true },
        loop: true,
        speed: reduceMotion ? 0 : 1200,
        allowTouchMove: true,
        grabCursor: false,
        autoplay: reduceMotion
          ? false
          : {
              delay: 5200,
              disableOnInteraction: false,
              pauseOnMouseEnter: false,
            },
      });
    } catch (error) {
      console.warn('Hero background switched to the local fallback.', error);
      startFallback();
      return;
    }

    document.addEventListener('visibilitychange', () => {
      if (!swiper.autoplay) return;
      if (document.hidden) swiper.autoplay.stop();
      else swiper.autoplay.start();
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHeroBackground, { once: true });
  } else {
    initHeroBackground();
  }

  window.addEventListener('pageshow', initHeroBackground);
})();
