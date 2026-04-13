# Reporte Técnico - Pregunta 4: Poda Alfa-Beta y Estrategias de Mejora

Este documento detalla la lógica implementada en el motor Minimax del agente (fantasma) para el proyecto de Pac-Man. La arquitectura aborda el algoritmo de poda Alfa-Beta integrando mitigación para el "efecto de horizonte limitado" y optimizaciones de tiempo de ejecución mediante heurísticas avanzadas.

## 1. Diseño de la Heurística Base

El comportamiento del agente parte de un árbol Minimax de profundidad acotada (4 niveles). La función de utilidad (heurística) evalúa el tablero utilizando la distancia Manhattan. Dado que el fantasma es el nodo maximizador, persigue retornar el valor numérico más alto, por lo que la distancia se procesa como un valor negativo. Mientras más cercano esté de Pac-Man, mayor será el puntaje.

## 2. Memoria Tabú con Horizonte Limitado

El problema clásico en búsquedas sobre grafos ortogonales (grids) son los bucles ciclícos al alternar entre celdas colindantes. Se incluyó una restricción por defecto mediante una lista FIFO (`self.tabu_list`) limitada a un horizonte de memoria de 3 posiciones históricas reales del motor.

A nivel recursivo, cuando el algoritmo de evaluación estática (`evaluate`) procesa una coordenada proyectada, verifica si existe en la memoria tabú. Del caso ser positivo, incurre en una penalización bruta (`-100` puntos) sobre el puntaje heurístico originado. Esto fuerza a Alfa-Beta a catalogar dichas sub-ramas como opciones desastrosas, logrando que el árbol evite automáticamente caminos que causan regresiones recientes, pero manteniendo la estructura del mapa permeable al expirar el límite después de tres tics.

## 3. Continuación Heurística 

Fijar dinámicamente un horizonte estático (profundidad de 4) en laberintos propicia el "efecto de horizonte". Un árbol puede podarse a pocos pasos de atrapar a Pac-Man valorando erróneamente un estado aparentemente "calmado".

Implementamos la Continuación Heurística operando bajo la misma premisa que la Espera en Reposo (Quiescence Search). Cuando el motor recursivo alcanza la hoja terminal (`depth == 0`), se somete la coordenada proyectada a un filtro de volatilidad: si la distancia espacial contra Pac-Man es inferior o igual a 2 bloques, el estado se considera crítico o inestable. En lugar de retornar un valor prematuro, el motor inyecta un estado temporal especial (`is_quiescence`) y expande esa rama específica 2 niveles más abajo. Esto fuerza una resolución del conflicto inmediato impidiendo el colapso de decisiones precolisión.

## 4. Búsqueda Ambiciosa (Move Ordering)

La eficiencia de cualquier algoritmo de poda depende intrínsecamente del orden de evaluación espacial de los nodos hijos en las expansiones preliminares. Generar direcciones secuenciales ciegas causa sobrecarga al evaluar invariablemente cientos de nodos perdedores.

Implementando Búsqueda Ambiciosa, intervenimos el arreglo antes de las llamadas iterativas del árbol. Calculamos la evaluación base temporal por cada dirección posible y aplicamos un ordenamiento dinámico a priori.
- Si el nodo es el Fantasma (maximizador), se ordenan las opciones explorando primero aquellos ruteos que apuntan matemáticamente hacia valores altos locales.
- Si operamos sobre las predicciones de Pac-Man (minimizador), forzamos primero los estados de pérdida directa.

Esta heurística secundaria detecta ramas predominantes desde los primeros picos de evaluación, causando que la condicional `beta <= alpha` o viceversa se cumpla casi de forma instantánea al comienzo de una arista, resultando en ahorros considerables de recursos computacionales sin restar capacidad deductiva.
