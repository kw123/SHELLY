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
try:
	import queue as Queue
except:
	import Queue
import cProfile
import pstats
import logging
import urllib
import requests

import traceback


#import pydevd_pycharm
#pydevd_pycharm.settrace('localhost', port=5678, stdoutToServer=True, stderrToServer=True)

try:
	unicode("x")
except:
	unicode = str


try:
	# noinspection PyUnresolvedReferences
	import indigo
except ImportError:
	pass
################################################################################
##########  Static parameters, not changed in pgm
################################################################################

##


######### set new  pluginconfig defaults
# this needs to be updated for each new property added to pluginprops. 
# indigo ignores the defaults of new properties after first load of the plugin 
kDefaultPluginPrefs = {
				"indigoFolderName":			"Shelly",
				"IndigoServerIPNumber":		"192.168.1.x",
				"portOfIndigoServer":		"9780",
				"userIDOfShellyDevices":	"",
				"passwordOfShellyDevices":	"",
				"portOfShellyDevices":		"80",
				"sensorApiVersion":			"2",
				"tempUnits":				"C",
				"tempDigits":				"1",
				"energyDigits":				"1",
				"powerDigits":				"1",
				"voltageDigits":			"1",
				"currentDigits":			"1",
				"unfiCurl":					"/usr/bin/curl",
				"SQLLoggingEnable":			"on-on",
				"logStateChanges":			"no",
				"debugSetupDevices":		False,
				"debugHTTPlistener":		False,
				"debugPolling":				False,
				"debugPing":				False,
				"debugActions":				False,
				"debugSQLSuppresslog":		False,
				"debugSpecial":				False,
				"debugall":					False,
				"logFileActive2":			"standard",
				"do_cProfile":				"on/off/print"
				}



## which child type 
_externalSensorDevTypes			= ["ext_temperature","ext_humidity"]
_childDevTypes					= {	"ext_temperature":{			"state":"Temperature",	"dataKey":"tC",	"nameExt":"_ext_Temp_"},
									"ext_humidity":{			"state":"Humidity",		"dataKey":"hum","nameExt":"_ext_hum_"},
									"shellyht-child":{			"state":"Humidity",		"dataKey":"hum","nameExt":"_hum_"},
									"shellyswitch25-child":{	"state":"",				"dataKey":"",	"nameExt":"_relay-2"},
									"shellyix3-child":{			"state":"",				"dataKey":"",	"nameExt":"_input-2"},
									"shelly4pro-child":{		"state":"",				"dataKey":"",	"nameExt":"_relay-2"},
									"shellyem-child":{			"state":"",				"dataKey":"",	"nameExt":"_EM"}
								}
_relayDevices					= ["shelly1","shelly1l","shelly1pm","shellyswitch25","shellyswitch25-child","shellyem","shelly4pro","shelly4pro-child","shellyplug","shellyplug-s"]

#http//ip:port/settings/?commands=
#eg: http//ip:port/settings/?external_power=1000
			   # key from props									comand to be send							looking for string to come back
_settingCmds ={
			### emeter settings
			 "SENDTOSHELLYDEVICE-emeter_0_ctraf_type":			["settings/meter/0?ctraf_type",				"ctraf_type"],
			 "SENDTOSHELLYDEVICE-emeter_1_ctraf_type":			["settings/meter/1?ctraf_type",				"ctraf_type"],
			 "SENDTOSHELLYDEVICE-emeter_2_ctraf_type":			["settings/meter/2?ctraf_type",				"ctraf_type"],
			 "SENDTOSHELLYDEVICE-emeter_3_ctraf_type":			["settings/meter/3?ctraf_type",				"ctraf_type"],
			 "SENDTOSHELLYDEVICE-emeter_4_ctraf_type":			["settings/meter/4?ctraf_type",				"ctraf_type"],
			 "SENDTOSHELLYDEVICE-emeter_5_ctraf_type":			["settings/meter/5?ctraf_type",				"ctraf_type"],
### roller settings
			 "SENDTOSHELLYDEVICE-roller_mode":					["settings?mode=",							"mode"],
			 "SENDTOSHELLYDEVICE-roller_0_maxtime":				["roller/0?maxtime=",						"maxtime"],
			 "SENDTOSHELLYDEVICE-roller_0_maxtime_open":		["roller/0?maxtime_open=",					"maxtime_open"],
			 "SENDTOSHELLYDEVICE-roller_0_maxtime_close":		["roller/0?maxtime_close=",					"maxtime_close"],
			 "SENDTOSHELLYDEVICE-roller_0_default_state":		["roller/0?default_state=",					"default_state"],
			 "SENDTOSHELLYDEVICE-roller_0_swap":				["roller/0?swap=",							"swap"],
			 "SENDTOSHELLYDEVICE-roller_0_swap_inputs":			["roller/0?swap_inputs=",					"swap_inputs"],
			 "SENDTOSHELLYDEVICE-roller_0_input_mode":			["roller/0?input_modee=",					"input_mode"],
			 "SENDTOSHELLYDEVICE-roller_0_btn_type":			["roller/0?btn_typee=",						"btn_type"],
			 "SENDTOSHELLYDEVICE-roller_0_btn_reverse":			["roller/0?btn_reverse=",					"btn_reverse"],
			 "SENDTOSHELLYDEVICE-roller_0_obstacle_mode":		["roller/0?obstacle_mode=",					"obstacle_mode"],
			 "SENDTOSHELLYDEVICE-roller_0_obstacle_action":		["roller/0?obstacle_action=",				"obstacle_action"],
			 "SENDTOSHELLYDEVICE-roller_0_off_power":			["roller/0?off_power=",						"off_power"],
			 "SENDTOSHELLYDEVICE-roller_0_positioning":			["roller/0?positioning=",					"positioning"],
			 "SENDTOSHELLYDEVICE-roller_0_obstacle_power":		["roller/0?obstacle_powere=",				"obstacle_power"],
			 "SENDTOSHELLYDEVICE-roller_0_obstacle_delay":		["roller/0?obstacle_delay=",				"obstacle_delay"],
			 "SENDTOSHELLYDEVICE-roller_0_safety_mode":			["roller/0?safety_mode=",					"safety_mode"],
			 "SENDTOSHELLYDEVICE-roller_0_safety_action":		["roller/0?safety_action=",					"safety_action"],
			 "SENDTOSHELLYDEVICE-roller_0_safety_allowed_on_trigger": ["roller/0?safety_allowed_on_trigger=","safety_allowed_on_trigger"],
			### relay settings
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
			### light settings
			 "SENDTOSHELLYDEVICE-light_0_swap_inputs":			["settings/light/0?swap_inputs=",			"swap_inputs"],
			 "SENDTOSHELLYDEVICE-light_0_btn_reverse":			["settings/light/0?btn_reverse=",			"btn_reverse"],
			 "SENDTOSHELLYDEVICE-light_0_default_state":		["settings/light/0?default_state=",			"default_state"],
			 "SENDTOSHELLYDEVICE-light_0_name":					["settings/light/0?name=",					"name"],
			 "SENDTOSHELLYDEVICE-light_1_swap_inputs":			["settings/light/1?swap_inputs=",			"swap_inputs"],
			 "SENDTOSHELLYDEVICE-light_1_btn_reverse":			["settings/light/1?btn_reverse=",			"btn_reverse"],
			 "SENDTOSHELLYDEVICE-light_1_default_state":		["settings/light/1?default_state=",			"default_state"],
			 "SENDTOSHELLYDEVICE-light_1_name":					["settings/light/1?name=",					"name"],
			### button device
			 "SENDTOSHELLYDEVICE-input_0_btn_type":				["settings/input/0?btn_type=",				"btn_type"],
			 "SENDTOSHELLYDEVICE-input_0_btn_reverse":			["settings/input/0?btn_reverse=",			"btn_reverse"],
			 "SENDTOSHELLYDEVICE-input_1_btn_type":				["settings/input/1?btn_type=",				"btn_type"],
			 "SENDTOSHELLYDEVICE-input_1_btn_reverse":			["settings/input/1?btn_reverse=",			"btn_reverse"],
			 "SENDTOSHELLYDEVICE-input_2_btn_type":				["settings/input/2?btn_type=",				"btn_type"],
			 "SENDTOSHELLYDEVICE-input_2_btn_reverse":			["settings/input/2?btn_reverse=",			"btn_reverse"],
			 "SENDTOSHELLYDEVICE-longpush_duration_ms_min":		["settings/?longpush_duration_ms_min=",		"longpush_duration_ms"],
			 "SENDTOSHELLYDEVICE-longpush_duration_ms_max":		["settings/?longpush_duration_ms_max=",		"longpush_duration_ms"],
			 "SENDTOSHELLYDEVICE-multipush_time_between_pushes_ms_max": ["settings/?multipush_time_between_pushes_ms_max=", "multipush_time_between_pushes_ms"],
			### misc settings
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
			 "SENDTOSHELLYDEVICE-remain_awake":					["settings?remain_awake=",					"remain_awake"],
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
			 "SENDTOSHELLYDEVICE-pulse_mode":					["settings?pulse_mode=",					"pulse_mode"],
			 "SENDTOSHELLYDEVICE-set_volume":					["settings?set_volume=",					"set_volume"]
	}

_alarmStates= ["none","mild","high","unknown","test"]
## these are the properties of the shelly devices

