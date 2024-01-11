import cv2
import numpy as np
import os

pokeid = {"infernape V": "swshp-SWSH252", "gen1": ""}
url = os.path.join("downloaded_images", pokeid + ".png")
print("Leyendo imagen:", url)
img = cv2.imread(url, 1)
# img = cv2.imread("infernape-dp1-121.png", 1)
# img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)


# print(img)

# print(img.shape)

# blue, green, red

# for i in range(100):
#     for j in range(img.shape[1]):
#         blue = random.randint(0, 255)
#         green = random.randint(0, 255)
#         red = random.randint(0, 255)
#         img[i][j] = [blue, green, red]

# Draw a rectangle
# img = cv2.rectangle(img, (120, 20), (420, 100), (0, 255, 0), 2)
# img = cv2.rectangle(img, (500, 20), (640, 100), (0, 255, 0), 2)

# name = img[10:50, 60:210]

green = (0, 255, 0)
blue = (255, 0, 0)
red = (0, 0, 255)
white = (255, 255, 255)
black = (0, 0, 0)

# img = cv2.rectangle(img, (130, 30), (450, 90), (0, 255, 0), 2)
# name rectangle
img = cv2.rectangle(img, (0, 10), (450, 100), green, 2)
name = img[10:90, 0:450]

# hp rectangle
img = cv2.rectangle(img, (505, 11), (705, 100), blue, 2)

# type rectangle
type = cv2.rectangle(img, (637, 0), (730, 100), red, 2)

while True:
    cv2.imshow("Image", img)

    # print mouse position on image when clicked
    def click_event(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(x, ", ", y)

    cv2.setMouseCallback("Image", click_event)

    if cv2.waitKey(1) == ord("q"):
        break


cv2.destroyAllWindows()
