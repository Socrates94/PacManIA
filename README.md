# Pac-Man con IA: Poda Alfa-Beta y Estrategias Colaborativas (Python + OpenGL)

Este es el proyecto final de Inteligencia Artificial para el comportamiento de agentes (fantasmas) en Pac-Man, desarrollado en Python utilizando **Pygame** para la lógica principal y **OpenGL** preconfigurado con una proyección 2D ortogonal estricta.

El proyecto destaca por la implementación de enfoques heurísticos avanzados para convertir a los fantasmas en entidades verdaderamente inteligentes, gestionando búsquedas eficientes en espacios de estados complejos.

## Requisitos Previos

Para ejecutar este proyecto, necesitas tener instalado:

- [Anaconda](https://www.anaconda.com/) o [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
- Python 3.9 (recomendado para la integración correcta de las bibliotecas gráficas).

## Instalación y Configuración

Sigue estos pasos para preparar tu entorno de trabajo:

1. **Activar el entorno de Conda:**
   ```bash
   conda activate pacman
   ```
   *(Si aún no has creado el entorno, puedes hacerlo con `conda create -n pacman python=3.9`)*

2. **Instalar dependencias necesarias:**
   Asegúrate de instalar los siguientes paquetes si es la primera vez que cargas el entorno:
   ```bash
   pip install pygame PyOpenGL numpy pandas
   ```

## Cómo Ejecutar el Proyecto

Una vez ubicado en la raíz del proyecto y con el entorno activado, ejecuta el simulador con:

```bash
python main.py
```

## Controles del Juego

| Tecla | Acción |
| :--- | :--- |
| **W** | Mover hacia Arriba (Eje Z) |
| **S** | Mover hacia Abajo (Eje Z) |
| **A** | Mover hacia la Izquierda (Eje X) |
| **D** | Mover hacia la Derecha (Eje X) |
| **ESC** | Salir del juego |

*(Nota: En la versión final, se implementó un buffer de teclado para minimizar la latencia de respuesta durante los cruces estrechos de la cuadrícula, haciendo más fluido el escape y testeo ante la IA).*

## Arquitectura de Inteligencia Artificial Implementada

El proyecto modela a los fantasmas como agentes, cada uno con una lógica distintiva y un rol específico dictado por los requerimientos técnicos:

* **Blinky (Fantasma Rojo) - Búsqueda Aleatoria Estructurada**:
  Se desplaza explorando el nivel a base de números aleatorios pero de forma **coherente**. Evalúa la matriz de control local absteniéndose activamente de retroceder por sus propios pasos, logrando recorridos más naturales que un simple "rebote", salvo que se tope contra algún callejón sin salida.

* **Pinky (Fantasma Rosa) - Poda Alfa-Beta Pura (Agente Predictivo)**:
  Ejerce asedio al jugador recurriendo al método Minimax en un horizonte determinado (4 niveles de profundidad). Pinky funge como nodo maximizador aplicando una métrica deductiva calculando su Distancia Manhattan frente a las coordenadas del jugador, sumado a una **bonificación de alineamiento** (+3 puntos) si logra posicionarse en el mismo eje (fila o columna) que el objetivo, optimizando emboscadas rápidas en pasillos rectos.

* **Inky y Clyde (Azules/Naranjas) - Caza en Manada (Flanking)**:
  En lugar de seguir la estela inmediata del jugador, operan bajo un enrutamiento colaborativo buscando un acorralamiento ("pincer"). Este comportamiento emerge de instanciar a ambos agentes evaluando la misma red predictiva Alfa-Beta pero naciendo desde cuadrantes opuestos del mapa, forzando cortes geográficos y cerrando vías de escape para Pac-Man basado en su agresividad algorítmica.

### Optimizaciones del Motor Minimax:

La evaluación exhaustiva del árbol exigió aplicar técnicas de ahorro y mejora de decisiones heurísticas implementadas en el script `Ghost.py`:

- **Búsqueda Ambiciosa (Move Ordering):** Reordenamiento dinámico a priori de los ramales antes de expandirlos iterativamente, logrando truncamientos inmediatos (Beta <= Alfa o Alfa >= Beta) que redujeron sustancialmente el número de nodos evaluados en vano.
- **Continuación Heurística (Quiescence Search):** Atenuación del "Efecto de horizonte limitado". Se expanden temporalmente proyecciones "inestables" (proximidad espacial <= 2) extendiendo la ramificación dos ciclos adicionales en profundidad cero, impidiendo cesar cálculos al filo de una captura inmediata.
- **Memoria Tabú con Horizonte Limitado**: Implementación de una pila histórica cíclica indexada a las últimas tres casillas. Toda rama Alfa-Beta proyectada sobre memoria fresca sufre una penalización bruta, destrozando puntuaciones en falsos empates que solo provocarían ciclos retrocesivos en bucle.

## Estructura del Proyecto

- `main.py`: Gestión del bucle, detección de entradas asíncronas y renderizado OpenGL convertido a proyección paralela (Ortogonal 2D).
- `Ghost.py`: Concentra la carga principal definiendo las ramas del árbol de estados Minimax y procesando las estrategias de persecución de los agentes.
- `Pacman.py`: Control interactivo principal del usuario y ajustes de hitbox al plano dimensional de Euclides XZ.
- `mapa.csv`: Maneja la lectura de texturas y paredes opacas del mapeo visual.
- `mapa_codigos.csv`: Contiene la lógica topológica pura mediante una "Matriz de Control" cruzada. Determina las intersecciones y rutas de navegación disponibles para evitar colisiones y evaluar ruteo interno.
- `REPORTE_EXAMEN.md` y `Reporte_Pregunta4.md`: Documentos técnicos integrales abordando justificaciones matemáticas e ingenieriles detalladas del simulador para su evaluación.

---
El desarrollo se gestó bajo un entorno de Linux y mantiene neutralidad en librerías estándar en pos de garantizar compatibilidad operativa entre sistemas.
