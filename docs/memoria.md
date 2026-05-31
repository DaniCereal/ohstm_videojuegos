# Memoria del proyecto: OH Hermes Sent The Message

## 1. Introducción

**OH Hermes Sent The Message** es un videojuego de plataformas 2D desarrollado en Python con la librería Arcade. El proyecto toma como base una estructura de juego tipo metroidvania: el jugador controla a Hermes, explora un conjunto de salas conectadas, desbloquea mejoras de movilidad, conversa con personajes mitológicos y avanza por un mapa dividido en niveles.

El objetivo principal del desarrollo ha sido construir una experiencia jugable centrada en movimiento, exploración y progresión. A lo largo del proyecto se han ido incorporando sistemas de guardado, salas seguras, diálogos, audio contextual, economía mediante plumas, mejoras, mapa de navegación y transiciones entre salas.

## 2. Concepto del juego

El juego está ambientado en una interpretación mitológica en la que Hermes recorre distintas zonas conectadas entre sí. El diseño del mapa se organiza como una cuadrícula de salas, donde cada sala se identifica mediante coordenadas de fila y columna. Por ejemplo, la sala `(2, 0)` representa una posición concreta dentro del mapa general.

La estructura global se divide en varias zonas:

- Tierra: zona inicial y núcleo de exploración.
- Olimpo: salas superiores del mapa, asociadas a Zeus y a una música diferenciada.
- Inframundo: salas inferiores, asociadas a Hades y a otra ambientación sonora.
- Habitaciones seguras: salas especiales que funcionan como checkpoint y restauran la vida.

El jugador empieza una nueva partida en la sala inicial `(2, 0)`. A medida que avanza puede encontrar a personajes como Dédalo, Zeus y Hades, además de comprar mejoras usando plumas.

## 3. Tecnologías utilizadas

El proyecto se ha desarrollado principalmente con:

- **Python** como lenguaje principal.
- **Arcade** como motor 2D para renderizado, físicas, sprites, sonido y gestión de vistas.
- **Tiled** para la construcción de mapas `.tmx`.
- **JSON** para guardar configuración y progreso de partida.
- Recursos gráficos y sonoros almacenados dentro de `assets/`.

La entrada principal del juego se encuentra en `src/main.py`. Desde ahí se crea la ventana de Arcade, se cargan los ajustes y se muestra el menú principal.

## 4. Estructura del proyecto

La organización general del proyecto es:

- `src/main.py`: punto de entrada del juego.
- `src/constants.py`: constantes generales de ventana, escalas y movimiento.
- `src/data/settings.py`: configuración de audio, vídeo y controles.
- `src/data/savegame.py`: sistema de guardado y carga de partida.
- `src/models/character.py`: clase base para personajes.
- `src/models/player.py`: lógica de animaciones y estado del jugador.
- `src/views/game_view.py`: vista principal del juego y núcleo de la lógica jugable.
- `src/views/menu_view.py`: menú principal.
- `src/views/pause_view.py`: menú de pausa.
- `src/views/settings_view.py`: pantalla de ajustes.
- `src/views/credits_view.py`: créditos.
- `assets/Niveles/`: mapas `.tmx`.
- `assets/Sprites/`: sprites del personaje, NPCs, plumas y otros elementos.
- `assets/Music/`: música y efectos de sonido.
- `assets/VSX/`: voces de personajes y sonidos contextuales.
- `docs/Dialogues/`: textos de los diálogos.

## 5. Sistema de salas y mapa

El mapa del juego se representa como una cuadrícula. Cada sala tiene una coordenada `(fila, columna)` y se asocia a un archivo `.tmx` dentro de `assets/Niveles/`.

En `game_view.py` existe un diccionario `LEVEL_FILES` que relaciona cada coordenada con su archivo de mapa. A partir de él se construyen:

- `LEVEL_GRID`: salas que existen realmente porque tienen archivo `.tmx`.
- `LEVEL_ORDER`: orden de salas cargables.
- `LEVELS`: lista de rutas de mapas usadas por el juego.

