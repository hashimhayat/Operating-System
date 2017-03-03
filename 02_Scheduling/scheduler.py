'''
Lab 2 - Scheduling
Created by Hashim Hayat
Main: Scheduler
'''

import copy
from processhandler import *


class Scheduler:

	def __init__(self, processTable, algo='fcfs'):

		self.processTable = copy.deepcopy(processTable)
		self.process_state = {}
		self.states = {
						'unstarted':[],
						'ready':[],
						'running':[],	
						'blocked':[],
						'terminated':[]
					}

		self.algorithm = algo 		# Algorithm in use 
		self.clock = -1				# Time at which scheduler is right now.
		self.active = True 			# Indicates if the Scheduler is working or not
		self.X = 0					# next random number
		self.logs = ""

	# Initialises the Scheduler with the specified algorithm.
	def init(self):

		# Put all processes in the unstarted state
		self.initProcesses()

		if self.algorithm == 'fcfs':
			self.FSFS()
		elif self.algorithm == 'roundrobin':
			pass
		elif self.algorithm == 'uniprogrammed':
			pass
		elif self.algorithm == 'sjf':
			pass
		else:
			print("Wrong Algorithm!")

	# Puts all processes in the process table into unstarted list status
	def initProcesses(self):
		for p in self.processTable.sortedStore:
			self.states['unstarted'].append(p)
			self.process_state[p] = 'unstarted'

	# Updates the state of a process (P).
	# Adding a process to the scheduler is also updation
	# so the same function can be used

	def updateState(self, Process, newState):

		prevState = Process.state

		# Remove the process from old state
		self.states[prevState].remove(Process)

		# Update the state of process:
		#  - self.state = 'unstarted'
		#  - self.IO = 0
		#  - self.finishTime = 0
		#  - self.turnAroundTime = 0
		#  - self.waitingTime = 0

		Process.state = newState
		Process.time = self.clock

		# Running:
			# calculate remainingburst
		if newState == 'running':

			t = self.randomOS(Process.B)

			# If t, the value returned by randomOS(), is larger than the total CPU
			# time remaining, set t to the remaining time.

			if t > Process.remainingCPU:
				t = Process.remainingCPU
			Process.remainingBurst = t

		# Blocked:
			# calculate remaining IO
		if newState == 'blocked':
			Process.IO = self.randomOS(Process.M)

		# 

		# Enqueue it in the new state list
		self.states[newState].append(Process)

	# -------------------- Random Numbers --------------------- #

	# Reads the next Random number from the file
	# Stores that in self.nextR
	def getNextUDRI(self):
		with open('random-numbers.txt','r') as randoms:
			for i, random in enumerate(randoms):
				if i == self.X:
					self.X += 1
					return int(random)

	# The simple function randomOS(U) reads a random non-negative integer 
	# X from a file named random-numbers (in the current directory) and returns the value 1 + (X mod U).
	def randomOS(self,U):
		return 1 + (self.getNextUDRI() % U)

	# Create the Result logs. Takes the ProcessTable.
	def createLogs(self,PT):  

		logs = "\n"
		logs += PT.view('unsorted') + '\n' +  PT.view('sorted') + '\n\n'
		logs += "The scheduling algorithm used was First Come First Served\n\n"

		for p in range(len(PT.sortedStore)):

			logs += "Process " + str(p) + ":\n"
			logs += "  (A,B,C,M) = " + PT.sortedStore[p].__repr__() + "\n"
			logs += "  Finishing time: " + str(PT.sortedStore[p].finishTime) + "\n"
			logs += "  Turnaround time: " + str(PT.sortedStore[p].turnAroundTime) + "\n"
			logs += "  I/O time time: " + str(PT.sortedStore[p].IO) + "\n"
			logs += "  Waiting time: " + str(PT.sortedStore[p].waitingTime) + "\n\n"

		logs += "Summary Data:\n"
		logs += "  Finishing time: " + "\n"
		logs += "  CPU Utilization: " + "\n"
		logs += "  I/O Utilization: " + "\n"
		logs += "  Throughput: " + " processes per hundred cycles\n"
		logs += "  Average turnaround time: " + "\n"
		logs += "  Average waiting time: " + "\n"

		return logs

	# String Representation of the Scheduler
	def __repr__(self):
		#return self.createLogs(self.processTable)
		return self.logs

	def FSFS(self):

		self.logs = "\nThis detailed printout gives the state and remaining burst for each process\n\n"
		spaces = {'unstarted':'   ', 'running':'     ','ready':'       ','blocked':'     ', 'terminated':' '}

		while (self.active):

			# Algorithm goes here.

			# A list of processes that have been updated in this cycle
			# ensures that a process only changes its state once per cycle
			PROCESSES = []

			# -------------------- RUNNING PROCESSE --------------------- #			

			# if a process is in running state
				# decrement its remaining burst by 1
				# put it in blocked state if its remaining burst is 0 
				# decrement the total CPU time
				# put it in terminate state if CPU time is over

			if (self.states['running']):

				# FIX REMAINING BURST
				process = self.states['running'][0]
				process.remainingBurst -= 1
				process.remainingCPU -= 1

				if process.remainingCPU <= 0:	
					self.updateState(process, 'terminated')

				elif process.remainingBurst == 0:
					self.updateState(process, 'blocked')
				PROCESSES.append(process)

			# -------------------- READY PROCESSES --------------------- #		

			# If a process is in ready state 
				# increment the waitingtime of the process
				# if the running is empty put the process in the running state

			# Break Ties
				# These ties are broken
				# by favoring the process with the earliest arrival time A. 
				# If the arrival times are the same for two processes with the same priority, 
				# then favor the process that is listed earliest in the input. 

			if (self.states['ready']):

				self.states['ready'] = sorted(self.states['ready'], key=lambda x: x.time, reverse=False)

				temp = self.states['ready'][:]
				processToRun = None
				activeReady = []	# process that shall stay in the ready state

				for process in temp:
					if process not in PROCESSES:
						process.waitingTime += 1

						activeReady.append(process)

						if len(self.states['running']) == 0:
							self.updateState(process, 'running')
							PROCESSES.append(process)

				if self.clock == 936:
					print(activeReady)
						

				# if activeReady:
				# 	# sort by arrival times
				# 	sortedActiveReady = sorted(activeReady, key=lambda x: x.A, reverse=False)
				# 	# Smalled arrival time
				# 	firstArrived = sortedActiveReady[0]

				# 	minArrival = []
				# 	for process in sortedActiveReady:
				# 		if process.A == firstArrived.A:
				# 			minArrival.append(process)

				# 	# favoring the process with the earliest arrival time A. 
				# 	if len(minArrival) == 1:
				# 		processToRun = minArrival[0]
				# 	else:
				# 		# favoring the process that is listed earliest in the input. 
				# 		sortedActiveReady = sorted(minArrival, key=lambda x: x.I, reverse=False)
				# 		processToRun = sortedActiveReady[0]
		
				# 	if len(self.states['running']) == 0:
				# 		self.updateState(processToRun, 'running')
				# 		PROCESSES.append(processToRun)

			# -------------------- BLOCKED PROCESSES --------------------- #		

			# if a process is in blocked state
				# decrement its remaining IO
				# if IO is 0 put it in ready state

			if (self.states['blocked']):

				temp = self.states['blocked'][:]
				for process in temp:
					if process not in PROCESSES:
						process.IO -= 1

						if process.IO == 0:
							if len(self.states['running']) == 0:
								self.updateState(process, 'running')
							else:
								self.updateState(process, 'ready')
							PROCESSES.append(process)

			# -------------------- UNSTARTED PROCESSE --------------------- #		

			# if there are processes in the "unstarted" state
				# check the arival time of the all processes in the unstarted queue 
				# put the process in the running state if:
				# process arrival time has come 
				# if there is no other process in the running state put in running
				# else put in ready

			if (self.states['unstarted']):
				temp = self.states['unstarted'][:]
				for process in temp:
					if process.A == self.clock:
						if len(self.states['running']) == 0:
							self.updateState(process, 'running')
						else:
							self.updateState(process, 'ready')
						PROCESSES.append(process)




			# Collect delaied logs here.
			self.logs += "Before cycle    " + str(self.clock + 1) + ":"

			for process in self.processTable.sortedStore:
				if process.state == 'running':
					burstRemaining = process.remainingBurst
				else:
					burstRemaining = process.IO

				self.logs += " " + spaces[process.state] + process.state + "  " + str(burstRemaining)
			self.logs += ".\n"

			# increment the clock after each loop
			self.clock += 1


			# Turn off scheduler if all processes are terminated
			if (len(self.states['terminated']) == self.processTable.count):
				self.active = False


processTable = ProcessTable("/Users/student/Desktop/input-4.txt");
print(processTable.view('sorted'))
scheduler = Scheduler(processTable)
scheduler.init()
#print(scheduler)














