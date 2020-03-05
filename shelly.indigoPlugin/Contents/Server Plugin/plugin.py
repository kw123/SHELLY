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

# default properties of device types
#             shelly/stettings type:{}
_emptyProps ={	# switches
				"SHSW-1":{"props":{"SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"ipNumber":"", "shellyMAC":"", "pollingFrequency":20, "expirationSeconds":180,"displaySelect":"relay_0" },
						"tempLimits":[0,0],
						"setPage":{"0":"relay/0?","1":"relay/1?"}
						},

				"SHSW-PM":{"props":{"SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"ipNumber":"", "shellyMAC":"", "pollingFrequency":20, "expirationSeconds":180,"displaySelect":"relay_0" },
						"tempLimits":[0,0],
						"setPage":{"0":"relay/0?","1":"relay/1?"}
						},

			 	"SHSW-25":{"props":{"SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"ipNumber":"", "shellyMAC":"", "pollingFrequency":20, "expirationSeconds":180,"displaySelect":"relay_0" },
						"tempLimits":[0,0],
						"setPage":{"0":"relay/0?","1":"relay/1?"}
						},

				"SHEM":{"props":{"SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"ipNumber":"", "shellyMAC":"", "pollingFrequency":20, "expirationSeconds":180,"displaySelect":"relay_0" },
						"tempLimits":[0,0],
						"setPage":{"0":"relay/0?","1":"relay/1?"}
						},
				# dimmers
				"SHDM-1":{"props":{"SupportsOnState":False, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, 
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"ipNumber":"", "shellyMAC":"", "pollingFrequency":20, "expirationSeconds":180},
						"tempLimits":[3000,6500],
						"rgbLimits":[1,255],
						"setPage":{"white":"light/0?","white":"light/0?"}
						},

				"SHBLB-1":{"props":{"SupportsOnState":False, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, 
						"SupportsColor":True, "SupportsRGB":True, "SupportsWhite":True, "SupportsWhiteTemperature":True, "SupportsRGBandWhiteSimultaneously":True, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"ipNumber":"", "shellyMAC":"", "pollingFrequency":20, "expirationSeconds":180},
						"tempLimits":[3000,6500],
						"rgbLimits":[1,255],
						"setPage":{"white":"light/0?","color":"light/0?"}
						},

				"SHRGBW2":{"props":{"SupportsOnState":False, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False, 
						"SupportsColor":True, "SupportsRGB":True, "SupportsWhite":True, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":True, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"ipNumber":"", "shellyMAC":"", "pollingFrequency":20, "expirationSeconds":180 },
						"tempLimits":[3000,6500],
						"rgbLimits":[1,255],
						"setPage":{"white":"white/0?","color":"color/0?"}
						},
				# sensors
				"SHHT-1":{"props":{"SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"ipNumber":"", "shellyMAC":"", "pollingFrequency":10, "expirationSeconds":50400,"displaySelect":"Temperature" },
						"tempLimits":[0,0],
						"setPage":{}
						}, 

				"SHWT-1":{"props":{"SupportsOnState":True, "SupportsSensorValue":True, "SupportsStatusRequest":True, "AllowOnStateChange":False,  
						"SupportsColor":False, "SupportsRGB":False, "SupportsWhite":False, "SupportsWhiteTemperature":False, "SupportsRGBandWhiteSimultaneously":False, "SupportsTwoWhiteLevels":False, "SupportsTwoWhiteLevelsSimultaneously":False,
						"ipNumber":"", "shellyMAC":"", "pollingFrequency":10, "expirationSeconds":50400,"displaySelect":"Flood"},
						"tempLimits":[0,0],
						"setPage":{}
						}

			}
_sqlLoggerIgnoreStates			= {"status, sensorvalue_ui, updateReason, lastStatusChange, displayStatus, lastMessageFromDevice"}

_debugAreas 					= ["SetupDevices","HTTPlistener","Polling","Ping","Actions","SQLSuppresslog","Special","all"]

## this is ipnumber --> devId, copied to self.SHELLY[ip#] = copy.deepCopy(_emptyShelly)
_emptyShelly 					= { "ipNumber":"", "shellyMAC":"", "lastData":{}, "lastCheck":0, "state":"", "reset":False, "lastActive":0, "queue":0, "deviceEnabled":False, "pollingFrequency":10, 
									"defaultTask":"status",  "expirationSeconds":100, "lastMessageFromDevice":0,  "lastMessage-settings":"", "lastMessage-status":"",
									"lastAlarm":0, "childIndigoId":0, "devType":"", "actionDefined":False}

_colorSets 						= ["SupportsColor", "SupportsRGB", "SupportsWhite", "SupportsWhiteTemperature", "SupportsRGBandWhiteSimultaneously", "SupportsTwoWhiteLevels", "SupportsTwoWhiteLevelsSimultaneously"]

_supportsBatteryLevel 			= ["SHHT-1","SHWT-1"]
_GlobalConst_fillMinMaxStates 	= ["Temperature","Temperature_ext_0","Temperature_ext_1","Pressure","Humidity"]
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

		self.pluginShortName 			= "shelly"

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


			self.startTime = time.time()

			self.getDebugLevels()

			self.setVariables()

			#### basic check if we can do get path for files			 
			self.initFileDir()

			self.checkcProfile()

			self.myLog( text = " --V {}   initializing  -- ".format(self.pluginVersion), destination="standard")

			self.setupBasicFiles()

			self.startupFIXES()

			self.readConfig()

			self.resetMinMaxSensors(init=True)

			self.setSqlLoggerIgnoreStatesAndVariables()

			self.startHTTPListening()

	  
 			self.indiLOG.log(10, "startup(self): setting variables, debug ..   finished ")

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
			self.queueActive	  			= False
			self.SHELLY						= {}
			self.CHILDRENtoParents			= {}
			self.varExcludeSQLList			= {}
			self.queueList					= []
			self.doNotrestartDev			= ""
			self.executeUpdateStatesDictActive = ""
			self.updateStatesDict				= {}
			self.ipNumberRangeToTest		 = []
			self.nextIPSCAN 				 = ""
			self.setLogfile(self.pluginPrefs.get("logFileActive2", "standard"))
			self.unfiCurl					= self.pluginPrefs.get(u"unfiCurl", "/usr/bin/curl")
			if self.unfiCurl == "curl" or len(self.unfiCurl) < 4:
				self.unfiCurl = "/usr/bin/curl"
				self.pluginPrefs["unfiCurl"] = self.unfiCurl

			try:
				xx = (self.pluginPrefs.get("SQLLoggingEnable", "on-on")).split("-")
				self.SQLLoggingEnable ={"devices":xx[0]=="on", "variables":xx[1]=="on"}
			except:
				self.SQLLoggingEnable ={"devices":False, "variables":False}

			try:
				self.tempUnits				= self.pluginPrefs.get(u"tempUnits", u"Celsius")
			except:
				self.tempUnits				= u"Celsius"

			try:
				self.tempDigits				 = int(self.pluginPrefs.get(u"tempDigits", 1))
			except:
				self.tempDigits				 = 1

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
			try: 	
				self.indigoFolderId = indigo.devices.folders.getId(self.indigoFolderName)
			except:
				try:
					ff = indigo.devices.folder.create(self.indigoFolderName)
					self.indigoFolderId = ff.id
				except:
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

######################################################################################
	# Indigo xml callbacks 
######################################################################################

####-------------------------------------------------------------------------####
	def buttonConfirmconfirmIpNumberSetupCALLBACK(self, valuesDict, typeId=""):
		ip = valuesDict["ipNumber"].strip()
		if self.isValidIP(ip):
			self.SHELLY[0]["ipNumber"] = ip
			self.addToShellyPollerQueue(0, "settings")
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
	def buttonPrintShellyDevInfoCALLBACK(self):

		out =""
		for devId in self.SHELLY:
			if devId == 0: continue
			try: 
				dev = indigo.devices[devId]
				name = dev.name.encode("utf8")
				devType = dev.name.encode("utf8")
			except:
				name = "dev does not exist"
				devType = "---"
			childID = self.SHELLY[devId]["childIndigoId"]
			parentID = 0
			if childID !=0:
				if childID in self.CHILDRENtoParents: 
					parentID = self.CHILDRENtoParents[childID]
			out += "\n:::: {:30s} - {:16d}  {:12s}  {:20s}  {:12s}  {:16d}  {:16d}  {:5.0f}[sec]  {:5.0f}[sec]\n".format( name, devId, devType, self.SHELLY[devId]["ipNumber"], self.SHELLY[devId]["shellyMAC"], childID, parentID, self.SHELLY[devId]["expirationSeconds"], self.SHELLY[devId]["pollingFrequency"])	
			out += "settings  JSON from SHELLYdevice ::::::::::::::::\n"+json.dumps(self.SHELLY[devId]["lastMessage-settings"], sort_keys=True, indent=4)+"\n"
			out += "status    JSON from SHELLYdevice ::::::::::::::::\n"+json.dumps(self.SHELLY[devId]["lastMessage-status"],   sort_keys=True, indent=4)
		out+= "\n child to parent ids:{}\n".format(self.CHILDRENtoParents)
		if out !="":
			out0 = "\n:::: Device ----------------        -  ........ dev.id  devType               IP#                   shell-MAC#           childID          parentID      expTime  pollingFreq"
			self.indiLOG.log(20,out0+out )
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


####------================------- sprinkler ------================-----------END


####-------------------------------------------------------------------------####
	def readConfig(self):  ## only once at startup
		try:
			pass
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 
#

####-------------------------------------------------------------------------####
	def writeJson(self,data, fName="", fmtOn=False ):
		try:

			if format:
				out = json.dumps(data, sort_keys=True, indent=2)
			else:
				out = json.dumps(data)

			if fName !="":
				f=open(fName,u"w")
				f.write(out)
				f.close()
			return out

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return ""



####-------------------------------------------------------------------------####
	def deviceStartComm(self, dev):
		try:
			if dev.id == self.doNotrestartDev: return 
			if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(20,"\n\ndeviceStartComm called for {}; dev={}".format(dev.id, dev.name) )

				#self.indiLOG.log(40,"\n\ndev: {} \nuc(dev):{}\n has props:{}\n states:{}  \nglobalprops:{}\n\n".format(dev.name, unicode(dev), unicode(dev.pluginProps), unicode(dev.states), unicode(dev.globalProps)) )


			if "brightness" in dev.states: 
				dev.onBrightensToLast = True
				dev.replaceOnServer()
				dev = indigo.devices[dev.id]

			self.renewShelly(dev, startCom=True)

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))


####-------------------------------------------------------------------------####
	def renewShelly(self, dev, startCom=False):
		try:


			isChild = False
			## skip childs

			props = dev.pluginProps

			parentIndigoId = dev.pluginProps["parentIndigoId"]

			if dev.pluginProps["parentIndigoId"] != 0:
				if parentIndigoId not in self.SHELLY:
					self.SHELLY[parentIndigoId] = copy.copy(_emptyShelly)
				self.SHELLY[parentIndigoId]["childIndigoId"] = dev.id
				isChild = True

			#self.indiLOG.log(20,"parentIndigoId:{} ischild:{}".format(parentIndigoId, isChild))

			if not isChild:
					if self.pluginState == "init":
						dev.stateListOrDisplayStateIdChanged()
						self.initShelly(dev.id,  dev.states["shellyMAC"], dev.address, devType=dev.deviceTypeId)

					if dev.id not in self.SHELLY:
						self.SHELLY[dev.id] = {}
						self.initShelly(dev.id,  dev.states["shellyMAC"], dev.address, devType=dev.deviceTypeId)

					dev.stateListOrDisplayStateIdChanged()

					for item in _emptyShelly:
						if item not in self.SHELLY[dev.id]:
							self.SHELLY[dev.id][item] = _emptyShelly[item]

					self.SHELLY[dev.id]["deviceEnabled"] = True
					try: self.SHELLY[dev.id]["expirationSeconds"]	= float(dev.pluginProps["expirationSeconds"])
					except: pass
					try: self.SHELLY[dev.id]["pollingFrequency"]	= float(dev.pluginProps["pollingFrequency"])
					except: pass
					try: self.SHELLY[dev.id]["childIndigoId"] 		= 		dev.pluginProps["childIndigoId"]
					except: pass
					try: self.SHELLY[dev.id]["devType"] 			= 		dev.deviceTypeId
					except: pass

					actionDefined = False
					try: actionDefined = dev.states["report_url"].find("ok") >-1
					except: 
						try: actionDefined = len(dev.states["action_from_Device"]) >-1
						except: pass
					self.SHELLY[dev.id]["actionDefined"] = actionDefined

					self.startShellyDevicePoller("start", shellySelect=dev.id)

					if dev.deviceTypeId == ["SHBLB-1","SHRGBW2"]:
						for sType in _colorSets:
							try: 	self.SHELLY[dev.id][sType] = dev.pluginProps[sType]
							except: pass
					self.startShellyDevicePoller("start", shellySelect=dev.id)

					if self.SHELLY[dev.id]["childIndigoId"] >0:
						description0 = "pol-freq:{}[sec]; relay#0; parent of {}".format( self.SHELLY[dev.id]["pollingFrequency"], self.SHELLY[dev.id]["childIndigoId"] )
					else:
						description0 = "pol-freq:{}[sec]".format( self.SHELLY[dev.id]["pollingFrequency"] )

					if dev.description != description0:
						dev.description =  description0
						self.doNotrestartDev = dev.id
						dev.replaceOnServer()
						dev = indigo.devices[dev.id]
						time.sleep(0.1)
						self.doNotrestartDev = ""

			else:
				parentId = dev.pluginProps["parentIndigoId"]
				self.CHILDRENtoParents[dev.id] = parentId
				#self.indiLOG.log(20,"parentIndigoId:{} polling:{}".format(parentId, self.SHELLY[parentId]["pollingFrequency"] ))

				description = "pol-freq:{}[sec]; relay#1; child of {}".format( self.SHELLY[parentId]["pollingFrequency"], self.CHILDRENtoParents[dev.id] )
				if dev.description != description:
					dev.description =  description
					self.doNotrestartDev = dev.id
					dev.replaceOnServer()
					time.sleep(0.1)
					dev = indigo.devices[dev.id]
					self.doNotrestartDev = ""

			if False and startCom:			
				self.indiLOG.log(20,"isChild:{}; parentIndigoId:{} states:{}".format(isChild, parentIndigoId, unicode(dev.states).encode("utf8")  ))
				if dev.id in self.SHELLY:
					self.indiLOG.log(20,"shelly:{}".format(self.SHELLY[dev.id]))
				else:
					self.indiLOG.log(20," ... not in SHELLY")

				if dev.id in self.CHILDRENtoParents:
					self.indiLOG.log(20,"CHILDRENtoParents:{}\n\n".format(self.CHILDRENtoParents[dev.id]))
				else:
					self.indiLOG.log(20," ... not in CHILDRENtoParents")

			return

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))




####-------------------------------------------------------------------------####
	def deviceDeleted(self, dev):  ### indigo calls this 

		if dev.id in self.SHELLY:
			if 	self.SHELLY[dev.id]["childIndigoId"]  ==0:
				try: 	del self.SHELLY[dev.id]
				except: pass

			else:
				child = self.SHELLY[dev.id]["childIndigoId"]
				self.indiLOG.log(20,"deviceDeleted trying to del child devid:{}".format(child) )
				try:	indigo.device.delete(child)
				except: pass

				try: 	del self.SHELLY[self.SHELLY[dev.id]["childIndigoId"] ]
				except: pass
				try: 	del self.SHELLY[dev.id]
				except: pass
	
		if dev.id in self.CHILDRENtoParents:
			parent = self.CHILDRENtoParents[dev.id]
			self.indiLOG.log(20,"deviceDeleted trying to del parent devid:{}".format(parent) )
			try: 	indigo.device.delete(parent)
			except: pass
			try: 	self.SHELLY[self.CHILDRENtoParents[dev.id]]["childIndigoId"] = 0	
			except: pass
			try: 	del self.CHILDRENtoParents[dev.id]
			except: pass


		return

####-------------------------------------------------------------------------####
	def deviceStopComm(self, dev):
		try: self.indiLOG.log(20,"deviceStopComm called for dev={}".format(dev.name.encode("utf8")) )
		except: pass
		try:	self.SHELLY[dev.id]["deviceEnabled"] = False
		except: pass
		#self.stopShellyDevicePoller( shellySelect=dev.id)


####-------------------------------------------------------------------------####
	#def didDeviceCommPropertyChange(self, origDev, newDev):
	#	 #if origDev.pluginProps['xxx'] != newDev.pluginProps['address']:
	#	 #	  return True
	#	 return False
	###########################		INIT	## END	 ########################




	###########################		DEVICE	#################################


####-------------------------------------------------------------------------####
	def getDeviceConfigUiValues(self, pluginProps, typeId="", devId=0):
		try:
			theDictList =  super(Plugin, self).getDeviceConfigUiValues(pluginProps, typeId, devId)
			try: ##Only if it exists already
				theDictList[0]["shellyMAC"] = self.SHELLY[int(devId)]["shellyMAC"]
				theDictList[0]["ipNumber"]  = self.SHELLY[int(devId)]["ipNumber"]
			except: pass
			return theDictList

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"theDictList {}".format(theDictList))
		return theDictList

####-------------------------------------------------------------------------####
	def validateDeviceConfigUi(self, valuesDict, typeId, devId):

		error =""
		errorDict = indigo.Dict()
		valuesDict[u"MSG"] = "OK"
		try:
			dev = indigo.devices[devId]
			if self.isValidIP(valuesDict["ipNumber"]):
				valuesDict[u"address"] = valuesDict["ipNumber"].strip()
			else:
				valuesDict[u"MSG"] = "bad Ip number, please reenter"
				return False, valuesDict

			if "childIndigoId"  not in valuesDict: valuesDict["childIndigoId"] = 0
			if "parentIndigoId" not in valuesDict: valuesDict["parentIndigoId"] = 0

			dev.states["shellyMAC"] = valuesDict["shellyMAC"].upper()

			if devId not in self.SHELLY:
				self.initShelly(dev.id, valuesDict[u"shellyMAC"], valuesDict["ipNumber"].strip())
			else:
				self.SHELLY[devId]["ipNumber"] 		=  valuesDict["ipNumber"].strip()
				self.SHELLY[devId]["shellyMAC"] 	=  valuesDict[u"shellyMAC"]

			self.SHELLY[devId]["pollingFrequency"] 	= valuesDict[u"pollingFrequency"]
				
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			return ( False, valuesDict, errorDict )

		return ( True, valuesDict )

########################################
	def padIP(self,xxx):
		return xxx



####-------------------------------------------------------------------------####

####-------------------------------------------------------------------------####

# noinspection SpellCheckingInspection
	def validatePrefsConfigUi(self, valuesDict):


		self.debugLevel			= []
		for d in _debugAreas:
			if valuesDict[u"debug"+d]: self.debugLevel.append(d)

		self.unfiCurl	= valuesDict[u"unfiCurl"]

		self.setLogfile(valuesDict[u"logFileActive2"])
	 

		self.indigoFolderName = valuesDict["indigoFolderName"]
		try: 	
			self.indigoFolderId = indigo.devices.folders.getId(self.indigoFolderName)
		except:
			try:
				ff = indigo.devices.folder.create(self.indigoFolderName)
				self.indigoFolderId = ff.id
			except:
				self.indigoFolderId =0



		try: 
			xx = valuesDict["SQLLoggingEnable"].split("-")
			yy = {"devices":xx[0]=="on", "variables":xx[1]=="on"}
			if yy != self.SQLLoggingEnable:
				self.SQLLoggingEnable = yy
				self.actionList["setSqlLoggerIgnoreStatesAndVariables"] = True
		except Exception, e:
			self.indiLOG.log(30,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.SQLLoggingEnable = {"devices":True, "variables":True}

		self.tempUnits					= valuesDict[u"tempUnits"]	# Celsius, Fahrenheit, Kelvin
		self.tempDigits					= int(valuesDict[u"tempDigits"])  # 0/1/2

		self.IndigoServerIPNumber 		= valuesDict[u"IndigoServerIPNumber"]
		self.portOfIndigoServer 		= int(valuesDict[u"portOfIndigoServer"])
		self.userIDOfShellyDevices 		= valuesDict[u"userIDOfShellyDevices"]
		self.passwordOfShellyDevices 	= valuesDict[u"passwordOfShellyDevices"]

		return True, valuesDict

	###########################	   MAIN LOOP  ############################
####-------------------------------------------------------------------------####
	def initConcurrentThread(self):

		now = datetime.datetime.now()
		self.messagesQueue	  = Queue.Queue()
		self.quitNow		  = u""

		self.startTime		  = time.time()
		self.stackReady		  = True


		for ii in range(2):
			if self.pluginPrefs.get(u"IndigoServerIPNumber","") == "none": break
			self.sleep(10)



		self.writeJson(self.pluginVersion, fName=self.indigoPreferencesPluginDir + "currentVersion")


		self.lastMinuteChecked	= -1
		self.lasthourChecked 	= now.hour
		self.lastDayChecked		= -1
		self.lastSecChecked		= 0
		self.countLoop			= 0
		self.currentVersion		= 7.0

		if self.currentVersion != self.pluginVersion :
			pass
		else:
			pass
		self.lastUpdateSend = time.time()  
		self.pluginState	= "run"

		self.initShelly(0,  "0", "0")

		for dev in indigo.devices.iter(self.pluginId):
			self.renewShelly(dev, startCom=False)
			if not dev.enabled:
				if dev.id in self.SHELLY: self.SHELLY[dev.id]["deviceEnabled"] = False
		#indigo.server.log(" print shelly:\n{};\n children:\ns{}".format(self.SHELLY, self.CHILDRENtoParents))

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
		self.sleep(1)
		if self.quitNow !="":
			indigo.server.log( u"runConcurrentThread stopping plugin due to:  ::::: " + self.quitNow + " :::::")
			serverPlugin = indigo.server.getPlugin(self.pluginId)
			serverPlugin.restart(waitUntilDone=False)


		self.indiLOG.log(20, u"killing 2")
		subprocess.call("/bin/kill -9 "+unicode(self.myPID), shell=True )

		return



####-----------------   main loop          ---------
	def dorunConcurrentThread(self): 

		self.initConcurrentThread()


		if self.logFileActive !="standard":
			indigo.server.log(u" ..  initialized")
			self.indiLOG.log(10, u" ..  initialized, starting loop" )
		else:	 
			indigo.server.log(u" ..  initialized, starting loop ")

		########   ------- here the loop starts	   --------------
		try:
			while self.quitNow == "":
				self.countLoop += 1
				self.sleep(9.)

				if self.countLoop > 2: 
					anyChange = self.periodCheck()

		except self.StopThread:
			indigo.server.log( u"stop requested from indigo ")
		## stop and processing of messages received 
		if self.quitNow !="": indigo.server.log( "quitNow: "+self.quitNow +"--- you might see an indigo error message, can be ignored ")
		else: indigo.server.log( "quitNow:  empty")

		self.stackReady	 = False 
		self.pluginState = "stop"



		self.stopShellyDevicePoller()
		self.sleep(0.1)



		return

####-------------------------------------------------------------------------####
	def periodCheck(self):
		anyChange= False
		try:
			now = datetime.datetime.now()
			if self.ipNumberRangeToTest !=[]:
				rangestart = int(self.ipNumberRangeToTest[0].split(".")[3])
				rangeEnd   = int( self.ipNumberRangeToTest[1].split(".")[3]) + 1
				ip0        = self.ipNumberRangeToTest[1].split(".")
				ip0        = ip0[0]+"."+ip0[1]+"."+ip0[2]+"."
				for ipx in range(rangestart, rangeEnd):
					self.nextIPSCAN = ip0 + str(ipx)
					self.SHELLY[0]["ipNumber"] = self.nextIPSCAN
					self.addToShellyPollerQueue(0, "settings")
					for ii in range (20):
						time.sleep(1)
						if self.nextIPSCAN == "": break

			if self.lastMinuteChecked == now.minute: return 

			for devId in self.SHELLY:
				if devId >0:
					if time.time() - self.SHELLY[devId]["lastMessageFromDevice"] > self.SHELLY[devId]["expirationSeconds"]:
						dev= indigo.devices[devId]
						dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOff)
						dev.updateStateOnServer("expired", now.strftime(_defaultDateStampFormat))

					
			self.lastMinuteChecked = now.minute

			if self.lasthourChecked == now.hour: return 
			self.resetMinMaxSensors()
			for devId in self.SHELLY:
				if devId == 0: continue
				self.addToShellyPollerQueue(devId, "settings")
			self.lasthourChecked = now.hour



			return 
		except Exception, e:
			if len(unicode(e)) > 5 :
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				self.indiLOG.log(40,"devId {} ".format(devId))

		return anyChange


####-------------------------------------------------------------------------####
	def performActionList(self):
		try:
			#if self.actionList["setTime"] != []: 
			ASS	
		except Exception, e:
			if len(unicode(e)) > 5 :
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		#self.actionList["setTime"] = []
		return


####-------------------------------------------------------------------------####
	def checkDay(self,now):
		return 



####-------------------------------------------------------------------------####
	def addtoAnalyzePollerQueue(self, data):

		try:
			#self.indiLOG.log(20,"addtoAnalyzePollerQueue  data:{}".format(data))
			## add to message queue
			self.messagesQueue.put(data)
			if not self.queueActive: 
				self.workOnQueue()

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"data:{}".format(data))