Las conexiones entre salas se definen manualmente en `ROOM_CONNECTIONS`. Cada sala puede tener salidas por:

- `left`
- `right`
- `top`
- `bottom`

Cuando el jugador cruza un borde de pantalla, el juego comprueba si existe una conexión en esa dirección. Si existe, se carga la sala de destino. Si el jugador cae hacia abajo y no hay una sala conectada, se considera caída al vacío y se pierde una vida.

## 6. Spawn y transición entre salas

El sistema de aparición del jugador depende del lado por el que entra en la sala. Se usan puntos de spawn predefinidos por dirección:

- Entrada por la izquierda.
- Entrada por la derecha.
- Entrada por abajo.
- Entrada por arriba.

Después de colocar al jugador, el juego ejecuta una corrección de colisión para evitar que aparezca dentro de plataformas o bloques sólidos. Este sistema se implementó para solucionar problemas en los que Hermes aparecía incrustado en el terreno al iniciar partida o al bajar a determinadas salas.

## 7. Movimiento del jugador

El jugador usa un sistema de movimiento de plataformas con físicas de Arcade. Las acciones principales son:

- Movimiento horizontal.
- Salto.
- Coyote time.
- Salto variable.
- Dash.
- Doble salto.
- Wall jump.
- Wall slide.

Algunas habilidades están bloqueadas al inicio y se desbloquean mediante mejoras:

- `has_double_jump`
- `has_dash`
- `has_wall_jump`

El wall jump incluye control para evitar saltos consecutivos abusivos en la misma pared. Al tocar suelo se reinicia la posibilidad de hacer un salto grande, mientras que repetir saltos en la misma pared produce saltos más pequeños.

## 8. Animaciones y sprites

El personaje principal se implementa mediante `PlayerCharacter`, que carga animaciones desde carpetas de sprites:

- `Estatico`
- `Movimiento`
- `Salto`
- `Caida`
- `Dash`

Cada animación se carga como una secuencia de texturas y se guarda también su versión invertida horizontalmente. Esto permite que el personaje mire a izquierda o derecha sin duplicar manualmente todos los sprites.

La animación activa depende del estado del jugador:

- Si está haciendo dash, usa la animación de dash.
- Si cae o se desliza por pared, usa caída.
- Si sube, usa salto.
- Si se mueve horizontalmente, usa caminar.
- Si no se mueve, usa idle.

## 9. Sistema de vidas y Game Over

El jugador empieza con 3 vidas. Si cae al vacío o toca una zona de reset, pierde una vida y vuelve al punto de entrada de la sala actual. Si pierde las 3 vidas, se muestra la pantalla de Game Over.

Desde Game Over, el botón de reintentar carga el último checkpoint guardado. Si el jugador había visitado una habitación segura, reaparece allí con las vidas restauradas.

El sistema evita duplicar la música al reiniciar desde Game Over: se detiene la música de la pantalla de muerte y se crea una única instancia de la vista de juego.

## 10. Habitaciones seguras y guardado

Las habitaciones seguras están definidas en `SAFE_ROOMS`:

- `(1, 1)`
- `(1, 5)`
- `(4, 4)`

Al entrar en una habitación segura:

- Se guarda la partida.
- Se registra esa sala como último checkpoint.
- Se restauran las vidas.
- Se guardan plumas, mejoras y progreso de diálogos.
- Se reinicia el estado temporal de plumas recogidas en salas normales.

El guardado se almacena en `src/data/savegame.json`. La lógica se encuentra en `src/data/savegame.py`.

El guardado incluye:

- Sala actual.
- Última habitación segura.
- Lado de entrada.
- Puntuación.
- Vidas y vida máxima.
- Progreso de Dédalo.
- Estado de conversación con Zeus.
- Estado de conversación con Hades.
- Progreso parcial de diálogos.
- Número de plumas.
- Mejoras desbloqueadas.

## 11. Nueva partida y continuar

Desde el menú principal hay dos formas de empezar:

