import cv2

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
    cv2.rectangle(
        frame,
        (rect_x, rect_y),
        (rect_x + rect_width, rect_y + rect_height),
        rect_color,
        border,
    )

    # smaller_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
