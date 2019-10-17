from math import ceil

import base64
import cv2
import json
import numpy as np
import requests

API_key = "googleのAPIkey"

# api を叩いてレスポンスを受け取る関数
def request_cloud_vision_api(image_base64):
	GOOGLE_CLOUD_VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate?key='
	API_KEY = API_key
	api_url = GOOGLE_CLOUD_VISION_API_URL + API_KEY
	req_body = json.dumps({
		'requests': [{
			'image': {
				'content': image_base64.decode('utf-8')  # jsonに変換するためにstring型に変換する
			},
			'features': [{
				'type': 'DOCUMENT_TEXT_DETECTION',  # OCR mode
			}]
		}]
	})
	res = requests.post(api_url, data=req_body)
	return res.json()


def get_image_label(image_base64):
	GOOGLE_CLOUD_VISION_API_URL = 'https://vision.googleapis.com/v1/images:annotate?key='
	API_KEY = API_key
	api_url = GOOGLE_CLOUD_VISION_API_URL + API_KEY
	req_body = json.dumps({
		'requests': [{
			'image': {
				'content': image_base64.decode('utf-8')  # jsonに変換するためにstring型に変換する
			},
			'features': [{
				'type': 'OBJECT_LOCALIZATION',  # img label mode
			}]
		}]
	})
	res = requests.post(api_url, data=req_body)
	return res.json()


# 画像ファイルを開いて base64 に変換する関数
def img_to_base64(filepath):
	with open(filepath, 'rb') as img:
		img_byte = img.read()
	return base64.b64encode(img_byte)


# openCV で行った画像処理を base64 に変換する関数
def numpy_img_to_base64(img):
	res, dst_data = cv2.imencode('.jpg', img)
	dst_base64 = base64.b64encode(dst_data)
	return dst_base64


# Google Cloud Vision からOCR結果のjsonから座標情報を取得
def ocr_result_box_point(result):
	Data = {"allData": []}
	for res1 in result["responses"]:
		for res2 in res1["textAnnotations"]:
			data = {"description": res2["description"], "vertices": []}
			for res3 in res2["boundingPoly"]["vertices"]:
				data["vertices"].append(res3)
			Data["allData"].append(data)
	return Data


# 改行情報を含めた文章の取得
def res_block_grope(result):
	Data = {"allBlock": []}
	for res1 in result["responses"]:
		for res2 in res1["fullTextAnnotation"]["pages"]:
			for res3 in res2["blocks"]:
				data = {"description": {}, "direction": {},
				        "vertices": res3["boundingBox"]["vertices"]}
				vers = res3["boundingBox"]["vertices"]
				ren_x = max(vers[0]["x"], vers[1]["x"], vers[2]["x"], vers[3]["x"]) - min(
					vers[0]["x"], vers[1]["x"], vers[2]["x"], vers[3]["x"])
				ren_y = max(vers[0]["y"], vers[1]["y"], vers[2]["y"], vers[3]["y"]) - min(
					vers[0]["y"], vers[1]["y"], vers[2]["y"], vers[3]["y"])
				if ren_x > ren_y:
					data["direction"] = "Horizontal"
				else:
					data["direction"] = "Vertical"
				string = []
				for res4 in res3["paragraphs"]:
					for res5 in res4["words"]:
						for res6 in res5["symbols"]:
							string.append(res6["text"])
							if 'property' in res6:
								if 'detectedBreak' in res6["property"]:
									if res6["property"][
										"detectedBreak"][
										"type"] == "EOL_SURE_SPACE" or "LINE_BREAK":
										string.append("\n")
				strings = ''.join(string)
				data["description"] = strings
				Data["allBlock"].append(data)
	return Data


def table_block(result):
	Data = {"allWord": []}
	for res1 in result["responses"]:
		for res2 in res1["fullTextAnnotation"]["pages"]:
			for res3 in res2["blocks"]:
				for res4 in res3["paragraphs"]:
					for res5 in res4["words"]:
						for res6 in res5["symbols"]:
							if "confidence" in res6:
								if res6["confidence"] >= 0.45:
									data = {"description": res6["text"], "vertices": res6["boundingBox"]["vertices"]}
									Data["allWord"].append(data)
	return Data


# score  0~1の範囲で正当確率で取得制限
def result_img_label(res_json, score):
	Data = {"allLabel": []}
	if res_json["responses"][0] == {}:
		return Data
	for res1 in res_json["responses"]:
		for res2 in res1["localizedObjectAnnotations"]:
			if res2["score"] < score:
				continue
			data = {"name": res2["name"], "vertices": []}

			for res3 in res2["boundingPoly"]["normalizedVertices"]:
				data["vertices"].append(res3)
			Data["allLabel"].append(data)
	return Data


# OCRによって認識されたすべての文字列を返す関数
def ocr_result_text(result):
	result_text = result["responses"][0]["fullTextAnnotation"]["text"]
	return result_text


# openCV で処理をされた画像に認識された場所を可視化する
def ocr_cv_img_draw_poly(img):
	img_base64 = numpy_img_to_base64(img)
	result = request_cloud_vision_api(img_base64)
	poly_point = ocr_result_box_point(result)
	for i, poly1 in enumerate(poly_point["allData"]):
		poly_x = {}
		poly_y = {}
		for i2, poly2 in enumerate(poly_point["allData"][i]["vertices"]):
			poly_x[i2] = poly_point["allData"][i]["vertices"][i2]["x"]
			poly_y[i2] = poly_point["allData"][i]["vertices"][i2]["y"]
		pts = np.array((
			(poly_x[0], poly_y[0]),
			(poly_x[1], poly_y[1]),
			(poly_x[2], poly_y[2]),
			(poly_x[3], poly_y[3])
		))
		cv2.polylines(img, [pts], True, (0, 0, 0), thickness=2)
	return img


