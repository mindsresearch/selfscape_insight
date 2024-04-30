"""topics.py takes a json file and creates a collage of the file

A longer description of what your code does,
including what json it takes in, and what it
contributes to the final output

Description:
1. Reads the given JSON file
2. Changing all special characters to readable characters for python
3. Creates a temporary directory for storing images
4. Uses requests to ask for an image from Google Images given a term from the JSON file
5. Saves the return images to the temp dir
6. Creates a collage using the images and their names as the descriptor words
7. Saves the collage as a .jpg
8. Removes the temp dir

Input JSON file:
* your_topics.json (Facebook removed this from its data requests, unable to find after January 2024)
* ads_interests.json

Contributions:
Outputs a randomly sorted collage of images with descriptor words

Functions:
    run(file_path): Runs the feature.
    special_character(df): Converts the strings in the given DataFrame to latin-1 then to utf-8 to handle any special characters in the names of the topics
    create_collage(image_folder, output_path, collage_size=(4096, 2160)): Creates a collage of given size using the images from image_folder with the image names under each image and saved to the output_path


Example usage:
    >>> from features import topics as tps
    >>> tps.run(args.file_path + "path to desire file")

    $ python3 topics.py -file_path "file path"
    filepath to the json file to be made into a collage

Dependencies:
    pandas for data handling
    requests and BeautifulSoup4 for webscraping image acquisition
    pillow (PIL) for image handling
    os for grabbing path files
    tqdm for progress bars
    random for shuffling images
    tempfile for the holding the individual images before collage creation


Note:
    This sub-module is part of the 'selfscape_insight' package in the 'features' module.

Version:
    1.1

Author:
    Carter Jacobs
"""

import argparse
import os
import random
import tempfile
# Add your other built-in imports here

import pandas as pd
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
# Add your other third-party/external imports here


def special_character (df):
    temp_df = df.copy()
    for x in range(0, len(df)):
        temp_df.iloc[x] = df.iloc[x].encode("latin-1").decode("utf-8")
    return temp_df

def create_collage(image_folder, output_path, collage_size=(4096, 2160)):
    # Get all image files from the folder
    image_files = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
    
    # Shuffle the order of the image files
    random.shuffle(image_files)
    
    # Create a new blank image for the collage
    collage = Image.new('RGB', collage_size)
    draw = ImageDraw.Draw(collage)
    
    # Calculate the width and height for each image tile
    total_images = len(image_files)
    width = int(total_images ** 0.5)  # Calculate number of images that can fit horizontally
    height = (total_images + width - 1) // width  # Calculate number of images that can fit vertically

    tile_width = collage_size[0] // width
    tile_height = collage_size[1] // height

    # Paste each image onto the collage
    for i, image_file in enumerate(image_files):
        try:
            font_size = int(tile_height * 0.1)
            image_path = os.path.join(image_folder, image_file)
            img = Image.open(image_path)
            img = img.resize((tile_width, tile_height - int(font_size * 1.2)))  # Resize image to fit the tile size
            collage.paste(img, ((i % width) * tile_width, (i // width) * tile_height))  # Paste image onto the collage
            # Draw image name under each picture
            font_path = os.path.join(os.path.dirname(__file__), "NotoSans_Local.ttf")
            font = ImageFont.truetype(font_path, font_size)
            topic = image_file.replace(".jpg","")
            # topic = topic[:20]
            draw.text(((i % width) * tile_width, (i // width) * tile_height + tile_height - int(font_size * 1.2)), topic, font=font, fill=(255, 255, 255))
        except (Image.UnidentifiedImageError):
            print(f"Skipping invalid image file: {image_file}")

    # Save the collage
    collage.save(output_path)

def run(file_path):
    print("Running the collage feature module")

    topics = pd.read_json(file_path)
    topics.columns = ["Ads_interests"]
    topics["Ads_interests"] = special_character(topics["Ads_interests"])

    output_path = os.path.basename(file_path).split(".")[0] + ".jpg"

    with tempfile.TemporaryDirectory() as temp_dir_topics:
        print(f"Created temporary directory: {temp_dir_topics}")
        
        # Download images to the temporary directory
        for index, row in tqdm(topics.iterrows(), desc="Topics: ", total=len(topics)):
            lead = row["Ads_interests"]
            params = {
                "q": lead,
                "tbm": "isch",
            }
            html = requests.get("https://www.google.com/search", params=params, timeout=30)
            soup = BeautifulSoup(html.content, features="lxml")
            image = soup.find_all("img")[1]["src"]
            data = requests.get(image).content
            with open(os.path.join(temp_dir_topics, f"{lead}.jpg"), "wb") as f:
                f.write(data)

        # Create collage using images in the temporary directory
        create_collage(temp_dir_topics, output_path)
    return "Your collage has been created: " + str(output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='topics',
                                     description='Creates a collage of images with name underneath for a single JSON file')
    parser.add_argument('-file_path', metavar='PATH_2_FILE',
                        help='path to file to use for creating a collage', required=True)
    args = parser.parse_args()
    print(run(args.file_path))
