#packages
import json
import xlrd
import nltk
import csv
import string
import pandas as pd
from nltk.metrics.distance import *

'''
#####Version 6 (refactored)#####


To do:
optimize getfreqs (bottleneck)
convert outputs from csv to xlws
merge identical results on output files 
comments for search results

plan of action:
change getfreqs to binary search DONE
change writetocsv for all errors
add new function to clean results.csv into a freq>0results.csv

tier 1 cleaning on raw results (lexical/typing execution)_(exchnages, transpositions, compound errors, etc)
re filter tier 2 errors

xlrd manipulation to output filtered data in 1 sheet
'''


#list of entries 
items = []
endEntryCount = 5000


#parse JSONL with indent to dict
def parse(filename,total):
    #open JSONL
    print("Starting parse...")
    with open(filename,'r',encoding='utf8', errors='ignore') as f:
        #remove first and last brackets
        data = f.read()[1:-2]
        #extract JSON item
        data = data.split('}\n{')
        #extract next n entires to items 
        for i in range(total,endEntryCount+total):
            item = data[i]
            #parse item to python dict type
            item_dict = json.loads('{'+item+'}')
            #append parsed item to item list
            items.append(item_dict)

#splits sentence into constituent parts (NLTK)
#takes sentence, returns array of words
def tokenizeElem(s):
    sentence = s
    tokens = nltk.word_tokenize(sentence)
    return tokens

#takes two tokenized sentences, returns typo pair
def getWrongPair(s1,s2):
    omit = False
    delete = False
    errorPair = ['','']
    #if number of tokens do not match, omission exists
    if len(s1)<len(s2):
        omit = True
    if len(s1)<len(s2):
        delete = True
    #loop through each word in sentence
    for i in range(min(len(s1),len(s2))):
        if s1[i]!=s2[i] and omit:
            #one word is split into two
            if s1[i] == s2[i]+s2[i+1]:
                errorPair[0] = s1[i]
                errorPair[1] = s2[i+1]
                return errorPair
            #one word is omitted
            elif s1[i] == s2[i+1]:
                errorPair[0] = '[omission]'
                errorPair[1] = s2[i]
                return errorPair
        #incorrect spelling
        elif s1[i]!=s2[i]:
            errorPair[0] = s1[i]
            errorPair[1] = s2[i]
           # print(errorPair)
            return errorPair
    #no spelling error, likely spacing error
    errorPair[0] = ''
    errorPair[1] = ''
    return errorPair

#takes dict entry of typos, returns array of typo pair
def getTypoFromSentences(list,size):
    #array of pairs of error/repair words
    pairs = []
    lendict = len(list)
    #loop through dict
    for i in range(size,lendict):
        numMistakes = len(items[i]['edits'])
        for j in range(numMistakes):
            #extract incorrected and fixed sentences from dict
            src_sent = items[i]['edits'][j]['src']['text']
            tgt_sent = items[i]['edits'][j]['tgt']['text']
            #tokenize sentences into array of words
            tokenedsrc = tokenizeElem(src_sent)
            tokenedtgt = tokenizeElem(tgt_sent)
            #isolate the error word and fixed word
            wrongPair = getWrongPair(tokenedsrc,tokenedtgt)
            #append to 
            pairs.append(wrongPair)
    return pairs

