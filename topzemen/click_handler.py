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
from time import sleep, time


class ClickHandler:

	LEFT_BUTTON = 1
	RIGHT_BUTTON = 3
	MIDDLE_BUTTON = 2

	LAST_CLICK_WAIT_TIME_IN_MS = 500

	CLICK_EVENT_BUTTON = 0
	CLICK_EVENT_TIME = 1

	CALLBACK_CLICK_SEQUENCE = 0
	CALLBACK_FUNCTION = 1

	def __init__(self) -> None:
		self.thread: threading.Thread = None  # type: ignore

		self.click_events = []
		self.callbacks = []

		self.running = False
		self.loop_running = False

	def click_handler_loop(self):

		self.running = True
		self.loop_running = True

		while self.running:
			sleep(0.01)
			now = self.milli_time()
			if len(self.click_events) > 0:
				last_click_time = self.click_events[len(self.click_events) - 1][
					ClickHandler.CLICK_EVENT_TIME
				]
				if last_click_time + ClickHandler.LAST_CLICK_WAIT_TIME_IN_MS < now:
					self.handle_clicks(self.click_events)
					self.remove_clicks()
		self.loop_running = False

	def milli_time(self) -> float:
		return time() * 1000

	def generate_click_event(self, button: int):
		now = self.milli_time()
		return (button, now)

	def click_left(self, event):
		# anchor for Tk Event
		self.click_events.append(self.generate_click_event(ClickHandler.LEFT_BUTTON))

	def click_middle(self, event):
		# anchor for Tk Event
		self.click_events.append(self.generate_click_event(ClickHandler.MIDDLE_BUTTON))

	def click_right(self, event):
		# anchor for Tk Event
		self.click_events.append(self.generate_click_event(ClickHandler.RIGHT_BUTTON))

	def remove_clicks(self):
		self.click_events = []

	def run(self) -> None:
		self.thread = threading.Thread(target=self.click_handler_loop, args=())
		self.thread.daemon = True  # so these threads get killed when program exits
		self.thread.start()

	def bind(self, click_sequence, callback_function):
		self.callbacks.append((click_sequence, callback_function))

	def handle_clicks(self, click_events: list):
		click_sequence = [x[ClickHandler.CLICK_EVENT_BUTTON] for x in click_events]
		#print("Click Sequence:", click_sequence)
		for callback in self.callbacks:
			if click_sequence == callback[ClickHandler.CALLBACK_CLICK_SEQUENCE]:
				callback[ClickHandler.CALLBACK_FUNCTION]()

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
		print("Click handler stopped")
