import os
from io import BytesIO
from os import path

import requests
from dotenv import dotenv_values
from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

c = dotenv_values(".env")

url = "http://192.168.0.200:2283"
apikey = c["immich_api"]
albumid = "713e43d8-099a-4d5e-960e-29187669c709"  # frame


headers = {"Accept": "application/json", "x-api-key": apikey}


# # Get the list of photos from the API using the albumid
response = requests.get(url + "/api/albums/" + albumid, headers=headers)

if response.status_code != 200:
    print("Failed to get album")
    exit()

data = response.json()
image_urls = data["assets"]
imgs = []
print(f"Found {len(image_urls)} images in album {albumid}")

# Download each image from the URL and save it to the directory
headers = {"Accept": "application/octet-stream", "x-api-key": apikey}

# creaate images directory if it doesn't exist
if not path.exists("images"):
    os.mkdir("images")

for id in image_urls:
    asseturl = url + "/api/assets/" + str(id["id"]) + "/original"
    response = requests.get(asseturl, headers=headers)

    photo_path = f"images/{id['id']}.jpeg"
    imgs.append(id["id"])

    # Only download file if it doesn't already exist
    if path.exists(photo_path):
        print(f"File {photo_path} already exists")
        continue

    with open(photo_path, "wb") as f:
        # open response with pillow
        img = Image.open(BytesIO(response.content)).convert("RGB")
        img.save(f, format="jpeg")

    print(f"Downloaded {photo_path}")

for file in os.listdir("images"):
    file = os.path.splitext(file)
    basename = file[0]
    if basename not in imgs:
        # delete the file
        os.remove(f"images/{basename}.jpeg")
