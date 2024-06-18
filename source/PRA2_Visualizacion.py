#!/usr/bin/env python
# coding: utf-8


# Cargamos las librerías
import pandas as pd
import os
import re

# Creamos un directorio si no existe para guardar los csv que creamos
# Obtenemos el directorio actual donde está el notebook
nombre_dir = 'data'
directorio_actual = os.getcwd()
ruta = os.path.join(directorio_actual, nombre_dir)

# Comprobamos si existe o no el directorio
if not os.path.exists(ruta):
    os.makedirs(ruta)
    print(f"Directorio creado para guardar los csv.")
else:
    print(f"El directorio para guardar los csv ya existe.")

# Cargamos los datos
data = pd.read_csv('data/roda_pra1_visualizacion.csv', delimiter=',', decimal='.')
data = data.fillna(0)

# Creamos variables Renewable Consumption y Non Renewable Consumption
data['Renewable Consumption'] = data['solar_consumption'] + data['wind_consumption'] + data['hydro_consumption'] + data['nuclear_consumption']
data['Non Renewable Consumption'] = data['coal_consumption'] + data['oil_consumption'] + data['gas_consumption'] + data['fossil_fuel_consumption']

# Excluimos la Antártida de los datos
data = data[data['continent'] != 'Antarctica']

# Cambiamos el nombre de algunos paises
data['country'] = data['country'].replace({
    'United States': 'USA',
    'United Kingdom': 'UK',
    'South Korea': 'S. Korea'
})

# Filtramos los datos apartir de 1965
data = data[data['year'] >= 1965]

# La función rename_columns para renombrar las columnas:
# Reemplaza los guiones bajos (_) por espacios
# Convierte todo el texto a minúsculas
# Luego capitaliza solo la primera letra de la cadena

def rename_columns(col):
    if isinstance(col, int):  # Verificar si la columna es un número
        return str(col)
    col = col.replace('_', ' ').lower()
    # Reemplazar 'co2' y 'gdp' por sus versiones en mayúsculas
    col = re.sub(r'\bco2\b', 'CO2', col, flags=re.IGNORECASE)
    col = re.sub(r'\bgdp\b', 'GDP', col, flags=re.IGNORECASE)
    return col[0].upper() + col[1:]


#Pregunta 1: Consumo de combustibles fósiles y emisiones de CO2
# 
# Objetivo:
# Evaluar cómo ha evolucionado el consumo de combustibles fósiles  y su impacto en las emisiones de CO2.

# Pregunta 1
# Selecccionamos los datos relevantes 
df_fuel_emissions = data[['year','continent','country', 'population','coal_consumption', 'co2', 'oil_consumption', 'gas_consumption']]

df_fuel_emissions = df_fuel_emissions.groupby(['year']).agg({
    'co2': 'sum',
    'coal_consumption': 'sum',
    'oil_consumption': 'sum',
    'gas_consumption': 'sum'
}).reset_index()

# Redondeamos los valores a 2 decimales
df_fuel_emissions  = df_fuel_emissions .round(2)

# Estandarizamos los nombres de las columnas
df_fuel_emissions.columns = [rename_columns(col) for col in df_fuel_emissions.columns]

# Guardamos los datos procesados para Flourish en un csv
df_fuel_emissions.to_csv('data/pregunta1.csv', index=False)


# Pregunta 2: Impacto ambiental de los combustibles
# 
# Objetivo:
# Analizar cómo se relacionan las emisiones de CO2 con el consumo de diferentes tipos de combustibles.

# Pregunta 2
# Selecccionamos los datos relevantes 
df_fuel_emissions = data[['year','continent','country', 'population','coal_consumption', 'co2', 'oil_consumption', 'gas_consumption', 'biofuel_consumption']]

df_fuel_emissions = df_fuel_emissions.groupby(['year', 'continent','country']).agg({
    'co2': 'sum',
    'coal_consumption': 'sum',
    'oil_consumption': 'sum',
    'gas_consumption': 'sum',
    'biofuel_consumption': 'sum'
}).reset_index()

# Transformamos los datos
df_fuel_emissions = df_fuel_emissions.melt(id_vars=['year', 'continent', 'country', 'co2'],
                    value_vars=['coal_consumption', 'oil_consumption', 'gas_consumption', 'biofuel_consumption'],
                    var_name='fuel',
                    value_name='fuel_quantity')

# Quitamos el sufijo '_consumption' en la columna 'fuel'
df_fuel_emissions['fuel'] = df_fuel_emissions['fuel'].str.replace('_consumption', '')

# Eliminamos las filas donde 'co2' o 'fuel_quantity' sean iguales a 0
df_fuel_emissions = df_fuel_emissions[(df_fuel_emissions['co2'] != 0) & (df_fuel_emissions['fuel_quantity'] != 0)]

# Estandarizamos los nombres de las columnas
df_fuel_emissions.columns = [rename_columns(col) for col in df_fuel_emissions.columns]

# Guardamos los datos procesados para Flourish en un csv
df_fuel_emissions.to_csv('data/pregunta2.csv', index=False)


# Pregunta 3: Transición energética
# 
# Objetivo:
# Analizar cómo ha evolucionado el consumo de energías renovables en comparación con las no renovables globalmente y por continente durante los últimos 20 años.

# Pregunta 3
# Filtramos los datos desde el año 2000
data_recent = data[data['year'] >= 2000].copy()

