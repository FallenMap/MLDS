#Librerias
import pandas as pd
import warnings
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
warnings.filterwarnings('ignore')

###################################################### Carga Inicial de los DataFrame
df_natalidad = pd.read_csv("https://github.com/FallenMap/MLDS/raw/master/obs_tnatalidad_2023.csv", delimiter=';', encoding='latin-1')
df_localidades = pd.read_csv("https://raw.githubusercontent.com/FallenMap/MLDS/master/indicadores-por-localidades-de-bogota-1999-2015.csv", delimiter=';')


#Filtrado de datos necesarios dataframe Natalidad
#Columnas a tener en cuenta:
cols_natalidad = ['AÑO','LOCALIDAD_MADRE','EDAD_MADRE','SEXO','TIPO_PARTO','MIGRANTE','TIEMPO_GESTACION',
                  'PERTENENCIA_ETNICA','REGIMEN_SEGURIDAD','NOM_ADMINISTRADORA','TOTAL NACIDOS VIVOS','POBLACION']

#Filtrado de información
df_natalidad = df_natalidad[cols_natalidad]


#Filtrado de datos necesarios dataframe Localidad

#Columnas a tener en cuenta:
cols_localidades = ['Año','Localidad' ,'Viviendas gestionadas por localidad (VIP, VIS, NO VIS)','Población en edad escolar de 5 a 16 años por localidades',
        'Población bajo la línea de pobreza Bogotá Multipropósito','Ocupaciones ilegales identificadas','Tasa global de cobertura bruta en educación',
        'Tasa de desempleo Jefes de hogar Multipropósito', 'Geometry', 'geo_point_2d']

#Filtrado de información
df_localidades = df_localidades[cols_localidades]

# Se toman en cuenta solo los años desde 2010 en adelante para el dataset de localidad (Ambos dataset inician desde el mismo año)
df_localidades = df_localidades[df_localidades["Año"] >= 2010]


# Informaciónde datasets
# print(df_natalidad.info())
# print(df_localidades.info())


###################################################### Relleno de datos localidad
# Se asume mismo número de viviendas gestionadas por localidad a lo largo de los años (Se toma la media)
df_localidades['Viviendas gestionadas por localidad (VIP, VIS, NO VIS)'] = df_localidades.groupby('Localidad')['Viviendas gestionadas por localidad (VIP, VIS, NO VIS)'].transform('mean')

# Se asume misma población por localidad a lo largo de los años (Se toma la media)
df_localidades['Población bajo la línea de pobreza Bogotá Multipropósito'] = df_localidades.groupby('Localidad')['Población bajo la línea de pobreza Bogotá Multipropósito'].transform('mean')

# Se asume misma tasa de desempleo por localidad a lo largo de los años (Se toma la media)
df_localidades['Tasa de desempleo Jefes de hogar Multipropósito'] = df_localidades.groupby('Localidad')['Tasa de desempleo Jefes de hogar Multipropósito'].transform('mean')

# Calculo de promedios (media)
promedio_poblacion = df_localidades['Población bajo la línea de pobreza Bogotá Multipropósito'].mean()
promedio_desempleo = df_localidades['Tasa de desempleo Jefes de hogar Multipropósito'].mean()

# Relleno de información
df_localidades.loc[df_localidades['Localidad'] == 'Sumapaz', 'Población bajo la línea de pobreza Bogotá Multipropósito'] = promedio_poblacion
df_localidades.loc[df_localidades['Localidad'] == 'Sumapaz', 'Tasa de desempleo Jefes de hogar Multipropósito'] = promedio_desempleo

# Información de dataset localidad
# print(df_localidades.loc[df_localidades['Localidad'] == "Sumapaz", ['Tasa de desempleo Jefes de hogar Multipropósito', 'Población bajo la línea de pobreza Bogotá Multipropósito']])

# Exportar df localidad limpio
df_localidades.to_excel("localidades_limpio.xlsx", index = False)

###################################################### Relleno de datos natalidad
# Función para rellenar datos faltantes de población
def fill_poblacion(row):
    if pd.isna(row['POBLACION']):
        localidad = row['LOCALIDAD_MADRE']
        año = row['AÑO']
        return poblacion_media_la[(poblacion_media_la['LOCALIDAD_MADRE'] == localidad) & (poblacion_media_la['AÑO'] == año)]['POBLACION'].values
    return row['POBLACION']

# Rellenar datos faltantes con "Sin información" excepto en población
faltantes_natalidad = [ "EDAD_MADRE", "MIGRANTE", "TIEMPO_GESTACION", "NOM_ADMINISTRADORA"]
df_natalidad[faltantes_natalidad] = df_natalidad[faltantes_natalidad].fillna("SIN INFORMACION")

# Población media por localidad y año
poblacion_media_la = df_natalidad.groupby(['LOCALIDAD_MADRE', 'AÑO'])['POBLACION'].mean().reset_index()

# Aplicar la función para rellenar datos faltantes en POBLACION
df_natalidad['POBLACION'] = df_natalidad.apply(fill_poblacion, axis=1)

# Reemplaza todas las cadenas que contienen "Sin información" con "SIN INFORMACION"
df_natalidad['MIGRANTE'] = np.where((df_natalidad['MIGRANTE'].str.contains('Sin información', case=False, na=False)) |
                                    (df_natalidad['MIGRANTE'] == 'NACIDO VIVO|6970885'),
                                    'SIN INFORMACION',
                                    df_natalidad['MIGRANTE'])

# Reemplaza "Sin información" por "SIN INFORMACION" en la columna "TIEMPO_GESTACION"
df_natalidad['TIEMPO_GESTACION'] = df_natalidad['TIEMPO_GESTACION'].replace('Sin información', 'SIN INFORMACION', regex=True)

# Pone un 0 en la población de localidades desconocidas
df_natalidad.loc[df_natalidad['LOCALIDAD_MADRE'] == 'Localidad Desconocida', 'POBLACION'] = 0

# Exportar df natalidad limpio
df_natalidad.to_excel("natalidad_limpio.xlsx", index = False)