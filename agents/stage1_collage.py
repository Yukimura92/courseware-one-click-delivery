"""Stage 1: Generate collage covers (二图版 + 五图版 + 十二图版)."""
import argparse, json, os, sys
from PIL import Image, ImageDraw, ImageFont

CANVAS_W, CANVAS_H = 1200, 1600
IMG_W = 1120
IMG_H = int(IMG_W * 9 / 16)  # 630
LEFT_X = 40

def load_config(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def find_font(size):
    candidates = [
        "msyh.ttc", "msyhbd.ttc", "msyh.ttf", "msyhbd.ttf",
        "C:/Windows/Fonts/msyh.ttc", "C:/Windows/Fonts/msyhbd.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
    ]
    for fp in candidates:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                continue
    return ImageFont.load_default()

def draw_centered_text(draw, text, y, font, fill=(255, 255, 255)):
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    x = (CANVAS_W - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)

def create_two_pic(pages_dir, page_files, out_dir, title, bottom, bg_color, page_count):
    """Generate 二图版 collage images."""
    font_title = find_font(66)
    font_bottom = find_font(56)
    num_pics = min(5, len(page_files) // 2)
    results = []

    for idx in range(num_pics):
        p1 = page_files[idx * 2]
        p2 = page_files[idx * 2 + 1]
        canvas = Image.new('RGB', (CANVAS_W, CANVAS_H), bg_color)
        draw = ImageDraw.Draw(canvas)

        # Title
        draw_centered_text(draw, title, 72, font_title)

        # Image 1 at y=168
        img1 = Image.open(os.path.join(pages_dir, p1)).convert('RGB')
        img1 = img1.resize((IMG_W, IMG_H), Image.LANCZOS)
        canvas.paste(img1, (LEFT_X, 168))

        # Image 2 at y=812
        img2 = Image.open(os.path.join(pages_dir, p2)).convert('RGB')
        img2 = img2.resize((IMG_W, IMG_H), Image.LANCZOS)
        canvas.paste(img2, (LEFT_X, 812))

        # Bottom text at y=1472
        draw_centered_text(draw, bottom, 1472, font_bottom)

        fname = f"2pic-0{idx+1}-pages-{idx*2+1:02d}-{idx*2+2:02d}.jpg"
        out_path = os.path.join(out_dir, fname)
        canvas.save(out_path, 'JPEG', quality=92)
        results.append(out_path)
        print(f"  [二图版] {fname}")
    return results

def create_five_pic(pages_dir, page_files, out_dir, title, bottom, bg_color, page_count):
    """Generate 五图版 collage images."""
    font_title = find_font(66)
    font_bottom = find_font(56)
    num_groups = len(page_files) // 5
    results = []
    small_w = (IMG_W - 18) // 2  # 551
    small_h = int(small_w * 9 / 16)  # 310

    for g in range(num_groups):
        group = page_files[g * 5 : g * 5 + 5]
        canvas = Image.new('RGB', (CANVAS_W, CANVAS_H), bg_color)
        draw = ImageDraw.Draw(canvas)

        # Title at y=60
        draw_centered_text(draw, title, 60, font_title)

        # Big image (first page = cover) at y=154
        big = Image.open(os.path.join(pages_dir, group[0])).convert('RGB')
        big = big.resize((IMG_W, IMG_H), Image.LANCZOS)
        canvas.paste(big, (LEFT_X, 154))

        # Small grid 2×2 at y=798
        grid_y = 798
        for i in range(4):
            row, col = divmod(i, 2)
            sx = LEFT_X + col * (small_w + 18)
            sy = grid_y + row * (small_h + 18)
            small = Image.open(os.path.join(pages_dir, group[i + 1])).convert('RGB')
            small = small.resize((small_w, small_h), Image.LANCZOS)
            canvas.paste(small, (sx, sy))

        # Bottom text at y=1464
        draw_centered_text(draw, bottom, 1464, font_bottom)

        fname = f"5pic-0{g+1}-pages-{g*5+1:02d}-{g*5+5:02d}.jpg"
        out_path = os.path.join(out_dir, fname)
        canvas.save(out_path, 'JPEG', quality=92)
        results.append(out_path)
        print(f"  [五图版] {fname}")
    return results

def create_twelve_pic(pages_dir, page_files, out_dir, bg_color, page_count):
    """Generate 十二图版 collage images (no title, no bottom text)."""
    results = []
    gap_l = 6   # left column vertical gap
    gap_r = 6   # right column vertical gap
    G_col = 10  # column gap
    M = 16      # margin

    # Solve: W_r = 3*W_l + (128*6 - 32*6)/27 = 3*W_l + 21.33
    # W_r + W_l + G_col + 2*M = 1200 → W_r + W_l = 1158
    # W_l ≈ 284, W_r ≈ 874
    w_l = 284
    w_r = 874
    h_l = int(w_l * 9 / 16)  # ~160
    h_r = int(w_r * 9 / 16)  # ~492

    # Verify height alignment
    left_h = 9 * h_l + 8 * gap_l  # ~1488
    right_h = 3 * h_r + 2 * gap_r  # ~1488
    top_margin = (CANVAS_H - left_h) // 2

    left_x = M
    right_x = M + w_l + G_col

    # 2 twelve-pic images
    configs = [
        # First: right=pages 1-3, left=pages 4-12
        {"right": [0, 1, 2], "left": list(range(3, 12))},
        # Second: right=pages 4-6, left=pages 7-15
        {"right": [3, 4, 5], "left": list(range(6, 15))},
    ]

    for ci, cfg in enumerate(configs):
        canvas = Image.new('RGB', (CANVAS_W, CANVAS_H), bg_color)

        # Left column: 9 small images
        for i, pidx in enumerate(cfg["left"]):
            if pidx >= len(page_files):
                break
            sy = top_margin + i * (h_l + gap_l)
            img = Image.open(os.path.join(pages_dir, page_files[pidx])).convert('RGB')
            img = img.resize((w_l, h_l), Image.LANCZOS)
            canvas.paste(img, (left_x, sy))

        # Right column: 3 large images
        for i, pidx in enumerate(cfg["right"]):
            if pidx >= len(page_files):
                break
            sy = top_margin + i * (h_r + gap_r)
            img = Image.open(os.path.join(pages_dir, page_files[pidx])).convert('RGB')
            img = img.resize((w_r, h_r), Image.LANCZOS)
            canvas.paste(img, (right_x, sy))

        fname = f"12pic-0{ci+1}-pages.jpg"
        out_path = os.path.join(out_dir, fname)
        canvas.save(out_path, 'JPEG', quality=92)
        results.append(out_path)
        print(f"  [十二图版] {fname}")
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, help='JSON config file')
    args = parser.parse_args()
    cfg = load_config(args.config)

    pages_dir = cfg['pages_dir']
    out_dir = cfg['out_dir']
    title = cfg['title']
    bottom = cfg['bottom']
    bg_color = tuple(cfg['bg_color'])  # [R, G, B]
    page_count = cfg['page_count']

    # Find page image files
    prefix = cfg.get('page_prefix', '')
    page_files = sorted([
        f for f in os.listdir(pages_dir)
        if f.lower().endswith(('.jpg', '.png', '.jpeg'))
    ])
    if prefix:
        page_files = [f for f in page_files if f.startswith(prefix)]
    page_files = page_files[:page_count]

    print(f"Pages dir: {pages_dir}")
    print(f"Found {len(page_files)} page images")
    print(f"Output dir: {out_dir}")

    # 二图版
    print("\n--- 二图版 ---")
    create_two_pic(pages_dir, page_files, out_dir, title, bottom, bg_color, page_count)

    # 五图版
    print("\n--- 五图版 ---")
    create_five_pic(pages_dir, page_files, out_dir, title, bottom, bg_color, page_count)

    # 十二图版
    print("\n--- 十二图版 ---")
    create_twelve_pic(pages_dir, page_files, out_dir, bg_color, page_count)

    print("\nStage 1 done.")

if __name__ == '__main__':
    main()
