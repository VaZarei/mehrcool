/**
 * Cookie consent: GTM / GA4 load only after the visitor accepts. The choice is
 * kept in localStorage; "Cookie settings" links ([data-cookie-settings]) reopen the banner.
 */
const KEY = "mc_cookie_consent";
const ID_PATTERN = /^[A-Za-z0-9_-]+$/;

function loadScript(src) {
  const s = document.createElement("script");
  s.async = true;
  s.src = src;
  document.head.appendChild(s);
}

function loadAnalytics({ gtm, ga4 }) {
  window.dataLayer = window.dataLayer || [];
  if (gtm && ID_PATTERN.test(gtm)) {
    window.dataLayer.push({ "gtm.start": Date.now(), event: "gtm.js" });
    loadScript(`https://www.googletagmanager.com/gtm.js?id=${gtm}`);
  }
  if (ga4 && ID_PATTERN.test(ga4)) {
    window.gtag = function gtag() {
      window.dataLayer.push(arguments);
    };
    window.gtag("js", new Date());
    window.gtag("config", ga4, { anonymize_ip: true });
    loadScript(`https://www.googletagmanager.com/gtag/js?id=${ga4}`);
  }
}

function showBanner(ids) {
  if (document.getElementById("cookie-banner")) return;
  const box = document.createElement("div");
  box.id = "cookie-banner";
  box.setAttribute("role", "dialog");
  box.setAttribute("aria-label", "Cookie consent");
  box.style.cssText =
    "position:fixed;left:1rem;right:1rem;bottom:1rem;z-index:10000;max-width:42rem;margin:0 auto;" +
    "padding:1rem 1.25rem;background:#fff;color:#111;border:1px solid #ccc;border-radius:12px;" +
    "box-shadow:0 8px 30px rgba(0,0,0,.2);font:15px/1.5 system-ui,sans-serif;";
  const text = document.createElement("p");
  text.style.margin = "0 0 .75rem";
  text.append("We use analytics cookies to understand how the site is used. They are off unless you accept. See our ");
  const link = document.createElement("a");
  link.href = "/cookies/";
  link.textContent = "cookie policy";
  text.append(link, ".");
  const row = document.createElement("div");
  row.style.cssText = "display:flex;gap:.75rem;flex-wrap:wrap;";
  const make = (label, value) => {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = label;
    b.style.cssText =
      "padding:.6rem 1.1rem;border-radius:8px;border:1px solid #1e2c66;background:#1e2c66;color:#fff;font:inherit;cursor:pointer;";
    b.addEventListener("click", () => {
      localStorage.setItem(KEY, value);
      box.remove();
      if (value === "granted") loadAnalytics(ids);
    });
    return b;
  };
  row.append(make("Accept analytics", "granted"), make("Reject", "denied"));
  box.append(text, row);
  document.body.appendChild(box);
}

export function initConsent() {
  const meta = document.querySelector('meta[name="analytics-ids"]');
  if (!meta) return;
  const ids = { gtm: meta.dataset.gtm, ga4: meta.dataset.ga4 };
  const choice = localStorage.getItem(KEY);
  if (choice === "granted") loadAnalytics(ids);
  else if (choice !== "denied") showBanner(ids);
  document.addEventListener("click", (event) => {
    if (!event.target.closest("[data-cookie-settings]")) return;
    localStorage.removeItem(KEY);
    showBanner(ids);
  });
}
