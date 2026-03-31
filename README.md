# Pac-Man en 3D con OpenGL y Python

Este es un proyecto de Pac-Man desarrollado en Python utilizando **Pygame** para la lógica del juego y **OpenGL** para la renderización gráfica en 3D. El juego incluye fantasmas con diferentes niveles de inteligencia artificial, incluyendo algoritmos de búsqueda y poda Alfa-Beta.

## Requisitos Previos

Para ejecutar este proyecto, necesitas tener instalado:

- [Anaconda](https://www.anaconda.com/) o [Miniconda](https://docs.conda.io/en/latest/miniconda.html).
- Python 3.9 (recomendado para el entorno).

## Instalación y Configuración

Sigue estos pasos para preparar tu entorno de trabajo cada vez que abras una nueva terminal:

1. **Activar el entorno de Conda:**
   ```bash
   conda activate pacman
   ```
   *(Si aún no has creado el entorno, puedes hacerlo con `conda create -n pacman python=3.9`)*

2. **Instalar dependencias necesarias:**
   Si es la primera vez que lo levantas, asegúrate de tener instaladas las bibliotecas:
   ```bash
   pip install pygame PyOpenGL numpy pandas
   ```

## Cómo Ejecutar el Proyecto

Una vez ubicado en la raíz del proyecto y con el entorno activado, ejecuta:

```bash
python3 main.py
```

## Controles del Juego

| Tecla | Acción |
| :--- | :--- |
| **W** | Mover hacia Arriba (Eje Z) |
| **S** | Mover hacia Abajo (Eje Z) |
| **A** | Mover hacia la Izquierda (Eje X) |
| **D** | Mover hacia la Derecha (Eje X) |
| **Flecha Izquierda** | Rotar cámara a la izquierda |
| **Flecha Derecha** | Rotar cámara a la derecha |
| **ESC** | Salir del juego |

## Estructura del Proyecto

- `main.py`: Script principal que gestiona el bucle del juego, la cámara y la renderización OpenGL.
- `Pacman.py`: Clase que define el comportamiento y dibujo del personaje Pac-Man.
- `Ghost.py`: Clase de los fantasmas con IA integrada (Random, Pathfinding, Alpha-Beta).
- `mapa.csv`: Archivo que define la estructura física del laberinto.
- `assets/`: Imágenes `.bmp` utilizadas para las texturas de los personajes y el mapa.

## Notas Técnicas

- El juego utiliza una **Matriz de Control (MC)** para mapear las coordenadas de píxeles a intersecciones lógicas, permitiendo que la IA tome decisiones coherentes en el laberinto.
- Se ha corregido un error de desbordamiento de índice (`IndexError`) en el movimiento de los fantasmas mediante validación de límites en tiempo real.

---
Desarrollado como proyecto de gráficas por computadora y lógica de IA.
