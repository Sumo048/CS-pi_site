// Lazy media shared by Astro components and React islands.
//
// Videos are rendered with <source data-src> and data-poster, so nothing is
// fetched on first load. When a video comes within MARGIN of the viewport we
// attach the poster and sources and play it; when it leaves, we pause it.
// Large images use <img data-src> and are swapped in the same way.

const MARGIN = "300px 0px";
const reduceMotion =
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;

export function base(path: string): string {
  const b = import.meta.env.BASE_URL.replace(/\/$/, "");
  return `${b}/${path.replace(/^\//, "")}`;
}

function hydrate(v: HTMLVideoElement) {
  if (v.dataset.loaded) return;
  v.dataset.loaded = "1";
  if (v.dataset.poster) v.poster = v.dataset.poster;
  v.querySelectorAll<HTMLSourceElement>("source[data-src]").forEach((s) => {
    s.src = s.dataset.src!;
  });
  v.load();
}

let videoIO: IntersectionObserver | null = null;
function getVideoIO() {
  if (videoIO || typeof IntersectionObserver === "undefined") return videoIO;
  videoIO = new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        const v = e.target as HTMLVideoElement;
        if (e.isIntersecting) {
          hydrate(v);
          if (!reduceMotion) v.play().catch(() => {});
        } else if (!v.paused) {
          v.pause();
        }
      }
    },
    { rootMargin: MARGIN },
  );
  return videoIO;
}

/** Start observing a lazy video. Returns a cleanup function. */
export function observeVideo(v: HTMLVideoElement): () => void {
  if (reduceMotion) {
    v.removeAttribute("autoplay");
    v.controls = true;
  }
  const io = getVideoIO();
  if (!io) {
    hydrate(v);
    return () => {};
  }
  io.observe(v);
  return () => io.unobserve(v);
}

let imgIO: IntersectionObserver | null = null;
export function observeImage(img: HTMLImageElement) {
  if (typeof IntersectionObserver === "undefined") {
    img.src = img.dataset.src!;
    return;
  }
  imgIO ??= new IntersectionObserver(
    (entries) => {
      for (const e of entries) {
        if (!e.isIntersecting) continue;
        const el = e.target as HTMLImageElement;
        el.src = el.dataset.src!;
        imgIO!.unobserve(el);
      }
    },
    { rootMargin: MARGIN },
  );
  imgIO.observe(img);
}
