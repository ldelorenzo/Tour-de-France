# Playing with tour de france individual time trial data

import re
import numpy as np
import matplotlib.pyplot as plt
import csv
import translitcodec
import datetime as dt
from matplotlib.dates import date2num   # dont understand why
from scipy.stats import norm
import scipy.stats





def cleanTime(fileTime):
  strTime = fileTime.translate(None, 'inat ')


  # Convert from utf-8 to ASCII
  strTimeA = strTime.decode('utf-8').encode('translit/long').encode('ascii')

  # Make time list (hours, minutes, seconds)
  if "'" in strTimeA:
    timeList = list(re.compile(r"(?:(\d+)h)?(\d+)\'(\d+)\'\'").match(strTimeA).groups())

  else:
    timeList = strTimeA.split(':')


  if timeList[0] == ''  or timeList[0] is None:
    timeList[0] = 0
  if len(timeList) == 2:
    timeList.insert(0,0)

  return timeList






class StageTime:
  def __init__(self,timeList,baseTime=0):

    self.seconds = int(timeList.pop())
    self.minutes = int(timeList.pop())
    self.hours = int(timeList.pop())
    self.baseTime = baseTime

  def offset(self):
    return self.seconds + 60*self.minutes + 3600*self.hours

  def totalTime(self):
    return self.baseTime + self.offset()



def cleanName(strName):
  return strName.decode('utf-8').encode('translit/long').encode('ascii').lower().lstrip()

class ReadData:
  def __init__(self, filename):

    csvfile = open(filename,"r")
    reader = csv.DictReader(csvfile,fieldnames=["place","name","team","time"])
    baseTime = StageTime(cleanTime(reader.next()["time"])).totalTime()
    results =[baseTime]
    resultsOffset = [0]
    for row in reader:
      tempTime = cleanTime(row["time"])
      totalTime= StageTime(tempTime,baseTime).totalTime()
      results.append(totalTime)
      resultsOffset.append(StageTime(tempTime,baseTime).offset())

    self.results = results
    self.resultsOffset = resultsOffset


class ReadNames:
  def __init__(self, filename):
    csvfile = open(filename,"r")
    reader = csv.DictReader(csvfile,fieldnames=["place","name","team","time"])
    names =[]
    for row in reader:
      name=row["name"].decode('utf-8').encode('translit/long').encode('ascii').lower().lstrip()
      names.append(name)

    self.names = names


class Cyclist:
  def __init__(self,name):
    self.name =name
    self.performances = []

  def addPerformance(self, performance):
    self.performances.append(performance)



#  def listPerfs(self):
#    return self.performances


# Class of Performances.. stores race, cyclist, finishing place, total time, offset time from winner
class Performance:
  def __init__(self, race, cyclist, place, offsetTime):
    self.race = race
    self.cyclist = cyclist
    self.place = place
    self.offsetTime = offsetTime

# Class Races, has attributes performances
class Race:
  def __init__(self, name, date, winningTime):
    self.name = name
    self.date = date
    self.winningTime = winningTime
    self.performances = []


  def addPerformance(self, performance):
    self.performances.append(performance)



# Find race name from name of file
def getRace(filename):
  front = filename.split(".csv")[0]
  return front.split("/").pop()


def getDate(raceName):
  csvfile = open("./Tour de France data/races.csv","r")
  reader = csv.DictReader(csvfile,fieldnames=["raceName","date","distance"])
  for row in reader:
    if raceName == row["raceName"]:
      dateTemp =  row["date"]
      format = "%m-%d-%Y"
      return dt.datetime.strptime(dateTemp, format)


def findNorm(race):
  allTimes = [perf.offsetTime for perf in race.performances]
  return norm.fit(allTimes)

def findNorm2(race):
  allTimes = [perf.totalTime for perf in race.performances]
  return norm.fit(allTimes)







# Initiate dictionary of all races/cyclists
raceDict = {}
cyclistDict = {}

def addDict(filename):

  csvfile = open(filename,"r")
  reader = csv.DictReader(csvfile,fieldnames=["place","name","team","time"])

  firstRow = reader.next()
  winningTime = StageTime(cleanTime(firstRow["time"])).totalTime()
  raceName = getRace(filename)
  raceDate = getDate(raceName)
  race = Race(raceName,raceDate,winningTime)


  #Deal with first row by itself because it is formatted differently
  offsetTime = 0
  name = cleanName(firstRow["name"])
  perf = Performance(race, name,firstRow["place"], offsetTime)
  print firstRow["place"]
  # If cyclist already in dictionary, retrieve
  cyclist = cyclistDict.get(name)

  # Otherwise create new
  if cyclist is None:
    cyclist = Cyclist(name)

  # Add performance to cyclist, add cyclist to dictionary
  cyclist.addPerformance(perf)
  cyclistDict[name] = cyclist

  # Add performance to race
  race.addPerformance(perf)

  #csvfile.seek(0)       # resets csv iterator to 0
  for row in reader:
    offsetTime = StageTime(cleanTime(row["time"]),winningTime).offset()
    name = cleanName(row["name"])
    perf = Performance(race, name,row["place"], offsetTime)

    # If cyclist already in dictionary, retrieve
    cyclist = cyclistDict.get(name)

    # Otherwise create new
    if cyclist is None:
      cyclist = Cyclist(name)

    # Add performance to cyclist, add cyclist to dictionary
    cyclist.addPerformance(perf)
    cyclistDict[name] = cyclist

    # Add performance to race
    race.addPerformance(perf)

  # Add race to race dictionary
  raceDict[raceName] = race

