#coding=utf-8
#!flask/bin/python
from flask import Flask, jsonify, Response
from flask import request, send_file
from flask_restful import reqparse
import json
import os
from flask import redirect, url_for
from werkzeug import secure_filename
import shutil
from mysqlop import *
from flask_cors import *
from detectimg import *
from glob import glob
from werkzeug.security import generate_password_hash, check_password_hash
from flask.ext.mail import Mail, Message
from threading import Thread
import random
import string
import urllib
import subprocess
import urllib2
import re
import mimetypes
import uniout
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import mlab
from matplotlib import rcParams

import Demo.PR.prsimple as prdemo
import Demo.SEALOCR.fileocr as sealocrdemo

app = Flask(__name__)

#CORS(app, supports_credentials=True)
cors = CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
# CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

LFILE_EXTENSIONS = set(['jpg', 'JPG', 'jpeg', 'JPEG','png', 'mp4', 'bmp', 'PNG', 'BMP', 'tif', 'TIF'])
IMAGE_EXTENSIONS = set(['jpg', 'JPG', 'jpeg','JPEG','png', 'bmp', 'PNG', 'BMP', 'tif', 'TIF'])
VIDEO_EXTENSIONS = set(['mp4', 'MP4'])
VIDEOU_EXTENSIONS = set(['mp4', 'MP4','avi', 'AVI', 'mts', 'MTS', 'mov', 'MOV', 'wmv', 'WMV', 'mpg', 'MPG','ts', 'TS'])
LABEL_EXTENSIONS = set(['txt'])
MODEL_EXTENSIONS = set(['params', 'weights', 'backup'])

structuresize_classify = {"mobilenet":224,
                            "shufflenet":224,
                            "googlenet":300,
                            "densenet121":224,
                            "densenet161":224,
                            "densenet169":224,
                            "densenet201":224,
                            "inception_bn":224,
                            "inception_resnet_v2":224,
                            "inception_v3":299,
                            "resnet18":224, 
                            "resnet34":224, 
                            "resnet50":224,
                            "resnet101":224,
                            "resnext18":224,
                            "resnext34":224,
                            "resnext50":224,
                            "resnext101":224,
                            "squeezenet":224,
                            "vgg11":224,
                            "vgg16":224,
                            "vgg19":224,
                            "alexnet":224,
                            "lenet":28,
                            "inception_bn_28":28,
                            "resnet20_28":28,
                            "resnet38_28":28,
                            "resnet56_28":28,
                            "resnext20_28":28,
                            "resnext38_28":28,
                            "resnext56_28":28}

structuresize_detect = {"SSD_VGG16_512x512":512,
                            "SSD_VGG16_300x300":300,
                            "SSD_Inception_v3_512x512":512,
                            "SSD_Resnet50_512x512":512,
                            "SSD_Resnet101_512x512":512,
                            "SSD_Mobilenet_300x300":300,
                            "SSD_Mobilenet_512x512":512,
                            "SSD_Mobilenet_608x608":608,
                            "Fast_rcnn_VGG":512,
                            "Faster_rcnn_Resnet101":512}

ipport = "http://demo.codvision.com:16831"
rootpath = "/static/user/"
taglistname = "/tag.json"
traininfoimage = "/train.jpg"
trainlogfile = "/test.log"
ziplabel = "/label"
zipmodel = "/model"
trainparamsfile = "/trainparams.json"
dirl = "./static/"
exampledir = rootpath+"example"
docname = "doc.txt"
scrapylogfile = 'scrapy.log'

notpassreasonfilename = 'reason.list'

filelistname = "file.list"
filewtaglistname = "filewtag.list"
filewotaglistname = "filewotag.list"
filechecklistname = "filecheck.list"
filenochecklistname = "filenocheck.list"
filepasslistname = "filepass.list"
filenopasslistname = "filenopass.list"
filestatisticlabeler = "statisticlabeler.json"
filestatisticreviewer = "statisticreviewer.json"
filelistchangename = "ischange.json"
filelistjsonstr = '{"filelist":1, "taglist":1, "notaglist":1, "tagstatics":1, "checklist":1, "notchecklist":1, "passlist":1, "notpasslist":1, "statisticlabeler": 1, "statisticreviewer":1}'

# Mail
MAIL_SERVER = 'smtp.codvision.com'
MAIL_PORT = 587
MAIL_USE_TLS = False
MAIL_USERNAME = 'web@codvision.com'
MAIL_PASSWORD = '1q2w3E4r'
FLASKY_MAIL_SUBJECT_PREFIX = '[codvision]'
FLASKY_MAIL_SENDER = 'web@codvision.com'
FLASKY_ADMIN = 'www.codvision.com'

# task status
LABELING = 1
TRAINING = 2
TRAINED = 3

# user
COMMON = 0
EDIT         = 1
MANAGE  = 2
SUPER      = 3

zhfont = matplotlib.font_manager.FontProperties(fname='simkai.ttf')

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

def random_char(num):
       return ''.join(random.choice(string.ascii_letters) for x in range(num))

def compare(x, y):  
    stat_x = os.stat(dirl+x)  
    stat_y = os.stat(dirl+y)  
    if stat_x.st_ctime < stat_y.st_ctime:  
        return -1  
    elif stat_x.st_ctime > stat_y.st_ctime:  
        return 1  
    else:  
        return 0 

def compare1(x, y):  
    stat_x = os.stat(dirl+x)  
    stat_y = os.stat(dirl+y)  
    if stat_x.st_ctime < stat_y.st_ctime:  
        return 1
    elif stat_x.st_ctime > stat_y.st_ctime:  
        return -1  
    else:  
        return 0 

def ischanged(d, sub):
    ischangelistfile = d + filelistchangename
    if os.path.exists(ischangelistfile):
        jsondata = json.load(file(ischangelistfile))
        if jsondata[sub] == 1:
            return True
        return False
    else:
        fp = open(ischangelistfile,'w')
        fp.write(filelistjsonstr)
        fp.close()
        return True

def setchanged(d, sub, value):
    ischangelistfile = d + filelistchangename
    if not os.path.exists(ischangelistfile):
        fp = open(ischangelistfile,'w')
        fp.write(filelistjsonstr)
        fp.close()
    else:
        f = file(ischangelistfile, "r")
        jsondata = json.load(f)
        jsondata[sub] = value
        f.close()
        with open(ischangelistfile, 'w') as json_file:
            json_file.write(json.dumps(jsondata))
    return 

def listfile(d, isvideo=0):
    #print 'listfile'
    fullfilelistname = d+filelistname
    namelist = []
    changed = ischanged(d, 'filelist')
    if changed or not os.path.exists(fullfilelistname):
        global dirl
        extensions = IMAGE_EXTENSIONS
        if isvideo == 1:
            extensions = VIDEO_EXTENSIONS
        for parentdir,dirname,filenames in os.walk(d):  
            for filename in filenames:  
                if filename.split('.')[-1] in extensions:  
                    namelist.append(filename)
        dirl = d
        #print namelist
        namelist.sort(compare)
        #print namelist
        fl = open(fullfilelistname, 'w')
        for name in namelist:
            fl.write(name+'\n')
        fl.close()
        setchanged(d, 'filelist', 0)
    else:
        fl = open(fullfilelistname, 'r')
        for line in fl.readlines():
            namelist.append(line.strip())
    return namelist

def listfilelink(d, taskname, isvideo=0):
    #print 'listfilelink:'+taskname
    fullfilelistname = d+taskname+'.list'
    namelist = []
    spl = taskname.split("_")
    start = int(spl[-2])
    num = int(spl[-1])
    #print start, num
    if not os.path.exists(fullfilelistname):
        fl = open(fullfilelistname, 'w')
        fulllist = listfile(d)
        for i in range(start-1, start-1+num):
            name=fulllist[i]
            namelist.append(name)
            fl.write(name+'\n')
        fl.close()
    else:
        fl = open(fullfilelistname, 'r')
        for line in fl.readlines():
            namelist.append(line.strip())
    return namelist

def listfilewithtag(d, arg=""):
    namelist = []
    # print arg
    if arg=="":
        fullfilelistname = d+filewtaglistname
        changed = ischanged(d, 'taglist')
        if changed or not os.path.exists(fullfilelistname):
            for parentdir,dirname,filenames in os.walk(d+'../data'):  
                for filename in filenames:  
                    if filename.split('.')[-1] in LFILE_EXTENSIONS:  
                        labelname = filename+'.txt'
                        if os.path.exists(d+'../label/'+labelname):
                            namelist.append(filename)
            fl = open(fullfilelistname, 'w')
            for name in namelist:
                fl.write(name+'\n')
            fl.close()
            setchanged(d, 'taglist', 0)
        else:
            fl = open(fullfilelistname, 'r')
            for line in fl.readlines():
                namelist.append(line.strip())
    else:
        if type(arg)==unicode:
            arg = arg.encode('utf-8')
        # arguments = ' -rl '+ '\"'+arg+'\" ' + d+'/*.txt'
        # print arguments
        process = subprocess.Popen(['grep', '-rl', '\"'+arg+'\"', d+'../label/'], stdout=subprocess.PIPE)
        # process = subprocess.Popen('grep'+arguments, stdout=subprocess.PIPE, shell=True)
        stdout, stderr = process.communicate()
        out = stdout.split('\n')[:-1]
        for name in out:
            namelist.append(os.path.splitext(os.path.basename(name))[0])
    # print namelist
    return namelist

def listfilewithtaglink(d, taskname, arg=""):
    namelist = []
    taskfilelist = d+taskname+'.list'
    fulllist = []
    fl = open(taskfilelist, 'r')
    for line in fl.readlines():
        fulllist.append(line.strip())
    # print arg
    if arg=="":
        for filename in fulllist:
            labelname = filename+'.txt'
            if os.path.exists(d+'../label/'+labelname):
                namelist.append(filename)
    else:
        if type(arg)==unicode:
            arg = arg.encode('utf-8')
        for filename in fulllist:
            labelname = filename+'.txt'
            with open(d+'../label/'+labelname) as foo:
                for line in foo.readlines():
                    if arg in line:
                        namelist.append(filename)
                        break
    # print namelist
    return namelist

def listfilewithouttag(d, isvideo=0):
    fullfilelistname = d+filewotaglistname
    changed = ischanged(d, 'notaglist')
    namelist = []
    if changed or not os.path.exists(fullfilelistname):
        for parentdir,dirname,filenames in os.walk(d):  
            for filename in filenames:  
                if filename.split('.')[-1] in LFILE_EXTENSIONS:  
                    labelname = filename+'.txt'
                    if not os.path.exists((d+labelname).replace('/data/','/label/')):
                        namelist.append(filename)
        fl = open(fullfilelistname, 'w')
        for name in namelist:
            fl.write(name+'\n')
        fl.close()
        setchanged(d, 'notaglist', 0)
    else:
        fl = open(fullfilelistname, 'r')
        for line in fl.readlines():
            namelist.append(line.strip())
    return namelist

def listfilewithouttaglink(d, taskname, isvideo=0):
    namelist = []
    taskfilelist = d+taskname+'.list'
    fulllist = []
    fl = open(taskfilelist, 'r')
    for line in fl.readlines():
        fulllist.append(line.strip())
    for filename in full:
        labelname = filename+'.txt'
        if not os.path.exists(d+'../label/'+labelname):
            namelist.append(filename)
    return namelist

def listfilechecked(d):
    namelist = []
    labeledlist = listfilewithtag(d, "")
    changed = ischanged(d, 'checklist')
    fullfilelistname = d+filechecklistname
    if changed or not os.path.exists(fullfilelistname):
        for labelfile in labeledlist:
            libelfilepath = (d+labelfile+'.txt').replace('/data/','/label/')
            jsondata = json.load(open(libelfilepath))
            checked = True
            for obj in jsondata['objects']:
                if 'checked' not in obj:
                    checked = False
                    break
            if checked:
                namelist.append(labelfile)
        fl = open(fullfilelistname, 'w')
        for name in namelist:
            fl.write(name+'\n')
        fl.close()
        setchanged(d, 'checklist', 0)
    else:
        fl = open(fullfilelistname, 'r')
        for line in fl.readlines():
            namelist.append(line.strip())
    return namelist

def listfilecheckedlink(d, taskname):
    namelist = []
    labeledlist = listfilewithtaglink(d, taskname, "")
    for labelfile in labeledlist:
        libelfilepath = (d+labelfile+'.txt').replace('/data/','/label/')
        jsondata = json.load(open(libelfilepath))
        checked = True
        for obj in jsondata['objects']:
            if 'checked' not in obj:
                checked = False
                break
        if checked:
            namelist.append(labelfile)
    return namelist

def listfilenotchecked(d):
    namelist = []
    labeledlist = listfilewithtag(d, "")
    changed = ischanged(d, 'notchecklist')
    fullfilelistname = d+filenochecklistname
    if changed or not os.path.exists(fullfilelistname):
        for labelfile in labeledlist:
            libelfilepath = (d+labelfile+'.txt').replace('/data/','/label/')
            jsondata = json.load(open(libelfilepath))
            notchecked = False
            for obj in jsondata['objects']:
                if 'checked' not in obj:
                    notchecked = True
                    break
            if notchecked:
                namelist.append(labelfile)
        fl = open(fullfilelistname, 'w')
        for name in namelist:
            fl.write(name+'\n')
        fl.close()
        setchanged(d, 'notchecklist', 0)
    else:
        fl = open(fullfilelistname, 'r')
        for line in fl.readlines():
            namelist.append(line.strip())
    return namelist

def listfilenotcheckedlink(d, taskname):
    namelist = []
    labeledlist = listfilewithtaglink(d, taskname, "")
    for labelfile in labeledlist:
        libelfilepath = (d+labelfile+'.txt').replace('/data/','/label/')
        jsondata = json.load(open(libelfilepath))
        notchecked = False
        for obj in jsondata['objects']:
            if 'checked' not in obj:
                notchecked = True
                break
        if notchecked:
            namelist.append(labelfile)
    return namelist

def listfilepassed(d):
    namelist = []
    labeledlist = listfilechecked(d)
    changed = ischanged(d, 'passlist')
    fullfilelistname = d+filepasslistname
    if changed or not os.path.exists(fullfilelistname):
        for labelfile in labeledlist:
            libelfilepath = (d+labelfile+'.txt').replace('/data/','/label/')
            jsondata = json.load(open(libelfilepath))
            passed = True
            for obj in jsondata['objects']:
                if obj['checked'] == "NO":
                    passed = False
                    break
            if passed:
                namelist.append(labelfile)
        fl = open(fullfilelistname, 'w')
        for name in namelist:
            fl.write(name+'\n')
        fl.close()
        setchanged(d, 'passlist', 0)
    else:
        fl = open(fullfilelistname, 'r')
        for line in fl.readlines():
            namelist.append(line.strip())
    return namelist

def listfilepassedlink(d, taskname):
    namelist = []
    labeledlist = listfilecheckedlink(d, taskname)
    for labelfile in labeledlist:
        libelfilepath = (d+labelfile+'.txt').replace('/data/','/label/')
        jsondata = json.load(open(libelfilepath))
        passed = True
        for obj in jsondata['objects']:
            if obj['checked'] == "NO":
                passed = False
                break
        if passed:
            namelist.append(labelfile)
    return namelist


def listfilenotpassed(d):
    namelist = []
    labeledlist = listfilechecked(d)
    changed = ischanged(d, 'notpasslist')
    fullfilelistname = d+filenopasslistname
    if changed or not os.path.exists(fullfilelistname):
        for labelfile in labeledlist:
            libelfilepath = (d+labelfile+'.txt').replace('/data/','/label/')
            jsondata = json.load(open(libelfilepath))
            notpass = False
            for obj in jsondata['objects']:
                if obj['checked'] == "NO":
                    notpass = True
                    break
            if notpass:
                namelist.append(labelfile)
        fl = open(fullfilelistname, 'w')
        for name in namelist:
            fl.write(name+'\n')
        fl.close()
        setchanged(d, 'notpasslist', 0)
    else:
        fl = open(fullfilelistname, 'r')
        for line in fl.readlines():
            namelist.append(line.strip())
    return namelist

