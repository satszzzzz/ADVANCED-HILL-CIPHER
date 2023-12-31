from PIL import Image
import numpy as np

def padImage(image, factor):
    '''
    Convert an image to an image padded with black whose dimensions are evenly divisible by factor. If the image is already evenly divisible by factor it returns the original image

    Args:
        image (PIL.Image): Image to pad
        factor (int): The number the width and height of the image must be evenly divisible by

    Returns:
        PIL.Image: The padded image

    '''
    hlength = len(image)
    vlength = len(image[0])
    if(hlength % factor != 0):
        # buffer_col = np.full((1, vlength, 3), 0, dtype="uint8")
        # for _ in range(0, factor - (hlength % factor)):
        #     image = np.vstack((image, buffer_col))
        #     hlength += 1
        buffer_col = np.full((factor - (hlength % factor), vlength, 3), 0, dtype="uint8")
        image = np.vstack((image, buffer_col))
        hlength += factor - (hlength % factor)
    if(vlength % factor != 0):
        buffer_row = np.full((hlength, 1, 3), 0, dtype="uint8")
        for _ in range(0, factor - (vlength % factor)):
            image = np.hstack((image, buffer_row))
            vlength += 1
    return Image.fromarray(image)



def matrixMultImage(key, image, block_size, mode):
    '''
    Left Multiply 3x3 chunks of the image by corresponding 3x3 chunks of the key.
    Multiplies all the color channels by the key then combines into an Image.

    Args:
        key (PIL.Image): The key image to multiply image by
        image (PIL.Image): The image to multiply by the key
        block_size (int): The size of the subkey tiled to form the key image

    Returns:
        PIL.Image: The resulting image from computing key.image
    ''' 
    color_channels = image.split()
    enciphered_channels = []
    #since the key is greyscale we only use a single color channel
    key = np.array(key.split()[0])
    i = 0
    j = 0
    for color_channel in color_channels:
        color_channel = np.array(color_channel)
        while(i < len(color_channel)):
            while(j < len(color_channel[0])):
                color_channel[i:i+block_size, j:j+block_size] = np.matmul(key[i:i+block_size, j:j+block_size], color_channel[i:i+block_size, j:j+block_size])
                j += block_size
            i += block_size
            j = 0
        i = 0
        enciphered_channels.append(Image.fromarray(color_channel))
    
    if(mode=='-d'):
        return Image.merge('RGB',enciphered_channels)

    xored=[]

    i=0
    j=0

    l,b=np.array(enciphered_channels[0]).shape
    key2=[]
    m=0

    for _ in range(3):
        key2.append(generate_matrix(l,b))

    for color_channel,k in zip(enciphered_channels,key2):
        color_channel=np.array(color_channel)
        while(i < len(color_channel)):
            while(j < len(color_channel[0])):
                color_channel[i:i+block_size, j:j+block_size] = (k[i:i+block_size,j:j+block_size])^color_channel[i:i+block_size, j:j+block_size]
                j += block_size
            i += block_size
            j = 0
        i = 0
        key2[m]=Image.fromarray(k)
        m+=1
        xored.append(Image.fromarray(color_channel))
    
    return Image.merge('RGB', xored),Image.merge('RGB', key2)


def generate_matrix(n, m):
   return np.array([[np.random.randint(256)
                         for _ in range(0, m)] for _ in range(0, n)], dtype="uint8")