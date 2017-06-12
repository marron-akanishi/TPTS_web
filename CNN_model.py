from chainer import cuda, Function, FunctionSet, gradient_check, Variable, optimizers, serializers
from chainer.training import extensions
import chainer.functions as F

class CNN():
    def __init__(self):
        self.model = FunctionSet(
            conv1 = F.Convolution2D(3,32,3,pad=1),
            conv2 = F.Convolution2D(32,64,3,pad=1),
            conv3 = F.Convolution2D(64,64,3,pad=1),
            conv4 = F.Convolution2D(64,64,3,pad=1),
            conv5 = F.Convolution2D(64,32,3,pad=1),
            conv6 = F.Convolution2D(32,32,3,pad=1),
            # conv7 = F.Convolution2D(16,16,3,pad=1),
            # conv8 = F.Convolution2D(16,16,3,pad=1),
            l1 = F.Linear(512,256),#1つ目の値は計算方法があるが適当でもChainerが実行時に正しい値を教えてくれる
            l3 = F.Linear(256,3),
        ).to_cpu()
            

    def forward(self, x_data, y_data, train=True):
        x, t = Variable(x_data), Variable(y_data)
        h = F.relu(self.model.conv1(x))
        h = F.max_pooling_2d(F.relu(self.model.conv2(h)), 2)
        h = F.relu(self.model.conv3(h))
        h = F.max_pooling_2d(F.relu(self.model.conv4(h)), 2)
        h = F.relu(self.model.conv5(h))
        h = F.max_pooling_2d(F.relu(self.model.conv6(h)), 2)
        # h = F.relu(self.model.conv7(h))
        # h = F.max_pooling_2d(F.relu(self.model.conv8(h)), 2)
        h = F.dropout(F.relu(self.model.l1(h)), train=train)
        #h = F.dropout(F.relu(self.model.l2(h)), train=train)
        y = self.model.l3(h)

        if train:   # 学習時
            return F.softmax_cross_entropy(y, t)
        else:
            return y       # 評価時