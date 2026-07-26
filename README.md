# MDI_2026_RandomizadorHorarios
Generador de horarios que modela la oferta de materias como un grafo de conflictos y encuentra combinaciones de grupos sin choques de horario. Proyecto para Matemáticas Discretas I

# Randomizador de Horarios

Generador de horarios en Python que modela la oferta académica como un
grafo de conflictos: cada grupo de una materia es un nodo, y una arista
conecta dos grupos que chocan en horario. Las propuestas válidas
corresponden a combinaciones sin choques (conjuntos independientes del
grafo, uno por materia).

## Integrante
Maria Paula Pérez Meléndez

## Problema
¿Cómo optimizar la selección de horarios según la oferta de materias de
un semestre, evitando choques y priorizando profesores mejor calificados en foros estudiantiles?

## Requisitos
- Python 3.10+
- pandas
- networkx
- openpyxl

Instalar con:
\`\`\`
pip install pandas networkx openpyxl
\`\`\`

## Datos
El archivo `MD_BaseDatos.xlsx` (hoja "Base") contiene la oferta real de
materias usada para generar el horario del semestre actual, extraída del
SIA. Columnas: Materia, Grupo, Profesor, Cupos, Dias de la semana, Hora
inicio, Hora fin, Calificacion (escala 0-4).

## Ejecución
descargar el archivo .py que se encuentra en la rama feature, además el archivo .xlsx ya que es la base de datos con la que se realizan las pruebas, los requisitos se encuentran en un archivo .txt 

\`\`\`
python generador_horarios.py
\`\`\`

## Ejemplo de uso
El script imprime el tamaño del grafo de conflictos y hasta 10 propuestas
de horario ordenadas por calificación promedio de profesores.

## Estado actual
- [x] Carga y limpieza de datos reales del SIA
- [x] Construcción del grafo de conflictos con networkx
- [x] Generación de propuestas válidas (conjuntos independientes)
- [ ] Interfaz gráfica (fuera de alcance para esta entrega, ver informe)
- [ ] Validación con más de un semestre de datos
