import io
import os
from os import listdir
from os.path import isfile, join

import boto3
import pandas as pd
from PIL import Image, ImageFilter
import requests
import yaml


class mwoImageSlicer(object):
	"""

	"""

	def __init__(self, boto_client, config_file="mwo_ocr_config.yaml"):
		"""

		"""

		with open("mwo_ocr_config.yaml", "r") as in_config:
			self.config_values = yaml.safe_load(in_config)

		self.boto_client = boto_client

		self.image_list = [] #placeholder for list of images to process via OCR


	def main(self):
		"""
		"""
		if self.config_values["rerun_images"] == True:
			self.image_list = self.get_files_in_folder()
		else:	
			self.image_list = self.get_unprocessed_files()

		print(len(self.image_list), "images loaded to class")


	def assemble_2d_img_array(self, img=None, col_map=None, row_map=None):
		"""
		img: PIL class image object
		col_map: pixel coordinates of data columns in dict format
		row_map: pixel map of row heights in dict format
		for example configs see: mwo_ocr_config.yaml

		"""

		#assemble 2d images array
		if not img:
			img = self.current_img
		if not col_map:
			col_map = self.config_values["col_width_1600_1050"]
		if not row_map:
			row_map = self.config_values["row_heights_1600_1050"]

		image_array_2d = [] #list to hold columns of image data. each column will be a list of values
		v_slices = [] #holds column slices of image
		
		for key in col_map.keys():
			coords = col_map[key]
			v_slice = self.slice_image(img=self.current_img, x1=coords[0], y1=coords[1], 
				x2=coords[2], y2=coords[3], standardize_res=True)
			v_slices.append(v_slice)
		print(len(v_slices), "column slices")
		for i in range(len(v_slices)):

			h_slices = [] #holds player slice of column
			for key in row_map.keys():
				p_slice = self.slice_image(img=v_slices[i], x1=0, y1=row_map[key][0], 
					x2=v_slices[i].height, y2=row_map[key][1])

				h_slices.append(p_slice)

			image_array_2d.append(h_slices)
		self.image_array_2d = image_array_2d
		return image_array_2d
	
	def img_to_dataframe(self, img, save_img=True, resize=True, thresh=True, save_df=False, 
		filepath="../output/df_from_img/"):
		"""
		Uses AWS Rekognition to parse images from MWO screenshots
		Screenshots are split into single element components and resized before sending
		The resulting text is assembled into a dataframe that matches the MWO scorecard

		img is the image to be processed
		Setting thresh=True will greyscale by calling the grey_min_max() function to threshold each image before sending to AWS
		Setting save_df=True saves the resulting dataframe as a pipe-delimited text file
		Setting save_img=True will save the image slices to ../data/test_data/
		
		"""
		
		match_dict = {
						"clan":[],
						"name":[],
	            		"mech":[],
	            		"status":[],
	            		"score":[],
	            		"kills":[],
	            		"assists":[],
	            		"damage":[], 
	            		"ping":[]
		}
		print("horizontal slicing")
		h_slices = self.slice_image_horizontal(img)
		print("vertical slicing")
		for i in range(len(h_slices)):
			
			player_row_imgs = self.slice_image_vertical(h_slices[i])
			
			
			#resize images prior to OCR
			if resize:
				for j in range(len(player_row_imgs)):
					player_row_imgs[j] = self.resize_image(player_row_imgs[j], mode="width")

			#threshold images prior to OCR
			if thresh:
				for j in range(len(player_row_imgs)):
					player_row_imgs[j] = self.grey_min_max(player_row_imgs[j])
			
			if save_img:
				for j in range(len(player_row_imgs)):
					player_row_imgs[j].save("../data/test_data/"+"player_img"+str(j)+"_"+str(i)+".jpg")
			#get OCR for each image in player slice
			print("OCR runnin on slice {} of {}".format(i, len(h_slices)))
			match_dict["clan"].append(self.get_image_ocr(player_row_imgs[0])["text"])
			match_dict["name"].append(self.get_image_ocr(player_row_imgs[1])["text"])
			match_dict["mech"].append(self.get_image_ocr(player_row_imgs[2])["text"])
			#threshing the status column removes "dead" entries as those are shown in red
			match_dict["status"].append(self.get_image_ocr(player_row_imgs[3])["text"])
			match_dict["score"].append(self.get_image_ocr(player_row_imgs[4])["text"])
			match_dict["kills"].append(self.get_image_ocr(player_row_imgs[5])["text"])
			match_dict["assists"].append(self.get_image_ocr(player_row_imgs[6])["text"])
			match_dict["damage"].append(self.get_image_ocr(player_row_imgs[7])["text"])
			match_dict["ping"].append(self.get_image_ocr(player_row_imgs[8])["text"])

		print("converting to dataframe")
		match_df = pd.DataFrame.from_dict(match_dict)
		match_df = match_df[["clan", "name", "mech", "status", "score", "kills", 
							 "assists", "damage", "ping"]]
		if save_df:
			print("saving dataframe to ", filepath, self.image_name)
			self.save_dataframe(match_df, file_name=self.image_name, file_path=filepath)

		return match_df


	def save_dataframe(self, dataframe, file_name, file_path):
		"""
		Saves a dataframe to pipe-delimited text format
		"""

		if not file_path:
			file_path = self.data_save

		if not os.path.exists(file_path):
			os.makedirs(file_path)
		dataframe.to_csv(file_path+file_name[:-4] + ".txt", sep="|", index=False)


	def grey_min_max(self, img, min_grey=150):
		"""
		Sets all pixels below min_grey to black
		Sets all pixesl above min_grey to white
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


	def get_image_ocr(self, img, full_resp=False, show=False, size=False):
		"""
		Uses AWS Rekognition to get the text value from an image slice of a MWO screenshot
		This function only returns a single word (it was designed for getting text resonse from a single cell of an image)
		"""
		if show:
			img.show()
		if size:
			print(img.size)
		#convert image to byte array for use with AWS Rekognition API
		img_byte_arr = io.BytesIO()
		img.save(img_byte_arr, format='PNG')
		img_byte_arr = img_byte_arr.getvalue()

		response = self.boto_client.detect_text(Image={'Bytes': img_byte_arr})
		#limit return to first text read and confidence
		
		try:
			resp_text = {
							"text":response['TextDetections'][0]['DetectedText'],
							"confidence":response['TextDetections'][0]['Confidence']
						}
		except:
			#provide data for empty images
			resp_text = {
							"text":"",
							"confidence":0
			}
		if full_resp:
			return response
		else:
			return resp_text


	def get_resolution(self, img_file, folder="../data/images/", display=False):
		"""
		Returns the weidth and height of an image
		"""

		img = Image.open(folder+img_file)
		if display:
			img.show()
		return img.size


	def get_files_in_folder(self, folder=None, ext=None):
		"""
		Returns a list of files matching a passed extension in a specified folder 
		Default folder is set in mwo_ocr_config.yaml
		"""
		if not folder:
			folder = self.config_values["raw_image_path"]
		if not ext:
			ext = self.config_values["file_extension"]
		
		img_files = [file for file in listdir(folder) if isfile(join(folder, file))]
		img_files = [file for file in img_files if file[-3:]==ext]
		print(len(img_files), "files in {folder}".format(folder=folder))

		return img_files

	def get_unprocessed_files(self, raw_folder=None, filter_folder=None, ext=None):
		"""
		Returns a list of images not yet processed for OCR
		Basic implementation is the main raw image folder image list less 
		the dataframe files present in the raw output folder.
		"""
		if not raw_folder:
			raw_folder = self.config_values["raw_image_path"]
		if not filter_folder:
			filter_folder = self.config_values["initial_ocr_data"]
		if not ext:
			ext = "txt"

		start_img_list = self.get_files_in_folder()
		print(len(start_img_list), "images in {raw_folder}".format(raw_folder=raw_folder))
			
		processed_images = self.get_files_in_folder(ext=ext, folder=filter_folder)
		filter_files = [file[:-4] for file in processed_images]
		print(len(filter_files), "potential files removed by presence in {filter_folder}".format(filter_folder=filter_folder))
		filtered_img_list = [score for score in start_img_list if score[:-4] not in filter_files]
		print(len(filtered_img_list), "remaining images to process")

		return filtered_img_list


	def load_image(self, image=None, folder_path=None): #this might be unnecessary
		"""
		Stores an image file as a class data object (PIL Image class type) for manipulation

		"""
		if not image:
			print("image file required, please specify an image file")
			return
		if not folder_path:
			folder_path = self.config_values["raw_image_path"]	

		img = Image.open(folder_path+image)
		self.current_img = img
		self.image_name = image


	def resize_image(self, img, mode="width", new_base=300, print_size=False):
		"""
		Resizes an image while maintaining aspect ratio

		new_width is the new width of the image in pixels
		height will be set based on the aspect ratio and the passed width parameter
		"""
		if mode == "width":
			width_pct = (new_base / float(img.size[0])) #get new width as a percent of old width for aspect ratio 
			new_height = int((float(img.size[1])*float(width_pct))) #get new height based on new/old width percentage
			img = img.resize((new_base, new_height), Image.ANTIALIAS) #resize image: AWS OCR needs minimum of 80x80 pixels
			if print_size:
				print("new size", img.size)

			return img

		elif mode == "height":
			height_pct = (new_base / float(img.size[1]))
			new_width = int((float(img.size[0])*float(height_pct)))
			img = img.resize((new_width, new_base), Image.ANTIALIAS)
			if print_size:
				print("new size", img.size)

			return img


	def slice_image(self, img, x1, y1, x2, y2, standardize_res=False):
		""" 
		img: must be a PIL Image class
		coords: length 4 tuple or list with x1, y1, x2, y2 for image cropping

			Cuts a MWO scorecard image into single elements in preparation for OCR and aggregation of data.
			There are 24 players per match. 
			The following data elements will be captured for each player:
				- clan: string
            	- name: string
	            - mech: string
	            - status: string
	            - score: integer
	            - kills: integer
	            - assists: integer
	            - damage: integer
	            - ping: integer

	        input: a horizontal slice from slice_image_horizontal
	        return: a list of images containing the information listed above
		"""

		if not img:
			print("No image or area selected, please pass a PIL image object")
			return

		else:
			#check to see if image is of standard 1680 x 1050 resolution
			if img.size != (1680, 1050) and standardize_res==True:
				print("resizing image", img)
				#resize if needed, this is done to match the slicing pattern
				img = self.resize_image(img, new_width=1680)
			#print(img.size)
			#print(x1, y1, x2, y2)
			image_slice = img.crop((x1, y1, x2, y2))

			return image_slice

			