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
			self.FCFS()
		elif self.algorithm == 'roundrobin':
			pass
		elif self.algorithm == 'lcfs':
			self.LCFS()
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
		if prevState == 'ready':

			toRemove = []
			c = 0
			for sub in self.states['ready']:

				for p in range(len(sub)):
					if Process == sub[p]:
						sub.remove(Process)
						break

				if not sub:
					toRemove.append(c)
				c += 1

			for rm in range(len(toRemove)):
				self.states['ready'].pop(rm)
		else:

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

		# Arrival:
			# Create a priority queue:
			# Same sub list if same time. (process.time)
			# [[p1],[p2,p3],[p4],[p5]]

		if newState == 'ready':

			if self.states['ready']:

				# last element in the ready list [[t=34],[t=35],[t=45X]]
				l = len(self.states['ready']) - 1
				# time of the sub list
				time = self.states['ready'][l][0].time

				if Process.time == time:
					self.states['ready'][l].append(Process)
				else:
					self.states['ready'].append([Process])

			else:
				self.states['ready'].append([Process])

			return

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

# -------------------------- LAST COME FIRST SERVE ----------------------------

	def LCFS(self):

		self.logs = "\nThis detailed printout gives the state and remaining burst for each process \nLCFS\n"
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

			# -------------------- BLOCKED PROCESSES --------------------- #		

			# if a process is in blocked state
				# decrement its remaining IO
				# if IO is 0 put it in ready state

			if (self.states['blocked']):

				#temp = sorted(self.states['blocked'][:], key=lambda x: x, reverse=True)
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

			# -------------------- READY PROCESSES --------------------- #		

			# If a process is in ready state 
				# increment the waitingtime of the process
				# if the running is empty put the process X in the running state
				# Finding process X:
					# first one in the queue if its arrival time in the ready state is unique and earliest
					# if more than one processes arrived at the same time, use tie breaker

			# Break Ties
				# These ties are broken
				# by favoring the process with the earliest arrival time A. 
				# If the arrival times are the same for two processes with the same priority, 
				# then favor the process that is listed earliest in the input. 

			if (self.states['ready']):
				# TODO: update waiting time

				processToRun = None

				to_pop = len(self.states['ready']) - 1

					# [[p],[p,p],[p],[p]]
				if len(self.states['ready'][to_pop]) == 1:
					processToRun = self.states['ready'][to_pop][0]

				else:
					# [[p,p],[p],[p,p]]
					subList = self.states['ready'][to_pop][:]

					# favoring the process with the earliest arrival time A. 
					sortedByArrival = sorted(subList, key=lambda x: x.A, reverse=False)
					smallest = sortedByArrival[0].A
					all_smallest = [element for index, element in enumerate(sortedByArrival) if smallest == element.A]

					if len(all_smallest) == 1:
						processToRun = all_smallest[0]
					else:
						# favoring the process that is listed earliest in the input.
						sortedByInput = sorted(subList, key=lambda x: x.I, reverse=False)
						processToRun = sortedByInput[0]

				if len(self.states['running']) == 0:					
					self.updateState(processToRun, 'running')
					PROCESSES.append(processToRun)


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


			# -------------------- COLLECTION LOGS FOR EACH INSTANCE --------------------- #

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

# -------------------------- FIRST COME FIRST SERVE ----------------------------

	def FCFS(self):

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
				# if the running is empty put the process X in the running state
				# Finding process X:
					# first one in the queue if its arrival time in the ready state is unique and earliest
					# if more than one processes arrived at the same time, use tie breaker

			# Break Ties
				# These ties are broken
				# by favoring the process with the earliest arrival time A. 
				# If the arrival times are the same for two processes with the same priority, 
				# then favor the process that is listed earliest in the input. 

			if (self.states['ready']):

				# TODO: update waiting time

				processToRun = None

					# [[p],[p,p],[p],[p]]
				if len(self.states['ready'][0]) == 1:
					processToRun = self.states['ready'][0][0]

				else:
					# [[p,p],[p],[p]]
					subList = self.states['ready'][0][:]

					# favoring the process with the earliest arrival time A. 
					sortedByArrival = sorted(subList, key=lambda x: x.A, reverse=False)
					smallest = sortedByArrival[0].A
					all_smallest = [element for index, element in enumerate(sortedByArrival) if smallest == element.A]

					if len(all_smallest) == 1:
						processToRun = all_smallest[0]
					else:
						# favoring the process that is listed earliest in the input.
						sortedByInput = sorted(subList, key=lambda x: x.I, reverse=False)
						processToRun = sortedByInput[0]

				if len(self.states['running']) == 0:					
					self.updateState(processToRun, 'running')
					PROCESSES.append(processToRun)


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


			# -------------------- COLLECTION LOGS FOR EACH INSTANCE --------------------- #

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



processTable = ProcessTable("/Users/student/Desktop/input-3.txt");
print(processTable.view('sorted'))
scheduler = Scheduler(processTable,'fcfs')
scheduler.init()
print(scheduler)














