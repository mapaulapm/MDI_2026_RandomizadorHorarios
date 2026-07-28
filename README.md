# MDI_2026_RandomizadorHorarios

Generador de horarios en Python que modela la oferta académica como un **grafo de conflictos**, donde cada grupo de una materia corresponde a un nodo y cada arista representa un choque de horario entre dos grupos. El sistema genera propuestas de horario sin conflictos utilizando un algoritmo de **backtracking con poda**.

Proyecto desarrollado para la asignatura **Matemáticas Discretas I**.

---

## Integrante

- Maria Paula Pérez Meléndez

---

## Problema

¿Cómo optimizar la selección de horarios según la oferta académica de un semestre, evitando choques entre materias y priorizando profesores mejor calificados según foros estudiantiles?

---

## Requisitos

- Python 3.10 o superior
- pandas
- networkx
- openpyxl

Instalación:

```bash
pip install pandas networkx openpyxl
```

También es posible instalar todas las dependencias desde el archivo `requirements.txt` mediante:

```bash
pip install -r requirements.txt
```

---

## Datos

El archivo `MD_BaseDatos.xlsx` (hoja **Base**) contiene la oferta académica utilizada para las pruebas, extraída del SIA de la Universidad Nacional de Colombia.

Columnas utilizadas:

- Materia
- Grupo
- Profesor
- Cupos
- Días de la semana
- Hora inicio
- Hora fin
- Calificación

---

## Ejecución

1. Descargar el archivo principal `.py`.
2. Descargar el archivo `MD_BaseDatos.xlsx`.
3. Instalar las dependencias.
4. Ejecutar el archivo `.py`.

```bash
python entrega-final-v1.py
```

---

## Ejemplo de uso

El programa imprime:

- El tamaño del grafo de conflictos (número de nodos y aristas).
- Varias propuestas de horario sin choques.
- Una representación tabular de cada horario encontrado.

El comportamiento puede personalizarse modificando los siguientes parámetros:

- `max_opciones`: cantidad máxima de horarios a generar.
- `min_calificacion`: calificación mínima aceptada para los profesores.
- `max_calificacion`: calificación máxima aceptada.
- `materias_fijas`: permite fijar un grupo específico para una materia determinada.
- `incluir_cero`: permite aceptar profesores sin calificación registrada.
- 
En caso de querer cierto grupo de cierta materia fijo se debe de escribir en la sección materias_fijas y mantener tambien la materia en materias_a_seleccionar .
---

## Estado actual

- ✅ Carga y limpieza de datos reales del SIA.
- ✅ Construcción del grafo de conflictos con NetworkX.
- ✅ Generación de propuestas de horario mediante backtracking.
- ✅ Filtrado por cupos y calificación de profesores.
- ✅ Soporte para materias con grupo fijo.
- ❌ Interfaz gráfica (propuesta como trabajo futuro).