####-------------------------------------------------------------------------####
	def workOnQueue(self):

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
		return 
 
####-------------------------------------------------------------------------####
	def execUpdate(self, items):
		try:
			if self.decideMyLog(u"Polling"): self.indiLOG.log(20,"queue received: data:{}".format(items) )
			if "shellIndigoDevNumber" in items:
						sDevId = items["shellIndigoDevNumber"]
						ipNumber =""
						if "ipNumber" in items: ipNumber = items["ipNumber"]
						else:					ipNumber = ""
						#self.indiLOG.log(20,"queue checking devid:{};  IP # in SHELLY :>{}< vs  dev:>{}<".format( sDevId, self.SHELLY[sDevId]["ipNumber"], ipNumber) )

						if sDevId == 0:
							for devId in self.SHELLY:
								if self.SHELLY[devId]["ipNumber"] != ipNumber: continue
								items["shellIndigoDevNumber"] = devId
								#self.indiLOG.log(20,"execUpdate shellIndigoDevNumber found: {} ".format(devId))
								break

							doNotCreate = False
							if items["shellIndigoDevNumber"] == 0:
								for dd in indigo.devices.iter(self.pluginId):
									if dd.address == ipNumber:
										if not dd.enabled:
											self.indiLOG.log(20,"execUpdate shellIndigoDevNumber ==0, .. dev:{}  is disabled, will NOT create new one;  ipNumber:{}".format(dd.name.encode("utf8"), ipNumber))
										else:
											self.indiLOG.log(20,"execUpdate .. dev:{}  is unexpected message, will NOT create new one; ipNumber:{}".format(dd.name.encode("utf8"), ipNumber))
										doNotCreate = True

									self.renewShelly(dd, startCom=False)
								if doNotCreate: return 
								self.indiLOG.log(20,"execUpdate shellIndigoDevNumber ==0, creating new dev for ipNumber:{}".format(ipNumber))

								items["shellIndigoDevNumber"]  = self.createShellyDevice(items["data"], ipNumber)
								# if shell 25 = 2 relays create second device
								if "device" not in items["data"]:
									self.indiLOG.log(40,"execUpdate  new dev ipnumber:{} not complete data:{}".format(items,ipNumber) )
									return 

								if items["data"]["device"]["type"] == "SHSW-25":
									devId = items["shellIndigoDevNumber"]
									self.SHELLY[devId]["childIndigoId"] = self.createShellyDevice(items["data"], ipNumber, parentId=devId)
									dev = indigo.devices[devId]
									props = dev.pluginProps
									props["childIndigoId"] = self.SHELLY[devId]["childIndigoId"] 
									dev.replacePluginPropsOnServer(props)
									self.CHILDRENtoParents[self.SHELLY[devId]["childIndigoId"]] = devId

								self.nextIPSCAN = ""

						if items["shellIndigoDevNumber"] > 0:
							#self.indiLOG.log(20,"execUpdate shellIndigoDevNumber ok:{}".format(items["shellIndigoDevNumber"]) )
							dev = indigo.devices[items["shellIndigoDevNumber"]]

							if "page" in items:
								if items["page"] == "settings":
									self.SHELLY[dev.id]["lastMessage-settings"] = items["data"]
									self.fillShellyDeviceStates( items["data"], dev, items["page"], ipNumber )
								elif items["page"] == "status":
									self.SHELLY[dev.id]["lastMessage-status"] = items["data"]
									self.fillShellyDeviceStates( items["data"], dev, items["page"], ipNumber )
								else: # there was an action get the whole dataset 
									self.addToShellyPollerQueue(sDevId, "status")

			### action http page received
			elif "page" in items and items["page"] == "httpAction":
					#{"ipNumber":192.168.1.x, "page":"httpAction", "data":{"path": {'path': '/data?hum=33&temp=15.25'},}
					if self.decideMyLog(u"Polling"): self.indiLOG.log(20,"queue page item present" )
					if "ipNumber" not in items: 
						#self.indiLOG.log(20,"queue ipNumber item present" )
						return 
					ipNumber = items["ipNumber"]
					if "data" not in items: 
						#self.indiLOG.log(20,"queue data item present" )
						return 
					data = items["data"]["path"]
					found = False
					for devId in self.SHELLY:
						#self.indiLOG.log(20,"queue checking devid:{};  IP # in SHELLY :>{}< vs  dev:>{}<".format(devId, self.SHELLY[devId]["ipNumber"], ipNumber) )
						if self.SHELLY[devId]["ipNumber"] != ipNumber: continue
						## get full update = set status to device
						#self.indiLOG.log(20,"queue existing dev, requesting full status" )
						self.addToShellyPollerQueue(devId, "settings")
						self.addToShellyPollerQueue(devId, "status")
						found = True
						dev = indigo.devices[devId]
						self.fillShellyDeviceStates( items["data"]["path"], dev, items["page"], ipNumber )
						break
					if not found:
						#self.indiLOG.log(20,"queue received: new dev not in SHELLY" )
						## get full description to trigger dev generation
						doNotCreate = False
						for dd in indigo.devices.iter(self.pluginId):
							if dd.address == ipNumber:
								if not dd.enabled:
									self.indiLOG.log(20,"execUpdate .. dev:{}  is disabled, will NOT create new one; ipNumber:{}".format(dd.name.encode("utf8"), ipNumber))
								else:
									self.indiLOG.log(20,"execUpdate .. dev:{}  is unexpected message, will NOT create new one; ipNumber:{}".format(dd.name.encode("utf8"), ipNumber))

								doNotCreate = True
							self.renewShelly(dd, startCom=False)
						if doNotCreate: return 
						self.initShelly(0, "", ipNumber, startPoller=True)
						self.addToShellyPollerQueue(0, "settings")

			## junk data 
			else:
				pass


		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40," data:{}".format(items) )
		return 

