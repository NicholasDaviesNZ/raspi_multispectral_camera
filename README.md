# Multi spectral camera built from raspberry pi
## Set up:
OS setups:
Currently the 4b gets 64bit bookworm by defalt and the pi zeros get 32 bit bulls eye. Use the pi imager, and hopefully it will work. The imager will give you the option to edit/customise the os, make sure you do this and give it a username and password - there is no defalt anymore so if you dont it will just give you permission denied errors. The Pi4b is the main pi for this project and its username@host should be pi@pi4b the zeros are pi_zero_1@pizero1 or pi_zero_2@pizero2 etc. Note you dont need to activate wifi on the zeros (or the 4 b for that matter) but it will make trouble shooting easier. Give it wifi creds, change the keyboard layout to your layout (probably us) go to the next tab and enable ssh by password. Pi imager  generates firstrun.sh in the boot directory at the end of the write, if your having trouble getting anything to connect to wifi check in there incase it has hashed the password wrong or something try echo 'raspberry' | openssl passwd -6 -stdin to generate a hash for the password raspberry. Flash the 4b and the verious pi zeros using imager. A note that there seems (for me at this point in time anyway) to be an issue with using imager setting the keyboard type, so be aware that if you use anything which is different between your keyboard and a uk keyboard ie special chars it may result in passwords being declined- by default pi imager seems to set keyboard to UK and changing it does not always work. 

After the image has written follow the below, including some trobule shooting tips
For a usb network need to change these on the boot partition:
Https://Artivis.Github.Io/Post/2020/Pi-Zero/
plug to centre micro usb port otg port - the central port, not the outside one 
add dtoverlay=dwc2 to the end of the config.txt file (zeros and 4b)
add modules-load=dwc2,g_ether after rootwait in the cmdline.txt file. note that there must be exactly 1 space after rootwait, and one space before the next command (zeros only)

Trobule shooting: 
if you have trouble with ssh add blank file with no extention called ssh to the boot partition
if you have trouble with user configuration Add userconf.txt containing pi:$6$/4.VdYgDm7RJ0qM1$FwXCeQgDKkqrOU3RIRuDSKpauAbBvP11msq9X58c8Que2l1Dwq3vdJMgiZlQSbEXGaY5esVHGBNbCxKLVNqZW1
to the boot partition (username pi, password is raspberry)
for wifi if you have trouble try addeding a file called wpa_supplicant.conf containing:
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    ssid="xxxxxx"
    psk="xxxxxxx"
}
to the boot partition


for the pi zeros, go into the root partition and sudo nano /etc/dhcpcd.conf and go to the end
for pi zero 1 add:

interface usb0
static ip_address=10.0.1.11/16
static routers=10.0.1.1

This sets the static ip for pi zero 1 to 10.0.1.11 - note the /16 defines the bits to read to get the address, if you use a 192.168 address it will need to be /24
Then to pi zero 2, sudo nano /etc/dhcpcd.conf

interface usb0
static ip_address=10.0.1.12/16
static routers=10.0.1.1

this sets the static ip for pi zero 2 to 10.0.1.12

The 4b uses network manager so we will do it in the gui later. 

then check the host names are correct (for every device), for the zeros and the pi4 nano /etc/hostname and check it is correct (pi4b pizero1 pizero2 etc.)
go into nano /etc/hosts and check it looks something like this: where pi4b is whatever the host name should be, pizero1 etc.                        
127.0.0.1       localhost pi4b
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters

127.0.1.1               pi4b

If you need to edit it will be sudo nano /etc/... sudo will be your normal linux password

Now we are ready to boot, plug the pi zeros into the central/otg micro port, and into the usb3 ports on the pi 4 and plug it in.
go have a coffee, all of them need to do a bunch or initalisation and it take 5 min or so so if its not working give it a while to finish installing the os's.
Check your router for the verious ip addresses, they should show us as pi4b pizero1 etc. get the ip address for at least the 4b. I have had trouble with this and have had to connect it via ethernet to the router, then using sudo raspi-config get the wifi connected, not strictly needed but if the imager doesnt get it working this is another option. Note depending on your routers dhcp time out settings this may be different tomorrow so if you cant log in go check it it has changed, you can set to to a static ip in the router if you want, but i wont go into that here. 

once you have the ip address from the router, ssh into the 4b - ssh pi@192.168.xxx.xxx whatever the ip is that you found from the router - note if your router is on a 10.0.1.x there may be a conflict and you might be a conflict, im nto sure, if there is either change your how router to a 192.168 configuration or change this from being 10.xxx to being 192.168.xxx . if you have trouble with ssh add verbose flag, ssh -vvv pi@...
once your in run sudo raspi-config and go to interfaces and enable vnc connections. you can do updates etc here if you want to.
Now load up your vnc viewer and connect to it with the same ip, username and password that you used for ssh and you should get the raspberry pi os desktop. 

Now we need to configure the pi4b end of the network with the zeros. 
click on the wifi network icon in the top right, go to advanced options, edit connections. under ethernet you should see wired connection 1 wired connection 2 etc. double click on one of these and if the device is eth0 interface ignore it (the real ethernet port) if it is usb0 do the following:
go to ipv4 settings set it to manual and click add, set the ip to 10.0.1.2 and the netmask to 16, gate way can stay blank. check taht ipv6 is set to automatic. click save and exit
find the usb1 interface and do the same but with 10.0.1.3
Now back in the network connections box click ethernet and click the little + button in the bottom left and choose bridge set device to usb0 and leave other things as default and it should autogenerate a new bridge port 1 connection,
go to ipv4 settings and add the ip 10.0.1.20 and netmask 16 and save the connection. 

Now within the bridge connection click add choose ethernet and add the usbxs as devices one at a time. 

check taht the bridge connection is set to auto connect, then go and disable autoconnect on the usb0 and usb1 wired connection interfaces. 

Reboot

re connect via the vnc viewer, and everything *should* have worked, you should be connected to the network bridge, and if you try ssh pi_zero_2@10.0.1.12 it should prompt you about a fingerprint then ask for a password, same for pi_zero_1@10.0.1.11 

For now we will leave the wifi on the zeros on, but will turn it off later. Just make sure that the pi4b is always connecting over usb now wifi. it means during the software setup we can ssh into them from your main computer, rather than creating a chain and going through the ethernet over usb to have a look at what is going on in them. we can also connect direcly to the zeros using vs code through ssh tunnels from our main machine using the wifi if we want to. 
When we want to turn wifi off add the following to the config.txt file of the pi zeros. 
dtoverlay=disable-wifi
dtoverlay=disable-bt


Now taht you have confirmed everything works, shutdown all of the pi's and download this git repo as a zip folder and extract it on your main computer. insert the pi4b sd card into your computer and copy the folders inside the pi4b folder to the /home/pi/ so it should look like /home/pi/camera/ for example. there is a folder called reflectance_cameras, the contence fo this goes onto the pi zeros which are downward facing (zero 1 and zero 2) and transmitance_cameras (zeros 3 and 4 if they exist). again to /home/pi_zero_1/webserver/ etc. 

open your pi4 vnc connection back up and open two terminals and ssh into each of the pi zeros, navigate to home/pi_zero_x/webserver and either activate a vertual env and then run python webserver.py or just run it without the env, do this for all of the pi's. 

