#!/usr/bin/python3
import pandas as pd 
import os
import sys

def save_csv(dictionList, fileName):
    df = pd.DataFrame(dictionList, columns = ['block', 'trial', 'flankers', 
                                                'firstTime', 'firstValue',
                                                'maxTime', 'maxValue',
                                                'timeDifferent'])

    df.to_csv(fileName[:-11] + 'result2.0.csv', index = False)


def run(filename):
    df = pd.read_csv(fileName, sep = "\t")
    blocks = df['block']  # list of block
    trials = df["trial"]  # list of trial
    times = df["time"]    # list of time
    values = df["value"]
    flankers = df["flankers"]
    blockTrialList = []
    dictionList = []

    for i in range(0, len(blocks)):
        tempMaxValue = -2
        if times[i] > 0: 
            tempBlocktrial = {'block': blocks[i], 'trial': trials[i]}
            if tempBlocktrial not in blockTrialList: # find the first value
                blockTrialList.append(tempBlocktrial)
                tempValue = {'block': blocks[i], 'trial':trials[i], 
                'flankers' : flankers[i], 'firstTime': times[i], 
                'firstValue': values[i], 'maxTime': -1, 'maxValue': tempMaxValue}
                dictionList.append(tempValue)
            else:
                if values[i] > dictionList[len(dictionList) - 1]['maxValue']:
                    index = len(dictionList) - 1
                    dictionList[index]['maxValue'] = values[i]
                    dictionList[index]['maxTime'] = times[i]
                    dictionList[index]['timeDifferent'] = times[i] - dictionList[index]['firstTime']

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