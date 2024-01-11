import cv2
import msgpack

# import easyocr
import imagehash
from PIL import Image
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
    min_dist = min(code - img_hash for code in card_hashes[type])
    min_hash = [h for h in card_hashes[type] if h - img_hash == min_dist][0]
    return min_hash, min_dist


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
        my_card_img = frame[rect_y : rect_y + rect_height, rect_x : rect_x + rect_width]
        my_card_img = cv2.flip(my_card_img, 1)

        my_card_img = Image.fromarray(my_card_img)
        perceptual_hash, difference_hash, wavelet_hash = get_hashes(my_card_img)
        card_hashes["distance"] = card_hashes["perceptual"] - perceptual_hash
        card_hashes["distance"] = card_hashes["distance"].astype("int")
        min_row = card_hashes["distance"].idxmin()

        # Obtain the filename
        similar_id = card_hashes.loc[min_row, "id"]
        distance = card_hashes.loc[min_row, "distance"]

        # similar_hash, difference = most_similar_hash(perceptual_hash)
        # similar_id = card_hashes[
        #     card_hashes["perceptual"] == similar_hash
        # ].reset_index()["id"][0]

        similar_card = [card for card in data if card["id"] == similar_id][0]
        print(similar_card["name"], similar_card["id"], distance)

        similar_card_img = cv2.imread(get_image_route(similar_card["id"]))
        similar_card_img = cv2.resize(similar_card_img, (0, 0), fx=0.5, fy=0.5)
        cv2.imshow("Detection", similar_card_img)

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
