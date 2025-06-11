import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import math
import os

def limpiar_coordenadas(geo):
    """
    Limpia la coordenada GEO eliminando espacios
    Convierte a formato flotante
    """
    try:
        # Eliminar espacios y separar
        coords = str(geo).replace(' ', '').split(',')
        return [float(coords[0]), float(coords[1])]
    except Exception as e:
        st.error(f"Error limpiando coordenada {geo}: {e}")
        return None

def calcular_distancia(coord1, coord2):
    """Calcular distancia en kilómetros entre dos coordenadas"""
    try:
        # Desempaquetar coordenadas
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Fórmula de haversine
        R = 6371  # Radio de la Tierra en km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat/2)**2 + 
             math.cos(math.radians(lat1)) * 
             math.cos(math.radians(lat2)) * 
             math.sin(dlon/2)**2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        
        return R * c
    except Exception as e:
        st.error(f"Error en cálculo de distancia: {e}")
        return np.nan

def main():
    st.title('🗺️ Buscador de Rutas Cercanas')
    st.subheader('v 11/06/2025')
    
    ruta_archivo = 'GEOS.xlsx'
    
    try:
        # Leer el archivo
        df = pd.read_excel(ruta_archivo)
        
        # Verificar columnas necesarias
        columnas_requeridas = ['GEO', 'Nombre de Ruta', 'Status SN', 'Dias visita']
        columnas_opcionales = ['Vendedor', 'Supervisor']
        
        # Verificar que existan las columnas requeridas
        for col in columnas_requeridas:
            if col not in df.columns:
                st.error(f"Columna requerida '{col}' no encontrada")
                st.write("Columnas disponibles:", df.columns.tolist())
                st.stop()
        
        # Añadir columnas opcionales si no existen
        for col in columnas_opcionales:
            if col not in df.columns:
                df[col] = 'No disponible'
                st.warning(f"Columna '{col}' no encontrada, usando valor por defecto")
        
        # Limpiar coordenadas GEO
        df['Coordenadas_Limpias'] = df['GEO'].apply(limpiar_coordenadas)
        
        # Eliminar filas con coordenadas inválidas
        df = df.dropna(subset=['Coordenadas_Limpias'])
        
        # Columnas para mostrar (ahora sabemos que existen)
        columnas_mostrar = [
            'GEO', 'Nombre de Ruta', 'Vendedor', 
            'Supervisor', 'Status SN', 'Dias visita'
        ]
        
        # Resto del código igual...
        # Input de coordenadas
        col1, col2 = st.columns(2)
        with col1:
            latitud = st.text_input('Latitud', '-17.8572415')
        with col2:
            longitud = st.text_input('Longitud', '-63.1895311')
        
        # Coordenada objetivo
        punto_objetivo = [float(latitud), float(longitud)]
        
        # Calcular distancias
        df['Distancia'] = df['Coordenadas_Limpias'].apply(
            lambda x: calcular_distancia(punto_objetivo, x) if x is not None else np.nan
        )
        
        # Ordenar por distancia y mostrar los 5 más cercanos
        cercanos = df.dropna(subset=['Distancia']).sort_values('Distancia').head(5)
        
        # Mostrar resultados
        st.dataframe(cercanos[columnas_mostrar + ['Distancia']])
        
        # Resto del código del mapa igual...
        
    except Exception as e:
        st.error(f"Error procesando datos: {e}")
        # Mostrar más información del error
        import traceback
        st.error(traceback.format_exc())
        
if __name__ == "__main__":
    main()
