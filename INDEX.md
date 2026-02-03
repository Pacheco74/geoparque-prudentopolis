# 📚 Índice de Arquivos - Geoparque Prudentópolis Dashboard 3D

Este é o índice completo de todos os arquivos do projeto. Use-o como guia de navegação.

---

## 🚀 Início Rápido

**Para começar rapidamente:**
1. Leia: `QUICKSTART.md` (5 minutos)
2. Execute: `streamlit run geoparque_dashboard.py`
3. Explore o dashboard!

---

## 📄 Documentação Principal

### 1. README.md
**Descrição:** Documentação principal do projeto  
**Conteúdo:**
- Visão geral do projeto
- Características e funcionalidades
- Por que visualização 3D?
- Instalação básica
- Estrutura do projeto
- Capturas de tela
- Licença e créditos

**Quando usar:** Primeira leitura para entender o projeto

---

### 2. QUICKSTART.md
**Descrição:** Guia de início em 5 minutos  
**Conteúdo:**
- Três opções de instalação rápida
- Modo demonstração (dados sintéticos)
- Com dados reais (SRTM)
- Com Mapbox (melhor visual)
- Primeiros passos no dashboard
- Troubleshooting básico

**Quando usar:** Quer começar AGORA sem ler muito

---

### 3. GUIA_INSTALACAO.md
**Descrição:** Guia completo e detalhado de instalação  
**Conteúdo:**
- Pré-requisitos detalhados
- Instalação passo a passo
- Obtenção de dados SRTM (3 métodos)
- Configuração de APIs (Mapbox, OpenTopography)
- Execução e deploy
- Funcionalidades avançadas
- Troubleshooting detalhado
- Recursos adicionais

**Quando usar:** Instalação em produção ou problemas complexos

---

### 4. COMANDOS_UTEIS.md
**Descrição:** Referência de comandos para desenvolvimento e operação  
**Conteúdo:**
- Gerenciamento de dependências
- Comandos Docker
- Deploy (Heroku, Streamlit Cloud, AWS)
- Troubleshooting avançado
- Testes e benchmarks
- Monitoramento
- Segurança (HTTPS, nginx)
- Backup e rollback

**Quando usar:** Referência rápida durante desenvolvimento/deploy

---

## 💻 Código Fonte

### 5. geoparque_dashboard.py
**Descrição:** Dashboard principal em Streamlit  
**Tamanho:** ~550 linhas  
**Conteúdo:**
- Interface completa do dashboard
- Visualização 3D com PyDeck
- Mapas de declividade
- Perfis altimétricos
- Upload de shapefiles
- Tema Dark Geological

**Funcionalidades principais:**
- `load_css()` - Estilo personalizado
- `generate_elevation_data()` - Dados sintéticos
- `create_3d_terrain_map()` - Mapa 3D
- `create_slope_heatmap()` - Mapa de calor
- `create_elevation_profile()` - Perfis topográficos

**Quando modificar:** Personalização de interface, novos gráficos

---

### 6. srtm_processor.py
**Descrição:** Módulo para processamento de dados SRTM (.tif)  
**Tamanho:** ~250 linhas  
**Conteúdo:**
- Leitura de arquivos GeoTIFF
- Recorte por bounding box
- Cálculo de declividade (slope)
- Cálculo de orientação (aspect)
- Extração de curvas de nível
- Estatísticas de terreno

**Funções principais:**
- `load_srtm_data()` - Carrega arquivo .tif
- `calculate_slope_from_elevation()` - Calcula slope
- `calculate_aspect_from_elevation()` - Calcula aspect
- `extract_contour_lines()` - Gera contornos
- `get_elevation_statistics()` - Estatísticas

**Quando usar:** Processamento de dados topográficos reais

---

### 7. data_utils.py
**Descrição:** Utilitários para download via APIs e análises  
**Tamanho:** ~400 linhas  
**Conteúdo:**
- Cliente para APIs de elevação
- Classificação de terreno (EMBRAPA)
- Análise de rugosidade (TRI)
- Identificação de picos e vales
- Conversão para GeoJSON

**Classes principais:**
- `ElevationAPIClient` - Download via APIs
- `TerrainAnalyzer` - Análise geomorfológica
- `GeoJSONConverter` - Export de dados

**Quando usar:** Obter dados sem arquivo SRTM local

---

### 8. exemplo_download_dados.py
**Descrição:** Script de demonstração de uso das APIs  
**Tamanho:** ~350 linhas  
**Conteúdo:**
- Download via Open-Elevation
- Análise de terreno
- Export para GeoJSON
- Exemplos práticos comentados

**Como executar:**
```bash
python exemplo_download_dados.py
```

**Quando usar:** Aprender a usar as APIs, download inicial de dados

---

## ⚙️ Configuração

### 9. requirements.txt
**Descrição:** Dependências Python do projeto  
**Conteúdo:**
- Streamlit 1.31.0
- PyDeck 0.8.1
- Plotly 5.18.0
- GeoPandas 0.14.2
- Rasterio 1.3.9
- E mais...

**Como usar:**
```bash
pip install -r requirements.txt
```

---

### 10. env.example
**Descrição:** Template de variáveis de ambiente  
**Conteúdo:**
- MAPBOX_ACCESS_TOKEN
- OPENTOPOGRAPHY_API_KEY
- Configurações do dashboard
- Caminhos de dados

**Como usar:**
1. Copiar: `cp env.example .env`
2. Editar `.env` com suas chaves
3. Nunca commitar `.env` no Git!

---

### 11. gitignore.txt
**Descrição:** Arquivos a serem ignorados pelo Git  
**Conteúdo:**
- Python cache
- Virtual environments
- Dados grandes (.tif, .shp)
- Arquivos de saída (.csv, .geojson)
- Segredos (.env)

