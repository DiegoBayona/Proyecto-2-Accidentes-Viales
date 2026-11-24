"""Prepara los tres CSV principales y resume siniestros viales de Bogotá."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd


# Las rutas se calculan desde este archivo para que el proyecto funcione
# sin depender de una ruta fija del computador.
CARPETA_PROYECTO = Path(__file__).resolve().parents[1]
CARPETA_DATOS = CARPETA_PROYECTO / "data"
CARPETA_RESULTADOS = CARPETA_PROYECTO / "resultados"
CARPETA_FIGURAS = CARPETA_RESULTADOS / "figuras"

FRANJAS = [
    "Madrugada (00-05)",
    "Mañana (06-11)",
    "Tarde (12-17)",
    "Noche (18-23)",
]

COLUMNAS_ACCIDENTES = [
    "CODIGO_ACCIDENTE",
    "FECHA_HORA_ACC",
    "HORA_OCURRENCIA_ACC",
    "GRAVEDAD",
    "LOCALIDAD",
    "CLASE_ACC",
]

COLUMNAS_CAUSAS = ["CODIGO_ACCIDENTE", "CODIGO_CAUSA", "NOMBRE"]

COLUMNAS_VIAS = [
    "CODIGO_ACCIDENTE",
    "ES_PRINCIPAL",
    "GEOMETRICAA",
    "GEOMETRICAB",
    "GEOMETRICAC",
    "UTILIZACION",
    "CALZADAS",
    "CARRILES",
    "SUPERFICIE_RODADURA",
    "ESTADO",
    "CONDICIONES",
    "ILUMINACION_ARTIFICIAL",
    "SEMAFORO",
    "VISUALVIA",
]

CARACTERISTICAS_VIA = COLUMNAS_VIAS[2:]


def limpiar_texto(datos, columnas):
    """Unifica espacios y mayúsculas en las variables de texto seleccionadas."""
    for columna in columnas:
        datos[columna] = datos[columna].astype("string").str.strip().str.upper()
        datos[columna] = datos[columna].replace("", pd.NA)
    return datos


def guardar_figuras(accidentes, causas, vias):
    """Crea gráficos descriptivos para el informe y la presentación."""
    CARPETA_FIGURAS.mkdir(parents=True, exist_ok=True)

    # Compara la distribución de gravedad dentro de cada franja horaria.
    gravedad_hora = pd.crosstab(
        accidentes["FRANJA"],
        accidentes["GRAVEDAD"],
        normalize="index",
    ) * 100
    gravedad_hora = gravedad_hora.reindex(FRANJAS)
    gravedad_hora = gravedad_hora.reindex(
        columns=["SOLO DANOS", "CON HERIDOS", "CON MUERTOS"],
        fill_value=0,
    )
    gravedad_hora.plot(
        kind="bar",
        stacked=True,
        color=["steelblue", "darkorange", "firebrick"],
        figsize=(9, 5),
    )
    plt.title("Gravedad registrada por franja horaria")
    plt.xlabel("Franja horaria")
    plt.ylabel("Siniestros (%)")
    plt.xticks(rotation=0)
    plt.legend(title="Gravedad")
    plt.tight_layout()
    plt.savefig(CARPETA_FIGURAS / "gravedad_por_franja.png", dpi=180)
    plt.close()

    # Prioriza localidades con suficiente volumen para que la comparación sea estable.
    localidad = accidentes.groupby("LOCALIDAD", dropna=False).agg(
        total=("CODIGO_ACCIDENTE", "size"),
        graves=("CASO_GRAVE", "sum"),
    )
    localidad = localidad[localidad["total"] >= 10000].copy()
    localidad["porcentaje_grave"] = localidad["graves"] / localidad["total"] * 100
    localidad = localidad.sort_values("porcentaje_grave").tail(10)
    localidad["porcentaje_grave"].plot(
        kind="barh",
        color="darkorange",
        figsize=(9, 5),
    )
    plt.title("Localidades con mayor proporción de siniestros graves")
    plt.xlabel("Con heridos o muertos (%)")
    plt.ylabel("Localidad (mínimo 10.000 registros)")
    plt.tight_layout()
    plt.savefig(CARPETA_FIGURAS / "gravedad_por_localidad.png", dpi=180)
    plt.close()

    # Muestra las causas más frecuentes contando cada causa una sola vez por siniestro.
    causa_frecuente = causas.groupby("NOMBRE")["CODIGO_ACCIDENTE"].nunique()
    causa_frecuente = causa_frecuente.sort_values().tail(10)
    causa_frecuente.plot(kind="barh", color="steelblue", figsize=(9, 5))
    plt.title("Causas registradas con mayor frecuencia")
    plt.xlabel("Siniestros asociados")
    plt.ylabel("Causa")
    plt.tight_layout()
    plt.savefig(CARPETA_FIGURAS / "causas_frecuentes.png", dpi=180)
    plt.close()

    # Compara uso de la vía con el porcentaje de siniestros con heridos o muertos.
    uso_via = vias[vias["CARACTERISTICA"] == "UTILIZACION"]
    uso_via = uso_via.pivot_table(
        index="CATEGORIA",
        columns="GRAVEDAD",
        values="NUMERO_SINIESTROS",
        aggfunc="sum",
        fill_value=0,
    )
    for gravedad in ["SOLO DANOS", "CON HERIDOS", "CON MUERTOS"]:
        if gravedad not in uso_via.columns:
            uso_via[gravedad] = 0
    uso_via["TOTAL"] = uso_via[
        ["SOLO DANOS", "CON HERIDOS", "CON MUERTOS"]
    ].sum(axis=1)
    uso_via = uso_via[uso_via["TOTAL"] >= 500].copy()
    uso_via["porcentaje_grave"] = (
        uso_via["CON HERIDOS"] + uso_via["CON MUERTOS"]
    ) / uso_via["TOTAL"] * 100
    uso_via["porcentaje_grave"].sort_values().plot(
        kind="barh",
        color="seagreen",
        figsize=(9, 5),
    )
    plt.title("Gravedad según el uso de la vía")
    plt.xlabel("Con heridos o muertos (%)")
    plt.ylabel("Uso de la vía (mínimo 500 asociaciones)")
    plt.tight_layout()
    plt.savefig(CARPETA_FIGURAS / "gravedad_por_uso_via.png", dpi=180)
    plt.close()


def main():
    """Carga, integra, resume y guarda resultados reproducibles."""
    CARPETA_RESULTADOS.mkdir(parents=True, exist_ok=True)

    # Se cargan solo las variables necesarias de los CSV ubicados directamente
    # en data; no se consulta la carpeta data complementario.
    accidentes = pd.read_csv(
        CARPETA_DATOS / "ACCIDENTE.csv",
        usecols=COLUMNAS_ACCIDENTES,
        dtype={"CODIGO_ACCIDENTE": "Int64"},
    )
    causas = pd.read_csv(
        CARPETA_DATOS / "VM_ACC_CAUSA.csv",
        usecols=COLUMNAS_CAUSAS,
        dtype={
            "CODIGO_ACCIDENTE": "Int64",
            "CODIGO_CAUSA": "string",
            "NOMBRE": "string",
        },
    )
    tipos_vias = {columna: "string" for columna in COLUMNAS_VIAS}
    tipos_vias["CODIGO_ACCIDENTE"] = "Int64"
    vias = pd.read_csv(
        CARPETA_DATOS / "VM_ACC_VIA.csv",
        usecols=COLUMNAS_VIAS,
        dtype=tipos_vias,
    )

    # Normaliza categorías y crea la franja horaria a partir de la hora reportada.
    accidentes = limpiar_texto(
        accidentes,
        ["GRAVEDAD", "LOCALIDAD", "CLASE_ACC"],
    )
    accidentes["FECHA_HORA_ACC"] = pd.to_datetime(
        accidentes["FECHA_HORA_ACC"],
        errors="coerce",
        utc=True,
    )
    accidentes["HORA"] = pd.to_numeric(
        accidentes["HORA_OCURRENCIA_ACC"].astype("string").str[:2],
        errors="coerce",
    )
    accidentes["FRANJA"] = pd.cut(
        accidentes["HORA"],
        bins=[0, 6, 12, 18, 24],
        right=False,
        labels=FRANJAS,
    ).astype("string")
    accidentes["CASO_GRAVE"] = accidentes["GRAVEDAD"].isin(
        ["CON HERIDOS", "CON MUERTOS"]
    )

    # Cada fila de accidentes debe representar un siniestro único.
    if accidentes["CODIGO_ACCIDENTE"].duplicated().any():
        raise ValueError("ACCIDENTE contiene CODIGO_ACCIDENTE duplicados.")

    # Deduplica las causas repetidas para un mismo siniestro y causa.
    causas = limpiar_texto(causas, ["NOMBRE"])
    causas = causas.dropna(
        subset=["CODIGO_ACCIDENTE", "CODIGO_CAUSA", "NOMBRE"]
    )
    causas = causas.drop_duplicates(
        subset=["CODIGO_ACCIDENTE", "CODIGO_CAUSA", "NOMBRE"]
    )
    columnas_accidente = [
        "CODIGO_ACCIDENTE",
        "GRAVEDAD",
        "LOCALIDAD",
        "FRANJA",
    ]
    causas_integradas = causas.merge(
        accidentes[columnas_accidente],
        on="CODIGO_ACCIDENTE",
        how="inner",
        validate="many_to_one",
    )
    # Si hay códigos distintos con el mismo nombre en un siniestro, se cuenta
    # una sola asociación por nombre para no inflar las frecuencias.
    causas_integradas = causas_integradas.drop_duplicates(
        subset=["CODIGO_ACCIDENTE", "NOMBRE"]
    )
    resumen_causas = (
        causas_integradas.groupby(
            ["NOMBRE", "LOCALIDAD", "FRANJA", "GRAVEDAD"],
            dropna=False,
        )
        .size()
        .reset_index(name="NUMERO_SINIESTROS")
    )

    # Se usan únicamente los registros identificados como vía principal.
    # Un siniestro puede tener varias vías principales registradas.
    vias = limpiar_texto(vias, CARACTERISTICAS_VIA + ["ES_PRINCIPAL"])
    vias_principales = vias[vias["ES_PRINCIPAL"] == "1"].copy()
    vias_integradas = vias_principales.merge(
        accidentes[columnas_accidente],
        on="CODIGO_ACCIDENTE",
        how="inner",
        validate="many_to_one",
    )

    # Cada siniestro se cuenta una sola vez por característica y categoría.
    tablas_resumen_vias = []
    for caracteristica in CARACTERISTICAS_VIA:
        tabla = vias_integradas[
            [
                "CODIGO_ACCIDENTE",
                "LOCALIDAD",
                "FRANJA",
                "GRAVEDAD",
                caracteristica,
            ]
        ].dropna(subset=[caracteristica])
        tabla = tabla.drop_duplicates(
            subset=["CODIGO_ACCIDENTE", caracteristica]
        )
        tabla = tabla.rename(columns={caracteristica: "CATEGORIA"})
        tabla["CARACTERISTICA"] = caracteristica
        resumen_caracteristica = (
            tabla.groupby(
                [
                    "CARACTERISTICA",
                    "CATEGORIA",
                    "LOCALIDAD",
                    "FRANJA",
                    "GRAVEDAD",
                ],
                dropna=False,
            )
            .size()
            .reset_index(name="NUMERO_SINIESTROS")
        )
        tablas_resumen_vias.append(resumen_caracteristica)
    resumen_vias = pd.concat(tablas_resumen_vias, ignore_index=True)

    # La tabla integrada conserva una fila por accidente y guarda el número
    # de causas y vías enlazadas, sin multiplicar registros.
    causas_por_accidente = (
        causas_integradas.groupby("CODIGO_ACCIDENTE")["NOMBRE"]
        .nunique()
        .reset_index(name="NUMERO_CAUSAS")
    )
    vias_por_accidente = (
        vias_integradas.groupby("CODIGO_ACCIDENTE")
        .size()
        .reset_index(name="NUMERO_VIAS_PRINCIPALES")
    )
    accidentes_integrados = accidentes.merge(
        causas_por_accidente,
        on="CODIGO_ACCIDENTE",
        how="left",
        validate="one_to_one",
    )
    accidentes_integrados = accidentes_integrados.merge(
        vias_por_accidente,
        on="CODIGO_ACCIDENTE",
        how="left",
        validate="one_to_one",
    )
    accidentes_integrados["NUMERO_CAUSAS"] = (
        accidentes_integrados["NUMERO_CAUSAS"].fillna(0).astype("int64")
    )
    accidentes_integrados["NUMERO_VIAS_PRINCIPALES"] = (
        accidentes_integrados["NUMERO_VIAS_PRINCIPALES"].fillna(0).astype("int64")
    )

    # Calcula cobertura de las relaciones para documentar qué tanto se puede
    # generalizar cada análisis.
    ids_accidentes = set(accidentes["CODIGO_ACCIDENTE"].dropna())
    ids_causas = set(causas["CODIGO_ACCIDENTE"].dropna())
    ids_vias = set(vias_principales["CODIGO_ACCIDENTE"].dropna())
    ids_causas_validas = set(causas_integradas["CODIGO_ACCIDENTE"].dropna())
    ids_vias_validas = set(vias_integradas["CODIGO_ACCIDENTE"].dropna())

    calidad = pd.DataFrame(
        [
            ["Siniestros en ACCIDENTE", len(accidentes)],
            ["CODIGO_ACCIDENTE único en ACCIDENTE", accidentes["CODIGO_ACCIDENTE"].nunique()],
            ["Siniestros sin gravedad", int(accidentes["GRAVEDAD"].isna().sum())],
            ["Siniestros con causa registrada y nombre válido", len(ids_causas_validas)],
            ["Siniestros con vía principal registrada y cruce válido", len(ids_vias_validas)],
            ["Cobertura de causas sobre ACCIDENTE (%)", round(len(ids_causas_validas) / len(ids_accidentes) * 100, 2)],
            ["Cobertura de vías principales sobre ACCIDENTE (%)", round(len(ids_vias_validas) / len(ids_accidentes) * 100, 2)],
            ["Claves de causas no presentes en ACCIDENTE", len(ids_causas - ids_accidentes)],
            ["Claves de vías principales no presentes en ACCIDENTE", len(ids_vias - ids_accidentes)],
            ["Filas de causas luego de deduplicar", len(causas)],
            ["Filas de vías principales", len(vias_principales)],
        ],
        columns=["INDICADOR", "VALOR"],
    )

    # Guarda tablas de análisis e integración para el dashboard.
    resumen_accidentes = (
        accidentes.dropna(subset=["GRAVEDAD"])
        .groupby(["LOCALIDAD", "FRANJA", "GRAVEDAD"], dropna=False)
        .size()
        .reset_index(name="NUMERO_SINIESTROS")
    )
    resumen_accidentes.to_csv(
        CARPETA_RESULTADOS / "resumen_accidentes.csv",
        index=False,
        encoding="utf-8-sig",
    )
    resumen_causas.to_csv(
        CARPETA_RESULTADOS / "resumen_causas.csv",
        index=False,
        encoding="utf-8-sig",
    )
    resumen_vias.to_csv(
        CARPETA_RESULTADOS / "resumen_vias.csv",
        index=False,
        encoding="utf-8-sig",
    )
    accidentes_integrados.to_csv(
        CARPETA_RESULTADOS / "accidentes_integrados.csv",
        index=False,
        encoding="utf-8-sig",
    )
    calidad.to_csv(
        CARPETA_RESULTADOS / "resumen_calidad.csv",
        index=False,
        encoding="utf-8-sig",
    )

    # Los gráficos resumen los patrones principales con métodos vistos en clase.
    guardar_figuras(accidentes, causas_integradas, resumen_vias)

    print("Análisis terminado.")
    print("Siniestros en ACCIDENTE:", len(accidentes))
    print("Causas integradas:", len(causas_integradas))
    print("Registros de vía principal integrados:", len(vias_integradas))
    print(calidad.to_string(index=False))
    print("Resultados guardados en:", CARPETA_RESULTADOS)


if __name__ == "__main__":
    main()
