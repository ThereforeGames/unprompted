import torch
import requests

from models.clipseg import CLIPDensePredT
from PIL import Image
from torchvision import transforms
from matplotlib import pyplot as plt

import cv2

# load model
model = CLIPDensePredT(version='ViT-B/16', reduce_dim=64)
model.eval();

# non-strict, because we only stored decoder weights (not CLIP weights)
model.load_state_dict(torch.load('weights/rd64-uni.pth', map_location=torch.device('cuda')), strict=False);

# load and normalize image
input_image = Image.open('example_image.jpg')

# or load from URL...
# image_url = 'https://farm5.staticflickr.com/4141/4856248695_03475782dc_z.jpg'
# input_image = Image.open(requests.get(image_url, stream=True).raw)

transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    transforms.Resize((512, 512)),
])
img = transform(input_image).unsqueeze(0)

prompts = ['a spoon']

# predict
with torch.no_grad():
    preds = model(img.repeat(1,1,1,1), prompts)[0]

for i in range(len(prompts)):
	filename = f"{i}.png"
	plt.imsave(filename,torch.sigmoid(preds[i][0]))
	
	# TODO: Figure out how to convert the plot above to numpy instead of re-loading image
	img = cv2.imread(filename)

	gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

	(thresh, bw_image) = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)

	blur_image = cv2.GaussianBlur(bw_image, (19,19), 0)

	cv2.imwrite(f"{i}_bw.png",bw_image)
	cv2.imwrite(f"{i}_blur.png",blur_image)