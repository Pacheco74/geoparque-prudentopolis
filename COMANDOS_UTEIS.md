# 🔧 Comandos Úteis e Troubleshooting Avançado

Este arquivo contém comandos úteis para desenvolvimento, deploy e resolução de problemas.

---

## 📦 Gerenciamento de Dependências

### Atualizar todas as bibliotecas
```bash
pip list --outdated
pip install --upgrade -r requirements.txt
```

### Gerar requirements.txt atualizado
```bash
pip freeze > requirements-freeze.txt
```

### Instalar versões específicas
```bash
pip install streamlit==1.31.0 pydeck==0.8.1 plotly==5.18.0
```

### Limpar cache do pip
```bash
pip cache purge
```

---

## 🐳 Docker

### Build da imagem
```bash
docker build -t geoparque-dashboard:latest .
```

### Build com cache limpo
```bash
docker build --no-cache -t geoparque-dashboard:latest .
```

### Executar container
```bash
docker run -d \
  --name geoparque \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  geoparque-dashboard:latest
```

### Logs do container
```bash
docker logs -f geoparque
```

### Acessar shell do container
```bash
docker exec -it geoparque /bin/bash
```

### Parar e remover
```bash
docker stop geoparque
docker rm geoparque
```

### Docker Compose
```bash
# Iniciar serviços
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar serviços
docker-compose down

# Rebuild após mudanças
docker-compose up -d --build
```

---

## 🚀 Deploy

### Heroku

```bash
# Login
heroku login

# Criar app
heroku create geoparque-prudentopolis

# Configurar buildpack
heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-apt
heroku buildpacks:add --index 2 heroku/python

# Deploy
git push heroku main

# Ver logs
heroku logs --tail

# Configurar variáveis de ambiente
heroku config:set MAPBOX_ACCESS_TOKEN=pk.eyJ...
```

### Streamlit Cloud

```bash
# 1. Fazer push para GitHub
git add .
git commit -m "Initial commit"
git push origin main

# 2. Acessar https://share.streamlit.io/
# 3. Conectar repositório
# 4. Configurar secrets em Settings > Secrets:
```

```toml
# .streamlit/secrets.toml
[mapbox]
access_token = "pk.eyJ..."

[settings]
center_lat = -25.1973
center_lon = -50.9780
```

### AWS EC2

```bash
# Conectar via SSH
ssh -i key.pem ubuntu@ec2-instance.amazonaws.com

# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Clonar repositório
git clone https://github.com/user/geoparque.git
cd geoparque

# Executar
docker-compose up -d

# Configurar firewall
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 8501
```

---

## 🔍 Troubleshooting Avançado

### Problema: GDAL não instala

**Windows:**
```bash
# Baixar wheel pré-compilado
# https://www.lfd.uci.edu/~gohlke/pythonlibs/

pip install GDAL-3.4.3-cp310-cp310-win_amd64.whl
```

**macOS:**
```bash
brew install gdal
export CPLUS_INCLUDE_PATH=/usr/local/include
export C_INCLUDE_PATH=/usr/local/include
pip install GDAL==$(gdal-config --version)
```

**Linux:**
```bash
sudo add-apt-repository ppa:ubuntugis/ppa
sudo apt update
sudo apt install gdal-bin libgdal-dev
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip install GDAL==$(gdal-config --version)
```

### Problema: Streamlit travando

```bash
# Limpar cache
streamlit cache clear

# Executar com debug
streamlit run geoparque_dashboard.py --logger.level=debug

# Aumentar limites de memória
streamlit run geoparque_dashboard.py \
  --server.maxUploadSize=200 \
  --server.maxMessageSize=200
```

### Problema: PyDeck não renderiza

**Verificar WebGL:**
```javascript
// Abrir console do navegador (F12)
// Cole e execute:
var canvas = document.createElement('canvas');
var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
if (gl && gl instanceof WebGLRenderingContext) {
  console.log('WebGL habilitado!');
} else {
  console.log('WebGL NÃO disponível');
}
```

**Forçar renderização CPU:**
```python
# Em geoparque_dashboard.py
r = pdk.Deck(
    layers=layers,
    initial_view_state=view_state,
    map_provider='carto',  # Alternativa ao Mapbox
    map_style='dark'
)
```

