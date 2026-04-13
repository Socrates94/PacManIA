# Segundo Parcial: Inteligencia Artificial

**Institución**: Benemérita Universidad Autónoma de Puebla  
**Facultad**: Ciencias de la Computación  
**Posgrado**: Maestría en Ciencias de la Computación  
**Profesor**: Dr. Iván Olmos Pineda  
**Alumno**: José Daniel Flores Morales  
**Matrícula**: 225470536  

---

## Introducción

Este trabajo presenta el desarrollo de un sistema de Inteligencia Artificial aplicado a un Pac-Man en 3D. El motor del juego fue construido con Python, apoyándose en Pygame para el control de la lógica y la gestión de recursos de audio, mientras que la parte visual descansa sobre OpenGL. El reto no solo fue el renderizado, sino lograr que los fantasmas tomen decisiones coherentes dentro del laberinto mediante el algoritmo de Poda Alfa-Beta, respetando en todo momento una matriz de control predefinida que limita sus movimientos.

---

## Consideraciones Previas: Transición a 2D y Control de Latencia

Antes de desarrollar la Inteligencia Artificial, fue necesario acondicionar el entorno base proporcionado para garantizar una jugabilidad óptima y facilitar la depuración visual del tablero. Esto implicó dos modificaciones clave en el motor original.

### 1. Transición de Semi-3D a Vista 2D Ortogonal
El código base renderizaba el laberinto utilizando una perspectiva tridimensional completa, lo que distorsionaba visualmente las esquinas y dificultaba juzgar mentalmente las intersecciones (un aspecto crucial para comprobar si los fantasmas realizaban los giros correctamente). 

Para resolver esto, reemplacé la configuración de perspectiva por una matriz de **proyección ortogonal**, "aplastando" la profundidad y logrando una vista cenital 2D perfecta, sin alterar las verdaderas coordenadas 3D de los modelos en el espacio estricto de OpenGL.

**Código implementado en `main.py`:**
```python
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Sustitución de perspectiva por proyección ortogonal pura
    # screen_width=900, screen_height=800 -> ratio de 1.125
    glOrtho(-230.625, 230.625, -205.0, 205.0, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # La cámara se eleva sobre el eje Y mirando hacia abajo (plano XZ)
    gluLookAt(EYE_X, EYE_Y, EYE_Z, CENTER_X, CENTER_Y, CENTER_Z, UP_X, UP_Y, UP_Z)
```

### 2. Implementación de Buffer de Teclado
Uno de los mayores obstáculos al inicializar el proyecto era la extrema latencia de respuesta para mover a Pac-Man. Al girar en un cruce, si el usuario no presionaba la tecla en el **frame exacto** donde el modelo coincidía matemáticamente con la Matriz de Control (MC), el juego ignoraba el comando.

Diseñé un "buffer de teclado" o ventana de tolerancia. Cuando se detecta una pulsación de tecla válida, se captura la dirección deseada (`act_teclado`) manteniéndola activa por un máximo de 20 frames (`lon_ventana`). Si el jugador cruza una intersección mientras este buffer siga vivo, asume el giro.

**Lógica integrada en el bucle del juego (`main.py`):**
```python
    # Variables de buffer globales
    act_teclado = -1
    delta = 0
    lon_ventana = 20 # frames de vida para el evento

    # Detección y refresco de intención de movimiento
    if keys[pygame.K_w]: act_teclado = 0; delta = 0
    elif keys[pygame.K_d]: act_teclado = 1; delta = 0
    elif keys[pygame.K_s]: act_teclado = 2; delta = 0
    elif keys[pygame.K_a]: act_teclado = 3; delta = 0

    # Decaimiento del buffer por frames transcurridos
    if act_teclado != -1:
        delta += 1
        if delta > lon_ventana:
            act_teclado = -1 
            
    # El comando amortiguado se transfiere para evaluación
    pc.update(act_teclado)
```
Esto eliminó la frustración durante de las pruebas, haciendo que cruzar y doblar en las esquinas estrechas se sintiera fluido. Un requisito fundamental para poder testear rutas de escape justas contra los algoritmos caza de la IA.

