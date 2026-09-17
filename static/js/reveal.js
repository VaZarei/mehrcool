/**
 * Scroll-in reveal: adds .is-visible once, when an element enters the viewport.
 * Motion itself lives in CSS (opacity + 12px translate, critically damped) and is
 * disabled entirely under prefers-reduced-motion.
 */
export function initReveal() {
  const items = document.querySelectorAll(".reveal");
  if (!items.length) return;

  if (!("IntersectionObserver" in window) || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    items.forEach((el) => el.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      for (const entry of entries) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      }
    },
    { rootMargin: "0px 0px -8% 0px", threshold: 0.05 }
  );
  items.forEach((el) => observer.observe(el));
}
