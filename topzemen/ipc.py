#!/usr/bin/python3
#
##############################################################################################
#
# TopZemen - Floating Pictures on your Screen
#
# For updates see git-repo at
# https://github.com/pronopython/topzemen
#
##############################################################################################
#
# Copyright (C) 2023 PronoPython
#
# Contact me at pronopython@proton.me
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################################
#

import threading
from multiprocessing.connection import Listener
from multiprocessing.connection import Client
from time import sleep


class IpcMessageService:

	CALLBACK_MESSAGE = 0
	CALLBACK_FUNCTION = 1

	def __init__(self) -> None:
		self.callbacks = []
		self.__messages_to_send = []
		self.__messages_to_send_lock = threading.Lock()
		self.__received_messages = []
		self.__received_messages_lock = threading.Lock()

	def listen(self, message, callback_function):
		self.callbacks.append((message, callback_function))

	def send(self, message: str):
		self.__messages_to_send_lock.acquire()
		self.__messages_to_send.append(message)
		self.__messages_to_send_lock.release()

	def get_next_message_to_send(self):
		self.__messages_to_send_lock.acquire()
		if len(self.__messages_to_send) > 0:
			message_to_send = self.__messages_to_send.pop()
		else:
			message_to_send = None
		self.__messages_to_send_lock.release()
		return message_to_send

	def add_received_message(self, message):
		self.__received_messages_lock.acquire()
		self.__received_messages.append(message)
		self.__received_messages_lock.release()

	def handleMessages(self, name=""):
		self.__received_messages_lock.acquire()
		new_messages = self.__received_messages.copy()
		self.__received_messages.clear()
		self.__received_messages_lock.release()

		for message in new_messages:
			#print(name + "handle msg", message)
			for callback in self.callbacks:
				if message == callback[IpcMessageService.CALLBACK_MESSAGE]:
					callback[IpcMessageService.CALLBACK_FUNCTION]()


class IpcMessageClient(IpcMessageService):

	STATUS_NOT_CONNECTED = 0
	STATUS_CONNECTED = 1

	def __init__(self) -> None:
		super().__init__()
		self.thread: threading.Thread = None  # type: ignore
		self.running = False
		self.loop_running = False
		self.status = IpcMessageClient.STATUS_NOT_CONNECTED

	def client_loop(self):

		self.running = True
		self.loop_running = True
		conn = None
		while self.running:

			if conn == None:
				try:
					conn = Client(("localhost", 6000), authkey=b"topzemen_ipc")
				except ConnectionRefusedError:
					sleep(1)
					continue

			try:
				message_to_send = self.get_next_message_to_send()
				if message_to_send != None:
					conn.send(message_to_send)

				while conn.poll():
					message = conn.recv()
					self.add_received_message(message)

				self.handleMessages()

			except EOFError:
				# got disconnected
				conn.close()
				conn = None
			except ConnectionResetError:
				# got disconnected
				conn.close()
				conn = None

			sleep(0.05)

		if conn != None:
			conn.close()

		self.loop_running = True

	def run(self) -> None:
		self.thread = threading.Thread(target=self.client_loop, args=())
		self.thread.daemon = True  # so these threads get killed when program exits
		self.thread.start()

	def is_running(self) -> bool:
		return self.thread.is_alive()

	def close(self) -> None:
		if not self.is_running():
			self.thread.join()

	def stop(self):
		self.running = False
		while self.loop_running:
			sleep(0.06)
		self.close()
		print("Message client stopped")


class IpcMessageBroker(IpcMessageService):
	def __init__(self) -> None:
		super().__init__()
		self.broker_thread: threading.Thread = None  # type: ignore
		self.accept_thread: threading.Thread = None  # type: ignore
		self.running = False
		self.broker_loop_running = False
		self.accept_loop_running = False
		self.connections = []
		self.listener = None

	def connections_accept_loop(self):
		print("connections accept loop started...")

		self.running = True
		self.accept_loop_running = True

		while self.running:
			if self.listener != None:
				conn = self.listener.accept()
				id = self.listener.last_accepted
				self.connections.append((conn, id))
				print("connection accepted from", id)
			sleep(0.2)
		self.accept_loop_running = False

	def broker_loop(self):
		print("Broker started...")
		self.listener = Listener(("localhost", 6000), authkey=b"topzemen_ipc")
		self.running = True
		self.broker_loop_running = True

		messages_to_broker = []

		while self.running:
			for connection, id in self.connections:
				try:
					if connection.poll():
						msg = connection.recv()
						messages_to_broker.append(msg)
				except EOFError:
					# self.connections.remove(connection)
					pass
				except ConnectionResetError:
					# got disconnected
					pass

			next_own_message = self.get_next_message_to_send()
			if next_own_message != None:
				messages_to_broker.append(next_own_message)

			if len(messages_to_broker) > 0:
				for connection, id in self.connections:
					try:
						for msg in messages_to_broker:
							connection.send(msg)
					except EOFError:
						# self.connections.remove(connection)
						pass
					except BrokenPipeError:
						pass
					except ConnectionResetError:
						# got disconnected
						pass
				for msg in messages_to_broker:
					self.add_received_message(msg)
				messages_to_broker.clear()

			self.handleMessages("Broker:")

			sleep(0.02)
		self.listener.close()
		self.broker_loop_running = False

	def run(self) -> None:
		self.broker_thread = threading.Thread(target=self.broker_loop, args=())
		self.broker_thread.daemon = (
			True  # so these threads get killed when program exits
		)
		self.broker_thread.start()
		self.accept_thread = threading.Thread(
			target=self.connections_accept_loop, args=()
		)
		self.accept_thread.daemon = (
			True  # so these threads get killed when program exits
		)
		self.accept_thread.start()

	def is_running(self) -> bool:
		return self.broker_thread.is_alive() and self.accept_thread.is_alive()

	def close(self) -> None:
		if not self.is_running():
			self.broker_thread.join()
			self.accept_thread.join()

	def stop(self):
		self.running = False
		while self.broker_loop_running or self.accept_loop_running:
			sleep(0.06)
		self.close()
		print("Message broker stopped")
