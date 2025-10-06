# Hecho por Javier Muñoz
# Este programa imprime el codigo de otro archivo, enumerando cada línea y marcando la cantidad de print utilizados

# Importamos la librería necesaria para acceder a los argumentos del sistema
import sys

# Verificamos que el comando tenga el número correcto de argumentos
if len(sys.argv) != 2:
    print("Uso correcto: python typef.py <archivo.py>")
    sys.exit(1)

# Obtenemos el nombre del archivo desde los argumentos y inicializamos el contador de 'print'
archivo = sys.argv[1]
contador_print = 0

# Abrimos el archivo y mostramos su contenido línea por línea, numerando cada una
# También contamos cuántas veces aparece la palabra 'print'
try:
    with open(archivo, 'r', encoding='utf-8') as f:
        for i, linea in enumerate(f, start=1):
            print(f"{i:03d}: {linea}", end='')
            if 'print' in linea:
                contador_print += 1

    # Mostramos el total de líneas que contienen 'print'
    print(f"\nHubo {contador_print} print en el archivo.")

# Manejamos el caso en que el archivo no exista
except FileNotFoundError:
    print(f"El archivo '{archivo}' no se encontró.")

# Manejamos cualquier otro tipo de error
except Exception as e:
    print(f"Ocurrió un error: {e}")