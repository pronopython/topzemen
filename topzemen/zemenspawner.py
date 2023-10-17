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

import os
import platform
from random import randint
import sys
import threading
from time import sleep
from tkinter import Button, Entry, IntVar, Label, TclError, Tk
from typing import NoReturn
import subprocess
from tkinter import Frame
from tkinter import N
from tkinter import S
from tkinter import E
from tkinter import W

from topzemen.ipc import IpcMessageBroker


class DirCrawler:
	def __init__(self, rootpath) -> None:
		self.running = False
		self.rootpath = rootpath
		self.pause_crawl = False

		self.spawn_x_from = 1500
		self.spawn_x_to = 1750
		self.spawn_every_from = 3
		self.spawn_every_to = 20

	def crawler_loop(self) -> None:
		WORKING_EXTENSIONS = [".jpg", ".jpeg", ".tif", ".tiff", ".png", ".gif"]
		self.running = True
		self.loop_running = True
		skip_files = randint(0, 1000)

		while self.running:

			for root, d_names, f_names in os.walk(self.rootpath):
				for f_name in f_names:
					sleep(0.001)
					if skip_files > 0:
						skip_files -= 1
						continue
					else:
						skip_files = randint(0, 1000)

					f_fullPath = os.path.join(root, f_name)
					f_nameOnly, f_ext = os.path.splitext(f_name)
					if f_ext.lower() in WORKING_EXTENSIONS:
						if self.spawn_x_from <= self.spawn_x_to:
							spawn_x = randint(self.spawn_x_from, self.spawn_x_to)
						else:
							spawn_x = randint(self.spawn_x_from, self.spawn_x_from)
						if platform.system() == "Windows":
							subprocess.Popen(["topzemen_no_cli", f_fullPath, str(spawn_x)])
						else:
							subprocess.Popen(["topzemen", f_fullPath, str(spawn_x)])
						if self.spawn_every_from <= self.spawn_every_to:
							sleep_sec = randint(
								self.spawn_every_from, self.spawn_every_to
							)
						else:
							sleep_sec = randint(
								self.spawn_every_from, self.spawn_every_from
							)
						for s in range(0, sleep_sec):
							sleep(1)
							if not self.running:
								break
					while self.pause_crawl:
						sleep(1)
				if not self.running:
					break
		self.loop_running = False

	def run(self) -> None:
		self.thread = threading.Thread(target=self.crawler_loop, args=())
		self.thread.daemon = True  # so these threads get killed when program exits
		self.thread.start()

	def is_running(self) -> bool:
		return self.thread.is_alive()

	def close(self) -> None:
		if not self.is_running():
			self.thread.join()

	def stop(self) -> None:
		self.running = False
		self.pause_crawl = False
		while self.loop_running:
			sleep(0.06)
		self.close()
		print("Crawler stopped")

	def pause(self) -> None:
		self.pause_crawl = True

	def resume(self) -> None:
		self.pause_crawl = False


