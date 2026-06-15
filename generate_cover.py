from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


PHI = 1.618
WIDTH = 1200
HEIGHT = 630
ROOT = Path(__file__).parent
IMAGE_DIR = ROOT / "Imágenes"


def load_font(size):
    font_paths = [
        "C:/Windows/Fonts/seguisb.ttf",
        "C:/Windows/Fonts/segoeuib.ttf",
        "C:/Windows/Fonts/arialbd.ttf",
    ]
    for font_path in font_paths:
        try:
            return ImageFont.truetype(font_path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def paste_fit(canvas, image_path, box, scale=0.9):
    image = Image.open(image_path).convert("RGBA")
    x, y, w, h = box
    max_size = int(min(w, h) * scale)
    image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
    px = x + (w - image.width) // 2
    py = y + (h - image.height) // 2
    canvas.alpha_composite(image, (px, py))


def draw_gradient_background():
    canvas = Image.new("RGBA", (WIDTH, HEIGHT), "#f8f3df")
    draw = ImageDraw.Draw(canvas)
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(247 * (1 - t) + 206 * t)
        g = int(244 * (1 - t) + 232 * t)
        b = int(223 * (1 - t) + 229 * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
    return canvas


def draw_label(draw, text, xy, fill):
    font = load_font(24)
    x, y = xy
    pad_x = 16
    pad_y = 9
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.rounded_rectangle(
        (x, y, x + w + pad_x * 2, y + h + pad_y * 2),
        radius=16,
        fill=(255, 255, 255, 210),
    )
    draw.text((x + pad_x, y + pad_y - 1), text, font=font, fill=fill)


def main():
    cover = draw_gradient_background()
    draw = ImageDraw.Draw(cover)

    main_w = int(WIDTH / PHI)
    side_w = WIDTH - main_w
    top_h = int(HEIGHT / PHI)
    bottom_h = HEIGHT - top_h

    # Fibonacci-style rectangles: each following space shrinks by PHI.
    cozy_box = (0, 0, main_w, HEIGHT)
    curious_box = (main_w, 0, side_w, top_h)
    annoyed_box = (main_w, top_h, side_w, bottom_h)

    draw.rounded_rectangle((34, 34, main_w - 18, HEIGHT - 34), radius=36, fill=(255, 255, 255, 88))
    draw.rounded_rectangle((main_w + 12, 34, WIDTH - 34, top_h - 14), radius=32, fill=(255, 255, 255, 76))
    draw.rounded_rectangle((main_w + 44, top_h + 12, WIDTH - 52, HEIGHT - 42), radius=30, fill=(255, 255, 255, 70))

    paste_fit(cover, IMAGE_DIR / "Happy_Godzi.png", cozy_box, 0.82)
    paste_fit(cover, IMAGE_DIR / "hm_godzi.png", curious_box, 0.88)
    paste_fit(cover, IMAGE_DIR / "grumpy_godzi.png", annoyed_box, 0.86)

    title_font = load_font(70)
    subtitle_font = load_font(28)
    title = "Godzi's Favorite Climate"
    subtitle = "A tiny golden-ratio weather orbit"

    shadow = (55, 73, 71, 90)
    ink = (33, 59, 58, 255)
    draw.text((54, 474), title, font=title_font, fill=shadow)
    draw.text((50, 468), title, font=title_font, fill=ink)
    draw.text((54, 552), subtitle, font=subtitle_font, fill=(80, 103, 95, 255))

    draw_label(draw, "COZY_ORBIT", (56, 56), (45, 105, 88, 255))
    draw_label(draw, "CURIOUS_WEATHER", (main_w + 34, 48), (90, 84, 42, 255))
    draw_label(draw, "ANNOYED_GLOW", (main_w + 76, top_h + 28), (129, 64, 45, 255))

    cover.convert("RGB").save(ROOT / "cover.png", "PNG")


if __name__ == "__main__":
    main()