---

## Respuesta 1: Movimiento Aleatorio de Blinky (Rojo)

Para la primera parte del examen, implementé el comportamiento de Blinky basándome en decisiones aleatorias. Aunque parece una tarea sencilla, el desafío técnico consistió en asegurar que el fantasma se moviera de forma fluida y natural por el laberinto sin violar las reglas básicas de navegación.

### Lógica de navegación
El movimiento de Blinky no es puramente azaroso; se rige por un proceso de filtrado que evita comportamientos erráticos como el "rebote" constante:

1.  **Detección de cruces**: Utilicé la Matriz de Control (MC) para que el fantasma solo evalúe cambios de dirección cuando realmente llega a un nodo o intersección válida.
2.  **Eliminación del retroceso**: Programé una lógica que calcula la dirección opuesta a la que lleva el fantasma en ese momento. Esta dirección se descarta automáticamente de la lista de opciones posibles, forzándolo a seguir adelante o girar, pero nunca a "darse la vuelta" a menos que no tenga otra opción.
3.  **Selección de ruta**: Una vez que tenemos las direcciones permitidas, el sistema elige una al azar mediante el generador de números aleatorios integrado de Python.

### Implementación técnica
El fragmento clave de la clase `Ghost` que gestiona este comportamiento es el siguiente:

```python
def interseccion_random(self):
    # Localizamos la posición actual dentro de la matriz de lógica
    celId = self.MC[self.positionMC[1]][self.positionMC[0]]
    
    # Mapeo de IDs de la celda a los movimientos permitidos
    mapping = {10:0, 11:1, 12:2, 13:3, 21:4, 22:5, 23:6, 24:7, 25:8, 26:9, 27:10}
    
    if celId in mapping:
        self.option = list(self.options[mapping[celId]])
    
    # Aquí es donde evitamos que el fantasma regrese por donde vino
    self.dir_inv = (self.direction + 2) % 4
    if (celId != 0) and (celId != 26) and (celId != 27):
        if self.dir_inv in self.option:
            self.option.remove(self.dir_inv)
    
    # Si hay opciones legales, elegimos una aleatoriamente
    size = len(self.option)
    if size > 0:
        dir_rand = random.randint(0, size - 1)
        self.direction = self.option[dir_rand]
```

Este enfoque garantiza que Blinky explore el mapa de forma autónoma, sirviendo como un elemento de distracción mientras otros fantasmas aplican algoritmos de persecución más directos.

---

## Respuesta 2: Pinky y la Poda Alfa-Beta con Estrategia de Emboscada

Para Pinky (el fantasma rosa), el objetivo era implementar un sistema de toma de decisiones mucho más agresivo e inteligente. En lugar de simplemente perseguir a Pac-Man, diseñé una función de evaluación que intenta "leer" el juego para interceptar al jugador.

### Diseño de la Función de Evaluación
La efectividad de la Poda Alfa-Beta depende totalmente de su función de evaluación. Para Pinky, integré dos componentes heurísticos principales:

1.  **Heurística de Interceptación (Ambush)**: A diferencia de una persecución directa, programé a Pinky para que su objetivo sea un punto situado 2 posiciones por delante de la tendencia de movimiento de Pac-Man. Esto simula una emboscada, permitiendo que el fantasma corte rutas de escape en lugar de simplemente seguir el rastro del jugador.
2.  **Manhattan Proximity**: Como respaldo, mantengo un peso sobre la distancia directa. Esto evita que Pinky se aleje demasiado del jugador si el punto de emboscada resulta ser inaccesible temporalmente.

