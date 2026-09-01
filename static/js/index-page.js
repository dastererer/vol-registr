/**
 * @file index-page.js
 * @description GSAP animations for the landing page (index.html).
 *              Reads all timings/easing from APP_CONFIG.
 *              Depends on: config.js, utils.js, gsap + ScrollTrigger (CDN).
 */

/* global gsap, ScrollTrigger, window, APP_CONFIG */

document.addEventListener('DOMContentLoaded', () => {
    'use strict';

    const CFG = window.APP_CONFIG;
    const isMobileView = window.matchMedia('(max-width: 768px)').matches;
    const reducedMotion = CFG.REDUCED_MOTION === true;

    // ─── Hero Intro Timeline ────────────────────────
    if (!reducedMotion && typeof gsap !== 'undefined') {
        initHeroIntro(CFG.hero);
    }

    // ─── Card Modal (desktop only) ────────────────────
    if (!isMobileView) {
        initCardModal();
    }

    // ─── Registered Teams Modal ───────────────────────
    initRegisteredTeamsModal();

    // ─── Scroll-triggered Sections ──────────────────
    if (typeof ScrollTrigger !== 'undefined') {
        gsap.registerPlugin(ScrollTrigger);

        // Skip scroll animations on mobile and for reduced motion
        if (!isMobileView && !reducedMotion) {
            initCardsFlyIn(CFG.cards);
            initLocationScrollAnim(CFG.scroll);
            initEditorialSectionAnim(CFG.scroll);
            initTimelineScrollAnim(CFG.scroll);
        }
    }
});


// ═══════════════════════════════════════════════════════
//  Hero Section
// ═══════════════════════════════════════════════════════

/**
 * Build the intro GSAP timeline for the hero section.
 * @param {object} cfg - hero timings from APP_CONFIG.
 */
