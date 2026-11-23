// bring-the-humans-03 — "Bring the humans with a TikTok ad".
// Entrypoint: copy VIDEO.json into the output dir. The video itself is the
// entry; the house reads the TikTok post from VIDEO.json and counts its views.
// The ad video was rendered in this session by tools/render_ad.py.
import { copyFileSync, mkdirSync, readFileSync } from "node:fs";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = resolve(process.env.MAKEFUN_OUTPUT_DIR ?? join(here, "out"));
const videoPath = join(here, "VIDEO.json");

const raw = readFileSync(videoPath, "utf8");
const video = JSON.parse(raw) as { url?: unknown };
if (
  typeof video.url !== "string" ||
  !/^https:\/\/(www\.|m\.)?tiktok\.com\/@[^/]+\/video\/\d+$/.test(video.url)
) {
  throw new Error(
    'VIDEO.json must hold {"url": "https://www.tiktok.com/@<handle>/video/<id>"}',
  );
}

// Only create the output dir — never remove it (the grader runs as an
// unprivileged user on a read-only filesystem with /output mounted).
mkdirSync(outDir, { recursive: true });
copyFileSync(videoPath, join(outDir, "VIDEO.json"));
console.log(`wrote VIDEO.json -> ${join(outDir, "VIDEO.json")} (${video.url})`);
