import numpy as np
import cv2

def keprolOlv(kep):
    roi = cv2.imread(kep)
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)#fekete-fehér kép
    gray_blur = cv2.bilateralFilter(gray, 20, 1000, 1000)# 80,105,100
        
    circles = cv2.HoughCircles(gray_blur,cv2.HOUGH_GRADIENT,1,580, param1=46,param2=48,minRadius=200,maxRadius=570)#köröket keres
    if(None is circles):
        return 0
    else:
        circles = np.uint16(np.around(circles))#atrakja a köröket uint16 tipusba
#-----------------------------
#Itt lesz a szin detektálása késöbb meg a hasonlitás
        frameHSV = cv2.cvtColor(roi,cv2.COLOR_BGR2HSV)
        frameHSV=cv2.resize(frameHSV, None, fx=0.3,fy=0.3)

        h, s, v = cv2.split(frameHSV)#tömbök átalakítása
        filtered = (((68<v) + (v<3)) * (s>90) * (h<180)) * 255 #Ez adja meg melyiket keresse#v>20,s<95,h<200
#-----------------------------
#érmék hány százalékban sárgák?
        feketearanyok = []
        for c in circles:
            for c2 in c:
                fekete=0
                mind=1
                minoszlop = 0
                minsor = 0
                if(c2[2]>c2[0]):
                    minoszlop = 0
                else:
                    minoszlop=int((c2[0]-c2[2])*0.3)
                maxoszlop=int((c2[0]+c2[2])*0.3)
                if(c2[2]>c2[1]):
                    minsor = 0
                else:
                    minsor=int((c2[1]-c2[2])*0.3)
                maxsor=int((c2[1]+c2[2])*0.3)
                #ez kimaszkolja az adott pénzérmét
                for i in range(filtered.shape[0]):
                    for j in range(filtered.shape[1]):
                        if(((minsor<i) and (i<maxsor))and((minoszlop<j) and (j<maxoszlop))):
                            if(filtered[i,j]==255):#ha a megadott szinhez hasonlit akkor fekete++ 
                                fekete+=1
                            mind+=1
                
                feketearany=fekete/mind*100
                feketearanyok.append(feketearany)
        #circlesarga <= ha 10% nagyobb valoszinu sárga
#-----------------------------
    #megkeresi a legnagyobb radiust
        largestRadius = 0
        for i in circles[0,:]:
            if largestRadius < i[2]:
                largestRadius = i[2]
#-----------------------------
#körök által megadott érmék definiálása
        change = 0
        szazalek = 0
        for i in circles[0,:]:
            cv2.circle(roi,(i[0],i[1]),i[2],(0,255,0),2)#körök körvonala
            cv2.circle(roi, (i[0], i[1]),2, (0,0,255), 3)#körök középpontjai
            radius = i[2]#aktuális kör
            ratio = radius / largestRadius#arányosan a legnagyobbhoz képest
            if(ratio >= 0.98):#lehet 200
                if(feketearanyok[szazalek] > 10):
                    change = change + 200#jo arány és szin szerint
                else:
                    change = change + 50
            elif((0.977 > ratio ) and (ratio>=0.938)):#lehet 50
                if(10>feketearanyok[szazalek]):
                    change = change + 50#jo arány és szim szerint
                else:
                    if(ratio<0.945):
                        change = change + 20#ha kisebb
                    else:
                        change = change + 200#ha nagyobb 
            elif((0.938 > ratio ) and (ratio>=0.879)):#lehet 20
                if(10<feketearanyok[szazalek]):
                    change = change + 20#jo arány és szim szerint
                else:
                    if(ratio<0.89):
                        change = change + 10#ha kisebb
                    else:
                        change = change + 50#ha nagyobb
            elif((0.879 > ratio ) and (ratio>=0.849)):#lehet 10
                if(10>feketearanyok[szazalek]):
                    change = change + 10#jo arány és szim szerint
                else:
                    if(ratio<0.869):
                        change = change + 100#ha kisebb
                    else:
                        change = change + 20#ha nagyobb 
            elif((0.849 > ratio ) and (ratio>=0.75)):#lehet 100
                if(50 > feketearanyok[szazalek] and feketearanyok[szazalek] > 20):
                    change = change + 100#jo arány és szim szerint
                else:
                    if(ratio<0.823 and feketearanyok[szazalek]>10):
                        change = change + 5#ha kisebb
                    else:
                        change = change + 10#ha nagyobb 
            elif(ratio < 0.75):#lehet 5
                if(10<feketearanyok[szazalek]):
                    change = change + 5#jo arány és szim szerint
                else:
                    if(ratio>0.65):
                        change = change + 100#ha nagyobb
            szazalek+=1
            
        change = str(change)
        return change
        
def ttol(txt):#text to list
    kepek = []
    szamok = []
    with open(txt) as file:#fájl megnyitása majd sorrol sorra adatkiírás
        lines = file.readlines()
        kep = 0
        for line in lines:
            kep=0
            kepstr = ""
            szamstr = ""
            for i in line:
                if(kep==0 and i != ','):
                    kepstr+=i
                elif(i == ','):
                    kep=1
                elif(kep==1 and '0'<=i and i<='9'):
                    szamstr+= i
            inputpath = szamstr.rstrip()
            szamok.append(inputpath)
            kepek.append(kepstr)
        
    return kepek,szamok
#----------------------------------
#teszt függvény amelyben a gép által meg adott és a valódi eredményt hasonlitja össze
def test(er,changeer):
    mind = 0
    statistica = 0
    i=0
    for eredmeny in er:
        if (eredmeny == changeer[i]):
            statistica = statistica + 1
        mind = mind + 1
        i+=1
    
    print('mind: ',mind,'    statistica: ',statistica)
    eredmeny = (statistica/mind)*100
    print("Teszt aránya: ",eredmeny,'% jó')

er = []
changeer = []
kepek = []
kepek,er = ttol('kepek&eredmenyek.txt')

for kep in kepek:
    change = keprolOlv(kep)
    changeer.append(change)
    
test(er,changeer)

cv2.destroyAllWindows()