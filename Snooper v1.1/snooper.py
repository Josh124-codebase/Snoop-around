# Snooper
# Copyright (c) 2026 Onwuemenyi Joshua Akachukwu
# Licensed under the MIT License
# @Version 1.1

import os
import argparse
import time 
import math
import stat
import sys
from pathlib import Path

user_path = Path.home()

parser = argparse.ArgumentParser(prog="Snooper", description="Snooper A lightweight filesystem search tool by Onwuemenyi Joshua Akachukwu")
group = parser.add_mutually_exclusive_group()

parser.add_argument("-s", action="store_true", help="match only if filename === target filename i.e controls verbosity of search")
parser.add_argument("-i", action="store_true", help="Ignore case.")
group.add_argument("-e", type=str, nargs="*", action="store", help="extension search e.g .txt, .exe {can accept space seperated extension list}")
group.add_argument("-t", type=str, nargs="*", action="store", help="file search e.g example.txt {can accept space seperated file list}")
parser.add_argument("-D", type=str, default=f"{user_path}", action="store", help=f"The root directory to begin search. default = {user_path}")
parser.add_argument("-V", "--version", action="version", version="%(prog)s 1.1")
parser.add_argument("--tree", action="store_true", help="Displays entire filesystem in a tree starting from the directory passed in.")

args = parser.parse_args()
result = 0
dir_count = 0
file_count = 0
dept_count = 0

def search_config(args) :
	return {
		"root" : args.D,
		"targets" : args.t if args.t else args.e,
		"flags" : {
			"specific" : args.s,
			"ignore" : args.i,
		},
		"type" : "f" if args.t else "x",
		"tree" : args.tree,
	}

def snoop(params) : # params should be a dict containing the: root, targets, flags, search type {f for file x for extession}
	global result
	root = str(params["root"])
	Targets = params["targets"] or []
	flags = params["flags"]

	def do_checks(targ, obj, specific, ignore, type = "f", is_dir = False) :
		if specific :
			_match = (targ.lower() == obj.lower()) if ignore else (targ == obj)
		else :
			_match = (targ.lower() in obj.lower()) if ignore else (targ in obj)
		if _match:
			if is_dir :
				print(f"{obj} folder found in {root}\n")
			else :
				print(f"{obj} in {root}\n")

			return 1
		return 0

	try :
		with os.scandir(root) as root_dir :
			for entry in root_dir :
				if entry.is_dir() :
					for target in Targets:
						result += do_checks(target, entry.name, flags["specific"], flags["ignore"], "f",True)
					new_params = {
					"root" : entry.path,
					"flags" : params["flags"],
					"targets" :Targets,
					"type" :params["type"]
					}
					snoop(new_params)
				else :
					match params["type"] : 
						case "x":
							for target in Targets :
								result += do_checks(target, Path(entry.name).suffix,flags["specific"], flags["ignore"], "x")
						case _ :
							for target in Targets :
								result += do_checks(target, entry.name,flags["specific"], flags["ignore"])

				# print(entry.path)

	except OSError as e:
		return print(f"Error occured : [{e.strerror}]", file=sys.stderr)
				
def draw_tree(params, prefix=""):
    try:
        entries = sorted(
            os.scandir(params["root"]),
            key=lambda e: (e.is_file(), e.name.lower())
        )

        for i, entry in enumerate(entries):
            is_last = (i == len(entries) - 1)

            connector = "`-- " if is_last else "+-- "
            extension = "    " if is_last else "|   "

            # Detect hidden files
            hidden = False

            # Unix/Linux hidden files
            if entry.name.startswith("."):
                hidden = True

            # Windows hidden attribute
            try:
                hidden |= bool(entry.stat().st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
            except (AttributeError, OSError):
                pass

            marker = " [H]" if hidden else ""

            print(prefix + connector + entry.name + marker)

            if entry.is_dir(follow_symlinks=False):
                try:
                    draw_tree(
                        {"root": entry.path},
                        prefix + extension
                    )
                except PermissionError:
                    print(prefix + extension + "`-- [Permission Denied]")

    except PermissionError:
        raise
    except OSError as e:
        print(prefix + f"`-- [{e.strerror}]")

def time_handler(seconds) :
	time_info = ''
	hrl = 3600
	minl = 60
	secl = 1
	if seconds >= hrl : #hours
		hr = math.floor(seconds / hrl)
		rem = seconds - (hr * hrl)
		mins = math.floor(rem / minl)
		rem = rem - (mins * minl)
		sec = rem
		time_info += f"{hr} hr, {mins} min, {sec} sec"
	elif seconds >= minl: #minutes
		mins = math.floor(seconds / minl)
		rem = seconds - (mins * minl)
		sec = rem
		time_info += f"{mins} min, {sec} sec"
	else : #seconds
		time_info = f"{seconds} sec"
	return time_info

def init(command_line_args) :
	config = search_config(command_line_args)
	print(config["root"])
	start = time.perf_counter()
	if config["tree"]: 
		# print(config["root"])
		draw_tree(config)
	else :
		snoop(config)
		print(f"{result} result{'s' if result != 1 else ''} found!")

	end = time.perf_counter()
	diff = math.ceil(end - start)
	print(f"Process took {time_handler(diff)}")
init(args)