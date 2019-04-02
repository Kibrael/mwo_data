import json
import pandas as pd

full_screenshot = "../output/blog_files/ocr_responses/whole_screenshot_ocr_resp.json"
#screenshot_df = pd.read_json("../output/blog_files/whole_screenshot_ocr_resp.json")
with open(full_screenshot, "r") as infile:
	screenshot_data = json.load(infile)
words = []
for text_detected in screenshot_data["TextDetections"]:
	print(text_detected["DetectedText"])
	words.append(text_detected["DetectedText"])
print(words)