function initHeroIntro(cfg) {
    const hero = document.querySelector('.hero--swiper');
    if (!hero) return;

    const background = hero.querySelector('.hero-bg-swiper');
    const scrim = hero.querySelector('.hero-bg-scrim');
    const sweep = hero.querySelector('.hero-motion-sweep');
    const label = hero.querySelector('.hero__label-wrap');
    const introStage = document.querySelector('.hero-title__stage--intro');
    const finalStage = document.querySelector('.hero-title__stage--final');
    const introLines = document.querySelectorAll('.hero-title__stage--intro .hero-title__line');
    const finalLines = document.querySelectorAll('.hero-title__stage--final .hero-title__line');
    const text = hero.querySelector('.hero-text');
    const mobileFacts = window.matchMedia('(max-width: 767px)').matches;
    const factsPanel = hero.querySelector(mobileFacts ? '.hero-mobile-facts' : '.hero-stats-row');
    const factItems = mobileFacts
        ? gsap.utils.toArray('.hero-mobile-fact')
        : gsap.utils.toArray('.hero-stats-row > *');
    const buttons = gsap.utils.toArray('.hero-btn-container > *');
    const progress = hero.querySelector('.hero-bg-progress');
    const activeMeta = hero.querySelector('.hero-bg-slide.swiper-slide-active .hero-bg-slide__meta')
        || hero.querySelector('.hero-bg-slide__meta');

    [introStage, finalStage].forEach((stage) => {
        if (stage) stage.style.animation = 'none';
    });

    hero.classList.add('hero--motion-running');
    gsap.set(background, { opacity: 0.35, scale: 1.08, transformOrigin: 'center center' });
    gsap.set(scrim, { opacity: 0 });
    gsap.set(sweep, { opacity: 0, xPercent: 0 });
    gsap.set(label, { opacity: 0, x: -26, clipPath: 'inset(0 100% 0 0)' });
    gsap.set(introStage, { opacity: 1, xPercent: 0, clipPath: 'none' });
    gsap.set(finalStage, { opacity: 0, xPercent: 0, clipPath: 'none' });
    gsap.set(introLines, { yPercent: 115, skewY: 3 });
    gsap.set(finalLines, { yPercent: 115, skewY: 3 });
    gsap.set(text, { opacity: 0, y: 24 });
    gsap.set(factsPanel, { opacity: 0, clipPath: 'inset(0 100% 0 0)' });
    gsap.set(factItems, { opacity: 0, y: 20 });
    gsap.set(buttons, { opacity: 0, y: 24 });
    gsap.set(progress, { opacity: 0, scaleX: 0.62, transformOrigin: 'right center' });
    gsap.set(activeMeta, { opacity: 0, y: 24 });

    const tl = gsap.timeline({
        defaults: { ease: 'power4.out' },
        onComplete: () => {
            gsap.set(introStage, { opacity: 0 });
            gsap.set(finalStage, { opacity: 1 });
            hero.classList.remove('hero--motion-running');
            hero.classList.add('hero--motion-complete');
        },
    });

    tl.to(background, {
        opacity: 1,
        scale: 1,
        duration: cfg.background.duration,
        ease: cfg.background.ease,
    }, 0)
        .to(scrim, { opacity: 1, duration: cfg.background.duration * 0.7 }, 0)
        .to(sweep, {
            xPercent: 400,
            opacity: 0.78,
            duration: cfg.sweep.duration * 0.72,
            ease: 'power2.in',
        }, 0.12)
        .to(sweep, {
            xPercent: 470,
            opacity: 0,
            duration: cfg.sweep.duration * 0.28,
            ease: 'power2.out',
        })
        .to(label, {
            opacity: 1,
            x: 0,
            clipPath: 'inset(0 0% 0 0)',
            duration: cfg.label.duration,
            ease: cfg.label.ease,
        }, 0.16)
        .to(introLines, {
            yPercent: 0,
            skewY: 0,
            duration: cfg.title.duration,
            stagger: cfg.title.stagger,
            ease: cfg.title.ease,
        }, 0.3)
        .to(introLines, {
            yPercent: -115,
            skewY: -2,
            duration: cfg.title.exitDuration,
            stagger: cfg.title.exitStagger,
            ease: 'power3.in',
        }, 1.18)
        .set(finalStage, { opacity: 1 }, 1.28)
        .to(finalLines, {
            yPercent: 0,
            skewY: 0,
            duration: cfg.title.duration,
            stagger: cfg.title.stagger,
            ease: cfg.title.ease,
        }, 1.32)
        .to(text, {
            opacity: 1,
            y: 0,
            duration: cfg.text.duration,
            ease: cfg.text.ease,
        }, 1.7)
        .to(factsPanel, {
            opacity: 1,
            clipPath: 'inset(0 0% 0 0)',
            duration: cfg.facts.duration,
            ease: cfg.facts.ease,
        }, 1.76)
        .to(factItems, {
            opacity: 1,
            y: 0,
            duration: cfg.facts.duration,
            stagger: cfg.facts.stagger,
            ease: cfg.facts.ease,
        }, 1.86)
        .to(buttons, {
            opacity: 1,
            y: 0,
            duration: cfg.buttons.duration,
            stagger: cfg.buttons.stagger,
            ease: cfg.buttons.ease,
        }, 2.02)
        .to(progress, {
            opacity: 1,
            scaleX: 1,
            duration: cfg.progress.duration,
            ease: cfg.progress.ease,
        }, 2.12)
        .to(activeMeta, {
            opacity: 1,
            y: 0,
            duration: cfg.progress.duration,
            ease: cfg.progress.ease,
        }, 2.12);
}


// ═══════════════════════════════════════════════════════
//  Flip Cards (Scroll-Triggered)
// ═══════════════════════════════════════════════════════

/**
 * Scatter cards off-screen, then fly + flip them on scroll.
 * @param {object} cfg - cards config from APP_CONFIG.
 */