out_on_url = {"out_on_url":"onOffState=1"}
_emptyProps = {	# switches
				"shellyplug-s":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"", "pollingFrequency":-1, "automaticPollingFrequency":100, "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":   {
										"2":{
												"settings/actions?enabled=true&index=0&name=":	{"btn_on_url":"action=button", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											},
										"1":{
												"settings/relay/0?":							{"btn_on_url":"action=button", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											}
										},
						"childTypes_Sensors":["ext_temperature","ext_humidity"],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"shellyplug":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"", "pollingFrequency":-1, "automaticPollingFrequency":100, "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":   {
										"2":{
												"settings/actions?enabled=true&index=0&name=":	{"btn_on_url":"action=button",  "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											},
										"1":{
												"settings/relay/0?":							{"btn_on_url":"action=button",  "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											}
										},
						"childTypes_Sensors":["ext_temperature","ext_humidity"],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"shelly":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":False, "SupportsStatusRequest":False, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"", "pollingFrequency":-1, "automaticPollingFrequency":100, "expirationSeconds":57600},
						"action_url":   {
										"2":{
												"settings/actions?enabled=true&index=0&name=":	{"shortpush_url":"button=S", "double_shortpush_url":"button=SS", "triple_shortpush_url":"button=SSS", "longpush_url":"button=L"}
											},
										"1":{
												"settings/input/0?":							{"shortpush_url":"button=S", "double_shortpush_url":"button=SS", "triple_shortpush_url":"button=SSS", "longpush_url":"button=L"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[]
						},

				# ok
				"shelly1":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"", "pollingFrequency":-1, "automaticPollingFrequency":100, "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":   {
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"btn_on_url":"input=on", "btn_off_url":"input=off", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0", "longpush_url":"input=long", "shortpush_url":"input=short"}
											},
										"1":{
											"settings/relay/0?":							{"btn_on_url":"input=on", "btn_off_url":"input=off", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0", "longpush_url":"input=long", "shortpush_url":"input=short"}
											}
										},
						"childTypes_Sensors":["ext_temperature","ext_humidity"],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},
		
	
				"shelly1pm":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"childTypes_SplitDevices":["ext_temperature","ext_humidity"],
						"action_url":   {
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"btn_on_url":"input=on", "btn_off_url":"input=off", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0", "longpush_url":"input=long", "shortpush_url":"input=short"}
											},
										"1":{
											"settings/relay/0?":							{"btn_on_url":"input=on", "btn_off_url":"input=off", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0", "longpush_url":"input=long", "shortpush_url":"input=short"}
											}
										},
						"childTypes_Sensors":["ext_temperature","ext_humidity"],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"shelly1l":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"childTypes_SplitDevices":["ext_temperature","ext_humidity"],
						"action_url":   {
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"btn1_on_url":"input_1=on", "btn1_off_url":"input_1=off", "btn1_longpush_url":"input_1=long", "btn1_shortpush_url":"input_1=short",
																							 "btn2_on_url":"input_2=on", "btn2_off_url":"input_2=off", "btn2_longpush_url":"input_2=long", "btn2_shortpush_url":"input_2=short",
																							 "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											},
										"1":{}
										},
						"childTypes_Sensors":["ext_temperature","ext_humidity"],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},
			

				# ok
			 	"shellyswitch25-roller":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180, "mode":"roller"},
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?","roller":"roller/0?"},
																					  ### roller actions  "roller/0?go=" / "roller/0?roller_pos=" / "roller/0?duration=" / "roller/0?offset="
						"action_url":   {
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"roller_open_url":"state=open", "roller_close_url":"state=close", "roller_stop_url":"state=stop"}
											},
										"1":{
												"settings/roller/0?":						{"roller_open_url":"state=open", "roller_close_url":"state=close", "roller_stop_url":"state=stop"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				# ok
			 	"shellyswitch25":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":True,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180, "mode":"relay"},
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?","roller":"roller/0?"},
																					  ### roller actions  "roller/0?go=" / "roller/0?roller_pos=" / "roller/0?duration=" / "roller/0?offset="
						"action_url":   {
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"btn_on_url":"input=on", "btn_off_url":"input=off", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0", "longpush_url":"input=long", "shortpush_url":"input=short",
																						  	"roller_open_url":"state=open", "roller_close_url":"state=close", "roller_stop_url":"state=stop"},
											"settings/actions?enabled=true&index=1&name=":	{"btn_on_url":"input_1=on", "btn_off_url":"input_1=off", "out_on_url":"onOffState_1=1", "out_off_url":"onOffState_1=0", "longpush_url":"input_1=long", "shortpush_url":"input_1=short"}
											},
										"1":{
											"settings/relay/0?":{"btn_on_url":"input=on", "btn_off_url":"input=off", "out_on_url":"onOffState=1", "out_off_url":"onOffState=0", "longpush_url":"input=long", "shortpush_url":"input=short"},
											"settings/relay/1?":{"btn_on_url":"input_1=on", "btn_off_url":"input_1=off", "out_on_url":"onOffState_1=1", "out_off_url":"onOffState_1=0", "longpush_url":"input_1=long", "shortpush_url":"input_1=short"},
											"settings/roller/0?":{"roller_open_url":"state=open", "roller_close_url":"state=close", "roller_stop_url":"state=stop"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":["shellyswitch25-child"],
						"tempUnits":"C"
						},

			 	"shellyswitch25-child":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?","roller":{"0":"roller/0?","1":"roller/1?"}},
						"action_url":   {
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"btn_on_url":"input=on",   "btn_off_url":"input=off",   "out_on_url":"onOffState=1",   "out_off_url":"onOffState=0",   "longpush_url":"input=long",   "shortpush_url":"input=short"},
											"settings/actions?enabled=true&index=1&name=":	{"btn_on_url":"input_1=on", "btn_off_url":"input_1=off", "out_on_url":"onOffState_1=1", "out_off_url":"onOffState_1=0", "longpush_url":"input_1=long", "shortpush_url":"input_1=short"}
											},
										"1":{
											"settings/relay/0?":							{"btn_on_url":"input=on",   "btn_off_url":"input=off",   "out_on_url":"onOffState=1",   "out_off_url":"onOffState=0",   "longpush_url":"input=long",   "shortpush_url":"input=short"},
											"settings/relay/1?":							{"btn_on_url":"input_1=on", "btn_off_url":"input_1=off", "out_on_url":"onOffState_1=1", "out_off_url":"onOffState_1=0", "longpush_url":"input_1=long", "shortpush_url":"input_1=short"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

			 	"shellybutton1":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":False, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, "AllowSensorValueChange":False,  
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":57600, "SupportsBatteryLevel":True, "displaySelect":"event_cnt"},
						"action_url":   {
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"shortpush_url":"input=short", "double_shortpush_url":"input=short_double", "triple_shortpush_url":"input=short_triple", "longpush_url":"input=long"}
											},
										"1":{
											"settings/input/0?":							{"shortpush_url":"input=short", "double_shortpush_url":"input=short_double", "triple_shortpush_url":"input=short_triple", "longpush_url":"input=long"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[]
						},

			 	"shellyix3":{"props":{"isShellyDevice":True, "usesInputForOnOff":True, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"parentIndigoId":0,"children":"{}","isParent":True,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180, "displaySelect":"event_cnt"},
						"action_url":   {
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"btn_on_url":"input=on",   "btn_off_url":"input=off",   "shortpush_url":"input=short",   "double_shortpush_url":"input=short_double",   "triple_shortpush_url":"input=short_triple",   "longpush_url":"input=long",   "shortpush_longpush_url":"input=short_long",   "longpush_shortpush_url":"input=long_short"},
											"settings/actions?enabled=true&index=1&name=": 	{"btn_on_url":"input_1=on", "btn_off_url":"input_1=off", "shortpush_url":"input_1=short", "double_shortpush_url":"input_1=short_double", "triple_shortpush_url":"input_1=short_triple", "longpush_url":"input_1=long", "shortpush_longpush_url":"input_1=short_long", "longpush_shortpush_url":"input_1=long_short"},
											"settings/actions?enabled=true&index=2&name=": 	{"btn_on_url":"input_2=on", "btn_off_url":"input_2=off", "shortpush_url":"input_2=short", "double_shortpush_url":"input_2=short_double", "triple_shortpush_url":"input_2=short_triple", "longpush_url":"input_2=long", "shortpush_longpush_url":"input_2=short_long", "longpush_shortpush_url":"input_2=long_short"}
											},
										"1":{
											"settings/input/0?":							{"btn_on_url":"input=on",   "btn_off_url":"input=off",   "shortpush_url":"input=short",   "double_shortpush_url":"input=short_double",   "triple_shortpush_url":"input=short_triple",   "longpush_url":"input=long",   "shortpush_longpush_url":"input=short_long",   "longpush_shortpush_url":"input=long_short"},
											"settings/input/1?":							{"btn_on_url":"input_1=on", "btn_off_url":"input_1=off", "shortpush_url":"input_1=short", "double_shortpush_url":"input_1=short_double", "triple_shortpush_url":"input_1=short_triple", "longpush_url":"input_1=long", "shortpush_longpush_url":"input_1=short_long", "longpush_shortpush_url":"input_1=long_short"},
											"settings/input/2?":							{"btn_on_url":"input_2=on", "btn_off_url":"input_2=off", "shortpush_url":"input_2=short", "double_shortpush_url":"input_2=short_double", "triple_shortpush_url":"input_2=short_triple", "longpush_url":"input_2=long", "shortpush_longpush_url":"input_2=short_long", "longpush_shortpush_url":"input_2=long_short"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":["shellyix3-child","shellyix3-child"]
						},

			 	"shellyix3-child":{"props":{"isShellyDevice":True, "usesInputForOnOff":True, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180, "displaySelect":"event_cnt"},
						"action_url":   {
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"btn_on_url":"input=on", "btn_off_url":"input=off","shortpush_url":"input=short", "double_shortpush_url":"input=short_double", "triple_shortpush_url":"input=short_triple", "longpush_url":"input=long","shortpush_longpush_url":"input=short_long","longpush_shortpush_url":"input=long_short"},
											"settings/actions?enabled=true&index=1&name=": 	{"btn_on_url":"input_1=on", "btn_off_url":"input_1=off","shortpush_url":"input_1=short", "double_shortpush_url":"input_1=short_double", "triple_shortpush_url":"input_1=short_triple", "longpush_url":"input_1=long","shortpush_longpush_url":"input_1=short_long","longpush_shortpush_url":"input_1=long_short"},
											"settings/actions?enabled=true&index=2&name=": 	{"btn_on_url":"input_2=on", "btn_off_url":"input_2=off","shortpush_url":"input_2=short", "double_shortpush_url":"input_2=short_double", "triple_shortpush_url":"input_2=short_triple", "longpush_url":"input_2=long","shortpush_longpush_url":"input_2=short_long","longpush_shortpush_url":"input_2=long_short"}
											},
										"1":{
											"settings/input/0?":							{"btn_on_url":"input=on", "btn_off_url":"input=off","shortpush_url":"input=short", "double_shortpush_url":"input=short_double", "triple_shortpush_url":"input=short_triple", "longpush_url":"input=long","shortpush_longpush_url":"input=short_long","longpush_shortpush_url":"input=long_short"},
											"settings/input/1?":							{"btn_on_url":"input_1=on", "btn_off_url":"input_1=off","shortpush_url":"input_1=short", "double_shortpush_url":"input_1=short_double", "triple_shortpush_url":"input_1=short_triple", "longpush_url":"input_1=long","shortpush_longpush_url":"input_1=short_long","longpush_shortpush_url":"input_1=long_short"},
											"settings/input/2?":							{"btn_on_url":"input_2=on", "btn_off_url":"input_2=off","shortpush_url":"input_2=short", "double_shortpush_url":"input_2=short_double", "triple_shortpush_url":"input_2=short_triple", "longpush_url":"input_2=long","shortpush_longpush_url":"input_2=short_long","longpush_shortpush_url":"input_2=long_short"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[]
						},


			 	"shelly4pro":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":True,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?","2":"relay/2?","3":"relay/3?"},
						"action_url":   {
										"2":{},
										"1":{}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":["shelly4pro-child","shelly4pro-child","shelly4pro-child"],
						"tempUnits":"C"
						},

			 	"shelly4pro-child":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?","2":"relay/2?","3":"relay/3?"},
						"action_url":	{
										"2":{},
										"1":{}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"shellyem":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":True,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":	{
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{ "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											},
										"1":{
											"settings/relay/0?":							{ "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":["shellyem-child","shellyem-child"],
						"tempUnits":"C"
						},

				"shellyem-child":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180,"displaySelect":"power"},
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":	{
										"2":{},
										"1":{}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"shellyem3":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":True, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":True,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180 },
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":	{
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{ "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											},
										"1":{
											"settings/relay/0?":							{ "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":["shellyem-child","shellyem-child"],
						"tempUnits":"C"
						},

				"shellyem3-child":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":100,  "expirationSeconds":180,"displaySelect":"power"},
						"setPageActionPageOnShellyDev":{"0":"relay/0?","1":"relay/1?"},
						"action_url":	{
										"2":{},
										"1":{}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				# dimmers
				"shellydimmer":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, 
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":6,  "expirationSeconds":180},
						"rgbLimits":[0,255],
						"setPageActionPageOnShellyDev":{"white":"light/0?","white":"light/0?"},
						"action_url":   {
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{
												"btn1_on_url":"input_0=on", "btn1_off_url":"input_0=off", "btn1_longpush_url":"input_0=long", "btn1_shortpush_url":"input_0=short",  
												"btn2_on_url":"input_1=on", "btn2_off_url":"input_1=off", "btn2_longpush_url":"input_1=long", "btn2_shortpush_url":"input_1=short",  
												"out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											},
										"1":{"settings/light/0?":							{
												"btn1_on_url":"input_0=on", "btn1_off_url":"input_0=off", "btn1_longpush_url":"input_0=long", "btn1_shortpush_url":"input_0=short",  
												"btn2_on_url":"input_1=on", "btn2_off_url":"input_1=off", "btn2_longpush_url":"input_1=long", "btn2_shortpush_url":"input_1=short",  
												"out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"shellydimmer2":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, 
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":6,  "expirationSeconds":180},
						"rgbLimits":[0,255],
						"setPageActionPageOnShellyDev":{"white":"light/0?","white":"light/0?"},
						"action_url":   {
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{
												"btn1_on_url":"input_0=on", "btn1_off_url":"input_0=off", "btn1_longpush_url":"input_0=long", "btn1_shortpush_url":"input_0=short",  
												"btn2_on_url":"input_1=on", "btn2_off_url":"input_1=off", "btn2_longpush_url":"input_1=long", "btn2_shortpush_url":"input_1=short",  
												"out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											},
										"1":{"settings/light/0?":							{
												"btn1_on_url":"input_0=on", "btn1_off_url":"input_0=off", "btn1_longpush_url":"input_0=long", "btn1_shortpush_url":"input_0=short",  
												"btn2_on_url":"input_1=on", "btn2_off_url":"input_1=off", "btn2_longpush_url":"input_1=long", "btn2_shortpush_url":"input_1=short",  
												"out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},


				"ShellyBulbDuo":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, 
						"SupportsColor":True, "SupportsRGB":False, "SupportsWhite":True, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":6,  "expirationSeconds":180},
						"WhiteTemperatureMin":2700, "WhiteTemperatureMax":6500,
						"rgbLimits":[0,255],
						"action_url":	{
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{ "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											},
										"1":{
											"settings/light/0?":							{ "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											}
										},
						"childTypes_Sensors":[],
						"setPageActionPageOnShellyDev":{"white":"light/0?","white":"light/0?"},
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"shellybulb":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, 
						"SupportsColor":True, "SupportsRGB":True, "SupportsWhite":True, "SupportsWhiteTemperature":True, "SupportsRGBandWhiteSimultaneously":True, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":6,  "expirationSeconds":180, "isRGBWDevice":True},
						"WhiteTemperatureMin":3000, "WhiteTemperatureMax":6500,
						"rgbLimits":[0,255],
						"action_url":	{
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{ "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											},
										"1":{
											"settings/light/0?":							{ "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											}
										},
						"setPageActionPageOnShellyDev":{"white":"light/0?","color":"light/0?"},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},


				"ShellyVintage":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, 
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":True, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":6,  "expirationSeconds":180},
						"rgbLimits":[0,255],
						"action_url":	{
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"out_on_url":"onOffState=1","out_off_url":"onOffState=0"}
											},
										"1":{
											"settings/light/0?":							{"out_on_url":"onOffState=1","out_off_url":"onOffState=0"}
											}
										},
						"setPageActionPageOnShellyDev":{"white":"light/0?","color":"light/0?"},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"shellyrgbw2":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, 
						"SupportsColor":True, "SupportsRGB":True, "SupportsWhite":True, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":True, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":6,  "expirationSeconds":180, "isRGBWDevice":True},
						"rgbLimits":[0,255],
						"action_url":	{
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{
												"btn_on_url":"input=on", "btn_off_url":"input=off", "btn_longpush_url":"input=long", "btn_shortpush_url":"input=short",  "out_on_url":"onOffState=1", "out_off_url":"onOffState=0"}
											},
										"1":{}
										},
						"setPageActionPageOnShellyDev":{"white":"white/0?","color":"color/0?"},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				# sensors
				"shellydw":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":60,  "expirationSeconds":50400,"displaySelect":"lux","SupportsBatteryLevel":True  },
						"rgbLimits":[0,255],
						"setPageActionPageOnShellyDev":{},
						"action_url":	{
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"close_url":"onOffState=1","open_url":"onOffState=0", "twilight_url":"action=twilightOpen", "dark_url":"action=darkOpen", "close_url":"action=close", "vibration_url":"action=vibration"}
											},
										"1":{
											"settings/?twilight_url":{"none":"action=twilightOpen"},"settings/?dark_url":{"none":"action=darkOpen"},"settings/?close_url":{"none":"action=close"},"settings/?vibration_url":{"none":"action=vibration"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						}, 

				"shellymotionsensor":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":False, "SupportsStatusRequest":True, "AllowOnStateChange":False,  "SupportsBatteryLevel":True,
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":60,  "expirationSeconds":50400,"SupportsBatteryLevel":True },
						"setPageActionPageOnShellyDev":{},
						"action_url":	{
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{ "motion_on":"motion=on",  "motion_off":"motion=off", "tamper_alarm_on":"tamper=on","tamper_alarm_off":"tamper=off", "motion_bright": "bright=on", "motion_twilight":"twilight=on", "motion_dark":"dark=on"}
											},
										"1":{
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						}, 
				# ok


				"shellysmoke":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":60,  "expirationSeconds":50400,"displaySelect":"Temperature","SupportsBatteryLevel":True },
						"setPageActionPageOnShellyDev":{},
						"action_url":	{
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{ "fire_detected_url":"smoke=on", "fire_gone_url":"smoke=off"}
											},
										"1":{
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						}, 
				# ok
				"shellygas":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":50,  "expirationSeconds":180 ,"displaySelect":"Gas_concentration", "useAlarm":"10-600"},
						"setPageActionPageOnShellyDev":{"self_test":"self_test","mute":"mute","unmute":"unmute"},
						"action_url":   {
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"alarm_off_url":"alarm="+_alarmStates[0], "alarm_mild_url":"alarm="+_alarmStates[1], "alarm_heavy_url":"alarm="+_alarmStates[2]}
											},
										"1":{
												"settings/?":								{"alarm_off_url":"alarm="+_alarmStates[0], "alarm_mild_url":"alarm="+_alarmStates[1], "alarm_heavy_url":"alarm="+_alarmStates[2]}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[]
						},

				"shellyflood":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":60,  "expirationSeconds":50400,"displaySelect":"Temperature","SupportsBatteryLevel":True },
						"setPageActionPageOnShellyDev":{},
						"action_url":	{
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"report_url":"data", "flood_detected_url":"flood=1", "flood_gone_url":"flood=0"}
											},
										"1":{
											"settings/?report_url":	{"none":"data"},"settings/?flood_detected_url":{"none":"?flood=1"},"settings/?flood_gone_url":{"none":"?flood=0"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						}, 

				# ok
				"shellyht":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":False, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":True,"isChild":False,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":60,  "expirationSeconds":50400,"displaySelect":"Temperature","SupportsBatteryLevel":True},
						"setPageActionPageOnShellyDev":{},
						"action_url":	{
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"report_url":"data"}
											},
										"1":{
											"settings/?report_url":							{"none":"data"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":["shellyht-child"],
						"tempUnits":"C"
						},

				"shellyht-child":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":False, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":60,  "expirationSeconds":50400,"displaySelect":"Humidity","SupportsBatteryLevel":True},
						"setPageActionPageOnShellyDev":{},
						"action_url":	{
										"2":{
											"settings/actions?enabled=true&index=0&name=":	{"report_url":"data"}
											},
										"1":{
											"settings/?report_url":							{"none":"data"}
											}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"ext_temperature":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":False, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":60,  "expirationSeconds":180,"displaySelect":"Temperature"},
						"action_url":   {
										"2":{},
										"1":{}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						},

				"ext_humidity":{"props":{"isShellyDevice":True, "usesInputForOnOff":False, "isRelay":False, "devNo":0, "SupportsOnState":False, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"parentIndigoId":0,"children":"{}","isParent":False,"isChild":True,"ipNumber":"", "MAC":"","pollingFrequency":-1, "automaticPollingFrequency":60,  "expirationSeconds":180,"displaySelect":"Humidity"},
						"action_url":   {
										"2":{},
										"1":{}
										},
						"childTypes_Sensors":[],
						"childTypes_SplitDevices":[],
						"tempUnits":"C"
						}
			}

_definedShellyDeviceswAction =[]
for kk in _emptyProps:
	if "action_url" in _emptyProps[kk]:
		if "2" in _emptyProps[kk]["action_url"]:
			if _emptyProps[kk]["action_url"]["2"] != {}:
				_definedShellyDeviceswAction.append(kk)

#_definedShellyDeviceswAction	= ["shelly1","shelly1l","shelly1pm","shellyswitch25","shellyswitch25-roller","shellyem","shellydimmer","shellyflood","shellyht", "shellyem3","shellyplug","shellyplug-s","shelly4pro","shellydw","shellydw2","shellygas","shellybutton1","shellyix3"]

_urlPrefix			= {"1":"", "2":"&urls[]"}
_statusActionPage	= {"1":"settings", "2":"settings/actions"}
####  "children":{devtypeOfChild:{n:devidOfchild,n2:devIdofChild2}}"
####     eg      {"ext_temperature":{"1":123456,"3":534212},"ext_humidity":{"1":43256,"3":3214789}"shellyswitch25":{"1":123456}}
####  currently only for ex_temperature and shellyswitch25 the second relay

_sqlLoggerIgnoreStates			= "sensorvalue_ui, updateReason, lastStatusChange, displayStatus, lastMessageFromDevice, lastSuccessfullConfigPush"

_debugAreas 					= ["SetupDevices","HTTPlistener","Polling","Ping","Actions","SQLSuppresslog","Special","all"]

## this is devId --> ipnumber, copied to self.SHELLY[ip#] = copy.deepCopy(_emptyShelly)
_emptyShelly 					= { "ipNumber":"", "MAC":"", "lastCheck":0, "state":"", "reset":False, "lastActive":0, "queue":0, "deviceEnabled":False, "pollingFrequency":10, 
									"defaultTask":"status",  "expirationSeconds":100, "lastMessageFromDevice":0,  "lastMessage-Http":"",  "lastMessage-settings":"", "lastMessage-status":"","lastSuccessfullConfigPush":{"all":-10},
									"isChild":False,"isParent":True,"parentIndigoId":0,"children":{}, "lastAlarm":0, "devTypeId":"", "now":False,"tempUnits":"C","threadNumber":0,"getStatusDelay":True}


_GlobalConst_fillMinMaxStates 	= ["Temperature","Pressure","Humidity","Gas_concentration"]
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

		self.indigo_log_handler.setLevel(logging.INFO)
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
				self.errorLog(u"please check your download folder, delete old *.indigoPlugin files or this will happen again during next update" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"-------  the plugin has stopped, waiting for you to change the name and restart it  ---------------------------" )
				self.errorLog(u"-------  the plugin has stopped, waiting for you to change the name and restart it  ---------------------------" )
				self.errorLog(u"-------  the plugin has stopped, waiting for you to change the name and restart it  ---------------------------" )
				self.errorLog(u"-------  the plugin has stopped, waiting for you to change the name and restart it  ---------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.errorLog(u"---------------------------------------------------------------------------------------------------------------" )
				self.sleep(100000)
				self.quitNOW="wrong plugin name"
				return

			if not self.checkPluginPath(self.pluginName,  self.pathToPlugin):
				exit()


			self.initFileDir()

			self.writeJson(self.pluginVersion, fName=self.indigoPreferencesPluginDir + "currentVersion")

			self.startTime = time.time()

			self.getDebugLevels()

			self.setVariables()

			self.checkcProfile()

			self.indiLOG.log(2,u" --V {}   initializing  -- ".format(self.pluginVersion))

			self.setupBasicFiles()

			self.startupFIXES()

			self.readConfig()

			self.resetMinMaxSensors(init=True)

			self.setSqlLoggerIgnoreStatesAndVariables()

			self.startHTTPListening()

			self.indiLOG.log(10, "..  startup(self): setting variables, debug ..   finished, doing dev init")

		except Exception as e:
			self.indiLOG.log(50,u"--------------------------------------------------------------------------------------------------------------")
			self.indiLOG.log(50,u"Line {} has error={}".format(sys.exc_info()[2].tb_lineno, e))
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

		except Exception as e:
			self.exceptionHandler(40,e)
		return 

	
	####-------------------------------------------------------------------------####
	def startupFIXES(self): # change old names used
		try:
			return 
		except Exception as e:
			self.exceptionHandler(40,e)
		return 




####-------------------------------------------------------------------------####
	def setupBasicFiles(self):
		try:
			return 
		except Exception as e:
			self.exceptionHandler(40,e)
		return 



####-------------------------------------------------------------------------####
	def getDebugLevels(self):
		try:
			self.debugLevel			= []
			for d in _debugAreas:
				if self.pluginPrefs.get(u"debug"+d, False): self.debugLevel.append(d)


		except Exception as e:
			self.indiLOG.log(50,u"--------------------------------------------------------------------------------------------------------------")
			self.indiLOG.log(50,u"Line {} has error={}".format(sys.exc_info()[2].tb_lineno, e) )
			self.indiLOG.log(50,u"Error in startup of plugin, plugin prefs are wrong ")
			self.indiLOG.log(50,u"--------------------------------------------------------------------------------------------------------------")
		return




####-------------------------------------------------------------------------####
	def setVariables(self):
		try:
			self.messagesQueue	  			= Queue.Queue()

			self.deviceActionList			= []			
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

			self.testHTTPsuccess			= 0
			self.HTTPlisternerTestIP		= "127.0.0.1"
			try:
				xx = (self.pluginPrefs.get("SQLLoggingEnable", "on-on")).split("-")
				self.SQLLoggingEnable ={"devices":xx[0]=="on", "variables":xx[1]=="on"}
			except:
				self.SQLLoggingEnable ={"devices":False, "variables":False}

			try:
				self.tempUnits				= self.pluginPrefs.get(u"tempUnits", u"C")[0]
			except:
				self.tempUnits				= u"C"

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

			self.sensorApiVersion			= self.pluginPrefs.get(u"sensorApiVersion","1")

			self.portOfIndigoServer			= int(self.pluginPrefs.get(u"portOfIndigoServer","7980"))
			self.portOfShellyDevices		= int(self.pluginPrefs.get(u"portOfShellyDevices","80"))

			self.userIDOfShellyDevices		= self.pluginPrefs.get(u"userIDOfShellyDevices", u"")
			self.passwordOfShellyDevices	= self.pluginPrefs.get(u"passwordOfShellyDevices", u"")
			self.IndigoServerIPNumber		= self.pluginPrefs.get(u"IndigoServerIPNumber", u"192.168.1.x")

			self.logStateChanges			= self.pluginPrefs.get(u"logStateChanges", u"no")


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
				except Exception as e:
					self.exceptionHandler(40,e)
					self.indigoFolderId =0
			

			self.pythonPath					= u"/usr/bin/python2.7"
			if os.path.isfile(u"/Library/Frameworks/Python.framework/Versions/Current/bin/python3"):
				self.pythonPath				= u"/Library/Frameworks/Python.framework/Versions/Current/bin/python3"
			elif os.path.isfile(u"/usr/bin/python2.7"):
				self.pythonPath				= u"/usr/bin/python2.7"
			elif os.path.isfile(u"/usr/bin/python2.6"):
				self.pythonPath				= u"/usr/bin/python2.6"

		except Exception as e:
			self.indiLOG.log(50,u"--------------------------------------------------------------------------------------------------------------")
			self.indiLOG.log(50,u"Line {} has error={}".format(sys.exc_info()[2].tb_lineno, e))
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
		except Exception as e:
			self.exceptionHandler(40,e)
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

		self.useCurlOrPymethod	= valuesDict[u"useCurlOrPymethod"]

		self.setLogfile(valuesDict[u"logFileActive2"])
	 
		self.logStateChanges	= valuesDict[u"logStateChanges"]

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
		except Exception as e:
			self.indiLOG.log(30,u"Line {} has error={}".format(sys.exc_info()[2].tb_lineno, e))
			self.SQLLoggingEnable = {"devices":True, "variables":True}

		if changeLogging: self.setSqlLoggerIgnoreStatesAndVariables()


		self.tempUnits					= valuesDict[u"tempUnits"]	# C, F, K
		self.tempDigits					= int(valuesDict[u"tempDigits"])  # 0/1/2
		self.energyDigits				= int(valuesDict[u"energyDigits"])  # 0/1/2
		self.powerDigits				= int(valuesDict[u"powerDigits"])  # 0/1/2
		self.voltageDigits				= int(valuesDict[u"voltageDigits"])  # 0/1/2
		self.currentDigits				= int(valuesDict[u"currentDigits"])  # 0/1/2

		self.IndigoServerIPNumber 		= valuesDict[u"IndigoServerIPNumber"]
		self.portOfIndigoServer 		= int(valuesDict[u"portOfIndigoServer"])
		self.userIDOfShellyDevices 		= valuesDict[u"userIDOfShellyDevices"]
		self.passwordOfShellyDevices 	= valuesDict[u"passwordOfShellyDevices"]
		self.sensorApiVersion			= valuesDict[u"sensorApiVersion"]

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
		helpText +='(1) ON THE SHELLY DEVICE  \n'
		helpText +='    Setup shelly device as defned by the shelly manual:  \n'
		helpText +='    Using your phone, connect wifi to shellyxxx AP wifi SSID in phone setup   \n'
		helpText +='    - use browser to connect to 192.168.33.1 (that is a fixed ip#)   \n'
		helpText +='    - setup your home wifi network parameter (SSID, PWD, IP). I prefer using a fixed IP#   \n'
		helpText +='    - Restart.    \n'
		helpText +='   Optional: On regular browser, connect to http://ip# you just set with the phone   \n'
		helpText +='     upgrade device if available, set device parameters as needed, etc  \n'
		helpText +='   \n'
		helpText +='(2) IN THE PLUGIN:  \n'
		helpText +='    To add devices or do a refresh  \n'
		helpText +='    enter IP# / range in menu   \n'
		helpText +='        "Start Shelly device discovery Process for ONE device" or .. "an IP RANGE"  \n'
		helpText +='    It will query the IP# (or range) and check for a propper shelly response    \n'
		helpText +='    When a proper resonse is received, the plugin will add a new Shelly device  \n'
		helpText +='     if does not already exist   \n'
		helpText +='   \n'
		helpText +='(3) OPTIONAL if needed:  \n'
		helpText +='    Edit indigo Shelly device to tune parameters eg:  \n'
		helpText +='    expiration time:  after what time w/o message the device goes to "EXPIRED"  \n'
		helpText +='    polling time: how often should the plugiquerry the device  \n'
		helpText +='    status column: what to show in the status column (only for sensors)  \n'
		helpText +='    set relay and input settings eg default at power on, input button behavior etc  \n'
		helpText +='    IP number: here you can change the IP number of the device  if / when it was changed \n'
		helpText +='   \n'
		helpText +='== How it works:  \n'
		helpText +='   \n'
		helpText +='The plugin is:  \n'
		helpText +='(A) listening to any messages from the devices on a tcp port (set in config, default 7980)  \n'
		helpText +='    the plugin will push action url settings to each shelly device  \n'
		helpText +='    that causes the shelly device to SEND info to the plugin when anything changes  \n'
		helpText +='(B) polling the devices on a regular schedule (1/s .. min., set in dev edit)  \n'
		helpText +='     - http://ip#/settings         gets basic config parameters (dev type, rssi, etc)  \n'
		helpText +='     - http://ip#/status           gets live info eg temp, on/off, RGB, Power ...  \n'
		helpText +='(C) switching shelly devices, on/off set light  using eg:  \n'
		helpText +='     - http://ip#/relay/0?turn=on/off  sets relay 0 on/off  \n'
		helpText +='     - http://ip#/color/0?red=200&green=50&blue=30  sets RGB values  \n'
		helpText +='    etc.  \n'
		helpText +='(D) can set parameters on shelly devices (set in indigo device edit), with:  \n'
		helpText +='     - http://ip#/settings/relay/0?btn_type=toggle     set input button to toggle/momentary/.. \n'
		helpText +='     - http://ip#/settings/light/0?default_state=last  set the power-on state to last/on/off  \n'
		helpText +='     - http://ip#/settings/actions?enabled=true&index=0&name=btn_on_url&urls[]=http://ipofindigo:port/?input=on  to set the action send to indigo \n'
		helpText +='     and many other parameters like night mode ... \n'
		helpText +='(E) Menu option to get and print shelly-EM(3) emeter time series data to logfile  \n'
		helpText +='== REMARKS:   \n'
		helpText +='(A) The plugin will detect IP# changes for relay or temp devices automatically,  \n'
		helpText +='      but not for light bulbs, as they do not send out any updates  \n'
		helpText +='      you can change the IP# of the device in indigo device edit  \n'
		helpText +='(B) You can set a shelly IP# to be ignored, then the plugin will not be updating anything for that device  \n'
		helpText +='(C) There are a few utilities: print device info, push config to the shelly devices, mostly used for debugging  \n'
		helpText +='   \n'
		helpText +='== Currently supported devices:   \n'
		helpText +='  fully tested:   \n'
		helpText +='Shelly-1:                          12V 110-220V one basic relay  \n'
		helpText +='Shelly-1L:                         12V 110-220V one basic relay   w and w/o nutral line \n'
		helpText +='Shelly-1PM:                        12V 110-220Vrelay with internal temp sensor ...  \n'
		helpText +='Shelly-25 2-Relays:                like two Shelly-1PM in one - the plugin creates 2 devices: R1, R2   \n'
		helpText +='                                   the second relay will be added as device: hostName-shellyswitch25-child-1  \n'
		helpText +='          1-ROLLER:                it can also be configured as ONE ROLLER device in device edit  \n'
		helpText +='                                   during discovery it will inherit the current mode (relay/roller)  \n'
		helpText +='                                   but it can also be re-defined to relay-roller-relay in device edit  \n'
		helpText +='Shelly-EM Power 2 Ch. - 1 Relay:   110-220V measures Power, volt, has 1 relay - the plugin creates 3 devices: R + EM1 + EM2   \n'
		helpText +='                                   the EM devices  will be added as device: hostName-shellyem-child-1/2  \n'
		helpText +='Shelly-Duo                         110-220V LED light bulb w color temperature  \n'
		helpText +='Shelly-RGBW Light Bulb:            110-220V LED light bulb with 4 led (RGBW)  \n'
		helpText +='Shelly-RGBW dimmer:                110-220V 4 led dimmer (PWM) for RGBW  \n'
		helpText +='Shelly-Dimmer:                     110-220V dimmer  \n'
		helpText +='Shelly-Temp-Hum:                   battery / usb powered Temp. and Hum. sensor  \n'
		helpText +='Shelly-Flood-Temp:                 Flood alarm and Temperature sensor  \n'
		helpText +='Shelly- ext. oneWire Temp sensor:  External addon for Shelly-1 -1PM for up to 3 oneWire Temp sensors  \n'
		helpText +='                                   the sensors will be added as devices: hostName-ext_temperature-# (1,2,3)  \n'
		helpText +='Shelly- ext. DHT22  sensor:        External addon for Shelly-1 -1PM for 1 DHT22 T&H sensor  \n'
		helpText +='                                   the sensor will be added as devices: hostName-ext_temperature-1 and  hostName-ext_humidity-1  \n'
		helpText +='Shelly Door Window                 Door/window open(when dark or light) / close alarm. Lux and vibration measuremnt  \n'
		helpText +='Shelly Plug                        power outlets w relay and power measurement   \n'
		helpText +='Shelly PlugS                       power outlets w relay and power and energy measurement  \n'
		helpText +='Shelly-Vintage Bulb:               110-220V LED light bulb vintage style  \n'
		helpText +='Shelly-GAS-1:                      Gas sensor, values  "none","medium","high","unknown","test", can set speaker level 1-11,  \n' 
		helpText +='                                   start self test, mute, unmute  \n'
		helpText +='i3:                                3 input switches w short, long, double, tripple short/long/long/short push \n'
		helpText +='Button1                            1 input switch/button w rechargeable battery w short, long, double, tripple push  \n'
		helpText +='Shelly-smoke:                      battery,  smoke sensor on/off / temperature sensor   \n'
		helpText +='Shelly-motion:                     shelly motion / light/ vibration/ tamper sensor    \n'
		helpText +='  programmed, but not tested:   \n'
		helpText +='Shelly-EM3 Power 3 Ch. - 1 Relay:  110-220V measures Power, volt, has 1 relay - the plugin creates 4 devices: R + EM1 + EM2 + EM3  \n'
		helpText +='                                   the 3 EM  will be added as device: hostName-sheleeyEM3-child-1/2  \n'
		helpText +='Shelly-PRO4, 4 relay:              220V measures Power, volt, the plugin creates 4 relay devices  \n'
		helpText +='                                   the 2-4 relays will be added as device: hostName-shellypro-child-# (1/2/3)  \n'
		helpText +='=========================================================================================   \n'
		helpText +='   \n'
		indigo.server.log(helpText.encode('utf8'))
		self.indiLOG.log(10,helpText.encode('utf8'))



####-------------------------------------------------------------------------####
	def filterEmeterDevices(self, filter="", valuesDict=None, typeId=""):
		xList=[]
		for devId in self.SHELLY:
			if devId == 0: continue
			if not self.SHELLY[devId]["deviceEnabled"]: continue
			dev =  indigo.devices[devId]
			if dev.deviceTypeId.find("em-") ==-1: continue
			
			##self.indiLOG.log(10,u"forcing push menu {};  {}".format(devId, self.SHELLY[devId]["ipNumber"]) )
			name= indigo.devices[devId].name
			xList.append([str(devId), name])
		xList.sort(key = lambda x: x[1]) 
		return xList


####-------------------------------------------------------------------------####
	def filterActiveShellyDevices(self, filter="", valuesDict=None, typeId=""):
		xList=[]
		for devId in self.SHELLY:
			if devId != 0:
				if self.SHELLY[devId]["deviceEnabled"]:
					##self.indiLOG.log(10,u"forcing push menu {};  {}".format(devId, self.SHELLY[devId]["ipNumber"]) )
					name= indigo.devices[devId].name
					xList.append([str(devId), name])
		xList.sort(key = lambda x: x[1]) 
		if filter =="": xList.append(["0","all devices"])
		return xList


####-------------------------------------------------------------------------####
	def filterActiveShellyDevicesNotChild(self, filter="", valuesDict=None, typeId=""):
		xList=[]
		for devId in self.SHELLY:
			if devId != 0:
				if not self.SHELLY[devId]["deviceEnabled"]: continue
				if     self.SHELLY[devId]["isChild"]: 		continue
				dev = indigo.devices[devId]
				props = dev.pluginProps
				if  props["isChild"]: continue 
				if filter != "" and filter != dev.deviceTypeId: continue
				name= dev.name
				xList.append([str(devId), name])
		xList.sort(key = lambda x: x[1]) 
		if filter =="": xList.append(["0","all devices"])
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
			self.indiLOG.log(10,u"added IP#:{} back to accepted IP numbers,  currently ignored:{}".format(ipN, self.ignoredIPNumbers) )
			self.pluginPrefs["ignoredIPNumbers"] = (",".join(self.ignoredIPNumbers)).strip(",")
		return valuesDict

####-------------------------------------------------------------------------####
	def buttonConfirmconfirmpIgnoreIPNumberCALLBACK(self, valuesDict, typeId=""):
		ipN = valuesDict["ipNumber"].strip()
		if ipN not in self.ignoredIPNumbers:
			self.ignoredIPNumbers.append(ipN)
			self.indiLOG.log(10,u"added IP#:{} to ignored IP numbers, currently ignored:{}".format(ipN, self.ignoredIPNumbers) )
			self.pluginPrefs["ignoredIPNumbers"] = (",".join(self.ignoredIPNumbers)).strip(",")
		return valuesDict


####-------------------------------------------------------------------------####
	def buttonConfirmconfirmIpNumberSetupCALLBACK(self, valuesDict, typeId):
		ip = valuesDict["ipNumber"].strip()
		if self.isValidIP(ip):
			self.ipNumberRangeToTest = [ip, ip] 
			self.indiLOG.log(10,u"added IP#:{} to shelly discovery process".format(ip) )
			valuesDict["MSG"] = u"added IP#:{} to shelly discovery process".format(ip)
		else:
			self.indiLOG.log(10,u"bad IP:{} for shelly discovery process".format(ip) )
			valuesDict["MSG"] = u"bad IP:{} for shelly discovery process".format(ip) 
		return valuesDict




####-------------------------------------------------------------------------####
	def buttonConfirmconfirmIpNumberRangeSetupCALLBACK(self, valuesDict, typeId=""):
		ipFrom = valuesDict["ipNumberFrom"].strip()
		ipTo   = valuesDict["ipNumberTo"].strip()
		if self.isValidIP(ipFrom) and self.isValidIP(ipTo):
			self.ipNumberRangeToTest = [ipFrom, ipTo] 
			self.indiLOG.log(10,u"added IP#s:{} -- {}  to shelly discovery process".format(ipFrom, ipTo) )
		else:
			self.indiLOG.log(10,u"bad IP:{} - {} ".format(ipFrom, ipTo) )
		return valuesDict


####-------------------------------------------------------------------------####
	def buttonConfirmconfirmpPuschActionCALLBACK(self, valuesDict, typeId=""):
		devIdSelect = int(valuesDict["devId"])
		for devId in self.SHELLY:
			if devId == 0: continue
			if devId == devIdSelect or devIdSelect ==0:
				if self.SHELLY[devId]["pushIdActive"] in ["enabled","waiting"]:
					if devId not in indigo.devices: continue
					try:	dev = indigo.devices[devId]
					except:	continue
					if dev.enabled:
						self.SHELLY[devId]["lastSuccessfullConfigPush"] = {"all":-10}
						self.SHELLY[devId]["lastRequestedPush"] = time.time()
						self.pushRequest  = time.time()
						self.checkTimeIfPushToDevicesIsRequired = -1
						self.indiLOG.log(10,u"forcing push of config to {}; pushIdActive:{}".format(dev.name,  self.SHELLY[devId]["pushIdActive"]) )
		valuesDict["MSG"] = "forcing push of config to {}".format(devIdSelect)
		return valuesDict
####-------------------------------------------------------------------------####
	def buttonConfirmconfirmpPuschActionCancelCALLBACK(self, valuesDict, typeId=""):
		devIdSelect = 0
		for devId in self.SHELLY:
			if devId == 0: continue
			if devId == devIdSelect or devIdSelect ==0:
				self.SHELLY[devId]["lastSuccessfullConfigPush"] = time.time()
				self.SHELLY[devId]["lastRequestedPush"] = 0
				self.SHELLY[devId]["pushIdActive"] = "stop"
				self.pushRequest  = -1
				self.checkTimeIfPushToDevicesIsRequired = time.time() + 1000
				try:	devName = indigo.devices[devId].name
				except:	devName = devId
			self.indiLOG.log(10,u"stopping all pushes of config to {}".format(devName) )
		valuesDict["MSG"] = "forcing push of config to all"
		return valuesDict



####-------------------------------------------------------------------------####
	def buttonConfirmconfirmpgetEmeterCvsFileCALLBACK(self, valuesDict, typeId=""):
		devIdSelect = int(valuesDict["devId"])
		if  devIdSelect not in self.SHELLY: 
			self.indiLOG.log(10,u"bad selection for EM cvs data {}".format(devIdSelect) )
			return valuesDict
		dev = indigo.devices[int(devIdSelect)]
		props = dev.pluginProps
		if not props["isChild"]: return 
		page =  "emeter/"+str(int(dev.states["childNo"])-1)+"/em_data.csv"
		self.indiLOG.log(10,u"getting EM csv data for {}; with: {}".format(dev.name, page) )
		cvsData = self.getJsonFromDevices(dev.address, page, noJson=True)
		if len(cvsData) > 10:
			valuesDict["MSG"] = "check  ...shellyDirect/plugin.log file "
		else:
			valuesDict["MSG"] = "no data returned"
		self.indiLOG.log(10,u"csv data from:{}:\n{}".format(dev.name, cvsData) )
		return valuesDict


####-------------------------------------------------------------------------####
	def buttonConfirmconfirmpRequestStatusCALLBACK(self, valuesDict, typeId=""):
		try:
			devIdSelect = int(valuesDict["devId"])
			for devId in self.SHELLY:
				if devId == 0: continue
				if devId == devIdSelect or devIdSelect ==0:
					dev = indigo.devices[devId]
					self.indiLOG.log(10,u"sending status request to device:{}".format(dev.name) )
					self.sendStatusRequest(dev)
		except Exception as e:
			self.exceptionHandler(40,e)
		return 

		return valuesDict

####-------------------------------------------------------------------------####
	def buttonPrintShellyDevInfoCALLBACK(self, valuesDict, typeId=""):

		devIdSelect = int(valuesDict["devId"])
		out = u""
		for devId in self.SHELLY:
			if devId == 0: continue
			if devId == devIdSelect or devIdSelect ==0:
				props ={}
				try: 
					dev = indigo.devices[devId]
					name = dev.name
					deviceTypeId = dev.deviceTypeId
					props = dev.pluginProps
				except:
					name = u"dev does not exist"
					deviceTypeId = "---"
				out += u"\n:::::::: dev:{:33s} ID:{:14}  type: {:10s}   ::::::::::\n".format(name, devId, deviceTypeId)
				keys = sorted(self.SHELLY[devId])
				for item in keys:
					out+= u"{:33s}:  {}\n".format(item, unicode(self.SHELLY[devId][item]))
				out += u"states --------------------\n"
				dev = indigo.devices[devId]
				indigo.server.log(u"keys:"+ unicode(keys))
				keys = sorted(dev.states)
				for item in keys:
					out+= u"{:33s}:  {}\n".format(item, unicode(dev.states[item]))
				keys = sorted(dev.states)
				propList =[]
				out += u"props --------------------\n "
				for prop in props:
					for xx in ["SENDTOSHELLYDEVICE-","children", "isParent", "isChild","displaySelect" ]:
						if prop.find(xx) > -1:
							propList.append([prop,props[prop]])
				for item in propList:
					if item[0].find("SENDTOSHELLYDEVICE-") > -1:
							if item[0] not in _settingCmds: continue
							settings = _settingCmds[item[0]][0]+item[1]
							out+= u"{:33s}:  {}\n".format("set parameters",settings) 
					else:
							out+= u"{:33s}:  {}\n".format(item[0],item[1]) 


				if u"action_url" in _emptyProps[dev.deviceTypeId]:
					for item in _emptyProps[dev.deviceTypeId]["action_url"][self.sensorApiVersion]:
						action = unicode(_emptyProps[dev.deviceTypeId]["action_url"][self.sensorApiVersion][item]).replace("': '",":").replace("', '","   ").replace("{","").replace("}","").replace("'","")
						out += u"{:33s}:  {}\n".format(item, action) 
		ignoredIPNumbers = self.pluginPrefs.get(u"ignoredIPNumbers", "")
		if ignoredIPNumbers != "":
			out += u"\n---------------------------------------\n"
			out += u"{:33s}:  {}\n".format("ignored IP Numbers", ignoredIPNumbers) 


		if out !="":
			self.indiLOG.log(10, out )
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
			if self.decideMyLog(u"SetupDevices"): 
				self.indiLOG.log(10,u"deviceStartComm called for {}; dev={}".format(dev.id, dev.name) )

			if False and dev.id == self.doNotrestartDev: return 
			dev.stateListOrDisplayStateIdChanged()

			if "brightness" in dev.states: 
				dev.onBrightensToLast = True
				dev.replaceOnServer()
				dev = indigo.devices[dev.id]
			props = dev.pluginProps
			update = False
			if dev.deviceTypeId not in _emptyProps:
				self.indiLOG.log(40,u"dev: {}  has wrong deviceTypeId: {}; please delete device and restart plugin".format(dev.name, dev.deviceTypeId))
			else:	
				for pp in _emptyProps[dev.deviceTypeId]["props"]:
					if pp not in props:
						props[pp] = copy.copy(_emptyProps[dev.deviceTypeId]["props"][pp])
						update = True
				if update: 
					dev.replacePluginPropsOnServer(props)
					dev = indigo.devices[dev.id]

				self.renewShelly(dev)
				if self.decideMyLog(u"SetupDevices"): 
					self.indiLOG.log(10,u"deviceStartComm finished for {}; dev={}".format(dev.id, dev.name) )
					self.indiLOG.log(10,u"deviceStartComm .... props:{}".format(props) )
					states = unicode(dev.states)
					self.indiLOG.log(10,u"deviceStartComm  ... states:{}".format(states) )
		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"for dev: {}".format(dev.name))
		self.doNotrestartDev = ""
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
				if "all" not in self.SHELLY[devId]["lastSuccessfullConfigPush"]:
					self.SHELLY[dev.id]["lastSuccessfullConfigPush"] = {"all":-10}
				if self.SHELLY[dev.id]["lastSuccessfullConfigPush"] != {"all":-10}:
					self.SHELLY[dev.id]["lastSuccessfullConfigPush"] = {"all": time.mktime(datetime.datetime.strptime( dev.states["lastSuccessfullConfigPush"], _defaultDateStampFormat).timetuple() )}
			except: self.SHELLY[dev.id]["lastSuccessfullConfigPush"] = {"all":-10}
			if "lastRequestedPush" not in self.SHELLY[dev.id]:		self.SHELLY[dev.id]["lastRequestedPush"] = 0

			self.SHELLY[dev.id]["devTypeId"] 					 	 = dev.deviceTypeId
			self.SHELLY[dev.id]["deviceEnabled"] 					 = True
			if not props["isChild"]:
				self.SHELLY[dev.id]["queue"] 						 = Queue.Queue()

			if updateProps: dev.replacePluginPropsOnServer(props)

			if not self.SHELLY[dev.id]["isChild"]: self.startShellyDevicePoller("start", shellySelect=dev.id)
			#self.indiLOG.log(10,u"shelly at startdev  {} ".format(self.SHELLY))

			if "pushIdActive" not in self.SHELLY[dev.id]:
				if dev.enabled: self.SHELLY[dev.id]["pushIdActive"] = "enabled"
			if not dev.enabled: self.SHELLY[dev.id]["pushIdActive"] = "empty"
			

		except Exception as e:
			self.exceptionHandler(40,e)

		return




####-------------------------------------------------------------------------####
	def deviceDeleted(self, dev):  ### indigo calls this 

		props = dev.pluginProps
		delChild  =[]
		if dev.id in self.SHELLY:
			self.SHELLY[dev.id]["state"] = "stop"
			self.SHELLY[dev.id]["pushIdActive"] = "empty"
			self.sleep(2)
			if 	self.SHELLY[dev.id]["children"] != {}:
				children = self.SHELLY[dev.id]["children"]
				#self.indiLOG.log(10,u"devId:{}, children:{}".format(dev.id, children ))
				for devtype in children:
					#self.indiLOG.log(10,u"devId:{}, devtype:{}".format(dev.id, devtype ))
					for devNo in children[devtype]:
						#self.indiLOG.log(40,u"devId:{}, devNo:{}, devId:{}".format(dev.id, devNo, children[devtype][devNo] ))
						if type(children[devtype][devNo]) == type(1):
							delChild.append(children[devtype][devNo])  # that is the indigo devId of the child
	
		## this must be a child device, delete children entry at parent
			if  self.SHELLY[dev.id]["isChild"]:
				try:
					if self.SHELLY[dev.id]["parentIndigoId"] in indigo.devices: # if not already gone
						parentDev = indigo.devices[self.SHELLY[dev.id]["parentIndigoId"]]
						parentProps = parentDev.pluginProps
						children = self.SHELLY[parentDev.id]["children"]
						#self.indiLOG.log(10,u"devId:{}, children:{}".format(dev.id, children ))
						delDevType =[]
						for devtype in children:
							#self.indiLOG.log(10,u"devId:{}, devtype:{}".format(dev.id, devtype ))
							delDevNo =[]
							for devNo in children[devtype]:
								#self.indiLOG.log(40,u"devId:{}, devNo:{}, devId:{}".format(dev.id, devNo, children[devtype][devNo] ))
								if children[devtype][devNo] == dev.id: delDevNo.append(devNo)
							#self.indiLOG.log(40,u"devId:{}, delDevNo:{}".format(dev.id, delDevNo ))
							for devNo in delDevNo:
								del children[devtype][devNo]
							if children[devtype] =={}: delDevType.append(devtype)
							#self.indiLOG.log(40,u"devId:{}, delChild:{}".format(dev.id, delDevType ))
						for devtype in delDevType:
							del children[devtype]
				
						self.SHELLY[parentDev.id]["children"] = children
						parentProps["children"] = json.dumps(children)
						parentDev.replacePluginPropsOnServer(parentProps)
				except Exception as e:
					self.indiLOG.log(10,u"while deleting children devices is OK, was already deleted... Line {} has error={}".format(sys.exc_info()[2].tb_lineno, e))


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
			if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10,u"deviceStopComm called for dev={}".format(dev.name) )
		except: pass
		try:	self.SHELLY[dev.id]["deviceEnabled"] = False
		except: pass
		try:	self.SHELLY[dev.id]["pushIdActive"] = "empty"
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
			if devId not in self.SHELLY:
				self.indiLOG.log(30,u"the shelly device is new, recommended to use menu / scan to create new shelly devices !!")
				theDictList[0]["MSG"] = "use menu/scan to create new shelly devices"
			try: ##Only if it exists already
				if "isParent" in pluginProps:
					if "sensorNo" in pluginProps and "sensorNo" in dev.states:
							sensorNo = dev.states["sensorNo"]
							try: 	theDictList[0]["sensorNo"] = str(int(sensorNo)-1)
							except: theDictList[0]["sensorNo"] = "0"
				if devId in self.SHELLY:
						theDictList[0]["MAC"] = self.SHELLY[int(devId)]["MAC"]
						theDictList[0]["ipNumber"]  = self.SHELLY[int(devId)]["ipNumber"]

					
			except Exception as e:
				self.exceptionHandler(40,e)
			#self.indiLOG.log(10,u"theDictList {}".format(unicode(theDictList[0])))
			return theDictList

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"theDictList {}".format(theDictList[0]))
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
			#self.indiLOG.log(10,u"valuesDict {}".format(valuesDict))
			MAC = valuesDict["MAC"]
			ipNumber = valuesDict["ipNumber"]

			if not self.isValidIP(ipNumber):
				valuesDict[u"MSG"] = "ERROR: bad IP Number"
				errorDict[u"MSG"] = "bad IP Number"
				return ( False, valuesDict, errorDict )

			if not len(MAC):
				valuesDict[u"MSG"] = "ERROR: bad MAC Number"
				errorDict[u"MSG"] = "bad MAC Number"
				return ( False, valuesDict, errorDict )



			if devId not in self.SHELLY:
				for prop in _emptyProps[typeId]["props"]:
					if prop not in valuesDict:
						valuesDict[prop] = _emptyProps[typeId]["props"][prop]
				valuesDict["devNo"] = "0"
				valuesDict["address"] = ipNumber
				self.initShelly(dev, MAC, ipNumber, deviceTypeId=typeId)
				self.deviceActionList.append({"devId":int(devId), "action":"states", "states":{"MAC":MAC,"created":datetime.datetime.now().strftime(_defaultDateStampFormat)} ,"notBefore":time.time() + 1})
				#valuesDict[u"MSG"] = "ERROR: use menu/scan to create new shelly devices"
				#errorDict[u"MSG"] = "use menu/scan to create new shelly devices"
				return ( True, valuesDict, errorDict )


			if MAC != self.SHELLY[devId]["MAC"]:
				self.indiLOG.log(20,u" replacing mac#:{} with:{}".format(self.SHELLY[devId]["MAC"], MAC))
				dev = indigo.devices[devId]
				dev.updateStateOnServer("MAC",MAC)
				self.SHELLY[devId]["MAC"] = MAC


			if "isParent" in props:
				if valuesDict["ipNumber"] != self.SHELLY[dev.id]["ipNumber"]: self.SHELLY[dev.id]["ipNumber"] = ipNumber
				if dev.address != self.SHELLY[dev.id]["ipNumber"]: valuesDict["address"] = ipNumber


			for pp in["ipNumber", "pollingFrequency", "expirationSeconds"]:
				try: 
					self.SHELLY[devId][pp] = copy.copy(valuesDict[pp])
				except Exception as e:
					self.exceptionHandler(40,e)
					self.indiLOG.log(40,u"deviceTypeId:  {}, pp::{}::".format(dev.deviceTypeId,pp))
					self.indiLOG.log(40,u"replacing w default, valuesDict is: {}".format(valuesDict))
					self.indiLOG.log(40,u"_emptyProps: {}".format(_emptyProps[dev.deviceTypeId]))
					self.SHELLY[devId][pp] 	= copy.copy(_emptyProps[dev.deviceTypeId]["props"][pp])
					valuesDict[pp] 			= copy.copy(_emptyProps[dev.deviceTypeId]["props"][pp])

			#copy changes from child to parent props button settings, as only the parent will push 
			if dev.deviceTypeId.find("shellyswitch25") == 0 and dev.deviceTypeId.find("child") ==-1:
				self.SHELLY[devId]["mode"] 	 = valuesDict["SENDTOSHELLYDEVICE-mode"]
				valuesDict["mode"]			 = valuesDict["SENDTOSHELLYDEVICE-mode"]
				if   dev.deviceTypeId == "shellyswitch25" and 		 valuesDict["SENDTOSHELLYDEVICE-mode"] == "roller":
					valuesDict["isRelay"]  = False
					valuesDict["isParent"] = False
					self.indiLOG.log(20,u"{} changing devtype to roller".format(dev.name))
					self.deviceActionList.append({"devId":dev.id,"action":"changeDeviceTypeId","value":"shellyswitch25-roller"})
					return ( True, valuesDict )
				elif dev.deviceTypeId == "shellyswitch25-roller" and valuesDict["SENDTOSHELLYDEVICE-mode"] == "relay":
					valuesDict["isParent"] = True
					valuesDict["isRelay"]  = True
					self.indiLOG.log(20,u"{} changing devtype to relay".format(dev.name))
					self.deviceActionList.append({"devId":dev.id,"action":"changeDeviceTypeId","value":"shellyswitch25"})
					return ( True, valuesDict )

			if "isRGBWDevice" in valuesDict and valuesDict["isRGBWDevice"] and "rgbSetup" in valuesDict:
				if valuesDict["rgbSetup"] == "RGBW":
					valuesDict["SupportsColor"] = True
					valuesDict["SupportsRGB"] = True
					valuesDict["SupportsWhite"] = True
					valuesDict["SupportsRGBandWhiteSimultaneously"] = True
					valuesDict["SupportsWhiteTemperature"] = False

				elif valuesDict["rgbSetup"] == "RGB":
					valuesDict["SupportsColor"] = True
					valuesDict["SupportsRGB"] = True
					valuesDict["SupportsWhite"] = False
					valuesDict["SupportsRGBandWhiteSimultaneously"] = False
					valuesDict["SupportsWhiteTemperature"] = False

				elif valuesDict["rgbSetup"] == "WT":
					valuesDict["SupportsColor"] = True
					valuesDict["SupportsRGB"] = False
					valuesDict["SupportsWhite"] = True
					valuesDict["SupportsRGBandWhiteSimultaneously"] = False
					valuesDict["SupportsWhiteTemperature"] = True
				self.addToStatesUpdateDict(dev.id,"rgbwSetup", valuesDict["rgbSetup"])

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
					self.SHELLY[parentDev.id]["lastSuccessfullConfigPush"] = {"all": -10}
					self.SHELLY[devId]["lastRequestedPush"] = time.time()
	

			if newParameters:
				self.indiLOG.log(10,u"start pushing config parameters to: {}".format(dev.name))
				self.SHELLY[devId]["lastSuccessfullConfigPush"] = {"all": -10}
				self.pushRequest = time.time()


				
		except Exception as e:
			self.exceptionHandler(40,e)
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
		self.checkTimeIfPushToDevicesIsRequired = time.time() + 200

		if self.currentVersion != self.pluginVersion:
			# will put future updates here
			pass

		self.lastUpdateSend = time.time()  
		self.pluginState	= "run"

		self.initShelly(0,  "0", "0")


		self.indiLOG.log(10,u"..  setting up internal dev tables")
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
		except Exception as e:
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

		self.testHTTPlistener()

		if self.logFileActive !="standard":
			indigo.server.log(u"..  initialized")
			self.indiLOG.log(10, u"..  initialized, starting loop" )
		else:	 
			indigo.server.log(u"..  initialized, starting loop ")


		########   ------- here the loop starts	   --------------
		try:
			while self.quitNow == "":
				self.countLoop += 1
				self.sleep(3)

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
			self.checkForDeviceAction()

			if self.pushRequest >0 and time.time() - self.pushRequest > 0:
				self.checkIfPushToDevicesIsRequired(now, pushNow=True)

			if self.lastMinuteChecked == now.minute: return 
			self.lastMinuteChecked = now.minute

			self.checkForExpiredDevices(now)

			self.checkIfHTTPListernProcessRunsOk()

			if self.lasthourChecked == now.hour: return 
			self.lasthourChecked = now.hour
			self.checkIfPushToDevicesIsRequired(now)

			self.testHTTPlistener()

			self.resetMinMaxSensors()



		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"devId {} ".format(devId))

		return anyChange


###-------------------------------------------------------------------------####
	def checkForDeviceAction(self):
		try:
			if self.deviceActionList == []: return 
			copydeviceActionList = copy.copy(self.deviceActionList)
			delAction =[]
			ii = 0
			for action in copydeviceActionList:
				if "devId" in action:
					dev = indigo.devices[action["devId"]]
					if action["action"] == "changeDeviceTypeId":
						dev = indigo.device.changeDeviceTypeId(dev, action["value"])

						if action["value"] == "shellyswitch25":
							#recreate child device if not present
							props = dev.pluginProps
							props["isParent"] = True
							dev.replacePluginPropsOnServer(props)
							dev = indigo.devices[dev.id]
							if len(self.SHELLY[dev.id]["children"]) == 0:
								self.createShellyChildDevice( dev, "shellyswitch25", self.SHELLY[dev.id]["MAC"], self.SHELLY[dev.id]["ipNumber"], dev.name)
							dev.description ="Host of ..."
							dev.replaceOnServer()

						elif action["value"] == "shellyswitch25-roller":
							dev.description = "On=close=100%"
							dev.replaceOnServer()
							children = self.SHELLY[dev.id]["children"]
							devs, devNos = self.getChildDevices(children)
							for dd in devs:
								indigo.device.delete(dd.id)	
								del self.SHELLY[dd.id]
							dev = indigo.devices[dev.id]
							props = dev.pluginProps
							self.SHELLY[dev.id]["children"] = {}
							self.SHELLY[dev.id]["isParent"] = False
							props["children"] = {}
							props["isParent"] = False
							dev.replacePluginPropsOnServer(props)
						self.indiLOG.log(20,u"{} changed devtype to {}, need to edit device again and save".format(dev.name, action["value"]))
						delAction.insert(0,ii)

					if action["action"] == "checkStatus" and time.time() - action["notBefore"] < 0:
						self.addToShellyPollerQueue( action["devId"], "status", now=True)
						self.indiLOG.log(10,u"{} checking status after roller open/close action".format(dev.name))
						delAction.insert(0,ii)

					if action["action"] == "states" and time.time() - action["notBefore"] < 0:
						for state in action["states"]:
							dev.updateStateOnServer(state, action["states"][state])
						self.indiLOG.log(10,u"{} adding missing states ".format(dev.name))
						delAction.insert(0,ii)
				ii += 1

			#remove action from the end
			for jj in range(len(delAction)):
				del self.deviceActionList[delAction[jj]]

			return 
		except Exception as e:
			self.exceptionHandler(40,e)
			self.deviceActionList = []
		return 

###-------------------------------------------------------------------------####
	def checkIfHTTPListernProcessRunsOk(self):
		try:
			if self.testHTTPsuccess != 0:
				if time.time() - self.testHTTPsuccess  > 100:
					self.indiLOG.log(40,u"HTTPlisten test failed not working, please restart plugin")
				else:
					self.indiLOG.log(10,u"HTTPlisten test sucessfull")
				self.testHTTPsuccess = 0
		except Exception as e:
			self.exceptionHandler(40,e)
		return 

###-------------------------------------------------------------------------####
	def checkIfPushToDevicesIsRequired(self, now, pushNow=False):
		try:
			#self.indiLOG.log(10,u"checkIfPushToDevicesIsRequired dt min {}, push {}".format(time.time() - self.checkTimeIfPushToDevicesIsRequired, pushNow))
			if time.time() - self.checkTimeIfPushToDevicesIsRequired < 0 : 
				return 
			if time.time() - self.checkTimeIfPushToDevicesIsRequired < 24*60*60 and not pushNow: 
				return 
			self.checkTimeIfPushToDevicesIsRequired  = time.time() + 30
			if now.hour != 1 and not pushNow: return 
			for devId in self.SHELLY:
				if devId == 0: continue
				if self.SHELLY[devId]["isChild"]: continue


				try: # just in case not properly defined
					if self.SHELLY[devId]["lastSuccessfullConfigPush"]["all"] == 0: pass
				except:
					self.SHELLY[devId]["lastSuccessfullConfigPush"] = {"all":-10}

				if time.time() - self.SHELLY[devId]["lastSuccessfullConfigPush"]["all"] > self.repeatConfigPush or (pushNow and time.time() - self.SHELLY[devId]["lastRequestedPush"] < 10 ):
					if self.SHELLY[devId]["pushIdActive"] in ["enabled","waiting"]:
						#self.indiLOG.log(10,u"checkIfPushToDevicesIsRequired: {}; pushIdActive={}".format(devId, self.SHELLY[devId]["pushIdActive"]))
						self.addToPushConfigToShellyDeviceQueue(devId)
		except Exception as e:
			self.exceptionHandler(40,e)
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
					if "expired" not in dev.states: continue
					if time.time() - self.startTime > 300: # no expirtaion in first 5 minutes after start, give it time to receive messages
						props = dev.pluginProps
						if time.time() - self.SHELLY[devId]["lastMessageFromDevice"] > self.SHELLY[devId]["expirationSeconds"]:
							if dev.states["expired"].find("no") == 0 or len(dev.states["expired"]) < 10: # either "no ...  datestring" or  (empty or junk, must have datestring if not simply "no" )
								self.indiLOG.log(10,u"setting dev:{} to expired; minutes since last contact:{:.0f};  expiration Setting:{:.0f}[Min]".format(dev.name, (time.time() - self.SHELLY[devId]["lastMessageFromDevice"])/60, self.SHELLY[devId]["expirationSeconds"]/60))
								dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)
								dev.updateStateOnServer("expired", now.strftime(_defaultDateStampFormat))

					self.SHELLY[devId]["deviceEnabled"]  = dev.enabled

			for devId in delShelly:
				self.indiLOG.log(10,u"deleting {} {}".format(devId, self.SHELLY[devId]))
				del self.SHELLY[devId]
		except Exception as e:
			self.exceptionHandler(40,e)
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
						self.indiLOG.log(10,u"SHELLY discovery: skipping ip# {}, alread exists".format(self.nextIPSCAN))
						self.nextIPSCAN = ""
						break
				if self.nextIPSCAN == "": continue
				self.indiLOG.log(10,u"SHELLY discovery: probing  ip# {}, for 20 secs".format(self.nextIPSCAN))
				self.SHELLY[0]["ipNumber"] = self.nextIPSCAN
				self.addToShellyPollerQueue(0, "settings")
				for ii in range (20):
					time.sleep(1)
					if self.nextIPSCAN == "": break
			self.indiLOG.log(10,u"SHELLY discovery: finished")

		except Exception as e:
			self.exceptionHandler(40,e)
		return 

####-------------------------------------------------------------------------####
	def testHTTPlistener(self):
		try:
			self.SHELLY[0]["ipNumber"] = self.HTTPlisternerTestIP
			self.testHTTPsuccess = time.time()
			if self.decideMyLog(u"HTTPlistener"): self.indiLOG.log(10,u"..  starting http listener TEST @:http://{}:{}/test".format(self.HTTPlisternerTestIP, self.portOfIndigoServer) )
			self.getJsonFromDevices( self.HTTPlisternerTestIP, "test", jsonAction="", port = str(self.portOfIndigoServer), testHTTP=True)
		except Exception as e:
			self.exceptionHandler(40,e)
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

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"data:{}".format(data))
		return 


####-------------------------------------------------------------------------####
	def workOnQueue(self):
		try:
			self.queueActive  = True
			while not self.messagesQueue.empty():
				items = self.messagesQueue.get() 
				#if self.decideMyLog(u"Polling"): self.indiLOG.log(10,u"workOnQueue  items:{}".format(items))
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
		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"data:{}".format(data))
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
			if self.decideMyLog(u"Polling"): self.indiLOG.log(10,u"queue received: items:{}".format(items) )

			if "shellyIndigoDevNumber" in items: 					self.workOnRegularMessage(items)
								
			elif "page" in items and items["page"] == "httpAction":	self.workOnActionMessage(items)

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u" data:{}".format(items) )
		return 

####-------------------------------------------------------------------------####
	def workOnRegularMessage(self, items):
		try:
			ipNumber = ""
			if "ipNumber" in items: ipNumber = items["ipNumber"]
			else:					ipNumber = ""
			if ipNumber in self.ignoredIPNumbers: 
				if self.decideMyLog(u"Polling"): self.indiLOG.log(10,u"queue checking devid:{};  IP#:{} rejected in ignore list".format( items["shellyIndigoDevNumber"] , ipNumber) )
				return 
			# thhis is message from myself, for testing can be ignored
			if ipNumber == self.HTTPlisternerTestIP: 
				return 	

			newDeviceCreated = False
			# no indigo dev number, must be new 
			if items["shellyIndigoDevNumber"]  == 0:
				data = items["data"]
				self.indiLOG.log(10,u"execUpdate checking for new device received, ipNumber:{}; data:{} ".format( items["shellyIndigoDevNumber"], ipNumber, data) )
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
						self.indiLOG.log(10,u"execUpdate dev: {} IPNUMBER has changed ..  new IP#:{}, old IP#:{}".format(devIdFound, ipNumber, self.SHELLY[devIdFound]["ipNumber"]))
						self.changeIpNumber(dev, self.SHELLY[devIdFound]["ipNumber"], ipNumber)
						items["shellyIndigoDevNumber"] = devIdFound
						dev = indigo.devices[devIdFound]

				# is the device enabled in indigo?
				doNotCreate = False
				if items["shellyIndigoDevNumber"] == 0:
					for dd in indigo.devices.iter(self.pluginId):
						if dd.address == ipNumber:
							if not dd.enabled:
								self.indiLOG.log(10,u"execUpdate shellyIndigoDevNumber ==0, .. dev:{}  is disabled, will NOT create new one;  ipNumber:{}".format(dd.name, ipNumber))
							else:
								self.indiLOG.log(10,u"execUpdate .. msg dev:{}  is unexpected message, will NOT create new one; ipNumber:{}, data:{}".format(dd.name, ipNumber, data))
							doNotCreate = True

						#self.renewShelly(dd, startCom=False)
					if doNotCreate: return 

					if "device" not in data:
						self.indiLOG.log(30,u"execUpdate  new dev ipnumber:{}, sending request for settings, not enough info:{}".format(ipNumber, items) )
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
		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u" data:{}".format(items) )
	
####-------------------------------------------------------------------------####
	def workOnActionMessage(self, items):
		try:
			#{"ipNumber":192.168.1.x, "page":"httpAction", "data":{"path": {'path': '/?data&hum=33&temp=15.25'},}
			if self.decideMyLog(u"HTTPlistener"): self.indiLOG.log(10,u"workOnActionMessage queue page item present items:{}".format(items) )
			if "ipNumber" not in items: 
				return 
			ipNumber = items["ipNumber"]
			if ipNumber in self.ignoredIPNumbers: return 

			if ipNumber == self.HTTPlisternerTestIP:
				# reset open channel queue
				self.SHELLY[0]["ipNumber"] = ""
				self.testHTTPsuccess = time.time() + 100 
				if self.decideMyLog(u"HTTPlistener"): self.indiLOG.log(10,u"http listener self test received .. ok" )
				return 

			# bad data check, just a save gurad should not be the case
			if "data" not in items: return 
			data       = items["data"]["path"]
			found      = False
			devIdFound = 0
			for devId in self.SHELLY:
				if self.SHELLY[devId]["isChild"]: continue 
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
				self.addToShellyPollerQueue(devIdFound, "status")
				# check if we should push settings, good for battery devices, as they only wake up every x hours
				if  time.time() - self.SHELLY[devId]["lastSuccessfullConfigPush"]["all"] > self.repeatConfigPush:
					self.SHELLY[devId]["lastSuccessfullConfigPush"] = {"all": -10}
					self.addToPushConfigToShellyDeviceQueue(devId)
				


			if not found:
				## get full description to trigger dev generation
				doNotCreate = False
				for dd in indigo.devices.iter(self.pluginId):
					if dd.address == ipNumber:
						if not dd.enabled:
							self.indiLOG.log(10,u"execUpdate .. dev:{}  is disabled, will NOT create new one; ipNumber:{}, data:".format(dd.name, ipNumber, data))
							doNotCreate = True
						else:
							self.indiLOG.log(10,u"execUpdate .. dev:{}  httpAction has unexpected message,from ipNumber:{}, sending status request data:{}".format(dd.name, ipNumber, data))
				if doNotCreate: return  
				self.indiLOG.log(10,u"execUpdate ..   httpAction has unexpected message,from ipNumber:{}, sending settings request;  data received:{}".format(ipNumber, data))
				self.initShelly(0, "", ipNumber, startPoller=True)
				self.addToShellyPollerQueue(0, "settings")
		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u" data:{}".format(items) )
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

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u" data:{}".format(items) )
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

			if self.SHELLY[parentDev.id]["isParent"]:
				children = self.SHELLY[parentDev.id]["children"]
			else:
				children = {}
			
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

			self.indiLOG.log(10,u"external sensors toBeCreated: {}".format(toBeCreated))

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
					self.indiLOG.log(10,u"trying to create new SHELLY device,  name:{}, ipNumber:{}".format((baseName+nameX), ipNumber))
					try: 
						indigo.devices[baseName+nameX]
						self.indiLOG.log(10,u"... device, already exist, disabled? name:{}".format((baseName+nameX)))
						for dd in indigo.devices.iter(self.pluginId):
							self.renewShelly(dd, startCom=False)
						nameX += "_r_"+str(int(time.time()))		
						self.indiLOG.log(10,u"... changing name to: {}".format((baseName+nameX)))
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
					self.indiLOG.log(10,u"==> created: {}".format(devChild.name))
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


		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u" data:{}".format(data) )
		return 

####-------------------------------------------------------------------------####
	def createParentShellyDevice(self, data, ipNumber ):
		try:
			devId = 0

			if "device"  in data:
					deviceTypeId = data["device"]["hostname"]
					useDevType   = deviceTypeId.rsplit("-", 1)[0]
					if useDevType == "shellyswitch25" and "mode" in data and data["mode"] == "roller":
						useDevType  += "-roller"
					if useDevType.find("shellydw") !=-1:
						useDevType  = "shellydw"

					MAC    = data["device"]["mac"]
			else: return 0

			self.indiLOG.log(10,u"==> create ShellyDevice for {}, deviceTypeId:{}".format(ipNumber, useDevType) )


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
			if useDevType == "shellyswitch25-roller" and "mode" in data and data["mode"] == "roller":
				description = "On=close=100%"

			try:
				try: 
					indigo.devices[name_Parent]
					self.indiLOG.log(10,u"trying to create new SHELLY device, already exist, disabled? name:{}, ipNumber:{}".format(name_Parent, ipNumber))
					for dd in indigo.devices.iter(self.pluginId):
						self.renewShelly(dd, startCom=False)
					name_Parent += "_r_"+str(int(time.time()))
					self.indiLOG.log(10,u"... changing name to: {}".format((name_Parent)))
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
				self.addToPushConfigToShellyDeviceQueue(devParent.id)
				self.indiLOG.log(10,u"==> created: {}".format(devParent.name))
				devId = devParent.id

			except Exception as e:
				self.exceptionHandler(40,e)
				self.indiLOG.log(40,u"name:{}, props:{}, ipNumber:{}, description:{}, deviceTypeId:>>{}<<\n ".format(name_Parent, props, ipNumber,description, useDevType))
				return 0

			#now create regular splitoff childs if needed
			if useDevType != "shellyswitch25-roller":
				self.createShellyChildDevice( devParent, useDevType, MAC, ipNumber, name_Parent)
				

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"data:{}".format(data))
		return devId


####-------------------------------------------------------------------------####
	def createShellyChildDevice(self, devParent, useDevType, MAC, ipNumber, name_Parent):
		try:
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
				self.indiLOG.log(10,u"==> created: {}".format(devChild.name))

				# finish parent setup
				nextNo = 0
				if childType not in children: children[childType] ={}
				for dd in children[childType]:
					nextNo = max( nextNo, int(dd) )
				children[childType][str(nextNo+1)] = devChild.id
			parentProps = devParent.pluginProps
			parentProps["children"] = json.dumps(children)
			devParent.replacePluginPropsOnServer(parentProps)
			self.SHELLY[devParent.id]["isParent"] = True
			self.SHELLY[devParent.id]["children"] = children
				

		except Exception as e:
			self.exceptionHandler(40,e)
		return 


####-------------------------------------------------------------------------####
	def initDevProps(self, deviceTypeId, MAC, ipNumber):
		props = {}
		try:
			props		   					= copy.copy(_emptyProps[deviceTypeId]["props"])
			props["MAC"] 					= MAC
			props["ipNumber"] 				= ipNumber
				
		except Exception as e:
			self.exceptionHandler(40,e)

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
				self.SHELLY[devId]["push"]									= {}
			self.SHELLY[devId]["MAC"] 										= MAC
			self.SHELLY[devId]["ipNumber"] 									= ipNumber.strip()
			if "pushIdActive" not in self.SHELLY[devId]:
				self.SHELLY[devId]["pushIdActive"] 							= "empty"
			self.SHELLY[devId]["deviceEnabled"] 							= True
			self.SHELLY[devId]["devTypeId"] 								= deviceTypeId
			if not self.SHELLY[devId]["isChild"] and startPoller:			self.startShellyDevicePoller("start", shellySelect=devId)
			if "lastRequestedPush" not in self.SHELLY[devId]:				self.SHELLY[devId]["lastRequestedPush"] = 0

		except Exception as e:
			self.exceptionHandler(40,e)

		return 
		

####-------------------------------------------------------------------------####
####-------------------------------------------------------------------------####
####---------------------fill devices with info from shell-------------------####
####-------------------------------------------------------------------------####
####-------------------------------------------------------------------------####
	def fillShellyDeviceStates(self, data, dev, page, ipNumber):


		if page not in ["settings","status","init","httpAction"]: return 

		try:
			if  time.time() - self.SHELLY[dev.id]["lastSuccessfullConfigPush"]["all"] > self.repeatConfigPush-1200:
				self.SHELLY[dev.id]["lastSuccessfullConfigPush"] = {"all":-10}
				self.addToPushConfigToShellyDeviceQueue(dev.id)


			if self.SHELLY[dev.id]["isParent"]:
				children = self.SHELLY[dev.id]["children"]
			else:
				children = {}
		
			if "device" in data: 
				deviceTypeId = data["device"]["hostname"].rsplit("-", 1)[0]
				if deviceTypeId.find("shellydw") >-1: deviceTypeId = "shellydw"
				
			else:
				deviceTypeId = dev.deviceTypeId
			if deviceTypeId == "shellyswitch25":
				if "mode" in data and data["mode"] == "roller":
					if deviceTypeId.find("+roller") ==-1:
						deviceTypeId = "shellyswitch25-roller"

	
			if page == "httpAction":
				self.fillHTTPactionData(data, dev)
				self.executeUpdateStatesDict()
				self.addToShellyPollerQueue(dev.id, "status")
				
				return 

			self.fillExternalSensors(data, dev, children)

			self.fillLight(data, dev)

			self.fillSHWT( data, dev)

			self.fillSHSK( data, dev)

			self.fillSHGAS( data, dev)

			self.fillshellydw( data, dev)

			self.fillshellyMotion( data, dev)

			self.executeUpdateStatesDict()

			# now for devices with children 
			devs, devNos = self.getChildDevices(children)
			if False and len(children) >0:
				devids = [dd.id for dd in devs]
				self.indiLOG.log(10,u"{};   children:{};  childrenfromProps:{};  devids:{}, devNos:{}".format(dev.name, children, dev.pluginProps["children"], devids, devNos))
				
			if len(devs) ==0: devs = [dev, dev]
			else:			  
				dev0 = [dev]
				dev0.extend(devs)
				devs = dev0
			

			self.fillInputs(data, devs )

			self.fillRelays(data, devs)

			self.fillRollers(data, devs)

			self.filleMeters(data, devs)

			self.fillMeters(data, devs)

			
			if devs[0].id == devs[1].id: devs=[dev]

			for devNo in range(len(devs)):
				devX  = devs[devNo]

				if self.fillbasicProps(data, devX, devNo):
					devX = indigo.devices[devX.id]

				# for ext sensors dont fill with internal tmp sensor data, has same data
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

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"data:{}".format(data))

		self.executeUpdateStatesDict()
		return 

####-------------------------------------------------------------------------####
####  this is called when the device sends an action triggered by button, inputs, or temp/hum changes
####-------------------------------------------------------------------------####
	def fillHTTPactionData(self, data, dev):
		try:
			self.SHELLY[dev.id]["lastMessage-Http"] = data
			if self.decideMyLog(u"HTTPlistener"):self.indiLOG.log(10,u"doHTTPactionData {}, id:{}, devType:{},  data: {}".format(self.SHELLY[dev.id]["ipNumber"],dev.id, dev.deviceTypeId ,data) )
			if dev.deviceTypeId.split("-")[0] not in _definedShellyDeviceswAction: return

			children = self.SHELLY[dev.id]["children"]
			devs, devNos = self.getChildDevices(children)
			devs = [dev] + devs # indexes start w 1 for input .... 
			if self.decideMyLog(u"HTTPlistener"):self.indiLOG.log(10,u"doHTTPactionData  .. len(devs):{}, devNos:{}, children:{}".format(len(devs), devNos, children) )

			## eg data&hum=55&temp=33.7
			## eg ?onOffState=0 or 1
			## eg data?input=short/double_short/triple_short/long
			## /input_1=off or /?input_1=off ..
			dst = datetime.datetime.now().strftime(_defaultDateStampFormat) 

			## this makes it indendent of data format can have a / or ?  and strip first&
			posQ = data.find("/")
			if posQ >-1: data = data[posQ+1:]
			posQ = data.find("?")
			if posQ >-1: data = data[posQ+1:]
			posQ = data.find("?")
			if posQ >-1: data = data[posQ+1:]

			useDev = dev
			devNo = 0
			if self.decideMyLog(u"HTTPlistener"):self.indiLOG.log(10,u"doHTTPactionData  ..  data after: {}<".format(data) )
			TRIGGERS = []
			if True:
				cmd = data.split("&")
				for item in cmd:
					if len(item) < 1: continue
					x = item.split("=")  # eg input=on; input_1=on; "onOffState=1; "onOffState_1=1 ==> x=["input","on",True]; x=["input_1","on",True]
					if len(x) == 2:
						x.append(True)
						if   x[0] == "hum":   x[0] = "Humidity"
						elif x[0] == "temp":  x[0] = "Temperature"

						elif x[0].find("onOffState") == 0:
							if   x[1] == "1": x[1] = True
							elif x[1] == "0": x[1] = False
							if x[0].find("_") >-1:
								xxx = x[0].split("_") # for devices w 2 buttons onOfstate + onOfstate_1
								devNo = int(xxx[1])
								x[0] = xxx[0]
								useDev = devs[devNo]
							x[0] = "onOffState"

						elif x[0].find("action") == 0:
							x[2] = True

						elif x[0].find("alarm") == 0:
							pass


						elif x[0].find("action") == 0:
							if  x[1] == "button": 
								x[2] = dst


						elif x[0].find("input") == 0:# input=on; input_1=on;
							for inputType in [["1","on","input"],["0","off","input"],["short",dst,"input_short"],["short_double",dst,"input_short_double"],["short_triple",dst,"input_short_triple"],["long",dst,"input_long"],["long_short",dst,"input_long_short"],["short_long",dst,"input_short_long"]]:
								if x[1] == inputType[0]: 
									if x[0].find("_") >-1:
										xxx = x[0].split("_")# for devices w 2+ buttons input + input_1 + input_2
										devNo = int(xxx[1])
										x[0] = xxx[0]
										useDev = devs[devNo]
									x[1] = inputType[1]
									x[0] = inputType[2]
									break

						elif x[0] not in useDev.states: # x=["input_1","on",True] ==> x=["input","on",True]
							if x[0].split("_")[0] in useDev.states:
								x[0] = x[0].split("_")[0] 
							else: x[2] = False

						else:
							pass

						TRIGGERS.append(x)
					else:
						pass
						# TRIGGERS.append({"cmd":item})
				if self.decideMyLog(u"HTTPlistener"):self.indiLOG.log(10,u"doHTTPactionData {}  devType:{}  TRIGGERS:{}".format(self.SHELLY[dev.id]["ipNumber"], useDev.deviceTypeId , TRIGGERS) )
			else:
				return

			devID = str(useDev.id)
			deviceTypeId = useDev.deviceTypeId.split("-")[0]

			if deviceTypeId == "shellyflood":
				# data:= {'path': >>> '/data?temp=32.62&flood=1&batV=2.83'}<<< 
				for trigger in TRIGGERS:
					if trigger[0] == "flood":
						if trigger[1] == "1" and dev.states["Flood"] != "FLOOD": 
							self.addToStatesUpdateDict(devID, "Flood", "FLOOD" )
							self.addToStatesUpdateDict(devID, "onOffState", True)
							if "previousAlarm" in dev.states and "lastAlarm" in dev.states:
								self.addToStatesUpdateDict(dev.id, "previousAlarm", dev.states["lastAlarm"])
							self.addToStatesUpdateDict(devID, "lastAlarm", dst)
							useDev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
							self.SHELLY[useDev.id]["lastAlarm"] = time.time()

						if trigger[1] == "0" and dev.states["Flood"] == "FLOOD": 
							self.addToStatesUpdateDict(devID, "Flood", "dry" )
							self.addToStatesUpdateDict(devID, "onOffState", False)
							useDev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn) # green
							self.SHELLY[useDev.id]["lastAlarm"] = time.time()

			elif deviceTypeId.find("shellyht") >-1:
				# data:= /data?&hum=49&temp=29.00 
				for trigger in TRIGGERS:
					if trigger[0] == "Temperature":
						self.fillSensor(useDev, {"Temperature": trigger[1]}, "Temperature", "Temperature")

					if trigger[0] == "Humidity": # it goes to the child dev (devNo =1)
						self.fillSensor(devs[1], {"Humidity": trigger[1]},    "Humidity",    "Humidity")


			elif deviceTypeId.find("shellymotionsensor") >-1:
				for trigger in TRIGGERS:
					if trigger[0] == "motion":
						self.addToStatesUpdateDict(devID, "previousMotionTrigger",		dev.states["lastMotionTrigger"])
						self.addToStatesUpdateDict(devID, "lastMotionTrigger", 			dst)
						if x[1] == "on": 
							self.addToStatesUpdateDict(devID, "motionTrigger",			x[1],								"Motion")
							if not dev.states["onOffState"]: 
								self.addToStatesUpdateDict(devID, "onOffState", 		True,								"Motion",	force="ui")
							dev.updateStateImageOnServer(indigo.kStateImageSel.MotionSensorTripped)

						else:
							dev.updateStateImageOnServer(indigo.kStateImageSel.MotionSensor)
							self.addToStatesUpdateDict(devID, "onOffState", 			False,								"off",		force="ui")
							self.addToStatesUpdateDict(devID, "motionTrigger",			x[1],								"off")

					if trigger[0] == "tamper": # temaper overwrites motion ui value
						if x[1] == "on": 
							self.addToStatesUpdateDict(devID, "tamperTrigger",			True,								"Tamper")
							self.addToStatesUpdateDict(devID, "onOffState",				True,								"Tamper",	force="ui")
							self.addToStatesUpdateDict(devID, "previousTamperTrigger",	dev.states["lastTamperTrigger"])
							self.addToStatesUpdateDict(devID, "lastTamperTrigger", 		dst)
							dev.updateStateImageOnServer(indigo.kStateImageSel.MotionSensorTripped)

						else:
							self.addToStatesUpdateDict(devID, "tamperTrigger",			False,								"no")
							if dev.states["motionTrigger"]:
								self.addToStatesUpdateDict(devID, "onOffState",			True,								"Motion",	force="ui")
							else:
								self.addToStatesUpdateDict(devID, "onOffState",			False,								"off",		force="ui")
								dev.updateStateImageOnServer(indigo.kStateImageSel.MotionSensor)

					if trigger[0] == "bright":
						self.addToStatesUpdateDict(devID, "previousBrightTrigger",		dev.states["lastBrightTrigger"])
						self.addToStatesUpdateDict(devID, "lastBrightTrigger",			dst)

					if trigger[0] == "dark":
						self.addToStatesUpdateDict(devID, "previousDarkTrigger",		dev.states["lastDarkTrigger"])
						self.addToStatesUpdateDict(devID, "lastDarkTrigger",			dst)

					if trigger[0] == "twilight":
						self.addToStatesUpdateDict(devID, "previousTwilightTrigger", 	dev.states["lastTwilightTrigger"])
						self.addToStatesUpdateDict(devID, "lastTwilightTrigger",		dst)



			elif deviceTypeId.find("shellysmoke") >-1:
				for trigger in TRIGGERS:
					if trigger[0] == "smoke":
						if "previousAlarm" in dev.states and "lastAlarm" in dev.states:
							self.addToStatesUpdateDict(devID, "previousAlarm", dev.states["lastAlarm"])
						self.addToStatesUpdateDict(devID, "lastAlarm", dst)
						self.addToStatesUpdateDict(devID, "Alarm",     x[1])

					if    x[1] == "off": dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
					else: 				 dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)


			elif deviceTypeId.find("shellygas") >-1:
				for trigger in TRIGGERS:
					if trigger[0] == "alarm":
						if "previousAlarm" in dev.states and "lastAlarm" in dev.states:
							self.addToStatesUpdateDict(devID, "previousAlarm", dev.states["lastAlarm"])
						self.addToStatesUpdateDict(devID, "lastAlarm", dst)
						self.addToStatesUpdateDict(devID, "Alarm",     x[1])

					if    x[1] == _alarmStates[0]: dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
					elif  x[1] == _alarmStates[1]: dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)
					elif  x[1] == _alarmStates[2]: dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
					else: 						   dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)


			elif deviceTypeId in ["shellydw","shellydw2"]:
				for trigger in TRIGGERS:
					if trigger[0] == "action" and trigger[1] == "close":
						self.addToStatesUpdateDict(devID, "closedTriggered", datetime.datetime.now().strftime(_defaultDateStampFormat))
						self.addToStatesUpdateDict(devID, "state", "close")
						self.fillSwitch( useDev, {"onOffState":False}, "onOffState")

					if trigger[0] == "action" and trigger[1] == "darkOpen":
						self.addToStatesUpdateDict(devID, "darkOpen", datetime.datetime.now().strftime(_defaultDateStampFormat))
						self.addToStatesUpdateDict(devID, "state", "open")
						self.fillSwitch( useDev, {"onOffState":True}, "onOffState")

					if trigger[0] == "action" and trigger[1] == "twilightOpen":
						self.addToStatesUpdateDict(devID, "state", "open")
						self.fillSwitch( useDev, {"onOffState":True}, "onOffState")
						self.addToStatesUpdateDict(devID, "twilightOpen", datetime.datetime.now().strftime(_defaultDateStampFormat))

					if trigger[0].find("onOffState") == 0:	
						self.addToStatesUpdateDict(devID, "state", "open")
						self.fillSwitch( useDev, {"onOffState":True}, "onOffState")
						self.addToStatesUpdateDict(devID, "daylightOpen", datetime.datetime.now().strftime(_defaultDateStampFormat))
				
			## cover the rest of the defined devices w actions reporting
			if deviceTypeId in _definedShellyDeviceswAction:
				for trigger in TRIGGERS:
					if self.decideMyLog(u"HTTPlistener"):						self.indiLOG.log(10,u"doHTTPactionData   trigger:{}".format(trigger) )

					if trigger[0].find("onOffState") == 0:						self.fillSwitch( useDev, {trigger[0]:trigger[1]}, trigger[0])

					if trigger[0].find("state")  == 0 and trigger[1]=="open":	self.fillSwitch( useDev, {"onOffState":True}, "onOffState")

					if trigger[0].find("state")  == 0 and trigger[1]=="close": 	self.fillSwitch( useDev, {"onOffState":False}, "onOffState")

					if trigger[0].find("action") == 0 and trigger[1]=="button" and trigger[2] == "date": 
																				self.addToStatesUpdateDict(devID, "input", dst)

					# rest of simple defined dev/states and input etc
					if trigger[0] in dev.states:								self.addToStatesUpdateDict(devID, trigger[0], trigger[1]) # this does "input" etc




			# missing or wrong
			else:
				self.indiLOG.log(10,u"doHTTPactionData {};  not supported message:{}".format(self.SHELLY[dev.id]["ipNumber"], data) )

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"len(devs):{}".format(len(devs)))
		return 





####-------------------------------------------------------------------------####
	def fillbasicProps(self, data, dev, devNo):
		try:
			devID = str(dev.id)
			renew = False

			if dev.deviceTypeId not in _externalSensorDevTypes: #this info is handled in fillExternalSensors
				self.SHELLY[dev.id]["lastMessageFromDevice"]  = time.time()
				if True:															self.addToStatesUpdateDict(str(dev.id),"lastMessageFromDevice", 	datetime.datetime.now().strftime(_defaultDateStampFormat))
				if "expired" 	 in dev.states:	
					if dev.states["expired"].find("-") == -1: 						self.addToStatesUpdateDict(devID, "expired", 						"no" )
					elif dev.states["expired"].find("no") == -1: 					self.addToStatesUpdateDict(devID, "expired", 						"no, last expired: {}".format(dev.states["expired"]) )

			if "bat"         in data: 
				if "value"   in data["bat"] and "batteryLevel" in dev.states: 		self.addToStatesUpdateDict(devID, "batteryLevel", 					data["bat"]["value"])
				if "voltage" in data["bat"] and "batteryVoltage" in dev.states: 	self.addToStatesUpdateDict(devID, "batteryVoltage", 				data["bat"]["voltage"])

			if "charger" in data :
				if "charger" in dev.states: 										self.addToStatesUpdateDict(devID, "charger", 						"USB" if data["charger"] else "Battery"  )


			if "cloud" in data and "enabled" in data["cloud"]:
				if "cloud" in dev.states: 
					if not data["cloud"]["enabled"]: 	info = "disabled"
					else:
						if "connected" in data:
							if  data["cloud"]["connected"]: info = "connected"
							else:							info = "enabled,disconnected"
						else: info = "enabled"
					if True:														self.addToStatesUpdateDict(devID, "cloud", 							info )

			if "update"     in data  and "has_update" in data["update"] and \
									"software_update_available" in dev.states: 		self.addToStatesUpdateDict(devID, "software_update_available", 		"YES" if data["update"]["has_update"]  else "is up to date")

			if "sleep_mode" in data and  "sleepMode" in dev.states:
					mapto = {"m":"minutes", "h":"hours", "s":"seconds", "":"unknown"}
					try: 	yy = mapto[data["sleep_mode"]["unit"]]
					except: yy = "unknown"
					xx = u"{:d} {:}".format(data["sleep_mode"]["period"],yy)
					if True:														self.addToStatesUpdateDict(devID, "sleepMode", 						xx, 								xx)

			if "set_volume" in data and "volume" in dev.states: 					self.addToStatesUpdateDict(devID, "volume", 						data["set_volume"])

			if "wifi_sta"   in data and "ipv4_method" in data["wifi_sta"]:
				if "WiFi_ipv4_method" in dev.states: 								self.addToStatesUpdateDict(devID, "WiFi_ipv4_method", 				data["wifi_sta"]["ipv4_method"])


			if "uptime"   in data and "upFor" in dev.states:
				upFor  = int(data["uptime"]/60)
				upForM = upFor%60
				upFor  = int(upFor/60.)  
				upForH = upFor%24
				upForD  = int(upFor/24.)  
				upFor = ""
				if upForD > 0: 
					upFor += "{} Days, ".format(upForD)
					upFor += "{} Hours, ".format(upForH)
				else:
					if upForH > 0: upFor += "{} Hours, ".format(upForH)
				upFor += "{} Minutes".format(upForM)					
				#self.indiLOG.log(10,u"uptime:{:.0f}  upFor:{} M:{}, H:{}, D:{}".format(data["uptime"]/60, upFor, upForM, upForH, upForD ))
				if True:															self.addToStatesUpdateDict(devID, "upFor", 				upFor, 				upFor)


			if "act_reasons" in data:
				out =""
				for xx in data["act_reasons"]:
					out+=xx+";"

				if len(out) >0:	
					if "action_from_device" in dev.states:							self.addToStatesUpdateDict(devID, "action_from_device",				 out.strip(";"))



			if "connect_retries" in data:
				if "WiFi_connect_retries" in dev.states: 							self.addToStatesUpdateDict(devID, "WiFi_connect_retries", 			data["connect_retries"])

			if "wifi_sta"    in data:
				if "rssi" in data["wifi_sta"] and "WiFi_rssi" in dev.states: 		self.addToStatesUpdateDict(devID, "WiFi_rssi", 						data["wifi_sta"]["rssi"], decimalPlaces=0)

				if ("enabled" in data["wifi_sta"] and data["wifi_sta"]["enabled"])  or ("u'connected" in data["wifi_sta"] and data["wifi_sta"]["u'connected"]):
					ipNumber = data["wifi_sta"]["ip"]
					if self.isValidIP(ipNumber):
						if dev.address != ipNumber:
							if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(30,u"ip number changed for devID{}; old:{} new:{}".format(dev.id, dev.address, ipNumber) )
							props = dev.pluginProps
							props["address"] = ipNumber
							dev.replacePluginPropsOnServer(props)
							renew = True

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"data {} ".format(data))
		return renew

