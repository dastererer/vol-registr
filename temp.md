 ```markdown
     # REDESIGN SPEC — POCKET ACES COURT CUP 2 → SPORTS BRUTALISM
     ## Full visual reskin of an EXISTING Django site. Volleyball tournament registration. Game day: SATURDAY
   26.09.2026, first serve 09:00. Languages: EN + PL only (both already exist — preserve the mechanism exactly).

     You are a senior front-end engineer. Restyle this site into an aggressive, modern SPORTS aesthetic: brutalist
   structure, huge condensed uppercase typography, acid-volt accents on near-black asphalt, hard edges, clipped
   corners, asymmetric overlap layouts, scoreboard data strips. Zero glassmorphism, zero soft shadows, zero pink.

     You are working inside an existing Django 6 repo (`vol_registr` project, `tournament` app). You are NOT building a
   new site. You reskin templates and CSS while preserving every backend hook, template tag, form field, JS selector
   and the EN/PL i18n system.

     ---

     ## 1. PROJECT REALITY (verified facts — trust this, not your assumptions)

     - Templates: `tournament/templates/base.html` (nav + footer + a large inline `<style>` block of legacy brand CSS)
   and `tournament/templates/tournament/*.html` (`index.html`, `register.html`, `faq.html`, `team_detail.html`,
   `roster_update.html`, `vote_success.html`, `vote_error.html`, `pivate_policy_en.html`).
     - Served CSS (via `{% static_v %}`): `static/css/styles.css` + `registered-teams.css`, `sports-bg.css`,
   `sports-preview.css`, `arena-editorial.css`. SCSS sources exist in `static/scss/` but there is NO confirmed build
   pipeline — edit the served `.css` files directly; mirror token changes into `static/scss/_variables.scss` for
   hygiene.
     - JS (do not rename anything it touches): `static/js/navbar.js` (menu + language switcher), `index-page.js`,
   `register-page.js`, `faq.js`, `cards-swiper.js`, `config.js` (GSAP timing config — you MAY tune duration/ease values
   here, nothing else), `utils.js`.
     - CDN deps already loaded in `base.html`: GSAP 3.12.2 + ScrollTrigger, Swiper 11, Font Awesome 6.4. Keep them. Add
   NO new frameworks, NO Tailwind, NO WebGL/Three.js/Lottie/video backgrounds.
     - Admin panel (`tournament/templates/panel/`, `static/css/panel.css`, `static/js/panel.js`) is OUT OF SCOPE. Do
   not touch it.

     ### Protected hooks (hard contract — renaming any of these breaks the site)
     - navbar.js: `#siteNav`, `#navMenu`, `#navBurger`, `#navOverlay`, `#langToggle`, `.site-nav__lang-opt`
   (+`data-lang="en|pl"`), all `data-i18n` / `data-i18n-ph` attributes.
     - index/base JS: `#registeredTeamsModal`, `#registeredTeamsBtn`, `#registeredTeamsModalClose`,
   `.rt-modal-trigger`, `#heroPlayerContainer`, `.hero-title`, `.hero-title__stage`, `.hero-title__line`,
   `.hero-mobile-facts`, `#voteModal`, `#voteForm`, `#voteStatus`, `#voteModalClose`, `#voteTeamId`, `#voteTeamName`,
   `#voteEmail`, `.vote-btn` (+`data-team-id`, `data-team-name`), `.voting-board__meter-fill` (+`data-vote-width`).
     - register-page.js: `#step1`, `#step2`, `#step3`, `#stepSuccess`, `#stepperFill`, `.reg-step`, `.reg-field`,
   `.reg-btn`, `.reg-btn--next`, `.reg-panel__title/.hint/.note`, `.roster-row`, `.roster-first`, `.roster-last`,
   `#teamName`, `#capName`, `#phone`, `#email`, `#chkTerms`, `#chkPayment`, `.reg-logo-upload`, `.reg-check`.
     - faq.js: `.faq-list`, `.faq-item(.open)`, `.faq-question`, `.faq-form`, `.faq-form__body`. cards-swiper.js:
   `.cards-swiper .swiper-wrapper`, `.cards-swiper .swiper-slide`.
     - All Django template tags/filters (`{% url %}`, `{% static %}`, `{% static_v %}`, `{% csrf_token %}`, `{{
   registered_teams }}`, `{{ max_slots }}`, `{% widthratio %}`, `|asset_url`, `{% if registration_closed %}`, `{% if
   voting_enabled %}`) must keep working. Do not touch views, models, urls, forms.

     ### Known defect you must handle safely
     `base.html` references `{% url 'tournament_hub' %}` and `{% url 'tournament_gallery' %}`, which do NOT resolve in
   `tournament/urls.py` (NoReverseMatch risk). Replace with the non-raising pattern:
     `{% url 'tournament_hub' as hub_url %}` then `{% if hub_url %}<a href="{{ hub_url }}" …>Match Centre</a>{% endif
   %}` — same for gallery. Keep the `data-i18n` keys.

     ### Open content parameter (do NOT invent silently)
     Tournament day is fixed: **SAT 26.09.2026, 09:00, Outdoor Court by Dormitory No. 8, 8 teams, 150 zł/team.**
   Registration deadline is UNKNOWN — use `20.09.2026` as the visible placeholder and mark every occurrence with an
   HTML comment `<!-- [CONFIRM] registration deadline -->` so the owner can swap it.

     ---

     ## 2. THE PINK PURGE (exact inventory — all of this must die)

     Delete/replace every occurrence, then prove it with the grep gates in §18:
     - `#e41561` (`--brand-pink`), `#ff2d7a`, `#f34082`, any `rgba(228, 21, 97, …)` — concentrated in the inline
   `<style>` of `tournament/templates/base.html` (~30 usages: body radial blobs, `.gradient-text`, `.site-nav__cta`,
   `.btn-primary`, `.btn-cta`, `.divider`, `.vote-btn-main`, nav/footer glows and borders) plus 3 hits in
   `static/css/styles.css`.
     - The entire legacy inline `<style>` block in `base.html` (lines ~28–391) must be REMOVED and replaced by the new
   token layer (§7) living in `static/css/brutal.css`.
     - Also purge: `backdrop-filter` / `-webkit-backdrop-filter` everywhere in public CSS/templates; `border-radius:
   999px|9999px|50%` on public UI; `linear-gradient(135deg, var(--brand-pink), var(--brand-blue))` in all forms;
   `text-shadow: 2px 2px 0 rgba(73,192,255,…)`; the 5-layer radial-gradient `body` background; `transition: all …`.

     ---

     ## 3. FORBIDDEN — generic "AI design" patterns (hard negative constraints)

     1. NO glassmorphism: no `backdrop-filter`, no translucent `rgba(255,255,255,0.0x)` cards, no frosted nav.
     2. NO pink/magenta/fuchsia anywhere. NO purple-blue-pink gradient schemes. NO gradient text (`background-clip:
   text`). NO color gradients at all — solid fills only; the single exception is `repeating-linear-gradient` for the
   hatch texture in §11.
     3. NO pill buttons / `border-radius` > 2px. Radius is 0 (2px only on text inputs).
     4. NO soft/diffuse shadows (any `box-shadow` with blur > 0). Only hard offset shadows via `filter: drop-shadow(Xpx
   Ypx 0 <solid>)` — required because `clip-path` clips `box-shadow`.
     5. NO Montserrat, Inter, Roboto, Poppins, or default system-font look.
     6. NO `transition: all`. Always explicit property lists.
     7. NO bounce/elastic ease spam, NO infinite floating/bobbing loops, NO slow (>900ms) entrances.
     8. NO emoji as icons. Inline SVG for new icons; Font Awesome allowed ONLY where already in use (footer socials,
   vote heart, modal close).
     9. NO centered-everything symmetrical hero. NO uniform "3 cards with icon circle" SaaS grid.
     10. NO generic stock/3D illustrations. Use existing assets only: `static/assets/logo.png`,
   `static/assets/main_player.png`, team logos via `|asset_url`.
     11. NO new pages, routes, sections or copy blocks beyond this spec. NO lorem ipsum.
     12. NO renaming of protected hooks (§1), NO logic edits in JS except the i18n dictionary strings (§15) and
   `config.js` timing values.

     ---

     ## 4. FONTS (exact)

     Replace the Montserrat `<link>` in `base.html` with exactly this (all three families ship `latin-ext` — mandatory
   for Polish ą ć ę ł ń ó ś ź ż):

   ```

   https://fonts.googleapis.com/css2?family=Barlow+Condensed:ital,wght@0,600;0,700;0,800;1,700;1,800&family=Archivo:wgh
   t@400;500;600;700&family=Space+Mono:ital,wght@0,400;0,700&display=swap

   ```

     Stacks (tokens):
   ```

   --font-display: 'Barlow Condensed', 'Arial Narrow', Impact, sans-serif;
   --font-body:    'Archivo', system-ui, -apple-system, 'Segoe UI', sans-serif;
   --font-mono:    'Space Mono', 'Courier New', monospace;

   ```

     Usage rules:
     - Display (headings, buttons, big numbers, nav links): Barlow Condensed, UPPERCASE, weights 600–800. Hero/section
   Hs use italic 800.
     - Body copy, form inputs: Archivo 400/500.
     - Mono (meta labels, dates, scoreboard, table headers, footer headings, steppers, kickers): Space Mono, UPPERCASE,
   letter-spacing 0.10–0.14em. All numeric data uses mono (tabular by nature).
     - `body { -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility; }`
     - Acceptance: render the string `Zażółć gęślą jaźń` in all three families and confirm every diacritic displays.

     ---

     ## 5. DESIGN TOKENS (exact — this is the single source of truth)

     Create `static/css/brutal.css`. First rule in it:

     ```css
     html, body { background: #0A0C0E; color: #F4F4EF; }
   ```

   Then:

   ```css
     :root {
       /* color */
       --ink:        #0A0C0E;   /* page background: asphalt */
       --ink-2:      #0F1317;   /* raised surface */
       --ink-3:      #151B21;   /* card surface */
       --line:       #222B33;   /* hairline */
       --line-strong:#3A4650;   /* interactive border */
       --paper:      #F4F4EF;   /* primary text */
       --muted:      #9AA5AE;   /* secondary text */
       --volt:       #D8FF00;   /* PRIMARY accent: acid volt */
       --signal:     #FF4D00;   /* SECONDARY accent: deadlines, podium, alerts */
       --danger:     #FF3B30;
       --ok:         #35D07F;

       /* type */
       --font-display: 'Barlow Condensed', 'Arial Narrow', Impact, sans-serif;
       --font-body:    'Archivo', system-ui, -apple-system, 'Segoe UI', sans-serif;
       --font-mono:    'Space Mono', 'Courier New', monospace;

       /* fluid type scale */
       --fs-display-xl: clamp(4.5rem, 13vw, 11rem);    /* hero H1 */
       --fs-display-lg: clamp(3rem, 7vw, 6rem);        /* section H2 */
       --fs-display-md: clamp(1.9rem, 3.4vw, 2.9rem);  /* sub heads / card titles */
       --fs-display-sm: clamp(1.35rem, 2vw, 1.75rem);
       --fs-body:       clamp(0.95rem, 0.55vw + 0.72rem, 1.075rem);
       --fs-small:      0.85rem;
       --fs-mono-lg:    0.95rem;
       --fs-mono-md:    0.8rem;
       --fs-mono-sm:    0.7rem;

       /* layout */
       --container:   1440px;
       --gutter:      clamp(1.25rem, 4vw, 4rem);
       --section-y:   clamp(4.5rem, 9vw, 8.5rem);
       --seam:        clamp(16px, 3vw, 48px);      /* diagonal seam height */
       --nav-h:       68px;

       /* shape */
       --cut-btn:     14px;
       --cut-card:    20px;
       --btn-clip:    polygon(0 0, calc(100% - var(--cut-btn)) 0, 100% var(--cut-btn), 100% 100%, 0 100%);
       --card-clip:   polygon(0 0, calc(100% - var(--cut-card)) 0, 100% var(--cut-card), 100% 100%, var(--cut-card)
   100%, 0 calc(100% - var(--cut-card)));

       /* motion */
       --ease-out:  cubic-bezier(0.16, 1, 0.3, 1);    /* snappy entrance */
       --ease-hard: cubic-bezier(0.83, 0, 0.17, 1);   /* aggressive in-out */
       --ease-pop:  cubic-bezier(0.34, 1.56, 0.64, 1);/* rare pop */
       --t-hover:   140ms;
       --t-reveal:  600ms;

       /* z-index stack */
       --z-bg: 0; --z-content: 1; --z-overlap: 5; --z-nav: 50; --z-menu: 60; --z-modal: 100; --z-toast: 110;
     }
   ```

   Color law (WCAG-verified, do not deviate):
   • --volt on --ink ≈ 17:1, --paper on --ink ≈ 17.7:1, --muted on --ink ≈ 7.8:1 — all pass.
   • On any --volt surface the text is ALWAYS --ink (paper-on-volt ≈ 1.1:1 — forbidden).
   • --signal on --ink ≈ 5.9:1 → only for text ≥ 18px, icons, borders, meters. Never small body text.
   • Volt NEVER appears on light/paper backgrounds.

   ────────────────────────────────────────────────────────────────────────────────

   6. LAYER STACK (back → front)

   1. body --ink + fixed court-lines layer (body::before, z-index --z-bg, pointer-events none) — §11.
   2. .site-main content, z-index --z-content.
   3. Overlap elements (hero player, volt block, outlined numerals, ticker rotation), z-index --z-overlap.
   4. .site-nav sticky, z-index --z-nav.
   5. Mobile menu + overlay, z-index --z-menu (burger above it).
   6. Modals (#registeredTeamsModal, #voteModal, .card-modal-overlay), z-index --z-modal.

   Keep markup order in base.html: nav.site-nav → {% block content %} → footer.site-footer → modals → scripts.

   ────────────────────────────────────────────────────────────────────────────────

   7. LAYOUT, GRID, SPACING

   • Container: width: min(100% - 2 * var(--gutter), var(--container)); margin-inline: auto;
   • Desktop grids: 12 columns, gap: clamp(1rem, 2vw, 2rem).
   • Section vertical rhythm: padding-block: var(--section-y).
   • Diagonal seams between alternating sections (signature move) — apply to alternating bands:
   ```css
     .section--alt {
       background: var(--ink-2);
       clip-path: polygon(0 0, 100% var(--seam), 100% 100%, 0 100%);
       margin-top: calc(-1 * var(--seam));
       padding-top: calc(var(--section-y) + var(--seam));
     }
   ```

   • Section heading pattern (reuse everywhere): mono kicker (e.g. // 01 — TEAMS) in --volt, then H2 in
     --fs-display-lg, italic 800, uppercase, paper; optional outlined ghost word behind (-webkit-text-stroke: 2px
     var(--line); color: transparent).

   ────────────────────────────────────────────────────────────────────────────────

   8. SHAPE LANGUAGE

   • Corner cuts via --btn-clip / --card-clip (§5). No other radii.
   • Hard offset shadow (hover accents only): filter: drop-shadow(6px 6px 0 var(--volt)) — NEVER box-shadow on clipped
     elements.
   • Outlined display text: -webkit-text-stroke: 2px var(--paper); color: transparent; (ghost numerals/words use
     var(--line) stroke).
   • Frames/borders: 1px solid var(--line); interactive elements 1px solid var(--line-strong); emphasis 2px solid
     var(--volt).

   ────────────────────────────────────────────────────────────────────────────────

   9. BACKGROUND & TEXTURE (exact)

   Remove ALL legacy radial blobs and the grid overlay. New fixed court-lines layer on body::before — inline SVG data
   URI, real volleyball-court geometry (18×9 m, attack lines at 3 m → x=600/1200 of 1800):

   ```
     url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1800 900'%3E%3Cg fill='none'
   stroke='%23F4F4EF' stroke-opacity='0.05' stroke-width='4'%3E%3Crect x='8' y='8' width='1784' height='884'/%3E%3Cline
   x1='900' y1='8' x2='900' y2='892'/%3E%3Cline x1='600' y1='8' x2='600' y2='892'/%3E%3Cline x1='1200' y1='8' x2='1200'
   y2='892'/%3E%3C/g%3E%3C/svg%3E")
   ```

   body::before { content:''; position: fixed; inset: 0; z-index: var(--z-bg); pointer-events: none; background-image:
   <svg above>; background-repeat: no-repeat; background-position: center 12vh; background-size: min(1500px, 140vw)
   auto; }

   Optional hatch utility for alt bands/stickers: .hatch { background-image: repeating-linear-gradient(135deg,
   rgba(244,244,239,0.06) 0 1px, transparent 1px 10px); } — the ONLY permitted gradient.

   ────────────────────────────────────────────────────────────────────────────────

   10. COMPONENTS (exact specs)

   10.1 Top nav (.site-nav)

   • position: sticky; top: 0; height: var(--nav-h); background: var(--ink); border-bottom: 1px solid var(--line);
     z-index: var(--z-nav); NO blur, NO translucency. .scrolled state: border-bottom-color: var(--volt); (2px) —
     nothing else changes.
   • Inner: 3-zone flex — logo left / links center / controls right, gap: 24px, height 100%, container gutter.
   • Logo: logo.png height 34px (NO drop-shadow filter) + wordmark POCKET ACES Barlow 800 italic 20px, uppercase, ls
     0.04em, paper.
   • Links .site-nav__link: Barlow 600, 17px, uppercase, ls 0.10em, --muted; padding 10px 12px; position relative.
     Hover: paper + a 8×8px --volt square ::before at left (-14px). .active: paper with 3px volt underline (box-shadow:
     inset 0 -3px 0 var(--volt) — inset, un-clipped, allowed).
   • CTA .site-nav__cta: primary button skin (§10.3), height 40px.
   • Language toggle #langToggle: segmented control, border: 1px solid var(--line-strong), height 40px, mono 12px.
     .site-nav__lang-opt padding 0 12px, --muted; .active: background: var(--volt); color: var(--ink);. Separator
     hidden.
   • Burger #navBurger (<1024px only): 44×44px, border: 1px solid var(--line-strong), radius 0, 3 bars 18×2px paper,
     gap 5px, transitions 200ms --ease-out. Open (body.menu-open or existing aria state — match current JS): bar1
     translateY(7px) rotate(45deg), bar2 opacity: 0, bar3 translateY(-7px) rotate(-45deg).
   • Mobile menu: full-viewport background: var(--ink); border-left: 2px solid var(--volt); slide-in transform:
     translateX(100%) → 0, 280ms --ease-hard. Links: Barlow 800 italic 44px uppercase, staggered entrance 60ms. Keep
     #navOverlay: background: rgba(10,12,14,0.7) — NO blur.

   10.2 Buttons

   • .btn base: display:inline-flex; align-items:center; justify-content:center; gap:10px; height:52px; padding:0 26px;
     font: 700 20px/1 var(--font-display); text-transform:uppercase; letter-spacing:0.06em; clip-path: var(--btn-clip);
     border:2px solid transparent; cursor:pointer; transition (140ms --ease-out, explicit): transform,
     background-color, color, border-color, filter.
   • Primary (.btn-primary, .btn-cta, .site-nav__cta, .reg-btn): background: var(--volt); color: var(--ink);
     border-color: var(--volt); Hover: transform: translate(-3px,-3px); filter: drop-shadow(6px 6px 0 var(--paper));
     Active: translate(0,0); filter:none;
   • Ghost (.btn-outline, .rt-link-text): background: transparent; color: var(--paper); border-color:
     var(--line-strong); Hover: background: var(--volt); color: var(--ink); border-color: var(--volt); transform:
     translate(-3px,-3px); filter: drop-shadow(6px 6px 0 rgba(216,255,0,0.35));
   • Disabled/closed (.btn-cta--closed): background: var(--ink-3); color: var(--muted); border-color: var(--line); +
     mono label, no hover.
   • NO shimmer, NO gradient, NO glow blur.

   10.3 Hero (<section class="hero" id="hero">) — asymmetric overlap

   Desktop (≥1024px): 12-col grid, left span 7, right span 5, min-height: calc(100svh - var(--nav-h)), align-items:
   end, padding-bottom clamp(3rem, 6vh, 6rem).
   • Label .hero-label: mono 12px, uppercase, ls 0.14em, --volt text, border: 1px solid var(--volt); padding: 8px 14px;
      NO background fill. Text: SAT 26.09.2026 • 09:00 • OUTDOOR COURT BY DORMITORY NO. 8 (via existing
     data-i18n="hero.label").
   • H1: keep .hero-title__stage/__line structure (intro POCKET/ACES → final COURT/CUP 2). Each line: --fs-display-xl,
     Barlow 800 italic, uppercase, line-height: 0.86; letter-spacing: 0.01em; Line 1 solid paper; line 2 solid --volt.
     NO gradient text. Line wrappers overflow: hidden for the masked entrance (§13). Keep aria-hidden on intro stage.
   • Lede .hero-text: Archivo 400, --fs-body, --muted, max-width: 46ch; — keep data-i18n="hero.text".
   • Scoreboard strip (restyle .hero-stats-row): display:flex; border:1px solid var(--line); background: var(--ink-2);
     Cells separated by 1px solid var(--line) dividers, padding 14px 18px. Label mono 11px uppercase muted; value
     Barlow 800 30px paper; the slots cell value --volt. Cells: DATE → 26.09 SAT · FIRST SERVE → 09:00 · ENTRY → 150 ZŁ
      · SLOTS → {{ registered_teams }}/{{ max_slots }} (keep rt-modal-trigger anchor + classes on the slots cell).
     Price markup .hero-price__value/.hero-price__label keeps its hooks.
   • CTA row .hero-btn-container: primary JOIN TOURNAMENT → {% url 'register' %} (preserve {% if registration_closed %}
      branch), ghost SEE REGISTERED TEAMS → (keep #registeredTeamsBtn.rt-modal-trigger).
   • Right: .hero-player-container keeps id. main_player.png position:absolute; bottom:-6%; right:-4%; height:112%; z
     --z-overlap. Behind it: volt block position:absolute; inset:auto 10% 0 14%; height:72%; background: var(--volt);
     transform: rotate(-3deg); + outlined ghost 02 (font: 800 italic 22rem var(--font-display); -webkit-text-stroke:
     2px var(--line-strong); color: transparent; opacity:.55; position:absolute; top:-4%; right:0; pointer-events:none;
      aria-hidden).
   • Mobile facts .hero-mobile-facts stay mobile-only: 3 cells, mono label + Barlow 800 34px value; update hardcoded
     06.06 → 26.09.
   • Scroll indicator: 1px volt line 48px tall + mono SCROLL 10px rotated 90°, pulse = 1.6s --ease-hard translateY loop
     (the only looping animation allowed besides ticker).

   10.4 Ticker / marquee (new strip directly after </section> of hero)

   Full-width, background: var(--volt); color: var(--ink); border-block: 2px solid var(--ink); transform:
   rotate(-1deg); width: 104%; margin-left: -2%; overflow: hidden; Track: flex, white-space: nowrap; animation: ticker
   24s linear infinite; duplicated content (second copy aria-hidden="true"). Items: Barlow 800 italic 24px uppercase
   ink, separator ///. Content (data-i18n ticker.items): POCKET ACES COURT CUP 2 /// SAT 26.09.2026 /// FIRST SERVE
   09:00 /// 8 TEAMS /// 150 ZŁ PER TEAM /// OUTDOOR ///  @keyframes ticker { to { transform: translateX(-50%); } }

   10.5 Fan voting board (#fan-voting, keep {% if voting_enabled %} and all loop/widthratio logic)

   • Section header per §7 pattern: kicker // FAN AWARD, H2 keeps data-i18n="voting.title", subtitle voting.subtitle.
   • .voting-board: border: 1px solid var(--line); background: var(--ink-2); Head row: mono 11px uppercase muted,
     padding 12px 18px, border-bottom 2px solid var(--volt).
   • Rows: border-top: 1px solid var(--line); padding: 14px 18px; display:grid; grid-template-columns: 64px 1fr auto
     56px; align-items:center; gap:16px; Rank: mono 700 14px --volt. Podium rows (--podium): rank cell background:
     var(--volt); color: var(--ink); + 4px volt left border.
   • Team name: Barlow 700 24px uppercase paper (link hover: volt). Logo wrap: 44×44px, border: 1px solid
     var(--line-strong), img object-fit: contain; padding: 4px; Empty state letter: Barlow 800 24px volt on ink-3.
   • Meter .voting-board__meter: height: 6px; background: var(--ink-3); Fill: background: var(--volt); width: 0 →
     data-vote-width%; transition: width 800ms var(--ease-hard); triggered in view (keep existing JS/attribute flow).
   • Score: mono 700 16px paper + mono 10px muted label.
   • Vote button .vote-btn-main: 44×44px square (NOT round), border: 1px solid var(--line-strong); background:
     transparent; color: var(--paper); heart icon (keep FA). Hover: border-color: var(--signal); color: var(--signal);
     transform: translate(-2px,-2px); box-shadow: 4px 4px 0 var(--signal); (not clipped — box-shadow OK here).
     Voted/confirmed state: background: var(--signal); color: var(--ink); border-color: var(--signal);

   10.6 "Why Register" cards (.perspective-section--cards — keep GSAP flip mechanics + cards-swiper classes)

   • Faces: background: var(--ink-3); border: 1px solid var(--line); clip-path: var(--card-clip); NO blur, NO gradient,
     NO soft shadow.
   • Front: giant index numeral 01/02/03 — font: 800 110px var(--font-display); -webkit-text-stroke: 2px
     var(--line-strong); color: transparent; top-left; mono kicker --volt; title Barlow 700 30px uppercase paper; body
     Archivo 15px --muted.
   • Back face: background: var(--volt); color: var(--ink); title/body ink, mono details.
   • Hover (front): border-color: var(--volt); transform: translateY(-4px); transition: 160ms var(--ease-out);
   • Card modal #cardModalOverlay → modal skin §10.11.

   10.7 Location (.section--location)

   • Keep structure/hooks. Map frame .location-map: border: 1px solid var(--line-strong); iframe filter: grayscale(1)
     contrast(1.1); hover filter: none; transition: 300ms; volt 6px underline bar under the frame.
   • Info rows: mono 11px uppercase muted labels + Barlow 700 22px paper values; link .location__link: paper, volt 2px
     underline on hover.

   10.8 Arena / Venue (.section--arena)

   • Apply .section--alt diagonal seam (§7). H2 keeps data-i18n="arena.heading". Images: border: 1px solid
     var(--line-strong); with offset volt block behind (same technique as hero). Copy: Archivo --fs-body muted.

   10.9 Road / timeline (.section--road)

   • Desktop: 4 columns with 2px --line top connector; nodes = 14px volt squares on the line. Mobile: vertical, left
     rail.
   • Each .road-item: date .road-item__date mono 700 13px --volt uppercase; title Barlow 700 24px uppercase paper; desc
     Archivo 14px muted.
   • Content (mark every date <!-- [CONFIRM] … -->): 01 — REGISTRATION OPEN · NOW / 02 — ROSTER LOCK · 20.09.2026 / 03
     — SCHEDULE PUBLISHED · 22.09.2026 / 04 — GAME DAY · SAT 26.09.2026. Keep all data-i18n keys; add both dict entries
     (§15).

   10.10 FAQ page (.faq-list, .faq-item, .faq-question, .faq-form — keep js hooks)

   • Item: border: 1px solid var(--line); background: var(--ink-2); margin-bottom: -1px; (collapsed hairlines).
   • Question button: full width, padding: 18px 20px; font: 600 20px var(--font-display); text-transform: uppercase;
     color: var(--paper); text-align:left; prefixed by mono volt index Q.01. Plus icon: two 14×2px paper bars; .open →
     rotate 45° (becomes ×), 200ms --ease-out.
   • Answer: padding: 0 20px 20px 20px; border-left: 2px solid var(--volt); margin-left: 20px; font: 400 15px
     var(--font-body); color: var(--muted); open animation = max-height 300ms --ease-out (keep existing JS class
     toggle).
   • Question form .faq-form__card: panel skin (border:1px solid var(--line); background: var(--ink-2); padding:
     clamp(1.5rem,3vw,3rem);), inputs per §10.12, submit = primary button. Keep faq.js selectors and success-message
     flow.

   10.11 Modals (#registeredTeamsModal, #voteModal, .card-modal-overlay)

   • Overlay: position: fixed; inset: 0; background: rgba(10,12,14,0.82); z-index: var(--z-modal); NO backdrop blur.
     Entrance: content transform: translateY(24px); opacity: 0 → none/1, 240ms --ease-out.
   • Content .rt-modal__content: background: var(--ink-2); border: 2px solid var(--paper); clip-path: polygon(0 0,
     calc(100% - 24px) 0, 100% 24px, 100% 100%, 24px 100%, 0 calc(100% - 24px)); padding: 28px; max-width: 640px;
   • Title: Barlow 800 italic 34px uppercase paper (volt <i> icon allowed). Subtitle: mono 12px muted uppercase.
   • Close .rt-modal__close: 44×44px square, border: 1px solid var(--line-strong), × 20px paper; hover volt border +
     volt ×.
   • Registered-teams table: header row mono 11px uppercase muted, border-bottom: 2px solid var(--volt); rows
     border-top: 1px solid var(--line); padding: 12px 0; rank mono volt; .rt-in-tournament rank cell = volt block / ink
     text; .rt-reserve rows muted; row hover background: var(--ink-3).
   • Vote form: input per §10.12, submit primary; status messages: success --ok, error --danger, mono 12px. Keep every
     id/name/endpoint (/api/vote/) untouched.

   10.12 Forms (register page .reg-* — keep ALL ids/classes/step logic)

   • Layout ≥1024px: grid-template-columns: 5fr 7fr; gap: clamp(2rem,4vw,4rem); Left brand panel sticky (position:
     sticky; top: calc(var(--nav-h) + 24px);): H1 JOIN THE COURT (--fs-display-lg, italic 800), mono fact list
     (date/venue/fee/slots), step legend 01 SQUAD · 02 CAPTAIN · 03 CONFIRM mono with volt current marker. Right: form
     panel border: 1px solid var(--line); background: var(--ink-2); padding: clamp(1.5rem,3vw,3rem);
   • Stepper: 3 segments with mono numerals; #stepperFill height: 4px; background: var(--volt); transition: width 400ms
     var(--ease-hard); (JS sets width — do not change). .reg-step done/current: volt square node; upcoming: --line
     node, muted label.
   • Labels .reg-label: mono 11px uppercase ls 0.12em --muted, margin-bottom: 6px.
   • Inputs/selects/textareas: height: 48px; width: 100%; background: transparent; border: 1px solid
     var(--line-strong); border-radius: 0; color: var(--paper); font: 400 15px var(--font-body); padding: 0 14px;
     Focus: border-color: var(--volt); outline: 2px solid var(--volt); outline-offset: 0; Placeholder: --muted at 60%.
   • .reg-field { margin-bottom: 18px; } Error state: border-color: var(--danger); + mono 11px --danger message under
     field.
   • Roster rows .roster-row: display: grid; grid-template-columns: 1fr 1fr; gap: 12px;
   • Checkboxes .reg-check input: appearance: none; width: 20px; height: 20px; border: 1px solid var(--line-strong);
     checked: background: var(--volt); + inline SVG check (ink) as background-image; focus-visible same outline as
     inputs.
   • Logo upload .reg-logo-upload: dashed 1px dashed var(--line-strong) drop zone, mono hint; hover border-color:
     var(--volt).
   • Buttons .reg-btn, .reg-btn--next: primary skin §10.2, width 100% on mobile.
   • Success #stepSuccess: giant YOU'RE IN. Barlow 800 italic --fs-display-lg volt + mono confirmation copy; no
     confetti libs.
   • All copy through existing data-i18n keys; keep /api/register/ fetch logic, CSRF header handling, validation and
     step JS 100% intact.

   10.13 Footer (.site-footer)

   • background: var(--ink-2); border-top: 2px solid var(--volt); NO blur, NO gradient overlays.
   • Top zone: giant outlined wordmark POCKET ACES — font: 800 italic clamp(3rem,10vw,9rem)/0.9 var(--font-display);
     -webkit-text-stroke: 2px var(--line-strong); color: transparent; hover: color: var(--paper); transition: 300ms;
     (aria-hidden decorative, keep <img class="site-footer__skylogo"> out or height 28px mono-adjacent).
   • Grid 3 cols ≥768px (Navigation / Documents / Connect), 1 col mobile, gap 32px.
   • Column headings .site-footer__heading: mono 11px uppercase ls 0.14em --volt.
   • Links: mono 12px --muted, padding-block: 6px, hover paper + volt → prefix. Keep all document hrefs (PDFs) exactly
     — never rename asset files; labels keep data-i18n.
   • Socials: 44×44px squares, border: 1px solid var(--line-strong), FA icons 16px paper; hover background:
     var(--volt); color: var(--ink); border-color: var(--volt);
   • Contact email: Barlow 700 24px paper, hover volt.
   • Bottom bar: border-top: 1px solid var(--line); mono 11px muted, space-between: © 2026 POCKET ACES SPORT CLUB / SAT
     26.09.2026 · OUTDOOR.

   10.14 Secondary pages (team_detail.html, roster_update.html, vote_success/error, pivate_policy_en.html,
   match-centre/gallery if present)

   • They inherit the token layer automatically via brutal.css. Reskin their local components to the same language:
     page-hero H1 --fs-display-lg italic with mono volt kicker; panels = border:1px solid var(--line); background:
     var(--ink-2);; tables/lists = voting-board pattern; any leftover pink/glass classes map to §2 purge. Do not
     restructure their data flow.

   ────────────────────────────────────────────────────────────────────────────────

   11. MOTION SYSTEM (exact)

   • Easings/durations: ONLY the tokens in §5. Hover ≤160ms. Entrances 400–900ms. Stagger 60–120ms.
   • Hero timeline (GSAP already loaded; tune values in config.js, keep selectors): label y:16, opacity:0 → in, 400ms;
     H1 lines yPercent:110 → 0 inside overflow-hidden wrappers, 700ms, stagger 120ms, power4.out (≈ --ease-out);
     intro→final stage swap = hard clip-path wipe (no fades); strip + CTAs y:20 → 0, 400ms, stagger 80ms; player
     xPercent:8 → 0, 800ms. Total hero ≤ 2.2s.
   • Scroll reveals: add data-reveal to section headers, cards, rows. GSAP + ScrollTrigger: from { y: 36, clipPath:
     'inset(0 0 100% 0)' } to identity, 600ms --ease-out, start: 'top 88%', once: true, batch stagger 80ms. If GSAP
     fails to load, everything must be visible by default (no hidden-by-default CSS).
   • Voting meters: width animates on enter viewport, 800ms --ease-hard (existing data-vote-width flow).
   • Ticker: §10.4. Scroll indicator: §10.3. These two loops are the ONLY infinite animations.
   • prefers-reduced-motion: reduce → *, *::before, *::after { animation: none !important; transition: none !important;
     }, ticker static, all reveals visible.

   ────────────────────────────────────────────────────────────────────────────────

   12. RESPONSIVE MATH (copy these breakpoints)

   Fluid base already covers 320→1440 via clamp(). Explicit overrides:

   ┌────────────┬─────────────────────────────────────────────────────────────────────────────────────────────────────┐
   │ Breakpoint │ Overrides                                                                                           │
   ├────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
   │ ≤480px     │ --fs-display-xl: clamp(3.4rem, 17vw, 4.6rem); hero stacked, player img absolute behind content      │
   │            │ opacity: .22; scoreboard strip 2×2 grid; CTAs full-width column; ticker 18px; voting row            │
   │            │ grid-template-columns: 40px 1fr 48px (score wraps under name)                                       │
   ├────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
   │ ≤767px     │ burger nav; .hero-mobile-facts visible; timeline vertical; footer 1 col; modals margin: 16px;       │
   │            │ max-height: 85svh; overflow:auto                                                                    │
   ├────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
   │ 768–1023px │ hero left spans 12, player right-anchored height: 60vh; opacity:.35; cards 2-col                    │
   ├────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
   │ ≥1024px    │ full nav, hero 7/5 split per §10.3                                                                  │
   ├────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
   │ ≥1440px    │ --container: 1440px; --fs-display-xl: 12rem; --section-y: 9.5rem                                    │
   ├────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
   │ ≥1920px    │ --container: 1600px; --fs-display-xl: 12.5rem; --gutter: 5rem                                       │
   ├────────────┼─────────────────────────────────────────────────────────────────────────────────────────────────────┤
   │ ≥2560px    │ --container: 1760px; --fs-display-xl: 14rem; --gutter: 6rem                                         │
   └────────────┴─────────────────────────────────────────────────────────────────────────────────────────────────────┘

   Rules: NO horizontal scrollbar at any width (rotated ticker is contained by its negative-margin technique; ghost
   numerals overflow: hidden on sections). Touch targets ≥ 44px. 100svh for viewport locks (never raw 100vh on mobile).

   ────────────────────────────────────────────────────────────────────────────────

   13. i18n CONTENT UPDATES (EN/PL — exact)

   Mechanism stays byte-identical: dictionary T + MOBILE_TEXT_OVERRIDES in static/js/navbar.js, data-i18n/data-i18n-ph
   attributes, localStorage.pa_lang, pa_lang_change event. You may ONLY edit dictionary STRING VALUES and add keys
   (always to BOTH en and pl).

   Required string updates (outdated June dates → 26.09.2026):
   • hero.label — EN: SAT 26.09.2026 • 09:00 • OUTDOOR COURT BY DORMITORY NO. 8 / PL: SOB 26.09.2026 • 09:00 • BOISKO
     PLENEROWE PRZY DS NR 8
   • hero.text — EN: Registration is open for Pocket Aces Court Cup 2. Outdoor volleyball, 8 teams, first serve at
     09:00 on Saturday, September 26, 2026. Lock your spot before registration closes. / PL: Rejestracja na Pocket Aces
     Court Cup 2 jest otwarta. Gramy na zewnątrz, limit to 8 drużyn, pierwsze podanie 26 września 2026 o 09:00. Zapisz
     ekipę przed zamknięciem rejestracji.
   • New keys: ticker.items (EN/PL per §10.4; PL: POCKET ACES COURT CUP 2 /// SOBOTA 26.09.2026 /// PIERWSZE PODANIE
     09:00 /// 8 DRUŻYN /// 150 ZŁ OD DRUŻYNY /// NA ZEWNĄTRZ ///), road.* step dates per §10.9.
   • Then AUDIT: grep -rniE "june|czerw|06\.06|June 3|3 czerwca" tournament/templates static/js → every hit updated or
     commented <!-- [CONFIRM] -->. Do NOT rename PDF filenames that contain "czerwec" (asset paths stay).
   • Template <html lang="en"> stays; JS already switches document.documentElement.lang. Default <title>: Pocket Aces
     Court Cup 2 — 26.09.2026.

   ────────────────────────────────────────────────────────────────────────────────

   14. ACCESSIBILITY & PERFORMANCE

   • Focus-visible everywhere: outline: 2px solid var(--volt); outline-offset: 2px;
   • All interactive elements keyboard-reachable; modals keep Escape-to-close; burger keeps aria-expanded.
   • Contrast per §5 "Color law" — do not introduce unchecked pairs.
   • Images: explicit width/height or aspect-ratio; main_player.png fetchpriority="high" in hero; below-fold images
     loading="lazy".
   • No layout shift from fonts: font-display: swap (in the Google URL) + fallback stacks metric-compatible (Arial
     Narrow for condensed).
   • Ship no new dependencies; total new CSS ≈ one file (brutal.css).

   ────────────────────────────────────────────────────────────────────────────────

   15. FILE-BY-FILE EXECUTION PLAN (in this order)

   1. static/css/brutal.css — CREATE: tokens (§5), base resets, background layer (§9), all component styles (§10),
      motion utilities (§11), breakpoints (§12).
   2. tournament/templates/base.html — DELETE the entire legacy inline <style>; swap Montserrat link for the §4 font
      URL; add <link rel="stylesheet" href="{% static_v 'css/brutal.css' %} AFTER all other stylesheets; apply
      nav/footer markup classes per §10.1/§10.13 (keep every id/hook); fix tournament_hub/tournament_gallery with the
      non-raising {% url … as … %} pattern; update <title>.
   3. tournament/templates/tournament/index.html — purge inline legacy styles that violate §2/§3; restyle hero per
      §10.3 (keep all hooks); insert ticker (§10.4); add data-reveal attributes; update 06.06 → 26.09;
      voting/cards/location/arena/road classes per §10.5–§10.9.
   4. tournament/templates/tournament/register.html — reskin per §10.12 (zero logic changes).
   5. tournament/templates/tournament/faq.html, team_detail.html, roster_update.html, vote_success.html,
      vote_error.html, pivate_policy_en.html — reskin per §10.10/§10.14.
   6. static/css/styles.css, registered-teams.css, sports-bg.css, sports-preview.css, arena-editorial.css — remove the
      pink/glass/radius violations found by the §18 greps; let brutal.css win the cascade (it loads last).
   7. static/scss/_variables.scss — mirror the new token values (hygiene only; the served .css files are
      authoritative).
   8. static/js/navbar.js — dictionary string edits ONLY (§13).
   9. static/js/config.js — timing/ease values ONLY (§11). No selector/logic edits anywhere in JS.
   10. vol_registr/settings.py — bump STATIC_ASSET_VERSION default to 'arena-2026-09-v1' (cache-bust). Nothing else in
       settings.

   ────────────────────────────────────────────────────────────────────────────────

   16. ACCEPTANCE GATES (run all of these; report results)

   Static greps (Git Bash from repo root — every one must return ZERO hits):

   ```
     grep -rniE "#e41561|#ff2d7a|#f34082|brand-pink|228, ?21, ?97" tournament/templates static/css static/scss
   static/js
     grep -rni "backdrop-filter" tournament/templates static/css static/scss
     grep -rniE "border-radius:[^;]*(999|50%)" tournament/templates static/css/brutal.css
     grep -rni "montserrat" tournament/templates static/css static/scss
     grep -rniE "transition:[^;]*\ball\b" tournament/templates static/css static/scss
     grep -rniE "june|czerw" tournament/templates static/js   # only PDF filenames + [CONFIRM] comments may remain
   ```

   Runtime:

   ```
     python manage.py check                      # must pass
     python manage.py runserver                  # then GET / /register/ /faq/ /roster/ /privacy-policy/ → all 200
   ```

   Manual/visual checklist:
   • EN↔PL toggle switches EVERY data-i18n string with no missing-key leftovers; Zażółć gęślą jaźń renders correctly in
     all three fonts.
   • Register flow completes end-to-end (3 steps → success), vote modal opens/submits, registered-teams modal opens,
     FAQ accordion works, mobile menu works.
   • 320px and 2560px viewports: no horizontal scroll, hero intact, ticker contained.
   • No pink pixel anywhere; no blur anywhere; volt/ink contrast spot-check passes.
   • prefers-reduced-motion emulation: page fully visible, zero animation.

   If any grep command returns a match, you must automatically fix the violation and run the check again before telling me you are done.
   Definition of done = every gate green. Do not declare completion while any grep returns hits or any page errors.

   ```