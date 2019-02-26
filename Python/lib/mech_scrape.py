import os
import pandas as pd
import re
import requests
from requests import get

class mechScraper(object):
    """
        
    """

    def __init__(self):
        """
            Set initial class variables:
            - mech data urls
        """

        self.light_url = "https://wiki.mwomercs.com/index.php?title=Light_Mechs&action=edit"
        self.medium_url = "https://wiki.mwomercs.com/index.php?title=Medium_Mechs&action=edit"
        self.heavy_url = "https://wiki.mwomercs.com/index.php?title=Heavy_Mechs&action=edit"
        self.assault_url = "https://wiki.mwomercs.com/index.php?title=Assault_Mechs&action=edit"
        self.output_path = "../output/"

    def get_mech_df(self, url=None):
        """
            Scrapes page data from a passed URL to extract:
            - mech names
            - mech tonnage
            - mech weight class
            returns the data as a pandas dataframe
        """

        if not url:
            print("must pass URL")
            return

        print("scraping " + url)
        page = requests.get(url)
        page_string = page.text

        mech_obj = re.compile(r'===\s[\w\s-]+[\s()A-Z0-9-]*\s===')
        tonnage_obj = re.compile(r'Tonnage[\']*:[\s\d+]+')
        chasis_obj = re.compile(r'Var\w\wnts[\']+:[\sa-zA-Z0-9-,]+')


        #get matching name, tonnage, and variant list
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

            
    def save_data(self, data, weight_class, output_path=None):
        """
            Writes a pandas df to disc.
            Uses the weight class as a name for pipe-delimited text file.
        """
        if not output_path:
            output_path = self.output_path
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        
        print("saving data for " + weight_class)
        data.to_csv(output_path + weight_class + ".txt", sep="|", index=False)


    def main(self):
        """
            Scrapes URLs for mech data and compiles them to 
            pandas dataframes before writing them to disk.
        """

        assault_mech_df = self.get_mech_df(url=self.assault_url)
        heavy_mech_df = self.get_mech_df(url=self.heavy_url)
        medium_mech_df = self.get_mech_df(url=self.medium_url)
        light_mech_df = self.get_mech_df(url=self.light_url)

        self.save_data(assault_mech_df, "assault")
        self.save_data(heavy_mech_df, "heavy")
        self.save_data(medium_mech_df, "medium")
        self.save_data(light_mech_df, "light")
        self.save_data(pd.concat([assault_mech_df, heavy_mech_df, medium_mech_df, 
            light_mech_df]), "all_weights")


if __name__ =="__main__":
    mechScraper().main()
