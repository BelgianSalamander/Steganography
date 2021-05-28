from PIL import Image # type: ignore
import math, getopt, sys, time
from util import *

def image_to_bits(fp, pixels, num_bits_used, bits_stored, verbose = False):
    if verbose:
        print("Converting image into bits!")

    image = Image.open(fp)

    width, height = image.size
    pixels_needed = (width * height * bits_stored + 16 * 2 + 64) // num_bits_used
    scale = pixels / pixels_needed
    scale = math.sqrt(scale)

    if scale < 1:
        new_width = math.floor(width * scale)
        new_height = math.floor(height * scale)

        image = image.resize((new_width, new_height))

        if verbose:
            print("Downscaled image to fit in target")
            print("Old dimensions: " + str(width) + ", " + str(height))
            print("New dimensions: " + str(new_width) + ", " + str(new_height))

        width = new_width
        height = new_height

    meta_data = int_to_bits(width, 16) + int_to_bits(height, 16) + int_to_bits(bits_stored, 3)
    pixels_data = [0] * width * height * 3 * bits_stored
    index = 0
    pixels = image.load()

    start_time = time.time()
    intervals = width // 10

    for x in range(width):
        for y in range(height):
            for value in pixels[x,y]:
                bits = int_to_bits(value, 8)[:bits_stored]
                for bit in bits:
                    pixels_data[index] = bit
                    index += 1
        if verbose and (x + 1) % intervals == 0:
                time_left = (time.time() - start_time) / x * (width - x - 1)
                print(f"Transformed columns {x+1}/{width}; ETA : {round(time_left)} seconds!")

    if verbose:
        print("Converted image into bits!")

    return meta_data + pixels_data

def hide_bits_in_image(bits_to_hide, hide_in, num_bits_used, verbose = False):
    if verbose: print("Concealing bits!")
    pixels = hide_in.load()
    width = hide_in.width
    height = hide_in.height

    full_data = int_to_bits(len(bits_to_hide)) + bits_to_hide

    class FinishedEncoding(Exception):
        pass

    new_col = [0] * 3
    bits = int_to_bits(num_bits_used, 3)
    for i in range(3):
        new_col[i] = bits[i] // 2 * 2 + bits[i]
    pixels[0,0] = tuple(new_col)

    index = 0

    start = True
    start_time = time.time()

    intervals = width // 10

    try:
        for x in range(width):
            for y in range(start, height):
                start = False
                color = pixels[x, y]
                new_col = [0] * len(color)
                for i in range(len(color)):
                    value = color[i]
                    bits = int_to_bits(value, 8)


                    for bit_index in range(8 - num_bits_used, 8):
                        bits[bit_index] = full_data[index]
                        index += 1
                        if index >= len(full_data):
                            new_col[i] = bits_to_int(bits)
                            pixels[x,y] = tuple(new_col)
                            raise FinishedEncoding
                    new_col[i] = bits_to_int(bits)
                pixels[x,y] = tuple(new_col)
            if verbose and (x + 1) % intervals == 0:
                time_left = (time.time() - start_time) / x * (width - x - 1)
                print(f"Encrypted into columns {x+1}/{width}; ETA : {round(time_left)} seconds!")
    except FinishedEncoding:
        pass

if __name__ == "__main__":
    DEFAULTS = {'-o' : 'steg-concealed.png', '-v' : 'verbose', '-u' : '3', '-s' : '8'}

    if len(sys.argv[1:]) == 0:
        print("Salamander's python implementation of image steganography")
        print("Arguments")
        print("  -f : Path to image that will conceal other image (Required)")
        print("  -h : Path to image that will be concealed (Required)")
        print("  -o : Path to output location. Default is 'steg-concealed.png. Using png (or another lossless format) is necessary for the steganography to work")
        print("  -u : The amount of bits per byte that are replaced. Default is 3")
        print("  -s : The amount of bits per byte of the hidden image that are kept. Default is 8")
        print("  -v : To stop the program from being verbose, use '-v no'")
        exit()

    try:
        opts, _ = getopt.getopt(sys.argv[1:], 'f:v:h:o:u:s:')
    except getopt.GetoptError as e:
        print(e)
        exit()
    
    args = {a:b for a,b in opts}
    DEFAULTS.update(args)
    args = DEFAULTS
    
    if '-f' not in args:
        print("Please specify the input file! ('-f')")
        exit()

    if '-h' not in args:
        print("Please specify the image to conceal! ('-h')")

    target = Image.open(args['-f'])

    width, height = target.size

    bits = image_to_bits(args['-h'], width * height, int(args['-u']), int(args['-s']), args['-v'] == 'verbose')
    hide_bits_in_image(bits, target, int(args['-u']), args['-v'] == 'verbose')
    print("Saving image to disk")
    target.save(args['-o'])

    print("Concealing succesful!")