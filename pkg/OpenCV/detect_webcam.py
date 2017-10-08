import imutils
import cv2


def maxRect(r1, r2, r3):
    minX = min(r1[0], r2[0], r3[0])
    minY = min(r1[1], r2[1], r3[1])
    maxX = max(r1[0] + r1[2], r2[0] + r2[2], r3[0] + r3[2])
    maxY = max(r1[1] + r1[3], r2[1] + r2[3], r3[1] + r3[3])

    return minX, minY, maxX - minX, maxY - minY


cap = cv2.VideoCapture(0)

while True:
    ret, rgb = cap.read()
    rgb = imutils.resize(rgb, height=400)
    gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)

    morphKernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    grad = cv2.morphologyEx(gray, cv2.MORPH_GRADIENT, morphKernel)

    _, bw = cv2.threshold(grad, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    morphKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
    connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, morphKernel)

    _, contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    hierarchy = hierarchy[0]

    mrz = []

    idx = 0
    while idx >= 0:
        (x, y, w, h) = cv2.boundingRect(contours[idx])

        r = (1.0 * w / h) if h != 0 else 0
        if w > connected.shape[1] * 0.6 and 13 < r < 17:
            mrz.append((x, y, w, h))
            cv2.rectangle(rgb, (x, y), (x + w, y + h), (0, 255, 0), 1)
        else:
            cv2.rectangle(rgb, (x, y), (x + w, y + h), (0, 0, 255), 1)

        idx = hierarchy[idx][0]

    if len(mrz) == 3:
        (x, y, w, h) = maxRect(mrz[0], mrz[1], mrz[2])
        cv2.imshow('ROI', rgb[y:y + h, x:x + w].copy())
        cv2.rectangle(rgb, (x, y), (x + w, y + h), (0, 255, 255), 3)

        roi = gray[y:y + h, x:x + w].copy()

    cv2.imshow('Webcam', rgb)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
