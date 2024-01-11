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


my_img = cv2.imread("chimchar.jpg")
cv2.imshow("original", my_img)


gray = cv2.cvtColor(my_img, cv2.COLOR_BGR2GRAY)
cv2.imshow("grayscale", gray)

# convert to binary image
ret, thresh = cv2.threshold(gray, 125, 255, cv2.THRESH_BINARY)
cv2.imshow("threshold", thresh)


# increase contrast by 1.5 with opencv
contrast = cv2.convertScaleAbs(gray, alpha=1.5, beta=0)
# cv2.imshow("contrast", contrast)
# convert to binary image
ret, thresh = cv2.threshold(contrast, 135, 255, cv2.THRESH_BINARY)
cv2.imshow("threshold contrast", thresh)


cv2.waitKey(0)
cv2.release()
cv2.destroyAllWindows()