####-------------------------------------------------------------------------####
	def fillLight(self, data, dev):
		try:
			if  "lights" not in data: return 
			devID = str(dev.id)
			#self.indiLOG.log(10,u"fillLight  dev:{}: {}".format(dev.name,data["lights"] ))
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
				if "ison" in light :	ison = 1 if  light["ison"] else 0

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

				if  "redLevel"		in dev.states: self.addToStatesUpdateDict(devID, "redLevel",	int(red*100./255.)*ison)
				if  "greenLevel"	in dev.states: self.addToStatesUpdateDict(devID, "greenLevel",	int(green*100./255.)*ison)
				if  "blueLevel"		in dev.states: self.addToStatesUpdateDict(devID, "blueLevel",	int(blue*100./255.)*ison)


				#if self.decideMyLog(u"Special"): self.indiLOG.log(10,u"fillShellyDeviceStates mode:{}, light:{}".format( mode, light) )
				if mode  == "color":
					if "red" in light and "white" in light:
						rgb = (red + green + blue)/3
						if rgb > 2:  # cut off 1 values, need at least 4 to shine 
							if "whiteLevel" 	 in dev.states: self.addToStatesUpdateDict(devID, "whiteLevel", 	int(rgb*100./255.)*ison, uiValue="{:d}%".format(int(rgb*100./255.)*ison ))
							if "brightnessLevel" in dev.states: self.addToStatesUpdateDict(devID, "brightnessLevel",int(rgb*100./255.)*ison, uiValue="{:d}%".format(int(rgb*100./255.)*ison ))
						if rgb <=2 and "white" not in light:  # is it off and no white data present?
							if "whiteLevel" 	 in dev.states: self.addToStatesUpdateDict(devID, "whiteLevel", 	0, uiValue="0%")
							if "brightnessLevel" in dev.states: self.addToStatesUpdateDict(devID, "brightnessLevel",0, uiValue="0%")
						elif "white" in light and rgb <= 2:
							if "whiteLevel" 	 in dev.states: self.addToStatesUpdateDict(devID, "whiteLevel", 	int(white*100./255.)*ison, uiValue="{:d}%".format(int(white*100./255.)*ison ))
							if "brightnessLevel" in dev.states: self.addToStatesUpdateDict(devID, "brightnessLevel",int(white*100./255.)*ison, uiValue="{:d}%".format(int(white*100./255.)*ison ))
				elif mode  == "white" and "brightness" in light:
					#if self.decideMyLog(u"Actions"): self.indiLOG.log(10,u"fillShellyDeviceStates setting mode=white, using brigthness, white to {} and bright to :{}".format( int(brightness)*ison, int(brightness)*ison ) )
					if "brightnessLevel" in dev.states: self.addToStatesUpdateDict(devID, "brightnessLevel", int(brightness)*ison, uiValue="{:d}%".format(int(brightness)*ison ))
					if "whiteLevel" 	 in dev.states: self.addToStatesUpdateDict(devID, "whiteLevel",      int(brightness)*ison, uiValue="{:d}%".format(int(brightness)*ison ))

				if "temp" in light and "whiteTemperature" in dev.states: 
					#self.indiLOG.log(10,u"fillLight   ...  oldwhiteTemperature:{}: filling w {}".format(dev.states["whiteTemperature"], light["temp"] ))
					self.addToStatesUpdateDict(devID, "whiteTemperature", 	light["temp"])

				
				if "ison"       in light and "onOffState" in dev.states: 
					#self.indiLOG.log(40,u"checking lights  on dev:{}  light ison:{}".format(dev.name, light["ison"]))
					self.addToStatesUpdateDict(devID, "onOffState",	light["ison"] )
					if light["ison"]:	dev.updateStateImageOnServer(indigo.kStateImageSel.DimmerOn)
					else:				dev.updateStateImageOnServer(indigo.kStateImageSel.DimmerOff)
				if "gain"       in light and "gain"       in dev.states: self.addToStatesUpdateDict(devID, "gain", 		light["gain"])
		except Exception as e:
			self.exceptionHandler(40,e)
		return 



