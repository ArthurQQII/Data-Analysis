#!/usr/bin/python3
import pandas as pd 
import os
import sys

"""
This function is used to put the result into a csv file

dictionList: a list of many dictionaries which keep all useful information and result
fileName: this parameter is used to define the name of the csv file
"""
def save_csv(dictionList, fileName):
    df = pd.DataFrame(dictionList, columns = ['block', 'trial', 'flankers', 
                                                'firstTime', 'firstValue',
                                                'detectTime', 'detectValue',
                                                'timeDifferent'])

    df.to_csv(fileName[:-11] + 'result.csv', index = False)


"""
This function will read the file and analyse the data in the file, all result 
will be saved to a list of many dictionaries. Then all the result will be saved 
to csv file

fileName: the name of the file which will be analysed

"""
def run(fileName):
    df = pd.read_csv(fileName, sep = "\t")
    blocks = df['block']  # list of block
    trials = df["trial"]  # list of trial
    times = df["time"]    # list of time
    values = df["value"]
    flankers = df["flankers"]
    blockTrialList = []
    dictionList = []
    for i in range(0, len(trials)):
        if times[i] > 0: # make sure the time is positive
            tempBlocktrial = {'block': blocks[i], 'trial': trials[i]}
            if tempBlocktrial not in blockTrialList: # find the first value
                blockTrialList.append(tempBlocktrial)
                tempValue = {'block': blocks[i], 'trial':trials[i], 
                'flankers' : flankers[i], 'firstTime': times[i], 
                'firstValue': values[i], 'detectTime': -1, 'detectValue': -1}
                dictionList.append(tempValue)
            else:
                # find the value that matches the rule
                if dictionList[len(dictionList) - 1]['detectTime'] == -1: 
                    if values[i] >= -0.5:
                        index = len(dictionList) - 1
                        dictionList[index]['detectTime'] = times[i]
                        dictionList[index]['detectValue'] = values[i]
                        dictionList[index]['timeDifferent'] = times[i] - dictionList[index]['firstTime']
    # save the data to a csv file
    save_csv(dictionList, fileName)
   
          

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
        print("Done!")