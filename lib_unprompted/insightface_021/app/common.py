
import collections
Face = collections.namedtuple('Face', [
    'bbox', 'landmark', 'det_score', 'embedding', 'gender', 'age',
])
Face.__new__.__defaults__ = (None, ) * len(Face._fields)

class AppConfig:
    def __init__(self):
        #default config
        self.det_name = 'scrfd_2.5g_bnkps'
        self.det_model = None #you can set det_model for local onnx model
        self.rec_name = 'arcface_onnx_mfn'
        self.rec_model = None #you can set rec_model for local onnx model
