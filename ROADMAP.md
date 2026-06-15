# Golden Orbit of Godzilla — Project Roadmap
**Code in Place 2026 · Stanford University · Final Project**
_Última actualización: 2026-05-26_

---

## Concepto

Baby Godzilla pixel art que reacciona a datos de clima en tiempo real.
El usuario elige una ciudad → el programa fetch ea el clima → una fórmula matemática
convierte esos datos en un "comfort score" → Godzilla cambia de mood, color y efectos visuales.

> **Narrativa del proyecto:** como data analyst puedes tomar datos reales, pasarlos por una
> ecuación elegante, y representar algo valioso y divertido — sin necesitar ser matemático.

---

## Scope Refinado — Data Mapping, no Meteorología

Este proyecto no intenta predecir el clima ni decir si una ciudad es "mejor" que otra.
El objetivo es mostrar cómo Python puede tomar datos reales de clima y mapearlos a una
representación visual divertida: mood, color, movimiento y personalidad de Baby Godzilla.

Para evitar thresholds arbitrarios, la fórmula se calibra con datos históricos recientes:
`analyze_climate.py` analiza aproximadamente 6 meses de datos diarios para Mexico City,
Stanford y Tokyo. Con esos patrones, el score se interpreta de forma relativa:

- `ANNOYED_GLOW`: días más extremos o menos cómodos dentro del patrón observado
- `CURIOUS_WEATHER`: clima intermedio, cambiante o interesante
- `COZY_ORBIT`: días más cercanos al clima suave ideal

Resultado inicial de calibración histórica:

| Threshold | Valor |
|---|---:|
| `CURIOUS_THRESHOLD` | `0.07` |
| `COZY_THRESHOLD` | `0.13` |

Estos valores son modificables: si el proyecto necesita más drama visual, se pueden ajustar
para que los moods se repartan mejor en la demo.

El clima ideal de Godzilla no es seco: es fresco, con nubosidad, viento y lluvia ligera.
Por eso `IDEAL_CLIMATE["rain"]` usa `0.6`, y la fórmula mide distancia frente a esa
lluvia ligera. Además, temperaturas arriba de 24 C agregan una penalización simple para
que días cálidos/secos no queden clasificados como cozy solo por tener nubosidad cercana.

---

## Decisiones de Diseño Confirmadas

| Decisión | Detalle |
|---|---|
| Entorno | Pygame — entrega offline IDE → GitHub (permitido por CIP) |
| Personaje | PNG sprites pixel art (3 variantes) + overlays animados encima en Pygame |
| Pose | 3/4 frontal sentado, espinas en cascada diagonal derecha |
| Interface | Switch: 1 Godzilla + 3 botones de ciudad |
| Data source | Open-Meteo API (sin API key requerida) |
| Sonido | Fuera de scope por ahora — stretch goal al final |

---

## Decisión Visual Final — PNG + Data Overlays

Godzilla ya no se va a construir dibujando cada parte con `pygame.draw`.
La base visual serán imágenes PNG de Godzilla, una por mood. Python se usará para
renderizar información encima de esas imágenes:

- glows sobre espinas
- halos o pulsos según comfort score
- pequeños movimientos o breathing del sprite
- partículas o detalles visuales según lluvia/viento/nubosidad

Esto mantiene el proyecto profesional visualmente y deja el foco de aprendizaje en:
API data → fórmula → mood → visual mapping.

`godzilla.py` existe hoy como placeholder para verificar que Pygame abre una ventana,
pero no representa la dirección final del proyecto. Cuando los PNG estén en `assets/`,
la capa visual debe pasar a un módulo de sprites/overlays, no a funciones como
`draw_body()` o `draw_face()`.

---

## Orden de Ataque (Sprint Actual)

Plan original era B1→B2→...→B7 en orden estricto. Reordenamos para que Said empiece
por las partes que puede armar solo (lógica pura, sin pygame) y deje las partes más
densas (ya construidas con ayuda de Codex/Claude) para cuando tenga más contexto del
resto del proyecto.

**Orden real de trabajo:**

