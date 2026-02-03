"""
Módulo de Utilidades - Download e Processamento de Dados Topográficos
Inclui funções para obter dados via APIs (Mapbox, OpenTopography, etc.)
"""

import requests
import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
import json
import time

class ElevationAPIClient:
    """Cliente para APIs de elevação"""
    
    def __init__(self, mapbox_token: Optional[str] = None):
        self.mapbox_token = mapbox_token
        
    def get_elevation_mapbox(self, lat: float, lon: float) -> Optional[float]:
        """
        Obtém elevação de um ponto usando Mapbox Terrain API
        
        Parameters:
        -----------
        lat : float
            Latitude
        lon : float
            Longitude
            
        Returns:
        --------
        float or None
            Elevação em metros
        """
        
        if not self.mapbox_token:
            raise ValueError("Mapbox token não configurado")
        
        url = f"https://api.mapbox.com/v4/mapbox.mapbox-terrain-v2/tilequery/{lon},{lat}.json"
        
        params = {
            'layers': 'contour',
            'access_token': self.mapbox_token
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('features'):
                return data['features'][0]['properties'].get('ele')
            return None
            
        except requests.RequestException as e:
            print(f"Erro ao obter elevação: {e}")
            return None
    
    def get_elevation_batch_mapbox(self, coordinates: List[Tuple[float, float]], 
                                   batch_size: int = 100,
                                   delay: float = 0.1) -> pd.DataFrame:
        """
        Obtém elevação para múltiplos pontos com rate limiting
        
        Parameters:
        -----------
        coordinates : list of tuples
            Lista de (lat, lon)
        batch_size : int
            Tamanho do lote para processamento
        delay : float
            Delay entre requisições (segundos)
            
        Returns:
        --------
        pd.DataFrame
            DataFrame com lat, lon, elevation
        """
        
        results = []
        
        for i, (lat, lon) in enumerate(coordinates):
            elevation = self.get_elevation_mapbox(lat, lon)
            
            results.append({
                'lat': lat,
                'lon': lon,
                'elevation': elevation
            })
            
            # Rate limiting
            if (i + 1) % batch_size == 0:
                time.sleep(delay)
                print(f"Processados {i + 1}/{len(coordinates)} pontos...")
        
        return pd.DataFrame(results)
    
    def get_elevation_open_elevation(self, lat: float, lon: float) -> Optional[float]:
        """
        Obtém elevação usando Open-Elevation API (gratuita, sem token)
        
        Baseado em dados SRTM 30m
        """
        
        url = "https://api.open-elevation.com/api/v1/lookup"
        
        params = {
            'locations': f"{lat},{lon}"
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('results'):
                return data['results'][0]['elevation']
            return None
            
        except requests.RequestException as e:
            print(f"Erro ao obter elevação: {e}")
            return None

class TerrainAnalyzer:
    """Análise de terreno e classificação geomorfológica"""
    
    @staticmethod
    def classify_slope(slope: float) -> str:
        """
        Classifica declividade segundo EMBRAPA
        
        Parameters:
        -----------
        slope : float
            Declividade em graus
            
        Returns:
        --------
        str
            Classificação do terreno
        """
        
        if slope < 3:
            return "Plano"
        elif slope < 8:
            return "Suave Ondulado"
        elif slope < 20:
            return "Ondulado"
        elif slope < 45:
            return "Forte Ondulado"
        elif slope < 75:
            return "Montanhoso"
        else:
            return "Escarpado"
    
    @staticmethod
    def classify_elevation_zone(elevation: float, region: str = "parana") -> str:
        """
        Classifica zona altimétrica
        
        Parameters:
        -----------
        elevation : float
            Altitude em metros
        region : str
            Região para classificação contextual
            
        Returns:
        --------
        str
            Zona altimétrica
        """
        
        if region == "parana":
            if elevation < 300:
                return "Planície Litorânea"
            elif elevation < 600:
                return "Primeiro Planalto"
            elif elevation < 900:
                return "Segundo Planalto"
            elif elevation < 1200:
                return "Terceiro Planalto"
            else:
                return "Zona de Montanha"
        else:
            # Classificação genérica
            if elevation < 200:
                return "Terras Baixas"
            elif elevation < 500:
                return "Terras Médias"
            elif elevation < 1000:
                return "Terras Altas"
            else:
                return "Montanhoso"
    
    @staticmethod
    def calculate_terrain_ruggedness(elevation_df: pd.DataFrame, 
                                     grid_size: Optional[int] = None) -> float:
        """
        Calcula índice de rugosidade do terreno (TRI - Terrain Ruggedness Index)
        
        TRI = média das diferenças absolutas entre célula central e vizinhas
        """
        
        if grid_size is None:
            grid_size = int(np.sqrt(len(elevation_df)))
        
        elevation_matrix = elevation_df['elevation'].values.reshape(grid_size, grid_size)
        
        # Calcular diferenças com células vizinhas
        tri = np.zeros_like(elevation_matrix)
        
        for i in range(1, grid_size - 1):
            for j in range(1, grid_size - 1):
                center = elevation_matrix[i, j]
                
                # 8 vizinhos
                neighbors = [
                    elevation_matrix[i-1, j-1], elevation_matrix[i-1, j], elevation_matrix[i-1, j+1],
                    elevation_matrix[i, j-1],                              elevation_matrix[i, j+1],
                    elevation_matrix[i+1, j-1], elevation_matrix[i+1, j], elevation_matrix[i+1, j+1]
                ]
                
                # TRI = média das diferenças absolutas
                tri[i, j] = np.mean([abs(center - n) for n in neighbors])
        
        return float(np.mean(tri))
    
    @staticmethod
    def identify_peaks_and_valleys(elevation_df: pd.DataFrame,
                                   grid_size: Optional[int] = None,
                                   threshold: float = 50) -> dict:
        """
        Identifica picos e vales no terreno
        
        Parameters:
        -----------
        elevation_df : pd.DataFrame
            Dados de elevação
        grid_size : int
            Tamanho da grade
        threshold : float
            Diferença mínima para considerar pico/vale (metros)
            
        Returns:
        --------
        dict
            {'peaks': DataFrame, 'valleys': DataFrame}
        """
        
        if grid_size is None:
            grid_size = int(np.sqrt(len(elevation_df)))
        
        elevation_matrix = elevation_df['elevation'].values.reshape(grid_size, grid_size)
        
        peaks = []
        valleys = []
        
        for i in range(1, grid_size - 1):
            for j in range(1, grid_size - 1):
                center = elevation_matrix[i, j]
                
                # Verificar 8 vizinhos
                neighbors = [
                    elevation_matrix[i-1, j-1], elevation_matrix[i-1, j], elevation_matrix[i-1, j+1],
                    elevation_matrix[i, j-1],                              elevation_matrix[i, j+1],
                    elevation_matrix[i+1, j-1], elevation_matrix[i+1, j], elevation_matrix[i+1, j+1]
                ]
                
                # Pico: maior que todos os vizinhos
                if all(center > n + threshold for n in neighbors):
                    idx = i * grid_size + j
                    peaks.append({
                        'lat': elevation_df.iloc[idx]['lat'],
                        'lon': elevation_df.iloc[idx]['lon'],
                        'elevation': center
                    })
                
                # Vale: menor que todos os vizinhos
                if all(center < n - threshold for n in neighbors):
                    idx = i * grid_size + j
                    valleys.append({
                        'lat': elevation_df.iloc[idx]['lat'],
                        'lon': elevation_df.iloc[idx]['lon'],
                        'elevation': center
                    })
        
        return {
            'peaks': pd.DataFrame(peaks),
            'valleys': pd.DataFrame(valleys)
        }

class GeoJSONConverter:
    """Conversão de dados geoespaciais para GeoJSON"""
    
    @staticmethod
    def elevation_to_geojson(elevation_df: pd.DataFrame,
                            property_name: str = 'elevation') -> dict:
        """
        Converte DataFrame de elevação para GeoJSON
        
        Returns:
        --------
        dict
            GeoJSON FeatureCollection
        """
        
        features = []
        
        for _, row in elevation_df.iterrows():
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [row['lon'], row['lat']]
                },
                'properties': {
                    property_name: row.get(property_name, row.get('elevation'))
                }
            }
            
            # Adicionar outras propriedades se existirem
            for col in elevation_df.columns:
                if col not in ['lat', 'lon', property_name]:
                    feature['properties'][col] = row[col]
            
            features.append(feature)
        
        return {
            'type': 'FeatureCollection',
            'features': features
        }
    
    @staticmethod
    def contours_to_geojson(contours: List[dict]) -> dict:
        """
        Converte linhas de contorno para GeoJSON
        
        Parameters:
        -----------
        contours : list of dict
            Lista com 'elevation' e 'coordinates'
            
        Returns:
        --------
        dict
            GeoJSON FeatureCollection
        """
        
        features = []
        
        for contour in contours:
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'LineString',
                    'coordinates': contour['coordinates']
                },
                'properties': {
                    'elevation': contour['elevation']
                }
            }
            features.append(feature)
        
        return {
            'type': 'FeatureCollection',
            'features': features
        }

