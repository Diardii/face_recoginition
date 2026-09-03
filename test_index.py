import cv2

for i in range(10):
    cap = cv2.VideoCapture(i, cv2.CAP_V4L2)
    print(f"Index {i}: {cap.isOpened()}")
    if cap.isOpened():
        ret, frame = cap.read()
        print("  Read:", ret)
    cap.release()
