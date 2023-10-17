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

from typing import NoReturn
import sys
import os
import platform
import subprocess

from time import sleep
from topzemen.zemen_window_ai import ZemenWindowAi

from topzemen.click_handler import ClickHandler
from topzemen.zemen_window import ZemenWindow

from pathlib import Path

if len(sys.argv) > 1:
	imagefilename = sys.argv[1]

	if not os.path.isfile(imagefilename):
		print("Please start TopZemen with a path to an image.")
		sys.exit()
else:
	print("Please start TopZemen with a path to an image.")
	sys.exit()


class TopZemenApp:
	def __init__(self) -> None:
		self.running = False
		self.loop_running = False
		self.autoscroller = False
		self.start_hide = ZemenWindow.HIDE_NONE

	def run(self) -> NoReturn:

		self.last_click_time = 0

		self.clicks_right = 0

		spawn_x = 150
		zoom_level = 1

		if len(sys.argv) > 2:
			try:
				spawn_x = int(sys.argv[2])
				# print("spawn x", spawn_x)
				self.autoscroller = True
				self.start_hide = ZemenWindow.HIDE_TOP
				zoom_level = 0
			except:
				pass

		self.zemen_window = ZemenWindow(
			zoom_level=zoom_level, start_position_x=spawn_x, start_hide=self.start_hide
		)

		self.click_handler = ClickHandler()

		self.click_handler.bind(
			[
				ClickHandler.RIGHT_BUTTON,
				ClickHandler.RIGHT_BUTTON,
				ClickHandler.LEFT_BUTTON,
			],
			self.quit,
		)
		self.click_handler.bind(
			[ClickHandler.RIGHT_BUTTON, ClickHandler.RIGHT_BUTTON], self.open_image
		)
		self.click_handler.bind(
			[ClickHandler.LEFT_BUTTON, ClickHandler.RIGHT_BUTTON], self.zoom_out
		)
		self.click_handler.bind(
			[
				ClickHandler.LEFT_BUTTON,
				ClickHandler.RIGHT_BUTTON,
				ClickHandler.LEFT_BUTTON,
				ClickHandler.RIGHT_BUTTON,
			],
			self.zoom_out_2x,
		)
		self.click_handler.bind(
			[
				ClickHandler.LEFT_BUTTON,
				ClickHandler.RIGHT_BUTTON,
				ClickHandler.LEFT_BUTTON,
				ClickHandler.RIGHT_BUTTON,
				ClickHandler.LEFT_BUTTON,
				ClickHandler.RIGHT_BUTTON,
			],
			self.zoom_out_3x,
		)
		self.click_handler.bind(
			[ClickHandler.RIGHT_BUTTON, ClickHandler.LEFT_BUTTON], self.zoom_in
		)
		self.click_handler.bind(
			[
				ClickHandler.RIGHT_BUTTON,
				ClickHandler.LEFT_BUTTON,
				ClickHandler.RIGHT_BUTTON,
				ClickHandler.LEFT_BUTTON,
			],
			self.zoom_in_2x,
		)
		self.click_handler.bind(
			[
				ClickHandler.RIGHT_BUTTON,
				ClickHandler.LEFT_BUTTON,
				ClickHandler.RIGHT_BUTTON,
				ClickHandler.LEFT_BUTTON,
				ClickHandler.RIGHT_BUTTON,
				ClickHandler.LEFT_BUTTON,
			],
			self.zoom_in_3x,
		)
		self.click_handler.bind(
			[ClickHandler.MIDDLE_BUTTON], self.switch_to_next_alpha_transparency
		)

		self.zemen_window.set_click_handler(self.click_handler)

		self.click_handler.run()
		self.zemen_window.run()

		self.zemen_window.setImage(imagefilename)

		self.zemen_window_ai = ZemenWindowAi(
			self.zemen_window,
			callback_quit_function=self.quit,
			autoscroller=self.autoscroller,
		)
		self.zemen_window_ai.run()

		self.running = True
		self.loop_running = True
		while self.running:
			sleep(0.1)
		self.loop_running = False

		print("Stopping click handler...")
		self.click_handler.stop()
		print("ByeBye")
		sys.exit()

	def quit(self) -> None:
		print("Stopping Tk Window Thread handler...")
		self.zemen_window.stop()
		print("Stopping main loop...")
		self.stop_loop()

	def open_file(self, path) -> None:
		if platform.system() == "Windows":
			os.startfile(path)  # type: ignore
		elif platform.system() == "Darwin":
			subprocess.Popen(["open", path])
		else:
			subprocess.Popen(["xdg-open", path])

	def open_image(self) -> None:
		global imagefilename
		self.open_file(imagefilename)

	def zoom_in(self) -> None:
		self.zemen_window.zoom_in()

	def zoom_in_2x(self) -> None:
		self.zemen_window.zoom_in()
		self.zemen_window.zoom_in()

	def zoom_in_3x(self) -> None:
		self.zemen_window.zoom_in()
		self.zemen_window.zoom_in()
		self.zemen_window.zoom_in()

	def zoom_out(self) -> None:
		self.zemen_window.zoom_out()

	def zoom_out_2x(self) -> None:
		self.zemen_window.zoom_out()
		self.zemen_window.zoom_out()

	def zoom_out_3x(self) -> None:
		self.zemen_window.zoom_out()
		self.zemen_window.zoom_out()
		self.zemen_window.zoom_out()

	def switch_to_next_alpha_transparency(self) -> None:
		self.zemen_window.switch_to_next_alpha_transparency()

	def stop_loop(self) -> None:
		self.running = False
		while self.loop_running:
			sleep(0.06)


if __name__ == "__main__":
	app = TopZemenApp()
	app.run()


def main() -> NoReturn:  # type: ignore
	app = TopZemenApp()
	app.run()
