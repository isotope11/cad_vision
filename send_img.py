#!/usr/bin/env python
__version__ = '.01'
__author__ = 'Laird Foret (laird@isotope11.com)'
__copyright__ = '(C) 2015. GNU GPL 3.'

"""
Send image over TCP on specified port.
exmaple: python send_img.py images/camera.bmp

"""
# USAGE: python FileSender.py [file]

import sys, socket, cv2

HOST = socket.gethostname() 
PORT = 12345
FILE = sys.argv[1]


def send_image(IP, PORT, DATA):

	data_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	try:
		data_tcp.connect((IP, PORT))
		print >> sys.stderr, "send_image: connected to receiver..."
		#send data
		data_tcp.send(DATA)
		#close port
		data_tcp.close()
		print >> sys.stderr, "send_image: successfully sent data."
		print >> sys.stderr, "send_image: sent ", len(DATA), "bytes"
	except:
		print >> sys.stderr, "send_image: couldn't connect to receiver..."	
	#print >> sys.stderr, type(DATA) 

	
if __name__ == '__main__':

	IP = socket.gethostname() #this computer
	PORT = 12345
	FILENAME = 'images/camera.bmp'

	if len(sys.argv) > 1:
		try:
			FILENAME = str(sys.argv[1])
			FILE = open(FILENAME, "rb")
			image = FILE.read()
			FILE.close()
		except:
			print "******* Could not open image file *******"
			print "Unexpected error:", sys.exc_info()[0]
			#raise		
			sys.exit(-1)	
	else:
		FILE = open(FILENAME, "rb")
		image = FILE.read()
		FILE.close()
	send_image(IP, PORT, image)	

