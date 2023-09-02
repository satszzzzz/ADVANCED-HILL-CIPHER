from PIL import Image

q=Image.open('deciphered.jpg')

import numpy as np

x=np.array(q)

print(x.shape)
print(x)