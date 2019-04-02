from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import (QPushButton, QMainWindow, QWidget, QHBoxLayout, QTextEdit,
                             QLabel, QApplication, QLineEdit, QGridLayout, QSlider, QFileDialog)
from PyQt5.QtCore import pyqtSlot, QFileInfo, Qt
from PyQt5.QtGui import QIcon, QPixmap, QImage

import os
import cv2
import numpy as np

import sys

"""
lineEdit :
    linepath 
Buttom :
    open
    hdr
    tiltshift_x
    tiltshift_y
Ruler :
    ruler
QWidget:
    hinh1
    hinh2 

cach su dung co vi du ben duoi 

"""


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()

        ui = uic.loadUi('mainwindow.ui', self)

        li = ui.open.clicked.connect(self.pushOpen)
        hdr_button = ui.hdr.clicked.connect(self.hdr_process)
        blur_button_x = ui. tiltshift_x.clicked.connect(self.tiltshift_x_click)
        blur_button_y = ui.tiltshift_y.clicked.connect(self.tiltshift_y_click)
        ui.ruler.setMinimum(3)
        ui.ruler.setMaximum(21)
        ui.ruler.setValue(7)
        ui.ruler.setSingleStep(2)
        ui.ruler.setTickPosition(QSlider.TicksBelow)
        ui.ruler.setTickInterval(10)

        self.kernel = ui.ruler.value()

        self.widget_1 = ui.hinh1
        self.label = QLabel(self.widget_1)

        self.widget_2 = ui.hinh2
        self.label_2 = QLabel(self.widget_2)

        img = QImage('default.jpg')
        pixmap = QPixmap.fromImage(img)
        self.label.setPixmap(pixmap)
        self.label_2.setPixmap(pixmap)
        self.show()

    def pushOpen(self):
        # print ("asfasdfsadfasd")
        fname = QFileDialog.getOpenFileName(self, 'Open file', '/home/')
        d = QFileInfo(str(fname)).absoluteDir()
        self.absolute = d.absolutePath()
        text = str(self.absolute).split('\'')[1]
        self.linepath.setText(text)
        # fname.show()

    def tiltshift_x_click(self):
        # print(self.linepath.text())

        self.blurer(0, str(self.linepath.text()))

    def tiltshift_y_click(self):
        # blurer(1)
        self.blurer(1, str(self.linepath.text()))

    def getvalue(self, path):

        li = list()
        images = list()
        times = 0
        with open(os.path.join(path, 'list.txt')) as f:
            content = f.readlines()
        get_img = str(content[0]).split()[0]
        #
        print(get_img)
        ev = float()
        hinhLayMucXam = cv2.imread(os.path.join(path, get_img), 0)
        hinhLayMucXam = np.array(hinhLayMucXam)
        print(hinhLayMucXam.shape)
        mucXamtb = np.average(hinhLayMucXam)
        if (mucXamtb >= 0 and mucXamtb < 10):
            ev = 0.03125
        if (mucXamtb >= 10 and mucXamtb < 20):
            ev = 0.0625
        if (mucXamtb >= 20 and mucXamtb < 30):
            ev = 0.125
        if (mucXamtb >= 30 and mucXamtb < 40):
            ev = 0.25
        if (mucXamtb >= 40 and mucXamtb < 50):
            ev = 0.5
        if (mucXamtb >= 50 and mucXamtb < 60):
            ev = 1.0
        if (mucXamtb >= 60 and mucXamtb < 70):
            ev = 2.0
        if (mucXamtb >= 70 and mucXamtb < 80):
            ev = 4.0
        if (mucXamtb >= 80 and mucXamtb < 90):
            ev = 8.0
        if (mucXamtb >= 90 and mucXamtb < 100):
            ev = 16.0
        if (mucXamtb >= 100 and mucXamtb < 110):
            ev = 32.0
        if (mucXamtb >= 110 and mucXamtb < 120):
            ev = 64.0

        for line in content:
            # global times
            tokens = line.split()
            images.append(cv2.imread(os.path.join(path, tokens[0])))
            times = times+1
            li.append(ev)
            ev = ev*2
        li = np.array(li, dtype=np.float32)
        return images, li

    def hdr_process(self):
        images, times = self.getvalue(str(self.linepath.text()))
        # [Load images and exposure times]
        print(['scaca'], times)
        # [Estimate camera response] cau hinh tham so camera
        calibrate = cv2.createCalibrateDebevec()
        response = calibrate.process(images, times)
        # [Estimate camera response]

        # [Make HDR image]
        merge_debevec = cv2.createMergeDebevec()
        hdr = merge_debevec.process(images, times, response)
        # [Make HDR image]
        cv2.imwrite('hdr.png', hdr * 255)  # hdr

        (w, h, _) = hdr.shape
        img = QImage('hdr.png')
        pixmap = QPixmap.fromImage(img)
        self.label.setPixmap(pixmap)
        self.widget_1.setGeometry(0, 0, 500, 500)
        cv2.imshow('hdr', hdr)
        cv2.waitKey(0)
        self.widget_1.show()

    def blurer(self, typer, path):
        img = cv2.imread(path)
        cv2.waitKey(1)
        if (POSITION['start'] == (0, 0) or POSITION['end'] == (0, 0)):
            pass
        else:
            print(path)
            img = cv2.imread(path)

            imgB = img.copy()

            if (typer == 0):
                imgR = img[int(POSITION['start'][1])                           :int(POSITION['end'][1]), :]
                imgB = cv2.GaussianBlur(imgB, (self.kernel, self.kernel), 0)
                imgB[int(POSITION['start'][1]):int(
                    POSITION['end'][1]), :] = imgR
            if (typer == 1):
                imgR = img[:, int(POSITION['start'][0])                           :int(POSITION['end'][0])]
                imgB = cv2.GaussianBlur(imgB, (self.kernel, self.kernel), 0)
                imgB[:, int(POSITION['start'][0]):int(
                    POSITION['end'][0])] = imgR

                print("B: ", imgB[:, int(POSITION['start'][0]):int(
                    POSITION['end'][0])].shape, " R: ", imgR.shape)
            cv2.imwrite("tift.png", imgB)

            img = QImage("tift.png")
            pixmap = QPixmap.fromImage(img)

            img2 = QImage(path)
            pixmap2 = QPixmap.fromImage(img2)

            self.label.setPixmap(pixmap2)
            self.label_2.setPixmap(pixmap)

        cv2.imshow("test", img)
        cv2.waitKey(1)


# mac dinh
POSITION = {'start': (0, 0), 'end': (0, 0)}

# counter
i = 0
# nhan chuot


def mouse_drawing(event, x, y, flags, params):
    global i
    if event == cv2.EVENT_LBUTTONDOWN:
        if i % 2 == 0:
            POSITION['start'] = (x, y)
        else:
            POSITION['end'] = (x, y)
        i = i + 1
        print(POSITION)

        # cv2.imshow("test",img)
        cv2.waitKey(1)


# HDR process image
def loadExposureSeq(path):
    images = []
    times = []
    with open(os.path.join(path, 'list.txt')) as f:
        content = f.readlines()
    for line in content:
        tokens = line.split()
        images.append(cv2.imread(os.path.join(path, tokens[0])))
        times.append(1 / float(tokens[1]))

    return images, np.asarray(times, dtype=np.float32)


if __name__ == '__main__':
    cv2.namedWindow("test")
    cv2.setMouseCallback("test", mouse_drawing)
    # img = cv2.imread("/home/trungbanh/Downloads/web.png")
    # cv2.imshow("test",img)
    # cv2.waitKey(0)
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())
