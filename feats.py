import random
import time
import os
import msvcrt
import csv
from os import listdir
from os.path import isfile, join
import uuid


locipath="./Loci"
datas="./rawDatas/feats.csv"
f2=open('./rawDatas/global.txt', 'a') #print globalMessages

class Feat:
    """Class implementing the most important features of each feats
    """
    def __init__(self, nbRows, lengthColumn,memoTime,restiTime,sizeCell=None,separator="",separatorPlaceHolder=2,tempFile="temp.txt",indent=5,blocMode=False,revert=False):
        self.nbRows = nbRows
        self.lengthColumn= lengthColumn
        self.memoTime = memoTime
        self.restiTime= restiTime
        self.sizeCell= sizeCell
        self.separator=separator
        self.separatorPlaceHolder=separatorPlaceHolder
        self.solution=[]
        self.answer=[]
        self.table=""#string representation of the solution
        self.indent=indent
        self.tempFile=tempFile
        self.blocMode=blocMode
        self.revert=revert

    def proceed(self):
        """Proceed to the feat
        """
        self.waiter(self.nbRows)
        self.build_table_solution()
        self.print_table(self.nbRows)
        print("\n"*9)
        time.sleep(self.memoTime)
        print("\n"*30)
        timeResti=time.clock()
        self.createAndOpenSheet()

        do=raw_input("quit (q), load the answer file(l) : ")
        if(do=="l"):
            timeElapsed=round(time.clock()-timeResti)
            self.answer=self.buildAnswerFromFile(self.tempFile)
            [errors,points,nlines]=self.compareSolutionAnswer(self.solution,self.answer)
            self.print_debrief(errors,points,nlines,timeElapsed)
        return self.solution,self.answer

    def waiter(self,nR):
        time.sleep(1)
        self.printNumber("3")
        time.sleep(1)
        self.printNumber("2")
        time.sleep(1)
        self.printNumber("1")
        time.sleep(1)
        
    def printNumber(self,ms):
        print "\n" * 20
        print "            "+ms
        print "\n" * 19
        
    def createAndOpenSheet(self):
        """ Open a temp file as a recall sheet
        """
        with open(self.tempFile, 'w') as f:
            pass
        os.system("start "+self.tempFile)# windows only, for mac : os.system("open "+filename)

    def print_debrief(self,errors,points,nl,timeElapsed):
        """ Display User friendly outputs
        """
        self.print_table(nl)
        print("\n")
        print("you got "+str(points)+" points")
        print("remaining restitution time : "+str(self.restiTime-timeElapsed))+" s"
        message2="feat : %s, memotime : %s, points : %s \n"%(str(self.__class__.__name__),str(self.memoTime),str(points))
        f2.write(message2)      
        for error in errors:
            if(len(error)==4):
                print "at line %d,column %d you wrote %s instead of %s"  % (error[0], error[1],error[2],error[3])
            elif (len(error)==3):
                print "at line %d you wrote %s instead of %s"  % (error[0], error[1],error[2])                

    def print_table(self,nR):
        """ Display the table of the elements to be learned
        """
        print("\n"*(10+(20-nR)/2))
        lines=self.table.splitlines()
        if(self.revert):
            nR=len(lines)#dirty to avoid complications
        for l in range(nR):
            print(lines[l])
            
    def build_table_solution(self):
        """ Build the displayed table of the items to be learned
            and build the solution vector"""
        
        self.solution=[] # might be redundant
        self.table=""
        for r in range(self.nbRows):
            solutionline=[]
            row=" "*self.indent
            for l in range(self.lengthColumn):
                sep=""
                if(self.separator!=""):
                    if(l%self.separatorPlaceHolder==0):
                        sep=self.separator
                item=str(self.generateItem())       # use generateItem which must be implemented in inherited classes
                solutionline.append(item)
                if(self.sizeCell!=None):
                    decalTotal=self.sizeCell-len(item)
                    decalLeft=decalTotal/2
                    decalRight=decalTotal-decalLeft
                    row+=sep+" "*decalLeft+item+" "*decalRight
                else:
                    row+=sep+item
            self.table+=row+sep+"\n"
            self.solution.append(solutionline)

    def update_table_solution(self): # dirty and incomplete
        """ Rebuild the displayed table according to the current solution vector"""
        self.table=""
        sep=self.separator
        for solutionline in self.solution:
            row=""
            for item in solutionline:
                row+=sep+item
            self.table+=row+sep+"\n"

    def buildAnswerFromFile(self,fname):
        """ Read the recall file given by the user """
        answer=[]
        with open(fname, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';')
            for row in spamreader:
                lanswer=[]
                if(self.blocMode):
                    lanswer.extend(row)
                else:
                    for element in row:
                        lanswer.extend(element)
                answer.append(lanswer)
        return answer
            

    def compareSolutionAnswer(self,lsol,lansw):
        """ compare the recall file with the target, count the points and raise the errors"""
        indexL=0
        points=0
        errors=[]
        if(self.revert): # columns are taken as lines in order to compare columns by columns
            lsol=zip(*lsol)
            lansw=zip(*lansw)
        for linAns in lansw:
            lineErrors=0
            indexCol=0
            for item in linAns:
                if(lsol[indexL][indexCol]!=item):
                    errorReport=[indexL,indexCol,item,lsol[indexL][indexCol]]
                    errors.append(errorReport)
                    lineErrors+=1
                indexCol+=1
            if lineErrors==1:
                points+=indexCol/2
            else:
                if lineErrors==0:
                  points+=indexCol  
            indexL+=1
        return(errors,points,indexL)
    