####-------------------------------------------------------------------------####
	def fillshellydw(self, data, dev):
		try:
			if dev.deviceTypeId.find("shellydw") == -1: return 
			devID = str(dev.id)		
			if "lux" in data:
				self.addToStatesUpdateDict(devID, "lux", 			data["lux"]["value"], str(data["lux"]["value"])+"[lux]", decimalPlaces=1)
				self.addToStatesUpdateDict(devID, "illumination", 	data["lux"]["illumination"])
			if "accel" in data:
				self.addToStatesUpdateDict(devID, "tilt", 			data["accel"]["tilt"], str(data["accel"]["tilt"])+"º",decimalPlaces=0)
				self.addToStatesUpdateDict(devID, "vibration", 		"no" if data["accel"]["vibration"]==0 else "YES")
			if "sensor" in data:
				self.addToStatesUpdateDict(devID, "state", 			data["sensor"]["state"])
				self.addToStatesUpdateDict(devID, "onOffState",		data["sensor"]["state"] !="close")

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"{} data:{}".format(dev.id,data))
		return 



####-------------------------------------------------------------------------####
	def fillshellyMotion(self, data, dev):
		try:
			if dev.deviceTypeId.find("shellymotionsensor") == -1: return 
			devID = str(dev.id)		

			if  dev.displayStateImageSel == "SensorOff": forceupdateStateImage = True
			else: 										 forceupdateStateImage = False

			# for status info 
			if "lux" in data:
				self.addToStatesUpdateDict(devID, "lux", 			data["lux"]["value"], 			u"{:d} [Lux]".format(data["lux"]["value"]), decimalPlaces=0)
				self.addToStatesUpdateDict(devID, "illumination", 	data["lux"]["illumination"])

			if "sensor" in data:
				motion = data["sensor"]["motion"]
				tamper = data["sensor"]["vibration"] # == tamper
				self.addToStatesUpdateDict(devID, "motionTrigger", 	motion, "no" if motion else "YES")
				self.addToStatesUpdateDict(devID, "tamperTrigger", 	tamper, "no" if tamper else "YES")
				forceupdateStateImage = False

				if tamper:
						self.addToStatesUpdateDict(devID, "onOffState",	True, "Tamper", force = "ui")
						dev.updateStateImageOnServer(indigo.kStateImageSel.MotionSensorTripped)
				else:
					if motion:
						self.addToStatesUpdateDict(devID, "onOffState", True, "Motion", force = "ui")
						dev.updateStateImageOnServer(indigo.kStateImageSel.MotionSensorTripped)
					else:
						self.addToStatesUpdateDict(devID, "onOffState",	False, "off",   force = "ui")
						dev.updateStateImageOnServer(indigo.kStateImageSel.MotionSensor)

			else:
				if forceupdateStateImage:
					dev.updateStateImageOnServer(indigo.kStateImageSel.MotionSensor)


			## this is for settings only:
			if "motion" in data:
				if "enabled" in data["motion"]:
					self.addToStatesUpdateDict(devID, "motionTriggerEnabled", 	data["motion"]["enabled"])

				if "blind_time_minutes" in data["motion"]:
					xx = u"{:d} minutes".format(data["motion"]["blind_time_minutes"])
					self.addToStatesUpdateDict(devID, "motionBlindTime", 		xx)

				if "sensitivity" in data["motion"]:
					xx = data["motion"]["sensitivity"]
					if  	xx > 168: 	hml = "low"
					elif	xx > 84:  	hml = "med"
					else:				hml = "high"
					xx = u"{:d}/256 - {}".format(xx, hml)
					self.addToStatesUpdateDict(devID, "motionThreshold", 		xx)

				if "pulse_count" in data["motion"]:
					xx = u"{:d} to trigger".format(data["motion"]["pulse_count"])
					self.addToStatesUpdateDict(devID, "motionPulseCount", 		xx)

				if "operating_mode" in data["motion"]:
					mapto = {"0":"any light", "1":"only when dark", "2":"only when twilight", "3":"only when bright", "":"unknown"}
					try: 	xx = mapto[str(data["motion"]["operating_mode"])]
					except: xx = "unknown"
					self.addToStatesUpdateDict(devID, "motionOperationMode", 	xx)

			if "tamper_sensitivity" in data:
					xx = data["tamper_sensitivity"]
					if   xx  > 84: 	hml = "low"
					elif xx  > 42: 	hml = "med"
					else:			hml = "high"
					xx = u"{:d}/127 - {}".format(xx, hml)
					self.addToStatesUpdateDict(devID, "tamperThreshold", 		xx)

			if "twilight_threshold" in data:
					xx = u"{:d} [lux]".format(data["twilight_threshold"])
					self.addToStatesUpdateDict(devID, "twilightThreshold", 		xx)

			if "dark_threshold" in data:
					xx = u"{:d} [lux]".format(data["dark_threshold"])
					self.addToStatesUpdateDict(devID, "darkThreshold", 			xx)
	

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"{} data:{}".format(dev.id,data))
		return 


