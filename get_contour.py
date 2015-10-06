#!/usr/bin/env python
__version__ = '.01'
__author__ = 'Laird Foret (laird@isotope11.com)'
__copyright__ = '(C) 2015. GNU GPL 3.'

"""
#returns SVG of contour of object of a given image
"""

import cv2
import sys
import numpy as np
import time
import imghdr
import os
import colorsys


def auto_canny(image, sigma=0.33):
        # compute the median of the single channel pixel intensities
        v = np.median(image)
        # apply automatic Canny edge detection using the computed median
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        edged = cv2.Canny(image, lower, upper)
        # return the edged image
        return edged


def get_contour(Img_PathandFilename = 'temp_image_file', resize_dim=(640,480) ):
                #returns SVG of contour of object of a given image
                try:
                        img = cv2.imread(Img_PathandFilename)
                except:
                        print >> sys.stderr, "******* Could not open image file *******"
                        print >> sys.stderr, "Unexpected error:", sys.exc_info()[0]             
                        sys.exit(-1)    
                
                #resize image
                resized_img = cv2.resize(img, resize_dim, interpolation = cv2.INTER_AREA)
                print >> sys.stderr, "[ImageReceiver] resized image to:", resize_dim
                #apply canny
                edges = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
                #edges = auto_canny(edges)
                edges = cv2.Canny(edges,30,190)
                #ret,edges = cv2.threshold(edges, 127,255,cv2.THRESH_BINARY)
                
                #despeckle image
                kernel = np.ones((5,5),np.uint8)
                edges = cv2.dilate(edges,kernel,iterations = 2)
                #edges= cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
                edges = cv2.erode(edges,kernel,iterations = 1)
                #edges = cv2.adaptiveThreshold(edges, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,                                      cv2.THRESH_BINARY_INV, 11, 1)
                #BLUR THE IMAGE a bit
                #blurr = (3,3)
                #edges = cv2.blur(edges,blurr)
                #cv2.imwrite('blurred_image.jpg', edges)
                #print >> sys.stderr, "[ImageReceiver] blurred image:", blurr
                
                #find contours
                contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                print >> sys.stderr, "[ImageReceiver] Contours found:", len(contours)
                #import inspect
                #print >> sys.stderr, (inspect.getsourcefile(enumerate))
                #get areas of contours and sort them from greatest to smallest
                areaArray= []
                for i, c in enumerate(contours):
                        area = cv2.contourArea(c)
                        areaArray.append(area)
                #first sort the array by area
                sorted_areas = sorted(zip(areaArray, contours), key=lambda x: x[0], reverse=True)

                #find the nth largest contour [n-1][1], in this case 2
                #in this case return largest
                item_contour = sorted_areas[0][1]
                
                #create a blank image
                contour_image = np.zeros((resize_dim[1], resize_dim[0], 3), np.uint8)
                #draw contour on blank image
                cv2.drawContours(contour_image, [item_contour], -1, (0, 0, 255), 2)

                #for now just save contour image
                cv2.imwrite('contour_image.bmp', contour_image)
                
                #call potrace to convert to SVG
                os.system('potrace --svg -k 0.1 contour_image.bmp -o object_contour.svg')
                print >> sys.stderr, "[ImageReceiver] saved contour image: 'contour_image.bmp'"
                SVG_to_return = cv2.imread('object_contour.svg')
                
                #contours_to_return = np.reshape(item_contour, (640,2))
                contours_to_return = item_contour
                return SVG_to_return

get_contour(sys.argv[1])