def listfilenotpassedlink(d, taskname):
    namelist = []
    labeledlist = listfilecheckedlink(d, taskname)
    for labelfile in labeledlist:
        libelfilepath = (d+labelfile+'.txt').replace('/data/','/label/')
        jsondata = json.load(open(libelfilepath))
        notpass = False
        for obj in jsondata['objects']:
            if obj['checked'] == "NO":
                notpass = True
                break
        if notpass:
            namelist.append(labelfile)
    return namelist

def statisticlabeler(d):
    taggerlist = {}
    labeledlist = listfilewithtag(d, "")
    changed = ischanged(d, 'statisticlabeler')
    fullfilelistname = d+filestatisticlabeler
    if changed or not os.path.exists(fullfilelistname):
        for labelfile in labeledlist:
            labelfilepath = (d+labelfile+'.txt').replace('/data/','/label/')
            jsondata = json.load(open(labelfilepath))
            for obj in jsondata['objects']:
                if 'tagger' in obj:
                    if obj['tagger'] not in taggerlist:
                        taggerlist[obj['tagger']] = [1, 0, 0]
                        if 'checked' in obj:
                            taggerlist[obj['tagger']][1] = 1
                            if obj['checked'] == 'YES':
                                taggerlist[obj['tagger']][2] = 1
                    else:
                        taggerlist[obj['tagger']][0] = taggerlist[obj['tagger']][0] + 1
                        if 'checked' in obj:
                            taggerlist[obj['tagger']][1] = taggerlist[obj['tagger']][1] + 1
                            if obj['checked'] == 'YES':
                                taggerlist[obj['tagger']][2] = taggerlist[obj['tagger']][2] + 1
        fl = open(fullfilelistname, 'w')
        fl.write(json.dumps(taggerlist))
        fl.close()
        setchanged(d, 'statisticlabeler', 0)
    else:
        fl = open(fullfilelistname, 'r')
        taggerlist = json.load(fl)
    return taggerlist

def statisticreviewer(d):
    reviewerlist = {}
    labeledlist = listfilewithtag(d, "")
    changed = ischanged(d, 'statisticreviewer')
    fullfilelistname = d+filestatisticreviewer
    if changed or not os.path.exists(fullfilelistname):
        for labelfile in labeledlist:
            labelfilepath = (d+labelfile+'.txt').replace('/data/','/label/')
            jsondata = json.load(open(labelfilepath))
            for obj in jsondata['objects']:
                if 'reviewer' in obj:
                    if obj['reviewer'] not in reviewerlist:
                        reviewerlist[obj['reviewer']] = 1
                    else:
                        reviewerlist[obj['reviewer']] = reviewerlist[obj['reviewer']] + 1
        fl = open(fullfilelistname, 'w')
        fl.write(json.dumps(reviewerlist))
        fl.close()
        setchanged(d, 'statisticreviewer', 0)
    else:
        fl = open(fullfilelistname, 'r')
        reviewerlist = json.load(fl)
    return reviewerlist

'''
def listfilelabelby(d, usrname):
    namelist = []
    labeledlist = listfilewithtag(d, "")
    for labelfile in labeledlist:
        labelfilepath = (d+labelfile+'.txt').replace('/data/','/label/')
        jsondata = json.load(open(labelfilepath))
        flag = False
        for obj in jsondata['objects']:
            if 'tagger' in obj:
                if obj['tagger']==usrname:
                    flag = True
        if flag:
            namelist.append(labelfile)
    return namelist

def listfilecheckby(d, usrname):
    namelist = []
    labeledlist = listfilewithtag(d, "")
    for labelfile in labeledlist:
        labelfilepath = (d+labelfile+'.txt').replace('/data/','/label/')
        jsondata = json.load(open(labelfilepath))
        flag = False
        for obj in jsondata['objects']:
            if 'reviewer' in obj:
                if obj['reviewer'] == usrname:
                    flag = True
        if flag:
            namelist.append(labelfile)
    return namelist
'''

def countchecked(d):
    m = len(listfilechecked(d))
    return m

def countcheckedlink(d, taskname):
    m = len(listfilecheckedlink(d, taskname))
    return m

def countpassed(d):
    m = len(listfilepassed(d))
    return m

def countpassedlink(d, taskname):
    m = len(listfilepassedlink(d, taskname))
    return m

def countimagefilenum(d):
    m=0
    fullfilelistname = d+filelistname
    changed = ischanged(d, 'filelist')
    if changed or not os.path.exists(fullfilelistname):
        # print 'countimagefilenum', d
        for parentdir,dirname,filenames in os.walk(d):  
            for filename in filenames:  
                if filename.split('.')[-1] in LFILE_EXTENSIONS:   
                    m=m+1
    else:
        listfile = open(fullfilelistname) 
        m = len(listfile.readlines()) 
    return m

def countlabelfilenum(d):
    m=0
    # print 'countlabelfilenum ', d
    fullfilelistname = d+filewtaglistname
    changed = ischanged(d, 'taglist')
    if changed or not os.path.exists(fullfilelistname):
        for parentdir,dirname,filenames in os.walk(d):  
            for filename in filenames:  
                if filename.split('.')[-1] in LFILE_EXTENSIONS:  
                    labelname = filename+'.txt'
                    if os.path.exists((d+'/'+labelname).replace('/data/','/label/')):
                        m=m+1
    else:
        listfile = open(fullfilelistname) 
        m = len(listfile.readlines()) 
    return m

def countlabelfilenumlink(d, filelist, start, num):
    m=0
    for i in range(start-1, start-1+num):  
        filename = d+filelist[i]
        if filename.split('.')[-1] in LFILE_EXTENSIONS:  
            labelname = filename+'.txt'
            #print labelname
            if os.path.exists(labelname.replace('/data/','/label/')):
                m=m+1  
    return m

def getstatisticslink(d, filelist, start, num, tagfile):
    words = []
    if os.path.exists(tagfile):
        jsondata = json.load(file(tagfile))
        #print jsondata
        for name in jsondata['listname']:
            for word in jsondata['taglist'][name]:
                words.append(word)
        #print words
    else:
        words = ['tag1', 'tag2', 'tag3']        
    wordscount = dict.fromkeys(words,0)

    if True:
        for i in range(start-1, start-1+num):  
            filename = d+filelist[i]
            #print filename
            if filename.split('.')[-1] in LFILE_EXTENSIONS:  
                labelname = (filename+'.txt').replace('/data/','/label/')
                if os.path.exists(labelname):
                    labeldata = json.load(file(labelname))
                    for obj in labeldata['objects']:
                        for w in obj['tag']:
                            if w in wordscount:
                                wordscount[w] = wordscount[w]+ 1
        wl = len(words)
        # print wl
        string = "{"
        for i in range(wl-1):
            w = words[i]
            # print w
            #print "%s:%d,"%(w, wordscount[w])
            tempstr = 'u"%s": %d, '%(w, wordscount[w])
            if type(tempstr)==unicode:
                tempstr = tempstr.encode('utf-8')
            string = string + tempstr
            # print string
        w = words[wl-1]
        # print string
        tempstr = 'u"%s": %d'%(w, wordscount[w])
        if type(tempstr)==unicode:
            tempstr = tempstr.encode('utf-8')
        string = string + tempstr
        string = string + "}"
        # print string
        return string
    else:
        return '{}'
def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x()+rect.get_width()/2., 1.03*height, '%d' % int(height))

def getstatisticsfiglink(d, filelist, start, num, tagfile, figfile):
    words = []
    if os.path.exists(tagfile):
        jsondata = json.load(file(tagfile))
        #print jsondata
        for name in jsondata['listname']:
            for word in jsondata['taglist'][name]:
                words.append(word)
        #print words
    else:
        words = ['tag1', 'tag2', 'tag3']        
    wordscount = dict.fromkeys(words,0)

    if True:
        startleft = 0
        step = 0.6
        width = 0.4
        for i in range(start-1, start-1+num):  
            filename = d+filelist[i]
            #print filename
            if filename.split('.')[-1] in LFILE_EXTENSIONS:  
                labelname = (filename+'.txt').replace('/data/','/label/')
                if os.path.exists(labelname):
                    labeldata = json.load(file(labelname))
                    for obj in labeldata['objects']:
                        for w in obj['tag']:
                            if w in wordscount:
                                wordscount[w] = wordscount[w]+ 1
        wl = len(words)
        plt.figure(figsize=(wl*step,6)) 
        leftlist = []
        heightlist = []
        colorlist = []
        for i in range(wl):
            w = words[i]
            r = random.random()
            g = random.random()
            b = random.random()
            leftlist.append(startleft+i*step)
            heightlist.append(wordscount[w])
            colorlist.append((r, g, b))
        rects =plt.bar(left=leftlist,height = heightlist,color=colorlist, width =width,align="center",yerr=0.00001)
        autolabel(rects)
        plt.legend()
        plt.xticks(np.arange(startleft, startleft+wl*step, step),words, rotation=30, fontproperties=zhfont)
        plt.title('statistics')
        plt.savefig(figfile)
        plt.close('all')
    return

def getstatistics(d, tagfile):
    print 'getstatistics', d, tagfile
    words = []
    if os.path.exists(tagfile):
        jsondata = json.load(file(tagfile))
        #print jsondata
        for name in jsondata['listname']:
            for word in jsondata['taglist'][name]:
                words.append(word)
        #print words
    else:
        words = ['tag1', 'tag2', 'tag3']        
    wordscount = dict.fromkeys(words,0)

    if True:
        for parentdir,dirname,filenames in os.walk(d):  
            for filename in filenames:  
                if filename.split('.')[-1] in LFILE_EXTENSIONS:  
                    labelname = filename+'.txt'
                    labelfile = (d+labelname).replace('/data/','/label/')
                    if os.path.exists(labelfile):
                        labeldata = json.load(file(labelfile))
                        for obj in labeldata['objects']:
                            #print obj
                            for w in obj['tag']:
                                if w in wordscount:
                                    wordscount[w] = wordscount[w]+ 1
        wl = len(words)
        # print wl
        string = "{"
        for i in range(wl-1):
            w = words[i]
            # print w
            #print "%s:%d,"%(w, wordscount[w])
            tempstr = 'u"%s": %d, '%(w, wordscount[w])
            if type(tempstr)==unicode:
                tempstr = tempstr.encode('utf-8')
            string = string + tempstr
            # print string
        w = words[wl-1]
        # print string
        tempstr = 'u"%s": %d'%(w, wordscount[w])
        if type(tempstr)==unicode:
            tempstr = tempstr.encode('utf-8')
        string = string + tempstr
        string = string + "}"
        # print string
        return string
    else:
        return '{}'


def getstatisticsfig(d, tagfile, figfile):
    #print 'getstatistics', d, tagfile
    # fig1 = plt.figure()
    startleft = 0
    step = 0.6
    width = 0.4
    words = []
    if os.path.exists(tagfile):
        jsondata = json.load(file(tagfile))
        #print jsondata
        for name in jsondata['listname']:
            for word in jsondata['taglist'][name]:
                words.append(word)
        #print words
    else:
        words = ['tag1', 'tag2', 'tag3']        
    wordscount = dict.fromkeys(words,0)

    if True:
        for parentdir,dirname,filenames in os.walk(d):  
            for filename in filenames:  
                if filename.split('.')[-1] in LFILE_EXTENSIONS:  
                    labelname = filename+'.txt'
                    labelfile = (d+labelname).replace('/data/','/label/')
                    if os.path.exists(labelfile):
                        labeldata = json.load(file(labelfile))
                        for obj in labeldata['objects']:
                            #print obj
                            for w in obj['tag']:
                                if w in wordscount:
                                    wordscount[w] = wordscount[w]+ 1

        wl = len(words)
        #print wordscount
        figw = wl*step
        if figw < 8:
            figw = 8
        plt.figure(figsize=(figw,6)) 
        leftlist = []
        heightlist = []
        colorlist = []
        for i in range(wl):
            w = words[i]
            r = random.random()
            g = random.random()
            b = random.random()
            leftlist.append(startleft+i*step)
            heightlist.append(wordscount[w])
            colorlist.append((r, g, b))
        rects =plt.bar(left=leftlist,height = heightlist,color=colorlist, width =width,align="center",yerr=0.00001)
        autolabel(rects)
        plt.legend()
        plt.xticks(np.arange(startleft, startleft+wl*step, step),words, rotation=30, fontproperties=zhfont)
        plt.title('statistics')
        plt.savefig(figfile)
        plt.close('all')
    return

MB = 1 << 20
BUFF_SIZE = 10 * MB

def partial_response(path, start, end=None):
    print('Requested: %s, %s'%(start, end))
    file_size = os.path.getsize(path)
    print file_size

    # Determine (end, length)
    if end is None:
        end = start + BUFF_SIZE - 1
    end = min(end, file_size - 1)
    end = min(end, start + BUFF_SIZE - 1)
    length = end - start + 1

    # Read file
    with open(path, 'rb') as fd:
        fd.seek(start)
        bytes = fd.read(length)
    assert len(bytes) == length

    print path

    response = Response(
        bytes,
        206,
        mimetype=mimetypes.guess_type(path)[0],
        direct_passthrough=True,
    )
    print response
    response.headers.add(
        'Content-Range', 'bytes {0}-{1}/{2}'.format(
            start, end, file_size,
        ),
    )
    response.headers.add(
        'Accept-Ranges', 'bytes'
    )
    print('Response: %s'%response)
    print('Response: %s'%response.headers)
    return response

def get_range(request):
    range = request.headers.get('Range')
    print('Requested: %s'%range)
    #m = re.match('bytes=(?P<start>\d+)-(?P<end>\d+)?', range)
    m = None
    print m
    if m:
        start = m.group('start')
        end = m.group('end')
        start = int(start)
        if end is not None:
            end = int(end)
        return start, end
    else:
        return 0, None

def getmodellist(modelpath):
    global dirl
    mlist = []
    for parentdir,dirname,filenames in os.walk(modelpath):  
        for filename in filenames:  
            if filename.split('.')[-1] in MODEL_EXTENSIONS:  
                mlist.append(filename)
    dirl = modelpath
    mlist.sort(compare)
    return mlist

def getmodellistall(modelpath):
    mlist = []
    for parentdir,dirname,filenames in os.walk(modelpath):  
        for filename in filenames:  
            if filename.split('.')[-1] in MODEL_EXTENSIONS:  
                mlist.append(filename)
    return mlist

def getstructure(trainpath):
    global dirl
    slist = []
    for parentdir,dirname,filenames in os.walk(trainpath):  
        if len(dirname) !=0:
            for dirn in dirname:
                if(os.path.isdir(trainpath + dirn)):
                    slist.append(dirn)
    dirl = trainpath
    slist.sort(compare1)
    return slist

