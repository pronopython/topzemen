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

from random import randint
import threading
from time import sleep
from topzemen.ipc import IpcMessageClient

from topzemen.zemen_window import ZemenWindow


class ZemenWindowAi:
	def __init__(
		self, zemen_window: ZemenWindow, callback_quit_function=None, autoscroller=False
	) -> None:

		self.zemen_window = zemen_window
		self.callback_quit_function = callback_quit_function
		self.autoscroller = autoscroller
		self.velocity_in_pixels = 0

		self.message_client = IpcMessageClient()
		self.message_client.listen("close", self.message_close)
		self.message_client.listen(
			"close none autoscroll", self.message_close_none_autoscroll
		)
		self.message_client.listen("close autoscroll", self.message_close_autoscroll)
		self.message_client.listen("hide", self.message_hide)
		self.message_client.listen("show", self.message_show)
		self.message_client.run()

	def window_ai_loop(self):

		self.running = True
		self.loop_running = True

		max_wait_rounds = randint(5, 15)
		count_wait_rounds = 0
		check_screen_size = 0
		screen_height = self.zemen_window.get_screen_size()[1]

		if self.autoscroller:
			self.velocity_in_pixels = 1

		while self.running:
			sleep(0.01)

			count_wait_rounds += 1
			if count_wait_rounds > max_wait_rounds:
				count_wait_rounds = 0
				self.zemen_window.move_realtive(0, self.velocity_in_pixels)

			check_screen_size += 1
			if check_screen_size > 500:
				check_screen_size = 0
				screen_height = self.zemen_window.get_screen_size()[1]

			if self.zemen_window.y > screen_height:
				self.running = False

			if self.zemen_window.was_moved_by_mouse:
				self.velocity_in_pixels = 0

		self.loop_running = False
		self.callback_quit_function() # type: ignore

	def run(self) -> None:
		self.thread = threading.Thread(target=self.window_ai_loop, args=())
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
		print("ZemenWindowAi stopped")

	def message_close(self):
		self.stop()
		self.callback_quit_function() # type: ignore

	def message_close_none_autoscroll(self):
		if self.velocity_in_pixels == 0:
			self.message_close()

	def message_close_autoscroll(self):
		if self.velocity_in_pixels > 0:
			self.message_close()

	def message_hide(self):
		self.zemen_window.hide()

	def message_show(self):
		self.zemen_window.show()
