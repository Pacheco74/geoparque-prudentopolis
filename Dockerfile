# Dockerfile para Geoparque Prudentópolis Dashboard
# Build: docker build -t geoparque-dashboard .
# Run: docker run -p 8501:8501 geoparque-dashboard

FROM python:3.10-slim

# Metadados
LABEL maintainer="Geoparque Prudentópolis"
LABEL description="Dashboard 3D de Topografia e Geodiversidade"
LABEL version="1.0.0"

# Definir diretório de trabalho
WORKDIR /app

# Variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema para bibliotecas geoespaciais
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (cache Docker)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install GDAL==$(gdal-config --version) && \
    pip install -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p data output temp

# Expor porta do Streamlit
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando para iniciar o dashboard
CMD ["streamlit", "run", "geoparque_dashboard.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true", \
     "--server.enableCORS=false", \
     "--server.enableXsrfProtection=false"]
