#!/usr/bin/env python
from __future__ import print_function
import sys
import rospy
import roslib
from geometry_msgs.msg import *
from mavros_msgs.msg import *
from mavros_msgs.srv import *
import logging

class Takeoff:
	#args is a dictionary
	def __init__(self, args):
		logging.basicConfig(filename='takeoff.log',level=logging.DEBUG)
		#ROS Subscriptions
		self.current_pose_sub = None
	    self.state_sub = None
	    self.local_pos_pub = None
	    self.arming_client = None
	    self.set_mode_client = None
	    self.connection_state = None
	    self.measured_position = None

	    #Heights and Tolerances
	    self.rate = rospy.Rate(args['rate'])
	    self.height = args['height']
	    #tolerance is in meters. Read in as a tuple (x,y,z)
	    tolx,toly,tolz = args['tolerance']
	    self.tolerance = PoseStamped()
	    self.tolerance.pose.position.x =tolx
	   	self.tolerance.pose.position.y =toly
	    self.tolerance.pose.position.z =tolz
	    self.offset = None
	
	#Not sure about this... the callback for a subscription
	def state_callback(self, data):
	    self._log("State: "+str(data))
	    self.connection_state = data

	def pose_callback(self, data):
		self._log("Pose: "+str(data))
		self.measured_position = data.pose.pose.position
		#TODO Assign to current pose tuple


	def Init(self):
		self._log("Initializing takeoff.")
		#set subscriptions
		#get global position
		self.current_pose_sub = rospy.Subscriber("/mavros/global_position/local", PoseWithCovarianceStamped, self.state_callback)
		self.state_sub = rospy.Subscriber("/mavros/state", State, self.state_callback)
		self.local_pos_pub = rospy.Publisher("mavros/setpoint_position/local", PoseStamped, queue_size=20)
		self.arming_client = rospy.ServiceProxy("mavros/cmd/arming", CommandBool)
		self.set_mode_client = rospy.ServiceProxy("mavros/set_mode", SetMode)


		while self.connection_state and self.connection_state.connected:
			self.rate.sleep()

		while self.measured_position is None:
			self.rate.sleep()

		pose = PoseStamped()
		pose.pose.position.x = self.measured_position.x
		pose.pose.position.y = self.measured_position.y
		pose.pose.position.z = self.measured_position.z + self.height

		for i in range(0,100):
			local_pos_pub.publish(pose)
			self.rate.sleep()

		arming_client(True)
		set_mode_client(custom_mode="OFFBOARD")
		return "READY"


	#Returns when finished
	#@Return : "Success" or "Failure"
	def Run(self):
		target_pose = PoseStamped()
		target_pose.pose.position.x = self.measured_position.x
		target_pose.pose.position.y = self.measured_position.y
		target_pose.pose.position.z = self.measured_position.z + self.height

		self._log("Beginning Takeoff.")
		#While not in goal state. Publish then sleep.
		while !self._isGoal(target_pose, tolerance):
			local_pos_pub.publish(pose)
			self.rate.sleep()
		self._log("Takeoff Finished.")
		return "SUCCESS"



	def OnFail():
		return
		#No Idea what to do here... Maybe try to recover and move on to the next task, return, or land

	#Returns whether current pose is in tolerance of goal state. 
	#This code will be reused in each task. May want to move it.
	def _isGoal(self, goal, tolerance):
		inRange = True
		if(abs(self.measured_position.x - goal.pose.position.x) > tolerance.pose.position.x):
			inRange = False
		if(abs(self.measured_position.y - goal.pose.position.y) > tolerance.pose.position.y):
			inRange = False
		if(abs(self.measured_position.x - goal.pose.position.z) > tolerance.pose.position.z):
			inRange = False
		return inRange



	#All logs will be on debug level b/c who cares...
	def _log(self, logmsg):
		logging.debug(str(datetime.datetime.now())+ ":" + logmsg)
