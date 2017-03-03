'''
Lab 2 - Scheduling
Created by Hashim Hayat
Main: Scheduler
'''

import copy
from processhandler import *
from Algorithms import *


class Scheduler:

	def __init__(self, processTable, algo='fcfs'):

		self.processTable = copy.deepcopy(processTable)
		self.states = {
						'unstarted':[],
						'ready':[],
						'running':[],
						'blocked':[],
						'terminated':[]
					}

		self.algorithm = algo 		# Algorithm in use 
		self.clock = -1				# Time at which scheduler is right now.
		self.logs = ""

	# Initialises the Scheduler with the specified algorithm.
	def init(self):

		# Put all processes in the unstarted state
		self.initProcesses()

		if self.algorithm == 'fcfs':
			pass
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

	# Updates the state of a process (P).
	# Adding a process to the scheduler is also updation
	# so the same function can be used
	def updateState(self, Process, newState):

		prevState = Process.state

		# Remove the process from old state
		self.states[prevState].remove(P)

		# Update the state of process:
		#  - self.state = 'unstarted'
		#  - self.IO = 0
		#  - self.finishTime = 0
		#  - self.turnAroundTime = 0
		#  - self.waitingTime = 0

		Process.state = newState

		# Enqueue it in the new state list
		self.states[Process.state].append(Process)

	# -------------------- Random Numbers --------------------- #

	# Reads the next Random number from the file
	# Stores that in self.nextR
	def getNextRandom(self,U):
		with open('random-numbers.txt','r') as randoms:
			for i, random in enumerate(randoms):
				if i == U:
					return int(random)

	# The simple function randomOS(U), which you are to write, reads a random non-negative integer 
	# X from a file named random-numbers (in the current directory) and returns the value 1 + (X mod U).
	def randomOS(self,U):
		return 1 + (self.getNextRandom(U) % U)

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
		return self.createLogs(self.processTable)

	def FSFS(self):

		while (self.running):


			# increment the clock after each loop
			self.clock += 1


processTable = ProcessTable("/Users/student/Desktop/input-7.txt");

scheduler = Scheduler(processTable)
scheduler.init()
print(scheduler)














