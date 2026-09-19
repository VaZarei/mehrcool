/**
 * Hero video: the poster is always in the HTML; video <source> elements are only
 * attached when the viewport is desktop-sized, the user has not asked for reduced
 * motion or reduced data, and the connection is not constrained. Nothing is
 * downloaded otherwise, so phones on 4G get a still image only.
 */
export function initHeroVideo() {
  const hero = document.querySelector("[data-hero]");
  const video = hero?.querySelector("[data-hero-video]");
  if (!hero || !video) return;

  const sources = JSON.parse(video.dataset.sources || "[]");
  if (!sources.length) return;

  const wantsVideo =
    window.matchMedia("(min-width: 100px)").matches &&
    !window.matchMedia("(prefers-reduced-motion: reduce)").matches &&
    !navigator.connection?.saveData &&
    !/(^|-)2g$/.test(navigator.connection?.effectiveType || "");

  if (!wantsVideo) return;

  for (const { src, type } of sources) {
    const source = document.createElement("source");
    source.src = src;
    source.type = type;
    video.append(source);
  }

  hero.classList.add("has-video");
  video.addEventListener("playing", () => video.classList.add("is-playing"), { once: true });
  video.load();
  const attempt = video.play();
  if (attempt?.catch) attempt.catch(() => {});

  const toggle = hero.querySelector("[data-hero-toggle]");
  if (!toggle) return;
  const label = toggle.querySelector("[data-hero-toggle-label]");
  const sync = () => {
    const paused = video.paused;
    toggle.setAttribute("aria-pressed", String(paused));
    if (label) label.textContent = paused ? toggle.dataset.labelPlay : toggle.dataset.labelPause;
  };
  toggle.addEventListener("click", () => {
    if (video.paused) video.play().catch(() => {});
    else video.pause();
  });
  video.addEventListener("play", sync);
  video.addEventListener("pause", sync);
  sync();
}