### Problema: Memória insuficiente

```python
# Processar dados em chunks
def process_large_file(filepath, chunk_size=10000):
    chunks = []
    for chunk in pd.read_csv(filepath, chunksize=chunk_size):
        # Processar chunk
        processed = process_chunk(chunk)
        chunks.append(processed)
    return pd.concat(chunks)
```

### Problema: API rate limit excedido

```python
import time
from functools import wraps

def rate_limit(max_per_second):
    min_interval = 1.0 / max_per_second
    def decorator(func):
        last_called = [0.0]
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = min_interval - elapsed
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator

@rate_limit(10)  # 10 requisições por segundo
def get_elevation(lat, lon):
    # ...
```

---

## 🧪 Testes

### Teste manual básico
```bash
python -c "
import streamlit
import pydeck
import plotly
print('Todas as bibliotecas principais OK!')
"
```

### Teste de GDAL
```bash
python -c "
from osgeo import gdal
print(f'GDAL version: {gdal.__version__}')
"
```

### Teste de dados SRTM
```python
from srtm_processor import load_srtm_data

df = load_srtm_data('data/test.tif')
print(f"Loaded {len(df)} points")
print(df.head())
```

### Benchmark de performance
```python
import time

# Em geoparque_dashboard.py, adicione:
start = time.time()
elevation_df = generate_elevation_data(grid_size=100)
print(f"Tempo: {time.time() - start:.2f}s")
```

---

## 📊 Monitoramento

### Uso de recursos
```bash
# CPU e memória do container
docker stats geoparque

# Logs com timestamp
docker logs -f --timestamps geoparque

# Top processos no container
docker top geoparque
```

### Streamlit stats
```python
# Adicionar em geoparque_dashboard.py
import psutil

with st.sidebar:
    st.markdown("### 📊 System Stats")
    st.text(f"CPU: {psutil.cpu_percent()}%")
    st.text(f"RAM: {psutil.virtual_memory().percent}%")
```

---

## 🔐 Segurança

### Gerar secrets seguros
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### HTTPS com Let's Encrypt (produção)
```bash
sudo apt install certbot python3-certbot-nginx

sudo certbot --nginx -d geoparque.example.com

# Auto-renovação
sudo certbot renew --dry-run
```

### Configuração Nginx segura
```nginx
# nginx/nginx.conf
server {
    listen 80;
    server_name geoparque.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name geoparque.example.com;
    
    ssl_certificate /etc/letsencrypt/live/geoparque.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/geoparque.example.com/privkey.pem;
    
    location / {
        proxy_pass http://dashboard:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 💾 Backup

### Backup de dados
```bash
# Criar backup
tar -czf backup_$(date +%Y%m%d).tar.gz data/ output/

# Restaurar
tar -xzf backup_20240101.tar.gz
```

### Backup do banco (se houver)
```bash
# PostgreSQL
pg_dump -h localhost -U user dbname > backup.sql

# Restaurar
psql -h localhost -U user dbname < backup.sql
```

---

## 🔄 Atualizações

### Atualizar código em produção
```bash
# Pull últimas mudanças
git pull origin main

# Rebuild containers
docker-compose down
docker-compose up -d --build

# Ou com zero-downtime:
docker-compose up -d --no-deps --build dashboard
```

### Rollback para versão anterior
```bash
# Git
git log --oneline
git checkout <commit-hash>

# Docker
docker tag geoparque-dashboard:latest geoparque-dashboard:backup
docker pull geoparque-dashboard:v1.0.0
docker-compose up -d
```

---

## 📞 Suporte

### Logs centralizados
```bash
# Salvar logs
docker logs geoparque > logs/app_$(date +%Y%m%d).log

# Analisar erros
grep ERROR logs/app_*.log
```

### Debugging remoto
```python
# Em geoparque_dashboard.py
import pdb; pdb.set_trace()  # Breakpoint

# Ou com remote debugging
import debugpy
debugpy.listen(5678)
print("Aguardando debugger...")
debugpy.wait_for_client()
```

---

**Mantenha este arquivo atualizado com novos comandos úteis!**
