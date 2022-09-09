
def do_black_level_correction(image, height, width, bits):
    
        image_obc = 16 * 2 ** (bits - 8)
        image[image < image_obc] = image_obc
        image = image - image_obc

        return image

         