set the pi zeros to start the webservers on startup, run crontab -e and paste this with the correct username at the bottom of the file
@reboot /bin/sleep 10; /usr/bin/python3 /home/pi_zero_1/webserver/webserver.py >> /home/pi_zero_1/mycronlog.txt 2>&1


when creating the venv need to use: --system-site-packages as a flag to be able to accsess the system libcamera
python3 -m venv venv --system-site-packages  to create the virtual env
source venv/bin/activate

on the zero, we will create a web server using flask, to do this:
python3 -m venv venv --system-site-packages  to create the virtual env
source venv/bin/activate
python webserver.py should start a web server on  http://0.0.0.0:5000/
remember to create the ~/webserver and ~/webserver/captures directories

Note about collections needing to be cahnged to collections.abs if there is an error in dronekit, in __init__ file

Gide to connect to drone:
https://www.hackster.io/Matchstic/connecting-pixhawk-to-raspberry-pi-and-nvidia-jetson-b263a7
inside env pip install pymavlink dronekit imutils


To trigger RPi from gpio, plug into pin 8 of the splitter that is already on the drone for the motors, plug ground and signal in - same as motors. in parameters set servo8_function to -1 (gpio) set relay_pin to mainout8, cam1_type to 2 (relay) cam1_duration to 1 (this is the time that the relay is held open for) ground goes to ground on the Pi, and signal goes to GPIO13 which is on the 3.3v rail and 4 from the usb ports end. 


need to install sudo apt-get install libexiv2-dev libboost-python-dev
then pip install py3exiv2

for thermal need to install: sudo apt-get install -y i2c-tools
need to go into sudo raspi-config and interfaces enable i2c
may need to go into config.txt and uncoment the dtparam=i2c_arm=on line
and within the env, pip install smbus pip install RPI.GPIO adafruit-blinka and pip install adafruit-circuitpython-mlx90640
you may need to run the following to get some of the modules working:
cd ~
pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo -E env PATH=$PATH python3 raspi-blinka.py



I think I can add custom name spaces like this:
metadata = pyexiv2.ImageMetadata('./images/vis_1705181900.jpg')
metadata.read()
pyexiv2.xmp.register_namespace('/drone-dji/', 'drone-dji')
metadata['Xmp.drone-dji.FlightXSpeed'] = 1
metadata.write()



