import boto3
import io
import json

import numpy as np 
import pandas as pd
import requests
from PIL import Image, ImageFilter

from lib import mwo_image_slicer

client = boto3.client('rekognition') #instantiate AWS client

test_imgs_path = "E:/MWO/mwo_data/data/test_data/" #test images folder

def convert_to_byte_array(img):
	"""
	Converts an image file to a byte array for use with the 
	Rekognition API
	"""
	img_byte_arr = io.BytesIO()
	img.save(img_byte_arr, format='PNG')
	img_byte_arr = img_byte_arr.getvalue()
	return img_byte_arr

def grey_min_max(img, min_grey=185):
	"""

	"""
	img = img.convert("L")
	img_px = img.load()
	for i in range(img.size[1]):
		for j in range(img.size[0]):
			if img_px[j,i] < min_grey:
				img_px[j,i] = 0 
			else:
				img_px[j,i] = 255
		img.save("../data/test_data/testpx.jpg")
	return img

#instantiate image tools for project
print("loading image to slicer")
mwo_slicer = mwo_image_slicer.mwoImageSlicer(client) #handles image slicing and OCR requests
mwo_slicer.load_image(image="20171118200711_1.jpg") #set current image for handling

#cut and save vertical image slices. These are single data elements of the screenshot.
print("vertical slicing")
for i in range(len(h_slices)):
	player_row_imgs = mwo_slicer.slice_image_vertical(h_slices[i])
	save_img = True #set flag to save image slices
	if save_img:
		for j in range(len(player_row_imgs)):
			player_row_imgs[j].save("../data/test_data/"+"player_img"+str(j)+"_"+str(i)+".jpg")
			mwo_slicer.resize_image(player_row_imgs[j]).save("../data/test_data/"+"resize_player_img"+str(j)+"_"+str(i)+".jpg")

test_df = mwo_slicer.img_to_dataframe(mwo_slicer.current_img, "test1.jpg", save_img=True)
test_df.to_csv("../data/test_data/full_screenshot_sliced_df.csv", index=False)

#load test images: list of images in one row of screenshot
img4 = Image.open(test_imgs_path + "player_img5_0.jpg") #this is a 4


img4 = mwo_slicer.resize_image(img4) #resize to minimum AWS API size
img4 = img4.convert("L") #convert to greyscale
#img4px = img4.load() #get pixel representation of image

img4.show()
#send test image without mod
#img_byte_arr = io.BytesIO()
#img4.save(img_byte_arr, format='PNG')
#img_byte_arr = img_byte_arr.getvalue()
#response = client.detect_text(Image={'Bytes': img_byte_arr})
#print("OCR response for initial image after resize")
#print(response)


img4 = grey_min_max(img4)
img4.show()
##get brightest pixels and convert the rest to black
#cycle over pixels in image
#print(img4.size)
#img = Image.open("../data/test_data/testpx.jpg")
img = Image.open(test_imgs_path + "resize_player_img5_0.jpg")
img = img.convert("L")
img_px = img.load()

deltas_v = []
deltas_h = []
for i in range(img.size[1]):
	for j in range(img.size[0]):
		try:
			pixel_diff_h = img_px[j,i] - img_px[j, i+10]
			pixel_diff_v = img_px[j,i] - img_px[j+10, i]
		except:
			pixel_diff = 0
		deltas_h.append(pixel_diff_h)
		deltas_v.append(pixel_diff_v)

deltas_h.sort()
deltas_v.sort()
print(deltas_h[:40])
print(deltas_v[:40])

for i in range(img.size[1]):
	for j in range(img.size[0]):
		try:
			pixel_diff_h = 0 - img_px[j,i+5]
		except:
			pixel_diff_h = 0
		try:
			pixel_diff_v = 0 - img_px[j+5, i]
		except:
			pixel_diff_v = 0
		
		if pixel_diff_h <= -225 or pixel_diff_v <= -225:
			img_px[j,i] = 255
		else:
			img_px[j,i] = 0
		

img.save("../data/test_data/brightline.jpg")
img.show()
#img4.save("testpx.jpg")

im_test = Image.open("../data/test_data/testpx.jpg")
#img4.show()

#send test image after brighntess filter
img_byte_arr = io.BytesIO()
img4.save(img_byte_arr, format='PNG')
img_byte_arr = img_byte_arr.getvalue()
response = client.detect_text(Image={'Bytes': img_byte_arr})
#print("OCR response after mod")
print(response)
#find brightness center by gradient and pass to OCR API

#modify greyscale
#sharpen image
#add background
#threshing?