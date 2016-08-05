import sys
from functools import reduce
import time

#-------------------------

delPrvniRadka = True #vymazat zahlavi 'source, destination...'?

PSOUR = 0 #placing of source
PDEST = 1 #placing of destination
PDEP  = 2 #placing of departure
PARR  = 3 #placing of arrival
PFN   = 4 #placing of flight number

#span of time (hours)
TDIST1 = 1
TDIST2 = 4

#file or stdin
#FILENAME = "odlety.txt"
FILENAME  = ""

#-------------------------


def getListEl(iter,position):
    """ get list of elements from iterinar
    getListEl([['USM', 'HKT', '2016-10-11T10:10:00', '2016-10-11T11:10:00', 'PV511'],
               ['BWN', 'DPS', '2016-10-11T18:15:00', '2016-10-11T19:15:00', 'PV476']]
               ,PSOUR) ->
    ['USM', 'BWN']
    """
    r=[]
    return reduce(lambda s,x: s+[x[position]], iter, r )

def adjustTime(segment):
    """adjust time to number of hours
    adjustTime(['USM', 'HKT', '2016-10-11T10:10:00', '2016-10-11T11:10:00', 'PV511']) ->
    ['USM', 'HKT', 410048.1666666667, 410049.1666666667, 'PV511']
    """
    segment[PDEP]=time.mktime(time.strptime(segment[PDEP], "%Y-%m-%dT%H:%M:%S"))/3600
    segment[PARR]=time.mktime(time.strptime(segment[PARR], "%Y-%m-%dT%H:%M:%S"))/3600
    return segment


def subsequentSegms(segm1,segm2):
    """segm1 -> segm2 .... return -1
       segm2 -> segm1 .... return  1
       no subsequent  .... return  0
    """
    t= segm2[PDEP]- segm1[PARR]
    if (segm1[PDEST]==segm2[PSOUR])and(t>=TDIST1)and(t<=TDIST2):
        return -1
    t=segm1[PDEP] - segm2[PARR] 
    if (segm2[PDEST]==segm1[PSOUR])and(t>=TDIST1)and(t<=TDIST2):
        return 1
    return 0


def reproduceIterin(it, el):
    """from itiner (list of segments) and a segment make list of itiners (list of list of segments)
    if el isn't subseq -> return only singleton set
    """
    st=[it]
    for ind,segm in enumerate(it):
        subsq = subsequentSegms(el,segm)
        #print("subsequentSegms(el,segm) - ",el,"+",segm,"=",subsq)
        if subsq<0:
            dests = getListEl(it[ind:],PDEST)
            if not(el[PSOUR] in dests) or (el[PSOUR]==it[-1][PDEST]): #not A->B->A->B but A->B->A ok
                if not(el[PDEST] in dests):
                    if (ind==0):                            #let only extension el+it
                        if it[0][PSOUR]==it[-1][PDEST]:     #maybe A->B->A has been allowed
                            st+=[[el] + it[ind:-1]]         #only el + A->B and nothing remove
                        else:
                            st.remove(it)                   #we have already longer...
                            st+= [[el] + it[ind:]]          #el+it
          
        if subsq>0:
            if not(el[PDEST] in getListEl(it[0:ind+1],PDEST)) or (el[PDEST]==it[0][PSOUR]): #not A->B->A->B but A->B->A ok
                
                if (ind+1)==len(it):  #let only extension it+el
                        if it[0][PSOUR]==it[-1][PDEST]:     #maybe A->B->A has been allowed
                            st+= [it[1:]+[el]]              #only B->A + el and nothing remove
                        else:
                            st.remove(it)                   #we have already longer iter
                            st+= [it[0:]+[el]]              #it+el
                    

    return st

def makeGroup(data):
    """from list of segments make list of itiners
    """
    iterinars=[]
    for x in data:
        temp=[]
        for i in iterinars:
            temp+=reproduceIterin(i,x)
        iterinars=temp + [[x]]
    return removeSubiterins([*filter(lambda x: len(x)>1, iterinars)]) #only one segment isn't itiner



def contains_sublist(lst, sublst):
    """is sublst in lst?
    """
    n = len(sublst)
    return any((sublst == lst[i:i+n]) for i in range(len(lst)-n+1))


def removeSubiterins(it):
    """if there are some duplicates or sub-duplicates -> remove it
    """
    it = sorted(it, key=lambda x: len(x))   #sort - the longest is last
    stack=[]
    while (it):
        el=it.pop()                         #the longest
        stack.append(el);
        it = [i for i in it if not (contains_sublist(el,i))]    #remove sublists
    return stack

        

def betterPrint(data):
    """ get list of itiners and put form:
            2  >> 
            DPS ->( PV534 )-> BWN
            BWN ->( PV612 )-> DPS
            --------------------
    """
    for ind,x in enumerate(data):
        froms=getListEl(x,PSOUR)
        tos  =getListEl(x,PDEST)
        bys  =getListEl(x,PFN)
        print(ind+1," >> ")
        for i in range(0,len(x)):
            print(froms[i],"->(",bys[i],")->",tos[i])
        print(20*"-")

if (FILENAME==""):                  #from stdin
    data = sys.stdin.readlines()
else:
    try:
        with open(FILENAME) as f:   #name of file is known
            data = f.readlines()           
    except IOError:
        print('cannot open ',FILENAME)
        sys.exit(1)
    else:
        f.close()




stack=[]
#make list from stdin or file
data=reduce(lambda s,x: s+[(x.strip().split(','))], data, stack )

#remove head if necessary
if delPrvniRadka:
    del data[0]

#adjust format of time for all segments
data = [*map(adjustTime,data)]

#result to stdout
print(betterPrint(makeGroup(data)))




    


