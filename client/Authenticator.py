import hmac, base64, struct, hashlib, time
import cv2
from tkinter import Tk 
from tkinter.filedialog import askopenfilename

def get_hotp_token(secret, intervals_no):
    key = base64.b32decode(secret, True)
    #decoding our key
    msg = struct.pack(">Q", intervals_no)
    #conversions between Python values and C structs represente
    h = hmac.new(key, msg, hashlib.sha1).digest()
    o = o = h[19] & 15
    #Generate a hash using both of these. Hashing algorithm is HMAC
    h = (struct.unpack(">I", h[o:o+4])[0] & 0x7fffffff) % 1000000
    #unpacking
    return h
def get_totp_token(secret):
    #ensuring to give the same otp for 30 seconds
    x =str(get_hotp_token(secret,intervals_no=int(time.time())//30))
    #adding 0 in the beginning till OTP has 6 digits
    while len(x)!=6:
        x+='0'
    return x
#base64 encoded key

def countdown():
    t = 30
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1
    print("passcode expired")


filename = askopenfilename()
img=cv2.imread(filename)
det=cv2.QRCodeDetector()
val, pts, st_code=det.detectAndDecode(img)
# print(type(val))
secret = val
print("QR code accepted!!")
while(True):
    
    inp = input("Press enter to generate new otp")
    # secret = "qza&2)9q#@_o=o^p2f)i9kafsgo+7kx@odc4jmmpv+3sk&kuf%"
    secret = secret.encode("ascii")
    secret = base64.b32encode(secret)
    secret = secret.decode("ascii")
    print("Your passcode is: ", get_totp_token(secret))
    print("This passcode is valid for ")
    countdown()

    

