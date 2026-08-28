document.addEventListener('DOMContentLoaded', () => {
  const root = document.querySelector('.hero-bg-swiper');
  if (!root || typeof Swiper === 'undefined') return;

  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const progress = [...document.querySelectorAll('.hero-bg-progress span')];

  const setActiveProgress = (index) => {
    progress.forEach((item, itemIndex) => {
      item.classList.toggle('is-active', itemIndex === index);
      item.classList.toggle('is-past', itemIndex < index);
    });
  };

  const swiper = new Swiper(root, {
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
