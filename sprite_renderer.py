import math # Provides sin(), used to make the aura pulse over time.
import os # Builds file paths that work on any operating system.
import pygame

SPRITE_DIR = "Imágenes" # Folder where Godzi's mood sprites are stored.
SPRITE_SIZE = 280  # px, the sprite is a square image.

PHI = 1.618  # Same golden ratio used in comfort_model.py and sound_system.py.

MOOD_SPRITES = {
    "COZY_ORBIT": "Happy_GodziV2.png",
    "CURIOUS_WEATHER": "hm_godziV2.png",
    "ANNOYED_GLOW": "grumpy_godziV2.png",
}

# Each mood gets its own aura color, pulse speed, and amplitude. Colors are
# picked to contrast with both the app background and each sprite's own
# background, so the glow stays visible as a ring around Godzi:
# COZY glows warm and golden, CURIOUS glows cool and sky-blue, and ANNOYED
# glows coral-red and fast/nervous - same "PHI thread" as the sound and comfort score.
MOOD_AURA = {
    "COZY_ORBIT": {"color": (255, 200, 120), "speed": 1.0, "amplitude": 14},
    "CURIOUS_WEATHER": {"color": (130, 205, 235), "speed": 2.2, "amplitude": 10},
    "ANNOYED_GLOW": {"color": (235, 90, 80), "speed": 4.5, "amplitude": 8},
}

AURA_BASE_RADIUS = 175  # px, big enough to show a visible ring around the 280px sprite.
AURA_ALPHA = 130  # Aura transparency (0-255, lower means more see-through).


def load_sprites():
    """Loads the 3 PNGs, scales them to SPRITE_SIZE x SPRITE_SIZE, and returns a dict mood -> Surface."""
    sprites = {}
    for mood, filename in MOOD_SPRITES.items():
        path = os.path.join(SPRITE_DIR, filename)
        image = pygame.image.load(path).convert_alpha()
        sprites[mood] = pygame.transform.smoothscale(image, (SPRITE_SIZE, SPRITE_SIZE))
    return sprites


def draw_sprite(screen, sprites, mood, center):
    """Draws the current mood's sprite centered on `center` (cx, cy)."""
    sprite = sprites[mood]
    rect = sprite.get_rect(center=center)
    screen.blit(sprite, rect)


def living_wave(t, speed, amplitude):
    """Combines two sine waves (one of them scaled by PHI) so the pulse
    doesn't feel perfectly repetitive - same idea as comfort_model.py, but
    applied to time instead of weather."""
    wave = math.sin(t * speed) + 0.35 * math.sin(t * speed * PHI)
    return amplitude * wave


def draw_aura(screen, mood, center, t):
    """Draws a pulsing, semi-transparent aura behind Godzi.
    The radius pulses using living_wave(), and its color/speed depend on the mood."""
    settings = MOOD_AURA[mood]
    radius = int(AURA_BASE_RADIUS + living_wave(t, settings["speed"], settings["amplitude"]))
    radius = max(radius, 10)  # Keeps the radius from shrinking to zero or going negative.

    aura_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)  # A separate surface is needed for transparency.
    pygame.draw.circle(aura_surface, (*settings["color"], AURA_ALPHA), (radius, radius), radius)

    rect = aura_surface.get_rect(center=center)
    screen.blit(aura_surface, rect)