# Agrupamos por año y continente
df_energy = data_recent.groupby(['year', 'continent']).agg({
    'Renewable Consumption': 'sum',
    'Non Renewable Consumption': 'sum'
}).reset_index()

# Ordenamos el dataframe final por año 
df_energy = df_energy.sort_values('year')

# Estandarizamos los nombres de las columnas
df_energy.columns = [rename_columns(col) for col in df_energy.columns]

# Pivotamos los datos de consumo renovable y no renovable por país y año
renewable_df = data.pivot_table(values='Renewable Consumption', index='year', columns='continent', fill_value=0).reset_index()
non_renewable_df = data.pivot_table(values='Non Renewable Consumption', index='year', columns='continent', fill_value=0).reset_index()

# Guardamos los datos procesados para Flourish en un csv
renewable_df.to_csv('data/pregunta3_renovables.csv', index=False)
non_renewable_df.to_csv('data/pregunta3_no_renovables.csv', index=False)

# Pregunta 4: Desarrollo sostenible
# 
# Objetivo:
# Evaluar la correlación entre el aumento del PIB y los cambios en el consumo de energía per cápita en diferentes países.

# Pregunta 4
# Seleccionamos los datos relevantes
df_gdp_energy = data[['year', 'continent', 'country', 'gdp', 'energy_per_capita', 'population']]

# Eliminamos las filas donde 'gdp' o 'energy_per_capita' sean iguales a 0
df_gdp_energy = df_gdp_energy[(df_gdp_energy['gdp'] != 0) & (df_gdp_energy['energy_per_capita'] != 0)]

# Ordenamos los datos por la columna 'year'
df_gdp_energy = df_gdp_energy.sort_values(by='year')

# Estandarizamos los nombres de las columnas
df_gdp_energy.columns = [rename_columns(col) for col in df_gdp_energy.columns]

# Guardamos los datos procesados para Flourish en un csv
df_gdp_energy.to_csv('data/pregunta4.csv', index=False, decimal='.')


# Pregunta 5: Evolución consumo renovables y no renovables
# 
# Objetivo: Identificar qué países lideran el consumo de energía renovable y no renovable

# Pregunta 5
# Cargamos el csv con las banderas
flags = pd.read_csv('data/banderas.csv', delimiter=';')

# Pivotamos los datos de consumo renovable y no renovable por país y año
renewable_df = data.pivot_table(values='Renewable Consumption', index=['country', 'continent'], columns='year', fill_value=0).reset_index()
non_renewable_df = data.pivot_table(values='Non Renewable Consumption', index=['country', 'continent'], columns='year', fill_value=0).reset_index()

# Fusionamos la información de las banderas con los dataframes de consumo energético correspondiente
renewable_with_flags = pd.merge(renewable_df, flags, on='country', how='left')
non_renewable_with_flags = pd.merge(non_renewable_df, flags, on='country', how='left')

# Estandarizamos los nombres de las columnas
non_renewable_with_flags.columns = [rename_columns(col) for col in non_renewable_with_flags.columns]
renewable_with_flags.columns = [rename_columns(col) for col in renewable_with_flags.columns]

# Guardamos los datos procesados para Flourish en un csv
renewable_with_flags.to_csv('data/pregunta5_top_consumo_renovables.csv', index=False)
non_renewable_with_flags.to_csv('data/pregunta5_top_consumo_no_renovables.csv', index=False)


# Pregunta 6: Liderazgo en renovables
# 
# Objetivo:
# Identificar qué países han mostrado las mayores tasas de cambio en la producción y consumo de energías renovables (solar y eólica).

# Pregunta 6
# Calculamos la tasa de cambio en la producción de energía solar y eólica

# Cargamos el csv con las banderas
flags = pd.read_csv('data/banderas.csv', delimiter=';') 

# Filtramos los datos relevantes y selecccionamos los datos a partir del año 2000 
df_wind_solar = data.loc[data['year'] >= 2000, ['year', 'continent', 'country', 'solar_electricity', 'wind_electricity','solar_consumption','wind_consumption']].copy()

# Calculamos el total de energía solar + eólica generada
df_wind_solar['generated_solar_wind'] = df_wind_solar['solar_electricity'] + df_wind_solar['wind_electricity']

# Calculamos el total de energía solar + eólica consumida
df_wind_solar['consumption_solar_wind'] = df_wind_solar['solar_consumption'] + df_wind_solar['wind_consumption']

# Pivotamos los datos para obtener la estructura deseada
generated_df = df_wind_solar.pivot_table(values='generated_solar_wind', index=['country', 'continent'], columns='year', fill_value=0).reset_index()
consumption_df = df_wind_solar.pivot_table(values='consumption_solar_wind', index=['country', 'continent'], columns='year', fill_value=0).reset_index()

# Fusionamos la información de las banderas con los dataframes
generated_with_flags = pd.merge(generated_df, flags, on='country', how='left')
consumption_with_flags = pd.merge(consumption_df, flags, on='country', how='left')

# Estandarizamos los nombres de las columnas
generated_with_flags.columns = [rename_columns(col) for col in generated_with_flags.columns]
consumption_with_flags.columns = [rename_columns(col) for col in consumption_with_flags.columns]


# Guardamos los datos procesados para Flourish en un csv
generated_with_flags.to_csv('data/pregunta6_generado.csv', index=False)
consumption_with_flags.to_csv('data/pregunta6_consumido.csv', index=False)

print("Ejecución terminada")