def Area_calculation(x, y):
	countX = 0
	countY = 0
	for i in range(0, 4):
		if i == 3:
			a = 1
		else:
			a = i + 1
			countX = countX + x[i] * y[a]
			countY = countY + x[a] * y[i]
	area = (countX - countY) / 2
	return area


def sort_large_judge(block):
	count = []
	for i, B1 in enumerate(block["allBlock"]):
		Coordinate_X = []
		Coordinate_Y = []
		for j, B2 in enumerate(block["allBlock"][i]["vertices"]):
			Coordinate_X.insert(j, block["allBlock"][i]["vertices"][j]["x"])
			Coordinate_Y.insert(j, block["allBlock"][i]["vertices"][j]["y"])
		length = len(block["allBlock"][i]["description"])
		Area = Area_calculation(Coordinate_X, Coordinate_Y)
		size = round((Area / length))
		block["allBlock"][i]["size"] = size
		count.insert(i, Area / length)
	block["allBlock"].sort(key=lambda x: x['size'], reverse=True)
	return block


def ins_score_block(shape, blocks):
	for i, B1 in enumerate(blocks["allBlock"]):
		x = 0
		y = 0
		for B2 in B1["vertices"]:
			x += B2["x"]
			y += B2["y"]
		x = round(x / 4)
		y = round(y / 4)
		if (shape[0] / y) >= 2:
			if 2.5 >= round(shape[1] / x) >= 4 / 3:
				blocks["allBlock"][i]["score"] = 1.5
			elif 4 >= round(shape[1] / x) >= 5 / 3:
				blocks["allBlock"][i]["score"] = 1
			else:
				blocks["allBlock"][i]["score"] = 0.5
		else:
			blocks["allBlock"][i]["score"] = 0
	return blocks


def judge_title(large_block):
	title = {}
	for x in range(5):
		score = large_block["allBlock"][x]["score"]
		if score == 0:
			continue
		if title == {}:
			title = large_block["allBlock"][x]
			continue
		size = large_block["allBlock"][x]["size"]
		if title["score"] <= score and title["size"] <= size:
			title = large_block["allBlock"][x]
	return title


def sort_new_line_judge(block):
	for i, B1 in enumerate(block["allBlock"]):
		lines = B1["description"].count("\n")
		high = []
		for j, B2 in enumerate(B1["vertices"]):
			high.append(B2["y"])
		high = sorted(high)
		high = round((high[3] - high[0]) / lines)
		block["allBlock"][i]["high"] = high
	block["allBlock"].sort(key=lambda x: x['high'], reverse=True)
	return block


# 画像が上向きだったらそのまま,逆だったら180度回転させたものを返す
def ocr_vertical_judge(img, poly_box):
	poly_ver_size = len(poly_box["allBlock"])
	half_line = (poly_box["allBlock"][0]["vertices"][0]["y"] +
	             poly_box["allBlock"][poly_ver_size - 1]["vertices"][3]['y']) // 2

	sum_top = 0
	sum_bottom = 0

	for i in range(poly_ver_size):
		top_coo = poly_box["allBlock"][i]["vertices"][0]
		bottom_coo = poly_box["allBlock"][i]["vertices"][2]

		if top_coo["y"] > half_line and bottom_coo['y'] < half_line:
			sum_top += (bottom_coo['x'] - top_coo) * (half_line - top_coo['y'])
			sum_bottom += (bottom_coo['x'] - top_coo['x']) * (bottom_coo['y'] - half_line)
		elif bottom_coo['y'] >= half_line:
			sum_top += (bottom_coo['x'] - top_coo['x']) * (bottom_coo['y'] - top_coo['y'])
		else:
			sum_bottom += (bottom_coo['x'] - top_coo['x']) * (bottom_coo['y'] - top_coo['y'])

	if sum_top >= sum_bottom:
		return img
	else:
		img_rotate_180 = cv2.rotate(img, cv2.ROTATE_180)
		return img_rotate_180


# 文字の羅列が横だったらそのまま、縦だったら90度回転させたものを返す
def ocr_cross_parity_ceck(img, poly_box):
	poly_ver_size = len(poly_box["allBlock"])

	# 縦方向vertical,横方向horizontal
	sum_ver = 0
	sum_hor = 0

	for i in range(1, poly_ver_size):
		length_hor = poly_box["allBlock"][i]["vertices"][2]['y'] - poly_box["allBlock"][i]["vertices"][0][
			'y']
		length_ver = poly_box["allBlock"][i]["vertices"][1]['x'] - poly_box["allBlock"][i]["vertices"][0][
			'x']

		if length_hor >= length_ver:
			++length_hor
		else:
			sum_ver

	# bounding boxの横が縦より長かったら横
	if sum_hor > sum_ver:
		return img
	else:
		img_rotate_90 = img.transpose(1, 0, 2)[:, ::-1]
		return img_rotate_90


def color_check(img):
	orgHeight, orgWidth = img.shape[:2]
	size = (ceil(orgWidth / 10), ceil(orgHeight / 10))
	halfImg = cv2.resize(img, size)
	cv2.imwrite("test.jpg", halfImg)
	colorList = []
	for A in halfImg:
		for B in A:
			tmp = B.tolist()
			tmp = [i - (i % 30) for i in tmp]
			if tmp not in colorList:
				colorList.append(tmp)
	return len(colorList)
