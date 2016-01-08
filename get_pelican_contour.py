#!/usr/bin/env python
__version__ = '01072016'
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
import uuid


def auto_canny(image, sigma=0.33):
        # compute the median of the single channel pixel intensities
        v = np.median(image)
        # apply automatic Canny edge detection using the computed median
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))
        edged = cv2.Canny(image, lower, upper)
        # return the edged image
        return edged


#def get_contour(Img_PathandFilename = 'temp_image_file', resize_dim=(640,480) ):
def get_contour(Img_PathandFilename = 'temp_image_file', opaque="--opaque", fill="000000", img_format="-s", width="10", height="10", output="object_contour.svg", resize_dim=(640,480)):

                #returns SVG of contour of object of a given image
                try:
                        img = cv2.imread(Img_PathandFilename)
                except:
                        print >> sys.stderr, "******* Could not open image file *******"
                        print >> sys.stderr, "Unexpected error:", sys.exc_info()[0]             
                        sys.exit(-1)    

                #resize image
                resized_img = cv2.resize(img, resize_dim, interpolation = cv2.INTER_AREA)
                print >> sys.stderr, "[get_pelican_contour] resized image to:", resize_dim
                #apply canny
                edges = cv2.cvtColor(resized_img, cv2.COLOR_BGR2GRAY)
                #edges = auto_canny(edges)
                #edges  = cv2.GaussianBlur(edges, (3,3), 0)
                edges = cv2.Canny(edges,30,180)
                #ret,edges = cv2.threshold(edges, 127,255,cv2.THRESH_BINARY)
                #edges  = cv2.GaussianBlur(edges, (5,5), 0)
                 
                #despeckle image
                kernel = np.ones((5,5),np.uint8)
                #this line below is how "fat" or loose the object will fit in the foam
                edges = cv2.dilate(edges,kernel,iterations = 3)
                edges = cv2.erode(edges,kernel,iterations = 1)
 
                #BLUR THE IMAGE a bit
                #blurr = (3,3)
                #edges = cv2.blur(edges,blurr)
                #cv2.imwrite('blurred_image.jpg', edges)
                #print >> sys.stderr, "[ImageReceiver] blurred image:", blurr
                
                #find contours
                contours, hierarchy = cv2.findContours(edges,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
                print >> sys.stderr, "[get_pelican_contour] Contours found:", len(contours)
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
                
                #part of rescaling to make object touch edges of outputted SVG
                contour_size = cv2.minAreaRect(item_contour) 
                #print >> sys.stderr, "[get_pelican_contour] Contour size",  contour_size
                center_of_contour = [int(contour_size[0][0]),int(contour_size[0][1])]
                print >> sys.stderr, "[get_pelican_contour] Largest contour center",  center_of_contour
                contour_width = int(contour_size[1][0] )
                contour_height = int(contour_size[1][1] )
                print >> sys.stderr,"[get_pelican_contour] Largest contour_width", contour_width
                print >> sys.stderr,"[get_pelican_contour] Largest contour_height:", contour_height
                scaling_factor = 1.0
                if contour_width > contour_height: 
                	print >> sys.stderr, "[get_pelican_contour] Using contour_width to set scaling"
                	scaling_factor = scaling_factor + (1.0-(contour_width / resize_dim[0]))
                else: 
                	print >> sys.stderr, "[get_pelican_contour] Using contour_height to set scaling"
                	scaling_factor = scaling_factor + (1.0-(contour_height / resize_dim[1]))
                print >> sys.stderr, "[get_pelican_contour] scaling_factor", scaling_factor
                
                #create a blank image
                #contour_image = np.zeros((resize_dim[1], resize_dim[0], 3), np.uint8)
                #part of rescaling to make object touch edges of outputted SVG
                contour_image = np.zeros(((resize_dim[1]*scaling_factor), scaling_factor*resize_dim[0], 3), np.uint8)
     
                #scaling_factor = 1.0
                resized_contour = scaling_factor*np.array(item_contour)
                resized_contour = resized_contour.astype(int)
                #print item_contour[0], resized_contour[0]
                cv2.drawContours(contour_image, [resized_contour], -1, (255, 255, 255), -1)
                
                leftmost = tuple(resized_contour[resized_contour[:,:,0].argmin()][0])
                rightmost = tuple(resized_contour[resized_contour[:,:,0].argmax()][0])
                topmost = tuple(resized_contour[resized_contour[:,:,1].argmin()][0])
                bottommost = tuple(resized_contour[resized_contour[:,:,1].argmax()][0])
                #print "leftmost", leftmost
                #print "rightmost", rightmost
                #print "topmost", topmost
                #print "bottommost", bottommost
                
                #crop image to make object touch edges
             	cropped_contour_image = contour_image[topmost[1]:bottommost[1], leftmost[0]:rightmost[0]]
             	#print "cropped_contour_image size = ",cropped_contour_image.shape
                
                #Smooth rough edges
                #line below really seems to help
                #cropped_contour_image = cv2.GaussianBlur(cropped_contour_image, (5,5), 0)
                cropped_contour_image = cv2.dilate(cropped_contour_image,kernel,iterations = 2)
                cropped_contour_image = cv2.erode(cropped_contour_image,kernel,iterations = 1)
                
                #invert image
                cropped_contour_image = np.invert(cropped_contour_image)
                
                #for now just save contour image
                contour_image_filename = str(uuid.uuid1())+'.bmp'
                cv2.imwrite(contour_image_filename, cropped_contour_image )
                print >> sys.stderr, "[get_pelican_contour] saved contour image:", contour_image_filename
                    
                #call potrace to convert to SVG
                command_string = "potrace "+opaque+" --fillcolor '#"+fill+"' "+img_format+" -k 0.1 --width "+width+" --height "+height+" "+contour_image_filename+" -o "+output
                print command_string
                os.system(command_string)
                
                #SVG_to_return = cv2.imread('object_contour.svg')
                #SVG_to_return = cv2.imread(output)
				
				#remove temp image file
                command = 'rm ' + contour_image_filename
                os.system(command)
                
                #contours_to_return = np.reshape(item_contour, (640,2))
                #contours_to_return = item_contour
                #return SVG_to_return


get_contour(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
#if __name__=="__main__":
#       if len(sys.argv) > 1:
#       	get_contour(sys.argv[1])
#       else:
#       	print >> sys.stderr, "Usage: python get_contour.py 'path/imagefile_to_process'"
#       	sys.exit(-1)  
#



