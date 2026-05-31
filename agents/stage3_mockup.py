"""Stage 3: Paste page images into mockup screen areas."""
import argparse, json, os, sys
import numpy as np
import cv2
from PIL import Image

def norm(path):
    """Normalize path to forward slashes for cross-platform consistency."""
    return os.path.normpath(path).replace('\\', '/')

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def list_dir(path):
    """List directory with UTF-8 encoding safety."""
    # Use os.scandir which handles Unicode better on Windows
    entries = []
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    entries.append(entry.name)
    except OSError:
        entries = os.listdir(path)
    return entries

def detect_screen_region(mockup_path):
    """Detect white screen area. Uses PIL for I/O to avoid cv2.imread Unicode issues on Windows."""
    pil_img = Image.open(mockup_path).convert('RGB')
    img = np.array(pil_img, dtype=np.uint8)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    h, w = img.shape[:2]

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 235, 255, cv2.THRESH_BINARY)
    kernel = np.ones((5, 5), np.uint8)
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=3)
    opened = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, _ = cv2.findContours(opened, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    img_area = h * w
    candidates = []
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        area = cw * ch
        area_ratio = area / img_area
        aspect = cw / ch if ch > 0 else 0

        if 0.08 < area_ratio < 0.55 and 1.2 < aspect < 2.2 and y < h * 0.7:
            ideal_aspect = 16 / 9
            aspect_score = 1.0 - min(abs(aspect - ideal_aspect) / ideal_aspect, 0.5)
            pos_score = 1.0 - abs(y / h - 0.15) * 2
            size_score = area_ratio * 3
            score = aspect_score * 0.4 + pos_score * 0.3 + size_score * 0.3
            candidates.append((score, (x, y, cw, ch)))

    if not candidates:
        return None

    candidates.sort(key=lambda t: t[0], reverse=True)
    best = candidates[0][1]
    inset = 8
    rx, ry, rw, rh = best
    rx += inset
    ry += inset
    rw -= inset * 2
    rh -= inset * 2
    return (max(0, rx), max(0, ry), max(10, rw), max(10, rh))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True)
    parser.add_argument('--mockup-dir', required=True)
    args = parser.parse_args()

    cfg = load_config(args.config)
    pages_dir = norm(cfg['pages_dir'])
    out_dir = norm(cfg['out_dir'])
    page_prefix = cfg.get('page_prefix', '')
    mockup_dir = norm(args.mockup_dir)

    if not os.path.isdir(mockup_dir):
        print(f"ERROR: Mockup directory not found: {mockup_dir}")
        sys.exit(1)

    mockup_files = sorted([f for f in list_dir(mockup_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
    print(f"Mockups ({len(mockup_files)}): {mockup_files}")

    page_files = sorted([f for f in list_dir(pages_dir) if f.lower().endswith(('.jpg', '.png', '.jpeg'))])
    if page_prefix:
        page_files = [f for f in page_files if f.startswith(page_prefix)]
    page_files = page_files[:6]
    print(f"Pages ({len(page_files)}): {page_files}")
    print(f"Output dir: {out_dir}")

    total = 0
    for mi, mf in enumerate(mockup_files):
        mockup_path = mockup_dir + '/' + mf
        mockup_name = f"样机{mi+1:02d}"
        print(f"\n--- {mockup_name} ({mf}) ---")
        for pi, pf in enumerate(page_files):
            page_path = pages_dir + '/' + pf
            fname = f"{mockup_name}-page-{pi+1:02d}.jpg"
            out_path = out_dir + '/' + fname

            try:
                mockup = Image.open(mockup_path).convert('RGBA')
                page = Image.open(page_path).convert('RGB')

                screen_rect = detect_screen_region(mockup_path)
                if screen_rect is None:
                    print(f"  WARN: No screen detected in {mf}, skip")
                    continue

                sx, sy, sw, sh = screen_rect
                page_resized = page.resize((sw, sh), Image.LANCZOS)
                mockup_rgb = mockup.convert('RGB')
                mockup_rgb.paste(page_resized, (sx, sy))
                mockup_rgb.save(out_path, 'JPEG', quality=92)
                total += 1
                print(f"  {fname}")
            except Exception as e:
                print(f"  ERROR: {e}")

    print(f"\nStage 3 done: {total} images generated.")

if __name__ == '__main__':
    main()