def getstructurefrommodel(modelname):
    structurename = ''
    epoch = 0
    # detection
    if 'vgg16_reduced_300' in modelname:
        structurename = 'SSD_VGG16_300x300'
        epoch = int(modelname.split('.')[0].split('-')[-1])
    elif 'vgg16_reduced_512' in modelname:
        structurename = 'SSD_VGG16_512x512'
        epoch = int(modelname.split('.')[0].split('-')[-1])
    elif 'yolo' in modelname:
        structurename = 'yolo2'
    elif 'resnet50_512' in modelname:
        structurename = 'SSD_Resnet50_512x512'
        epoch = int(modelname.split('.')[0].split('-')[-1])
    elif 'resnet101_512' in modelname:
        structurename = 'SSD_Resnet101_512x512'
        epoch = int(modelname.split('.')[0].split('-')[-1])
    elif 'mobilenet_300' in modelname:
        structurename = 'SSD_Mobilenet_300x300'
        epoch = int(modelname.split('.')[0].split('-')[-1])
    elif 'mobilenet_512' in modelname:
        structurename = 'SSD_Mobilenet_512x512'
        epoch = int(modelname.split('.')[0].split('-')[-1])
    elif 'mobilenet_608' in modelname:
        structurename = 'SSD_Mobilenet_608x608'
        epoch = int(modelname.split('.')[0].split('-')[-1])
    elif 'inceptionv3_512' in modelname:
        structurename = 'SSD_Inception_v3_512x512'
        epoch = int(modelname.split('.')[0].split('-')[-1])
    # classify
    else:
        structurename = int(modelname.split('.')[0].split('-')[-2])
        epoch = int(modelname.split('.')[0].split('-')[-1])
    print structurename, epoch
    return structurename, epoch

def operationlog(info, types, usrname, ip="0.0.0.0"):
    db = Database()
    db.operationrecord(info, types, usrname, ip)

@app.route('/')
def root():
    return app.send_static_file('index.html')

#@cors.crossdomain(origin='*')
#@cors
#@app.after_request
@app.route('/static/<url>')
def imageshow(url):
    return url_for('static', filename=url) #,{'Access-Control-Allow-Origin': '*'} 


@app.route('/video')
def videoshow():
    path = 'test.mp4'
    start, end = get_range(request)
    result = partial_response(path, start, end)
    return result

# user api
@app.route('/api/userreg', methods = ['POST'])
def api_user_reg():
    curr_path = os.path.abspath(os.path.dirname(__file__))
    data = json.loads(request.data)
    usrname = data['name']
    email = data['email']
    passwd = data['passwd']
    active = data['active']
    level = data['level']
    groups = data['group']
    ipaddr = str(request.remote_addr)
    operationlog(""+ usrname + " " + email, "userreg", usrname, ipaddr)
    db = Database()
    passwd_hash = generate_password_hash(passwd)
    res = db.addusr(usrname, email, passwd_hash, active, level, groups, ipaddr)
    url = curr_path + rootpath + usrname
    if res:
        if not os.path.exists(url):
            os.mkdir(url)
        # add example task
        taskname = "example"
        tasktype = 0
        examplepath = curr_path + exampledir
        cmd = "cp -r %s %s"%(examplepath, url)
        os.system(cmd)
        db.writeTask(taskname, tasktype, 0.0, usrname)
        return 'OK'
    else:
        return "error: usrname or email exists"

@app.route('/api/userlogin', methods = ['POST'])
def api_user_login():
    curr_path = os.path.abspath(os.path.dirname(__file__))
    data = json.loads(request.data)
    usrname = data['name']
    passwd = data['passwd']
    #print usrname, passwd
    ipaddr = str(request.remote_addr)
    operationlog(""+ usrname, "userlogin", usrname,  ipaddr)
    url1 = curr_path + rootpath + usrname
    #print url1
    db = Database()
    #print 'verifyusr'
    res, level, group = db.verifyusr(usrname, passwd)
    #print res, level ,group
    if res:
        db.updateusrlogininfo(usrname, ipaddr)
        return '{"status":"OK", "level": %d, "group": "%s"}'%(level, group)
    else:
        #print usrname, passwd
        return '{"status":"Fail", "level": 0, "group": "common"}'

@app.route('/api/userlevel', methods = ['GET'])
def api_user_level():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    db = Database()
    res = db.qureyUserLevel(usrname)
    if len(res)>0:
        return str(res[0][0])
    else:
        return str(0)

@app.route('/api/getuserlist', methods = ['POST'])
def api_get_usrlist():
    curr_path = os.path.abspath(os.path.dirname(__file__))
    data = json.loads(request.data)
    usrname = data['name']
    passwd = data['passwd']
    #operationlog(""+ usrname, "getuserlist", usrname, str(request.remote_addr))
    db = Database()
    res, level, group = db.verifyusr(usrname, passwd)
    usrlist = []
    if res and level == SUPER:
        dbres = db.getuserlist()
        for usr in dbres:
            usrlist.append(usr)
    return str(usrlist)

@app.route('/api/getuserlist1', methods = ['GET'])
def api_get_usrlist1():
    usrlist = []
    db = Database()
    dbres = db.getuserlist()
    for usr in dbres:
        usrlist.append(usr)
    return str(usrlist)

@app.route('/api/delusr', methods = ['POST'])
def api_del_usr():
    curr_path = os.path.abspath(os.path.dirname(__file__))
    data = json.loads(request.data)
    usrname = data['name']
    passwd = data['passwd']
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    delusrname = args.get('usrname')
    operationlog(""+ usrname + " " + delusrname, "delusr", usrname,  str(request.remote_addr))
    db = Database()
    res, level, group  = db.verifyusr(usrname, passwd)
    if res and level == SUPER:
        db.delusr(delusrname)
        return 'OK'
    return 'Fail'

@app.route('/api/setusrlevel', methods = ['POST'])
def api_set_usrlevel():
    curr_path = os.path.abspath(os.path.dirname(__file__))
    data = json.loads(request.data)
    usrname = data['name']
    passwd = data['passwd']
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('level', type=int, location='args', required=True)
    args = get_parser.parse_args()
    setusrname = args.get('usrname')
    setlevel = args.get('level')
    operationlog(""+ setusrname + " " + str(setlevel), "setusrlevel", usrname, str(request.remote_addr))
    db = Database()
    res, level, group  = db.verifyusr(usrname, passwd)
    if res and level == SUPER:
        db.setusrlevel(setusrname, setlevel)
        return 'OK'
    return 'Fail'

@app.route('/api/setusrgroup', methods = ['POST'])
def api_set_usrgroup():
    curr_path = os.path.abspath(os.path.dirname(__file__))
    data = json.loads(request.data)
    usrname = data['name']
    passwd = data['passwd']
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('group', type=str, location='args', required=True)
    args = get_parser.parse_args()
    setusrname = args.get('usrname')
    setgroup = args.get('group')
    operationlog(""+ setusrname + " " + setgroup, "setusrgroup", usrname, str(request.remote_addr))
    db = Database()
    res, level, group  = db.verifyusr(usrname, passwd)
    if res and level == SUPER:
        db.setusrgroup(setusrname, setgroup)
        return 'OK'
    return 'Fail'

@app.route('/api/setusremail', methods = ['POST'])
def api_set_usremail():
    curr_path = os.path.abspath(os.path.dirname(__file__))
    data = json.loads(request.data)
    usrname = data['name']
    passwd = data['passwd']
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('email', type=str, location='args', required=True)
    args = get_parser.parse_args()
    setusrname = args.get('usrname')
    email = args.get('email')
    operationlog(""+ setusrname + " " + email, "setusremail", usrname,  str(request.remote_addr))
    db = Database()
    res, level, group  = db.verifyusr(usrname, passwd)
    if res and level == SUPER:
        db.setusremail(setusrname, email)
        return 'OK'
    return 'Fail'

@app.route('/api/setusrpasswd', methods = ['POST'])
def api_set_usrepasswd():
    curr_path = os.path.abspath(os.path.dirname(__file__))
    data = json.loads(request.data)
    usrname = data['name']
    passwd = data['passwd']
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('passwd', type=str, location='args', required=True)
    args = get_parser.parse_args()
    setusrname = args.get('usrname')
    setpasswd = args.get('passwd')
    setpasswd_hash = generate_password_hash(setpasswd)
    operationlog(""+ setusrname + " " + setpasswd, "setusrpasswd", usrname, str(request.remote_addr))
    db = Database()
    res, level, group  = db.verifyusr(usrname, passwd)
    if res and level == SUPER:
        db.setusrpasswd(setusrname, setpasswd_hash)
        return 'OK'
    return 'Fail'

# group API
@app.route('/api/getgrouplist', methods = ['GET'])
def api_get_grouplist():
    db = Database()
    res = db.getgrouplist()
    grouplist = []
    for group in res:
        grouplist.append(group[0])
    return str(grouplist)

@app.route('/api/addgroup', methods = ['POST'])
def api_add_group():
    curr_path = os.path.abspath(os.path.dirname(__file__))
    data = json.loads(request.data)
    usrname = data['name']
    passwd = data['passwd']
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('groupname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    groupname = args.get('groupname')
    operationlog(""+ groupname, "addgroup", usrname,  str(request.remote_addr))
    db = Database()
    res, level, group  = db.verifyusr(usrname, passwd)
    if res and level == SUPER:
        db.addgroup(groupname)
        return 'OK'
    return 'Fail'

@app.route('/api/delgroup', methods = ['POST'])
def api_del_group():
    curr_path = os.path.abspath(os.path.dirname(__file__))
    data = json.loads(request.data)
    usrname = data['name']
    passwd = data['passwd']
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('groupname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    groupname = args.get('groupname')
    operationlog(""+ groupname, "delgroup", usrname, str(request.remote_addr))
    db = Database()
    res, level, group  = db.verifyusr(usrname, passwd)
    if res and level == SUPER:
        db.delgroup(groupname)
        return 'OK'
    return 'Fail'

# file API
@app.route('/api/getfile', methods = ['GET'])
def api_get_file():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')  #start from 1
    #operationlog(""+ usrname + " " + taskname + " " + str(start) + " " + str(num), "getdir", usrname,  str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskurl = curr_path + rootpath + usrname + "/" + taskname
    # print taskurl

    url = taskurl + "/data/"
    name = filename
    labeled = 0

    filepath = url + name
    # print filepath

    if not os.path.exists(filepath):
        return '[]'

    string = '['
    labelname = (url + name+'.txt').replace('/data/','/label/')
    if os.path.exists(labelname):
        labeled = 1
    else:
        labeled = 0
    ipport1 = ipport
    if name.split('.')[-1] in VIDEO_EXTENSIONS:  
        ipport1 = ipport.replace('16831','16830')
    string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/" + name + '", "labeled": ' + str(labeled) + '}'
    string += ']'
    # print string
    return string

@app.route('/api/getdir', methods = ['GET'])
def api_get_dir():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('start', type=int, location='args', required=True)
    get_parser.add_argument('num', type=int, location='args', required=True)
    get_parser.add_argument('video', type=int, location='args', required=False)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    start = args.get('start')  #start from 1
    num = args.get('num')
    isvideo = args.get('video')
    #operationlog(""+ usrname + " " + taskname + " " + str(start) + " " + str(num), "getdir", usrname,  str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskurl = curr_path + rootpath + usrname + "/" + taskname
    #print taskurl

    url = taskurl + "/data/"
    labeled = 0
    namelist = []
    if os.path.exists(url):
        if os.path.islink(taskurl):
            namelist = listfilelink(url, taskname, isvideo)
        else:
            namelist = listfile(url, isvideo)
        #print namelist
        string = '['
        end = len(namelist)
        # if os.path.islink(taskurl):
        #     namelist = listfile(url, taskname, isvideo)
        #     spl = taskurl.split("_")
        #     gstart = int(spl[-2])
        #     gnum = int(spl[-1])
        #     start = gstart+start-1
        #     end = gstart+gnum-1
        if end>=1:
            if start > end:
                start = end
            if start+num > end:
                num = end-start+1
            for i in range(start-1, start-1+num-1):
                name = namelist[i]
                labelname = (url + name+'.txt').replace('/data/','/label/')
                if os.path.exists(labelname):
                    labeled = 1
                else:
                    labeled = 0
                ipport1 = ipport
                #print ipport
                if name.split('.')[-1] in VIDEO_EXTENSIONS:  
                    ipport1 = ipport.replace('16831','16830')
                #print ipport1
                string += '{ "name": "' + name + '", "url": "' + ipport1+ rootpath + usrname + "/" + taskname + "/data/"  + name + '", "labeled": ' + str(labeled) + '},'
                #print string
                #string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/"  + name + ' {"Access-Control-Allow-Origin": "*"} ", "labeled": ' + str(labeled) + '},'
            name = namelist[start-1+num-1]
            #print name
            labelname = (url + name+'.txt').replace('/data/','/label/')
            if os.path.exists(labelname):
                labeled = 1
            else:
                labeled = 0
            ipport1 = ipport
            if name.split('.')[-1] in VIDEO_EXTENSIONS:  
                ipport1 = ipport.replace('16831','16830')
            string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/" + name + '", "labeled": ' + str(labeled) + '}'
            #string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/" + name + ' {"Access-Control-Allow-Origin": "*"} ", "labeled": ' + str(labeled) + '}'
        string += ']'
        #print string
        return string
    else:
        return "[]"

# TODO link
@app.route('/api/getdirwithtag', methods = ['POST'])
def api_get_dirwithtag():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('start', type=int, location='args', required=True)
    get_parser.add_argument('num', type=int, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    start = args.get('start')  #start from 1
    num = args.get('num')
    data = json.loads(request.data)
    tag = data['tag']
    operationlog(""+ usrname + " " + taskname + " " + str(start) + " " + str(num), "getdirwithtag", usrname,  str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskdataurl = curr_path + rootpath + usrname + "/" + taskname
    print taskdataurl
    if os.path.islink(taskdataurl):
        namelist = listfilewithtaglink(taskdataurl+'/data/', taskname, tag)
    else:
        namelist = listfilewithtag(taskdataurl+'/data/', tag)
    string = '['
    end = len(namelist)
    if end>=1:
        if start > end:
            start = end
        if start+num > end:
            num = end-start+1
        for i in range(start-1, start-1+num-1):
            name = namelist[i]
            ipport1 = ipport
            if name.split('.')[-1] in VIDEO_EXTENSIONS:  
                ipport1 = ipport.replace('16831','16830')
            string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/"  + name + '", "labeled": 1},'
        name = namelist[start-1+num-1]
        ipport1 = ipport
        if name.split('.')[-1] in VIDEO_EXTENSIONS:  
            ipport1 = ipport.replace('16831','16830')
        string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/" + name + '", "labeled": 1}'
    string += ']'
    return string

# @app.route('/api/getdirwithtagget', methods = ['GET'])
# def api_get_dirwithtagget():
#     get_parser = reqparse.RequestParser()
#     get_parser.add_argument('usrname', type=str, location='args', required=True)
#     get_parser.add_argument('taskname', type=str, location='args', required=True)
#     get_parser.add_argument('start', type=int, location='args', required=True)
#     get_parser.add_argument('num', type=int, location='args', required=True)
#     get_parser.add_argument('tag', type=str, location='args', required=True)
#     args = get_parser.parse_args()
#     usrname = args.get('usrname')
#     taskname = args.get('taskname')
#     start = args.get('start')  #start from 1
#     num = args.get('num')
#     tag = args.get('tag')
#     operationlog(""+ usrname + " " + taskname + " " + str(start) + " " + str(num) + " " + tag, "getdirwithtag", usrname, str(request.remote_addr))
#     curr_path = os.path.abspath(os.path.dirname(__file__))
#     taskdataurl = curr_path + rootpath + usrname + "/" + taskname + '/data'
#     namelist = listfilewithtag(taskdataurl, tag)
#     string = '['
#     end = len(namelist)
#     if end>=1:
#         if start > end:
#             start = end
#         if start+num > end:
#             num = end-start+1
#         for i in range(start-1, start-1+num-1):
#             name = namelist[i]
#             string += '{ "name": "' + name + '", "url": "' + ipport + rootpath + usrname + "/" + taskname + "/data/"  + name + '", "labeled": 1},'
#         name = namelist[start-1+num-1]
#         string += '{ "name": "' + name + '", "url": "' + ipport + rootpath + usrname + "/" + taskname + "/data/" + name + '", "labeled": 1}'
#     string += ']'
#     return string

