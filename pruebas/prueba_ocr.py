import cv2
import msgpack

import easyocr
import imagehash
from PIL import Image
import os
import pandas as pd

reader = easyocr.Reader(["en"], gpu=True)


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


def tresh_image(img):
    gray = cv2.cvtColor(cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur((5, 5))


def get_detections(image):
    detections = reader.readtext(image)
    treshold = 0.5
    for d in detections:
        bbox, text, score = d

        # if score > treshold:
        #     print(f"Text: {text}, Score: {score}")
    return [d for d in detections if d[2] > treshold]


def normalize_text(text):
    # Remove all non-ascii characters
    text = "".join(i for i in text if ord(i) < 128)
    # Remove all non-alphanumeric characters (except spaces)
    text = "".join(i for i in text if i.isalnum() or i == " ")
    # Remove all leading and trailing whitespace
    text = text.strip()
    # Remove any consecutive spaces
    text = " ".join(text.split())
    return text


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
        # create a rect with width of half of the rect and height of the 10% of the rect
        # this rect will be used to crop the image
        frame = cv2.flip(frame, 1)
        my_card_img = frame[
            rect_y : rect_y + rect_height // 7, rect_x : rect_x + rect_width
        ]
        # my_card_img = cv2.flip(my_card_img, 1)
        detections = get_detections(my_card_img)
        if len(detections) == 0:
            print("No text detected")
            continue
        best_detection = sorted(detections, key=lambda x: x[2], reverse=True)[0]
        print(best_detection)

        bbox, text, score = best_detection
        if text.isdigit():
            possible_elections_id = [card["id"] for card in data if card["hp"] == text]
        else:
            text = normalize_text(text)
            if "Poke" in text:
                text = text.replace("Poke", "Poké")
            possible_elections_id = [
                card["id"] for card in data if text in card["name"]
            ]
        if len(possible_elections_id) > 0:
            possible_elections_df = card_hashes[
                card_hashes["id"].isin(possible_elections_id)
            ].copy()
        else:
            print("No card found with that name")
            possible_elections_df = card_hashes.copy()
        # bbox = [int(x) for x in bbox]
        # cv2.rectangle(my_card_img, bbox[0], bbox[2], (0, 255, 0), 5)
        # cv2.putText(
        #     my_card_img, text, (bbox[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 0, 0), 2
        # )

        # cv2.imshow("Detection", my_card_img)

        my_card_img = frame[rect_y : rect_y + rect_height, rect_x : rect_x + rect_width]
        my_card_img = cv2.flip(my_card_img, 1)

        my_card_img = Image.fromarray(my_card_img)
        perceptual_hash, difference_hash, wavelet_hash = get_hashes(my_card_img)
        possible_elections_df["distance"] = (
            possible_elections_df["perceptual"] - perceptual_hash
        )
        possible_elections_df["distance"] = possible_elections_df["distance"].astype(
            "int"
        )
        print(possible_elections_df.head(20))
        min_row = possible_elections_df["distance"].idxmin()

        # Obtain the filename
        similar_id = possible_elections_df.loc[min_row, "id"]
        distance = possible_elections_df.loc[min_row, "distance"]

        # similar_hash, difference = most_similar_hash(perceptual_hash)
        # similar_id = possible_elections_df[
        #     possible_elections_df["perceptual"] == similar_hash
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
