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


import platform
from topzemen.click_handler import ClickHandler

from PIL import Image, ImageTk

import threading
import tkinter
from tkinter import Tk


class ZemenWindow:
	SIZES = [64, 150, 300, 600]
	INIT_SIZE = 2
	HIDE_NONE = 0
	HIDE_TOP = 1

	def __init__(self, zoom_level=INIT_SIZE, start_position_x=150, start_position_y=50, start_hide = HIDE_NONE) -> None:
		self._last_mouse_event_x = 0
		self._last_mouse_event_y = 0
		self.thread: threading.Thread = None  # type: ignore
		self.alpha_selection = 0
		self.alpha_map = [1.0, 0.3, 0.5, 0.7]
		self.click_handler: ClickHandler = None  # type: ignore
		self.label_with_image = None
		self.zoom_level = zoom_level
		self.start_position_x = start_position_x
		self.start_position_y = start_position_y
		self.x = start_position_x
		self.y = start_position_y
		self.start_hide = start_hide
		self.height = 0
		self.width = 0
		self.original_image = None
		self.was_moved_by_mouse = False


	def set_click_handler(self, click_handler: ClickHandler) -> None:
		self.click_handler = click_handler

	def windowTkLoop(self) -> None:
		self.window = Tk()
		self.move_absolute(0,-1000) # hide temporarly until setup is done

		self.window.overrideredirect(True)
		self.window.wait_visibility(self.window)
		self.window.wm_attributes("-alpha", self.alpha_map[0])
		self.window.attributes("-topmost","true")

		print("Entering mainloop")
		self.window.mainloop()

	def update_size(self, height) -> None:

		if self.original_image_width / self.original_image_height < 1:
			# portrait
			newh = height
			neww = int((self.original_image_width * newh) / self.original_image_height)
		else:
			neww = height
			newh = int((self.original_image_height * neww) / self.original_image_width)

		resized_image = self.original_image.resize((neww, newh), Image.ANTIALIAS) # type: ignore
		self.photoimage = ImageTk.PhotoImage(resized_image)

		if self.label_with_image != None:
			self.label_with_image.configure(image=self.photoimage)

		self.window.geometry(str(neww) + "x" + str(newh))
		self.height = newh
		self.width = neww

	def setImage(self, imagefilename) -> None:
		first_run = self.original_image == None

		self.original_image = Image.open(imagefilename)
		self.original_image_width = self.original_image.width
		self.original_image_height = self.original_image.height

		self.update_size(ZemenWindow.SIZES[self.zoom_level])

		self.label_with_image = tkinter.Label(self.window, image=self.photoimage)
		if platform.system() == "Windows":
			self.label_with_image.place(x=-2, y=-2)
		else:
			self.label_with_image.place(x=-1, y=-1)

		self.label_with_image.bind("<ButtonRelease-1>", self.stop_move)
		self.label_with_image.bind("<B1-Motion>", self.do_move)
		self.label_with_image.bind("<ButtonPress-1>", self.click_left)
		self.label_with_image.bind("<ButtonPress-2>", self.click_middle)
		self.label_with_image.bind("<ButtonPress-3>", self.click_right)

		if first_run and self.start_hide == ZemenWindow.HIDE_TOP:
			self.move_absolute(self.start_position_x,0 - self.height)
		else:
			self.move_absolute(self.start_position_x,self.start_position_y)

	def zoom_in(self) -> None:
		if self.zoom_level < len(ZemenWindow.SIZES) - 1:
			self.zoom_level += 1
			self.update_size(ZemenWindow.SIZES[self.zoom_level])

	def zoom_out(self) -> None:
		if self.zoom_level > 0:
			self.zoom_level -= 1
			self.update_size(ZemenWindow.SIZES[self.zoom_level])

	def run(self) -> None:
		self.thread = threading.Thread(target=self.windowTkLoop, args=())
		self.thread.daemon = True  # so these threads get killed when program exits
		self.thread.start()

	def is_running(self) -> bool:
		return self.thread.is_alive()

	def close(self) -> None:
		if not self.is_running():
			print("Close ZemenWindow Loop")
			self.thread.join()

	def start_move(self, event) -> None:
		self._last_mouse_event_x = event.x
		self._last_mouse_event_y = event.y

	def stop_move(self, event) -> None:
		self._last_mouse_event_x = None
		self._last_mouse_event_y = None

	def do_move(self, event) -> None:
		deltax = event.x - self._last_mouse_event_x
		deltay = event.y - self._last_mouse_event_y
		self.x = self.window.winfo_x() + deltax
		self.y = self.window.winfo_y() + deltay
		self.window.geometry(f"+{self.x}+{self.y}")
		self.click_handler.remove_clicks()
		self.was_moved_by_mouse = True

	def move_realtive(self, deltax, deltay) -> None:
		self.x = self.window.winfo_x() + deltax
		self.y = self.window.winfo_y() + deltay
		self.window.geometry(f"+{self.x}+{self.y}")

	def move_absolute(self, x, y) -> None:
		self.x = x
		self.y = y
		self.window.geometry(f"+{self.x}+{self.y}")

	def click_middle(self, event) -> None:
		self.click_handler.click_middle(event)

	def click_right(self, event) -> None:
		self.click_handler.click_right(event)

	def click_left(self, event) -> None:
		self.click_handler.click_left(event)
		self.start_move(event)

	def stop(self) -> None:
		self.running = False
		self.window.quit()
		self.close()
		print("Tk Window Thread stopped")

	def get_screen_size(self) -> tuple:
		screen_width = self.window.winfo_screenwidth()
		screen_height = self.window.winfo_screenheight()
		return (screen_width,screen_height)
	
	def hide(self) -> None:
		self.window.withdraw()

	def show(self) -> None:
		self.window.deiconify()

	def switch_to_next_alpha_transparency(self) -> None:
		self.alpha_selection += 1
		if self.alpha_selection >= len(self.alpha_map):
			self.alpha_selection = 0
		self.window.wm_attributes("-alpha", self.alpha_map[self.alpha_selection])