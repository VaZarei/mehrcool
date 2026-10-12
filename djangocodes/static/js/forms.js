/**
 * Form enhancements on top of HTMX: after a fragment swap, move focus to the
 * first error or the success heading so screen-reader users hear the result,
 * and scroll it into view without a jump.
 */
export function initForms() {
  document.body.addEventListener("htmx:afterSwap", (event) => {
    const region = event.detail.target;
    if (!region?.matches?.("[data-form-region]")) return;
    const focusTarget =
      region.querySelector(".field--error input, .field--error select, .field--error textarea") ||
      region.querySelector("[data-focus]");
    if (focusTarget) {
      focusTarget.setAttribute("tabindex", focusTarget.tabIndex >= 0 ? focusTarget.tabIndex : "-1");
      focusTarget.focus({ preventScroll: true });
      focusTarget.scrollIntoView({ block: "center", behavior: "smooth" });
    }
  });

  // Instant press feedback on submit buttons is CSS; here we just prevent double submits without HTMX.
  document.querySelectorAll("form[data-once]").forEach((form) => {
    form.addEventListener("submit", () => {
      const button = form.querySelector('[type="submit"]');
      if (button) button.setAttribute("aria-disabled", "true");
    });
  });
}