class Dates(Feat):
    def __init__(self, nbRows, lengthColumn,memoTime,restiTime,separator="|",separatorPlaceHolder=2,tempFile="temp.txt",indent=5,freqMax=8000,dico='./dates/13jan.csv',sizeCell=20,blocMode=True,revert=True):
        Feat.__init__(self, nbRows, lengthColumn,memoTime,restiTime,sizeCell,separator,separatorPlaceHolder,tempFile,indent,blocMode=True)    
        self.dates=[]
        self.readDic(dico)#put 2 extra arguments + sizecell=20
    def readDic(self,dictionnary):
        with open(dictionnary, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for r,row in enumerate(spamreader):
                self.dates.extend(row)
                
    def generateItem(self):
        date=str(random.randint(1000, 2099))
        label=random.choice(self.dates)
        return date+self.separator+label

    def createAndOpenSheet(self): #overriding default method
        with open(self.tempFile, 'wb') as f:
            dates=[]
            random.shuffle(self.solution)#recall sheet is shuffled !
            self.update_table_solution()#update table accordingly
            for l in self.solution:
                datelabel=l[0][4:]
                date=l[0][:4]
                dates.append(date)
                f.write(datelabel+'\n')
            self.solution=dates
        os.system("start "+self.tempFile)# windows only, for mac : os.system("open "+filename)

    def buildAnswerFromFile(self,fname):
        answer=[]
        with open(fname, 'rb') as f:
            for line in f:
                answer.append(line[:4])
        return answer

    def compareSolutionAnswer(self,lsol,lansw): #override
        indexL=0
        points=0
        errors=[]
        for linAns in lansw:
            lineErrors=0
            indexCol=0
            date=""
            for digit in linAns:
                date+=digit
                if digit==self.separator:
                    break
            if(date!=self.separator):
                if(lsol[indexL]!=date):
                    errorReport=[indexL,date,lsol[indexL]]
                    errors.append(errorReport)
                    lineErrors+=1
                else:
                    points+=1
            indexL+=1
        return(errors,points,indexL)
                
class Numbers(Feat):
    def __init__(self, nbRows, lengthColumn,memoTime,restiTime,separator="|",separatorPlaceHolder=2,tempFile="temp.txt",indent=5,sizeCell=None,blocMode=False):
        Feat.__init__(self, nbRows, lengthColumn,memoTime,restiTime,sizeCell,separator,separatorPlaceHolder,tempFile,indent,blocMode)

    def generateItem(self):
        return random.randint(0, 9)

class Binaries(Feat):
    def __init__(self, nbRows, lengthColumn,memoTime,restiTime,separator="|",separatorPlaceHolder=2,tempFile="temp.txt",indent=5,sizeCell=None,blocMode=False):
        Feat.__init__(self, nbRows, lengthColumn,memoTime,restiTime,sizeCell,separator,separatorPlaceHolder,tempFile,indent,blocMode)

    def generateItem(self):
        return random.randint(0, 1)

class Words(Feat):
    def __init__(self, nbRows, lengthColumn,memoTime,restiTime,separator="|",separatorPlaceHolder=2,tempFile="temp.txt",indent=5,freqMax=8000,dico='./dictionnaries/french/newDic2.csv',sizeCell=20,blocMode=True,revert=True):
        Feat.__init__(self, nbRows, lengthColumn,memoTime,restiTime,sizeCell,separator,separatorPlaceHolder,tempFile,indent,blocMode,revert)
        self.nouns=[]
        self.verbs=[]
        self.readDic(dico,freqMax)#put 2 extra arguments + sizecell=20
        #revert

    def readDic(self,dictionnary,freqMax):
        with open(dictionnary, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=';', quotechar='"')
            for r,row in enumerate(spamreader):
                if(r==freqMax):
                    break
                if(row[0]=="n"):
                    self.nouns.append(row[1])
                if(row[0]=="v"):
                    self.verbs.append(row[1])
                    
    def generateItem(self):
        if(random.randint(0, 9)==9):
            return random.choice(self.verbs)
        else:
            return random.choice(self.nouns)
