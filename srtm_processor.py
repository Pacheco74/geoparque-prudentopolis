"""
Módulo de Processamento de Dados Topográficos (SRTM)
Utiliza rasterio para ler arquivos .tif de elevação
"""

import numpy as np
import pandas as pd
from pathlib import Path

try:
    import rasterio
    from rasterio.windows import Window
    RASTERIO_AVAILABLE = True
except ImportError:
    RASTERIO_AVAILABLE = False
    print("⚠️ rasterio não instalado. Instale com: pip install rasterio")

def load_srtm_data(filepath, bbox=None):
    """
    Carrega dados SRTM de um arquivo .tif
    
    Parameters:
    -----------
    filepath : str or Path
        Caminho para o arquivo SRTM (.tif)
    bbox : tuple, optional
        Bounding box (min_lon, min_lat, max_lon, max_lat)
        
    Returns:
    --------
    pd.DataFrame
        DataFrame com colunas: lat, lon, elevation
    """
    
    if not RASTERIO_AVAILABLE:
        raise ImportError("rasterio é necessário para processar arquivos SRTM")
    
    with rasterio.open(filepath) as src:
        # Obter metadados
        transform = src.transform
        
        # Se bbox fornecido, calcular window
        if bbox:
            min_lon, min_lat, max_lon, max_lat = bbox
            
            # Converter coordenadas para pixels
            row_start, col_start = src.index(min_lon, max_lat)
            row_stop, col_stop = src.index(max_lon, min_lat)
            
            # Criar window
            window = Window.from_slices(
                (row_start, row_stop),
                (col_start, col_stop)
            )
            
            elevation_data = src.read(1, window=window)
            window_transform = src.window_transform(window)
        else:
            elevation_data = src.read(1)
            window_transform = transform
        
        # Criar coordenadas
        rows, cols = elevation_data.shape
        
        data = []
        for row in range(rows):
            for col in range(cols):
                # Converter pixel para coordenadas geográficas
                lon, lat = rasterio.transform.xy(window_transform, row, col)
                elevation = float(elevation_data[row, col])
                
                # Filtrar valores NoData
                if elevation > -9999:
                    data.append({
                        'lat': lat,
                        'lon': lon,
                        'elevation': elevation
                    })
        
        return pd.DataFrame(data)

def resample_elevation_data(df, target_resolution=100):
    """
    Reamostrar dados de elevação para uma resolução específica
    
    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame com lat, lon, elevation
    target_resolution : int
        Número de pontos desejado em cada dimensão
        
    Returns:
    --------
    pd.DataFrame
        DataFrame reamostrado
    """
    
    # Obter limites
    min_lat, max_lat = df['lat'].min(), df['lat'].max()
    min_lon, max_lon = df['lon'].min(), df['lon'].max()
    
    # Criar grade regular
    lat_grid = np.linspace(min_lat, max_lat, target_resolution)
    lon_grid = np.linspace(min_lon, max_lon, target_resolution)
    
    # Interpolação simples (nearest neighbor)
    resampled_data = []
    
    for lat in lat_grid:
        for lon in lon_grid:
            # Encontrar ponto mais próximo
            distances = np.sqrt(
                (df['lat'] - lat)**2 + 
                (df['lon'] - lon)**2
            )
            nearest_idx = distances.idxmin()
            elevation = df.loc[nearest_idx, 'elevation']
            
            resampled_data.append({
                'lat': lat,
                'lon': lon,
                'elevation': elevation
            })
    
    return pd.DataFrame(resampled_data)

def calculate_slope_from_elevation(elevation_df, grid_size=None):
    """
    Calcula declividade (slope) a partir de dados de elevação
    
    Parameters:
    -----------
    elevation_df : pd.DataFrame
        DataFrame com lat, lon, elevation
    grid_size : int, optional
        Tamanho da grade (auto-detectado se None)
        
    Returns:
    --------
    pd.DataFrame
        DataFrame original com coluna 'slope' adicionada
    """
    
    if grid_size is None:
        grid_size = int(np.sqrt(len(elevation_df)))
    
    # Reshape elevação para matriz
    try:
        elevation_matrix = elevation_df['elevation'].values.reshape(grid_size, grid_size)
    except ValueError:
        raise ValueError(f"Dados não formam grade quadrada de {grid_size}x{grid_size}")
    
    # Calcular gradientes
    grad_y, grad_x = np.gradient(elevation_matrix)
    
    # Calcular slope em graus
    # slope = arctan(sqrt(dz/dx^2 + dz/dy^2))
    slope_radians = np.arctan(np.sqrt(grad_x**2 + grad_y**2))
    slope_degrees = np.degrees(slope_radians)
    
    # Adicionar ao DataFrame
    df_with_slope = elevation_df.copy()
    df_with_slope['slope'] = slope_degrees.flatten()
    
    return df_with_slope

