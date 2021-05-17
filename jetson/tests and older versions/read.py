import time
import socket



sock = socket.socket()
sock.connect(('192.168.250.90', 5693))
print ("connected")

while True:
	f = open("zalu.txt", "rt")
	n = int (f.readline())
	
	t = 0
	while t<n:
		t = t+1
		id = int (f.readline()) 
		var = float (f.readline())
		area = float (f.readline())
		x = float (f.readline())
		y = float (f.readline())
		#print (id,var,area,x,y)
		if (id == 1) & (var>=0.7) & (area > 304278) & (x > 600) & (x < 1000):
			print ("detected")
			strin = "rosservice call /script/start \"name: 'dance'\""
			sock.send(strin.encode())
			data = sock.recv(1024)
			print ("\nsended: ",data.decode())


			
				
	f.close()
	print("\n")
	time.sleep(1)
sock.close()
