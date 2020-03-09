# SHELLY
========== This plugin integrates Shelly wifi devices into Indigo. ======================  

 ++ No other software is needed ++  

The plugin can read the device status and can send commands to them,   
like relay on/off, light up, red=50% ..  
As soon as the shelly devices are properly configured the plugin will   
recognize them and add appropriate indigo devices, ready to be used  
  
== Here the steps:  
  
0. Setup indigo config.. set    
    > indigoIP#, port  used on shelly device to send actions to indigo   
    > curl or python connect is some older OSX versions use curl  
    > shelly device userid/passwd if enabled  

1.  Setup shelly device:  
    Using your phone connect wifi to shellyxxx AP wifi SSID in setup  
    > use browser to connect to 192.168.33.1 (that is a fixed ip#)  
    > setup your home wifi network parameter. I prefer using a fixed ip  
    > Restart;   
   On regular browser, connect to http://ip# you set with phone  
    > upgrade device if available  
    > add action: http://indigoIP:port/anyTextYouLike to the action fields  
    > switch eg relay on/off    
    > that should create a new device in indigo  
  
2.  To add more devices or do a refresh using indigo:  
    enter IP# in menu  
        "Start Shelly device discovery Process for ONE device" or .. "an IP RANGE"   
    It will query the IP# (range) and check for a propper shelly response   
    When a proper resonse is received, the plugin will try to add a new Shelly device   
     if does not already exist  

3. If not done in #1 in the shelly devices (http://ip#) add action url   
    http://indigoIP:port#/anyTextYouLike   
      on ALL shelly devices  
    That makes things faster, the device will send any changes to indigo,   
      where the plugin is listening on the given port  
    This is highly recommened for battery devices that go to sleep   
      and only wake up when sensors change (temp, hum, flood)  

4. if needed edit indigo Shelly device to tune parameters   
   > expiration time:  after waht time w/o message the device goes to "EXPIRED"   
   > polling time: how often should the plugiquerry the device  
   > status column: what to show in the status column (only for sensors)  
   > IP number: here you could change the IPnumber of the device .. not recommended  
   > Shelly MAC#: here you could change the mac of the device .. not recommended  
  
== How it works:  
The plugin is:   
(A) listening to any messages from the devices on port set in config)   
(B) polling the devices on a regular schedule (1/s .. min., set in dev edit)  
   > http://ip#/settings         gets basic config parameters (dev type, rssi, etc)  
   > http://ip#/status           gets live info eg temp, on/off, RGB, Power ...  
(C) setting parameters on shelly devices, eg:  
   > http://ip#/relay/0?turn=on/off  sets relay on/off  
   > http://ip#/color/0?red=200&green=50&blue=30  sets RGB values  
    etc.  
  
== Currently supported devices:
Shelly-1:                          12V 110-220V one basic relay  
Shelly-1PM:                        12V 110-220Vrelay with internal temp sensor ...  
Shelly-25 2-Relay:                 like two Shelly-1PM in one  
Shelly-Power 2 Channels - 1 Relay: 110-220V measures Power, volt, has 1 relay  
Shelly Duo                         110-220V LED light bulb w color temperature  
Shelly-RGBW Light Bulb:            110-220V LED light bulb with 4 led (RGBW)  
Shelly-RGBW dimmer:                110-220V 4 led dimmer (PWM) for RGBW  
Shelly-Dimmer:                     110-222V dimmer  
Shelly-1 Temp-Hum:                 battery / usb powered Temp. and Hum. sensor  
Shelly-Flood-Temp:                 Flood alarm and Temperature sensor  
Shelly- external temp add on:      For Shelly-1 -PM for up to 3 oneWire Temp sensors  
  
== Coming up:   
Shelly Door Window                 Door/window open alarm  
Shelly other Bulbs                 110-220V LED  


