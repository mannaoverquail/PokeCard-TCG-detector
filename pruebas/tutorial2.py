import cv2
import random

img = cv2.imread("infernape-card.png", 1)
img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)

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
img = cv2.rectangle(img, (60, 10), (210, 50), (0, 255, 0), 2)
img = cv2.rectangle(img, (250, 10), (320, 50), (0, 255, 0), 2)

cv2.imshow("Image", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