class ZemenSpawner:
	def __init__(self) -> None:
		self.running = False
		self.rootpath = ""
		self.dir_crawler: DirCrawler = None  # type: ignore

	def run(self) -> None:

		self.zemen_spawner_server = IpcMessageBroker()
		self.zemen_spawner_server.run()

		if len(sys.argv) > 1:
			self.rootpath = sys.argv[1]

			if not os.path.isdir(self.rootpath):
				print(
					"Please start the ZemenSpawner with a path to a directory to crawl."
				)
				sys.exit()
		else:
			print("Please start the ZemenSpawner with a path to a directory to crawl.")
			sys.exit()

		self.dir_crawler = DirCrawler(self.rootpath)
		self.dir_crawler.run()

		self.window = Tk()

		self.window.geometry("900x120")
		self.window.title("Zemen Spawner")

		frm = Frame(self.window)
		frm.grid(sticky=N + S + W + E)
		frm.columnconfigure(0, weight=1)

		entry_x_from_var = IntVar(
			master=self.window, value=self.dir_crawler.spawn_x_from
		)
		entry_x_from_var.trace(
			"w",
			lambda name, index, mode, var=entry_x_from_var: self.entry_x_from_var_callback(
				entry_x_from_var
			),
		)
		entry_x_from_label = Label(frm, text="horizontal from").grid(column=0, row=0)
		entry_x_from = Entry(frm, textvariable=entry_x_from_var)
		entry_x_from.grid(column=1, row=0)

		entry_x_to_var = IntVar(master=self.window, value=self.dir_crawler.spawn_x_to)
		entry_x_to_var.trace(
			"w",
			lambda name, index, mode, var=entry_x_to_var: self.entry_x_to_var_callback(
				entry_x_to_var
			),
		)
		entry_x_to_label = Label(frm, text="to").grid(column=2, row=0)
		entry_x_to = Entry(frm, textvariable=entry_x_to_var)
		entry_x_to.grid(column=3, row=0)
		entry_pixel_label = Label(frm, text="pixel").grid(column=4, row=0)

		button_stop_spawn = Button(
			frm, text="stop spawn", command=self.action_stop_spawn
		)
		button_stop_spawn.grid(column=0, row=1)

		button_resume_spawn = Button(
			frm, text="resume spawn", command=self.action_resume_spawn
		)
		button_resume_spawn.grid(column=1, row=1)

		entry_spawn_every_from_var = IntVar(
			master=self.window, value=self.dir_crawler.spawn_every_from
		)
		entry_spawn_every_from_var.trace(
			"w",
			lambda name, index, mode, var=entry_spawn_every_from_var: self.entry_spawn_every_from_var_callback(
				entry_spawn_every_from_var
			),
		)
		entry_spawn_every_from_label = Label(frm, text="spawn every").grid(
			column=2, row=1
		)
		entry_spawn_every_from = Entry(frm, textvariable=entry_spawn_every_from_var)
		entry_spawn_every_from.grid(column=3, row=1)

		entry_spawn_every_to_var = IntVar(
			master=self.window, value=self.dir_crawler.spawn_every_to
		)
		entry_spawn_every_to_var.trace(
			"w",
			lambda name, index, mode, var=entry_spawn_every_to_var: self.entry_spawn_every_to_var_callback(
				entry_spawn_every_to_var
			),
		)
		entry_spawn_every_to_label = Label(frm, text="to").grid(column=4, row=1)
		entry_spawn_every_to = Entry(frm, textvariable=entry_spawn_every_to_var)
		entry_spawn_every_to.grid(column=5, row=1)
		entry_spawn_every_seconds_label = Label(frm, text="seconds").grid(
			column=6, row=1
		)

		button_hide_all = Button(frm, text="hide all", command=self.action_hide_all)
		button_hide_all.grid(column=0, row=2)

		button_show_all = Button(frm, text="show all", command=self.action_show_all)
		button_show_all.grid(column=1, row=2)

		button_close_all_auto_scroller = Button(
			frm,
			text="close all autoscroller",
			command=self.action_close_all_autoscroller,
		)
		button_close_all_auto_scroller.grid(column=0, row=3)

		button_close_all_none_auto_scroller = Button(
			frm,
			text="close all manual positioned",
			command=self.action_close_all_none_autoscroller,
		)
		button_close_all_none_auto_scroller.grid(column=1, row=3)

		button_close_all = Button(frm, text="close all", command=self.action_close_all)
		button_close_all.grid(column=2, row=3)

		button_close_all_and_exit = Button(
			frm, text="close all & exit", command=self.action_close_all_and_exit
		)
		button_close_all_and_exit.grid(column=3, row=3)

		button_exit = Button(frm, text="exit", command=self.action_exit)
		button_exit.grid(column=4, row=3)

		self.window.mainloop()

	def action_close_all_autoscroller(self) -> None:
		self.zemen_spawner_server.send("close autoscroll")

	def action_close_all_none_autoscroller(self) -> None:
		self.zemen_spawner_server.send("close none autoscroll")

	def action_close_all(self) -> None:
		self.zemen_spawner_server.send("close")

	def action_hide_all(self) -> None:
		self.zemen_spawner_server.send("hide")

	def action_show_all(self) -> None:
		self.zemen_spawner_server.send("show")

	def action_close_all_and_exit(self) -> NoReturn:
		self.zemen_spawner_server.send("close")
		self.dir_crawler.stop()
		exit()

	def action_exit(self) -> NoReturn:
		self.dir_crawler.stop()
		exit()

	def action_stop_spawn(self) -> None:
		self.dir_crawler.pause()

	def action_resume_spawn(self) -> None:
		self.dir_crawler.resume()

	def entry_x_from_var_callback(self, var) -> None:
		try:
			self.dir_crawler.spawn_x_from = int(var.get())
		except TclError:
			pass

	def entry_x_to_var_callback(self, var) -> None:
		try:
			self.dir_crawler.spawn_x_to = int(var.get())
		except TclError:
			pass

	def entry_spawn_every_from_var_callback(self, var) -> None:
		try:
			self.dir_crawler.spawn_every_from = int(var.get())
		except TclError:
			pass

	def entry_spawn_every_to_var_callback(self, var) -> None:
		try:
			self.dir_crawler.spawn_every_to = int(var.get())
		except TclError:
			pass


if __name__ == "__main__":
	app = ZemenSpawner()
	app.run()


def main() -> NoReturn:  # type: ignore
	app = ZemenSpawner()
	app.run()
