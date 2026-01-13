import pandas as pd
import numpy as np

df = pd.read_csv('datos_calidad_aire_limpios.csv')

def calcular_aqi_individual(row):
    """Calcula AQI para cada contaminante individualmente"""
    contaminante = str(row['contaminante']).strip()  # Limpiar espacios
    valor = row['concentracion']
    
    if pd.isna(valor) or valor <= 0:
        return np.nan
    
    # AQI para NO2 (incluye NO2 y NO2*)
    if 'NO2' in contaminante:
        if valor <= 40:
            return (valor / 40) * 50
        elif valor <= 90:
            return 50 + ((valor - 40) / 50) * 50
        elif valor <= 120:
            return 100 + ((valor - 90) / 30) * 50
        elif valor <= 230:
            return 150 + ((valor - 120) / 110) * 50
        else:
            return 200 + ((valor - 230) / 170) * 100
    
    # AQI para PM10 (incluye PM10 y PM10*)
    elif 'PM10' in contaminante and 'PM2.5' not in contaminante:
        if valor <= 25:
            return (valor / 25) * 50
        elif valor <= 50:
            return 50 + ((valor - 25) / 25) * 50
        elif valor <= 90:
            return 100 + ((valor - 50) / 40) * 50
        elif valor <= 180:
            return 150 + ((valor - 90) / 90) * 50
        else:
            return 200 + ((valor - 180) / 120) * 100
    
    # AQI para O3 (incluye O3 y O3*)
    elif 'O3' in contaminante:
        if valor <= 100:
            return (valor / 100) * 50
        elif valor <= 140:
            return 50 + ((valor - 100) / 40) * 50
        elif valor <= 180:
            return 100 + ((valor - 140) / 40) * 50
        elif valor <= 240:
            return 150 + ((valor - 180) / 60) * 50
        else:
            return 200 + ((valor - 240) / 160) * 100
    
    # AQI para PM2.5 (incluye PM2.5 y PM2.5*)
    elif 'PM2.5' in contaminante:
        if valor <= 15:
            return (valor / 15) * 50
        elif valor <= 30:
            return 50 + ((valor - 15) / 15) * 50
        elif valor <= 55:
            return 100 + ((valor - 30) / 25) * 50
        elif valor <= 110:
            return 150 + ((valor - 55) / 55) * 50
        else:
            return 200 + ((valor - 110) / 90) * 100
    
    else:
        return np.nan

print("Calculando AQI individual...")
df['AQI_individual'] = df.apply(calcular_aqi_individual, axis=1)

# Filtrar solo contaminantes con AQI calculado
df_filtrado = df[df['AQI_individual'].notna()]

print("\nContaminantes con AQI calculado:")
print(df_filtrado.groupby('contaminante')['AQI_individual'].agg(['count', 'mean', 'min', 'max']))

df_filtrado.to_csv('datos_con_aqi_individual_corregido.csv', index=False)
print("\n✅ Archivo guardado: datos_con_aqi_individual_corregido.csv")