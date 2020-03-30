========== This plugin integrates Shelly wifi devices into Indigo. ======================   
   
 ++ No other software is needed, no special setup on Shellly devices ++   
   
The plugin can read the device status and can send commands to them,  
like relay on/off, light on, red=50% ..   
As soon as the shelly devices are setup (wifi, pi#) the plugin will be able  
to recognize them and add appropriate indigo devices, ready to be used.  
   
== Here the steps for setup  
   
(0)IN THE PLUGIN:  
   Setup indigo config.. set     
    - indigoIP#, port  used on shelly device to send actions to indigo  
    - shelly device userid/passwd if enabled  
    - some other parameter if needed .. use curl or python connect for some older OSX versions use curl  
   
(1) ONTHE SHELLY DEVICE 
    Setup shelly device as defned by the shelly manual: 
    Using your phone, connect wifi to shellyxxx AP wifi SSID in phone setup   
    - use browser to connect to 192.168.33.1 (that is a fixed ip#)   
    - setup your home wifi network parameter (SSID, PWD, IP). I prefer using a fixed IP#   
    - Restart.    
   Optional: On regular browser, connect to http://ip# you set with phone   
     upgrade device if available, set device parameters as needed  
   
(2) IN THE PLUGIN:  
    To add devices or do a refresh  
    enter IP# / range in menu   
        "Start Shelly device discovery Process for ONE device" or .. "an IP RANGE"  
    It will query the IP# (or range) and check for a propper shelly response    
    When a proper resonse is received, the plugin will try to add a new Shelly device  
     if does not already exist   
   
(3) OPTIONAL if needed:  
   Edit indigo Shelly device to tune parameters eg:  
    expiration time:  after what time w/o message the device goes to "EXPIRED"  
    polling time: how often should the plugiquerry the device  
    status column: what to show in the status column (only for sensors)  
    set relay and input settings eg default at power on, input button behavior etc  
    IP number: here you can change the IP number of the device  
   
== How it works:  
   
The plugin is:  
(A) listening to any messages from the devices a tcp port (set in config, default 7987)  
    the plugin will push action url settings to each shelly device  
    that causes the shelly device to SEND info to the plugin when anything changes  
(B) polling the devices on a regular schedule (1/s .. min., set in dev edit)  
     - http://ip#/settings         gets basic config parameters (dev type, rssi, etc)  
     - http://ip#/status           gets live info eg temp, on/off, RGB, Power ...  
(C) switching shelly devices, on/off set light eg:  
     - http://ip#/relay/0?turn=on/off  sets relay 0 on/off  
     - http://ip#/color/0?red=200&green=50&blue=30  sets RGB values  
    etc.  
(D) can set parameters on shelly devices (set in indigo device edit), with:  
     - http://ip#/settings/relay/0?btn_type=toggle     set input button to toggle/momentary/.. 
     - http://ip#/settings/light/0?default_state=last  set the power-on state to last/on/off  
    etc.  
== REMARKS:   
(A) The plugin will detect IP# changes for relay or temp devices automatically, 
      but not for light bulbs, as they do not send out any updates 
      you can change the IP# of the device in indigo device edit 
(B) You can set a shelly IP# to be ignored, then the plugin will not be updating anything for that device 
(C) There are a few utilities: print device info, push config to the shelly devices, mostly used for debugging 
   
== Currently supported devices:   
  fully tested:   
Shelly-1:                          12V 110-220V one basic relay  
Shelly-1PM:                        12V 110-220Vrelay with internal temp sensor ...  
Shelly-25 2-Relays:                like two Shelly-1PM in one - the plugin creates 2 devices: R1, R2 
                                   the second relay will be added as device: hostName-shellyswitch25-child-1
Shelly-EM Power 2 Ch. - 1 Relay:   110-220V measures Power, volt, has 1 relay - the plugin creates 3 devices: R + EM1 + EM2   
                                   the EM devices  will be added as device: hostName-shellyem-child-1/2
Shelly Duo                         110-220V LED light bulb w color temperature  
Shelly-RGBW Light Bulb:            110-220V LED light bulb with 4 led (RGBW)  
Shelly-RGBW dimmer:                110-220V 4 led dimmer (PWM) for RGBW  
Shelly-Dimmer:                     110-220V dimmer  
Shelly-1 Temp-Hum:                 battery / usb powered Temp. and Hum. sensor  
Shelly-Flood-Temp:                 Flood alarm and Temperature sensor  
Shelly- ext. oneWire Temp sensor:  External addon for Shelly-1 -1PM for up to 3 oneWire Temp sensors 
                                   the sensors will be added as devices: hostName-ext_temperature-# (1,2,3) 
Shelly- ext. DHT22  sensor:        External addon for Shelly-1 -1PM for 1 DHT22 T&H sensor 
                                   the sensor will be added as devices: hostName-ext_temperature-1 and  hostName-ext_humidity-1
  programmed, but not tested:   
Shelly-EM3 Power 3 Ch. - 1 Relay:  110-220V measures Power, volt, has 1 relay - the plugin creates 4 devices: R + EM1 + EM2 + EM3  
                                   the 3 EM  will be added as device: hostName-sheleeyEM3-child-1/2
Shelly-PRO4, 4 relay:              220V measures Power, volt, the plugin creates 4 relay devices 
                                   the 2-4 relays will be added as device: hostName-shellypro-child-# (1/2/3)
Shelly-Vintage Bulb:               110-220V LED light bulb vintage style  
Shelly Door Window                 Door/window open alarm  partially supported  
Shelly Plug PlugS                  power outlets w relay and power measurement  
   
=========================================================================================   
   

