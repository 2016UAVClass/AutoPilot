#Autopilot Controller
#Author: Turner Strayhorn
#Vanderbilt University 2017
#winston.t.strayhorn@vanderbilt.edu

import logging
import sys
import Missions
import Takeoff_Task

file = None

#millisecs
rate = 20.0
#meters
flyingHeight = 3
#(x,y,z)
takeoffTolerance = (1,1,1)
waypointTolerance = (2,2,1)
landingTolerance = (1,1,1)

#log
logging.basicConfig(filename='controller.log',level=logging.DEBUG)


	#All logs will be on debug level b/c who cares...
def _log(logmsg):
	logging.debug(str(datetime.datetime.now())+ ":" + logmsg)


#sets default arguments that are similar amongst tasks
def setArgs(args):
	args['rate'] = rate
	args['height'] = flyingHeight

#parses arguments. sets to global vars
def setParams(opt, arg):
	global file
	if opt in ("-f","--file"):
		file = arg

#checks validity of variables and makes sure they are set
def checkValidity():
	if file is None:
		return False
	return ".txt" in file[-4:]

#prints options for controller
def printHelp():
	print "\nAutopilot controller."
	print "-h or --help Help Menu"
	print "-f --file followed by file to give mission file."
	print "\n"

#parses text for each line in the file, creates and returns a task
#if textual error, returns None
def parseLine(line):
	#create arguments
	args = dict()
	setArgs(args)
	#TAKEOFF
	if("TAKEOFF" in line):
		_log("Adding Takeoff Task")
		args['tolerance'] = takeoffTolerance
		task = Takeoff_Task.Takeoff(args)
		return task

	if("GOTO" in line):
		_log("Adding Goto Task")
		#TODO Create GOTO task

		line = line.replace("GOTO:","")
		x,y,z = line.strip().split(",")
		#go ahead and create the waypoint tuple
		args['waypoint'] = (x,y,flyingHeight)
		args['tolerance'] = waypointTolerance
		task = Goto_Task.Goto(args)
		return task

	if("LAND" in line):
		_log("Adding Land Task")
		#TODO Create Land task

		args['tolerance'] = landingTolerance
		task = Land_Task.Land(args)
		return task

	if("PICKUP" in line):
		_log("Adding Land Task")
		#TODO Create pickup task
		
		args['tolerance'] = landingTolerance
		task = Land_Task.Land(args)
		return task

	if("DROPOFF" in line):
		_log("Adding Land Task")
		#TODO Create dropoff task
		
		args['tolerance'] = landingTolerance
		task = Land_Task.Land(args)
		return task

	#else, invalid
	_log("Invalid Task:" + line)
	print("Invalid Task:" + line)
	return None

#sets up the mission queue. Creates and fills with tasks
def setupMission():
	print "\nSetting up Mission"
	run = True
	tasks = []

	_log("Adding Disarm Task")
	#TODO: Add disarm task to start of the Queue

	#opens file
	try:
		f = open(file, 'r')
	except IOError:
		print "\nFile Cannot Be Found: Aborting Mission"
		_log("File Cannot Be Found: Aborting Mission")
		return
	for line in file:
		#fill queue with waypoints, then pickup, then return
		tasks.append(parseLine(line))
	
	#verify mission. Should at least be takeoff and landing.
	if len(tasks) < 2:
		run = False
	#No Tasks of None should be found
	for task in tasks:
		if task is None:
			run = False

	#run mission
	if run:
		runMission(tasks)
	else:
		_log("Mission Cannot Be Run. Invalid Tasks exist.")
		print "Mission Cannot Be Run. Invalid Tasks/Configuration exist."


#runs the mission
def runMission(tasks):
	print "Running mission"
	_log("Running mission")
	status = None
	#While tasks in the queue
	while tasks:
		_log("Popping task")
		task = tasks.pop(0)
		status = task.Init()
		if("READY" in status):
			status = task.Run()
			if("SUCCESS" not in status):
				status = task.OnFail()
				break

def main(args):
	#filepath and missiontype init to none
	#print help if in args
	arg = sys.argv
	if "-h" in arg or "--help" in arg:
		printHelp()
	else:
		arguments = []
		#chunk args into tuples
		for i in range(0, len(args), 2):
			arguments.append((args[i],args[i+1]))
		#move into tuples with args and opts
		for opt, arg in arguments:
			setParams(opt, arg)
		if checkValidity():
			setupMission()
		else:
			print "To run a mission, you must have a mission type and a file read-in."

if __name__ == "__main__":
    main(sys.argv[1:])

