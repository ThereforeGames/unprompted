import numpy as np

class FaceObject:
    def __init__(self):
        self.bbox = None
        self.kps5 = None
        self.landmark = None
        self.feat = None

    def compute_sim(self, another):
        assert self.feat is not None and another.feat is not None
        from np.linalg import norm
        feat1 = self.feat
        feat2 = another.feat
        sim = np.dot(feat1, feat2) / (norm(feat1) * norm(feat2))
        return sim