@app.route('/api/getdirwithouttag', methods = ['GET'])
def api_get_dirwithouttag():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('start', type=int, location='args', required=True)
    get_parser.add_argument('num', type=int, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    start = args.get('start')  #start from 1
    num = args.get('num')
    operationlog(""+ usrname + " " + taskname + " " + str(start) + " " + str(num) , "getdirwithouttag", usrname,  str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskdataurl = curr_path + rootpath + usrname + "/" + taskname
    if os.path.islink(taskdataurl):
        namelist = listfilewithouttaglink(taskdataurl+'/data/', taskname)
    else:
        namelist = listfilewithouttag(taskdataurl+'/data/')
    string = '['
    end = len(namelist)
    if end>=1:
        if start > end:
            start = end
        if start+num > end:
            num = end-start+1
        for i in range(start-1, start-1+num-1):
            name = namelist[i]
            ipport1 = ipport
            if name.split('.')[-1] in VIDEO_EXTENSIONS:  
                ipport1 = ipport.replace('16831','16830')
            string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/"  + name + '", "labeled": 0},'
        name = namelist[start-1+num-1]
        ipport1 = ipport
        if name.split('.')[-1] in VIDEO_EXTENSIONS:  
            ipport1 = ipport.replace('16831','16830')
        string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/" + name + '", "labeled": 0}'
    string += ']'
    return string

@app.route('/api/getdirchecked', methods = ['GET'])
def api_get_dirchecked():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('start', type=int, location='args', required=True)
    get_parser.add_argument('num', type=int, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    start = args.get('start')  #start from 1
    num = args.get('num')
    operationlog(""+ usrname + " " + taskname + " " + str(start) + " " + str(num) , "getdirchecked", usrname,  str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskdataurl = curr_path + rootpath + usrname + "/" + taskname
    if os.path.islink(taskdataurl):
        namelist = listfilecheckedlink(taskdataurl+'/data/', taskname)
    else:
        namelist = listfilechecked(taskdataurl+'/data/')
    string = '['
    end = len(namelist)
    if end>=1:
        if start > end:
            start = end
        if start+num > end:
            num = end-start+1
        for i in range(start-1, start-1+num-1):
            name = namelist[i]
            ipport1 = ipport
            if name.split('.')[-1] in VIDEO_EXTENSIONS:  
                ipport1 = ipport.replace('16831','16830')
            string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/"  + name + '", "labeled": 1},'
        name = namelist[start-1+num-1]
        ipport1 = ipport
        if name.split('.')[-1] in VIDEO_EXTENSIONS:  
            ipport1 = ipport.replace('16831','16830')
        string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/" + name + '", "labeled": 1}'
    string += ']'
    return string

@app.route('/api/getdirunchecked', methods = ['GET'])
def api_get_dirunchecked():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('start', type=int, location='args', required=True)
    get_parser.add_argument('num', type=int, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    start = args.get('start')  #start from 1
    num = args.get('num')
    operationlog(""+ usrname + " " + taskname + " " + str(start) + " " + str(num) , "getdirunchecked", usrname,  str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskdataurl = curr_path + rootpath + usrname + "/" + taskname
    print taskdataurl
    if os.path.islink(taskdataurl):
        namelist = listfilenotcheckedlink(taskdataurl+'/data/', taskname)
    else:
        namelist = listfilenotchecked(taskdataurl+'/data/')
    # print namelist
    string = '['
    end = len(namelist)
    if end>=1:
        if start > end:
            start = end
        if start+num > end:
            num = end-start+1
        for i in range(start-1, start-1+num-1):
            name = namelist[i]
            ipport1 = ipport
            if name.split('.')[-1] in VIDEO_EXTENSIONS:  
                ipport1 = ipport.replace('16831','16830')
            string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/"  + name + '", "labeled": 1},'
        name = namelist[start-1+num-1]
        ipport1 = ipport
        if name.split('.')[-1] in VIDEO_EXTENSIONS:  
            ipport1 = ipport.replace('16831','16830')
        string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/" + name + '", "labeled": 1}'
    string += ']'
    return string

@app.route('/api/getdirpassed', methods = ['GET'])
def api_get_dirpassed():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('start', type=int, location='args', required=True)
    get_parser.add_argument('num', type=int, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    start = args.get('start')  #start from 1
    num = args.get('num')
    operationlog(""+ usrname + " " + taskname + " " + str(start) + " " + str(num) , "getdirpassed", usrname,  str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskdataurl = curr_path + rootpath + usrname + "/" + taskname
    if os.path.islink(taskdataurl):
        namelist = listfilepassedlink(taskdataurl+'/data/', taskname)
    else:
        namelist = listfilepassed(taskdataurl+'/data/')
    string = '['
    end = len(namelist)
    if end>=1:
        if start > end:
            start = end
        if start+num > end:
            num = end-start+1
        for i in range(start-1, start-1+num-1):
            name = namelist[i]
            ipport1 = ipport
            if name.split('.')[-1] in VIDEO_EXTENSIONS:  
                ipport1 = ipport.replace('16831','16830')
            string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/"  + name + '", "labeled": 1},'
        name = namelist[start-1+num-1]
        ipport1 = ipport
        if name.split('.')[-1] in VIDEO_EXTENSIONS:  
            ipport1 = ipport.replace('16831','16830')
        string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/" + name + '", "labeled": 1}'
    string += ']'
    return string

