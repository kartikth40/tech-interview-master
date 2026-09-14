/* Tech Interview Master - front-end enhancements.
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
      // Skip anything inside a real code block (pre) - only inline tags.
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

  // ---- .py link modal viewer ----------------------------------------------
  // Intercept clicks on links to .py source files and show the code in a modal
  // dialog (fetched from the raw file MkDocs already ships), instead of navigating
  // away to raw text. Progressive enhancement: if JS/fetch fails, the raw link
  // still opens. Modifier clicks (new tab) are left alone.
  var dlg = null;

  function buildDialog() {
    if (dlg) return dlg;
    dlg = document.createElement("dialog");
    dlg.className = "tim-code-modal";
    dlg.innerHTML =
      '<div class="tim-code-modal__head">' +
      '  <span class="tim-code-modal__file"></span>' +
      '  <span class="tim-code-modal__actions">' +
      '    <a class="tim-code-modal__raw" target="_blank" rel="noopener">view raw ↗</a>' +
      '    <button class="tim-code-modal__copy" type="button">Copy</button>' +
      '    <button class="tim-code-modal__close" type="button" aria-label="Close">✕</button>' +
      '  </span>' +
      '</div>' +
      '<pre class="tim-code-modal__body"><code class="language-python"></code></pre>';
    document.body.appendChild(dlg);

    dlg.querySelector(".tim-code-modal__close").addEventListener("click", function () {
      dlg.close();
    });
    // Backdrop click closes
    dlg.addEventListener("click", function (e) {
      if (e.target === dlg) dlg.close();
    });
    dlg.querySelector(".tim-code-modal__copy").addEventListener("click", function () {
      var code = dlg.querySelector("code").textContent;
      navigator.clipboard && navigator.clipboard.writeText(code);
      var b = dlg.querySelector(".tim-code-modal__copy");
      var old = b.textContent; b.textContent = "Copied!";
      setTimeout(function () { b.textContent = old; }, 1200);
    });
    return dlg;
  }

  function openModal(url, filename) {
    var d = buildDialog();
    var codeEl = d.querySelector("code");
    d.querySelector(".tim-code-modal__file").textContent = filename;
    d.querySelector(".tim-code-modal__raw").setAttribute("href", url);
    codeEl.textContent = "Loading…";
    codeEl.removeAttribute("data-highlighted");
    codeEl.className = "language-python";
    if (typeof d.showModal === "function") d.showModal(); else d.setAttribute("open", "");

    fetch(url)
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.text(); })
      .then(function (text) {
        codeEl.textContent = text;
        // highlight.js colors the runtime-fetched source (Pygments is build-time only)
        if (window.hljs && typeof window.hljs.highlightElement === "function") {
          try { window.hljs.highlightElement(codeEl); } catch (e) { /* leave plain */ }
        }
      })
      .catch(function () {
        // Fetch failed → just navigate to the raw file as a fallback.
        d.close();
        window.location.href = url;
      });
  }

  function pyModals() {
    document.querySelectorAll('.md-content a[href$=".py"]').forEach(function (a) {
      if (a.dataset.timPy) return;
      a.dataset.timPy = "1";
      a.addEventListener("click", function (e) {
        // Respect new-tab / modified clicks and let them behave normally.
        if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
        e.preventDefault();
        var url = a.getAttribute("href");
        var filename = url.split("/").pop();
        openModal(a.href, filename);
      });
    });
  }

  // ---- Interactive, persistent task-list checkboxes ------------------------
  // Material renders `- [ ]` checkboxes as disabled. Re-enable them, restore
  // saved state from localStorage (keyed per page path + position), and persist
  // on toggle so progress survives reloads and navigation. Completed items dim.
  function interactiveCheckboxes() {
    var boxes = document.querySelectorAll(".md-content .task-list-item input[type=checkbox]");
    if (!boxes.length) return;
    var pageKey = "tim:tasks:" + location.pathname;
    var saved = {};
    try { saved = JSON.parse(localStorage.getItem(pageKey) || "{}"); } catch (e) { saved = {}; }

    boxes.forEach(function (box, i) {
      box.disabled = false;
      box.style.cursor = "pointer";
      var li = box.closest(".task-list-item");
      // restore
      if (saved[i] === true) {
        box.checked = true;
        if (li) li.classList.add("tim-task-done");
      }
      if (box.dataset.timBound) return;
      box.dataset.timBound = "1";

      function persist() {
        if (li) li.classList.toggle("tim-task-done", box.checked);
        var cur = {};
        try { cur = JSON.parse(localStorage.getItem(pageKey) || "{}"); } catch (e) { cur = {}; }
        if (box.checked) cur[i] = true; else delete cur[i];
        try { localStorage.setItem(pageKey, JSON.stringify(cur)); } catch (e) { /* storage full/blocked */ }
      }
      box.addEventListener("change", persist);

      // Make the whole item's text clickable (label-style), but don't hijack
      // clicks on the checkbox itself (avoids double toggle) or on real links.
      if (li) {
        li.style.cursor = "pointer";
        li.addEventListener("click", function (e) {
          if (e.target === box) return;                 // checkbox handles itself
          if (e.target.closest("a")) return;             // let links work
          if (window.getSelection && String(window.getSelection())) return; // don't toggle on text-select
          box.checked = !box.checked;
          persist();
        });
      }
    });
  }

  onPage(function () {
    tagPills();
    copyPulse();
    fadeIn();
    themeMermaid();
    pyModals();
    interactiveCheckboxes();
  });
})();