####-------------------------------------------------------------------------####
	def createShellyDevice(self, data, fromIP, parentId=""):
		try:
			devId = 0
			if "device" not in data: return devId
			devType = data["device"]["type"]
			shellyMAC = data["device"]["mac"]
			if data["wifi_sta"]["enabled"] and self.isValidIP(data["wifi_sta"]["ip"]):
				ipNumber = data["wifi_sta"]["ip"]
			else: ipNumber =fromIP

			if  parentId =="":
				for devId in self.SHELLY:
					if devId ==0: continue
					if self.SHELLY[devId]["ipNumber"] == ipNumber: 
						self.indiLOG.log(30, "ip# {} already exists devID: {}".format(ipNumber, devId))
						return devId

			props = self.initDevProps(devType, shellyMAC, ipNumber)
			name = "shelly_"+ipNumber
			if parentId != "": 
				name = "shelly_"+ipNumber+"-1"
				props["parentIndigoId"] =  parentId
				props["childIndigoId"]  =  0
				description = "pol-freq:{}[sec];relay#1 child of {}".format(self.SHELLY[devId]["pollingFrequency"], parentId )
			else:
				name = "shelly_"+ipNumber
				props["parentIndigoId"]	=  0
				props["childIndigoId"]	=  0
				description = "pol-freq:{}[sec]".format(self.SHELLY[devId]["pollingFrequency"] )
			try:
				try: 
					dev.indigo.device[name]
					self.indiLOG.log(40,"trying to create new SHELLY device, already exist, disabled? name:{}, props:{}, ipNumber:{}".format(name.encode("utf8"), props, ipNumber))
					for dd in indigo.devices.iter(self.pluginId):
						self.renewShelly(dd, startCom=False)
					return 0
				except: pass

				dev= indigo.device.create(
					protocol		= indigo.kProtocol.Plugin,
					address			= ipNumber,
					name			= name,
					description		= description,
					pluginId		= self.pluginId,
					deviceTypeId	= devType,
					folder			= self.indigoFolderId,
					props			= props
					)
				#dev.onBrightensToLast = True
				#dev.replaceOnServer()
				#dev= indigo.devices[dev.id]

			except Exception, e:
				self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				self.indiLOG.log(40,"name:{}, props:{}, ipNumber:{}".format(name, props, ipNumber))
				return 0

			devId= dev.id

			self.addToStatesUpdateDict(dev.id,"created", datetime.datetime.now().strftime(_defaultDateStampFormat) )
			self.addToStatesUpdateDict(dev.id,"shellyMAC", shellyMAC)
			if  parentId == "":
				self.initShelly(dev.id, shellyMAC, ipNumber, devType=devType)
				

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"data:{}".format(data))
		return devId


