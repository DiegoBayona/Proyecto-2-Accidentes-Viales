"""Dashboard para explorar gravedad, causas y características viales en Bogotá."""

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

COLOR_MAX = "#1E3A8A"
COLOR_OTROS = "#93C5FD"

st.set_page_config(page_title="Seguridad vial en Bogotá", layout="wide")

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(160deg, #060d1f 0%, #0b1936 55%, #11264f 100%);
        color: #f1f5f9;
    }
    .stApp h1, .stApp h2, .stApp h3, .stApp label, .stApp p, .stApp span,
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        color: #f8fafc;
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #060d1f 0%, #0b1936 100%);
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data
def cargar_resumenes():
    """Carga los CSV resumidos y normaliza valores nulos en localidad."""
    accidentes = pd.read_csv(CARPETA_RESULTADOS / "resumen_accidentes.csv")
    causas = pd.read_csv(CARPETA_RESULTADOS / "resumen_causas.csv")
    vias = pd.read_csv(CARPETA_RESULTADOS / "resumen_vias.csv")
    for df in (accidentes, causas, vias):
        df["LOCALIDAD"] = df["LOCALIDAD"].fillna("SIN REGISTRO")
    return accidentes, causas, vias


def resumen_gravedad(df, grupo):
    """Agrega por categoría y gravedad, calcula TOTAL y PORCENTAJE_GRAVE."""
    if df.empty:
        return pd.DataFrame(columns=GRAVEDADES + ["TOTAL", "PORCENTAJE_GRAVE"])

    piv = (
        df.groupby([grupo, "GRAVEDAD"], as_index=False)["NUMERO_SINIESTROS"]
        .sum()
        .pivot(index=grupo, columns="GRAVEDAD", values="NUMERO_SINIESTROS")
        .fillna(0)
    )
    for g in GRAVEDADES:
        if g not in piv.columns:
            piv[g] = 0.0

    piv["TOTAL"] = piv[GRAVEDADES].sum(axis=1)
    piv["PORCENTAJE_GRAVE"] = (
        (piv["CON HERIDOS"] + piv["CON MUERTOS"]) / piv["TOTAL"].replace(0, pd.NA) * 100
    ).fillna(0.0)
    return piv


def estilo_oscuro(fig, height=350):
    """Aplica estilo oscuro transparente consistente a cualquier figura Plotly."""
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(6, 13, 31, 0.45)",
        font={"color": "#f1f5f9"},
        legend={"bgcolor": "rgba(0,0,0,0)", "font": {"color": "#f1f5f9"}},
    )
    return fig


def barras_h_max(df, x, y, title, labels, hover_data=None, top_n=15, sort_by=None, height=360):
    """Barras horizontales ordenadas de mayor a menor (arriba el #1) destacando el máximo."""
    if df.empty:
        return None
    top = df.sort_values(sort_by or x, ascending=False).head(top_n).copy()
    max_val = top[x].max()
    top["_COLOR"] = top[x].apply(lambda v: "Max" if max_val > 0 and v == max_val else "Otro")
    top = top.iloc[::-1]

    fig = px.bar(
        top,
        x=x,
        y=y,
        color="_COLOR",
        color_discrete_map={"Max": COLOR_MAX, "Otro": COLOR_OTROS},
        orientation="h",
        hover_data=hover_data or [],
        title=title,
        labels=labels,
    )
    fig.update_layout(showlegend=False)
    return estilo_oscuro(fig, height=height)


st.markdown("## Seguridad vial en Bogotá")
st.caption(
    "Exploración de gravedad, causas registradas y características de las vías "
    "según localidad y franja horaria."
)
st.caption(
    "Limitación principal: la tabla vial cubre 493.675 siniestros "
    "(54,39 % de ACCIDENTE). No se dispone de aforos ni exposición al tránsito."
)

archivos = [
    CARPETA_RESULTADOS / "resumen_accidentes.csv",
    CARPETA_RESULTADOS / "resumen_causas.csv",
    CARPETA_RESULTADOS / "resumen_vias.csv",
]
if not all(a.exists() for a in archivos):
    st.error(
        "Primero ejecute `python app/analisis_seguridad_vial.py` desde la "
        "carpeta del proyecto para generar los resúmenes."
    )
    st.stop()

resumen_accidentes, resumen_causas, resumen_vias = cargar_resumenes()

localidades = sorted(resumen_accidentes["LOCALIDAD"].unique().tolist())
localidades_sel = st.sidebar.multiselect("Localidad", localidades, default=localidades)
franjas_sel = st.sidebar.multiselect("Franja horaria", FRANJAS, default=FRANJAS)

if not localidades_sel or not franjas_sel:
    st.warning("Seleccione al menos una localidad y una franja horaria.")
    st.stop()

acc_f = resumen_accidentes[
    resumen_accidentes["LOCALIDAD"].isin(localidades_sel)
    & resumen_accidentes["FRANJA"].isin(franjas_sel)
]

