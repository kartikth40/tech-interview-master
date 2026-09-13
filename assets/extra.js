/* Tech Interview Master — front-end enhancements.
   Wrapped in Material's document$ so everything re-runs on instant navigation. */

(function () {
  "use strict";

  // Material for MkDocs exposes an RxJS `document$` that emits on every page
  // (including instant-nav swaps). Fall back to a plain listener if absent.
  function onPage(fn) {
    if (window.document$ && typeof window.document$.subscribe === "function") {
      window.document$.subscribe(fn);
    } else {
      document.addEventListener("DOMContentLoaded", fn);
    }
  }

  // ---- (7) Q&A tag pills ---------------------------------------------------
  // Turn inline-code tokens like `Easy`, `Med`, `Hard`, and company names into
  // styled pills. Scoped to QA-Bank pages to avoid touching real code snippets.
  var DIFFICULTY = { easy: "tim-tag--easy", med: "tim-tag--med", hard: "tim-tag--hard" };
  var COMPANIES = new Set([
    "maang", "amazon", "meta", "google", "microsoft", "apple", "startups", "netflix"
  ]);

  function tagPills() {
    if (!/\/QA-Bank\//.test(location.pathname)) return;
    document.querySelectorAll(".md-content .md-typeset code").forEach(function (code) {
      // Skip anything inside a real code block (pre) — only inline tags.
      if (code.closest("pre")) return;
      if (code.classList.contains("tim-tag")) return;
      var t = code.textContent.trim();
      var key = t.toLowerCase();
      if (DIFFICULTY[key]) {
        code.classList.add("tim-tag", DIFFICULTY[key]);
      } else if (COMPANIES.has(key)) {
        code.classList.add("tim-tag", "tim-tag--company");
      }
    });
  }

  // ---- (13) Fade-in on scroll ---------------------------------------------
  function fadeIn() {
    var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var targets = document.querySelectorAll(
      ".md-content .md-typeset > h2, .md-content .grid.cards > ul > li, .md-content .md-typeset .admonition, .md-content .md-typeset .mermaid"
    );
    if (reduce || !("IntersectionObserver" in window)) {
      targets.forEach(function (el) { el.classList.add("tim-fade", "tim-in"); });
      return;
    }
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("tim-in");
          io.unobserve(e.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    targets.forEach(function (el) {
      el.classList.add("tim-fade");
      io.observe(el);
    });
  }

  // ---- (11) Copy-button success pulse -------------------------------------
  function copyPulse() {
    document.querySelectorAll(".md-clipboard").forEach(function (btn) {
      if (btn.dataset.timPulse) return;
      btn.dataset.timPulse = "1";
      btn.addEventListener("click", function () {
        btn.classList.remove("md-clipboard--active");
        // reflow to restart the animation
        void btn.offsetWidth;
        btn.classList.add("md-clipboard--active");
        setTimeout(function () { btn.classList.remove("md-clipboard--active"); }, 500);
      });
    });
  }

  // ---- (14) Mermaid green theming -----------------------------------------
  // Material auto-renders mermaid; we set brand theme variables so diagrams
  // match the palette. Re-init + re-render for the current color scheme.
  function themeMermaid() {
    if (!window.mermaid || typeof window.mermaid.initialize !== "function") return;
    var dark = document.body.getAttribute("data-md-color-scheme") === "slate";
    var vars = dark
      ? {
          primaryColor: "#173a29", primaryBorderColor: "#4cc47e",
          primaryTextColor: "#e6f4ec", lineColor: "#4cc47e",
          secondaryColor: "#1f2b25", tertiaryColor: "#12321f",
          fontFamily: "Manrope, system-ui, sans-serif"
        }
      : {
          primaryColor: "#e9f7ef", primaryBorderColor: "#2e9e5b",
          primaryTextColor: "#123", lineColor: "#2e9e5b",
          secondaryColor: "#f2fbf6", tertiaryColor: "#eafaf1",
          fontFamily: "Manrope, system-ui, sans-serif"
        };
    try {
      window.mermaid.initialize({
        startOnLoad: false,
        theme: "base",
        themeVariables: vars,
        securityLevel: "loose"
      });
    } catch (e) { /* non-fatal */ }
  }

  onPage(function () {
    tagPills();
    copyPulse();
    fadeIn();
    themeMermaid();
  });
})();
