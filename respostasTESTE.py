import cv2
import os
import numpy as np
 

class Respostas:
    #retorna lista de RA e respostas, baseado no parâmetro "contours"
    def get_answers(self, contours, img):
        if (contours is None):
            raise Exception("Os contornos da imagem para achar as respostas são nulos.")
        if (img is None):
            raise Exception("A imagem fornecida ao get_answers é nula")

        #define os ranges que serão utilizados para localizar as questões/respostas
        ListX = [[100, 106], [121, 128], [143, 148], [163, 168], [183, 189], [247, 253],[268, 273], [288, 293], [308, 313], [328, 336], [392, 398], [413, 419], [434, 440], [455, 461], [476, 482], [539, 545], [560, 566], [581, 587], [602, 608], [623, 629]]
        ListY = [[479, 492], [507, 517], [532, 543], [558, 569], [584, 595], [610, 621],[636, 646], [661, 672], [687, 698], [713, 725], [740, 750], [765, 775], [816, 828], [843, 854], [869, 879], [894, 906], [921, 931], [946, 956], [971, 982], [997, 1008], [1023, 1034], [1049, 1060], [1075, 1085], [1100, 1112], [1127, 1138], [1153, 1164]]
        #define os ranges que serão utilizados para localizar o RA
        RAx = [[454, 465], [474, 485], [494, 506], [515, 526], [535, 547], [556, 568],[577, 588], [597, 609], [618, 629], [638, 650]]
        RAy = [[324, 338], [351, 363], [376, 389], [402, 415]]



        listRet = []
        listNumbers = []
        listOrder = []
        listRA = []
        self.listcx = []
        self.listcy = []
        i=0
        
        for c in contours:
            #Only takes the central point of contours who have 100<Area<350
            i += 1
            if (30<cv2.contourArea(c)<125):
                # calculate moments for each contour
                M = cv2.moments(c)
                
 
                # calculate x,y coordinate of center
                self.cX = int(M["m10"] / M["m00"])
                self.cY = int(M["m01"] / M["m00"])            
                
                #Compare the central point to the Xo value of every letter and question number
                if(self.cX<=404 or self.cY>=438):
                    for x in range(0, 20):
                        if (self.cX >= ListX[x][0] and self.cX <= ListX[x][1]):
                            for j in range(0, 26):
                                if (self.cY >= ListY[j][0] and self.cY <= ListY[j][1]):
                                    cv2.circle(img, (self.cX, self.cY), 0, (0, 255, 0), -15)
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

                                    if (self.cX >= ListX[0][0] and self.cX <= ListX[4][1]):
                                        numero = str(j + 1)
                                    elif (self.cX >= ListX[5][0] and self.cX <= ListX[9][1]):
                                        numero = str(j + 27)
                                    elif (self.cX >= ListX[10][0] and self.cX <= ListX[14][1]):
                                        numero = str(j + 53)
                                    elif (self.cX >= ListX[15][0] and self.cX <= ListX[19][1]):  
                                        numero = str(j + 79)            

                                    listRet.append(letra)
                                    listNumbers.append(numero)
                                    cv2.putText(img, numero+' '+letra, (self.cX - 25, self.cY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                                    cv2.drawContours(img, c, -1, (0,0,255), 2)
                                    
                                    self.listcx.append(self.cX)
                                    self.listcy.append(self.cY)
                
                
                else:
                    for x in range(0,10):
                        if(self.cX >= RAx[x][0] and self.cX <= RAx[x][1]):
                            for j in range(0,4):
                                if(self.cY >= RAy[j][0] and self.cY <= RAy[j][1]):
                                    cv2.circle(img, (self.cX, self.cY), 0, (0, 255, 0), -15)
                                    listRA.append(str(x))

                                    cv2.putText(img, str(x), (self.cX - 25, self.cY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                                    cv2.drawContours(img, c, -1, (0,255,0), 1)

        #print(listRet)
        #print(listRA)
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

                    aux = self.listcx[x]
                    self.listcx[x] = self.listcx[j]
                    self.listcx[j] = aux

                    aux = self.listcy[x]
                    self.listcy[x] = self.listcy[j]
                    self.listcy[j] = aux


  #Insere os - nas questões deixadas em branco
        ctd = 1
        for x in range(0,len(listNumbers)):
            if (listNumbers[x]!=listNumbers[x-1]):
                if (ctd != int(listNumbers[x])):
                    listNumbers.insert(x,str(ctd))
                    listRet.insert(x,"-")
                    self.listcx.insert(x,ctd)
                    self.listcy.insert(x,ctd)
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

        #coloca o número do RA na ordem certa
        listRA.reverse()
        
        #mescla a lista em uma única string para ser adicionada à planilha
        listRA = ''.join(map(str, listRA))

        # cv2.imshow('oi',img)
        # cv2.waitKey()
        self.test_number += 1   
        #cv2.imwrite('ProvasCorrigidas/getcount'+str(self.test_number)+'.jpeg', img)
        #print(listOrder)


        return listRA, listOrder

    #método da construtora
    def __init__(self, contours, align_image):
        #pega o vetor de respostas do gabarito
        self.test_number = 0
        _,self.gabarito= self.get_answers(contours, align_image)
        if (self.gabarito is None or len(self.gabarito) < 50):
            raise Exception("Erro ao obter as respostas do gabarito.\n"+
                             "Verifique se há o mínimo de 50 respostas e se as mesmas estão bem assinaladas!")

    #retorna um dicionário com as listas de respostas corretas e incorretas
    def compare_answers(self, respostas, img10):
        if (respostas is None or len(respostas) < 50):
            raise Exception("Erro ao comparar as respostas da prova com o gabarito!\n"+
                            "Este erro ocorre quando as respostas encontradas de determinada prova "+
                            "não estão de acordo com o número minimo de respostas aceitadas (50)."+
                            "Verifique a qualidade da imagem e do scaneamento!")
        
        wrongAnswers = []
        correctAnswers = []
        for x in range((len(respostas))):
            if (len(respostas[x]) > 1) or respostas[x] != self.gabarito[x]:
                wrongAnswers.append([str(x+1), respostas[x]])
            else:
                correctAnswers.append([str(x+1), respostas[x]])
        Answers = {'correctAnswers': correctAnswers, 'wrongAnswers': wrongAnswers}

       #adiciona o número de acertos na folha de questões
        cv2.putText(img10, str(len(correctAnswers)), (609,230),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 1)

       #pinta questões certas e erradas
        for i in range(len(self.listcx)):
            if respostas[i] != self.gabarito[i]:
                cv2.rectangle(img10, (self.listcx[i]-8, self.listcy[i]- 6), (self.listcx[i]+8, self.listcy[i]+6), (0,0,255), -1)
            else:
                cv2.rectangle(img10, (self.listcx[i]-8, self.listcy[i]- 6), (self.listcx[i]+8, self.listcy[i]+6), (0,255,0), -1)
        
        cv2.imwrite('ProvasCorrigidas/getcount'+str(self.test_number)+'.jpeg', img10)
        
        return Answers
    

