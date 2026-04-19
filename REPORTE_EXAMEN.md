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

1. **Detección de cruces**: Utilicé la Matriz de Control (MC) para que el fantasma solo evalúe cambios de dirección cuando realmente llega a un nodo o intersección válida.
2. **Eliminación del retroceso**: Programé una lógica que calcula la dirección opuesta a la que lleva el fantasma en ese momento. Esta dirección se descarta automáticamente de la lista de opciones posibles, forzándolo a seguir adelante o girar, pero nunca a "darse la vuelta" a menos que no tenga otra opción.
3. **Selección de ruta**: Una vez que tenemos las direcciones permitidas, el sistema elige una al azar mediante el generador de números aleatorios integrado de Python.

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

Este enfoque garantiza que Blinky explore el mapa de forma autónoma, sirviendo como un elemento de distracción mie## Respuesta 2: Pinky y Poda Alfa-Beta

Para el comportamiento de Pinky implementamos un agente predictivo guiado por Poda Alfa-Beta y una heurística directa sobre la distancia Manhattan. En lugar de perseguir iterativamente celda a celda, Pinky calcula un árbol Minimax acotado a 4 niveles donde actúa como nodo maximizador.

Su objetivo es procesar matemáticamente la coordenada del objetivo en tiempo real, deconstruyendo la métrica en una evaluación base: `base_score = -(abs(g_row - p_row) + abs(g_col - p_col))`.
Con este mecanismo, Pinky mapea el escenario y poda automáticamente rutas evasivas que lo alejarían a largo plazo, consolidando un patrón de rastreo incesante cuya eficiencia descarta sub-arboles vacíos de forma nativa sin sacrificar su ejecución en tiempo real.

---

## Respuesta 3: Movimiento Colaborativo de Inky y Clyde (Caza en Manada)

La inteligencia en equipo de Inky y Clyde prescinde de compensaciones estáticas o lógicas ciegas (offsets geométricos en los targets que causaban bloqueos) y apalanca en su lugar un rastreo óptimo utilizando el mismo núcleo resolutivo Alfa-Beta perfeccionado.

Al instanciar a ambos agentes con una agresividad extrema asimétrica, **el concepto de pincer o acorralamiento de manada emerge geográficamente de sus coordenadas de origen**. Dado que Inky evalúa la red naciendo de una coordenada perimetral base y Clyde desde un flanco opuesto del mapa, el trazado y cálculo de la trayectoria de sus propios árboles clausura pasillos de forma coordinada, generando una auténtica red perimetral que acorrala al adversario forzándolo al fracaso estructural sin requerir pasarse posiciones entre ellos.

---

## Respuesta 4: Estrategias Alfa-Beta, Mejoras y Agente Inteligente

**¿Qué es un agente?**
En inteligencia artificial, un agente es cualquier entidad capaz de percibir su entorno autónomamente mediante sensores y actuar racionalmente vía actuadores para maximizar su eficiencia sobre un objetivo predeterminado. En esta representación, cada fantasma funge la definición de agente lógico: la lectura del `Grid MC` local conforma sus sensores de estado, el despachador central de Pygame actualiza las interfaces conformando sus actuadores mecánicos, y buscar la utilidad de intercepción negativa dictamina su nivel de racionalidad estricta.

Para blindar la operación algorítmica de los nodos en tiempo real apegándonos a los requerimientos de simulación, la matriz Alfa-Beta incrusta el siguiente cúmulo heurístico en su fase predictiva:

### 1. Búsqueda Ambiciosa (Move Ordering)

La agilidad real de una poda está delimitada en el orden generacional por el cual iteramos sobre cada ramal del cruce principal. Antes del ciclo recursivo, el nivel aplica un sort dinámico basado en una simulación artificial local de heurísticas anticipadas. El motor evaluador revisa a priori las interconexiones que arrojan un mejor base_score, maximizando de inicio. Hallar la mejor línea primero eleva el índice de truncamientos `Alfa/Beta` de los siguientes eslabones desatando un incremento bestial de recursos computacionales.

### 2. Continuación Heurística (Espera del Reposo)

