# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 17:25:07 2024

@author: barna
"""


import cv2
from skimage.feature import hog

im_test = cv2.imread('Numbers\8\8.png', 0)
_,hog_img = hog(im_test,orientations=9,pixels_per_cell = (8,8),
                cells_per_block=(1, 1),visualize = True)
cv2.imshow(hog_img,cmap='gray')