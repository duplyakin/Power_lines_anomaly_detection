import cv2
from cv_detector import CvDetector
from garland_classifier import GarlandClassifier, GARLAND_OK, GARLAND_PROBLEM

# TODO!
GARLAND_ID = 0
NUM_CLASSES = 1

GREEN_COLOUR = (0,255,0)
RED_COLOUR = (255, 0, 0)

class CvProcessor:
    def __init__(self):
        # TODO: create configs!
        self.detector = CvDetector("COCO-Detection/faster_rcnn_X_101_32x8d_FPN_3x.yaml",
                                   "/home/neurus/d2/garland_detector/output/model_final.pth",
                                   num_classes=NUM_CLASSES)
        self.garland_classifier = GarlandClassifier("/home/neurus/Projects/garland_classifier/insulators_garland_model.pth")


    def inference(self, image_path):
        img = cv2.imread(image_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        detector_outputs = self.detector.inference(img)
        instances = detector_outputs['instances'].to("cpu")
        pred_classes = instances.pred_classes
        pred_boxes = instances.pred_boxes
        print(pred_classes, pred_boxes)
        print(detector_outputs)

        result_img = img
        result_defects = {
            'line_broken': 0,
            'vibration_damper_displacement': 0,
            'garland_problem': 0
        }

        # 1. Garland analyze
        garland_ok_boxes = []
        garland_problem_boxes = []
        for idx in range(len(pred_classes)):
            if pred_classes[idx] == GARLAND_ID:
                bbox = pred_boxes[idx].tensor[0].tolist() # [x1,y1,x3,y3] in float
                print(bbox)
                x1, y1, x3, y3 = [int(v) for v in bbox]
                garland_subimg = img[y1:y3, x1:x3]
                idx = self.garland_classifier.inference(garland_subimg)
                if idx == GARLAND_OK:
                    print('GARLAND_OK')
                    garland_ok_boxes.append([x1,y1,x3,y3])
                else:
                    print('GARLAND_PROBLEM')
                    garland_problem_boxes.append([x1, y1, x3, y3])
        for box in garland_ok_boxes:
            x1,y1,x3,y3 = box
            result_img = cv2.rectangle(result_img, (x1,y1), (x3,y3), GREEN_COLOUR, 3)
        for box in garland_problem_boxes:
            result_defects['garland_problem'] = 1
            x1,y1,x3,y3 = box
            result_img = cv2.rectangle(result_img, (x1,y1), (x3,y3), RED_COLOUR, 3)

        # FINAL
        result_img = cv2.cvtColor(result_img, cv2.COLOR_RGB2BGR)
        res_img_path = 'result.jpg'
        cv2.imwrite(res_img_path, result_img)
        return res_img_path, result_defects