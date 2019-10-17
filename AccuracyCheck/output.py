import json
import ocrFunction as ocrFun

Path = "../sample_img/sample3.jpg"
img64 = ocrFun.img_to_base64(Path)

ocr_text = ocrFun.request_cloud_vision_api(img64)
get_label = ocrFun.get_image_label(img64)

label = ocrFun.result_img_label(get_label, 0.5)

block = ocrFun.res_block_grope(ocr_text)

print(json.dumps(block))

Data = {"AllData": []}
for blo in block["allBlock"]:
		data = {"description": blo["description"], "type": "text"}
		Data["AllData"].append(data)

for lab in label["allLabel"]:
		data = {"description": lab["name"], "type": "photo"}
		Data["AllData"].append(data)

# print(json.dumps(Data))
