import cv2
import numpy as np
from cubetools.onnx_predict import Model
from cubetools import image_tools
from cubetools.video_predict import VideoPredict
import requests
import io
import base64
from PIL import Image
import json

class ModelPredict(object):
    def __init__(self):
        self.video_predict = VideoPredict(callback_predict=self.predict)
        self.model = Model('app/model_data/glasses-detection-yolov10n.onnx')
        self.imgsz = 640
        self.confidence_thres = 0.2
        self.names = ['行人']
        # self.post_url = "http://10.72.57.201:32678/picasso/image/inference"
        self.post_url = "http://0.0.0.0:9010/picasso/image/inference"
    
    def parse_person_boxes(self, response_json):
        """
        解析服务返回的 JSON，提取行人坐标，返回 [ ["行人", [x1, y1, x2, y2]], ... ] 格式
        """
        labeled_boxes = []
        try:
            data = json.loads(response_json)
        except json.JSONDecodeError:
            return labeled_boxes  # 返回空列表表示解析失败

        for item in data.get("data", []):
            for person in item.get("person_server", []):
                rect = person.get("rect", [])
                if rect and len(rect) == 4:
                    labeled_boxes.append(["行人", rect])
        return labeled_boxes
    
    def predict(self, img):
        img_pil, img_ = image_tools.read_img(img)
        if "," in img:
            img = img.split(",")[1]

        img_bytes = base64.b64decode(img)
        payload = {"task_type": "person_server:DETECT"}
        print(payload)
        # 使用 with 打开文件，确保句柄自动关闭
        files = [('image_data', ("test.jpg", io.BytesIO(img_bytes), 'image/jpeg'))]
        try:
            response = requests.post(self.post_url, headers={}, data=payload, files=files)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return {"status": "err", "value": f"request failed: {e}"}
        labeled_boxes = self.parse_person_boxes(response.text)
        print(labeled_boxes)
        img_pil = image_tools.draw_all_box_and_label_pil2(img_pil, labeled_boxes)
        img_url = image_tools.pil2url(img_pil)

        return labeled_boxes, img_url
    

    def predict_video(self, url):
        return self.video_predict.read_predict(url)[1]
