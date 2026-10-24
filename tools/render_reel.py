#!/usr/bin/env python3
"""Rend un Reel HTML animé en MP4 1080x1920 (30 i/s) : chaque image est capturée
en figeant toutes les animations CSS à l'instant t. Usage : render_reel.py page.html sortie.mp4 [durée_s]"""
import sys, os, pathlib, subprocess, shutil
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", "/opt/pw-browsers")
from playwright.sync_api import sync_playwright

page_path = pathlib.Path(sys.argv[1]).resolve()
out = pathlib.Path(sys.argv[2]).resolve()
dur = float(sys.argv[3]) if len(sys.argv) > 3 else 20.0
fps = 30
frames = out.parent / "frames"
shutil.rmtree(frames, ignore_errors=True); frames.mkdir(parents=True)

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto(page_path.as_uri()); pg.wait_for_timeout(500)
    pg.evaluate("document.getAnimations().forEach(a=>a.pause())")
    for i in range(int(dur * fps)):
        t = i * 1000 / fps
        pg.evaluate(f"document.getAnimations().forEach(a=>a.currentTime={t})")
        pg.screenshot(path=str(frames / f"f{i:05d}.jpg"), type="jpeg", quality=92)
    b.close()

subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(frames / "f%05d.jpg"),
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)], check=True)
print(out)
