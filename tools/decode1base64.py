#
# base64 to png

import os
import base64
import json
import sys
# from PIL import Image
# from io import BytesIO

if __name__ == "__main__":
    labelfilepath = sys.argv[1]
    pngfilepath = sys.argv[2]

    annotation = json.load(open(labelfilepath))
    strs = annotation['url']

    imgdata=base64.b64decode(strs[22:])  
    file=open(pngfilepath,'wb')  
    file.write(imgdata)  
    file.close()

    # im = Image.open(BytesIO(base64.b64decode(strs)))
    # im.save('a.png', 'PNG')