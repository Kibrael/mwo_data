
# coding: utf-8

# In[5]:


import cv2
import os
import pandas as pd
from PIL import Image, ImageFilter
import pytesseract


# In[8]:



img = Image.open("data/images/20171118200710_1.jpg")
#img = img.filter( ImageFilter.SHARPEN )
w, h = img.size
print(w,h)
#may need to add different area maps for different screen resolutions
#winning team players
#args are (x start, y start, x end, y end)
#area map is for 1680 1050
p1_area = (570, 205, w-300, h-820)
p2_area = (570, 230, w-300, h-795)
p3_area = (570, 253, w-300, h-770)
p4_area = (570, 275, w-300, h-750)
p5_area = (570, 303, w-300, h-725)
p6_area = (570, 328, w-300, h-700)
p7_area = (570, 350, w-300, h-678)
p8_area = (570, 373, w-300, h-655)
p9_area = (570, 403, w-300, h-628)
p10_area = (570, 425, w-300, h-605)
p11_area = (570, 448, w-300, h-580)
p12_area = (570, 470, w-300, h-560)

#losing team players
p13_area = (570, 505, w-300, h-528)
p14_area = (570, 525, w-300, h-503)
p15_area = (570, 550, w-300, h-478)
p16_area = (570, 570, w-300, h-455)
p17_area = (570, 600, w-300, h-430)
p18_area = (570, 623, w-300, h-405)
p19_area = (570, 645, w-300, h-385)
p20_area = (570, 667, w-300, h-363)
p21_area = (570, 698, w-300, h-335)
p22_area = (570, 720, w-300, h-312)
p23_area = (570, 742, w-300, h-288)
p24_area = (570, 762, w-300, h-265)

#parse victory/defeat--first 12 players are winners
#top team is always the winner
cropped_img = img.crop(p18_area)
#cropped_img.show()


# In[28]:


class mwo_image_to_data(object):
    """
    """
    def __init__(self):
        pass

    def load_image_pil(self, image_path):
        """
            Loads an image using the PIL library.
        """
        
    def split_image_verticle_cv(self, image=None):
        """
        """
        img = cv2.imread(image, 0)
        w = img.shape[0]
        h = img.shape[1]
        
    def split_image_horizontal_cv(self, image=None):
        """
        """
        pass
    
    def split_image_verticle_pil(self, image=None):
        """
            Takes an MWO team score image and splits it into 12 rectanges, 
            1 for each player's stats.
        """
        if image is None:
            print("no image supplied")
        else: #split image into 24 rectangles, 1 for each player
            #winning team players
            #args are (x start, y start, x end, y end)
            img = Image.open(image)
            w, h = img.size
            #winning team players 1-12 (index 0-11)
            #losing team players are 13-24 (index 12-23)
            #FIXME move image map(s) to a file
            #FIXME: test image resizing for other resolutions 
                    #or create area maps for other resolutions
            #area map is for 1680 1050 resolution
            if img.size == (1680, 1050):
                player_areas = [(570, 205, w-300, h-820),
                                (570, 230, w-300, h-795),
                                (570, 253, w-300, h-770),
                                (570, 275, w-300, h-750),
                                (570, 303, w-300, h-725),
                                (570, 328, w-300, h-700),
                                (570, 350, w-300, h-678),
                                (570, 373, w-300, h-655),
                                (570, 403, w-300, h-628),
                                (570, 425, w-300, h-605),
                                (570, 448, w-300, h-580),
                                (570, 470, w-300, h-560),
                                (570, 505, w-300, h-528),
                                (570, 525, w-300, h-503),
                                (570, 550, w-300, h-478),
                                (570, 570, w-300, h-455),
                                (570, 600, w-300, h-430),
                                (570, 623, w-300, h-405),
                                (570, 645, w-300, h-385),
                                (570, 667, w-300, h-363),
                                (570, 698, w-300, h-335),
                                (570, 720, w-300, h-312),
                                (570, 742, w-300, h-288),
                                (570, 762, w-300, h-265)]

            player_images = []
            for player_area in player_areas:
                player_images.append(img.crop(player_area))
            return player_images
        
    def split_image_horizontal_pil(self, img=None, sharpen=False):
        """
            Splits a player score rectangle into sub parts for OCR processing.
            clan: string
            name: string
            mech: string
            status: string
            score: integer
            kills: integer
            assists: integer
            dmg: integer
            ping: integer
        """
        
        if img is not None:
            #load image
            if type(img) == str:
                img = Image.open(img)

            if sharpen:
                #sharpen image
                img = img.filter(ImageFilter.SHARPEN)
                
            image_slices = []
            w, h = img.size

            #get clan    x_start, y_start, x_end,   y_end
            clan_area = (0, 0, w-765, h)
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
    
    def show_img_cv(self, image):
        """
            Displays an image using the CV2 library
        """
        cv2.imshow("image", image)
    def show_img_pil(self, image):
        """
            Displays an image using the Pil library
        """
        image.show()


