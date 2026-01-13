import pandas as pd

print("Cargando datos meteorológicos...")
df_meteo = pd.read_csv('Dades_meteorològiques_diàries_de_la_XEMA_20260111.csv')

# PASO 1: Filtrar solo las variables que nos interesan
print("Filtrando variables relevantes...")
variables_interes = [
    'Precipitació acumulada diària',
    'Velocitat mitjana diària del vent 10 m (esc.)'
]

df_meteo_filtrado = df_meteo[df_meteo['NOM_VARIABLE'].isin(variables_interes)]

# PASO 2: Limpiar la columna VALOR (tiene comas en vez de puntos)
df_meteo_filtrado['VALOR'] = df_meteo_filtrado['VALOR'].str.replace(',', '.').astype(float)

# PASO 3: Convertir fecha al mismo formato que tu dataset de calidad del aire
df_meteo_filtrado['fecha'] = pd.to_datetime(df_meteo_filtrado['DATA_LECTURA'], format='%d/%m/%Y')

# PASO 4: Pivotar para tener precipitación y viento como columnas
df_meteo_pivotado = df_meteo_filtrado.pivot_table(
    index='fecha',
    columns='NOM_VARIABLE',
    values='VALOR',
    aggfunc='mean'
).reset_index()

# Renombrar columnas más simple
df_meteo_pivotado.columns = ['fecha', 'precipitacion_mm', 'viento_ms']

# PASO 5: Cargar tu dataset de calidad del aire
print("Cargando datos de calidad del aire...")
df_aire = pd.read_csv('datos_con_AQI.csv')

# Convertir fecha a datetime
df_aire['fecha'] = pd.to_datetime(df_aire['fecha'])

# PASO 6: Unir ambos datasets por fecha
print("Uniendo datasets...")
df_completo = df_aire.merge(
    df_meteo_pivotado,
    on='fecha',
    how='left'  # left join: mantiene todas las filas de calidad del aire
)

# PASO 7: Guardar
print("Guardando archivo final...")
df_completo.to_csv('datos_completos_con_meteo.csv', index=False)

print(f"\n✅ LISTO! Se generó 'datos_completos_con_meteo.csv'")
print(f"Total de filas: {len(df_completo):,}")
print(f"\nColumnas añadidas:")
print(f"  - precipitacion_mm: Lluvia diaria en milímetros")
print(f"  - viento_ms: Velocidad del viento en metros/segundo")

# Estadísticas
print(f"\nEstadísticas meteorológicas:")
print(f"  Precipitación promedio: {df_completo['precipitacion_mm'].mean():.2f} mm/día")
print(f"  Viento promedio: {df_completo['viento_ms'].mean():.2f} m/s")
print(f"  Días con lluvia (>0mm): {(df_completo['precipitacion_mm'] > 0).sum():,}")
print(f"  Días sin datos meteo: {df_completo['precipitacion_mm'].isna().sum():,}")