- **Jugar**: carga el progreso guardado, si existe.
- **Nueva partida**: reinicia el archivo de guardado y empieza desde cero.

Al empezar una partida desde cero, el jugador aparece en el primer nivel real del recorrido, la sala `(2, 0)`, y no en la primera habitación segura.

## 12. Sistema de plumas

Las plumas funcionan como recurso de progresión y moneda para comprar mejoras.

Tipos de plumas:

- Pluma normal: suma 1.
- Pluma dorada: suma más cantidad.
- Pluma azul: inicia un reto temporal con una estela de plumas.

El sistema registra qué plumas se han recogido de forma individual. Esto evita que desaparezcan todas las plumas de una sala al recoger solo una. Si el jugador sale y vuelve a entrar en una sala, aparecen las plumas que todavía no había recogido.

Al entrar en una habitación segura se reinicia el estado temporal de plumas, de forma que las plumas vuelven a estar disponibles.

## 13. Mejoras y tiendas

El juego incluye tiendas o puntos de compra donde se gastan plumas para obtener mejoras. Las mejoras implementadas son:

- Vida extra.
- Dash.
- Doble salto.
- Salto en pared.

La compra de vida aumenta la vida máxima y actualiza el HUD para mostrar el nuevo corazón. Las mejoras de movilidad se guardan en la partida, por lo que se mantienen al cambiar de sala, reiniciar desde checkpoint o continuar partida.

## 14. Diálogos y NPCs

El juego incluye un sistema de diálogo con cajas de texto. Cada línea puede tener un personaje asociado. Si una línea no especifica personaje, se muestra sin nombre.

NPCs principales:

- Dédalo.
- Zeus.
- Hades.

Los textos se almacenan en `docs/Dialogues/`:

- `DedaloFirstTimeMeet`
- `DedaloSecondTimeMeet`
- `ZeusFirstTimeMeet`
- `HadesNoTalkingToZeus`
- `HadesTalkingToZeus`

El sistema permite salir de una conversación mediante un botón de salir o con `Esc`. Si el jugador vuelve a hablar con el personaje, la conversación continúa desde la última línea vista.

## 15. Dédalo

Dédalo aparece en la sala `(2, 1)`. Su primera conversación sirve como punto importante de progresión, porque después de hablar con él se desbloquea el acceso al mapa grande.

También existe una segunda conversación con Dédalo que se activa después de conseguir el wall jump. Si el jugador vuelve a hablar con él después de completar sus diálogos, se repite una frase final.

## 16. Zeus y Hades

Zeus tiene su propia conversación y se registra si el jugador ya ha hablado con él.

Hades aparece en la sala `(4, 2)`. Su conversación depende de si Hermes ha hablado antes con Zeus:

- Si no ha hablado con Zeus, se usa `HadesNoTalkingToZeus`.
- Si ya ha hablado con Zeus, se usa `HadesTalkingToZeus`.

Esto permite que el diálogo cambie según el progreso narrativo del jugador.

## 17. Audio y voces

El proyecto usa música por zonas:

- Música de Tierra.
- Música de Olimpo.
- Música de Inframundo.
- Música de menú y Game Over.

Además, los diálogos tienen voces asociadas. Cuando habla un personaje, se reproduce aleatoriamente un audio de su carpeta:

- `assets/VSX/Dedalo`
- `assets/VSX/Zeus`
- `assets/VSX/Hades`
- `assets/VSX/Hermes/HermesSpeaking`

Hermes también tiene sonidos de movimiento. En acciones como salto o dash, existe una probabilidad de reproducir una línea de movimiento desde `assets/VSX/Hermes/Movement`.

## 18. Mapa grande desbloqueable

Inicialmente se implementó un minimapa en el HUD, pero se cambió por motivos de rendimiento. El mapa actual se abre como una vista superpuesta grande, similar a juegos como Valorant.

Características:

