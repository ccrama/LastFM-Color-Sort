import math
from PIL import Image

def apply(image_mapping, output_file, angle=0):
    sorted_images = sorted(image_mapping, key=image_mapping.get)
    max_edge_size = math.floor(math.sqrt(len(sorted_images)))
    final_image = Image.new('RGB', (max_edge_size * 150, max_edge_size * 150))

    slice = 0
    m = max_edge_size
    n = max_edge_size
    imindex = 0


    # TODO make this work for any angle, currently its either 45 degrees or 0 degrees
    if angle > 0:
        while slice < m + n - 1:
            z1 = 0 if slice < n else slice - n + 1
            z2 = 0 if slice < m else slice - m + 1
            
            j = j = slice - z2
            while j >= z1:
                im = Image.open(sorted_images[imindex])
                im = im.resize((150, 150), Image.ANTIALIAS)
                final_image.paste(im, (j * 150, (slice - j) * 150))
                imindex += 1
                j -= 1
            slice += 1
    else :
        for i in range(0, max_edge_size):
            for j in range(0, max_edge_size):
                im = Image.open(sorted_images[imindex])
                im = im.resize((150, 150), Image.ANTIALIAS)
                final_image.paste(im, (i * 150, j * 150))
                imindex += 1

    # reduce image size
    final_image.save(output_file)
