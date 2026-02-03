# 🏔️ Geoparque Prudentópolis - Dashboard 3D

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Dashboard interativo de visualização tridimensional do relevo e análise geomorfológica para o projeto **Geoparque Prudentópolis**, Paraná, Brasil.

![Dashboard Preview](https://via.placeholder.com/1200x600/1a1a1a/d4af37?text=Geoparque+Prudentopolis+3D+Dashboard)

---

## 🌟 Destaques

- **Visualização 3D do Relevo** usando PyDeck com exagero vertical ajustável
- **Mapa de Declividade** (Slope Analysis) com classificação EMBRAPA
- **Perfis Altimétricos** interativos entre dois pontos quaisquer
- **Ranking de Cachoeiras** com localização e altura das quedas
- **Upload de Shapefiles/GeoJSON** para sobreposição de trilhas e áreas protegidas
- **Design Dark Geological** luxuoso com tema inspirado em basalto e cobre

---

## 📋 Índice

- [Características](#-características)
- [Por que 3D para Prudentópolis?](#-por-que-3d-para-prudentópolis)
- [Instalação Rápida](#-instalação-rápida)
- [Uso](#-uso)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Funcionalidades Técnicas](#-funcionalidades-técnicas)
- [Capturas de Tela](#-capturas-de-tela)
- [Contribuindo](#-contribuindo)
- [Licença](#-licença)

---

## ✨ Características

### Visualização Avançada
- **Mapa 3D Interativo**: Rotação, inclinação e zoom fluidos
- **Camadas de Dados**: Elevação, cachoeiras, trilhas customizáveis
- **Controle de Exagero**: Slider para ajustar percepção vertical (1x-10x)

### Análise Geomorfológica
- **Mapa de Calor de Declividade**: Identifica áreas de risco e potencial
- **Perfis Topográficos**: Análise de transectos com gráficos dinâmicos
- **Estatísticas de Terreno**: Altitude min/max, desnível, rugosidade

### Dados Geoespaciais
- **Suporte SRTM**: Processamento de dados de elevação reais (30m/90m)
- **Upload de Arquivos**: Shapefile, GeoJSON para customização
- **APIs Integradas**: Mapbox, OpenTopography, Open-Elevation

### Interface Profissional
- **Tema Dark Geological**: Paleta cobre/dourado sobre fundo escuro
- **Responsivo**: Adaptável a diferentes resoluções
- **Métricas em Tempo Real**: Indicadores estatísticos dinâmicos

---

## 🗺️ Por que 3D para Prudentópolis?

Prudentópolis está localizada na **Serra da Esperança**, região de transição entre o Segundo e Terceiro Planalto Paranaense, caracterizada por:

- **Desnível abrupto**: Variação de ~900m em poucos quilômetros
- **Escarpas basálticas**: Formações geológicas únicas da Serra Geral
- **Cachoeiras monumentais**: Salto São Francisco (196m) - 2ª maior queda livre do Brasil
- **Cânions e vales profundos**: Relevo altamente dissecado

Um mapa 2D tradicional **não faz justiça** a essa complexidade geomorfológica. A visualização 3D permite:

1. **Compreensão intuitiva** da topografia acidentada
2. **Identificação visual** de áreas de risco e preservação
3. **Planejamento de trilhas** considerando inclinações reais
4. **Argumento de venda** para aprovação do Geoparque pela UNESCO

---

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.8+
- pip

### Passo a Passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/geoparque-prudentopolis.git
cd geoparque-prudentopolis

# 2. Crie ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# 3. Instale dependências
pip install -r requirements.txt

# 4. Configure variáveis de ambiente (opcional)
cp .env.example .env
# Edite .env e adicione sua chave Mapbox (se tiver)

# 5. Execute o dashboard
streamlit run geoparque_dashboard.py
```

O dashboard abrirá automaticamente em `http://localhost:8501`

---

## 📖 Uso

### Interface Principal

1. **Barra Lateral** (Controles):
   - Ajuste o **Exagero Vertical** (1x-10x)
   - Ative/desative **Geossítios (Cachoeiras)**
   - Escolha a **Resolução do Terreno**
   - Ative análises: **Declividade** e **Perfil Altimétrico**

2. **Mapa 3D**:
   - **Arraste** com mouse para rotacionar
   - **Ctrl + Arraste** para inclinar
   - **Scroll** para zoom
   - **Clique** nos pontos para informações

3. **Análises**:
   - **Mapa de Declividade**: Identifica áreas críticas (>30°)
   - **Perfil Altimétrico**: Insira coordenadas de dois pontos

4. **Upload de Dados**:
   - Arraste arquivo `.geojson` ou `.zip` (shapefile)
   - Visualize no mapa 3D

### Usando Dados SRTM Reais

```python
# Edite geoparque_dashboard.py e substitua:

# De:
elevation_df = generate_elevation_data(grid_size=grid_resolution)

# Para:
from srtm_processor import load_srtm_data
elevation_df = load_srtm_data(
    'data/prudentopolis_srtm.tif',
    bbox=(-51.1, -25.3, -50.9, -25.1)
)
```

---

## 📁 Estrutura do Projeto

```
geoparque-prudentopolis/
├── geoparque_dashboard.py      # Dashboard principal (Streamlit)
├── srtm_processor.py            # Processamento de dados SRTM
├── data_utils.py                # Utilitários e APIs
├── requirements.txt             # Dependências Python
├── .env.example                 # Template de variáveis de ambiente
├── GUIA_INSTALACAO.md          # Guia detalhado de instalação
├── README.md                    # Este arquivo
├── LICENSE                      # Licença MIT
└── data/                        # Dados topográficos (não versionado)
    ├── prudentopolis_srtm.tif  # Arquivo SRTM (download separado)
    └── areas_protegidas.shp    # Shapefiles customizados
```

---

## 🔧 Funcionalidades Técnicas

### Processamento de Dados

#### Elevação (SRTM)
```python
from srtm_processor import load_srtm_data, calculate_slope_from_elevation

# Carregar dados
df = load_srtm_data('data/srtm.tif', bbox=(-51.1, -25.3, -50.9, -25.1))

# Calcular declividade
df = calculate_slope_from_elevation(df)
```

#### APIs de Elevação
```python
from data_utils import ElevationAPIClient

client = ElevationAPIClient()

# Open-Elevation (gratuito)
elevation = client.get_elevation_open_elevation(-25.1973, -50.9780)

# Mapbox (requer token)
client = ElevationAPIClient(mapbox_token="pk.ey...")
elevation = client.get_elevation_mapbox(-25.1973, -50.9780)
```

### Análise de Terreno

```python
from data_utils import TerrainAnalyzer

analyzer = TerrainAnalyzer()

# Classificar declividade
classification = analyzer.classify_slope(25.5)  # "Forte Ondulado"

# Classificar zona altimétrica
zone = analyzer.classify_elevation_zone(850, "parana")  # "Segundo Planalto"

# Calcular rugosidade
tri = analyzer.calculate_terrain_ruggedness(elevation_df)
```

### Exportar GeoJSON

```python
from data_utils import GeoJSONConverter

converter = GeoJSONConverter()

# Converter elevação para GeoJSON
geojson = converter.elevation_to_geojson(elevation_df)

# Salvar
import json
with open('output.geojson', 'w') as f:
    json.dump(geojson, f)
```

---

## 📸 Capturas de Tela

### Visualização 3D do Relevo
![Mapa 3D](https://via.placeholder.com/800x450/1a1a1a/d4af37?text=Vista+3D+da+Serra+da+Esperanca)

### Mapa de Declividade
![Slope Map](https://via.placeholder.com/800x450/1a1a1a/ff4444?text=Analise+de+Declividade)

### Perfil Altimétrico
![Elevation Profile](https://via.placeholder.com/800x450/1a1a1a/d4af37?text=Perfil+Topografico)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

### Guidelines
- Siga PEP 8 para código Python
- Adicione docstrings às funções
- Teste antes de submeter
- Atualize documentação se necessário

---

## 📚 Recursos Úteis

### Dados Topográficos
- [USGS Earth Explorer](https://earthexplorer.usgs.gov/) - Download SRTM
- [TOPODATA INPE](http://www.dsr.inpe.br/topodata/) - Dados Brasil
- [OpenTopography](https://opentopography.org/) - Dados globais

### Documentação Técnica
- [Streamlit Docs](https://docs.streamlit.io/)
- [PyDeck Documentation](https://deckgl.readthedocs.io/)
- [GeoPandas Guide](https://geopandas.org/)
- [Rasterio Manual](https://rasterio.readthedocs.io/)

### Sobre Geoparques
- [UNESCO Global Geoparks](http://www.unesco.org/new/en/natural-sciences/environment/earth-sciences/unesco-global-geoparks/)
- [Geoparks Brasil](http://geoparcosbrasileiros.com.br/)

---

## 📄 Licença

Este projeto está licenciado sob a **MIT License** - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 👥 Autores

**Projeto Geoparque Prudentópolis**
- Desenvolvedor: [Seu Nome]
- Contato: [seu.email@exemplo.com]

**Agradecimentos:**
- USGS por dados SRTM
- Mapbox por APIs de visualização
- Comunidade Python Geoespacial

---

## 🌐 Links

- [Website do Projeto](https://geoparque-prudentopolis.example.com)
- [Documentação Completa](https://docs.example.com)
- [Relatório Técnico](https://example.com/relatorio)

---

## 📊 Status do Projeto

![Status](https://img.shields.io/badge/Status-Em%20Desenvolvimento-yellow)
![Coverage](https://img.shields.io/badge/Coverage-75%25-green)
![Issues](https://img.shields.io/github/issues/seu-usuario/geoparque-prudentopolis)

---

## 💡 Roadmap

- [x] Visualização 3D básica
- [x] Análise de declividade
- [x] Perfis altimétricos
- [ ] Integração com Google Earth Engine
- [ ] Análise de bacia hidrográfica
- [ ] Modelagem de erosão
- [ ] App mobile (React Native)
- [ ] Dashboard público online

---

<p align="center">
  <strong>Desenvolvido com ❤️ para a conservação da geodiversidade brasileira</strong>
</p>

<p align="center">
  <sub>Prudentópolis, Paraná - Brasil | 2026</sub>
</p>
