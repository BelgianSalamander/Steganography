from PIL import Image # type: ignore
from util import *
import getopt, sys, time

class FinishedReading(Exception):
    pass

def bits_to_image(bit, verbose = False):
    width = bits_to_int(bits[:16])
    height = bits_to_int(bits[16:32])
    bits_stored = bits_to_int(bits[32:35])
    if bits_stored == 0:
        bits_stored = 8
    bits_lost = 8 - bits_stored
    if verbose:
        print(f"Image is {width}x{height} pixels and stores {bits_stored} significant bits")
    img = Image.new("RGB", (width, height))
    intervals = width // 5
    pixels = img.load()
    index = 35
    start_time = time.time()
    for x in range(width):
        for y in range(height):
            pixel_data = bits[index : index + bits_stored * 3]
            r = bits_to_int(pixel_data[:bits_stored] ) << bits_lost
            g = bits_to_int(pixel_data[bits_stored:2*bits_stored] ) << bits_lost
            b = bits_to_int(pixel_data[2*bits_stored:] ) << bits_lost
            pixels[x,y] = (r,g,b)
            index += 3 * bits_stored
        if verbose and (x + 1) % intervals == 0:
                time_left = (time.time() - start_time) / x * (width - x - 1)
                print(f"Writing column {x+1}/{width}; ETA : {round(time_left)} seconds!")

    return img

def read_bits_from_image(fp, verbose = False):
    img = Image.open(fp)
    pixels = img.load()
    width = img.width
    height = img.height

    bits_read = []

    num_bits_used = 0
    first_col = pixels[0,0]
    for val in first_col:
        num_bits_used = num_bits_used * 2 + (val % 2)

    if num_bits_used == 0:
        num_bits_used = 8

    if verbose:
        print("Reading bits from image!")
        print("Image uses " + str(num_bits_used) + "-bit encoding!")

    intervals = width // 10

    index = 0

    start = True
    start_time = time.time()

    try:
        length = 0
        length_bits_read = 0
        for x in range(width):
            for y in range(start, height):
                start = False
                color = pixels[x, y]
                for i in range(len(color)):
                    value = color[i]
                    bits = int_to_bits(value, 8)[8 - num_bits_used:]
                    for bit in bits:
                        if length_bits_read < 64:
                            length *= 2
                            length += bit
                            length_bits_read += 1
                        else:
                            bits_read.append(bit)
                            index += 1
                            if index >= length:
                                raise FinishedReading
            if verbose and (x + 1) % intervals == 0:
                time_left = (time.time() - start_time) / x * (width - x - 1)
                print(f"Decoded column {x+1}/{width}; ETA : {round(time_left)} seconds!")

    except FinishedReading:
        pass

    if verbose:
        print("Read bits from image!")

    return bits_read

if __name__ == "__main__":
    DEFAULTS = {'-o' : 'steg-out.png', '-v' : 'verbose'}

    try:
        opts, _ = getopt.getopt(sys.argv[1:], 'f:o:v:')
    except getopt.GetoptError as e:
        print(e)
        exit()
    
    args = {a:b for a,b in opts}
    DEFAULTS.update(args)
    args = DEFAULTS
    
    if '-f' not in args:
        print("Please specify the input file! ('-f')")
        exit()

    bits = read_bits_from_image(args['-f'], args['-v'].lower() == 'verbose')
    img = bits_to_image(bits, args['-v'].lower() == 'verbose')
    img.save(args['-o'])

    print("Decryption succesful!")