# In[29]:


mwo = mwo_image_to_data()
test = mwo.split_image_verticle_pil("data/images/20171118200710_1.jpg") #get list of player rectangles
test2 = mwo.split_image_horizontal_pil(img=test[1])


# In[35]:



counter = 0
for img in test2:
    img.save("data/test_data/"+str(counter)+".jpg")
    counter +=1


# In[ ]:


test_2[0].show()


# In[ ]:


def pre_process(img=None, thresh=True, blur=True):
    if img:
        # load the example image and convert it to grayscale
        image = cv2.imread(img)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        if thresh:
            blur = False
            #thresholding requires grayscale image
            #"THRESH_TOZERO", cv2.THRESH_TOZERO
            #gray = cv2.threshold(gray, 0, 255,
            #    cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
            thresh_val, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_TOZERO)
        # make a check to see if median blurring should be done to remove noise
        elif blur:
            gray = cv2.medianBlur(gray, 3)

        # write the grayscale image to disk as a temporary file so we can apply OCR to it
        cv2.imwrite("data/images_processed/temp.png", gray)
    else:
        print("Image must be specified")


# In[ ]:


def apply_ocr(img=None, num_only=True):
    # load the image as a PIL/Pillow image, apply OCR, and then delete the temporary file
    if img:
        image=Image.open(img)
        image.show()
        if num_only:
            text = pytesseract.image_to_string(Image.open(img), config='outputbase digits')
        else:
            text = pytesseract.image_to_string(Image.open(img)) 
        
        #os.remove(img)
    else:
        print("No image file specified.")
    return text


# In[ ]:



player_imgs = split_image("data/images/20171118200710_1.jpg", area=player_areas[0])
index = 0
for img in player_imgs:
    img.save('data/images_processed/temp_image_{}.jpg'.format(index), 'JPEG')
    index +=1


# In[ ]:


pre_process(img="data/images_processed/temp_image_5.jpg") #takes a single image
text = apply_ocr(img="data/images_processed/temp.png") #follows pre_process using the temp image written
text


# In[ ]:


#convert text to var
#get aggregates by match


# In[ ]:


get_ipython().run_line_magic('matplotlib', 'inline')
from matplotlib import pyplot as plt
image = cv2.imread("data/images_processed/temp_image_5.jpg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
methods = [
	("THRESH_BINARY", cv2.THRESH_BINARY),
	("THRESH_BINARY_INV", cv2.THRESH_BINARY_INV),
	("THRESH_TRUNC", cv2.THRESH_TRUNC),
	("THRESH_TOZERO", cv2.THRESH_TOZERO),
	("THRESH_TOZERO_INV", cv2.THRESH_TOZERO_INV)]
 
# loop over the threshold methods
for (threshName, threshMethod) in methods:
    # threshold the image and show it
    (T, thresh) = cv2.threshold(gray, 0, 255, threshMethod)
    cv2.imshow(threshName, thresh)
    plt.imshow(thresh)
    plt.show()


# In[ ]:


$ python ocr.py --image images/example_01.png


# In[ ]:


beep = cv2.imread("data/images/20171118200710_1.jpg", 0)
beep.shape


# In[ ]:


cv2.imshow("img", beep)
cv2.waitKey(0)
cv2.destroyAllWindows()

