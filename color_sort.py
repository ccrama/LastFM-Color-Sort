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
    total_pages = 99999

    while page < total_pages + 1:
        print("Paginating {}/{}".format(page, total_pages))
        response = get_lastfm_albums()
        if response.status_code != 200:
            print(response.text)
            break
        page = int(response.json()['topalbums']['@attr']['page'])
        total_pages = int(response.json()['topalbums']['@attr']['totalPages'])
        page += 1

        for item in response.json()['topalbums']['album']:
            images = item['image']
            for image in images:
                if image['size'] == 'large':
                    results.append(image['#text'])
                    break

        if not getattr(response, 'from_cache', False):
            time.sleep(0.25)

def job(url):
    global image_files
    file_name = TEMP_DIR + str(url.split('/')[-1])
    image_files.append(file_name)

    if os.path.exists(file_name):
        return
    u = urlopen(url)
    f = open(file_name, 'wb')
    f.write(u.read())
    f.close()

def downloadImages():
    global results
    global image_files
    bar = Bar('Downloading images...', max=len(results))

    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    pool = Pool()
    for i in pool.imap(job, results):
        bar.next()
    for url in results:
        file_name = TEMP_DIR + str(url.split('/')[-1])
        if os.path.isfile(file_name):
            image_files.append(file_name)
    bar.finish()

def computeColor(images):
    for file in images:
        if file in image_mapping:
            yield
            continue
        thief = ColorThief(file)
        color = thief.get_color(quality=1)
        image_mapping[file] = colorsys.rgb_to_hsv(color[0], color[1], color[2])
        yield

def cacheImageColors():
    mapping_file = "color_mapping.csv"
    
    if os.path.isfile(mapping_file):
        print("Image color values already cached")
        return
    else:
        with alive_bar(len(image_files[:3000])) as bar:
            for i in computeColor(image_files[:3000]):
                bar()
        with open(mapping_file, 'w', newline="") as csv_file:
            writer = csv.writer(csv_file)
            for key, value in image_mapping.items():
                writer.writerow([key, value])

        print("Image color values saved to {}".format(mapping_file))

# Get main arguments from command line
import sys
method = sys.argv[1]
file_1 = sys.argv[2]
file_2 = sys.argv[3]

from methods.sort import apply as sort
from methods.recolor import apply as recolor

if method == 'download':
    paginateFully()
    downloadImages()
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



