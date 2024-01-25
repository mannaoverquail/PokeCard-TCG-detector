from flask import Flask, render_template, request, Response, redirect, url_for
import cv2
import imagehash
from PIL import Image
import pandas as pd
from urllib.parse import urlparse, parse_qs

from pokemontcgmanager.card import Card


# Helper Functions


def print_stats(card: dict):
    """
    Print basic statistics of a Pokémon card.

    Args:
        card (dict): Dictionary representing the Pokémon card.
    """
    print(
        card["id"],
        card["name"],
        card.get("cardmarket")["prices"]["averageSellPrice"],
        card.get("cardmarket")["updatedAt"],
    )


def get_hashes(img: dict) -> dict:
    """
    Calculate various types of hashes for an image.

    Args:
        img (PIL.Image): Image to calculate hashes for.

    Returns:
        dict: Dictionary with various hash types (perceptual, difference, wavelet, color).
    """
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


def adjust_query(query: str) -> str:
    """
    Adjusts the search query to ensure that 'name:"nombre"' format has the name in uppercase,
    or converts the name to uppercase if 'name:nombre' format is found.
    It also ensures that other Lucene operators remain unchanged.

    Args:
        query (str): The original search query.

    Returns:
        str: The adjusted search query with 'name:"NOMBRE"' format if 'name:"nombre"' format is found,
             or with 'name:NOMBRE' format if 'name:nombre' format is found, preserving other Lucene operators.
    """
    first_query = query.split()[0]
    if "name:" not in query and ":" not in first_query:
        query = query[0].upper() + query[1:]
        query = f"name:{query}"
    return query


card_hashes = pd.read_pickle("card_hashes_32b.pickle")


app = Flask(__name__)

img_height = 825
img_width = 600
aspect_ratio = img_height / img_width

rect_height = img_height // 2
rect_width = img_width // 2

# Initialize video capture
cap = cv2.VideoCapture(0)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * 1.4)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * 1.4)

rect_x = (width - rect_width) // 2
rect_y = (height - rect_height) // 2

rect_color = (0, 255, 0)
border = 2


def capture_image() -> Image or None:
    """
    Capture an image from the camera.

    Returns:
        PIL.Image or None: Captured image as a PIL Image or None if capture fails.
    """
    success, frame = cap.read()
    if success:
        frame = cv2.resize(frame, (0, 0), fx=1.4, fy=1.4)
        my_card_frame = frame[
            rect_y : rect_y + rect_height, rect_x : rect_x + rect_width
        ]
        my_card_img = Image.fromarray(my_card_frame)
        return my_card_img
    return None


def get_most_similar(img: Image, hash_type="perceptual", n=1):
    """
    Find the most similar Pokémon card based on image hash.

    Args:
        img (PIL.Image): Image to compare with the Pokémon card database.
        hash_type (str): Type of hash to use (perceptual, difference, wavelet, color).
        n (int): Number of similar cards to retrieve.

    Returns:
        str or list: ID(s) of the most similar Pokémon card(s).
    """
    hashes_dict = get_hashes(img)
    card_hashes["distance"] = card_hashes[hash_type] - hashes_dict[hash_type]
    card_hashes["distance"] = card_hashes["distance"].astype("int")
    if n > 1:
        min_rows = card_hashes["distance"].nsmallest(n).index
        similar_id = card_hashes.loc[min_rows, "id"].tolist()
    else:
        min_row = card_hashes["distance"].idxmin()
        similar_id = card_hashes.loc[min_row, "id"]

    return similar_id


# Routes and Views


@app.route("/")
def index():
    """
    Main route that displays the homepage.
    """
    return render_template("index.html")


@app.route("/detect_card")
def detect_card():
    return render_template("detector.html")


@app.route("/search", methods=["GET", "POST"])
def search_card():
    if request.method == "POST":
        search_query = request.form["search"]
        print(search_query)
        query = adjust_query(search_query)
        # Redirect to the '/cards?q={search_query}' route after submitting the form
        print(query)
        return redirect(url_for("cards", q=query))

    return render_template("search.html")


@app.route("/cards")
def cards():
    # check if there is any htmx request
    if request.headers.get("HX-Boosted") == "true":
        # get the target page from requests attributes
        page = int(request.args.get("target-page"))
        page = page if page > 0 else 1
        # get the url from the request
        url = request.headers.get("HX-Current-URL")

        # parse the url to get the query string
        parsed = urlparse(url)
        query_string = parse_qs(parsed.query)

        # get the search query from the query string
        search_query = query_string["q"][0]

        # get the page size from the query string
        page_size = query_string["page_size"][0] if "page_size" in query_string else 20

        response = Card.where(q=search_query, pageSize=page_size, page=page)
        # Check if there are more pages getting the first card of the next page
        last_card = page_size * page
        next_card = Card.where(q=search_query, pageSize=1, page=last_card + 1)
        last_page = len(next_card) == 0
        return render_template(
            "filtered_cards.html",
            cards=response,
            last_page=last_page,
            page=page,
        )

    search_query = request.args.get("q", None)
    page_size = request.args.get("page_size", 20)
    page = 1

    response = Card.where(q=search_query, pageSize=page_size, page=page)
    # Check if there are more pages getting the first card of the next page
    last_card = page_size * page
    next_card = Card.where(q=search_query, pageSize=1, page=last_card + 1)
    last_page = len(next_card) == 0

    return render_template(
        "filtered_cards.html",
        cards=response,
        last_page=last_page,
        page=page,
    )


@app.route("/card/<card_id>")
def card_page(card_id: str):
    response = Card.find(card_id)
    return render_template("card_page.html", pokemon=response)


@app.route("/about")
def about():
    return render_template("about.html")


# Functions for generating and streaming video frames


def generate_frames():
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/video_feed")
def video_feed():
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

            ret, buffer = cv2.imencode(".jpg", frame)
            if not ret:
                continue
            frame = buffer.tobytes()
            yield (b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    return Response(generate(), mimetype="multipart/x-mixed-replace; boundary=frame")


# Routes for comparing images and displaying similar Pokémon cards


@app.route("/perceptual_hash")
def perceptual():
    img = capture_image()
    if img is None:
        return Response(status=204)

    similar_id = get_most_similar(img, "perceptual")

    similar_card = Card.find(similar_id)

    print_stats(similar_card)

    # Provide htmx with the new card
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

    # Provide htmx with the new card
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

    # Provide htmx with the new card
    return (
        render_template(
            "pokemon_card.html",
            pokemon=similar_card,
        ),
        200,
    )


# Handling 404 errors


@app.errorhandler(404)
def not_found(e):
    """
    Error handler for not found (404) pages.
    """
    return render_template("404.html")


# Run the application if this script is executed
if __name__ == "__main__":
    app.run(debug=True)
