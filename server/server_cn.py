import socket
import rsa
import os
import tqdm
import hmac, base64, struct, hashlib, time
from secret_key_generator import secret_key_generator



def get_hotp_token(secret, intervals_no):
    secret = secret.encode("ascii")
    secret = base64.b32encode(secret)
    secret = secret.decode("ascii")
    key = base64.b32decode(secret, True)
    msg = struct.pack(">Q", intervals_no)
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = o = h[19] & 15
    h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    return h

def get_totp_token(secret):
    x =str(get_hotp_token(secret,intervals_no=int(time.time())//30))
    while len(x)!=6:
        x+='0'
    return x

port = 9898
s = socket.socket()
s.bind(('', port))
s.listen(10)
print("\n Server is listening on port : ", port , "\n")

print("Do you want to share files?")
print("Press 1 share and 2 to stop")
    
option = int(input())

while True:



    if(option == 1):
        conn, addr = s.accept()

        print("Incoming connection from: ", end = " ")
        print(addr)
        print("Do you like to accept the connection \n1. Accept\n2. Deny")
        if(int(input()) == 1):

            msg = "You are successfully connected to the server!!!!"
            print("Connection Successful")
            conn.send(msg.encode())

            publicStr_client = conn.recv(1024)
            public_key_client = rsa.key.PublicKey.load_pkcs1(publicStr_client, format='DER')


            SECRET_KEY = secret_key_generator.generate()
            with open('.secret.txt') as f:
                secret_key = f.read()
            encMessage = rsa.encrypt(secret_key.encode(),public_key_client)
            conn.send(encMessage)



            publicKey_server, privateKey_server = rsa.newkeys(1024)
            pubStr_server = publicKey_server.save_pkcs1(format='DER')
            # print(type(pubStr_server))
            conn.send(pubStr_server)   
            while(True):
                otp = conn.recv(1024)
                otp = rsa.decrypt(otp,privateKey_server).decode()
                my_otp = get_totp_token(secret_key)
                
                print(my_otp)
                print(otp)
                if(my_otp == otp ):
                    
                    msg = "OTP verified"
                    conn.send(msg.encode())

                    print("Please type the path of directory which you want to host for this client")
                    path = input()
                    dir_list = os.listdir(path)
                    ss = '<sep>'.join(dir_list)
                    conn.send(ss.encode())

                    filename = conn.recv(1024).decode()
                    print(filename)

                    filesize = os.path.getsize(filename)
                    
                    SEPARATOR = "<SEPARATOR>"

                    # send the filename and filesize
                    conn.send(f"{filename}{SEPARATOR}{filesize}".encode())

                    # start sending the file
                    # progress = tqdm.tqdm(range(filesize), f"Sending {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                    BUFFER_SIZE = 1024
                    with open(filename, "rb") as f:
                        print("f is:")
                        while True:
                            # read the bytes from the file
                            bytes_read = f.read(BUFFER_SIZE)
                            if not bytes_read:
                                print("breaking")
                                # file transmitting is done
                                break
                            print("not breaking")
                            # we use sendall to assure transimission in 
                            # busy networks
                            conn.send(bytes_read)
                            # progress.update(len(bytes_read))

                    print("shared")

                    conn.close()
                    break
                
                else:
                    print("OTP Invalid")
                    msg1 = "Invalid OTP"
                    conn.send(msg1.encode())


        else:
            conn.close()
    else:
        break



