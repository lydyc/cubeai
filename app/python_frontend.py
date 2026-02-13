import os
from cubetools.python_video_frontend import PythonVideoFrontend


class PythonFrontend(object):

    # 在__init__中定义Python前端界面
    def __init__(self):
        self.demo = PythonVideoFrontend(
            model_name_cn='力维行人检测',
            model_name_en='person-detection',
            local_image=True,
            local_video=True,
            streaming_video=True,
            show_image_results=False,
            # results2text=lambda x: x[0],
            image_examples=['demo_data/person1.jpg', 'demo_data/person2.jpg', 'demo_data/person3.jpg'],
            local_video_examples=['demo_data/person1.jpg'],
            streaming_video_examples=[f'file://{os.getcwd()}/demo_data/person1.jpg'],
            readme='README.md'
        )

    def launch(self, **kwargs):
        self.demo.launch(**kwargs)