####-------------------------------------------------------------------------####
	def initDevProps(self, devType, shellyMAC, ipNumber):
		props = {}
		try:
			props		   					= _emptyProps[devType]["props"]
			props["shellyMAC"] 				= shellyMAC
			props["ipNumber"] 				= self.padIP(ipNumber)
			props["SupportsBatteryLevel"] 	=  devType in _supportsBatteryLevel
				
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		return props


####-------------------------------------------------------------------------####
	def initShelly(self,devId, MAC, ipNumber, devType="", startPoller=True):
		try:
			self.SHELLY[devId] = copy.copy(_emptyShelly)
			self.SHELLY[devId]["shellyMAC"] 		= MAC
			self.SHELLY[devId]["ipNumber"] 			= ipNumber.strip()
			self.SHELLY[devId]["deviceEnabled"] 	= True
			self.SHELLY[devId]["queue"] 			= Queue.Queue()
			self.SHELLY[devId]["devType"] 			= devType
			if startPoller: self.startShellyDevicePoller("start", shellySelect=devId)
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))

		return 
		

####-------------------------------------------------------------------------####
	def fillShellyDeviceStates(self, data, dev, page, ipNumber):


		if page not in ["settings","status","init","httpAction"]: return 
		#self.indiLOG.log(20,"fillShellyDeviceStates dev{} page:{} data:{}".format(dev.name, page, data) )
		dl = False
		##if dev.name.find(".106") > 0: dl = True
		devID = str(dev.id)
		try:
		##	if dl: self.indiLOG.log(20,"fillShellyDeviceStates, devid:{},  data:{}".format(dev.id, data) )
			self.addToStatesUpdateDict(devID,"lastMessageFromDevice", datetime.datetime.now().strftime(_defaultDateStampFormat))
			props = dev.pluginProps

			if self.SHELLY[dev.id]["childIndigoId"] !=0:
				childId  = self.SHELLY[dev.id]["childIndigoId"]
				devChild = indigo.devices[childId]
				propsChild = devChild.pluginProps
			else:
				childId = 0

			if "device" in data: 
				devType = data["device"]["type"]
			if  "wifi_sta" in data:
				if ("enabled" in data["wifi_sta"] and data["wifi_sta"]["enabled"])  or ("u'connected" in data["wifi_sta"] and data["wifi_sta"]["u'connected"]):
					ipNumber = data["wifi_sta"]["ip"]
					if dev.address != ipNumber:
						if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(40,"ip number changed for devID{}; old:{} new:{}".format(dev.id, dev.address, ipNumber) )
						props["address"] = ipNumber
						dev.replacePluginPropsOnServer(props)
						dev = indigo.devices[dev.id]
						props = dev.pluginProps
			if "expired" in dev.states: self.addToStatesUpdateDict(devID, "expired", "no" )

			if page == "httpAction":
				if dev.deviceTypeId == "SHWT-1":
					# data:= {'path': >>> '/data?temp=32.62&flood=1&batV=2.83'<<< is data }
					check = data.split("?")
					if len(check) == 2:
						self.indiLOG.log(40,"flood: http data:{}".format(data) )
						check = check[1].split("&")
						for item in check:
							x = item.split("=")
							if len(x) == 2:
								if x[0] == "flood":
									flood = int(x[1])
									if flood == 1: 
										self.addToStatesUpdateDict(devID, "Flood", "FLOOD" )
										self.addToStatesUpdateDict(devID, "onOffState",True)
										self.addToStatesUpdateDict(devID, "lastAlarm",datetime.datetime.now().strftime(_defaultDateStampFormat))
										#self.addToStatesUpdateDict(devID, "sensorValue",True)
										self.executeUpdateStatesDict()
										dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
										self.SHELLY[dev.id]["lastAlarm"] = time.time()
										#self.indiLOG.log(40,"flood: setting trip to red" )
				self.SHELLY[dev.id]["lastMessageFromDevice"] = time.time()
				self.SHELLY[dev.id]["lastMessageData"] = data
				return 

			##u'report_url': "http://192.168.1.53:8888/data"
			if "report_url" in data and "report_url" in dev.states:
				if data["report_url"].find(self.IndigoServerIPNumber) > -1:
					self.addToStatesUpdateDict(devID, "report_url", "ok:"+data["report_url"])
					dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
					self.SHELLY[dev.id]["actionDefined"] = True
				else:
					self.addToStatesUpdateDict(devID, "report_url", "bad:"+data["report_url"])
					dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
					self.SHELLY[dev.id]["actionDefined"] = False

			if "update"     in data											and "update"		in dev.states: 		self.addToStatesUpdateDict(devID, 		"update", 			data["update"]["has_update"])
			if "bat"        in data											and "batteryLevel" 	in dev.states: 		self.addToStatesUpdateDict(devID, 		"batteryLevel", 	data["bat"]["value"])
			if "wifi_sta"   in data  and "rssi"			in data["wifi_sta"] and "rssi"      	in dev.states: 		self.addToStatesUpdateDict(devID, 		"rssi",           	data["wifi_sta"]["rssi"],      decimalPlaces=0)
			if "update"     in data  and "has_update"	in data["update"]   and "needs_software_Update" in dev.states: 	self.addToStatesUpdateDict(devID, 	"needs_software_Update", str(data["update"]["has_update"]), decimalPlaces="")
			if childId !=0:
				if "update" in data  and "update" 												in devChild.states: self.addToStatesUpdateDict(str(childId), "update", 			data["update"]["has_update"])
			if "sleep_mode" in data											and "sleep_mode" 	in dev.states: 	
				if "period" in data["sleep_mode"] and "unit" in data["sleep_mode"]:	
					sleepM = "{}{}".format(data["sleep_mode"]["period"],data["sleep_mode"]["unit"])
					if True:																						self.addToStatesUpdateDict(devID, 		"sleep_mode", 		sleepM )


			## dynamic values not settings page!!
			if page in ["status","settings"]:
				## fill regular data 
				if True:

					if "act_reasons" in data:
						out =""
						for xx in data["act_reasons"]:
							out+=xx+";"

						if len(out) >0:
							self.addToStatesUpdateDict(devID, "action_from_Device", out)
							self.SHELLY[dev.id]["actionDefined"] = True

					# returned structure: "ext_temperature":{"0":{"tC":22.88,"tF":73.175000},"1":{"tC":23.25,"tF":73.850000}}
					if "ext_temperature" in data:
						for nn in data["ext_temperature"]:
							state = "Temperature_ext_"+nn
							if state in dev.states and "tC" in data["ext_temperature"][nn]:
								self.fillSensor(dev, props, data["ext_temperature"][nn], "tC", state)

					self.fillSensor(dev, props, data, "tmp", "Temperature")
					self.fillSensor(dev, props, data, "hum", "Humidity")
					if "overtemperature" in dev.states and "overtemperature" in data:
						self.addToStatesUpdateDict(devID, "overtemperature", data["overtemperature"])
					if "overload" in dev.states and "overload" in data:
						self.addToStatesUpdateDict(devID, "overload", data["overload"])

					if "sensors" in data:
						sen = data["sensors"]
						if "temperature_threshold" in sen and "temperature_threshold"	in dev.states:	
							self.addToStatesUpdateDict(devID,"temperature_threshold", sens["temperature_threshold"])
						if "humidity_threshold" in sen    and "humidity_threshold" 	in dev.states: 		
							self.addToStatesUpdateDict(devID,"humidity_threshold",  sens["humidity_threshold"])

		
					## page status:  lights":[{"ison":true,"mode":"color", / "white""red":252,"green":255,"blue":236,"white":0,"gain":65,"temp":4750,"brightness":100,"effect":5}]
					if "lights" in data:
						for light in data["lights"]:
							if dl: self.indiLOG.log(20,"fillShellyDeviceStates, devid:{},  light:{}".format(dev.id,  light) )
							if "overpower" in dev.states and "overpower" in light:
								self.addToStatesUpdateDict(devID, "overpower", light["overpower"])
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


							if dl: self.indiLOG.log(20,"fillShellyDeviceStates mode:{}".format( mode) )
							if mode  == "color":
								if "red" in light and "white" in light:
									rgb = (red + green + blue)/3
									if rgb > 2:  # cut off 1 values, need at least 4 to shine 
										if dl: self.indiLOG.log(20,"fillShellyDeviceStates setting rgb!=0, white and bright to :{}".format( int(white*100./255.)*isOn ) )
										if "whiteLevel" 	 in dev.states: self.addToStatesUpdateDict(devID, "whiteLevel", 	int(rgb*100./255.)*isOn)
										if "brightnessLevel" in dev.states: self.addToStatesUpdateDict(devID, "brightnessLevel",int(rgb*100./255.)*isOn)
									if rgb <=2 and "white" not in light:  # is it off and no white data present?
										if dl: self.indiLOG.log(20,"fillShellyDeviceStates setting rgb<=2, white and bright to :{}".format( 0 ) )
										if "whiteLevel" 	 in dev.states: self.addToStatesUpdateDict(devID, "whiteLevel", 	0)
										if "brightnessLevel" in dev.states: self.addToStatesUpdateDict(devID, "brightnessLevel",0)
									elif "white" in light and rgb <= 2:
										if dl: self.indiLOG.log(20,"fillShellyDeviceStates setting rgb=0, white and bright to :{}".format( int(white*100./255.)*isOn ) )
										if "whiteLevel" 	 in dev.states: self.addToStatesUpdateDict(devID, "whiteLevel", 	int(white*100./255.)*isOn)
										if "brightnessLevel" in dev.states: self.addToStatesUpdateDict(devID, "brightnessLevel",int(white*100./255.)*isOn)
							elif mode  == "white" and "brightness" in light:
								if dl: self.indiLOG.log(20,"fillShellyDeviceStates setting mode=white, using brigthness, white to {} and bright to :{}".format( int(brightness)*isOn, int(brightness)*isOn ) )
								if "brightnessLevel" in dev.states: self.addToStatesUpdateDict(devID, "brightnessLevel", int(brightness)*isOn)
								if "whiteLevel" 	 in dev.states: self.addToStatesUpdateDict(devID, "whiteLevel",      int(brightness)*isOn)
							else:
								pass# bad data 

							if "temp" in light and "whiteTemperature" in dev.states: self.addToStatesUpdateDict(devID, "whiteTemperature", 	light["temp"])

							if dl: self.indiLOG.log(20,"fillShellyDeviceStates setting rgb to {} {} {}".format( int(red*100./255.)*isOn, int(green*100./255.)*isOn, int(blue*100./255.)*isOn ) )
							
							
							if "ison"       in light and "onOffState" in dev.states: 
								#self.indiLOG.log(40,"checking lights  on dev:{}  light ison:{}".format(dev.name, light["ison"]))
								self.addToStatesUpdateDict(devID, "onOffState",	light["ison"] )
								if light["ison"]:	dev.updateStateImageOnServer(indigo.kStateImageSel.DimmerOn)
								else:			dev.updateStateImageOnServer(indigo.kStateImageSel.DimmerOff)
							if "gain"       in light and "gain"       in dev.states: self.addToStatesUpdateDict(devID, "gain", 		light["gain"])

					if "inputs" in data:
						ii = 0
						for input in data["inputs"]:
							if childId > 0 and ii == 1:
								ddd = devChild
								ddp = propsChild
							else:
								ddd = dev
								ddp = props
								self.fillSensor(ddd, ddp, input, "input", "input", decimalPlaces=0)
							ii+=1

					if "relays" in data:
						out = ""
						ii = 0
						ok = 0
						urlFound = False
						for relay in data["relays"]:
							if childId > 0 and ii == 1:
								ddi = str(childId)
								ddd = devChild
								ddp = propsChild
							else:
								ddi = str(dev.id)
								ddd = dev
								ddp = props
							if "ison" in relay:
								self.fillSwitch(ddd, relay, "ison")

							for key in relay:
								if key.find("_url") >-1:
									if relay[key] == None: continue
									if relay[key].find(self.IndigoServerIPNumber+":"+str(self.portOfIndigoServer)+"/")> -1: 
										out = relay[key]
										ok += 100
										urlFound = True
										break
									else:
										ok -= 1

							if urlFound and "report_url" in dev.states:
								#self.indiLOG.log(40,"dev:{};  data:{}".format(dev.id, data))
								#self.indiLOG.log(40,"ok:{},   out:{}".format(ok, out))
								if ok >= 0:
									self.SHELLY[dev.id]["actionDefined"] = True
									self.addToStatesUpdateDict(ddi, "report_url", "ok:{}".format(out))
									ddd.updateStateImageOnServer(indigo.kStateImageSel.PowerOn)
								else:
									self.addToStatesUpdateDict(ddi, "report_url", "setup wrong IP#:port")
									ddd.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
									self.SHELLY[dev.id]["actionDefined"] = False
									#[{u'btn_off_url': u'http://192.168.1.50:7987/off', u'default_state': u'on', u'name': None, u'power': 0.0, u'btn_type': u'toggle', u'btn_on_url': u'http://192.168.1.50:7987/on', u'auto_on': 0.0, u'schedule': False, u'schedule_rules': [], u'ison': True, u'auto_off': 0.0, u'longpush_url': u'http://192.168.1.50:7987/long', u'out_on_url': u'http://1192.168.1.50:7987/on', u'out_off_url': u'http://192.168.1.50:7987/off', u'btn_reverse': 0, u'shortpush_url': u'http://192.168.1.50:7987/short', u'has_timer': False}]
	
							if "overpower" in dev.states and "overpower" in relay:
									self.addToStatesUpdateDict(devID, "overpower", relay["overpower"])

							ii+=1

					if "meters" in data:
						ii = 0
						for meter in data["meters"]:
							if "power" in meter: 
								if childId > 0 and ii == 1:
									ddi = str(childId)
									ddd = devChild
									ddp = propsChild
								else:
									ddi = str(dev.id)
									ddd = dev
									ddp = props
								self.fillSensor(ddd, ddp, meter, "power", "power", decimalPlaces=2)
							ii+=1

					if "emeters" in data:
						ii = 0
						for emeter in data["emeters"]:
							if "power" in emeter: 
								if childId > 0 and ii == 1:
									ddi = str(childId)
									ddd = devChild
									ddp = propsChild
								else:
									ddi = str(dev.id)
									ddd = dev
									ddp = props
								self.fillSensor(ddd, ddp, emeter, "voltage",  "voltage_"+str(ii))
								self.fillSensor(ddd, ddp, emeter, "power",    "power_"+str(ii))
								self.fillSensor(ddd, ddp, emeter, "reactive", "reactive_"+str(ii))
							ii+=1

				if dev.deviceTypeId =="SHWT-1":

					if "flood" in data  and "Flood" in dev.states:
						#self.indiLOG.log(40,"flood: regular data:{}".format(data) )
					
						flood = True if data["flood"]  else False
						if flood == 0 and time.time() - self.SHELLY[dev.id]["lastAlarm"] < 30 and dev.states["sensorValue"] == 1:				
							self.indiLOG.log(40,"flood: regular skipp update, too short a time after alarm")
							pass
						else:
							#self.indiLOG.log(40,"flood: setting trip to green" )
							self.addToStatesUpdateDict(devID, "Flood", "FLOOD" if data["flood"]  else "dry", decimalPlaces="")
							self.addToStatesUpdateDict(devID, "onOffState",flood, decimalPlaces="")
							#self.addToStatesUpdateDict(devID, "sensorValue",flood, decimalPlaces="")
							if flood == "FLOOD":
								self.addToStatesUpdateDict(devID, "lastAlarm",datetime.datetime.now().strftime(_defaultDateStampFormat))
								dev.updateStateImageOnServer(indigo.kStateImageSel.SensorTripped)
							else:
								dev.updateStateImageOnServer(indigo.kStateImageSel.SensorOn)
							self.executeUpdateStatesDict()


		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"data:{}".format(data))
		self.executeUpdateStatesDict()
		self.SHELLY[dev.id]["lastMessageFromDevice"] = time.time()
		self.SHELLY[dev.id]["lastMessageData"] = data