function initCardsFlyIn(cfg) {
    const wrappers = gsap.utils.toArray('.flip-card-wrapper');
    const cards    = gsap.utils.toArray('.flip-card');
    if (!wrappers.length) return;

    scatterCardsOffScreen(wrappers, cfg);

    // Cards start with back visible (rotationY 0)
    gsap.set(cards, { rotationY: 0 });

    const cardsTl = gsap.timeline({
        scrollTrigger: {
            trigger: '.perspective-section',
            start: cfg.scrollStart,
            toggleActions: 'play none none none',
            once: true,
        },
    });

    // Step 1 — Fly to grid position
    cardsTl.to(wrappers, {
        x: 0, y: 0, rotation: 0, scale: 1,
        duration: cfg.flyIn.duration,
        stagger: { each: cfg.flyIn.stagger, from: 0 },
        ease: cfg.flyIn.ease,
    });

    // Step 2 — Flip to front
    cardsTl.to(cards, {
        rotationY: 180,
        duration: cfg.flip.duration,
        stagger: cfg.flip.stagger,
        ease: cfg.flip.ease,
        onComplete() {
            wrappers.forEach(w => {
                const card = w.querySelector('.flip-card');
                if (card) card.flipped = true;
            });
        },
    }, '-=0.8');
}

/**
 * Place each card wrapper at a random off-screen position.
 * @param {Element[]} wrappers
 * @param {object} cfg
 */
function scatterCardsOffScreen(wrappers, cfg) {
    const vw = window.innerWidth;
    const vh = window.innerHeight;
    const { min: offMin, max: offMax } = cfg.randomOffset;
    const { min: rotMin, max: rotMax } = cfg.randomRotation;

    wrappers.forEach((wrapper, index) => {
        const side = index === 0
            ? 1                               // first → right
            : index === wrappers.length - 1
                ? 0                           // last  → left
                : Math.floor(Math.random() * 4);

        const offset = gsap.utils.random(offMin, offMax);
        let x = 0;
        let y = 0;

        switch (side) {
            case 0: x = -vw - offset; y = gsap.utils.random(-vh * 0.2, vh * 1.2); break;  // left
            case 1: x =  vw + offset; y = gsap.utils.random(-vh * 0.2, vh * 1.2); break;  // right
            case 2: y = -vh - offset; x = gsap.utils.random(-vw * 0.2, vw * 1.2); break;  // top
            default: y = vh + offset; x = gsap.utils.random(-vw * 0.2, vw * 1.2); break;  // bottom
        }

        gsap.set(wrapper, {
            x, y,
            opacity: 1,
            rotation: gsap.utils.random(rotMin, rotMax),
            scale: 0.98,
            force3D: true,
        });
    });
}


// ═══════════════════════════════════════════════════════
//  Location & Timeline Sections
// ═══════════════════════════════════════════════════════

/**
 * Slide-in animation for the location block.
 * @param {object} cfg - scroll config from APP_CONFIG.
 */
function initLocationScrollAnim(cfg) {
    const loc = cfg.locationSlide;

    gsap.from(['.location__title', '.divider--wide'], {
        scrollTrigger: { trigger: '.location-content', start: loc.start },
        y: loc.x * 0.35,
        opacity: 0,
        duration: loc.duration,
        stagger: 0.08,
    });

    gsap.from(['.location-map', '.location__info', '.location__link'], {
        scrollTrigger: { trigger: '.location-side', start: loc.start },
        x: loc.x,
        opacity: 0,
        duration: loc.duration,
        stagger: 0.08,
    });
}

/**
 * Reveal editorial support blocks on the landing page.
 * @param {object} cfg - scroll config from APP_CONFIG.
 */
function initEditorialSectionAnim(cfg) {
    const item = cfg.timelineItem;

    gsap.from('.deal-lead', {
        scrollTrigger: { trigger: '.perspective-section', start: item.start },
        y: item.y,
        opacity: 0,
        duration: item.duration,
    });

    gsap.from('.location-feature', {
        scrollTrigger: { trigger: '.location-features', start: item.start },
        y: item.y,
        opacity: 0,
        duration: item.duration,
        stagger: 0.08,
    });

}

/**
 * Staggered reveal for each timeline milestone.
 * @param {object} cfg - scroll config from APP_CONFIG.
 */
function initTimelineScrollAnim(cfg) {
    const item = cfg.timelineItem;

    gsap.utils.toArray('.road-item').forEach(el => {
        gsap.from(el, {
            scrollTrigger: { trigger: el, start: item.start },
            y: item.y, opacity: 0, duration: item.duration,
        });
    });
}


