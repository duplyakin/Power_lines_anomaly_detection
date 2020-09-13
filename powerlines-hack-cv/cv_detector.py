import detectron2
from detectron2.utils.logger import setup_logger
setup_logger()

from detectron2 import model_zoo
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg


class CvDetector:
    def __init__(self, model_config_path, model_path, num_classes):
        cfg = get_cfg()
        cfg.merge_from_file(model_zoo.get_config_file(model_config_path))
        cfg.MODEL.ROI_HEADS.NUM_CLASSES = num_classes

        cfg.MODEL.WEIGHTS = model_path
        cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.9  # set the testing threshold for this model
        self.cfg = cfg
        self.predictor = DefaultPredictor(self.cfg)

    def inference(self, image):
        outputs = self.predictor(image)
        return outputs