####-------------------------------------------------------------------------####
	def fillSwitch(self, dev, data, token):
		try:
			#self.indiLOG.log(40,"fillSwitch on dev:{}  token:{} ".format(dev.name, data[token]))
			if data[token]: 
				self.addToStatesUpdateDict(dev.id, "onOffState",1)
				dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOn)
			else:
				self.addToStatesUpdateDict(dev.id, "onOffState",0)
				dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOff)
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 

####-------------------------------------------------------------------------####
	def fillSensor(self, dev, props, data, token, state, unit="", decimalPlaces=""):
		try:
			if token in data  and state in dev.states:
				try: 		x = float(data[token])
				except:
					try:	x = float(data[token]["value"])
					except: 
						try: x = float(data[token]["tC"]) 
						except: 
							self.indiLOG.log(40,"fillSensor error  token:{}, data:{}".format(token, data ))
							return 

				if state.find("Temperature") > -1:
					if token not in data: return 
					try:
						if "units" in data[token] and data[token]["units"] !="C":
							x = (x-32.)*5./9.
					except: pass					
					x , xui = self.convTemp(x)
					self.addToStatesUpdateDict(dev.id, state, x, uiValue=xui, decimalPlaces=decimalPlaces)
					if "displaySelect" in props and props["displaySelect"] == "Temperature":
						dev.updateStateImageOnServer(indigo.kStateImageSel.TemperatureSensorOn)
					self.fillMinMaxSensors(dev,state,x,decimalPlaces=decimalPlaces)

				elif state == "Humidity":
					x , xui = self.convHum(x)
					self.addToStatesUpdateDict(dev.id, state, x, uiValue=xui, decimalPlaces=decimalPlaces)
					if "displaySelect" in props and props["displaySelect"] == "Humidity":
						dev.updateStateImageOnServer(indigo.kStateImageSel.HumiditySensorOn)
					self.fillMinMaxSensors(dev,"Humidity",x,decimalPlaces=decimalPlaces)


				else:
					if decimalPlaces == 0:	xui = "{:.0f}{}".format(x,unit.encode("utf8"))
					if decimalPlaces == 1:	xui = "{:.1f}{}".format(x,unit.encode("utf8"))
					if decimalPlaces == 2:	xui = "{:.2f}{}".format(x,unit.encode("utf8"))
					else: 					xui = "{}{}".format(x,unit.encode("utf8"))
					self.addToStatesUpdateDict(dev.id, state, x, uiValue=xui, decimalPlaces=decimalPlaces)


		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40," token:{}, value:{}, calledFrom:{}  data:{}".format(token, calledFrom, data ))
		return 

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
									self.addToStatesUpdateDict(dev.id,ttx+u"MaxYesterday", dev.states[ttx+u"MaxToday"], decimalPlaces = decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MinYesterday", dev.states[ttx+u"MinToday"], decimalPlaces = decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MaxToday",		dev.states[ttx], decimalPlaces = decimalPlaces)
									self.addToStatesUpdateDict(dev.id,ttx+u"MinToday",		dev.states[ttx], decimalPlaces = decimalPlaces)
							self.executeUpdateStatesDict(onlyDevID=dev.id,calledFrom="resetMinMaxSensors")
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
					self.addToStatesUpdateDict(dev.id,stateName+u"MaxToday",	 val, decimalPlaces=decimalPlaces)
				if val < float(dev.states[stateName+u"MinToday"]):
					self.addToStatesUpdateDict(dev.id,stateName+u"MinToday",	 val, decimalPlaces=decimalPlaces)
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return

