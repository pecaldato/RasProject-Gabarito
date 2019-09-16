import cv2
import numpy as np
 
class Respostas:

    #retorna lista de RA e respostas, baseado no parâmetro "contours"
    def get_answers(self, contours):

        #define os ranges que serão utilizados para localizar as questões/respostas
        ListX = [[117,143],[144,169],[170,195],[196,221],[222,247],[301,327],[328,353],[354,379],[380,405],[406,431],[485,511],
        [512,537],[538,563],[564,589],[590,615],[668,694],[695,720],[721,746],[747,772],[773,798]]
        ListY = ListY = [[472,498],[499,524],[525,550],[551,576],[577,602],[603,628],[629,654],[655,680],[681,706],[707,732],[733,758],
        [759,784],[808,834],[835,860],[861,886],[887,912],[913,938], [939,964],[965,990],[991,1016],[1017,1042],[1043,1068],[1069,1094],
        [1095,1120],[1121,1146],[1147,1172]]

        #define os ranges que serão utilizados para localizar o RA
        RAx = [[564,590],[591,616],[617,642], [643,668], [669,694], [695,720],[721,746],[747,772],[773,798],[799,824]]
        RAy = [[317,343],[344,369],[370,395],[396,421]]

        listRet = []
        listNumbers = []
        listOrder = []
        listRA = []

        for c in contours:
            #Only takes the central point of contours who have 100<Area<350
            if 90<cv2.contourArea(c)<300:
                # calculate moments for each contour
                M = cv2.moments(c)
 
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
                                    # cv2.putText(imReg, numero+' '+letra, (cX - 25, cY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                else:
                    for x in range(0,10):
                        if(cX >= RAx[x][0] and cX <= RAx[x][1]):
                            for j in range(0,4):
                                if(cY >= RAy[j][0] and cY <= RAy[j][1]):
                                    listRA.append(str(x))
                                    # cv2.putText(imReg, str(x), (cX - 25, cY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        
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
        return listRA, listOrder

    #método da construtora
    def __init__(self, contours):
        aff=contours
        #pega o vetor de respostas do gabarito
        _,self.gabarito = self.get_answers(aff)

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