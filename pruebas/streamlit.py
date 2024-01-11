import streamlit as st
import cv2
import imagehash
from PIL import Image
import os
import pandas as pd
import requests
from io import BytesIO
import numpy as np

from pokemontcgmanager.card import Card


# def get_img_by_url(url):
#     response = requests.get(url)
#     if response.status_code == 200:
#         img_data = BytesIO(response.content)
#         image = cv2.imdecode(np.frombuffer(img_data.read(), np.uint8), cv2.IMREAD_COLOR)

#     return image


def get_img_by_url(url: str) -> Image:
    response = requests.get(url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))

    return image


def get_hashes(img):
    perceptual = imagehash.phash(img)
    difference = imagehash.dhash(img)
    wavelet = imagehash.whash(img)
    return (perceptual, difference, wavelet)


def main():
    page_title = "Streamlit WebCam App"
    page_icon_url = r"https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.ajudandroid.com.br%2Fwp-content%2Fuploads%2F2016%2F04%2Fpokemon-trading-card-game-online.jpg&f=1&nofb=1&ipt=17193d4187d72c598de8f87062244f6b1c9dd91b7c8684d1e312c567de906890&ipo=images"
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon_url,
    )
    st.title("Webcam Display Steamlit App")
    st.caption("Powered by OpenCV, Streamlit")
    cap = cv2.VideoCapture(0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    rect_x = (width - rect_width) // 2
    rect_y = (height - rect_height) // 2

    rect_color = (0, 255, 0)
    border = 2
    frame_placeholder = st.empty()
    stop_button_pressed = st.button("Stop")
    get_detection_button_pressed = st.button("Get detection")
    while cap.isOpened() and not stop_button_pressed:
        ret, frame = cap.read()
        if not ret:
            st.write("Video Capture Ended")
            break

        # Edit frame properties to create rectangle
        # frame = cv2.resize(frame, (0, 0), fx=1.4, fy=1.4)
        frame = cv2.flip(frame, 1)
        cv2.rectangle(
            frame,
            (rect_x, rect_y),
            (rect_x + rect_width, rect_y + rect_height),
            rect_color,
            border,
        )
        # Adapt frame to streamlit
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # Display frame
        frame_placeholder.image(frame, channels="RGB")

        if cv2.waitKey(1) == ord("s") or get_detection_button_pressed:
            get_detection_button_pressed = False
            my_card_img = frame[
                rect_y : rect_y + rect_height, rect_x : rect_x + rect_width
            ]
            my_card_img = cv2.flip(my_card_img, 1)

            my_card_img = Image.fromarray(my_card_img)
            perceptual_hash, difference_hash, wavelet_hash = get_hashes(my_card_img)
            card_hashes["distance"] = card_hashes["perceptual"] - perceptual_hash
            card_hashes["distance"] = card_hashes["distance"].astype("int")
            min_row = card_hashes["distance"].idxmin()

            # Obtain the card id of the most similar card
            similar_id = card_hashes.loc[min_row, "id"]

            # Obtain the distance found to the image
            # distance = card_hashes.loc[min_row, "distance"]

            # Gets the card information from the API
            similar_card = Card.find(similar_id)

            print(
                similar_card["id"],
                similar_card["name"],
                similar_card["cardmarket"]["prices"]["averageSellPrice"],
                similar_card["cardmarket"]["updatedAt"],
            )
            col1, col2 = st.columns(2)
            with col2:
                st.write("Name", similar_card["name"])
                st.write(
                    "Price", similar_card["cardmarket"]["prices"]["averageSellPrice"]
                )
                st.write("Price updated at ", similar_card["cardmarket"]["updatedAt"])

            with col1:
                # Get the image of the card in the PIL format
                similar_card_img = get_img_by_url(similar_card["images"]["large"])
                # Display the image of the card found
                st.image(my_card_img, channels="RGB")

        if cv2.waitKey(1) & 0xFF == ord("q") or stop_button_pressed:
            break
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    img_height = 825
    img_width = 600
    aspect_ratio = img_height / img_width

    rect_height = img_height // 2
    rect_width = img_width // 2

    card_hashes = pd.read_pickle("card_hashes.pickle")
    main()
