from math import ceil

import cv2
import json
import numpy as np
import ocrFunction as ocrFun
from math import floor


# 邪魔な文字を削除して数字ならTRUE
def is_num(s):
	return s.replace(',', '').replace('.', '').replace('-', '').replace('|', '').isnumeric()


def check_list(point_list, TF):
	dup = [x for x in set(point_list) if point_list.count(x) > 1]
	if TF:
		length = len(dup)
		if length == 2:
			return True
		else:
			return False
	else:
		return dup


Path = "../sample_img/sample15.png"
img = cv2.imread(Path)
secimg = cv2.imread(Path)
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
img64 = ocrFun.img_to_base64(Path)
res_json = ocrFun.request_cloud_vision_api(img64)
file_json = open("response.json", "w")
json.dump(res_json, file_json, indent=4)
res_blo = ocrFun.table_block(res_json)

t = 200
ret, th2 = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY)

edges = cv2.Canny(th2, 1, 100, apertureSize=3)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
edges = cv2.dilate(edges, kernel)
# 輪郭抽出
contours, hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
# 面積でフィルタリング
rects = []
for cnt, hrchy in zip(contours, hierarchy[0]):
	if cv2.contourArea(cnt) < 900:
		continue  # 面積が小さいものは除く
	if hrchy[3] == -1:
		continue  # ルートノードは除く
	# 輪郭を囲む長方形を計算する。
	rect = cv2.minAreaRect(cnt)
	rect_points = cv2.boxPoints(rect).astype(int)

	rect_x = [x[0] for x in rect_points]
	rect_y = [y[1] for y in rect_points]
	if check_list(rect_x, True) & check_list(rect_y, True):  # 斜めの矩形を除外
		rects.append(rect_points)

# x-y 順でソート
rects = sorted(rects, key=lambda x: (x[0][1], x[0][0]))

# 描画する.
for i, rect in enumerate(rects):
	rect_x = np.sort(check_list([x[0] for x in rect], False))
	rect_y = np.sort(check_list([y[1] for y in rect], False))
	Rect = np.array([
		(rect_x[0] - 5, rect_y[0]),
		(rect_x[1] + 5, rect_y[0]),
		(rect_x[1] + 5, rect_y[1] + 3),
		(rect_x[0] - 5, rect_y[1] + 3),
	])
	rect_dup = np.array([rect_x, rect_y])
	color = np.random.randint(0, 255, 3).tolist()
	cv2.fillPoly(img, [Rect], (255, 255, 0))  # セルを同色で塗りつぶす

cv2.imwrite("fillimg.png", img)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

t = 200
ret, th2 = cv2.threshold(gray, t, 255, cv2.THRESH_BINARY)

edges = cv2.Canny(th2, 1, 100, apertureSize=3)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
edges = cv2.dilate(edges, kernel)
# 輪郭抽出
Contours, Hierarchy = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
Rects = []

for Cnt, Hrchy in zip(Contours, Hierarchy[0]):
	if cv2.contourArea(Cnt) < 4000:
		continue  # 面積が小さいものは除く
	if Hrchy[3] == -1:
		continue  # ルートノードは除く
	# 輪郭を囲む長方形を計算する。
	rect = cv2.minAreaRect(Cnt)
	rect_points = cv2.boxPoints(rect).astype(int)
	rect_x = [x[0] for x in rect_points]
	rect_y = [y[1] for y in rect_points]
	if check_list(rect_x, True) & check_list(rect_y, True):
		Rects.append(rect_points)

image2 = cv2.imread(Path)

for i, rect in enumerate(rects):
	color = np.random.randint(0, 255, 3).tolist()
	cv2.drawContours(image2, rects, i, color, 2)
	cv2.putText(image2, str(i), tuple(rect[0]), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1)

for i, rect in enumerate(Rects):
	# color = np.random.randint(0, 255, 3).tolist()
	cv2.drawContours(image2, Rects, i, (0, 0, 0), 7)
	cv2.putText(image2, str(i), tuple(rect[0]), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 100, 255), 5)

cv2.imwrite('image.png', image2)

table_list = []
for B1 in Rects:
	list = {"table_vert": B1.tolist(), "cells": []}
	table_X = np.sort(check_list([x[0] for x in B1], False))
	table_Y = np.sort(check_list([y[1] for y in B1], False))
	for B2 in rects:
		cell_X = np.sort(check_list([x[0] for x in B2], False))
		cell_Y = np.sort(check_list([y[1] for y in B2], False))
		cenX = (cell_X[0] + cell_X[1]) / 2
		cenY = (cell_Y[0] + cell_Y[1]) / 2
		if table_X[0] <= cenX <= table_X[1] and table_Y[0] <= cenY <= table_Y[1]:
			cell_ver = {"cell_vert": B2.tolist()}
			list["cells"].append(cell_ver)
	table_list.append(list)

res_blo["allWord"].pop(0)

