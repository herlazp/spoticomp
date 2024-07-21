# Usa la imagen base de Python
FROM python:3.8

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de requerimientos
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código del proyecto
COPY . .

# Establece el comando por defecto
CMD ["python", "app.py"]
