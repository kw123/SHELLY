# SHELLY
This plugin integrates Shelly wifi devices into Indigo.

No other software is needed. The plugin can read the device status 
and can send commands to them, like relay on/off, light up, red=50%..
As soon as the shelly devices are properly configured the plugin will 
recognize them and add appropriate indigo devices, ready to be used

To START,  here the basic steps:

0. Setup indigo config.. set indigIP#, port, curl or python connect 
   shelly device userid/passwd if set, etc

1.  Setup shelly device:
   Using phone connect wifi to shelly device wifi server in setup  
   Use browser to connect to 192.168.33.1 (that is a fixed ip#)
   Setup your home wifi network parameter. I prefer using a fixed ip
   Restart; on regular Browser connect http://ip#  
   upgrade device if available    
   add action: http://indigoIP:port/data to the action fields  
   switch eg relay on/off  
   that should create a new device in indigo  

2.  To add more devices enter IP# in "start shelly discovery process   
    for 1 or range of devices"that should create the new   
    shelly devices in indigo if not created by step 1  

3. If not done in #1 in the shelly devices (http://ip#) add action url http://indigoIP:port#/anything on ALL shelly devices
    That makes things faster, the device will send any changes to indigo, where the plugin is listening on the given port  
    This is highly recommened for battery devices that go to sleep and only wake up when sensors change (temp, hum, flood)

4. if needed edit indigo shelly device to tune parameters  
   expiration time, polling, status column.. 

How it works:  
The plugin is   
(A) listening to any messages from the devices (on port from config)   
(B) polling the devices on a regular schedule (1/sec .. minutes, set in dev edit)  
Using  commands http://ip#/settings --&gt; we get basic config parameters (rssi,etc)    
     and ip#/status --&gt; we get live info on devices, temp, on/off RGB, Power ...    
     set relay on/off --&gt; /relay/0?turn=on  /relay/0?turn=off    
     set RGB values -- &gt;  /color/0?red=200&amp;green=50&amp;blue=30    
etc.  

Currently supported devices:  
Shelly-1:                          one basic relay  
Shelly-1PM:                        relay with temp sensor and overload protection  
Shelly-25 2-Relay:                 like two Shelly-1PM in one  
Shelly-Power 2 Channels - 1 Relay: measures Power, voltage and has 1 relay  
Shelly-RGBW Light Bulb:          110-220V light bulb with 4 led  
Shelly-RGBW dimmer:                4 led dimmer  for red, blue, green and white  
Shelly-Dimmer:                     110-222V dimmer  
Shelly-1 Temp-Hum:                 battery / usb powered Temp. and Hum. sensor  
Shelly-Flood-Temp:                 Flood alarm and Temperature sensor  
Shelly Duo                         110-220V LED  

Coming up: 
Shelly Door Window                 Door/window open alarm  
Shelly Bulb                        110-220V LED  
Shelly Vintage A60                 110-220V LED  