1. **Setup de entorno** — conda env `cip-godzilla` (Python 3.12) + `requirements.txt` ✅ (archivo creado, falta que Said cree y active el env)
2. **Bloque 3 — `weather.py`** ← EMPEZAR ACÁ. Puro Python, testeable con `python weather.py`, sin pygame.
3. **Bloque 4 — Golden Orbit formula** (`comfort_score`, `mood_from_comfort`). Puro Python, mismo estilo.
4. **Revisión de Bloque 1** — leer `main.py` y entender el loop de Pygame. `godzilla.py` queda solo como placeholder temporal; la versión final usará PNG sprites + overlays.
5. **Bloque 2 — efectos animados** (`living_wave` sobre las espinas).
6. **Bloque 5 — botones de ciudad + switch**.
7. **Bloque 6 — panel de datos (UI)**.
8. **Bloque 7 — polish** (si da tiempo).

> La numeración "Bloque X" se mantiene igual al diseño original (para no romper la
> referencia a conceptos CIP) — este orden de ataque es solo la secuencia en la que
> los vamos a construir.

---

## Arte Final — 3 Moods

La dirección final es usar sprites PNG como base visual. Guardarlos en `assets/`:

| Archivo | Mood | Visual |
|---|---|---|
| `godzilla_cozy.png` | `COZY_ORBIT` | Mint #A8CFC4, espinas crema, ojo cerrado feliz, mejilla rosa |
| `godzilla_curious.png` | `CURIOUS_WEATHER` | Gris-verde desaturado, espinas con micro-glow cyan, ojo abierto alerta |
| `godzilla_glow.png` | `ANNOYED_GLOW` | Negro/navy, espinas cyan eléctrico #00D9FF, medio ojo, aura pulsante |

---

## Estructura de Archivos

```
Final Proyect/
├── main.py               ← loop principal, UI, eventos, animación
├── data_fetcher.py       ← fetch_weather() + llamadas a Open-Meteo
├── comfort_model.py      ← golden_distance() + comfort_score() + mood_from_comfort()
├── weather.py            ← runner de prueba para imprimir clima + comfort + mood
├── analyze_climate.py    ← análisis histórico para calibrar thresholds
├── sprite_renderer.py    ← carga PNGs y dibuja overlays/glows sobre el sprite
├── colors.py             ← paletas de colores por mood (opcional, puede ir en main.py)
├── assets/
│   ├── godzilla_cozy.png
│   ├── godzilla_curious.png
│   └── godzilla_glow.png
├── ROADMAP.md            ← este archivo
└── 2026-05-18-golden-orbit-godzilla-design.md  ← diseño original de referencia
```

---

## Fórmula Golden Orbit

```python
import math

PHI = 1.618  # Golden Ratio — constante de sensibilidad

IDEAL_CLIMATE = {
    "temperature": 18,    # °C — fresco
    "cloud_cover": 55,    # % — suavemente nublado
    "wind_speed": 14,     # km/h — brisa suave
    "rain": 0.6,          # mm — lluvia ligera
}

def comfort_score(weather):
    distance = (
        abs(weather["temperature"] - 18) / 20
        + abs(weather["cloud_cover"] - 55) / 55
        + abs(weather["wind_speed"] - 14) / 30
        + min(weather["rain"] / 2.0, 1.0)   # ← corrección: 0 lluvia = 0 penalización
    )
    return math.exp(-PHI * distance)

def mood_from_comfort(comfort):
    if comfort >= 0.72:
        return "COZY_ORBIT"
    elif comfort >= 0.38:
        return "CURIOUS_WEATHER"
    else:
        return "ANNOYED_GLOW"
```

> **Nota:** calibrar los thresholds (0.72, 0.38) después de imprimir el comfort score
> de las 3 ciudades con datos reales. Pueden necesitar ajuste.

---

## Ecuación de Animación — Living Wave

