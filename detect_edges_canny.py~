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
	edges = cv2.Canny(resized_img,50,150)
	#save image
	cv2.imwrite('images/canny_edge.bmp',resized_img)
	while 1:
		#show the image
		cv2.imshow('image',edges)
		#press ESC to stop
		k = cv2.waitKey(1) & 0xFF
		if k == 27:
			break

	cv2.destroyAllWindows()
	
