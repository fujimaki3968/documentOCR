import sys

import math
import cv2
import numpy as np
import ocrFunction as ocrFun

# mode 判別
args = sys.argv
if len(args) != 2:
		print("エラー\nmode一覧\nchcktext  : OCRを行って認識できた文字列を出力する\ndrawpoly  : どこが認識されたかを可視化する          ")
		exit()

if args[1] == "checktext":
		path = input("sample_imgに入っている画像の名前: ")
		Path = "../sample_img/{0}".format(path)
		img64 = ocrFun.img_to_base64(Path)
		res_json = ocrFun.request_cloud_vision_api(img64)
		fullText = ocrFun.ocr_result_text(res_json)

elif args[1] == "drawpoly":
		path = input("sample_imgに入っている画像の名前: ")
		Path = "../sample_img/{0}".format(path)
		img64 = ocrFun.img_to_base64(Path)
		img = cv2.imread(Path)
		res_json = ocrFun.request_cloud_vision_api(img64)
		file = open("test.json", "w")
		file.write(str(res_json))
		file.close()
		# print(res_json)
		poly_point = ocrFun.table_block(res_json)
		poly_box = ocrFun.res_block_grope(res_json)
		get_label = ocrFun.get_image_label(img64)
		label = ocrFun.result_img_label(get_label, 0.5)

		for i, poly1 in enumerate(poly_point["allWord"]):
				if i == 0:
						continue
				poly_x = {}
				poly_y = {}
				for i2, poly2 in enumerate(poly1["vertices"]):
						poly_x[i2] = poly2["x"]
						poly_y[i2] = poly2["y"]
				pts = np.array((
						(poly_x[0], poly_y[0]),
						(poly_x[1], poly_y[1]),
						(poly_x[2], poly_y[2]),
						(poly_x[3], poly_y[3])
				))
				cv2.polylines(img, [pts], True, (0, 0, 0), thickness=1)

		for poly1 in poly_box["allBlock"]:
				poly_x = {}
				poly_y = {}
				for i2, poly2 in enumerate(poly1["vertices"]):
						poly_x[i2] = poly2["x"]
						poly_y[i2] = poly2["y"]
				pts = np.array((
						(poly_x[0], poly_y[0]),
						(poly_x[1], poly_y[1]),
						(poly_x[2], poly_y[2]),
						(poly_x[3], poly_y[3])
				))
				cv2.polylines(img, [pts], True, (0, 255, 0), thickness=2)

		for im1 in label["allLabel"]:
				lab_x = {}
				lab_y = {}
				for i2, im2 in enumerate(im1["vertices"]):
						lab_x[i2] = math.ceil(im2["x"] * img.shape[1])
						lab_y[i2] = math.ceil(im2["y"] * img.shape[0])
				pts = np.array((
						(lab_x[0], lab_y[0]),
						(lab_x[1], lab_y[1]),
						(lab_x[2], lab_y[2]),
						(lab_x[3], lab_y[3]),
				))
				cv2.polylines(img, [pts], True, (0, 0, 255), thickness=2)
				font = cv2.FONT_HERSHEY_SIMPLEX
				cv2.putText(img, im1["name"], (lab_x[3], lab_y[3]), font, 2, (0, 0, 255), 2, cv2.LINE_AA)

		cv2.imwrite("result.jpg", img)
		# print("画像保存完了")

else:
		print("エラー\nmode一覧\nchcktext  : OCRを行って認識できた文字列を出力する\ndrawpoly  : どこが認識されたかを可視化する          ")
		exit()


