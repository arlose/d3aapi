from PIL import Image
import base64
import io
import numpy as np
import matplotlib.pyplot as plt

data = open('1.jpg.txt').read()
binary = base64.b64decode(data.replace(b'data:image/png;base64,', b''))
with open('test.png','wb') as out: 
    out.write(io.BytesIO(binary).read())


img=np.array(Image.open('test.png'))  
plt.figure("test")
plt.imshow(img)
plt.axis('off')
plt.show()
