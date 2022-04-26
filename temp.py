#checks pairs of words against US-SUBLTEX, appends freq
import json
import xlrd
import nltk
import csv
import string
import pandas as pd
import time

def getfreqs(pair):
    src = pair[0].lower()
    tgt = pair[1].lower()
    wb = xlrd.open_workbook('sortedSUBTLEXusfrequencyabove1.xls')
    sheet = wb.sheet_by_index(0)

    #loop through corpus, check for matches with pair words
    #append found frequencies to pair array
    for i in range(sheet.nrows):
        if src == sheet.cell_value(i,0):
            if len(pair)==4:
                print(1)
                pair[2] = sheet.cell_value(i,1)
            else:
                print(2)
                pair.append(sheet.cell_value(i,1))
        if tgt == sheet.cell_value(i,0):
            if len(pair)==3:
                print(3)
                pair.append(sheet.cell_value(i,1))
            else:
                print(4)
                pair.append(0)
                pair.append(sheet.cell_value(i,1))
    #the following if statements fill out remaining 0's
    if len(pair)==3:
        pair.append(0)
    if len(pair)!=4:
        print("no matches")
        pair.append(0)
        pair.append(0)

def binSearchgetfreqs(pair):
    src = pair[0].lower()
    tgt = pair[1].lower()
    wb = xlrd.open_workbook('sortedSUBTLEXusfrequencyabove1.xls')
    sheet = wb.sheet_by_index(0)

    pair.append(0)
    pair.append(0)


    srcIndex = binary_search_recursive(sheet,src,1,sheet.nrows)
    tgtIndex = binary_search_recursive(sheet,tgt,1,sheet.nrows)
    print(srcIndex,sheet.cell_value(srcIndex,0))
    print(tgtIndex,sheet.cell_value(tgtIndex,0))

    if srcIndex !=-1:
        pair[2] = sheet.cell_value(srcIndex,1)
    if tgtIndex !=-1:
        pair[3] = (sheet.cell_value(tgtIndex,1))



def binarySearch(sheet, word, low, high):
    # Repeat until the pointers low and high meet each other
    while low <= high:
        mid = low + (high - low)//2
        if sheet.cell_value(mid,0).lower() == word:
            return mid
        elif sheet.cell_value(mid,0).lower() < word:
            #print(sheet.cell_value(mid,0),word,low,high)
            low = mid + 1
        else:
            #print(word,sheet.cell_value(mid,0),low,high)
            high = mid - 1
    return -1

def binary_search_recursive(sheet, word, start, end):
    if start > end:
        return -1
    mid = (start + end) // 2
    if word == sheet.cell_value(mid,0).lower():
        return mid
    if word < sheet.cell_value(mid,0).lower():
        return binary_search_recursive(sheet, word, start, mid-1)
    else:
        return binary_search_recursive(sheet, word, mid+1, end)

if __name__ == '__maind__':
    a = ["letter","any"]
    b = ["chunkle","bingbong"]
    c = ["a","chunkle"]
    d = ["letr","a"]
    binSearchgetfreqs(a)
    binSearchgetfreqs(b)
    binSearchgetfreqs(c)
    binSearchgetfreqs(d)
    print(a)
    print(b)
    print(c)
    print(d)


def method_pandas_chunks(Error: str, Target: str) -> dict:
    """
    Find passport number and series using Pandas in chunks
    :param filename:csv filename path
    :param series: passport series
    :param number: passport number
    :return:
    """
    chunksize = 10 ** 5
    for df in pd.read_csv("t2.csv", chunksize=chunksize, dtype={'Err': str,'Tgt':str}):

      df_search = df[(df['Err'] == Error) & (df['Tgt'] == Target)]

      if not df_search.empty:
        break

    if not df_search.empty:
        return {'result': True, 'message': 'Passport found'}
    else:
        return {'result': False, 'message': 'Passport not found in Database'}

def searchcsv():
    df = pd.read_csv("t2.csv")
    res = df[(df["mistake"]=="is") & (df["fix"]=="if")]
    print(res)
    print(len(res))
    
    
if __name__ == '__main__':
    #method_pandas_chunks("is","if")
    searchcsv()
