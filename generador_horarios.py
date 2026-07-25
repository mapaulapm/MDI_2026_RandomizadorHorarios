import os
import pandas as pd
import networkx as nx
from itertools import product


try:
    CARPETA_SCRIPT = os.path.dirname(os.path.abspath(__file__))
except NameError:
    CARPETA_SCRIPT = os.getcwd()

RUTA = os.path.join(CARPETA_SCRIPT, "MD_BaseDatos.xlsx")
HOJA = "Base"
MINIMO_CALIFICACION = 2  


def parsear_hora(valor):
    """Convierte 'HH:MM' o 'HH:MM:SS' (str u objeto time) a horas decimales."""
    if pd.isna(valor):
        return None
    if hasattr(valor, "hour"): 
        return valor.hour + valor.minute / 60
    partes = str(valor).strip().split(":")
    h = int(partes[0])
    m = int(partes[1]) if len(partes) > 1 else 0
    return h + m / 60


def cargar_datos(ruta=RUTA, hoja=HOJA):
    df = pd.read_excel(ruta, sheet_name=hoja)
    df = df.dropna(subset=["Materia", "Grupo"])
    df["hora_inicio_dec"] = df["Hora inicio"].apply(parsear_hora)
    df["hora_fin_dec"] = df["Hora fin"].apply(parsear_hora)
    df["Dias de la semana"] = df["Dias de la semana"].str.strip()
    return df


def construir_grupos(df):
    """
    materias[materia] = lista de grupos.
    Cada grupo = {"grupo", "profesor", "calificacion", "sesiones": [(dia, ini, fin), ...]}
    Un grupo puede tener varias sesiones (una por dia), y no todas tienen que
    coincidir en horario entre si (ej. lunes 7-9, jueves 9-11).
    """
    materias = {}
    for (materia, grupo), sub in df.groupby(["Materia", "Grupo"]):
        sesiones = [
            (row["Dias de la semana"], row["hora_inicio_dec"], row["hora_fin_dec"])
            for _, row in sub.iterrows()
            if row["hora_inicio_dec"] is not None and row["hora_fin_dec"] is not None
        ]
        materias.setdefault(materia, []).append({
            "grupo": grupo,
            "profesor": sub["Profesor"].iloc[0],
            "calificacion": sub["Calificacion"].iloc[0],
            "sesiones": sesiones,
        })
    return materias


def sesiones_chocan(s1, s2):
    dia1, ini1, fin1 = s1
    dia2, ini2, fin2 = s2
    if dia1 != dia2:
        return False
    return not (fin1 <= ini2 or fin2 <= ini1)


def grupos_chocan(g1, g2):
    return any(sesiones_chocan(s1, s2) for s1 in g1["sesiones"] for s2 in g2["sesiones"])


def construir_grafo_conflictos(materias):
    """Nodo = (materia, grupo). Arista = choque de horario entre grupos de materias distintas."""
    G = nx.Graph()
    nodos_por_materia = {}
    for materia, grupos in materias.items():
        nodos = []
        for g in grupos:
            nodo_id = (materia, g["grupo"])
            G.add_node(nodo_id, **g)
            nodos.append(nodo_id)
        nodos_por_materia[materia] = nodos

    todos = list(G.nodes(data=True))
    for i in range(len(todos)):
        id1, data1 = todos[i]
        for id2, data2 in todos[i + 1:]:
            if id1[0] == id2[0]:
                continue  
            if grupos_chocan(data1, data2):
                G.add_edge(id1, id2)

    return G, nodos_por_materia


def generar_propuestas(G, nodos_por_materia, minimo_calificacion=MINIMO_CALIFICACION, top=30):
    materias_lista = list(nodos_por_materia.keys())
    propuestas = []
    for combo in product(*[nodos_por_materia[m] for m in materias_lista]):
        
        if any(G.has_edge(combo[i], combo[j])
               for i in range(len(combo)) for j in range(i + 1, len(combo))):
            continue
        calificaciones = [G.nodes[n]["calificacion"] for n in combo]
        if min(calificaciones) < minimo_calificacion:
            continue
        score = sum(calificaciones) / len(calificaciones)
        propuestas.append((score, combo))

    propuestas.sort(key=lambda x: x[0], reverse=True)
    return propuestas[:top]


def imprimir_propuesta(G, score, combo, indice):
    print(f"\nPropuesta {indice} | Calificacion promedio: {score:.2f}")
    for nodo in combo:
        materia, grupo = nodo
        data = G.nodes[nodo]
        sesiones_str = "; ".join(
            f"{d} {int(i)}:{int((i % 1) * 60):02d}-{int(f)}:{int((f % 1) * 60):02d}"
            for d, i, f in data["sesiones"]
        )
        print(f"   - {materia} | {grupo} | {data['profesor']} | "
              f"Calif: {data['calificacion']} | {sesiones_str}")


if __name__ == "__main__":
    df = cargar_datos()
    materias = construir_grupos(df)
    G, nodos_por_materia = construir_grafo_conflictos(materias)

    print(f"Grafo de conflictos: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")
    for m, nodos in nodos_por_materia.items():
        print(f"  {m}: {len(nodos)} grupos")

    propuestas = generar_propuestas(G, nodos_por_materia)
    print(f"\n{len(propuestas)} propuestas validas encontradas")

    for i, (score, combo) in enumerate(propuestas[:10], 1):
        imprimir_propuesta(G, score, combo, i)
