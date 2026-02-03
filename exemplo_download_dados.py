#!/usr/bin/env python3
"""
Script de exemplo: Download de dados de elevação para Prudentópolis
Demonstra uso das APIs disponíveis e processamento básico
"""

import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

from data_utils import ElevationAPIClient, TerrainAnalyzer, GeoJSONConverter, generate_grid_coordinates
import pandas as pd
import json
import time
from datetime import datetime

def exemplo_download_via_api():
    """
    Exemplo 1: Download de dados via Open-Elevation API (gratuita)
    """
    
    print("=" * 70)
    print("EXEMPLO 1: Download de dados via Open-Elevation API")
    print("=" * 70)
    
    # Configurar cliente (não requer token)
    client = ElevationAPIClient()
    
    # Definir área de interesse - Prudentópolis
    center_lat, center_lon = -25.1973, -50.9780
    
    print(f"\nCentro: {center_lat}, {center_lon} (Prudentópolis, PR)")
    print("Gerando grade de amostragem...")
    
    # Gerar grade de pontos (reduzida para exemplo)
    coordinates = generate_grid_coordinates(
        center_lat, 
        center_lon, 
        grid_size=10,  # 10x10 = 100 pontos (rápido para exemplo)
        extent=0.05    # ~5km de extensão
    )
    
    print(f"Total de pontos: {len(coordinates)}")
    print("\nBaixando dados de elevação...")
    print("(Este processo pode levar alguns minutos...)")
    
    # Coletar dados
    data = []
    
    for i, (lat, lon) in enumerate(coordinates):
        elevation = client.get_elevation_open_elevation(lat, lon)
        
        if elevation is not None:
            data.append({
                'lat': lat,
                'lon': lon,
                'elevation': elevation
            })
        
        # Progress
        if (i + 1) % 10 == 0:
            print(f"  Progresso: {i+1}/{len(coordinates)}")
        
        # Rate limiting (evitar sobrecarga da API gratuita)
        time.sleep(0.2)
    
    # Criar DataFrame
    df = pd.DataFrame(data)
    
    print(f"\n✓ Download concluído! {len(df)} pontos obtidos")
    print("\nPrimeiras linhas dos dados:")
    print(df.head())
    
    # Salvar CSV
    output_file = f'elevation_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    df.to_csv(output_file, index=False)
    print(f"\n✓ Dados salvos em: {output_file}")
    
    return df

def exemplo_analise_terreno(elevation_df):
    """
    Exemplo 2: Análise de características do terreno
    """
    
    print("\n" + "=" * 70)
    print("EXEMPLO 2: Análise de Terreno")
    print("=" * 70)
    
    analyzer = TerrainAnalyzer()
    
    # Estatísticas básicas
    print("\nEstatísticas de Elevação:")
    print(f"  Mínima: {elevation_df['elevation'].min():.1f}m")
    print(f"  Máxima: {elevation_df['elevation'].max():.1f}m")
    print(f"  Média: {elevation_df['elevation'].mean():.1f}m")
    print(f"  Mediana: {elevation_df['elevation'].median():.1f}m")
    print(f"  Desnível: {elevation_df['elevation'].max() - elevation_df['elevation'].min():.1f}m")
    
    # Classificação altimétrica
    print("\nClassificação Altimétrica (Paraná):")
    
    for _, row in elevation_df.sample(5).iterrows():
        zone = analyzer.classify_elevation_zone(row['elevation'], 'parana')
        print(f"  {row['elevation']:.0f}m → {zone}")
    
    # Análise de declividade (se tiver dados em grade)
    try:
        from srtm_processor import calculate_slope_from_elevation
        
        grid_size = int(len(elevation_df) ** 0.5)
        
        if len(elevation_df) == grid_size ** 2:
            print("\nCalculando declividade...")
            elevation_df = calculate_slope_from_elevation(elevation_df, grid_size)
            
            print(f"\nEstatísticas de Declividade:")
            print(f"  Média: {elevation_df['slope'].mean():.1f}°")
            print(f"  Máxima: {elevation_df['slope'].max():.1f}°")
            
            # Distribuição de classes
            print("\nDistribuição de Classes de Terreno:")
            
            for _, row in elevation_df.sample(5).iterrows():
                classification = analyzer.classify_slope(row['slope'])
                print(f"  {row['slope']:.1f}° → {classification}")
        
    except ImportError:
        print("\n⚠️  Módulo srtm_processor não disponível para cálculo de slope")
    
    return elevation_df

