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
    
    # Usar ruta relativa para el archivo Excel
    ruta_archivo = 'GEOS.xlsx'
    
    try:
        # Leer el archivo
        df = pd.read_excel(ruta_archivo)
        
        # Limpiar coordenadas GEO
        df['Coordenadas_Limpias'] = df['GEO'].apply(limpiar_coordenadas)
        
        # Eliminar filas con coordenadas inválidas
        df = df.dropna(subset=['Coordenadas_Limpias'])
        
        # Columnas para mostrar
        columnas_mostrar = [
            'GEO', 'Nombre de Ruta', 'Nombre Vendedor', 'Supervisor', 'Status SN', 'Dias visita'
        ]
        
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
        st.subheader("🎯 5 Rutas Más Cercanas")
        st.dataframe(cercanos[columnas_mostrar + ['Distancia']])
        
        # Crear mapa
        m = folium.Map(location=[float(latitud), float(longitud)], zoom_start=10)
        
        # Marker para punto objetivo (rojo)
        folium.CircleMarker(
            location=[float(latitud), float(longitud)],
            radius=10,
            popup="📍 Punto de Referencia",
            color='red',
            fill=True,
            fillColor='red',
            fillOpacity=0.7
        ).add_to(m)
        
        # Agregar markers para las rutas cercanas
        colors = ['blue', 'green', 'purple', 'orange', 'darkred']
        for i, (_, row) in enumerate(cercanos.iterrows()):
            if row['Coordenadas_Limpias'] is not None:
                lat, lon = row['Coordenadas_Limpias']
                popup_text = f"""
                <b>{row['Nombre de Ruta']}</b><br>
                Vendedor: {row['Nombre Vendedor']}<br>
                Supervisor: {row['Supervisor']}<br>
                Distancia: {row['Distancia']:.2f} km<br>
                Status: {row['Status SN']}<br>
                Días: {row['Dias visita']}
                """
                
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=8,
                    popup=folium.Popup(popup_text, max_width=300),
                    color=colors[i % len(colors)],
                    fill=True,
                    fillColor=colors[i % len(colors)],
                    fillOpacity=0.6
                ).add_to(m)
        
        # Mostrar mapa
        st.subheader("🗺️ Mapa de Ubicaciones")
        folium_static(m)
        
        # Estadísticas adicionales
        st.subheader("📊 Estadísticas")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Rutas", len(df))
        with col2:
            st.metric("Ruta más Cercana", f"{cercanos.iloc[0]['Distancia']:.2f} km")
        with col3:
            st.metric("Promedio Distancia (Top 5)", f"{cercanos['Distancia'].mean():.2f} km")
            
    except FileNotFoundError:
        st.error("❌ No se encontró el archivo 'GEOS.xlsx'. Asegúrate de que esté en el directorio correcto.")
    except Exception as e:
        st.error(f"❌ Error procesando datos: {e}")

if __name__ == "__main__":
    main()
