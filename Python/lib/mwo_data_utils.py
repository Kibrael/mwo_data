import pandas as pd

class mwo_data_engine(object):
	
	def __init__(self):
		"""
		"""
		self.mech_info_csv = "../output/variant_weights.txt"


	def combine_scores_with_scrape(self, scores_df, mech_info_df):
		"""
		Combines screenshot match data with mech variant, weightclass, and chassis web scrape
		"""
		if mech_info_df is None:
			mech_info_df = pd.read_csv(self.mech_info_csv, sep="|")

		#merge datasets to get tonnage, and weight class for each mech
		scores_and_weights = scores_df.merge(mech_info_df, how="left", left_on="mech", right_on="variant")
		return scores_and_weights

	def clean_mech_variants(self, scores_df):
		"""
		Fixes bad OCR results in the mech name column

		"""
		#use dictionary to map bad read to actual
		mech_name_map = {
		"-BW":"WHM-BW",
		"KGC-O00B":"KGC-000B",
		"UM- -R68(L)":"UM-R68(L)",
		"CTF-3 F-3D(C)":"CTF-3D(C)",
		"STK-3F(C) STK-3":"STK-3F(C)"
		}

		#test with pandas map to column
		for mech in mech_name_map.keys():
			if mech in list(scores_df.mech):
				scores_df.at[scores_df.index[scores_df.mech==mech], "mech"] = mech_name_map[mech]

		return scores_df

#FIXME: check if images are being resized to min 80x80 before being sent to OCR
