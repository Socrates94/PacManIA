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
import random

class Ghost:
    def __init__(self,mapa, mc, x_mc, y_mc, xini, yini, dir, tipo):
        #Matriz de control que almacena los IDs de las intersecciones
        self.MC = mc
        #Vectores que almacenan las coordenadas 
        self.XPxToMC = x_mc
        self.YPxToMC = y_mc
        #se resplanda el mapa en terminos de pixeles
        self.mapa = mapa
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
        #0: fantasma aleatorio
        #1: fantasma con pathfinding
        self.tipo = tipo
        #arreglo para almacenar las opciones del fantasma
        self.options = [
            [1,2],
            [2,3],
            [0,1],
            [0,3],
            [1,2,3],
            [0,2,3],
            [0,1,3],
            [0,1,2],
            [0,1,2,3],
            [1],
            [3]
        ]
        self.option = []
        self.dir_inv = 0
        
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
        #se actualiza la variable de posicion sobre el path
        if self.tipo == 1: #fantasma inteligente
            self.path_n += 1
        
    def path_ia(self,pacmanXY):
        # bloque para implementar la IA en los fantasmas
        if self.tipo == 2:
            self.poda_alfa_beta_logic(pacmanXY)
        else:
            self.interseccion_random()

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

    def evaluate(self, g_row, g_col, p_row, p_col):
        # Queremos que el fantasma minimice la distancia, 
        # así que como Maximizer, la utilidad es la distancia negativa.
        return -(abs(g_row - p_row) + abs(g_col - p_col))

    def minimax(self, g_row, g_col, p_row, p_col, depth, alpha, beta, maximizingPlayer):
        if depth == 0 or (g_row == p_row and g_col == p_col):
            return self.evaluate(g_row, g_col, p_row, p_col)

        if maximizingPlayer:
            max_eval = -float('inf')
            options = self.get_options_at(g_row, g_col)
            if not options:
                return self.evaluate(g_row, g_col, p_row, p_col)
            for move in options:
                nr, nc = self.get_next_mc_pos(g_row, g_col, move)
                if 0 <= nr < 10 and 0 <= nc < 10:
                    eval = self.minimax(nr, nc, p_row, p_col, depth - 1, alpha, beta, False)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = float('inf')
            options = self.get_options_at(p_row, p_col)
            # Si Pacman no tiene opciones (ej. en un pasillo), simulamos que sigue recto o se queda
            if not options:
                return self.evaluate(g_row, g_col, p_row, p_col)
            for move in options:
                nr, nc = self.get_next_mc_pos(p_row, p_col, move)
                if 0 <= nr < 10 and 0 <= nc < 10:
                    eval = self.minimax(g_row, g_col, nr, nc, depth - 1, alpha, beta, True)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval

    def poda_alfa_beta_logic(self, pacmanXY):
        # Convertir posiciones de píxeles a índices de la matriz MC
        self.positionMC[0] = self.XPxToMC[self.position[0] - 20]
        self.positionMC[1] = self.YPxToMC[self.position[2] - 20]
        
        # Para Pacman, como puede no estar exactamente en una intersección, 
        # buscamos el índice MC más cercano.
        p_x_px = pacmanXY[0] - 20
        p_z_px = pacmanXY[2] - 20
        
        # Encontrar los índices más cercanos en las listas de mapeo
        # Reutilizamos las claves de XPxToMC que no son -1
        x_indices = np.where(self.XPxToMC != -1)[0]
        z_indices = np.where(self.YPxToMC != -1)[0]
        
        p_col = self.XPxToMC[x_indices[np.argmin(np.abs(x_indices - p_x_px))]]
        p_row = self.YPxToMC[z_indices[np.argmin(np.abs(z_indices - p_z_px))]]

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
                val = self.minimax(nr, nc, p_row, p_col, 4, -float('inf'), float('inf'), False)
                if val > max_val:
                    max_val = val
                    best_move = move
        
        self.direction = best_move
        
        if self.direction == 0: self.position[2] -= 1
        elif self.direction == 1: self.position[0] += 1
        elif self.direction == 2: self.position[2] += 1
        elif self.direction == 3: self.position[0] -= 1

    def interseccion_random(self):
        #se determina en que tipo de celda esta el fantasma
        self.positionMC[0] = self.XPxToMC[self.position[0] - 20]
        self.positionMC[1] = self.YPxToMC[self.position[2] - 20]
        celId = self.MC[self.positionMC[1]][self.positionMC[0]]
        #a partir de la celda actual se generan sus opciones posibles
        if celId == 0:
            self.option = [self.direction]
        elif celId == 10: #options = [1, 2]
            self.option = self.options[0]
        elif celId == 11: #options = [2, 3]
            self.option = self.options[1]
        elif celId == 12: #options = [0, 1]
            self.option = self.options[2]
        elif celId == 13: #options = [0, 3]
            self.option = self.options[3]
        elif celId == 21: #options = [1, 2, 3]
            self.option = self.options[4]
        elif celId == 22: #options = [0, 2, 3]
            self.option = self.options[5]
        elif celId == 23: #options = [0, 1, 3]
            self.option = self.options[6]
        elif celId == 24: #options = [0, 1, 2]
            self.option = self.options[7]
        elif celId == 25: #options = [0, 1, 2, 3]
            self.option = self.options[8]
        elif celId == 26: #options = [1]
            self.option = self.options[9]
        elif celId == 27: #options = [3]
            self.option = self.options[10]
        
        #se calcula la direccion inversa a la actual
        if self.direction == 0:
            self.dir_inv = 2
        elif self.direction == 1:
            self.dir_inv = 3
        elif self.direction == 2:
            self.dir_inv = 0
        else:
            self.dir_inv = 1

        #se elimina la direccion invertida a la actual, evitando que el
        #fantasma regrese por el camion por donde llego (rebote)
        if (celId != 0) and (celId != 26) and (celId != 27):
            self.option.remove(self.dir_inv)
        
        #se elige aleatoriamente una opcion entre las disponibles
        size = len(self.option)
        dir_rand = random.randint(0, size - 1)
        
        #se actualiza el vector de direccion y posicion del fantasma
        self.direction = self.option[dir_rand]
        
        if self.direction == 0:
            self.position[2] -= 1
        elif self.direction == 1:
            self.position[0] += 1
        elif self.direction == 2:
            self.position[2] += 1
        elif self.direction == 3:
            self.position[0] -= 1
            
        if (celId != 0) and (celId != 26) and (celId != 27):
            self.option.append(self.dir_inv)    
    
    def update2(self,pacmanXY):
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
            if self.tipo == 1 or self.tipo == 2: #agente inteligente, se manda la posición del objetivo
                self.path_ia(pacmanXY)
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