**Como usar:** Renomear para `.gitignore` na raiz do projeto

---

## 🐳 Deploy e Containerização

### 12. Dockerfile
**Descrição:** Imagem Docker para o dashboard  
**Conteúdo:**
- Base: Python 3.10 slim
- Instalação GDAL
- Dependências Python
- Configuração Streamlit
- Health check

**Como usar:**
```bash
docker build -t geoparque-dashboard .
docker run -p 8501:8501 geoparque-dashboard
```

---

### 13. docker-compose.yml
**Descrição:** Orquestração de serviços Docker  
**Conteúdo:**
- Serviço dashboard (Streamlit)
- Serviço nginx (reverse proxy)
- Volumes para dados
- Rede privada

**Como usar:**
```bash
docker-compose up -d
```

---

## 📜 Legal

### 14. LICENSE.txt
**Descrição:** Licença MIT do projeto  
**Conteúdo:**
- Permissões de uso
- Limitações de responsabilidade
- Condições de distribuição

**Resumo:** Livre para usar, modificar e distribuir (com atribuição)

---

## 📊 Estrutura de Diretórios Recomendada

```
geoparque-prudentopolis/
│
├── 📄 README.md                    # Documentação principal
├── 📄 QUICKSTART.md                # Início rápido
├── 📄 GUIA_INSTALACAO.md          # Instalação detalhada
├── 📄 COMANDOS_UTEIS.md           # Referência de comandos
├── 📄 LICENSE.txt                  # Licença
│
├── 💻 geoparque_dashboard.py       # Dashboard principal
├── 💻 srtm_processor.py            # Processamento SRTM
├── 💻 data_utils.py                # Utilitários e APIs
├── 💻 exemplo_download_dados.py   # Script de exemplo
│
├── ⚙️ requirements.txt             # Dependências
├── ⚙️ .env.example                 # Template de config
├── ⚙️ .gitignore                   # Ignorar arquivos
│
├── 🐳 Dockerfile                   # Imagem Docker
├── 🐳 docker-compose.yml           # Orquestração
│
└── 📁 data/                        # Dados (não versionado)
    ├── prudentopolis_srtm.tif     # Arquivo SRTM
    └── areas_protegidas.shp       # Shapefiles
```

---

## 🎯 Fluxo de Trabalho Recomendado

### Para Desenvolvimento

1. **Primeiro Contato:**
   - Ler `README.md`
   - Executar `QUICKSTART.md`

2. **Instalação Completa:**
   - Seguir `GUIA_INSTALACAO.md`
   - Configurar `env.example` → `.env`

3. **Desenvolvimento:**
   - Modificar `geoparque_dashboard.py`
   - Consultar `COMANDOS_UTEIS.md` para comandos

4. **Testes:**
   - Executar `exemplo_download_dados.py`
   - Testar localmente

5. **Deploy:**
   - Usar `Dockerfile` + `docker-compose.yml`
   - Consultar seção deploy em `GUIA_INSTALACAO.md`

### Para Usuários Finais

1. **Instalação Rápida:**
   - Executar comandos de `QUICKSTART.md`

2. **Uso:**
   - Abrir dashboard
   - Explorar funcionalidades

3. **Problemas:**
   - Consultar troubleshooting em `QUICKSTART.md`
   - Se persistir, ver `GUIA_INSTALACAO.md`

---

## 🔗 Referências Cruzadas

### Quer fazer X? → Veja arquivo Y

| Objetivo | Arquivo |
|----------|---------|
| Começar rápido | `QUICKSTART.md` |
| Entender o projeto | `README.md` |
| Instalar em produção | `GUIA_INSTALACAO.md` |
| Resolver problema | `GUIA_INSTALACAO.md` → Troubleshooting |
| Comando Docker | `COMANDOS_UTEIS.md` → Docker |
| Processar SRTM | `srtm_processor.py` |
| Usar API elevação | `data_utils.py` |
| Customizar interface | `geoparque_dashboard.py` |
| Deploy com Docker | `Dockerfile` + `docker-compose.yml` |
| Obter dados | `exemplo_download_dados.py` |

---

## 📞 Suporte

**Problemas?**
1. Veja troubleshooting em `QUICKSTART.md` (problemas comuns)
2. Consulte `GUIA_INSTALACAO.md` (problemas complexos)
3. Verifique `COMANDOS_UTEIS.md` (comandos específicos)

**Dúvidas sobre código?**
- Cada arquivo Python tem docstrings detalhados
- Consulte comentários inline

**Contribuir?**
- Veja seção "Contribuindo" em `README.md`

---

## 🎓 Ordem de Leitura Sugerida

**Para Iniciantes:**
1. README.md (visão geral)
2. QUICKSTART.md (começar)
3. Explorar o dashboard
4. GUIA_INSTALACAO.md (quando precisar de mais)

**Para Desenvolvedores:**
1. README.md (contexto)
2. GUIA_INSTALACAO.md (instalação completa)
3. geoparque_dashboard.py (código principal)
4. srtm_processor.py (processamento)
5. data_utils.py (APIs)
6. COMANDOS_UTEIS.md (referência)

**Para Deploy:**
1. GUIA_INSTALACAO.md (seção deploy)
2. Dockerfile + docker-compose.yml
3. COMANDOS_UTEIS.md (operações)

---

**Versão do Índice:** 1.0.0  
**Última atualização:** Fevereiro 2026

---

<p align="center">
  <strong>🏔️ Geoparque Prudentópolis - Conservação da Geodiversidade Brasileira</strong>
</p>
