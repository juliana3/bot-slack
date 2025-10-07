# Imagen base oficial de Python
FROM python:3.11-slim

# Define el directorio de trabajo
WORKDIR /app

# Copia los archivos de dependencias
COPY requirements.txt .

# Instala dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del proyecto
COPY . .

# Carga variables de entorno desde .env (opcional, solo si usás python-dotenv)
ENV PYTHONUNBUFFERED=1

# Expone el puerto (ajustá si tu app usa otro)
EXPOSE 5000

# Comando de inicio (para Flask, por ejemplo)
CMD ["python", "app.py"]
