from __future__ import print_function
import tensorflow as tf

import argparse
import os
from six.moves import cPickle

from model import Model

from six import text_type

from datetime import datetime
from random import randint

def main():
    parser = argparse.ArgumentParser(
                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--save_dir', type=str, default='save/gsc-body',
                        help='model directory to store checkpointed models')
    parser.add_argument('-n', type=int, default=randint(800,1600),
                        help='number of characters to sample')
    parser.add_argument('--prime', type=text_type, default=u'<br>',
                        help='prime text')
    parser.add_argument('--sample', type=int, default=1,
                        help='0 to use max at each timestep, 1 to sample at '
                             'each timestep, 2 to sample on spaces')
    parser.add_argument('--file_prefix', type=str, default='body',
                        help='output text file name prefix')

    args = parser.parse_args()
    sample(args)


def sample(args):
    with open(os.path.join(args.save_dir, 'config.pkl'), 'rb') as f:
        saved_args = cPickle.load(f)
    with open(os.path.join(args.save_dir, 'chars_vocab.pkl'), 'rb') as f:
        chars, vocab = cPickle.load(f)
    model = Model(saved_args, training=False)
    with tf.Session() as sess:
        tf.global_variables_initializer().run()
        saver = tf.train.Saver(tf.global_variables())
        ckpt = tf.train.get_checkpoint_state(args.save_dir)
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(sess, ckpt.model_checkpoint_path)
            sample_result = model.sample(sess, chars, vocab, args.n, args.prime, args.sample)
            print(sample_result)

            currenttime = str(datetime.now().strftime("%y-%m-%d-%H-%M"))

            with open('./generated/{}-{}.txt'.format(args.file_prefix, currenttime), 'w') as f:
                f.write(sample_result)

if __name__ == '__main__':
    main()
