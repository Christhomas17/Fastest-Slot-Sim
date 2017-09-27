# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
import pandas as pd
import numpy as np
import random as rd
import re

import os

import datetime

from OpenPyXLHelperFunctions import data_from_range
import openpyxl


#file = 'CinderellaTheGlassSlipper_V01_New.xlsx'
#wb = openpyxl.load_workbook(file)


def convert_lines_to_positive_values(x):
    tempMin = 0
    for item in x:
        tempMin = min(item)

    if tempMin < 0:
        for rowIndex,row in enumerate(x):
            for colIndex,item in enumerate(row):
                x[rowIndex][colIndex] = item + abs(tempMin)
                
    return(x)
    
def get_reel_length(df,count):
    totalLength = len(df)
    length = [totalLength - sum(pd.isnull(df[i][:])) for i in range(count)]
    return(length)

def get_stops(numReels,length):
    return([rd.randint(0,length[i]-1) for i in range(numReels)])

def get_line_win(lineSymbols, includedSymbols, symbolList,payTable):
    counts = [0]*len(symbolList)
    for index,curSymbol in enumerate(symbolList):
        
        for symbol in lineSymbols:
            if symbol in includedSymbols[curSymbol]:
                counts[index] += 1
            else:
                break
            
    tempPays = [0]*len(symbolList)
    for index,symb in enumerate(symbolList):
        try:        
            tempPays[index]=payTable[symb][counts[index]]
        except:
            tempPays[index] = 0
    
    return(max(tempPays))




def create_symbol_list(symbols,scatter):
    rows,cols=symbols.shape
    includedSymbols={}
    symbolsList = list(symbols.index)
    
    for row in range(rows):
        tempList=[]
        for col in range(cols):
            if not pd.isnull(symbols.iloc[row,col]):
                tempList.append(symbols.iloc[row,col])
                
        tempList=tempList
        includedSymbols[symbolsList[row]]=tempList
        
    symbolsList.remove(scatter)
    
    return(includedSymbols,symbolsList)
 

def get_scatter_win(window,scatter,payTable):
#    window = [reels[(stop[i]+row)%reelLengths[i]][i] for i in range(numReels) for row in windowOffsets]
#    count = window.count(scatter)  
    count = 0
    
    for item in window:
        count += item.count(scatter)

    try:
        pay = payTable[scatter][count]
    except:
        pay = 0        
    return([pay,count])

def get_window_symbols(reels,stop,numReels, reelLengths,windowOffsets):    
    #creates list of lists(like matrix)
    window = [[reels[(stop[i]+row)%reelLengths[i]][i] for i in range(numReels)] for row in windowOffsets]
    return(window)

def clean_and_get_reel_info(reelsAsDf):
    reels = reelsAsDf
    numReels = reels.shape[1]
    reelLengths=get_reel_length(reels,numReels)
    reels = [tuple(x) for x in reels.to_records(index=False)]
    
    return([reels,reelLengths,numReels])

def replace_fairy(window,fairy,cinderella,servant,wild, numLines):
    numRows = len(window)
    numCols = len(window[0])
    
    fairyPresent = False
    fairyPay = 0
    
    for row in range(numRows):
        col = 4
        if window[row][col] == fairy:
            fairyPresent = True
            break
            
    count = 0
    if fairyPresent:
        for row in range(numRows):
            for col in range(numCols):
                if window[row][col] == servant:                    
                    window[row][col] = cinderella
                    
        for row in range(numRows):
            for col in range(numCols):
                if window[row][col] in [wild,cinderella,fairy]: 
                    count += 1
                else:
                    return(window,0)
                
    if count == numRows*numCols:
#        print(window) 
        fairyPay = 50*numLines
            
    return(window,fairyPay)

def replace_free_fairy(window,fairy,cinderella,servant,wild, numLines,fgMult):
    numRows = len(window)
    numCols = len(window[0])
    
    fairyPresent = False
    fairyPay = 0
    
    for row in range(numRows):
        col = 4
        if window[row][col] == fairy:
            fairyPresent = True
            break
            
    count = 0
    if fairyPresent:
        for row in range(numRows):
            for col in range(numCols):
                if window[row][col] == servant:                    
                    window[row][col] = cinderella
                    
        for row in range(numRows):
            for col in range(numCols):
                if window[row][col] in [wild,cinderella,fairy]: 
                    count += 1
                else:
                    return(window,0,fairyPresent)
                
    if count == numRows*numCols:
