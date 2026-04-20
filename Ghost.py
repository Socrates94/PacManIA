import pygame
from pygame.locals import *

# Cargamos las bibliotecas de OpenGL
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

import numpy as np
import random

class Ghost:
    
    def __init__(self,mapa, mc, x_mc, y_mc, xini, yini, dir, tipo):
        
        #se resplanda el mapa en terminos de pixeles
        self.mapa = mapa
        
        #Matriz de control que almacena los IDs de las intersecciones
        self.MC = mc
        
        #Vectores que almacenan las coordenadas 
        self.XPxToMC = x_mc
        self.YPxToMC = y_mc
        
 
        #se inicializa la posicion del fantasma en terminos de pixeles
        self.position = []
        self.position.append(xini)
        self.position.append(1) #YPos
        self.position.append(yini)
        
        #se define el arreglo para la posicion en la matriz de control
        self.positionMC = []
        self.positionMC.append(self.XPxToMC[self.position[0] - 20]) #coord en x
        self.positionMC.append(self.YPxToMC[self.position[2] - 20]) #coord en y
        
        #se inicializa una direccion valida
        self.direction = dir
        
        #se almacena que tipo de fantasma sera:
        #0: Nivel básico (Aleatorio).
        #1: Sin uso activo en la versión actual (Pathfinding obsoleto).
        #2: Nivel táctico (Poda Alfa-Beta con heurísticas, Pinky).
        #3: Nivel avanzado (Caza en manada, Inky y Clyde).
        self.tipo = tipo
        
        #arreglo para almacenar las opciones del fantasma
        self.options = [
            [1,2],      # índice 0 → código 10 → derecha y abajo
            [2,3],      # indice 1 → código 11 → abajo y izquierda
            [0,1],      # indice 2 → código 12 → arriba y derecha
            [0,3],      # indice 3 → código 13 → arriba y izquierda
            [1,2,3],    # indice 4 → código 21 → T: der, abajo, izq
            [0,2,3],    # indice 5 → código 22 → T: arr, abajo, izq
            [0,1,3],    # indice 6 → código 23 → T: arr, der, izq
            [0,1,2],    # indice 7 → código 24 → T: arr, der, abajo
            [0,1,2,3],  # indice 8 → código 25 → cruce completo
            [1],        # indice 9 → código 26 → solo derecha
            [3]         # indice 10 → código 27 → solo izquierda
        ]
        
        self.option = []
        self.dir_inv = 0
        self.tabu_list = []
        
    def loadTextures(self, texturas, id):
        self.texturas = texturas
        self.Id = id

    def drawFace(self, x1, y1, z1, x2, y2, z2, x3, y3, z3, x4, y4, z4):
        glBegin(GL_QUADS)
        glTexCoord2f(0.0, 0.0)
        glVertex3f(x1, y1, z1)
        glTexCoord2f(0.0, 1.0)
        glVertex3f(x2, y2, z2)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(x3, y3, z3)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(x4, y4, z4)
        glEnd()
   
    def sigue_adelante(self):
        #si el fantasma esta en un tunel, no es necesario calcular la siguiente posicion a traves del path
        #solo se sigue la direccion actual y se aumenta el contador que accede a la posicion del path actual
        if self.direction == 0: #up
            self.position[2] -= 1
        elif self.direction == 1: #right
            self.position[0] += 1
        elif self.direction == 2: #down
            self.position[2] += 1
        else: #left
            self.position[0] -= 1
        
    def path_ia(self,pacmanXY, all_ghosts=None):
        # bloque para implementar la IA en los fantasmas
        if self.tipo == 2 or self.tipo == 3:
            self.poda_alfa_beta_logic(pacmanXY, all_ghosts=all_ghosts, is_manada=(self.tipo == 3))
        else:
            self.interseccion_random()

    # Pregunta 1: Comportamiento base, fantasma rojo con movimientos aleatorios
    def interseccion_random(self):
        
        #se determina en que tipo de celda esta el fantasma, donde esta exactamente
        self.positionMC[0] = self.XPxToMC[self.position[0] - 20]
        self.positionMC[1] = self.YPxToMC[self.position[2] - 20]
        celId = self.MC[self.positionMC[1]][self.positionMC[0]]
        
        #a partir de la celda actual se generan sus opciones posibles
        mapping = {10:0, 11:1, 12:2, 13:3, 21:4, 22:5, 23:6, 24:7, 25:8, 26:9, 27:10}
        
        if celId == 0:
            self.option = [self.direction]
        elif celId in mapping:
            self.option = list(self.options[mapping[celId]])
        
        #se calcula la direccion inversa a la actual
        self.dir_inv = (self.direction + 2) % 4
        #opuesto(0=arriba)    → (0+2)%4 = 2 = abajo     
        #opuesto(1=derecha)   → (1+2)%4 = 3 = izquierda 
        #opuesto(2=abajo)     → (2+2)%4 = 0 = arriba     
        #opuesto(3=izquierda) → (3+2)%4 = 1 = derecha    

        #se elimina la direccion invertida a la actual, evitando que el
        #fantasma regrese por el camino por donde llego (rebote)
        if (celId != 0) and (celId != 26) and (celId != 27): #
            if self.dir_inv in self.option:
                self.option.remove(self.dir_inv)
        
        #se elige aleatoriamente una opcion entre las disponibles
        size = len(self.option)
        if size > 0:
            dir_rand = random.randint(0, size - 1)
            #se actualiza el vector de direccion y posicion del fantasma
            self.direction = self.option[dir_rand]
        else:
            # Si por alguna razon no hay opciones excepto la inversa, mantenemos la actual
            pass
        
        if self.direction == 0:
            self.position[2] -= 1
        elif self.direction == 1:
            self.position[0] += 1
        elif self.direction == 2:
            self.position[2] += 1
        elif self.direction == 3:
            self.position[0] -= 1

    # Pregunta 2: Lógica de entorno y adyacencias
    def get_options_at(self, row, col):
        celId = self.MC[row][col]
        if celId == 10: return [1, 2]
        elif celId == 11: return [2, 3]
        elif celId == 12: return [0, 1]
        elif celId == 13: return [0, 3]
        elif celId == 21: return [1, 2, 3]
        elif celId == 22: return [0, 2, 3]
        elif celId == 23: return [0, 1, 3]
        elif celId == 24: return [0, 1, 2]
        elif celId == 25: return [0, 1, 2, 3]
        elif celId == 26: return [1]
        elif celId == 27: return [3]
        else: return []

    def get_next_mc_pos(self, row, col, direction):
        if direction == 0: return row - 1, col
        elif direction == 1: return row, col + 1
        elif direction == 2: return row + 1, col
        elif direction == 3: return row, col - 1
        return row, col

    # Pregunta 3: Funciones de evaluación y heurísticas
    def evaluate(self, g_row, g_col, p_row, p_col, partner_row=None, partner_col=None):
        """
        Funcion de evaluacion con dos componentes heuristicos.
        Componente 1 (comun): distancia Manhattan negativa hacia Pac-Man.
        Componente 2 (segun tipo): alineamiento directo para Pinky,
                                   heuristica de flanqueo por producto punto para manada.
        """
        # Componente heuristico 1: distancia Manhattan base
        base_score = -(abs(g_row - p_row) + abs(g_col - p_col))

        # Componente heuristico 2: diferenciado por estrategia de caza
        if self.tipo == 3:  # manada: encasillamiento continuo por gradientes
            if hasattr(self, 'Id'):
                row_dist = abs(g_row - p_row)
                col_dist = abs(g_col - p_col)
                # Sobrescribimos el base_score comun con pesos asimetricos dependientes 
                # de la posicion del fantasma.
                if self.Id == 4:
                    # Inky penaliza mas la distancia a lo largo de las columnas (X/horizontal).
                    # Esto obliga al Minimax a mover a Inky horizontalmente primero.
                    base_score = -(row_dist + 5.0 * col_dist)
                elif self.Id == 5:
                    # Clyde penaliza mas la distancia a lo largo de las filas (Z/vertical).
                    # Esto obliga al Minimax a mover a Clyde verticalmente primero.
                    base_score = -(5.0 * row_dist + col_dist)
            else:
                pacman_options = len(self.get_options_at(p_row, p_col))
                base_score -= pacman_options * 2

            # Agregamos la penalización por Producto Punto (Herd Hunting estricto)
            # Para forzar que reaccionen velozmente si coinciden en la misma ruta
            if partner_row is not None and partner_col is not None:
                v1_row = g_row - p_row
                v1_col = g_col - p_col
                
                v2_row = partner_row - p_row
                v2_col = partner_col - p_col
                
                dot_product = (v1_row * v2_row) + (v1_col * v2_col)
                
                # Si > 0, vienen del mismo lado. Si es muy alto, están literalmente empalmados.
                # Castigo severo multiplicando el valor para forzar abandono de esa ruta
                if dot_product > 0:
                    base_score -= (dot_product * 3.0)

        else:  # Pinky: bonificar si esta alineado en el mismo eje que Pac-Man
            if g_row == p_row or g_col == p_col:
                base_score += 3

        return base_score

    # Algoritmo minimax para la busqueda de la mejor jugada (construccion del arbol de estados)
    def minimax(self, g_row, g_col, p_row, p_col, depth, alpha, beta, maximizingPlayer, is_quiescence=False, partner_row=None, partner_col=None):
        dist = abs(g_row - p_row) + abs(g_col - p_col)

        # Estrategia 1: Continuacion Heuristica Espera en reposo (Quiescence Search)
        # Si al llegar al limite la situacion es critica, se extiende la busqueda
        if depth == 0 and not is_quiescence and dist <= 2:
            return self.minimax(g_row, g_col, p_row, p_col, 2, alpha, beta, maximizingPlayer, True, partner_row, partner_col)

        if depth == 0 or dist == 0:
            return self.evaluate(g_row, g_col, p_row, p_col, partner_row, partner_col)

        if maximizingPlayer:
            max_eval = -float('inf')
            options = self.get_options_at(g_row, g_col)
            if not options:
                return self.evaluate(g_row, g_col, p_row, p_col, partner_row, partner_col)

            # Estrategia 2: Busqueda Ambiciosa (Move Ordering)
            # Se ordenan los movimientos para maximizar cortes alfa-beta desde el inicio
            options.sort(key=lambda m: self.evaluate(*self.get_next_mc_pos(g_row, g_col, m), p_row, p_col, partner_row, partner_col), reverse=True)

            for move in options:
                nr, nc = self.get_next_mc_pos(g_row, g_col, move)
                if 0 <= nr < 10 and 0 <= nc < 10:
                    # Estrategia 3: Tabu con horizonte limitado
                    # Las posiciones tabu se penalizan directamente sin expandir esa rama
                    if (nr, nc) in self.tabu_list:
                        eval = -100
                    else:
                        eval = self.minimax(nr, nc, p_row, p_col, depth - 1, alpha, beta, False, is_quiescence, partner_row, partner_col)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = float('inf')
            options = self.get_options_at(p_row, p_col)
            if not options:
                return self.evaluate(g_row, g_col, p_row, p_col, partner_row, partner_col)

            # Estrategia 2: Busqueda Ambiciosa (Move Ordering) - minimizador
            options.sort(key=lambda m: self.evaluate(g_row, g_col, *self.get_next_mc_pos(p_row, p_col, m), partner_row, partner_col), reverse=False)

            for move in options:
                nr, nc = self.get_next_mc_pos(p_row, p_col, move)
                if 0 <= nr < 10 and 0 <= nc < 10:
                    eval = self.minimax(g_row, g_col, nr, nc, depth - 1, alpha, beta, True, is_quiescence, partner_row, partner_col)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval

    # Pregunta 4: Toma de decisiones y alfa-beta (caza en manada)
    def poda_alfa_beta_logic(self, pacmanXY, all_ghosts=None, is_manada=False):
        # Convertir posiciones de píxeles a índices de la matriz MC
        self.positionMC[0] = self.XPxToMC[self.position[0] - 20]
        self.positionMC[1] = self.YPxToMC[self.position[2] - 20]
        
        # Para Pacman, como puede no estar exactamente en una intersección, 
        # buscamos el índice MC más cercano.
        p_x_px = pacmanXY[0] - 20
        p_z_px = pacmanXY[2] - 20
        
        # Encontrar los índices más cercanos en las listas de mapeo
        x_indices = np.where(self.XPxToMC != -1)[0]
        z_indices = np.where(self.YPxToMC != -1)[0]
        
        p_col = self.XPxToMC[x_indices[np.argmin(np.abs(x_indices - p_x_px))]]
        p_row = self.YPxToMC[z_indices[np.argmin(np.abs(z_indices - p_z_px))]]

        partner_row = None
        partner_col = None
        if is_manada and all_ghosts is not None:
            for other in all_ghosts:
                if other.tipo == 3 and other != self:
                    px = other.position[0] - 20
                    pz = other.position[2] - 20
                    partner_col = self.XPxToMC[x_indices[np.argmin(np.abs(x_indices - px))]]
                    partner_row = self.YPxToMC[z_indices[np.argmin(np.abs(z_indices - pz))]]
                    break

        options = self.get_options_at(self.positionMC[1], self.positionMC[0])
        
        # Evitar regresar por donde vino a menos que sea necesario
        if self.direction == 0: inv = 2
        elif self.direction == 1: inv = 3
        elif self.direction == 2: inv = 0
        else: inv = 1
        
        if len(options) > 1 and inv in options:
            options.remove(inv)

        # Inicializar best_move con la primera opción válida si existe
        best_move = options[0] if options else self.direction
        max_val = -float('inf')

        for move in options:
            nr, nc = self.get_next_mc_pos(self.positionMC[1], self.positionMC[0], move)
            if 0 <= nr < 10 and 0 <= nc < 10:
                val = self.minimax(nr, nc, p_row, p_col, 4, -float('inf'), float('inf'), False, False, partner_row, partner_col)
                if val > max_val:
                    max_val = val
                    best_move = move
        
        self.direction = best_move
        
        # Almacenar en la lista tabú con un horizonte limitado a 3 posiciones
        self.tabu_list.append((self.positionMC[1], self.positionMC[0]))
        if len(self.tabu_list) > 3:
            self.tabu_list.pop(0)
        
        if self.direction == 0: self.position[2] -= 1
        elif self.direction == 1: self.position[0] += 1
        elif self.direction == 2: self.position[2] += 1
        elif self.direction == 3: self.position[0] -= 1

    def update2(self,pacmanXY, all_ghosts=None):
        # Control de límites para evitar IndexError
        y_idx = self.position[2] - 20
        x_idx = self.position[0] - 20
        
        if y_idx < 0 or y_idx >= len(self.YPxToMC) or x_idx < 0 or x_idx >= len(self.XPxToMC):
            # Reposicionar en el límite si se sale
            self.position[2] = max(20, min(self.position[2], len(self.YPxToMC) + 19))
            self.position[0] = max(20, min(self.position[0], len(self.XPxToMC) + 19))
            return

        #si el fantasma se encuentra en una interseccion (valida o "falsa interseccion")
        if ((self.YPxToMC[self.position[2] - 20] != -1) and 
            (self.XPxToMC[self.position[0] - 20] != -1)):
            if self.tipo in [1, 2, 3]: #agente inteligente o manada, se manda la posición del objetivo
                self.path_ia(pacmanXY, all_ghosts)
            else:
                self.interseccion_random()
        else: #si no se encuentra en una interseccion o es falsa interseccion
            self.sigue_adelante()
        
    def draw(self):
        glPushMatrix()
        glColor3f(1.0, 1.0, 1.0)
        glTranslatef(self.position[0], self.position[1], self.position[2])
        glScaled(10,1,10)
        #Activate textures
        glEnable(GL_TEXTURE_2D)
        #front face
        glBindTexture(GL_TEXTURE_2D, self.texturas[self.Id])
        self.drawFace(-1.0, 1.0, -1.0, -1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0)    
        glDisable(GL_TEXTURE_2D)  
        glPopMatrix()        