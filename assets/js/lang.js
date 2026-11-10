/* RBM — language handling + mobile menu.
 * No dependencies. Progressive enhancement: the site works fully
 * without JS; this script only adds language auto-detection on the
 * root page, manual preference persistence, anchor-preserving language
 * links and the mobile menu toggle.
 *
 * In Node (tests), this file exports the pure helpers and never touches
 * the DOM:  require("../assets/js/lang.js")  →  { pickLanguage, normalizeTag }
 */
(function () {
  "use strict";

  var STORAGE_KEY = "rbm-pref-lang";
  var LEGACY_STORAGE_KEY = "bytetsc-pref-lang";
  var SUPPORTED = ["ja", "en", "pt"];
  var ROOT_FALLBACK = "ja";

  /* Return the base language of a BCP-47 tag: "en-US" -> "en", "pt-BR" -> "pt". */
  function normalizeTag(tag) {
    return String(tag || "").toLowerCase().split("-")[0];
  }

  /* Pick the first supported language from a list of BCP-47 tags,
   * ignoring regional variants. Falls back to Japanese when nothing
   * matches, the list is empty or the input is unusable. */
  function pickLanguage(locales) {
    if (!locales) { return ROOT_FALLBACK; }
    if (typeof locales !== "object" || typeof locales.length !== "number") {
      locales = [locales];
    }
    for (var i = 0; i < locales.length; i++) {
      var base = normalizeTag(locales[i]);
      if (SUPPORTED.indexOf(base) !== -1) { return base; }
    }
    return ROOT_FALLBACK;
  }

  /* --- Node / non-DOM environment: expose pure helpers and stop here. --- */
  if (typeof window === "undefined" || typeof document === "undefined") {
    if (typeof module !== "undefined" && module.exports) {
      module.exports = { pickLanguage: pickLanguage, normalizeTag: normalizeTag };
    }
    return;
  }

  /* Storage may be unavailable (private mode, blocked cookies, file://). */
  function readSaved() {
    try {
      var v = window.localStorage.getItem(STORAGE_KEY);
      if (SUPPORTED.indexOf(v) !== -1) { return v; }
      var legacy = window.localStorage.getItem(LEGACY_STORAGE_KEY);
      if (SUPPORTED.indexOf(legacy) !== -1) {
        savePref(legacy);
        return legacy;
      }
      return null;
    } catch (e) { return null; }
  }
  function savePref(lang) {
    try { window.localStorage.setItem(STORAGE_KEY, lang); } catch (e) { /* ignore */ }
  }

  /* --- Root page: honor manual choice first, then browser languages. ---
   * The root page itself IS the Japanese page, so we only ever redirect
   * away from "/" (never back to it): no redirect loops are possible.
   * Localized pages like "/en/" are never redirected automatically. */
  var rootEl = document.documentElement;
  if (rootEl.getAttribute("data-root-page") === "true") {
    var saved = readSaved();
    var target = saved;
    if (!target) {
      var locales = null;
      try { locales = navigator.languages || [navigator.language]; } catch (e) { locales = null; }
      target = pickLanguage(locales);
    }
    if (target !== "ja") {
      var base = rootEl.getAttribute("data-alt-" + target) || ("/" + target + "/");
      var dest = base + window.location.search + window.location.hash;
      try { window.location.replace(dest); } catch (e) { window.location.href = dest; }
      return; // page is being replaced
    }
  }

  /* --- On every page: wire up the language switcher and menu. --- */
  function init() {
    var pageLang = normalizeTag(document.documentElement.lang || "ja");
    var toggled = false;

    var switchers = document.querySelectorAll("[data-lang-switch]");
    for (var s = 0; s < switchers.length; s++) {
      var links = switchers[s].querySelectorAll("a[data-lang]");
      for (var i = 0; i < links.length; i++) {
        var link = links[i];
        var lang = link.getAttribute("data-lang");
        if (!lang) { continue; }
        if (normalizeTag(lang) === pageLang) {
          link.setAttribute("aria-current", "true");
        }
        /* Manual clicks always win over auto-detection. */
        link.addEventListener("click", function () {
          savePref(this.getAttribute("data-lang"));
        });
        /* Refresh at click time and on hash changes after same-page navigation. */
        var updateHref = function (node) {
          var alt = rootEl.getAttribute("data-alt-" + normalizeTag(node.getAttribute("data-lang")));
          if (alt) { node.setAttribute("href", alt + (window.location.hash || "")); }
        };
        updateHref(link);
        link.addEventListener("click", function () { updateHref(this); });
        (function (node) {
          window.addEventListener("hashchange", function () { updateHref(node); });
        })(link);
      }
    }

    /* --- Mobile menu: closed by default only when JS is running. --- */
    var menuBtn = document.querySelector(".menu-toggle");
    var nav = document.querySelector(".site-nav");
    if (menuBtn && nav && window.matchMedia) {
      var mql = window.matchMedia("(max-width: 760px)");
      var apply = function () {
        if (!mql.matches || toggled) { return; }
        document.body.classList.add("nav-closed");
        menuBtn.setAttribute("aria-expanded", "false");
      };
      apply();
      menuBtn.addEventListener("click", function () {
        toggled = true;
        var willClose = document.body.classList.toggle("nav-closed");
        menuBtn.setAttribute("aria-expanded", willClose ? "false" : "true");
      });
      if (mql.addListener) { mql.addListener(apply); }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }

  /* Expose pure helper for in-browser debugging/tests. */
  window.RBM = window.RBM || {};
  window.RBM.pickLanguage = pickLanguage;
})();