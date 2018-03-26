#coding: utf-8
# extract object from images based on the annotation

import cv2
import os
import sys
import json
import uniout
import random
import string


LFILE_EXTENSIONS = set(['jpg', 'JPG', 'jpeg', 'JPEG','png', 'mp4', 'bmp', 'PNG', 'BMP', 'tif', 'TIF'])

# extract taglist
exttaglist = [u"大客车", u"面包车", u"工程车", u"商务车", u"货车", u"小轿车", u"SUV", u"﻿小轿车", u"其他类型车"]

def random_char(num):
       return ''.join(random.choice(string.ascii_letters) for x in range(num))

def gettagedfilelist(d):
    namelist = []
    for parentdir,dirname,filenames in os.walk(d+'/data/'):  
        for filename in filenames:  
            if filename.split('.')[-1] in LFILE_EXTENSIONS:  
                    labelname = filename+'.txt'
                    if os.path.exists(d+'/label/'+labelname):
                        namelist.append(filename)
    return namelist

def isCover(box0, box1):
    l0 = int(box0[0])
    r0 = int(box0[1])
    t0 = int(box0[2])
    b0 = int(box0[3])
    l1 = int(box1[0])
    r1 = int(box1[1])
    t1 = int(box1[2])
    b1 = int(box1[3])
    cl = max(l0, l1)
    cr = min(r0, r1)
    ct = max(t0, t1)
    cb = min(b0, b1)
    if cl<cr and ct<cb:
        return True
    return False

def isCoverlist(left, top, size, objlist):
    r0 = [left, left+size, top, top+size]
    for obj in objlist:
        r1 = [obj[0], obj[0]+obj[2], obj[1], obj[1]+obj[2]]
        if isCover(r0, r1):
            return True
    return False


def extractobj(imgpath, annotationpath, extractpath, isCombin=True, isGenFalse=True, Gennum = 2):
    img = cv2.imread(imgpath)
    h, w, _ = img.shape
    annotation = json.load(open(annotationpath))
    objlist = []
    for obj in annotation['objects']:
        tag = obj['tag'][0] # TODO multi tag
        if tag in exttaglist:
            left = int(obj['x_start']*w)
            right = int(obj['x_end']*w+0.5)
            top = int(obj['y_start']*h)
            bot = int(obj['y_end']*h+0.5)
            centerx = (left+right)/2
            centery = (top+bot)/2
            objw = right-left
            objh = bot-top
            if objw>=objh:
                top = centery-objw/2
                bot = centery+objw/2
            else:
                left = centerx-objh/2
                right = centerx+objh/2
            objlist.append((left, top, right-left))
            if left>0 and top>0 and right<w and bot<h:
                objimg = img[top:bot, left:right]
                if isCombin:
                    objname = extractpath+'/true/'+random_char(5)+'.jpg'
                else:
                    if not os.path.exists(extractpath+'/'+tag):
                        os.mkdir(extractpath+'/'+tag)
                    if type(tag)==unicode:
                        tag = tag.encode('utf-8')
                    objname = extractpath+'/'+tag+'/'+random_char(5)+'.jpg'
                cv2.imwrite(objname, objimg)
        else:
            if isGenFalse:
                left = int(obj['x_start']*w)
                right = int(obj['x_end']*w+0.5)
                top = int(obj['y_start']*h)
                bot = int(obj['y_end']*h+0.5)
                centerx = (left+right)/2
                centery = (top+bot)/2
                objw = right-left
                objh = bot-top
                if objw>=objh:
                    top = centery-objw/2
                    bot = centery+objw/2
                else:
                    left = centerx-objh/2
                    right = centerx+objh/2
                if left>0 and top>0 and right<w and bot<h:
                    objimg = img[top:bot, left:right]
                    objname = extractpath+'/false/'+random_char(5)+'.jpg'
                    cv2.imwrite(objname, objimg)
                
    if isGenFalse:
        for obj in objlist:
            num = 0
            while num<Gennum:
                size = obj[2]
                left = int(random.random()*w)
                top = int(random.random()*h)
                right = left+size
                bot = top+size
                num = num+1 # TODO
                if left>0 and top>0 and right<w and bot<h:
                    if not isCoverlist(left, top, size, objlist):
                        objimg = img[top:bot, left:right]
                        objname = extractpath+'/false/'+random_char(5)+'.jpg'
                        cv2.imwrite(objname, objimg)
    return

if __name__ == "__main__":
    filepath = sys.argv[1]
    extractpath = sys.argv[2]
    isCombin = True
    isGenFalse = True
    if not os.path.exists(extractpath):
        os.mkdir(extractpath)
    if isCombin and not os.path.exists(extractpath+'/true'):
        os.mkdir(extractpath+'/true')
    if isGenFalse and not os.path.exists(extractpath+'/false'):
        os.mkdir(extractpath+'/false')

    filelist = gettagedfilelist(filepath)
    l = len(filelist)
    for i in range(l):
        imgpath = filepath+'/data/'+filelist[i]
        annotationpath = filepath+'/label/'+filelist[i]+'.txt'
        extractobj(imgpath, annotationpath, extractpath, isCombin, isGenFalse)