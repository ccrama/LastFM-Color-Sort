import json
import time
import requests_cache
import os
import requests
from multiprocessing import Pool
from progress.bar import Bar
from urllib.request import urlopen
from PIL import Image
import numpy as np
from colorthief import ColorThief
from alive_progress import alive_bar
import colorsys
import csv
from ast import literal_eval as make_tuple
from concurrent import futures

from dotenv import load_dotenv
load_dotenv()

import os

API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
USER_AGENT = os.environ.get("USER_AGENT")
TARGET_USER = os.environ.get("TARGET_USER")

mapping_file = "color_mapping.csv"

TEMP_DIR = 'images_cache/'

requests_cache.install_cache()
page = 1
results = []
image_files = []
image_mapping = {}

def get_lastfm_albums():
    headers = {'user-agent': USER_AGENT}
    url = 'http://ws.audioscrobbler.com/2.0/'
    payload = {'method':'user.gettopalbums'}

    payload['api_key'] = API_KEY
    payload['format'] = 'json'
    payload['user'] = TARGET_USER
    payload['limit'] = 500
    payload['page'] = page

    response = requests.get(url, headers=headers, params=payload)
    return response

def paginateFully():
    global page
    global results

    bar = None

    # Get total pages
    response = get_lastfm_albums()
    if response.status_code != 200:
        print(response.text)
        return
    total_pages = int(response.json()['topalbums']['@attr']['totalPages'])


    with alive_bar(title="Getting LastFM Albums", total=total_pages) as bar:
        while page < total_pages + 1:
            response = get_lastfm_albums()
            if response.status_code != 200:
                print(response.text)
                break
            page = int(response.json()['topalbums']['@attr']['page'])
            total_pages = int(response.json()['topalbums']['@attr']['totalPages'])

            bar()

            page += 1

            for item in response.json()['topalbums']['album']:
                images = item['image']
                for image in images:
                    if image['size'] == 'large':
                        results.append(image['#text'])
                        break

            if not getattr(response, 'from_cache', False):
                time.sleep(0.25)

def job(url, success):
    try:
        file_name = TEMP_DIR + str(url.split('/')[-1])

        if os.path.exists(file_name):
            success(file_name)
            return
        u = urlopen(url)
        f = open(file_name, 'wb')
        f.write(u.read())
        f.close()
        success(file_name)
    except:
        pass

def addImage(file_name):
    global image_files
    if os.path.isfile(file_name):
        image_files.append(file_name)

def downloadImages():
    global results
    global image_files

    with alive_bar(len(results), title='Downloading images...') as bar:

        if not os.path.exists(TEMP_DIR):
            os.makedirs(TEMP_DIR)

        with futures.ThreadPoolExecutor(100) as executor:
            for i in executor.map(job, results, [addImage] * len(results)):
                bar()

def addColorMapping(file, color):
    global image_mapping
    image_mapping[file] = color

def computeColor(file, success):
    thief = ColorThief(file)
    color = thief.get_color(quality=1)

    success(file,  colorsys.rgb_to_hsv(color[0], color[1], color[2]))

def cacheImageColors():
    mapping_file = "color_mapping.csv"
    
    if os.path.isfile(mapping_file):
        print("Image color values already cached")
        return
    else:
        with alive_bar(len(image_files), title="Computing color values") as bar:
         with futures.ThreadPoolExecutor(10) as executor:
            for i in executor.map(computeColor, image_files, [addColorMapping] * len(image_files)):
                bar()
        with open(mapping_file, 'w', newline="") as csv_file:
            writer = csv.writer(csv_file)
            for key, value in image_mapping.items():
                writer.writerow([key, value])

        print("Image color values saved to {}".format(mapping_file))

# Get main arguments from command line
if __name__ == '__main__':       
    import sys
    method = sys.argv[1]
    file_1 = None
    file_2 = None

    if len(sys.argv) > 2:
        file_1 = sys.argv[2]
    if len(sys.argv) > 3:
        file_2 = sys.argv[3]

    from methods.sort import apply as sort
    from methods.recolor import apply as recolor

    if method == 'download':
        paginateFully()

        print("Found {} images".format(len(results)))
        downloadImages()

        print("Downloaded {} images".format(len(image_files)))
        cacheImageColors()

    if method == 'sort':
        if file_1 == None:
            print("Please provide an output file name")
            sys.exit(1)
        if os.path.isfile(file_1):
            print("Output file already exists")
            sys.exit(1)
        if not os.path.isfile(mapping_file):
            print("Please run the script with the download method first")
            sys.exit(1)

        with open(mapping_file) as f:
            rdr = csv.reader(f)
            image_mapping = {row[0]: make_tuple(row[1]) for row in rdr}

            sort(image_mapping, file_1)

    if method == 'recolor':
        if file_1 == None:
            print("Please provide an input file for recoloring")
            sys.exit(1)
        if file_2 == None:
            print("Please provide an output file name")
            sys.exit(1)
        if os.path.isfile(file_2):
            print("Output file already exists")
            sys.exit(1)
        if not os.path.isfile(mapping_file):
            print("Please run the script with the download method first")
            sys.exit(1)

        with open(mapping_file) as f:
            rdr = csv.reader(f)
            image_mapping = {row[0]: make_tuple(row[1]) for row in rdr}

            recolor(image_mapping, file_1, file_2)