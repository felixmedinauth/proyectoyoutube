# Proyecto YouTube 2026

Aplicación Django para gestionar subidas a YouTube con autenticación OAuth.

## Requisitos mínimos

- Python 3.8+
- pip

## Instalación rápida

```bash
# 1. Crear ambiente virtual
python -m venv venv

# 2. Activar ambiente
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Instalar dependencias (minimalista, ~50 MB)
pip install -r requirements.txt

# 4. Ejecutar migraciones
python manage.py migrate

# 5. Iniciar servidor
python manage.py runserver
```

## Tamaño del proyecto

- **Código fuente**: ~8 MB
- **requirements.txt**: 7 paquetes principales
- **Ambiente virtual instalado**: ~100-150 MB (NO incluido en repo)
- **Tamaño en GitHub**: <10 MB (código puro)

## Dependencias principales

- Django 5.1+
- Google API Python Client (YouTube)
- Google Auth & OAuth
- MySQL driver (mysqlclient)
- Requests + urllib3 (HTTP)

## Notas

- `.gitignore` previene que se suban: venv/, __pycache__, .pyc, db.sqlite3
- requirements.txt usa versiones específicas para minimizar resolución de pip
- No incluye paquetes innecesarios (tqdm, pydantic, sqlparse, etc.)
