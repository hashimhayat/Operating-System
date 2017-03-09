'''
Lab 2 - Scheduling
Created by Hashim Hayat
Main: Scheduler
'''

import copy
from processhandler import *

class Scheduler:

	def __init__(self, processTable):

		self.processTable = copy.deepcopy(processTable)
		self.process_state = {}
		self.states = {
						'unstarted':[],
						'ready':[],
						'running':[],	
						'blocked':[],
						'terminated':[]
					}

		self.algorithm = 'fcfs' 		# Algorithm in use 
		self.clock = -1					# Time at which scheduler is right now.
		self.active = True 				# Indicates if the Scheduler is working or not
		self.X = 0						# next random number
		self.logs = self.initLogs()		# logs that are generated at the end
		self.algoInfo = self.algoInfo()	# Info about the algorithm being used <DEV / DEBUG>
		self.quantum = 0				# Quantum of the scheduler
		self.didNotTakeBurst = False

		# LOGGING INFO
		self.finishTime = 0
		self.CPUutilization = 0
		self.IOUtilization = 0
		self.throughput = 0
		self.avgTurnaround = 0
		self.avgWaitingTime = 0

		# DEBUG
		self.verbose = True

	# Initialises the Scheduler with the specified algorithm.
	def init(self,algo,q=2):

		self.algorithm = algo
		# Put all processes in the unstarted state
		self.initProcesses()

		if self.algorithm == 'fcfs':
			self.FCFS()
		elif self.algorithm == 'roundrobin':
			self.quantum = q
			self.roundRobin()
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

	def cleanReady(self):
		toRemove = []
		s = 0
		for _sub in self.states['ready']:
			if len(_sub) == 0:
				toRemove.append(s)
			s += 1

		for rm in toRemove:
			self.states['ready'].pop(rm)

	# Updates the state of a process (P).
	# Adding a process to the scheduler is also updation
	# so the same function can be used

	def updateState(self, Process, newState):

		prevState = Process.state

		# Remove the process from old state
		if prevState == 'ready':
			for sub in self.states['ready']:
				for p in range(len(sub)):
					if Process == sub[p]:
						sub.remove(sub[p])
						break
			self.cleanReady()
			
		if prevState != 'ready':
			self.states[prevState].remove(Process)

		if prevState == 'unstarted':
			Process.turnAroundTime = self.clock

		Process.state = newState
		Process.time = self.clock

		# Terminated
			# update finish time
		if newState == 'terminated':
			Process.finishTime = self.clock
			Process.turnAroundTime = self.clock - Process.turnAroundTime
			self.avgTurnaround += Process.turnAroundTime
			
		# Running:
			# calculate remainingburst
		if newState == 'running':

			self.CPUutilization += 1

			if self.algorithm == 'roundrobin':

				Process.Q = self.quantum

				if Process.remainingBurst <= 0:
					t,rand = self.randomOS(Process.B)

					if t > Process.remainingCPU:
						t = Process.remainingCPU
					Process.remainingBurst = t
	 				
					if self.verbose:
						self.logs += 'Find burst when choosing ready process to run ' + str(rand) + '\n'
			else:

				t,rand = self.randomOS(Process.B)

				if t > Process.remainingCPU:
					t = Process.remainingCPU
				Process.remainingBurst = t
 				
				if self.verbose:
					self.logs += 'Find burst when choosing ready process to run ' + str(rand) + '\n'

		# Blocked:
			# calculate remaining IO
		if newState == 'blocked':
			Process.IO,rand = self.randomOS(Process.M)
			
			if self.verbose:
				self.logs += 'Find I/O burst when blocking a process ' + str(rand) + '\n'

		# Arrival:
			# Create a priority queue:
			# Same sub list if same time. (process.time)
			# [[p1],[p2,p3],[p4],[p5]]

		if newState == 'ready':

			if self.states['ready']:
				l = len(self.states['ready']) - 1 			# last element in the ready list [[t=34],[t=35],[t=45X]]
				time = self.states['ready'][l][0].time		# time of the sub list
				self.states['ready'][l].append(Process) if Process.time == time else self.states['ready'].append([Process])
					
			else:
				self.states['ready'].append([Process])

			return

		# Enqueue it in the new state list
		self.states[newState].append(Process)

	def updateWaitingTime(self):

		for sub in self.states['ready']:
			for p in sub:
				p.waitingTime += 1
				self.avgWaitingTime += 1

	def updateIOtime(self):

		if self.states['blocked']:
			self.IOUtilization += 1

		for p in self.states['blocked']:
			p.IOtime += 1


	def preparingLogOff(self):
		self.finishTime = self.clock - 1 
		self.avgWaitingTime = ("%.6f" % round((self.avgWaitingTime + 0.0 / self.processTable.count + 0.0),7))
		self.avgTurnaround = ("%.6f" % round((self.avgTurnaround / self.processTable.count),7))
		self.IOUtilization = ("%.6f" % round((self.IOUtilization / self.finishTime),7))
		self.CPUutilization = ("%.6f" % round((self.CPUutilization / self.finishTime),7))
		self.throughput = ("%.6f" % round(((self.processTable.count / self.finishTime)*100),7))
		print(self)


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
		rand = self.getNextUDRI()
		return 1 + (rand % U), rand

	# Create the Result logs. Takes the ProcessTable.
	def createLogs(self):  

		PT = self.processTable

		logs = "\n"

		for p in range(len(PT.sortedStore)):

			logs += "Process " + str(p) + ":\n"
			logs += "        (A,B,C,M) = " + PT.sortedStore[p].__repr__() + "\n"
			logs += "        Finishing time: " + str(PT.sortedStore[p].finishTime) + "\n"
			logs += "        Turnaround time: " + str(PT.sortedStore[p].turnAroundTime) + "\n"
			logs += "        I/O time: " + str(PT.sortedStore[p].IOtime) + "\n"
			logs += "        Waiting time: " + str(PT.sortedStore[p].waitingTime) + "\n\n"

		logs += "Summary Data:\n"
		logs += "        Finishing time: " + str(self.finishTime) + "\n"
		logs += "        CPU Utilization: " + str(self.CPUutilization) + "\n"
		logs += "        I/O Utilization: " + str(self.IOUtilization) + "\n"
		logs += "        Throughput: " + str(self.throughput) + " processes per hundred cycles\n"
		logs += "        Average turnaround time: " + str(self.avgTurnaround) + "\n"
		logs += "        Average waiting time: " + str(self.avgWaitingTime) + "\n"
		return logs

	def initLogs(self):
		logs = self.processTable.view('unsorted') + '\n' + self.processTable.view('sorted') + '\n'
		logs += "\nThis detailed printout gives the state and remaining burst for each process \n\n"
		return logs

	def generateLogs(self): 
		self.logs += "Before cycle " + ' '* (4 - len(str(self.clock + 1))) + str(self.clock + 1) + ': '

		for process in self.processTable.sortedStore:
			remainingTime = process.Q if self.algorithm == 'roundrobin' else process.remainingBurst 
			burstRemaining = remainingTime if process.state == 'running' else process.IO
			self.logs += ' ' * (11 - len(process.state)) + process.state + '  ' + str(burstRemaining)
		self.logs += '.\n'


	def algoInfo(self):
		return {'lcfs':'Last Come First Served','fcfs':'First Come First Served','roundrobin':'Round Robin','pjfs':'Preemptive Shortest Job First'}

	# String Representation of the Scheduler
	def __repr__(self):
		#return self.createLogs(self.processTable)
		return self.logs + "The scheduling algorithm used was " + self.algoInfo[self.algorithm] + '\n' + self.createLogs()

