import os
import textwrap
from collections import defaultdict
from copy import deepcopy
from datetime import datetime
import networkx as nx
import pandas as pd

try:
    CARPETA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
except NameError:
    CARPETA_SCRIPT = os.getcwd()

RUTA_DATOS = os.path.join(CARPETA_SCRIPT, "MD_BaseDatos.xlsx")
HOJA_DATOS = "Base"


def normalizar_hora_texto(valor):
    """Convierte 'HH:MM:SS', 'HH:MM' o datetime.time a texto 'HH:MM'."""
    if pd.isna(valor):
        return None
    if hasattr(valor, "hour"):  # datetime.time
        return f"{valor.hour:02d}:{valor.minute:02d}"
    partes = str(valor).strip().split(":")
    return f"{int(partes[0]):02d}:{int(partes[1]):02d}"


def cargar_datos(ruta=RUTA_DATOS, hoja=HOJA_DATOS):
    df = pd.read_excel(ruta, sheet_name=hoja)
    df = df.dropna(subset=["Materia", "Grupo"]).copy()
    df["Dias de la semana"] = df["Dias de la semana"].astype(str).str.strip()
    df["Hora inicio"] = df["Hora inicio"].apply(normalizar_hora_texto)
    df["Hora fin"] = df["Hora fin"].apply(normalizar_hora_texto)
    df["Calificacion"] = df["Calificacion"].fillna(0).astype(int)
    df["Cupos"] = df["Cupos"].fillna(0).astype(int)
    df = df.dropna(subset=["Hora inicio", "Hora fin"])
    return df.to_dict("records")


datos = cargar_datos()

# Agrupar horarios por (materia, grupo)
horarios_dict = defaultdict(list)
for fila in datos:
    horarios_dict[(fila["Materia"], fila["Grupo"])].append(fila)


def convertir_hora(hora_str):
    return datetime.strptime(hora_str, "%H:%M")


def hay_choque(h1, h2):
    if h1["Dias de la semana"] != h2["Dias de la semana"]:
        return False
    inicio1, fin1 = convertir_hora(h1["Hora inicio"]), convertir_hora(
        h1["Hora fin"]
    )
    inicio2, fin2 = convertir_hora(h2["Hora inicio"]), convertir_hora(
        h2["Hora fin"]
    )
    return inicio1 < fin2 and inicio2 < fin1


def construir_grafo_conflictos():
    G = nx.Graph()
    claves = list(horarios_dict.keys())
    for clave in claves:
        G.add_node(clave)

    for i in range(len(claves)):
        m1, g1 = claves[i]
        for j in range(i + 1, len(claves)):
            m2, g2 = claves[j]
            if m1 == m2:
                continue
            if any(
                hay_choque(h1, h2)
                for h1 in horarios_dict[(m1, g1)]
                for h2 in horarios_dict[(m2, g2)]
            ):
                G.add_edge((m1, g1), (m2, g2))
    return G


def generar_opciones(
    materias,
    max_opciones=5,
    min_calificacion=3,
    max_calificacion=None,
    incluir_cero=False,
    materias_fijas=None,
):
    if materias_fijas is None:
        materias_fijas = {}

    opciones = []
    grupos_por_materia = {}

    for materia in materias:
        # MATERIA FIJA (Respeta la elección explícita del usuario sin descartarla por calificación)
        if materia in materias_fijas:
            grupo_fijo = materias_fijas[materia]
            horarios = horarios_dict.get((materia, grupo_fijo), [])

            if not horarios:
                print(
                    f"⚠️ No se encontró el grupo fijo '{grupo_fijo}' para {materia}"
                )
                grupos_por_materia[materia] = []
                continue

            grupos_por_materia[materia] = [(grupo_fijo, horarios)]
            continue

        # MATERIAS A SELECCIONAR
        grupos = [
            (grp, hs)
            for (mat, grp), hs in horarios_dict.items()
            if mat == materia
        ]
        grupos = [g for g in grupos if any(int(h["Cupos"]) > 0 for h in g[1])]

        grupos_filtrados = []
        for grupo, horarios in grupos:
            calificaciones = [int(h["Calificacion"]) for h in horarios]
            if not calificaciones:
                continue

            max_calif = max(calificaciones)
            tiene_cero = 0 in calificaciones

            if max_calificacion is not None and max_calif > max_calificacion:
                continue

            if incluir_cero:
                if max_calif >= min_calificacion or tiene_cero:
                    grupos_filtrados.append((grupo, horarios))
            else:
                if max_calif >= min_calificacion and not tiene_cero:
                    grupos_filtrados.append((grupo, horarios))

        grupos_filtrados.sort(
            key=lambda x: max(int(h["Calificacion"]) for h in x[1]),
            reverse=True,
        )

        grupos_por_materia[materia] = grupos_filtrados

    def backtracking(idx, seleccion, horarios_ocupados):
        if len(opciones) >= max_opciones:
            return

        if idx == len(materias):
            opciones.append(deepcopy(seleccion))
            return

        materia = materias[idx]
        for grupo, horarios in grupos_por_materia.get(materia, []):
            if all(
                not hay_choque(h, h_ocp)
                for h in horarios
                for h_ocp in horarios_ocupados
            ):
                seleccion.append((materia, grupo, horarios))
                horarios_ocupados.extend(horarios)
                backtracking(idx + 1, seleccion, horarios_ocupados)
                for _ in horarios:
                    horarios_ocupados.pop()
                seleccion.pop()

    backtracking(0, [], [])
    return opciones


