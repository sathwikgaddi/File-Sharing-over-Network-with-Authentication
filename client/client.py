import socket
import sys
import rsa
import os
import tqdm
import hmac, base64, struct, hashlib, time
import qrcode





if (len(sys.argv) > 1):
    ServerIp = sys.argv[1]
else:
    print("Enter Valid IP of the server to want to receivein arguments and run")
    exit(1)


s = socket.socket()


PORT = 9898


s.connect((ServerIp, PORT))

msg = s.recv(1024).decode("utf-8")

print(msg)

publicKey_client, privateKey_client = rsa.newkeys(1024)
pubStr_client = publicKey_client.save_pkcs1(format='DER')
s.send(pubStr_client)


secret_key = s.recv(1024)
secret_key = rsa.decrypt(secret_key,privateKey_client).decode()
img = qrcode.make(secret_key)
 
# Saving as an image file
img.save('secret_QR.png')
print("Please find the secret_qr.img file in your directory to use for the registration in the authenticator app")




publicStr_server = s.recv(1024)
print(type(publicStr_server))

public_key_server = rsa.key.PublicKey.load_pkcs1(publicStr_server, format='DER')

while(True):

    option = int(input("1. Receive a file\n2. Exit\n Enter an option to continue: "))
    if(option == 1):
        while(True):
            otp = input("Please Enter your Otp from the authenticator!!!")

            encMessage = rsa.encrypt(otp.encode(),public_key_server)

            s.send(encMessage)

            vmsg = s.recv(1024).decode()
            print(vmsg)

            if(vmsg == "OTP verified"):

                file_str = s.recv(1024).decode()

                file_list = file_str.split('<sep>')

                for i in range(len(file_list)):
                    print(str(i+1) + " " + file_list[i])

                print("Select a file to receive")

                name = input()

                s.send(name.encode())
                BUFFER_SIZE = 4096
                SEPARATOR = "<SEPARATOR>"
                received = s.recv(BUFFER_SIZE).decode()
                filename, filesize = received.split(SEPARATOR)
                # remove absolute path if there is
                filename = os.path.basename(filename)
                # convert to integer
                filesize = int(filesize)
                print(filesize)
                # progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
                with open(filename, "wb") as f:
                    while True:
                        # read 1024 bytes from the socket (receive)
                        bytes_read = s.recv(BUFFER_SIZE)
                        if not bytes_read:    
                            # nothing is received
                            # file transmitting is done
                            break
                        # write to the file the bytes we just received
                        f.write(bytes_read)

                print("File received successfully!!!\n")    
                        
                break

            elif (vmsg == "OTP Invalid"):
                print("Invalid otp!!!, please enter otp again")

    else:
        break