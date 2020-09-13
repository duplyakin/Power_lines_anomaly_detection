from __future__ import print_function, division

import torch
from PIL import Image
from torchvision import transforms
from torch.autograd import Variable


GARLAND_OK = 0
GARLAND_PROBLEM = 1

class GarlandClassifier:
    def __init__(self, model_path):
        self.img_transforms = transforms.Compose([
            transforms.Resize((256,256)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = torch.load(model_path)
        model.eval()
        model.to(self.device)
        self.model = model

    def inference(self, image):
        # NOTE: image is a numpy array (RGB, from opencv)
        # but ToTensor() needs PIL image, so here we have to convert
        # (https://stackoverflow.com/questions/43232813/convert-opencv-image-format-to-pil-image-format)
        image = Image.fromarray(image)
        image_tensor = self.img_transforms(image).float()
        image_tensor = image_tensor.unsqueeze_(0)
        print(image_tensor.shape)
        input = Variable(image_tensor)
        input = input.to(self.device)
        output = self.model(input)
        index = output.data.cpu().numpy().argmax()
        # 0 - "ok", 1 - "problem"
        return index
