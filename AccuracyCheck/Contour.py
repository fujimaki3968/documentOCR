import numpy as np
import cv2
from matplotlib import pyplot as plt

# path = input("sample_imgに入っている画像の名前: ")
Path = "../sample_img/test.jpg"
img = cv2.imread(Path)

gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

(thresh, im_bw) = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
thresh = 127
im_bw = cv2.threshold(gray, thresh, 255, cv2.THRESH_BINARY)[1]
ksize = 51
blur = cv2.blur(gray, (ksize, ksize))
rij = gray/blur
index_1 = np.where(rij >= 0.98)
index_0 = np.where(rij < 0.98)
rij[index_0] = 0
rij[index_1] = 1
RIJ = rij*255
cv2.imwrite("rij_image.png", RIJ)

delshadow = cv2.imread("rij_image.png")
result = cv2.Canny(delshadow,80,90)
cv2.imwrite("result.jpg", result)
