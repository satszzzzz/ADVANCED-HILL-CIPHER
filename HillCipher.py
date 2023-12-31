import numpy as np
from sympy import Matrix
import ImageManip as IManip
from PIL import Image


def generateSubKey(n):
    '''Generate an nxn matrix that is invertible mod 256

    Args:
        n (int): The size of the matrix

    Returns:
        ndarray: nxn array modularly invertible 256
    '''
    found = False
    while(not found):
        key = np.array([[np.random.randint(256)
                         for _ in range(0, n)] for _ in range(0, n)], dtype="uint8")
        try:
            Matrix(key).inv_mod(256)
            found = True
        except:
            pass
    return key


def generateKey(width, height, block_size, complexKey):
    '''
    Generate an mxn matrix that consists of 3x3 keys (invertible mod 256).
    This is the key to encode the image with

    Args:
        width (int): width of the key Image to generate
        height (int): height of the key Image to generate
        block_size (int): size of the square subkey that will be tiled to form the key image
        complexKey (bool): True = Generate a key where every block_size x block_size section is unique. False = Tile a single key to form the image.

    Returns:
        PIL.Image: The tiled key as an image 
    '''
    key = np.empty((width, height), dtype="uint8")
    subkey = generateSubKey(block_size)
    i = 0
    j = 0
    while i < width:
        while j < height:
            if complexKey:
                subkey = generateSubKey(block_size)
            key[i:i+block_size, j:j+block_size] = subkey
            j += block_size
        i += block_size
        j = 0
    key = Image.fromarray(key)
    return Image.merge('RGB', (key, key, key))


def invertKey(key, block_size, complexKey):
    '''Convert a key to the inverse mod 256 for decrypting

    Args:
        key (PIL.Image): The key image to invert
        block_size (int): The size of the keys tiled in the key image (nxn Square key, block_size = n)
        complexKey (bool): Was the key generatedusing the -c flag (non-uniform tiled key)

    Returns:
        PIL.Image: the inverse key as an image
    '''
    i = 0
    j = 0
    key = np.array(key.split()[0])
    subkey = np.array(Matrix(key[i:i+block_size, j:j+block_size]).inv_mod(256))
    while i < len(key):
        while j < len(key[0]):
            if complexKey:
                subkey = np.array(
                    Matrix(key[i:i+block_size, j:j+block_size]).inv_mod(256))
            key[i:i+block_size, j:j+block_size] = subkey
            j += block_size
        i += block_size
        j = 0
    key = Image.fromarray(np.uint8(key))

    return Image.merge('RGB', (key, key, key))


def encipherImage(key, image, block_size, mode):
    '''
    Encodes an image with a given key

    Args:
        key (PIL.Image): The key to use for encryption
        image (PIL.Image): The image to encrypt
        block_size (int): The size of the square keys to be tiled 

    Returns:
        PIL.Image: The encrypted image
    '''
    if mode=='-e':
        multiplied,key2 = IManip.matrixMultImage(key, image, block_size, mode)
        multiplied = np.array(multiplied)
        return Image.fromarray(np.uint8(np.mod(multiplied, 256))),key2
    else:
        multiplied = IManip.matrixMultImage(key, image, block_size, mode)
        multiplied = np.array(multiplied)
        return Image.fromarray(np.uint8(np.mod(multiplied, 256)))


def decipherImage(key, image, block_size, complexKey, key2, mode):
    '''
    Decodes an image with a given key

    Args:
        key (PIL.Image): The key used to encrypt the image
        image (PIL.Image): Image to decrypt
        block_size (int): size of the subkey tiled to form the key image
        complexKey (bool): Was the image encrypted with the -c flag?

    Returns:
        PIL.Image: Decrypted Image
    '''

    enciphered_channels=list(image.split())
    key2=list(key2.split())
    xored=[]

    i=0
    j=0

    for color_channel,k in zip(enciphered_channels,key2):
        color_channel=np.array(color_channel)
        k=np.array(k)
        while(i < len(color_channel)):
            while(j < len(color_channel[0])):
                color_channel[i:i+block_size, j:j+block_size] = (k[i:i+block_size,j:j+block_size])^color_channel[i:i+block_size, j:j+block_size]
                j += block_size
            i += block_size
            j = 0
        i = 0
        xored.append(Image.fromarray(color_channel))
    
    image=Image.merge('RGB',xored)

    return encipherImage(invertKey(key, block_size, complexKey), image, block_size, '-d')
