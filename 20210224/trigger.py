#!/usr/bin/python3
import pandas as pd 
import os
import sys

dictionList = []

"""
save the data to a file
"""
def save_csv(dictionList):
    df = pd.DataFrame(dictionList, columns = ['data', 'block', 'trial', 'oneTrigger', 'trigger'])
    df.to_csv(os.getcwd() + '/trigger.csv', index = False)

"""
read all data to check each block and trial have a trigger or or two
"""
def run(fileName):
    df = pd.read_csv(fileName, sep = "\t")
    file = os.path.split(fileName)[1][:-11]
    blocks = df['block'] 
    trials = df["trial"]
    times = df["time"] 
    triggers = df["trigger"]
    blockTrialList = []
    for i in range(0, len(trials)):
        if times[i] > 0:
            tempBlocktrial = {'block': blocks[i], 'trial': trials[i]}
            if tempBlocktrial not in blockTrialList: # find the first value
                blockTrialList.append(tempBlocktrial)
                tempValue = {'data': file, 'block': blocks[i], 'trial':trials[i], 'oneTrigger': 1, 'trigger': triggers[i]}
                dictionList.append(tempValue)
            else:
                index = len(dictionList) - 1
                if dictionList[index]['trigger'] != triggers[i]:
                    dictionList[index]['trigger'] = "left/right"
                    dictionList[index]['oneTrigger'] = 0

    

if __name__ == "__main__":
    # no directory input or too many 
    if len(sys.argv) != 2:
        print("You need to input a directory like: python3 main.py <directory>")
    # input value is not a directory
    elif os.path.isdir(os.getcwd() + '/' + sys.argv[1]) == False:
        print("You need to input a directory not a file")
    else:
        print("processing.....")
        directory = '/' + sys.argv[1] + '/'
        path = os.listdir(os.getcwd() + directory)
        for p in path:
            if os.path.isdir(os.getcwd() + directory + p):
                filesCurrent = os.listdir(os.getcwd() + directory + p)
                for f in filesCurrent:
                    if f[-11:] == "trigger.txt":
                        fileName = os.getcwd() + directory + p + "/" + f
                        run(fileName)

        save_csv(dictionList)
        print("Done!")