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

    /* ── API Routes ───────────────────────────────── */
    API_REGISTER_URL: '/api/register/',

    /* ── Hero Section Timings ─────────────────────── */
    hero: {
        logo:       { duration: 0.4, ease: 'power4.out' },
        title:      { duration: 0.7, stagger: 0.12, ease: 'power4.out' },
        label:      { duration: 0.4, ease: 'power4.out' },
        text:       { duration: 0.4, stagger: 0.08, ease: 'power4.out' },
        player:     { duration: 0.8, ease: 'power4.out', mobileOpacity: 0.3 },
        scroll:     { duration: 0.4, delay: 0.08 },
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
