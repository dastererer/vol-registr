const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

if (window.AOS) {
  window.AOS.init({
    once: true,
    duration: reduceMotion ? 0 : 620,
    easing: 'cubic-bezier(.2,.75,.25,1)',
    offset: 42,
    disable: reduceMotion,
  });
}

const canvases = [...document.querySelectorAll('canvas[data-lottie-src]')];

if (canvases.length) {
  import('https://cdn.jsdelivr.net/npm/@lottiefiles/dotlottie-web@0.79.2/+esm')
    .then(({ DotLottie }) => {
      const mount = (canvas) => {
        if (canvas.dataset.lottieReady === 'true') return;
        canvas.dataset.lottieReady = 'true';
        new DotLottie({
          canvas,
          src: canvas.dataset.lottieSrc,
          autoplay: !reduceMotion,
          loop: !reduceMotion && canvas.dataset.lottieLoop !== 'false',
        });
      };

      if (!('IntersectionObserver' in window)) {
        canvases.forEach(mount);
        return;
      }

      const observer = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            mount(entry.target);
            observer.unobserve(entry.target);
          });
        },
        { rootMargin: '180px' },
      );
      canvases.forEach((canvas) => observer.observe(canvas));
    })
    .catch(() => {
      canvases.forEach((canvas) => canvas.classList.add('motion-canvas--fallback'));
    });
}
