import os
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

WIDTH, HEIGHT = 1280, 720
FPS = 30
DURATION = 3  # seconds
FRAMES = FPS * DURATION
OUTPUT = "videos/sunset.mp4"
FRAMES_DIR = "/tmp/sunset_frames"

os.makedirs(FRAMES_DIR, exist_ok=True)
os.makedirs("videos", exist_ok=True)


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def blend_colors(colors, t):
    """Blend through a list of colors based on t in [0,1]."""
    n = len(colors) - 1
    idx = min(int(t * n), n - 1)
    local_t = t * n - idx
    return lerp_color(colors[idx], colors[idx + 1], local_t)


def draw_sky_gradient(draw, t):
    """Draw vertical sky gradient from top to horizon."""
    horizon_y = int(HEIGHT * 0.55)

    sky_top_colors = [
        (20, 10, 60),   # deep indigo at start
        (80, 30, 120),  # purple mid
        (200, 80, 40),  # orange-red end
    ]
    sky_horizon_colors = [
        (255, 120, 40),  # warm orange
        (255, 80, 20),   # deeper orange
        (255, 160, 60),  # golden
    ]

    for y in range(horizon_y):
        row_t = y / horizon_y
        top_color = blend_colors(sky_top_colors, t)
        horiz_color = blend_colors(sky_horizon_colors, t)
        color = lerp_color(top_color, horiz_color, row_t)
        draw.line([(0, y), (WIDTH, y)], fill=color)


def draw_sea_gradient(draw, t):
    """Draw sea/ground below horizon."""
    horizon_y = int(HEIGHT * 0.55)

    sea_horizon_colors = [
        (180, 60, 10),
        (120, 30, 10),
        (80, 20, 40),
    ]
    sea_bottom_colors = [
        (10, 10, 40),
        (5, 5, 20),
        (5, 5, 15),
    ]

    for y in range(horizon_y, HEIGHT):
        row_t = (y - horizon_y) / (HEIGHT - horizon_y)
        top_color = blend_colors(sea_horizon_colors, t)
        bot_color = blend_colors(sea_bottom_colors, t)
        color = lerp_color(top_color, bot_color, row_t)
        draw.line([(0, y), (WIDTH, y)], fill=color)


def draw_sun(img, draw, t):
    horizon_y = int(HEIGHT * 0.55)
    sun_r = 70

    # Sun moves from above horizon to just below it
    sun_x = WIDTH // 2
    sun_start_y = horizon_y - 160
    sun_end_y = horizon_y + sun_r // 2
    sun_y = int(sun_start_y + (sun_end_y - sun_start_y) * t)

    # Glow
    glow_r = sun_r + 80
    glow = Image.new("RGBA", (glow_r * 2, glow_r * 2), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    alpha = int(180 - t * 80)
    glow_draw.ellipse([(0, 0), (glow_r * 2, glow_r * 2)], fill=(255, 180, 50, alpha))
    glow = glow.filter(ImageFilter.GaussianBlur(radius=30))
    img.paste(glow, (sun_x - glow_r, sun_y - glow_r), glow)

    # Sun disk — clip to horizon
    clip_top = max(0, sun_y - sun_r)
    clip_bottom = min(horizon_y, sun_y + sun_r)
    if clip_top < clip_bottom:
        sun_color = blend_colors(
            [(255, 240, 100), (255, 180, 60), (255, 100, 30)], t
        )
        draw.ellipse(
            [(sun_x - sun_r, sun_y - sun_r), (sun_x + sun_r, sun_y + sun_r)],
            fill=sun_color,
        )
        # Re-draw sea over the sun below horizon
        for y in range(horizon_y, sun_y + sun_r + 1):
            if y >= HEIGHT:
                break
            row_t = (y - horizon_y) / (HEIGHT - horizon_y)
            sea_h = blend_colors([(180, 60, 10), (120, 30, 10), (80, 20, 40)], t)
            sea_b = blend_colors([(10, 10, 40), (5, 5, 20), (5, 5, 15)], t)
            color = lerp_color(sea_h, sea_b, row_t)
            draw.line([(0, y), (WIDTH, y)], fill=color)


def draw_reflection(draw, t):
    """Sun reflection on water."""
    horizon_y = int(HEIGHT * 0.55)
    cx = WIDTH // 2

    for i in range(15):
        y = horizon_y + 20 + i * 12
        if y >= HEIGHT:
            break
        width = int(80 - i * 4)
        alpha_factor = max(0, 1 - i / 15) * (1 - t * 0.5)
        color = blend_colors(
            [(255, 200, 80), (255, 140, 40), (200, 80, 20)], t
        )
        lum = int(255 * alpha_factor)
        r = min(255, color[0])
        g = min(255, int(color[1] * alpha_factor + 10))
        b = min(255, int(color[2] * alpha_factor))
        if width > 2:
            draw.ellipse(
                [(cx - width, y - 3), (cx + width, y + 3)],
                fill=(r, g, b),
            )


def draw_clouds(draw, t, frame_idx):
    """Simple cloud wisps."""
    horizon_y = int(HEIGHT * 0.55)
    clouds = [
        (200, 80, 260, 60),
        (900, 100, 200, 50),
        (500, 140, 300, 45),
        (100, 160, 180, 35),
        (1050, 60, 220, 40),
    ]
    for (cx, cy, cw, ch) in clouds:
        drift = int(frame_idx * 0.3)
        cx = (cx + drift) % (WIDTH + 100) - 50
        alpha = int(80 + 40 * t)
        color = blend_colors(
            [(255, 180, 120), (255, 140, 80), (200, 100, 80)], t
        )
        draw.ellipse(
            [(cx - cw // 2, cy - ch // 2), (cx + cw // 2, cy + ch // 2)],
            fill=color,
        )


def draw_horizon_haze(draw, t):
    horizon_y = int(HEIGHT * 0.55)
    haze_color = blend_colors(
        [(255, 150, 80), (255, 100, 40), (220, 80, 40)], t
    )
    for dy in range(-15, 15):
        y = horizon_y + dy
        opacity = max(0, 1 - abs(dy) / 15)
        r = min(255, int(haze_color[0] * opacity + 0 * (1 - opacity)))
        g = min(255, int(haze_color[1] * opacity))
        b = min(255, int(haze_color[2] * opacity))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


print(f"Generating {FRAMES} frames...")
for frame_idx in range(FRAMES):
    t = frame_idx / (FRAMES - 1)  # 0 → 1

    img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw_sky_gradient(draw, t)
    draw_clouds(draw, t, frame_idx)
    draw_sea_gradient(draw, t)
    draw_horizon_haze(draw, t)
    draw_sun(img, draw, t)
    draw_reflection(draw, t)

    img.save(f"{FRAMES_DIR}/frame_{frame_idx:04d}.png")

    if frame_idx % 15 == 0:
        print(f"  Frame {frame_idx}/{FRAMES}")

print("Encoding video with ffmpeg...")
os.system(
    f"ffmpeg -y -framerate {FPS} -i {FRAMES_DIR}/frame_%04d.png "
    f"-c:v libx264 -pix_fmt yuv420p -crf 18 {OUTPUT}"
)
print(f"Done! Video saved to: {OUTPUT}")