####-------------------------------------------------------------------------####
	def fillSHWT(self, data, dev):
		try:
			if dev.deviceTypeId.find("shellyflood")==-1: return 
			if "flood" in data  and "Flood" in dev.states:
				#self.indiLOG.log(10,u"flood: regular data:{}".format(data) )
				devID = str(dev.id)		
				flood = True if data["flood"]  else False
				if flood and not dev.states["onOffState"]:
						#self.indiLOG.log(40,u"flood: setting trip to green" )
						self.addToStatesUpdateDict(devID, "Flood", "FLOOD" )
						self.addToStatesUpdateDict(devID, "onOffState",True)
						self.addToStatesUpdateDict(devID, "previousAlarm", dev.states["lastAlarm"])
						self.addToStatesUpdateDict(devID, "lastAlarm", datetime.datetime.now().strftime(_defaultDateStampFormat))
						dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
				if not flood and dev.states["onOffState"]:
						self.addToStatesUpdateDict(devID, "Flood", "dry" )
						self.addToStatesUpdateDict(devID, "onOffState",False)
						dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"{} data:{}".format(dev.id,data))
		return 



####-------------------------------------------------------------------------####
	def fillSHSK(self, data, dev):
		try:
			if dev.deviceTypeId != "shellysmoke": return 
			if "smoke" in data  and "Smoke" in dev.states:
				#self.indiLOG.log(10,u"flood: regular data:{}".format(data) )
				devID = str(dev.id)		
				smoke = data["smoke"]
				if smoke and not dev.states["onOffState"]:
						#self.indiLOG.log(40,u"flood: setting trip to green" )
						self.addToStatesUpdateDict(devID, "Smoke", "smoke" )
						self.addToStatesUpdateDict(devID, "onOffState",True)
						self.addToStatesUpdateDict(devID, "previousAlarm", dev.states["lastAlarm"])
						self.addToStatesUpdateDict(devID, "lastAlarm", datetime.datetime.now().strftime(_defaultDateStampFormat))
						dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
				if not smoke and dev.states["onOffState"]:
						self.addToStatesUpdateDict(devID, "Smoke", "clear" )
						self.addToStatesUpdateDict(devID, "onOffState",False)
						dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"{} data:{}".format(dev.id,data))
		return 


####-------------------------------------------------------------------------####
	def fillSHGAS(self, data, dev):
		try:
			if dev.deviceTypeId != "shellygas":			return 
			devID = str(dev.id)		

			if "gas_sensor" 		not in data: 		return 
			if "concentration" 		not in data:		return
			if "concentration" 		not in data:		return
			if "Gas_concentration" 	not in dev.states: 	return 
			if "Alarm" 				not in dev.states: 	return 
			if "sensor_state" 		not in dev.states: 	return 
			#'data': { u'gas_sensor': {u'sensor_state': u'normal', u'alarm_state': u'none', u'self_test_state': u'completed'}, 'concentration': {u'is_valid': True, u'ppm': 0} }
			#self.indiLOG.log(10,u"flood: regular data:{}".format(data) )
			#self.indiLOG.log(40,u"flood: setting trip to green" )
			GS = data["gas_sensor"]
			CO = data["concentration"]
			alarmState = unicode(GS["alarm_state"])
			if alarmState == "heavy": alarmState = "high"
			props = dev.pluginProps

			if "self_test_state" not in self.SHELLY[dev.id]: self.SHELLY[dev.id]["self_test_state"] = 0
			if GS["self_test_state"] != "completed":
				#if self.decideMyLog(u"Special"): self.indiLOG.log(10,u"fillSHGAS setting freq to 10 secs" )
				self.SHELLY[dev.id]["pollingFrequency"]	 = 10	
			if GS["self_test_state"] == "not_completed" and GS["sensor_state"] == "normal": # startup is finished, but not self test, force selftest
				if "self_test_state" not in self.SHELLY[dev.id] or time.time() - self.SHELLY[dev.id]["self_test_state"] > 100: # only force if last force > 100 secs agao
					self.SHELLY[dev.id]["self_test_state"] = time.time()
					self.addToShellyPollerQueue( dev.id, "self_test", now=True)
					warmingUp = "starting"
				else:
					warmingUp = "waiting"
			else:
				warmingUp = "normal" 

			if GS["self_test_state"] == "completed" and GS["sensor_state"] == "normal":
				if not dev.states["onOffState"]:
					#if self.decideMyLog(u"Special"): self.indiLOG.log(10,u"fillSHGAS setting freq time" )
					if time.time() - self.SHELLY[dev.id]["self_test_state"] < 50:
						#if self.decideMyLog(u"Special"): self.indiLOG.log(10,u"fillSHGAS setting freq to {}".format(float(dev.pluginProps["pollingFrequency"])) )
						self.SHELLY[dev.id]["pollingFrequency"] = float(props["pollingFrequency"])		
					self.addToStatesUpdateDict(devID, "onOffState", True)
			else:
				self.addToStatesUpdateDict(devID, "onOffState", False)


			self.addToStatesUpdateDict(devID, "sensor_state", 	 GS["sensor_state"])
			self.addToStatesUpdateDict(devID, "self_test_state", GS["self_test_state"])


			if CO["is_valid"]:
				if CO["ppm"] > 30: # thats a whiff,  
					self.SHELLY[dev.id]["pollingFrequency"] = 15# fast polling if there is any gas  	
				else:
					self.SHELLY[dev.id]["pollingFrequency"] = float(props["pollingFrequency"]) 	

				self.fillMinMaxSensors(dev,"Gas_concentration",CO["ppm"], decimalPlaces=0)
				self.addToStatesUpdateDict(devID, "Gas_concentration", CO["ppm"], uiValue="{:d} [ppm]".format(CO["ppm"]), decimalPlaces=0)
				self.addToStatesUpdateDict(devID, "sensorValue", CO["ppm"], uiValue="{:d} [ppm]".format(CO["ppm"]), decimalPlaces=0)
			else:
				if GS["sensor_state"] == "warm_up" and warmingUp != "normal":
					self.addToStatesUpdateDict(devID, "Gas_concentration", -99 , uiValue = warmingUp, decimalPlaces=0)
					self.addToStatesUpdateDict(devID, "sensorValue", -99, uiValue=warmingUp)

				elif GS["sensor_state"] == "not_completed" and warmingUp != "normal":
					self.addToStatesUpdateDict(devID, "Gas_concentration", -99 , uiValue = warmingUp, decimalPlaces=0)
					self.addToStatesUpdateDict(devID, "sensorValue", -99, uiValue=warmingUp, decimalPlaces=0)

				elif GS["sensor_state"] == "warmup":
					self.addToStatesUpdateDict(devID, "Gas_concentration", -99 , uiValue = "warmup", decimalPlaces=0)
					self.addToStatesUpdateDict(devID, "sensorValue", -99, uiValue="warmup", decimalPlaces=0)

				else:
					self.addToStatesUpdateDict(devID, "Gas_concentration", -99 , uiValue = "error", decimalPlaces=0)
					self.addToStatesUpdateDict(devID, "sensorValue", -99, uiValue="error", decimalPlaces=0)

			if "useAlarm" in props:
				if props["useAlarm"] != "sensor":
					try:
						alarmLimits = props["useAlarm"] .split("-")
						alarmLimits = [int(alarmLimits[0]),int(alarmLimits[1])]
						if   CO["ppm"] < alarmLimits[0]:	alarmState = "none"
						elif CO["ppm"] > alarmLimits[1]:	alarmState = "high"
						else:								alarmState = "medium"
					except:
						self.indiLOG.log(30,'"Use for Alarm State.." in device edit not set')
				
			self.addToStatesUpdateDict(devID, "Alarm", alarmState, uiValue=alarmState)

			if   alarmState == _alarmStates[0]: dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn) # green
			elif alarmState == _alarmStates[1]: dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)# grey
			elif alarmState == _alarmStates[2]: dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped) # red
			else: 								dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"{} data:{}".format(dev.id,data))
		return 

