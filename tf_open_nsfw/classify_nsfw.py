import sys
import argparse
import urllib

import tensorflow as tf

from tf_open_nsfw.model import OpenNsfwModel, InputType
from tf_open_nsfw.image_utils import create_tensorflow_image_loader
from tf_open_nsfw.image_utils import create_yahoo_image_loader

import numpy as np

IMAGE_LOADER_TENSORFLOW = "tensorflow"
IMAGE_LOADER_YAHOO = "yahoo"


def classify_nsfw(image_url,
                  weights_src="tf_open_nsfw/data/open_nsfw-weights.npy",
                  image_loader=IMAGE_LOADER_YAHOO,
                  input_type=InputType.TENSOR):
    tf.reset_default_graph()

    try:
        image_src = urllib.request.urlopen(image_url).read()
    except Exception as e:
        print(e)
        return 100.0, 0.0

    model = OpenNsfwModel()

    with tf.Session() as sess:
        model.build(weights_path=weights_src, input_type=input_type)

        fn_load_image = None

        if input_type == InputType.TENSOR:
            if image_loader == IMAGE_LOADER_TENSORFLOW:
                fn_load_image = create_tensorflow_image_loader(sess)
            else:
                fn_load_image = create_yahoo_image_loader()
        elif input_type == InputType.BASE64_JPEG:
            import base64
            fn_load_image = lambda filename: np.array([base64.urlsafe_b64encode(open(filename, "rb").read())])

        sess.run(tf.global_variables_initializer())

        image = fn_load_image(image_src)

        predictions = sess.run(model.predictions, feed_dict={model.input: image})

        return predictions[0][0], predictions[0][1]
