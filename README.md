#Autopilot
Contains Autopilot Controller, Task Scripts, and Mission Files


TODO:
	We need to write the following tasks as specified. Each task should be a python class with Ctor, Init() method, and Run() method. They need a _log method as well

	GOTO: Takes in a waypoint in either init or ctor. Verifies that the waypoint is within a reasonable distance. Maybe converts waypoint to local? Publishes waypoint.
	
	LAND: Lands the vehicle at a point.

	LANDONTRAP. Lands the vehicle on top of the trap

	TOGGLE SWITCH: Toggles the servo for the dropoff, pickup

	ARM: Arms vehicle

	Look at Takeoff_task for example.