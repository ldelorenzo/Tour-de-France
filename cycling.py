def cleanTime(strTime):
	return strTime.translate(None, 'inat ')


class StageTime:
	def __init__(self,strTime,baseTime=0):

		# Make time list (hours, minutes, seconds)
		timeList = strTime.split(':')
		if len(timeList) == 2:
			timeList.insert(0,0)

		self.seconds = int(timeList.pop())
		self.minutes = int(timeList.pop())
		self.hours = int(timeList.pop())
		self.baseTime = baseTime

	def offset(self):
		return self.seconds + 60*self.minutes + 3600*self.hours

	def totalTime(self):
		return self.baseTime + self.offset()





import numpy as np
import matplotlib.pyplot as plt
import csv
# Open file
with open("./Tour de France data/2014_stage20.csv") as csvfile:
	reader = csv.DictReader(csvfile,fieldnames=["place","name","team","time"])
	for row in reader:
		print(row["name"])	


# Open file
csvfile = open("./Tour de France/2014_stage20.csv","r") 
reader = csv.DictReader(csvfile,fieldnames=["place","name","team","time"])
cleanTime2 = []

baseTime = StageTime(cleanTime(reader.next()["time"])).totalTime()

results =[baseTime]
resultsOffset = [0]


for row in reader:
	test = cleanTime(row["time"])
	test2 = StageTime(test,baseTime).totalTime()
	print test2
	results.append(test2)
	resultsOffset.append(StageTime(test,baseTime).offset())
	#print test

print resultsOffset

print np.histogram(resultsOffset,bins=10)





#import pandas as pd
#df=pd.read_csv("./Tour de France/2014_stage20.csv")

