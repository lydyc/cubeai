# -*- coding: utf-8 -*-
from app.model_predict import ModelPredict
import requests
import json
import os

class AppCore(object):
    def __init__(self):
        self.model_predict = ModelPredict()

    def predict(self, img):
        return self.model_predict.predict(img)

    def predict_video(self, url):
        return self.model_predict.predict_video(url)


if __name__ == '__main__':
    import os
    os.chdir('..')

    app_core = AppCore()
    res = app_core.predict("demo_data/222.jpg","person_server:ALL")
    print(res)

