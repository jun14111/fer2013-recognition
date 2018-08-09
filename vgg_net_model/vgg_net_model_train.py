# -*- coding: utf-8 -*-

import time
import numpy as np
import tensorflow as tf
import tensorlayer as tl
from tensorlayer.layers import *

import fer2013_input

# 参数
EPOCH_NUM = 200  # training iter = epoch * batch
BATCH_SIZE = 128

LEARNING_RATE = 0.0001
IMAGE_SIZE = fer2013_input.IMG_SIZE

X = tf.placeholder(dtype=tf.float32, shape=[
    None, IMAGE_SIZE, IMAGE_SIZE, 1], name='x')
Y_CORRECT = tf.placeholder(dtype=tf.int64, shape=[None], name='y_correct')

TRAIN_DATA_SRC = fer2013_input.TRAIN_DATA_SRC
TEST_DATA_SRC = fer2013_input.TEST_DATA_SRC
MODEL_SAVE_PATH = "../drive/machine_learning/fer2013/model/vgg_net/"


def vgg_net_model(x, y_correct, reuse):
    w_init = tf.truncated_normal_initializer(stddev=5e-2)
    w_init2 = tf.truncated_normal_initializer(stddev=0.04)
    b_init2 = tf.constant_initializer(value=0.1)
    with tf.variable_scope("vgg_net_model", reuse=reuse):
        input_layer = InputLayer(x, name="input")

        # 卷积层组 1
        conv_1_1 = Conv2d(input_layer, 64, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_1_1')
        conv_1_2 = Conv2d(conv_1_1, 64, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_1_2')
        lrn_1 = LocalResponseNormLayer(conv_1_2, depth_radius=4, bias=1.0, alpha=0.001 / 9.0, beta=0.75, name='lrn_1')

        # 池化 1
        pool_1 = MaxPool2d(lrn_1, (3, 3), (2, 2),
                           padding='SAME', name='lrn_1')

        # 卷积层组 2
        conv_2_1 = Conv2d(pool_1, 128, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_2_1')
        conv_2_2 = Conv2d(conv_2_1, 128, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_2_2')
        lrn_2 = LocalResponseNormLayer(conv_2_2, depth_radius=4, bias=1.0, alpha=0.001 / 9.0, beta=0.75, name='lrn_2')

        # 池化 2
        pool_2 = MaxPool2d(lrn_2, (3, 3), (2, 2),
                           padding='SAME', name='pool_2')

        # 卷积层组 3
        conv_3_1 = Conv2d(pool_2, 256, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_3_1')
        conv_3_2 = Conv2d(conv_3_1, 256, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_3_2')
        conv_3_3 = Conv2d(conv_3_2, 256, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_3_3')
        lrn_3 = LocalResponseNormLayer(conv_3_3, depth_radius=4, bias=1.0, alpha=0.001 / 9.0, beta=0.75, name='lrn_3')

        # 池化 3
        pool_3 = MaxPool2d(lrn_3, (3, 3), (2, 2),
                           padding='SAME', name='pool_3')

        # 卷积层组 4
        conv_4_1 = Conv2d(pool_3, 512, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_4_1')
        conv_4_2 = Conv2d(conv_4_1, 512, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_4_2')
        conv_4_3 = Conv2d(conv_4_2, 512, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_4_3')
        lrn_4 = LocalResponseNormLayer(conv_4_3, depth_radius=4, bias=1.0, alpha=0.001 / 9.0, beta=0.75, name='lrn_4')

        # 池化 4
        pool_4 = MaxPool2d(lrn_4, (3, 3), (2, 2),
                           padding='SAME', name='pool_4')

        # 卷积层组 4
        conv_5_1 = Conv2d(pool_4, 512, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_5_1')
        conv_5_2 = Conv2d(conv_5_1, 512, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_5_2')
        conv_5_3 = Conv2d(conv_5_2, 512, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_5_3')
        lrn_5 = LocalResponseNormLayer(conv_5_3, depth_radius=4, bias=1.0, alpha=0.001 / 9.0, beta=0.75, name='lrn_5')

        # 池化 5
        pool_5 = MaxPool2d(lrn_5, (3, 3), (2, 2),
                           padding='SAME', name='pool_5')

        # 全连接层
        flatten_layer = FlattenLayer(pool_5, name='flatten')

        fc1 = DenseLayer(flatten_layer, 4096, act=tf.nn.relu,
                         W_init=w_init2, b_init=b_init2, name='fc1')
        fc2 = DenseLayer(fc1, 4096, act=tf.nn.relu,
                         W_init=w_init2, b_init=b_init2, name='fc2')
        fc3 = DenseLayer(fc2, 1000, act=tf.nn.relu,
                         W_init=w_init2, b_init=b_init2, name='fc3')

        model = DenseLayer(fc3, 7, act=None, W_init=w_init2, name='output')

        y_pred = model.outputs

        ce = tl.cost.cross_entropy(y_pred, y_correct, name='COST')
        # l2 for the MLP, without this, the ACCURACY will be reduced by 15%.
        l2 = 0
        for p in tl.layers.get_variables_with_name('relu/W', True, True):
            l2 += tf.contrib.layers.l2_regularizer(0.004)(p)
        cost = ce + l2

        correct_prediction = tf.equal(tf.argmax(y_pred, 1), y_correct)
        accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

        return model, cost, accuracy


def vgg_net_model_bn(x, y_correct, reuse, is_train):
    """ Batch normalization should be placed before rectifier. """

    w_init = tf.truncated_normal_initializer(stddev=5e-2)
    w_init2 = tf.truncated_normal_initializer(stddev=0.04)
    b_init2 = tf.constant_initializer(value=0.1)

    with tf.variable_scope("vgg_net_model_fn", reuse=reuse):
        input_layer = InputLayer(x, name="input")

        # 卷积层组 1
        conv_1_1 = Conv2d(input_layer, 64, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_1_1')
        conv_1_2 = Conv2d(conv_1_1, 64, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_1_2')
        bn_1 = BatchNormLayer(conv_1_2, is_train, act=tf.nn.relu, name='bn_1')

        # 池化 1
        pool_1 = MaxPool2d(bn_1, (3, 3), (2, 2),
                           padding='SAME', name='lrn_1')

        # 卷积层组 2
        conv_2_1 = Conv2d(pool_1, 128, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_2_1')
        conv_2_2 = Conv2d(conv_2_1, 128, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_2_2')
        bn_2 = BatchNormLayer(conv_2_2, is_train, act=tf.nn.relu, name='bn_2')

        # 池化 2
        pool_2 = MaxPool2d(bn_2, (3, 3), (2, 2),
                           padding='SAME', name='pool_2')

        # 卷积层组 3
        conv_3_1 = Conv2d(pool_2, 256, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_3_1')
        conv_3_2 = Conv2d(conv_3_1, 256, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_3_2')
        conv_3_3 = Conv2d(conv_3_2, 256, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_3_3')
        bn_3 = BatchNormLayer(conv_3_3, is_train, act=tf.nn.relu, name='bn_3')

        # 池化 3
        pool_3 = MaxPool2d(bn_3, (3, 3), (2, 2),
                           padding='SAME', name='pool_3')

        # 卷积层组 4
        conv_4_1 = Conv2d(pool_3, 512, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_4_1')
        conv_4_2 = Conv2d(conv_4_1, 512, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_4_2')
        conv_4_3 = Conv2d(conv_4_2, 512, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_4_3')
        bn_4 = BatchNormLayer(conv_4_3, is_train, act=tf.nn.relu, name='bn_4')

        # 池化 4
        pool_4 = MaxPool2d(bn_4, (3, 3), (2, 2),
                           padding='SAME', name='pool_4')

        # 卷积层组 4
        conv_5_1 = Conv2d(pool_4, 512, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_5_1')
        conv_5_2 = Conv2d(conv_5_1, 512, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_5_2')
        conv_5_3 = Conv2d(conv_5_2, 512, (3, 3), (1, 1), act=tf.nn.relu,
                          padding='SAME', W_init=w_init, name='conv_5_3')
        bn_5 = BatchNormLayer(conv_5_3, is_train, act=tf.nn.relu, name='bn_5')

        # 池化 5
        pool_5 = MaxPool2d(bn_5, (3, 3), (2, 2),
                           padding='SAME', name='pool_5')

        # 全连接层
        flatten_layer = FlattenLayer(pool_5, name='flatten')

        fc1 = DenseLayer(flatten_layer, 4096, act=tf.nn.relu,
                         W_init=w_init2, b_init=b_init2, name='fc1')
        fc2 = DenseLayer(fc1, 4096, act=tf.nn.relu,
                         W_init=w_init2, b_init=b_init2, name='fc2')
        fc3 = DenseLayer(fc2, 1000, act=tf.nn.relu,
                         W_init=w_init2, b_init=b_init2, name='fc3')

        model = DenseLayer(fc3, 7, act=None, W_init=w_init2, name='output')

        y_pred = model.outputs

        ce = tl.cost.cross_entropy(y_pred, y_correct, name='_cost')
        # l2 for the MLP, without this, the ACCURACY will be reduced by 15%.
        l2 = 0
        for p in tl.layers.get_variables_with_name('relu/W', True, True):
            l2 += tf.contrib.layers.l2_regularizer(0.004)(p)
        cost = ce + l2

        correct_prediction = tf.equal(tf.argmax(y_pred, 1), y_correct)
        accurary = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))

        return model, cost, accurary


def distort_fn(x, is_train=False):
    """
    The images are processed as follows:
    .. They are cropped to 24 x 24 pixels, centrally for evaluation or randomly for training.
    .. They are approximately whitened to make the vgg_net_model insensitive to dynamic range.
    For training, we additionally apply a series of random distortions to
    artificially increase the data set size:
    .. Randomly flip the image from left to right.
    .. Randomly distort the image brightness.

    图像处理如下：
        它们被裁剪为24 x 24像素，集中用于评估或随机进行训练。
        它们可以看作新数据，使 model 对动态范围不敏感。
    对于培训，我们还应用一系列随机扭曲
    人为增加数据集大小：
        随机翻转图像从左到右。
        随机扭曲图像亮度。
    """
    # print('begin', x.shape, np.min(x), np.max(x))
    x = tl.prepro.crop(x, 24, 24, is_random=is_train)
    # print('after crop', x.shape, np.min(x), np.max(x))
    if is_train:
        # x = tl.prepro.zoom(x, zoom_range=(0.9, 1.0), is_random=True)
        # print('after zoom', x.shape, np.min(x), np.max(x))
        x = tl.prepro.flip_axis(x, axis=1, is_random=True)
        # print('after flip',x.shape, np.min(x), np.max(x))
        x = tl.prepro.brightness(x, gamma=0.1, gain=1, is_random=True)
        # print('after brightness',x.shape, np.min(x), np.max(x))
        # tmp = np.max(x)
        # x += np.random.uniform(-20, 20)
        # x /= tmp
    # normalize the image
    x = (x - np.mean(x)) / max(np.std(x), 1e-5)  # avoid values divided by 0
    # print('after norm', x.shape, np.min(x), np.max(x), np.mean(x))
    return x


# using local response normalization 使用 lrn
NETWORK, COST, _ = vgg_net_model(X, Y_CORRECT, False)
_, COST_TEST, ACCURACY = vgg_net_model(X, Y_CORRECT, True)
# you may want to try batch normalization 使用 bn
# NETWORK, COST, _ = vgg_net_model_bn(X, Y_CORRECT, False, is_train=True)
# _, COST_TEST, ACCURACY = vgg_net_model_bn(X, Y_CORRECT, True, is_train=False)


TRAIN_PARAMS = NETWORK.all_params
TRAIN_OP = tf.train.AdamOptimizer(LEARNING_RATE, beta1=0.9, beta2=0.999, epsilon=1e-08,
                                  use_locking=False).minimize(COST, var_list=TRAIN_PARAMS)
# 初始化变量
INIT = tf.global_variables_initializer()

SAVER = tf.train.Saver()


def train():
    # 加载会话
    with tf.Session() as sess:
        sess.run(INIT)
        NETWORK.print_params(False)
        NETWORK.print_layers()
        print("------------------------------")
        print("learning_rate: %f" % LEARNING_RATE)
        print("batch_size: %d" % BATCH_SIZE)
        print("EPOCH_NUM: %d" % EPOCH_NUM)

        data, labels = fer2013_input.load_data(TRAIN_DATA_SRC, "train", one_hot=False)

        epoch = 0

        while epoch < EPOCH_NUM:
            start_time = time.time()
            epoch_i = 0
            for batch_xs, batch_ys in tl.iterate.minibatches(data, labels, BATCH_SIZE, shuffle=True):
                # data augmentation for training
                # batch_xs = tl.prepro.threading_data(batch_xs, fn=distort_fn, is_train=True)
                batch_xs = np.reshape(batch_xs, (-1, 48, 48, 1))
                sess.run(TRAIN_OP, feed_dict={X: batch_xs, Y_CORRECT: batch_ys})

                if epoch_i == 127:
                    acc = sess.run(ACCURACY, feed_dict={X: batch_xs, Y_CORRECT: batch_ys})

                    loss = sess.run(COST, feed_dict={X: batch_xs, Y_CORRECT: batch_ys})
                    print("epoch {:d} of {:d} took {:.2fs}".format(epoch + 1, EPOCH_NUM, time.time() - start_time) +
                          ", Minibatch Loss= {:.6f}".format(loss) +
                          ", Training Accuracy= {:.5f}".format(acc))
                epoch_i += 1
            epoch += 1

        print("------------------------------")
        print("train finished")

        # 模型保存目录
        save_path = MODEL_SAVE_PATH

        # 创建目录
        if tf.gfile.Exists(save_path):
            tf.gfile.DeleteRecursively(save_path)
        tf.gfile.MakeDirs(save_path)

        SAVER.save(sess, save_path, epoch)
        print("save model success")


if __name__ == '__main__':
    train()