def generate_grid_coordinates(center_lat: float,
                             center_lon: float,
                             grid_size: int = 100,
                             extent: float = 0.15) -> List[Tuple[float, float]]:
    """
    Gera grade de coordenadas para download de dados
    
    Parameters:
    -----------
    center_lat, center_lon : float
        Centro da área
    grid_size : int
        Número de pontos em cada dimensão
    extent : float
        Extensão em graus (aproximadamente)
        
    Returns:
    --------
    list of tuples
        Lista de (lat, lon)
    """
    
    lat_range = np.linspace(center_lat - extent, center_lat + extent, grid_size)
    lon_range = np.linspace(center_lon - extent, center_lon + extent, grid_size)
    
    coordinates = []
    for lat in lat_range:
        for lon in lon_range:
            coordinates.append((lat, lon))
    
    return coordinates

# Exemplo de uso
if __name__ == "__main__":
    print("Módulo de Utilidades de Dados Topográficos")
    print("=" * 60)
    
    # Exemplo 1: Obter elevação de um ponto
    print("\n1. Obtendo elevação via Open-Elevation (gratuito):")
    client = ElevationAPIClient()
    
    # Prudentópolis - centro
    lat, lon = -25.1973, -50.9780
    elevation = client.get_elevation_open_elevation(lat, lon)
    print(f"   Coordenadas: {lat}, {lon}")
    print(f"   Elevação: {elevation}m")
    
    # Exemplo 2: Classificação
    print("\n2. Classificação de terreno:")
    analyzer = TerrainAnalyzer()
    
    slope = 25.5
    classification = analyzer.classify_slope(slope)
    print(f"   Declividade: {slope}°")
    print(f"   Classificação: {classification}")
    
    elevation = 850
    zone = analyzer.classify_elevation_zone(elevation, "parana")
    print(f"   Altitude: {elevation}m")
    print(f"   Zona: {zone}")
    
    print("\n" + "=" * 60)
    print("Funções disponíveis:")
    print("- ElevationAPIClient: Obter dados via APIs")
    print("- TerrainAnalyzer: Classificação e análise de terreno")
    print("- GeoJSONConverter: Exportar para formatos geoespaciais")
    print("- generate_grid_coordinates: Criar grades de amostragem")