# ------------------------------- ROUND ROBIN ---------------------------------

	def roundRobin(self):
	
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

				process = self.states['running'][0]
				process.remainingBurst -= 1
				process.remainingCPU -= 1
				process.Q -= 1

				if process.remainingCPU <= 0:	
					self.updateState(process, 'terminated')

				elif process.remainingBurst == 0:
					self.updateState(process, 'blocked')
			
				elif process.Q == 0:
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

				if len(self.states['running']) == 0 and processToRun not in PROCESSES:		
					self.updateState(processToRun, 'running')
					PROCESSES.append(processToRun)

			# -------------------- BLOCKED PROCESSES --------------------- #		

			# if a process is in blocked state
				# decrement its remaining IO
				# if IO is 0 put it in ready state

			if (self.states['blocked']):

				# block list is sorted in reverse order of its incoming time
				#temp = sorted(self.states['blocked'][:], key=lambda x: x.I, reverse=True)
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
				temp = sorted(self.states['unstarted'][:], key=lambda x: x.A, reverse=True)
				for process in temp:
					if process.A == self.clock:
						if len(self.states['running']) == 0:
							self.updateState(process, 'running')
						else:
							self.updateState(process, 'ready')
						PROCESSES.append(process)


			# Ensures that atleast one process runs if it in ready list
			if len(self.states['running']) == 0 and self.states['ready']:
				processToRun = self.states['ready'][0][0]
				self.updateState(processToRun, 'running')


			# -------------------- COLLECTION LOGS FOR EACH INSTANCE --------------------- #

			# Update Process Status

			self.updateWaitingTime()
			self.updateIOtime()

			# generate logs
			self.generateLogs()

			# increment the clock after each loop
			self.clock += 1

			# Turn off scheduler if all processes are terminated
			if (len(self.states['terminated']) == self.processTable.count):
				self.preparingLogOff()
				self.active = False



# -------------------------- LAST COME FIRST SERVE ----------------------------

	def LCFS(self):

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

				# block list is sorted in reverse order of its incoming time
				temp = sorted(self.states['blocked'][:], key=lambda x: x.I, reverse=False)
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

			self.cleanReady()
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


			# -------------------- COLLECTION LOGS FOR EACH INSTANCE --------------------- #

			# Update Process Status

			self.updateWaitingTime()
			self.updateIOtime()

			# generate logs
			self.generateLogs()

			# increment the clock after each loop
			self.clock += 1

			# Turn off scheduler if all processes are terminated
			if (len(self.states['terminated']) == self.processTable.count):
				self.preparingLogOff()
				self.active = False


# -------------------------- FIRST COME FIRST SERVE ----------------------------

	def FCFS(self):

		self.logs = "\nThis detailed printout gives the state and remaining burst for each process\n\n"

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

				temp = sorted(self.states['blocked'][:], key=lambda x: x.A, reverse=False)
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

			# Update Process Status

			self.updateWaitingTime()
			self.updateIOtime()

			# generate logs
			self.generateLogs()

			# increment the clock after each loop
			self.clock += 1

			# Turn off scheduler if all processes are terminated
			if (len(self.states['terminated']) == self.processTable.count):
				self.preparingLogOff()
				self.active = False		

filePath = "/Users/student/Desktop/Input/input-6.txt"

processTable = ProcessTable(filePath);
scheduler = Scheduler(processTable)
scheduler.verbose = False
scheduler.init('lcfs')















