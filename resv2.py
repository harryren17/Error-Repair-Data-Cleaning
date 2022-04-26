#packages
import json
import xlrd
import nltk
import csv
import string

#global
items = []
entryCount = 0

#parse JSONL with indent to dict
def parse(filename,entryCount):
    #open JSONL
    with open(filename,'r',encoding='utf8', errors='ignore') as f:
        #remove first and last brackets
        data = f.read()[1:-2]
        #extract JSON item
        data = data.split('}\n{')
        #extract first 200 entires to items 
        totalcount = 0
        while entryCount<200:
            item = data[totalcount]
            #parse item to python dict type
            item_dict = json.loads('{'+item+'}')

            pair = getTypoFromSentence(item_dict)
            getfreqs(pair)
            if(len(pair)==4 and pair[2]!=0 and pair[3]!=0):
                #append parsed item to item list
                items.append(pair)
                entryCount+=1
            totalcount+=1

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

#takes dict of typos, returns array of typo pairs
def getTypoFromSentence(item):
    #array of pairs of error/repair words
    pairs = []
    numMistakes = len(item['edits'])
    for j in range(numMistakes):
        #extract incorrected and fixed sentences from dict
        src_sent = item['edits'][j]['src']['text']
        tgt_sent = item['edits'][j]['tgt']['text']
        #tokenize sentences into array of words
        tokenedsrc = tokenizeElem(src_sent)
        tokenedtgt = tokenizeElem(tgt_sent)
        #isolate the error word and fixed word
        wrongPair = getWrongPair(tokenedsrc,tokenedtgt)
        #append to 
        pairs.append(wrongPair)
    return pairs

#converts list of error/repair arrays into csv file
def writeTocsv(list):
    header = ['mistake','fix']
    with open('results.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for i in range(len(list)):
            #before writing to csv, append frequencies
            getfreqs(list[i])
            print(list[i])
            try:
                writer.writerow(list[i])
            except:
                writer.writerow("error: non english character")

#checks pairs of words against US-SUBLTEX, appends freq
def getfreqs(pair):
    src = pair[0].lower()
    tgt = pair[1].lower()
    wb = xlrd.open_workbook('SUBTLEXusfrequencyabove1.xls')
    sheet = wb.sheet_by_index(0)

    #loop through corpus, check for matches with pair words
    #append found frequencies to pair array
    for i in range(sheet.nrows):
        if src == sheet.cell_value(i,0):
            if len(pair)==4:
                pair[2] = sheet.cell_value(i,1)
            else:
                pair.append(sheet.cell_value(i,1))
        if tgt == sheet.cell_value(i,0):
            if len(pair)==3:
                pair.append(sheet.cell_value(i,1))
            else:
                pair.append(0)
                pair.append(sheet.cell_value(i,1))


if __name__ == '__main__':
    #parse jsonl to dict
    parse('github-typo-corpus.v1.0.0.jsonl',0)
    #convert dict to array of typo pairs
    
    #write array of typo pairs to csv (also add frequencies)
    writeTocsv(items)
    print('complete')

 