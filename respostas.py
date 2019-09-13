class Respostas:

    #retorna lista de RA e respostas, baseado no parâmetro "contours"
    def get_answers(self, contours):

        #define os ranges que serão utilizados para localizar as questões/respostas
        ListX = [[166,203],[204,239],[240,276],[277,312],[313,349],[426,463],[464,499],[500,536],[537,572],[573,609],[686,723],
  [724,759],[760,796],[797,832],[833,869],[946,983],[984,1019],[1020,1056],[1057,1092],[1093,1129]]
        ListY = ListY = [[668,705],[706,741],[742,778],[779,814],[815,851],[852,888],[889,924],[925,961],[962,997],[998,1034],[1035,1071],
  [1072,1107],[1144,1181],[1182,1217],[1219,1254],[1255,1290],[1291,1327], [1328,1364],[1365,1400],[1401,1437],[1438,1473],[1474,1510],[1511,1547],
  [1548,1583],[1584,1620],[1621,1656]]

        #define os ranges que serão utilizados para localizar o RA
        RAx = [[798,835],[836,871],[872,908], [909,944], [945,981], [982,1018],[1019,1054],[1055,1091],[1092,1127],[1128,1164]]
        RAy = [[448,484],[485,521],[522,557],[558,594]]

        listRet = []
        listNumbers = []
        listOrder = []
        listRA = []

        for c in self.contours:
            #Only takes the central point of contours who have 100<Area<350
            if 100<cv2.contourArea(c)<300:
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
                                    cv2.circle(imReg, (cX, cY), 0, (255, 255, 255), -15)
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
                                    cv2.putText(imReg, numero+' '+letra, (cX - 25, cY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                else:
                    for x in range(0,10):
                        if(cX >= RAx[x][0] and cX <= RAx[x][1]):
                            for j in range(0,4):
                                if(cY >= RAy[j][0] and cY <= RAy[j][1]):
                                    listRA.append(str(x))
                                    cv2.putText(imReg, str(x), (cX - 25, cY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
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

        #pega o vetor de respostas do gabarito
        _,self.gabarito = get_answers(contours)

    #retorna um dicionário com as listas de respostas corretas e incorretas
    def compare_answers(self, respostas):
        
        wrongAnswers = []
        correctAnswer = []
        for x in range(len(respostas)):
            if (len(respostas[x]) > 1) or respostas[x] != self.gabarito[x]:
                wrongAnswer.append([str(x+1), respostas[x]])
            else:
                correctAnswers.append([str(x+1), Respostas[x]])
        Answers = {'correctAnswers' = correctAnswers, 'wrongAnswers:' = wrongAnswers}
        return Answers

    

