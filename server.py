
import socket,cv2,pickle,struct,imutils,threading,smtplib,getpass
from email.mime.text import MIMEText
# Socket Creation
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

host_ip = ''
port = 1234

# Socket Bind
s.bind((host_ip,port))
# Socket Listen
s.listen()

connected_clients={}
vid=cv2.VideoCapture(0)

hostname = socket.gethostname()   
IPAddr = socket.gethostbyname(hostname)

print("Welcome To AI Powered Video Chat Application\n")

mode=input("Do you want to unable AI Mode (y/n) ? : ")
if(mode=="y"):
	alert_mode=input("Do you want alert notification on detecting mutliple faces on client side (y/n) ? : ")
	if(alert_mode=="y"):
		# creates SMTP session
		smtp = smtplib.SMTP('smtp.gmail.com', 587)
		# start TLS for security
		smtp.starttls()
		sender_email_id=input("Enter sender's email ID for notification : ")
		sender_email_id_password=getpass.getpass()
		receiver_email_id=input("Enter reciever's email for notification : ")
		

print("\nLISTENING ON HOST:{} AND PORT:{}\n".format(IPAddr,port))
print("Waiting for Clients to connect.....")

def alert_mail(name, addr, face_len):
	smtp.login(sender_email_id, sender_email_id_password)
	content="ALERT: {} with address {} is looking suspicious, {} faces detected".format(name,addr[0],face_len)
	msg = MIMEText(content)
	msg['Subject'] = 'Alert Notification'
	msg['From'] = sender_email_id
	msg['To'] = receiver_email_id
	smtp.sendmail(sender_email_id, receiver_email_id, msg.as_string())
	smtp.quit()

def send_vid(conn, addr):
	model=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
	while True:
		img,frame = vid.read()
		if(mode=="y"):
			faces = model.detectMultiScale(frame)
			if len(faces) == 0:
				pass
			else:
				x1 = faces[0][0]
				y1 = faces[0][1]
				x2 = x1 + faces[0][2]
				y2 = y1 + faces[0][3]
				new_frame = cv2.rectangle(frame, (x1,y1), (x2,y2), [0,255,0], 5)
				frame = imutils.resize(frame,width=360)
				a = pickle.dumps(frame)
				message = struct.pack("Q",len(a))+a
				conn.sendall(message)
				cv2.imshow("You",new_frame)
				key = cv2.waitKey(1) & 0xFF
				if key ==ord('q'):
					conn.close()
		elif(mode=="n"):
			img,frame = vid.read()
			frame = imutils.resize(frame,width=360)
			a = pickle.dumps(frame)
			message = struct.pack("Q",len(a))+a
			conn.sendall(message)
			cv2.imshow("You",frame)
			key = cv2.waitKey(1) & 0xFF
			if key ==ord('q'):
				conn.close()
		else:
			print("Invalid Input........Program Terminated!!!")
			exit()
	cv2.destroyAllWindows()

def recv_vid(conn, addr):
	model=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
	data = b""
	payload_size = struct.calcsize("Q")
	# extract client name from dictionary
	key_list = list(connected_clients.keys())
	val_list = list(connected_clients.values())
	position = val_list.index([conn,addr])
	name = key_list[position]
	while True:
		while len(data) < payload_size:
			packet = conn.recv(4*1024) # 4K
			if not packet: break
			data+=packet
		packed_msg_size = data[:payload_size]
		data = data[payload_size:]
		msg_size = struct.unpack("Q",packed_msg_size)[0]
		
		while len(data) < msg_size:
			data += conn.recv(4*1024)
		frame_data = data[:msg_size]
		data  = data[msg_size:]
		frame = pickle.loads(frame_data)
		#face detection
		if(mode=="y"):
			faces = model.detectMultiScale(frame)
			if len(faces) == 0:
				pass
			else:
				fl=len(faces)
				if(alert_mode=="y" and fl>=2):
					print("ALERT: {} with address {} is looking suspicious, {} faces detected".format(name,addr[0],fl))
					print("\n Kicked {} {}".format(name,addr[0]))
					alert_mail(name,addr,fl)
					#cv2.destroyAllWindows()
					break
				x1 = faces[0][0]
				y1 = faces[0][1]
				x2 = x1 + faces[0][2]
				y2 = y1 + faces[0][3]
				new_frame = cv2.rectangle(frame, (x1,y1), (x2,y2), [0,255,0], 5)
				cv2.imshow(name,new_frame)
				key = cv2.waitKey(1) & 0xFF
				if key  == ord('q'):
					break
		elif (mode=="n"):
			cv2.imshow(name,frame)
			key = cv2.waitKey(1) & 0xFF
			if key  == ord('q'):
				break
		else:
			exit()
	cv2.destroyAllWindows()

def user(conn, addr):
	tr = threading.Thread(target=recv_vid, args=(conn, addr))
	tr.start()
	send_vid(conn, addr)

i=1
while True:
	# Socket Accept
	conn, addr = s.accept()
	print("\n")
	print('Client with IP {} has connected and named as Client {}'.format(addr[0],i))
	connected_clients.update( {'client {}'.format(i) : [conn,addr]} )
	i=i+1
	t = threading.Thread(target=user, args=(conn, addr))
	t.start()