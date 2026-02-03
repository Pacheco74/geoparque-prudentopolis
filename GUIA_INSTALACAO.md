# 🏔️ Geoparque Prudentópolis - Dashboard 3D
## Guia Completo de Instalação e Configuração

---

## 📋 Índice
1. [Pré-requisitos](#pré-requisitos)
2. [Instalação](#instalação)
3. [Obtenção de Dados SRTM](#obtenção-de-dados-srtm)
4. [Configuração de APIs](#configuração-de-apis)
5. [Execução do Dashboard](#execução-do-dashboard)
6. [Funcionalidades Avançadas](#funcionalidades-avançadas)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Pré-requisitos

### Sistema Operacional
- Windows 10/11, macOS 10.15+, ou Linux (Ubuntu 20.04+)
- Python 3.8 ou superior

### Verificar versão do Python:
```bash
python --version
# ou
python3 --version
```

### Software Adicional (Recomendado)
- **QGIS** (para visualizar e processar dados geoespaciais)
- **Git** (para controle de versão)

---

## 📦 Instalação

### 1. Clone ou baixe o projeto
```bash
git clone https://github.com/seu-usuario/geoparque-prudentopolis.git
cd geoparque-prudentopolis
```

### 2. Crie um ambiente virtual (Recomendado)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Instalação de bibliotecas geoespaciais (podem requerer passos extras)

#### Windows:
Algumas bibliotecas geoespaciais requerem binários pré-compilados:
```bash
# Visite: https://www.lfd.uci.edu/~gohlke/pythonlibs/
# Baixe os arquivos .whl apropriados para:
# - GDAL
# - rasterio
# - Fiona

# Depois instale:
pip install GDAL-3.X.X-cpXX-cpXX-win_amd64.whl
pip install rasterio-1.X.X-cpXX-cpXX-win_amd64.whl
pip install Fiona-1.X.X-cpXX-cpXX-win_amd64.whl
```

#### macOS:
```bash
# Instale Homebrew se ainda não tiver
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instale GDAL
brew install gdal

# Instale as bibliotecas Python
pip install GDAL==$(gdal-config --version)
pip install rasterio fiona
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get update
sudo apt-get install -y gdal-bin libgdal-dev python3-gdal
pip install GDAL==$(gdal-config --version)
pip install rasterio fiona geopandas
```

---

## 🌍 Obtenção de Dados SRTM

### Opção 1: Download Manual (Recomendado)

#### a) USGS Earth Explorer
1. Acesse: https://earthexplorer.usgs.gov/
2. Crie uma conta gratuita
3. Busque por coordenadas de Prudentópolis:
   - Latitude: -25.1973
   - Longitude: -50.9780
4. Selecione "Digital Elevation > SRTM"
5. Escolha resolução (30m ou 90m)
6. Faça download do arquivo `.tif`

#### b) OpenTopography
1. Acesse: https://opentopography.org/
2. Navegue até "Data > Global Data"
3. Selecione "SRTM GL1 (30m)"
4. Defina a área de interesse (bounding box):
   ```
   Norte: -25.1°
   Sul: -25.3°
   Leste: -50.9°
   Oeste: -51.1°
   ```
5. Faça download no formato GeoTIFF

### Opção 2: Download Programático

#### Usando Python (srtm.py)
```python
import srtm

# Obter dados de elevação
elevation_data = srtm.get_data()

# Obter elevação de um ponto
latitude, longitude = -25.1973, -50.9780
altitude = elevation_data.get_elevation(latitude, longitude)
print(f"Altitude: {altitude}m")
```

#### Usando API do Mapbox (Requer chave de API)
```python
import requests

def get_elevation_mapbox(lat, lon, access_token):
    url = f"https://api.mapbox.com/v4/mapbox.mapbox-terrain-v2/tilequery/{lon},{lat}.json"
    params = {
        'layers': 'contour',
        'access_token': access_token
    }
    response = requests.get(url, params=params)
    return response.json()
```

### Opção 3: Dados Incluídos (Sintéticos)
O dashboard já inclui dados sintéticos para demonstração. Para usar dados reais:

1. Coloque seu arquivo SRTM na pasta `data/`
2. Modifique o código em `geoparque_dashboard.py`:

```python
# Substitua a função generate_elevation_data() por:
from srtm_processor import load_srtm_data

elevation_df = load_srtm_data(
    'data/prudentopolis_srtm.tif',
    bbox=(-51.1, -25.3, -50.9, -25.1)
)
```

---

## 🔑 Configuração de APIs

### Mapbox (Para mapas base 3D)

1. **Criar conta:**
   - Acesse: https://account.mapbox.com/auth/signup/
   - Crie uma conta gratuita

2. **Obter token de acesso:**
   - Dashboard > Access Tokens
   - Copie o "Default public token" ou crie um novo

3. **Configurar no projeto:**

Crie um arquivo `.env` na raiz do projeto:
```env
MAPBOX_ACCESS_TOKEN=pk.eyJ1IjoieW91cl91c2VybmFtZSIsImEiOiJjbHh4eHh4eHgifQ.xxxxxxxxxxxxxxxxxx
```

4. **Usar no código:**
```python
import os
from dotenv import load_dotenv

load_dotenv()
MAPBOX_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN')

# No PyDeck
r = pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    mapbox_key=MAPBOX_TOKEN,
    # ...
)
```

### Limites de uso gratuito:
- **Mapbox:** 200,000 requisições/mês
- Suficiente para desenvolvimento e demonstrações

---

## 🚀 Execução do Dashboard

### Modo Básico
```bash
streamlit run geoparque_dashboard.py
```

O dashboard abrirá automaticamente no navegador em: `http://localhost:8501`

### Modo Avançado (com configurações)
```bash
streamlit run geoparque_dashboard.py --server.port 8080 --server.address 0.0.0.0
```

### Deploy em Produção

#### Streamlit Cloud (Gratuito)
1. Faça push do código para GitHub
2. Acesse: https://share.streamlit.io/
3. Conecte seu repositório
4. Configure secrets (API keys) no painel

#### Heroku
```bash
# Criar Procfile
echo "web: streamlit run geoparque_dashboard.py --server.port=$PORT" > Procfile

# Deploy
heroku create geoparque-prudentopolis
git push heroku main
```

#### Docker
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "geoparque_dashboard.py", "--server.address", "0.0.0.0"]
```

---

## 🎯 Funcionalidades Avançadas

### 1. Upload de Shapefiles

**Formato esperado:**
- `.shp` principal
- `.shx` (índice)
- `.dbf` (atributos)
- `.prj` (projeção)

**Como usar:**
1. Compacte todos os arquivos em um `.zip`
2. Faça upload no dashboard
3. O sistema processará e sobrepõe no mapa 3D

### 2. Análise de Declividade

**Interpretação:**
- **0-5°:** Terreno plano (baixo risco de erosão)
- **5-15°:** Ondulado (agricultura possível)
- **15-30°:** Inclinado (requer manejo conservacionista)
- **>30°:** Fortemente inclinado (áreas de preservação)

### 3. Perfil Altimétrico

**Como usar:**
1. Ative "Perfil Altimétrico" na barra lateral
2. Insira coordenadas de dois pontos
3. Clique em "Gerar Perfil"
4. Analise a variação de elevação

**Aplicações:**
- Planejamento de trilhas
- Análise de rotas de acesso
- Estudo de escarpas

### 4. Exagero Vertical

**Valores recomendados:**
- **1.0x:** Representação real (pode parecer plano)
- **3.0x:** Equilíbrio (recomendado)
- **5-10x:** Ênfase em variações sutis

---

## ⚠️ Troubleshooting

### Problema: "ModuleNotFoundError: No module named 'rasterio'"

**Solução:**
```bash
# Windows
pip install pipwin
pipwin install rasterio

# macOS/Linux
pip install rasterio==1.3.9
```

### Problema: PyDeck não renderiza o mapa 3D

**Solução 1:** Verificar token do Mapbox
```python
# Adicione debug no código
print(f"Mapbox token: {MAPBOX_TOKEN[:10]}...")
```

**Solução 2:** Usar estilo sem autenticação
```python
# Substitua no código
map_style='mapbox://styles/mapbox/dark-v10'
# por
map_style=None  # Usa OpenStreetMap
```

### Problema: Dashboard muito lento

**Soluções:**
1. Reduzir resolução do grid:
   ```python
   grid_resolution = 50  # ao invés de 150
   ```

2. Usar cache do Streamlit:
   ```python
   @st.cache_data
   def funcao_pesada():
       # ...
   ```

3. Limitar área de análise (bbox menor)

### Problema: Erro ao processar Shapefile

**Solução:**
```bash
# Instalar GDAL corretamente
pip uninstall gdal fiona geopandas
pip install gdal fiona geopandas --no-cache-dir
```

### Problema: Gráficos não aparecem

**Solução:**
Verificar versão do Plotly:
```bash
pip install plotly==5.18.0 --upgrade
```

---

## 📚 Recursos Adicionais

### Documentação
- **Streamlit:** https://docs.streamlit.io/
- **PyDeck:** https://deckgl.readthedocs.io/
- **Plotly:** https://plotly.com/python/
- **GeoPandas:** https://geopandas.org/

### Tutoriais
- [SRTM Data Processing](https://github.com/USGS/srtm)
- [PyDeck Examples](https://github.com/visgl/deck.gl/tree/master/bindings/pydeck/examples)
- [Streamlit Gallery](https://streamlit.io/gallery)

### Datasets
- **SRTM:** https://earthexplorer.usgs.gov/
- **TOPODATA (Brasil):** http://www.dsr.inpe.br/topodata/
- **IBGE:** https://www.ibge.gov.br/geociencias/downloads-geociencias.html

---

## 📞 Suporte

Para problemas técnicos ou dúvidas:
- Abra uma issue no GitHub
- Consulte a documentação oficial das bibliotecas
- Comunidade Streamlit: https://discuss.streamlit.io/

---

## 📄 Licença

Este projeto é disponibilizado sob licença MIT. Veja arquivo `LICENSE` para detalhes.

---

## 🎓 Créditos

**Desenvolvido para o Projeto Geoparque Prudentópolis**
- Dados topográficos: USGS/SRTM
- Visualização: PyDeck, Plotly
- Framework: Streamlit

**Agradecimentos:**
- USGS Earth Explorer
- Mapbox
- Comunidade Python Geoespacial

---

**Última atualização:** Fevereiro 2026
