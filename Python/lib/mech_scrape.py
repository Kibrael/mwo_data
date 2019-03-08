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
        chassis_obj = re.compile(r'Var\w\wnts[\']+:[\sa-zA-Z0-9-,]+')
        hero_obj = re.compile(r'[\']+Hero[\']+:[,\s[()\.\'\w-]+')
        champ_obj = re.compile(r'[\']+Champion[\']+:\s?[+\s[()\w-]+')
        special_obj = re.compile(r'[\']+Special[\']+:\s?[\/,\s[()\w-]*')

        #get matching name, tonnage, and variant list
        mech_results = mech_obj.finditer(page_string)
        tonnage_results = tonnage_obj.finditer(page_string)
        chassis_results = chassis_obj.finditer(page_string)
        hero_results = hero_obj.finditer(page_string)
        champion_results = champ_obj.finditer(page_string)
        special_results = special_obj.finditer(page_string)
        #print([spec.group() for spec in special_results])

        #clean regex results to get desired text for each mech: name, weight, chassis variants
        mech_names = [mech_name.group().replace("===", "").strip() for mech_name in mech_results]
        mech_weights = [mech_weight.group().replace("\n", "")[-3:].strip() for mech_weight in tonnage_results]
        #chassis variants is a list of lists
        chassis_variants = [chassis.group().replace("\n","")[12:].replace(",","").split() for chassis in chassis_results]

        hero_variants = [hero.group().replace("\n","")[11:].strip() for hero in hero_results]
        hero_names = [hero[:hero.find("(")].strip() for hero in hero_variants]
        hero_names = [hero.replace("'''Special'''","") for hero in hero_names]
        
        for i in range(len(hero_variants)):
            #fix Archer Tempest hero typo
            if "ACR-T" in hero_variants[i]:
                hero_variants[i] = hero_variants[i].replace("ACR-T", "ARC-T")
                print(hero_variants[i])
                print("Archer tempest fixed \n\n")
            if "(" in hero_variants[i]:
                #take from open parenthesis to the right
                hero_variants[i] = hero_variants[i][hero_variants[i].index("("):].replace("'''Special'''","")
            
            if "," in hero_variants[i]:
                hero_variants[i] = hero_variants[i].split(",")

                for j in range(len(hero_variants[i])):
                    if "(" in hero_variants[i][j]:
                        hero_variants[i][j] = hero_variants[i][j][hero_variants[i][j].find("(")+1:]
                        hero_variants[i][j] = hero_variants[i][j].replace(")","")                            
            else:
                hero_variants[i] = [hero_variants[i].replace("'''Special'''","").replace("(","").replace(")","")]
            
            

        champion_variants = [champ.group() for champ in champion_results]
        
        #process scrape data for special variants to remove clutter
        special_variants = [spec.group() for spec in special_results]
        
        special_variants = [spec[spec.index(":")+1:].strip().replace(" ","") for spec in special_variants]
        special_list = [] #use list to hold all special variants as there are fewer than number of chassis
        for i in range(len(special_variants)):
            if "," in special_variants[i]:
                special_variants[i] = special_variants[i].split(",")
            else:
                special_variants[i] = [special_variants[i]]
            #convert special variants to single list
            for j in range(len(special_variants[i])):
                special_list.append(special_variants[i][j])
       
        for i in range(len(special_list)):
            if special_list[i] == "ACR-2R(S)":
                print("Archer special fixed")
                special_list[i] = "ARC-2R(S)"
        print()
        
        #FIXME need to match special varints by first 3 letters to mech name for each mech
        #print(len(mech_names), len(hero_variants), "hero", len(champion_variants), "champ", len(special_variants), "special")
        #convert lists to dict as preprocess for converstion to dataframe
        mech_dict = {
                        "mechs":mech_names,
                        "tonnage":mech_weights,
                        "variants":chassis_variants,
                        "hero_chassis":hero_variants,
                        "hero_names":hero_names,
                        #"champions":champion_variants
                    }

        mech_df = pd.DataFrame(mech_dict)
        
        #match special variants to base chassis to get weight data
        mech_df["special_variants"] = ""
        for index, row in mech_df.iterrows():
            
            add_specials = []
            for i in range(len(special_list)):

                #check for clan IIC model
                if "IIC" in row["variants"][0]:
                    clan = True
                else:
                    clan = False

                mech_letters = row["variants"][0][:3].upper()
                if clan:
                    if mech_letters == special_list[i][:3].upper() and "IIC" in special_list[i]:
                        add_specials.append(special_list[i])
                else:
                    if mech_letters == special_list[i][:3].upper() and "IIC" not in special_list[i]:
                        add_specials.append(special_list[i])

            mech_df.at[index, "special_variants"] = add_specials
        mech_df = mech_df[["mechs", "tonnage","hero_names", "hero_chassis", "variants",
                           "special_variants"]]
        print(mech_df)
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
        all_weights_df = pd.concat([assault_mech_df, heavy_mech_df, medium_mech_df, 
                                    light_mech_df])

        self.save_data(assault_mech_df, "assault")
        self.save_data(heavy_mech_df, "heavy")
        self.save_data(medium_mech_df, "medium")
        self.save_data(light_mech_df, "light")
        self.save_data(all_weights_df, "all_weights")
        #get maximum new columns needed for splitting variants
        max_cols = all_weights_df.variants.apply(lambda x: len(x)).max()
        melt_cols = []

        for i in range(max_cols):
            all_weights_df["var_"+str(i)] = ""
            melt_cols.append("var_"+str(i))

        variant_weights_df = pd.DataFrame()
        for index, row in all_weights_df.iterrows():
            for i in range(len(row["variants"])):
                #add each variant to variant weights as a row with mech, tonnage, variant
                new_row_dict = {
                                "mech_name":row["mechs"],
                                "tonnage":row["tonnage"],
                                "variant":row["variants"][i].upper()
                                }
                new_row_df = pd.DataFrame(new_row_dict, index=[0])
                variant_weights_df = pd.concat([variant_weights_df, new_row_df])

            for i in range(len(row["hero_chassis"])):
                new_row_dict = {
                                "mech_name":row["hero_names"],
                                "tonnage":row["tonnage"],
                                "variant":row["hero_chassis"][i].upper()
                                }
                new_row_df = pd.DataFrame(new_row_dict, index=[0])
                variant_weights_df = pd.concat([variant_weights_df, new_row_df])


            for i in range(len(row["special_variants"])):
                #print(row["special_variants"][i])
                new_row_dict = {
                                "mech_name":row["mechs"],
                                "tonnage":row["tonnage"],
                                "variant":row["special_variants"][i].upper()
                                }
                new_row_df = pd.DataFrame(new_row_dict, index=[0])
                variant_weights_df = pd.concat([variant_weights_df, new_row_df])  

        #remove duplicate rows 

        self.save_data(variant_weights_df, "variant_weights")

if __name__ =="__main__":
    mechScraper().main()