- Se abre con la tecla `M` por defecto.
- La tecla se puede cambiar desde ajustes.
- Solo está disponible después de hablar con Dédalo por primera vez.
- Muestra salas existentes.
- Muestra conexiones entre salas.
- Marca habitaciones seguras.
- Marca la sala actual del jugador.

Este cambio reduce carga en el juego porque el mapa no se dibuja constantemente en cada frame.

## 19. Ajustes y controles

La pantalla de ajustes permite modificar:

- Volumen de música.
- Volumen de voces.
- Volumen de efectos.
- Pantalla completa.
- Controles de movimiento.
- Dash.
- Pausa.
- Reinicio.
- Mapa.

Los controles se guardan en `src/data/settings.json`, por lo que se mantienen entre ejecuciones.

## 20. Menús y vistas

El proyecto usa el sistema de vistas de Arcade:

- `MainMenu`: menú principal.
- `GameView`: juego.
- `PauseMenuView`: pausa.
- `SettingsView`: ajustes.
- `CreditsView`: créditos.
- `GameOverView`: pantalla de fin de partida.

Esta división permite separar responsabilidades. Por ejemplo, el menú principal no contiene lógica de físicas, y la pantalla de ajustes puede abrirse desde menú o pausa.

## 21. Eliminación de enemigos

Durante el desarrollo se decidió eliminar la lógica de enemigos. Se retiraron:

- Clases de enemigos.
- Carga de enemigos desde Tiled.
- Colisiones contra enemigos.
- Actualización y patrullaje.
- Referencias a capas `Enemies`.

La decisión simplifica el diseño actual y centra la experiencia en exploración, movimiento, diálogos, plumas y progresión.

## 22. Problemas encontrados y soluciones

Durante el desarrollo se resolvieron varios problemas:

- El jugador aparecía incrustado en plataformas: se añadió corrección de spawn.
- Las transiciones entre salas no siempre funcionaban: se centralizaron las conexiones en `ROOM_CONNECTIONS`.
- El wall jump permitía encadenados excesivos: se añadió control según pared y reinicio al tocar suelo.
- Al perder todas las vidas se cargaba mal el progreso: se separó Game Over del respawn desde checkpoint.
- La música se duplicaba al reintentar: se corrigió la creación de vistas y la parada de música.
- Las plumas desaparecían por sala completa: se pasó a registro individual por pluma.
- El minimapa permanente producía lag: se sustituyó por mapa grande bajo demanda.

## 23. Estado actual

El juego cuenta actualmente con:

- Movimiento base de plataformas.
- Dash, doble salto y wall jump desbloqueables.
- Sistema de salas conectadas.
- Checkpoints mediante habitaciones seguras.
- Guardado y carga de partida.
- Game Over con reintento desde checkpoint.
- Plumas como recurso.
- Tiendas de mejoras.
- Diálogos con Dédalo, Zeus y Hades.
- Voces aleatorias por personaje.
- Sonidos contextuales de Hermes.
- Mapa grande desbloqueable.
- Ajustes configurables.
- Menú, pausa, créditos y pantalla de Game Over.

## 24. Posibles mejoras futuras

Algunas mejoras posibles para continuar el desarrollo son:

- Añadir más variedad visual a NPCs pendientes.
- Pulir la interfaz del mapa grande.
- Guardar de forma persistente las compras de vida por sala concreta.
- Añadir más contenido narrativo.
- Revisar el balance de costes de plumas.
- Añadir animaciones específicas para NPCs secundarios.
- Mejorar la respuesta visual al desbloquear habilidades.
- Añadir una pantalla de tutorial o indicaciones iniciales.

## 25. Conclusión

El proyecto ha evolucionado desde un prototipo de movimiento en plataformas hasta una base funcional de juego de exploración. La estructura actual permite seguir añadiendo salas, diálogos, mejoras y contenido narrativo sin rehacer los sistemas principales.

Los sistemas más importantes ya están conectados entre sí: mapa, salas, guardado, checkpoints, progresión, diálogos, audio y mejoras. Esto deja una base sólida para continuar desarrollando el juego y convertirlo en una experiencia más completa.