def calculate_aspect_from_elevation(elevation_df, grid_size=None):
    """
    Calcula orientação de vertentes (aspect) a partir de dados de elevação
    
    Parameters:
    -----------
    elevation_df : pd.DataFrame
        DataFrame com lat, lon, elevation
    grid_size : int, optional
        Tamanho da grade
        
    Returns:
    --------
    pd.DataFrame
        DataFrame com coluna 'aspect' (0-360°, 0=Norte)
    """
    
    if grid_size is None:
        grid_size = int(np.sqrt(len(elevation_df)))
    
    elevation_matrix = elevation_df['elevation'].values.reshape(grid_size, grid_size)
    
    # Gradientes
    grad_y, grad_x = np.gradient(elevation_matrix)
    
    # Calcular aspect (orientação)
    aspect_radians = np.arctan2(-grad_y, grad_x)
    aspect_degrees = np.degrees(aspect_radians)
    
    # Converter para 0-360° (0 = Norte)
    aspect_degrees = (90 - aspect_degrees) % 360
    
    df_with_aspect = elevation_df.copy()
    df_with_aspect['aspect'] = aspect_degrees.flatten()
    
    return df_with_aspect

def extract_contour_lines(elevation_df, intervals=[600, 700, 800, 900, 1000, 1100, 1200]):
    """
    Extrai linhas de contorno (curvas de nível) dos dados de elevação
    
    Parameters:
    -----------
    elevation_df : pd.DataFrame
        DataFrame com lat, lon, elevation
    intervals : list
        Altitudes para as curvas de nível
        
    Returns:
    --------
    list of dict
        Lista de dicionários com coordenadas de cada contorno
    """
    
    import matplotlib.pyplot as plt
    from matplotlib import _contour
    
    grid_size = int(np.sqrt(len(elevation_df)))
    
    # Preparar dados
    lats = elevation_df['lat'].unique()
    lons = elevation_df['lon'].unique()
    elevations = elevation_df['elevation'].values.reshape(grid_size, grid_size)
    
    # Criar contornos
    contours = []
    
    for level in intervals:
        # Usar matplotlib para gerar contornos
        fig, ax = plt.subplots()
        cs = ax.contour(lons, lats, elevations, levels=[level])
        plt.close(fig)
        
        # Extrair paths
        for collection in cs.collections:
            for path in collection.get_paths():
                vertices = path.vertices
                contours.append({
                    'elevation': level,
                    'coordinates': vertices.tolist()
                })
    
    return contours

def get_elevation_statistics(elevation_df):
    """
    Calcula estatísticas descritivas dos dados de elevação
    
    Returns:
    --------
    dict
        Estatísticas da elevação
    """
    
    return {
        'min_elevation': elevation_df['elevation'].min(),
        'max_elevation': elevation_df['elevation'].max(),
        'mean_elevation': elevation_df['elevation'].mean(),
        'median_elevation': elevation_df['elevation'].median(),
        'std_elevation': elevation_df['elevation'].std(),
        'range': elevation_df['elevation'].max() - elevation_df['elevation'].min(),
        'q25': elevation_df['elevation'].quantile(0.25),
        'q75': elevation_df['elevation'].quantile(0.75)
    }

# Exemplo de uso:
if __name__ == "__main__":
    # Exemplo de como usar o módulo
    print("Módulo de Processamento SRTM")
    print("=" * 50)
    print("\nFunções disponíveis:")
    print("- load_srtm_data(filepath, bbox=None)")
    print("- resample_elevation_data(df, target_resolution=100)")
    print("- calculate_slope_from_elevation(elevation_df)")
    print("- calculate_aspect_from_elevation(elevation_df)")
    print("- extract_contour_lines(elevation_df, intervals)")
    print("- get_elevation_statistics(elevation_df)")
    print("\nExemplo:")
    print("""
    # Carregar dados SRTM
    df = load_srtm_data('prudentopolis_srtm.tif', 
                        bbox=(-51.1, -25.3, -50.9, -25.1))
    
    # Calcular slope
    df = calculate_slope_from_elevation(df)
    
    # Obter estatísticas
    stats = get_elevation_statistics(df)
    print(stats)
    """)
