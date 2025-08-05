# Imagen base oficial de PostgreSQL
FROM postgres:15

# Variables de entorno para crear base de datos y usuario automáticamente
ENV POSTGRES_DB=mydatabase
ENV POSTGRES_USER=myuser
ENV POSTGRES_PASSWORD=mypassword

# Copiar un script SQL inicial si lo tienes
# (por ejemplo, para crear tablas automáticamente)
# Se ejecutará al iniciar el contenedor por primera vez
#COPY init.sql /docker-entrypoint-initdb.d/

# Exponer el puerto por defecto de PostgreSQL
EXPOSE 5432
