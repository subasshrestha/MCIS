import cv2
import os


def crop_face(image_path, destination_path):
    face_cascade = cv2.CascadeClassifier(os.path.join(os.getcwd(), 'haarcascade_frontalface_default.xml'))
    eye_cascade = cv2.CascadeClassifier(os.path.join(os.getcwd(), 'haarcascade_eye.xml'))
    img = cv2.imread(image_path)
    # plt.imshow(img)
    height = img.shape[0]
    width = img.shape[1]
    size = height * width

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    eyesn = 0
    for (x, y, w, h) in faces:
        imgCrop = img[y:y + h, x:x + w]
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = img[y:y + h, x:x + w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        for (ex, ey, ew, eh) in eyes:
            eyesn = eyesn + 1
            if eyesn >= 2:
                if not os.path.exists(destination_path):
                    os.makedirs(destination_path)
                cv2.imwrite(os.path.join(destination_path, '1.jpg'), imgCrop)
                return True
        return False