def exemplo_exportar_geojson(elevation_df):
    """
    Exemplo 3: Exportar dados para GeoJSON
    """
    
    print("\n" + "=" * 70)
    print("EXEMPLO 3: Exportar para GeoJSON")
    print("=" * 70)
    
    converter = GeoJSONConverter()
    
    # Converter para GeoJSON
    geojson = converter.elevation_to_geojson(elevation_df)
    
    # Salvar arquivo
    output_file = f'elevation_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.geojson'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2)
    
    print(f"\n✓ GeoJSON salvo em: {output_file}")
    print(f"  Total de features: {len(geojson['features'])}")
    print("\nPrimeira feature (exemplo):")
    print(json.dumps(geojson['features'][0], indent=2))
    
    print("\n💡 Este arquivo pode ser:")
    print("  - Visualizado em QGIS")
    print("  - Importado em Google Earth")
    print("  - Usado em aplicações web (Leaflet, Mapbox)")

def exemplo_identificar_picos():
    """
    Exemplo 4: Identificar picos e vales (requer dados em grade)
    """
    
    print("\n" + "=" * 70)
    print("EXEMPLO 4: Identificação de Picos e Vales")
    print("=" * 70)
    
    print("\n⚠️  Esta função requer dados em grade regular")
    print("Execute primeiro o download com grid_size maior (ex: 20x20)")
    
    # Exemplo conceitual
    print("\nFunção disponível:")
    print("  analyzer.identify_peaks_and_valleys(elevation_df, threshold=50)")
    print("\nRetorna:")
    print("  {'peaks': DataFrame, 'valleys': DataFrame}")

def exemplo_completo():
    """
    Executa todos os exemplos em sequência
    """
    
    print("\n" + "=" * 70)
    print("SCRIPT DE DEMONSTRAÇÃO - APIs e Processamento de Dados")
    print("Geoparque Prudentópolis - Dashboard 3D")
    print("=" * 70)
    
    try:
        # Exemplo 1: Download
        elevation_df = exemplo_download_via_api()
        
        # Exemplo 2: Análise
        elevation_df = exemplo_analise_terreno(elevation_df)
        
        # Exemplo 3: Export
        exemplo_exportar_geojson(elevation_df)
        
        # Exemplo 4: Info adicional
        exemplo_identificar_picos()
        
        print("\n" + "=" * 70)
        print("✓ TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
        print("=" * 70)
        
        print("\n📁 Arquivos gerados:")
        print("  - elevation_data_YYYYMMDD_HHMMSS.csv")
        print("  - elevation_data_YYYYMMDD_HHMMSS.geojson")
        
        print("\n💡 Próximos passos:")
        print("  1. Abra o arquivo CSV em Excel/Pandas para análise")
        print("  2. Visualize o GeoJSON em QGIS ou aplicação web")
        print("  3. Modifique os parâmetros (grid_size, extent) para mais dados")
        print("  4. Integre com o dashboard Streamlit")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        print("\nVerifique:")
        print("  1. Conexão com internet (para APIs)")
        print("  2. Instalação de dependências (pip install -r requirements.txt)")
        print("  3. Versões corretas das bibliotecas")
        
        import traceback
        print("\nDetalhes do erro:")
        traceback.print_exc()

if __name__ == "__main__":
    print("\nScript de Demonstração - APIs e Processamento")
    print("=" * 70)
    print("\nOpções:")
    print("  1. Executar exemplo completo (download + análise + export)")
    print("  2. Apenas download de dados")
    print("  3. Apenas análise de terreno (requer CSV existente)")
    print("  4. Apenas exportar GeoJSON (requer CSV existente)")
    print("  5. Sair")
    
    try:
        opcao = input("\nEscolha uma opção (1-5): ").strip()
        
        if opcao == '1':
            exemplo_completo()
        elif opcao == '2':
            exemplo_download_via_api()
        elif opcao == '3':
            csv_file = input("Caminho do arquivo CSV: ").strip()
            df = pd.read_csv(csv_file)
            exemplo_analise_terreno(df)
        elif opcao == '4':
            csv_file = input("Caminho do arquivo CSV: ").strip()
            df = pd.read_csv(csv_file)
            exemplo_exportar_geojson(df)
        elif opcao == '5':
            print("Saindo...")
        else:
            print("Opção inválida!")
            
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\nErro: {e}")