####-------------------------------------------------------------------------####
	def fillExternalSensors(self, data, parentDev, children):
		try:
			#   structure: "ext_temperature":{"0":{"tC":22.88,"tF":73.175000},"1":{"tC":23.25,"tF":73.850000}}
			#self.indiLOG.log(10,u"===fillExternalSensors==== parentDev:{} data:{}".format(parentDev.id, unicode(data)[0:50]))
			for childDevType in _childDevTypes:
				#self.indiLOG.log(10,u"===fillExternalSensors childDevType:{}".format(childDevType))
				if childDevType in data and type(data[childDevType]) == type({}) and data[childDevType] !={}:
					if _childDevTypes[childDevType]["dataKey"] == "": continue # this will select only ext_sensors
					#self.indiLOG.log(10,u"===fillExternalSensors childDevType data:{}".format(data[childDevType]))
					for ii in data[childDevType]:
						xxx = data[childDevType][ii]
						devNo 	  = ii
						devNoText = str(int(ii)+1)
						#self.indiLOG.log(10,u"===fillExternalSensors ii:{}, xxx:{}".format(ii, xxx))
						if _childDevTypes[childDevType]["dataKey"] in xxx:
							state = _childDevTypes[childDevType]["state"]
							#self.indiLOG.log(10,u"===fillExternalSensors state :{},  dev-children:{}".format(state,children))
							if childDevType not in children: continue
							if devNo not in children[childDevType]: continue
							childDevId = children[childDevType][devNo] 
							if childDevId ==0: continue
							try: 	childDev = indigo.devices[childDevId]
							except: continue
							#self.indiLOG.log(10,u"===fillExternalSensors childDevId :{}".format(childDevId))
							if state in childDev.states:
								#self.indiLOG.log(10,u"===fillExternalSensors filling sensor w xxx:{}, key:{}, state:{}".format(xxx, _childDevTypes[childDevType]["dataKey"], state))
								self.fillSensor(childDev, xxx, _childDevTypes[childDevType]["dataKey"], state)
								self.addToStatesUpdateDict(str(childDev.id),"lastMessageFromDevice", datetime.datetime.now().strftime(_defaultDateStampFormat))
								self.SHELLY[childDev.id]["lastMessageFromDevice"] = time.time()
								if "expired" 	 in childDev.states:	
									if childDev.states["expired"].find("-") == -1: # do we have a date string, if not just set it o no
											self.addToStatesUpdateDict(childDev.id, "expired", "no" )
									else:  # if datestring, check if we have a no in front
										if childDev.states["expired"].find("no") == -1:
											self.addToStatesUpdateDict(childDev.id, "expired", "no, last expired: {}".format(childDev.states["expired"]) )
		except Exception as e:
			self.exceptionHandler(40,e)
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
		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"deviceTypeId:{}; children {}, devNos:{}".format(deviceTypeId, children, devNos))
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
		except Exception as e:
			self.exceptionHandler(40,e)
		return devIDs

####-------------------------------------------------------------------------####
	def fillInputs(self, data, devs):
		try:
			if "inputs" not in data: return
			devNo = 0
			dts = datetime.datetime.now().strftime(_defaultDateStampFormat)
			for input in data["inputs"]:
				if len(devs) < devNo+1: continue
				try: devIDs = str(devs[devNo].id)
				except:
					self.indiLOG.log(40,u"fillInputs, devNo:{}, len(devs):{}, data {} ".format(devNo,len(devs), data))
					continue

				inp = "no"
				useInput = False
				usesInputForOnOff = False
				if "input" in input:
					if   str(input["input"]) == "1": inp = "on"
					else:							 inp = "off"
					if "input" in devs[devNo].states:	
						useInput = True
						self.addToStatesUpdateDict(devIDs, "input", inp)
						props = devs[devNo].pluginProps 
						if "usesInputForOnOff" in props and props["usesInputForOnOff"]: 
							self.addToStatesUpdateDict(devIDs, "onOffState", inp == "on")
							usesInputForOnOff = True

					if "input_"+str(devNo+1) in devs[devNo].states:	 
						self.addToStatesUpdateDict(devIDs, "input_"+str(devNo+1),	inp)
					#self.indiLOG.log(10,u"fillInputs, input: devIDs:{};   inp:{}".format(devIDs, inp) )

				if "lastEvent" in devs[devNo].states: lastEvent = devs[devNo].states["lastEvent"]
				else: lastEvent = ""

				if "event" in input and ( not useInput or (useInput and inp == "on") or usesInputForOnOff ):
					for xxx in [["input_short","S","short"], ["input_short_double","SS","short_double"], ["input_short_tripple","SSS","short_tripple"], ["input_long","L","long"], ["input_long_short","LS","long_short"], ["input_short_long","SL","short_long"]]:
						if input["event"] == xxx[1]  and xxx[0] in devs[devNo].states: 
							self.addToStatesUpdateDict(devIDs, xxx[0], dts)
							if "lastEvent" in devs[devNo].states: self.addToStatesUpdateDict(devIDs, "lastEvent",xxx[2]  )
							#self.indiLOG.log(10,u"fillInputs,event: devIDs:{};   xxx:{}".format(devIDs, xxx) )
							lastEvent = xxx[1]

				if "event_cnt" in input	and  "event_cnt" in devs[devNo].states: 
					uiText = str(input["event_cnt"])
					if lastEvent != "":
						props = devs[devNo].pluginProps
						if "displaySelect" in props:
							if props["displaySelect"] == "event_cnt":
								uiText = "last_Ev#:"+uiText+"-Type:"+lastEvent
					#self.indiLOG.log(10,u"fillInputs, event_cnt: devIDs:{};   evc:{}, uiValue:{}".format(devIDs, input["event_cnt"],uiText) )
					self.addToStatesUpdateDict(devIDs, "event_cnt", input["event_cnt"], uiValue=uiText)
				devNo += 1

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"data {} ".format(data))
		return 


####-------------------------------------------------------------------------####
	def fillRelays(self,  data, devs):
		try:
			if "relays" not in data: return
			devNo = 0
			for relay in data["relays"]:
				if "ison" in relay:												self.fillSwitch(devs[devNo], relay, "ison")
				if "overPower" in devs[devNo].states and "overpower" in relay:		self.addToStatesUpdateDict(str(devs[devNo].id), "overPower", relay["overpower"])
				devNo += 1


		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"data {} ".format(data))
		return 


####-------------------------------------------------------------------------####
	def fillRollers(self,  data, devs):
		try:
			if "rollers" not in data: return
			devNo = 0
			for roller in data["rollers"]:
				dev = devs[devNo]
				devId = str(dev.id)
				if "positioning" in dev.states and "positioning" in roller:			self.addToStatesUpdateDict(devId, "positioning", roller["positioning"])
				if "calibrating" in dev.states and "calibrating" in roller:			self.addToStatesUpdateDict(devId, "calibrating", roller["calibrating"])
				if "current_pos" in dev.states and "current_pos" in roller:
																					position = int(roller["current_pos"])
																					self.addToStatesUpdateDict(devId, "current_pos", position)
																					self.addToStatesUpdateDict(devId, "brightnessLevel", position, uiValue="{:d}%".format(position))
				if "last_direction" in dev.states and "last_direction" in roller:	self.addToStatesUpdateDict(devId, "last_direction", roller["last_direction"])
				if "stop_reason"    in dev.states and "stop_reason" in roller:		self.addToStatesUpdateDict(devId, "stop_reason", roller["stop_reason"])
				if "safety_switch"  in dev.states and "safety_switch" in roller:	self.addToStatesUpdateDict(devId, "safety_switch", roller["safety_switch"])
				if "state" 			in dev.states and "state" in roller:
																					self.addToStatesUpdateDict(devId, "state", roller["state"])
																					if   roller["state"] == "open" : self.fillSwitch( dev, {"onOffState":True},  "onOffState")
																					elif roller["state"] == "close": self.fillSwitch( dev, {"onOffState":False}, "onOffState")
				if "power" 	in roller and	"power"	in dev.states:					self.addToStatesUpdateDict(dev.id, "power",  round(roller["power"],self.powerDigits), 	 uiValue="{:.{}f}[W]".format(roller["power"],self.powerDigits), 		decimalPlaces=self.powerDigits)
				devNo += 1

# settings:[{"maxtime":10.00,"maxtime_open":10.00,"maxtime_close":10.00,"default_state":"stop","swap":false,"swap_inputs":false,"input_mode":"openclose","button_type":"toggle","btn_reverse":0,"state":"stop","power":0.00,"is_valid":false,"safety_switch":false,"roller_open_url":"http://192.168.1.50:7987/?roller=open","roller_close_url":"http://192.168.1.50:7987/?roller=close","roller_stop_url":"http://192.168.1.50:7987/?roller=stop","schedule":false,"schedule_rules":[],"obstacle_mode":"disabled","obstacle_action":"stop","obstacle_power":200,"obstacle_delay":1,"safety_mode":"while_opening","safety_action":"stop","safety_allowed_on_trigger":"none","off_power":2,"positioning":true}]
# status [{"state":"stop","power":0.00,"is_valid":false,"safety_switch":false,"overtemperature":false,"stop_reason":"normal","last_direction":"open","current_pos":101,"calibrating":true,"positioning":true}],
		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"data {} ".format(data))
		return 


####-------------------------------------------------------------------------####
	def fillMeters(self,  data, devs):
		try:
			if "meters" not in data: return
			devNo = 0
			for meter in data["meters"]:
				if devNo > len(devs)-1: continue
				if "power" 	in meter and	"power"				in devs[devNo].states:	self.addToStatesUpdateDict(devs[devNo].id, "power", 		 round(meter["power"],self.powerDigits), 	 uiValue="{:.{}f}[W]".format(meter["power"],self.powerDigits), 		decimalPlaces=self.powerDigits)
				if "total"	in meter and	"energy" 			in devs[devNo].states:	self.addToStatesUpdateDict(devs[devNo].id, "energy", 		 round(meter["total"],self.energyDigits), 	 uiValue="{:.{}f}[Wmin]".format(meter["total"],self.energyDigits), 	decimalPlaces=self.energyDigits)
				if "energy" in meter and 	"energy" 			in devs[devNo].states:	self.addToStatesUpdateDict(devs[devNo].id, "energy", 		 round(meter["energy"],self.energyDigits), 	 uiValue="{:.{}f}[Wmin]".format(meter["total"],self.energyDigits), 	decimalPlaces=self.energyDigits)
				if "counters" in meter and	"energy_counters" 	in devs[devNo].states:	self.addToStatesUpdateDict(devs[devNo].id, "energy_counters",str(meter["counters"]).strip("[]"))					
				devNo += 1

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"data {} ".format(data))
		return 

####-------------------------------------------------------------------------####
	def filleMeters(self,  data, devs):
		try:
			if "emeters" not in data: return
			devNo = 1 	# this is for the child devices, ie shelly EM, start at dev#1
						# need to change indexs  other devices ie EM3 or it might just work .. as soon as I get one
			for emeter in data["emeters"]:
				if devNo > len(devs)-1: break
				##self.indiLOG.log(10,u"devNo {} , ndevs(:{};  dev:{}; emeter:{}".format(devNo, len(devs), devs[devNo].name, emeter))
				if "power" 	in emeter and "power" 			in devs[devNo].states:	self.addToStatesUpdateDict(devs[devNo].id, "power", 		 round(emeter["power"],self.powerDigits), 		uiValue="{:.{}f}[W]".format(emeter["power"],self.powerDigits), 					decimalPlaces=self.powerDigits)
				if "power" 	in emeter and "voltage" 		in devs[devNo].states:	self.addToStatesUpdateDict(devs[devNo].id, "voltage", 		 round(emeter["voltage"],self.voltageDigits), 	uiValue="{:.{}f}[V]".format(emeter["voltage"],self.voltageDigits), 				decimalPlaces=self.voltageDigits)
				if "power" 	in emeter and "current" 		in devs[devNo].states:	self.addToStatesUpdateDict(devs[devNo].id, "current", 		 round(emeter["current"],self.currentDigits), 	uiValue="{:.{}f}[A]".format(emeter["current"],self.currentDigits), 				decimalPlaces=self.currentDigits)
				if "reactive" in emeter and "reactive" 		in devs[devNo].states:	self.addToStatesUpdateDict(devs[devNo].id, "reactive", 		 round(emeter["reactive"],self.energyDigits), 	uiValue="{:.{}f}[Wmin]".format(emeter["reactive"],self.energyDigits), 			decimalPlaces=self.energyDigits)
				if "total" 	in emeter and "energy" 			in devs[devNo].states:	self.addToStatesUpdateDict(devs[devNo].id, "energy", 		 round(emeter["total"],self.energyDigits), 		uiValue="{:.{}f}[Wmin]".format(emeter["total"],self.energyDigits), 				decimalPlaces=self.energyDigits)
				if "total_returned" in emeter and "energyReturned" in devs[devNo].states:	
																					self.addToStatesUpdateDict(devs[devNo].id, "energyReturned", round(emeter["total_returned"],self.energyDigits), uiValue="{:.{}f}[Wmin]".format(emeter["total_returned"],self.energyDigits),	decimalPlaces=self.energyDigits)
				if emeter["is_valid"] and emeter["power"] != 0:
																					self.addToStatesUpdateDict(devs[devNo].id, "onOffState", True)
																					devs[devNo].updateStateImageOnServer(indigo.kStateImageSel.PowerOn)
				if not emeter["is_valid"] or emeter["power"] == 0:
																					self.addToStatesUpdateDict(devs[devNo].id, "onOffState", False)
																					devs[devNo].updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
				devNo += 1

		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"data {} ".format(data))
		return 




###-------------------------------------------------------------------------####
	def fillSwitch(self, dev, data, token, onOffState=True):
		try:
			if onOffState and "onOffState" in dev.states:
				if data[token]: 
					self.addToStatesUpdateDict(dev.id, "onOffState",True)
					if not dev.states["onOffState"]:
						if "lastOnOffChange" in dev.states and "lastStatusChange" in dev.states:
							self.addToStatesUpdateDict(dev.id, "lastOnOffChange",dev.states["lastStatusChange"])
						self.addToStatesUpdateDict(dev.id, "lastStatusChange",datetime.datetime.now().strftime(_defaultDateStampFormat))
					dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOn)
				else:
					self.addToStatesUpdateDict(dev.id, "onOffState",False)
					if dev.states["onOffState"]:
						if "lastOnOffChange" in dev.states and "lastStatusChange" in dev.states:
							self.addToStatesUpdateDict(dev.id, "lastOnOffChange",dev.states["lastStatusChange"])
						self.addToStatesUpdateDict(dev.id, "lastStatusChange",datetime.datetime.now().strftime(_defaultDateStampFormat))
					dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
			else:
					self.addToStatesUpdateDict(dev.id, token, data[token])
	
		except Exception as e:
			self.exceptionHandler(40,e)
		return 


####-------------------------------------------------------------------------####
	def fillSensor(self, dev, data, token, state):
		try:
			### we can get:
			### :{u'tF': 72.84, u'tC': 22.69}
			### :{u'value': 72.84,... 

			if token not in data: 		return dev
			props = dev.pluginProps
			#if dev.id == 1570076651:self.indiLOG.log(10,u":::::fillSensor  {}  data:{}, token:{}, state:{}".format( dev.id , data, token,  state ))

			decimalPlaces = ""
			internal = ""
			unit = ""
			if state.split("_internal")[0] in dev.states or state+"_internal" in dev.states:
				
				#if dev.id == 1570076651:self.indiLOG.log(10,u":::::fillSensor  passed 1")
				devUnits = self.tempUnits
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
							self.indiLOG.log(40,u"fillSensor error  token:{}, data:{} ".format(token, data, dev.name ))
							return dev

				#self.indiLOG.log(10,u"fillSensor token:{}, data:{} T:{} {}".format(token, data, x , dev.name ))
				if state.find("Temperature") > -1:
					#if dev.id == 446084418:self.indiLOG.log(10,u":::::fillSensor  passed 2")
					decimalPlaces = self.tempDigits
					try:
						devUnits = self.SHELLY[dev.id]["tempUnits"]
						if token in data:
							if "units" in data[token]:
								devUnits = data[token]["units"]
								if self.SHELLY[dev.id]["tempUnits"] != data["units"]:
									props["tempUnits"] = data[token]["units"]
									dev.replacePluginPropsOnServer(props)
									dev = indigo.devices[dev.id]
									self.SHELLY[dev.id]["tempUnits"] = data["token"]["units"]
					except: pass	
					x1 , xui = self.convTemp(x, devUnits)
					#self.indiLOG.log(10,u"fillSensor x:{}, x1:{}, xui:{}, devUnits:{}, tempUnits:{}".format(x , x1, xui, devUnits, self.tempUnits ))
					x = x1
					if "Temperature" in dev.states:
						self.addToStatesUpdateDict(str(dev.id), "Temperature", x, uiValue=xui, decimalPlaces=decimalPlaces)
						if "displaySelect" in props and props["displaySelect"] == "Temperature":
							dev.updateStateImageOnServer(indigo.kStateImageSel.TemperatureSensorOn)
						self.fillMinMaxSensors(dev,state,x,decimalPlaces=decimalPlaces)
					elif "Temperature_internal" in dev.states:
						self.addToStatesUpdateDict(str(dev.id), "Temperature_internal", x, uiValue=xui, decimalPlaces=decimalPlaces)
					return dev

				elif state == "Humidity":
					if state in dev.states:
						x , xui = self.convHum(x)
						self.addToStatesUpdateDict(str(int(dev.id)), state, x, uiValue=xui, decimalPlaces=0)
						if "displaySelect" in props and props["displaySelect"] == "Humidity":
							dev.updateStateImageOnServer(indigo.kStateImageSel.HumiditySensorOn)
						self.fillMinMaxSensors(dev,"Humidity",x,decimalPlaces=0)

				else:
					pass


		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u" token:{}, data:{}".format(token, data ))
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
	def convTemp(self, temp, devUnits):
		try:
			suff=""
			useFormat="{:.1f}"
			temp = float(temp)
			if temp == 999.9:
				return 999.9,"badSensor", 1
			if self.tempUnits == "F":
				suff = u"ºF"
				if devUnits == u"C":
					temp = temp * 9. / 5. + 32.
			if self.tempUnits == "C":
				suff = u"ºC"
				if devUnits == u"F":
					temp = (temp -32. ) *5./9.

			if self.tempDigits == 0:
				cString = "%d"
				useFormat ="{:d}"
			else:
				cString = "%."+unicode(self.tempDigits)+"f"
			uiValue = (cString % temp).strip()+suff
			#self.indiLOG.log(10,u"convTemp temp:{}, devUnits:{} ui:{}".format(temp, devUnits , uiValue ))
			return round(temp,self.tempDigits) , uiValue 
		except Exception as e:
			self.exceptionHandler(40,e)
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
										if (float(dev.states[ttx+u"MaxToday"]) == float(dev.states[ttx+u"MinToday"]) and float(dev.states[ttx+u"MaxToday"]) == 0.) :	 reset = True
									except: pass
								if reset:
									self.addToStatesUpdateDict(dev.id,ttx+u"MaxYesterday",  val,decimalPlaces=decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MinYesterday",  val,decimalPlaces=decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MaxToday",		val,decimalPlaces=decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MinToday",		val,decimalPlaces=decimalPlaces)

							elif nHour ==0:	 # update at midnight 
									self.addToStatesUpdateDict(dev.id,ttx+u"MaxYesterday",  dev.states[ttx+u"MaxToday"], decimalPlaces = decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MinYesterday",  dev.states[ttx+u"MinToday"], decimalPlaces = decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MaxToday",		dev.states[ttx], decimalPlaces = decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MinToday",		dev.states[ttx], decimalPlaces = decimalPlaces)
			self.executeUpdateStatesDict()

		except Exception as e:
			self.exceptionHandler(40,e)
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
		except Exception as e:
			self.exceptionHandler(40,e)
		return

#



####------------------shelly poller queue management ----------------------------START
####------------------shelly poller queue management ----------------------------START
####------------------shelly poller queue management ----------------------------START


####-------------------------------------------------------------------------####
	def addToShellyPollerQueue(self, shellyIndigoDevNumber, page, now=False, getStatusDelay=0):
		try:
			if self.SHELLY[shellyIndigoDevNumber]["isChild"]: return
			if self.SHELLY[shellyIndigoDevNumber]["state"] != "running":
				self.startShellyDevicePoller("start", shellySelect=shellyIndigoDevNumber)
				time.sleep(0.1)
			try: 
				self.SHELLY[shellyIndigoDevNumber]["now"] = now	
				if getStatusDelay >0: self.SHELLY[shellyIndigoDevNumber]["getStatusDelay"] = getStatusDelay	
				self.SHELLY[shellyIndigoDevNumber]["queue"].put(page)
				if self.decideMyLog(u"Polling"): self.indiLOG.log(10,u"addToShellyPollerQueue ip#:{}; page:{}; now:{};  getStatusDelay:{}".format(self.SHELLY[shellyIndigoDevNumber]["ipNumber"], page, now, time.time()-self.SHELLY[shellyIndigoDevNumber]["getStatusDelay"]))
			except Exception as e:
				self.exceptionHandler(40,e)
				self.indiLOG.log(10,u"addToShellyPollerQueue error for  devid:{} in shelly:{}".format(shellyIndigoDevNumber,self.SHELLY[shellyIndigoDevNumber]))

			#self.indiLOG.log(10,u"addToShellyPollerQueue added devid:{} page:{} to queue:{}".format(shellyIndigoDevNumber, page, list(self.SHELLY[shellyIndigoDevNumber]["queue"].queue)))
		except Exception as e:
			self.exceptionHandler(40,e)
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
					except Exception as e:
						self.exceptionHandler(40,e)
						self.indiLOG.log(40,u"shellyIndigoDevNumber:{};  SHELLY:{}".format(shellyIndigoDevNumber, self.SHELLY))
						continue

					if shellySelect == "all" or shellyIndigoDevNumber == shellySelect:
							if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10, u"starting UpdateshellyQueues for devId:{} ".format(shellyIndigoDevNumber) )
							if self.SHELLY[shellyIndigoDevNumber]["state"] != "running":
								self.startOneShellyDevicePoller(shellyIndigoDevNumber)

			elif state == "restart":
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
								self.indiLOG.log(10, u"re - starting UpdateshellyQueues for devId:{} ".format(shellySelect) )
								self.startOneShellyDevicePoller(shellyIndigoDevNumber, reason="not running")
		except Exception as e:
			self.exceptionHandler(40,e)
			self.indiLOG.log(40,u"self.SHELLY:{}".format(self.SHELLY))
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
					self.indiLOG.log(10, u"no  {} is not in indigo devices, need to create first".format(shellyIndigoDevNumber) )
					return 
			
			if self.SHELLY[shellyIndigoDevNumber]["state"] == "running":
					if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10, u"no need to start Thread, ipnumber {} thread already running".format(self.SHELLY[shellyIndigoDevNumber]["ipNumber"]) )
					return 

			if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10, u".. (re)starting   thread for ipnumber:{}, state was: {}; reason:{}".format(self.SHELLY[shellyIndigoDevNumber]["ipNumber"], self.SHELLY[shellyIndigoDevNumber]["state"], reason) )
			self.SHELLY[shellyIndigoDevNumber]["lastCheck"]= time.time()
			self.SHELLY[shellyIndigoDevNumber]["state"]	= "start"
			self.SHELLY[shellyIndigoDevNumber]["thread"] = threading.Thread(name=u'self.shellyPollerThread', target=self.shellyPollerThread, args=(shellyIndigoDevNumber,))
			self.SHELLY[shellyIndigoDevNumber]["thread"].start()

			self.SHELLY[shellyIndigoDevNumber]["pushIdActive"]	= "empty"
			self.SHELLY[shellyIndigoDevNumber]["pushstate"]	= "start"
			self.SHELLY[shellyIndigoDevNumber]["pushthread"] = threading.Thread(name=u'self.pushThreadLoop', target=self.pushThreadLoop, args=(shellyIndigoDevNumber,))
			self.SHELLY[shellyIndigoDevNumber]["pushthread"].start()
			time.sleep(0.2) # give other procs time to finish
		except Exception as e:
			self.exceptionHandler(40,e)
		return 