#



####------------------shelly poller queue management ----------------------------START
####------------------shelly poller queue management ----------------------------START
####------------------shelly poller queue management ----------------------------START


####-------------------------------------------------------------------------####
	def addToShellyPollerQueue(self, shellIndigoDevNumber, page):
		try:
			if self.SHELLY[shellIndigoDevNumber]["state"] != "running":
				self.startShellyDevicePoller("start", shellySelect=shellIndigoDevNumber)
				time.sleep(0.1)
			try: 	self.SHELLY[shellIndigoDevNumber]["queue"].put(page)
			except: 
				self.indiLOG.log(20,"addToShellyPollerQueue error devid:{} shelly:{}".format(shellIndigoDevNumber,self.SHELLY[shellIndigoDevNumber]))

			#self.indiLOG.log(20,"addToShellyPollerQueue added devid:{} page:{} to queue:{}".format(shellIndigoDevNumber, page, list(self.SHELLY[shellIndigoDevNumber]["queue"].queue)))
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return


####-------------------------------------------------------------------------####
	def startShellyDevicePoller(self, state, shellySelect="all"):
		try:
			if state =="start":
				self.laststartUpdateshellyQueues = time.time()
				if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(20, u"starting UpdateshellyQueues for:{} ".format(shellySelect) )
				for shellIndigoDevNumber in self.SHELLY:
					try:
						if not self.SHELLY[shellIndigoDevNumber][u"deviceEnabled"]: 
							continue
					except Exception, e:
						self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
						self.indiLOG.log(40,"shellIndigoDevNumber:{};  SHELLY:{}".format(shellIndigoDevNumber, self.SHELLY))
						continue

					if shellySelect == "all" or shellIndigoDevNumber == shellySelect:
							self.startOneShellyDevicePoller(shellIndigoDevNumber)

			elif state =="restart":
				self.indiLOG.log(20, u"re - starting UpdateshellyQueues for:{} ".format(shellySelect) )
				if (shellySelect == "all" and time.time() - self.laststartUpdateshellyQueues > 70) or shellySelect != "all":
					self.laststartUpdateshellyQueues = time.time()
					for shellIndigoDevNumber in self.SHELLY:
						if not self.SHELLY[shellIndigoDevNumber][u"deviceEnabled"] : continue
						if shellySelect == "all" or shellIndigoDevNumber == shellySelect:
							if time.time() - self.SHELLY[shellIndigoDevNumber]["lastCheck"]> 100:
								self.stopShellyDevicePoller(shellySelect=shellIndigoDevNumber)
								time.sleep(0.5)
							if  time.time() - self.SHELLY[shellIndigoDevNumber]["lastCheck"]> 100:
								self.startOneShellyDevicePoller(shellIndigoDevNumber, reason="active messages pending timeout")
							elif self.SHELLY[shellIndigoDevNumber]["state"]!= "running":
								self.startOneShellyDevicePoller(shellIndigoDevNumber, reason="not running")
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
			self.indiLOG.log(40,"self.SHELLY:{}".format(self.SHELLY))
		return 

####-------------------------------------------------------------------------####
	def startOneShellyDevicePoller(self, shellIndigoDevNumber, reason=""):
		try:
			if shellIndigoDevNumber not in self.SHELLY:
				for dev in indigo.devices.iter(self.pluginId):
					if dev.id == int(shellIndigoDevNumber):
						self.initShelly(dev.id, dev.states["shellyMAC"], dev.address, devType=dev.deviceTypeId, startPoller=False)

			if shellIndigoDevNumber not in self.SHELLY:
					self.indiLOG.log(20, u"no  {} is not in indigo devices, need to create first".format(shellIndigoDevNumber) )
					return 
			
			if self.SHELLY[shellIndigoDevNumber]["state"] == "running":
					if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(20, u"no need to start Thread, ipnumber {} thread already running".format(self.SHELLY[shellIndigoDevNumber]["ipNumber"]) )
					return 

			if self.decideMyLog(u"SetupDevices"): self.indiLOG.log(20, u" .. (re)starting   thread for ipnumber:{}, state was: {}; reason:{}".format(self.SHELLY[shellIndigoDevNumber]["ipNumber"], self.SHELLY[shellIndigoDevNumber]["state"], reason) )
			self.SHELLY[shellIndigoDevNumber]["lastCheck"]= time.time()
			self.SHELLY[shellIndigoDevNumber]["state"]	= "start"
			self.sleep(0.1)
			self.SHELLY[shellIndigoDevNumber]["thread"] = threading.Thread(name=u'self.shellyPollerThread', target=self.shellyPollerThread, args=(shellIndigoDevNumber,))
			self.SHELLY[shellIndigoDevNumber]["thread"].start()
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
			for shellIndigoDevNumber in self.SHELLY:
				self.stopOneShellyDevicePoller(shellIndigoDevNumber, reason="")
		return 
###-------------------------------------------------------------------------####
	def stopOneShellyDevicePoller(self, shellIndigoDevNumber, reason=""):
		if shellIndigoDevNumber in self.SHELLY:
			self.SHELLY[shellIndigoDevNumber]["state"]	= "stop "+reason
			self.SHELLY[shellIndigoDevNumber]["reset"]	= True
		return 
