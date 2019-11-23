#  https://github.com/mgthk/meteredwifi4kids
#
# This program is provided as it, without any warranty.
# Thank you for using this program. I hope it works well for you.
# Feel free to improve it.
#


import threading
import datetime
import time
import I2C_LCD_driver
from py532lib.i2c import *
from py532lib.frame import *
from py532lib.constants import *
from collections import deque #use as a fifo queue


 
def nfc_reader():

   pn532 = Pn532_i2c()
   pn532.SAMconfigure()

   while True:

      if not running:
        print("Not running")
        return

      card_data = pn532.read_mifare().get_data()
      if card_data is None:
        print("Card data is none")
        continue

      card_data_hex_string = "".join("%02x" % b for b in card_data)
      cardid = card_data_hex_string[-8:]
      print("Card id : " + cardid)

      with queue_lock:
        # replaced print with deque.append
        queue.append(cardid)
        #time.sleep(1)

def wifi_usage_timer():

    global wifi_usage_remain_minute

    wifi_usage_remain_count_file = "/home/pi/py532lib/" + datetime.datetime.now().strftime("%Y%m%d")
    print("Usage remaining counter file : " + wifi_usage_remain_count_file)

    while True:

        if not os.path.isfile(wifi_usage_remain_count_file):
           print(wifi_usage_remain_count_file + " not exists. Create one and set default.")
           count_file = open(wifi_usage_remain_count_file,"w+")
           count_file.write(str(authorized_wifi_usage_remain_minute))
           count_file.close()

        count_file = open(wifi_usage_remain_count_file,"r")
        wifi_usage_remain_minute = int(count_file.read())
        count_file.close()

        if isWiFiEnabled:

                print("Sleep 60 seconds...")
                time.sleep(60)
                wifi_usage_remain_minute = wifi_usage_remain_minute - 1

                count_file = open(wifi_usage_remain_count_file,"w")
                count_file.write(str(wifi_usage_remain_minute))
                count_file.close()
                print("WiFi usage remaining in minute =", wifi_usage_remain_minute)
        #else:
                #print("WiFi not enabled. Counter not update. WiFi usage remaining in minute =", wifi_usage_remain_minute)

        
def enableWifi():
    print("Enabling WiFi")

    #run systemctl start hostapd
    os.system("/usr/bin/sudo /bin/systemctl start hostapd")  
    return True

def disableWifi():
    print("Disabling WiFi")

    #run systemctl stop hostapd
    os.system("/usr/bin/sudo /bin/systemctl stop hostapd")
    return False

def updateLCD():
    print("updateLCD")
    isWiFiEnabled
    wifi_usage_remain_minute

    wifi_status = "Off"

    if isWiFiEnabled:
       wifi_status = "On"
    else:
       wifi_status = "Off"
       
    lcdMsg1 = "Wifi " + wifi_status + ". " + str(wifi_usage_remain_minute) + " min"

    mylcd.lcd_display_string(lcdMsg1, 1)

    now = datetime.datetime.now()

    lcdMsg2 = now.strftime("%Y-%m-%d %H:%M")	
    mylcd.lcd_display_string(lcdMsg2, 2)
    #time.sleep(1)

def isAuthorizedCard(provided_cardid):


    print("Detected card id:", provided_cardid)
    print("Authorized card id:", authorized_cardid)
    if authorized_cardid == provided_cardid:
       print("card authorized")
       return True  
    else:
       print("card not authorized")
       return False 

#Main
#Init params
no_card_timer=0
isWiFiEnabled=False
wifi_usage_remain_minute=0

queue = deque() #queue to pass information from thread to main process
queue_lock = threading.Lock() #prevent possible issues from 
running = True

print("Init LCD... ")
mylcd = I2C_LCD_driver.lcd()
mylcd.lcd_clear()


#wifi_usage_remain_count_file = "/home/pi/py532lib/" + datetime.datetime.now().strftime("%Y%m%d")
#print("Usage remaining counter file : " + wifi_usage_remain_count_file)

authorized_cardid_file = "/home/pi/py532lib/authorizedcardid"
print("authorized cardid file : " + authorized_cardid_file)

cardid_file = open(authorized_cardid_file,"r")
authorized_cardid = cardid_file.read().rstrip()
cardid_file.close()

authorized_wifitime_file = "/home/pi/py532lib/authorizedwifitime"
print("authorized wifi time file : " + authorized_wifitime_file)

wifitime_file = open(authorized_wifitime_file,"r")
authorized_wifi_usage_remain_minute = int(wifitime_file.read().rstrip())
wifitime_file.close()

nfc_thread = threading.Thread(target=nfc_reader)
nfc_thread.start()

wifi_usage_timer_thread = threading.Thread(target=wifi_usage_timer)
wifi_usage_timer_thread.start()

disableWifi()
updateLCD()

while True: #also cheap, but easy
    if queue: #bool(deque) works like bool(list)
        with queue_lock:
            cardid = queue.popleft()
            no_card_timer=0
            print("isWiFiEnabled", isWiFiEnabled)

            if wifi_usage_remain_minute <= 0:
                isWiFiEnabled = disableWifi()

            if isWiFiEnabled:
                print("Wifi already enabled. Do Nothing")

            else:
                if wifi_usage_remain_minute > 0  :

                    if isAuthorizedCard(cardid):
                       print("Card authorized : ", cardid)
                       isWiFiEnabled = enableWifi()
                    else:
                       print("Card not authorized : ", cardid) 
                       disableWifi()
 
                else:
                    print("No more usage time left.", wifi_usage_remain_minute)

            updateLCD()
            continue

    else:
        no_card_timer = no_card_timer+1
        #print ("Card not present timer = ", no_card_timer)
        if no_card_timer >= 10: 
           no_card_timer=0
           print("isWiFiEnabled", isWiFiEnabled)
           #unconditional force shutdown wifi
           isWiFiEnabled = disableWifi()
           updateLCD()
 
    time.sleep(1)
