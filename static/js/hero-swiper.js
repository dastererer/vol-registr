document.addEventListener('DOMContentLoaded', () => {
  const root = document.querySelector('.hero-bg-swiper');
  if (!root) return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const progress = [...document.querySelectorAll('.hero-bg-progress span')];
  const slides = [...root.querySelectorAll('.hero-bg-slide')];

  const setActiveProgress = (index) => {
    progress.forEach((item, itemIndex) => {
      item.classList.toggle('is-active', itemIndex === index);
      item.classList.toggle('is-past', itemIndex < index);
    });
  };

  if (typeof window.Swiper !== 'function') {
    let activeIndex = 0;
    root.classList.add('hero-bg-swiper--fallback');

    const setActiveSlide = (index) => {
      slides.forEach((slide, slideIndex) => {
        slide.classList.toggle('is-fallback-active', slideIndex === index);
      });
      setActiveProgress(index);
    };

    setActiveSlide(activeIndex);
    if (!reduceMotion && slides.length > 1) {
      window.setInterval(() => {
        if (document.hidden) return;
        activeIndex = (activeIndex + 1) % slides.length;
        setActiveSlide(activeIndex);
      }, 5200);
    }
    return;
  }

  const swiper = new window.Swiper(root, {
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
    on: {
      init(instance) {
        setActiveProgress(instance.realIndex);
      },
      realIndexChange(instance) {
        setActiveProgress(instance.realIndex);
      },
    },
  });

  document.addEventListener('visibilitychange', () => {
    if (!swiper.autoplay) return;
    if (document.hidden) swiper.autoplay.stop();
    else swiper.autoplay.start();
  });
});
