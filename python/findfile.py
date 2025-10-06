# Hecho por Javier Muñoz
# Este programa busca cuántas veces aparece una palabra en un archivo de texto

#Importa la librería necesaria
import sys

# Verificamos que se hayan pasado los argumentos correctamente
if len(sys.argv) != 3:
    print("Uso: python findfile.py <archivo> <palabra>")
    sys.exit(1)

archivo = sys.argv[1]
palabra = sys.argv[2]
contador = 0

# Abrimos el archivo y contamos las apariciones de la palabra
try:
    with open(archivo, 'r', encoding='utf-8') as f:
        for linea in f:
            contador += linea.count(palabra)

    print(f"{palabra} : {contador}")

# Manejamos errores si el archivo no se encuentra o hay otro problema
except FileNotFoundError:
    print(f"El archivo '{archivo}' no se encontró.")
except Exception as e:
    print(f"Ocurrió un error: {e}")