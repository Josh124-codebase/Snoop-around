# Snooper version 1.0

import os
import argparse
from pathlib import Path

user_path = Path.home()

parser = argparse.ArgumentParser(prog="Snooper", description="Snooper is a tool for searching through a file system")
group = parser.add_mutually_exclusive_group()

parser.add_argument("-s", action="store_true", help="match only if filename === target filename i.e controls verbosity of search")
parser.add_argument("-i", action="store_true", help="Ignore case.")
group.add_argument("-e", type=str, nargs="*", action="store", help="extension search e.g .txt, .exe {can accept space seperated extension list}")
group.add_argument("-t", type=str, nargs="*", action="store", help="file search e.g example.txt {can accept space seperated file list}")
parser.add_argument("-D", default=f"{user_path}", action="store", help=f"The root directory to begin search. default = {user_path}")
parser.add_argument("-p", type=str, action="store", default="snoop.result.txt", help="prints output into filename provided. default = snoop.result.txt")
parser.add_argument("-V", "--version", action="version", version="%(prog)s 1.0")
parser.add_argument("--tree", action="store_true", help="Displays entire file system in a tree starting from the directory passed in.")

args = parser.parse_args()

def handle_flags(args) :
	if args.tree :
		return {"tree" : True, "root": args.D}

	return {
		"root" : args.D,
		"targets" : args.t if args.t else args.e,
		"flags" : {
			"specific" : args.s,
			"ignore" : args.i,
			"print_to_file" : args.p
		},
		"type" : "f" if args.t else "x"
	}

result = 0

def Snoop(params) : # this should be a dict containing the: root, targets, flags, type
	global result
	root = str(params["root"])
	Target = params["targets"] or []
	flags = params["flags"]

	objs = []
	try :
		# objs = os.listdir(root);
		objs = Path(root)
	
	except Exception as e:
		return print(e)


	def do_checks(targ, obj, specific, ignore, type = "f", is_dir = False) :
		if specific :
			_match = (targ.lower() == obj.lower()) if ignore else (targ == obj)
		else :
			_match = (targ.lower() in obj.lower()) if ignore else (targ in obj)
		if _match:
			if is_dir :
				print(f"{obj} folder found in {root}\n")
			elif type == "x" :
				print(f"{file_path} in {root}\n")
			else :
				print(f"{obj} found in {root}\n")

			return 1
		return 0


	for obj in objs.iterdir() :
		obj = str(obj)
		if len(Target) == 0 :
			break
		_match = False
		node_path = os.path.join(root, obj)
		if os.path.isdir(node_path) :
			try :
				for targ in Target :
					result += do_checks(targ, obj, flags["specific"], flags["ignore"], "f",True)
				new_params = {
					"root" : node_path,
					"flags" : params["flags"],
					"targets" :Target,
					"type" :params["type"]
				}
				
				Snoop(new_params)
			except Exception as e :
				print(e)
		else :
			for targ in Target :
				match params["type"] :
					case "x" :
						file_path = Path(obj)
						f_name = file_path.stem
						obj = file_path.suffix
						result += do_checks(targ, obj, flags["specific"], flags["ignore"], "x")

					case "f" :
						result += do_checks(targ, obj, flags["specific"], flags["ignore"], "f")


def print_to_file(opened_file, text) :
	try :
		opened_file.write(f"/n{text}")
		return True
	except Exception as e :
		return False


def start_snoop(params) :
	args = handle_flags(params)
	for obj in os.listdir(args["root"]) :
		new_params = args
		new_params["root"] = os.path.join(args["root"], obj)
		Snoop(new_params)

Snoop(handle_flags(args))
print(f"{result} result{'s' if result > 1 else ''} found!")