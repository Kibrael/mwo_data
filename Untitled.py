
# coding: utf-8

# In[30]:


import base64
import boto3
import requests

MWO_IMGS = "/Users/roellk/data_practice/mwo_data/data/images/"
TEST_IMG = "20171118200710_1.jpg"


# In[37]:






with open(MWO_IMGS+TEST_IMG, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read())
    
img = {
      "Bytes": encoded_string
      }
   
response = client.detect_text(Image=img)
textDetections=response['TextDetections']
print('Detected text')
for text in textDetections:
        print('Detected text:' + text['DetectedText'])
        print('Confidence: ' + "{:.2f}".format(text['Confidence']) + "%")
        print('Id: {}'.format(text['Id']))
        if 'ParentId' in text:
            print ('Parent Id: {}'.format(text['ParentId']))
        print('Type:' + text['Type'])
        print


# In[24]:


request_syntax = {
   "Image": { 
      "Bytes": "blob",
      "S3Object": { 
         "Bucket": "string",
         "Name": "string",
         "Version": "string"
      }
   }
}


# In[ ]:


sample_response = {
   "TextDetections": [ 
      { 
         "Confidence": number,
         "DetectedText": "string",
         "Geometry": { 
            "BoundingBox": { 
               "Height": number,
               "Left": number,
               "Top": number,
               "Width": number
            },
            "Polygon": [ 
               { 
                  "X": number,
                  "Y": number
               }
            ]
         },
         "Id": number,
         "ParentId": number,
         "Type": "string"
      }
   ]
}


# In[9]:


session = boto3.Session(profile_name='default')

rekognition = session.client('rekognition')
response = requests.get('https://upload.wikimedia.org/wikipedia/commons/thumb/8/88/Stephen_Hawking_David_Fleming_Martin_Curley.png/640px-Stephen_Hawking_David_Fleming_Martin_Curley.png')
response_content = response.content
#rekognition_response = rekognition.detect_faces(Image={'Bytes': response_content}, Attributes=['ALL'])
                           
#print(rekognition_response)


# In[10]:


dir(session)


# In[19]:


client=boto3.client('rekognition')
dir(client)


# In[5]:





# In[7]:


cd aws-python-sample



python s3_sample.py

