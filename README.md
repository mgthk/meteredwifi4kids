# meteredwifi4kids
Use case

  Use NFC access card to activate WiFi hotspot on Raspberry Pi 3 until daily credit (in minutes) used up. Good for letting kids to use WiFi on their own schedule while limiting the amount of time spending on the Internet.

Materials:

Hardware:
1. A Raspberry Pi 3B (tested Ok) or above with a microSD card
2. PN532 based NFC card reader (I2C bus capable, able to take 5V power input)
3. Mifare Classic or NTag 213 (216 should work too)
4. 16x2 or 20x4 LCD using I2C bus (able to take 5V power input)
5. breadboard, 1-to-many I2C extender or similar extender
6. At least 12 pieces of Dupont wires
7. A LAN cable
8. Broadband connection

Software:
1. Raspbian
2. raspap-webgui
3. py532lib

Preflight check:

1. Pi3B has I2C enabled
2. Pi3B has time sync properly setup
3. Pi3B is connected to broadband connection using LAN cable
4. Performed below actions
<pre>
sudo apt update
sudo apt upgrade
</pre>
5. Password of pi has been changed, preferably to a complex one
6. Disable auto-login to GUI console (quite optional, depends on age of the kids and if you believe that they don't know how to connect the Pi to TV and using USB keyboard and mouse to poke around.) 
7. Make sure the Pi3B has been disconnected from power supply before plugging or unpluggin dupont wires to prevent risk of causing any damage in event of wrong cable connection.

Setup Procedures:

PN532 (adopted from https://blog.stigok.com/2017/10/12/setting-up-a-pn532-nfc-module-on-a-raspberry-pi-using-i2c.html)

1. Connect the Pi3's 5V, GND, SDA and SCL to breadboard, 1-to-many I2C extender or similar extender

2. Connect PN532's 5V, GND, SDA and SCL to breadboard, 1-to-many I2C extender or similar extender

3. sudo apt install i2c-tools

4. pi@raspberrypi:~ $ i2cdetect -y 1

<pre>
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- 24 -- -- -- -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
</pre>
If the PN532 is connected to the Pi correctly, 24 should be displayed, which is the address of the PN532.  If the value you got is not 24, see Trouble Shooting below.

5. sudo apt install libnfc5 libnfc-bin libnfc-examples

6. sudo vi /etc/nfc/libnfc.conf
add below:

<pre>
device.name = "PN532 over I2C"
device.connstring = "pn532_i2c:/dev/i2c-1"
</pre>

7. pi@raspberrypi:~ $ nfc-list -v
<pre>
nfc-list uses libnfc 1.7.1
NFC device: pn532_i2c:/dev/i2c-1 opened
0 ISO14443A passive target(s) found.

0 Felica (212 kbps) passive target(s) found.

0 Felica (424 kbps) passive target(s) found.

0 ISO14443B passive target(s) found.

0 ISO14443B' passive target(s) found.

0 ISO14443B-2 ST SRx passive target(s) found.

0 ISO14443B-2 ASK CTx passive target(s) found.

0 Jewel passive target(s) found.
</pre>

8. nfc-poll

9. place a card on the reader to see if it can be read properly

10. cd ~

11. git clone https://github.com/HubCityLabs/py532lib.git

I2C LCD (adopted from http://www.circuitbasics.com/raspberry-pi-i2c-lcd-set-up-and-programming/)

1. Connect LCD's 5V, GND, SDA and SCL to breadboard, 1-to-many I2C extender or similar extender

2. pi@raspberrypi:~ $ i2cdetect -y 1
<pre>
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:          -- -- -- -- -- -- -- -- -- -- -- -- --
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
20: -- -- -- -- 24 -- -- 27 -- -- -- -- -- -- -- --
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
50: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --
70: -- -- -- -- -- -- -- --
</pre>
the 27 is the address of the LCD. If the value you got is not 27, see Trouble Shooting below.

Install raspap-webgui

1. cd /tmp

2. wget -q https://git.io/voEUQ -O /tmp/raspap && bash /tmp/raspap

3. follow on screen instructions to complete raspap-webgui setup and reboot the Pi3.

4. Remember to login to raspap-webgui (use browser and via LAN connection) to do the followings:
a. update SSID and password for WiFi access point
b. update administrator login and password for raspap-webgui

5. Reboot if needed

Install meteredwifi4kids

1. cd ~

2. git clone --depth=1 https://github.com/mgthk/meteredwifi4kids.git

3. cd meteredwifi4kids

4. move below files
<pre>
mv meteredwifi4kids.py ../py532lib
mv I2C_LCD_driver.py ../py532lib
mv authorizedcardid ../py532lib
mv authorizedwifitime ../py532lib
</pre>

5. sudo vi /etc/rc.local, add below just before "exit0"
 <pre>
#prevent access to Pi via ssh and raspap-webgui from WiFi client
iptables -A INPUT -i wlan0 -p tcp --destination-port 22 -j DROP
iptables -A INPUT -i wlan0 -p tcp --destination-port 80 -j DROP

#stop the wifi hot spot
/usr/bin/sudo /bin/systemctl stop hostapd

cd /home/pi/py532lib
/usr/bin/nohup /usr/bin/python3 meteredwifi4kids.py > /tmp/meteredwifi4kids.py.log 2>&1 &
</pre>

6. cd ~/py532lib
7. python3 meteredwifi4kids.py
8. Debug log will be shown on console. Put a card on the PN532, the card's ID should be printed. Take note of it.
9. Press a few times of Ctrl-C to break the program
10. vi authorizedcard
11. replace the sample ID with the one you noted down at step 10
12. save and exit

Test run

1. Remove the card from PN532
2. cd ~/py532lib
3. run "python3 meteredwifi4kids.py"
4. Use smart phone or a notebook computer with WiFi turned on to verify the SSID you have chosen for your Pi3 is NOT availab.e
5. Put the card on the PN532 and wait a few seconds
6. Check the smart phone or notebook computer again to see if the SSID is available now
7. Remove the card and wait about 15 to 30seconds. The SSID should be disappeared.

Put it into action

1. sudo reboot now
2. Wait for the Pi3B to reboot
3. Once it's back, run ps -ef | grep metered to see if meteredwifi4kids.py is running properly

Known Issues

1. Daily remaining usage count files (file name in yyyymmdd format) are located at /home/pi/py532lib. You may set a crontab job to clean them regularly.

Trouble Shooting

1. If the LCD is located at another address other than 27, edit I2C_LCD_driver.py and change the 0x27 in line ADDRESS = 0x27 to the value you have identified.
2. If the PN532 is located at another address other than 24, edit py532lib's constants.py and change the  0x24 in line PN532_I2C_SLAVE_ADDRESS = 0x24 to the value you have identified.