La puntuación final es una suma ponderada: `Utilidad = -(0.7 * Distancia_Emboscada + 0.3 * Distancia_Directa)`. El signo negativo es crucial porque, como agentes maximizadores, los fantasmas buscan el valor más alto (que en este caso es la menor penalización por distancia).

### Justificación del Diseño
Elegí este modelo de "doble objetivo" porque resuelve el problema de los fantasmas que se limitan a seguir la espalda del jugador. Al intentar predecir hacia dónde va Pac-Man, el algoritmo de Alfa-Beta descarta ramas de búsqueda que no conducen a un cierre de caminos, haciendo que el movimiento de Pinky se sienta mucho más estratégico. Con una profundidad de búsqueda de 4 niveles, el fantasma logra anticipar colisiones en las intersecciones cercanas sin comprometer el rendimiento.

---

## Respuesta 3: Movimiento Colaborativo de Inky y Clyde (Caza en Manada)

Para los fantasmas Inky (Cian) y Clyde (Naranja), implementé una estrategia de "caza en manada" que los obliga a trabajar como un equipo coordinado para acorralar a Pac-Man desde ángulos opuestos.

### Estrategia de la "Tenaza"
La lógica colaborativa se basa en una distribución de roles dinámicos que evita que ambos fantasmas sigan la misma ruta, lo cual suele ser el punto débil de muchas implementaciones de IA:

1.  **Sincronización de objetivos**: Inky mantiene una persecución directa y agresiva, mientras que Clyde calcula un "punto de espejo" en el flanco opuesto de Pac-Man. Si Inky está atacando desde el norte, Clyde intentará rodear por el sur, creando una tenaza táctica.
2.  **Heurística de Separación**: Añadí un componente a la función de evaluación que penaliza a los fantasmas de la manada si se encuentran a menos de 3 celdas de distancia entre sí cuando están cerca de Pac-Man. Esto los fuerza a diversificarse y cubrir más salidas de escape del laberinto simultáneamente.

### Función de Evaluación Colaborativa
La función resultante integra tres factores:
`Utilidad = -(Distancia_Objetivo + Penalización_Tabú + Penalización_Amontonamiento)`

Al compartir la información de sus posiciones en el bucle principal del juego, los agentes de tipo 3 pueden detectar si su compañero ya está cubriendo una sección del laberinto, permitiendo que la Poda Alfa-Beta elija caminos que maximicen el área de control del equipo. Esta coordinación hace que el escape para el jugador sea significativamente más difícil, ya que los fantasmas no solo lo persiguen, sino que intentan cerrarle el paso de forma conjunta.

---

## Respuesta 4: Concepto de Agente y Estrategias Heurísticas

Para establecer la base teórica del proyecto, primero definimos qué es un **agente**. En inteligencia artificial, un agente es cualquier entidad que percibe su entorno mediante sensores (lectura del estado de la matriz y distancias) y ejecuta acciones (movimientos en las coordenadas) de forma autónoma para lograr un objetivo definido. En este simulador, tanto Pac-Man como los fantasmas operan bajo esta arquitectura.

Para maximizar la inteligencia de los agentes sin saturar el rendimiento, integré dos estrategias principales que robustecen la Poda Alfa-Beta y resuelven vulnerabilidades clásicas del motor de juego:

### 1. Minimax Dependiente del Adversario
El mecanismo clásico de Minimax asume que el rival siempre buscará la jugada más destructiva. Sin embargo, en Pac-Man los fantasmas no juegan de forma matemáticamente perfecta; responden a comportamientos programados y cometen "errores" posicionales según su rol.
Para escalar el algoritmo, el agente aplica un Minimax dependiente del adversario, explotando directamente los patrones predecibles del enemigo. En vez de expandir el árbol de decisión hacia escenarios de fatalidad irreal (evaluando qué pasaría si el fantasma jugara perfecto), el agente adapta el cálculo asumiendo los movimientos deterministas de su cazador. Esto poda inherentemente decisiones innecesarias y permite al agente anticiparse al movimiento real con gran eficiencia de cálculo.

