import cv2
import sys


if __name__=="__main__":

	img = None

	try:
		img = cv2.imread('images/EOS_650D_Top_View.jpg')
	
	except:
		pass
	
	if len(sys.argv) > 1:
		try:
			print str(sys.argv[1])
			img = cv2.imread(str(sys.argv[1]))
		except:
			print "******* Could not open image file *******"
			print "Unexpected error:", sys.exc_info()[0]
			#raise		
			sys.exit(-1)
		
	dim = (640,480)
	resized_img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
	#apply canny 
	#edges = cv2.Canny(resized_img,50,150)
	imgray = cv2.cvtColor(resized_img,cv2.COLOR_BGR2GRAY)
	cv2.imshow('imgray', imgray)
	cv2.waitKey()

	ret,thresh = cv2.threshold(imgray,127,255,0)
	cv2.imshow('thresh', thresh)
	cv2.waitKey()
	contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
	cnt = contours[0]
	M = cv2.moments(cnt)
	print M
	
	#find center of object
	cx = int(M['m10']/M['m00'])
	cy = int(M['m01']/M['m00'])

	area = cv2.contourArea(cnt)
	print area
	perimeter = cv2.arcLength(cnt,True)
	print "perimeter:", perimeter
	epsilon = 0.1*cv2.arcLength(cnt,True)
	approx = cv2.approxPolyDP(cnt,epsilon,True)
	print "approx:", approx
	#print "contours:", contours
	
	cv2.drawContours(resized_img, approx, -1, (255,0,0), 2)
	#cv2.drawContours(imgray, contours, 3, (0,255,0), 3)
	#cnt = contours[4]
	#cv2.drawContours(img, [cnt], 0, (0,255,0), 3)
	
	#save image
	#cv2.imwrite('images/canny_edge.bmp',resized_img)
	while 1:
		#show the image
		cv2.imshow('image',resized_img)
		#press ESC to stop
		k = cv2.waitKey(1) & 0xFF
		if k == 27:
			break

	cv2.destroyAllWindows()
	
