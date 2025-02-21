# Usa una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /backend

# Copia los archivos de tu aplicación al contenedor
COPY . .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que corre tu aplicación
EXPOSE 8000

# Comando para correr tu aplicación
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]