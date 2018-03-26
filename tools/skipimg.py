import numpy as np
import cv2
import os
import time
from PIL import Image
import imagehash
import sys
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

LFILE_EXTENSIONS = set(['jpg', 'JPG', 'jpeg', 'JPEG','png', 'mp4', 'bmp', 'PNG', 'BMP', 'tif', 'TIF'])

def hashimg(imgpath):
	#print imgpath
        ptlen = len(imgpath.split('.'))
        txtname = imgpath+'.hash'
	if os.path.exists(txtname)==True:
		return 0
        #print txtname
        image = Image.open(imgpath)
        # print imgpath
        h = str(imagehash.dhash(image))
        #print h
        hashfile = open(txtname,'w')
        hashfile.write(h)
        hashfile.close()

if __name__ == '__main__':
        sourcefolder = sys.argv[1]
        for parents, folders, filenames in os.walk(sourcefolder):
                for filename in filenames:
                        if filename.split('.')[-1] in LFILE_EXTENSIONS:
                                hashimg(sourcefolder+'/'+filename)
        hashlist = []
        for parents, folders, filenames in os.walk(sourcefolder):
                for filename in filenames:
                         if filename.split('.')[-1] == 'hash':
                                hashlist.append(filename)
	removelist = []
        for parents, folders, filenames in os.walk(sourcefolder):
                for filename in filenames:
                        if filename.split('.')[-1] in LFILE_EXTENSIONS:
                                tempimgpath = sourcefolder+'/'+filename
                                temphashpath = sourcefolder+'/'+filename+'.hash'
				imgtxtpath = sourcefolder+'/'+filename+'.txt'
                                fn = filename+'.hash'
				temphash = open(temphashpath,'r')
                                temphash0 = temphash.readline()
                                checkFlag = False
                                for hashpatht in hashlist:
                                        if hashpatht == fn:
                                                hashlist.remove(hashpatht)
                                for hashpatht in hashlist:
                                        hashpath0 = sourcefolder+'/'+hashpatht
                                        hasht = open(hashpath0,'r')
                                        hasht0 = hasht.readline()
                                        if temphash0 == hasht0:
                                                checkFlag = True
                                                #print tempimgpath
						if os.path.exists(imgtxtpath) == True:
							removelist.append(imgtxtpath)
                                                removelist.append(temphashpath)
                                                removelist.append(tempimgpath)
                                                #os.remove(temphashpath)
                                                #os.remove(tempimgpath)
                                        if checkFlag == True:
                                                break
        for removefile in removelist:
		print removefile
                os.remove(removefile)
	print "done"