por_gravedad = (
    acc_f.groupby("GRAVEDAD")["NUMERO_SINIESTROS"]
    .sum()
    .reindex(GRAVEDADES, fill_value=0)
)
total = int(por_gravedad.sum())
graves = int(por_gravedad["CON HERIDOS"] + por_gravedad["CON MUERTOS"])
muertos = int(por_gravedad["CON MUERTOS"])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Siniestros", f"{total:,}")
c2.metric("Con heridos o muertos", f"{graves:,}", f"{graves / total * 100:.1f}%" if total else "0.0%")
c3.metric("Con muertos", f"{muertos:,}", f"{muertos / total * 100:.1f}%" if total else "0.0%")
c4.metric("Localidades seleccionadas", f"{len(localidades_sel)}")

# 1. Franja horaria y gravedad
por_hora = acc_f.groupby(["FRANJA", "GRAVEDAD"], as_index=False)["NUMERO_SINIESTROS"].sum()
fig_hora = px.bar(
    por_hora,
    x="FRANJA",
    y="NUMERO_SINIESTROS",
    color="GRAVEDAD",
    barmode="stack",
    category_orders={"FRANJA": FRANJAS, "GRAVEDAD": GRAVEDADES},
    color_discrete_map={
        "SOLO DANOS": COLOR_OTROS,
        "CON HERIDOS": "#3B82F6",
        "CON MUERTOS": COLOR_MAX,
    },
    title="Siniestros por franja horaria y gravedad",
    labels={"FRANJA": "Franja horaria", "NUMERO_SINIESTROS": "Siniestros", "GRAVEDAD": "Gravedad"},
)
st.plotly_chart(estilo_oscuro(fig_hora, height=340), width="stretch")

# 2. Localidades
min_loc = st.sidebar.number_input("Mínimo de siniestros por localidad", min_value=1, value=10000, step=1000)
loc_df = resumen_gravedad(acc_f, "LOCALIDAD")
loc_df = loc_df[loc_df["TOTAL"] >= min_loc].reset_index()
fig_loc = barras_h_max(
    loc_df,
    x="PORCENTAJE_GRAVE",
    y="LOCALIDAD",
    title="Proporción de siniestros con heridos o muertos por localidad",
    labels={"PORCENTAJE_GRAVE": "Siniestros graves (%)", "LOCALIDAD": "Localidad", "TOTAL": "Siniestros"},
    hover_data=["TOTAL"],
)
if fig_loc:
    st.plotly_chart(fig_loc, width="stretch")
else:
    st.info("No hay localidades que cumplan el mínimo seleccionado.")

# 3. Causas (sin tabla)
cau_f = resumen_causas[
    resumen_causas["LOCALIDAD"].isin(localidades_sel)
    & resumen_causas["FRANJA"].isin(franjas_sel)
]
min_cau = st.sidebar.number_input("Mínimo de siniestros para mostrar una causa", min_value=1, value=500, step=100)
cau_df = resumen_gravedad(cau_f, "NOMBRE")
cau_df = cau_df[cau_df["TOTAL"] >= min_cau].reset_index()
fig_cau = barras_h_max(
    cau_df,
    x="PORCENTAJE_GRAVE",
    y="NOMBRE",
    title="Causas con mayor proporción de siniestros graves",
    labels={
        "PORCENTAJE_GRAVE": "Siniestros graves (%)",
        "NOMBRE": "Causa registrada",
        "TOTAL": "Asociaciones con la causa",
        "CON MUERTOS": "Siniestros con muertos",
    },
    hover_data=["TOTAL", "CON MUERTOS"],
)
if fig_cau:
    st.plotly_chart(fig_cau, width="stretch")
else:
    st.info("No hay causas con el mínimo de observaciones seleccionado.")

# 4. Vías
caracteristicas = sorted(resumen_vias["CARACTERISTICA"].dropna().unique().tolist())
caracteristica = st.selectbox("Característica de la vía", caracteristicas)
via_f = resumen_vias[
    resumen_vias["LOCALIDAD"].isin(localidades_sel)
    & resumen_vias["FRANJA"].isin(franjas_sel)
    & (resumen_vias["CARACTERISTICA"] == caracteristica)
]
via_df = resumen_gravedad(via_f, "CATEGORIA").reset_index()
fig_via = barras_h_max(
    via_df,
    x="PORCENTAJE_GRAVE",
    y="CATEGORIA",
    title=f"Gravedad según {caracteristica}",
    labels={
        "PORCENTAJE_GRAVE": "Siniestros graves (%)",
        "CATEGORIA": "Categoría registrada",
        "TOTAL": "Asociaciones con la categoría",
    },
    hover_data=["TOTAL"],
    sort_by="TOTAL",
)
if fig_via:
    st.plotly_chart(fig_via, width="stretch")
else:
    st.info("No hay categorías viales para los filtros seleccionados.")

st.info(
    "Los porcentajes describen siniestros registrados, no el riesgo por viaje o "
    "por vehículo. Las causas y vías tienen coberturas distintas; un siniestro "
    "puede tener varias causas o registros viales, por lo que las categorías no "
    "son excluyentes. Las asociaciones no demuestran causalidad."
)