'''Code below not used
def rgb2hsv(rgb):
    return scale_hsv( colorsys.rgb_to_hsv(norm(rgb[0]), norm(rgb[1]), norm(rgb[2])) )

def norm( x):
        return (x/255.0)

def scale_hsv( hsv):
        return ([(hsv[0]*180),(hsv[1]*255),(hsv[2]*255)])


def remove_background(img, roi_size, bg_percent):
                #get samples from the 4 corners of the picture
                #this will be assumed to be background colors.
                #taking the average of this color, remove all similar (within percentage) color from picture
                if roi_size == None: roi_size = 25
                if bg_percent == None: bg_percent = 0.05
                topl = img[ 0:roi_size, 0:roi_size ]
                topr = img[0:roi_size , (img.shape[1]-roi_size ):img.shape[1]]
                bottom_l = img[(img.shape[0]-roi_size ):img.shape[0], 0:roi_size ]
                bottom_r = img[(img.shape[0]-roi_size ):img.shape[0], (img.shape[1]-roi_size ):img.shape[1]]

                #get avg color
                avg_bg_color_RGB = np.mean(np.array([cv2.mean(topl), cv2.mean(topr), cv2.mean(bottom_l), cv2.mean(bottom_r)]).astype(int), axis=0)
                #avg_bg_color = np.rint([avg_bg_color[0],  avg_bg_color[1],  avg_bg_color[2]] 
                R_lower = int(avg_bg_color_RGB[0] - (avg_bg_color_RGB[0] * bg_percent))
                if R_lower < 0: R_lower = 0
                R_upper = int(avg_bg_color_RGB[0] + (avg_bg_color_RGB[0] * bg_percent))
                if R_upper >255: R_upper = 255
                G_lower = int(avg_bg_color_RGB[1] - (avg_bg_color_RGB[1] * bg_percent))
                if G_lower < 0: G_lower = 0
                G_upper = int(avg_bg_color_RGB[1] + (avg_bg_color_RGB[1] * bg_percent))
                if G_upper >255: G_upper = 255
                B_lower = int(avg_bg_color_RGB[2] - (avg_bg_color_RGB[2] * bg_percent))
                if B_lower < 0: B_lower = 0
                B_upper = int(avg_bg_color_RGB[2] + (avg_bg_color_RGB[2] * bg_percent))
                if B_upper >255: B_upper = 255
                
                lower_RGB = np.array([R_lower, G_lower, B_lower]) 
                upper_RGB = np.array([R_upper, G_upper, B_upper])
                lower_HSV = np.array(rgb2hsv([R_lower, G_lower, B_lower])) 
                upper_HSV = np.array(rgb2hsv([R_upper, G_upper, B_upper]))
                #lower_HSV = np.array([20,0,0])
                upper_HSV = np.array([180,255,255])
                img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
                                
                # lower mask
                mask0 = cv2.inRange(img, lower_RGB, upper_RGB)
                
                print >> sys.stderr, "avg_bg_color_RGB:", avg_bg_color_RGB
                print >> sys.stderr, 'RGB_lower:', R_lower, G_lower, B_lower 
                print >> sys.stderr, 'RGB_upper:', R_upper, G_upper, B_upper 
                print >> sys.stderr, 'lower_HSV:', lower_HSV
                print >> sys.stderr, 'upper_HSV:', upper_HSV
                print >> sys.stderr, 'mask0:', mask0.shape
                
                # upper mask (170-180)
                #lower_red = np.array([170,50,50])
                #upper_red = np.array([180,255,255])
                #mask1 = cv2.inRange(img_hsv, lower_red, upper_red)

                # set my output img to zero everywhere except my mask
                #output_img = img.copy()
                #output_img[np.where(mask==0)] = 0

                # or your HSV image, which I *believe* is what you want
                output_hsv = img.copy()
                output_hsv[np.where(mask0==0)] = 0
                #output_hsv = cv2.bitwise_and(img,img, mask= mask0)
                output_rgb = cv2.cvtColor(output_hsv, cv2.COLOR_HSV2RGB)
                
                cv2.imwrite('background_mask.jpg', mask0)
                cv2.imwrite('background_removed.jpg', output_hsv)
                cv2.imwrite('image_HSV.jpg', img_hsv)
                # convert to hsv and find range of colors
                #hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
                
'''