Cortar simulación por niveles secos genera puntos muertos en la evaluación de horizontes locales (El enemigo perdiendo el vector un cuadro antes del impacto). Contrarrestamos eso adoptando un *Quiescence Search*: Toda vez que el nivel `depth == 0` entra contra la variable, el nodo es verificado. Si la contigüidad espacial del objetivo arroja métricas relativas inminentes (`Distancia <= 2`), la variable rompe el límite e inyecta la función `is_quiescence` dilatando la prospección dos ciclos extra a fondo previniendo abandonos ilógicos frente a los cruceros activos.

### 3. Memoria Tabú con Horizonte Limitado

Dada la topología compacta del diseño, neutralizamos parálisis infinitas en iteraciones. Incrustamos un control de memoria FIFO. El registro guarda iteración limitadamente a 3 transiciones pasadas. Durante la evaluación exploratoria en desarrollo, toda variable evaluada recayente sobre el Tabú absorbe un gravamen negativo abismal de `-100` pts. Así, Alpha-Beta mutila por default de las secuencias aquellos arboles que supongan ciclos o retrocesos ociosos, pero consintiendo regresar tarde a un pasillo si pasaron más de tres turnos limpios.

---

## Respuesta 5: Demostración y Video del Proyecto

Para facilitar la evaluación y presentar los resultados de forma profesional, he desplegado una **Showcase Landing Page** donde se detalla el funcionamiento del sistema y se aloja el video demostrativo del examen.

**Enlace al Proyecto**: [Presentación Pac-Man IA](https://github.com/Socrates94/PacManIA)
*(Nota: El sitio web configurado en Netlify contiene el video explicativo de 5 minutos solicitado en las instrucciones).*

### Pruebas de Ejecución

En el video se demuestran los siguientes escenarios:

1. **Aislamiento de Blinky**: Movimiento aleatorio coherente en un mapa vacío.
2. **Interceptación de Pinky**: Demostración de cómo Pinky corta el paso en intersecciones críticas.
3. **Caza coordinada de Inky/Clyde**: Ejemplo de cómo los dos fantasmas colaboran para atrapar a Pac-Man en un callejón sin salida.
4. **Resilencia del Algoritmo**: Estabilidad de la Poda Alfa-Beta frente a cambios bruscos de dirección del jugador.

---

## Conclusiones

La implementación de este proyecto permitió integrar conceptos avanzados de Inteligencia Artificial en un entorno gráfico de tiempo real. El uso de la Poda Alfa-Beta no solo mejoró la competitividad de los enemigos, sino que, mediante la integración de heurísticas estratégicas y mejoras como la búsqueda Tabú, se logró un equilibrio entre dificultad para el jugador y eficiencia computacional. El proyecto cumple con todos los objetivos planteados en el segundo parcial, demostrando la versatilidad de los algoritmos de búsqueda en espacios de estados complejos.

---

## Nota Técnica: Portabilidad y Compatibilidad (Windows/Linux)

Dado que el desarrollo se realizó en un entorno Linux pero la evaluación podría realizarse en Windows, se integraron las siguientes previsiones técnicas para garantizar la portabilidad del código:

1. **Manejo Universal de Paths**: Se utilizó el módulo `os.path` de forma sistemática para la carga de texturas, sonidos y archivos CSV. Esto evita errores de ejecución por el uso de diferentes separadores de directorios (`/` vs `\`).
2. **Librerías Cross-Platform**: El motor utiliza `Pygame`, `PyOpenGL`, `NumPy` y `Pandas`, las cuales poseen implementaciones nativas consistentes en ambos sistemas operativos.
3. **Gestión de Reinicio**: La lógica de retorno al menú emplea `os.execl`, una llamada de bajo nivel que permite a Python relanzar el proceso de forma limpia. Se recomienda ejecutar el proyecto desde una terminal estándar para asegurar que la redirección del flujo sea exitosa.
4. **Renderizado OpenGL**: Se optó por un perfil de OpenGL estandarizado (v2.1+) para asegurar compatibilidad con controladores gráficos de Windows sin requerir configuraciones de sombreadores (shaders) específicas de cada fabricante.

---

**Fecha de Entrega**: 19 de abril de 2026.
