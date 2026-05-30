# tdv-platform
El proyecto de un videojuego de la asignatura "Tecnología de Videojuegos" de la UAH creado por Luis Azaña, Daniel Cordos, Daniel Silva y Brayan Nicolás Cotoara.

Este proyecto se desarrolla mediante el uso de Visual Studio Code con el lenguaje de programacion de Python y el uso de las libreria Arcade

Para que funcione este proyecto, se necesita que su Visual Studio Code contenga,o que su ordenador pueda procesar, las versiones que este en requirements.txt. Para poder instalar las versiones, tendras que poner la siguiente linea en la terminal :
    pip install -r requirements.txt

Para ejecutar este videojuego se necesitara la instalacion de lo dicho con anterioriad por motivos de funcionalidad. Tras la instalacion de las versiones, tendreis que ejecutar el archivo main.py desde vuestro Visual Studio Code para que empieze a funcionar.


La organizacion de este trabajo se divide en tres carpetas:
    assets: Contiene los recursos multimedia y visuales.
        Images: Imágenes con el logo del juego y de la Universidad de Alcalá.
        Mapas: Fondos para los diferentes niveles, al igual que las plataformas que los construyen.
        Mp4, SFX y Music: Música del juego (de cada nivel, pantallas de ajuste o menú), efectos especiales y sonidos (tanto al hablar como de las acciones de los personajes).Niveles: Todos los niveles creados en Tiled, los tilesets que los conforman y la perspectiva de cómo se vería todo junto guardado en un .world.
        Sprites: Representaciones de nuestros personajes en formato de sprites con un toque artístico de pixel art.
    Docs: Documentación del proyecto.
        Memoria: Para dar contexto a la historia y a la aparición de los personajes. También incluye la temática que va a tener el juego tanto en historia como en jugabilidad.Diálogos: Los textos que van a tener nuestros personajes entre sí.
    Src: Código fuente del juego.
        Data: La información de guardado para almacenar el progreso.
        Generación: El código encargado de generar los personajes con sus respectivos sprites y datos acerca de su movimiento.
        Pantallas: La creación de las diferentes pantallas que puede haber en el videojuego, como el menú, los ajustes e incluso las pantallas donde se va a desarrollar el juego.



¡Disfrutad del proyecto!