#packages
import json
import xlrd
import nltk
import csv
import string

#nltk.download('punkt')

#list of entries 
items = []

#parse JSONL with indent to dict
def parse(filename):
    #open JSONL
    with open(filename,'r',encoding='utf8', errors='ignore') as f:
        #remove first and last brackets
        data = f.read()[1:-2]
        #extract JSON item
        data = data.split('}\n{')

        #extract first 200 entires to items 
        for i in range(200):
            item = data[i]
            #parse item to python dict type
            item_dict = json.loads('{'+item+'}')
            #append parsed item to item list
            items.append(item_dict)

#splits sentence into constituent parts (NLTK)
def tokenizeElem(s):
    sentence = s
    tokens = nltk.word_tokenize(sentence)
    #print(tokens)
    return tokens

#takes two tokenized sentences, returns typo pair
def getWrongPair(s1,s2):
    #print("source:")
   # print(s1)
    #print("target")
    #print(s2)
    #print("error")
    omit = False
    delete = False
    errorPair = ['','']
    #if number of tokens do not match, omission
    if len(s1)<len(s2):
        omit = True
    if len(s1)<len(s2):
        delete = True
    for i in range(min(len(s1),len(s2))):
        if s1[i]!=s2[i] and omit:
            if s1[i] == s2[i]+s2[i+1]:
                errorPair[0] = s1[i]
                errorPair[1] = s2[i+1]
                #print(errorPair)
                return errorPair
                break
            elif s1[i] == s2[i+1]:
                errorPair[0] = '[omission]'
                errorPair[1] = s2[i]
                #print(errorPair)
                return errorPair
                break
            

        elif s1[i]!=s2[i]:
            errorPair[0] = s1[i]
            errorPair[1] = s2[i]
           # print(errorPair)
            return errorPair
            break

    errorPair[0] = ''
    errorPair[1] = ''
    return errorPair




        

#takes dict of typos, returns array of typo pairs
def getTypoFromSentences(list):
    pairs = []
    lendict = len(list)
    for i in range(lendict):
        numMistakes = len(items[i]['edits'])
        #print(numMistakes)
        for j in range(numMistakes):
            src_sent = items[i]['edits'][j]['src']['text']
            tgt_sent = items[i]['edits'][j]['tgt']['text']
            #print(src_sent)
            #print(tgt_sent)
            tokenedsrc = tokenizeElem(src_sent)
            tokenedtgt = tokenizeElem(tgt_sent)
            #print(tokenedsrc)
            #print(tokenedtgt)
            wrongPair = getWrongPair(tokenedsrc,tokenedtgt)
            pairs.append(wrongPair)
    return pairs

def writeTocsv(list):
    header = ['mistake','fix']
    with open('results.csv','w',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for i in range(len(list)):
            #add get freqs
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
    parse('github-typo-corpus.v1.0.0.jsonl')
    #print as json
    #print(json.dumps(items,indent=2))
    print('\n\n\n')
    #print 1 entry
   # print(items[4]['edits'][0]['src']['text'])
   # print(items[4]['edits'][0]['tgt']['text'])
   # sen = items[4]['edits'][0]['tgt']['text']
    data = getTypoFromSentences(items)
    print(data)
    writeTocsv(data)
    print('complete')
   # tokenizeElem(sen)
 