import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import math
import os
import numpy as np
import pandas as pd

# Se carga el archivo de la clase Cubo
import sys
sys.path.append('..')
from Pacman import Pacman
from Ghost import Ghost


screen_width = 900
screen_height = 800
#vc para el obser.
FOVY=60.0
ZNEAR=0.01
ZFAR=900.0
#Variables para definir la posicion del observador
#gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
EYE_X = 200.0
EYE_Y = 400.0
EYE_Z = 200.0
CENTER_X = 200.0
CENTER_Y = 0.0
CENTER_Z = 200.0
UP_X=0.0
UP_Y=0.0
UP_Z=-1.0
#Variables para dibujar los ejes del sistema
X_MIN=-500
X_MAX=500
Y_MIN=-500

Y_MAX=500
Z_MIN=-500
Z_MAX=500
#Dimension del plano
DimBoard = 400
#Variables para el control del observador
theta = 0.0
radius = 300


#Arreglo para el manejo de texturas
textures = []

#Nombre de los archivos a usar
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
file_1 = os.path.join(BASE_PATH, 'mapa.bmp')
img_pacman = os.path.join(BASE_PATH, 'pacman.bmp')
img_ghost1 = os.path.join(BASE_PATH, 'fantasma1.bmp') #blinky
img_ghost2 = os.path.join(BASE_PATH, 'fantasma2.bmp') #pinky
img_ghost3 = os.path.join(BASE_PATH, 'fantasma3.bmp') #inky
img_ghost4 = os.path.join(BASE_PATH, 'fantasma4.bmp') #clyde

# Lee los tableros de navegacion
file_csv = os.path.join(BASE_PATH, 'mapa.csv')
matrix = np.array(pd.io.parsers.read_csv(file_csv, header=None)).astype("int")
zmatrix = len(matrix)
xmatrix = len(matrix[0])


#Arreglos para imprimir intersecciones en el mapa del pacman
zarray = [-180 + 200, -128 + 200, -90 + 200, -50 + 200, -12 + 200, 28 + 200, 64 + 200, 102 + 200, 140 + 200, 180 + 200]
xarray = [-180 + 200, -150 + 200, -108 + 200, -65 + 200, -22 + 200, 21 + 200, 64 + 200, 107 + 200, 149 + 200, 178 + 200]

#Matriz de Control para mapeo entre pixeles <-> coord donde se localizan esquinas
MC = [
    [10,  0, 21,  0, 11, 10,  0, 21,  0, 11],
    [24,  0, 25, 21, 23, 23, 21, 25,  0, 22],
    [12,  0, 22, 12, 11, 10, 13, 24,  0, 13],
    [ 0,  0,  0, 10, 23, 23, 11,  0,  0,  0],
    [26,  0, 25, 22,  0,  0, 24, 25,  0, 27],
    [ 0,  0,  0, 24,  0,  0, 22,  0,  0,  0],
    [10,  0, 25, 23, 11, 10, 23, 25,  0, 11],
    [12, 11, 24, 21, 23, 23, 21, 22, 10, 13],
    [10, 23, 13, 12, 11, 10, 13, 12, 23, 11],
    [12,  0,  0,  0, 23, 23,  0,  0,  0, 13]
]

xMC = [0,30,71,114,156,199,242,286,328,358]

#XPxToMC = np.zeros((359,), dtype=int)
XPxToMC = np.full(359, -1, dtype=int)
XPxToMC[0] = 0
XPxToMC[30] = 1
XPxToMC[71] = 2
XPxToMC[114] = 3
XPxToMC[156] = 4
XPxToMC[199] = 5
XPxToMC[242] = 6
XPxToMC[286] = 7
XPxToMC[328] = 8
XPxToMC[358] = 9
 
yMC = [0,51,90,130,168,208,244,282,320,360]

#YPxToMC = np.zeros((361,), dtype=int)
YPxToMC = np.full(361, -1, dtype=int)
YPxToMC[0] = 0
YPxToMC[51] = 1
YPxToMC[90] = 2
YPxToMC[130] = 3
YPxToMC[168] = 4
YPxToMC[208] = 5
YPxToMC[244] = 6
YPxToMC[282] = 7
YPxToMC[320] = 8
YPxToMC[360] = 9

#pacman object
pc = Pacman(matrix, MC, XPxToMC, YPxToMC)
# Inicialización de objetos de fantasmas (individuales para pruebas dinámicas)
#se almacena que tipo de fantasma sera:
#0: Nivel básico (Aleatorio).
#1: Sin uso activo en la versión actual (Pathfinding obsoleto).
#2: Nivel táctico (Poda Alfa-Beta con heurísticas, Pinky).
#3: Nivel avanzado (Caza en manada, Inky y Clyde).
blinky = Ghost(matrix, MC, XPxToMC, YPxToMC, 378, 20, 0, 0)
pinky = Ghost(matrix, MC, XPxToMC, YPxToMC, 378, 380, 2, 2)
inky = Ghost(matrix, MC, XPxToMC, YPxToMC, 20, 380, 3, 3)
clyde = Ghost(matrix, MC, XPxToMC, YPxToMC, 378, 20, 1, 3)

