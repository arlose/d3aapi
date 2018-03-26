import mxnet as mx
import logging
import numpy as np
import cv2
import scipy.io as sio
from symbol.mobilenet import MobileNet

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
num_round = 44
prefix = "model/MobileNet"
model = mx.model.FeedForward.load(prefix, num_round, ctx=mx.gpu(), numpy_batch_size=1)
# synset = [l.strip() for l in open('Inception/synset.txt').readlines()]


symbol = MobileNet(alpha=0.5, num=10)
internals = symbol.get_internals()
internalnames = internals.list_outputs()
_, out_shapes, _ = internals.infer_shape(data=(1,3, 128, 128))
shape_dict = dict(zip(internals.list_outputs(), out_shapes))
for symbolname in internalnames:
    print symbolname, shape_dict[symbolname]

# @profile
def PreprocessImage(path, show_img=False):
    # load image
    img = cv2.imread(path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # print img
    mean_img = mx.nd.load('mean.bin').values()[0].asnumpy()
    # print mean_img
    if img.shape[0] > img.shape[1]:
        newsize = (128, img.shape[0] * 128 / img.shape[1])
    else:
        newsize = (img.shape[1] * 128 / img.shape[0], 128)
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

right = 0

sum = 0
with open('train/test.lst', 'r') as fread:
    for line in fread.readlines()[:]:
        sum +=1
        batch  = 'train/'+line.split("\t")[2].strip("\n")
        print batch
        batch = PreprocessImage(batch, False)
        [prob, data1, label1] = model.predict(batch, return_data=True)
        pred = np.argmax(prob)
        # # Get top1 label
        # top1 = synset[pred[0]]
        top_1 = pred
        label = int(float(line.split("\t")[1]))
        print top_1, label

        if top_1 == label:
            # print ' right'
            right += 1
print 'top 1 accuracy: %f '%(right/(1.0*sum))

print sum

# fea_symbol = internals["bn_data_output"]

# feature_extractor = mx.model.FeedForward(ctx=mx.gpu(), symbol=fea_symbol, 
#                                          arg_params=model.arg_params,
#                                          aux_params=model.aux_params,
#                                          allow_extra_params=True)
# print feature_extractor

# data_shape = (3, 128, 128)  
# right = 0
# val = mx.io.ImageRecordIter(  
#         path_imgrec = "test1.rec",
#         mean_img    = "mean.bin",
#         scale       = 1./255, 
#         rand_crop   = False,  
#         rand_mirror = False,  
#         data_shape  = data_shape,  
#         batch_size  = 1)  
  
# [prob, data1, label1] = model.predict(val, return_data=True)  
# print prob
# print data1
# print label1
# preds = np.argmax(prob, axis=1)
# for i in range(len(preds)):
#     if preds[i]==label1[i]:
#         right += 1
# print 'top 1 accuracy: %f '%(right/(1.0*len(preds)))
