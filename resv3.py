#packages
import json
import xlrd
import nltk
import csv
import string

#list of entries 
items = []


#parse JSONL with indent to dict
def parse(filename,total):
    #open JSONL
    print("Starting parse...")
    with open(filename,'r',encoding='utf8', errors='ignore') as f:
        #remove first and last brackets
        data = f.read()[1:-2]
        #extract JSON item
        data = data.split('}\n{')
        #extract next 200 entires to items 
        for i in range(total,200+total):
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

#converts list of error/repair arrays into csv file
def writeTocsv(list,size,total):
    header = ['mistake','fix','mistake freq','fix freq']
    with open('results.csv','a',newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for i in range(total,len(list)):
            #before writing to csv, append frequencies
            if size>200:
                break
            getfreqs(list[i])
            #s = number element in csv
            #i = i in loop
            #t = total number of lines parsed
            print(f's:{size} i:{i} t:{total} - {list[i]}')
            total+=1
            if(len(list[i])==4): 
                if list[i][2] !=0 and list[i][3]!= 0:
                    size+=1
                    print(size,total)
                    try:
                        print("writing to csv")
                        writer.writerow(list[i])
                    except:
                        writer.writerow("error: non english character")
    csvfile.close()
    return size,total

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
    size = 0
    total = 0
    #repeats until 200 elements in csv output
    while size<200:
        parse('github-typo-corpus.v1.0.0.jsonl',total)
        #convert dict to array of typo pairs
        data = getTypoFromSentences(items,size)
        #write array of typo pairs to csv (also add frequencies)
        size,total = writeTocsv(data,size,total)
    print('complete')

 