for all_data in res_blo["allWord"]:
	center_count_x = 0
	center_count_y = 0
	for vertice in all_data["vertices"]:
		center_count_x += vertice["x"]
		center_count_y += vertice["y"]
	center_count_x = ceil(center_count_x / 4)
	center_count_y = ceil(center_count_y / 4)
	all_data["center"] = {
		"x": center_count_x,
		"y": center_count_y
	}

for T, table_vert in enumerate(table_list):
	for C, cells in enumerate(table_vert["cells"]):
		count_equal = 0
		cell_xy = {"max_x": 0, "max_y": 0, "min_x": 99999999, "min_y": 99999999}
		region_y = [0, 0]
		for cell_vert in cells["cell_vert"]:
			cell_xy["max_x"] = max(cell_xy["max_x"], cell_vert[0])
			cell_xy["max_y"] = max(cell_xy["max_y"], cell_vert[1])
			cell_xy["min_x"] = min(cell_xy["min_x"], cell_vert[0])
			cell_xy["min_y"] = min(cell_xy["min_y"], cell_vert[1])
			time_x = floor((cell_xy["max_x"] - cell_xy["min_x"])/10) + 1
			time_y = floor((cell_xy["max_y"] - cell_xy["min_y"])/10) + 1
			color_data = {"color_list": []}
			for axis_x in range(time_x):
				for axis_y in range(time_y):
					color = secimg[cell_xy["min_y"]+(axis_y*10), cell_xy["min_x"]+(axis_x*10)]
					point_color = [i - (i % 40) for i in color.tolist()]
					if point_color not in color_data["color_list"]:
						color_data["color_list"].append(point_color)
			cell_vert.append(color_data)


		for cells_equal in table_vert["cells"]:
			cell_xy_equal = {"max_x": 0, "max_y": 0, "min_x": 99999999, "min_y": 99999999}
			for cell_vert_equal in cells_equal["cell_vert"]:
				cell_xy_equal["max_x"] = max(cell_xy_equal["max_x"], cell_vert_equal[0])
				cell_xy_equal["max_y"] = max(cell_xy_equal["max_y"], cell_vert_equal[1])
				cell_xy_equal["min_x"] = min(cell_xy_equal["min_x"], cell_vert_equal[0])
				cell_xy_equal["min_y"] = min(cell_xy_equal["min_y"], cell_vert_equal[1])
			if cell_xy["max_x"] < cell_xy_equal["max_x"] and \
					cell_xy["max_y"] < cell_xy_equal["max_y"] and \
					cell_xy["min_x"] > cell_xy_equal["min_x"] and \
					cell_xy["min_y"] > cell_xy_equal["min_y"]:
				count_equal = 1
		if count_equal:
			continue
		for center in res_blo["allWord"]:
			if center["center"]["x"] >= cell_xy["min_x"] and \
					center["center"]["x"] <= cell_xy["max_x"] and \
					center["center"]["y"] >= cell_xy["min_y"] and \
					center["center"]["y"] <= cell_xy["max_y"]:
				table_list[T]["cells"][C]["coordinate"] = cell_xy
				table_list[T]["cells"][C]["flag"] = 0
				try:
					table_list[T]["cells"][C]["description"] += center["description"].replace(',', '').replace('.', '').replace('-', '').replace('|', '')
				except KeyError:
					table_list[T]["cells"][C]["description"] = str(center["description"]).replace(',', '').replace('.', '').replace(	'-', '').replace('|', '')



cell_list = [[] for _ in table_list]
deletion_count = 0
for del_section, deletion in enumerate(table_list):
	for cells in deletion["cells"]:
		if "description" in cells:
			cell_list[del_section].append(cells)

print(json.dumps(cell_list))

# print(json.dumps(cell_list))
cellCheck = []
flag = 0
word = 0
for Csection in cell_list:
	for one_word in Csection:
		wordCheck = []
		if one_word["flag"]:
			continue
		word_equal = 0

		for word_index, two_word in enumerate(Csection):
			if two_word["flag"]:
				continue
			# print(two_word)
			if two_word["coordinate"]["min_y"] < one_word["coordinate"]["min_y"] and \
					two_word["coordinate"]["max_x"] < one_word["coordinate"]["max_x"] + 15 and \
					two_word["coordinate"]["min_x"] > one_word["coordinate"]["min_x"] - 15:
				one_word["flag"] = 1
				two_word["flag"] = 1
				word_equal = 1
				word = word_index
		if word_equal:
			wordCheck.append(one_word)
			wordCheck.append(Csection[word])
			cellCheck.append(wordCheck)

parent = []
child = []
for cell_group in cellCheck:
	if len(cell_group) == 2:
		parent.append(cell_group[1]["description"])
		child.append(cell_group[0]["description"])

output = {
	"parent": ",".join(map(str, parent)),
	"child": ",".join(map(str, child))
}

# print(json.dumps(cellCheck))

# print(json.dumps(output))

#
# print(json.dumps(cellCheck))
