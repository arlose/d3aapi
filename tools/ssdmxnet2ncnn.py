import mxnet as mx
from collections import namedtuple
import numpy as np
import argparse
import os

# example: 
# cd ..
# python tools/ssdmxnet2ncnn.py --prefix tools/pdn_mobilenet_300 --epoch 70 --size 300 --classnum 10

# detection example
# ./ssdmobilenet test.jpg pdn_mobilenet_300.proto pdn_mobilenet_300.bin 300

def parse_args():
    parser = argparse.ArgumentParser(description='mxnet ssd model transform')
    parser.add_argument('--epoch', dest='epoch', help='epoch of trained model',
                        default=0, type=int)
    parser.add_argument('--prefix', dest='prefix', help='trained model prefix',
                        default=os.path.join(os.getcwd(), 'model', 'ssd_'),
                        type=str)
    parser.add_argument('--size', dest='size', help='input image size',
                        default=300, type=int)
    parser.add_argument('--classnum', dest='classnum', help='class num',
                        default=10, type=int)
    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()
    prefix = args.prefix
    epoch = args.epoch
    size = args.size
    classnum = args.classnum
    sym, arg_params, aux_params = mx.model.load_checkpoint(prefix, epoch)
    nms_thresh = 0.5
    confidence_thresh = 0.3
    force_suppress = False
    nms_topk = 400
    all_layers = sym.get_internals()
    anchor_boxes = all_layers['multibox_anchors_output']
    loc_preds = all_layers['multibox_loc_pred_output']
    cls_preds = all_layers['multibox_cls_pred_output']
    cls_prob = mx.symbol.SoftmaxActivation(data=cls_preds, mode='channel', name='cls_prob')
    out = mx.symbol.contrib.MultiBoxDetection(*[cls_prob, loc_preds, anchor_boxes], \
            name="detection", nms_threshold=nms_thresh, force_suppress=force_suppress,
            variances=(0.1, 0.1, 0.2, 0.2), nms_topk=nms_topk, threshold = confidence_thresh)
    

    mxnetparamfile = '%s-%04d.params' % (prefix, epoch)
    mxnetjsonfile = '%s-symbol.json' % (prefix)
    ncnnbinfile = '%s.bin' % (prefix)
    ncnnprotofile = '%s.proto' % (prefix)

    outj = out.tojson()
    fh = open(mxnetjsonfile, 'w') 
    fh.write(outj) 
    fh.close() 

    cmd = 'tools/mxnet2ncnn %s %s %s %s %d %d'%(mxnetjsonfile, mxnetparamfile, ncnnprotofile, ncnnbinfile, size, classnum)
    os.system(cmd)