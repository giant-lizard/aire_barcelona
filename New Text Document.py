import pandas as pd
import glob

# PASO 1: Cargar diccionarios
print("Cargando diccionarios...")
contaminantes = pd.read_csv('qualitat_aire_contaminants.csv')
estaciones = pd.read_csv('2025_qualitat_aire_estacions.csv')

# PASO 2: Cargar TODOS los archivos mensuales
print("Buscando archivos mensuales...")
archivos = glob.glob('*_qualitat_aire_BCN.csv')
print(f"Encontrados {len(archivos)} archivos")

# PASO 3: Procesar cada archivo
datos_limpios = []

for archivo in archivos:
    print(f"Procesando {archivo}...")
    
    try:
        # Leer archivo
        df = pd.read_csv(archivo)
        
        # Ver qué columnas tiene este archivo
        print(f"  Columnas encontradas: {list(df.columns[:10])}...")  # Mostrar primeras 10
        
        # Identificar columnas de horas (pueden ser H01 o V01_H01 o similar)
        columnas_horas = [col for col in df.columns if 'H' in col and col not in ['MUNICIPI', 'PROVINCIA']]
        
        # Quedarnos solo con columnas importantes
        columnas_id = ['ESTACIO', 'CODI_CONTAMINANT', 'ANY', 'MES', 'DIA']
        
        # Verificar que existen todas las columnas ID
        columnas_id_disponibles = [col for col in columnas_id if col in df.columns]
        
        if len(columnas_id_disponibles) < 5:
            print(f"  ⚠️  Saltando {archivo}, faltan columnas importantes")
            continue
        
        df_filtrado = df[columnas_id_disponibles + columnas_horas]
        
        # Transformar formato ancho → largo (MELT)
        df_largo = pd.melt(
            df_filtrado,
            id_vars=columnas_id_disponibles,
            value_vars=columnas_horas,
            var_name='hora_raw',
            value_name='valor'
        )
        
        # Extraer el número de hora (funciona para H01, V01_H01, etc.)
        df_largo['hora'] = df_largo['hora_raw'].str.extract(r'H(\d+)')[0].astype(int)
        
        # Crear fecha completa
        df_largo['fecha'] = pd.to_datetime(
            df_largo[['ANY', 'MES', 'DIA']].rename(columns={'ANY': 'year', 'MES': 'month', 'DIA': 'day'})
        )
        
        datos_limpios.append(df_largo)
        print(f"  ✅ Procesado correctamente")
        
    except Exception as e:
        print(f"  ❌ Error en {archivo}: {str(e)}")
        continue

# PASO 4: Juntar todo
print("\nJuntando todos los meses...")
df_final = pd.concat(datos_limpios, ignore_index=True)

# PASO 5: Añadir nombres de contaminantes
print("Añadiendo nombres de contaminantes...")
df_final = df_final.merge(
    contaminantes[['Codi_Contaminant', 'Desc_Contaminant']],
    left_on='CODI_CONTAMINANT',
    right_on='Codi_Contaminant',
    how='left'
)

# PASO 6: Añadir coordenadas de estaciones
print("Añadiendo coordenadas...")
df_final = df_final.merge(
    estaciones[['Estacio', 'Latitud', 'Longitud', 'nom_cabina']].drop_duplicates(),
    left_on='ESTACIO',
    right_on='Estacio',
    how='left'
)

# PASO 7: Limpiar valores nulos
print("Limpiando valores nulos...")
df_final = df_final.dropna(subset=['valor'])

# PASO 8: Quedarnos solo con columnas necesarias
df_final = df_final[[
    'fecha', 'hora', 'ESTACIO', 'nom_cabina', 
    'CODI_CONTAMINANT', 'Desc_Contaminant', 
    'valor', 'Latitud', 'Longitud'
]]

# Renombrar para que sea más claro
df_final.columns = [
    'fecha', 'hora', 'codigo_estacion', 'nombre_estacion',
    'codigo_contaminante', 'contaminante',
    'concentracion', 'latitud', 'longitud'
]

# PASO 9: Guardar
print("\nGuardando archivo final...")
df_final.to_csv('datos_calidad_aire_limpios.csv', index=False)

print(f"\n✅ LISTO! Se generó 'datos_calidad_aire_limpios.csv'")
print(f"Total de filas: {len(df_final):,}")
print(f"Rango de fechas: {df_final['fecha'].min()} a {df_final['fecha'].max()}")