#converts array of error/repair/freq1/freq2 arrays into csv file, applies filter to results
def writeTocsv(list,size,total):
    header = ['mistake','fix','mistake freq','fix freq','type','Efreq']
    with open('results.csv','a',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for i in range(total,len(list)):
            #before writing to csv, append frequencies
            if size>endEntryCount:
                break
            binSearchgetfreqs(list[i])
            #s = number element in csv
            #i = i in loop
            #t = total number of lines parsed
            
            total+=1
            T1Filter(list[i])
            list[i].append(0)
            print(f's:{size} i:{i} t:{total-1} - {list[i]}')
            #only write if not null
            if (list[i][4]!= "NULL"):
                try:             
                            #add filter function here for stuff like:
                            #clear mispellings, scrambles, etc
                    #print("writing ^ to csv")
                    writer.writerow(list[i])
                    size+=1
                except:
                    print("something wrong in writerow likely non eng char")
                    #writer.writerow("error: non english character")
            
            #if(len(list[i])==4): 
            #    if list[i][2] !=0 and list[i][3]!= 0:
            #        size+=1
            #        print(size,total)
            #        passfilter(list[i])
            #        list[i].append(1)
            #        try:
            #            #add filter function here for stuff like:
            #            #clear mispellings, scrambles, etc
            #            print("writing to csv")
            #            writer.writerow(list[i])
            #        except:
            #            writer.writerow("error: non english character")
    csvfile.close()
    return size,total

#tag entry with type
#input is a len 4 list [word1, word2, freq1, freq2]
def passfilter(entry):
    #pair length less than 2
    if len(entry[0]) <= 2 and len(entry[1])<=2:
        entry.append("TINY")
        return
    #caps
    if entry[0].lower() == entry[1].lower() or (entry[2]==entry[3]and entry[2]!=0):
        entry.append("CAPS")
        return
    #scramble
    if sorted(entry[0])==sorted(entry[1]):
        entry.append("SCRM")
        return
    #split words: setup->set up or a lot-> alot
    if entry[0] in entry[1] or entry[1] in entry[0]:
        if abs(len(entry[0])-len(entry[1])) == 1:
            entry.append("1LET")
            return
        else:
            entry.append("SPLT")
            return
    #low freq likely mispelled
    if entry[2]<11 or entry[3]<11:
        entry.append("LFRQ")
        return
    else: entry.append("STND")

def T1Filter(entry):
    #empty
    if (entry[0]=="" and entry[1] =="") or num_there(entry[1]):
        entry.append("NULL")
        return
    #omission
    if entry[0] == "[omission]" or entry[1] == "[omission]":
        entry.append("Omission")
        return
    #caps
    if entry[0].lower() == entry[1].lower() or (entry[2]==entry[3]and entry[2]!=0):
        entry.append("Caps Error")
        return
    #transposition/scramble
    if sorted(entry[0])==sorted(entry[1]):
        entry.append("Exchange")
        return


    dif = nltk.edit_distance(entry[0],entry[1])
    if dif == 1:
        #difference threshold for morphological error (very crude solution)
        if dif==1 and len(entry[0])==len(entry[1]):
            #entry.append(dif)
            entry.append("Substitution")
            return
        elif dif==1 and len(entry[0])<len(entry[1]):
            entry.append("Deletion")
            return
        elif dif==1 and len(entry[0])>len(entry[1]):
            entry.append("Insertion")
            return

    #Morphological errors
    if (entry[0] in entry[1] or entry[1] in entry[0])and entry[0]!= "a" and entry[1]!="a":
        if entry[2]>0 and entry[3]>0:
            entry.append("Compound")
            return
        else:
            entry.append("MORPH")
            return
    
    else:
            entry.append("Standard")
            return
        

    
    #Exchange
    #Compound Words
    '''
    disable
    deletion: diable
    duplication: dissable
    insertion: dislable
    insertion: dixlable
    substituion: dixable

    morph, enable
    '''
    
    
def num_there(s):
        return any(i.isdigit() for i in s)      

#sorts raw data in to different csvs based on type
def T2sort():
    with open('results.csv') as inp, open('t2.csv','a',newline='') as outp:
        clean_writer = csv.writer(outp)
        for row in csv.reader(inp):
            #print(row)
            try:
                freq1 = row[2]
                freq2 = row[3]
                #print(freq1,freq2)
                if freq1!="0" and freq2!="0":
                    #print(row)
                    clean_writer.writerow(row)
            except:
                continue
def T3sort():
    df = pd.read_csv("t2.csv")
    with open('t2.csv') as inp, open('t3.csv','a',newline='') as outp:
        t3Writer = csv.writer(outp)
        for row in csv.reader(inp):
            try:
                numRes = searchcsv(row[0],row[1],df)
                if numRes>1 and row[5]!=1:
                    row[5]= numRes
                    t3Writer.writerow(row)
                else:
                    row[5] = 1
                    t3Writer.writerow(row)
            except: continue

    df = pd.read_csv('t3.csv')
    df.drop_duplicates( inplace=True)
    df.to_csv('t3.csv')


def searchcsv(E,T,df):    
    res = df[(df["mistake"]==E) & (df["fix"]==T)]
    #print(res)
    #print(len(res))
    return (len(res))          

def sortResults():
    #prevWord = ""
    #with open('results.csv') as inp, open('results_clean.csv', 'w',newline='') as out:
    #    writer = csv.writer(out)
    #    for row in csv.reader(inp):
    #        try:
    #            if row[0]!=prevWord and row[0]!="mistake":
    #                writer.writerow(row)
    #                prevWord = row[0]
    #        except:
    #            continue

    with open('results.csv') as inp, open('temp_CAPS.csv', 'w',newline='') as caps, open('temp_SCRM.csv', 'w',newline='') as scrm, open('temp_1LET.csv', 'w',newline='') as olet, open('temp_STND.csv', 'w',newline='') as stnd, open('temp_TINY.csv', 'w',newline='') as tiny, open('temp_SPLT.csv', 'w',newline='') as splt, open('temp_LFRQ.csv', 'w',newline='') as lfrq:
        caps_writer = csv.writer(caps)
        scrm_writer = csv.writer(scrm)
        olet_writer = csv.writer(olet)
        stnd_writer = csv.writer(stnd)
        tiny_writer = csv.writer(tiny)
        splt_writer = csv.writer(splt)
        lfrq_writer = csv.writer(lfrq)
        for row in csv.reader(inp):
            try:
                type = row[4]
                if type == "CAPS":
                    caps_writer.writerow(row)
                elif type == "SCRM":
                    scrm_writer.writerow(row)
                elif type == "1LET":
                    olet_writer.writerow(row)
                elif type == "STND":
                    stnd_writer.writerow(row)
                elif type == "TINY":
                    tiny_writer.writerow(row)
                elif type == "SPLT":
                    splt_writer.writerow(row)
                elif type == "LFRQ":
                    lfrq_writer.writerow(row)
            except:
                continue
def binSearchgetfreqs(pair):
    try:
        src = pair[0].lower()
        tgt = pair[1].lower()
        wb = xlrd.open_workbook('sortedSUBTLEXusfrequencyabove1.xls')
        sheet = wb.sheet_by_index(0)

        errorPair = ['','']
        pair.append(0)
        pair.append(0)
        srcIndex = binary_search_recursive(sheet,src,1,sheet.nrows)
        tgtIndex = binary_search_recursive(sheet,tgt,1,sheet.nrows)
        #print(srcIndex,sheet.cell_value(srcIndex,0))
        #print(tgtIndex,sheet.cell_value(tgtIndex,0))

        if srcIndex !=-1:
            pair[2] = sheet.cell_value(srcIndex,1)
        if tgtIndex !=-1:
            pair[3] = (sheet.cell_value(tgtIndex,1))
    except:
        pair.append(0)
        pair.append(0)

def binary_search_recursive(sheet, word, start, end):
    if start > end:
        return -1
    mid = (start + end) // 2
    if word == str(sheet.cell_value(mid,0)).lower():
        return mid
    if word < str(sheet.cell_value(mid,0)).lower():
        return binary_search_recursive(sheet, word, start, mid-1)
    else:
        return binary_search_recursive(sheet, word, mid+1, end)
##########################################NOT IN USE############################
def copy_csv(filename):
    df = pd.read_csv(filename)
    df.to_csv('copy_of_' + filename)

def cleanCSV(filename, cleanfilename):
    copy_csv(filename)
    prevWord = ""
    with open(filename) as inp, open('copy_of_'+filename) as copy, open(cleanfilename, 'w',newline='') as out:
        writer = csv.writer(out)
        for row in csv.reader(inp):
            try:
                if row[0]!=prevWord and row[0]!="mistake":
                    row[5]+=1
                    writer.writerow(row)
                    prevWord = row[0]
                else:
                    for crow in csv.reader(copy):
                        break
            except:
                continue

################################################################################



if __name__ == '__main__':
    size = 0
    total = 0
    #repeats until (n) elements in csv output 
    while total<endEntryCount:
        parse('github-typo-corpus.v1.0.0.jsonl',total)
        #convert dict to array of typo pairs
        data = getTypoFromSentences(items,size)
        #write array of typo pairs to csv (also add frequencies)
        size,total = writeTocsv(data,size,total)
        
    print(' writing complete\n')
    print('now sorting')
    T2sort()
    print("done sorting\n")

    print("Beginning Freq Combo")
    T3sort()
    print("phew")
    



 
