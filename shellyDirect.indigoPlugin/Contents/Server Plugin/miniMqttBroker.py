#! /Library/Frameworks/Python.framework/Versions/Current/bin/python3
# -*- coding: utf-8 -*-
####################
# shellyDirect Plugin,  minimal built in MQTT broker
# Developed by Karl Wachs
#
# minimal MQTT 3.1.1 broker, stdlib socket only, NO module to install, NO external broker needed.
# the shelly gen2 devices connect to it (MQTT server = indigo-ip:port in the device settings)
# and publish their status / events. the broker only RECEIVES, it implements exactly that:
#	accept, CONNECT (optional user/password), PUBLISH qos 0/1/2, SUBSCRIBE/UNSUBSCRIBE (acked, nothing is
#	ever delivered), PINGREQ, DISCONNECT, keepalive timeout, same client id reconnect replaces old connection.
# not implemented on purpose: forwarding messages to subscribers, retained messages, will, TLS, sessions.
#
# callbacks, all called from the connection threads:
#	on_connect(clientIp, clientId)
#	on_disconnect(clientIp, clientId, reason)
#	on_message(clientIp, clientId, topic, payload)		payload is bytes
#	on_idle(clientIp, clientId)							about every second while connected
import socket
import struct
import threading
import time


def encodeLength(n):
	out = b""
	while True:
		b1 = n % 128
		n //= 128
		if n > 0:	out += bytes([b1 | 0x80])
		else:		out += bytes([b1]); break
	return out


def decodeString(data, pos):
	"""returns (string, next position)"""
	ln = struct.unpack("!H", data[pos:pos+2])[0]
	return data[pos+2:pos+2+ln].decode("utf-8", "replace"), pos+2+ln


class MqttConnection:
	def __init__(self, broker, sock, address):
		self.broker			= broker
		self.sock			= sock
		self.clientIp		= address[0]
		self.clientId		= ""
		self.keepalive		= 60
		self.running		= True
		self.replaced		= False	# true when the same client id connected again, then no on_disconnect for this one
		self.kPacketTimeout	= 20	# secs to finish reading a packet that has started

	####-----------------  wire format  ---------
	def send(self, data):
		self.sock.sendall(data)

	def readByte(self, deadline=0):
		"""once a packet has started we must finish it, a timeout mid packet is not the end of it"""
		while True:
			try:
				b1 = self.sock.recv(1)
				if b1 == b"": raise IOError("connection closed by client")
				return b1[0]
			except	socket.timeout:
				if deadline == 0 or time.time() > deadline: raise

	def readExactly(self, n, deadline=0):
		out = b""
		while len(out) < n:
			try:
				chunk = self.sock.recv(n - len(out))
				if chunk == b"": raise IOError("connection closed by client")
				out += chunk
			except	socket.timeout:
				if deadline == 0 or time.time() > deadline: raise
		return out

	def readPacket(self):
		"""returns (packetType, flags, payloadBytes), None when nothing arrived"""
		try:	header = self.readByte()
		except	socket.timeout: return None
		deadline = time.time() + self.kPacketTimeout
		length, multiplier = 0, 1
		while True:
			b1 = self.readByte(deadline=deadline)
			length += (b1 & 0x7F) * multiplier
			if b1 & 0x80 == 0: break
			multiplier *= 128
			if multiplier > 128 ** 3: raise IOError("bad remaining length")
		if length > self.broker.maxPacketSize: raise IOError("packet too large: {}".format(length))
		return header >> 4, header & 0x0F, self.readExactly(length, deadline=deadline)

	####-----------------  packets  ---------
	def handleConnect(self, data):
		protocol, pos = decodeString(data, 0)
		level	= data[pos]
		flags	= data[pos+1]
		self.keepalive = struct.unpack("!H", data[pos+2:pos+4])[0]
		pos += 4
		self.clientId, pos = decodeString(data, pos)
		if flags & 0x04:	# will topic + message, accepted and ignored
			dummy, pos = decodeString(data, pos)
			ln = struct.unpack("!H", data[pos:pos+2])[0]
			pos += 2 + ln
		user, password = "", ""
		if flags & 0x80: user, pos = decodeString(data, pos)
		if flags & 0x40: password, pos = decodeString(data, pos)

		if protocol not in ["MQTT", "MQIsdp"] or level not in [3, 4]:
			self.send(b"\x20\x02\x00\x01")			# CONNACK wrong protocol version
			raise IOError("wrong protocol {} level {}".format(protocol, level))
		if self.broker.user != "" and (user != self.broker.user or password != self.broker.password):
			self.send(b"\x20\x02\x00\x04")			# CONNACK bad user name or password
			raise IOError("bad user name or password from client id:{}".format(self.clientId))
		if self.clientId == "": self.clientId = "ip-{}".format(self.clientIp)
		self.send(b"\x20\x02\x00\x00")				# CONNACK ok
		self.broker.registerClient(self)
		if self.broker.on_connect is not None: self.broker.on_connect(self.clientIp, self.clientId)

	def handlePublish(self, flags, data):
		qos = (flags >> 1) & 0x03
		topic, pos = decodeString(data, 0)
		if qos > 0:
			packetId = data[pos:pos+2]
			pos += 2
			if   qos == 1: self.send(b"\x40\x02" + packetId)	# PUBACK
			elif qos == 2: self.send(b"\x50\x02" + packetId)	# PUBREC, client answers with PUBREL
		if self.broker.on_message is not None:
			self.broker.on_message(self.clientIp, self.clientId, topic, data[pos:])

	def handleSubscribe(self, data):
		packetId = data[0:2]
		pos = 2
		codes = b""
		while pos < len(data):
			dummy, pos = decodeString(data, pos)
			pos += 1		# requested qos
			codes += b"\x00"	# granted qos 0, nothing is ever sent anyway
		self.send(b"\x90" + encodeLength(2 + len(codes)) + packetId + codes)

	####-----------------  read loop  ---------
	def loop(self):
		reason = "stopped"
		connected = False
		try:
			self.sock.settimeout(1.0)
			lastRx = time.time()
			while self.running and self.broker.running:
				packet = self.readPacket()
				if packet is None:
					if not connected and time.time() - lastRx > 10:	raise IOError("no CONNECT within 10 secs")
					# client must send something within keepalive, allow 1.5 x as the spec says
					if self.keepalive > 0 and time.time() - lastRx > self.keepalive * 1.5: raise IOError("keepalive timeout")
					if connected and self.broker.on_idle is not None: self.broker.on_idle(self.clientIp, self.clientId)
					continue
				lastRx = time.time()
				packetType, flags, data = packet
				if not connected:
					if packetType != 1: raise IOError("first packet is not CONNECT")
					self.handleConnect(data)
					connected = True
				elif packetType == 3:	self.handlePublish(flags, data)
				elif packetType == 6:	self.send(b"\x70\x02" + data[0:2])		# PUBREL --> PUBCOMP
				elif packetType == 8:	self.handleSubscribe(data)
				elif packetType == 10:	self.send(b"\xb0\x02" + data[0:2])		# UNSUBSCRIBE --> UNSUBACK
				elif packetType == 12:	self.send(b"\xd0\x00")					# PINGREQ --> PINGRESP
				elif packetType == 14:	reason = "disconnect from client"; break
		except	Exception as e:
			reason = str(e)
		self.close()
		self.broker.unregisterClient(self)
		if connected and not self.replaced and self.broker.on_disconnect is not None: self.broker.on_disconnect(self.clientIp, self.clientId, reason)

	def close(self):
		self.running = False
		try:	self.sock.close()
		except:	pass


