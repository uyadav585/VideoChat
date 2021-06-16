import socket,cv2, pickle,struct,threading,imutils

# create socket
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
host_ip = input("Enter the server's IP : ")
port = int(input("Enter the port on which server is listening on : "))
s.connect((host_ip,port)) # a tuple


def recv_vid():
        data = b""
        payload_size = struct.calcsize("Q")
        while True:
                while len(data) < payload_size:
                        packet = s.recv(4*1024) # 4K
                        if not packet: break
                        data+=packet
                packed_msg_size = data[:payload_size]
                data = data[payload_size:]
                msg_size = struct.unpack("Q",packed_msg_size)[0]

                while len(data) < msg_size:
                        data += s.recv(4*1024)
                frame_data = data[:msg_size]
                data  = data[msg_size:]
                frame = pickle.loads(frame_data)
                cv2.imshow("recving From Server",frame)
                key = cv2.waitKey(1) & 0xFF
                if key  == ord('q'):
                        break

def send_vid():
        vid=cv2.VideoCapture(0)
        while True:
                img,frame = vid.read()
                frame = imutils.resize(frame,width=320)
                a = pickle.dumps(frame)
                message = struct.pack("Q",len(a))+a
                s.sendall(message)
                cv2.imshow("You",frame)
                key = cv2.waitKey(1) & 0xFF
                if key ==ord('q'):
                        s.close()

#s.close()
tr = threading.Thread(target=recv_vid)
tr.start()
send_vid()
