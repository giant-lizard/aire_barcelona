import pandas as pd
import numpy as np

print("Cargando datos limpios...")
df = pd.read_csv('datos_calidad_aire_limpios.csv')

# PASO 1: Pivotar para tener cada contaminante como columna
print("Pivotando datos...")
df_pivotado = df.pivot_table(
    index=['fecha', 'hora', 'codigo_estacion', 'nombre_estacion', 'latitud', 'longitud'],
    columns='contaminante',
    values='concentracion',
    aggfunc='mean'  # Por si hay duplicados
).reset_index()

# PASO 2: Calcular AQI simplificado
print("Calculando AQI...")

def calcular_aqi_simple(row):
    """
    Calcula AQI basado en EPA simplificado
    Toma el MÁXIMO de los AQI individuales
    """
    aqi_values = []
    
    # AQI para NO2 (µg/m³)
    if pd.notna(row.get('NO2', np.nan)):
        no2 = row['NO2']
        if no2 <= 40:
            aqi_no2 = (no2 / 40) * 50
        elif no2 <= 90:
            aqi_no2 = 50 + ((no2 - 40) / 50) * 50
        elif no2 <= 120:
            aqi_no2 = 100 + ((no2 - 90) / 30) * 50
        elif no2 <= 230:
            aqi_no2 = 150 + ((no2 - 120) / 110) * 50
        else:
            aqi_no2 = 200 + ((no2 - 230) / 170) * 100
        aqi_values.append(aqi_no2)
    
    # AQI para PM10 (µg/m³)
    if pd.notna(row.get('PM10', np.nan)):
        pm10 = row['PM10']
        if pm10 <= 25:
            aqi_pm10 = (pm10 / 25) * 50
        elif pm10 <= 50:
            aqi_pm10 = 50 + ((pm10 - 25) / 25) * 50
        elif pm10 <= 90:
            aqi_pm10 = 100 + ((pm10 - 50) / 40) * 50
        elif pm10 <= 180:
            aqi_pm10 = 150 + ((pm10 - 90) / 90) * 50
        else:
            aqi_pm10 = 200 + ((pm10 - 180) / 120) * 100
        aqi_values.append(aqi_pm10)
    
    # AQI para O3 (µg/m³)
    if pd.notna(row.get('O3', np.nan)):
        o3 = row['O3']
        if o3 <= 100:
            aqi_o3 = (o3 / 100) * 50
        elif o3 <= 140:
            aqi_o3 = 50 + ((o3 - 100) / 40) * 50
        elif o3 <= 180:
            aqi_o3 = 100 + ((o3 - 140) / 40) * 50
        elif o3 <= 240:
            aqi_o3 = 150 + ((o3 - 180) / 60) * 50
        else:
            aqi_o3 = 200 + ((o3 - 240) / 160) * 100
        aqi_values.append(aqi_o3)
    
    # El AQI final es el MÁXIMO (el peor contaminante domina)
    if aqi_values:
        return max(aqi_values)
    else:
        return np.nan

# Aplicar cálculo de AQI a cada fila
df_pivotado['AQI'] = df_pivotado.apply(calcular_aqi_simple, axis=1)

# PASO 3: Añadir categoría de AQI
def categoria_aqi(aqi):
    if pd.isna(aqi):
        return 'Sin datos'
    elif aqi <= 50:
        return 'Bueno'
    elif aqi <= 100:
        return 'Moderado'
    elif aqi <= 150:
        return 'No saludable (sensibles)'
    elif aqi <= 200:
        return 'No saludable'
    elif aqi <= 300:
        return 'Muy no saludable'
    else:
        return 'Peligroso'

df_pivotado['categoria_AQI'] = df_pivotado['AQI'].apply(categoria_aqi)

# PASO 4: Limpiar filas sin AQI
print("Limpiando filas sin AQI...")
df_pivotado = df_pivotado.dropna(subset=['AQI'])

# PASO 5: Guardar
print("Guardando archivo final...")
df_pivotado.to_csv('datos_con_AQI.csv', index=False)

print(f"\n✅ LISTO! Se generó 'datos_con_AQI.csv'")
print(f"Total de filas: {len(df_pivotado):,}")
print(f"\nDistribución de AQI:")
print(df_pivotado['categoria_AQI'].value_counts())
print(f"\nAQI promedio: {df_pivotado['AQI'].mean():.1f}")
print(f"AQI mínimo: {df_pivotado['AQI'].min():.1f}")
print(f"AQI máximo: {df_pivotado['AQI'].max():.1f}")