class MqttBroker:
	def __init__(self, port=1883, user="", password=""):
		self.port			= int(port)
		self.user			= user
		self.password		= password
		self.on_connect		= None
		self.on_disconnect	= None
		self.on_message		= None
		self.on_idle		= None
		self.running		= False
		self.lsock			= None
		self.thread			= None
		self.clients		= dict()	# client id --> MqttConnection
		self.lock			= threading.Lock()
		self.maxClients		= 100
		self.maxPacketSize	= 256 * 1024
		self.lastError		= ""

	def start(self):
		"""opens the listening port, raises if the port is in use"""
		self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.lsock.bind(("", self.port))
		self.lsock.listen(20)
		self.lsock.settimeout(1.0)
		self.running = True
		self.thread = threading.Thread(name="miniMqttBroker", target=self.acceptLoop, daemon=True)
		self.thread.start()

	def stop(self):
		self.running = False
		try:	self.lsock.close()
		except:	pass
		with self.lock:
			conns = list(self.clients.values())
		for conn in conns: conn.close()
		if self.thread is not None: self.thread.join(timeout=5)

	def acceptLoop(self):
		while self.running:
			try:
				sock, address = self.lsock.accept()
			except	socket.timeout:
				continue
			except	Exception as e:
				if self.running: self.lastError = str(e)
				time.sleep(1)
				continue
			with self.lock:
				tooMany = len(self.clients) >= self.maxClients
			if tooMany:
				try:	sock.close()
				except:	pass
				continue
			conn = MqttConnection(self, sock, address)
			threading.Thread(name="miniMqttBroker-conn", target=conn.loop, daemon=True).start()

	def registerClient(self, conn):
		# same client id again (device rebooted, network hick up): the old connection is replaced
		with self.lock:
			old = self.clients.get(conn.clientId)
			self.clients[conn.clientId] = conn
		if old is not None and old is not conn:
			old.replaced = True
			old.close()

	def unregisterClient(self, conn):
		with self.lock:
			if self.clients.get(conn.clientId) is conn: del self.clients[conn.clientId]

	def connectedClients(self):
		with self.lock:
			return [(conn.clientIp, conn.clientId) for conn in self.clients.values()]
