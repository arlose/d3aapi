# -*- coding: utf-8 -*-

import pyyolo
import numpy as np
import sys
import cv2
import mxnet as mx
import scipy.io as sio
#from symbol.mobilenet import MobileNet
import json
#import uniout

import numpy as np
import os.path as osp

from detection.ssd.ssddetector import ssddetector

def PreprocessImage(path, meanfile, size, show_img=False):
    # load image
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # print img
    mean_img = mx.nd.load(meanfile).values()[0].asnumpy()
    # print mean_img
    if img.shape[0] > img.shape[1]:
        newsize = (size, img.shape[0] * size / img.shape[1])
    else:
        newsize = (img.shape[1] * size / img.shape[0], size)
    img = cv2.resize(img,newsize)
    if img.shape[0] > img.shape[1]:
        margin = (img.shape[0] - img.shape[1]) / 2;
        img = img[margin:margin + img.shape[1], :]
    else:
        margin = (img.shape[1] - img.shape[0]) / 2;
        img = img[:, margin:margin + img.shape[0]]
    img = np.swapaxes(img, 0, 2)
    img = np.swapaxes(img, 1, 2)
    img = img/255.0
    img = img[np.newaxis, :]
    return img

thresh = 0.24
hier_thresh = 0.5

def convertoutputyolo(outputs, w, h):
    res = '{'
    length = len(outputs)
    res += '"length": '+ str(length)
    if length != 0:
        res += ',"objects":['
        for i in range(length):
            x_start = outputs[i]['left']*1.0/w
            x_end = outputs[i]['right']*1.0/w
            y_start = outputs[i]['top']*1.0/h
            y_end = outputs[i]['bottom']*1.0/h
            tag = outputs[i]['class']
            info = str(outputs[i]['prob'])
            res += '{ "x_start": %.3lf, "y_start": %.3lf, "x_end": %.3lf, "y_end": %.3lf, "tag": ["%s"], "info": "%s"}'%(x_start, y_start, x_end, y_end, tag, info)
            if i!= length-1:
                res += ','
        res += ']'
    res += '}'
    #res.replace('\'', '\"')
    return res

def convertoutputssd(outputs):
    res = '{'
    length = len(outputs)
    res += '"length": '+ str(length)
    if length != 0:
        res += ',"objects":['
        for i in range(length):
            x_start = outputs[i][0]
            x_end = outputs[i][2]
            y_start = outputs[i][1]
            y_end = outputs[i][3]
            tag = outputs[i][4]
            info = str(outputs[i][5])
            res += '{ "x_start": %.3lf, "y_start": %.3lf, "x_end": %.3lf, "y_end": %.3lf, "tag": ["%s"], "info": "%s"}'%(x_start, y_start, x_end, y_end, tag, info)
            if i!= length-1:
                res += ','
        res += ']'
    res += '}'
    #res.replace('\'', '\"')
    return res

def convertoutputcls(label, prob, length):
    res = '{'
    res += '"length":  %d'%(length)
    res += ',"objects":['
    for i in range(length):
        tag = label[i]
        info = str(prob[i])
        res += '{ "x_start": 0.0, "y_start": 0.0, "x_end": 1.0, "y_end": 1.0, "tag": "%s", "info": "%s"}'%(tag, info)
        if i!= length-1:
            res += ','
    res += ']}'
    return res

def detection_yolo(datacfg, cfgfile, weightfile, imgfile):
    pyyolo.init(datacfg, cfgfile, weightfile)
    # image
    catograys = {}

    img = cv2.imread(imgfile)

    img = img.transpose(2,0,1)
    c, h, w = img.shape[0], img.shape[1], img.shape[2]
    #print c, h, w
    data = img.ravel()/255.0
    data = np.ascontiguousarray(data, dtype=np.float32)
    outputs = pyyolo.detect(w, h, c, data, thresh, hier_thresh)	
    #print outputs
    res = convertoutputyolo(outputs, w, h)
    pyyolo.cleanup()
    return res

def detection_mx(network, prefix, epoch, wordsfile, data_shape, imagefile):
    imagelist = [imagefile]
    outputs = ssddetector(network, prefix, epoch, wordsfile, data_shape, imagelist)   
    # print outputs
    res = convertoutputssd(outputs)
    return res

def classify(prefix, num_round, imagefile, meanfile, size, tagfile):
    model = mx.model.FeedForward.load(prefix, num_round, ctx=mx.cpu(), numpy_batch_size=1)
    batch = PreprocessImage(imagefile, meanfile, size, False)
    [prob, data1, label1] = model.predict(batch, return_data=True)
    pred = np.argsort(-prob)
    # print pred[0]
    length = min(5, len(pred[0]))
    jsondata = json.load(file(tagfile))
    label = []
    maxprob = []
    words=[]
    for name in jsondata['listname']:
            for word in jsondata['taglist'][name]:
                words.append(word)
    for i in range(length):
        label.append(words[pred[0][i]])
        maxprob.append(prob[0][pred[0][i]])
    # print label
    # print maxprob
    res = convertoutputcls(label, maxprob, length)
    return res

    # synset = [l.strip() for l in open('Inception/synset.txt').readlines()]


#symbol = MobileNet(alpha=0.5, num=10)

if __name__ == "__main__":
    # datacfg = './static/user/public/plate/train/voc.data'
    # cfgfile = './static/user/public/plate/train/yolo.cfg'
    # weightfile = './static/user/public/plate/train/yolo_final.weights'
    # res = detection(datacfg, cfgfile, weightfile, imgfile)
    # modelprefix = './static/user/fj/task110/train//classify'
    # number = 500
    # meanfile = './static/user/fj/task110/train/mean.bin'
    # tagfile = './static/user/fj/task110/tag.json'
    # res = classify(modelprefix, number, imgfile, meanfile, tagfile)

    network = 'mobilenet'
    prefix = '/home/mq/ImageServer/static/user/uniview/pdn/train/SSD_Mobilenet_300x300/pdn_mobilenet_300'
    epoch = 70
    wordsfile = '/home/mq/ImageServer/static/user/uniview/pdn/train/SSD_Mobilenet_300x300/words.txt'
    data_shape = (300, 300)

    # network = 'vgg16_reduced'
    # prefix = '/home/mq/ImageServer/static/user/uniview/foods/train/SSD_VGG16_300x300/foods_vgg16_reduced_300'
    # epoch = 200
    # wordsfile = '/home/mq/ImageServer/static/user/uniview/foods/train/SSD_VGG16_300x300/words.txt'
    # data_shape = (300, 300)

    imagefile = './test.jpg'
    res = detection_mx(network, prefix, epoch, wordsfile, data_shape, imagefile)
    print res