def configurar_fantasmas(opcion):
    ghosts_activos = []
    if opcion == 1:
        ghosts_activos.append(blinky)
    elif opcion == 2:
        ghosts_activos.append(pinky)
    elif opcion == 3:
        ghosts_activos.extend([inky, clyde])
    elif opcion == 4:
        ghosts_activos.extend([blinky, pinky, inky, clyde])
    return ghosts_activos

def mostrar_menu():
    print("\n" + "="*75)
    print("\t\t MENU DEL JUEGO")
    print("     Juego de Pac-Man con el algoritmo Minimax poda alfa beta")
    print("="*75)
    print("1. Fantasma (Blinky - rojo) movimientos aleatorios")
    print("2. Fantasma (Pinky - rosa) solitario con dos heuristicas")
    print("3. Fantasmas (Inky/Clyde - cian/naranja) cazar en manada")
    print("4. Todos los fantasmitas atacando a la vez (Blinky, Pinky, Inky, Clyde)")
    print("5. Salir")
    print("="*75 + "\n")
    
    while True:
        try:
            opcion = int(input("Selecciona una opción del menu (1-5): "))
            if 1 <= opcion <= 5:
                return opcion
            else:
                print("Por favor, ingresa un número entre 1 y 5.")
        except ValueError:
            print("Entrada no válida. Ingresa un número.")

opcion_menu = mostrar_menu()
if opcion_menu == 5:
    sys.exit()

# Lista de fantasmas activos
ghosts = configurar_fantasmas(opcion_menu)


collision_detected = False
return_to_menu = False


pygame.init()

def Axis():
    glShadeModel(GL_FLAT)
    glLineWidth(3.0)
    #X axis in red
    glColor3f(1.0,0.0,0.0)
    glBegin(GL_LINES)
    glVertex3f(X_MIN,0.0,0.0)
    glVertex3f(X_MAX,0.0,0.0)
    glEnd()
    #Y axis in green
    glColor3f(0.0,1.0,0.0)
    glBegin(GL_LINES)
    glVertex3f(0.0,Y_MIN,0.0)
    glVertex3f(0.0,Y_MAX,0.0)
    glEnd()
    #Z axis in blue
    glColor3f(0.0,0.0,1.0)
    glBegin(GL_LINES)
    glVertex3f(0.0,0.0,Z_MIN)
    glVertex3f(0.0,0.0,Z_MAX)
    glEnd()
    glLineWidth(1.0)

def Texturas(filepath):
    textures.append(glGenTextures(1))
    id = len(textures) - 1
    glBindTexture(GL_TEXTURE_2D, textures[id])
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    image = pygame.image.load(filepath).convert()
    w, h = image.get_rect().size
    image_data = pygame.image.tostring(image,"RGBA")
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
    glGenerateMipmap(GL_TEXTURE_2D) 
    
def Init():
    # Configuración de la ventana
    screen = pygame.display.set_mode(
        (screen_width, screen_height), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Juego de Pac-Man Poda Alfa Beta")

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    # Utilizamos proyeccion ortogonal en vez de perspectiva para la vista en 2D
    # screen_width=900, screen_height=800 -> ratio=1.125
    glOrtho(-230.625, 230.625, -205.0, 205.0, ZNEAR, ZFAR)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    # Para la vista cenital 2D, la cámara se eleva sobre el eje Y mirando hacia abajo (plano XZ)
    gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)
    glClearColor(0,0,0,0)
    glEnable(GL_DEPTH_TEST)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    # Inicializar el mezclador de audio
    pygame.mixer.init()
    global sonido_chomp, sonido_death
    sonido_chomp = pygame.mixer.Sound('pacman_chomp.wav')
    sonido_death = pygame.mixer.Sound('pacman_death.wav')
    sonido_chomp.play(-1) # Reproducir en bucle infinito

    #textures[0]: plano
    Texturas(file_1)
    #textures[1]: pacman
    Texturas(img_pacman)
    #textures[2]: fantasma1
    Texturas(img_ghost1)
    #textures[3]: fantasma2
    Texturas(img_ghost2)
    #textures[4]: fantasma3
    Texturas(img_ghost3)
    #textures[5]: fantasma4
    Texturas(img_ghost4)

    # se pasan las texturas a los objetos de forma fija
    pc.loadTextures(textures, 1)
    blinky.loadTextures(textures, 2)
    pinky.loadTextures(textures, 3)
    inky.loadTextures(textures, 4)
    clyde.loadTextures(textures, 5)
    
def PlanoTexturizado():
    #Activate textures
    glColor3f(1.0,1.0,1.0)
    glEnable(GL_TEXTURE_2D)
    #front face
    glBindTexture(GL_TEXTURE_2D, textures[0])    
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex3d(0, 0, 0)
    glTexCoord2f(0.0, 1.0)
    glVertex3d(0, 0, DimBoard)
    glTexCoord2f(1.0, 1.0)
    glVertex3d(DimBoard, 0, DimBoard)
    glTexCoord2f(1.0, 0.0)
    glVertex3d(DimBoard, 0, 0)
    glEnd()              
    glDisable(GL_TEXTURE_2D)

