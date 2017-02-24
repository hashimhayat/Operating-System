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
		self.states = {
						'unstarted':[],
						'ready':[],
						'running':[],
						'blocked':[],
						'terminated':[]
					}

		self.algorithm = algo 		# Algorithm in use 
		self.time = 0				# Time at which scheduler is right now.
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
	def updateState(self, P, newState):

		# Remove the process from old state
		self.states[P.state].remove(P)

		# Update state of the Process itself
		P.state = newState

		# Enqueue it in the new state list
		self.states[P.state].append(P)

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

	# Update the logs before each cycle.
	def updateLogs(self):
		# Before cycle    0:   unstarted  0  unstarted  0  unstarted  0  unstarted  0  unstarted  0.
		self.logs += "Before cycle    " + self.time

		# for p in self.processTable.sortedStore:
		# 	self.logs


		"unstarted  " + self.states['unstarted']

	# String Representation of the Scheduler
	def __repr__(self):
		return self.logs


processTable = ProcessTable("/Users/student/Desktop/input-7.txt");

# print(processTable.view('unsorted'))
# print(processTable.view('sorted'))

scheduler = Scheduler(processTable)
scheduler.init()
print(scheduler)

















