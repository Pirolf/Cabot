import cPickle
import os
import sys
import time
import numpy as np
import pandas as pd
import cStringIO as StringIO
import urllib
import caffe

REPO_DIRNAME = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + '/../caffe')

class ImageClassifier(object):
  default_args = {
    'model_def_file': (
             '{}/models/bvlc_reference_caffenet/deploy.prototxt'.format(REPO_DIRNAME)),
          'pretrained_model_file': (
             '{}/models/bvlc_reference_caffenet/bvlc_reference_caffenet.caffemodel'.format(REPO_DIRNAME)),
          'mean_file': (
           '{}/python/caffe/imagenet/ilsvrc_2012_mean.npy'.format(REPO_DIRNAME)),
          'class_labels_file': (
           '{}/data/ilsvrc12/synset_words.txt'.format(REPO_DIRNAME)),
          'bet_file': (
           '{}/data/ilsvrc12/imagenet.bet.pickle'.format(REPO_DIRNAME)),
  }
  for key, val in default_args.iteritems():
    if not os.path.exists(val):
          raise Exception(
            "File for {} is missing. Should be at: {}".format(key, val))
  default_args['image_dim'] = 256
  default_args['raw_scale'] = 255.

  def __init__(self, model_def_file, pretrained_model_file, mean_file,
                 raw_scale, class_labels_file, bet_file, image_dim):
      caffe.set_mode_cpu()
      self.net = caffe.Classifier(
      model_def_file, pretrained_model_file,
      image_dims=(image_dim, image_dim), raw_scale=raw_scale,
      mean=np.load(mean_file).mean(1).mean(1), channel_swap=(2, 1, 0)
      )

      with open(class_labels_file) as f:
              labels_df = pd.DataFrame([
                  {
                    'synset_id': l.strip().split(' ')[0],
                    'name': ' '.join(l.strip().split(' ')[1:]).split(',')[0]
                  }
                  for l in f.readlines()
              ])
      self.labels = labels_df.sort('synset_id')['name'].values

      self.bet = cPickle.load(open(bet_file))
        # A bias to prefer children nodes in single-chain paths
        # I am setting the value to 0.1 as a quick, simple model.
        # We could use better psychological models here...
      self.bet['infogain'] -= np.array(self.bet['preferences']) * 0.1

  def classify_image(self, image):
        try:
            starttime = time.time()
            scores = self.net.predict([image], oversample=True).flatten()
            endtime = time.time()

            indices = (-scores).argsort()[:5]
            predictions = self.labels[indices]

            # In addition to the prediction text, we will also produce
            # the length for the progress bar visualization.
            meta = [
                (p, '%.5f' % scores[i])
                for i, p in zip(indices, predictions)
            ]
            # Compute expected information gain
            expected_infogain = np.dot(
                self.bet['probmat'], scores[self.bet['idmapping']])
            expected_infogain *= self.bet['infogain']

            # sort the scores
            infogain_sort = expected_infogain.argsort()[::-1]
            bet_result = [(self.bet['words'][v], '%.5f' % expected_infogain[v])
                          for v in infogain_sort[:5]]
            return (True, meta, bet_result, '%.3f' % (endtime - starttime))

        except Exception as err:
            return (False, 'Something went wrong when classifying the '
                           'image. Maybe try another one?')
  def classify_url(self, imageUrl):
      try:
            string_buffer = StringIO.StringIO(
              urllib.urlopen(imageUrl).read())
            image = caffe.io.load_image(string_buffer)
      except Exception as err:
            return False

      result = self.classify_image(image)
      return  result