avaiable flight controler data:
FORMAT_VERSION: 120.0
SYSID_THISMAV: 1.0
SYSID_MYGCS: 255.0
PILOT_THR_FILT: 0.0
PILOT_TKOFF_ALT: 0.0
PILOT_THR_BHV: 0.0
SERIAL0_BAUD: 115.0
SERIAL0_PROTOCOL: 2.0
SERIAL1_PROTOCOL: 2.0
SERIAL1_BAUD: 57.0
SERIAL2_PROTOCOL: 2.0
SERIAL2_BAUD: 57.0
SERIAL3_PROTOCOL: 5.0
SERIAL3_BAUD: 38.0
SERIAL4_PROTOCOL: 5.0
SERIAL4_BAUD: 38.0
SERIAL5_PROTOCOL: 23.0
SERIAL5_BAUD: 57.0
SERIAL6_PROTOCOL: -1.0
SERIAL6_BAUD: 57.0
SERIAL1_OPTIONS: 0.0
SERIAL2_OPTIONS: 0.0
SERIAL3_OPTIONS: 0.0
SERIAL4_OPTIONS: 0.0
SERIAL5_OPTIONS: 0.0
SERIAL6_OPTIONS: 0.0
SERIAL_PASS1: 0.0
SERIAL_PASS2: -1.0
SERIAL_PASSTIMO: 15.0
SERIAL7_PROTOCOL: 2.0
SERIAL7_BAUD: 115200.0
SERIAL7_OPTIONS: 0.0
TELEM_DELAY: 0.0
GCS_PID_MASK: 0.0
RTL_ALT: 3000.0
RTL_CONE_SLOPE: 3.0
RTL_SPEED: 0.0
RTL_ALT_FINAL: 0.0
RTL_CLIMB_MIN: 0.0
RTL_LOIT_TIME: 500.0
RTL_ALT_TYPE: 0.0
FS_GCS_ENABLE: 1.0
GPS_HDOP_GOOD: 140.0
SUPER_SIMPLE: 0.0
WP_YAW_BEHAVIOR: 2.0
LAND_SPEED: 50.0
LAND_SPEED_HIGH: 0.0
PILOT_SPEED_UP: 250.0
PILOT_ACCEL_Z: 250.0
FS_THR_ENABLE: 1.0
FS_THR_VALUE: 975.0
THR_DZ: 100.0
FLTMODE1: 5.0
FLTMODE2: 5.0
FLTMODE3: 5.0
FLTMODE4: 5.0
FLTMODE5: 5.0
FLTMODE6: 6.0
FLTMODE_CH: 6.0
INITIAL_MODE: 0.0
SIMPLE: 0.0
LOG_BITMASK: 176126.0
ESC_CALIBRATION: 0.0
TUNE: 0.0
FRAME_TYPE: 1.0
ARMING_ACCTHRESH: 0.75
ARMING_RUDDER: 2.0
ARMING_MIS_ITEMS: 0.0
ARMING_CHECK: 1.0
ARMING_OPTIONS: 0.0
DISARM_DELAY: 10.0
ANGLE_MAX: 3000.0
PHLD_BRAKE_RATE: 8.0
PHLD_BRAKE_ANGLE: 3000.0
LAND_REPOSITION: 1.0
FS_EKF_ACTION: 1.0
FS_EKF_THRESH: 0.800000011920929
FS_CRASH_CHECK: 1.0
RC_SPEED: 490.0
ACRO_BAL_ROLL: 1.0
ACRO_BAL_PITCH: 1.0
ACRO_TRAINER: 2.0
CAM_MAX_ROLL: 0.0
CAM_AUTO_ONLY: 0.0
CAM1_TYPE: 2.0
CAM1_DURATION: 0.5
CAM1_SERVO_ON: 1900.0
CAM1_SERVO_OFF: 1100.0
CAM1_TRIGG_DIST: 0.0
CAM1_RELAY_ON: 1.0
CAM1_INTRVAL_MIN: 2.5
CAM1_FEEDBAK_PIN: -1.0
CAM1_FEEDBAK_POL: 1.0
CAM2_TYPE: 6.0
CAM2_DURATION: 0.10000000149011612
CAM2_SERVO_ON: 1300.0
CAM2_SERVO_OFF: 1100.0
CAM2_TRIGG_DIST: 0.0
CAM2_RELAY_ON: 1.0
CAM2_INTRVAL_MIN: 0.0
CAM2_FEEDBAK_PIN: -1.0
CAM2_FEEDBAK_POL: 1.0
RELAY_PIN: 108.0
RELAY_PIN2: -1.0
RELAY_PIN3: -1.0
RELAY_PIN4: -1.0
RELAY_DEFAULT: 0.0
RELAY_PIN5: -1.0
RELAY_PIN6: -1.0
CHUTE_ENABLED: 0.0
LGR_ENABLE: 0.0
COMPASS_OFS_X: 59.04372787475586
COMPASS_OFS_Y: 22.636859893798828
COMPASS_OFS_Z: 16.316762924194336
COMPASS_DEC: 0.43461617827415466
COMPASS_LEARN: 0.0
COMPASS_USE: 1.0
COMPASS_AUTODEC: 1.0
COMPASS_MOTCT: 0.0
COMPASS_MOT_X: 0.0
COMPASS_MOT_Y: 0.0
COMPASS_MOT_Z: 0.0
COMPASS_ORIENT: 0.0
COMPASS_EXTERNAL: 0.0
COMPASS_OFS2_X: 20.738725662231445
COMPASS_OFS2_Y: 32.568031311035156
COMPASS_OFS2_Z: 23.510894775390625
COMPASS_MOT2_X: 0.0
COMPASS_MOT2_Y: 0.0
COMPASS_MOT2_Z: 0.0
COMPASS_OFS3_X: 45.359619140625
COMPASS_OFS3_Y: 98.01114654541016
COMPASS_OFS3_Z: 40.31854248046875
COMPASS_MOT3_X: 0.0
COMPASS_MOT3_Y: 0.0
COMPASS_MOT3_Z: 0.0
COMPASS_DEV_ID: 658433.0
COMPASS_DEV_ID2: 658953.0
COMPASS_DEV_ID3: 0.0
COMPASS_USE2: 1.0
COMPASS_ORIENT2: 6.0
COMPASS_EXTERN2: 1.0
COMPASS_USE3: 1.0
COMPASS_ORIENT3: 0.0
COMPASS_EXTERN3: 0.0
COMPASS_DIA_X: 0.9873450994491577
COMPASS_DIA_Y: 1.0451915264129639
COMPASS_DIA_Z: 1.0011500120162964
COMPASS_ODI_X: -0.008948312141001225
COMPASS_ODI_Y: -0.003143231151625514
COMPASS_ODI_Z: -0.10354256629943848
COMPASS_DIA2_X: 1.0591179132461548
COMPASS_DIA2_Y: 0.9531747698783875
COMPASS_DIA2_Z: 0.998706042766571
COMPASS_ODI2_X: 0.005142141133546829
COMPASS_ODI2_Y: 0.08852104842662811
COMPASS_ODI2_Z: 0.059311509132385254
COMPASS_DIA3_X: 1.0
COMPASS_DIA3_Y: 1.0
COMPASS_DIA3_Z: 1.0
COMPASS_ODI3_X: 0.0
COMPASS_ODI3_Y: 0.0
COMPASS_ODI3_Z: 0.0
COMPASS_CAL_FIT: 16.0
COMPASS_OFFS_MAX: 1800.0
COMPASS_PMOT_EN: 0.0
COMPASS_TYPEMASK: 0.0
COMPASS_FLTR_RNG: 0.0
COMPASS_AUTO_ROT: 2.0
COMPASS_PRIO1_ID: 658433.0
COMPASS_PRIO2_ID: 658953.0
COMPASS_PRIO3_ID: 0.0
COMPASS_ENABLE: 1.0
COMPASS_SCALE: 0.0
COMPASS_SCALE2: 0.0
COMPASS_SCALE3: 0.0
COMPASS_OPTIONS: 0.0
COMPASS_DEV_ID4: 0.0
COMPASS_DEV_ID5: 0.0
COMPASS_DEV_ID6: 0.0
COMPASS_DEV_ID7: 0.0
COMPASS_DEV_ID8: 0.0
INS_GYROFFS_X: 0.004141105338931084
INS_GYROFFS_Y: -0.01659642904996872
INS_GYROFFS_Z: -0.0038545913994312286
INS_GYR2OFFS_X: -0.0026801349595189095
INS_GYR2OFFS_Y: -0.0008279753383249044
INS_GYR2OFFS_Z: 0.0028306525200605392
INS_ACCSCAL_X: 1.0007152557373047
INS_ACCSCAL_Y: 0.9993409514427185
INS_ACCSCAL_Z: 1.0015047788619995
INS_ACCOFFS_X: 0.017316000536084175
INS_ACCOFFS_Y: 0.035424407571554184
INS_ACCOFFS_Z: -0.06230347603559494
INS_ACC2SCAL_X: 0.996779203414917
INS_ACC2SCAL_Y: 0.989189863204956
INS_ACC2SCAL_Z: 0.9819318056106567
INS_ACC2OFFS_X: -0.20175372064113617
INS_ACC2OFFS_Y: 0.06577982008457184
INS_ACC2OFFS_Z: 0.1863088607788086
INS_GYRO_FILTER: 20.0
INS_ACCEL_FILTER: 20.0
INS_USE: 1.0
INS_USE2: 1.0
INS_STILL_THRESH: 2.5
INS_GYR_CAL: 1.0
INS_TRIM_OPTION: 1.0
INS_ACC_BODYFIX: 2.0
INS_POS1_X: 0.0
INS_POS1_Y: 0.0
INS_POS1_Z: 0.0
INS_POS2_X: 0.0
INS_POS2_Y: 0.0
INS_POS2_Z: 0.0
INS_GYR_ID: 3408650.0
INS_GYR2_ID: 2687242.0
INS_ACC_ID: 3408650.0
INS_ACC2_ID: 2687498.0
INS_FAST_SAMPLE: 3.0
INS_LOG_BAT_CNT: 1024.0
INS_LOG_BAT_MASK: 0.0
INS_LOG_BAT_OPT: 0.0
INS_LOG_BAT_LGIN: 20.0
INS_LOG_BAT_LGCT: 32.0
INS_ENABLE_MASK: 127.0
INS_HNTCH_ENABLE: 0.0
INS_HNTC2_ENABLE: 0.0
INS_GYRO_RATE: 1.0
INS_TCAL1_ENABLE: 0.0
INS_TCAL2_ENABLE: 0.0
INS_ACC1_CALTEMP: 44.323673248291016
INS_GYR1_CALTEMP: 18.719806671142578
INS_ACC2_CALTEMP: 43.0
INS_GYR2_CALTEMP: 9.0
INS_TCAL_OPTIONS: 0.0
WPNAV_SPEED: 1000.0
WPNAV_RADIUS: 200.0
WPNAV_SPEED_UP: 250.0
WPNAV_SPEED_DN: 150.0
WPNAV_ACCEL: 250.0
WPNAV_ACCEL_Z: 100.0
WPNAV_RFND_USE: 1.0
WPNAV_JERK: 1.0
WPNAV_TER_MARGIN: 10.0
WPNAV_ACCEL_C: 0.0
LOIT_ANG_MAX: 0.0
LOIT_SPEED: 1250.0
LOIT_ACC_MAX: 500.0
LOIT_BRK_ACCEL: 250.0
LOIT_BRK_JERK: 500.0
LOIT_BRK_DELAY: 1.0
CIRCLE_RADIUS: 1000.0
CIRCLE_RATE: 20.0
CIRCLE_OPTIONS: 1.0
ATC_SLEW_YAW: 6000.0
ATC_ACCEL_Y_MAX: 27000.0
ATC_RATE_FF_ENAB: 1.0
ATC_ACCEL_R_MAX: 110000.0
ATC_ACCEL_P_MAX: 110000.0
ATC_ANGLE_BOOST: 1.0
ATC_ANG_RLL_P: 4.5
ATC_ANG_PIT_P: 4.5
ATC_ANG_YAW_P: 4.5
ATC_ANG_LIM_TC: 1.0
ATC_RATE_R_MAX: 0.0
ATC_RATE_P_MAX: 0.0
ATC_RATE_Y_MAX: 0.0
ATC_INPUT_TC: 0.15000000596046448
ATC_RAT_RLL_P: 0.13500000536441803
ATC_RAT_RLL_I: 0.13500000536441803
ATC_RAT_RLL_D: 0.003599999938160181
ATC_RAT_RLL_FF: 0.0
ATC_RAT_RLL_IMAX: 0.5
ATC_RAT_RLL_FLTT: 20.0
ATC_RAT_RLL_FLTE: 0.0
ATC_RAT_RLL_FLTD: 20.0
ATC_RAT_RLL_SMAX: 0.0
ATC_RAT_PIT_P: 0.13500000536441803
ATC_RAT_PIT_I: 0.13500000536441803
ATC_RAT_PIT_D: 0.003599999938160181
ATC_RAT_PIT_FF: 0.0
ATC_RAT_PIT_IMAX: 0.5
ATC_RAT_PIT_FLTT: 20.0
ATC_RAT_PIT_FLTE: 0.0
ATC_RAT_PIT_FLTD: 20.0
ATC_RAT_PIT_SMAX: 0.0
ATC_RAT_YAW_P: 0.18000000715255737
ATC_RAT_YAW_I: 0.017999999225139618
ATC_RAT_YAW_D: 0.0
ATC_RAT_YAW_FF: 0.0
ATC_RAT_YAW_IMAX: 0.5
ATC_RAT_YAW_FLTT: 20.0
ATC_RAT_YAW_FLTE: 2.5
ATC_RAT_YAW_FLTD: 0.0
ATC_RAT_YAW_SMAX: 0.0
ATC_THR_MIX_MIN: 0.10000000149011612
ATC_THR_MIX_MAX: 0.5
ATC_THR_MIX_MAN: 0.10000000149011612
ATC_THR_G_BOOST: 0.0
PSC_POSZ_P: 1.0
PSC_VELZ_P: 5.0
PSC_VELZ_I: 0.0
PSC_VELZ_IMAX: 1000.0
PSC_VELZ_FLTE: 5.0
PSC_VELZ_D: 0.0
PSC_VELZ_FLTD: 5.0
PSC_VELZ_FF: 0.0
PSC_ACCZ_P: 0.5
PSC_ACCZ_I: 1.0
PSC_ACCZ_D: 0.0
PSC_ACCZ_FF: 0.0
PSC_ACCZ_IMAX: 800.0
PSC_ACCZ_FLTT: 0.0
PSC_ACCZ_FLTE: 20.0
PSC_ACCZ_FLTD: 0.0
PSC_ACCZ_SMAX: 0.0
PSC_POSXY_P: 1.0
PSC_VELXY_P: 2.0
PSC_VELXY_I: 1.0
PSC_VELXY_IMAX: 1000.0
PSC_VELXY_FLTE: 5.0
PSC_VELXY_D: 0.5
PSC_VELXY_FLTD: 5.0
PSC_VELXY_FF: 0.0
PSC_ANGLE_MAX: 0.0
PSC_JERK_XY: 5.0
PSC_JERK_Z: 5.0
SR0_RAW_SENS: 2.0
SR0_EXT_STAT: 2.0
SR0_RC_CHAN: 2.0
SR0_RAW_CTRL: 0.0
SR0_POSITION: 3.0
SR0_EXTRA1: 10.0
SR0_EXTRA2: 10.0
SR0_EXTRA3: 3.0
SR0_PARAMS: 0.0
SR0_ADSB: 0.0
SR1_RAW_SENS: 0.0
SR1_EXT_STAT: 0.0
SR1_RC_CHAN: 0.0
SR1_RAW_CTRL: 0.0
SR1_POSITION: 0.0
SR1_EXTRA1: 0.0
SR1_EXTRA2: 0.0
SR1_EXTRA3: 0.0
SR1_PARAMS: 0.0
SR1_ADSB: 0.0
SR2_RAW_SENS: 4.0
SR2_EXT_STAT: 4.0
SR2_RC_CHAN: 4.0
SR2_RAW_CTRL: 4.0
SR2_POSITION: 4.0
SR2_EXTRA1: 4.0
SR2_EXTRA2: 4.0
SR2_EXTRA3: 4.0
SR2_PARAMS: 0.0
SR2_ADSB: 4.0
SR3_RAW_SENS: 0.0
SR3_EXT_STAT: 0.0
SR3_RC_CHAN: 0.0
SR3_RAW_CTRL: 0.0
SR3_POSITION: 0.0
SR3_EXTRA1: 0.0
SR3_EXTRA2: 0.0
SR3_EXTRA3: 0.0
SR3_PARAMS: 0.0
SR3_ADSB: 0.0
SR4_RAW_SENS: 0.0
SR4_EXT_STAT: 0.0
SR4_RC_CHAN: 0.0
SR4_RAW_CTRL: 0.0
SR4_POSITION: 0.0
SR4_EXTRA1: 0.0
SR4_EXTRA2: 0.0
SR4_EXTRA3: 0.0
SR4_PARAMS: 0.0
SR4_ADSB: 0.0
AHRS_GPS_GAIN: 1.0
AHRS_GPS_USE: 1.0
AHRS_YAW_P: 0.20000000298023224
AHRS_RP_P: 0.20000000298023224
AHRS_WIND_MAX: 0.0
AHRS_TRIM_X: -0.0027168705128133297
AHRS_TRIM_Y: -0.022009948268532753
AHRS_TRIM_Z: 0.0
AHRS_ORIENTATION: 0.0
AHRS_COMP_BETA: 0.10000000149011612
AHRS_GPS_MINSATS: 6.0
AHRS_EKF_TYPE: 3.0
MNT1_TYPE: 0.0
MNT2_TYPE: 0.0
LOG_BACKEND_TYPE: 1.0
LOG_FILE_BUFSIZE: 200.0
LOG_DISARMED: 0.0
LOG_REPLAY: 0.0
LOG_FILE_DSRMROT: 0.0
LOG_MAV_BUFSIZE: 8.0
LOG_FILE_TIMEOUT: 5.0
LOG_FILE_MB_FREE: 500.0
LOG_FILE_RATEMAX: 0.0
LOG_MAV_RATEMAX: 0.0
LOG_DARM_RATEMAX: 0.0
BATT_MONITOR: 4.0
BATT_CAPACITY: 2800.0
BATT_SERIAL_NUM: -1.0
BATT_LOW_TIMER: 10.0
BATT_FS_VOLTSRC: 0.0
BATT_LOW_VOLT: 13.199999809265137
BATT_LOW_MAH: 0.0
BATT_CRT_VOLT: 12.800000190734863
BATT_CRT_MAH: 500.0
BATT_FS_LOW_ACT: 2.0
BATT_FS_CRT_ACT: 1.0
BATT_ARM_VOLT: 13.199999809265137
BATT_ARM_MAH: 1000.0
BATT_OPTIONS: 0.0
BATT_VOLT_PIN: 8.0
BATT_CURR_PIN: 4.0
BATT_VOLT_MULT: 18.008350372314453
BATT_AMP_PERVLT: 36.36399841308594
BATT_AMP_OFFSET: 0.0
BATT_VLT_OFFSET: 0.0
BATT2_MONITOR: 0.0
BATT3_MONITOR: 0.0
BATT4_MONITOR: 0.0
BATT5_MONITOR: 0.0
BATT6_MONITOR: 0.0
BATT7_MONITOR: 0.0
BATT8_MONITOR: 0.0
BATT9_MONITOR: 0.0
BRD_SER1_RTSCTS: 2.0
BRD_SER2_RTSCTS: 2.0
BRD_SAFETY_DEFLT: 1.0
BRD_SBUS_OUT: 0.0
BRD_SERIAL_NUM: 0.0
BRD_SAFETY_MASK: 16368.0
BRD_HEAT_TARG: 45.0
BRD_IO_ENABLE: 1.0
BRD_SAFETYOPTION: 3.0
BRD_RTC_TYPES: 1.0
BRD_RTC_TZ_MIN: 0.0
BRD_VBUS_MIN: 4.300000190734863
BRD_VSERVO_MIN: 0.0
BRD_SD_SLOWDOWN: 0.0
BRD_OPTIONS: 1.0
BRD_BOOT_DELAY: 0.0
BRD_HEAT_P: 50.0
BRD_HEAT_I: 0.07000000029802322
BRD_HEAT_IMAX: 70.0
BRD_HEAT_LOWMGN: 0.0
BRD_SD_MISSION: 0.0
CAN_P1_DRIVER: 0.0
CAN_P2_DRIVER: 0.0
CAN_D1_PROTOCOL: 1.0
CAN_D2_PROTOCOL: 1.0
CAN_SLCAN_CPORT: 0.0
CAN_SLCAN_SERNUM: -1.0
CAN_SLCAN_TIMOUT: 0.0
CAN_SLCAN_SDELAY: 1.0
CAN_LOGLEVEL: 0.0
SPRAY_ENABLE: 0.0
BARO1_GND_PRESS: 100785.3671875
BARO_GND_TEMP: 0.0
BARO_ALT_OFFSET: 0.0
BARO_PRIMARY: 0.0
BARO_EXT_BUS: -1.0
BARO2_GND_PRESS: 0.0
BARO3_GND_PRESS: 0.0
BARO_FLTR_RNG: 0.0
BARO_PROBE_EXT: 0.0
BARO1_DEVID: 751361.0
BARO2_DEVID: 0.0
BARO3_DEVID: 0.0
BARO1_WCF_ENABLE: 0.0
BARO2_WCF_ENABLE: 0.0
BARO3_WCF_ENABLE: 0.0
BARO_FIELD_ELV: 0.0
BARO_ALTERR_MAX: 2000.0
BARO_OPTIONS: 0.0
GPS_TYPE: 1.0
GPS_TYPE2: 0.0
GPS_NAVFILTER: 8.0
GPS_AUTO_SWITCH: 1.0
GPS_MIN_DGPS: 100.0
GPS_SBAS_MODE: 2.0
GPS_MIN_ELEV: -100.0
GPS_INJECT_TO: 127.0
GPS_SBP_LOGMASK: -256.0
GPS_RAW_DATA: 0.0
GPS_GNSS_MODE: 0.0
GPS_SAVE_CFG: 2.0
GPS_GNSS_MODE2: 0.0
GPS_AUTO_CONFIG: 1.0
GPS_RATE_MS: 200.0
GPS_RATE_MS2: 200.0
GPS_POS1_X: 0.0
GPS_POS1_Y: 0.0
GPS_POS1_Z: 0.0
GPS_POS2_X: 0.0
GPS_POS2_Y: 0.0
GPS_POS2_Z: 0.0
GPS_DELAY_MS: 0.0
GPS_DELAY_MS2: 0.0
GPS_BLEND_MASK: 5.0
GPS_BLEND_TC: 10.0
GPS_DRV_OPTIONS: 0.0
GPS_COM_PORT: 1.0
GPS_COM_PORT2: 1.0
GPS_MB1_TYPE: 0.0
GPS_MB2_TYPE: 0.0
GPS_PRIMARY: 0.0
GPS_CAN_NODEID1: 0.0
GPS_CAN_NODEID2: 0.0
GPS1_CAN_OVRIDE: 0.0
GPS2_CAN_OVRIDE: 0.0
SCHED_DEBUG: 0.0
SCHED_LOOP_RATE: 400.0
SCHED_OPTIONS: 0.0
AVOID_ENABLE: 3.0
AVOID_ANGLE_MAX: 1000.0
AVOID_DIST_MAX: 5.0
AVOID_MARGIN: 2.0
AVOID_BEHAVE: 0.0
AVOID_BACKUP_SPD: 0.75
AVOID_ALT_MIN: 0.0
AVOID_ACCEL_MAX: 3.0
AVOID_BACKUP_DZ: 0.10000000149011612
RALLY_TOTAL: 0.0
RALLY_LIMIT_KM: 0.30000001192092896
RALLY_INCL_HOME: 1.0
MOT_YAW_HEADROOM: 200.0
MOT_THST_EXPO: 0.6499999761581421
MOT_SPIN_MAX: 0.949999988079071
MOT_BAT_VOLT_MAX: 0.0
MOT_BAT_VOLT_MIN: 0.0
MOT_BAT_CURR_MAX: 0.0
MOT_PWM_TYPE: 5.0
MOT_PWM_MIN: 1000.0
MOT_PWM_MAX: 2000.0
MOT_SPIN_MIN: 0.15000000596046448
MOT_SPIN_ARM: 0.10000000149011612
MOT_BAT_CURR_TC: 5.0
MOT_THST_HOVER: 0.3484412133693695
MOT_HOVER_LEARN: 2.0
MOT_SAFE_DISARM: 0.0
MOT_SPOOL_TIME: 0.5
MOT_BOOST_SCALE: 0.0
MOT_BAT_IDX: 0.0
MOT_SLEW_UP_TIME: 0.0
MOT_SLEW_DN_TIME: 0.0
MOT_SAFE_TIME: 1.0
RCMAP_ROLL: 1.0
RCMAP_PITCH: 2.0
RCMAP_THROTTLE: 3.0
RCMAP_YAW: 4.0
EK2_ENABLE: 0.0
EK3_ENABLE: 1.0
EK3_VELNE_M_NSE: 0.30000001192092896
EK3_VELD_M_NSE: 0.5
EK3_VEL_I_GATE: 500.0
EK3_POSNE_M_NSE: 0.5
EK3_POS_I_GATE: 500.0
EK3_GLITCH_RAD: 25.0
EK3_ALT_M_NSE: 2.0
EK3_HGT_I_GATE: 500.0
EK3_HGT_DELAY: 60.0
EK3_MAG_M_NSE: 0.05000000074505806
EK3_MAG_CAL: 3.0
EK3_MAG_I_GATE: 300.0
EK3_EAS_M_NSE: 1.399999976158142
EK3_EAS_I_GATE: 400.0
EK3_RNG_M_NSE: 0.5
EK3_RNG_I_GATE: 500.0
EK3_MAX_FLOW: 2.5
EK3_FLOW_M_NSE: 0.25
EK3_FLOW_I_GATE: 300.0
EK3_FLOW_DELAY: 10.0
EK3_GYRO_P_NSE: 0.014999999664723873
EK3_ACC_P_NSE: 0.3499999940395355
EK3_GBIAS_P_NSE: 0.0010000000474974513
EK3_ABIAS_P_NSE: 0.019999999552965164
EK3_WIND_P_NSE: 0.20000000298023224
EK3_WIND_PSCALE: 1.0
EK3_GPS_CHECK: 31.0
EK3_IMU_MASK: 3.0
EK3_CHECK_SCALE: 100.0
EK3_NOAID_M_NSE: 10.0
EK3_BETA_MASK: 0.0
EK3_YAW_M_NSE: 0.5
EK3_YAW_I_GATE: 300.0
EK3_TAU_OUTPUT: 25.0
EK3_MAGE_P_NSE: 0.0010000000474974513
EK3_MAGB_P_NSE: 9.999999747378752e-05
EK3_RNG_USE_HGT: -1.0
EK3_TERR_GRAD: 0.10000000149011612
EK3_BCN_M_NSE: 1.0
EK3_BCN_I_GTE: 500.0
EK3_BCN_DELAY: 50.0
EK3_RNG_USE_SPD: 2.0
EK3_ACC_BIAS_LIM: 1.0
EK3_MAG_MASK: 0.0
EK3_OGN_HGT_MASK: 0.0
EK3_VIS_VERR_MIN: 0.10000000149011612
EK3_VIS_VERR_MAX: 0.8999999761581421
EK3_WENC_VERR: 0.10000000149011612
EK3_FLOW_USE: 1.0
EK3_HRT_FILT: 2.0
EK3_MAG_EF_LIM: 50.0
EK3_GSF_RUN_MASK: 3.0
EK3_GSF_USE_MASK: 3.0
EK3_GSF_RST_MAX: 2.0
EK3_ERR_THRESH: 0.20000000298023224
EK3_AFFINITY: 0.0
EK3_SRC1_POSXY: 3.0
EK3_SRC1_VELXY: 3.0
EK3_SRC1_POSZ: 1.0
EK3_SRC1_VELZ: 3.0
EK3_SRC1_YAW: 1.0
EK3_SRC2_POSXY: 0.0
EK3_SRC2_VELXY: 0.0
EK3_SRC2_POSZ: 1.0
EK3_SRC2_VELZ: 0.0
EK3_SRC2_YAW: 0.0
EK3_SRC3_POSXY: 0.0
EK3_SRC3_VELXY: 0.0
EK3_SRC3_POSZ: 1.0
EK3_SRC3_VELZ: 0.0
EK3_SRC3_YAW: 0.0
EK3_SRC_OPTIONS: 1.0
EK3_DRAG_BCOEF_X: 0.0
EK3_DRAG_BCOEF_Y: 0.0
EK3_DRAG_M_NSE: 0.5
EK3_DRAG_MCOEF: 0.0
EK3_OGNM_TEST_SF: 2.0
EK3_GND_EFF_DZ: 4.0
EK3_PRIMARY: 0.0
EK3_LOG_LEVEL: 0.0
EK3_GPS_VACC_MAX: 0.0
MIS_TOTAL: 0.0
MIS_RESTART: 0.0
MIS_OPTIONS: 0.0
RSSI_TYPE: 0.0
RNGFND1_TYPE: 0.0
RNGFND2_TYPE: 0.0
RNGFND3_TYPE: 0.0
RNGFND4_TYPE: 0.0
RNGFND5_TYPE: 0.0
RNGFND6_TYPE: 0.0
RNGFND7_TYPE: 0.0
RNGFND8_TYPE: 0.0
RNGFND9_TYPE: 0.0
RNGFNDA_TYPE: 0.0
TERRAIN_ENABLE: 1.0
TERRAIN_SPACING: 100.0
TERRAIN_OPTIONS: 0.0
TERRAIN_MARGIN: 0.05000000074505806
TERRAIN_OFS_MAX: 30.0
FLOW_TYPE: 0.0
PLND_ENABLED: 0.0
RPM1_TYPE: 0.0
RPM2_TYPE: 0.0
ADSB_TYPE: 0.0
AVD_ENABLE: 0.0
NTF_LED_BRIGHT: 3.0
NTF_BUZZ_TYPES: 5.0
NTF_LED_OVERRIDE: 0.0
NTF_DISPLAY_TYPE: 0.0
NTF_BUZZ_PIN: -1.0
NTF_LED_TYPES: 123079.0
NTF_BUZZ_ON_LVL: 1.0
NTF_BUZZ_VOLUME: 100.0
NTF_LED_LEN: 1.0
THROW_MOT_START: 0.0
OSD_TYPE: 0.0
WP_NAVALT_MIN: 0.0
BTN_ENABLE: 0.0
THROW_NEXTMODE: 18.0
THROW_TYPE: 0.0
GND_EFFECT_COMP: 1.0
DEV_OPTIONS: 0.0
BCN_TYPE: 0.0
PRX_IGN_GND: 0.0
PRX_LOG_RAW: 0.0
PRX_FILT: 0.25
PRX_ALT_MIN: 1.0
PRX1_TYPE: 0.0
PRX2_TYPE: 0.0
PRX3_TYPE: 0.0
ACRO_THR_MID: 0.0
SYSID_ENFORCE: 0.0
STAT_BOOTCNT: 92.0
STAT_FLTTIME: 1031.0
STAT_RUNTIME: 131385.0
STAT_RESET: 250412944.0
GRIP_ENABLE: 0.0
FRAME_CLASS: 1.0
SERVO1_MIN: 1000.0
SERVO1_MAX: 2000.0
SERVO1_TRIM: 1000.0
SERVO1_REVERSED: 0.0
SERVO1_FUNCTION: 33.0
SERVO2_MIN: 1000.0
SERVO2_MAX: 2000.0
SERVO2_TRIM: 1000.0
SERVO2_REVERSED: 0.0
SERVO2_FUNCTION: 34.0
SERVO3_MIN: 1000.0
SERVO3_MAX: 2000.0
SERVO3_TRIM: 1000.0
SERVO3_REVERSED: 0.0
SERVO3_FUNCTION: 35.0
SERVO4_MIN: 1000.0
SERVO4_MAX: 2000.0
SERVO4_TRIM: 1000.0
SERVO4_REVERSED: 0.0
SERVO4_FUNCTION: 36.0
SERVO5_MIN: 1100.0
SERVO5_MAX: 1900.0
SERVO5_TRIM: 1500.0
SERVO5_REVERSED: 0.0
SERVO5_FUNCTION: 0.0
SERVO6_MIN: 1100.0
SERVO6_MAX: 1900.0
SERVO6_TRIM: 1500.0
SERVO6_REVERSED: 0.0
SERVO6_FUNCTION: 0.0
SERVO7_MIN: 1100.0
SERVO7_MAX: 1900.0
SERVO7_TRIM: 1500.0
SERVO7_REVERSED: 0.0
SERVO7_FUNCTION: 0.0
SERVO8_MIN: 1100.0
SERVO8_MAX: 1900.0
SERVO8_TRIM: 1500.0
SERVO8_REVERSED: 0.0
SERVO8_FUNCTION: -1.0
SERVO9_MIN: 1100.0
SERVO9_MAX: 1900.0
SERVO9_TRIM: 1500.0
SERVO9_REVERSED: 0.0
SERVO9_FUNCTION: 0.0
SERVO10_MIN: 1100.0
SERVO10_MAX: 1900.0
SERVO10_TRIM: 1500.0
SERVO10_REVERSED: 0.0
SERVO10_FUNCTION: 0.0
SERVO11_MIN: 1100.0
SERVO11_MAX: 1900.0
SERVO11_TRIM: 1500.0
SERVO11_REVERSED: 0.0
SERVO11_FUNCTION: 0.0
SERVO12_MIN: 1100.0
SERVO12_MAX: 1900.0
SERVO12_TRIM: 1500.0
SERVO12_REVERSED: 0.0
SERVO12_FUNCTION: 0.0
SERVO13_MIN: 1100.0
SERVO13_MAX: 1900.0
SERVO13_TRIM: 1500.0
SERVO13_REVERSED: 0.0
SERVO13_FUNCTION: 0.0
SERVO14_MIN: 1100.0
SERVO14_MAX: 1900.0
SERVO14_TRIM: 1500.0
SERVO14_REVERSED: 0.0
SERVO14_FUNCTION: 0.0
SERVO15_MIN: 1100.0
SERVO15_MAX: 1900.0
SERVO15_TRIM: 1500.0
SERVO15_REVERSED: 0.0
SERVO15_FUNCTION: 0.0
SERVO16_MIN: 1100.0
SERVO16_MAX: 1900.0
SERVO16_TRIM: 1500.0
SERVO16_REVERSED: 0.0
SERVO16_FUNCTION: 0.0
SERVO_RATE: 50.0
SERVO_VOLZ_MASK: 0.0
SERVO_SBUS_RATE: 50.0
SERVO_BLH_MASK: 0.0
SERVO_BLH_AUTO: 0.0
SERVO_BLH_TEST: 0.0
SERVO_BLH_TMOUT: 0.0
SERVO_BLH_TRATE: 10.0
SERVO_BLH_DEBUG: 0.0
SERVO_BLH_OTYPE: 0.0
SERVO_BLH_PORT: 0.0
SERVO_BLH_POLES: 14.0
SERVO_BLH_3DMASK: 0.0
SERVO_BLH_RVMASK: 0.0
SERVO_ROB_POSMIN: 0.0
SERVO_ROB_POSMAX: 4095.0
SERVO_FTW_MASK: 0.0
SERVO_FTW_RVMASK: 0.0
SERVO_FTW_POLES: 14.0
SERVO_DSHOT_RATE: 0.0
SERVO_DSHOT_ESC: 0.0
SERVO_GPIO_MASK: 0.0
SERVO_32_ENABLE: 0.0
RC1_MIN: 989.0
RC1_TRIM: 1501.0
RC1_MAX: 2011.0
RC1_REVERSED: 0.0
RC1_DZ: 20.0
RC1_OPTION: 0.0
RC2_MIN: 988.0
RC2_TRIM: 1504.0
RC2_MAX: 2011.0
RC2_REVERSED: 0.0
RC2_DZ: 20.0
RC2_OPTION: 0.0
RC3_MIN: 988.0
RC3_TRIM: 988.0
RC3_MAX: 2011.0
RC3_REVERSED: 0.0
RC3_DZ: 30.0
RC3_OPTION: 0.0
RC4_MIN: 988.0
RC4_TRIM: 1498.0
RC4_MAX: 2011.0
RC4_REVERSED: 0.0
RC4_DZ: 20.0
RC4_OPTION: 0.0
RC5_MIN: 1000.0
RC5_TRIM: 1500.0
RC5_MAX: 2000.0
RC5_REVERSED: 0.0
RC5_DZ: 0.0
RC5_OPTION: 153.0
RC6_MIN: 1000.0
RC6_TRIM: 1500.0
RC6_MAX: 2000.0
RC6_REVERSED: 0.0
RC6_DZ: 0.0
RC6_OPTION: 0.0
RC7_MIN: 1000.0
RC7_TRIM: 1500.0
RC7_MAX: 2000.0
RC7_REVERSED: 0.0
RC7_DZ: 0.0
RC7_OPTION: 0.0
RC8_MIN: 1000.0
RC8_TRIM: 1500.0
RC8_MAX: 2000.0
RC8_REVERSED: 0.0
RC8_DZ: 0.0
RC8_OPTION: 0.0
RC9_MIN: 1000.0
RC9_TRIM: 1500.0
RC9_MAX: 2000.0
RC9_REVERSED: 0.0
RC9_DZ: 0.0
RC9_OPTION: 0.0
RC10_MIN: 1000.0
RC10_TRIM: 1500.0
RC10_MAX: 2000.0
RC10_REVERSED: 0.0
RC10_DZ: 0.0
RC10_OPTION: 0.0
RC11_MIN: 1000.0
RC11_TRIM: 1500.0
RC11_MAX: 2000.0
RC11_REVERSED: 0.0
RC11_DZ: 0.0
RC11_OPTION: 0.0
RC12_MIN: 1000.0
RC12_TRIM: 1500.0
RC12_MAX: 2000.0
RC12_REVERSED: 0.0
RC12_DZ: 0.0
RC12_OPTION: 0.0
RC13_MIN: 1000.0
RC13_TRIM: 1500.0
RC13_MAX: 2000.0
RC13_REVERSED: 0.0
RC13_DZ: 0.0
RC13_OPTION: 0.0
RC14_MIN: 1000.0
RC14_TRIM: 1500.0
RC14_MAX: 2000.0
RC14_REVERSED: 0.0
RC14_DZ: 0.0
RC14_OPTION: 0.0
RC15_MIN: 1000.0
RC15_TRIM: 1500.0
RC15_MAX: 2000.0
RC15_REVERSED: 0.0
RC15_DZ: 0.0
RC15_OPTION: 0.0
RC16_MIN: 1000.0
RC16_TRIM: 1500.0
RC16_MAX: 2000.0
RC16_REVERSED: 0.0
RC16_DZ: 0.0
RC16_OPTION: 0.0
RC_OVERRIDE_TIME: 3.0
RC_OPTIONS: 32.0
RC_PROTOCOLS: 1.0
RC_FS_TIMEOUT: 1.0
TCAL_ENABLED: 0.0
SRTL_ACCURACY: 2.0
SRTL_POINTS: 300.0
SRTL_OPTIONS: 0.0
WINCH_TYPE: 0.0
PILOT_SPEED_DN: 0.0
LAND_ALT_LOW: 1000.0
FHLD_XY_P: 0.20000000298023224
FHLD_XY_I: 0.30000001192092896
FHLD_XY_IMAX: 3000.0
FHLD_XY_FILT_HZ: 5.0
FHLD_FLOW_MAX: 0.6000000238418579
FHLD_FILT_HZ: 5.0
FHLD_QUAL_MIN: 10.0
FHLD_BRAKE_RATE: 8.0
FOLL_ENABLE: 0.0
AUTOTUNE_AXES: 7.0
AUTOTUNE_AGGR: 0.10000000149011612
AUTOTUNE_MIN_D: 0.0010000000474974513
SCR_ENABLE: 0.0
TUNE_MIN: 0.0
TUNE_MAX: 0.0
OA_TYPE: 0.0
SID_AXIS: 0.0
FS_VIBE_ENABLE: 1.0
FS_OPTIONS: 16.0
ZIGZ_AUTO_ENABLE: 0.0
ACRO_OPTIONS: 0.0
AUTO_OPTIONS: 0.0
GUID_OPTIONS: 0.0
FS_GCS_TIMEOUT: 5.0
RTL_OPTIONS: 0.0
FLIGHT_OPTIONS: 0.0
RNGFND_FILT: 0.5
GUID_TIMEOUT: 3.0
SURFTRAK_MODE: 1.0
FS_DR_ENABLE: 2.0
FS_DR_TIMEOUT: 30.0
ACRO_RP_RATE: 360.0
ACRO_RP_EXPO: 0.30000001192092896
ACRO_RP_RATE_TC: 0.0
ACRO_Y_RATE: 202.5
ACRO_Y_EXPO: 0.0
ACRO_Y_RATE_TC: 0.0
PILOT_Y_RATE: 202.5
PILOT_Y_EXPO: 0.0
PILOT_Y_RATE_TC: 0.0
TKOFF_SLEW_TIME: 2.0
TKOFF_RPM_MIN: 0.0
WVANE_ENABLE: 0.0
PLDP_THRESH: 0.8999999761581421
PLDP_RNG_MIN: 0.0
PLDP_DELAY: 0.0
PLDP_SPEED_DN: 0.0
SURFTRAK_TC: 1.0
CAM_RC_TYPE: 0.0
FFT_ENABLE: 0.0
VISO_TYPE: 0.0
VTX_ENABLE: 0.0
MSP_OSD_NCELLS: 0.0
MSP_OPTIONS: 0.0
FRSKY_UPLINK_ID: 13.0
FRSKY_DNLINK1_ID: 20.0
FRSKY_DNLINK2_ID: 7.0
FRSKY_DNLINK_ID: 27.0
FRSKY_OPTIONS: 0.0
GEN_TYPE: 0.0
EAHRS_TYPE: 0.0
EFI_TYPE: 0.0
ARSPD_ENABLE: 0.0
CUST_ROT_ENABLE: 0.0
ESC_TLM_MAV_OFS: 0.0
FENCE_ENABLE: 1.0
FENCE_TYPE: 3.0
FENCE_ACTION: 1.0
FENCE_ALT_MAX: 35.0
FENCE_RADIUS: 50.0
FENCE_MARGIN: 2.0
FENCE_TOTAL: 6.0
FENCE_ALT_MIN: -10.0
NMEA_RATE_MS: 100.0
NMEA_MSG_EN: 3.0


