import numpy as np
import scimath as sm
import matplotlib.pyplot as plt
import json
import yaml
import sys
import os

# Make sure that caffe is on the python path:
configStream = open("FluffyHaiiro.yaml", "r")
config = yaml.load(configStream)

caffe_root = config.get(':caffe_root_path')

sys.path.insert(0, caffe_root + 'python')

import caffe

plt.rcParams['figure.figsize'] = (10, 10)
plt.rcParams['image.interpolation'] = 'nearest'
plt.rcParams['image.cmap'] = 'gray'


if not os.path.isfile(caffe_root + '/models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel'):
    #print("Downloading pre-trained CaffeNet model...")
    os.system('python ../scripts/download_model_binary.py ../models/bvlc_reference_caffenet')

caffe.set_mode_cpu()
net = caffe.Net(caffe_root + '/models/bvlc_reference_caffenet/deploy.prototxt',
      caffe_root + '/models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel',
      caffe.TEST)

# input preprocessing: 'data' is the name of the input blob == net.inputs[0]
transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
transformer.set_transpose('data', (2,0,1))
transformer.set_mean('data', np.load(caffe_root + '/python/caffe/imagenet/ilsvrc_2012_mean.npy').mean(1).mean(1)) # mean pixel
transformer.set_raw_scale('data', 255)  # the reference model operates on images in [0,255] range instead of [0,1]
transformer.set_channel_swap('data', (2,1,0))  # the reference model has channels in BGR order instead of RGB

# set net to batch size of 50
net.blobs['data'].reshape(50,3,227,227)

#net.blobs['data'].data[...] = transformer.preprocess('data', caffe.io.load_image(caffe_root + 'examples/images/cat.jpg'))
imagePath = ""
if len(sys.argv) == 2:
	imagePath = str(sys.argv[1])
else:
	imagePath = '/home/mizu/Downloads/sashimi.jpg'

net.blobs['data'].data[...] = transformer.preprocess('data', caffe.io.load_image(imagePath))
out = net.forward()
#print("Predicted class is #{}.".format(out['prob'].argmax()))

imagenet_labels_filename = caffe_root + '/data/ilsvrc12/synset_words.txt'
try:
    labels = np.loadtxt(imagenet_labels_filename, str, delimiter='\t')
except:
    os.system('. ../data/ilsvrc12/get_ilsvrc_aux.sh')
    labels = np.loadtxt(imagenet_labels_filename, str, delimiter='\t')

# sort top k predictions from softmax output
top_k = net.blobs['prob'].data[0].flatten().argsort()[-1:-6:-1]
#write to a file?
#commaSeparatedResult = labels[top_k]

#for label in commaSeparatedResult:
#	print label
print json.dumps(labels[top_k].tolist())
# CPU mode: how much time used
# net.forward()  # call once for allocation
# %timeit net.forward()

