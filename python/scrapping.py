# Hecho por Javier Muñoz
# Este programa busca scrapear el resultado del día de una página de resultados de fútbol

import requests
from bs4 import BeautifulSoup

# URL local de Live Server
URL = "http://127.0.0.1:5500/python/web_scrap/index.html"

def obtener_resultado_destacado(url):
    try:
        # Obtener el contenido HTML
        response = requests.get(url)
        response.raise_for_status()

        # Parsear el HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Buscar el marcador destacado
        marcador = soup.find(id="featured-score")

        if marcador:
            resultado = marcador.text.strip()
            equipo_local = marcador.get("data-home", "Equipo local")
            equipo_visitante = marcador.get("data-away", "Equipo visitante")
            print("🎯 Partido destacado:")
            print(f"🏠 {equipo_local} vs 🛫 {equipo_visitante}")
            print(f"📊 Resultado: {resultado}")
        else:
            print("❌ No se encontró el marcador destacado.")

    except requests.exceptions.RequestException as e:
        print("Error al acceder a la página: {e}")

# Ejecutar
if __name__ == "__main__":
    obtener_resultado_destacado(URL)