dji exif keys
['Exif.Image.ImageDescription', 'Exif.Image.Make', 'Exif.Image.Model', 'Exif.Image.Orientation', 'Exif.Image.XResolution', 'Exif.Image.YResolution', 'Exif.Image.ResolutionUnit', 'Exif.Image.Software', 'Exif.Image.DateTime', 'Exif.Image.YCbCrPositioning', 'Exif.Image.ExifTag', 'Exif.Photo.ExposureTime', 'Exif.Photo.FNumber', 'Exif.Photo.ExposureProgram', 'Exif.Photo.ISOSpeedRatings', 'Exif.Photo.ExifVersion', 'Exif.Photo.DateTimeOriginal', 'Exif.Photo.DateTimeDigitized', 'Exif.Photo.ComponentsConfiguration', 'Exif.Photo.CompressedBitsPerPixel', 'Exif.Photo.ShutterSpeedValue', 'Exif.Photo.ApertureValue', 'Exif.Photo.ExposureBiasValue', 'Exif.Photo.MaxApertureValue', 'Exif.Photo.SubjectDistance', 'Exif.Photo.MeteringMode', 'Exif.Photo.LightSource', 'Exif.Photo.Flash', 'Exif.Photo.FocalLength', 'Exif.Photo.MakerNote', 'Exif.Photo.FlashpixVersion', 'Exif.Photo.ColorSpace', 'Exif.Photo.PixelXDimension', 'Exif.Photo.PixelYDimension', 'Exif.Photo.InteroperabilityTag', 'Exif.Iop.InteroperabilityIndex', 'Exif.Iop.InteroperabilityVersion', 'Exif.Photo.ExposureIndex', 'Exif.Photo.FileSource', 'Exif.Photo.SceneType', 'Exif.Photo.CustomRendered', 'Exif.Photo.ExposureMode', 'Exif.Photo.WhiteBalance', 'Exif.Photo.DigitalZoomRatio', 'Exif.Photo.FocalLengthIn35mmFilm', 'Exif.Photo.SceneCaptureType', 'Exif.Photo.GainControl', 'Exif.Photo.Contrast', 'Exif.Photo.Saturation', 'Exif.Photo.Sharpness', 'Exif.Photo.SubjectDistanceRange', 'Exif.Photo.BodySerialNumber', 'Exif.Image.GPSTag', 'Exif.GPSInfo.GPSVersionID', 'Exif.GPSInfo.GPSLatitudeRef', 'Exif.GPSInfo.GPSLatitude', 'Exif.GPSInfo.GPSLongitudeRef', 'Exif.GPSInfo.GPSLongitude', 'Exif.GPSInfo.GPSAltitudeRef', 'Exif.GPSInfo.GPSAltitude', 'Exif.Image.XPComment', 'Exif.Image.XPKeywords', 'Exif.Thumbnail.Compression', 'Exif.Thumbnail.XResolution', 'Exif.Thumbnail.YResolution', 'Exif.Thumbnail.ResolutionUnit', 'Exif.Thumbnail.JPEGInterchangeFormat', 'Exif.Thumbnail.JPEGInterchangeFormatLength']

