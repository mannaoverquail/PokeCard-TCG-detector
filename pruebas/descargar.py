import requests
import os


def descargar_imagen(url, nombre_archivo, carpeta_destino):
    try:
        # Realiza la solicitud HTTP GET para obtener la imagen
        respuesta = requests.get(url)
        respuesta.raise_for_status()  # Lanza una excepción si la solicitud no tiene éxito

        # Extrae el nombre del archivo de la URL
        nombre_archivo = os.path.join(carpeta_destino, nombre_archivo)

        # Guarda el contenido de la respuesta en un archivo local
        with open(nombre_archivo, "wb") as archivo:
            archivo.write(respuesta.content)

        print(f"Imagen descargada con éxito: {nombre_archivo}")
    except requests.exceptions.RequestException as e:
        print(f"Error al descargar la imagen: {e}")


if __name__ == "__main__":
    # URL de la imagen que deseas descargar
    url_imagen = "https://ejemplo.com/ejemplo.jpg"

    # Carpeta donde deseas guardar la imagen descargada
    carpeta_destino = "downloaded_imgs"

    # Crea la carpeta de destino si no existe
    os.makedirs(carpeta_destino, exist_ok=True)

    # Llama a la función para descargar la imagen
    descargar_imagen(url_imagen, carpeta_destino)
