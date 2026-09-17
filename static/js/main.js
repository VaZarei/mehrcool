/**
 * Entry module. Every behaviour is progressive enhancement: the site is fully
 * usable (phone links, forms, navigation) before this file runs or if it never does.
 */
import { initHeader } from "./header.js";
import { initHeroVideo } from "./hero-video.js";
import { initReveal } from "./reveal.js";
import { initAnalytics } from "./analytics.js";
import { initForms } from "./forms.js";

document.documentElement.classList.remove("no-js");

initHeader();
initHeroVideo();
initReveal();
initAnalytics();
initForms();