@app.route('/api/getdirnotpassed', methods = ['GET'])
def api_get_dirnotpassed():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('start', type=int, location='args', required=True)
    get_parser.add_argument('num', type=int, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    start = args.get('start')  #start from 1
    num = args.get('num')
    operationlog(""+ usrname + " " + taskname + " " + str(start) + " " + str(num) , "getdirnotpassed", usrname,  str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskdataurl = curr_path + rootpath + usrname + "/" + taskname
    if os.path.islink(taskdataurl):
        namelist = listfilenotpassedlink(taskdataurl+'/data/', taskname)
    else:
        namelist = listfilenotpassed(taskdataurl+'/data/')
    string = '['
    end = len(namelist)
    if end>=1:
        if start > end:
            start = end
        if start+num > end:
            num = end-start+1
        for i in range(start-1, start-1+num-1):
            name = namelist[i]
            ipport1 = ipport
            if name.split('.')[-1] in VIDEO_EXTENSIONS:  
                ipport1 = ipport.replace('16831','16830')
            string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/"  + name + '", "labeled": 1},'
        name = namelist[start-1+num-1]
        ipport1 = ipport
        if name.split('.')[-1] in VIDEO_EXTENSIONS:  
            ipport1 = ipport.replace('16831','16830')
        string += '{ "name": "' + name + '", "url": "' + ipport1 + rootpath + usrname + "/" + taskname + "/data/" + name + '", "labeled": 1}'
    string += ']'
    return string

@app.route('/api/uploadvideo2image', methods = ['POST'])
def api_upload_vifile():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    get_parser.add_argument('interval', type=int, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    interval = args.get('interval')
    operationlog(""+ usrname + " " + taskname + " " + filename, "uploadvideo2image", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url1 = curr_path + rootpath + usrname + "/" + taskname + "/data" 
    print url1
    # randomstring = random_char(5)
    extension = filename.split('.')[-1]
    setchanged(url1+'/', 'filelist', 1)
    if extension in VIDEOU_EXTENSIONS:
        oldurl = url1 + "/" + filename
        print oldurl
        if os.path.exists(url1):
            #print request.files
            file = request.files['file']
            #print os.path.join(url1, filename)
            file.save(oldurl)
            file.close()
            argument = " -y -i %s -r %f -q:v 2 -f image2 %s/%s_%%4d.jpg"%(oldurl, float(1.0/interval), url1, filename.split('.')[-2])
            print argument
            proc = subprocess.Popen("ffmpeg" + argument, shell=True)
            return url1
        else:
            return "[]" #"error: usrname or taskname not exists"
    else:
        return "error: unsurport video format, only surport mp4, avi, mpg, ts"

# @app.route('/api/uploadtestvideo2image', methods = ['POST'])
# def api_upload_testvifile():
#     get_parser = reqparse.RequestParser()
#     get_parser.add_argument('usrname', type=str, location='args', required=True)
#     get_parser.add_argument('taskname', type=str, location='args', required=True)
#     get_parser.add_argument('filename', type=str, location='args', required=True)
#     get_parser.add_argument('interval', type=int, location='args', required=True)
#     args = get_parser.parse_args()
#     usrname = args.get('usrname')
#     taskname = args.get('taskname')
#     filename = args.get('filename')
#     interval = args.get('interval')
#     operationlog(""+ usrname + " " + taskname + " " + filename, "uploadtestvideo2image", usrname, str(request.remote_addr))
#     curr_path = os.path.abspath(os.path.dirname(__file__))
#     url1 = curr_path + rootpath + usrname + "/" + taskname + "/test" 
#     print url1
#     # randomstring = random_char(5)
#     extension = filename.split('.')[-1]
#     if extension in VIDEOU_EXTENSIONS:
#         oldurl = url1 + "/" + filename
#         print oldurl
#         if os.path.exists(url1):
#             #print request.files
#             file = request.files['file']
#             #print os.path.join(url1, filename)
#             file.save(oldurl)
#             file.close()
#             argument = " -y -i %s -r %f -q:v 2 -f image2 %s/%s_%%4d.jpg"%(oldurl, float(1.0/interval), url1, filename.split('.')[-2])
#             print argument
#             proc = subprocess.Popen("ffmpeg" + argument, shell=True)
#             return url1
#         else:
#             return "[]" #"error: usrname or taskname not exists"
#     else:
#         return "error: unsurport video format, only surport mp4, avi, mpg, ts"

@app.route('/api/uploadvideofile', methods = ['POST'])
def api_upload_vfile():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    operationlog(""+ usrname + " " + taskname + " " + filename, "uploadvideofile", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url1 = curr_path + rootpath + usrname + "/" + taskname + "/data" 
    setchanged(url1+'/', 'filelist', 1)
    # randomstring = random_char(5)
    extension = filename.split('.')[-1]
    ipport1 = ipport.replace('16831','16830')
    if extension in VIDEOU_EXTENSIONS:
        newfilename = filename.split('.')[-2]+'.mp4'
        url = url1 + "/" + newfilename
        oldurl = url1 + "/" + filename
        if os.path.exists(url1):
            #print request.files
            file = request.files['file']
            #print os.path.join(url1, filename)
            file.save(oldurl)
            file.close()
            if extension not in VIDEO_EXTENSIONS:
                # transcode by ffmpeg
                argument = " -y -i %s -c:v libx264 -strict -2 %s"%(oldurl, url)
                print argument
                proc = subprocess.Popen("ffmpeg" + argument, shell=True)
            return ipport1 + rootpath + usrname + "/" + taskname + "/data/"  + newfilename 
        else:
            return "[]" #"error: usrname or taskname not exists"
    else:
        return "error: unsurport video format, only surport mp4, avi, mpg, ts"

@app.route('/api/uploadtestvideofile', methods = ['POST'])
def api_upload_testvfile():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    operationlog(""+ usrname + " " + taskname + " " + filename, "uploadtestvideofile", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url1 = curr_path + rootpath + usrname + "/" + taskname + "/test" 
    # randomstring = random_char(5)
    extension = filename.split('.')[-1]
    ipport1 = ipport.replace('16831','16830')
    if extension in VIDEOU_EXTENSIONS:
        newfilename = filename.split('.')[-2]+'.mp4'
        url = url1 + "/" + newfilename
        oldurl = url1 + "/" + filename
        if os.path.exists(url1):
            #print request.files
            file = request.files['file']
            #print os.path.join(url1, filename)
            file.save(oldurl)
            file.close()
            if extension not in VIDEO_EXTENSIONS:
                # transcode by ffmpeg
                argument = " -y -i %s -c:v libx264 -strict -2 %s"%(oldurl, url)
                print argument
                proc = subprocess.Popen("ffmpeg" + argument, shell=True)
            return ipport1 + rootpath + usrname + "/" + taskname + "/test/"  + newfilename 
        else:
            return "[]" #"error: usrname or taskname not exists"
    else:
        return "error: unsurport video format, only surport mp4, avi, mpg, ts"

@app.route('/api/uploadfile', methods = ['POST'])
def api_upload_file():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    operationlog(""+ usrname + " " + taskname + " " + filename, "uploadfile", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url1 = curr_path + rootpath + usrname + "/" + taskname + "/data" 
    setchanged(url1+'/', 'filelist', 1)
    # randomstring = random_char(5)
    # (shotname,extension) = os.path.splitext(filename);
    # newfilename = shotname+'_'+randomstring+extension
    newfilename = filename
    url = url1 + "/" + newfilename
    if os.path.exists(url1):
        #print request.files
        file = request.files['file']
        #print os.path.join(url1, filename)
        file.save(url)
        file.close()
        return url
    else:
        return "[]" #"error: usrname or taskname not exists"

@app.route('/api/uploadtestfile', methods = ['POST'])
def api_upload_testfile():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    operationlog(""+ usrname + " " + taskname + " " + filename, "uploadtestfile", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url1 = curr_path + rootpath + usrname + "/" + taskname + "/test" 
    # randomstring = random_char(5)
    # (shotname,extension) = os.path.splitext(filename);
    # newfilename = shotname+'_'+randomstring+extension
    newfilename = filename
    url = url1 + "/" + newfilename
    if os.path.exists(url1):
        #print request.files
        file = request.files['file']
        #print os.path.join(url1, filename)
        file.save(url)
        file.close()
        return url
    else:
        return "[]" #"error: usrname or taskname not exists"

@app.route('/api/uploadurlfile', methods = ['POST'])
def api_upload_urlfile():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    operationlog(""+ usrname + " " + taskname, "uploadurlfile", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    filepath = curr_path + rootpath + usrname + "/" + taskname + "/data/" 
    setchanged(filepath, 'filelist', 1)
    if os.path.exists(filepath):
        data = json.loads(request.data)
        # print data
        fileurl = data['url']
        # print fileurl
        extension = fileurl.split('.')[-1]
        if extension in LFILE_EXTENSIONS:
            randomstring = random_char(5)
            filename = filepath+randomstring+'.'+extension
            # print filename
            # headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
            headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'} 
            req = urllib2.Request(url = fileurl, headers = headers)
            # print fileurl
            # print req
            try:
                binary_data = urllib2.urlopen(req).read()
                #print binary_data
                temp_file = open(filename, 'wb')
                temp_file.write(binary_data)
                temp_file.close()
                return 'OK'
            except urllib2.HTTPError, e:
                print e.code
                return 'error, http forbidden'
            except urllib2.URLError, e:
                print e.reason
                return 'error, http forbidden'
            return 'OK'
        else:
            return 'Error, unsurport extension'
    else:
        return "error: usrname or taskname not exists"

# @app.route('/api/uploadurltestfile', methods = ['POST'])
# def api_upload_urltestfile():
#     get_parser = reqparse.RequestParser()
#     get_parser.add_argument('usrname', type=str, location='args', required=True)
#     get_parser.add_argument('taskname', type=str, location='args', required=True)
#     args = get_parser.parse_args()
#     usrname = args.get('usrname')
#     taskname = args.get('taskname')
#     operationlog(""+ usrname + " " + taskname, "uploadurltestfile", usrname, str(request.remote_addr))
#     curr_path = os.path.abspath(os.path.dirname(__file__))
#     filepath = curr_path + rootpath + usrname + "/" + taskname + "/test/" 
#     if os.path.exists(filepath):
#         data = json.loads(request.data)
#         # print data
#         fileurl = data['url']
#         # print fileurl
#         extension = fileurl.split('.')[-1]
#         if extension in LFILE_EXTENSIONS:
#             randomstring = random_char(5)
#             filename = filepath+randomstring+'.'+extension
#             # print filename
#             # headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
#             headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'} 
#             req = urllib2.Request(url = fileurl, headers = headers)
#             # print fileurl
#             # print req
#             try:
#                 binary_data = urllib2.urlopen(req).read()
#                 #print binary_data
#                 temp_file = open(filename, 'wb')
#                 temp_file.write(binary_data)
#                 temp_file.close()
#                 return 'OK'
#             except urllib2.HTTPError, e:
#                 print e.code
#                 return 'error, http forbidden'
#             except urllib2.URLError, e:
#                 print e.reason
#                 return 'error, http forbidden'
#             return 'OK'
#         else:
#             return 'Error, unsurport extension'
#     else:
#         return "error: usrname or taskname not exists"

@app.route('/api/scrapyimg', methods = ['POST'])
def api_upload_scrapyimg():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    filepath = curr_path + rootpath + usrname + "/" + taskname + "/data/" 
    setchanged(filepath, 'filelist', 1)
    if os.path.exists(filepath):
        data = json.loads(request.data)
        engine = data['engine']
        keyword = data['keyword']
        start = int(data['start'])
        num = int(data['num'])
        # print data
        # print engine, keyword, start, num
        if type(keyword)==unicode:
            keyword = keyword.encode('utf-8')
        if type(engine)==unicode:
            engine = engine.encode('utf-8')
        operationlog(""+ usrname + " " + taskname+ " " + engine+ " " + str(keyword)+ " " + str(start)+ " " + str(num), "scrapyimg", usrname, str(request.remote_addr))
        # print 'operation'
        # new threads
        # scrapyimg(filepath, engine, keyword, start, num)
        argument = " tools/scrapy.py %s %s %s %d %d"%(filepath, engine,  keyword, start, num)
        print argument
        proc = subprocess.Popen("python" + argument, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=True)
        # print 'subprocess'

        return 'OK'
    else:
        return "error: usrname or taskname not exists"

# @app.route('/api/scrapytestimg', methods = ['POST'])
# def api_upload_scrapytestimg():
#     get_parser = reqparse.RequestParser()
#     get_parser.add_argument('usrname', type=str, location='args', required=True)
#     get_parser.add_argument('taskname', type=str, location='args', required=True)
#     args = get_parser.parse_args()
#     usrname = args.get('usrname')
#     taskname = args.get('taskname')
#     curr_path = os.path.abspath(os.path.dirname(__file__))
#     filepath = curr_path + rootpath + usrname + "/" + taskname + "/test/" 
#     if os.path.exists(filepath):
#         data = json.loads(request.data)
#         engine = data['engine']
#         keyword = data['keyword']
#         start = int(data['start'])
#         num = int(data['num'])
#         # print data
#         # print engine, keyword, start, num
#         if type(keyword)==unicode:
#             keyword = keyword.encode('utf-8')
#         if type(engine)==unicode:
#             engine = engine.encode('utf-8')
#         operationlog(""+ usrname + " " + taskname+ " " + engine+ " " + str(keyword)+ " " + str(start)+ " " + str(num), "scrapyimg", usrname, str(request.remote_addr))
#         # print 'operation'
#         # new threads
#         # scrapyimg(filepath, engine, keyword, start, num)
#         argument = " tools/scrapy.py %s %s %s %d %d"%(filepath, engine,  keyword, start, num)
#         # print argument
#         proc = subprocess.Popen("python" + argument, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=True)
#         # print 'subprocess'

#         return 'OK'
#     else:
#         return "error: usrname or taskname not exists"

# @app.route('/api/scrapyimgget', methods = ['GET'])
# def api_upload_scrapyimgget():
#     get_parser = reqparse.RequestParser()
#     get_parser.add_argument('usrname', type=str, location='args', required=True)
#     get_parser.add_argument('taskname', type=str, location='args', required=True)
#     get_parser.add_argument('engine', type=str, location='args', required=True)
#     get_parser.add_argument('keyword', type=str, location='args', required=True)
#     args = get_parser.parse_args()
#     usrname = args.get('usrname')
#     taskname = args.get('taskname')
#     engine = args.get('engine')
#     keyword = args.get('keyword')
#     start = 1
#     num = 10
#     curr_path = os.path.abspath(os.path.dirname(__file__))
#     filepath = curr_path + rootpath + usrname + "/" + taskname + "/data/" 
#     print filepath
#     if os.path.exists(filepath):
#         operationlog(""+ usrname + " " + taskname+ " " + engine+ " " + str(keyword)+ " " + str(start)+ " " + str(num), "scrapyimg", usrname, str(request.remote_addr))
#         # new threads
#         # scrapyimg(filepath, engine, keyword, start, num)
#         argument = " tools/scrapy.py %s %s %s %d %d"%(filepath, engine,  keyword, start, num)
#         print argument
#         proc = subprocess.Popen("python" + argument, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=True)
#         return 'OK'
#     else:
#         return "error: usrname or taskname not exists"

@app.route('/api/getscrapystat', methods = ['GET'])
def api_get_scrapystat():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    file_object = open(scrapylogfile)
    mLines = file_object.readlines()
    print mLines
    targetLine = mLines[-1]
    file_object.close()
    print targetLine
    return targetLine

@app.route('/api/delsamefile', methods = ['GET'])
def api_del_sameimg():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    operationlog(""+ usrname + " " + taskname, "delsameimg", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    filepath = curr_path + rootpath + usrname + "/" + taskname + "/data/" 
    setchanged(filepath, 'filelist', 1)
    if os.path.exists(filepath):
        # new threads
        argument = "tools/skipimg.py %s"%(filepath)
        print argument
        proc = subprocess.Popen("python " + argument, stdout=subprocess.PIPE,stderr=subprocess.STDOUT, shell=True)
        return 'OK'
    else:
        return "error: usrname or taskname not exists"

# @app.route('/api/uploadurlfileget', methods = ['GET'])
# def api_upload_urlfileget():
#     get_parser = reqparse.RequestParser()
#     get_parser.add_argument('usrname', type=str, location='args', required=True)
#     get_parser.add_argument('taskname', type=str, location='args', required=True)
#     get_parser.add_argument('url', type=str, location='args', required=True)
#     args = get_parser.parse_args()
#     usrname = args.get('usrname')
#     taskname = args.get('taskname')
#     fileurl = args.get('url')
#     print fileurl
#     operationlog(""+ usrname + " " + taskname, "uploadurlfile", usrname, str(request.remote_addr))
#     curr_path = os.path.abspath(os.path.dirname(__file__))
#     filepath = curr_path + rootpath + usrname + "/" + taskname + "/data/" 
#     print filepath
#     if os.path.exists(filepath):
#         extension = fileurl.split('.')[-1]
#         if extension in LFILE_EXTENSIONS:
#             randomstring = random_char(5)
#             filename = filepath+randomstring+'.'+extension
#             headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
#             req = urllib2.Request(url = fileurl, headers = headers)
#             binary_data = urllib2.urlopen(req).read()
#             temp_file = open(filename, 'wb')
#             temp_file.write(binary_data)
#             temp_file.close()
#             return 'OK'
#         else:
#             return 'Error, unsurport extension'
#     else:
#         return "[]" #"error: usrname or taskname not exists"

@app.route('/api/delfile', methods = ['GET'])
def api_del_file():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    operationlog(""+ usrname + " " + taskname + " " + filename, "delfile", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url1 = curr_path + rootpath + usrname + "/" + taskname + "/data" 
    setchanged(url1+'/', 'filelist', 1)
    url = url1 + "/" + filename
    if os.path.exists(url):
        os.remove(url)
        urltxt = (url+'.txt').replace('/data/','/label/')
        if os.path.exists(urltxt):
            os.remove(urltxt)
        return url1
    else:
        return  "[]" #"error: file not exists"

@app.route('/api/filecount', methods = ['GET'])
def api_file_count():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskurl = curr_path + rootpath + usrname + "/" + taskname
    url = taskurl + "/data/" 
    #print url
    if not os.path.islink(taskurl):
        count = countimagefilenum(url)
        return str(count)
    else:
        filelist = listfile(url)
        spl = taskurl.split("_")
        gstart = int(spl[-2])
        gnum = int(spl[-1])
        if gstart+gnum-1 > len(filelist):
            return '-1'
        else:
            return str(gnum)
    return '-1'

@app.route('/api/labeledfilecount', methods = ['GET'])
def api_labelfile_count():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskurl = curr_path + rootpath + usrname + "/" + taskname
    url = taskurl + "/data/" 
    if not os.path.islink(taskurl):
        count = countlabelfilenum(url)
        return str(count)
    else:
        filelist = listfile(url)
        #print url
        spl = taskurl.split("_")
        gstart = int(spl[-2])
        gnum = int(spl[-1])
        #print gstart, gnum
        if gstart+gnum-1 > len(filelist):
            return '-1'
        else:
            return str(countlabelfilenumlink(url, filelist, gstart, gnum))
        return '-1'


@app.route('/api/checkedfilecount', methods = ['GET'])
def api_checkedfile_count():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskurl = curr_path + rootpath + usrname + "/" + taskname
    url = taskurl + "/data/" 
    if not os.path.islink(taskurl):
        count = countchecked(url)
        return str(count)
    else:
        return str(countcheckedlink(url, taskname))

@app.route('/api/passedfilecount', methods = ['GET'])
def api_passedfile_count():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskurl = curr_path + rootpath + usrname + "/" + taskname
    url = taskurl + "/data/" 
    if not os.path.islink(taskurl):
        count = countpassed(url)
        return str(count)
    else:
        return str(countpassedlink(url, taskname))

# tag API

@app.route('/api/loadtag', methods = ['GET'])
def api_load_tag():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url = curr_path + rootpath + usrname + "/" + taskname + "/" + taglistname
    if os.path.exists(url):
        f = open(url)
        txt = f.read()
        #print txt
        return txt
    else:
        return '{"listname":["tagname"],"taglist": {"tagname":["tag1","tag2","tag3"]}}'


@app.route('/api/savetag', methods = ['POST'])
def api_save_tag():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    operationlog(""+ usrname + " " + taskname, "savetag", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url1 = curr_path + rootpath + usrname + "/" + taskname 

    if os.path.exists(url1):
        url = url1 + taglistname
        #print request.data
        f=open(url,'w')
        f.writelines(request.data)
        f.close()
        setchanged(url1+'/data/', 'tagstatics', 1)
        return request.data + "\n"
    else:
        return "error: usrname or taskname not exists"

@app.route('/api/changetag', methods = ['POST'])
def api_change_tag():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    data = json.loads(request.data)
    oldtag = data['oldtag']
    newtag = data['newtag']
    #print oldtag, newtag
    operationlog(""+ usrname + " " + taskname + " " + oldtag + " " + newtag, "changetag", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url = curr_path + rootpath + usrname + "/" + taskname
    url1 = url + taglistname
    # url2 = curr_path + rootpath + usrname + "/" + taskname + "/data/*.txt"
    url3 = url + "/label/"
    setchanged(url+'/data/', 'tagstatics', 1)
    if os.path.exists(url1):
        # cmd = "sed -i 's/\"%s\"/\"%s\"/g' %s"%(oldtag, newtag, url1)
        # print cmd
        # os.system(cmd)
        argument = " -i 's/\"%s\"/\"%s\"/g' %s"%(oldtag, newtag, url1)
        process = subprocess.Popen('sed'+argument, shell=True)
        #print "tag done"
        #cmd = 'sed -i "s/\"%s\"/\"%s\"/g" %s'%(oldtag, newtag, url2)

        #cmd = "find %s -name *.txt |  xargs -i sed -i 's/\"%s\"/\"%s\"/g' {}"%(url3, oldtag, newtag)
        #os.system(cmd)
        #print cmd
        argument = " %s -name *.txt |  xargs -i sed -i 's/\"%s\"/\"%s\"/g' {}"%(url3, oldtag, newtag)
        process = subprocess.Popen('find'+argument, shell=True)
        #print "ok"
        return 'OK'
    else:
        return "error: usrname or taskname not exists"

# label API

@app.route('/api/loadlabel', methods = ['GET'])
def api_load_label():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    labelname = filename + ".txt"
    url = curr_path + rootpath + usrname + "/" + taskname + "/label/"  + labelname
    if os.path.exists(url):
        f = open(url)
        txt = f.read()
        #print txt
        return txt
    else:
        return '{ "length": 0}'

@app.route('/api/loadtestlabel', methods = ['GET'])
def api_load_testlabel():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    labelname = filename + ".txt"
    url = curr_path + rootpath + usrname + "/" + taskname + "/test/"  + labelname
    if os.path.exists(url):
        f = open(url)
        txt = f.read()
        #print txt
        return txt
    else:
        return '{ "length": 0}'

@app.route('/api/saveannolabel', methods = ['POST'])
def api_save_annolabel():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    #operationlog(""+ usrname + " " + taskname + " " + filename, "savelabel", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url = curr_path + rootpath + usrname + "/" + taskname
    url1 = url + "/label" 
    #print url1
    if os.path.exists(url1):
        labelname = "/" + filename + ".anno"
        url = url1 + labelname
        #print request.data
        f=open(url,'w')
        f.writelines(request.data)
        f.close()
        return request.data + "\n"
    else:
        return "error: usrname or taskname not exists"

@app.route('/api/loadannolabel', methods = ['GET'])
def api_load_annolabel():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    labelname = filename + ".anno"
    url = curr_path + rootpath + usrname + "/" + taskname + "/test/"  + labelname
    if os.path.exists(url):
        f = open(url)
        txt = f.read()
        #print txt
        return txt
    else:
        return '{ "length": 0}'

@app.route('/api/loadseglabel', methods = ['GET'])
def api_load_seglabel():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    labelname = filename + ".txt"
    url = curr_path + rootpath + usrname + "/" + taskname + "/label/"  + labelname
    if os.path.exists(url):
        f = open(url)
        txt = f.read()
        #print txt
        return txt
    else:
        return ''

@app.route('/api/dellabel', methods = ['GET'])
def api_del_label():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    operationlog(""+ usrname + " " + taskname + " " + filename, "dellabel", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    labelname = filename + ".txt"
    url = curr_path + rootpath + usrname + "/" + taskname 
    url1 = curr_path + rootpath + usrname + "/" + taskname + "/label/"  + labelname
    setchanged(url+'/data/', 'taglist', 1)
    setchanged(url+'/data/', 'notaglist', 1)
    setchanged(url+'/data/', 'tagstatics', 1)
    setchanged(url+'/data/', 'checklist', 1)
    setchanged(url+'/data/', 'notchecklist', 1)
    setchanged(url+'/data/', 'passlist', 1)
    setchanged(url+'/data/', 'notpasslist', 1)
    setchanged(url+'/data/', 'statisticlabeler', 1)
    setchanged(url+'/data/', 'statisticreviewer', 1)
    if os.path.exists(url1):
        os.remove(url1)
        return '{ "length": 0}'
    else:
        return '{ "length": 0}'

@app.route('/api/delseglabel', methods = ['GET'])
def api_del_seglabel():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    operationlog(""+ usrname + " " + taskname + " " + filename, "dellsegabel", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    labelname = filename + ".txt"
    url = curr_path + rootpath + usrname + "/" + taskname
    url1 = curr_path + rootpath + usrname + "/" + taskname + "/label/"  + labelname
    setchanged(url+'/data/', 'taglist', 1)
    setchanged(url+'/data/', 'notaglist', 1)
    setchanged(url+'/data/', 'tagstatics', 1)
    setchanged(url+'/data/', 'checklist', 1)
    setchanged(url+'/data/', 'notchecklist', 1)
    setchanged(url+'/data/', 'passlist', 1)
    setchanged(url+'/data/', 'notpasslist', 1)
    setchanged(url+'/data/', 'statisticlabeler', 1)
    setchanged(url+'/data/', 'statisticreviewer', 1)
    if os.path.exists(url1):
        os.remove(url1)
    return '{ "length": 0}'

@app.route('/api/savelabel', methods = ['POST'])
def api_save_label():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    operationlog(""+ usrname + " " + taskname + " " + filename, "savelabel", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url = curr_path + rootpath + usrname + "/" + taskname
    url1 = url + "/label" 
    #print url1
    if os.path.exists(url1):
        setchanged(url+'/data/', 'taglist', 1)
        setchanged(url+'/data/', 'notaglist', 1)
        setchanged(url+'/data/', 'tagstatics', 1)
        setchanged(url+'/data/', 'checklist', 1)
        setchanged(url+'/data/', 'notchecklist', 1)
        setchanged(url+'/data/', 'passlist', 1)
        setchanged(url+'/data/', 'notpasslist', 1)
        setchanged(url+'/data/', 'statisticlabeler', 1)
        setchanged(url+'/data/', 'statisticreviewer', 1)
        labelname = "/" + filename + ".txt"
        url = url1 + labelname
        #print request.data
        f=open(url,'w')
        f.writelines(request.data)
        f.close()
        return request.data + "\n"
    else:
        return "error: usrname or taskname not exists"

@app.route('/api/saveseglabel', methods = ['POST'])
def api_save_seglabel():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    operationlog(""+ usrname + " " + taskname + " " + filename, "saveseglabel", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url = curr_path + rootpath + usrname + "/" + taskname
    url1 = url + "/label" 
    #print url1
    if os.path.exists(url1):
        setchanged(url+'/data/', 'taglist', 1)
        setchanged(url+'/data/', 'notaglist', 1)
        setchanged(url+'/data/', 'tagstatics', 1)
        setchanged(url+'/data/', 'checklist', 1)
        setchanged(url+'/data/', 'notchecklist', 1)
        setchanged(url+'/data/', 'passlist', 1)
        setchanged(url+'/data/', 'notpasslist', 1)
        setchanged(url+'/data/', 'statisticlabeler', 1)
        setchanged(url+'/data/', 'statisticreviewer', 1)
        labelname = "/" + filename + ".txt"
        url = url1 + labelname
        # print request
        # print request.files
        #ifile = request.files['file']
        lines = request.data.split('\n')
        f=open(url,'w')
        f.write(lines[3])
        f.close()
        return "ok"
    else:
        return "error: usrname or taskname not exists"

@app.route('/api/labelstatistics', methods = ['GET'])
def api_label_statistics():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    operationlog(""+ usrname + " " + taskname, "labelstatistics", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskurl = curr_path + rootpath + usrname + "/" + taskname
    url1 = taskurl + "/data/" 
    tagfile = taskurl + taglistname
    if not os.path.islink(taskurl):
        #print url1
        statistics = getstatistics(url1, tagfile)
        # print statistics
        return statistics
    else:
        filelist = listfile(url1)
        spl = taskurl.split("_")
        gstart = int(spl[-2])
        gnum = int(spl[-1])
        if gstart+gnum-1 > len(filelist):
            return '{}'
        else:
            return getstatisticslink(url1, filelist, gstart, gnum, tagfile)
        return '{}'

@app.route('/api/labelstatisticsfig', methods = ['GET'])
def api_label_statisticsfig():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    operationlog(""+ usrname + " " + taskname, "labelstatistics", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    figname = 'tag_'+random_char(5)+'.png'
    taskurl = curr_path + rootpath + usrname + "/" + taskname
    url1 = taskurl + "/data/" 
    tagfile = taskurl + taglistname
    figfile = taskurl + "/" + figname
    figurl =  ipport + rootpath + usrname + "/" + taskname + "/" + figname
    rmfigpath = taskurl + "/tag_*.png"
    pnglist = glob(rmfigpath)
    # print pnglist
    changed = ischanged(url1, 'tagstatics')
    if len(pnglist)>0:
        shutil.copy(pnglist[0], figfile)
        os.remove(pnglist[0])
        if not changed:
            return figurl

    if not os.path.islink(taskurl):
        #print url1
        getstatisticsfig(url1, tagfile, figfile)
        setchanged(url1, 'tagstatics', 0)
        # print statistics
        return figurl
    else:
        filelist = listfile(url1)
        spl = taskurl.split("_")
        gstart = int(spl[-2])
        gnum = int(spl[-1])
        if gstart+gnum-1 > len(filelist):
            return ''
        else:
            getstatisticsfiglink(url1, filelist, gstart, gnum, tagfile, figfile)
            setchanged(url1, 'tagstatics', 1)
            return figurl
        return ''

@app.route('/api/getstatisticslabeler', methods = ['GET'])
def api_getstatisticslabeler():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    operationlog(""+ usrname + " " + taskname, "statlabel", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url = curr_path + rootpath + usrname + "/" + taskname + '/data/'
    res = statisticlabeler(url)
    return str(res)

@app.route('/api/getstatisticsreviewer', methods = ['GET'])
def api_getstatisticsreviewer():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    operationlog(""+ usrname + " " + taskname, "statreview", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url = curr_path + rootpath + usrname + "/" + taskname + '/data/'
    res = statisticreviewer(url)
    return str(res)

@app.route('/api/loadreason', methods = ['GET'])
def api_load_reason():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url = curr_path + rootpath + usrname + "/" + taskname + "/" + notpassreasonfilename
    if os.path.exists(url):
        f = open(url)
        txt = f.read()
        #print txt
        return txt
    else:
        return '{"reasonlist":["please add same reason"]}'


@app.route('/api/savereason', methods = ['POST'])
def api_save_reason():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    operationlog(""+ usrname + " " + taskname, "savereason", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url1 = curr_path + rootpath + usrname + "/" + taskname 

    if os.path.exists(url1):
        url = url1 + '/' + notpassreasonfilename
        #print request.data
        f=open(url,'w')
        f.writelines(request.data)
        f.close()
        return request.data + "\n"
    else:
        return "error: usrname or taskname not exists"


@app.route('/api/getoperations', methods = ['GET'])
def api_get_operations():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('start', type=int, location='args', required=True)
    get_parser.add_argument('num', type=int, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    start = args.get('start')
    num = args.get('num')
    db = Database()
    res = db.queryOperations(usrname, start, num)
    oplist = []
    if len(res)>0:
        for op in res:
            oplist.append(op)
    #print oplist
    return str(oplist)

@app.route('/api/getoperationscount', methods = ['GET'])
def api_get_operationscount():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    db = Database()
    res = db.queryOperationsCount(usrname)
    # print res
    #print oplist
    return str(res[0][0])

# task API
@app.route('/api/gettasklist', methods = ['GET'])
def api_get_tasklist():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    #print 'gettasklist'
    db = Database()
    tasklist = db.qureyTaskname(usrname)
    #print 'tasklist', tasklist
    return str(tasklist)
    # if len(tasklist)==1:
    #     return '('+str(tasklist[0])+')'
    # else:
    #     return str(tasklist)

@app.route('/api/addtask', methods = ['GET'])
def api_add_task(): 
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('type', type=int, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    tasktype = args.get('type')
    operationlog(""+ usrname + " " + taskname+ " " + str(tasktype), "addtask", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url1 = curr_path + rootpath + usrname + "/" + taskname
    url2 = url1 + '/data'
    url3 = url1 + '/label'
    url4 = url1 + '/test'
    #print url1
    #print url2
    db = Database()
    if not os.path.exists(url1):
        os.mkdir(url1) 
        os.mkdir(url2)   
        os.mkdir(url3) 
        os.mkdir(url4) 
        db.writeTask(taskname, tasktype, 0.0, usrname)
    tasklist = db.qureyTaskname(usrname)
    return str(tasklist)

@app.route('/api/gettaskdesc', methods = ['GET'])
def api_get_taskdesc(): 
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    operationlog(""+ usrname + " " + taskname, "gettaskdesc", usrname, str(request.remote_addr))
    db = Database()
    taskdesc = db.qureyTaskdesc(usrname, taskname)
    return str(taskdesc)

@app.route('/api/settaskdesc', methods = ['POST'])
def api_set_taskdesc():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    desc = request.data
    #operationlog("", "gettrainingtaskinfo", str(request.remote_addr))
    db = Database()
    operationlog(""+ usrname + " " + taskname, "gettaskdesc", usrname, str(request.remote_addr))
    db.setTaskdesc(usrname, taskname, desc)
    return "OK"


@app.route('/api/deltask', methods = ['GET'])
def api_del_task():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    operationlog(""+ usrname + " " + taskname, "deltask", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url1 = curr_path + rootpath + usrname + "/" + taskname
    #print url1
    db = Database()
    if os.path.exists(url1):
        if os.path.islink(url1):
            cmd = "rm "+ url1
            #print cmd
            os.system(cmd)
        else:
            shutil.rmtree(url1) 
        db.delTask(usrname, taskname)
    tasklist = db.qureyTaskname(usrname)
    return str(tasklist)

@app.route('/api/starttask', methods = ['GET'])
def api_start_task():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    operationlog(""+ usrname + " " + taskname, "starttask", usrname, str(request.remote_addr)) 

    db = Database()
    db.startTask(usrname, taskname)
    db.updateTask(usrname, taskname, 0.0, 0)
    curr_path = os.path.abspath(os.path.dirname(__file__))
    trainpath = curr_path + rootpath + usrname + "/" + taskname+ '/train/'
    # print curr_path
    # print trainpath
    # if os.path.exists(url1):
    #     shutil.rmtree(url1) 
    if not os.path.exists(trainpath):
        os.mkdir(trainpath)
    paramfile = curr_path + rootpath + usrname + "/" + taskname + trainparamsfile
    # print paramfile
    f = file(paramfile, "r")
    jsondata = json.load(f)
    structure = jsondata['structure']
    structureurl = trainpath+structure
    # print structureurl
    if not os.path.exists(structureurl):
        os.mkdir(structureurl)
    tasklist = db.qureyTaskname(usrname)
    return str(tasklist)

@app.route('/api/stoptask', methods = ['GET'])
def api_stop_task():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    operationlog(""+ usrname + " " + taskname, "stoptask", usrname, str(request.remote_addr))
    db = Database()
    # pid = db.getTaskpid(usrname, taskname)[0][0]
    # print pid
    # if pid!=0 and pid!= 'None':
    #     cmd = "kill -9 "+str(pid)
    #     os.system(cmd)
    res = db.getTaskStatus(usrname, taskname)
    if len(res)>0:
        status = res[0][0]
        if status == 1:
            db.clearTask(usrname, taskname) # not used
        else:
            db.stopTask(usrname, taskname)
    # db.clearWorker(taskname)
    tasklist = db.qureyTaskname(usrname)
    return str(tasklist)

@app.route('/api/taskinfostructure', methods = ['GET'])
def api_task_infostructure():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url = ipport + rootpath + usrname + "/" + taskname + '/train/'
    trainpath = curr_path + rootpath + usrname + "/" + taskname + '/train/'
    structurelist = getstructure(trainpath)
    return str(structurelist).replace('\'','\"')

@app.route('/api/taskinfo', methods = ['GET'])
def api_task_info():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('structure', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    structure = args.get('structure')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url = ipport + rootpath + usrname + "/" + taskname + '/train/'
    trainpath = curr_path + rootpath + usrname + "/" + taskname + '/train/'
    # paramfile = curr_path + rootpath + usrname + "/" + taskname + trainparamsfile
    # f = file(paramfile, "r")
    # jsondata = json.load(f)
    # structure = jsondata['structure']
    structureurl = trainpath+structure
    for fi in os.listdir(structureurl):
        if fi.split('.')[-1]=='jpg':  
            url = url + structure + '/' + fi
            return url
    return ''

@app.route('/api/tasklog', methods = ['GET'])
def api_task_log():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('structure', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    structure = args.get('structure')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    #url = ipport + rootpath + usrname + "/" + taskname + '/train/'
    #print url
    trainpath = curr_path + rootpath + usrname + "/" + taskname + '/train/'
    # paramfile = curr_path + rootpath + usrname + "/" + taskname + trainparamsfile
    # f = file(paramfile, "r")
    # jsondata = json.load(f)
    # structure = jsondata['structure']
    structurepath = trainpath+structure
    #print trainpath
    logfile = structurepath+trainlogfile
    # print logfile
    #for file in os.listdir(trainpath):
        #print file
    #    if file.split('.')[-1]=='jpg':  
    #           url = url + file
    # loglinenumbers = 100
    string = ''
    if os.path.exists(logfile):
        with open(logfile) as f:
            txt=f.readlines()
        length = len(txt)
        # keys=[k for k in range(0,len(txt))]
        # result={k:v for k,v in zip(keys,txt[::])}
        string = ''
        for i in range(length):
            string = string + txt[i]
            #print result[i]
    
    return string

@app.route('/api/gettrainingtaskinfo', methods = ['POST'])
def api_traintask_info():
    tasklist = []
    data = json.loads(request.data)
    usrname = data['name']
    passwd = data['passwd']
    #operationlog("", "gettrainingtaskinfo", str(request.remote_addr))
    db = Database()
    res, level, group  = db.verifyusr(usrname, passwd)
    if res and level >= SUPER:
        reslist = db.gettrainingtaskinfo()
        for task in reslist:
            tasklist.append(task)
    return str(tasklist)

@app.route('/api/transfertaskdata', methods = ['POST'])
def api_transfer_taskdata(): 
    # get_parser = reqparse.RequestParser()
    # get_parser.add_argument('fromusrname', type=str, location='args', required=True)
    # get_parser.add_argument('fromtaskname', type=str, location='args', required=True)
    # get_parser.add_argument('start', type=int, location='args', required=True)
    # get_parser.add_argument('num', type=int, location='args', required=True)
    # get_parser.add_argument('trasferusrname', type=str, location='args', required=True)
    # get_parser.add_argument('trasfertaskname', type=str, location='args', required=True)
    # get_parser.add_argument('isLable', type=int, location='args', required=True)
    # get_parser.add_argument('isCopy', type=int, location='args', required=True)
    # args = get_parser.parse_args()
    data = json.loads(request.data)
    usrname = data['name']
    passwd = data['passwd']
    fromusrname = data['fromusrname']
    fromtaskname = data['fromtaskname']
    start = data['start']
    num = data['num']
    newusrname = data['trasferusrname']
    newtaskname = data['trasfertaskname']
    isLabel = data['isLabel']
    isCopy = data['isCopy']
    #operationlog("", "gettrainingtaskinfo", str(request.remote_addr))
    db = Database()
    res, level, group  = db.verifyusr(usrname, passwd)
    if res and level >= MANAGE:
        operationlog("From:"+ fromusrname+"$"+fromtaskname+" start:"+str(start)+" num:"+str(num)+" TO:"+newusrname+"$"+newtaskname, "transfertaskdata", usrname, str(request.remote_addr))
        #print usrname+" "+fromusrname+" "+fromtaskname+" "+str(start)+" "+str(num)+" "+newusrname+" "+newtaskname
        curr_path = os.path.abspath(os.path.dirname(__file__))
        oldtaskurl = curr_path + rootpath + fromusrname + "/" + fromtaskname + "/data/"
        newtaskurl = curr_path + rootpath + newusrname + "/" + newtaskname + "/data/"
        namelist = listfile(oldtaskurl, 0) 
        gstart = int(start)
        oldtagpath = oldtaskurl + '..' + taglistname
        newtagpath = newtaskurl + '..' + taglistname
        #print oldtagpath
        #print newtagpath
        if os.path.islink(oldtaskurl):
            spl = oldtaskurl.split("_")
            gstart = int(spl[-2])+int(start)
        for i in range(int(num)):
            index = i+1
            filepath = oldtaskurl+namelist[index+gstart-2]
            filetxtpath = (oldtaskurl+namelist[index+gstart-2]+'.txt').replace('/data/','/label/')
            newfilepath = newtaskurl+fromtaskname+'_'+namelist[index+gstart-2]
            newfiletxtpath = (newfilepath+'.txt').replace('/data/','/label/')
            if os.path.exists(filepath):
                shutil.copy(filepath, newfilepath)
                if isLabel==1 and os.path.exists(filetxtpath):
                    shutil.copy(filetxtpath, newfiletxtpath)
                if isCopy==0:
                    os.remove(filepath)
                    if os.path.exists(filetxtpath):
                        os.remove(filetxtpath)
        #print 'copy tag'
        if os.path.exists(oldtagpath):
            shutil.copy(oldtagpath, newtagpath)
        #print filetxtpath
        setchanged(newtaskurl, 'filelist', 1)
        #print 'setchange '+newtaskurl

        return 'OK'
    else:
        return 'Fail'

# @app.route('/api/transfertaskdataget', methods = ['GET'])
# def api_transfer_taskdataget(): 
#     get_parser = reqparse.RequestParser()
#     get_parser.add_argument('fromusrname', type=str, location='args', required=True)
#     get_parser.add_argument('fromtaskname', type=str, location='args', required=True)
#     get_parser.add_argument('start', type=int, location='args', required=True)
#     get_parser.add_argument('num', type=int, location='args', required=True)
#     get_parser.add_argument('trasferusrname', type=str, location='args', required=True)
#     get_parser.add_argument('trasfertaskname', type=str, location='args', required=True)
#     get_parser.add_argument('isLabel', type=int, location='args', required=True)
#     get_parser.add_argument('isCopy', type=int, location='args', required=True)
#     args = get_parser.parse_args()
#     fromusrname = args.get('fromusrname')
#     taskname = args.get('fromtaskname')
#     start = args.get('start')
#     num = args.get('num')
#     newusrname = args.get('trasferusrname')
#     newtaskname = args.get('trasfertaskname')
#     isLabel = args.get('isLabel')
#     isCopy = args.get('isCopy')
#     usrname = 'fj'
#     #operationlog("", "gettrainingtaskinfo", str(request.remote_addr))
#     operationlog(""+ fromusrname+" "+taskname+" "+str(start)+" "+str(num)+" "+newusrname+" "+newtaskname, "transfertaskdata", usrname, str(request.remote_addr))
#     print fromusrname+" "+taskname+" "+str(start)+" "+str(num)+" "+newusrname+" "+newtaskname
#     # TODO
#     return 'OK'


# @app.route('/api/gettrainingtaskinfoget', methods = ['GET'])
# def api_task_infoget():
#     tasklist = []
#     operationlog("", "gettrainingtaskinfo", str(request.remote_addr))
#     db = Database()
#     reslist = db.gettrainingtaskinfo()
#     for task in reslist:
#         tasklist.append(task)
#     return str(tasklist)

@app.route('/api/distrableuserlist', methods = ['GET'])
def api_distrable_userlist(): 
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    operationlog(""+ usrname, "distrableuserlist", usrname, str(request.remote_addr))
    usrlist = []
    db = Database()
    res = db.qureyGroupUserList(usrname, False)
    for usr in res:
        usrlist.append(usr) 
    return str(usrlist)

@app.route('/api/distreduserlist', methods = ['GET'])
def api_distred_userlist(): 
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    operationlog(""+ usrname + " " + taskname, "distreduserlist", usrname, str(request.remote_addr))
    usrlist = []
    curr_path = os.path.abspath(os.path.dirname(__file__))
    newtaskname = usrname+'_'+taskname+'_*'
    db = Database()
    res = db.qureyGroupUserList(usrname, False)

    for usr in res:
        newtaskurl = curr_path + rootpath + usr[0] + "/" + newtaskname
        newtasklist = glob(newtaskurl)
        # print newtasklist
        if len(newtasklist)>0:
            for taskurl in newtasklist:
                disttaskinfo=[]
                # print task.split('/')[-1]
                disttaskinfo.append(usr[0])
                disttaskinfo.append(usr[1])
                disttaskinfo.append(taskurl.split('/')[-1])
                count=-1
                url = taskurl + "/data/" 
                filelist = listfile(url)
                #print url
                spl = taskurl.split("_")
                gstart = int(spl[-2])
                gnum = int(spl[-1])
                #print gstart, gnum
                if gstart+gnum-1 <= len(filelist):
                    count = countlabelfilenumlink(url, filelist, gstart, gnum)
                disttaskinfo.append(count) #TODO
                usrlist.append(disttaskinfo) 

    # print usrlist
    return str(usrlist)

@app.route('/api/distributetask', methods = ['GET'])
def api_distribute_task(): 
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('distusrname', type=str, location='args', required=True)
    get_parser.add_argument('start', type=int, location='args', required=True)
    get_parser.add_argument('num', type=int, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    distusrname = args.get('distusrname')
    start = args.get('start')
    num = args.get('num')
    operationlog(""+ usrname + " " + taskname + " " + distusrname, "distributetask", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    orgtaskurl = curr_path + rootpath + usrname + "/" + taskname
    newtaskname = usrname+'_'+taskname+'_'+str(start)+'_'+str(num)
    newtaskurl = curr_path + rootpath + distusrname + "/" + newtaskname

    db = Database()
    if not os.path.exists(newtaskurl):
        cmd = 'ln -s %s %s'%(orgtaskurl, newtaskurl)
        os.system(cmd)
        tasktype = db.getTasktype(usrname, taskname)
        db.writeTask(newtaskname, tasktype, 0.0, distusrname)
    tasklist = db.qureyTaskname(usrname)
    return str(tasklist)

@app.route('/api/undistributetask', methods = ['GET'])
def api_undistribute_task():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('distusrname', type=str, location='args', required=True)
    get_parser.add_argument('disttaskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    distusrname = args.get('distusrname')
    disttaskname = args.get('disttaskname')
    operationlog(""+ usrname + " " + taskname + " " + distusrname +  " " + disttaskname, "undistributetask", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    orgtaskurl = curr_path + rootpath + usrname + "/" + taskname
    # newtaskname = usrname+'_'+taskname+'_*'
    newtaskurl = curr_path + rootpath + distusrname + "/" + disttaskname
    db = Database()
    # newtasklist = glob(newtaskurl)
    # for newtask in newtasklist:
    cmd = 'rm %s'%(newtaskurl)
    os.system(cmd)
    db.delTask(distusrname, newtaskurl.split('/')[-1])
    tasklist = db.qureyTaskname(usrname)
    return str(tasklist)

@app.route('/api/demoplaterecog', methods = ['POST'])
def api_demo_platerecog():
    #get_parser = reqparse.RequestParser()
    #get_parser.add_argument('filename', type=str, location='args', required=False)
    #args = get_parser.parse_args()
    filename = random_char(5)+'.jpg'
    operationlog(""+ filename, "demoplaterecog",  'demo' , str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    imgfile = curr_path + '/Demo/Image/' + filename
    ifile = request.files['file']
    #print os.path.join(url, filename)
    ifile.save(imgfile)
    ifile.close()
    img = cv2.imread(imgfile)
    res = prdemo.prsimple(img)
    return str(res)

@app.route('/api/demosealrecog', methods = ['POST'])
def api_demo_sealrecog():
    # get_parser = reqparse.RequestParser()
    # get_parser.add_argument('filename', type=str, location='args', required=True)
    # args = get_parser.parse_args()
    filename = random_char(5)+'.jpg'
    # filename = args.get('filename')
    # print filename
    operationlog(""+ filename, "demosealrecog",  'demo' , str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    imgfile = curr_path + '/Demo/Image/' + filename
    ifile = request.files['file']
    #print os.path.join(url, filename)
    ifile.save(imgfile)
    ifile.close()
    img = cv2.imread(imgfile)
    res = sealocrdemo.fileocr(img)
    return str(res)

@app.route('/api/detectimage', methods = ['POST'])
def api_detect_image():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('filename', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    filename = args.get('filename')
    operationlog(""+ usrname + " " + taskname+ " " + filename, "detectimage", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    imgfile = curr_path + '/test/' + filename
    ifile = request.files['file']
    #print os.path.join(url, filename)
    ifile.save(imgfile)
    ifile.close()
    db = Database()
    tasktype = db.getTasktype(usrname, taskname)

    tagfile = curr_path +rootpath+usrname+'/'+taskname+taglistname
    paramfile = curr_path +rootpath+usrname+'/'+taskname+trainparamsfile
    f = file(paramfile, "r")
    jsondata = json.load(f)
    structure = jsondata['structure']
    number = jsondata['epoch']

    if tasktype == 0:
        if structure == 'yolo2':
            datacfg = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/voc.data'
            cfgfile = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/yolo.cfg'
            weightfile = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/yolo.backup'
            res = detection_yolo(datacfg, cfgfile, weightfile, imgfile)
        else:
            prefix = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure
            wordsfile = prefix + '/' + 'words.txt'
            modellists = os.listdir(prefix)
            modelprefix = ''
            size = structuresize_detect[structure]
            for modelname in modellists:
                if modelname.split('.')[-1]  == 'params':
                    modelprefix = modelname.split('-')[0]
                    break
            network = 'vgg16_reduced'
            if structure == "SSD_Inception_v3_512x512":
                network = 'inceptionv3'
            if structure == "SSD_Resnet50_512x512":
                network = 'resnet50'
            if structure == "SSD_Resnet101_512x512":
                network = 'resnet101'
            if structure == "SSD_Mobilenet_300x300":
                network = 'mobilenet'
            if structure == "SSD_Mobilenet_512x512":
                network = 'mobilenet'
            if structure == "SSD_Mobilenet_608x608":
                network = 'mobilenet'
            # print network
            prefix = prefix+'/'+modelprefix
            # print prefix
            epoch = number
            # print epoch
            # print wordsfile
            size = int(modelprefix.split('_')[-1])
            data_shape = (size, size)
            # print data_shape
            # print imgfile
            res = detection_mx(network, prefix, epoch, wordsfile, data_shape, imgfile)
            # print res
    # network = 'vgg16_reduced'
    # prefix = '/home/mq/ImageServer/static/user/uniview/foods/train/foods_vgg16_reduced_300'
    # epoch = 100
    # wordsfile = './words.txt'
    # data_shape = (300, 300)
    # imagefile = './test.jpg'
    # res = detection_mx(network, prefix, epoch, wordsfile, data_shape, imagefile)

    if tasktype == 1:
        modelprefix = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/classify'

        meanfile = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/mean.bin'
        
        size = structuresize_classify[structure]
        
        # print modelprefix
        # print number
        # print imgfile
        # print meanfile
        # print size
        # print tagfile
        res = classify(modelprefix, number, imgfile, meanfile, size, tagfile)
        # print res
    #return '{"length": 0}'
    return res

@app.route('/api/autolabelimage', methods = ['GET'])
def api_auto_label(): 
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('start', type=int, location='args', required=True)
    get_parser.add_argument('num', type=int, location='args', required=True)
    get_parser.add_argument('pretrainmodel', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    start = args.get('start')
    num = args.get('num')
    pretrainmodel = args.get('pretrainmodel')
    operationlog(""+ usrname + " " + taskname, "autolabelimage", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskurl = curr_path + rootpath + usrname + "/" + taskname
    #print taskurl
    db = Database()
    tasktype = db.getTasktype(usrname, taskname)
    tagfile = curr_path +rootpath+usrname+'/'+taskname+taglistname
    #paramfile = curr_path +rootpath+usrname+'/'+taskname+trainparamsfile
    #f = file(paramfile, "r")
    #jsondata = json.load(f)
    #structure = jsondata['structure']
    #number = jsondata['epoch']
    #print jsondata
    if pretrainmodel != '':
        structure, epoch = getstructurefrommodel(pretrainmodel)
        url = taskurl + "/data/"
        # print url
        imglist = []
        labeled = 0
        if os.path.exists(url):
            namelist = listfile(url)
            #print namelist
            end = len(namelist)
            if os.path.islink(taskurl):
                spl = taskurl.split("_")
                gstart = int(spl[-2])
                gnum = int(spl[-1])
                start = gstart+start-1
                end = gstart+gnum-1
            if end>=1:
                if start > end:
                    start = end
                if start+num > end:
                    num = end-start+1
                for i in range(start-1, start-1+num):
                    name = namelist[i]
                    labelname = (url + name+'.txt').replace('/data/','/label/')
                    if os.path.exists(labelname):
                        labeled = 1
                    else:
                        labeled = 1
                        filename = url + name
                        res = ''
                        if tasktype == 0:
                            if structure == 'yolo2':
                                datacfg = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/voc.data'
                                cfgfile = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/yolo.cfg'
                                weightfile = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/yolo.backup'
                                # print datacfg
                                # print cfgfile
                                # print weightfile
                                res = detection_yolo(datacfg, cfgfile, weightfile, filename)
                            else:
                                prefix = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure
                                wordsfile = prefix + '/' + 'words.txt'
                                modellists = os.listdir(prefix)
                                modelprefix = ''
                                size = structuresize_detect[structure]
                                for modelname in modellists:
                                    if modelname.split('.')[-1]  == 'params':
                                        modelprefix = modelname.split('-')[0]
                                        break
                                network = 'vgg16_reduced'
                                if structure == "SSD_Inception_v3_512x512":
                                    network = 'inceptionv3'
                                if structure == "SSD_Resnet50_512x512":
                                    network = 'resnet50'
                                if structure == "SSD_Resnet101_512x512":
                                    network = 'resnet101'
                                if structure == "SSD_Mobilenet_300x300":
                                    network = 'mobilenet'
                                if structure == "SSD_Mobilenet_512x512":
                                    network = 'mobilenet'
                                if structure == "SSD_Mobilenet_608x608":
                                    network = 'mobilenet'
                                # print network
                                prefix = prefix+'/'+modelprefix
                                # print prefix
                                # epoch = number
                                # print epoch
                                # print wordsfile
                                size = int(modelprefix.split('_')[-1])
                                data_shape = (size, size)
                                # print data_shape
                                # print filename
                                res = detection_mx(network, prefix, epoch, wordsfile, data_shape, filename)
                                print res
                        if tasktype == 1:
                            modelprefix = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/classify'
                            meanfile = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/mean.bin'
                            size = structuresize_classify[structure]
                            # print modelprefix
                            # print number
                            # print imgfile
                            # print meanfile
                            # print size
                            # print tagfile
                            res = classify(modelprefix, epoch, filename, meanfile, size, tagfile)
                            # print res	
                        f=open(labelname,'w')
                        f.writelines(res)
                        f.close()
        return "OK"
    else:
        return "Error"
    return 'OK'

@app.route('/api/inferlabel', methods = ['GET'])
def api_infer_label():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('index', type=int, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    index = args.get('index')
    print index
    operationlog(""+ usrname + " " + taskname+ " "+str(index), "inferlabel", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskurl = curr_path + rootpath + usrname + "/" + taskname
    url = taskurl + "/data/"
    namelist = listfile(url, 0) 
    gstart = 1
    if os.path.islink(taskurl):
        spl = taskurl.split("_")
        gstart = int(spl[-2])
    filepath1 = url+namelist[index+gstart-3]
    filetxtpath1 = (url+namelist[index+gstart-3]+'.txt').replace('/data/','/label/')
    filepath2 = url+namelist[index+gstart-2]
    if os.path.exists(filepath1) and os.path.exists(filetxtpath1) and os.path.exists(filepath2):
        argument = " tools/kcftracker.py %s %s "%(filepath1, filepath2)
        print argument
        proc = subprocess.Popen("python" + argument, shell=True)
        return 'OK'
    else:
        return 'Failed'

@app.route('/api/autolabeltestimage', methods = ['POST'])
def api_auto_testlabel(): 
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('pretrainmodel', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    pretrainmodel = args.get('pretrainmodel')
    filelistdata = request.data.replace('\'','\"')
    # print filelistdata
    jsondata = json.loads(filelistdata)
    # print jsondata
    namelist = jsondata['imageList']
    # print namelist
    operationlog(""+ usrname + " " + taskname, "autolabeltestimage", usrname, str(request.remote_addr))
    curr_path = os.path.abspath(os.path.dirname(__file__))
    taskurl = curr_path + rootpath + usrname + "/" + taskname
    #print taskurl
    db = Database()
    tasktype = db.getTasktype(usrname, taskname)
    tagfile = curr_path +rootpath+usrname+'/'+taskname+taglistname
    #paramfile = curr_path +rootpath+usrname+'/'+taskname+trainparamsfile
    #f = file(paramfile, "r")
    #jsondata = json.load(f)
    #structure = jsondata['structure']
    #number = jsondata['epoch']
    print jsondata
    if pretrainmodel != '':
        structure, epoch = getstructurefrommodel(pretrainmodel)
        url = taskurl + "/test/"
        print url

        if os.path.exists(url):
            for name in namelist:
                labelname = url + name+'.txt'
                filename = url + name
                res = ''
                if tasktype == 0:
                    if structure == 'yolo2':
                        datacfg = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/voc.data'
                        cfgfile = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/yolo.cfg'
                        weightfile = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/yolo.backup'
                        # print datacfg
                        # print cfgfile
                        # print weightfile
                        res = detection_yolo(datacfg, cfgfile, weightfile, filename)
                    else:
                        prefix = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure
                        wordsfile = prefix + '/' + 'words.txt'
                        modellists = os.listdir(prefix)
                        modelprefix = ''
                        size = structuresize_detect[structure]
                        for modelname in modellists:
                            if modelname.split('.')[-1]  == 'params':
                                modelprefix = modelname.split('-')[0]
                                break
                        network = 'vgg16_reduced'
                        if structure == "SSD_Inception_v3_512x512":
                            network = 'inceptionv3'
                        if structure == "SSD_Resnet50_512x512":
                            network = 'resnet50'
                        if structure == "SSD_Resnet101_512x512":
                            network = 'resnet101'
                        if structure == "SSD_Mobilenet_300x300":
                            network = 'mobilenet'
                        if structure == "SSD_Mobilenet_512x512":
                            network = 'mobilenet'
                        if structure == "SSD_Mobilenet_608x608":
                            network = 'mobilenet'
                        print network
                        prefix = prefix+'/'+modelprefix
                        # print prefix
                        # epoch = number
                        # print epoch
                        # print wordsfile
                        size = int(modelprefix.split('_')[-1])
                        data_shape = (size, size)
                        # print data_shape
                        print filename
                        res = detection_mx(network, prefix, epoch, wordsfile, data_shape, filename)
                        print res
                if tasktype == 1:
                    modelprefix = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/classify'
                    meanfile = curr_path +rootpath+usrname+'/'+taskname+'/train/'+structure+'/mean.bin'
                    size = structuresize_classify[structure]
                    # print modelprefix
                    # print number
                    # print imgfile
                    # print meanfile
                    # print size
                    # print tagfile
                    res = classify(modelprefix, epoch, filename, meanfile, size, tagfile)
                    # print res 
                f=open(labelname,'w')
                f.writelines(res)
                f.close()
        return "OK"
    else:
        return "Error"
    return 'OK'

@app.route('/api/getworkerlist', methods = ['GET'])
def api_get_workerlist():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    db = Database()
    workerlist = db.qureyWorkerlist(usrname)
    #print workerlist
    workerl = []
    if len(workerlist)>0:
        for worker in workerlist:
            #print worker
            ISFORMAT="%Y-%m-%d %H:%M:%S"
            updatetime = time.mktime(time.strptime(worker[4],ISFORMAT))
            timenow = time.time()
            timediff = timenow - updatetime
            if timediff > 360:
                print "del worker", worker[0]
                db.delWorker(worker[0])
            else:
                workerl.append(worker)
    #print workerl
    return str(workerl)

@app.route('/api/modifyworkerowner', methods = ['POST'])
def api_modify_workerowner():
    curr_path = os.path.abspath(os.path.dirname(__file__))
    data = json.loads(request.data)
    usrname = data['name']
    passwd = data['passwd']
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('workername', type=str, location='args', required=True)
    get_parser.add_argument('ownername', type=str, location='args', required=True)
    args = get_parser.parse_args()
    workername = args.get('workername')
    ownername = args.get('ownername')
    operationlog(""+ workername + " " + ownername, "modifyworkerowner", usrname, str(request.remote_addr))
    db = Database()
    res, level, group  = db.verifyusr(usrname, passwd)
    if res and level == SUPER:
        db.modifyworkerowner(workername, ownername)
        return 'OK'
    return 'Fail'

@app.route('/api/getmanagerusrlist', methods = ['POST'])
def api_get_managerlist():
    curr_path = os.path.abspath(os.path.dirname(__file__))
    data = json.loads(request.data)
    usrname = data['name']
    passwd = data['passwd']
    operationlog("", "getmanagerusrlist", usrname, str(request.remote_addr))
    db = Database()
    res, level, group = db.verifyusr(usrname, passwd)
    usrlist = ['all']
    if res and level >= MANAGE:
        reslist = db.getmanagerusrlist()
        for usr in reslist:
            usrlist.append(usr[0])
    return str(usrlist)

# @app.route('/api/getmanagerusrlistget', methods = ['GET'])
# def api_get_managerlist1():
#     curr_path = os.path.abspath(os.path.dirname(__file__))
#     db = Database()
#     usrlist = []
#     reslist = db.getmanagerusrlist()
#     for usr in reslist:
#         usrlist.append(usr[0])
#     return str(usrlist)

@app.route('/api/getlabelzip', methods = ['POST']) #TODO verify
def api_get_labelzip():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    randomstring = random_char(5)
    url = ipport + rootpath + usrname + "/" + taskname + ziplabel + randomstring + ".tar"
    tarpath = curr_path + rootpath + usrname + "/" + taskname + ziplabel + randomstring + ".tar"
    rmtarpath = curr_path + rootpath + usrname + "/" + taskname + ziplabel + "*.tar"
    txtpath = curr_path + rootpath + usrname + "/" + taskname + '/label'
    taskpath = curr_path + rootpath + usrname + "/" + taskname
    #print url
    # print txtpath
    data = json.loads(request.data)
    # print data
    usrname = data['name']
    passwd = data['passwd']
    operationlog(""+ usrname+" "+taskname, "getlabeltar", usrname, str(request.remote_addr))
    db = Database()
    res, level, group = db.verifyusr(usrname, passwd)
    if res and level >= MANAGE:
        cmd = 'rm %s'%(rmtarpath)
        os.system(cmd)
        #os.remove(rmtarpath)
        #cmd = 'zip -qjr %s %s'%(tarpath, txtpath)
        cmd = 'tar -cf %s -C %s label'%(tarpath, taskpath)
        print cmd
        os.system(cmd)
        # print url
        return url
    return 'Fail'

# @app.route('/api/getlabelzipget', methods = ['GET']) #TODO verify
# def api_get_labelzipget():
#     get_parser = reqparse.RequestParser()
#     get_parser.add_argument('usrname', type=str, location='args', required=True)
#     get_parser.add_argument('taskname', type=str, location='args', required=True)
#     args = get_parser.parse_args()
#     usrname = args.get('usrname')
#     taskname = args.get('taskname')
#     curr_path = os.path.abspath(os.path.dirname(__file__))
#     randomstring = random_char(5)
#     url = ipport + rootpath + usrname + "/" + taskname + ziplabel + randomstring + ".zip"
#     tarpath = curr_path + rootpath + usrname + "/" + taskname + ziplabel + randomstring + ".zip"
#     txtpath = curr_path + rootpath + usrname + "/" + taskname + '/data/*.txt'
#     cmd = 'zip -qj %s %s'%(tarpath, txtpath)
#     os.system(cmd)
#     return url
    

@app.route('/api/getmodel', methods = ['POST']) #TODO verify
def api_get_model():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('structure', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    structure = args.get('structure')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    randomstring = random_char(5)
    url = ipport + rootpath + usrname + "/" + taskname + "/train" + zipmodel+ randomstring + ".zip"
    tarpath = curr_path + rootpath + usrname + "/" + taskname + "/train" + zipmodel+ randomstring + ".zip"
    rmtarpath = curr_path + rootpath + usrname + "/" + taskname + "/train" + zipmodel + "*.zip"
    zippath = curr_path + rootpath + usrname + "/" + taskname + "/train/" + structure + "/*"
    #othermodelpath = curr_path + rootpath + usrname + "/" + taskname + '/train/*.weights'

    data = json.loads(request.data)
    usrname = data['name']
    passwd = data['passwd']
    operationlog(""+ usrname+" "+taskname, "getmodel", usrname, str(request.remote_addr))
    db = Database()
    res, level, group  = db.verifyusr(usrname, passwd)
    if res and level >= MANAGE:
        # cmd = 'rm %s'%(rmtarpath)
        # os.system(cmd)
        os.remove(rmtarpath)
        #cmd = 'rm %s'%(othermodelpath)
        #os.system(cmd)
        cmd = 'zip -qj %s %s'%(tarpath, zippath)
        print cmd
        os.system(cmd)
        return url
    return 'Fail'

# @app.route('/api/getmodel1', methods = ['GET']) #TODO verify
# def api_get_model1():
#     get_parser = reqparse.RequestParser()
#     get_parser.add_argument('usrname', type=str, location='args', required=True)
#     get_parser.add_argument('taskname', type=str, location='args', required=True)
#     get_parser.add_argument('structure', type=str, location='args', required=True)
#     args = get_parser.parse_args()
#     usrname = args.get('usrname')
#     taskname = args.get('taskname')
#     structure = args.get('structure')
#     curr_path = os.path.abspath(os.path.dirname(__file__))
#     randomstring = random_char(5)
#     url = ipport + rootpath + usrname + "/" + taskname + "/train" + zipmodel+ randomstring + ".zip"
#     tarpath = curr_path + rootpath + usrname + "/" + taskname + "/train" + zipmodel+ randomstring + ".zip"
#     rmtarpath = curr_path + rootpath + usrname + "/" + taskname + "/train" + zipmodel + "*.zip"
#     zippath = curr_path + rootpath + usrname + "/" + taskname + "/train/" + structure + "/*"
#     #othermodelpath = curr_path + rootpath + usrname + "/" + taskname + '/train/*.weights'

#     if True:
#         cmd = 'rm %s'%(rmtarpath)
#         os.system(cmd)
#         #cmd = 'rm %s'%(othermodelpath)
#         #os.system(cmd)
#         cmd = 'zip -qj %s %s'%(tarpath, zippath)
#         print cmd
#         os.system(cmd)
#         return url
#     return 'Fail'

@app.route('/api/getdefaulttrainparams', methods = ['GET']) #TODO verify
def api_get_defaulttrainparams():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('structure', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    structure = args.get('structure')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    defaultparam = ''
    # print structure
    if 'SSD' in structure:
        defaultparam = '{"structure":"%s","epoch":200,"batchsize":32,"learningrate":"0.002","weightdecay":0.0005,"momentum":0.9,"optimizer":"SGD","Retrain":0}'%structure
    elif 'yolo' in structure:
        defaultparam = '{"structure":"%s","epoch":5000,"batchsize":32,"learningrate":"0.0001","weightdecay":0.0005,"momentum":0.9,"optimizer":"SGD","Retrain":0}'%structure
    else:
        defaultparam = '{"structure":"%s","epoch":200,"batchsize":64,"learningrate":"0.05","weightdecay":0.0005,"momentum":0.9,"optimizer":"SGD","Retrain":0}'%structure
    # print defaultparam
    return defaultparam

@app.route('/api/gettrainparams', methods = ['GET']) #TODO verify
def api_get_trainparams():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    parampath = curr_path + rootpath + usrname + "/" + taskname + trainparamsfile
    jsonstring = "{}"
    #print parampath
    if os.path.exists(parampath):
        jsonstring = open(parampath).read()
    #print jsonstring
    operationlog(""+ usrname+" "+taskname, "gettrainparams", usrname, str(request.remote_addr))
    return jsonstring

@app.route('/api/savetrainparams', methods = ['POST']) #TODO verify
def api_save_trainparams():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    parampath = curr_path + rootpath + usrname + "/" + taskname + trainparamsfile
    open(parampath, 'w').write(request.data)
    operationlog(""+ usrname+" "+taskname + request.data, "savetrainparams", usrname, str(request.remote_addr))
    return request.data

@app.route('/api/getdetstructure', methods = ['GET']) 
def api_get_detstructure():
    #return str(["yolo2"]).replace('\'','\"')
    return str(["yolo2", "SSD_VGG16_300x300", "SSD_VGG16_512x512","SSD_Inception_v3_512x512", 
                    "SSD_Resnet50_512x512", "SSD_Resnet101_512x512", "SSD_Mobilenet_300x300", "SSD_Mobilenet_512x512", "SSD_Mobilenet_608x608"]).replace('\'','\"')
    # , "Faster_rcnn_VGG", "Faster_rcnn_Resnet101"

@app.route('/api/getclsstructure', methods = ['GET']) 
def api_get_recstructure():
    #return str(["mobilenet", "googlenet", "resnet101"]).replace('\'','\"')
    return str(["mobilenet","shufflenet","googlenet", "densenet121", "densenet161", "densenet169", "densenet201", "inception_bn","inception_resnet_v2","inception_v3",
                    "resnet18", "resnet34", "resnet50","resnet101","resnext18","resnext34","resnext50","resnext101",
                    "squeezenet","vgg11","vgg16","vgg19","alexnet","lenet","inception_bn_28",
                    "resnet20_28","resnet38_28","resnet56_28",
                    "resnext20_28","resnext38_28","resnext56_28"]).replace('\'','\"')

@app.route('/api/getoptmethod', methods = ['GET']) 
def api_get_clsoptmethod():
    #return str(["yolo2", "ssd"]).replace('\'','\"')
    return str(["SGD", "AdaGrad", "RMSProp", "Adam", "Adamax", "Nadam"]).replace('\'','\"')

@app.route('/api/getpretrainmodel', methods = ['GET']) 
def api_get_pretrainmodel():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    get_parser.add_argument('structure', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    structure = args.get('structure')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    trainpath = curr_path + rootpath + usrname + "/" + taskname + '/train/'
    structurepath = trainpath+structure
    # print structure
    modellist = getmodellist(structurepath+'/')
    # print modellist
    return str(modellist).replace('\'','\"')
    # if structure=='yolo2':
    #     return str(["yolotest1.param", "yolotest2.param", "yolotest3.param"]).replace('\'','\"')
    # else:
    #     return str(["test11.param", "test12.param", "test13.param"]).replace('\'','\"')

@app.route('/api/getpretrainmodelall', methods = ['GET']) 
def api_get_pretrainmodelall():
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('usrname', type=str, location='args', required=True)
    get_parser.add_argument('taskname', type=str, location='args', required=True)
    args = get_parser.parse_args()
    usrname = args.get('usrname')
    taskname = args.get('taskname')
    curr_path = os.path.abspath(os.path.dirname(__file__))
    trainpath = curr_path + rootpath + usrname + "/" + taskname + '/train/'
    modellist = getmodellistall(trainpath+'/')
    # print modellist
    return str(modellist).replace('\'','\"')
    # return str(["yolotest1.param", "yolotest2.param", "yolotest3.param"]).replace('\'','\"')

@app.route('/api/loaddoc', methods = ['GET'])
def api_load_doc():
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url = curr_path + rootpath + docname
    if os.path.exists(url):
        f = open(url)
        txt = f.read()
        #print txt
        return txt
    else:
        return '{}'


@app.route('/api/savedoc', methods = ['POST'])
def api_save_doc():
    curr_path = os.path.abspath(os.path.dirname(__file__))
    url = curr_path + rootpath + docname
    #print request.data
    f=open(url,'w')
    f.writelines(request.data)
    f.close()
    return request.data + "\n"

if __name__ == '__main__':
    #app.run()
    app.run(host="0.0.0.0", port=8031)
