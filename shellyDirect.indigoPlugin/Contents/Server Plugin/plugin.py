#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################
# shelly Plugin
# Developed by Karl Wachs
# karlwachs@me.com

import os
import sys
import subprocess
import pwd
import datetime
import time
import json
import copy
import math
import socket
import threading
import Queue
import cProfile
import pstats
import logging

#import pydevd_pycharm
#pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)

try:
	# noinspection PyUnresolvedReferences
	import indigo
except ImportError:
	pass
################################################################################
##########  Static parameters, not changed in pgm
################################################################################

## list of dev type, not used right now
_definedShellyDevicesAll		= ["shelly1","shelly1pm","shellyswitch25","shellyem","shellydimmer","ShellyBulbDuo","shellybulb","SHRGBW2","ShellyVintage","shellyflood","shellyht","shellydw","shellyem3","shellyplug","shellyplug-s","shelly4pro"]


##
_definedShellyDeviceswAction	= ["shelly1","shelly1pm","shellyswitch25","shellyem","shellydimmer","shellyflood","shellyht", "shellyem3","shellyplug","shellyplug-s","shelly4pro"]

## which types support battery status
_supportsBatteryLevel 			= ["shellyflood","shellyht","shellydw"]

## which child type 
_externalSensorDevTypes			= ["ext_temperature","ext_humidity"]
_childDevTypes					= {	"ext_temperature":{			"state":"Temperature",	"dataKey":"tC",	"nameExt":"_ext_Temp_"},
									"ext_humidity":{			"state":"Humidity",		"dataKey":"hum","nameExt":"_ext_hum_"},
									"shellyht-child":{			"state":"Humidity",		"dataKey":"hum","nameExt":"_hum_"},
									"shellyswitch25-child":{	"state":"",				"dataKey":"",	"nameExt":"_relay-2"},
									"shelly4pro-child":{		"state":"",				"dataKey":"",	"nameExt":"_relay-2"},
									"shellyem-child":{			"state":"",				"dataKey":"",	"nameExt":"_EM"}
								}

#http//ip:port/settings/?commands=
#eg: http//ip:port/settings/?external_power=1000
			   # key from props									comand to be send				looking for string to come back
settingCmds ={
			 "SENDTOSHELLYDEVICE-emeter_0_ctraf_type":			["settings/meter/0?ctraf_type",				"ctraf_type"],
			 "SENDTOSHELLYDEVICE-emeter_1_ctraf_type":			["settings/meter/1?ctraf_type",				"ctraf_type"],
			 "SENDTOSHELLYDEVICE-emeter_2_ctraf_type":			["settings/meter/2?ctraf_type",				"ctraf_type"],
			 "SENDTOSHELLYDEVICE-emeter_3_ctraf_type":			["settings/meter/3?ctraf_type",				"ctraf_type"],
			 "SENDTOSHELLYDEVICE-emeter_4_ctraf_type":			["settings/meter/4?ctraf_type",				"ctraf_type"],
			 "SENDTOSHELLYDEVICE-emeter_5_ctraf_type":			["settings/meter/5?ctraf_type",				"ctraf_type"],
			 "SENDTOSHELLYDEVICE-relay_0_max_power":			["settings/relay/0?max_power=",				"max_power"],
			 "SENDTOSHELLYDEVICE-relay_1_max_power":			["settings/relay/1?max_power=",				"max_power"],
			 "SENDTOSHELLYDEVICE-relay_2_max_power":			["settings/relay/2?max_power=",				"max_power"],
			 "SENDTOSHELLYDEVICE-relay_3_max_power":			["settings/relay/3?max_power=",				"max_power"],
			 "SENDTOSHELLYDEVICE-relay_4_max_power":			["settings/relay/4?max_power=",				"max_power"],
			 "SENDTOSHELLYDEVICE-relay_5_max_power":			["settings/relay/5?max_power=",				"max_power"],
			 "SENDTOSHELLYDEVICE-relay_0_default_state":		["settings/relay/0?default_state=",			"default_state"],
			 "SENDTOSHELLYDEVICE-relay_1_default_state":		["settings/relay/1?default_state=",			"default_state"],
			 "SENDTOSHELLYDEVICE-relay_2_default_state":		["settings/relay/2?default_state=",			"default_state"],
			 "SENDTOSHELLYDEVICE-relay_3_default_state":		["settings/relay/3?default_state=",			"default_state"],
			 "SENDTOSHELLYDEVICE-relay_4_default_state":		["settings/relay/4?default_state=",			"default_state"],
			 "SENDTOSHELLYDEVICE-relay_5_default_state":		["settings/relay/5?default_state=",			"default_state"],
			 "SENDTOSHELLYDEVICE-relay_0_btn_type":				["settings/relay/0?btn_type=",				"btn_type"],
			 "SENDTOSHELLYDEVICE-relay_1_btn_type":				["settings/relay/1?btn_type=",				"btn_type"],
			 "SENDTOSHELLYDEVICE-relay_2_btn_type":				["settings/relay/2?btn_type=",				"btn_type"],
			 "SENDTOSHELLYDEVICE-relay_3_btn_type":				["settings/relay/3?btn_type=",				"btn_type"],
			 "SENDTOSHELLYDEVICE-relay_4_btn_type":				["settings/relay/4?btn_type=",				"btn_type"],
			 "SENDTOSHELLYDEVICE-relay_5_btn_type":				["settings/relay/5?btn_type=",				"btn_type"],
			 "SENDTOSHELLYDEVICE-relay_0_btn_reverse":			["settings/relay/0?btn_reverse=",			"btn_reverse"],
			 "SENDTOSHELLYDEVICE-relay_1_btn_reverse":			["settings/relay/1?btn_reverse=",			"btn_reverse"],
			 "SENDTOSHELLYDEVICE-relay_2_btn_reverse":			["settings/relay/2?btn_reverse=",			"btn_reverse"],
			 "SENDTOSHELLYDEVICE-relay_3_btn_reverse":			["settings/relay/3?btn_reverse=",			"btn_reverse"],
			 "SENDTOSHELLYDEVICE-relay_4_btn_reverse":			["settings/relay/4?btn_reverse=",			"btn_reverse"],
			 "SENDTOSHELLYDEVICE-relay_5_btn_reverse":			["settings/relay/5?btn_reverse=",			"btn_reverse"],
			 "SENDTOSHELLYDEVICE-relay_0_name":					["settings/relay/0?name=",					"name"],
			 "SENDTOSHELLYDEVICE-relay_1_name":					["settings/relay/1?name=",					"name"],
			 "SENDTOSHELLYDEVICE-relay_2_name":					["settings/relay/2?name=",					"name"],
			 "SENDTOSHELLYDEVICE-relay_3_name":					["settings/relay/3?name=",					"name"],
			 "SENDTOSHELLYDEVICE-relay_4_name":					["settings/relay/4?name=",					"name"],
			 "SENDTOSHELLYDEVICE-relay_5_name":					["settings/relay/5?name=",					"name"],
			 "SENDTOSHELLYDEVICE-light_0_swap_inputs":			["settings/light/0?swap_inputs=",			"swap_inputs"],
			 "SENDTOSHELLYDEVICE-light_0_btn_reverse":			["settings/light/0?btn_reverse=",			"btn_reverse"],
			 "SENDTOSHELLYDEVICE-light_0_default_state":		["settings/light/0?default_state=",			"default_state"],
			 "SENDTOSHELLYDEVICE-light_0_name":					["settings/light/0?name=",					"name"],
			 "SENDTOSHELLYDEVICE-light_1_swap_inputs":			["settings/light/1?swap_inputs=",			"swap_inputs"],
			 "SENDTOSHELLYDEVICE-light_1_btn_reverse":			["settings/light/1?btn_reverse=",			"btn_reverse"],
			 "SENDTOSHELLYDEVICE-light_1_default_state":		["settings/light/1?default_state=",			"default_state"],
			 "SENDTOSHELLYDEVICE-light_1_name":					["settings/light/1?name=",					"name"],
			 "SENDTOSHELLYDEVICE-external_power":				["settings?external_power=",				"external_power"],
			 "SENDTOSHELLYDEVICE-temperature_offset":			["settings?temperature_offset=",			"temperature_offset"],
			 "SENDTOSHELLYDEVICE-humidity_offset":				["settings?humidity_offset=",				"humidity_offset"],
			 "SENDTOSHELLYDEVICE-temperature_threshold":		["settings?temperature_threshold=",			"temperature_threshold"],
			 "SENDTOSHELLYDEVICE-humidity_threshold":			["settings?humidity_threshold=",			"humidity_threshold"],
			 "SENDTOSHELLYDEVICE-temperature_units":			["settings?temperature_units=",				"temperature_unit"],  # sending temperature_units, receiving temperature_unit
			 "SENDTOSHELLYDEVICE-sleep_mode_period":			["settings?sleep_mode_period=",				"sleep_mode"],
			 "SENDTOSHELLYDEVICE-dark_threshold":				["settings?dark_threshold=",				"dark_threshold"],
			 "SENDTOSHELLYDEVICE-twilight_threshold":			["settings?twilight_threshold=",			"twilight_threshold"],
			 "SENDTOSHELLYDEVICE-tilt_enabled":					["settings?tilt_enabled=",					"tilt_enabled"],
			 "SENDTOSHELLYDEVICE-vibration_enabled":			["settings?vibration_enabled=",				"vibration_enabled"],
			 "SENDTOSHELLYDEVICE-max_power":					["settings?max_power=",						"max_power"],
			 "SENDTOSHELLYDEVICE-longpush_time":				["settings?longpush_time=",					"longpush_time"],
			 "SENDTOSHELLYDEVICE-mode":							["settings?mode=",							"mode"],
			 "SENDTOSHELLYDEVICE-power":						["settings/power/0?power=",					"power"],
			 "SENDTOSHELLYDEVICE-led_status_disable":			["settings?led_status_disable=",			"led_status_disable"],
			 "SENDTOSHELLYDEVICE-led_power_disable":			["settings?led_power_disable=",				"led_power_disable"],
			 "SENDTOSHELLYDEVICE-fade_rate":					["settings?fade_rate=",						"fade_rate"],
			 "SENDTOSHELLYDEVICE-transition":					["settings?transition=",					"transition"],
			 "SENDTOSHELLYDEVICE-min_brightness":				["settings?min_brightness=",				"min_brightness"],
			 "SENDTOSHELLYDEVICE-ext_sensors_temperature_unit":	["settings?ext_sensors_temperature_unit=",	"temperature_unit"],
			 "SENDTOSHELLYDEVICE-nightMode_enable":				["settings/night_mode?enabled=",			"night_mode"],
			 "SENDTOSHELLYDEVICE-nightMode_start_time":			["settings/night_mode?start_time=",			"start_time"],
			 "SENDTOSHELLYDEVICE-nightMode_end_time":			["settings/night_mode?end_time=",			"end_time"],
			 "SENDTOSHELLYDEVICE-brightness":					["settings/night_mode?brightness=",			"brightness"],
			 "SENDTOSHELLYDEVICE-pulse_mode":					["settings?pulse_mode=",					"pulse_mode"]
	}


