import cv2
import msgpack

# import easyocr
import numpy as np
import imagehash
from PIL import Image, ImageEnhance, ImageFilter
import os
import pandas as pd

model_path = os.path.join(
    "ssd_mobilenet_v2_fpnlite_640x640_coco17_tpu-8", "saved_model"
)


def get_image_route(card_id: str):
    return os.path.join("downloaded_images", card_id + ".png")


def get_hashes(img):
    perceptual = imagehash.phash(img)
    difference = imagehash.dhash(img)
    wavelet = imagehash.whash(img)
    return (perceptual, difference, wavelet)


def most_similar_hash(img_hash, type="perceptual"):
    min_dif = min(abs(h - img_hash) for h in card_hashes[type])
    min_hash = [h for h in card_hashes[type] if abs(h - img_hash) == min_dif][0]
    return min_hash, min_dif


card_hashes = pd.read_pickle("card_hashes.pickle")


data_source = "cards.msgpack"
with open(data_source, "rb") as file:
    data = msgpack.load(file, raw=False)


img_height = 825
img_width = 600
aspect_ratio = img_height / img_width

rect_height = img_height // 2
rect_width = img_width // 2


cap = cv2.VideoCapture(0)


width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * 1.4)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * 1.4)

rect_x = (width - rect_width) // 2
rect_y = (height - rect_height) // 2

rect_color = (0, 255, 0)
border = 2


def enhance_image(img):
    # Convert to OpenCV format
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # Denoise the image
    denoised_img = cv2.fastNlMeansDenoisingColored(img_cv, None, 10, 10, 7, 21)

    # Convert back to PIL format
    img_pil = Image.fromarray(cv2.cvtColor(denoised_img, cv2.COLOR_BGR2RGB))

    # Enhance color
    enhancer = ImageEnhance.Color(img_pil)
    img_enhanced_color = enhancer.enhance(1.5)

    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img_enhanced_color)
    img_enhanced_contrast = enhancer.enhance(1.5)

    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(img_enhanced_contrast)
    img_enhanced_sharpness = enhancer.enhance(2)

    # Convert back to OpenCV format
    img_enhanced = cv2.cvtColor(np.array(img_enhanced_sharpness), cv2.COLOR_RGB2BGR)

    return img_enhanced


# Cargar la imagen de referencia (objeto)
imagen_referencia = cv2.imread(get_image_route("xy4-44"), cv2.IMREAD_GRAYSCALE)


while True:
    ret, frame = cap.read()
    frame = cv2.resize(frame, (0, 0), fx=1.4, fy=1.4)
    frame = cv2.flip(frame, 1)

    cv2.rectangle(
        frame,
        (rect_x, rect_y),
        (rect_x + rect_width, rect_y + rect_height),
        rect_color,
        border,
    )
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) == ord("s"):
        # img = frame[rect_y : rect_y + rect_height, rect_x : rect_x + rect_width]
        # imagen = cv2.flip(img, 1)

        # Cargar la imagen en la que deseas buscar el objeto
        imagen_busqueda = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Inicializar el detector ORB
        orb = cv2.ORB_create()

        # Encontrar los puntos clave y los descriptores en ambas imágenes
        keypoints_referencia, descriptores_referencia = orb.detectAndCompute(
            imagen_referencia, None
        )
        keypoints_busqueda, descriptores_busqueda = orb.detectAndCompute(
            imagen_busqueda, None
        )

        # Inicializar el detector de coincidencias
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

        # Realizar la coincidencia de descriptores
        coincidencias = bf.match(descriptores_referencia, descriptores_busqueda)

        # Ordenar las coincidencias por distancia (menor distancia es mejor)
        coincidencias = sorted(coincidencias, key=lambda x: x.distance)

        # Dibujar las coincidencias en la imagen de búsqueda
        imagen_coincidencias = cv2.drawMatches(
            imagen_referencia,
            keypoints_referencia,
            imagen_busqueda,
            keypoints_busqueda,
            coincidencias[:10],
            outImg=None,
        )

        # Mostrar la imagen con las coincidencias
        cv2.imshow("Coincidencias", imagen_coincidencias)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