dji xmp keys:
['Xmp.xmp.ModifyDate', 'Xmp.xmp.CreateDate', 'Xmp.tiff.Make', 'Xmp.tiff.Model', 'Xmp.dc.format', 'Xmp.drone-dji.AbsoluteAltitude', 'Xmp.drone-dji.RelativeAltitude', 'Xmp.drone-dji.GpsLatitude', 'Xmp.drone-dji.GpsLongtitude', 'Xmp.drone-dji.GimbalRollDegree', 'Xmp.drone-dji.GimbalYawDegree', 'Xmp.drone-dji.GimbalPitchDegree', 'Xmp.drone-dji.FlightRollDegree', 'Xmp.drone-dji.FlightYawDegree', 'Xmp.drone-dji.FlightPitchDegree', 'Xmp.drone-dji.FlightXSpeed', 'Xmp.drone-dji.FlightYSpeed', 'Xmp.drone-dji.FlightZSpeed', 'Xmp.drone-dji.CamReverse', 'Xmp.drone-dji.GimbalReverse', 'Xmp.drone-dji.SelfData', 'Xmp.drone-dji.CalibratedFocalLength', 'Xmp.drone-dji.CalibratedOpticalCenterX', 'Xmp.drone-dji.CalibratedOpticalCenterY', 'Xmp.drone-dji.RtkFlag', 'Xmp.crs.Version', 'Xmp.crs.HasSettings', 'Xmp.crs.HasCrop', 'Xmp.crs.AlreadyApplied']


