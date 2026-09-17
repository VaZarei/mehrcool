/**
 * Sticky header: condenses once content scrolls underneath it, closes the
 * mobile menu on Escape / outside tap, and keeps the state in sync with scroll
 * position without layout thrash (a sentinel + IntersectionObserver, no scroll
 * handler).
 */
export function initHeader() {
  const header = document.querySelector("[data-header]");
  if (!header) return;

  const sentinel = document.createElement("div");
  sentinel.setAttribute("aria-hidden", "true");
  sentinel.style.cssText = "position:absolute;top:0;left:0;width:1px;height:1px;pointer-events:none;";
  header.before(sentinel);

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      ([entry]) => header.classList.toggle("is-condensed", !entry.isIntersecting),
      { rootMargin: "-48px 0px 0px 0px", threshold: 0 }
    );
    observer.observe(sentinel);
  }

  const menu = header.querySelector("[data-menu]");
  if (!menu) return;

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menu.open) {
      menu.open = false;
      menu.querySelector("summary")?.focus();
    }
  });

  document.addEventListener("pointerdown", (event) => {
    if (menu.open && !menu.contains(event.target)) menu.open = false;
  });

  // Lock body scroll while the sheet is open on small screens.
  menu.addEventListener("toggle", () => {
    document.documentElement.style.overflow = menu.open && window.innerWidth < 1024 ? "hidden" : "";
  });
}