####-------------------------------------------------------------------------####
	def resetUpdateQueue(self, ipnumber):
		self.SHELLY[shellIndigoDevNumber]["reset"]= True
		return
####-------------------------------------------------------------------------####
	def testIfAlreadyInQ(self, page, ipnumber):
		currentQueue = list(self.SHELLY[shellIndigoDevNumber]["queue"].queue)
		for q in currentQueue:
			if q == page:
				if self.decideMyLog(u"Polling"): self.indiLOG.log(10, u"NOT adding to update list already presend {}".format(next) )
				return True
		return False

####-------------------------------------------------------------------------####
	def shellyPollerThread(self, shellIndigoDevNumber):
		try:
			self.SHELLY[shellIndigoDevNumber]["state"] = "running"
			if self.decideMyLog(u"Polling"): self.indiLOG.log(20, u"shellyPollerThread starting  for devId:{}; ipnumber# {}".format(shellIndigoDevNumber, self.SHELLY[shellIndigoDevNumber]["ipNumber"]) )
			tries 		= 0
			retryTime 	= .0
			lastDefault = time.time()

			lastEXE = time.time()
			while self.SHELLY[shellIndigoDevNumber]["state"] != "stop":
				self.SHELLY[shellIndigoDevNumber]["lastCheck"] = time.time()
				addBack =[]
				ipNumber = self.SHELLY[shellIndigoDevNumber]["ipNumber"]

				waitStart = time.time()
				for ii in range(1000):
					if time.time() - waitStart > 0.2 + retryTime: break
					time.sleep(0.2 + retryTime)
					try:
						if ipNumber != self.SHELLY[shellIndigoDevNumber]["ipNumber"]:
							ipNumber = self.SHELLY[shellIndigoDevNumber]["ipNumber"]
							break
					except: 
						# this device has been removed, exit thread
						if shellIndigoDevNumber not in self.SHELLY:
							return 

				if shellIndigoDevNumber not in self.SHELLY: break

				if not self.isValidIP(ipNumber): 
					retryTime = 1
					continue

				defaultTask 	 = self.SHELLY[shellIndigoDevNumber]["defaultTask"]
				pollingFrequency = self.SHELLY[shellIndigoDevNumber]["pollingFrequency"]
				if pollingFrequency == -1:
					pollingFrequency = 10
					if self.SHELLY[shellIndigoDevNumber]["actionDefined"]:
						pollingFrequency = 30
					elif self.SHELLY[shellIndigoDevNumber]["devType"] in _supportsBatteryLevel: 
						pollingFrequency = 12

					

				while not self.SHELLY[shellIndigoDevNumber]["queue"].empty() or (time.time() - lastDefault) > pollingFrequency:
					lastDefault = time.time()
					self.SHELLY[shellIndigoDevNumber]["lastActive"] = time.time()

					if not self.SHELLY[shellIndigoDevNumber]["queue"].empty(): 
						page = self.SHELLY[shellIndigoDevNumber]["queue"].get()
						fromQueue = True
					else:
						page = defaultTask
						fromQueue = False

					if self.decideMyLog(u"Special"): self.indiLOG.log(20, u"shellyPollerThread  ip{}; wait:{:.1f}; default wait:{}  page:{}".format(ipNumber, time.time()-lastEXE, pollingFrequency, page ) )
					lastEXE = time.time()

					if not self.SHELLY[shellIndigoDevNumber][u"deviceEnabled"]: 		
						if self.decideMyLog(u"Polling"): self.indiLOG.log(20, u"shellyPollerThread  {}; skipping:{} is OFF".format(shellIndigoDevNumber, ipNumber) )
						self.SHELLY[shellIndigoDevNumber]["reset"]= True
						break

					if False and self.decideMyLog(u"Polling"): self.indiLOG.log(10, u"shellyPollerThread  {};  executing:{}   {}".format(shellIndigoDevNumber, ipNumber, page) )

					if self.SHELLY[shellIndigoDevNumber][u"ipNumber"] == "": 	
						if self.decideMyLog(u"Polling"): self.indiLOG.log(20, u"shellyPollerThread {}; skipping:{}  ip set blank".format(shellIndigoDevNumber, ipNumber)  )
						continue

					if self.SHELLY[shellIndigoDevNumber]["reset"]: 
						if self.decideMyLog(u"Polling"): self.indiLOG.log(20, u"shellyPollerThread  {}; resetting:{} queue data".format(shellIndigoDevNumber, ipNumber) )
						continue

					#if self.decideMyLog(u"Polling"): self.indiLOG.log(20, u" send to ipNumber:{}  page:{}".format(ipNumber, page) )
					retCode, jData = self.execShellySend(ipNumber, page)

					if retCode ==0: # all ok?
						self.addtoAnalyzePollerQueue({"shellIndigoDevNumber":shellIndigoDevNumber,"page":page,"ipNumber":ipNumber,"data": jData})
						if shellIndigoDevNumber == 0: 
							self.SHELLY[shellIndigoDevNumber]["ipNumber"] = ""
						tries      = 0
						retryTime  = 0.
						continue

					else: # no response, retry ..
						tries      +=1
						retryTime  = 2

						if tries  > 5 and tries < 10: # wait a little longer
							if self.decideMyLog(u"Polling"): self.indiLOG.log(20, u"last querry were not successful wait, then try again")
							retryTime = 5

						if tries  > 20:
							if self.decideMyLog(u"Polling"): self.indiLOG.log(20, u"last querry were not successful  skip")
							retryTime = 0
							break

						if fromQueue: addBack.append(page)
					if shellIndigoDevNumber not in self.SHELLY: break

				try: 	self.SHELLY[shellIndigoDevNumber]["queue"].task_done()
				except: pass
				if addBack !=[]:
					for nxt in addBack:
						self.SHELLY[shellIndigoDevNumber]["queue"].put(nxt)
				self.SHELLY[shellIndigoDevNumber]["reset"]=False

		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		self.indiLOG.log(20, u"ip#: {}  devID:{}; update thread stopped, state was:{}".format(ipNumber, shellIndigoDevNumber, self.SHELLY[shellIndigoDevNumber]["state"]) )
		self.SHELLY[shellIndigoDevNumber]["state"]= "stopped - exiting thread"
		return



####-------------------------------------------------------------------------####
	def execShellySend(self,  ipNumber, page, endAction="repeatUntilFinished"):
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
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return 1, ret


####-------------------------------------------------------------------------####
	def testPing(self, ipN):
		try:
			ss = time.time()
			ret = subprocess.call(u"/sbin/ping  -c 1 -W 40 -o " + ipN, shell=True) # send max 2 packets, wait 40 msec   if one gets back stop
			if self.decideMyLog(u"Ping"): self.indiLOG.log(10, u" sbin/ping  -c 1 -W 40 -o {} return-code: {}".format(ipN, ret) )

			#indigo.server.log(  ipN+"-1  "+ unicode(ret) +"  "+ unicode(time.time() - ss)  )

			if int(ret) ==0:  return 0
			self.sleep(0.1)
			ret = subprocess.call(u"/sbin/ping  -c 1 -W 400 -o " + ipN, shell=True)
			if self.decideMyLog(u"Ping"): self.indiLOG.log(10, "/sbin/ping  -c 1 -W 400 -o {} ret-code: ".format(ipN, ret) )

			#indigo.server.log(  ipN+"-2  "+ unicode(ret) +"  "+ unicode(time.time() - ss)  )

			if int(ret) ==0:  return 0
			return 1
		except Exception, e:
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
			# Query hardware module (dev) for its current status here:
			try:
				devId = dev.id

				if devId not in self.SHELLY: return 

				page = "settings"
				if self.decideMyLog(u"Actions"): self.indiLOG.log(20,"sending to dev{} page={}".format(dev.name.encode("utf8"), page))
				self.addToShellyPollerQueue( devId, page)
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
				dev.updateStateImageOnServer(indigo.kStateImageSel.PowerOon)

		self.executeUpdateStatesDict()