filenames = ["./Tour de France data/2014_stage20.csv","./Tour de France data/2013_stage17.csv","./Tour de France data/2013_stage11.csv","./Tour de France data/2012_stage19.csv", "./Tour de France data/2012_stage9.csv", "./Tour de France data/2011_stage20.csv", "./Tour de France data/2010_stage19.csv"]

for name in filenames:
  addDict(name)


# Testing

#allTimes = [perf.offsetTime for perf in raceDict["2014_stage20"].performances]
#print allTimes
#alloffsets = [perf.offsetTime for perf in raceDict["2014_stage20"].performances]
#print alloffsets



#for key in cyclistDict:
#  print key, 'corresponds to', [perf.place for perf in cyclistDict[key].performances]


#print sorted(cyclistDict.keys())





x=[]
y=[]
label =[]
cyclist = "tony martin"



for perf in cyclistDict[cyclist].performances:
  lookup = perf.race.name
  print lookup
  (mu, std) = findNorm(raceDict[lookup])
  print mu
  print std
  label.append(raceDict[lookup].date)
  x.append(date2num(raceDict[lookup].date))
  offset = perf.offsetTime
  print offset
  cdfPlace = scipy.stats.norm(loc=mu,scale=std).cdf(offset)
  print cdfPlace
  print perf.place
  y.append(cdfPlace)



print x
print y



fig = plt.figure()
graph = fig.add_subplot(111)
graph.plot(x,y,'b-o')
# Set the xtick locations to correspond to just the dates you entered.
graph.set_xticks(x)
# Set the xtick labels to correspond to just the dates you entered.
graph.set_xticklabels(
        [date.strftime("%Y-%m-%d") for date in label]
        )
plt.xlabel('Race Date')
plt.ylabel('Place')
plt.show()







"""
# Open file
csvfile = open("./Tour de France data/2014_stage20.csv","r")
reader = csv.DictReader(csvfile,fieldnames=["place","name","team","time"])

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
  """
'''
y2014Stage20 = ReadData("./Tour de France data/2014_stage20.csv")
y2014Stage20RO = y2014Stage20.resultsOffset


y2013Stage17RO = ReadData("./Tour de France data/2013_stage17.csv").resultsOffset


y2013Stage11RO = ReadData("./Tour de France data/2013_stage11.csv").resultsOffset


y2012Stage19 = ReadData("./Tour de France data/2012_stage19.csv")
y2012Stage19RO = y2012Stage19.resultsOffset

y2012Stage9RO = ReadData("./Tour de France data/2012_stage9.csv").resultsOffset


y2011Stage20RO = ReadData("./Tour de France data/2011_stage20.csv").resultsOffset

y2010Stage19RO = ReadData("./Tour de France data/2010_stage19.csv").resultsOffset
print y2010Stage19RO

plt.hist(y2010Stage19RO)
plt.title('')
plt.xlabel('Time (s)')
plt.ylabel('Count')
plt.show()

'''
'''
y2011Stage20RO = ReadData("./Tour de France data/2011_stage20.csv").resultsOffset


# Fit a normal distribution to the data:
mu, std = norm.fit(y2011Stage20RO)

# Plot the histogram.
plt.hist(y2011Stage20RO, bins=25, normed=True, color='r')

# Plot the PDF.
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
p = norm.pdf(x, mu, std)
plt.plot(x, p, 'k', linewidth=2)
title = "Fit results: mu = %.2f,  std = %.2f" % (mu, std)
plt.title(title)
plt.xlabel('Offset Time (s)')
plt.ylabel('Probability')

plt.show()

# Gives the cdf of a given number for a given normal distribution
print scipy.stats.norm(loc=mu,scale=std).cdf(500)


plt.hist(y2011Stage20RO,bins=25)
plt.title('')
plt.xlabel('Time (s)')
plt.ylabel('Count')
plt.show()
'''
#import pandas as pd
#df=pd.read_csv("./Tour de France/2014_stage20.csv")