#Se mueve al observador circularmente al rededor del plano XZ a una altura fija (EYE_Y)
def lookat():
    global EYE_X
    global EYE_Z
    global radius
    center = DimBoard / 2
    EYE_X = radius * (math.cos(math.radians(theta)) + math.sin(math.radians(theta))) + center
    EYE_Z = radius * (-math.sin(math.radians(theta)) + math.cos(math.radians(theta))) + center
    glLoadIdentity()
    gluLookAt(EYE_X,EYE_Y,EYE_Z,CENTER_X,CENTER_Y,CENTER_Z,UP_X,UP_Y,UP_Z)

def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    Axis()
    PlanoTexturizado()
    if not collision_detected:
        pc.draw()
    for g in ghosts:
        g.draw()
        g.update2(pc.position, ghosts)
    
done = False
Init()

# Mapeo de nombres para el mensaje de victoria
nombres_modos = {
    1: "Blinky (Rojo) Aleatorio",
    2: "Pinky (Rosa) Poda Alfa-Beta",
    3: "Inky y Clyde (Manada)",
    4: "Todos los fantasmas"
}
nombre_modo_actual = nombres_modos.get(opcion_menu, "Desconocido")

# Variables del temporizador de supervivencia
tiempo_inicio = pygame.time.get_ticks()
tiempo_limite = 30000  # 30 segundos en milisegundos

# Variables del buffer de teclado
act_teclado = -1
delta = 0
lon_ventana = 30 # frames de tolerancia (pixeles dados) para mantener la tecla vigente
# con 30 quedo muy bien

while not done:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                done = True
    
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        pass # Deshabilitado para mantener la vista 2D estricta
    if keys[pygame.K_LEFT]:
        pass # Deshabilitado para mantener la vista 2D estricta
    
    # Se verifica la direccion para el pacman actualizando el buffer
    if keys[pygame.K_w]:
        act_teclado = 0  # up
        delta = 0
    elif keys[pygame.K_d]:
        act_teclado = 1  # right
        delta = 0
    elif keys[pygame.K_s]:
        act_teclado = 2  # down
        delta = 0
    elif keys[pygame.K_a]:
        act_teclado = 3  # left
        delta = 0
    
    # Control de vida del buffer (la ventana o delta)
    if act_teclado != -1:
        delta += 1
        if delta > lon_ventana:
            act_teclado = -1 # expira el buffer si no se usa a tiempo
            
    # Mandamos al update el estado actual del buffer de teclado
    pc.update(act_teclado)

    # Deteccion de colisiones hitboxes
    for g in ghosts:
        # Distancia Euclidiana en el plano XZ 
        dist = math.sqrt((pc.position[0] - g.position[0])**2 + (pc.position[2] - g.position[2])**2)
        
        if dist < 12: # Umbral de colision
            collision_detected = True
            pygame.mixer.stop() # Detener sonidos en colisión
            sonido_death.play()
            display() # Dibujamos una ultima vez para que desaparezca pacman
            pygame.display.flip()
            
            # Calcular tiempo sobrevivido
            tiempo_actual = pygame.time.get_ticks()
            segundos_sobrevividos = (tiempo_actual - tiempo_inicio) / 1000.0
            
            print("\n" + "="*40)
            print("          ¡ G A M E   O V E R !")
            print("        Pac-Man ha sido atrapado")
            print(f"      Tiempo sobreviviste: {segundos_sobrevividos:.2f} s")
            print("="*40 + "\n")
            pygame.display.set_caption(f"GAME OVER - Sobreviviste {segundos_sobrevividos:.1f}s")
            pygame.time.wait(2000) # Esperamos 3 segundos para que el usuario lo vea
            done = True
            return_to_menu = True
            break

    # Verificacion del temporizador de victoria (1 minuto)
    tiempo_actual = pygame.time.get_ticks()
    tiempo_transcurrido = tiempo_actual - tiempo_inicio
    
    # Calcular y mostrar segundos restantes en la barra de titulo
    segundos_restantes = max(0, (tiempo_limite - tiempo_transcurrido) // 1000)
    pygame.display.set_caption(f"Pac-Man IA - Tiempo Restante: {segundos_restantes}s")

    if tiempo_transcurrido >= tiempo_limite and not collision_detected:
        pygame.mixer.stop()
        display() # Dibujamos una ultima vez
        pygame.display.flip()
        print("\n" + "="*50)
        print("          ¡ V I C T O R Y !")
        print(f" Sobreviviste 30 segundos contra: {nombre_modo_actual}")
        print("="*50 + "\n")
        pygame.display.set_caption("VICTORIA - ¡Sobreviviste!")
        pygame.time.wait(2000) # Esperamos 4 segundos para que el usuario lo vea
        done = True
        return_to_menu = True
        break

    display()
    pygame.display.flip()
    pygame.time.wait(10)

pygame.quit()

if return_to_menu:
    os.execl(sys.executable, sys.executable, *sys.argv)