# noinspection SpellCheckingInspection
	def actionControlDimmerRelay(self, action, dev):
		try:
			devId = dev.id
			if self.decideMyLog(u"Actions"): self.indiLOG.log(20,"devId {} ation={}; values:{}".format(devId, action.deviceAction, action.actionValue))

			if devId  in self.CHILDRENtoParents:
				devId = self.CHILDRENtoParents[dev.id]
			if devId not in self.SHELLY: return 

			setAction = False
			actionValues ={}
			IndigoStateMapToShellyDev ={'redLevel':"red", 'greenLevel':"green", 'blueLevel':"blue", 'whiteLevel':"white", "brightnessLevel":"brightness", "whiteTemperature":"temp","TurnOff":"turn","TurnOn":"turn"}

			page = ""
			extraPage = ""

			if dev.deviceTypeId in ["SHBLB-1","SHRGBW2","SHDM-1"]:
				## ["SupportsColor", "SupportsRGB", "SupportsWhite", "SupportsWhiteTemperature", "SupportsRGBandWhiteSimultaneously", "SupportsTwoWhiteLevels" "SupportsTwoWhiteLevelsSimultaneously"]

				if dev.deviceTypeId == "SHDM-1": mode ="white"
				else:							 mode = dev.states["mode"] # == white or color

				onOffState = 0
				if "onOffState" in dev.states:
					if dev.states["onOffState"]: onOffState = 1
					else:					 	 onOffState = -1

				rgbLimits = _emptyProps[dev.deviceTypeId]["rgbLimits"]
				tempLimits = _emptyProps[dev.deviceTypeId]["tempLimits"]

				if action.deviceAction == indigo.kDeviceAction.SetColorLevels:
					actionValues = action.actionValue
					setAction = True

				if "gredLevel" in actionValues or "redLevel" in actionValues or "blueLevel" in actionValues:
						if mode != "color": extraPage = "settings?mode=color"
						actionValues["whiteLevel"] 	= 0

				elif "whiteLevel" in actionValues :
						if mode != "color": extraPage = "settings?mode=color"
						actionValues["redLevel"] 	= 0
						actionValues["greenLevel"] 	= 0
						actionValues["blueLevel"] 	= 0

				elif "whiteTemperature" in actionValues:
					if mode == "color": extraPage = "settings?mode=white"
					try: actionValues["brightnessLevel"] = int(dev.states["whiteLevel"])
					except: pass
					setAction = True

				elif "brightnessLevel" in actionValues:
					if mode == "color": extraPage = "settings?mode=white"
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
					newOnState = not dev.onState
					if newOnState: 	actionValues["TurnOff"] = "off"
					else: 			actionValues["TurnOn"] 	= "on"
					setAction = True

					###### SET BRIGHTNESS ######
				if action.deviceAction == indigo.kDimmerRelayAction.SetBrightness:
					if mode == "color":
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
					if mode == "color":
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
					if mode == "color":
						actionValues["redLevel"] 	= newBrightness
						actionValues["greenLevel"] 	= newBrightness
						actionValues["blueLevel"] 	= newBrightness
						actionValues["whiteLevel"] 	= 0
					else:
						actionValues["brightnessLevel"]	= newBrightness
					setAction = True

				if self.decideMyLog(u"Actions"): self.indiLOG.log(20,"sending actionValues={}".format(actionValues))
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
										if colorAction == "whiteTemperature": # this requires to be in white mode
											page += "{}={}&".format(IndigoStateMapToShellyDev[colorAction], int(min(tempLimits[1],max(tempLimits[0],actionValues[colorAction]))))
										elif colorAction == "whiteLevel":
											page += "{}={}&".format(IndigoStateMapToShellyDev[colorAction], int(min(rgbLimits[1],max(rgbLimits[0],actionValues[colorAction]*255/100.))))
										elif colorAction == "brightnessLevel":
											page += "{}={}&".format(IndigoStateMapToShellyDev[colorAction], int(min(100,         max(1,actionValues[colorAction]))))
										else:
											page += "{}={}&".format(IndigoStateMapToShellyDev[colorAction], int(min(rgbLimits[1],max(rgbLimits[0],actionValues[colorAction]*255/100.))))


			elif dev.deviceTypeId in ["SHSW-1","SHSW-PM","SHSW-25","SHEM"]:
				if True:							 mode = "0"
				if dev.id in self.CHILDRENtoParents: mode = "1"
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
					newOnState = not dev.onState
					if newOnState: 	actionValues["TurnOff"] 	= "off"
					else: 			actionValues["TurnOn"] 	= "on"
					setAction = True
				if setAction:
						for colorAction in IndigoStateMapToShellyDev:	
							if colorAction in actionValues:
									page += "{}={}&".format("turn", actionValues[colorAction])
				if self.decideMyLog(u"Actions"): self.indiLOG.log(20,"dev {}  mode:{};  page:{} devType:{};  CHILDRENtoParents:{}".format(dev.name, mode, page, dev.deviceTypeId, self.CHILDRENtoParents))
			else:
				self.indiLOG.log(40,"action{}  for {}  not implemented".format(dev.name, actionControlDimmerRelay))


			if len(page) > 0:
				if extraPage !="":
					self.addToShellyPollerQueue( devId, extraPage)
					time.sleep(0.2)

				page = page.strip("&")
				page = _emptyProps[dev.deviceTypeId]["setPage"][mode]+page			
				if self.decideMyLog(u"Actions"): self.indiLOG.log(20,"sending dev:{} ={}".format(dev.name, page))
				self.addToShellyPollerQueue( devId, page)

			else:
				return

			return
		except Exception, e:
			self.indiLOG.log(40,"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
		return






##############################################################################################

	####-----------------	 ---------
	def getJsonFromDevices(self, ipNumber, page, jsonAction=""):

		try:
			#if self.decideMyLog(u"Polling"): self.indiLOG.log(20,"getJsonFromDevices: ip:{} page:{}".format(ipNumber, page) )
			if not self.isValidIP(ipNumber): return {}


			if self.useCurlOrPymethod.find("curl") > -1:
				if len(self.userIDOfShellyDevices) >0:
					UID= " -u "+self.userIDOfShellyDevices+":"+str(self.passwordOfShellyDevices)
				else: UID =""
				cmdR  = self.unfiCurl+UID+" 'http://"+ipNumber+":"+str(self.portOfShellyDevices)+"/"+page+"'"

				if self.decideMyLog(u"Polling"): self.indiLOG.log(20,"Connection: "+cmdR )
				try:
					ret = subprocess.Popen(cmdR, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True).communicate()
					try:
						jj = json.loads(ret[0])
					except :
						self.indiLOG.log(40,"Shelly repose from {}  no json object returned: {}".format(ret[0], ret[0]))
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
				url = "http://"+ipNumber+":"+str(self.portOfShellyDevices)+"/"+page

				try:
						if len(self.userIDOfShellyDevices) >0:
							resp = requests.get(url,auth=(self.userIDOfShellyDevices, self.passwordOfShellyDevices))
						else:
							resp = requests.get(url)
  
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
			#if "1929700622" in self.updateStatesDict: self.indiLOG.log(10, u"executeUpdateStatesList calledfrom: "+calledFrom +"; onlyDevID: " +onlyDevID +"; updateStatesList: " +unicode(self.updateStatesDict))
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
				if devId =="0": continue
				devID = int(devId)
				oneNew = False
				if len(local[devId]) > 0:
					changedOnly = []
					dev = indigo.devices[devID]
					props = dev.pluginProps
					for state in local[devId]:
						if not local[devId][state]["force"]: 
							if dev.states[state] == local[devId][state]["value"] : continue
						dd = {u"key":state, "value":local[devId][state]["value"]}
						if local[devId][state]["uiValue"]		!="": dd["uiValue"]			= local[devId][state]["uiValue"]
						if local[devId][state]["decimalPlaces"]	!="": dd["decimalPlaces"]	= local[devId][state]["decimalPlaces"]
						if state !="lastMessageFromDevice": oneNew = True
						changedOnly.append(dd)
						#self.indiLOG.log(40,"adding status dev:{}; state:{} dd:{}".format(dev.name.encode("utf8"), state, changedOnly ) )

						if  "displaySelect" in props and props["displaySelect"] == state:
							if "SupportsSensorValue" in props and props["SupportsSensorValue"]:
								xx = copy.copy(dd)
								xx["key"] = "sensorValue"
								changedOnly.append(xx)
					if oneNew:
						dd = {u"key":"lastStatusChange", "value":dateString}
						changedOnly.append(dd)
						#self.indiLOG.log(40,"adding status dev:{}; state:{} dd:{}".format(dev.name.encode("utf8"), state, changedOnly ) )
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
		self.myLog( text="myLogSet setting parameters -- logFileActive= {}; logFile= {};  debug plugin:{}".format(self.logFileActive, self.logFile, self.debugLevel) , destination="standard")



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

	####-----------------  print to logfile or indigo log  ---------
	def myLog(self,	 text="", mType="", errorType="", showDate=True, destination=""):
		   

		try:
			if	self.logFileActive =="standard" or destination.find("standard") >-1:
				if errorType == u"smallErr":
					self.indiLOG.error(u"------------------------------------------------------------------------------")
					self.indiLOG.error(text.encode(u"utf8"))
					self.indiLOG.error(u"------------------------------------------------------------------------------")

				elif errorType == u"bigErr":
					self.indiLOG.error(u"==================================================================================")
					self.indiLOG.error(text.encode(u"utf8"))
					self.indiLOG.error(u"==================================================================================")

				elif mType == "":
					indigo.server.log(text)
				else:
					indigo.server.log(text, type=mType)


			if	self.logFileActive !="standard":

				ts =""
				try:
					if len(self.logFile) < 3: return # not properly defined
					f =  open(self.logFile,"a")
				except Exception, e:
					indigo.server.log(u"Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
					try:
						f.close()
					except:
						pass
					return
			
				if errorType == u"smallErr":
					if showDate: ts = datetime.datetime.now().strftime(u"%H:%M:%S")
					f.write(u"----------------------------------------------------------------------------------\n")
					f.write((ts+u" ".ljust(12)+u"-"+text+u"\n").encode(u"utf8"))
					f.write(u"----------------------------------------------------------------------------------\n")
					f.close()
					return

				if errorType == u"bigErr":
					if showDate: ts = datetime.datetime.now().strftime(u"%H:%M:%S")
					f.write(u"==================================================================================\n")
					f.write((ts+u" "+u" ".ljust(12)+u"-"+text+u"\n").encode(u"utf8"))
					f.write(u"==================================================================================\n")
					f.close()
					return
				if showDate: ts = datetime.datetime.now().strftime(u"%H:%M:%S")
				if mType == u"":
					f.write((ts+u" " +u" ".ljust(25)  +u"-" + text + u"\n").encode("utf8"))
					#indigo.server.log((ts+u" " +u" ".ljust(25)  +u"-" + text + u"\n").encode("utf8"))
				else:
					f.write((ts+u" " +mType.ljust(25) +u"-" + text + u"\n").encode("utf8"))
					#indigo.server.log((ts+u" " +mType.ljust(25) +u"-" + text + u"\n").encode("utf8"))
				f.close()
				return


		except	Exception, e:
			if len(unicode(e)) > 5:
				self.indiLOG.log(50,u"myLog Line {} has error={}".format(sys.exc_traceback.tb_lineno, e))
				indigo.server.log(text)
				try: f.close()
				except: pass


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
	def startHTTPListening(self):
		try:
			self.indiLOG.log(20, u" ..   starting HTTP listener on port:{} ".format(self.portOfIndigoServer) )

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




