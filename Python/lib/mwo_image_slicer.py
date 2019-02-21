import boto3
import io
import os
from os import listdir
from os.path import isfile, join
import pandas as pd
from PIL import Image, ImageFilter



class mwoImageSlicer(object):
	"""

	"""

	def __init__(self, boto_client):
		"""

		"""
		self.boto_client = boto_client
		self.image_folder = "../data/images/"
		self.save_folder = "../data/images/"

		#horizontal slicing dimensions
		self.score_1680_1050 = [(570, 205, 1380, 230),
                                (570, 230, 1380, 255),
                                (570, 253, 1380, 280),
                                (570, 275, 1380, 300),
                                (570, 303, 1380, 325),
                                (570, 328, 1380, 350),
                                (570, 350, 1380, 372),
                                (570, 373, 1380, 395),
                                (570, 403, 1380, 422),
                                (570, 425, 1380, 455),
                                (570, 448, 1380, 470),
                                (570, 470, 1380, 490),
                                (570, 505, 1380, 522),
                                (570, 525, 1380, 547),
                                (570, 550, 1380, 572),
                                (570, 570, 1380, 595),
                                (570, 600, 1380, 620),
                                (570, 623, 1380, 645),
                                (570, 645, 1380, 665),
                                (570, 667, 1380, 687),
                                (570, 698, 1380, 715),
                                (570, 720, 1380, 738),
                                (570, 742, 1380, 762),
                                (570, 762, 1380, 785)]

        #Vertical slicing dimensions
        #these are the vertical coordinates for 1680 by 1050 resolution
        #(x_start, y_start, x_end, y_end)
        #FIXME: this won't work as the actual cropping is done from relative areas on non-standard image sizes
		self.score_parts_1680_1050 = {
							        	"clan_area":(0, 0, 915, 1050),
							        	"name_area":(50, 0, 1130, 1050),
							        	"mech_area":(265, 0, 1215, 1050),
							        	"status_area":(390, 0, 1330, 1050),
							        	"score_area":(500, 0, 1430, 1050),
							        	"kills_area":(590, 0, 1505, 1050),
							        	"assist_area":(650, 0, 1560, 1050),
							        	"dmg_area":(710, 0, 1640, 1050),
							        	"ping_area":(760, 0, 1680, 1050)
							         }


	def img_to_dataframe(self, img):
		"""
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
		h_slices = self.slice_image_horizontal(img)
		for slic in h_slices:
			player_row_imgs = self.slice_image_vertical(slic)
			#get OCR for each image in player slice
			match_dict["clan"].append(self.get_image_ocr(player_row_imgs[0])["text"])
			match_dict["name"].append(self.get_image_ocr(player_row_imgs[1])["text"])
			match_dict["mech"].append(self.get_image_ocr(player_row_imgs[2])["text"])
			match_dict["status"].append(self.get_image_ocr(player_row_imgs[3])["text"])
			match_dict["score"].append(self.get_image_ocr(player_row_imgs[4])["text"])
			match_dict["kills"].append(self.get_image_ocr(player_row_imgs[5])["text"])
			match_dict["assists"].append(self.get_image_ocr(player_row_imgs[6])["text"])
			match_dict["damage"].append(self.get_image_ocr(player_row_imgs[7])["text"])
			match_dict["ping"].append(self.get_image_ocr(player_row_imgs[8])["text"])
		
		match_df = pd.DataFrame.from_dict(match_dict)
		match_df = match_df[["clan", "name", "mech", "status", "score", "kills", "assists", "damage", "ping"]]
		return match_df


	def get_image_ocr(self, img):
		"""
		
		"""
		img = self.resize_image(img)
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

		return resp_text


	def download_images(self, url, save_folder):
		"""
			Downloads files from a target site

		"""

		pass


	def get_images_in_folder(self, folder="../data/images/"):
		"""
			Returns a list of image files in a specified folder

		"""

		img_files = [file for file in listdir(folder) if isfile(join(folder, file))]
		img_files = [file for file in img_files if file[-3:]=="jpg"]
		
		return img_files


	def load_image(self, image_path): #this might be unnecessary
		"""
			Stores an image file as a class data object for manipulation
		"""

		pass


	def resize_image(self, img, new_width=200):
		"""
			Resizes an image while maintaining aspect ratio
		"""

		width_pct = (new_width / float(img.size[0])) #get new width as a percent of old width for aspect ratio 
		new_height = int((float(img.size[1])*float(width_pct))) #get new height based on new/old width percentage
		img = img.resize((new_width, new_height), Image.ANTIALIAS) #resize image: AWS OCR needs minimum of 80x80 pixels

		return img


	def slice_image_horizontal(self, img):
		"""
			Cuts a MWO scorecard screen capture into 24 horizontal segments, 1 for each player
			These rectangles are further cut by slice_image_veritcal() before being sent to AWS Rekognition for OCR
			
			input: MWO match screenshot
			Returns a list of horizontal slices of the screenshot, 1 per player
		"""

		if img is not None:
           
        	#split image into 24 rectangles, 1 for each player
            #args are (x start, y start, x end, y end)
			img = Image.open(self.image_folder+img)
			w, h = img.size
			#winning team players are positions 1-12 (index 0-11)
			#losing team players are positions 13-24 (index 12-23)

			#FIXME: test image resizing for other resolutions 
			        #or create area maps for other resolutions

			player_images = [] #holds one image slice (horizontal bar) for each of the 24 players
			for player_area in self.score_1680_1050:
			    player_images.append(img.crop(player_area))
			return player_images

		else:
			print("no image supplied")
		    

	def slice_image_vertical(self, img, sharpen=False):
		""" 
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

		if img is not None:

            #load image for processing if one was passed
			if type(img) == str:
			    img = Image.open(img)

			if sharpen:
			    #sharpen image
			    img = img.filter(ImageFilter.SHARPEN)
			    
			image_slices = []
			w, h = img.size #get size of passed image, these are the horizontal slices of player data
			#image cropping uses relative mapping
			#get clan    x_start, y_start, x_end,   y_end
			clan_area = (0, 0, w-760, h)
			image_slices.append(img.crop(clan_area))
			#get player name
			name_area = (50, 0, w-550, h)
			image_slices.append(img.crop(name_area))
			#get mech
			mech_area = (265, 0, w-465, h)
			image_slices.append(img.crop(mech_area))
			#get status
			status_area = (390, 0, w-350, h)
			image_slices.append(img.crop(status_area))
			#get match score
			score_area = (500, 0, w-250, h)
			image_slices.append(img.crop(score_area))
			#get kills
			kills_area = (590, 0, w-175, h)
			image_slices.append(img.crop(kills_area))
			#get assists
			assist_area = (650, 0, w-120, h)
			image_slices.append(img.crop(assist_area))
			#get damage
			dmg_area = (710, 0, w-40, h)
			image_slices.append(img.crop(dmg_area))
			#get ping
			ping_area = (760, 0, w, h)
			image_slices.append(img.crop(ping_area))
		else:
			print("No image or area selected")

		return image_slices

