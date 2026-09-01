/**
 * @file config.js
 * @description Centralized configuration for GSAP animation timings,
 *              easing curves, breakpoints, and API endpoints.
 *              Change values here instead of digging through animation code.
 */

/* global window */

window.APP_CONFIG = Object.freeze({

    /* ── Breakpoints ──────────────────────────────── */
    MOBILE_BREAKPOINT: 768,

    /* ── Accessibility ────────────────────────────── */
    /** True when the user requests reduced motion. Decorative
        animations must be skipped; functional transitions
        complete instantly (see GSAP timeScale guard below). */
    REDUCED_MOTION: window.matchMedia('(prefers-reduced-motion: reduce)').matches,

    /* ── API Routes ───────────────────────────────── */
    API_REGISTER_URL: '/api/register/',

    /* ── Hero Section Timings ─────────────────────── */
    hero: {
        background: { duration: 1.15, ease: 'power3.out' },
        sweep:      { duration: 1.25 },
        sponsor:    { enterDuration: 0.5, itemDuration: 0.52, hold: 0.42, exitDuration: 0.62 },
        title:      { duration: 0.72, stagger: 0.1, exitDuration: 0.5, exitStagger: 0.06, ease: 'power4.out' },
        label:      { duration: 0.55, ease: 'power4.out' },
        text:       { duration: 0.55, ease: 'power3.out' },
        facts:      { duration: 0.5, stagger: 0.08, ease: 'power3.out' },
        buttons:    { duration: 0.55, stagger: 0.1, ease: 'back.out(1.35)' },
        partner:    { duration: 0.62, ease: 'back.out(1.2)' },
    },

    /* ── Flip Cards ───────────────────────────────── */
    cards: {
        flyIn: {
            duration: 0.6,
            stagger: 0.08,
            ease: 'power4.out',
        },
        flip: {
            duration: 0.6,
            stagger: 0.08,
            ease: 'power3.inOut',
        },
        /** Random position range multiplier. */
        randomOffset: { min: 120, max: 260 },
        randomRotation: { min: -25, max: 25 },
        scrollStart: 'top 80%',
    },

    /* ── Scroll Animations ────────────────────────── */
    scroll: {
        locationSlide: { x: 50, duration: 0.6, start: 'top 80%' },
        timelineItem:  { y: 30, duration: 0.6, start: 'top 85%' },
    },

    /* ── Registration Page ────────────────────────── */
    registration: {
        introHeroText:  { y: 40, duration: 0.6, stagger: 0.08, ease: 'power4.out' },
        formPanel:      { x: 50, duration: 0.6, ease: 'power4.out' },
        formField:      { y: 20, duration: 0.6, stagger: 0.08, ease: 'power4.out' },
        passReveal:     { scale: 0.5, rotateX: -30, duration: 0.6, ease: 'power4.out' },

        /** Idle floating animation for the VIP pass. */
        passFloat:      { y: -15, duration: 0.6, ease: 'power3.inOut' },
        passSpin:       { duration: 0.8, ease: 'power3.inOut' },
        passMouseTilt:  { multiplier: 0.1, duration: 0.14, ease: 'power4.out' },
        passResetDelay: 0.14,

        /** Form submission animations. */
        hideFields:     { y: -20, duration: 0.4, stagger: 0.08, ease: 'power3.inOut' },
        successReveal:  { duration: 0.6, ease: 'power4.out' },
        celebrationSpin: 720,
    },
});

/* ── Reduced Motion Guard ─────────────────────────
   Honour prefers-reduced-motion for every GSAP-driven
   animation site-wide: run the global timeline ~1000x
   faster so tweens complete instantly while callbacks
   and control flow stay intact. CSS animations and
   transitions are already killed via the
   `@media (prefers-reduced-motion: reduce)` block. */
if (window.APP_CONFIG.REDUCED_MOTION && window.gsap) {
    window.gsap.globalTimeline.timeScale(1000);
}
