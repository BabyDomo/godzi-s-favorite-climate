import pygame # Imports Pygame, the library used to create the window, draw graphics, and handle events.
import sprite_renderer # Imports our module that loads and draws Godzi's mood sprite (PNG images).
import sound_system # Imports our module that generates Godzi's procedural mood sounds.
from data_fetcher import CITIES, fetch_weather # Imports city coordinates and the function that gets live weather data.
from comfort_model import comfort_score, mood_from_comfort # Imports the model that turns weather into comfort and mood.

WIDTH, HEIGHT = 800, 600 # Defines the size of the Pygame window.
BG_COLOR = (217, 238, 233) # Defines the soft background color for the main screen.
# Defines the UI color palette for buttons and text.
BUTTON_COLOR = (168, 207, 196)
BUTTON_SELECTED_COLOR = (95, 143, 136)
BUTTON_TEXT_COLOR = (47, 75, 70)
PANEL_TEXT_COLOR = (47, 75, 70)

# Friendlier names for each mood, shown in the info panel instead of the raw constant.
MOOD_LABELS = {
    "COZY_ORBIT": "Cozy",
    "CURIOUS_WEATHER": "Curious (Not Good Enough)",
    "ANNOYED_GLOW": "Annoyed Glow",
}


def make_city_buttons(): # Creates one clickable button rectangle for each city and centers them at the top of the window.
    buttons = {}
    button_width, button_height = 160, 40
    gap = 20
    start_x = (WIDTH - (len(CITIES) * button_width + (len(CITIES) - 1) * gap)) // 2
    for i, city_name in enumerate(CITIES):
        x = start_x + i * (button_width + gap)
        buttons[city_name] = pygame.Rect(x, 20, button_width, button_height)
    return buttons


def draw_buttons(screen, font, buttons, current_city): # Draws all city buttons and highlights the currently selected city.
    for city_name, rect in buttons.items():
        color = BUTTON_SELECTED_COLOR if city_name == current_city else BUTTON_COLOR
        pygame.draw.rect(screen, color, rect, border_radius=8)
        label = font.render(city_name, True, BUTTON_TEXT_COLOR)
        label_rect = label.get_rect(center=rect.center)
        screen.blit(label, label_rect)


def get_clicked_city(buttons, pos): # Checks whether the mouse clicked inside any city button and returns that city name.
    for city_name, rect in buttons.items():
        if rect.collidepoint(pos):
            return city_name
    return None


def draw_info_panel(screen, font, current_city, weather, comfort, mood): # Builds and draws the weather, comfort, and mood text panel on the left side of the screen.
    lines = [
        f"City: {current_city}",
        f"Temperature: {weather['temperature']:.1f} C",
        f"Cloud cover: {weather['cloud_cover']:.0f} %",
        f"Wind speed: {weather['wind_speed']:.1f} km/h",
        f"Rain: {weather['rain']:.1f} mm",
        f"Comfort score: {comfort:.3f}",
        f"Mood: {MOOD_LABELS[mood]}",
    ]
    for i, line in enumerate(lines):
        label = font.render(line, True, PANEL_TEXT_COLOR)
        screen.blit(label, (20, 90 + i * 24))


def main(): # Initializes Pygame, creates the window, clock, font, and starting UI state.
    pygame.init()
    pygame.mixer.init() # Initializes the audio mixer so Godzi's procedural growls can play.
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Godzilla's Cozy Orbit")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 22)

    buttons = make_city_buttons() # Creates the city buttons once before the main loop starts.
    sprites = sprite_renderer.load_sprites() # Loads and scales the three Godzi mood sprites once before the main loop starts.

    current_city = "Mexico City" # Sets the initial city to display when the program starts.
    weather = fetch_weather(CITIES[current_city]["lat"], CITIES[current_city]["lon"])
    comfort = comfort_score(weather)
    mood = mood_from_comfort(comfort)

    note = sound_system.choose_note(comfort, mood) # Picks the starting growl's note based on comfort and mood.
    duration = sound_system.choose_rhythm(comfort, mood) # Picks the starting growl's duration based on comfort and mood.
    sound_system.play_note(note, duration) # Plays Godzi's growl once when the program starts.

    t = 0.0 # Animation clock for the pulsing aura, grows a little every frame.

    running = True # Starts the main event loop that keeps the window open and responsive until the user closes it.
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked_city = get_clicked_city(buttons, event.pos)
                if clicked_city and clicked_city != current_city:
                    current_city = clicked_city
                    weather = fetch_weather(CITIES[current_city]["lat"], CITIES[current_city]["lon"])
                    comfort = comfort_score(weather)
                    new_mood = mood_from_comfort(comfort)
                    if new_mood != mood: # Only plays a new growl when the mood actually changes, not on every click.
                        note = sound_system.choose_note(comfort, new_mood)
                        duration = sound_system.choose_rhythm(comfort, new_mood)
                        sound_system.play_note(note, duration)
                    mood = new_mood

        screen.fill(BG_COLOR) # Clears the screen with the background color before drawing the new frame.
        draw_buttons(screen, font, buttons, current_city)
        draw_info_panel(screen, font, current_city, weather, comfort, mood)
        sprite_renderer.draw_aura(screen, mood, (WIDTH // 2, HEIGHT - 165), t) # Draws the pulsing aura behind Godzi, mood sets its color and speed.
        sprite_renderer.draw_sprite(screen, sprites, mood, (WIDTH // 2, HEIGHT - 165)) # Draws the Godzi sprite matching the current mood.
        pygame.display.flip()
        t += 0.05 # Advances the animation clock so the aura keeps pulsing.
        clock.tick(30)
    pygame.quit()

if __name__ == '__main__':
    main()
