#coding=utf-8
import os

def gentag(taglist):
    string = '{"listname":["种类"],"taglist":{"种类":['
    num = len(taglist)
    i=0
    for tag in taglist:
        string += '"%s"'%(tag)
        i=i+1
        if i<num:
            string += ","
    string += ']}}'
    return string

imgNum =0

os.system("rm -rf ./data")

taglist = {}

for parentdir,dirname,filenames in os.walk("."):  
            label = parentdir.split('/')[-1]
            #print label
            if label not in taglist:
                taglist[label] = 1
            else:
                taglist[label] = taglist[label]+1

ft = open('tag.json', 'w')
tagstring = gentag(taglist)
print tagstring
ft.write(tagstring)
ft.close()