```python
PHI = 1.618

def living_wave(t, i, speed, phase, amplitude):
    """
    t         = tiempo (crece cada frame: t += 0.05)
    i         = índice del elemento (cada espina tiene un número)
    speed     = qué tan rápido se mueve (cambia con el mood)
    phase     = delay entre elementos (crea el efecto de ola viajando)
    amplitude = qué tan grande es el movimiento (cambia con el viento)
    """
    wave = (
        math.sin(t * speed + i * phase)
        + 0.35 * math.sin(t * speed * PHI + i * phase * PHI)
    )
    return amplitude * wave
```

Esta ecuación controla:
- El pulso de los halos en las espinas (radio que crece/encoge)
- La intensidad del glow (varía por mood)
- El breathing del sprite (escala ±3px)

---

## Ciudades Preset

```python
CITIES = {
    "Mexico City": {"lat": 19.4326, "lon": -99.1332},
    "Stanford":    {"lat": 37.4419, "lon": -122.1430},
    "Tokyo":       {"lat": 35.6762, "lon": 139.6503},
}
```

---

## API Open-Meteo

```
URL base:
https://api.open-meteo.com/v1/forecast
  ?latitude={lat}
  &longitude={lon}
  &current=temperature_2m,cloud_cover,wind_speed_10m,rain
```

> **Gotcha importante:** NO usar `current_weather=true` — ese endpoint no devuelve
> `cloud_cover` ni `rain`. Usar siempre `current=` con los campos explícitos.

Campos del JSON a extraer:
```python
data["current"]["temperature_2m"]   # float, °C
data["current"]["cloud_cover"]      # int, %
data["current"]["wind_speed_10m"]   # float, km/h
data["current"]["rain"]             # float, mm
```

---

## Roadmap — 7 Bloques

### BLOQUE 1 — Ventana y sprite estático
**Conceptos CIP:** variables, diccionarios, funciones, loop while

**Goal:** abrir ventana Pygame, cargar los 3 PNGs en un diccionario, mostrar el correcto
según una variable `mood` hardcodeada. El dibujo vectorial actual solo fue una prueba de entorno.

**Pseudocódigo:**
```
sprites = diccionario con los 3 PNGs cargados
mood = "COZY_ORBIT"   ← hardcodeado para testear

loop principal:
    limpiar pantalla
    dibujar sprites[mood] centrado
    actualizar pantalla
```

**Test:** cambias `mood` manualmente a `"ANNOYED_GLOW"` y ves el sprite correcto. ✓

---

### BLOQUE 2 — Efectos animados encima del sprite
**Conceptos CIP:** `math.sin()`, for loops con índice, listas de posiciones, variable `t`

**Goal:** halos pulsantes en las espinas usando `living_wave`. El sprite base no cambia —
los efectos se dibujan encima como círculos semitransparentes.

**Pseudocódigo:**
```
SPINE_POSITIONS = lista de (dx, dy) relativos al centro del sprite
                  (medir en el PNG dónde están las espinas)
t = 0

cada frame:
    para i, (dx, dy) en enumerate(SPINE_POSITIONS):
        radio = 8 + living_wave(t, i, speed, 0.6, amplitude)
        dibujar círculo con color del mood en (cx+dx, cy+dy) con ese radio
    t += 0.05
```

**Test:** ves halos que pulsan como olas viajando por las espinas. ✓

---

### BLOQUE 3 — Datos del clima
**Conceptos CIP:** funciones, try/except básico, JSON, diccionarios

**Goal:** `fetch_weather(lat, lon)` devuelve dict con 4 valores o FALLBACK si falla.

**Pseudocódigo:**
```
FALLBACK = {"temperature": 20, "cloud_cover": 50, "wind_speed": 10, "rain": 0}

función fetch_weather(lat, lon):
    intentar:
        hacer request a Open-Meteo URL
        parsear JSON
        retornar diccionario con los 4 campos
    si error:
        retornar FALLBACK
```

**Test:** `python weather.py` imprime datos reales de Mexico City. ✓

---

### BLOQUE 4 — Fórmula Golden Orbit
**Conceptos CIP:** funciones, math, condicionales

**Goal:** `comfort_score(weather)` → float 0-1. `mood_from_comfort(score)` → string.

