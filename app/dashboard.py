"""Dashboard sencillo para explorar gravedad, causas y características viales."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


CARPETA_PROYECTO = Path(__file__).resolve().parents[1]
CARPETA_RESULTADOS = CARPETA_PROYECTO / "resultados"

FRANJAS = [
    "Madrugada (00-05)",
    "Mañana (06-11)",
    "Tarde (12-17)",
    "Noche (18-23)",
]

GRAVEDADES = ["SOLO DANOS", "CON HERIDOS", "CON MUERTOS"]


@st.cache_data
def cargar_resumenes():
    """Lee las tablas agregadas que genera el script de análisis."""
    accidentes = pd.read_csv(CARPETA_RESULTADOS / "resumen_accidentes.csv")
    causas = pd.read_csv(CARPETA_RESULTADOS / "resumen_causas.csv")
    vias = pd.read_csv(CARPETA_RESULTADOS / "resumen_vias.csv")
    return accidentes, causas, vias


st.set_page_config(page_title="Seguridad vial en Bogotá", layout="wide")
st.title("Seguridad vial en Bogotá")
st.caption(
    "Exploración de gravedad, causas registradas y características de las vías "
    "según localidad y franja horaria."
)

archivos_resultado = [
    CARPETA_RESULTADOS / "resumen_accidentes.csv",
    CARPETA_RESULTADOS / "resumen_causas.csv",
    CARPETA_RESULTADOS / "resumen_vias.csv",
]

if not all(archivo.exists() for archivo in archivos_resultado):
    st.error(
        "Primero ejecute `python app/analisis_seguridad_vial.py` desde la "
        "carpeta del proyecto para generar los resúmenes."
    )
    st.stop()

resumen_accidentes, resumen_causas, resumen_vias = cargar_resumenes()

# Conserva los registros sin localidad como una categoría visible en los filtros.
for tabla in [resumen_accidentes, resumen_causas, resumen_vias]:
    tabla["LOCALIDAD"] = tabla["LOCALIDAD"].fillna("SIN REGISTRO")

# Los filtros permiten comparar lugares y horarios sin volver a cargar los CSV originales.
localidades = sorted(resumen_accidentes["LOCALIDAD"].dropna().unique().tolist())
localidades_seleccionadas = st.sidebar.multiselect(
    "Localidad",
    localidades,
    default=localidades,
)
franjas_seleccionadas = st.sidebar.multiselect(
    "Franja horaria",
    FRANJAS,
    default=FRANJAS,
)

if not localidades_seleccionadas or not franjas_seleccionadas:
    st.warning("Seleccione al menos una localidad y una franja horaria.")
    st.stop()

filtro_accidentes = resumen_accidentes[
    resumen_accidentes["LOCALIDAD"].isin(localidades_seleccionadas)
    & resumen_accidentes["FRANJA"].isin(franjas_seleccionadas)
]

# Calcula indicadores generales para la selección actual.
por_gravedad = (
    filtro_accidentes.groupby("GRAVEDAD")["NUMERO_SINIESTROS"]
    .sum()
    .reindex(GRAVEDADES, fill_value=0)
)
total = int(por_gravedad.sum())
graves = int(por_gravedad["CON HERIDOS"] + por_gravedad["CON MUERTOS"])
muertos = int(por_gravedad["CON MUERTOS"])
porcentaje_grave = graves / total * 100 if total else 0
porcentaje_muertos = muertos / total * 100 if total else 0

columna_1, columna_2, columna_3, columna_4 = st.columns(4)
columna_1.metric("Siniestros", f"{total:,}")
columna_2.metric("Con heridos o muertos", f"{graves:,}", f"{porcentaje_grave:.1f}%")
columna_3.metric("Con muertos", f"{muertos:,}", f"{porcentaje_muertos:.1f}%")
columna_4.metric("Localidades seleccionadas", f"{len(localidades_seleccionadas)}")

# Compara las categorías de gravedad por franja horaria.
por_hora = (
    filtro_accidentes.groupby(["FRANJA", "GRAVEDAD"], as_index=False)[
        "NUMERO_SINIESTROS"
    ]
    .sum()
)
figura_hora = px.bar(
    por_hora,
    x="FRANJA",
    y="NUMERO_SINIESTROS",
    color="GRAVEDAD",
    barmode="stack",
    category_orders={"FRANJA": FRANJAS, "GRAVEDAD": GRAVEDADES},
    title="Siniestros por franja horaria y gravedad",
    labels={
        "FRANJA": "Franja horaria",
        "NUMERO_SINIESTROS": "Siniestros",
        "GRAVEDAD": "Gravedad",
    },
)
st.plotly_chart(figura_hora, width="stretch")

# Calcula porcentajes por localidad y permite definir un mínimo de observaciones.
por_localidad = (
    filtro_accidentes.groupby(["LOCALIDAD", "GRAVEDAD"], as_index=False)[
        "NUMERO_SINIESTROS"
    ]
    .sum()
    .pivot(index="LOCALIDAD", columns="GRAVEDAD", values="NUMERO_SINIESTROS")
    .fillna(0)
)
for gravedad in GRAVEDADES:
    if gravedad not in por_localidad.columns:
        por_localidad[gravedad] = 0
por_localidad["TOTAL"] = por_localidad[GRAVEDADES].sum(axis=1)
por_localidad["PORCENTAJE_GRAVE"] = (
    por_localidad["CON HERIDOS"] + por_localidad["CON MUERTOS"]
) / por_localidad["TOTAL"] * 100

minimo_localidad = st.sidebar.number_input(
    "Mínimo de siniestros por localidad",
    min_value=1,
    value=10000,
    step=1000,
)
localidades_comparables = por_localidad[
    por_localidad["TOTAL"] >= minimo_localidad
].sort_values("PORCENTAJE_GRAVE", ascending=False)

figura_localidad = px.bar(
    localidades_comparables.head(15).reset_index(),
    x="PORCENTAJE_GRAVE",
    y="LOCALIDAD",
    orientation="h",
    hover_data=["TOTAL"],
    title="Proporción de siniestros con heridos o muertos por localidad",
    labels={
        "PORCENTAJE_GRAVE": "Siniestros graves (%)",
        "LOCALIDAD": "Localidad",
        "TOTAL": "Siniestros",
    },
)
figura_localidad.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(figura_localidad, width="stretch")

# La tabla de causas cuenta cada nombre una sola vez por siniestro.
causas_filtradas = resumen_causas[
    resumen_causas["LOCALIDAD"].isin(localidades_seleccionadas)
    & resumen_causas["FRANJA"].isin(franjas_seleccionadas)
]
por_causa = (
    causas_filtradas.groupby(["NOMBRE", "GRAVEDAD"], as_index=False)[
        "NUMERO_SINIESTROS"
    ]
    .sum()
    .pivot(index="NOMBRE", columns="GRAVEDAD", values="NUMERO_SINIESTROS")
    .fillna(0)
)
for gravedad in GRAVEDADES:
    if gravedad not in por_causa.columns:
        por_causa[gravedad] = 0
por_causa["TOTAL"] = por_causa[GRAVEDADES].sum(axis=1)
por_causa["PORCENTAJE_GRAVE"] = (
    por_causa["CON HERIDOS"] + por_causa["CON MUERTOS"]
) / por_causa["TOTAL"] * 100
minimo_causa = st.sidebar.number_input(
    "Mínimo de siniestros para mostrar una causa",
    min_value=1,
    value=500,
    step=100,
)
causas_comparables = por_causa[por_causa["TOTAL"] >= minimo_causa].copy()

if not causas_comparables.empty:
    causas_comparables = causas_comparables.sort_values(
        "PORCENTAJE_GRAVE",
        ascending=False,
    ).head(15)
    figura_causas = px.bar(
        causas_comparables.reset_index(),
        x="PORCENTAJE_GRAVE",
        y="NOMBRE",
        orientation="h",
        hover_data=["TOTAL", "CON MUERTOS"],
        title="Causas con mayor proporción de siniestros graves",
        labels={
            "PORCENTAJE_GRAVE": "Siniestros graves (%)",
            "NOMBRE": "Causa registrada",
            "TOTAL": "Asociaciones con la causa",
            "CON MUERTOS": "Siniestros con muertos",
        },
    )
    figura_causas.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(figura_causas, width="stretch")
    st.dataframe(
        causas_comparables.sort_values("TOTAL", ascending=False).reset_index(),
        width="stretch",
    )
else:
    st.info("No hay causas con el mínimo de observaciones seleccionado.")

# Cada característica vial se muestra por separado para evitar cruces muchos-a-muchos.
caracteristicas = sorted(resumen_vias["CARACTERISTICA"].dropna().unique().tolist())
caracteristica = st.selectbox("Característica de la vía", caracteristicas)
vias_filtradas = resumen_vias[
    resumen_vias["LOCALIDAD"].isin(localidades_seleccionadas)
    & resumen_vias["FRANJA"].isin(franjas_seleccionadas)
    & (resumen_vias["CARACTERISTICA"] == caracteristica)
]
por_categoria = (
    vias_filtradas.groupby(["CATEGORIA", "GRAVEDAD"], as_index=False)[
        "NUMERO_SINIESTROS"
    ]
    .sum()
    .pivot(index="CATEGORIA", columns="GRAVEDAD", values="NUMERO_SINIESTROS")
    .fillna(0)
)
for gravedad in GRAVEDADES:
    if gravedad not in por_categoria.columns:
        por_categoria[gravedad] = 0
por_categoria["TOTAL"] = por_categoria[GRAVEDADES].sum(axis=1)
por_categoria["PORCENTAJE_GRAVE"] = (
    por_categoria["CON HERIDOS"] + por_categoria["CON MUERTOS"]
) / por_categoria["TOTAL"] * 100
por_categoria = por_categoria.sort_values("TOTAL", ascending=False)

figura_vias = px.bar(
    por_categoria.reset_index(),
    x="PORCENTAJE_GRAVE",
    y="CATEGORIA",
    orientation="h",
    hover_data=["TOTAL"],
    title=f"Gravedad según {caracteristica}",
    labels={
        "PORCENTAJE_GRAVE": "Siniestros graves (%)",
        "CATEGORIA": "Categoría registrada",
        "TOTAL": "Asociaciones con la categoría",
    },
)
figura_vias.update_layout(yaxis={"categoryorder": "total ascending"})
st.plotly_chart(figura_vias, width="stretch")

st.info(
    "Los porcentajes describen siniestros registrados, no el riesgo por viaje o "
    "por vehículo. Las causas y vías tienen coberturas distintas; un siniestro "
    "puede tener varias causas o registros viales, por lo que las categorías no "
    "son excluyentes. Las asociaciones no demuestran causalidad."
)