### 2. Espera del Reposo (Quiescence Search)
El principal riesgo al truncar el análisis computacional a una profundidad máxima fija (como 4 niveles de búsqueda) es caer presa del "Efecto de horizonte limitado". El algoritmo puede priorizar una ruta que parece segura en el nivel 4, sin identificar que al movimiento 5 será capturado indefectiblemente.
Para evitar descuidos críticos, se emplea la *Espera del reposo*. Al tocar la profundidad límite, el agente evalúa si el estado es sumamente volátil (ej. inminente cercanía o emboscada en curso). Si el entorno es hostil, la evaluación de esa rama no se detiene; se expande un par de profundidades extra hasta llegar a un estado de reposo temporal donde el cálculo heurístico sea confiable. Esta técnica garantiza solidez en el control posicional y evita "suicidios" accidentales provocados por cortas visiones espaciales.

---

## Respuesta 5: Demostración y Video del Proyecto

Para facilitar la evaluación y presentar los resultados de forma profesional, he desplegado una **Showcase Landing Page** donde se detalla el funcionamiento del sistema y se aloja el video demostrativo del examen.

**Enlace al Proyecto**: [Presentación Pac-Man IA](https://github.com/Socrates94/PacManIA)  
*(Nota: El sitio web configurado en Netlify contiene el video explicativo de 5 minutos solicitado en las instrucciones).*

### Pruebas de Ejecución
En el video se demuestran los siguientes escenarios:
1.  **Aislamiento de Blinky**: Movimiento aleatorio coherente en un mapa vacío.
2.  **Interceptación de Pinky**: Demostración de cómo Pinky corta el paso en intersecciones críticas.
3.  **Caza coordinada de Inky/Clyde**: Ejemplo de cómo los dos fantasmas colaboran para atrapar a Pac-Man en un callejón sin salida.
4.  **Resilencia del Algoritmo**: Estabilidad de la Poda Alfa-Beta frente a cambios bruscos de dirección del jugador.

---

## Conclusiones

La implementación de este proyecto permitió integrar conceptos avanzados de Inteligencia Artificial en un entorno gráfico de tiempo real. El uso de la Poda Alfa-Beta no solo mejoró la competitividad de los enemigos, sino que, mediante la integración de heurísticas estratégicas y mejoras como la búsqueda Tabú, se logró un equilibrio entre dificultad para el jugador y eficiencia computacional. El proyecto cumple con todos los objetivos planteados en el segundo parcial, demostrando la versatilidad de los algoritmos de búsqueda en espacios de estados complejos.

---

## Nota Técnica: Portabilidad y Compatibilidad (Windows/Linux)

Dado que el desarrollo se realizó en un entorno Linux pero la evaluación podría realizarse en Windows, se integraron las siguientes previsiones técnicas para garantizar la portabilidad del código:

1.  **Manejo Universal de Paths**: Se utilizó el módulo `os.path` de forma sistemática para la carga de texturas, sonidos y archivos CSV. Esto evita errores de ejecución por el uso de diferentes separadores de directorios (`/` vs `\`).
2.  **Librerías Cross-Platform**: El motor utiliza `Pygame`, `PyOpenGL`, `NumPy` y `Pandas`, las cuales poseen implementaciones nativas consistentes en ambos sistemas operativos.
3.  **Gestión de Reinicio**: La lógica de retorno al menú emplea `os.execl`, una llamada de bajo nivel que permite a Python relanzar el proceso de forma limpia. Se recomienda ejecutar el proyecto desde una terminal estándar para asegurar que la redirección del flujo sea exitosa.
4.  **Renderizado OpenGL**: Se optó por un perfil de OpenGL estandarizado (v2.1+) para asegurar compatibilidad con controladores gráficos de Windows sin requerir configuraciones de sombreadores (shaders) específicas de cada fabricante.

---
**Fecha de Entrega**: 19 de abril de 2026.