###-------------------------------------------------------------------------####
	def stopShellyDevicePoller(self, shellySelect="all"):
		if shellySelect != "all":
			if shellySelect in self.SHELLY:
				if self.SHELLY[shellySelect]["state"] == "running":
					self.indiLOG.log(10, u"stopping Thread, ipnumber {}, devId:{}".format(self.SHELLY[shellySelect]["ipNumber"], shellySelect) )
					self.stopOneShellyDevicePoller(shellySelect, reason="")
					return 
		else:
			for shellyIndigoDevNumber in self.SHELLY:
				self.stopOneShellyDevicePoller(shellyIndigoDevNumber, reason="")
		return 
###-------------------------------------------------------------------------####
	def stopOneShellyDevicePoller(self, shellyIndigoDevNumber, reason=""):
		if shellyIndigoDevNumber in self.SHELLY:
			self.SHELLY[shellyIndigoDevNumber]["state"]		= "stop "+reason
			self.SHELLY[shellyIndigoDevNumber]["pushstate"]	= "stop "+reason
			self.SHELLY[shellyIndigoDevNumber]["reset"]		= True
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
			if self.decideMyLog(u"Polling"): self.indiLOG.log(10, u"shellyPollerThread starting  for devId:{}; ipnumber# {}, threadNumber:{}".format(shellyIndigoDevNumber, self.SHELLY[shellyIndigoDevNumber]["ipNumber"], threadNumber) )
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
					if shellyIndigoDevNumber !=0: self.indiLOG.log(10, u"shellyPollerThread stopping due to other thread running  for devId:{}; ipnumber# {}".format(shellyIndigoDevNumber, self.SHELLY[shellyIndigoDevNumber]["ipNumber"]) )
					break
				addBack =[]
				ipNumber = self.SHELLY[shellyIndigoDevNumber]["ipNumber"]

				waitStart = time.time()
				for ii in range(1000):
					if time.time() - waitStart > 0.2 + retryTime: break
					time.sleep(0.2 + retryTime)
					try:
						if ipNumber != self.SHELLY[shellyIndigoDevNumber]["ipNumber"]:
							self.indiLOG.log(10, u"shellyPollerThread changed IPnumber:{}, continuing w new IP#{};  devId:{}}".format(ipNumber, self.SHELLY[shellyIndigoDevNumber]["ipNumber"], shellyIndigoDevNumber) )
							ipNumber = self.SHELLY[shellyIndigoDevNumber]["ipNumber"]
							break
					except: 
						# this device has been removed, exit thread
						if shellyIndigoDevNumber not in self.SHELLY:
							break 
					if self.SHELLY[shellyIndigoDevNumber]["now"]: 
						lastDefaultRequestTime = -10
						####self.indiLOG.log(10, u"shellyPollerThread now: true   ipnumber# {}".format( self.SHELLY[shellyIndigoDevNumber]["ipNumber"]) )
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
					if self.SHELLY[shellyIndigoDevNumber]["lastSuccessfullConfigPush"]["all"] > 0 and time.time() - self.SHELLY[shellyIndigoDevNumber]["lastSuccessfullConfigPush"]["all"] < self.repeatConfigPush:
						pollingFrequency = _emptyProps[self.SHELLY[shellyIndigoDevNumber]["devTypeId"]]["props"]["automaticPollingFrequency"]

					

				while not self.SHELLY[shellyIndigoDevNumber]["queue"].empty() or (time.time() - lastDefaultRequestTime) > pollingFrequency:
					self.SHELLY[shellyIndigoDevNumber]["lastActive"] = time.time()

					if lastDefaultRequestTime < 0: # this is a now request for status
						lastDefaultRequestTime = 1
						page = defaultTask
						fromQueue = False
						lastDefaultRequestTime = time.time()
						
					else:
						if not self.SHELLY[shellyIndigoDevNumber]["queue"].empty(): 
								page = self.SHELLY[shellyIndigoDevNumber]["queue"].get()
								fromQueue = True
						else:
								page = defaultTask
								fromQueue = False
						lastDefaultRequestTime = time.time()

					if page == "status" and time.time() - self.SHELLY[shellyIndigoDevNumber]["getStatusDelay"] < 0: 
						lastDefaultRequestTime = max( time.time()-pollingFrequency, self.SHELLY[shellyIndigoDevNumber]["getStatusDelay"]-pollingFrequency )
						continue


					lastEXE = time.time()

					if not self.SHELLY[shellyIndigoDevNumber][u"deviceEnabled"]: 		
						self.SHELLY[shellyIndigoDevNumber]["reset"]= True
						break


					if self.SHELLY[shellyIndigoDevNumber][u"ipNumber"] == "": 	
						continue

					if self.SHELLY[shellyIndigoDevNumber]["reset"]: 
						continue

					#if self.decideMyLog(u"Polling"): self.indiLOG.log(10, u" send to ipNumber:{}  page:{}".format(ipNumber, page) )
					jData , retCode = self.execShellySend(ipNumber, page)
					#if self.decideMyLog(u"Polling"): self.indiLOG.log(10, "ret page:{}; json:{}".format(page,jData) )

					if retCode == "0": # all ok?
						self.addtoAnalyzePollerQueue({"shellyIndigoDevNumber":shellyIndigoDevNumber,"page":page,"ipNumber":ipNumber,"data": jData})
						if shellyIndigoDevNumber == 0: 
							self.SHELLY[shellyIndigoDevNumber]["ipNumber"] = ""
						tries      = 0
						retryTime  = 0
						continue

					else: # no response, retry ..
						tries      +=1
						retryTime  = 2

						if tries  > 2 and tries <=20: # wait a little longer
							if self.decideMyLog(u"Polling"): self.indiLOG.log(10, u"shellyPollerThread last querry were not successful wait, then try again; ip:{}".format(ipNumber))
							retryTime = tries+4

						if tries  > 20:
							if self.decideMyLog(u"Polling"): self.indiLOG.log(10, u"shellyPollerThread last querry were not successful  skip; ip:{}".format(ipNumber))
							retryTime = 20
							break

						if fromQueue: addBack.append(page)
					if shellyIndigoDevNumber not in self.SHELLY: break

				try: 	self.SHELLY[shellyIndigoDevNumber]["queue"].task_done()
				except: pass
				if addBack !=[]:
					for nxt in addBack:
						self.SHELLY[shellyIndigoDevNumber]["queue"].put(nxt)
				self.SHELLY[shellyIndigoDevNumber]["reset"]=False

		except Exception as e:
			if unicode(e).find("None") == -1:
				self.indiLOG.log(10,u"Line {} has error={}".format(sys.exc_info()[2].tb_lineno, e))
		try: 
			if shellyIndigoDevNumber != 0: self.indiLOG.log(10, u"shellyPollerThread: ip#:{}  devId:{}; update thread stopped".format(ipNumber, shellyIndigoDevNumber) )
		except: pass
		return



####-------------------------------------------------------------------------####
	def execShellySend(self,  ipNumber, page, timeoutMax=10):
		ret = ""
		try:
			self.lastUpdateSend = time.time()

			pingR = self.testPing(ipNumber)
			if pingR != 0:
				if self.decideMyLog(u"Ping") : self.indiLOG.log(10,u" ipnumber{}  does not answer ping - , skipping update".format(ipNumber) )
				return  "ping offline", "pingOffline, timeout"
	
			#if self.decideMyLog(u"Polling"): self.indiLOG.log(10, u"execShellySend  send to ipNumber:{}  page:{}".format(ipNumber, page) )
			retJson,  err = self.getJsonFromDevices(ipNumber, page, timeoutMax=timeoutMax)
			return  retJson, err

		except Exception as e:
			if unicode(e).find("None") == -1:
				self.exceptionHandler(40,e)
		return  ret, "err"


####-------------------------------------------------------------------------####
	def testPing(self, ipN):
		try:
			ss = time.time()
			ret = subprocess.call(u"/sbin/ping  -c 1 -W 40 -o " + ipN, shell=True) # send max 2 packets, wait 40 msec   if one gets back stop
			if self.decideMyLog(u"Ping"): self.indiLOG.log(10, u" sbin/ping  -c 1 -W 40 -o {}  ret-code: {}".format(ipN, ret) )

			if int(ret) ==0:  return 0
			self.sleep(0.1)
			ret = subprocess.call(u"/sbin/ping  -c 1 -W 400 -o " + ipN, shell=True)
			if self.decideMyLog(u"Ping"): self.indiLOG.log(10, "/sbin/ping  -c 1 -W 400 -o {} ret-code: {}".format(ipN, ret) )

			#indigo.server.log(  ipN+"-2  "+ unicode(ret) +"  "+ unicode(time.time() - ss)  )

			if int(ret) == 0:  return 0
			return 1
		except Exception as e:
			if unicode(e).find("None") == -1:
				self.exceptionHandler(40,e)

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
			if self.decideMyLog(u"Actions"): self.indiLOG.log(10,u"sending to dev {} page={}".format(dev.name, page))
			time.sleep(0.2)
			self.addToShellyPollerQueue( queueID, page)
			page = "status"
			if self.decideMyLog(u"Actions"): self.indiLOG.log(10,u"sending to dev {} page={}".format(dev.name, page))
			self.addToShellyPollerQueue( queueID, page)
			return
		except Exception as e:
			self.exceptionHandler(40,e)
		return




	####-----------------
	########################################
	# shell 25 roller calibration, stop go_pos
	######################
####-------------------------------------------------------------------------####
	def startShelly25CalibrationCALLBACKaction(self, action1=None, typeId="", devId=0):
		valuesDict = action1.props
		self.startShelly25CalibrationCALLBACKmenu(valuesDict)
		return
####-------------------------------------------------------------------------####
	def startShelly25CalibrationCALLBACKmenu(self, valuesDict, typeId=""):
		page 	= "roller/0/calibrate"
		queueID	= int(valuesDict["devId"])
		if self.decideMyLog(u"Actions"): self.indiLOG.log(10,u"ACTIONS: dev {} sending   page:{}".format(queueID, page))
		self.addToShellyPollerQueue( queueID, page, now=True)
		self.deviceActionList.append({"devId":int(queueID),"action":"checkStatus","notBefore":time.time() + 20})
		return

####-------------------------------------------------------------------------####
	def startShelly25StopCALLBACKaction(self, action1=None, typeId="", devId=0):
		valuesDict = action1.props
		self.startShelly25StopCALLBACKmenu(valuesDict)
		return
####-------------------------------------------------------------------------####
	def startShelly25StopCALLBACKmenu(self, valuesDict, typeId=""):
		page 	= "roller/0/?go=stop"
		queueID	= int(valuesDict["devId"])
		if self.decideMyLog(u"Actions"): self.indiLOG.log(10,u"ACTIONS: dev {} sending   page:{}".format(queueID, page))
		self.addToShellyPollerQueue( queueID, page, now=True)
		self.deviceActionList.append({"devId":int(queueID),"action":"checkStatus","notBefore":time.time() + 20})
		return

####-------------------------------------------------------------------------####
	def startShelly25roller_posCALLBACKaction(self, action1=None, typeId="", devId=0):
		valuesDict = action1.props
		self.startShelly25roller_posCALLBACKmenu(valuesDict)
		return
####-------------------------------------------------------------------------####
	def startShelly25roller_posCALLBACKmenu(self, valuesDict, typeId=""):
		page 	= "roller/0/?go=to_pos&roller_pos="+valuesDict["roller_pos"]
		queueID	= int(valuesDict["devId"])
		if self.decideMyLog(u"Actions"): self.indiLOG.log(10,u"ACTIONS: dev {} sending   page:{}".format(queueID, page))
		self.addToShellyPollerQueue( queueID, page, now=True)
		self.deviceActionList.append({"devId":int(queueID),"action":"checkStatus","notBefore":time.time() + 20})
		return

####-------------------------------------------------------------------------####
	def startShelly25roller_poswTimerCALLBACKaction(self, action1=None, typeId="", devId=0):
		valuesDict = action1.props
		self.startShelly25roller_poswTimerCALLBACKmenu(valuesDict)
		return
####-------------------------------------------------------------------------####
	def startShelly25roller_poswTimerCALLBACKmenu(self, valuesDict, typeId=""):
		page 	= "roller/0/?go="+valuesDict["direction"]+"&duration="+valuesDict["duration"]
		queueID	= int(valuesDict["devId"])
		if self.decideMyLog(u"Actions"): self.indiLOG.log(10,u"ACTIONS: dev {} sending   page:{}".format(queueID, page))
		self.addToShellyPollerQueue( queueID, page, now=True)
		self.deviceActionList.append({"devId":int(queueID),"action":"checkStatus","notBefore":time.time() + 20})

		return

####-------------------------------------------------------------------------####
	def gasAlarmSetCALLBACKaction(self, action1=None, typeId="", devId=0):
		valuesDict = action1.props
		self.gasAlarmSetCALLBACKmenu(valuesDict)
		return

####-------------------------------------------------------------------------####
	def gasAlarmSetCALLBACKmenu(self, valuesDict, typeId=""):

		checkStatusTime = time.time() + 20
		if  valuesDict["action"] in ["self_test", "mute", "unmute"]:
			queueID	= int(valuesDict["devId"])
			page = valuesDict["action"]
			if self.decideMyLog(u"Actions"): self.indiLOG.log(10,u"ACTIONS: dev {} sending   page:{}".format(queueID, page))
			self.addToShellyPollerQueue( queueID, page, now=True)
			self.deviceActionList.append({"devId":queueID,"action":"checkStatus","notBefore":time.time()+ 20})
			if page.find("test") >-1:
				self.SHELLY[queueID]["self_test_state"] 	= time.time()
				self.SHELLY[queueID]["pollingFrequency"]	= 10	

		return 

####-------------------------------------------------------------------------####
	def actionControlGeneral(self, action, dev):
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
			if self.decideMyLog(u"Actions"): self.indiLOG.log(10,u"ACTIONS:  {}; --  action=\n{}".format(dev.name, action))

			props = dev.pluginProps
			if props["isChild"]: queueID = int(props["parentIndigoId"])
			else:				 queueID = dev.id


			setAction = False
			actionValues ={}
			IndigoStateMapToShellyDev ={'redLevel':"red", 'greenLevel':"green", 'blueLevel':"blue", 'whiteLevel':"white", "brightnessLevel":"brightness", "whiteTemperature":"temp","TurnOff":"turn","TurnOn":"turn"}
			IndigoStateMapToShellyDev['self_test'] = "self_test"
			IndigoStateMapToShellyDev['mute'] = "mute"
			IndigoStateMapToShellyDev['unmute'] = "unmute"

			page 	  = ""
			extraPage = ""
			checkStatusTime = -1

			try: 	WhiteTemperatureMin = _emptyProps[dev.deviceTypeId]["WhiteTemperatureMin"]
			except:	WhiteTemperatureMin = 1000
			try: 	WhiteTemperatureMax = _emptyProps[dev.deviceTypeId]["WhiteTemperatureMax"]
			except:	WhiteTemperatureMax = 9000
			try:	rgbLimits = _emptyProps[dev.deviceTypeId]["rgbLimits"]
			except:	rgbLimits = [0,0]

			setThermometer = {}



			if "redLevel" in dev.states or "brightnessLevel" in dev.states or  "whiteLevel" in dev.states:
				if action.deviceAction == indigo.kDeviceAction.SetColorLevels:
					actionValues = action.actionValue
					setAction = True

				setThermometer["lights"] = [{}]



				if dev.deviceTypeId in ["shellydimmer","ShellyVintage","ShellyBulbDuo"]:	channel = "white"
				elif "mode" in dev.states:													channel = dev.states["mode"] # == white or color
				else:																		channel = "white" 
				
				if "redLevel" in actionValues: 												channel = "color"
				elif "greenLevel" in actionValues: 											channel = "color"
				elif "blueLevel" in actionValues: 											channel = "color"
				elif "whiteLevel" in actionValues: 											channel = "white"

				setThermometer["lights"][0]["mode"] = channel

				if "onOffState" in dev.states:
					if dev.states["onOffState"]: onOffState = 1
					else: 						 onOffState = -1
				else:							 onOffState = 0



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
						if dev.states["onOffState"]: 	actionValues["TurnOff"] = "off"
						else: 							actionValues["TurnOn"] 	= "on"
						setAction = True

					###### SET BRIGHTNESS ######
				if action.deviceAction == indigo.kDimmerRelayAction.SetBrightness:
					if channel == "color":
						actionValues["redLevel"] 	= action.actionValue
						actionValues["greenLevel"] 	= action.actionValue
						actionValues["blueLevel"] 	= action.actionValue
						actionValues["whiteLevel"] 	= 0
					else:
						actionValues["brightnessLevel"] 	= max(0,action.actionValue)
						if "whiteLevel" in actionValues: del actionValues["whiteLevel"]
					setAction = True

					###### set Color level ######
				if action.deviceAction == indigo.kDimmerRelayAction.SetColorLevels:
					if channel == "color":
						actionValues["redLevel"] 	= int(actionValues["redLevel"])
						actionValues["greenLevel"] 	= int(actionValues["greenLevel"])
						actionValues["blueLevel"] 	= int(actionValues["blueLevel"])
						if "whiteLevel" in actionValues: del actionValues["whiteLevel"]
					else:
						if "whiteTemperature" in actionValues:
							actionValues["whiteTemperature"]	= actionValues["whiteTemperature"]
						if "whiteLevel" in actionValues:
							actionValues["brightnessLevel"]	= actionValues["whiteLevel"]
							del actionValues["whiteLevel"]
						try:
							del actionValues["redLevel"] 
							del actionValues["greenLevel"] 
							del actionValues["blueLevel"] 
						except: pass
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
						if "whiteLevel" in actionValues: del actionValues["whiteLevel"]
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

				# for non RGB devices: only use brightness not white level
				if "redLevel" not in dev.states and "whiteLevel" in actionValues: 
					del actionValues["whiteLevel"]

				if "channel" in dev.states and channel != dev.states["channel"]:
					extraPage = "settings/?mode={}".format(channel)

				if setAction:
						ison = False
						for colorAction in IndigoStateMapToShellyDev:	
							if colorAction in actionValues:
								if colorAction in ["TurnOff","TurnOn"]:
									if "TurnOff" in actionValues and actionValues["TurnOff"] == "off":
										ison = False
										page += "{}={}&".format("turn", "off")
									else:
										ison = True
										page += "{}={}&".format("turn", "on")
								else:
									if actionValues[colorAction] > 0 and not ison:
										ison = True
										page += "{}={}&".format("turn", "on")

									if True: # actionValues[colorAction] != dev.states[colorAction]:
										if colorAction == "whiteTemperature": # this requires to be in white channel
											page += "{}={}&".format(IndigoStateMapToShellyDev[colorAction], int(min(WhiteTemperatureMax,max(WhiteTemperatureMin,actionValues[colorAction]))))
											setThermometer["lights"][0]["temp"] = int(min(WhiteTemperatureMax,max(WhiteTemperatureMin,actionValues[colorAction])))
										elif colorAction == "whiteLevel":
											if actionValues[colorAction] ==0:
												ison = False
												page += "{}={}&".format("turn", "off")
											page += "{}={}&".format(IndigoStateMapToShellyDev[colorAction], int(min(rgbLimits[1],max(rgbLimits[0],actionValues[colorAction]*255/100.))))
											setThermometer["lights"][0]["white"] = int(min(rgbLimits[1],max(rgbLimits[0],actionValues[colorAction]*255/100.)))
										elif colorAction == "brightnessLevel":
											if actionValues[colorAction] ==0:
												ison = False
												page += "{}={}&".format("turn", "off")
											page += "{}={}&".format(IndigoStateMapToShellyDev[colorAction], int(min(100,         max(0,actionValues[colorAction]))))
											setThermometer["lights"][0]["brightness"] = actionValues[colorAction]
										else:
											page += "{}={}&".format(IndigoStateMapToShellyDev[colorAction], int(min(rgbLimits[1],max(rgbLimits[0],actionValues[colorAction]*255/100.))))
											setThermometer["lights"][0][IndigoStateMapToShellyDev[colorAction]] = int(min(rgbLimits[1],max(rgbLimits[0],actionValues[colorAction]*255/100.)))
						setThermometer["lights"][0]["ison"] = ison
						setThermometer["lights"][0]["mode"] = channel

				if "mode" in dev.states and channel != dev.states["mode"]:
					extraPage = "settings/?mode={}".format(channel)

			elif dev.deviceTypeId  == "shellyswitch25-roller":
				checkStatusTime = time.time() + 20
				channel = "roller"
				if   action.deviceAction == indigo.kDimmerRelayAction.TurnOn:
					page 	= "go=open"
				elif action.deviceAction == indigo.kDimmerRelayAction.TurnOff:
					page 	= "go=close"
				elif action.deviceAction == indigo.kDimmerRelayAction.Toggle:
					if "state" in dev.states:
						if dev.states["state"] == "close":	page 	= "go=open"
						else:								page 	= "go=close"
						setAction = True
				elif action.deviceAction == indigo.kDimmerRelayAction.SetBrightness:
					page 	= "go=to_pos&roller_pos="+str(max(0,min(100,int(action.actionValue))))

			elif dev.deviceTypeId in _relayDevices:
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
						if dev.states["onOffState"]: 	actionValues["TurnOff"] = "off"
						else: 							actionValues["TurnOn"] 	= "on"
						setAction = True

				if setAction:
						for thisAction in IndigoStateMapToShellyDev:	
							if thisAction in actionValues:
								page += "{}={}&".format("turn", actionValues[thisAction])



			elif dev.deviceTypeId.find("shellygas") !=-1:
				checkStatusTime = time.time() + 20
				page = ""
				if    action.deviceAction == "self_test": 	channel 	= "self_test"
				elif  action.deviceAction == "mute": 		channel 	= "mute"
				elif  action.deviceAction == "unmute": 		channel 	= "unmute"

			else:
				self.indiLOG.log(10,u"ACTION not implemented: {}  action:{}".format(dev.name, unicode(action) ))


			if len(page) > 0:

				if setThermometer != {}:
					#self.indiLOG.log(10,u"setThermometer  send: {}".format(setThermometer ))
					self.fillLight( setThermometer, dev)
					self.executeUpdateStatesDict()

				if extraPage != "":
					self.addToShellyPollerQueue( queueID, extraPage, now=True, getStatusDelay=time.time()+1)
					time.sleep(0.2)

				page = page.strip("&")
				page = _emptyProps[dev.deviceTypeId]["setPageActionPageOnShellyDev"][channel]+page			
				if self.decideMyLog(u"Actions"): self.indiLOG.log(10,u"ACTIONS: dev {} sending  channel:{};  page:{} deviceTypeId:{}".format(dev.name, channel, page, dev.deviceTypeId))
				if self.logStateChanges == u"all" or (self.logStateChanges == u"onOff" and ("turn" in page )):
					self.indiLOG.log(20,u'send "{}"  {}'.format(dev.name, page) )
				now = True if  setThermometer == {} else False
				getStatusDelay = 0 if  setThermometer == {} else time.time()+1
				self.addToShellyPollerQueue( queueID, page, now=True, getStatusDelay=getStatusDelay)
				if checkStatusTime > 0:
					self.deviceActionList.append({"devId":int(queueID),"action":"checkStatus","notBefore":checkStatusTime})

			else:
				self.indiLOG.log(10,u"ACTION not implemented: {}  action:{}".format(dev.name, unicode(action) ))
				return


			return
		except Exception as e:
			self.exceptionHandler(40,e)
		return


