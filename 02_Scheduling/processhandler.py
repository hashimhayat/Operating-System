'''
Lab 2 - Scheduling
Created by Hashim Hayat
Module: File Handler
'''
import os

class Process:
	def __init__(self,A,B,C,M):
		self.A = A 					#-> Arrival time
		self.B = B 					#-> CPU burst
		self.C = C 					#-> Total CPU required by the job
		self.M = M 					#-> Multiplier to find I/O burst = B x M
		self.state = 'unstarted'	#-> State of a process

		# Loging Times
		self.IO = 0
		self.finishTime = 0
		self.turnAroundTime = 0
		self.waitingTime = 0

	# Returns a string representation of a process
	def __repr__(self):
		return '(' + str(self.A) + ' ' + str(self.B) + ' ' + str(self.C) + ' ' + str(self.M) + ')'

class ProcessTable:
	def __init__(self,filePath):
		self.count = 0
		self.store = []
		self.sortedStore = []
		self.readFile(filePath)

	# Read Jobs:
	# Reads the job data from a file and returns the raw data as a string
	# input: 3 (0 1 20 1) (0 1 20 1) (10 1 10 1)

	def readFile(self,filePath):
		fd = open(filePath,'r')
		content = fd.read().strip().replace(")","").replace("(","- ").split(" - ")
		self.count = int(content[0])
		self.buildStore(content,self.count)
		
		fd.close()

	# Parse the raw data and returns process objects

	def buildStore(self,content,processes):
		
		# go to each process (0 1 20 1)
		# create a process and append it in the store
		for p in range(1,processes+1):

			P = content[p].split(" ")	# P is a temp process
			process = Process(int(P[0]),int(P[1]),int(P[2]),int(P[3]))
			self.store.append(process)

		self.sortProcesses()

	# Sort processes by arrival time A

	def sortProcesses(self):
		self.sortedStore = sorted(self.store, key=lambda x: x.A, reverse=False)

	# View string reps of processes in the Process Table
	# Takes sorted or unsorted as argument

	def view(self,ty='sorted'):

		tmpList = []

		if ty == 'sorted':
			tmpList = self.sortedStore
			result = "The original input was: " + str(self.count) + " "
		elif ty == 'unsorted':
			tmpList = self.store
			result = "The (sorted) input is:  " + str(self.count) + " "

		for i in range(self.count):
			result += tmpList[i].__repr__() + " "

		return result

		

















