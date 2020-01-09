
from ftplib import FTP
import os, sys
import time
#Image Resizing
from PIL import Image
import PIL
#Convert PNG - DDS
from wand.image import Image as OpenThis
#SerialKey = "" Here

class get_IP_Port:
    def __init__(self):
        self.IP = None
        self.Port = None
        
    def Set_IP_Port(self):
        with open("IP_Port.txt", "r") as file:
            line = file.readlines()
            self.IP = line[0][7:].strip()
            self.IP = self.IP.rstrip()
            self.Port = line[1][6:].strip()
            self.Port = self.Port.rstrip()
            
    def getIP(self):
        self.Set_IP_Port()        
        return self.IP
    def getPort(self):
        self.Set_IP_Port()        
        return self.Port
        
class RunProfileIt:
    def __init__(self, IP=None, Port=1337):
        self.IP = IP
        self.Port = Port
        self.root = "system_data/priv/cache/profile/"
        self.PS4AccountCodeTemp = []
        self.PS4AccountCode = []
        self.AllUsers = []
        self.ftp = FTP()
        
        #Time 
        self.T1 = 0
        self.T2 = 0
        self.TotalT = 0
        
        #System Username
        self.firstName = []
        self.lastName = []
        
        #PC Images
        self.ImgDir = os.getcwd() + "\Profile Image"
        self.Img2Upload = []
        
    def connect(self, root): #Connect FTP and go to root dir
        try:
            self.ftp.set_debuglevel(2)
            self.ftp.connect(self.IP, self.Port)
            self.ftp.login("", "")  
            self.ftp.cwd(root)    
        except:
            print("Connection failed : Invalid IP, port or PS4 not in FTP mode")
            time.sleep(20)
            sys.exit()
            
    def GetAccountCode(self): #Get profile codes exp:[0x1CAC16A1] 
        self.connect(self.root)
        self.ftp.retrlines("LIST ", self.PS4AccountCodeTemp.append)
        
        """Remove dir info from account Code"""
        
        for onlyCode in self.PS4AccountCodeTemp:
            self.PS4AccountCode.append(onlyCode.split(" ")[-1])
            
        self.PS4AccountCode.reverse()
        self.PS4AccountCode.pop()
        return(self.PS4AccountCode)
        
    def AccountCode_2_Name(self):   
        self.GetAccountCode()
        for user in self.PS4AccountCode:
            if len(user) > 4:
                self.root = self.root
                self.connect(self.root + "/" + user)
                
                print(self.root)
                """download online.json for userName"""
                with open("Temp.txt", "wb") as file:
                    self.ftp.retrbinary("RETR " + "online.json", file.write, 1024)
                with open("Temp.txt", "r", encoding = "utf8") as file:
                    reading = file.read()
                    
                    def firstNameIndex():
                        start = reading.find("firstName") + len("firstName") + 3
                        end = reading.find("lastName") - 3
                        self.firstName.append(reading[start : end])
                    def lastNameIndex():
                        start = reading.find("lastName") + len("lastName") + 3
                        end = start
                        for i in range(50):
                            if reading[start+i].isalpha():
                                end += 1
                            else:
                                break
                        self.lastName.append(reading[start : end])
                        
                    firstNameIndex()  
                    lastNameIndex()   
                        
    def GetUserName(self): #Show Users' Name 
        self.AccountCode_2_Name()
        print()
        print("Your PS4 System Account(s):-\n")

        for user in range(1, len(self.firstName)+1):
            print(str(user) + ": " + self.firstName[user-1] +" "+ self.lastName[user-1])
    
    def ResizeImg(self):
        ImgFRMT = (".JPG", ".PNG", ".DDS", ".JPEG", ".ICO")
        Imgfrmt = (".jpg", ".png", ".dds", ".jpeg", ".ico")
        AllImg = os.listdir(self.ImgDir)
        FoundImg = []
        index = 1
        
        """Choose Image"""
        if len(AllImg) < 2:
            print("Couldn't find any images in (ProfileIt\Profile Image) ")
            time.sleep(20)
            sys.exit()
        else:
            print("\nImages found:-")
            for Img in AllImg: #Check Image Format from last indexs
                if "." in Img: #has extension (format)
                    if (Img[-4:] or Img[-5:] in ImgFRMT) or (Img[-5:] or Img[-4:] in Imgfrmt):
                        print(str(index) +": "+ Img )
                        FoundImg.append(Img)        
                        index += 1
            choose = int(input("\nWhich image would you like to upload[#number!]: "))
            ResizeImg = Image.open(self.ImgDir + "\\" + FoundImg[choose - 1])
        
        """Check size"""
        
        atLeast = 440
        ImgSize = ResizeImg.size
        ImgWidth = ImgSize[0]
        ImgHeight = ImgSize[1]
        
        if ImgWidth == atLeast and ImgHeight == atLeast or ImgWidth > atLeast and ImgHeight > atLeast:
    
            """Resize"""
            
            #Check and create temp folder
            try:
                os.mkdir(self.ImgDir + "\\temp")
            except:
                pass #Pass any Ecxeptions
            
            required_dds = ("avatar64", "avatar128", "avatar260", "avatar440")
            tempDir = self.ImgDir + "\\" + "temp\\"
            
            avatar = ResizeImg.resize((440, 440), PIL.Image.ANTIALIAS)
            avatar.save(tempDir + "avatar.png")
            
            #Resize all PNGs
            for dds in required_dds:
                if "64" in dds:
                    avatar = ResizeImg.resize((64, 64), PIL.Image.ANTIALIAS)
                    avatar.save(tempDir + "avatar64.png")
                else:
                    s = int(dds[-3:])
                    avatar = ResizeImg.resize((s, s), PIL.Image.ANTIALIAS)
                    avatar.save(tempDir + "avatar" + str(s) + ".png")
                    
            #Convert PNG - DDS
            for dds in required_dds:
                with OpenThis(filename = tempDir + dds + ".png") as Original:
                    Original.save(filename = tempDir + dds + ".dds") 
                os.remove(tempDir + dds + ".png")
            
            for upload in os.listdir(tempDir):
                if upload == "avatar.png":
                    self.Img2Upload.append(upload)
                elif upload[-3:] != "png":
                    self.Img2Upload.append(upload)
                    
        else:
            print("Image too small. Minimum size 440x440")
            time.sleep(10)
            sys.exit()
        
    def Upload(self):
        self.T1 = time.time()
        #Resize Images
        self.ResizeImg()
        
        #Get All Accounts found on system
        self.GetUserName()
        choose = input("\nWhich profile icon would you like to change[number!]: ")
        while choose not in "1234567890":
            print("\nPlease choose the image number...")
            choose = input("Which profile icon would you like to change[number!]: ")

        #Reconnect server / Go to chosen user folder 
        while int(choose) > len(self.PS4AccountCode) or int(choose) < 1:
            print("Number (", choose, ") isn't available")
            choose = input("Which profile icon would you like to change[number!]: ")
            
        self.connect(self.root + self.PS4AccountCode[int(choose) - 1])
        
        #Upload Images
        success = False
        for Image in self.Img2Upload:
            save = open(self.ImgDir + "\\temp\\" + Image, "rb")
            try:
                self.ftp.storbinary("STOR " + Image, save,1024)
                success = True
            except:
                success = False
                
        if success == True:
            print("\nSuccessfully Uploaded. Happy modding!\nTool made by @OfficialAhmed0")
            try:
                os.rmdir(self.ImgDir + "\\temp")
            except:
                print("ATTENTION!Please remove temp folder. path:(Profileit\profile Images) if any error occurs")
        else:
            print("Sorry Something went wrong.")
            
        """Timing"""
        
        self.T2 = time.time()
        self.TotalT = self.T2 - self.T1
        if self.TotalT < 60:
            return "\nTime Elapsed: " + str(round(self.TotalT, 2)) + "s"
        else:
            return "\nTime Elapsed: " + str(round(self.TotalT/60, 2)) + " minutes" 
                       
"""Start of Program"""
Valid = False

try:
   #Check Key statements
except:
    print("Cannot find Original Key: @OfficialAhmed0.Key")
    time.sleep(10)
    sys.exit()
    
if Valid == True:
    print(RunProfileIt(get_IP_Port().getIP(), int(get_IP_Port().getPort())).Upload())
    for quit in range(20):
        print("Auto quit " + str(quit) + "/20", end="")
        time.sleep(1)
else:
    #Invalid statement here
    time.sleep(10)
    sys.exit()


    
