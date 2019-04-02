
# coding: utf-8

# In[1]:


#This notebook will contain functions to build and update a list of mechs current in Mechwarrior Online.
#Mech list pages can be found at:
#Light: https://wiki.mwomercs.com/index.php?title=Light_Mechs&action
#Medium: https://wiki.mwomercs.com/index.php?title=Medium_Mechs&action
#Heavy:https://wiki.mwomercs.com/index.php?title=Heavy_Mechs&action
#Assault: https://wiki.mwomercs.com/index.php?title=Assault_Mechs&action

#all mechs via gamepedia: https://mwo.gamepedia.com/Category:Playable


# In[2]:


import requests
from requests import get
import re
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
import lxml.html as lh
import pandas as pd


# In[21]:


#url='https://wiki.mwomercs.com/index.php?title=Light_Mechs&action=edit'
url = "https://wiki.mwomercs.com/index.php?title=Assault_Mechs&action=edit"
#has 4 tables, 1 for each weight class
#Create a handle, page, to handle the contents of the website
page = requests.get(url)
page_string = page.text

page_string = page_string.replace("\n", " ")
#page_string
#define regex for searching page text
mech_obj = re.compile(r'===\s[\w\s-]+[\s()A-Z0-9-]*\s===')
tonnage_obj = re.compile(r'Tonnage[\']*:[\s\d+]+')
chasis_obj = re.compile(r'Var\w\wnts[\']+:[\sa-zA-Z0-9-,]+')

#get matching tonnage, variant list using regex pattern
mech_results = mech_obj.finditer(page_string)
tonnage_results = tonnage_obj.finditer(page_string)
chasis_results = chasis_obj.finditer(page_string)

#for result in tonnage_results:
#    print(result.group())

#clean regex results to get desired text for each mech: name, weight, chasis variants
mech_names = [mech_name.group().replace("===", "").strip() for mech_name in mech_results]
mech_weights = [mech_weight.group().replace("\n", "")[-5:].strip() for mech_weight in tonnage_results]
chasis_variants = [chasis.group().replace("\n","")[12:].replace(",","").split() for chasis in chasis_results]

#convert lists to dict as preprocess for converstion to dataframe
mech_dict = {
    "mechs":mech_names,
    "tonnage":mech_weights,
    "variants":chasis_variants
}

#print(len(mech_names), len(mech_weights), len(chasis_variants))

#for i in range(len(chasis_variants)):
#    print(mech_weights[i], mech_names[i], chasis_variants[i])


# In[5]:


text = "| === Dire Wolf (DWF) ===  \'\'\'T"
mech_obj = re.compile(r'===\s[\w\s-]+[\s()A-Z0-9-]*\s===')
mech_test = mech_obj.finditer(text)
mech_names = [mech_name.group() for mech_name in mech_results]
mech_names


# In[6]:


def get_mech_df(url=None):
    if not url:
        print("must pass URL")
        return

    url=url
    page = requests.get(url)
    page_string = page.text

    mech_obj = re.compile(r'===\s[\w\s-]+[\s()A-Z0-9-]*\s===')
    tonnage_obj = re.compile(r'Tonnage[\']*:[\s\d+]+')
    chasis_obj = re.compile(r'Var\w\wnts[\']+:[\sa-zA-Z0-9-,]+')


    #get matching tonnage, variant list
    mech_results = mech_obj.finditer(page_string)
    tonnage_results = tonnage_obj.finditer(page_string)
    chasis_results = chasis_obj.finditer(page_string)
    
    #clean regex results to get desired text for each mech: name, weight, chasis variants
    mech_names = [mech_name.group().replace("===", "").strip() for mech_name in mech_results]
    mech_weights = [mech_weight.group().replace("\n", "")[-3:].strip() for mech_weight in tonnage_results]
    chasis_variants = [chasis.group().replace("\n","")[12:].replace(",","").split() for chasis in chasis_results]

    #convert lists to dict as preprocess for converstion to dataframe
    mech_dict = {
        "mechs":mech_names,
        "tonnage":mech_weights,
        "variants":chasis_variants
    }
    mech_df = pd.DataFrame(mech_dict)
    return mech_df


# In[20]:


#compile mech data and write to disk
assault_mech_df = get_mech_df(url='https://wiki.mwomercs.com/index.php?title=Assault_Mechs&action=edit')
heavy_mech_df = get_mech_df(url="https://wiki.mwomercs.com/index.php?title=Heavy_Mechs&action=edit")
medium_mech_df = get_mech_df(url="https://wiki.mwomercs.com/index.php?title=Medium_Mechs&action=edit")
light_mech_df = get_mech_df(url="https://wiki.mwomercs.com/index.php?title=Light_Mechs&action=edit")

assualt_mech_df.to_csv("output/assault_mechs.txt", sep="|", index=False)
heavy_mech_df.to_csv("output/heavy_mechs.txt", sep="|", index=False)
medium_mech_df.to_csv("output/medium_mechs.txt", sep="|", index=False)
light_mech_df.to_csv("output/light_mechs.txt", sep="|", index=False)


# In[14]:


light_mech_df


# In[19]:


get_ipython().system('pwd')

