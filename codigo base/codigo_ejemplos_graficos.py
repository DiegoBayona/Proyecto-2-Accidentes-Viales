"""
Sesión 12A — Principios de Diseño Visual I
Ejemplos reproducibles de visualizaciones con buenas prácticas.

Requisitos: pandas, numpy y matplotlib.
Ejecutar el script desde Spyder o Jupyter. Se guardan seis gráficos en
la carpeta seleccionada.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Definición de datos
datos = pd.DataFrame({
    "Herramienta": ["Plataforma virtual", "Correo institucional",
                    "Biblioteca digital", "Herramientas colaborativas",
                    "Tutorías virtuales"],
    "Porcentaje": [92, 87, 74, 68, 51]
}).sort_values("Porcentaje", ascending=True)

## 1. Comunicación clara

# pandas
datos.plot(
    x="Herramienta",
    y="Porcentaje",
    kind="barh",
    legend=False,
    title="Uso de herramientas digitales",
    xlabel="Estudiantes (%)",
    xlim=(0, 100),
    figsize=(9, 5.5)
)

# plt.show()

# matplotlib
plt.figure(figsize=(9, 5.5))
plt.barh(datos["Herramienta"], datos["Porcentaje"])
plt.title("Uso de herramientas digitales")
plt.xlabel("Estudiantes (%)")
plt.xlim(0, 100)
plt.tight_layout()

## 2. Percepción visual y agrupación

# Definición de datos
datos2 = pd.DataFrame({
    "X": [1, 2, 2, 3, 3, 4, 7, 8, 8, 9, 9, 10, 4, 5, 5, 6, 6, 7],
    "Y": [2, 1, 3, 2, 4, 3, 7, 6, 8, 7, 9, 8, 10, 9, 11, 10, 12, 11],
    "Grupo": ["A"] * 6 + ["B"] * 6 + ["C"] * 6
})
colores = {"A": "steelblue", "B": "darkorange", "C": "seagreen"}

# pandas
datos2.plot(
    x="X",
    y="Y",
    kind="scatter",
    c=datos2["Grupo"].map(colores),
    title="Agrupación de observaciones",
    xlabel="Variable X",
    ylabel="Variable Y",
    figsize=(7, 5),
    legend=False
)

# matplotlib
plt.figure(figsize=(7, 5))

for grupo, color in colores.items():
    subconjunto = datos2[datos2["Grupo"] == grupo]
    plt.scatter(subconjunto["X"], subconjunto["Y"], color=color, label=grupo)

plt.title("Agrupación de observaciones")
plt.xlabel("Variable X")
plt.ylabel("Variable Y")
plt.legend(title="Grupo")
plt.tight_layout()

## 3. Jerarquía visual: destacar una categoría por una razón explícita

# Definición de datos
datos3 = pd.DataFrame({
    "Herramienta": ["Plataforma virtual", "Correo institucional",
                    "Biblioteca digital", "Herramientas colaborativas",
                    "Tutorías virtuales"],
    "Porcentaje": [92, 87, 74, 68, 51]
}).sort_values("Porcentaje", ascending=True)

# pandas
datos3.plot(
    x="Herramienta",
    y="Porcentaje",
    kind="barh",
    color=["steelblue", "steelblue", "steelblue", "steelblue", "darkorange"],
    legend=False,
    title="Uso de herramientas digitales",
    xlabel="Estudiantes (%)",
    xlim=(0, 100),
    figsize=(9, 5.5)
)

# matplotlib
colores3 = ["steelblue", "steelblue", "steelblue", "steelblue", "darkorange"]

plt.figure(figsize=(9, 5.5))
plt.barh(datos3["Herramienta"], datos3["Porcentaje"], color=colores3)

plt.title("Uso de herramientas digitales")
plt.xlabel("Estudiantes (%)")
plt.xlim(0, 100)
plt.tight_layout()

## 4. Teoría del color: paleta cualitativa, secuencial y divergente

# Definición de datos
datos4 = pd.DataFrame({
    "Facultad": ["Ingeniería", "Economía", "Derecho",
                 "Medicina", "Ciencias"],
    "Programa A": [35, 25, 20, 30, 40],
    "Programa B": [25, 35, 30, 20, 25],
    "Programa C": [40, 40, 50, 50, 35]
})
datos4["Diferencia"] = datos4["Programa A"] - datos4["Programa A"].mean()

# Paleta cualitativa, pandas
datos4.set_index("Facultad").plot(
    kind="bar",
    color=["steelblue", "darkorange", "seagreen"],
    title="Distribución de estudiantes por programa",
    ylabel="Participación (%)",
    figsize=(9, 5.5)
)

# Paleta cualitativa, matplotlib
x = np.arange(len(datos4))
ancho = 0.25

plt.figure(figsize=(9, 5.5))

for i, (programa, color) in enumerate(zip(
    ["Programa A", "Programa B", "Programa C"],
    ["steelblue", "darkorange", "seagreen"]
)):
    plt.bar(x + (i - 1) * ancho, datos4[programa],
            width=ancho, label=programa, color=color)

plt.xticks(x, datos4["Facultad"])
plt.title("Distribución de estudiantes por programa")
plt.ylabel("Participación (%)")
plt.legend()
plt.tight_layout()

# Paleta secuencial, pandas
datos4_ordenados = datos4.sort_values("Programa A")

datos4_ordenados.plot(
    x="Facultad",
    y="Programa A",
    kind="bar",
    color=plt.cm.Blues(datos4_ordenados["Programa A"] / datos4_ordenados["Programa A"].max()),
    title="Participación del Programa A por facultad",
    ylabel="Participación (%)",
    legend=False,
    figsize=(9, 5.5)
)

# Paleta secuencial, matplotlib
plt.figure(figsize=(9, 5.5))

plt.bar(
    datos4_ordenados["Facultad"],
    datos4_ordenados["Programa A"],
    color=plt.cm.Blues(
        datos4_ordenados["Programa A"] / datos4_ordenados["Programa A"].max()
    )
)

plt.title("Participación del Programa A por facultad")
plt.ylabel("Participación (%)")
plt.tight_layout()

# Paleta divergente, pandas
datos4.plot(
    x="Facultad",
    y="Diferencia",
    kind="bar",
    color=datos4["Diferencia"].map(
        lambda x: "steelblue" if x >= 0 else "darkorange"
    ),
    title="Diferencia frente al promedio",
    ylabel="Diferencia (puntos porcentuales)",
    legend=False,
    figsize=(9, 5.5)
)

# Paleta divergente, matplotlib
colores = ["steelblue" if x >= 0 else "darkorange"
           for x in datos4["Diferencia"]]

plt.figure(figsize=(9, 5.5))

plt.bar(datos4["Facultad"], datos4["Diferencia"], color=colores)
plt.axhline(0, color="black", linewidth=0.8)

plt.title("Diferencia frente al promedio")
plt.ylabel("Diferencia (puntos porcentuales)")
plt.tight_layout()
