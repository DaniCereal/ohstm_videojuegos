# Oh Hermes, Send the Message

Proyecto de videojuego para la asignatura **Tecnología de Videojuegos** de la UAH, creado por Daniel Cordos, Daniel Silva, Brayan Nicolás Cotoara y Luis Azaña.

El juego está desarrollado en **Python** con la librería **Arcade**. Es un plataformas 2D de exploración en el que Hermes recorre salas conectadas, consigue mejoras, recoge plumas y habla con personajes de la mitología griega.

## Instalación

Para ejecutar el proyecto es necesario instalar las dependencias indicadas en `requirements.txt`.

```bash
pip install -r requirements.txt
```

Después, ejecuta el archivo principal:

```bash
python src/main.py
```

También se puede ejecutar desde Visual Studio Code abriendo el proyecto y lanzando `src/main.py`.

## Controles por defecto

| Acción | Tecla |
| --- | --- |
| Mover arriba / saltar | `W` |
| Mover abajo | `S` |
| Mover izquierda | `A` |
| Mover derecha | `D` |
| Dash | `Shift izquierdo` |
| Interactuar / hablar / comprar | `E` |
| Abrir mapa | `M` |
| Pausa | `Esc` |
| Reiniciar sala | `R` |

Los controles pueden modificarse desde **Ajustes**. Se puede acceder a esta pantalla desde el menú principal o desde el menú de pausa dentro del juego.

## Estructura del proyecto

La organización principal del proyecto es:

- `assets/`: recursos multimedia y visuales.
- `assets/images/`: imágenes del juego, logos y recursos visuales generales.
- `assets/Mapas/`: fondos y recursos relacionados con mapas.
- `assets/mp4/`: vídeos utilizados en menús o pantallas.
- `assets/Music/`: música, efectos y sonidos.
- `assets/Niveles/`: niveles creados con Tiled y archivos `.tmx`.
- `assets/Sprites/`: sprites de personajes, plumas y otros elementos.
- `assets/VSX/`: voces y sonidos contextuales de personajes.
- `docs/`: documentación del proyecto.
- `docs/Dialogues/`: textos de diálogos de los personajes.
- `docs/memoria.md`: memoria técnica del proyecto.
- `src/`: código fuente del juego.
- `src/data/`: guardado de partida y configuración.
- `src/models/`: modelos base de personajes.
- `src/views/`: pantallas del juego, como menú, ajustes, pausa, créditos y vista principal.

## Ajustes

Desde la pantalla de ajustes se puede modificar:

- Volumen de música.
- Volumen de voces.
- Volumen de efectos.
- Pantalla completa.
- Controles del jugador.

La configuración se guarda automáticamente en `src/data/settings.json`.

## Guardado

El progreso de la partida se guarda en `src/data/savegame.json`. El juego registra la última habitación segura visitada, vidas, plumas, mejoras desbloqueadas y progreso de diálogos.

## Documentación

La memoria completa del proyecto está en:

```text
docs/memoria.md
```

¡Disfrutad del proyecto!
