from flask import Flask, render_template, request, Response, redirect, url_for
import cv2
import numpy as np
import imagehash
from PIL import Image
from io import BytesIO
import requests
import pandas as pd

from pokemontcgmanager.card import Card


def print_stats(card):
    print(
        card["id"],
        card["name"],
        card.get("cardmarket")["prices"]["averageSellPrice"],
        card.get("cardmarket")["updatedAt"],
    )


def get_hashes(img):
    perceptual = imagehash.phash(img, 32, 8)
    difference = imagehash.dhash(img, 32)
    wavelet = imagehash.whash(img, 32)
    color = imagehash.colorhash(img)
    return {
        "perceptual": perceptual,
        "difference": difference,
        "wavelet": wavelet,
        "color": color,
    }


def get_img_by_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        img_data = BytesIO(response.content)
        image = cv2.imdecode(np.frombuffer(img_data.read(), np.uint8), cv2.IMREAD_COLOR)

    return image


app = Flask(__name__)

card_hashes = pd.read_pickle("card_hashes_32b.pickle")

img_height = 825
img_width = 600
aspect_ratio = img_height / img_width

rect_height = img_height // 2
rect_width = img_width // 2


# Inicializa la captura de video
cap = cv2.VideoCapture(0)


width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * 1.4)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * 1.4)

rect_x = (width - rect_width) // 2
rect_y = (height - rect_height) // 2

rect_color = (0, 255, 0)
border = 2


def capture_image():
    success, frame = cap.read()
    if success:
        frame = cv2.resize(frame, (0, 0), fx=1.4, fy=1.4)
        my_card_frame = frame[
            rect_y : rect_y + rect_height, rect_x : rect_x + rect_width
        ]
        # my_card_img = cv2.flip(my_card_img, 1)

        my_card_img = Image.fromarray(my_card_frame)
        return my_card_img
    return None


def get_most_similar(img: Image, hash_type="perceptual", n=1):
    hashes_dict = get_hashes(img)
    card_hashes["distance"] = card_hashes[hash_type] - hashes_dict[hash_type]
    card_hashes["distance"] = card_hashes["distance"].astype("int")
    if n > 1:
        min_rows = card_hashes["distance"].nsmallest(n).index
        # Obtain the filename
        similar_id = card_hashes.loc[min_rows, "id"].tolist()
    else:
        min_row = card_hashes["distance"].idxmin()
        # Obtain the filename
        similar_id = card_hashes.loc[min_row, "id"]

    return similar_id


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/detect_card")
def detect_card():
    return render_template("detector.html")


@app.route("/search", methods=["GET", "POST"])
def search_card():
    if request.method == "POST":
        search_query = request.form["search"]
        if ":" not in search_query:
            search_query = f"name:{search_query.title()}"
        parameter = search_query.split(":")[0]
        other = " ".join(search_query.split(":")[1:])
        other = f'"{other}"'
        query = f"{parameter}:{other}"
        # Redirige a la ruta '/cards?q={search_query}' después de enviar el formulario
        return redirect(url_for("cards", q=query))

    return render_template("search.html")


@app.route("/cards")
def cards():
    search_query = request.args.get("q", None)
    # Aquí puedes manejar el parámetro 'q' como desees, por ejemplo, buscar tarjetas
    # con la consulta 'search_query' y mostrar los resultados.
    response = Card.where(q=search_query, pageSize=20, page=1)
    return render_template("filtered_cards.html", cards=response)


@app.route("/card/<card_id>")
def card_page(card_id: str):
    response = Card.find(card_id)
    print(response)
    return render_template("card_page.html", pokemon=response)


@app.route("/about")
def about():
    return render_template("about.html")


def generate_frames():
    while True:
        # Captura un fotograma desde la cámara
        success, frame = cap.read()
        if not success:
            break
        else:
            # Realiza cualquier procesamiento de imagen necesario aquí
            # En este ejemplo, solo mostramos el fotograma capturado
            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/video_feed")
def video_feed():
    filter_type = request.args.get("filter")

    def generate():
        while True:
            success, frame = cap.read()
            frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (0, 0), fx=1.4, fy=1.4)
            cv2.rectangle(
                frame,
                (rect_x, rect_y),
                (rect_x + rect_width, rect_y + rect_height),
                rect_color,
                border,
            )
            if not success:
                break
            if filter_type == "grayscale":
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            elif filter_type == "blur":
                frame = cv2.GaussianBlur(frame, (15, 15), 0)

            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/perceptual_hash")
def perceptual():
    img = capture_image()
    if img is None:
        return Response(status=204)

    similar_id = get_most_similar(img, "perceptual")

    similar_card = Card.find(similar_id)

    print_stats(similar_card)

    # Give htmx the new card
    return (
        render_template(
            "pokemon_card.html",
            pokemon=similar_card,
        ),
        200,
    )


@app.route("/difference_hash")
def difference():
    img = capture_image()
    if img is None:
        return Response(status=204)

    similar_id = get_most_similar(img, "difference")

    similar_card = Card.find(similar_id)

    print_stats(similar_card)

    # Give htmx the new card
    return (
        render_template(
            "pokemon_card.html",
            pokemon=similar_card,
        ),
        200,
    )


@app.route("/wavelet_hash")
def wavelet():
    img = capture_image()
    if img is None:
        return Response(status=204)

    similar_id = get_most_similar(img, "wavelet")

    similar_card = Card.find(similar_id)

    print_stats(similar_card)

    # Give htmx the new card
    return (
        render_template(
            "pokemon_card.html",
            pokemon=similar_card,
        ),
        200,
    )


@app.route("/color_hash")
def color_hash():
    img = capture_image()
    if img is None:
        return Response(status=204)

    similar_cards = get_most_similar(img, "color", 10)

    similar_card_list = []
    for id in similar_cards:
        similar_card = Card.find(id)
        print_stats(similar_card)
        similar_card_list.append(similar_card)

    # Give htmx the new card
    return (
        render_template(
            "pokemon_card_list.html",
            pokemones=similar_card_list,
        ),
        200,
    )


# Errors


@app.errorhandler(404)
def not_found(e):  # inbuilt function which takes error as parameter
    # defining function
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True)