## these are the properties of the shelly devices
_emptyProps ={	# switches
				"shellyplug-s":{"props":{"isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"", "pollingFrequency":-1, "automaticPollingFrequency":100, "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":   {"settings/relay/0?":{"btn_on_url":"input=on", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}},
						"childTypes_Sensors":["ext_temperature","ext_humidity"],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},
				"shellyplug":{"props":{"isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"", "pollingFrequency":-1, "automaticPollingFrequency":100, "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":   {"settings/relay/0?":{"btn_on_url":"input=on",  "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}},
						"childTypes_Sensors":["ext_temperature","ext_humidity"],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},
				"shelly1":{"props":{"isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"", "pollingFrequency":-1, "automaticPollingFrequency":100, "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":   {"settings/relay/0?":{"btn_on_url":"input=on", "btn_off_url":"input=off", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0", "longpush_url":"input=long", "shortpush_url":"input=short"}},
						"childTypes_Sensors":["ext_temperature","ext_humidity"],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},
			
				"shelly1pm":{"props":{"isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"childTypes_SplitDevices":["ext_temperature","ext_humidity"],
						"action_url":   {"settings/relay/0?":{"btn_on_url":"input=on", "btn_off_url":"input=off", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0", "longpush_url":"input=long", "shortpush_url":"input=short"}},
						"childTypes_Sensors":["ext_temperature","ext_humidity"],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

			 	"shellyswitch25":{"props":{"isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":True,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":   {"settings/relay/0?":{"btn_on_url":"input=on", "btn_off_url":"input=off", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0", "longpush_url":"input=long", "shortpush_url":"input=short"},
									     "settings/relay/1?":{"btn_on_url":"input=on", "btn_off_url":"input=off", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0", "longpush_url":"input=long", "shortpush_url":"input=short"}
									},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":["shellyswitch25-child"],
						"tempUnits":"C"
						},

			 	"shellyswitch25-child":{"props":{"isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":   {"settings/relay/0?":{"btn_on_url":"input=on", "btn_off_url":"input=off", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0", "longpush_url":"input=long", "shortpush_url":"input=short"},
									     "settings/relay/1?":{"btn_on_url":"input=on", "btn_off_url":"input=off", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0", "longpush_url":"input=long", "shortpush_url":"input=short"}
									},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},


			 	"shelly4pro":{"props":{"isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":True,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?","2":"relay/2?","3":"relay/3?"},
						"action_url":   {},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":["shelly4pro-child","shelly4pro-child","shelly4pro-child"],
						"tempUnits":"C"
						},

			 	"shelly4pro-child":{"props":{"isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?","2":"relay/2?","3":"relay/3?"},
						"action_url": {},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"shellyem":{"props":{"isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":True,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":{"settings/relay/0?":{ "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":["shellyem-child","shellyem-child"],
						"tempUnits":"C"
						},

				"shellyem-child":{"props":{"isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180,"displaySelect":"power"},
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":{},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"shellyem3":{"props":{"isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":True,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":{"settings/relay/0?":{ "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":["shellyem-child","shellyem-child"],
						"tempUnits":"C"
						},

				"shellyem3-child":{"props":{"isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180,"displaySelect":"power"},
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":{},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				# dimmers
				"shellydimmer":{"props":{"isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, 
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"WhiteTemperatureMin":3000, "WhiteTemperatureMax":6500,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":6,  "expirationSeconds":180},
						"rgbLimits":[1,255],
						"setPageActionPageOnShellyDev":{"white":"light/0?","white":"light/0?"},
						"action_url":   {"settings/light/0?":{
										"btn1_on_url":"input_0=on", "btn1_off_url":"input_0=off", "btn1_longpush_url":"input_0=long", "btn1_shortpush_url":"input_0=short",  
										"btn2_on_url":"input_1=on", "btn2_off_url":"input_1=off", "btn2_longpush_url":"input_1=long", "btn2_shortpush_url":"input_1=short",  
										"out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
									},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"ShellyBulbDuo":{"props":{"isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, 
						"SupportsColor":True, "SupportsRGB":False, "SupportsWhite":True, "SupportsWhiteTemperature":True, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":6,  "expirationSeconds":180},
						"WhiteTemperatureMin":2700, "WhiteTemperatureMax":6500,
						"rgbLimits":[1,255],
						"action_url":  {"settings/light/0?":{ "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}},
						"childTypes_Sensors":[],
						"setPageActionPageOnShellyDev":{"white":"light/0?","white":"light/0?"},
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"shellybulb":{"props":{"isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, 
						"SupportsColor":True, "SupportsRGB":True, "SupportsWhite":True, "SupportsWhiteTemperature":True, "SupportsRGBandWhiteSimultaneously":True, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":6,  "expirationSeconds":180},
						"WhiteTemperatureMin":3000, "WhiteTemperatureMax":6500,
						"rgbLimits":[1,255],
						"action_url":   {},
						"setPageActionPageOnShellyDev":{"white":"light/0?","color":"light/0?"},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},


				"ShellyVintage":{"props":{"isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, 
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":True, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":6,  "expirationSeconds":180},
						"WhiteTemperatureMin":3000, "WhiteTemperatureMax":6500,
						"rgbLimits":[1,255],
						"action_url":  {"settings/light/0?":{"out_on_url":"onOffState=1","out_off_url":"onOffState=0"}},
						"setPageActionPageOnShellyDev":{"white":"light/0?","color":"light/0?"},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"shellyrgbw2":{"props":{"isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, 
						"SupportsColor":True, "SupportsRGB":True, "SupportsWhite":True, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":True, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":6,  "expirationSeconds":180 },
						"WhiteTemperatureMin":3000, "WhiteTemperatureMax":6500,
						"rgbLimits":[1,255],
						"action_url":   {},
						"setPageActionPageOnShellyDev":{"white":"white/0?","color":"color/0?"},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				# sensors
				"shellydw":{"props":{"isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":60,  "expirationSeconds":50400,"displaySelect":"lux" },
						"WhiteTemperatureMin":3000, "WhiteTemperatureMax":6500,
						"rgbLimits":[1,255],
						"setPageActionPageOnShellyDev":{},
						"action_url":{"settings/?twilight_url=":{"none":"data?"},"settings/?dark_url=":{"none":"data?"}},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						}, 

				"shellyflood":{"props":{"isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":60,  "expirationSeconds":50400,"displaySelect":"Temperature" },
						"setPageActionPageOnShellyDev":{},
						"actionReturns":{"flood":["0","1"]},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						}, 

				"shellyht":{"props":{"isRelay":False, "devNo":0, "SupportsOnState":False, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":True,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":60,  "expirationSeconds":50400,"displaySelect":"Temperature"},
						"setPageActionPageOnShellyDev":{},
						"action_url":{"settings/?report_url=":{"none":"data?"}},
						"actionReturns":{},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":["shellyht-child"],
						"tempUnits":"C"
						},

				"shellyht-child":{"props":{"isRelay":False, "devNo":0, "SupportsOnState":False, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":60,  "expirationSeconds":50400,"displaySelect":"Humidity"},
						"setPageActionPageOnShellyDev":{},
						"action_url":{"settings/?report_url=":{"none":"data?"}},
						"actionReturns":{},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},
				"ext_temperature":{"props":{"isRelay":False, "devNo":0, "SupportsOnState":False, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"WhiteTemperatureMin":3000, "WhiteTemperatureMax":6500,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":60,  "expirationSeconds":180,"displaySelect":"Temperature"},
						"action_url":   {},
						"actionReturns":{},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},
				"ext_humidity":{"props":{"isRelay":False, "devNo":0, "SupportsOnState":False, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"WhiteTemperatureMin":3000, "WhiteTemperatureMax":6500,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":60,  "expirationSeconds":180,"displaySelect":"Humidity"},
						"action_url":   {},
						"actionReturns":{},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						}
			}
####  "children":{devtypeOfChild:{n:devidOfchild,n2:devIdofChild2}}"
####     eg      {"ext_temperature":{"1":123456,"3":534212},"ext_humidity":{"1":43256,"3":3214789}"shellyswitch25":{"1":123456}}
####  currently only for ex_temperature and shellyswitch25 the second relay

_sqlLoggerIgnoreStates			= "sensorvalue_ui, updateReason, lastStatusChange, displayStatus, lastMessageFromDevice, lastSuccessfullConfigPush"

_debugAreas 					= ["SetupDevices","HTTPlistener","Polling","Ping","Actions","SQLSuppresslog","Special","all"]

## this is devId --> ipnumber, copied to self.SHELLY[ip#] = copy.deepCopy(_emptyShelly)
_emptyShelly 					= { "ipNumber":"", "MAC":"", "lastCheck":0, "state":"", "reset":False, "lastActive":0, "queue":0, "deviceEnabled":False, "pollingFrequency":10, 
									"defaultTask":"status",  "expirationSeconds":100, "lastMessageFromDevice":0,  "lastMessage-Http":"",  "lastMessage-settings":"", "lastMessage-status":"","lastSuccessfullConfigPush":0,
									"isChild":False,"isParent":True,"parentIndigoId":0,"children":{}, "lastAlarm":0, "devTypeId":"", "now":False,"tempUnits":"C","threadNumber":0}

_colorSets 						= ["SupportsColor", "SupportsRGB", "SupportsWhite", "SupportsWhiteTemperature", "SupportsRGBandWhiteSimultaneously", "SupportsTwoWhiteLevels", "SupportsTwoWhiteLevelsSimultaneously"]

_GlobalConst_fillMinMaxStates 	= ["Temperature","Pressure","Humidity"]
_defaultDateStampFormat			= "%Y-%m-%d %H:%M:%S"

################################################################################
################################################################################
################################################################################

# 
# noinspection PySimplifyBooleanCheck,PySimplifyBooleanCheck,PySimplifyBooleanCheck,PySimplifyBooleanCheck,PySimplifyBooleanCheck,PySimplifyBooleanCheck,PySimplifyBooleanCheck,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyAttributeOutsideInit,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences,PyUnresolvedReferences
class Plugin(indigo.PluginBase):
####-------------------------------------------------------------------------####
	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)

		self.pluginShortName 			= "shellyDirect"

		self.quitNow					= ""
		self.getInstallFolderPath		= indigo.server.getInstallFolderPath()+"/"
		self.indigoPath					= indigo.server.getInstallFolderPath()+"/"
		self.indigoRootPath 			= indigo.server.getInstallFolderPath().split("Indigo")[0]
		self.pathToPlugin 				= self.completePath(os.getcwd())

		major, minor, release 			= map(int, indigo.server.version.split("."))
		self.indigoVersion 				= float(major)+float(minor)/10.
		self.indigoRelease 				= release
	

		self.pluginVersion				= pluginVersion
		self.pluginId					= pluginId
		self.pluginName					= pluginId.split(".")[-1]
		self.myPID						= os.getpid()
		self.pluginState				= "init"

		self.myPID 						= os.getpid()
		self.MACuserName				= pwd.getpwuid(os.getuid())[0]

		self.MAChome					= os.path.expanduser(u"~")
		self.userIndigoDir				= self.MAChome + "/indigo/"
		self.indigoPreferencesPluginDir = self.getInstallFolderPath+"Preferences/Plugins/"+self.pluginId+"/"
		self.indigoPluginDirOld			= self.userIndigoDir + self.pluginShortName+"/"
		self.PluginLogFile				= indigo.server.getLogsFolderPath(pluginId=self.pluginId) +"/plugin.log"


		formats=	{   logging.THREADDEBUG: "%(asctime)s %(msg)s",
						logging.DEBUG:       "%(asctime)s %(msg)s",
						logging.INFO:        "%(asctime)s %(msg)s",
						logging.WARNING:     "%(asctime)s %(msg)s",
						logging.ERROR:       "%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s",
						logging.CRITICAL:    "%(asctime)s.%(msecs)03d\t%(levelname)-12s\t%(name)s.%(funcName)-25s %(msg)s" }

		date_Format = { logging.THREADDEBUG: "%Y-%m-%d %H:%M:%S",
						logging.DEBUG:       "%Y-%m-%d %H:%M:%S",
						logging.INFO:        "%Y-%m-%d %H:%M:%S",
						logging.WARNING:     "%Y-%m-%d %H:%M:%S",
						logging.ERROR:       "%Y-%m-%d %H:%M:%S",
						logging.CRITICAL:    "%Y-%m-%d %H:%M:%S" }
		formatter = LevelFormatter(fmt="%(msg)s", datefmt="%Y-%m-%d %H:%M:%S", level_fmts=formats, level_date=date_Format)

		self.plugin_file_handler.setFormatter(formatter)
		self.indiLOG = logging.getLogger("Plugin")  
		self.indiLOG.setLevel(logging.THREADDEBUG)

		self.indigo_log_handler.setLevel(logging.WARNING)
		indigo.server.log("initializing	 ... ")

		indigo.server.log(  u"path To files:          =================")
		indigo.server.log(  u"indigo                  {}".format(self.indigoRootPath))
		indigo.server.log(  u"installFolder           {}".format(self.indigoPath))
		indigo.server.log(  u"plugin.py               {}".format(self.pathToPlugin))
		indigo.server.log(  u"Plugin params           {}".format(self.indigoPreferencesPluginDir))

		self.indiLOG.log( 0, "!!!!INFO ONLY!!!!  logger  enabled for   0             !!!!INFO ONLY!!!!")
		self.indiLOG.log( 5, "!!!!INFO ONLY!!!!  logger  enabled for   THREADDEBUG   !!!!INFO ONLY!!!!")
		self.indiLOG.log(10, "!!!!INFO ONLY!!!!  logger  enabled for   DEBUG         !!!!INFO ONLY!!!!")
		self.indiLOG.log(20, "!!!!INFO ONLY!!!!  logger  enabled for   INFO          !!!!INFO ONLY!!!!")
		self.indiLOG.log(30, "!!!!INFO ONLY!!!!  logger  enabled for   WARNING       !!!!INFO ONLY!!!!")
		self.indiLOG.log(40, "!!!!INFO ONLY!!!!  logger  enabled for   ERROR         !!!!INFO ONLY!!!!")
		self.indiLOG.log(50, "!!!!INFO ONLY!!!!  logger  enabled for   CRITICAL      !!!!INFO ONLY!!!!")

		indigo.server.log(  u"check                   {}  <<<<    for detailed logging".format(self.PluginLogFile))
		indigo.server.log(  u"Plugin short Name       {}".format(self.pluginShortName))
		indigo.server.log(  u"my PID                  {}".format(self.myPID))	 
		indigo.server.log(  u"set params for indigo V {}".format(self.indigoVersion))	 

####-------------------------------------------------------------------------####
	def __del__(self):
		indigo.PluginBase.__del__(self)

	###########################		INIT	## START ########################

####-------------------------------------------------------------------------####
	def startup(self):
		try:
			if self.pathToPlugin.find("/"+self.pluginName+".indigoPlugin/")==-1:
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"The pluginname is not correct, please reinstall or rename")
				self.errorLog(u"It should be   /Libray/....../Plugins/"+self.pluginName+".indigPlugin")
				p=max(0,self.pathToPlugin.find("/Contents/Server"))
				self.errorLog(u"It is: "+self.pathToPlugin[:p])
				self.errorLog(u"please check your download folder, delete old *.indigoPlugin files or this will happen again during next update")
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.sleep(100000)
				self.quitNOW="wromg plugin name"
				return

			if not self.checkPluginPath(self.pluginName,  self.pathToPlugin):
				exit()


			self.initFileDir()

			self.writeJson(self.pluginVersion, fName=self.indigoPreferencesPluginDir + "currentVersion")

			self.startTime = time.time()

			self.getDebugLevels()

			self.setVariables()

			self.checkcProfile()

			self.indiLOG.log(30," --V {}   initializing  -- ".format(self.pluginVersion))

			self.setupBasicFiles()

			self.startupFIXES()

			self.readConfig()

			self.resetMinMaxSensors(init=True)

			self.setSqlLoggerIgnoreStatesAndVariables()

			self.startHTTPListening()

 			self.indiLOG.log(10, "..  startup(self): setting variables, debug ..   finished, doing dev init")

		except Exception, e:
			self.indiLOG.log(50,u"--------------------------------------------------------------------------------------------------------------")
			self.indiLOG.log(50,u"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(50,u"Error in startup of plugin, waiting for 2000 secs then restarting plugin")
			self.indiLOG.log(50,u"--------------------------------------------------------------------------------------------------------------")
			self.sleep(2000)
			exit(1)
		return


####-------------------------------------------------------------------------####
	def initFileDir(self):

		try:
			if not os.path.exists(self.indigoPreferencesPluginDir):
				os.mkdir(self.indigoPreferencesPluginDir)

		except Exception, e:
			self.indiLOG.log(40,u"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 

	
	####-------------------------------------------------------------------------####
	def startupFIXES(self): # change old names used
		try:
			return 
		except Exception, e:
			self.indiLOG.log(40,u"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 




####-------------------------------------------------------------------------####
	def setupBasicFiles(self):
		try:
			return 
		except Exception, e:
			self.indiLOG.log(40,u"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 



####-------------------------------------------------------------------------####
	def getDebugLevels(self):
		try:
			self.debugLevel			= []
			for d in _debugAreas:
				if self.pluginPrefs.get(u"debug"+d, False): self.debugLevel.append(d)


		except Exception, e:
			self.indiLOG.log(50,u"--------------------------------------------------------------------------------------------------------------")
			self.indiLOG.log(50,u"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e) )
			self.indiLOG.log(50,u"Error in startup of plugin, plugin prefs are wrong ")
			self.indiLOG.log(50,u"--------------------------------------------------------------------------------------------------------------")
		return




####-------------------------------------------------------------------------####
	def setVariables(self):
		try:
			self.messagesQueue	  			= Queue.Queue()

			self.repeatConfigPush			= 3*24*60*60
			self.pushRequest 				= -1
			self.queueActive	  			= False
			self.SHELLY						= {}
			self.varExcludeSQLList			= {}
			self.queueList					= []
			self.doNotrestartDev			= ""
			self.executeUpdateStatesDictActive = ""
			self.updateStatesDict			= {}
			self.ipNumberRangeToTest		= []
			self.nextIPSCAN 				= ""
			self.ignoredIPNumbers 			= (self.pluginPrefs.get("ignoredIPNumbers", "")).split(",")
			self.setLogfile(self.pluginPrefs.get("logFileActive2", "standard"))
			self.unfiCurl					= self.pluginPrefs.get(u"unfiCurl", "/usr/bin/curl")
			if self.unfiCurl == "curl" or len(self.unfiCurl) < 4:
				self.unfiCurl = "/usr/bin/curl"
				self.pluginPrefs["unfiCurl"] = self.unfiCurl

			self.testHTTPsuccess			 = 0
			self.HTTPlisternerTestIP		= "127.0.0.1"
			try:
				xx = (self.pluginPrefs.get("SQLLoggingEnable", "on-on")).split("-")
				self.SQLLoggingEnable ={"devices":xx[0]=="on", "variables":xx[1]=="on"}
			except:
				self.SQLLoggingEnable ={"devices":False, "variables":False}

			try:
				self.tempUnits				= self.pluginPrefs.get(u"tempUnits", u"Celsius")
			except:
				self.tempUnits				= u"Celsius"

			try: 	self.tempDigits			 = int(self.pluginPrefs.get(u"tempDigits", 1))
			except:	self.tempDigits			 = 1

			try: 	self.energyDigits		 = int(self.pluginPrefs.get(u"energyDigits", 1))
			except:	self.energyDigits		 = 1

			try: 	self.powerDigits		 = int(self.pluginPrefs.get(u"powerDigits", 1))
			except:	self.powerDigits		 = 1

			try: 	self.voltageDigits		 = int(self.pluginPrefs.get(u"voltageDigits", 1))
			except:	self.voltageDigits		 = 1

			try: 	self.currentDigits		 = int(self.currentDigits.get(u"currentDigits", 1))
			except:	self.currentDigits		 = 1


			self.portOfIndigoServer			= int(self.pluginPrefs.get(u"portOfIndigoServer","7987"))
			self.portOfShellyDevices		= int(self.pluginPrefs.get(u"portOfShellyDevices","80"))

			self.userIDOfShellyDevices		= self.pluginPrefs.get(u"userIDOfShellyDevices", u"")
			self.passwordOfShellyDevices	= self.pluginPrefs.get(u"passwordOfShellyDevices", u"")
			self.IndigoServerIPNumber		= self.pluginPrefs.get(u"IndigoServerIPNumber", u"192.168.1.x")

			self.useCurlOrPymethod				= self.pluginPrefs.get(u"useCurlOrPymethod", "/usr/bin/curl")
			if self.useCurlOrPymethod == "curl" or len(self.useCurlOrPymethod) < 4:
				self.useCurlOrPymethod = "/usr/bin/curl"
				self.pluginPrefs["useCurlOrPymethod"] = self.useCurlOrPymethod

			self.indigoFolderName		= self.pluginPrefs.get(u"indigoFolderName", u"shelly")
			self.indigoFolderId = indigo.devices.folders.getId(self.indigoFolderName)
			if self.indigoFolderId == 0:
				try:
					ff = indigo.devices.folder.create(self.indigoFolderName)
					self.indigoFolderId = ff.id
				except Exception, e:
					self.indiLOG.log(40,u"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
					self.indigoFolderId =0
			

			self.pythonPath					= u"/usr/bin/python2.6"
			if os.path.isfile(u"/usr/bin/python2.7"):
				self.pythonPath				= u"/usr/bin/python2.7"
			elif os.path.isfile(u"/usr/bin/python2.6"):
				self.pythonPath				= u"/usr/bin/python2.6"

		except Exception, e:
			self.indiLOG.log(50,u"--------------------------------------------------------------------------------------------------------------")
			self.indiLOG.log(50,u"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(50,u"Error in startup of plugin, waiting for 2000 secs then restarting plugin")
			self.indiLOG.log(50,u"--------------------------------------------------------------------------------------------------------------")
			self.sleep(2000)
			exit(1)

		self.lastSaveConfig = 0

		return



####-------------------------------------------------------------------------####
	def readConfig(self):  ## only once at startup
		try:
			pass
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 
#

######################################################################################
# 		get config 
######################################################################################

####-------------------------------------------------------------------------####
	def validatePrefsConfigUi(self, valuesDict):


		self.debugLevel			= []
		for d in _debugAreas:
			if valuesDict[u"debug"+d]: self.debugLevel.append(d)

		self.unfiCurl	= valuesDict[u"unfiCurl"]

		self.setLogfile(valuesDict[u"logFileActive2"])
	 

		self.indigoFolderName = valuesDict["indigoFolderName"]
		self.indigoFolderId = indigo.devices.folders.getId(self.indigoFolderName)
		if self.indigoFolderId == 0:
			try:
				ff = indigo.devices.folder.create(self.indigoFolderName)
				self.indigoFolderId = ff.id
			except:
				self.indigoFolderId =0


		changeLogging = False
		try: 
			xx = valuesDict["SQLLoggingEnable"].split("-")
			yy = {"devices":xx[0]=="on", "variables":xx[1]=="on"}
			if yy != self.SQLLoggingEnable:
				self.SQLLoggingEnable = yy
				changeLogging = True
		except Exception, e:
			self.indiLOG.log(30,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.SQLLoggingEnable = {"devices":True, "variables":True}

		if changeLogging: self.setSqlLoggerIgnoreStatesAndVariables()


		self.tempUnits					= valuesDict[u"tempUnits"]	# Celsius, Fahrenheit, Kelvin
		self.tempDigits					= int(valuesDict[u"tempDigits"])  # 0/1/2
		self.energyDigits				= int(valuesDict[u"energyDigits"])  # 0/1/2
		self.powerDigits				= int(valuesDict[u"powerDigits"])  # 0/1/2
		self.voltageDigits				= int(valuesDict[u"voltageDigits"])  # 0/1/2
		self.currentDigits				= int(valuesDict[u"currentDigits"])  # 0/1/2

		self.IndigoServerIPNumber 		= valuesDict[u"IndigoServerIPNumber"]
		self.portOfIndigoServer 		= int(valuesDict[u"portOfIndigoServer"])
		self.userIDOfShellyDevices 		= valuesDict[u"userIDOfShellyDevices"]
		self.passwordOfShellyDevices 	= valuesDict[u"passwordOfShellyDevices"]

		return True, valuesDict



###-------------------------------------------------------------------------####
###----------menu items            -----------------------------------------####
###-------------------------------------------------------------------------####
	def buttonPrintHelpToLogCALLBACK(self):

		helpText ='  \n'
		helpText +='========== This plugin integrates Shelly wifi devices into Indigo. ======================   \n'
		helpText +='   \n'
		helpText +=' ++ No other software is needed, no special setup on Shellly devices ++   \n'
		helpText +='   \n'
		helpText +='The plugin can read the device status and can send commands to them,  \n'
		helpText +='like relay on/off, light on, red=50% ..   \n'
		helpText +='As soon as the shelly devices are setup (wifi, pi#) the plugin will be able  \n'
		helpText +='to recognize them and add appropriate indigo devices, ready to be used.  \n'
		helpText +='   \n'
		helpText +='== Here the steps for setup  \n'
		helpText +='   \n'
		helpText +='(0)IN THE PLUGIN:  \n'
		helpText +='   Setup indigo config.. set     \n'
		helpText +='    - indigoIP#, port  used on shelly device to send actions to indigo  \n'
		helpText +='    - shelly device userid/passwd if enabled  \n'
		helpText +='    - some other parameter if needed .. use curl or python connect for some older OSX versions use curl  \n'
		helpText +='   \n'
		helpText +='(1) ONTHE SHELLY DEVICE \n'
		helpText +='    Setup shelly device as defned by the shelly manual: \n'
		helpText +='    Using your phone, connect wifi to shellyxxx AP wifi SSID in phone setup   \n'
		helpText +='    - use browser to connect to 192.168.33.1 (that is a fixed ip#)   \n'
		helpText +='    - setup your home wifi network parameter (SSID, PWD, IP). I prefer using a fixed IP#   \n'
		helpText +='    - Restart.    \n'
		helpText +='   Optional: On regular browser, connect to http://ip# you set with phone   \n'
		helpText +='     upgrade device if available, set device parameters as needed  \n'
		helpText +='   \n'
		helpText +='(2) IN THE PLUGIN:  \n'
		helpText +='    To add devices or do a refresh  \n'
		helpText +='    enter IP# / range in menu   \n'
		helpText +='        "Start Shelly device discovery Process for ONE device" or .. "an IP RANGE"  \n'
		helpText +='    It will query the IP# (or range) and check for a propper shelly response    \n'
		helpText +='    When a proper resonse is received, the plugin will try to add a new Shelly device  \n'
		helpText +='     if does not already exist   \n'
		helpText +='   \n'
		helpText +='(3) OPTIONAL if needed:  \n'
		helpText +='   Edit indigo Shelly device to tune parameters eg:  \n'
		helpText +='    expiration time:  after what time w/o message the device goes to "EXPIRED"  \n'
		helpText +='    polling time: how often should the plugiquerry the device  \n'
		helpText +='    status column: what to show in the status column (only for sensors)  \n'
		helpText +='    set relay and input settings eg default at power on, input button behavior etc  \n'
		helpText +='    IP number: here you can change the IP number of the device  \n'
		helpText +='   \n'
		helpText +='== How it works:  \n'
		helpText +='   \n'
		helpText +='The plugin is:  \n'
		helpText +='(A) listening to any messages from the devices a tcp port (set in config, default 7987)  \n'
		helpText +='    the plugin will push action url settings to each shelly device  \n'
		helpText +='    that causes the shelly device to SEND info to the plugin when anything changes  \n'
		helpText +='(B) polling the devices on a regular schedule (1/s .. min., set in dev edit)  \n'
		helpText +='     - http://ip#/settings         gets basic config parameters (dev type, rssi, etc)  \n'
		helpText +='     - http://ip#/status           gets live info eg temp, on/off, RGB, Power ...  \n'
		helpText +='(C) switching shelly devices, on/off set light eg:  \n'
		helpText +='     - http://ip#/relay/0?turn=on/off  sets relay 0 on/off  \n'
		helpText +='     - http://ip#/color/0?red=200&green=50&blue=30  sets RGB values  \n'
		helpText +='    etc.  \n'
		helpText +='(D) can set parameters on shelly devices (set in indigo device edit), with:  \n'
		helpText +='     - http://ip#/settings/relay/0?btn_type=toggle     set input button to toggle/momentary/.. \n'
		helpText +='     - http://ip#/settings/light/0?default_state=last  set the power-on state to last/on/off  \n'
		helpText +='     and many other parameters (night mode ...) \n'
		helpText +='(E) Menu option to get and print shelly-EM(3) emeter time series data to logfile  \n'
		helpText +='== REMARKS:   \n'
		helpText +='(A) The plugin will detect IP# changes for relay or temp devices automatically, \n'
		helpText +='      but not for light bulbs, as they do not send out any updates \n'
		helpText +='      you can change the IP# of the device in indigo device edit \n'
		helpText +='(B) You can set a shelly IP# to be ignored, then the plugin will not be updating anything for that device \n'
		helpText +='(C) There are a few utilities: print device info, push config to the shelly devices, mostly used for debugging \n'
		helpText +='   \n'
		helpText +='== Currently supported devices:   \n'
		helpText +='  fully tested:   \n'
		helpText +='Shelly-1:                          12V 110-220V one basic relay  \n'
		helpText +='Shelly-1PM:                        12V 110-220Vrelay with internal temp sensor ...  \n'
		helpText +='Shelly-25 2-Relays:                like two Shelly-1PM in one - the plugin creates 2 devices: R1, R2 \n'
		helpText +='                                   the second relay will be added as device: hostName-shellyswitch25-child-1\n'
		helpText +='Shelly-EM Power 2 Ch. - 1 Relay:   110-220V measures Power, volt, has 1 relay - the plugin creates 3 devices: R + EM1 + EM2   \n'
		helpText +='                                   the EM devices  will be added as device: hostName-shellyem-child-1/2\n'
		helpText +='Shelly Duo                         110-220V LED light bulb w color temperature  \n'
		helpText +='Shelly-RGBW Light Bulb:            110-220V LED light bulb with 4 led (RGBW)  \n'
		helpText +='Shelly-RGBW dimmer:                110-220V 4 led dimmer (PWM) for RGBW  \n'
		helpText +='Shelly-Dimmer:                     110-220V dimmer  \n'
		helpText +='Shelly-1 Temp-Hum:                 battery / usb powered Temp. and Hum. sensor  \n'
		helpText +='Shelly-Flood-Temp:                 Flood alarm and Temperature sensor  \n'
		helpText +='Shelly- ext. oneWire Temp sensor:  External addon for Shelly-1 -1PM for up to 3 oneWire Temp sensors \n'
		helpText +='                                   the sensors will be added as devices: hostName-ext_temperature-# (1,2,3) \n'
		helpText +='Shelly- ext. DHT22  sensor:        External addon for Shelly-1 -1PM for 1 DHT22 T&H sensor \n'
		helpText +='                                   the sensor will be added as devices: hostName-ext_temperature-1 and  hostName-ext_humidity-1\n'
		helpText +='  programmed, but not tested:   \n'
		helpText +='Shelly-EM3 Power 3 Ch. - 1 Relay:  110-220V measures Power, volt, has 1 relay - the plugin creates 4 devices: R + EM1 + EM2 + EM3  \n'
		helpText +='                                   the 3 EM  will be added as device: hostName-sheleeyEM3-child-1/2\n'
		helpText +='Shelly-PRO4, 4 relay:              220V measures Power, volt, the plugin creates 4 relay devices \n'
		helpText +='                                   the 2-4 relays will be added as device: hostName-shellypro-child-# (1/2/3)\n'
		helpText +='Shelly-Vintage Bulb:               110-220V LED light bulb vintage style  \n'
		helpText +='Shelly Door Window                 Door/window open alarm  partially supported  \n'
		helpText +='Shelly Plug PlugS                  power outlets w relay and power measurement  \n'
		helpText +='   \n'
		helpText +='=========================================================================================   \n'
		helpText +='   \n'
		indigo.server.log(helpText.encode('utf8'))
		self.indiLOG.log(20,helpText.encode('utf8'))



####-------------------------------------------------------------------------####
	def filterEmeterDevices(self, filter="", valuesDict=None, typeId=""):
		xList=[]
		for devId in self.SHELLY:
			if devId == 0: continue
			if not self.SHELLY[devId]["deviceEnabled"]: continue
			dev =  indigo.devices[devId]
			if dev.deviceTypeId.find("em-") ==-1: continue
			
			##self.indiLOG.log(20,u"forcing push menu {};  {}".format(devId, self.SHELLY[devId]["ipNumber"]) )
			name= indigo.devices[devId].name.encode("utf8")
			xList.append([str(devId), name])
		xList.sort(key = lambda x: x[1]) 
		return xList


####-------------------------------------------------------------------------####
	def filterActiveShellyDevices(self, filter="", valuesDict=None, typeId=""):
		xList=[]
		for devId in self.SHELLY:
			if devId != 0:
				if self.SHELLY[devId]["deviceEnabled"]:
					##self.indiLOG.log(20,u"forcing push menu {};  {}".format(devId, self.SHELLY[devId]["ipNumber"]) )
					name= indigo.devices[devId].name.encode("utf8")
					xList.append([str(devId), name])
		xList.sort(key = lambda x: x[1]) 
		xList.append(["0","all devices"])
		return xList


####-------------------------------------------------------------------------####
	def filterActiveShellyDevicesNotChild(self, filter="", valuesDict=None, typeId=""):
		xList=[]
		for devId in self.SHELLY:
			if devId != 0:
				if not self.SHELLY[devId]["deviceEnabled"]: continue
				if     self.SHELLY[devId]["isChild"]: 		continue
				dev= indigo.devices[devId]
				props = dev.pluginProps
				if not props["isChild"]: return 
					##self.indiLOG.log(20,u"forcing push menu {};  {}".format(devId, self.SHELLY[devId]["ipNumber"]) )
				name= dev.name.encode("utf8")
				xList.append([str(devId), name])
		xList.sort(key = lambda x: x[1]) 
		xList.append(["0","all devices"])
		return xList

####-------------------------------------------------------------------------####
	def filterignoredIPNumbers(self, filter="", valuesDict=None, typeId=""):
		xList=[]
		for ipN in self.ignoredIPNumbers:
			if self.isValidIP(ipN):
				xList.append([ipN, ipN])
		xList.append(["0","all IPNUmbers"])
		return xList

####-------------------------------------------------------------------------####
	def buttonConfirmconfirmpUnIgnoreIPNumberCALLBACK(self, valuesDict, typeId=""):
		ipN = valuesDict["ipNumber"].strip()
		if ipN == "0":
			self.pluginPrefs["ignoredIPNumbers"] = ""
			self.ignoredIPNumbers =[]
			return valuesDict

		ignoredIPNumbers = self.pluginPrefs.get(u"ignoredIPNumbers", "").split(",")
		if ipN in ignoredIPNumbers:
			self.ignoredIPNumbers.remove(ipN)
			self.indiLOG.log(20,u"added IP#:{} back to accepted IP numbers,  currently ignored:{}".format(ipN, self.ignoredIPNumbers) )
			self.pluginPrefs["ignoredIPNumbers"] = (",".join(self.ignoredIPNumbers)).strip(",")
		return valuesDict

####-------------------------------------------------------------------------####
	def buttonConfirmconfirmpIgnoreIPNumberCALLBACK(self, valuesDict, typeId=""):
		ipN = valuesDict["ipNumber"].strip()
		if ipN not in self.ignoredIPNumbers:
			self.ignoredIPNumbers.append(ipN)
			self.indiLOG.log(20,u"added IP#:{} to ignored IP numbers, currently ignored:{}".format(ipN, self.ignoredIPNumbers) )
			self.pluginPrefs["ignoredIPNumbers"] = (",".join(self.ignoredIPNumbers)).strip(",")
		return valuesDict


####-------------------------------------------------------------------------####
	def buttonConfirmconfirmIpNumberSetupCALLBACK(self, valuesDict, typeId=""):
		ip = valuesDict["ipNumber"].strip()
		if self.isValidIP(ip):
			self.ipNumberRangeToTest = [ip, ip] 
			self.indiLOG.log(20,u"added IP#:{} to shelly discovery process".format(ip) )
		else:
			self.indiLOG.log(20,u"bad IP:{} for shelly discovery process".format(ip) )
		return valuesDict




####-------------------------------------------------------------------------####
	def buttonConfirmconfirmIpNumberRangeSetupCALLBACK(self, valuesDict, typeId=""):
		ipFrom = valuesDict["ipNumberFrom"].strip()
		ipTo   = valuesDict["ipNumberTo"].strip()
		if self.isValidIP(ipFrom) and self.isValidIP(ipTo):
			self.ipNumberRangeToTest = [ipFrom, ipTo] 
			self.indiLOG.log(20,u"added IP#s:{} -- {}  to shelly discovery process".format(ipFrom, ipTo) )
		else:
			self.indiLOG.log(20,u"bad IP:{} - {} ".format(ipFrom, ipTo) )
		return valuesDict


####-------------------------------------------------------------------------####
	def buttonConfirmconfirmpPuschActionCALLBACK(self, valuesDict, typeId=""):
		devIdSelect = int(valuesDict["devId"])
		for devId in self.SHELLY:
			if devId == 0: continue
			if devId == devIdSelect or devIdSelect ==0:
				self.SHELLY[devId]["lastSuccessfullConfigPush"] = -10
				self.pushRequest  = time.time()
				self.indiLOG.log(20,u"forcing push of config to {}".format(indigo.devices[devId].name.encode("utf8")) )
		return valuesDict



####-------------------------------------------------------------------------####
	def buttonConfirmconfirmpgetEmeterCvsFileCALLBACK(self, valuesDict, typeId=""):
		devIdSelect = int(valuesDict["devId"])
		if  devIdSelect not in self.SHELLY: 
			self.indiLOG.log(20,u"bad selection for EM cvs data {}".format(devIdSelect) )
			return valuesDict
		dev = indigo.devices[int(devIdSelect)]
		props = dev.pluginProps
		if not props["isChild"]: return 
		page =  "emeter/"+str(int(dev.states["childNo"])-1)+"/em_data.csv"
		self.indiLOG.log(20,u"getting EM csv data for {}; with: {}".format(dev.name.encode("utf8"), page) )
		cvsData = self.getJsonFromDevices(dev.address, page, noJson=True)
		if len(cvsData) > 10:
			valuesDict["MSG"] ="check  ...shellyDirect/plugin.log file "
		else:
			valuesDict["MSG"] ="no data returned"
		self.indiLOG.log(20,u"csv data from:{}:\n{}".format(dev.name.encode("utf8"), cvsData) )
		return valuesDict


####-------------------------------------------------------------------------####
	def buttonConfirmconfirmpRequestStatusCALLBACK(self, valuesDict, typeId=""):
		try:
			devIdSelect = int(valuesDict["devId"])
			for devId in self.SHELLY:
				if devId == 0: continue
				if devId == devIdSelect or devIdSelect ==0:
					dev = indigo.devices[devId]
					self.indiLOG.log(20,u"sending status request to device:{}".format(dev.name.encode("utf8")) )
					self.sendStatusRequest(dev)
		except Exception, e:
			self.indiLOG.log(40,u"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 

		return valuesDict

####-------------------------------------------------------------------------####
	def buttonPrintShellyDevInfoCALLBACK(self, valuesDict, typeId=""):

		devIdSelect = int(valuesDict["devId"])
		out =""
		for devId in self.SHELLY:
			if devId == 0: continue
			if devId == devIdSelect or devIdSelect ==0:
				props ={}
				try: 
					dev = indigo.devices[devId]
					name = dev.name.encode("utf8")
					deviceTypeId = dev.deviceTypeId
					props = dev.pluginProps
				except:
					name = "dev does not exist"
					deviceTypeId = "---"
				out += "\n:::::::: dev:{:33s} ID:{:14}  type: {:10s}   ::::::::::\n".format(name, devId, deviceTypeId)
				keys = sorted(self.SHELLY[devId])
				for item in keys:
					out+= "{:33s}:  {}\n".format(item, unicode(self.SHELLY[devId][item]).encode("utf8"))
				dev = indigo.devices[devId]
				keys = sorted(dev.states)
				for item in keys:
					out+= "{:33s}:  {}\n".format(item, unicode(dev.states[item]).encode("utf8"))
				keys = sorted(dev.states)
				propList =[]
				for prop in props:
					for xx in ["SENDTOSHELLYDEVICE-","children", "isParent", "isChild","displaySelect" ]:
						if prop.find(xx) > -1:
							propList.append([prop,props[prop]])
				for item in propList:
					if item[0].find("SENDTOSHELLYDEVICE-") > -1:
							if item[0] not in settingCmds: continue
							settings = settingCmds[item[0]][0]+item[1]
							out+= "{:33s}:  {}\n".format("set parameters",settings) 
					else:
							out+= "{:33s}:  {}\n".format(item[0],item[1]) 


				if "action_url" in _emptyProps[dev.deviceTypeId]:
					for item in _emptyProps[dev.deviceTypeId]["action_url"]:
						action = unicode(_emptyProps[dev.deviceTypeId]["action_url"][item]).replace("': '",":").replace("', '","   ").replace("{","").replace("}","").replace("'","")
						out += "{:33s}:  {}\n".format(item, action) 
		ignoredIPNumbers = self.pluginPrefs.get(u"ignoredIPNumbers", "")
		if ignoredIPNumbers != "":
			out += "\n---------------------------------------\n"
			out += "{:33s}:  {}\n".format("ignored IP Numbers", ignoredIPNumbers) 


		if out !="":
			self.indiLOG.log(20, out )
			indigo.server.log(out)
		return 


######################################################################################
	# Indigo Trigger Start/Stop
######################################################################################

####-------------------------------------------------------------------------####
	def triggerStartProcessing(self, trigger):
		self.triggerList.append(trigger.id)

####-------------------------------------------------------------------------####
	def triggerStopProcessing(self, trigger):
		if trigger.id in self.triggerList:
			self.triggerList.remove(trigger.id)

	#def triggerUpdated(self, origDev, newDev):
	#	self.triggerStopProcessing(origDev)
	#	self.triggerStartProcessing(newDev)


######################################################################################
	# Indigo Trigger Firing
######################################################################################

####-------------------------------------------------------------------------####
	def triggerEvent(self, eventId):
		if	time.time() < self.currentlyBooting: # no triggering in the first 100+ secs after boot 
			#self.indiLOG.log(10, u"triggerEvent: %s suppressed due to reboot" % eventId)
			return
		for trigId in self.triggerList:
			trigger = indigo.triggers[trigId]
			if trigger.pluginTypeId == eventId:
				indigo.trigger.execute(trigger)
		return


######################################################################################
	# dev start / stop / delete / setup
######################################################################################

####-------------------------------------------------------------------------####
	def deviceStartComm(self, dev):
		try:
			if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(20,"deviceStartComm called for {}; dev={}".format(dev.id, dev.name) )
			if dev.id == self.doNotrestartDev: return 
			dev.stateListOrDisplayStateIdChanged()

			if "brightness" in dev.states: 
				dev.onBrightensToLast = True
				dev.replaceOnServer()
				dev = indigo.devices[dev.id]
			props = dev.pluginProps
			update = False
			if dev.deviceTypeId not in _emptyProps:
				self.indiLOG.log(40,"dev: {}  has wrong deviceTypeId: {}; please delete device and restart plugin".format(dev.name.encode("utf8"), dev.deviceTypeId))
			else:	
				for pp in _emptyProps[dev.deviceTypeId]["props"]:
					if pp not in props:
						props[pp] = copy.copy(_emptyProps[dev.deviceTypeId]["props"][pp])
						update = True
				if update: 
					dev.replacePluginPropsOnServer(props)
					dev = indigo.devices[dev.id]

				self.renewShelly(dev)
				if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(20,"deviceStartComm finished for {}; dev={}, props:{}".format(dev.id, dev.name,props) )
				self.doNotrestartDev = ""
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"for dev: {}".format(dev.name.encode("utf8")))
		return 


####-------------------------------------------------------------------------####
	def renewShelly(self, dev, startCom=False):
		try:

			props = dev.pluginProps
			updateProps = False

			if dev.id not in self.SHELLY:
				self.SHELLY[dev.id] = copy.copy(_emptyShelly)

			for prop in props:
				self.SHELLY[dev.id][prop] = copy.copy(props[prop])

			try: 
				children = json.loads(props["children"])
			except:
				props["children"] = "{}"
				children = {}
				updateProps = True

			self.SHELLY[dev.id]["children"] 						= children

			try:	self.SHELLY[dev.id]["parentIndigoId"] 			= int(props["parentIndigoId"])
			except: 
					self.SHELLY[dev.id]["parentIndigoId"]			= 0
					props["parentIndigoId"] 						= 0
					updateProps										= True

			try: 	self.SHELLY[dev.id]["expirationSeconds"]		= float(props["expirationSeconds"])
			except: 
					self.SHELLY[dev.id]["expirationSeconds"]		= _emptyProps[dev.deviceTypeId]["expirationSeconds"]
					props["expirationSeconds"] 						= _emptyProps[dev.deviceTypeId]["expirationSeconds"]
					updateProps										= True

			try: 	self.SHELLY[dev.id]["pollingFrequency"]			= float(props["pollingFrequency"])
			except: 
					self.SHELLY[dev.id]["pollingFrequency"]			= _emptyProps[dev.deviceTypeId]["automaticPollingFrequency"]
					props["automaticPollingFrequency"] 				= _emptyProps[dev.deviceTypeId]["automaticPollingFrequency"]
					updateProps= True

			try: 	self.SHELLY[dev.id]["lastMessageFromDevice"]	= time.mktime(datetime.datetime.strptime( dev.states["lastMessageFromDevice"], _defaultDateStampFormat).timetuple() )
			except: self.SHELLY[dev.id]["lastMessageFromDevice"]	= 0

			try: 	
				if self.SHELLY[dev.id]["lastSuccessfullConfigPush"] >=0:
					self.SHELLY[dev.id]["lastSuccessfullConfigPush"] = time.mktime(datetime.datetime.strptime( dev.states["lastSuccessfullConfigPush"], _defaultDateStampFormat).timetuple() )
			except: self.SHELLY[dev.id]["lastSuccessfullConfigPush"] = 0

			self.SHELLY[dev.id]["devTypeId"] 					 	 = dev.deviceTypeId
			self.SHELLY[dev.id]["deviceEnabled"] 					 = True
			if not props["isChild"]:
				self.SHELLY[dev.id]["queue"] 						 = Queue.Queue()

			if updateProps: dev.replacePluginPropsOnServer(props)

			if not self.SHELLY[dev.id]["isChild"]: self.startShellyDevicePoller("start", shellySelect=dev.id)
			#self.indiLOG.log(20,"shelly at startdev  {} ".format(self.SHELLY))

			

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		return




####-------------------------------------------------------------------------####
	def deviceDeleted(self, dev):  ### indigo calls this 

		props = dev.pluginProps
		delChild  =[]
		if dev.id in self.SHELLY:
			self.SHELLY[dev.id]["state"] = "stop"
			self.sleep(2)
			if 	self.SHELLY[dev.id]["children"] != {}:
				children = self.SHELLY[dev.id]["children"]
				#self.indiLOG.log(20,"devId:{}, children:{}".format(dev.id, children ))
				for devtype in children:
					#self.indiLOG.log(20,"devId:{}, devtype:{}".format(dev.id, devtype ))
					for devNo in children[devtype]:
						#self.indiLOG.log(40,"devId:{}, devNo:{}, devId:{}".format(dev.id, devNo, children[devtype][devNo] ))
						if type(children[devtype][devNo]) == type(1):
							delChild.append(children[devtype][devNo])  # that is the indigo devId of the child
	
		## this must be a child device, delete children entry at parent
			if  self.SHELLY[dev.id]["isChild"]:
				try:
					if self.SHELLY[dev.id]["parentIndigoId"] in indigo.devices: # if not already gone
						parentDev = indigo.devices[self.SHELLY[dev.id]["parentIndigoId"]]
						parentProps = parentDev.pluginProps
						children = self.SHELLY[parentDev.id]["children"]
						#self.indiLOG.log(20,"devId:{}, children:{}".format(dev.id, children ))
						delDevType =[]
						for devtype in children:
							#self.indiLOG.log(20,"devId:{}, devtype:{}".format(dev.id, devtype ))
							delDevNo =[]
							for devNo in children[devtype]:
								#self.indiLOG.log(40,"devId:{}, devNo:{}, devId:{}".format(dev.id, devNo, children[devtype][devNo] ))
								if children[devtype][devNo] == dev.id: delDevNo.append(devNo)
							#self.indiLOG.log(40,"devId:{}, delDevNo:{}".format(dev.id, delDevNo ))
							for devNo in delDevNo:
								del children[devtype][devNo]
							if children[devtype] =={}: delDevType.append(devtype)
							#self.indiLOG.log(40,"devId:{}, delChild:{}".format(dev.id, delDevType ))
						for devtype in delDevType:
							del children[devtype]
				
						self.SHELLY[parentDev.id]["children"] = children
						parentProps["children"] = json.dumps(children)
						parentDev.replacePluginPropsOnServer(parentProps)
				except Exception, e:
					self.indiLOG.log(20,"while deleting children devices is OK, was already deleted... Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))


		try:		del self.SHELLY[dev.id]
		except: 	pass

		for childId in delChild:
			try: 	del self.SHELLY[childId]
			except: pass
			try: 	indigo.device.delete(childId)
			except: pass

		return


####-------------------------------------------------------------------------####
	def deviceStopComm(self, dev):
		try: 
			if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(20,"deviceStopComm called for dev={}".format(dev.name.encode("utf8")) )
		except: pass
		try:	self.SHELLY[dev.id]["deviceEnabled"] = False
		except: pass
		#self.stopShellyDevicePoller( shellySelect=dev.id)


###############################################################################
##############################   DEVICE edit  #################################
####-------------------------------------------------------------------------####
	def filterselectParentDevice(self, filter="", valuesDict=None, typeId="", devId=""):
		xList=[]
		for devId in self.SHELLY:
			if self.SHELLY[devId]["typeId"] != filter: continue
			props = dev.pluginProps
			if "isParent" in props and props["isParent"]:
				if "children" in props:
					children = json.loads(props["children"])
					if children == {} or dev.deviceTypeId not in children or children[dev.deviceTypeId] == {}:
						xList.append([str(devId), dev.name])
		if xList == []:
			xList.append(["-1", "no free hosting device available"])
		return xList

####-------------------------------------------------------------------------####
	def getDeviceConfigUiValues(self, pluginProps, typeId="", devId=""):
		try:
			theDictList =  super(Plugin, self).getDeviceConfigUiValues(pluginProps, typeId, devId)
			try: ##Only if it exists already
				if "isParent" in pluginProps:
					if "sensorNo" in pluginProps and "sensorNo" in dev.states:
							sensorNo = dev.states["sensorNo"]
							try: 	theDictList[0]["sensorNo"] = str(int(sensorNo)-1)
							except: theDictList[0]["sensorNo"] = "0"
					if devId in self.SHELLY:
						theDictList[0]["MAC"] = self.SHELLY[int(devId)]["MAC"]
						theDictList[0]["ipNumber"]  = self.SHELLY[int(devId)]["ipNumber"]

					
			except Exception, e:
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			#self.indiLOG.log(20,"theDictList {}".format(unicode(theDictList[0])))
			return theDictList

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"theDictList {}".format(unicode(theDictList[0])))
		return theDictList

####-------------------------------------------------------------------------####
	def validateDeviceConfigUi(self, valuesDict, typeId, devId):

		error = ""
		errorDict = indigo.Dict()
		valuesDict[u"MSG"] = "OK"
		try:
			dev = indigo.devices[devId]
			props = dev.pluginProps
			devNo = "0"
			newParameters = False
			#self.indiLOG.log(20,"valuesDict {}".format(valuesDict))

			for pp in["ipNumber", "pollingFrequency", "expirationSeconds"]:
				self.SHELLY[devId][pp] = copy.copy(valuesDict[pp])

			if props["isParent"]:
				valuesDict["address"] = copy.copy(valuesDict["ipNumber"])
				children = self.SHELLY[devId]["children"]
				if children != {}: 
					childDevs, devNos = self.getChildDevices(children)
					for childDev in childDevs:
						childProps = childDev.pluginProps
						for pp in["ipNumber", "pollingFrequency", "expirationSeconds"]:
							childProps[pp] = copy.copy(valuesDict[pp])
							self.SHELLY[childDev.id][pp] = copy.copy(valuesDict[pp])
						childProps["address"] = copy.copy(valuesDict["ipNumber"])
						childDev.replacePluginPropsOnServer(childProps)

			if not props["isChild"]:
				for pp in valuesDict:
					if pp.find("SENDTOSHELLYDEVICE-") ==-1: continue
					if "devNo" not in props: props["devNo"] = "0"
					test = copy.copy(valuesDict[pp].replace("/0?","/"+props["devNo"]+"?") )
					if pp not in props or test != props[pp]: newParameters = True
					valuesDict[pp] = copy.copy(test)
					self.SHELLY[devId][pp] = copy.copy(valuesDict[pp])

			#copy changes from child to parent props button settings, as only the parent will push 
			if props["isChild"]:
				int(props["parentIndigoId"])
				parentDev = indigo.devices[int(props["parentIndigoId"])]
				parentProps = parentDev.pluginProps
				for pp in valuesDict:
					if pp.find("SENDTOSHELLYDEVICE-") ==-1: continue
					test = copy.copy(valuesDict[pp].replace("/0?","/"+props["devNo"]+"?"))
					if pp not in parentProps or test != parentProps[pp]: newParameters = True
					parentProps[pp] = copy.copy(test)
					self.SHELLY[devId][pp] = copy.copy(valuesDict[pp])
				if newParameters:
					parentDev.replacePluginPropsOnServer(parentProps)
					self.SHELLY[parentDev.id]["lastSuccessfullConfigPush"] = -10
	

			if newParameters:
				self.indiLOG.log(20,"start pushing config parameters to: {}".format(dev.name.encode("utf8")))
				self.SHELLY[devId]["lastSuccessfullConfigPush"] = -10
				self.pushRequest = time.time()


				
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			errorDict["MSG"] = unicode(e)
			valuesDict["MSG"] = unicode(e)
			return ( False, valuesDict, errorDict )

		return ( True, valuesDict )

###############################################################################
##############################   DEVICE edit end  ############################


####-------------------------------------------------------------------------####
	###########################	   MAIN LOOP  ############################
####-------------------------------------------------------------------------####
	def initConcurrentThread(self):



		now = datetime.datetime.now()
		self.quitNow		  = u""

		self.startTime		  = time.time()


		for ii in range(2):
			if self.pluginPrefs.get(u"IndigoServerIPNumber","") != "": break
			self.sleep(10)

		self.lastMinuteChecked	= -1
		self.lasthourChecked 	= now.hour
		self.lastDayChecked		= -1
		self.lastSecChecked		= 0
		self.countLoop			= 0
		self.currentVersion		= 7.0

		if self.currentVersion != self.pluginVersion:
			# will put future updates here
			pass

		self.lastUpdateSend = time.time()  
		self.pluginState	= "run"

		self.initShelly(0,  "0", "0")


		self.indiLOG.log(20,u"..  setting up internal dev tables")
		for dev in indigo.devices.iter(self.pluginId):
			self.renewShelly(dev, startCom=False)
			if not dev.enabled:
				if dev.id in self.SHELLY: self.SHELLY[dev.id]["deviceEnabled"] = False

		return 



	###########################	   cProfile stuff   ############################ START
	####-----------------  ---------
	def getcProfileVariable(self):

		try:
			if self.timeTrVarName in indigo.variables:
				xx = (indigo.variables[self.timeTrVarName].value).strip().lower().split("-")
				if len(xx) ==1: 
					cmd = xx[0]
					pri = ""
				elif len(xx) == 2:
					cmd = xx[0]
					pri = xx[1]
				else:
					cmd = "off"
					pri  = ""
				self.timeTrackWaitTime = 20
				return cmd, pri
		except Exception, e:
			pass

		self.timeTrackWaitTime = 60
		return "off",""

	####-----------------            ---------
	def printcProfileStats(self,pri=""):
		try:
			if pri !="": pick = pri
			else:		 pick = 'cumtime'
			outFile		= self.indigoPreferencesPluginDir+"timeStats"
			indigo.server.log(" print time track stats to: "+outFile+".dump / txt  with option: "+pick)
			self.pr.dump_stats(outFile+".dump")
			sys.stdout 	= open(outFile+".txt", "w")
			stats 		= pstats.Stats(outFile+".dump")
			stats.strip_dirs()
			stats.sort_stats(pick)
			stats.print_stats()
			sys.stdout = sys.__stdout__
		except: pass
		"""
		'calls'			call count
		'cumtime'		cumulative time
		'file'			file name
		'filename'		file name
		'module'		file name
		'pcalls'		primitive call count
		'line'			line number
		'name'			function name
		'nfl'			name/file/line
		'stdname'		standard name
		'time'			internal time
		"""

	####-----------------            ---------
	def checkcProfile(self):
		try: 
			if time.time() - self.lastTimegetcProfileVariable < self.timeTrackWaitTime: 
				return 
		except: 
			self.cProfileVariableLoaded = 0
			self.do_cProfile  			= "x"
			self.timeTrVarName 			= "enableTimeTracking_"+self.pluginShortName
			indigo.server.log("testing if variable "+self.timeTrVarName+" is == on/off/print-option to enable/end/print time tracking of all functions and methods (option:'',calls,cumtime,pcalls,time)")

		self.lastTimegetcProfileVariable = time.time()

		cmd, pri = self.getcProfileVariable()
		if self.do_cProfile != cmd:
			if cmd == "on": 
				if  self.cProfileVariableLoaded ==0:
					indigo.server.log("======>>>>   loading cProfile & pstats libs for time tracking;  starting w cProfile ")
					self.pr = cProfile.Profile()
					self.pr.enable()
					self.cProfileVariableLoaded = 2
				elif  self.cProfileVariableLoaded >1:
					self.quitNow = " restart due to change  ON  requested for print cProfile timers"
			elif cmd == "off" and self.cProfileVariableLoaded >0:
					self.pr.disable()
					self.quitNow = " restart due to  OFF  request for print cProfile timers "
		if cmd == "print"  and self.cProfileVariableLoaded >0:
				self.pr.disable()
				self.printcProfileStats(pri=pri)
				self.pr.enable()
				indigo.variable.updateValue(self.timeTrVarName,"done")

		self.do_cProfile = cmd
		return 

	####-----------------            ---------
	def checkcProfileEND(self):
		if self.do_cProfile in["on","print"] and self.cProfileVariableLoaded >0:
			self.printcProfileStats(pri="")
		return
	###########################	   cProfile stuff   ############################ END



####-----------------   main loop          ---------
	def runConcurrentThread(self):

		self.dorunConcurrentThread()
		self.checkcProfileEND()
		self.sleep(2)
		if self.quitNow !="":
			indigo.server.log( u"runConcurrentThread stopping plugin due to:  ::::: " + self.quitNow + " :::::")
			serverPlugin = indigo.server.getPlugin(self.pluginId)
			serverPlugin.restart(waitUntilDone=False)

		subprocess.call("/bin/kill -9 "+unicode(self.myPID), shell=True )

		return



####-----------------   main loop          ---------
	def dorunConcurrentThread(self): 

		self.initConcurrentThread()


		if self.logFileActive !="standard":
			indigo.server.log(u"..  initialized")
			self.indiLOG.log(20, u"..  initialized, starting loop" )
		else:	 
			indigo.server.log(u"..  initialized, starting loop ")


		########   ------- here the loop starts	   --------------
		try:
			while self.quitNow == "":
				self.countLoop += 1
				self.sleep(5.)

				if self.countLoop > 2: 
					anyChange = self.periodCheck()

		except self.StopThread:
			indigo.server.log( u"stop requested from indigo ")
		self.stopShellyDevicePoller()

		if self.quitNow != "": indigo.server.log( "quitNow: {} --- you might see an indigo error message, can be ignored ".format(self.quitNow))
		else: indigo.server.log( "quitNow:  empty")

		self.pluginState = "stop"


		return

####-------------------------------------------------------------------------####
#  periods checks every x secs / hour / day 
####-------------------------------------------------------------------------####
	def periodCheck(self):
		anyChange= False
		try:
			now = datetime.datetime.now()
			self.checkForNewScanRequest()

			if self.pushRequest >0 and time.time() - self.pushRequest > 0:
				self.checkIfPushToDevicesIsRequired(now,pushNow=True)

			if self.lastMinuteChecked == now.minute: return 
			self.lastMinuteChecked = now.minute

			self.checkForExpiredDevices(now)

			self.checkIfHTTPListernProcessRunsOk()

			if self.lasthourChecked == now.hour: return 
			self.lasthourChecked = now.hour
			self.checkIfPushToDevicesIsRequired(now)

			self.testHTTPlistener()

			self.resetMinMaxSensors()


		except Exception, e:
			if len(unicode(e)) > 5 :
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				self.indiLOG.log(40,"devId {} ".format(devId))

		return anyChange


###-------------------------------------------------------------------------####
	def checkIfHTTPListernProcessRunsOk(self):
		try:
			if self.testHTTPsuccess != 0:
				if time.time() - self.testHTTPsuccess  > 100:
					self.indiLOG.log(40,"HTTPlisten test failed not working, please restart plugin")
				else:
					self.indiLOG.log(20,"HTTPlisten test sucessfull")
				self.testHTTPsuccess = 0
		except Exception, e:
			if len(unicode(e)) > 5 :
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 

###-------------------------------------------------------------------------####
	def checkIfPushToDevicesIsRequired(self, now, pushNow=False):
		try:
			#Only every 2hours 1/3/5/..
			if now.hour %2 == 0 and not pushNow: return 
			for devId in self.SHELLY:
				if devId == 0: continue
				if self.SHELLY[devId]["isChild"]: continue

				if time.time() - self.SHELLY[devId]["lastSuccessfullConfigPush"] > self.repeatConfigPush:
					self.addToShellyPollerQueue(devId, "settings")
					self.pushConfigToShellyDevice(devId)
		except Exception, e:
			if len(unicode(e)) > 5 :
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 

###-------------------------------------------------------------------------####
	def checkForExpiredDevices(self, now):
		try:
			delShelly =[]
			for devId in self.SHELLY:
				if devId >0:
					try: dev = indigo.devices[devId]
					except: 
						delShelly.append(devId) 
						continue
					if time.time() - self.startTime > 300: # no expirtaion in first 5 minutes after start, give it time to receive messages
						props = dev.pluginProps
						if time.time() - self.SHELLY[devId]["lastMessageFromDevice"] > self.SHELLY[devId]["expirationSeconds"]:
							if dev.states["expired"].find("no") == 0 or len(dev.states["expired"]) < 10: # either "no ...  datestring" or  (empty or junk, must have datestring if not simply "no" )
								self.indiLOG.log(20,"setting dev:{} to expired; minutes since last contact:{:.0f};  expiration Setting:{:.0f}[Min]".format(dev.name.encode("utf8"), (time.time() - self.SHELLY[devId]["lastMessageFromDevice"])/60, self.SHELLY[devId]["expirationSeconds"]/60))
								dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)
								dev.updateStateOnServer("expired", now.strftime(_defaultDateStampFormat))

					self.SHELLY[devId]["deviceEnabled"]  = dev.enabled

			for devId in delShelly:
				self.indiLOG.log(20,"deleting {} {}".format(devId, self.SHELLY[devId]))
				del self.SHELLY[devId]
		except Exception, e:
			if len(unicode(e)) > 5 :
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 


####-------------------------------------------------------------------------####
	def checkForNewScanRequest(self):
		try:
			if self.ipNumberRangeToTest == []: return 

			rangestart = int(self.ipNumberRangeToTest[0].split(".")[3])
			rangeEnd   = int( self.ipNumberRangeToTest[1].split(".")[3]) + 1
			ip0        = self.ipNumberRangeToTest[1].split(".")
			ip0        = ip0[0]+"."+ip0[1]+"."+ip0[2]+"."
			self.ipNumberRangeToTest = []
			for ipx in range(rangestart, rangeEnd):
				self.nextIPSCAN = ip0 + str(ipx)
				for devId in self.SHELLY: 
					if devId == 0: continue
					if self.nextIPSCAN == self.SHELLY[devId]["ipNumber"]: 
						self.indiLOG.log(20,"SHELLY discovery: skipping ip# {}, alread exists".format(self.nextIPSCAN))
						self.nextIPSCAN = ""
						break
				if self.nextIPSCAN == "": continue
				self.indiLOG.log(20,"SHELLY discovery: probing  ip# {}, for 20 secs".format(self.nextIPSCAN))
				self.SHELLY[0]["ipNumber"] = self.nextIPSCAN
				self.addToShellyPollerQueue(0, "settings")
				for ii in range (20):
					time.sleep(1)
					if self.nextIPSCAN == "": break
			self.indiLOG.log(20,"SHELLY discovery: finished")

		except Exception, e:
			if len(unicode(e)) > 5 :
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 

####-------------------------------------------------------------------------####
	def testHTTPlistener(self):
		try:
			self.SHELLY[0]["ipNumber"] = self.HTTPlisternerTestIP
			self.testHTTPsuccess = time.time()
			if self.decideMyLog(u"HTTPlistener"): self.indiLOG.log(20,u"..  starting http listener TEST @:http://{}:{}/test".format(self.HTTPlisternerTestIP, self.portOfIndigoServer) )
			self.getJsonFromDevices( self.HTTPlisternerTestIP, "test", jsonAction="", port = str(self.portOfIndigoServer), testHTTP=True)
		except Exception, e:
			if len(unicode(e)) > 5 :
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return


####-------------------------------------------------------------------------####
	def performActionList(self):
		return


####-------------------------------------------------------------------------####
	def checkDay(self,now):
		return 


####-------------------------------------------------------------------------####
# receiving data in queue add to list to work on
####-------------------------------------------------------------------------####
	def addtoAnalyzePollerQueue(self, data):
		try:
			self.messagesQueue.put(data)
			if not self.queueActive: 
				self.workOnQueue()

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"data:{}".format(data))
		return 


####-------------------------------------------------------------------------####
	def workOnQueue(self):
		try:
			self.queueActive  = True
			while not self.messagesQueue.empty():
				items = self.messagesQueue.get() 
				#if self.decideMyLog(u"Polling"): self.indiLOG.log(20,"workOnQueue  items:{}".format(items))
				for ii in range(40):
					if self.queueList ==u"update" : break
					if self.queueList ==u""		  : break
					if ii > 0:	pass
					time.sleep(0.05)
				self.execUpdate(items)
				self.queueList = "update"  
				#### indigo.server.log(unicode(item[1])+"  "+ unicode(beaconUpdatedIds)+" "+ item[3])
			self.messagesQueue.task_done()
			self.queueActive  = False
			self.queueList = ""	 
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"data:{}".format(data))
		return 



 
####-------------------------------------------------------------------------####
####-------------------------------------------------------------------------####
# this where we get incoming message:
#  first check if the device alread exists (shellyIndigoDevNumber exists& IP# is known)   or if it is an action ()
# if dev does not exist, try to create
# then fill indigo dev states
####-------------------------------------------------------------------------####
####-------------------------------------------------------------------------####

	def execUpdate(self, items):
		try:
			if self.decideMyLog(u"Polling"): self.indiLOG.log(20,"queue received: items:{}".format(items) )

			if "shellyIndigoDevNumber" in items: 					self.workOnRegularMessage(items)
								
			elif "page" in items and items["page"] == "httpAction":	self.workOnActionMessage(items)

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40," data:{}".format(items) )
		return 

####-------------------------------------------------------------------------####
	def workOnRegularMessage(self, items):
		try:
			ipNumber = ""
			if "ipNumber" in items: ipNumber = items["ipNumber"]
			else:					ipNumber = ""
			if ipNumber in self.ignoredIPNumbers: 
				if self.decideMyLog(u"Polling"): self.indiLOG.log(20,"queue checking devid:{};  IP#:{} rejected in ignore list".format( items["shellyIndigoDevNumber"] , ipNumber) )
				return 
			# thhis is message from myself, for testing can be ignored
			if ipNumber == self.HTTPlisternerTestIP: 
				return 	

			newDeviceCreated = False
			# no indigo dev number, must be new 
			if items["shellyIndigoDevNumber"]  == 0:
				data = items["data"]
				self.indiLOG.log(20,"execUpdate checking for new device received, ipNumber:{}; data:{} ".format( items["shellyIndigoDevNumber"], ipNumber, data) )
				devIdFound = 0
				if "mac" in data: MAC = data["mac"]
				if "device" in data and "mac" in data["device"]: MAC = data["device"]["mac"]
				else: MAC = ""

				# do we have a device with that ip#, do not use child, at this point we need the host/ parent
				for devId in self.SHELLY:
					if self.SHELLY[devId]["ipNumber"] == ipNumber and not self.SHELLY[devId]["isChild"]: 
						items["shellyIndigoDevNumber"] = devId
					if MAC  == self.SHELLY[devId]["MAC"]:
						devIdFound =  devId

				# did the ip number change? if so fix 
				if devIdFound > 0:
					if items["shellyIndigoDevNumber"] != devIdFound:  # ip number changed
						dev = indigo.devices[devIdFound]
						self.indiLOG.log(20,"execUpdate dev: {} IPNUMBER has changed ..  new IP#:{}, old IP#:{}".format(devIdFound, ipNumber, self.SHELLY[devIdFound]["ipNumber"]))
						self.changeIpNumber(dev, self.SHELLY[devIdFound]["ipNumber"], ipNumber)
						items["shellyIndigoDevNumber"] = devIdFound
						dev = indigo.devices[devIdFound]

				# is the device enabled in indigo?
				doNotCreate = False
				if items["shellyIndigoDevNumber"] == 0:
					for dd in indigo.devices.iter(self.pluginId):
						if dd.address == ipNumber:
							if not dd.enabled:
								self.indiLOG.log(20,"execUpdate shellyIndigoDevNumber ==0, .. dev:{}  is disabled, will NOT create new one;  ipNumber:{}".format(dd.name.encode("utf8"), ipNumber))
							else:
								self.indiLOG.log(20,"execUpdate .. msg dev:{}  is unexpected message, will NOT create new one; ipNumber:{}, data:{}".format(dd.name.encode("utf8"), ipNumber, data))
							doNotCreate = True

						#self.renewShelly(dd, startCom=False)
					if doNotCreate: return 

					if "device" not in data:
						self.indiLOG.log(30,"execUpdate  new dev ipnumber:{}, sending request for settings, not enough info:{}".format(ipNumber, items) )
						self.addToShellyPollerQueue(0, "settings", now=True)
						return 

					items["shellyIndigoDevNumber"]   = self.createParentShellyDevice(items["data"], ipNumber)
					newDeviceCreated = True
					self.nextIPSCAN = ""

					# could not createa new device, ignore .. need to fix later
					if items["shellyIndigoDevNumber"] == 0:
						return 


			# deive ok, fill device states etc
			if items["shellyIndigoDevNumber"]  > 0:
				dev = indigo.devices[items["shellyIndigoDevNumber"] ]
				if "page" in items:
					if items["page"] == "settings":
						self.SHELLY[dev.id]["lastMessage-settings"] = items["data"]
						self.fillShellyDeviceStates( items["data"], dev, items["page"], ipNumber )
					elif items["page"] == "status":
						self.SHELLY[dev.id]["lastMessage-status"] = items["data"]
						self.checkIfExtSensorDevicesnNeedToBeCreated(items["data"], dev, ipNumber)
						self.fillShellyDeviceStates( items["data"], dev, items["page"], ipNumber )
					else: # there was an action get the whole dataset 
						self.addToShellyPollerQueue(items["shellyIndigoDevNumber"] , "status", now=True)
				if newDeviceCreated:
					self.addToShellyPollerQueue(items["shellyIndigoDevNumber"] , "status", now=True)
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40," data:{}".format(items) )
	
####-------------------------------------------------------------------------####
	def workOnActionMessage(self, items):
		try:
			#{"ipNumber":192.168.1.x, "page":"httpAction", "data":{"path": {'path': '/data?hum=33&temp=15.25'},}
			if self.decideMyLog(u"Polling"): self.indiLOG.log(20,"queue page item present" )
			if "ipNumber" not in items: 
				return 
			ipNumber = items["ipNumber"]
			if ipNumber in self.ignoredIPNumbers: return 

			if ipNumber == self.HTTPlisternerTestIP:
				# reset open channel queue
				self.SHELLY[0]["ipNumber"] = ""
				self.testHTTPsuccess = time.time() + 100 
				if self.decideMyLog(u"HTTPlistener"): self.indiLOG.log(20,"http listener self test received .. ok" )
				return 

			# bad data check, just a save gurad should not be the case
			if "data" not in items: 
				return 
			data = items["data"]["path"]
			found = False
			devIdFound =0
			for devId in self.SHELLY:
				if self.SHELLY[devId]["ipNumber"] == ipNumber: 
					try: 
						dev = indigo.devices[devId]
						devIdFound = devId
						found = True
						break
					except: continue

			if found: 
				self.fillShellyDeviceStates( items["data"]["path"], dev, items["page"], ipNumber )
				self.SHELLY[devIdFound]["now"] = True
				self.addToShellyPollerQueue(devIdFound, "settings")
				# check if we should push settings, good for battery devices, as thye only wake up every x hours
				if time.time() - self.SHELLY[devId]["lastSuccessfullConfigPush"] > self.repeatConfigPush:
					self.pushConfigToShellyDevice(devId)
				


			if not found:
				## get full description to trigger dev generation
				doNotCreate = False
				for dd in indigo.devices.iter(self.pluginId):
					if dd.address == ipNumber:
						if not dd.enabled:
							self.indiLOG.log(20,"execUpdate .. dev:{}  is disabled, will NOT create new one; ipNumber:{}, data:".format(dd.name.encode("utf8"), ipNumber, data))
							doNotCreate = True
						else:
							self.indiLOG.log(20,"execUpdate .. dev:{}  httpAction has unexpected message,from ipNumber:{}, sending status request data:{}".format(dd.name.encode("utf8"), ipNumber, data))
				if doNotCreate: return  
				self.indiLOG.log(20,"execUpdate ..   httpAction has unexpected message,from ipNumber:{}, sending settings request;  data received:{}".format(ipNumber, data))
				self.initShelly(0, "", ipNumber, startPoller=True)
				self.addToShellyPollerQueue(0, "settings")
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40," data:{}".format(items) )
		return 


####-------------------------------------------------------------------------####
	def changeIpNumber(self, dev, oldIP, ipNumber):
		try:
			self.SHELLY[dev.id]["ipNumber"] = ipNumber
			props = dev.pluginProps
			props["ipNumber"] = ipNumber
			props["address"] = ipNumber
			dev.replacePluginPropsOnServer(props)
			if int(props["parentIndigoId"]) >0:
				children = json.dumps(props["children"])
				deviceTypeId = dev.deviceTypeId
				childDevs, devNos = self.getChildDevices(children)
				for childDev in childDevs:
					self.SHELLY[childDev.id]["ipNumber"] = ipNumber
					childProps = childDev.pluginProps
					childProps["ipNumber"] = ipNumber
					childProps["address"] = ipNumber
					childDev.replacePluginPropsOnServer(childProps)

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40," data:{}".format(items) )
		return 


###-------------------------------------------------------------------------####
###-------------------------------------------------------------------------####
###-------------------------------------------------------------------------####
###----------------------  create new devs    ------------------------------####
###-------------------------------------------------------------------------####
###-------------------------------------------------------------------------####
####-------------------------------------------------------------------------####
	def checkIfExtSensorDevicesnNeedToBeCreated(self, data, parentDev, ipNumber):
		try:

			# have we got an external addon device in data?
			extDeviceTypeDevType = []
			extDeviceTypeData = []
			for extChildType in _emptyProps[parentDev.deviceTypeId]["childTypes_Sensors"]:

				if extChildType  not in data: continue
				if  type(data[extChildType]) != type({}): continue
				extDeviceTypeDevType.append(extChildType)
				extDeviceTypeData.append(data[extChildType])
			if extDeviceTypeDevType == []: return 

			# yes
			#  check if already exists
			# we should have this:
			# 	children ={"ext_temperature":{"1":12345,"2":234345,"3":48484}
			# this we get
			# extDeviceTypeData =[{"1":{tC:45..},"3":{"tC":22}}, ..]
			# extDeviceTypeFound =["ext_temperature","ext_Humidity", ..]

			children = self.SHELLY[parentDev.id]["children"]
			
			# toBeCreated ={ "type":{"1":{tC:45..},"3":{"tC":22}}}
			toBeCreated = {}
			for nn in range(len(extDeviceTypeDevType)):
				extDevType = extDeviceTypeDevType[nn]
				toBeCreated[extDevType] = copy.copy(extDeviceTypeData[nn])
				for devNo  in extDeviceTypeData[nn]:
					if extDevType in children and devNo in children[extDevType]: 
						del toBeCreated[extDevType][devNo]
				if toBeCreated[extDevType] == {}: del toBeCreated[extDevType]

			# any children, if not we are done
			if toBeCreated == {}: return 

			self.indiLOG.log(20,"external sensors toBeCreated: {}".format(toBeCreated))

			# we have to create new child devices
			baseName = parentDev.name
			parentProps = parentDev.pluginProps
			parentIndigoId = parentDev.id
			nameX = "-sensor-99"
			for devTypeId in toBeCreated:
				if toBeCreated[devTypeId] =={}: continue
				for nn in toBeCreated[devTypeId]:
					devNo = nn
					devNoText = str(int(nn)+1)
					nameX = "-"+devTypeId+"-"+devNoText
					props = self.initDevProps(devTypeId, self.SHELLY[parentIndigoId]["MAC"], ipNumber)
					props["parentIndigoId"] =  parentIndigoId
					props["isChild"]	=  True
					props["devNo"]		=  str(devNo) # this can be  1/2/3
					description = "Hosted by {}".format( parentIndigoId )
					self.indiLOG.log(20,"trying to create new SHELLY device,  name:{}, ipNumber:{}".format((baseName+nameX).encode("utf8"), ipNumber))
					try: 
						indigo.devices[baseName+nameX]
						self.indiLOG.log(20,"... device, already exist, disabled? name:{}".format((baseName+nameX).encode("utf8")))
						for dd in indigo.devices.iter(self.pluginId):
							self.renewShelly(dd, startCom=False)
						nameX += "_r_"+str(int(time.time()))		
						self.indiLOG.log(20,"... changing name to: {}".format((baseName+nameX).encode("utf8")))
					except: pass

					devChild = indigo.device.create(
						protocol		= indigo.kProtocol.Plugin,
						address			= ipNumber,
						name			= baseName+nameX,
						description		= description,
						pluginId		= self.pluginId,
						deviceTypeId	= devTypeId,
						folder			= self.indigoFolderId,
						props			= props
						)
					self.indiLOG.log(20,"==> created: {}".format(devChild.name.encode("utf8")))
					if devTypeId not in children: children[devTypeId]={}
					children[devTypeId][devNo] = devChild.id
					devChild.updateStateOnServer("sensorNo",devNoText)
					devChild.updateStateOnServer("created",datetime.datetime.now().strftime(_defaultDateStampFormat))
					devChild.updateStateOnServer("MAC",self.SHELLY[parentDev.id]["MAC"])
					self.initShelly(devChild, self.SHELLY[parentDev.id]["MAC"], ipNumber, deviceTypeId=devTypeId, startPoller=False )
					devChild.updateStateOnServer("created",datetime.datetime.now().strftime(_defaultDateStampFormat))
					self.SHELLY[devChild.id]["isChild"] = True
			parentProps["children"] = json.dumps(children)

			self.SHELLY[parentIndigoId]["children"] = children
			self.SHELLY[parentIndigoId]["isParent"] = True
			parentProps["children"] = json.dumps(children)
			parentProps["isParent"] = True
			parentDev.replacePluginPropsOnServer(parentProps)
			parentDev = indigo.devices[parentIndigoId]
			parentDev.description =  "Host of ..."
			parentDev.replaceOnServer()


		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40," data:{}".format(data) )
		return 

####-------------------------------------------------------------------------####
	def createParentShellyDevice(self, data, ipNumber ):
		try:
			devId = 0

			if "device"  in data:
					deviceTypeId = data["device"]["hostname"]
					useDevType   = deviceTypeId.rsplit("-", 1)[0]
					MAC    = data["device"]["mac"]
			else: return 0

			self.indiLOG.log(20,"==> create ShellyDevice for {}, deviceTypeId:{}".format(ipNumber, useDevType) )


			for devId in self.SHELLY:
				if devId == 0: continue
				if self.SHELLY[devId]["ipNumber"] == ipNumber and self.SHELLY[devId]["devTypeId"] == useDevType: 
					self.indiLOG.log(30, "ip# {} already exists devID: {}".format(ipNumber, devId))
					return 0

			
			props = self.initDevProps(useDevType, MAC, ipNumber)
			if props == {}:
				self.indiLOG.log(30, "ip# {} can not create dev with type: {}".format(ipNumber, useDevType))
				return 0
			name_Parent = "shelly_"+ipNumber
			if _emptyProps[useDevType]["childTypes_SplitDevices"] == []:
				description = ""
			else:
				description = "Host of ..."
				props["isParent"] = True 
			try:
				try: 
					indigo.devices[name_Parent]
					self.indiLOG.log(20,"trying to create new SHELLY device, already exist, disabled? name:{}, ipNumber:{}".format(name_Parent.encode("utf8"), ipNumber))
					for dd in indigo.devices.iter(self.pluginId):
						self.renewShelly(dd, startCom=False)
					name_Parent += "_r_"+str(int(time.time()))
					self.indiLOG.log(20,"... changing name to: {}".format((name_Parent).encode("utf8")))
				except: pass

				props["devNo"]   	=  "0"
				devParent = indigo.device.create(
					protocol		= indigo.kProtocol.Plugin,
					address			= ipNumber,
					name			= name_Parent,
					description		= description,
					pluginId		= self.pluginId,
					deviceTypeId	= useDevType,
					folder			= self.indigoFolderId,
					props			= props
					)
				self.initShelly(devParent, MAC, ipNumber, deviceTypeId=useDevType)
				devParent.updateStateOnServer("MAC",MAC)
				devParent.updateStateOnServer("created",datetime.datetime.now().strftime(_defaultDateStampFormat))
				self.pushConfigToShellyDevice(devParent.id)
				self.indiLOG.log(20,"==> created: {}".format(devParent.name.encode("utf8")))
				devId = devParent.id

			except Exception, e:
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				self.indiLOG.log(40,"name:{}, props:{}, ipNumber:{}".format(name_Parent, props, ipNumber))
				return 0

			#now create regular splitoff childs if needed
			devNo = 0
			children = self.SHELLY[devParent.id]["children"]
			for childType in _emptyProps[useDevType]["childTypes_SplitDevices"]:
				devNo += 1
				props = self.initDevProps(childType, MAC, ipNumber)
				description = "Hosted by {}".format(devParent.id)
				props["isChild"] = True 
				props["parentIndigoId"] = devParent.id
				name = "{}-{}-{}".format(name_Parent, childType, devNo)
				props["devNo"]   	=  str(devNo) # this can be 1/2/3/4/5 eg shell25 has 1, EM has 2 EM3 has 3 pro has 3
				devChild = indigo.device.create(
					protocol		= indigo.kProtocol.Plugin,
					address			= ipNumber,
					name			= name,
					description		= description,
					pluginId		= self.pluginId,
					deviceTypeId	= childType,
					folder			= self.indigoFolderId,
					props			= props
					)
				self.initShelly(devChild, MAC, ipNumber, deviceTypeId=childType, startPoller=False )
				devChild.updateStateOnServer("childNo",devNo)
				devChild.updateStateOnServer("MAC",MAC)
				devChild.updateStateOnServer("created",datetime.datetime.now().strftime(_defaultDateStampFormat))
				self.indiLOG.log(20,"==> created: {}".format(devChild.name.encode("utf8")))

				# finish parent setup
				nextNo = 0
				if childType not in children: children[childType] ={}
				for dd in children[childType]:
					nextNo = max( nextNo, int(dd) )
				children[childType][str(nextNo+1)] = devChild.id
			parentProps = devParent.pluginProps
			parentProps["children"] = json.dumps(children)
			devParent.replacePluginPropsOnServer(parentProps)
			self.SHELLY[devId]["isParent"] = True
			self.SHELLY[devId]["children"] = children
				

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"data:{}".format(data))
		return devId


####-------------------------------------------------------------------------####
	def initDevProps(self, deviceTypeId, MAC, ipNumber):
		props = {}
		try:
			props		   					= copy.copy(_emptyProps[deviceTypeId]["props"])
			props["MAC"] 					= MAC
			props["ipNumber"] 				= ipNumber
			props["SupportsBatteryLevel"] 	= deviceTypeId in _supportsBatteryLevel
				
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		return props


####-------------------------------------------------------------------------####
	def initShelly(self, dev, MAC, ipNumber, deviceTypeId="", startPoller=True):
		try:
			
			if dev == 0: useDevId = True
			else:		 useDevId = False
			if useDevId:
				devId = 0
			else:
				devId = dev.id
				props = dev.pluginProps

			if devId not in self.SHELLY: self.SHELLY[devId]					= copy.copy(_emptyShelly)
			if startPoller and self.SHELLY[devId]["queue"] ==0: 
				self.SHELLY[devId]["queue"]									= Queue.Queue()
			self.SHELLY[devId]["MAC"] 										= MAC
			self.SHELLY[devId]["ipNumber"] 									= ipNumber.strip()
			self.SHELLY[devId]["deviceEnabled"] 							= True
			self.SHELLY[devId]["devTypeId"] 								= deviceTypeId
			if not self.SHELLY[devId]["isChild"] and startPoller:			self.startShellyDevicePoller("start", shellySelect=devId)
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		return 
		

####-------------------------------------------------------------------------####
####-------------------------------------------------------------------------####
####---------------------fill devices with info from shell-------------------####
####-------------------------------------------------------------------------####
####-------------------------------------------------------------------------####
	def fillShellyDeviceStates(self, data, dev, page, ipNumber):


		if page not in ["settings","status","init","httpAction"]: return 

		try:
			if time.time() - self.SHELLY[dev.id]["lastSuccessfullConfigPush"] > self.repeatConfigPush-600:
				self.pushConfigToShellyDevice(dev.id)


			children = self.SHELLY[dev.id]["children"]
		
			if "device" in data: 
				deviceTypeId = data["device"]["hostname"].rsplit("-", 1)[0]
			else:
				deviceTypeId = dev.deviceTypeId

	
			if page == "httpAction":
				self.doHTTPactionData(data, dev)
				self.executeUpdateStatesDict()
				return 

			self.fillExternalSensors(data, dev, children)

			self.fillLight(data, dev)

			self.fillSHWT( data, dev)
			self.fillshellydw( data, dev)


			# now for devices with children 
			devs, devNos = self.getChildDevices( children)
			if False and len(children) >999:
				devids = [dd.id for dd in devs]
				self.indiLOG.log(20,"{};   children:{};  childrenfromProps:{};  devids:{}, devNos:{}".format(dev.name, children,dev.pluginProps["children"], devids, devNos))
				
			if len(devs) ==0: devs = [dev, dev]
			else:			  
				dev0 = [dev]
				dev0.extend(devs)
				devs = dev0
			

			self.fillInputs(data, devs )

			self.fillRelays(data, devs)

			self.filleMeters(data, devs)

			self.fillMeters(data, devs)

			
			if devs[0].id == devs[1].id: devs=[dev]

			for devNo in range(len(devs)):
				devX  = devs[devNo]
				props = devX.pluginProps

				devX  = devs[devNo]
				props = devX.pluginProps
				self.fillbasicProps(data, devX, devNo)
				if  "wifi_sta" in data:
					if self.fillWiFi(data, devX):
						devX = indigo.devices[devX]

				# for ext sensors dont fill with inetrnal tmp sensor data, has same data
				if "ext_temperature" != devX.deviceTypeId:
					if "tmp" in data: devX = self.fillSensor(devX, data, "tmp", "Temperature")
				if "ext_humidity" != devX.deviceTypeId:
					if "hum" in data: devX = self.fillSensor(devX, data, "hum", "Humidity")


				for tProp in ["overtemperature","overload"]:
					if tProp in devX.states and tProp in data:
						self.addToStatesUpdateDict(str(devX.id), tProp, data[tProp])

				if "sensors" in data:
					for tProp in ["temperature_threshold","humidity_threshold"]:
						if tProp in data["sensors"] and tProp in dev.states:	
							self.addToStatesUpdateDict(str(devX.id),tProp, data["sensors"][tProp])

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"data:{}".format(data))

		self.executeUpdateStatesDict()
		return 

####-------------------------------------------------------------------------####
	def fillWiFi(self, data, dev):
		try:
			if ("enabled" in data["wifi_sta"] and data["wifi_sta"]["enabled"])  or ("u'connected" in data["wifi_sta"] and data["wifi_sta"]["u'connected"]):
				ipNumber = data["wifi_sta"]["ip"]
				if dev.address != ipNumber:
					if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(40,"ip number changed for devID{}; old:{} new:{}".format(dev.id, dev.address, ipNumber) )
					props = dev.pluginProps
					props["address"] = ipNumber
					dev.replacePluginPropsOnServer(props)
					return dev
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"data {} ".format(data))
		return dev

####-------------------------------------------------------------------------####
	def fillbasicProps(self, data, dev, devNo):
		try:
			devID = str(dev.id)

			if dev.deviceTypeId not in _externalSensorDevTypes: #this info is handled in fillExternalSensors
				self.SHELLY[dev.id]["lastMessageFromDevice"]  = time.time()
				self.addToStatesUpdateDict(str(dev.id),"lastMessageFromDevice", datetime.datetime.now().strftime(_defaultDateStampFormat))
				if "expired" 	 in dev.states:	
					if dev.states["expired"].find("-") == -1: # do we have a date string, if not just set it to no
						self.addToStatesUpdateDict(devID, "expired", "no" )
					elif dev.states["expired"].find("no") == -1: # if datestring, check if we have a no in front
						self.addToStatesUpdateDict(devID, "expired", "no, last expired: {}".format(dev.states["expired"]) )

			if "bat"         in data: 
				if "value"   in data["bat"] and "batteryLevel" in dev.states: 		self.addToStatesUpdateDict(devID, "batteryLevel", 					data["bat"]["value"])
				if "voltage" in data["bat"] and "batteryVoltage" in dev.states: 	self.addToStatesUpdateDict(devID, "batteryVoltage", 				data["bat"]["voltage"])
	
			if "wifi_sta"    in data  and "rssi"	in data["wifi_sta"] and "rssi" in dev.states: 		
																					self.addToStatesUpdateDict(devID, "rssi", 							data["wifi_sta"]["rssi"], decimalPlaces=0)

			if "update"      in data  and "has_update" in data["update"] and "software_update_available" in dev.states: 	
																					self.addToStatesUpdateDict(devID, "software_update_available", 		 "YES" if data["update"]["has_update"]  else "is up to date", decimalPlaces="")
			if "sleep_mode"  in data and "sleep_mode" in dev.states: 	
				if "period"  in data["sleep_mode"] and "unit" in data["sleep_mode"]:	
					sleepM = "{}{}".format(data["sleep_mode"]["period"],data["sleep_mode"]["unit"])
					if True:														self.addToStatesUpdateDict(devID, 		"sleep_mode", 				sleepM )

			if "act_reasons" in data:
				out =""
				for xx in data["act_reasons"]:
					out+=xx+";"

				if len(out) >0:
					self.addToStatesUpdateDict(devID, "action_from_Device", out.strip(";"))

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"data {} ".format(data))
		return 

####-------------------------------------------------------------------------####
	def fillLight(self, data, dev):
		try:
			if  "lights" not in data: return 
			devID = str(dev.id)
			for light in data["lights"]:
				if "overPower" in dev.states and "overpower" in light:
					self.addToStatesUpdateDict(devID, "overPower", light["overpower"])
				mode = "white"
				rgb = 0
				brightness= 0
				white = 0
				red = 0
				blue = 0
				green = 0
				ison = 1
				if "ison" in light :	isOn = 1 if  light["ison"] else 0

				if "mode" in dev.states:
					if "mode" in light: mode = light["mode"]
					else:			 	mode = dev.states["mode"]
					self.addToStatesUpdateDict(devID, "mode", mode)
				if mode == "": mode = "white"

				if "red"   in light:
					red		=  min(255,light["red"]    + 0.4)
					red		= 0 if red < 2 else red

				if "green" in light: 
					green	=  min(255,light["green"] + 0.4)
					green	= 0 if green < 2 else green

				if "blue"  in light: 
					blue	=  min(255,light["blue"]  + 0.4)
					blue	= 0 if blue < 2 else blue

				if "white"  in light:  		
					white	=  min(255,light["white"] + 0.4)
					white	= 0 if white < 2 else white

				if "brightness"  in light: 
					brightness = min(100,light["brightness"]+0.4)

				if  "redLevel"		in dev.states: self.addToStatesUpdateDict(devID, "redLevel",	int(red*100./255.)*isOn)
				if  "greenLevel"	in dev.states: self.addToStatesUpdateDict(devID, "greenLevel",	int(green*100./255.)*isOn)
				if  "blueLevel"		in dev.states: self.addToStatesUpdateDict(devID, "blueLevel",	int(blue*100./255.)*isOn)


				#if self.decideMyLog(u"Special"): self.indiLOG.log(20,"fillShellyDeviceStates mode:{}, light:{}".format( mode, light) )
				if mode  == "color":
					if "red" in light and "white" in light:
						rgb = (red + green + blue)/3
						if rgb > 2:  # cut off 1 values, need at least 4 to shine 
							if "whiteLevel" 	 in dev.states: self.addToStatesUpdateDict(devID, "whiteLevel", 	int(rgb*100./255.)*isOn)
							if "brightnessLevel" in dev.states: self.addToStatesUpdateDict(devID, "brightnessLevel",int(rgb*100./255.)*isOn)
						if rgb <=2 and "white" not in light:  # is it off and no white data present?
							if "whiteLevel" 	 in dev.states: self.addToStatesUpdateDict(devID, "whiteLevel", 	0)
							if "brightnessLevel" in dev.states: self.addToStatesUpdateDict(devID, "brightnessLevel",0)
						elif "white" in light and rgb <= 2:
							if "whiteLevel" 	 in dev.states: self.addToStatesUpdateDict(devID, "whiteLevel", 	int(white*100./255.)*isOn)
							if "brightnessLevel" in dev.states: self.addToStatesUpdateDict(devID, "brightnessLevel",int(white*100./255.)*isOn)
				elif mode  == "white" and "brightness" in light:
					#if self.decideMyLog(u"Special"): self.indiLOG.log(20,"fillShellyDeviceStates setting mode=white, using brigthness, white to {} and bright to :{}".format( int(brightness)*isOn, int(brightness)*isOn ) )
					if "brightnessLevel" in dev.states: self.addToStatesUpdateDict(devID, "brightnessLevel", int(brightness)*isOn)
					if "whiteLevel" 	 in dev.states: self.addToStatesUpdateDict(devID, "whiteLevel",      int(brightness)*isOn)

				if "temp" in light and "whiteTemperature" in dev.states: self.addToStatesUpdateDict(devID, "whiteTemperature", 	light["temp"])

				
				if "ison"       in light and "onOffState" in dev.states: 
					#self.indiLOG.log(40,"checking lights  on dev:{}  light ison:{}".format(dev.name, light["ison"]))
					self.addToStatesUpdateDict(devID, "onOffState",	light["ison"] )
					if light["ison"]:	dev.updateStateImageOnServer(indigo.kStateImageSel.DimmerOn)
					else:				dev.updateStateImageOnServer(indigo.kStateImageSel.DimmerOff)
				if "gain"       in light and "gain"       in dev.states: self.addToStatesUpdateDict(devID, "gain", 		light["gain"])
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 



####-------------------------------------------------------------------------####
	def fillshellydw(self, data, dev):
		try:
			if dev.deviceTypeId != "shellydw": return 
			devID = str(dev.id)		
			self.addToStatesUpdateDict(devID, "lux", 			data["lux"]["value"], str(data["lux"]["value"])+"[lux]", decimalPlaces=1)
			self.addToStatesUpdateDict(devID, "illumination", 	data["lux"]["illumination"])
			self.addToStatesUpdateDict(devID, "tilt", 			data["accel"]["tilt"], str(data["accel"]["tilt"])+"º",decimalPlaces=0)
			self.addToStatesUpdateDict(devID, "vibration", 		"no" if data["accel"]["vibration"] else "YES")
			self.addToStatesUpdateDict(devID, "batteryLevel", 	data["bat"]["value"], decimalPlaces=0)
			self.addToStatesUpdateDict(devID, "batteryVoltage", data["bat"]["voltage"], decimalPlaces=2)
			self.addToStatesUpdateDict(devID, "state", 			data["sensor"]["state"])
			self.addToStatesUpdateDict(devID, "onOffState",		data["sensor"]["state"] !="close", decimalPlaces="")

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"{} data:{}".format(dev.id,data))
		return 

#

####-------------------------------------------------------------------------####
	def fillSHWT(self, data, dev):
		try:
			if dev.deviceTypeId != "shellyflood": return 
			if "flood" in data  and "Flood" in dev.states:
				#self.indiLOG.log(20,"flood: regular data:{}".format(data) )
				devID = str(dev.id)		
				flood = True if data["flood"]  else False
				if flood and not dev.states["onOffState"]:
						#self.indiLOG.log(40,"flood: setting trip to green" )
						self.addToStatesUpdateDict(devID, "Flood", "FLOOD" , decimalPlaces="")
						self.addToStatesUpdateDict(devID, "onOffState",True, decimalPlaces="")
						self.addToStatesUpdateDict(devID, "previousAlarm", dev.states["lastAlarm"])
						self.addToStatesUpdateDict(devID, "lastAlarm", datetime.datetime.now().strftime(_defaultDateStampFormat))
						dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
				if not flood and dev.states["onOffState"]:
						self.addToStatesUpdateDict(devID, "Flood", "dry" , decimalPlaces="")
						self.addToStatesUpdateDict(devID, "onOffState",False, decimalPlaces="")
						dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"{} data:{}".format(dev.id,data))
		return 

####-------------------------------------------------------------------------####
	def fillExternalSensors(self, data, parentDev, children):
		try:
			#   structure: "ext_temperature":{"0":{"tC":22.88,"tF":73.175000},"1":{"tC":23.25,"tF":73.850000}}
			#self.indiLOG.log(20,"===fillExternalSensors==== parentDev:{} data:{}".format(parentDev.id, unicode(data)[0:50]))
			for childDevType in _childDevTypes:
				#self.indiLOG.log(20,"===fillExternalSensors childDevType:{}".format(childDevType))
				if childDevType in data and type(data[childDevType]) == type({}) and data[childDevType] !={}:
					if _childDevTypes[childDevType]["dataKey"] == "": continue # this will select only ext_sensors
					#self.indiLOG.log(20,"===fillExternalSensors childDevType data:{}".format(data[childDevType]))
					for ii in data[childDevType]:
						xxx = data[childDevType][ii]
						devNo 	  = ii
						devNoText = str(int(ii)+1)
						#self.indiLOG.log(20,"===fillExternalSensors ii:{}, xxx:{}".format(ii, xxx))
						if _childDevTypes[childDevType]["dataKey"] in xxx:
							state = _childDevTypes[childDevType]["state"]
							#self.indiLOG.log(20,"===fillExternalSensors state :{},  dev-children:{}".format(state,children))
							if childDevType not in children: continue
							if devNo not in children[childDevType]: continue
							childDevId = children[childDevType][devNo] 
							if childDevId ==0: continue
							try: 	childDev = indigo.devices[childDevId]
							except: continue
							#self.indiLOG.log(20,"===fillExternalSensors childDevId :{}".format(childDevId))
							if state in childDev.states:
								#self.indiLOG.log(20,"===fillExternalSensors filling sensor w xxx:{}, key:{}, state:{}".format(xxx, _childDevTypes[childDevType]["dataKey"], state))
								self.fillSensor(childDev, xxx, _childDevTypes[childDevType]["dataKey"], state)
								self.addToStatesUpdateDict(str(childDev.id),"lastMessageFromDevice", datetime.datetime.now().strftime(_defaultDateStampFormat))
								self.SHELLY[childDev.id]["lastMessageFromDevice"] = time.time()
								if "expired" 	 in childDev.states:	
									if childDev.states["expired"].find("-") == -1: # do we have a date string, if not just set it o no
											self.addToStatesUpdateDict(childDev.id, "expired", "no" )
									else:  # if datestring, check if we have a no in front
										if childDev.states["expired"].find("no") == -1:
											self.addToStatesUpdateDict(childDev.id, "expired", "no, last expired: {}".format(childDev.states["expired"]) )
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 

####-------------------------------------------------------------------------####
	def getChildDevices(self, children):
#        eg: children:{u'shellyswitch25-child': {u'1': 577953272}};
		returnDevs =[]
		devNos =[]
		try:
			for deviceTypeId in children:
				for childDevNo in children[deviceTypeId]:
					if childDevNo != "":
						devID = children[deviceTypeId][childDevNo]
						childDev = indigo.devices[devID]
						if deviceTypeId in _childDevTypes:
							returnDevs.append(childDev)
							devNos.append(childDevNo)
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"deviceTypeId:{}; children {}, devNos:{}".format(deviceTypeId, children, devNos))
		return returnDevs, devNos
####-------------------------------------------------------------------------####
	def getChildDevIDs(self, parentId):
#        eg: children:{u'shellyswitch25-child': {u'1': 577953272}};
		devIDs =[]
		if self.SHELLY[parentId]["children"] == {}: return []
		try:
			for deviceTypeId in self.SHELLY[parentId]["children"]:
				for childDevNo in self.SHELLY[parentId]["children"][deviceTypeId]:
					if childDevNo != "":
						devIDs.append(self.SHELLY[parentId]["children"][deviceTypeId][childDevNo])
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return devIDs

####-------------------------------------------------------------------------####
	def fillInputs(self, data, devs):
		try:
			if "inputs" not in data: return
			ii = 0
			for input in data["inputs"]:
				if "input" in input:
					if   input["input"] == "1": input["input"] = "on"
					else:						input["input"] = "off"
					if "input" 	 			in devs[ii].states: self.addToStatesUpdateDict(str(devs[ii].id), "input",   			input["input"])
					if "input_"+str(ii+1)	in devs[ii].states: self.addToStatesUpdateDict(str(devs[ii].id), "input_"+str(ii+1),	input["input"])
					ii+=1


		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"data {} ".format(data))
		return 

####-------------------------------------------------------------------------####
	def fillRelays(self,  data, devs):
		try:
			if "relays" not in data: return
			ii = 0
			for relay in data["relays"]:
				if "ison" in relay:
					self.fillSwitch(devs[ii], relay, "ison")
				if "overPower" in devs[ii].states and "overpower" in relay:
					self.addToStatesUpdateDict(str(devs[ii].id), "overPower", relay["overpower"])
				ii+=1


		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"data {} ".format(data))
		return 


####-------------------------------------------------------------------------####
	def fillMeters(self,  data, devs):
		try:
			if "meters" not in data: return
			devNo = 0
			for meter in data["meters"]:
				if devNo > len(devs)-1: continue
				if "power" 	in meter and	"power"				in devs[devNo].states:	self.fillSensor(devs[devNo], meter, "power",	"power",			decimalPlaces=self.powerDigits)
				if "energy" in meter and	"energy" 			in devs[devNo].states:	self.fillSensor(devs[devNo], meter, "energy",	"energy",			decimalPlaces=self.energyDigits)
				if "total" 	in meter and	"energy" 			in devs[devNo].states:	self.fillSensor(devs[devNo], meter, "total",	"energy",			decimalPlaces=self.powerDigits)
				if "counter" in meter and	"energy_counter" 	in devs[devNo].states:	self.fillSensor(devs[devNo], meter, "counter",	"energy_counter",	decimalPlaces="")
				devNo+=1

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"data {} ".format(data))
		return 

####-------------------------------------------------------------------------####
	def filleMeters(self,  data, devs):
		try:
			if "emeters" not in data: return
			devNo = 1 	# this is for the child devices, ie shelly EM, start at dev#1
						# need to change indexs  other devices ie EM3 or it might just work .. as soon as I get one
			for emeter in data["emeters"]:
				if devNo > len(devs)-1: break
				##self.indiLOG.log(20,"devNo {} , ndevs(:{};  dev:{}; emeter:{}".format(devNo, len(devs), devs[devNo].name, emeter))
				if "power" in emeter:
					if "power" 					in devs[devNo].states:	self.fillSensor(devs[devNo], emeter, "power", 			"power", 			decimalPlaces=self.powerDigits)
					if "voltage" 				in devs[devNo].states:	self.fillSensor(devs[devNo], emeter, "voltage", 		"voltage", 			decimalPlaces=self.voltageDigits)
					if "reactive" 				in devs[devNo].states:	self.fillSensor(devs[devNo], emeter, "reactive", 		"reactive", 		decimalPlaces=self.powerDigits)
					if "current" 				in devs[devNo].states:	self.fillSensor(devs[devNo], emeter, "current", 		"current", 			decimalPlaces=self.currentDigits)
					if "energy" 				in devs[devNo].states:	self.fillSensor(devs[devNo], emeter, "total", 			"energy", 			decimalPlaces=self.energyDigits)
					if "energyTotal" 			in devs[devNo].states:	self.fillSensor(devs[devNo], emeter, "total_returned",	"energyReturned", 	decimalPlaces=self.energyDigits)
					# set setae and icon power onoff w power !=0
					if "is_valid" in emeter: 
						if emeter["is_valid"] and emeter["power"] != 0:
							self.addToStatesUpdateDict(devs[devNo].id, "onOffState", True)
							devs[devNo].updateStateImageOnServer(indigo.kStateImageSel.PowerOn)
						if not emeter["is_valid"] or emeter["power"] == 0:
							self.addToStatesUpdateDict(devs[devNo].id, "onOffState", False)
							devs[devNo].updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
				devNo += 1

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"data {} ".format(data))
		return 



####-------------------------------------------------------------------------####
	def doHTTPactionData(self, data, dev):
		try:
			self.SHELLY[dev.id]["lastMessage-Http"] = data
			if self.decideMyLog(u"HTTPlistener"):self.indiLOG.log(20,"doHTTPactionData {}   data:{}".format(self.SHELLY[dev.id]["ipNumber"], data) )
			if dev.deviceTypeId not in _definedShellyDeviceswAction: return

			children = self.SHELLY[dev.id]["children"]
			devs, devNos = self.getChildDevices( children)

			## eg data?hum=55&temp=33.7
			## eg data?onOffState=0/1
			cmd = data.split("?")
			useDev = dev
			if len(cmd) == 2:
				cmd = cmd[1].split("&")
				TRIGGERS = []
				for item in cmd:
					if len(item) < 1: continue
					x = item.split("=")
					if len(x) == 2:
						x.append(True)
						if   x[0] == "hum":   x[0] = "Humidity"
						elif x[0] == "temp":  x[0] = "Temperature"

						if x[0].find("onOffState") == 0:
							if   x[1] == "1": x[1] = True
							elif x[1] == "0": x[1] = False
							if x[0] == "onOffState_1":
								useDev = devs[0]
							x[0] = "onOffState"


						if x[0].find("input") == 0:
							if   x[1] == "1": x[1] = "on"
							elif x[1] == "0": x[1] = "off"
							elif x[1] == "long": 
									x[1] =datetime.datetime.now().strftime(_defaultDateStampFormat)  
									x[0] +="_long"
							elif x[1] == "short": 
									x[1] =datetime.datetime.now().strftime(_defaultDateStampFormat)  
									x[0] +="_short"

						elif x[0] not in useDev.states:
							if x[0].split("_")[0] in useDev.states:
								x[0] = x[0].split("_")[0] 
							else: x[2] = False

						TRIGGERS.append([x[0],x[1],x[2]])
					else:
						TRIGGERS.append({"cmd":item})
				if self.decideMyLog(u"HTTPlistener"):self.indiLOG.log(20,"doHTTPactionData {}   TRIGGERS:{}".format(self.SHELLY[dev.id]["ipNumber"], TRIGGERS) )
			else:
				return
			devID = str(useDev.id)

			if useDev.deviceTypeId == "shellyflood":
				# data:= {'path': >>> '/data?temp=32.62&flood=1&batV=2.83'}<<< 
				for trigger in TRIGGERS:
					if trigger[0] == "flood":
						if trigger[1] == "1" and dev.states["Flood"] != "FLOOD": 
							if self.decideMyLog(u"HTTPlistener"): self.indiLOG.log(20,"doHTTPactionData setting flood state to ON" )
							self.addToStatesUpdateDict(devID, "Flood", "FLOOD" )
							self.addToStatesUpdateDict(devID, "onOffState", True)
							if "previousAlarm" in dev.states and "lastAlarm" in dev.states:
								self.addToStatesUpdateDict(dev.id, "previousAlarm", dev.states["lastAlarm"])
							self.addToStatesUpdateDict(devID, "lastAlarm", datetime.datetime.now().strftime(_defaultDateStampFormat))
							useDev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
							self.SHELLY[useDev.id]["lastAlarm"] = time.time()

			elif useDev.deviceTypeId == "shellyht":
				# data:= /data?&hum=49&temp=29.00 
				for trigger in TRIGGERS:
					if trigger[0] == "Temperature":
						self.fillSensor(useDev, {"Temperature": trigger[1]}, "Temperature", "Temperature", unit="", decimalPlaces="")
					if trigger[0] == "Humidity":
						self.fillSensor(devs[0], {"Humidity": trigger[1]},    "Humidity",    "Humidity", unit="", decimalPlaces=0)

			elif useDev.deviceTypeId == "shellydw":
				self.indiLOG.log(20,"doHTTPactionData {};  shellydw not implemented yet message:{}".format(self.SHELLY[dev.id]["ipNumber"], data) )
				
			## cover the rest of the defined devices w actions reporting
			elif useDev.deviceTypeId in _definedShellyDeviceswAction:
				for trigger in TRIGGERS:
					if self.decideMyLog(u"HTTPlistener"):self.indiLOG.log(20,"doHTTPactionData   trigger:{}".format(trigger) )
					if trigger[0].find("onOffState") == 0:	self.fillSwitch( useDev, {trigger[0]:trigger[1]}, trigger[0])
					else: 									self.fillSwitch( useDev, {trigger[0]:trigger[1]}, trigger[0], onOffState=False)

			# missing or wrong
			else:
				self.indiLOG.log(20,"doHTTPactionData {};  not supported message:{}".format(self.SHELLY[dev.id]["ipNumber"], data) )

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"len(devs):{}".format(len(devs)))
		self.executeUpdateStatesDict()
		return 

#
###-------------------------------------------------------------------------####
	def fillSwitch(self, dev, data, token, onOffState=True):
		try:
			if onOffState and "onOffState" in dev.states:
				#self.indiLOG.log(20,"{}:  {};  data[token]:{};  state:{}".format(dev.name, onOffState, data[token], dev.states["onOffState"]))
				if data[token]: 
					self.addToStatesUpdateDict(dev.id, "onOffState",True)
					dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOn)
					if not dev.states["onOffState"]:
						if "lastOnOffChange" in dev.states and "lastStatusChange" in dev.states:
							self.addToStatesUpdateDict(dev.id, "lastOnOffChange",dev.states["lastStatusChange"])
				else:
					self.addToStatesUpdateDict(dev.id, "onOffState",False)
					if dev.states["onOffState"]:
						if "lastOnOffChange" in dev.states and "lastStatusChange" in dev.states:
							self.addToStatesUpdateDict(dev.id, "lastOnOffChange",dev.states["lastStatusChange"])
					dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
			else:
					self.addToStatesUpdateDict(dev.id, token, data[token])
	
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 


####-------------------------------------------------------------------------####
	def fillSensor(self, dev, data, token, state, unit="", decimalPlaces=""):
		try:
			### we can get:
			### :{u'tF': 72.84, u'tC': 22.69}
			### :{u'value': 72.84,... 

			if token not in data: 		return dev
			props = dev.pluginProps
			#if dev.id == 1570076651:self.indiLOG.log(20,":::::fillSensor  {}  data:{}, token:{}, state:{}".format( dev.id , data, token,  state ))


			internal = ""
			if state.split("_internal")[0] in dev.states or state+"_internal" in dev.states:
				#if dev.id == 1570076651:self.indiLOG.log(20,":::::fillSensor  passed 1")
				try: 		
					x = float(data[token])
				except:
					try:	
						x = float(data[token]["value"])
					except: 
						try: 
							x = float(data[token]["tC"]) 
							if state.find("internal") == -1: internal = "_internal"
						except: 
							self.indiLOG.log(40,"fillSensor error  token:{}, data:{} ".format(token, data, dev.name.encode("utf8") ))
							return dev

				if state.find("Temperature") > -1:
					#if dev.id == 446084418:self.indiLOG.log(20,":::::fillSensor  passed 2")
					decimalPlaces = self.tempDigits
					try:
						if "units" in data:
							if self.SHELLY[dev.id]["tempUnits"] != data["units"]:
								props["tempUnits"] = data["units"]
								dev.replacePluginPropsOnServer(props)
								dev = indigo.devices[dev.id]
								self.SHELLY[dev.id]["tempUnits"] = data["units"]
					except: pass	
					if self.SHELLY[dev.id]["tempUnits"]  == "F":
							x = (x-32.)*5./9.
					x , xui = self.convTemp(x)
					if dev.id == 446084418: self.indiLOG.log(20,":::::fillSensor  {}  token:{}, x:{}, xui:{}; shelly units:{}, internal:{}".format( dev.id , token,  x, xui.encode("utf8"), self.SHELLY[dev.id]["tempUnits"],internal  ))
					if "Temperature" in dev.states:
						self.addToStatesUpdateDict(str(dev.id), "Temperature", x, uiValue=xui, decimalPlaces=decimalPlaces)
						if "displaySelect" in props and props["displaySelect"] == "Temperature":
							dev.updateStateImageOnServer(indigo.kStateImageSel.TemperatureSensorOn)
						self.fillMinMaxSensors(dev,state,x,decimalPlaces=decimalPlaces)
					if "Temperature_internal" in dev.states:
						self.addToStatesUpdateDict(str(dev.id), "Temperature_internal", x, uiValue=xui, decimalPlaces=decimalPlaces)
					return dev

				elif state == "Humidity":
					if state in dev.states:
						x , xui = self.convHum(x)
						self.addToStatesUpdateDict(str(int(dev.id)), state, x, uiValue=xui, decimalPlaces=decimalPlaces)
						if "displaySelect" in props and props["displaySelect"] == "Humidity":
							dev.updateStateImageOnServer(indigo.kStateImageSel.HumiditySensorOn)
						self.fillMinMaxSensors(dev,"Humidity",x,decimalPlaces=decimalPlaces)


				else:
					if state in dev.states:
						if decimalPlaces == 0:	xui = "{:.0f}{}".format(x,unit.encode("utf8"))
						if decimalPlaces == 1:	xui = "{:.1f}{}".format(x,unit.encode("utf8"))
						if decimalPlaces == 2:	xui = "{:.2f}{}".format(x,unit.encode("utf8"))
						else: 					xui = "{}{}".format(x,unit.encode("utf8"))
						self.addToStatesUpdateDict(str(dev.id), state, x, uiValue=xui, decimalPlaces=decimalPlaces)
						return dev


		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40," token:{}, data:{}".format(token, data ))
		return dev

####-------------------------------------------------------------------------####
	def getTimetimeFromDateString(self, dateString, fmrt=_defaultDateStampFormat): 
		if len(dateString) > 9:
			try:
				return  time.mktime(  datetime.datetime.strptime(dateString, fmrt).timetuple()  )
			except:
				return 0		
		else:
			return 0



####-------------------------------------------------------------------------####
	def convTemp(self, temp):
		try:
			suff=""
			useFormat="{:.1f}"
			temp = float(temp)
			if temp == 999.9:
				return 999.9,"badSensor", 1
			if self.tempUnits == u"Fahrenheit":
				temp = temp * 9. / 5. + 32.
				suff = u"ºF"
			elif self.tempUnits == u"Kelvin":
				temp += 273.15
				suff = u"ºK"
			else:
				suff = u"ºC"
			if self.tempDigits == 0:
				cString = "%d"
				useFormat ="{:d}"
			else:
				cString = "%."+unicode(self.tempDigits)+"f"
			uiValue = (cString % temp).strip()+suff
			return round(temp,self.tempDigits) , uiValue 
		except:pass
		return -99, u""



####-------------------------------------------------------------------------####
	def convHum(self, hum):
		try:
			humU = (u"%3d" %float(hum)).strip()
			return int(float(hum)), humU + u"%"
		except:
			return -99, u""



####----------------------reset sensor min max at midnight -----------------------------------####
	def resetMinMaxSensors(self, init=False):
		try:
			nHour = (datetime.datetime.now()).hour 
			for dev in indigo.devices.iter(self.pluginId):
				if	dev.enabled: 
					for ttx in _GlobalConst_fillMinMaxStates:
						if ttx in dev.states and ttx+u"MaxToday" in dev.states:
							try:	val = float(dev.states[ttx])
							except: val = 0
							try:
								xxx = unicode(dev.states[ttx]).split(".")
								if len(xxx) ==1:
									decimalPlaces = 1
								else:
									decimalPlaces = len(xxx[1])
							except:
								decimalPlaces = 2

							if init: # at start of pgm
								reset = False
								try: 
									int(dev.states[ttx+u"MinYesterday"])
								except:
									reset = True
								if not reset: 
									try:
										if	(float(dev.states[ttx+u"MaxToday"]) == float(dev.states[ttx+u"MinToday"]) and float(dev.states[ttx+u"MaxToday"]) == 0.) :	 reset = True
									except: pass
								if reset:
									self.addToStatesUpdateDict(dev.id,ttx+u"MaxYesterday", val,decimalPlaces=decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MinYesterday", val,decimalPlaces=decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MaxToday",		val,decimalPlaces=decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MinToday",		val,decimalPlaces=decimalPlaces)

							elif nHour ==0:	 # update at midnight 
									self.addToStatesUpdateDict(dev.id,ttx+u"MaxYesterday",  dev.states[ttx+u"MaxToday"], decimalPlaces = decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MinYesterday",  dev.states[ttx+u"MinToday"], decimalPlaces = decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MaxToday",		dev.states[ttx], decimalPlaces = decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MinToday",		dev.states[ttx], decimalPlaces = decimalPlaces)
			self.executeUpdateStatesDict()

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return
####----------------------reset sensor min max at midnight -----------------------------------####
	def fillMinMaxSensors(self,dev,stateName,value,decimalPlaces):
		try:
			if value == "": return 
			if stateName not in _GlobalConst_fillMinMaxStates: return 
			if stateName in dev.states and stateName+u"MaxToday" in dev.states:
				val = float(value)
				if val > float(dev.states[stateName+u"MaxToday"]):
					self.addToStatesUpdateDict(str(dev.id),stateName+u"MaxToday",	 val, decimalPlaces=decimalPlaces)
				if val < float(dev.states[stateName+u"MinToday"]):
					self.addToStatesUpdateDict(str(dev.id),stateName+u"MinToday",	 val, decimalPlaces=decimalPlaces)
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return

#



####------------------shelly poller queue management ----------------------------START
####------------------shelly poller queue management ----------------------------START
####------------------shelly poller queue management ----------------------------START


####-------------------------------------------------------------------------####
	def addToShellyPollerQueue(self, shellyIndigoDevNumber, page, now=False):
		try:
			if self.SHELLY[shellyIndigoDevNumber]["isChild"]: return
			if self.SHELLY[shellyIndigoDevNumber]["state"] != "running":
				self.startShellyDevicePoller("start", shellySelect=shellyIndigoDevNumber)
				time.sleep(0.1)
			try: 
				self.SHELLY[shellyIndigoDevNumber]["now"] = now	
				self.SHELLY[shellyIndigoDevNumber]["queue"].put(page)
			except Exception, e:
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				self.indiLOG.log(20,"addToShellyPollerQueue error for  devid:{} in shelly:{}".format(shellyIndigoDevNumber,self.SHELLY[shellyIndigoDevNumber]))

			#self.indiLOG.log(20,"addToShellyPollerQueue added devid:{} page:{} to queue:{}".format(shellyIndigoDevNumber, page, list(self.SHELLY[shellyIndigoDevNumber]["queue"].queue)))
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return


####-------------------------------------------------------------------------####
	def startShellyDevicePoller(self, state, shellySelect="all"):
		try:
			if state =="start":
				self.laststartUpdateshellyQueues = time.time()
				for shellyIndigoDevNumber in self.SHELLY:
					if self.SHELLY[shellyIndigoDevNumber]["isChild"]: continue
					try:
						if not self.SHELLY[shellyIndigoDevNumber][u"deviceEnabled"]: 
							continue
					except Exception, e:
						self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
						self.indiLOG.log(40,"shellyIndigoDevNumber:{};  SHELLY:{}".format(shellyIndigoDevNumber, self.SHELLY))
						continue

					if shellySelect == "all" or shellyIndigoDevNumber == shellySelect:
							if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(20, u"starting UpdateshellyQueues for devId:{} ".format(shellyIndigoDevNumber) )
							if self.SHELLY[shellyIndigoDevNumber]["state"] != "running":
								self.startOneShellyDevicePoller(shellyIndigoDevNumber)

			elif state =="restart":
				if (shellySelect == "all" and time.time() - self.laststartUpdateshellyQueues > 70) or shellySelect != "all":
					self.laststartUpdateshellyQueues = time.time()
					for shellyIndigoDevNumber in self.SHELLY:
						if self.SHELLY[shellyIndigoDevNumber]["isChild"]: continue
						if not self.SHELLY[shellyIndigoDevNumber][u"deviceEnabled"] : continue
						if shellySelect == "all" or shellyIndigoDevNumber == shellySelect:
							if time.time() - self.SHELLY[shellyIndigoDevNumber]["lastCheck"]> 100:
								self.stopShellyDevicePoller(shellySelect=shellyIndigoDevNumber)
								time.sleep(0.5)
							if  time.time() - self.SHELLY[shellyIndigoDevNumber]["lastCheck"]> 100:
								self.startOneShellyDevicePoller(shellyIndigoDevNumber, reason="active messages pending timeout")
							elif self.SHELLY[shellyIndigoDevNumber]["state"] != "running":
								self.indiLOG.log(20, u"re - starting UpdateshellyQueues for devId:{} ".format(shellySelect) )
								self.startOneShellyDevicePoller(shellyIndigoDevNumber, reason="not running")
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"self.SHELLY:{}".format(self.SHELLY))
		return 

####-------------------------------------------------------------------------####
	def startOneShellyDevicePoller(self, shellyIndigoDevNumber, reason=""):
		try:
			if self.SHELLY[shellyIndigoDevNumber]["isChild"]: return
			if shellyIndigoDevNumber not in self.SHELLY:
				for dev in indigo.devices.iter(self.pluginId):
					if dev.id == int(shellyIndigoDevNumber):
						self.initShelly(dev.id, dev.states["MAC"], dev.address, deviceTypeId=dev.deviceTypeId, startPoller=False)

			if shellyIndigoDevNumber not in self.SHELLY:
					self.indiLOG.log(20, u"no  {} is not in indigo devices, need to create first".format(shellyIndigoDevNumber) )
					return 
			
			if self.SHELLY[shellyIndigoDevNumber]["state"] == "running":
					if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(20, u"no need to start Thread, ipnumber {} thread already running".format(self.SHELLY[shellyIndigoDevNumber]["ipNumber"]) )
					return 

			if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(20, u".. (re)starting   thread for ipnumber:{}, state was: {}; reason:{}".format(self.SHELLY[shellyIndigoDevNumber]["ipNumber"], self.SHELLY[shellyIndigoDevNumber]["state"], reason) )
			self.SHELLY[shellyIndigoDevNumber]["lastCheck"]= time.time()
			self.SHELLY[shellyIndigoDevNumber]["state"]	= "start"
			self.SHELLY[shellyIndigoDevNumber]["thread"] = threading.Thread(name=u'self.shellyPollerThread', target=self.shellyPollerThread, args=(shellyIndigoDevNumber,))
			self.SHELLY[shellyIndigoDevNumber]["thread"].start()
			time.sleep(0.2) # give other procs time to finish
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 
###-------------------------------------------------------------------------####
	def stopShellyDevicePoller(self, shellySelect="all"):
		if shellySelect != "all":
			if shellySelect in self.SHELLY:
				if self.SHELLY[shellySelect]["state"] == "running":
					self.indiLOG.log(20, u"stopping Thread, ipnumber {}, devId:{}".format(self.SHELLY[shellySelect]["ipNumber"], shellySelect) )
					self.stopOneShellyDevicePoller(shellySelect, reason="")
					return 
		else:
			for shellyIndigoDevNumber in self.SHELLY:
				self.stopOneShellyDevicePoller(shellyIndigoDevNumber, reason="")
		return 
###-------------------------------------------------------------------------####
	def stopOneShellyDevicePoller(self, shellyIndigoDevNumber, reason=""):
		if shellyIndigoDevNumber in self.SHELLY:
			self.SHELLY[shellyIndigoDevNumber]["state"]	= "stop "+reason
			self.SHELLY[shellyIndigoDevNumber]["reset"]	= True
		return 
####-------------------------------------------------------------------------####
	def resetUpdateQueue(self, shellyIndigoDevNumber):
		self.SHELLY[shellyIndigoDevNumber]["reset"]= True
		return
####-------------------------------------------------------------------------####
	def testIfAlreadyInQ(self, page, ipnumber):
		currentQueue = list(self.SHELLY[shellyIndigoDevNumber]["queue"].queue)
		for q in currentQueue:
			if q == page:
				if self.decideMyLog(u"Polling"): self.indiLOG.log(10, u"NOT adding to update list already presend {}".format(next) )
				return True
		return False

####-------------------------------------------------------------------------####
	def shellyPollerThread(self, shellyIndigoDevNumber):
		try:
			self.SHELLY[shellyIndigoDevNumber]["state"] = "running"
			threadNumber = time.time()
			if self.decideMyLog(u"Polling"): self.indiLOG.log(20, u"shellyPollerThread starting  for devId:{}; ipnumber# {}, threadNumber:{}".format(shellyIndigoDevNumber, self.SHELLY[shellyIndigoDevNumber]["ipNumber"], threadNumber) )
			tries 		= 0
			retryTime 	= .0
			lastDefaultRequestTime = time.time()
			fromQueue  = True
			lastEXE = time.time()
			ipNumber = self.SHELLY[shellyIndigoDevNumber]["ipNumber"]
			self.SHELLY[shellyIndigoDevNumber]["threadNumber"] = threadNumber
			while self.SHELLY[shellyIndigoDevNumber]["state"] == "running":
				self.SHELLY[shellyIndigoDevNumber]["lastCheck"] = time.time()
				#has another process started? if yes, stop this one.
				if self.SHELLY[shellyIndigoDevNumber]["threadNumber"] != threadNumber: 
					if shellyIndigoDevNumber !=0: self.indiLOG.log(20, u"shellyPollerThread stopping due to other thread running  for devId:{}; ipnumber# {}".format(shellyIndigoDevNumber, self.SHELLY[shellyIndigoDevNumber]["ipNumber"]) )
					break
				addBack =[]
				ipNumber = self.SHELLY[shellyIndigoDevNumber]["ipNumber"]

				waitStart = time.time()
				for ii in range(1000):
					if time.time() - waitStart > 0.2 + retryTime: break
					time.sleep(0.2 + retryTime)
					try:
						if ipNumber != self.SHELLY[shellyIndigoDevNumber]["ipNumber"]:
							self.indiLOG.log(20, u"shellyPollerThread changed IPnumber:{}, continuing w new IP#{};  devId:{}}".format(ipNumber, self.SHELLY[shellyIndigoDevNumber]["ipNumber"], shellyIndigoDevNumber) )
							ipNumber = self.SHELLY[shellyIndigoDevNumber]["ipNumber"]
							break
					except: 
						# this device has been removed, exit thread
						if shellyIndigoDevNumber not in self.SHELLY:
							break 
					if self.SHELLY[shellyIndigoDevNumber]["now"]: 
						lastDefaultRequestTime = -10
						####self.indiLOG.log(20, u"shellyPollerThread now: true   ipnumber# {}".format( self.SHELLY[shellyIndigoDevNumber]["ipNumber"]) )
						break


				if shellyIndigoDevNumber not in self.SHELLY: break
				self.SHELLY[shellyIndigoDevNumber]["now"] = False

				if not self.isValidIP(ipNumber): 
					retryTime = 1
					continue

				defaultTask 	 = self.SHELLY[shellyIndigoDevNumber]["defaultTask"]
				pollingFrequency = self.SHELLY[shellyIndigoDevNumber]["pollingFrequency"]
				if pollingFrequency == -1:
					pollingFrequency = 10
					if self.SHELLY[shellyIndigoDevNumber]["lastSuccessfullConfigPush"] >0 and time.time() - self.SHELLY[shellyIndigoDevNumber]["lastSuccessfullConfigPush"] < self.repeatConfigPush:
						pollingFrequency = _emptyProps[self.SHELLY[shellyIndigoDevNumber]["devTypeId"]]["props"]["automaticPollingFrequency"]

					

				while not self.SHELLY[shellyIndigoDevNumber]["queue"].empty() or (time.time() - lastDefaultRequestTime) > pollingFrequency:
					self.SHELLY[shellyIndigoDevNumber]["lastActive"] = time.time()

					if lastDefaultRequestTime < 0: # thsi is a now request for status
						lastDefaultRequestTime = 1
						page = defaultTask
						fromQueue = False
						
					else:
						if not self.SHELLY[shellyIndigoDevNumber]["queue"].empty(): 
							page = self.SHELLY[shellyIndigoDevNumber]["queue"].get()
							fromQueue = True
						else:
							page = defaultTask
							fromQueue = False

						lastDefaultRequestTime = time.time()

					lastEXE = time.time()

					if not self.SHELLY[shellyIndigoDevNumber][u"deviceEnabled"]: 		
						if self.decideMyLog(u"test"): self.indiLOG.log(20, u"shellyPollerThread  {}; skipping:{} is OFF".format(shellyIndigoDevNumber, ipNumber) )
						self.SHELLY[shellyIndigoDevNumber]["reset"]= True
						break

					if self.decideMyLog(u"test"): self.indiLOG.log(10, u"shellyPollerThread  {};  executing:{}   {}".format(shellyIndigoDevNumber, ipNumber, page) )

					if self.SHELLY[shellyIndigoDevNumber][u"ipNumber"] == "": 	
						if self.decideMyLog(u"test"): self.indiLOG.log(20, u"shellyPollerThread {}; skipping:{}  ip set blank".format(shellyIndigoDevNumber, ipNumber)  )
						continue

					if self.SHELLY[shellyIndigoDevNumber]["reset"]: 
						if self.decideMyLog(u"Polling"): self.indiLOG.log(20, u"shellyPollerThread  {}; resetting:{} queue data".format(shellyIndigoDevNumber, ipNumber) )
						continue

					#if self.decideMyLog(u"Polling"): self.indiLOG.log(20, u" send to ipNumber:{}  page:{}".format(ipNumber, page) )
					retCode, jData = self.execShellySend(ipNumber, page)
					#if self.decideMyLog(u"Polling"): self.indiLOG.log(20, "ret page:{}; json:{}".format(page,jData) )

					if retCode ==0: # all ok?
						self.addtoAnalyzePollerQueue({"shellyIndigoDevNumber":shellyIndigoDevNumber,"page":page,"ipNumber":ipNumber,"data": jData})
						if shellyIndigoDevNumber == 0: 
							self.SHELLY[shellyIndigoDevNumber]["ipNumber"] = ""
						tries      = 0
						retryTime  = 0
						continue

					else: # no response, retry ..
						tries      +=1
						retryTime  = 2

						if tries  > 5 and tries < 10: # wait a little longer
							if self.decideMyLog(u"Polling"): self.indiLOG.log(20, u"shellyPollerThread last querry were not successful wait, then try again; ip:{}".format(ipNumber))
							retryTime = 5

						if tries  > 20:
							if self.decideMyLog(u"Polling"): self.indiLOG.log(20, u"shellyPollerThread last querry were not successful  skip; ip:{}".format(ipNumber))
							retryTime = 0
							break

						if fromQueue: addBack.append(page)
					if shellyIndigoDevNumber not in self.SHELLY: break

				try: 	self.SHELLY[shellyIndigoDevNumber]["queue"].task_done()
				except: pass
				if addBack !=[]:
					for nxt in addBack:
						self.SHELLY[shellyIndigoDevNumber]["queue"].put(nxt)
				self.SHELLY[shellyIndigoDevNumber]["reset"]=False

		except Exception, e:
			if unicode(e).find("None") == -1:
				self.indiLOG.log(20,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		try: 
			if shellyIndigoDevNumber != 0: self.indiLOG.log(20, u"shellyPollerThread: ip#:{}  devId:{}; update thread stopped".format(ipNumber, shellyIndigoDevNumber) )
		except: pass
		return



####-------------------------------------------------------------------------####
	def execShellySend(self,  ipNumber, page):
		ret = ""
		try:
			self.lastUpdateSend = time.time()

			pingR = self.testPing(ipNumber)
			if pingR != 0:
				if self.decideMyLog(u"Ping") : self.indiLOG.log(20,u" ipnumber{}  does not answer ping - , skipping update".format(ipNumber) )
				return 1, "ping offline"
	
			#if self.decideMyLog(u"Polling"): self.indiLOG.log(20, u"execShellySend  send to ipNumber:{}  page:{}".format(ipNumber, page) )
			retJson = self.getJsonFromDevices(ipNumber, page)
			return 0, retJson

		except Exception, e:
			if unicode(e).find("None") == -1:
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 1, ret


####-------------------------------------------------------------------------####
	def testPing(self, ipN):
		try:
			ss = time.time()
			ret = subprocess.call(u"/sbin/ping  -c 1 -W 40 -o " + ipN, shell=True) # send max 2 packets, wait 40 msec   if one gets back stop
			if self.decideMyLog(u"Ping"): self.indiLOG.log(10, u" sbin/ping  -c 1 -W 40 -o {} return-code: {}".format(ipN, ret) )

			if int(ret) ==0:  return 0
			self.sleep(0.1)
			ret = subprocess.call(u"/sbin/ping  -c 1 -W 400 -o " + ipN, shell=True)
			if self.decideMyLog(u"Ping"): self.indiLOG.log(10, "/sbin/ping  -c 1 -W 400 -o {} ret-code: ".format(ipN, ret) )

			#indigo.server.log(  ipN+"-2  "+ unicode(ret) +"  "+ unicode(time.time() - ss)  )

			if int(ret) ==0:  return 0
			return 1
		except Exception, e:
			if unicode(e).find("None") == -1:
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		#indigo.server.log(  ipN+"-3  "+ unicode(ret) +"  "+ unicode(time.time() - ss)  )
		return 1




####------------------shelly update queue management ----------------------------END
####------------------shelly update queue management ----------------------------END
####------------------shelly update queue management ----------------------------END





	####-----------------
	########################################
	# General Action callback
	######################
	def actionControlUniversal(self, action, dev):
		###### BEEP ######
		if action.deviceAction == indigo.kUniversalAction.Beep:
			# Beep the hardware module (dev) here:
			# ** IMPLEMENT ME **
			indigo.server.log(u"sent \"{}\" beep request not implemented".format(dev.name))

		###### STATUS REQUEST ######
		elif action.deviceAction == indigo.kUniversalAction.RequestStatus:
			self.sendStatusRequest(dev)
		return


####-------------------------------------------------------------------------####
	def sendStatusRequest(self, dev):
		try:
			queueID = dev.id
			props = dev.pluginProps
			if int(props["parentIndigoId"]) !=0:	queueID = int(props["parentIndigoId"])

			page = "settings"
			if self.decideMyLog(u"Actions"): self.indiLOG.log(20,"sending to dev {} page={}".format(dev.name.encode("utf8"), page))
			time.sleep(0.2)
			self.addToShellyPollerQueue( queueID, page)
			page = "status"
			if self.decideMyLog(u"Actions"): self.indiLOG.log(20,"sending to dev {} page={}".format(dev.name.encode("utf8"), page))
			self.addToShellyPollerQueue( queueID, page)
			return
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return


####-------------------------------------------------------------------------####
	def actionControlGeneral(self, action, dev):
		###### STATUS REQUEST ######
		return 


	########################################
	# Sensor Action callback
	######################
	def actionControlSensor(self, action, dev):
		return 

		###### TURN ON ######
		if action.sensorAction == indigo.kSensorAction.TurnOn:
			self.addToStatesUpdateDict(dev.id,u"status", u"up")

		###### TURN OFF ######
		elif action.sensorAction == indigo.kSensorAction.TurnOff:
			self.addToStatesUpdateDict(dev.id,u"status", u"down")

		###### TOGGLE ######
		elif action.sensorAction == indigo.kSensorAction.Toggle:
			if dev.onState: 
				self.addToStatesUpdateDict(dev.id,u"status", "down")
				dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
			else:
				self.addToStatesUpdateDict(dev.id,u"status", "up")
				dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOn)

		self.executeUpdateStatesDict()



# noinspection SpellCheckingInspection
	def actionControlDimmerRelay(self, action, dev):
		try:
			devId = dev.id
			if self.decideMyLog(u"Actions"): self.indiLOG.log(20,"ACTIONS:  devId {} action={}; values:{}".format(devId, action.deviceAction, action.actionValue))

			props = dev.pluginProps
			if props["isChild"]: queueID = int(props["parentIndigoId"])
			else:				 queueID = dev.id


			setAction = False
			actionValues ={}
			IndigoStateMapToShellyDev ={'redLevel':"red", 'greenLevel':"green", 'blueLevel':"blue", 'whiteLevel':"white", "brightnessLevel":"brightness", "whiteTemperature":"temp","TurnOff":"turn","TurnOn":"turn"}

			page 	  = ""
			extraPage = ""

			try: 	WhiteTemperatureMin = _emptyProps[dev.deviceTypeId]["WhiteTemperatureMin"]
			except:	WhiteTemperatureMin = 1000
			try: 	WhiteTemperatureMax = _emptyProps[dev.deviceTypeId]["WhiteTemperatureMax"]
			except:	WhiteTemperatureMax = 9000
			try:	rgbLimits = _emptyProps[dev.deviceTypeId]["rgbLimits"]
			except:	rgbLimits = [0,0]

			if dev.deviceTypeId in ["ShellyBulbDuo"]:
				if action.deviceAction == indigo.kDeviceAction.SetColorLevels:
					actionValues = action.actionValue
					setAction = True

				channel = "white"
				if "whiteLevel" in actionValues:
					actionValues["brightnessLevel"] = actionValues["whiteLevel"]
					del actionValues["whiteLevel"]
				if "whiteTemperature" in actionValues:
					actionValues["whiteLevel"] = int( 100.*(actionValues["whiteTemperature"]-WhiteTemperatureMin)/(WhiteTemperatureMax-WhiteTemperatureMin) )
					del actionValues["whiteTemperature"]

				try: 	del actionValues["redLevel"]
				except: pass
				try: 	del actionValues["blueLevel"]
				except: pass
				try: 	del actionValues["greenLevel"]
				except: pass

				###### TURN ON ######
				if action.deviceAction == indigo.kDimmerRelayAction.TurnOn:
					actionValues["TurnOn"] 	= "on"
					setAction = True

				###### TURN OFF ######
				if action.deviceAction == indigo.kDimmerRelayAction.TurnOff:
					actionValues["TurnOff"] 	= "off"
					setAction = True

				###### TOGGLE ######
				if action.deviceAction == indigo.kDimmerRelayAction.Toggle:
					if "onOffState" in dev.states:
						newOnState = not dev.states["onOffState"]
						if newOnState: 	actionValues["TurnOff"] = "off"
						else: 			actionValues["TurnOn"] 	= "on"
						setAction = True


				for colorAction in IndigoStateMapToShellyDev:	
					if colorAction in actionValues:
						if colorAction in ["TurnOff","TurnOn"]:
							page += "{}={}&".format("turn", actionValues[colorAction])
						else:
							page += "{}={}&".format(IndigoStateMapToShellyDev[colorAction], int(min(100, max(0,actionValues[colorAction]))))
				if self.decideMyLog(u"Actions"): self.indiLOG.log(20,"ACTIONS: dev {} sending  channel:{};  page:{} deviceTypeId:{}, actionValues:{}".format(dev.name, channel, page, dev.deviceTypeId,actionValues ))






			elif dev.deviceTypeId in ["shellybulb","shellyrgbw2","shellydimmer","ShellyVintage"]:
				if action.deviceAction == indigo.kDeviceAction.SetColorLevels:
					actionValues = action.actionValue
					setAction = True

				if dev.deviceTypeId in["shellydimmer"]:	channel = "white"
				elif "mode" in dev.states:				channel = dev.states["mode"] # == white or color
				else:									channel = "white" 

				if "onOffState" in dev.states:
					if dev.states["onOffState"]: onOffState = 1
					else: 						 onOffState = -1
				else:							 onOffState = 0



				if "redLevel" in actionValues or "redLevel" in actionValues or "blueLevel" in actionValues:
						if channel != "color": extraPage = "settings?mode=color"
						actionValues["whiteLevel"] 	= 0

				elif "whiteLevel" in actionValues  and dev.deviceTypeId in ["ShellyBulbDuo"]:
						if channel != "color": extraPage = "settings?mode=color"
						actionValues["brightness"] 	= int(dev.states["whiteLevel"])
						del actionValues["redLevel"]
						del actionValues["blueLevel"]
						del actionValues["greenLevel"]

				elif "whiteLevel" in actionValues:
						if channel != "color": extraPage = "settings?mode=color"
						actionValues["redLevel"] 	= 0
						actionValues["greenLevel"] 	= 0
						actionValues["blueLevel"] 	= 0

				elif "whiteTemperature" in actionValues:
					if channel == "color": extraPage = "settings?mode=white"
					try: actionValues["brightnessLevel"] = int(dev.states["whiteLevel"])
					except: pass
					setAction = True

				elif "brightnessLevel" in actionValues:
					if channel == "color": extraPage = "settings?mode=white"
					setAction = True


				###### TURN ON ######
				if action.deviceAction == indigo.kDimmerRelayAction.TurnOn:
					actionValues["TurnOn"] 	= "on"
					setAction = True

				###### TURN OFF ######
				if action.deviceAction == indigo.kDimmerRelayAction.TurnOff:
					actionValues["TurnOff"] 	= "off"
					setAction = True

				###### TOGGLE ######
				if action.deviceAction == indigo.kDimmerRelayAction.Toggle:
					if "onOffState" in dev.states:
						newOnState = not dev.states["onOffState"]
						if newOnState: 	actionValues["TurnOff"] = "off"
						else: 			actionValues["TurnOn"] 	= "on"
						setAction = True

					###### SET BRIGHTNESS ######
				if action.deviceAction == indigo.kDimmerRelayAction.SetBrightness:
					if channel == "color":
						actionValues["redLevel"] 	= action.actionValue
						actionValues["greenLevel"] 	= action.actionValue
						actionValues["blueLevel"] 	= action.actionValue
						actionValues["whiteLevel"] 	= 0
					else:
						actionValues["brightnessLevel"] 	= max(1,action.actionValue)
					setAction = True


					###### BRIGHTEN BY ######
				if action.deviceAction == indigo.kDimmerRelayAction.BrightenBy:
					newBrightness = dev.brightness + action.actionValue
					if newBrightness > 100:
						newBrightness = 100
					if channel == "color":
						actionValues["redLevel"] 	= newBrightness
						actionValues["greenLevel"] 	= newBrightness
						actionValues["blueLevel"] 	= newBrightness
						actionValues["whiteLevel"] 	= 0
					else:
						actionValues["brightnessLevel"]	= newBrightness
					setAction = True

					###### DIM BY ######
				if action.deviceAction == indigo.kDimmerRelayAction.DimBy:
					newBrightness = dev.brightness - action.actionValue
					if newBrightness <= 0: 	newBrightness = 1
					if newBrightness >100: 	newBrightness = 100
					if channel == "color":
						actionValues["redLevel"] 	= newBrightness
						actionValues["greenLevel"] 	= newBrightness
						actionValues["blueLevel"] 	= newBrightness
						actionValues["whiteLevel"] 	= 0
					else:
						actionValues["brightnessLevel"]	= newBrightness
					setAction = True

				if self.decideMyLog(u"Actions"): self.indiLOG.log(20,"====== sending actionValues={}".format(actionValues))
				if setAction:
						for colorAction in IndigoStateMapToShellyDev:	
							if colorAction in actionValues:
								if colorAction in ["TurnOff","TurnOn"]:
									page += "{}={}&".format("turn", actionValues[colorAction])
								else:
									if actionValues[colorAction] > 0:
										if onOffState == -1: 
											page += "{}={}&".format("turn", "on")
											onOffState = 0
									if True: # actionValues[colorAction] != dev.states[colorAction]:
										if colorAction == "whiteTemperature": # this requires to be in white channel
											page += "{}={}&".format(IndigoStateMapToShellyDev[colorAction], int(min(WhiteTemperatureMax,max(WhiteTemperatureMin,actionValues[colorAction]))))
										elif colorAction == "whiteLevel":
											page += "{}={}&".format(IndigoStateMapToShellyDev[colorAction], int(min(rgbLimits[1],max(rgbLimits[0],actionValues[colorAction]*255/100.))))
										elif colorAction == "brightnessLevel":
											page += "{}={}&".format(IndigoStateMapToShellyDev[colorAction], int(min(100,         max(1,actionValues[colorAction]))))
										else:
											page += "{}={}&".format(IndigoStateMapToShellyDev[colorAction], int(min(rgbLimits[1],max(rgbLimits[0],actionValues[colorAction]*255/100.))))


			elif dev.deviceTypeId in ["shelly1","shelly1pm","shellyswitch25","shellyswitch25-child","shellyem","shelly4pro","shelly4pro-child"]:
				if self.SHELLY[dev.id]["isChild"]:	channel = str(dev.states["childNo"])
				else: 								channel	= "0"
				###### TURN ON ######
				if action.deviceAction == indigo.kDimmerRelayAction.TurnOn:
					actionValues["TurnOn"] 	= "on"
					setAction = True

				###### TURN OFF ######
				if action.deviceAction == indigo.kDimmerRelayAction.TurnOff:
					actionValues["TurnOff"] = "off"
					setAction = True

				###### TOGGLE ######
				if action.deviceAction == indigo.kDimmerRelayAction.Toggle:
					if "onOffState" in dev.states:
						newOnState = not dev.states["onOffState"]
						if newOnState: 	actionValues["TurnOff"] = "off"
						else: 			actionValues["TurnOn"] 	= "on"
						setAction = True

				if setAction:
						for colorAction in IndigoStateMapToShellyDev:	
							if colorAction in actionValues:
									page += "{}={}&".format("turn", actionValues[colorAction])

			else:
				self.indiLOG.log(40,"action{}  for {}  not implemented".format(dev.name, dev.deviceTypeId))


			if len(page) > 0:
				if extraPage !="":
					self.addToShellyPollerQueue( queueID, extraPage, now=True)
					time.sleep(0.2)


				page = page.strip("&")
				page = _emptyProps[dev.deviceTypeId]["setPageActionPageOnShellyDev"][channel]+page			
				if self.decideMyLog(u"Actions"): self.indiLOG.log(20,"ACTIONS: dev {} sending  channel:{};  page:{} deviceTypeId:{}".format(dev.name, channel, page, dev.deviceTypeId))
				self.addToShellyPollerQueue( queueID, page, now=True)

			else:
				return

			return
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return




####-------------------------------------------------------------------------####
	def pushConfigToShellyDevice(self, devId, delay = 0):
		try:
			if devId not in self.SHELLY: return
			self.sleep(delay) 
			dev = indigo.devices[devId]
			deviceTypeId = dev.deviceTypeId
			props = dev.pluginProps
			ipNumber = self.SHELLY[devId]["ipNumber"]
			port = self.portOfShellyDevices
			pushTried = False
			pushSuccessfull = False
			if self.pushRequest > 0: self.pushRequest = time.time() + 100
			if deviceTypeId in _emptyProps:  
				if "action_url" in _emptyProps[deviceTypeId]:  
					pageBack = "http://"+self.IndigoServerIPNumber+":"+str(self.portOfIndigoServer)
					actionURLs = _emptyProps[deviceTypeId]["action_url"]
					#self.indiLOG.log(20,"action setting :{} ".format(actionURL) )
					for parameter in actionURLs:
						for setting in actionURLs[parameter]:
							searchFor1 = actionURLs[parameter][setting]
							searchFor2 = pageBack
							if setting =="none":
								page = parameter+pageBack +"/"+ actionURLs[parameter][setting]
								###  = eg settings/?report_url=ttp://ip:port/data?"
							elif actionURLs[parameter][setting] == "disable":
								page = parameter+ setting + "=x" 
								searchFor1 = parameter
								searchFor2 = "x"
								###  = eg settings/relay/0?shortpush_url="
							else:
								page = parameter + setting + "=" + pageBack +"/?"+ actionURLs[parameter][setting]
								###  = eg settings/relay/0?btn_on_url=http://ip:port/input=on"
							if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(20,"{}, sending action page:{}".format(ipNumber, page) )
							pushTried = True
							retCode, jData = self.execShellySend(ipNumber, page)
							udata = unicode(jData)
							if udata.find( searchFor1 ) == -1 or udata.find(searchFor2) ==1:
								if udata.find("offline") == -1:
									self.indiLOG.log(20,"send action_url to devId:{}, send page:{}; answer not ok:>{}<".format(devId, page, udata) )
							else:
								self.SHELLY[devId]["lastSuccessfullConfigPush"] = time.time()
								pushSuccessfull = True
								self.pushRequest = -1
			if pushTried:
				if pushSuccessfull:
					self.indiLOG.log(20,"successfull action_url push to devId:{}".format(devId) )
				else:
					self.indiLOG.log(20,"not successfull action_url push to devId:{}, send page:{}; device is offline".format(devId, page) )


			pushSuccessfull = False
			pushTried = False
			for prop in props:
				if prop.find("SENDTOSHELLYDEVICE-") > -1:
					if props[prop] == "none": continue
					## remove tag then 
					##  replace -.- with / and QqQ with ?  ..  /? do not work in XML tag name
					## should be come something like:  settings/relay/1?btn_type=toggle
					if prop not in settingCmds: continue
					cmd 			= settingCmds[prop][0]
					setTo 			= props[prop]
					findItem 		= settingCmds[prop][1]
					page 			= cmd + setTo
					checkFeedBack 	= True
					if self.decideMyLog(u"SetupDevices"):self.indiLOG.log(20,"{},  setting page >{}<".format(ipNumber, page) )
					pushTried = True
					retCode, jData = self.execShellySend(ipNumber, page)
					udata = unicode(jData)
					if checkFeedBack and (udata.find( findItem ) == -1):
						if udata.find("offline")  == -1:
							self.indiLOG.log(20,"send config to devId:{} not successfull for page:{}; answer not ok:>{}<".format(devId, page, udata) )
					else:
						self.SHELLY[devId]["lastSuccessfullConfigPush"] = time.time()
						pushSuccessfull = True
						self.pushRequest = -1

			if pushTried:
				if pushSuccessfull:
					self.indiLOG.log(20,"successfull config push to devId:{}".format(devId) )
				else:
					self.indiLOG.log(20,"not successfull config push to devId:{}, send page:{}; device is offline".format(devId, page) )



			if time.time() - self.SHELLY[devId]["lastSuccessfullConfigPush"]  < 100:
				self.addToStatesUpdateDict(str(devId),"lastSuccessfullConfigPush", datetime.datetime.now().strftime(_defaultDateStampFormat))



		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 




##############################################################################################

	####-----------------	 ---------
	def getJsonFromDevices(self, ipNumber, page, jsonAction="", port = "", testHTTP=False, noJson=False):

		try:
			#if self.decideMyLog(u"Polling"): self.indiLOG.log(20,"getJsonFromDevices: ip:{} page:{}".format(ipNumber, page) )
			if not self.isValidIP(ipNumber): return {}

			usePort = str(self.portOfShellyDevices)
			if port !="": usePort = str(port)
			if self.useCurlOrPymethod.find("curl") > -1:
				if len(self.userIDOfShellyDevices) >0:
					UID= " -u "+self.userIDOfShellyDevices+":"+self.passwordOfShellyDevices
				else: UID =""
				cmdR  = self.unfiCurl+UID+" 'http://"+ipNumber+":"+usePort+"/"+page+"'"

				if self.decideMyLog(u"Polling"): self.indiLOG.log(20,"Connection: "+cmdR )
				try:
					ret = subprocess.Popen(cmdR, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
					if testHTTP: return {}
					if noJson: return ret[0]
					try:
						jj = json.loads(ret[0])
					except :
						if ipNumber != self.HTTPlisternerTestIP:
							self.indiLOG.log(30,"Shelly repose from {}  no json object returned: {}".format(ipNumber, ret[0]) )
						return {}

					if  jsonAction=="print":
						self.indiLOG.log(20,u" Connection  info\n{}".format( json.dumps(jj, sort_keys=True, indent=2)) )

					return jj

				except	Exception, e:
					self.indiLOG.log(40,"Connection: in Line {} has error={}   Connection".format(sys.exc_traceback.tb_lineno, e) )
				return {}

			############# does not work on OSX	el capitan ssl lib too old	##########
			elif self.useCurlOrPymethod =="requests":

				if data =={}: dataDict = ""
				else:		  dataDict = json.dumps(data)
				url = "http://"+ipNumber+":"+usePort+"/"+page

				try:
						if len(self.userIDOfShellyDevices) >0:
							resp = requests.get(url,auth=(self.userIDOfShellyDevices, self.passwordOfShellyDevices))
						else:
							resp = requests.get(url)
  						if testHTTP: return {}

						try:
							jj = resp.json()
						except :
							self.indiLOG.log(40,"Shelly repose from {}  no json object returned:".format(ipNumber, resp) )
							return {}
 
						if  jsonAction =="print":
							self.indiLOG.log(20,u" Connection  info\n{}".format(json.dumps(jj, sort_keys=True, indent=2)) )

						return jj

				except	Exception, e:
					self.indiLOG.log(40,"in Line {} has error={}   Connection".format(sys.exc_traceback.tb_lineno, e) )

		except	Exception, e:
			self.indiLOG.log(40,"in Line {} has error={}   Connection".format(sys.exc_traceback.tb_lineno, e))
		return {}



####-------------------------------------------------------------------------####


	def addToStatesUpdateDict(self,devId,key,value,uiValue="",decimalPlaces="", force=False):
		devId=unicode(devId)
		#self.indiLOG.log(20,"addToStatesUpdateDict devId:{}; key:{}, value:{}; uiValue:{}, decPlace:{}".format(devId,key,value,uiValue,decimalPlaces) )
		try:
				if devId not in self.updateStatesDict: 
					self.updateStatesDict[devId] = {}
				if key in self.updateStatesDict[devId]:
					if value == self.updateStatesDict[devId][key]["value"]: return 
				self.updateStatesDict[devId][key] = {"value":value,"decimalPlaces":decimalPlaces,"uiValue":uiValue, "force":force}

			#self.updateStatesDict = local	  
		except Exception, e:
			if	unicode(e).find(u"UnexpectedNullErrorxxxx") >-1: return newStates
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 

####-------------------------------------------------------------------------####
	def executeUpdateStatesDict(self,onlyDevID="0",calledFrom=""):
		try:
			if len(self.updateStatesDict) ==0: return
			#self.indiLOG.log(20, u"executeUpdateStatesList  updateStatesList: {}".format(self.updateStatesDict))
			onlyDevID = unicode(onlyDevID)

			local ={}
			#		 
			if onlyDevID == "0":
				for ii in range(5):
					try: 
						local = copy.deepcopy(self.updateStatesDict)
						break
					except Exception, e:
						self.sleep(0.05)
				self.updateStatesDict={} 

			elif onlyDevID in self.updateStatesDict:
				for ii in range(5):
					try: 
						local = {onlyDevID: copy.deepcopy(self.updateStatesDict[onlyDevID])}
						break
					except Exception, e:
						self.sleep(0.05)

				try: 
					del self.updateStatesDict[onlyDevID]
				except Exception, e:
					pass
			else:
				return 

			self.lastexecuteUpdateStatesDictCalledFrom = (calledFrom,onlyDevID)

			dateString = datetime.datetime.now().strftime(_defaultDateStampFormat)
			for devId in local:
				#self.indiLOG.log(20,"dev:{}   updating {}".format(devId, local))
				if onlyDevID !="0" and onlyDevID != devId: continue
				if devId == "0": continue
				try: devID = int(devId)
				except Exception, e:
					self.indiLOG.log(40,"executeUpdateStatesDict bad devID:{}, local:{}".format(unicode(devId)[0:25], unicode(local[devId])[0:40]) )

					continue
				oneNew = False
				onOffStateNotChanged = True
				if len(local[devId]) > 0:
					changedOnly = []
					dev = indigo.devices[devID]
					props = dev.pluginProps
					for state in local[devId]:
						if state == "onOffState" and dev.states["onOffState"] != local[devId][state]["value"]: onOffStateNotChanged = False
						if not local[devId][state]["force"]: 
							if state not in dev.states:
								self.indiLOG.log(40,"executeUpdateStatesDict dev:{} state:{} not present ".format(dev.name.encode("utf8"),state) )
								continue
							if dev.states[state] == local[devId][state]["value"] : continue
						dd = {u"key":state, "value":local[devId][state]["value"]}
						if local[devId][state]["uiValue"]		!="": dd["uiValue"]			= local[devId][state]["uiValue"]
						if local[devId][state]["decimalPlaces"]	!="": dd["decimalPlaces"]	= local[devId][state]["decimalPlaces"]
						
						changedOnly.append(dd)

						#if dev.id == 422345573: self.indiLOG.log(20,"adding status dev:{}; state:{} dd:{} to sensorValue".format(dev.name.encode("utf8"), state, dd ) )
						if  "displaySelect" in props and props["displaySelect"] == state:
							if "SupportsSensorValue" in props and props["SupportsSensorValue"]:
								#if dev.id == 422345573: self.indiLOG.log(20,"adding status dev:{}; added to sensorValue".format(dev.name.encode("utf8") ) )
								xx = copy.copy(dd)
								xx["key"] = "sensorValue"
								changedOnly.append(xx)
							oneNew = True
					if oneNew and not (props["isRelay"] and onOffStateNotChanged):
						dd = {u"key":"lastStatusChange", "value":dateString}
						changedOnly.append(dd)
					#self.indiLOG.log(20,"adding status dev:{}; state:{}; onOffStateNotChanged:{}, deviceTypeId :{} dd:{}".format(dev.name.encode("utf8"), state, onOffStateNotChanged, props["isRelay"]  , changedOnly) )
					#self.indiLOG.log(20,"dev:{} updating states:{} ".format(devId, changedOnly))
					
					self.execUpdateStatesList(dev,changedOnly)

		except Exception, e:
				if	unicode(e).find(u"UnexpectedNullErrorxxxx") >-1: return 
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		self.executeUpdateStatesDictActive = ""
		return

####-------------------------------------------------------------------------####
	def execUpdateStatesList(self,dev,chList):
		try:

			if len(chList) ==0: return

			if self.indigoVersion >6:
				dev.updateStatesOnServer(chList)

			else:
				for uu in chList:
					dev.updateStateOnServer(uu[u"key"],uu[u"value"])


		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,u"chList: "+ unicode(chList))



	####-----------------	 ---------
	def completePath(self,inPath):
		if len(inPath) == 0: return ""
		if inPath == " ":	 return ""
		if inPath[-1] !="/": inPath +="/"
		return inPath


####-------------------------------------------------------------------------####
	def writeJson(self,data, fName="", fmtOn=False ):
		try:

			if format:
				out = json.dumps(data, sort_keys=True, indent=2)
			else:
				out = json.dumps(data)

			try:
				if fName !="":
					f=open(fName,u"w")
					f.write(out)
					f.close()
				return out
			except: pass

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return ""


########################################
########################################
####----checkPluginPath----
########################################
########################################
	####------ --------
	def checkPluginPath(self, pluginName, pathToPlugin):

		if pathToPlugin.find("/" + self.pluginName + ".indigoPlugin/") == -1:
			self.indiLOG.log(50,u"--------------------------------------------------------------------------------------------------------------")
			self.indiLOG.log(50,u"The pluginName is not correct, please reinstall or rename")
			self.indiLOG.log(50,u"It should be   /Libray/....../Plugins/" + pluginName + ".indigoPlugin")
			p = max(0, pathToPlugin.find("/Contents/Server"))
			self.indiLOG.log(50,u"It is: " + pathToPlugin[:p])
			self.indiLOG.log(50,u"please check your download folder, delete old *.indigoPlugin files or this will happen again during next update")
			self.indiLOG.log(50,u"---------------------------------------------------------------------------------------------------------------")
			self.sleep(100)
			return False
		return True

########################################
########################################
####-----------------  logging ---------
########################################
########################################

	####----------------- ---------
	def setLogfile(self, lgFile):
		self.logFileActive =lgFile
		if   self.logFileActive =="standard":	self.logFile = ""
		elif self.logFileActive =="indigo":		self.logFile = self.indigoPath.split("Plugins/")[0]+"Logs/"+self.pluginId+"/plugin.log"
		else:									self.logFile = self.indigoPreferencesPluginDir +"plugin.log"
		indigo.server.log("myLogSet setting parameters -- logFileActive= {}; logFile= {};  debug plugin:{}".format(self.logFileActive, self.logFile, self.debugLevel)  )



	####-----------------  check logfile sizes ---------
	def checkLogFiles(self):
		return
		try:
			self.lastCheckLogfile = time.time()
			if self.logFileActive =="standard": return 
			
			fn = self.logFile.split(".log")[0]
			if os.path.isfile(fn + ".log"):
				fs = os.path.getsize(fn + ".log")
				if fs > self.maxLogFileSize:  
					if os.path.isfile(fn + "-2.log"):
						os.remove(fn + "-2.log")
					if os.path.isfile(fn + "-1.log"):
						os.rename(fn + ".log", fn + "-2.log")
						os.remove(fn + "-1.log")
					os.rename(fn + ".log", fn + "-1.log")
					indigo.server.log(" reset logfile due to size > %.1f [MB]" %(self.maxLogFileSize/1024./1024.) )
		except	Exception, e:
				self.indiLOG.log(50, u"checkLogFiles Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			
			
	####-----------------	 ---------
	def decideMyLog(self, msgLevel):
		try:
			if msgLevel	 == u"all" or u"all" in self.debugLevel:	 return True
			if msgLevel	 == ""	 and u"all" not in self.debugLevel:	 return False
			if msgLevel in self.debugLevel:							 return True
			return False
		except	Exception, e:
			if len(unicode(e)) > 5:
				indigo.server.log( u"decideMyLog Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return False


	####-----------------	 ---------
	def setSqlLoggerIgnoreStatesAndVariables(self):
		try:
			if self.indigoVersion <  7.4:                             return 
			if self.indigoVersion == 7.4 and self.indigoRelease == 0: return 

			outOND  = ""
			outOffD = ""
			outONV  = ""
			outOffV = ""
			if self.decideMyLog(u"SQLSuppresslog"): self.indiLOG.log(20,"setSqlLoggerIgnoreStatesAndVariables settings:{} ".format( self.SQLLoggingEnable) )
			if not self.SQLLoggingEnable["devices"]: # switch sql logging off
					for dev in indigo.devices.iter(self.pluginId):	
						sp = dev.sharedProps
						if "sqlLoggerIgnoreStates" not in sp or _sqlLoggerIgnoreStates not in sp["sqlLoggerIgnoreStates"]: 
							sp["sqlLoggerIgnoreStates"] = copy.copy(_sqlLoggerIgnoreStates)
							dev.replaceSharedPropsOnServer(sp)
							outOffD += dev.name+"; "

			else:  # switch sql logging (back) on
					for dev in indigo.devices.iter(self.pluginId):	
						### alsways set completely
						sp = dev.sharedProps
						if "sqlLoggerIgnoreStates" in sp and len(sp["sqlLoggerIgnoreStates"]) > 0: 
							outOffD += dev.name+"; "
							sp["sqlLoggerIgnoreStates"] = ""
							dev.replaceSharedPropsOnServer(sp)



			if not self.SQLLoggingEnable["variables"]:

				for v in self.varExcludeSQLList:
					var = indigo.variables[v]
					sp = var.sharedProps
					if "sqlLoggerIgnoreChanges" in sp and sp["sqlLoggerIgnoreChanges"] == "true": 
						continue
					outOffV += var.name+"; "
					sp["sqlLoggerIgnoreChanges"] = "true"
					var.replaceSharedPropsOnServer(sp)

			else:
				for v in self.varExcludeSQLList:
					var = indigo.variables[v]
					sp = var.sharedProps
					if "sqlLoggerIgnoreChanges" not in sp  or sp["sqlLoggerIgnoreChanges"] != "true": 
						continue
					outONV += var.name+"; "
					sp["sqlLoggerIgnoreChanges"] = ""
					var.replaceSharedPropsOnServer(sp)

			if self.decideMyLog(u"SQLSuppresslog"): 
				self.indiLOG.log(20," \n\n")
				if outOffD !="":
					self.indiLOG.log(20," switching off SQL logging for special devtypes/states:\n{}\n for devices:\n>>>{}<<<".format(json.dumps(_sqlLoggerIgnoreStates, sort_keys=True, indent=2), outOffD.encode("utf8")) )

				if outOND !="":
					self.indiLOG.log(20," switching ON SQL logging for special states for devices: {}".format(outOND.encode("utf8")) )

				if outOffV !="":
					self.indiLOG.log(20," switching off SQL logging for variables :{}".format(outOffV.encode("utf8")) )

				if outONV !="":
					self.indiLOG.log(20," switching ON SQL logging for variables :{}".format(outONV.encode("utf8")) )
				self.indiLOG.log(20,"setSqlLoggerIgnoreStatesAndVariables settings end\n")



		except Exception, e:
			self.indiLOG.log(40,u"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 


##################################################################################################################
##################################################################################################################
##################################################################################################################
###################	 Listen section  receive data from SHELLY DEVICES via HTTP comm  #####################

####-------------------------------------------------------------------------####
####-------------------------------------------------------------------------####
	def isValidIP(self, ip0):
		if ip0 is None: return False
		ipx = ip0.split(u".")
		if len(ipx) != 4:
			return False
		else:
			for ip in ipx:
				try:
					if int(ip) < 0 or  int(ip) > 255: 
						return False
				except:
					return False
		return True

####-------------------------------------------------------------------------####
	def isValidMAC(self, MAC):
		if MAC is None:		return False
		if len(MAC) != 12:	return False
		return True

####-------------------------------------------------------------------------####
	def startHTTPListening(self):
		try:
			self.indiLOG.log(20, u"..  starting HTTP listener on port:{} ".format(self.portOfIndigoServer) )

			self.httpThread = threading.Thread(name='daemon_server', target=self.start_HTTP_server, args=(self.portOfIndigoServer,) )
			self.httpThread.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
			self.httpThread.start()


		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

####-------------------------------------------------------------------------####
	def start_HTTP_server(self, port):
		'''Start a simple webserver serving path on port'''
		httpd = HTTPServer(('', port), RequestHandler)
		httpd.serve_forever()

####-------------------------------------------------------------------------####
####-------------------------------------------------------------------------####
####-------------------------------------------------------------------------####
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer


class RequestHandler(BaseHTTPRequestHandler):
	def do_HEAD(self):
		if indigo.activePlugin.decideMyLog(u"HTTPlistener"): indigo.activePlugin.indiLOG.log(20, u"RequestHandler  doHead ip{} , path:{}".format(self.client_address, self.path))
		return
	
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/plain')
		self.wfile.flush()
		try:
			if indigo.activePlugin.decideMyLog(u"HTTPlistener"): indigo.activePlugin.indiLOG.log(20, u"RequestHandler  do_GET ..  ip{} , path:{}".format(self.client_address, self.path))
			indigo.activePlugin.addtoAnalyzePollerQueue( {"ipNumber":self.client_address[0], "page":"httpAction", "data":{"path": self.path}}  )
		except Exception, e:
			indigo.activePlugin.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return


###################	 HTTP listen section  receive data from shelly devices via HTTP comm  end			 #################
##################################################################################################################
##################################################################################################################




##################################################################################################################
####-----------------  valiable formatter for differnt log levels ---------
# call with: 
# formatter = LevelFormatter(fmt='<default log format>', level_fmts={logging.INFO: '<format string for info>'})
# handler.setFormatter(formatter)
class LevelFormatter(logging.Formatter):
	def __init__(self, fmt=None, datefmt=None, level_fmts={}, level_date={}):
		self._level_formatters = {}
		self._level_date_format = {}
		for level, formt in level_fmts.items():
			# Could optionally support level names too
			self._level_formatters[level] = logging.Formatter(fmt=formt, datefmt=level_date[level])
		# self._fmt will be the default format
		super(LevelFormatter, self).__init__(fmt=formt, datefmt=datefmt)

	def format(self, record):
		if record.levelno in self._level_formatters:
			return self._level_formatters[record.levelno].format(record)

		return super(LevelFormatter, self).format(record)




