FROM python:3.9

# Directorio de trabajo
WORKDIR /app

# Copiar archivos de la aplicación
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Puerto expuesto por la aplicación
EXPOSE 8000

# Comando para ejecutar la aplicación
CMD ["gunicorn", "app.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]