#        print(window) 
        fairyPay = 50*numLines*fgMult
            
    return(window,fairyPay,fairyPresent)




def play_base(reels,reelLengths,numReels,symbolsList,includedSymbols,windowOffsets,
              lines,payTable,scatter,numLines,wild,fairy,servant,cinderella):
    totalPay = 0 
    stop = get_stops(numReels,reelLengths)
    window = get_window_symbols(reels,stop,numReels,reelLengths,windowOffsets)
#    print(window)
    
    window,fairyPay = replace_fairy(window,fairy,cinderella,servant,wild,numLines)
    totalPay += fairyPay
                    
#    print(window)
    for line in lines:
        lineSymbols = get_line_symbols(window,line,numReels)
        totalPay += get_line_win(lineSymbols, includedSymbols, symbolsList,payTable)
#        
    scatterWin,scatterCount = get_scatter_win(window,scatter,payTable)
    totalPay = totalPay + scatterWin*numLines
    
    return(totalPay,scatterCount)


def get_free_line_win(lineSymbols, includedSymbols, symbolList,payTable):
    counts = [0]*len(symbolList)    
    for index,curSymbol in enumerate(symbolList):
        
        for symbol in lineSymbols:
            if symbol in includedSymbols[curSymbol]:
                counts[index] += 1
            else:
                break
        
        
            
            
    tempPays = [0]*len(symbolList)
    for index,symb in enumerate(symbolList):
        try:        
            tempPays[index]=payTable[symb][counts[index]]            
            
        except:
            tempPays[index] = 0
    
    return(max(tempPays))


def play_free(reels,reelLengths,numReels,symbolsList,includedSymbols,windowOffsets,
              lines,payTable,scatter,numLines,wild,fairy,servant,cinderella,fgMult):
    totalPay = 0 
    stop = get_stops(numReels,reelLengths)
    window = get_window_symbols(reels,stop,numReels,reelLengths,windowOffsets)
    
    window,fairyPay,fairyPresent = replace_free_fairy(window,fairy,cinderella,servant,wild,numLines,fgMult)
    totalPay += fairyPay
    
    if fairyPresent:
        #written like this for clarity
        fgMult = fgMult
    else:
        fgMult = 1
                    
    for line in lines:
        lineSymbols = get_line_symbols(window,line,numReels)
        totalPay += get_free_line_win(lineSymbols, includedSymbols, symbolsList,payTable)*fgMult
      
    scatterWin,scatterCount = get_scatter_win(window,scatter,payTable)
    totalPay = totalPay + scatterWin*numLines
    
    return(totalPay,scatterCount)



def get_line_symbols(window,line,numReels):     
     return([window[line[i]][i] for i in range(numReels)])
 

def play(n,file):
###########################
#Import Data
    wb = openpyxl.load_workbook(file, read_only = True, data_only= True)
    baseReels = data_from_range('AI4:Am104','Basic',wb)
    freeReels  = data_from_range('AH4:AL133','Feature',wb)
    basePayTable = pd.read_excel("BasePays.xlsx", header = 0, index_col=0)
    freePayTable = pd.read_excel('FreePays.xlsx',header = 0, index_col = 0)
    symbols = pd.read_excel("Symbols.xlsx",header = 0, index_col=0)
    freeSymbols = pd.read_excel('FreeSymbols.xlsx', header = 0 ,index_col = 0)
    
    fgMult = data_from_range('AB132','Feature',wb)
    fgMult = fgMult[0][0]
    
    simulatedReturn = data_from_range('Z205', 'Basic',wb)[0][0]
    
    wb.close()
    
    baseWindowOffsets = pd.read_table('ReelOffsets.txt', header = None)
    freeWindowOffsets = pd.read_table('FreeReelOffsets.txt', header = None)
    lines = pd.read_table('Lines.txt', header = None, sep = ',')
    freeLines = pd.read_table('FreeLines.txt', header = None, sep = '\t')
    
#############################    
#define constants
    scatter = 'Sp'    
    wild = 'Wild'    
    fairy = 'Fairy'
    servant = 'Sv'
    cinderella = 'Ci'
    
    reelHeights = [3]*5
