from PIL import Image
import math
from colorthief import ColorThief
import colorsys
import os

def apply(image_mapping, input_image, output_file):
    input = Image.open(input_image)
    width, height = input.size

    # create cache dir
    if not os.path.exists("cache"):
        os.makedirs("cache")

    final_image = Image.new('RGB', (width * 3, height * 3))
    across = math.floor(width / 20)
    high = math.floor(height / 20)

    for i in range(0, across):
        for j in range(0, high):
            crop_rectangle = (20 * i, 20 * j, (20 * i) + 20, (20 * j) + 20)
            print(crop_rectangle)
            cropped_im = input.crop(crop_rectangle)
            cropped_im.save("cache/intermediate.png", quality=100)
            thief = ColorThief("cache/intermediate.png")
            color = thief.get_color(quality=1)
            hls = colorsys.rgb_to_hsv(color[0], color[1], color[2])
            res_key, _ = min(image_mapping.items(), key=lambda x: abs(hls[0] - x[1][0]))
            im = Image.open(res_key)
            im = im.resize((60, 60), Image.ANTIALIAS)
            final_image.paste(im, (i * 60, j * 60))


    final_image.save(output_file)
