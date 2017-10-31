import os
from os.path import abspath, basename
import numpy as np
import scipy.fftpack
import cv2
from dlib import simple_object_detector

# 検出に必要なファイル
face_detector = simple_object_detector(abspath(__file__).replace(basename(__file__),"detector_face.svm"))
eye_detector = simple_object_detector(abspath(__file__).replace(basename(__file__),"detector_eye.svm"))

def face_2d(temp_file, userid, filename):
    # 最終検出結果
    get = False
    # 顔の位置
    facex = []
    facey = []
    facew = []
    faceh = []
    # 画像をメモリー上にデコード
    img = cv2.imdecode(np.asarray(bytearray(temp_file), dtype=np.uint8), 1)
    # 画像サイズを半分に縮小(処理時間短縮)
    orgWidth, orgHeight = img.shape[:2]
    size = (int(orgHeight/2), int(orgWidth/2))
    image = cv2.resize(img, size)
    # 画像から顔を検出
    try:
        faces = face_detector(image)
    except:
        faces = 0
    # 二次元の顔が検出できた場合
    if len(faces) > 0:
        # 顔だけ切り出して目の検索
        for i, area in enumerate(faces):
            # 最小サイズの指定
            if area.bottom()-area.top() < image.shape[0]*-1 or area.right()-area.left() < image.shape[1]*-1:
                continue
            face = image[area.top():area.bottom(), area.left():area.right()]
            # 出来た画像から目を検出
            eyes = eye_detector(face)
            if len(eyes) > 0:
                facex.append(area.left()*2)
                facey.append(area.top()*2)
                facew.append((area.right()-area.left())*2)
                faceh.append((area.bottom()-area.top())*2)
                get = True
    if get:
        return (phash_calc(image), facex, facey, facew, faceh)
    else:
        return (None, facex, facey, facew, faceh)

def phash_calc(image, hash_size=32):
    check_image = cv2.resize(image, (hash_size, hash_size))
    check_image = cv2.cvtColor(check_image, cv2.COLOR_RGB2GRAY)
    dct = scipy.fftpack.dct(check_image)
    dctlowfreq = dct[:8, 1:9]
    avg = dctlowfreq.mean()
    diff = dctlowfreq > avg
    value_str = ""
    for value in [flatten for inner in diff for flatten in inner]:
        value_str += '1' if value else '0'
    return value_str

def dhash_calc(image, hash_size = 7):
    check_image = cv2.resize(image,(hash_size,hash_size+1))
    check_image = cv2.cvtColor(check_image, cv2.COLOR_RGB2GRAY)
    # Compare adjacent pixels.
    difference = []
    for row in range(hash_size):
        for col in range(hash_size):
            pixel_left = check_image[col, row]
            pixel_right = check_image[col + 1, row]
            difference.append(pixel_left > pixel_right)
    # Convert the binary array to a hexadecimal string.
    decimal_value = 0
    hex_string = []
    for index, value in enumerate(difference):
        if value:
            decimal_value += 2**(index % 8)
        if (index % 8) == 7:
            hex_string.append(hex(decimal_value)[2:].rjust(2, '0'))
            decimal_value = 0
    return ''.join(hex_string)
