# -*- coding: utf-8 -*-
import uniout
#==========================
import xml.etree.ElementTree as ET
import os

def genlabeltxtfromxml(xmlfile):
    tree = ET.parse(xmlfile)
    root = tree.getroot()
    # print('root-tag:',root.tag,',root-attrib:',root.attrib,',root-text:',root.text)
    # for child in root:
    #      print('child-tag是：',child.tag,',child.attrib：',child.attrib,',child.text：',child.text)
    #      for sub in child:
    #           print('sub-tag是：',sub.tag,',sub.attrib：',sub.attrib,',sub.text：',sub.text)
    sizenode = root.find('size') 
    width = 1000
    height = 1000
    for s in sizenode:
        #print s.tag, s.text
        if s.tag=='width':
            width = int(s.text)
        if s.tag=='height':
            height= int(s.text)


    animNode = root.findall('object') #查找root节点下第一个tag为country的节点
    #print(animNode.tag,animNode.attrib,animNode.text)
    length = len(animNode)
    string = ''
    string +='{"length":%d, "objects":['%length

    index = 0
    for node in animNode:
        string += '{'
        for sub in node:
            if sub.tag=='name': 
                string += '"info":"", "tag":["%s"],'%sub.text
            if sub.tag=='bndbox': 
                for box in sub:
                    if box.tag=="xmin":
                        string += '"x_start": %.3f, '%float(int(box.text)*1.0/width)
                    if box.tag=="ymin":
                        string += '"y_start": %.3f, '%float(int(box.text)*1.0/height)
                    if box.tag=="xmax":
                        string += '"x_end": %.3f, '%float(int(box.text)*1.0/width)
                    if box.tag=="ymax":
                        string += '"y_end": %.3f'%float(int(box.text)*1.0/height)
        if index<length-1:
            string += '},'
        else:
            string += '}'
        index += 1

    string += ']}'

    s = string.replace('\'','\"')
    return s

IMAGE_EXTENSIONS = set(['xml'])

if __name__ == '__main__':
    for parentdir,dirname,filenames in os.walk('.'):  
        for filename in filenames:  
            if filename.split('.')[-1] in IMAGE_EXTENSIONS: 
                txtfilename = filename.replace('xml','jpg.txt')
                string = genlabeltxtfromxml(filename)
                f = open(txtfilename, 'w')
                f.writelines(string)
                f.close()
    
# {"length": 6, "objects": [{"info": "\u6d59AQT885", "x_start": 0.67, "x_end": 0.713, "y_end": 0.565, "tag": ["blueplate"], "y_start": 0.543}, {"info": "\u6d59AQT063", "x_start": 0.398, "x_end": 0.435, "y_end": 0.498, "tag": ["blueplate"], "y_start": 0.473}, {"info": "\u6d59ASL956", "x_start": 0.961, "x_end": 0.988, "y_end": 0.207, "tag": ["blueplate"], "y_start": 0.188}, {"info": "\u6d59AJ2287", "x_start": 0.552, "x_end": 0.579, "y_end": 0.093, "tag": ["blueplate"], "y_start": 0.077}, {"info": "", "x_start": 0.435, "x_end": 0.465, "y_end": 0.055, "tag": ["blueplate"], "y_start": 0.045}, {"info": "", "x_start": 0.678, "x_end": 0.706, "y_end": 0.023, "tag": ["blueplate"], "y_start": 0.012}]}