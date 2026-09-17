/**
 * Analytics events: phone taps, WhatsApp taps, form completions and quote-wizard
 * steps. Pushes to the GTM dataLayer when present and to gtag when present.
 * Elements opt in with data-event="phone_click" (plus optional data-event-label).
 */
function track(name, params = {}) {
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({ event: name, ...params });
  if (typeof window.gtag === "function") window.gtag("event", name, params);
}

export function initAnalytics() {
  document.addEventListener(
    "click",
    (event) => {
      const el = event.target.closest("[data-event]");
      if (!el) return;
      track(el.dataset.event, {
        event_label: el.dataset.eventLabel || el.getAttribute("href") || "",
        page_path: window.location.pathname,
      });
    },
    { passive: true }
  );

  // Server-triggered events (HX-Trigger header) after a successful submission.
  document.body.addEventListener("lead:contact", () => track("generate_lead", { lead_type: "contact" }));
  document.body.addEventListener("lead:emergency", () => track("generate_lead", { lead_type: "emergency" }));
  document.body.addEventListener("quote:step", (event) =>
    track("quote_step_complete", { step: event.detail?.step ?? "" })
  );
  document.body.addEventListener("lead:quote", () => track("generate_lead", { lead_type: "quote" }));
}

export { track };
