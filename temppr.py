
#coding:utf-8
# import Demo.PR.prsimple as prdemo
import cv2
import threading
import time
# from aip import AipOcr
import Demo.SEALOCR.fileocr as sealocrdemo

class test(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        st = time.time()
        img = cv2.imread("/home/mq/ImageServer/temp.jpg")
        # prdemo.prsimple(img)
        print time.time()-st

if __name__ == '__main__':
    img = cv2.imread("/home/mq/ImageServer/Demo/SEALOCR/gz/timg16.jpg")
    mess = sealocrdemo.fileocr(img)
    print mess
    # nfuncs = 1
    # threads = []
    # for i in range(nfuncs):
    #     t = test()
    #     threads.append(t)
    # temp = 0
    # for i in range(nfuncs):
    #     threads[i].start()