// ═══════════════════════════════════════════════════════
//  Card Modal (Desktop)
// ═══════════════════════════════════════════════════════

/**
 * Click a card → show its front face enlarged in a centered modal
 * with a blurred backdrop. Click overlay or press Escape to close.
 */
function initCardModal() {
    const overlay  = document.getElementById('cardModalOverlay');
    const modalBox = document.getElementById('cardModalCard');
    const modalBody = document.getElementById('cardModalBody');
    const closeButton = document.getElementById('cardModalClose');
    if (!overlay || !modalBox || !modalBody || !closeButton) return;

    let lastTrigger = null;

    // Click on any card wrapper → open modal
    document.querySelectorAll('.flip-card-wrapper').forEach(wrapper => {
        wrapper.addEventListener('click', (e) => {
            e.stopPropagation();
            const front = wrapper.querySelector('.flip-card-front');
            if (!front) return;

            // Clone front face into modal
            const clone = front.cloneNode(true);
            clone.classList.add('card-modal__front');
            clone.removeAttribute('style');
            clone.querySelectorAll('[style]').forEach((node) => node.removeAttribute('style'));
            clone.querySelectorAll('[id]').forEach((node) => node.removeAttribute('id'));

            const title = clone.querySelector('.card-front__title');
            if (title) title.id = 'cardModalTitle';

            modalBody.replaceChildren(clone);
            lastTrigger = wrapper.querySelector('.flip-card__open') || wrapper;

            overlay.classList.add('active');
            overlay.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
            window.requestAnimationFrame(() => closeButton.focus());
        });
    });

    closeButton.addEventListener('click', () => closeCardModal(overlay, lastTrigger));

    // Close only when the dimmed backdrop itself is clicked.
    overlay.addEventListener('click', (event) => {
        if (event.target === overlay) closeCardModal(overlay, lastTrigger);
    });

    // Close on Escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && overlay.classList.contains('active')) {
            closeCardModal(overlay, lastTrigger);
        }
    });
}

function closeCardModal(overlay, lastTrigger = null) {
    overlay.classList.remove('active');
    overlay.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
    if (lastTrigger && typeof lastTrigger.focus === 'function') lastTrigger.focus();
}

// ═══════════════════════════════════════════════════════
//  Registered Teams Modal
// ═══════════════════════════════════════════════════════

/**
 * Click the 'Registered Teams' button to open a modal
 * showing the list of teams.
 */
function initRegisteredTeamsModal() {
    const modal = document.getElementById('registeredTeamsModal');
    const openBtns = document.querySelectorAll('.rt-modal-trigger');
    const closeBtn = document.getElementById('registeredTeamsModalClose');

    if (!modal || openBtns.length === 0 || !closeBtn) {
        return;
    }

    // Open modal
    openBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            modal.classList.add('active');
            document.body.classList.add('rt-modal-open');
            document.documentElement.classList.add('rt-modal-open');
            document.body.style.overflow = 'hidden';
            document.documentElement.style.overflow = 'hidden';
        });
    });

    // Close via button
    closeBtn.addEventListener('click', () => {
        closeModal();
    });

    // Close via overlay click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeModal();
        }
    });

    // Close via Escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });

    function closeModal() {
        modal.classList.remove('active');
        document.body.classList.remove('rt-modal-open');
        document.documentElement.classList.remove('rt-modal-open');
        document.body.style.overflow = '';
        document.documentElement.style.overflow = '';
        // Remove hash without scrolling
        if (window.location.hash === '#registeredTeamsModal') {
            history.replaceState(null, null, ' ');
        }
    }

    // Check if URL has hash to open modal on load
    if (window.location.hash === '#registeredTeamsModal') {
        modal.classList.add('active');
        document.body.classList.add('rt-modal-open');
        document.documentElement.classList.add('rt-modal-open');
        document.body.style.overflow = 'hidden';
        document.documentElement.style.overflow = 'hidden';
    }
}