def mostrar_horario_tabla(opcion):
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    horas = [f"{h:02d}:00" for h in range(7, 21)]
    matriz = defaultdict(list)

    def horas_entre(inicio, fin):
        hi = int(inicio.split(":")[0])
        hf = int(fin.split(":")[0])
        return [f"{h:02d}:00" for h in range(hi, hf)]

    def abreviar_materia(nombre):
        return nombre.split("(")[0].strip()[:18]

    for materia, grupo, horarios in opcion:
        mat = abreviar_materia(materia)
        for h in horarios:
            if h["Dias de la semana"] in dias:
                for hora in horas_entre(h["Hora inicio"], h["Hora fin"]):
                    texto = f"{mat} {grupo}"
                    if texto not in matriz[(hora, h["Dias de la semana"])]:
                        matriz[(hora, h["Dias de la semana"])].append(texto)

    ancho_hora = 10
    ancho_celda = 22
    sep = "|"
    linea = "-" * (ancho_hora + (ancho_celda + 1) * len(dias) + 1)

    print(linea)
    print(sep + "Hora".center(ancho_hora), end="")
    for d in dias:
        print(sep + d[:3].center(ancho_celda), end="")
    print(sep)
    print(linea)

    for hora in horas:
       
        lineas_por_dia = []
        for d in dias:
            contenido = "\n".join(matriz.get((hora, d), [""]))
            if contenido:
                lineas_envueltas = textwrap.wrap(contenido, width=ancho_celda)
            else:
                lineas_envueltas = [""]
            lineas_por_dia.append(lineas_envueltas)

        max_altura = max(len(l) for l in lineas_por_dia)

        for i in range(max_altura):
            etiqueta_hora = hora if i == 0 else ""
            print(sep + etiqueta_hora.center(ancho_hora), end="")
            for d_idx, d in enumerate(dias):
                lineas = lineas_por_dia[d_idx]
                txt = lineas[i] if i < len(lineas) else ""
                print(sep + txt.ljust(ancho_celda), end="")
            print(sep)
        print(linea)


if __name__ == "__main__":
    G = construir_grafo_conflictos()
    print(
        f"Grafo de conflictos: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas"
    )

    # todas las materias deben de aparecer en materias_a_seleccionar, en caso de querer un grupo fijo tienen que salir adicionalmente en materias_fijas junto con el número de grupo que se desea    materias_a_seleccionar = [
        "Fundamentos de electricidad y magnetismo (1000017-B)",
        "Cálculo en varias variables (1000006-B)",
        "Estructuras de datos (2016699)",
        "Matemáticas discretas I (2025963)",
        "Arquitectura de computadores (2016697)"
    ]

    materias_fijas = {
        "Estructuras de datos (2016699)": "(6) Grupo 6",
        "Fundamentos de electricidad y magnetismo (1000017-B)": "(10) Grupo 10",
        "Cálculo en varias variables (1000006-B)": "(10) Grupo 10",
    

    }

    opciones_generadas = generar_opciones(
        materias_a_seleccionar,
        max_opciones=5,
        min_calificacion=1,
        max_calificacion=5,
        incluir_cero=True,
        materias_fijas=materias_fijas,
    )

    if not opciones_generadas:
        print(
            " No se encontraron opciones válidas con los filtros aplicados."
        )
    else:
        for idx, opcion in enumerate(opciones_generadas, start=1):
            # Suma de la calificación única por profesor en el grupo elegido
            suma_calif = sum(
                max(int(h["Calificacion"]) for h in horarios)
                for _, _, horarios in opcion
            )

            print("\n" + "=" * 125)
            print(
                f" OPCIÓN {idx} | Balance de Calificación Profesores = {suma_calif}"
            )
            print("=" * 125)
            mostrar_horario_tabla(opcion)
