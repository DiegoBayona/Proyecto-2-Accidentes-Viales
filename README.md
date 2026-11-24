# Accidentes viales en Bogotá: gravedad, causas y características de las vías

Proyecto 2 del curso **Aplicaciones en Ciencia de Datos (DATA-1002)** de la Universidad de los Andes.

Nuestro objetivo es explorar cómo se relacionan la gravedad de los siniestros viales con las causas registradas y las características de las vías en Bogotá, considerando la localidad y la franja horaria. El análisis busca apoyar una decisión práctica: dónde y cuándo conviene priorizar inspecciones de seguridad vial.

El proyecto incluye:

- Integración y preparación de datos con `pandas`.
- Resúmenes reproducibles y gráficos con `pandas` y `matplotlib`.
- Un dashboard interactivo construido con `streamlit` y `plotly`.
- Un informe académico con hallazgos, limitaciones y recomendaciones.

## Integrantes

- Diego Bayona
- Sebastian Barragan
- Julian Ruiz
- Samuel Colmenares

## Pregunta analítica

> ¿Cómo se relacionan las características de las vías y las causas registradas con la gravedad de los siniestros viales en Bogotá, y cómo varían estos patrones según la localidad y la franja horaria para identificar prioridades de intervención en seguridad vial?

## Datos utilizados

Se utilizaron tres tablas del servicio oficial **Siniestralidad BD**, publicado por la Secretaría Distrital de Movilidad:

| Tabla | Contenido utilizado |
|---|---|
| `ACCIDENTE.csv` | Código del siniestro, fecha y hora, gravedad, localidad y clase de accidente. Es la tabla principal y define la unidad de análisis. |
| `VM_ACC_CAUSA.csv` | Código y nombre de las causas registradas para cada siniestro. |
| `VM_ACC_VIA.csv` | Características viales, como uso, calzadas, carriles, superficie, iluminación y semáforo. |

Fuente oficial:

- [Portal de datos abiertos de movilidad de Bogotá — Siniestralidad BD](https://datos.movilidadbogota.gov.co/maps/ea243e7de8e846c8bd27e47c08771d66/about)


## Metodología

1. Se cargaron solo las variables necesarias de las tres tablas principales.
2. Se normalizaron espacios y mayúsculas.
3. La hora se transformó en cuatro franjas: madrugada, mañana, tarde y noche.
4. Las causas se deduplicaron por siniestro y causa registrada.
5. Para el análisis vial se conservaron los registros marcados como vía principal.
6. Las causas y las características viales se integraron con `CODIGO_ACCIDENTE`.
7. Se calcularon frecuencias, conteos y proporciones por gravedad, localidad y franja.
8. Se verificó la cardinalidad de las relaciones y se documentaron los registros sin correspondencia.

### Interpretación de los resultados

Los valores representan **asociaciones entre siniestros registrados**, no tasas de riesgo ni probabilidades individuales. Un siniestro puede tener varias causas o varios registros de vía, por lo que las categorías no son excluyentes.

Además, no hay aforos, cantidad de viajes, velocidad observada ni datos de población expuesta. Por eso, los resultados no permiten atribuir causalidad ni estimar el riesgo de transitar por una vía.

## Principales hallazgos

La madrugada presenta la mayor proporción de siniestros con heridos o muertos y con muertos. Kennedy concentra el mayor número de siniestros, mientras que localidades como San Cristóbal, Usme, Rafael Uribe Uribe, Bosa y Ciudad Bolívar presentan las mayores proporciones graves entre las localidades con al menos 10.000 registros.

Entre las asociaciones causa-localidad-franja, el exceso de velocidad en Kennedy durante la noche tiene 452 casos graves de 549 asociaciones y 78 casos con muertos. Para la causa “cruzar sin observar”, el cruce Kennedy-noche muestra 951 casos graves de 954 asociaciones.

En vías principales, Kennedy de noche registra diferencias entre doble sentido y un sentido. En Usme de tarde también aparece una diferencia según el semáforo registrado. Estos resultados son descriptivos y deben verificarse en campo.

## Limitaciones

- La tabla vial cubre 493.675 siniestros, equivalentes al 54,39 % de `ACCIDENTE`.
- 307.038 códigos únicos de vía principal no aparecen en `ACCIDENTE`.
- La causa cubre el 97,35 % de los accidentes, aunque existen registros sin nombre válido.
- Los archivos contienen 1.286 registros anteriores a 2007, mientras que la ficha oficial declara cobertura desde ese año.
- 2026 es un año parcial.
- No hay diccionario completo para interpretar todas las categorías de geometría y visualización vial.
- No se dispone de datos de exposición al tránsito ni aforos.

El dashboard permite:

- Filtrar por localidad y franja horaria.
- Consultar el total de siniestros y los casos con heridos o muertos.
- Comparar gravedad por franja y localidad.
- Explorar causas registradas.
- Seleccionar una característica vial y comparar sus categorías.
- Ajustar los mínimos de observaciones para las comparaciones.

También muestra una nota visible sobre la cobertura vial y la ausencia de datos de exposición al tránsito.

## Informe

El informe académico se encuentra en:

- [docs/Proyecto2.docx](docs/Proyecto2.docx)

Y contiene: 

- Pregunta analítica.
- Procedencia y unidad de análisis.
- Integración y preparación de datos.
- Estrategia de análisis.
- Resultados descriptivos y visualizaciones.
- Limitaciones.
- Conclusiones y recomendaciones.
- Referencias.

## Recomendaciones derivadas

Como acción inicial, el proyecto propone:

- Priorizar inspecciones nocturnas y de madrugada en Kennedy.
- Revisar velocidad y cruces peatonales en Kennedy.
- Verificar en campo la semaforización reportada en Usme durante la tarde.
- Ampliar las verificaciones a San Cristóbal, Usme, Rafael Uribe Uribe, Bosa y Ciudad Bolívar.

Estas recomendaciones son prioridades de verificación. El análisis no demuestra que una obra o control específico tenga una eficacia causal.
