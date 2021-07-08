
import os
import time
import pickle
import random
import numpy as np
import tensorflow as tf
import sys
from input import DataInput, DataInputTest
from model import Model

os.environ['CUDA_VISIBLE_DEVICES'] = '1'
random.seed(1234)
np.random.seed(1234)
tf.set_random_seed(1234)

train_batch_size = 32
test_batch_size = 512
predict_batch_size = 32
predict_users_num = 1000
predict_ads_num = 100

with open('dataset.pkl', 'rb') as f:
    train_set = pickle.load(f)
    test_set = pickle.load(f)
    cate_list = pickle.load(f)
    user_count, item_count, cate_count = pickle.load(f)

best_auc = 0.0


def calc_auc(raw_arr):
    """Summary
    Args:
        raw_arr (TYPE): Description
    Returns:
        TYPE: Description
    """
    # 根据预测的结果正排
    arr = sorted(raw_arr, key=lambda d: d[2])

    auc = 0.0
    fp1, tp1, fp2, tp2 = 0.0, 0.0, 0.0, 0.0
    for record in arr:
        fp2 += record[0]  # 没有点击
        tp2 += record[1]  # 点击了
        auc += (fp2 - fp1) * (tp2 + tp1)
        fp1, tp1 = fp2, tp2

    # if all nonclick or click, disgard
    threshold = len(arr) - 1e-3
    if tp2 > threshold or fp2 > threshold:
        return -0.5

    if tp2 * fp2 > 0.0:  # normal auc
        return (1.0 - auc / (2.0 * tp2 * fp2))
    else:
        return None


def _auc_arr(score):
    # 把score变数组形式
    score_p = score[:, 0]
    score_n = score[:, 1]
    # print "============== p ============="
    # print score_p
    # print "============== n ============="
    # print score_n
    score_arr = []
    for s in score_p.tolist():
        score_arr.append([0, 1, s])
    for s in score_n.tolist():
        score_arr.append([1, 0, s])
    return score_arr


def _eval(sess, model):
    # 评估模型
    auc_sum = 0.0
    score_arr = []
    for _, uij in DataInputTest(test_set, test_batch_size):  # 载入数据
        auc_, score_ = model.eval(sess, uij)  # 得到分数
        score_arr += _auc_arr(score_)
        auc_sum += auc_ * len(uij[0])  # 计算auc
    test_gauc = auc_sum / len(test_set)
    Auc = calc_auc(score_arr)
    global best_auc
    if best_auc < test_gauc:
        best_auc = test_gauc  # 记录最好的auc
        model.save(sess, 'save_path/ckpt')
    return test_gauc, Auc


def _test(sess, model):
    # 测试模型
    auc_sum = 0.0
    score_arr = []
    predicted_users_num = 0
    print("test sub items")
    for _, uij in DataInputTest(test_set, predict_batch_size):  # 载入数据
        if predicted_users_num >= predict_users_num:
            break
        score_ = model.test(sess, uij)  # 得到预测分数
        score_arr.append(score_)
        predicted_users_num += predict_batch_size
    return score_[0]


gpu_options = tf.GPUOptions(allow_growth=True)  # gpu


# gpu_options=gpu_options
# device_count = {'GPU': 0}

with tf.Session(config=tf.ConfigProto(device_count={'GPU': 0})) as sess:

    model = Model(user_count, item_count, cate_count, cate_list,
                  predict_batch_size, predict_ads_num)
    sess.run(tf.global_variables_initializer())
    sess.run(tf.local_variables_initializer())  # 实例化模型

    print('test_gauc: %.4f\t test_auc: %.4f' % _eval(sess, model))
    sys.stdout.flush()
    lr = 1.0
    start_time = time.time()
    for _ in range(50):

        random.shuffle(train_set)  # 打乱数据集

        epoch_size = round(len(train_set) / train_batch_size)
        loss_sum = 0.0
        for _, uij in DataInput(train_set, train_batch_size):
            loss = model.train(sess, uij, lr)  # 开始训练
            loss_sum += loss

            if model.global_step.eval() % 1000 == 0:  # 打印过程
                test_gauc, Auc = _eval(sess, model)
                print('Epoch %d Global_step %d\tTrain_loss: %.4f\tEval_GAUC: %.4f\tEval_AUC: %.4f' %
                      (model.global_epoch_step.eval(), model.global_step.eval(),
                       loss_sum / 1000, test_gauc, Auc))
                sys.stdout.flush()  # stdout刷新
                loss_sum = 0.0

            if model.global_step.eval() % 336000 == 0:
                lr = 0.1

        print('Epoch %d DONE\tCost time: %.2f' %
              (model.global_epoch_step.eval(), time.time()-start_time))
        sys.stdout.flush()
        model.global_epoch_step_op.eval()

    print('best test_gauc:', best_auc)
    sys.stdout.flush()