"""Cute sound module for Godzilla's mood system.

This file generates short, soft, game-like sounds for each Godzilla mood and is
now connected to main.py. The idea is similar to the visual comfort model:
weather data becomes a comfort score, the comfort score becomes a mood, and
this module gives that mood a small musical personality.

The sound logic uses two friendly mathematical ideas:

Fibonacci values, related to PHI, to choose rhythmic durations.
A pentatonic scale, which tends to sound soft and pleasant, to avoid harsh
or dissonant notes.

Each mood uses a different subset of notes and rhythm values:
COZY_ORBIT sounds slower and calmer, CURIOUS_WEATHER sounds more alert and
balanced, and ANNOYED_GLOW sounds shorter and more nervous while still staying
cute.

The file can also run by itself as a small audio test, but its main role is to
provide reusable sound functions for the main Pygame project.
"""

import io # Creates an in-memory file so the generated WAV does not need to be saved to disk.
import math # Provides sin() and pi for generating the sound wave.
import struct # Converts numeric audio samples into binary data for the WAV file.
import wave # Writes the generated tone as a valid WAV audio stream.

try: # Tries to import Pygame so the module can play sounds.
    import pygame
except ImportError:
    pygame = None # Keeps the file safe if Pygame is not installed.


FIBONACCI = [1, 1, 2, 3, 5, 8, 13, 21, 34] # Fibonacci values used as musical rhythm units.

# Friendly pentatonic notes used to keep the sounds soft, simple, and game-like.
PENTATONIC_NOTES = {
    "C4": 261.63,
    "D4": 293.66,
    "E4": 329.63,
    "G4": 392.00,
    "A4": 440.00,
    "C5": 523.25,
    "D5": 587.33,
    "E5": 659.25,
}

# Each mood gets its own note range so the same comfort system also creates different sound personalities.
MOOD_NOTES = {
    "COZY_ORBIT": ["C4", "E4", "G4"],
    "CURIOUS_WEATHER": ["E4", "G4", "A4", "C5"],
    "ANNOYED_GLOW": ["A4", "C5", "D5", "E5"],
}
# Each mood gets Fibonacci rhythm values: cozy is slower, curious is medium, annoyed is quicker.
MOOD_RHYTHM = {
    "COZY_ORBIT": FIBONACCI[5:8],       # 8, 13, 21 -> long notes
    "CURIOUS_WEATHER": FIBONACCI[3:6],  # 3, 5, 8 -> medium notes
    "ANNOYED_GLOW": FIBONACCI[0:3],     # 1, 1, 2 -> short and fast notes
}

RHYTHM_UNIT = 0.14  # Converts each Fibonacci rhythm unit into seconds.


def choose_note(comfort, mood):
    """Chooses a sound note using the current comfort level and mood."""
    notes = MOOD_NOTES[mood]
    index = min(int(comfort * len(notes)), len(notes) - 1)
    return notes[index]


def choose_rhythm(comfort, mood):
    """Chooses a sound duration using Fibonacci rhythm values and the current mood"""
    fib_values = MOOD_RHYTHM[mood]
    index = min(int(comfort * len(fib_values)), len(fib_values) - 1)
    return fib_values[index] * RHYTHM_UNIT


def generate_tone(frequency, duration, volume=0.25, sample_rate=44100):
    """Generates a short sine-wave tone with fade-out and slight vibrato."""
    n_samples = max(int(sample_rate * duration), 1)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file: # Creates a small WAV file in memory using one audio channel and 16-bit samples.
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        for i in range(n_samples): # Writes each audio sample one by one to build the tone.
            t = i / sample_rate
            envelope = 1.0 - (i / n_samples)  # fade-out: evita el "click" final
            vibrato = 1 + 0.03 * math.sin(2 * math.pi * 6 * t)  # leve "temblor" tipo gruñido
            sample = math.sin(2 * math.pi * frequency * vibrato * t) * volume * envelope
            wav_file.writeframes(struct.pack("<h", int(sample * 32767)))
    buffer.seek(0)
    return buffer


def play_note(note, duration):
    """Plays a generated note with Pygame, or prints the note if audio is unavailable"""
    if pygame is None:
        print(f"(sin audio) nota={note} duracion={duration:.2f}s")
        return
    try:
        tone = generate_tone(PENTATONIC_NOTES[note], duration)
        sound = pygame.mixer.Sound(tone)
        sound.play()
    except Exception as error:
        print(f"No se pudo reproducir el sonido: {error}")


if __name__ == "__main__": # Runs a standalone sound test only when this file is executed directly.
    if pygame is not None:
        pygame.mixer.init()

    for mood in ("COZY_ORBIT", "CURIOUS_WEATHER", "ANNOYED_GLOW"): # Tests each mood with three comfort levels to hear how notes and rhythm change.
        print(f"\n--- {mood} ---")
        for comfort in (0.85, 0.5, 0.15):
            note = choose_note(comfort, mood)
            rhythm = choose_rhythm(comfort, mood)
            print(f"comfort={comfort:.2f} -> nota={note}, duracion={rhythm:.2f}s")
            play_note(note, rhythm)
            if pygame is not None:
                pygame.time.wait(int(rhythm * 1000) + 150)

    if pygame is not None: # Closes the audio mixer cleanly after the standalone test.
        pygame.mixer.quit()
