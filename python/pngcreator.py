# Hecho por Javier Muñoz
# Este programa crea una cantidad de imágenes introducidas por el usuario en la carpeta que el usuario decida

# Importo las librerías necesarias
import sys
import os
import random
import string

# Verificamos que se hayan pasado dos argumentos y que la cantidad sea válida
if len(sys.argv) != 3 or not sys.argv[2].isdigit() or int(sys.argv[2]) <= 0:
    print("Uso: python pngcreator.py <nombre_carpeta> <cantidad>")
    print("La cantidad debe ser un número entero positivo.")
    sys.exit(1)

# Asignamos los argumentos una vez validados
carpeta = sys.argv[1]
cantidad = int(sys.argv[2])

# Creamos la carpeta si no existe
os.makedirs(carpeta, exist_ok=True)

# Función para generar nombres únicos de 15 caracteres que no existan en disco ni en memoria
def generar_nombre_unico(carpeta, existentes):
    while True:
        nombre = ''.join(random.choices(string.ascii_letters + string.digits, k=15)) + ".png"
        ruta = os.path.join(carpeta, nombre)
        if nombre not in existentes and not os.path.exists(ruta):
            return nombre

nombres_creados = set()

# Creamos los archivos vacíos con nombres únicos
for _ in range(cantidad):
    nombre = generar_nombre_unico(carpeta, nombres_creados)
    ruta = os.path.join(carpeta, nombre)
    with open(ruta, 'wb') as f:
        f.write(b'')  # Archivo PNG vacío
    nombres_creados.add(nombre)

print(f"Se han creado {cantidad} archivos PNG únicos en la carpeta '{carpeta}'.")