############################
#clean up data, and make it faster
    baseReels,baseReelLengths,baseNumReels = clean_and_get_reel_info(baseReels)
    freeReels,freeReelLengths,freeNumReels = clean_and_get_reel_info(freeReels)
    
    

    lines = lines.values.tolist()
    lines = convert_lines_to_positive_values(lines)
    numLines = len(lines)
    
    freeLines = freeLines.values.tolist()
    
    
    basePayTable = basePayTable.to_dict("index")
    freePayTable = freePayTable.to_dict("index")

    baseIncludedSymbols,baseSymbolsList=create_symbol_list(symbols,scatter)
    freeIncludedSymbols, freeSymbolsList = create_symbol_list(freeSymbols,scatter)
   

    baseWindowOffsets = baseWindowOffsets[0].tolist()
    freeWindowOffsets = freeWindowOffsets[0].tolist()
    
    
    
    #used only for debugging purposes
#    reels = baseReels
#    reelLengths = baseReelLengths
#    numReels = baseNumReels
#    symbolsList = baseSymbolsList
#    includedSymbols = baseIncludedSymbols
#    payTable = basePayTable
#    windowOffsets = baseWindowOffsets
#    
#    reels = freeReels
#    reelLengths = freeReelLengths
#    numReels = freeNumReels
#    symbolsList = freeSymbolsList
#    includedSymbols = freeIncludedSymbols
#    payTable = freePayTable
#    lines = freeLines
#    windowOffsets = freeWindowOffsets
    
    
    mod=n/100
   
    
    totalPay = 0
    scatterHits = 0
    totalReturn = 0
    
    for i in range(n):
        if i%mod ==0:
            print(i, totalReturn)
            
            
        windowWin,windowScatterCount = play_base(baseReels,baseReelLengths,
                                                 baseNumReels,baseSymbolsList,baseIncludedSymbols,
                                                 baseWindowOffsets,lines,basePayTable,scatter,numLines,
                                                 wild,fairy,servant,cinderella)
        
#        stop = get_stops(baseNumReels,baseReelLengths)
#        window = get_window_symbols(baseReels,stop,baseNumReels,baseReelLengths,baseWindowOffsets)
#        scatterPay,windowScatterCount = get_scatter_win(window,scatter,basePayTable)
        totalPay += windowWin
        
        if windowScatterCount >= 3: 
#            print(window)
            scatterHits += 1
            freeGamesRemaining = 8
            
            while freeGamesRemaining > 0:
            
                freePay, freeScatterCount = play_free(freeReels,freeReelLengths,
                                                      freeNumReels,freeSymbolsList,freeIncludedSymbols,
                                                      freeWindowOffsets,freeLines,freePayTable,scatter,numLines,
                                                      wild,fairy,servant,cinderella, fgMult)
                totalPay += freePay
                
                if freeScatterCount >= 2:
                    freeGamesRemaining += 5
                    
                freeGamesRemaining -= 1
                
                totalReturn = totalPay/i/numLines
                
    print(totalReturn)
    return(float(totalReturn),scatterHits/n,simulatedReturn)
#    return(totalPay/n/numLines,scatterHits/n)    



#n = 1000    

#start = datetime.datetime.now()
#
#x,y = play(n)
##print(x)
#end = datetime.datetime.now()
#print('%f return after %d iterations which took %s' % (x,n,end - start))
##print("%s helllo" % (str(x)))
#
#print('it took %s time to complete %d iterations' %(end-start, n))


#file = open('results.txt','w')
#
#for i in range(10):
##    start = datetime.datetime.now()
#
#    x = play(n)
#    file.write(x + '\n')
#    
#    end = datetime.datetime.now()
#    
#    print('it took %s time to complete %s iterations %s' %(end-start, n,x))
#
#
##    file.write( 'it took %s time to complete %s iterations with a final return of %s \n' %(end-start, n,x))
#    
#f.close()

def do_all():
    n = 10000000
    
    files = os.listdir()
    
    temp = []
    for file in files:
        try:
            filename, extension = file.split('.')
            if extension == 'xlsx':
                if re.search('^Cinderella',filename):
                    temp.append(filename + '.' + extension)
        except:
           pass 
            
    files = temp
    
    
        
    for filename in files:
#        print(filename)
        start = datetime.datetime.now()
        totReturn,scatter,simReturn = play(n,filename)
        end = datetime.datetime.now()
        
        with open(filename + '.txt', 'w') as file:
        
            file.write('%s - Simulated return of  %.4f  vs %.4f after %d iterations which took %s' % (filename,totReturn,simReturn, n,end - start))
    


if __name__ == '__main__':
    do_all()















