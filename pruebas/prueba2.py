import cv2
import msgpack

# import easyocr
import numpy as np
import imagehash
from PIL import Image, ImageEnhance, ImageFilter
import os
import pandas as pd


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


def encontrar_contorno_carta(contornos):
    # Suponiendo que la carta será uno de los contornos más grandes en la imagen
    # Puedes ajustar esto según sea necesario
    contorno_carta = max(contornos, key=cv2.contourArea)
    return contorno_carta


def preprocess_img(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bkg_level = gray[100, 100]
    thresh_level = bkg_level  # ajustar según sea necesario
    retval, thresh_image = cv2.threshold(gray, thresh_level, 255, cv2.THRESH_BINARY)

    return thresh_image


# def find_cards(thresh):
#     cnts, hier = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
#     index_sort = sorted(range(len(cnts)), key=lambda i : cv2.contourArea(cnts[i]), reverse=True)

#     if len(cnts) == 0:
#         return [], []

#     cnts_sort = []
#     hier_sort = []
#     cnt_is_card = np.zeros(len(cnts),dtype=int)

#     for i in index_sort:
#         cnts_sort.append(cnts[i])
#         hier_sort.append(hier[0][i])

#     for i in range(len(cnts_sort)):
#         size = cv2.contourArea(cnts_sort[i])
#         peri = cv2.arcLength(cnts_sort[i],True)
#         approx = cv2.approxPolyDP(cnts_sort[i], 0.01*peri, True)

#         if size < CARD_MAX_AREA and size > CARD_MIN_AREA\
#             and hier_sort[i][3] == -1 and len(approx) == 4:
#             cnt_is_card[i] = 1

#     return cnts_sort, cnt_is_card


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
        img = frame[rect_y : rect_y + rect_height, rect_x : rect_x + rect_width]
        imagen = cv2.flip(img, 1)

        treshold_image = preprocess_img(imagen)

        # Encontrar contornos basados en los bordes detectados
        contornos, _ = cv2.findContours(
            treshold_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Puedes dibujar los contornos en la imagen para visualizarlos
        # imagen_contornos = imagen.copy()
        cv2.drawContours(treshold_image, contornos, -1, (0, 255, 0), 3)
        # Filtrar y encontrar el contorno de la carta
        # contorno_carta = encontrar_contorno_carta(contornos)

        # Recortar la imagen usando el contorno de la carta
        # x, y, w, h = cv2.boundingRect(contorno_carta)
        # carta_recortada = imagen[y : y + h, x : x + w]

        # Mostrar la carta recortada
        # cv2.imshow("Carta Recortada", carta_recortada)
        cv2.imshow("Contornos", treshold_image)
    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
