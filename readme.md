### Table of Contents
	[Blog Examples](https://github.com/Kibrael/mwo_data#blog-examples)
	[Instructions](https://github.com/Kibrael/mwo_data#instructions)
	[Repository Structure](https://github.com/Kibrael/mwo_data#repository-structure)

## MechWarrior Online Match Score Data Project
Disclaimer: This project is not affiliated with [PGI](http://piranhagames.com/) or [MechWarrior](https://mwomercs.com/).
### Project Goal:
This project aims to construct a dataset based on game results from MechWarrior online. 
Match results will be combined with mech weights to facilitate analysis of tonnage deltas 
between teams.

The resulting dataset will contain nearly 600 images converted to pipe delimited text files
and mech tonnage by variant in the same format.

The combination of these datasets will allow statistical inference into matchmaking engine
priorities.

## Blog Examples
Please see [this link] for a discussion on the use and results of these code files.	
- [Whole screenshot](Python/whole_screenshot_example.py): Code for sending the entire test image to the AWS Rekognition API. This is a test of the return and is not optimal for dataframe construction.  
- [Horizontal slicing](Python/single_row_example.py): Code for sending horizontal slices of the test image to the AWS Rekognition APi. This example includes both a single row return as well as an example on assembling a dataframe from multiple API calls. This method optimizes cost at the expense of data cleaning time.
- [Horizontal and vertical slicing combination](Python/split_screenshot_example.py): This example slices an image into individual cells and sends each cell individually to the Rekognition API. This method optimizes for data cleaning time at the expense of cost.
- Analysis powered by [kite](kite.com)

## Instructions
- This project relies on [Python](https://www.python.org/downloads/) 3.7
- Install [requirements](requirements.txt)
- Set up your [AWS credentials](https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html)
- running code for single screenshot
- running code for many screenshots
- running web scrape code

## Repository Structure
- image data
	- data source (screencapture)
- [Web Scraping](Python/run_mech_scrape.py): Uses the [mech_scrape](Python/lib/mech_scrape.py) class to gather tonnage for each mech variant in [MechWarrior Online](https://mwomercs.com/).
- test data
- image handling
- initial dataframes
- cleaned dataframes
