import cv2
import numpy as np
 
class Respostas:

    #retorna lista de RA e respostas, baseado no parâmetro "contours"
    def get_answers(self, contours, img):

        #define os ranges que serão utilizados para localizar as questões/respostas
        ListX = [[93,113],[114,135],[136,155],[156,175],[176,196],[240,260],[261,280],[281,300],[301,320],[321,343],[385,405],
        [406,426],[427,447],[448,468],[469,489],[532,552],[553,573],[574,594],[595,615],[616,636]]
        ListY = [[472,499],[500,524],[525,550],[551,576],[577,602],[603,628],[629,653],[654,679],[680,705],[706,732],[733,757],
        [758,782],[809,835],[836,861],[862,886],[887,913],[914,938],[939,963],[964,989],[990,1015],[1016,1041],[1042,1067],[1068,1092],
        [1093,1119],[1120,1145],[1146,1171]]

        #define os ranges que serão utilizados para localizar o RA
        RAx = [[448,469],[470,489],[490,510], [511,530], [531,551], [552,572],[573,592],[593,613],[614,633],[634,654]]
        RAy = [[317,343],[344,369],[370,395],[396,421]]

        listRet = []
        listNumbers = []
        listOrder = []
        listRA = []
        i=0
        
        for c in contours:
            #Only takes the central point of contours who have 100<Area<350
            i += 1
            if (60<cv2.contourArea(c)<80):
                # calculate moments for each contour
                M = cv2.moments(c)
                cv2.drawContours(img, c, -1, (0,255,0), 3)
 
                # calculate x,y coordinate of center
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])

                #Compare the central point to the Xo value of every letter and question number
                if(cX<=760 or cY>=625):
                    for x in range(0, 20):
                        if (cX >= ListX[x][0] and cX <= ListX[x][1]):
                            for j in range(0, 26):
                                if (cY >= ListY[j][0] and cY <= ListY[j][1]):
                                    # cv2.circle(imReg, (cX, cY), 0, (255, 255, 255), -15)
                                    if (x==0 or x==5 or x==10 or x==15):
                                        letra = "A"
                                    elif (x==1 or x==6 or x==11 or x==16):
                                        letra = "B"
                                    elif (x==2 or x==7 or x==12 or x==17):
                                        letra = "C"
                                    elif (x==3 or x==8 or x==13 or x==18):
                                        letra = "D"
                                    elif (x==4 or x==9 or x==14 or x==19):
                                        letra = "E"  

                                    if (cX >= ListX[0][0] and cX <= ListX[4][1]):
                                        numero = str(j + 1)
                                    elif (cX >= ListX[5][0] and cX <= ListX[9][1]):
                                        numero = str(j + 27)
                                    elif (cX >= ListX[10][0] and cX <= ListX[14][1]):
                                        numero = str(j + 53)
                                    elif (cX >= ListX[15][0] and cX <= ListX[19][1]):  
                                        numero = str(j + 79)            

                                    listRet.append(letra)
                                    listNumbers.append(numero)
                                    cv2.putText(img, numero+' '+letra, (cX - 25, cY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                
                else:
                    for x in range(0,10):
                        if(cX >= RAx[x][0] and cX <= RAx[x][1]):
                            for j in range(0,4):
                                if(cY >= RAy[j][0] and cY <= RAy[j][1]):
                                    listRA.append(str(x))
                                    cv2.putText(img, str(x), (cX - 25, cY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        #print(listRet)
        #print(listNumbers)
        for x in range(0,len(listNumbers)-1):
            for j in range(x,len(listNumbers)):
                if (int(listNumbers[x]) >= int(listNumbers[j])):
                    aux = listNumbers[x]
                    listNumbers[x] = listNumbers[j]
                    listNumbers[j] = aux

                    aux = listRet[x]
                    listRet[x] = listRet[j]
                    listRet[j] = aux


  #Insere os - nas questões deixadas em branco
        ctd = 1
        for x in range(0,len(listNumbers)):
            if (listNumbers[x]!=listNumbers[x-1]):
                if (ctd != int(listNumbers[x])):
                    listNumbers.insert(x,str(ctd))
                    listRet.insert(x,"-")
                ctd += 1
        x = 0
        while x < len(listNumbers):
            ctd = x
            aux = []
            while (int(listNumbers[ctd]) == int(listNumbers[x])):
                aux.append(listRet[ctd])
                ctd += 1
                if (ctd == len(listNumbers)):
                    break
            x = ctd
            listOrder.append(aux)
        
        listRA = listRA.reverse()  

         #cv2.imshow('oi',img)
         #cv2.waitKey()   
        cv2.imwrite('getcount.jpeg', img)
        print(len(listOrder))
        return listRA, listOrder

    #método da construtora
    def __init__(self, contours, align_image):
        #pega o vetor de respostas do gabarito
        _,self.gabarito = self.get_answers(contours, align_image)

    #retorna um dicionário com as listas de respostas corretas e incorretas
    def compare_answers(self, respostas):
        
        wrongAnswers = []
        correctAnswers = []
        for x in range((len(respostas))):
            if (len(respostas[x]) > 1) or respostas[x] != self.gabarito[x]:
                wrongAnswers.append([str(x+1), respostas[x]])
            else:
                correctAnswers.append([str(x+1), respostas[x]])
        Answers = {'correctAnswers': correctAnswers, 'wrongAnswers:': wrongAnswers}
        return Answers