**Test:** imprimes comfort de las 3 ciudades — los valores tienen sentido lógico.
Calibras thresholds si hace falta. ✓

---

### BLOQUE 5 — Botones de ciudad + switch
**Conceptos CIP:** diccionarios, eventos Pygame, condicionales, listas

**Goal:** 3 botones en pantalla. Click → fetch → recalcula → cambia sprite y efectos.

**Pseudocódigo:**
```
ciudad_actual = "Mexico City"
weather = fetch_weather(...)
comfort = comfort_score(weather)
mood = mood_from_comfort(comfort)

loop:
    si click en botón X:
        ciudad_actual = X
        weather = fetch_weather(CITIES[X])
        comfort = comfort_score(weather)
        mood = mood_from_comfort(comfort)
    
    dibujar todo
```

**Test:** clickeas Tokyo y el mood cambia distinto que Mexico City. ✓

---

### BLOQUE 6 — Panel de datos
**Conceptos CIP:** strings con f-strings, pygame.font, condicionales

**Goal:** mostrar ciudad, temperatura, nubosidad, viento, lluvia, comfort y mood en pantalla.

**Pseudocódigo:**
```
función draw_ui(screen, ciudad, weather, comfort, mood):
    dibujar textos con los valores
    dibujar barra: rect con ancho proporcional a comfort (0 a 1)
```

**Test:** los números cambian cuando switcheas ciudad. ✓

---

### BLOQUE 7 — Polish (si da tiempo)
Solo después de que Bloques 1-6 funcionan:

- [ ] Partículas de lluvia (lista de puntos `y` que incrementan, se resetean al fondo)
- [ ] Fondo de color diferente por mood
- [ ] Breathing del sprite con `pygame.transform.scale`
- [ ] Sonido pentatónico con `pygame.mixer`

---

## Regla de Trabajo

> Si te trabas en algo: abre una conversación nueva, di **"estoy en el Bloque X,
> aquí está mi código, esperaba Y pero pasa Z"** — y se resuelve como tutor,
> sin que la IA escriba todo por ti.

---

## Checklist de Anotaciones para el Video (por bloque)

Para cada bloque, antes de pasar al siguiente, anotar en el código (comentarios
propios) o en un doc aparte:

- [ ] ¿Qué problema resuelve este bloque? (1 frase)
- [ ] ¿Qué función(es) nuevas se agregaron y qué recibe/devuelve cada una?
- [ ] ¿Qué concepto de CIP se usó? (loop, dict, try/except, math.sin, eventos, etc.)
- [ ] ¿Cómo lo testeaste? (qué corriste, qué viste)
- [ ] ¿Hubo algo que no entendías al principio y ahora sí? (esto es oro para el video)

---

## Estado Actual del Proyecto

- [x] Concepto y narrativa definidos
- [x] Fórmula Golden Orbit diseñada
- [x] Arquitectura de archivos definida — Godzilla final usa PNG sprites + overlays, no dibujo vectorial
- [x] Roadmap completo documentado y reordenado (ver "Orden de Ataque")
- [x] `requirements.txt` creado (pygame, requests)
- [x] Bloque 1 — ventana Pygame verificada con placeholder temporal en `godzilla.py`
- [x] Setup de entorno verificado — `python main.py` abre la ventana Pygame
- [x] Bloque 3 — `data_fetcher.py` trae datos reales de Open-Meteo y usa fallback si falla
- [x] Bloque 4 — `comfort_model.py` implementa `golden_distance()`, `comfort_score()` y `mood_from_comfort()`
- [x] Calibrar thresholds de mood con datos reales — `analyze_climate.py` estimó p33/p66 con 6 meses de historia
- [ ] Conectar `data_fetcher.py` + `comfort_model.py` con `main.py`
- [ ] Reemplazar placeholder vectorial por PNG sprites en `assets/`
- [ ] Bloque 2 — efectos animados
- [ ] Bloque 5 — botones + switch
- [ ] Bloque 6 — UI panel
- [ ] Bloque 7 — polish