####-------------------------------------------------------------------------####
	def pushThreadLoop(self, devId):
		try:
			self.SHELLY[devId]["pushstate"] = "running"
			if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10, u"pushThreadLoop starting for devId:{}".format(devId))
			if devId not in self.SHELLY: return 

			while self.SHELLY[devId]["pushstate"] == "running":
				if devId not in indigo.devices: 
					self.sleep(20)
					if devId not in self.SHELLY: return 
					continue
				self.sleep(2)

				if self.SHELLY[devId]["pushIdActive"] == "new":
					self.SHELLY[devId]["pushIdActive"] = "active"
					if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10, u"pushThreadLoop adding devId: {} to execPush".format(devId))
					self.execPush(devId, delay = 0)
					self.SHELLY[devId]["pushIdActive"] = "waiting"

				if self.SHELLY[devId]["pushIdActive"] == "stop":
					self.SHELLY[devId]["pushIdActive"] = "waiting"

				if devId not in self.SHELLY: return 
				
			if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10, u"pushThreadLoop stopped ")
		except Exception as e:
			if unicode(e).find("None") == -1:
				self.exceptionHandler(40,e)
		return


####-------------------------------------------------------------------------####
	def addToPushConfigToShellyDeviceQueue(self, devId, delay = 0):
		try:
			if devId not in self.SHELLY: 	return
			dev = indigo.devices[int(devId)]
			if not dev.enabled: 			return 
			if self.SHELLY[devId]["pushIdActive"] in ["active","stop"]: 										
				if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10, u"addToPushConfigToShellyDeviceQueue devId:{} not adding, already in queue".format(devId))
				return 
			if time.time() - self.SHELLY[devId]["lastSuccessfullConfigPush"]["all"] < 200: 	
				if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10, u"addToPushConfigToShellyDeviceQueue devId:{} not adding, just finsihed {:.0f} secs ago".format(devId,time.time() - self.SHELLY[devId]["lastSuccessfullConfigPush"]["all"]))
				return 
			if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10, u"addToPushConfigToShellyDeviceQueue adding dev:{}".format(dev.name) )
			self.SHELLY[devId]["pushIdActive"] = "new"
				
		except Exception as e:
			if unicode(e).find("None") == -1:
				self.exceptionHandler(40,e)
		return

####-------------------------------------------------------------------------####
	def execPush(self, devId, delay = 0):
		try:
			if devId not in self.SHELLY: return
			self.sleep(delay) 
			dev = indigo.devices[int(devId)]
			if not dev.enabled: return 
			deviceTypeId 		= dev.deviceTypeId
			props 				= dev.pluginProps
			ipNumber 			= self.SHELLY[devId]["ipNumber"]
			port 				= self.portOfShellyDevices
			pushTried 			= False
			pushSuccessfull 	= False
			delayCounter 		= 0
			delayEveryx 		= 3
			SleepFor 			= 10
			sleepAfterTimeout 	= 63.
			retCode 			= "0"
			self.addToShellyPollerQueue(devId, "settings")
			self.sleep(1)
			if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10,u"addToPushConfigToShellyDeviceQueue starting for :{}, last pushes:{} ".format(dev.name, self.SHELLY[devId]["lastSuccessfullConfigPush"]) )
			if self.SHELLY[devId]["lastSuccessfullConfigPush"]["all"]  > 200: return  
			

			if "action_url" in _emptyProps[deviceTypeId]:  
					pageBack = "http://"+self.IndigoServerIPNumber+":"+str(self.portOfIndigoServer)
					actionURLs = _emptyProps[deviceTypeId]["action_url"][self.sensorApiVersion]

					existingActionSettings, retCode = self.execShellySend(ipNumber, _statusActionPage[self.sensorApiVersion], timeoutMax=10)
					currentActions = "" # unicode(currentActions)
					if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10,u"action actionURLs :{}\n exitings Actions:{}".format(actionURLs, existingActionSettings) )

					for parameter in actionURLs: # eg parameter = settings/actions?report_url="
						if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10,u"action parameter :{}<".format(parameter) )
						for setting in actionURLs[parameter]: 
							searchFor1 = actionURLs[parameter][setting]
							searchFor2 = pageBack

							## define page to be send to shelly device 
							# eg settings = "none"  ;actionURLs[parameter][setting] = "data?"
							if setting == "none":
								if searchFor1 in currentActions and searchFor2 in currentActions: 
									pushSuccessfull = True
									if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10,u"action already set: {};  >{}< >{}< ".format(dev.name, searchFor1, searchFor2) )
									break
								page = parameter+_urlPrefix[self.sensorApiVersion]+"="+pageBack +"/?"+ actionURLs[parameter][setting]
								###  = eg settings/?report_url=ttp://ip:port/data?"
							elif actionURLs[parameter][setting] == "disable":
								searchFor1 = parameter
								searchFor2 = "x"
								if searchFor1 in currentActions and searchFor2 in currentActions: 
									if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10,u"action already set: {};  >{}< >{}< ".format(dev.name, searchFor1, searchFor2) )
									pushSuccessfull = True
									break
								page = parameter +_urlPrefix[self.sensorApiVersion]+"="+ setting + "=x" 
								###  = eg settings/relay/0?shortpush_url="
							else:
								if searchFor1 in currentActions and searchFor2 in currentActions: 
									if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10,u"action already set: {};  >{}< >{}< ".format(dev.name, searchFor1, searchFor2) )
									self.SHELLY[devId]["lastSuccessfullConfigPush"][currentActions] = time.time()
									break
								page = parameter + setting + _urlPrefix[self.sensorApiVersion]+ "=" + pageBack +"/?"+ actionURLs[parameter][setting]
								###  = eg settings/relay/0?btn_on_url=http://ip:port/input=on"

							# allready done?
							if page not in self.SHELLY[devId]["lastSuccessfullConfigPush"]:
								self.SHELLY[devId]["lastSuccessfullConfigPush"][page] = -10 
							if self.SHELLY[devId]["lastSuccessfullConfigPush"][page] > 200: continue

							# if not try twice 
							for tries in range(2):
								if self.SHELLY[devId]["pushIdActive"] == "stop": 	return 
								if self.SHELLY[devId]["pushstate"]    != "running": return 
								delayCounter += 1
								if retCode != "0" and retCode.find("timeout") >-1: 
									if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10,u"delaying send by {} due to retcode {}".format(sleepAfterTimeout, retCode[0:50]) )
									for ii in range(int(sleepAfterTimeout)):
										if self.testPing(ipNumber) == 0: break
										self.sleep(0.5)
								elif delayCounter%delayEveryx == 0:
									if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10,u"delaying send by {} secs after {} sends".format(SleepFor, delayCounter) )
									self.sleep(SleepFor+delayCounter/5.)
								else:
									self.sleep(1.5)

								if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10,u"action setting tries:{}; :{}< parm[][]:{}< ".format(tries, setting,actionURLs[parameter][setting]) )
								searchFor1 = unicode(actionURLs[parameter][setting])
								searchFor2 = unicode(pageBack)



								if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10,u"{}, sending action page:{}".format(ipNumber, page) )
								pushTried = True
								jData, retCode = self.execShellySend(ipNumber, page, timeoutMax=2)
								udata = unicode(jData)
								s1 = udata.find(searchFor1) >-1
								s2 = udata.find(searchFor2) >-1
								if  not s1 or not s2: # not successfull
									if udata.find("offline") == -1:
										self.indiLOG.log(10,u"send action_url to devId:{},  search1:>>{}<< ok?:{}, search2:>>{}<< ok?:{}\nanswer not ok:>{}<".format(devId, searchFor1, s1, searchFor2, s2, udata) )
									continue
								else:
									self.indiLOG.log(10,u"send action_url to devId:{}\nanswer ok:>{}<".format(devId, udata) )
									self.SHELLY[devId]["lastSuccessfullConfigPush"][page] = time.time()

			retCode = "0"
			for prop in props:
				if prop.find("SENDTOSHELLYDEVICE-") > -1:
					if props[prop] == "none": break
					if prop not in _settingCmds: 
						self.indiLOG.log(30,u"props devId:{} , prop:{} not defined, check code".format(devId, prop) )
						break

					for tries in range(2):
						if self.SHELLY[devId]["pushIdActive"] == "stop": 	return 
						if self.SHELLY[devId]["pushstate"]   != "running":	return 
						self.indiLOG.log(10,u"props devId:{} , prop:{}, props[prop]:{}".format(devId, prop, props[prop]) )


						## remove tag then 
						##  replace -.- with / and QqQ with ?  ..  /? do not work in XML tag name
						## should be come something like:  settings/relay/1?btn_type=toggle

						cmd 			= _settingCmds[prop][0]
						setTo 			= props[prop]
						findItem 		= _settingCmds[prop][1]
						page 			= cmd + setTo
						if page not in self.SHELLY[devId]["lastSuccessfullConfigPush"]:
							self.SHELLY[devId]["lastSuccessfullConfigPush"][page]  = -10 

						delayCounter += 1
						if retCode != "0" and retCode.find("timeout") >-1: 
							if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10,u"delaying send by {} due to retcode {}".format(sleepAfterTimeout, retCode[0:50]) )
							for ii in range(int(sleepAfterTimeout)):
								if self.testPing(ipNumber) == 0: break
								self.sleep(0.5) 
						elif 	delayCounter %delayEveryx == 0:
							if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(10,u"delaying send by {} secs after {} sends".format(SleepFor, delayCounter) )
							self.sleep(SleepFor +delayCounter/5)
						else:
							self.sleep(1.5)

						if self.SHELLY[devId]["lastSuccessfullConfigPush"][page]  < 200:
							if self.decideMyLog(u"SetupDevices"):self.indiLOG.log(10,u"{},  setting page >{}<".format(ipNumber, page) )
							pushTried = True
							jData, retCode = self.execShellySend(ipNumber, page, timeoutMax=2)
							udata = unicode(jData)
							if udata.find( findItem ) == -1:
								if udata.find("offline")  == -1:
									self.indiLOG.log(10,u"send config to devId:{} not successfull for page:{}\nanswer not ok:>{}<".format(devId, page, udata) )
								continue
							else:
								self.SHELLY[devId]["lastSuccessfullConfigPush"][page] = time.time()
								self.indiLOG.log(10,u"send action_url to devId:{}\nanswer ok:>{}<".format(devId, udata) )
								break


			allPages = True
			for xx in self.SHELLY[devId]["lastSuccessfullConfigPush"]:
				if xx == "all": continue
				if self.SHELLY[devId]["lastSuccessfullConfigPush"][xx]  < 200:
					allPages = False
					break

			if allPages:
				self.SHELLY[devId]["lastSuccessfullConfigPush"]["all"] = time.time()
				self.indiLOG.log(10,u"successfull action_url push to devId:{}, timer settings:{}".format(dev.name, self.SHELLY[devId]["lastSuccessfullConfigPush"]) )
				self.pushRequest = -1
			else:
				self.SHELLY[devId]["lastSuccessfullConfigPush"]["all"] = -10



		except Exception as e:
			if unicode(e).find("None") == -1:
				self.exceptionHandler(40,e)
		return 




##############################################################################################

	####-----------------	 ---------
	def getJsonFromDevices(self, ipNumber, page, jsonAction="", port = "", testHTTP=False, noJson=False, timeoutMax=10 ):

		try:
			if self.decideMyLog(u"Special"): self.indiLOG.log(10,u"getJsonFromDevices: ip:{} page:{}".format(ipNumber, page) )
			if not self.isValidIP(ipNumber): return {}, "ipNotValid"

			usePort = str(self.portOfShellyDevices)
			if port !="": usePort = str(port)
			if self.useCurlOrPymethod.find("curl") > -1:
				if len(self.userIDOfShellyDevices) >0:
					UID = " -u "+self.userIDOfShellyDevices+":"+self.passwordOfShellyDevices
				else: UID = ""
				#usepage = page.replace("[","\[").replace("]","\]")
				usepage = page
				cmdR  = self.useCurlOrPymethod+" -m "+str(timeoutMax)+" --globoff 'http://"+ipNumber+":"+usePort+"/"+usepage+"'"

				if self.decideMyLog(u"Polling"): self.indiLOG.log(10,u"Connection: "+cmdR )
				try:
					ret, err = self.readPopen(cmdR)
					if testHTTP: return {}, "0"
					if noJson: return {}, "0"
					try:
						jj = json.loads(ret)
					except :
						retCode = "timeout" if err.find("timed out") >-1 else err[0:50]
						if ipNumber != self.HTTPlisternerTestIP:
							self.indiLOG.log(10,u"Shelly curl response from {}  no json object returned: >{}<>{}<".format(ipNumber, ret, retCode) )
						return {}, retCode
					if  jsonAction == "print":
						self.indiLOG.log(10,u" Connection  info\n{}".format( json.dumps(jj, sort_keys=True, indent=2)) )

					return jj, "0"

				except	Exception as e:
					self.indiLOG.log(40,u"Connection: in Line {} has error={}   Connection".format(sys.exc_info()[2].tb_lineno, e) )
				return {}, "1"

			############# does not work on OSX	el capitan ssl lib too old	##########
			elif self.useCurlOrPymethod == "requests":

				url = "http://"+ipNumber+":"+usePort+"/"+page

				request = requests.Session()
				try:
						if len(self.userIDOfShellyDevices) >0:
							resp = request.get(url,auth=(self.userIDOfShellyDevices, self.passwordOfShellyDevices))
						else:
							resp = request.get(url)
						if testHTTP: return {}, "0"

						try:
							jj = resp.json()
						except :
							if noJson: return {}, "0"
							r = unicode(resp)
							r =  "timeout" if r.find("timed out")>-1 else rr[0:50]
							self.indiLOG.log(40,u"Shelly reponse from {} url:{},  no json object returned:>{}<".format(ipNumber, url, resp) )
							return {}, r
 
						if  jsonAction == "print":
							self.indiLOG.log(10,u" Connection  info\n{}".format(json.dumps(jj, sort_keys=True, indent=2)) )

						return jj, "0"

				except	Exception as e:
					if testHTTP: return {}, "0"
					self.exceptionHandler(40,e)
					self.indiLOG.log(40,u"url testHTTP:{}, used: {}".format(testHTTP, url))
		
		except	Exception as e:
			self.exceptionHandler(40,e)
		return {}, "1"



####-------------------------------------------------------------------------####


	def addToStatesUpdateDict(self,devId,key,value,uiValue="",decimalPlaces="", force=""):
		devId=unicode(devId)
		#self.indiLOG.log(10,u"addToStatesUpdateDict devId:{}; key:{}, value:{}; uiValue:{}, decPlace:{}".format(devId,key,value,uiValue,decimalPlaces) )
		try:
				if devId not in self.updateStatesDict: 
					self.updateStatesDict[devId] = {}
				if key in self.updateStatesDict[devId]:
					if value == self.updateStatesDict[devId][key]["value"]: return 
				self.updateStatesDict[devId][key] = {"value":value,"decimalPlaces":decimalPlaces,"uiValue":uiValue, "force":force}

			#self.updateStatesDict = local	  
		except Exception as e:
			if	unicode(e).find(u"UnexpectedNullErrorxxxx") >-1: return newStates
			self.exceptionHandler(40,e)
		return 

####-------------------------------------------------------------------------####
	def executeUpdateStatesDict(self,onlyDevID="0",calledFrom=""):
		try:
			if len(self.updateStatesDict) ==0: return
			#self.indiLOG.log(10, u"executeUpdateStatesList  updateStatesList: {}".format(self.updateStatesDict))
			onlyDevID = unicode(onlyDevID)

			local ={}
			#		 
			if onlyDevID == "0":
				for ii in range(5):
					try: 
						local = copy.deepcopy(self.updateStatesDict)
						break
					except Exception as e:
						self.sleep(0.05)
				self.updateStatesDict={} 

			elif onlyDevID in self.updateStatesDict:
				for ii in range(5):
					try: 
						local = {onlyDevID: copy.deepcopy(self.updateStatesDict[onlyDevID])}
						break
					except Exception as e:
						self.sleep(0.05)

				try: 
					del self.updateStatesDict[onlyDevID]
				except Exception as e:
					pass
			else:
				return 

			self.lastexecuteUpdateStatesDictCalledFrom = (calledFrom,onlyDevID)

			dateString = datetime.datetime.now().strftime(_defaultDateStampFormat)
			for devId in local:
				#self.indiLOG.log(10,u"dev:{}   updating {}".format(devId, local))
				if onlyDevID !="0" and onlyDevID != devId: continue
				if devId == "0": continue
				try: devID = int(devId)
				except Exception as e:
					self.indiLOG.log(40,u"executeUpdateStatesDict bad devID:{}, local:{}".format(unicode(devId)[0:25], unicode(local[devId])[0:40]) )

					continue
				oneNew = False
				onOffStateNotChanged = True
				if len(local[devId]) > 0:
					changedOnly = []
					dev = indigo.devices[devID]
					props = dev.pluginProps
					for state in local[devId]:
						if state not in dev.states:
							self.indiLOG.log(40,u"executeUpdateStatesDict dev:{} state:{} not present ".format(dev.name, state) )
							continue

						if state == "onOffState" and dev.states["onOffState"] != local[devId][state]["value"]: 
							onOffStateNotChanged = False
							oneNew = True

						if local[devId][state]["force"] == "": 
							if dev.states[state] == local[devId][state]["value"]: continue
						elif local[devId][state]["force"] == "ui":
							if state+".ui" in dev.states:
								if dev.states[state+".ui"] == local[devId][state]["uiValue"]: continue

						dd = {u"key":state, u"value":local[devId][state]["value"]}
						if local[devId][state]["uiValue"]		!="": dd["uiValue"]			= local[devId][state]["uiValue"]
						if local[devId][state]["decimalPlaces"]	!="": dd["decimalPlaces"]	= local[devId][state]["decimalPlaces"]

						if state.find("last") == -1 and state.find("previous") == -1 and state.find(u"upFor") == -1:
							if self.logStateChanges == u"all" or (self.logStateChanges == u"onOff" and state == "onOffState") or (self.logStateChanges == u"all-noWiFi" and state != "WiFi_rssi"):
								if state+'.ui' in dev.states:
									self.indiLOG.log(20,u'received "{}" {} to "{}"; ui="{}"'.format(dev.name, state, local[devId][state]["value"], local[devId][state]["uiValue"]) )
								else:
									self.indiLOG.log(20,u'received "{}" {} to "{}"'.format(dev.name, state, local[devId][state]["value"]) )

						changedOnly.append(dd)

						#if dev.id == 422345573: self.indiLOG.log(10,u"adding status dev:{}; state:{} dd:{} to sensorValue".format(dev.name, state, dd ) )
						if  "displaySelect" in props and props["displaySelect"] == state:
							if "SupportsSensorValue" in props and props["SupportsSensorValue"]:
								#if dev.id == 422345573: self.indiLOG.log(10,u"adding status dev:{}; added to sensorValue".format(dev.name ) )
								xx = copy.copy(dd)
								xx["key"] = "sensorValue"
								changedOnly.append(xx)
							oneNew = True
					if oneNew and not (props["isRelay"] and onOffStateNotChanged):
						dd = {u"key":"lastStatusChange", "value":dateString}
						changedOnly.append(dd)
					#self.indiLOG.log(10,u"dev:{} updating states:{} ".format(devId, changedOnly))
					
					self.execUpdateStatesList(dev,changedOnly)

		except Exception as e:
				if	unicode(e).find(u"UnexpectedNullErrorxxxx") >-1: return 
				self.exceptionHandler(40,e)
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


		except Exception as e:
			self.exceptionHandler(40,e)
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

		except Exception as e:
			self.exceptionHandler(40,e)
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
		except	Exception as e:
				self.indiLOG.log(50, u"checkLogFiles Line {} has error={}".format(sys.exc_info()[2].tb_lineno, e))
			
			
	####-----------------	 ---------
	def decideMyLog(self, msgLevel):
		try:
			if msgLevel	 == u"all" or u"all" in self.debugLevel:	 return True
			if msgLevel	 == ""	 and u"all" not in self.debugLevel:	 return False
			if msgLevel in self.debugLevel:							 return True
			return False
		except	Exception as e:
			self.exceptionHandler(40,e)
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
			if self.decideMyLog(u"SQLSuppresslog"): self.indiLOG.log(10,u"setSqlLoggerIgnoreStatesAndVariables settings:{} ".format( self.SQLLoggingEnable) )
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
				self.indiLOG.log(10,u" \n\n")
				if outOffD !="":
					self.indiLOG.log(10,u" switching off SQL logging for special devtypes/states:\n{}\n for devices:\n>>>{}<<<".format(json.dumps(_sqlLoggerIgnoreStates, sort_keys=True, indent=2), outOffD) )

				if outOND !="":
					self.indiLOG.log(10,u" switching ON SQL logging for special states for devices: {}".format(outOND) )

				if outOffV !="":
					self.indiLOG.log(10,u" switching off SQL logging for variables :{}".format(outOffV) )

				if outONV !="":
					self.indiLOG.log(10,u" switching ON SQL logging for variables :{}".format(outONV) )
				self.indiLOG.log(10,u"setSqlLoggerIgnoreStatesAndVariables settings end\n")



		except Exception as e:
			self.exceptionHandler(40,e)
		return 

####-------------------------------------------------------------------------####
	def readPopen(self, cmd):
		try:
			ret, err = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
			return ret.decode('utf_8'), err.decode('utf_8')
		except Exception as e:
			self.exceptionHandler(40,e)

####-----------------  exception logging ---------
	def exceptionHandler(self, level, exception_error_message):

		try:
			try: 
				if u"{}".format(exception_error_message).find("None") >-1: return exception_error_message
			except: 
				pass

			filename, line_number, method, statement = traceback.extract_tb(sys.exc_info()[2])[-1]
			#module = filename.split('/')
			log_message = "'{}'".format(exception_error_message )
			log_message +=  "\n{} @line {}: '{}'".format(method, line_number, statement)
			if level > 0:
				self.indiLOG.log(level, log_message)
			return "'{}'".format(log_message )
		except Exception as e:
			indigo.server.log( "{}".format(e))


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
			self.indiLOG.log(10, u"..  starting HTTP listener on port:{} ".format(self.portOfIndigoServer) )

			self.httpThread = threading.Thread(name='daemon_server', target=self.start_HTTP_server, args=(self.portOfIndigoServer,) )
			self.httpThread.setDaemon(True) # Set as a daemon so it will be killed once the main thread is dead.
			self.httpThread.start()


		except Exception as e:
			self.exceptionHandler(40,e)

####-------------------------------------------------------------------------####
	def start_HTTP_server(self, port):
		'''Start a simple webserver serving path on port'''
		httpd = HTTPServer(('', port), RequestHandler)
		httpd.serve_forever()

####-------------------------------------------------------------------------####
####-------------------------------------------------------------------------####
####-------------------------------------------------------------------------####

## try = python 2.7 ;  except:  python3 
try:
	from BaseHTTPServer import BaseHTTPRequestHandler
except:
	from http.server import BaseHTTPRequestHandler
try:
	from BaseHTTPServer import HTTPServer
except:
	from http.server import HTTPServer



class RequestHandler(BaseHTTPRequestHandler):
	def do_HEAD(self):
		if indigo.activePlugin.decideMyLog(u"HTTPlistener"): indigo.activePlugin.indiLOG.log(10, u"RequestHandler  doHead ip{} , path:{}".format(self.client_address, self.path))
		return
	
	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/plain')
		self.wfile.flush()
		try:
			if indigo.activePlugin.decideMyLog(u"HTTPlistener"): indigo.activePlugin.indiLOG.log(10, u"RequestHandler  do_GET ..  ip{} , path:{}".format(self.client_address, self.path))
			indigo.activePlugin.addtoAnalyzePollerQueue( {"ipNumber":self.client_address[0], "page":"httpAction", "data":{"path": self.path}}  )
		except Exception as e:
			indigo.activePlugin.indiLOG.log(40,"Line {} has error={}".format(sys.exc_info()[2].tb_lineno, e))
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




