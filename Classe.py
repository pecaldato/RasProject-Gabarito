import cv2
import numpy as np
import xlsxwriter
from os import walk
import os
from time import sleep
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar
from tkinter import scrolledtext
from tkinter import *
import tkinter as tk
from tkinter import Menu
import threading
import shutil

#Declaração da classe de manipulação de imagem
class Image:
    #Declaração das variáveis globais
    MAX_MATCHES = 5000
    GOOD_MATCH_PERCENT = 0.05
    gabaritoPath = ""
    janela = Tk()
    caixaTexto = None
    btParar = None
    stop_threads = False

    # Função iniciadora da classe.
    def __init__(self, im1, im2):
        self.im1 = im1
        self.im2 = im2

    #Função de alinhamento de imagens. im2 é a referência.
    def alignImages(self, im1, im2):
        # Convert images to grayscale
        im1Gray = cv2.cvtColor(self.im1, cv2.COLOR_BGR2GRAY)
        im2Gray = cv2.cvtColor(self.im2, cv2.COLOR_BGR2GRAY)
        
        # Detect ORB features and compute descriptors.
        orb = cv2.ORB_create(MAX_MATCHES)
        keypoints1, descriptors1 = orb.detectAndCompute(im1Gray, None)
        keypoints2, descriptors2 = orb.detectAndCompute(im2Gray, None)
        
        # Match features.
        matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
        matches = matcher.match(descriptors1, descriptors2, None)
        
        # Sort matches by score
        matches.sort(key=lambda x: x.distance, reverse=False)

        # Remove not so good matches
        numGoodMatches = int(len(matches) * GOOD_MATCH_PERCENT)
        matches = matches[:numGoodMatches]

        # Draw top matches
        # imMatches = cv2.drawMatches(im1, keypoints1, im2, keypoints2, matches, None)
        # cv2.imwrite("matches.jpeg", imMatches)
        
        # Extract location of good matches
        points1 = np.zeros((len(matches), 2), dtype=np.float32)
        points2 = np.zeros((len(matches), 2), dtype=np.float32)

        for i, match in enumerate(matches):
            points1[i, :] = keypoints1[match.queryIdx].pt
            points2[i, :] = keypoints2[match.trainIdx].pt
        
        # Find homography
        h, mask = cv2.findHomography(points1, points2, cv2.RANSAC)

        # Use homography
        height, width, channels = im2.shape
        im1Reg = cv2.warpPerspective(im1, h, (width, height))
        
        return im1Reg, h

    #Função main principal
    def iniciar():
        #Limpa a caixa de texto
        caixaTexto.delete(1.0,tk.END)
        global stop_threads

        #Desabilita o botao Iniciar
        btIniciar['state'] = 'disable'

        # Read reference image
        #Para evitar que o usuário edite as imagens essencias do programa, elas foram transformadas em npy
        imReference = np.load("base.npy")
        imReference2 = np.load("baseCortado.npy")

        
        try:
            # Utiliza a imagem que o usuário selecionou.
            im = cv2.imread(gabaritoPath, cv2.IMREAD_COLOR)
        
            #Redimenciona a imagem para ficar no tamanho adequado
            altura_imagem, largura_imagem = im.shape[:2]
            largura_desejada = 1280
            percentual_largura = float(largura_desejada) / float(largura_imagem)
            altura_desejada = int((altura_imagem * percentual_largura))
            im = cv2.resize(im,(largura_desejada, altura_desejada), interpolation = cv2.INTER_CUBIC)
            
            #Alinha a imagem do gabarito com a imagem base
            imReg, h = alignImages(im, imReference)
            imReg, h = alignImages(imReg, imReference2)

            #Acha os contornos do gabarito
            blurred = cv2.pyrMeanShiftFiltering(imReg,5,100)
            gray = cv2.cvtColor(blurred,cv2.COLOR_BGR2GRAY)
            ret, threshold = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            contours,_ = cv2.findContours(threshold,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)

            #Envia os contornos do gabarito e recebe uma lista com as letras assinaladas pelo aluno
            template, _ = getAnswer(contours, imReg)

            #########################################################################################################################

            #Pega todos os arquivos da pasta ProvasParaCorrigir
            files = []
            for (dirpath, dirnames, filenames) in walk("ProvasParaCorrigir"):
            files.extend(filenames)


            #Cria o arquivo do Excel
            workbook = xlsxwriter.Workbook('Resultados.xlsx')
            worksheet = workbook.add_worksheet()

            cell_format_wrong = workbook.add_format()
            cell_format_wrong.set_font_color('red')
            cell_format_wrong.set_align('center')
            # cell_format_wrong.set_font_size(15)
            cell_format_right = workbook.add_format()
            cell_format_right.set_font_color('green')
            cell_format_right.set_align('center')

            cell_format_infos = workbook.add_format()
            cell_format_infos.set_bold()
            cell_format_infos.set_align('center')

            worksheet.write(0, 0, "RA")
            worksheet.write(1, 0, "Acertos")
            worksheet.write(2, 0, "Erros")
            worksheet.write(3, 0, "Porcentagem")
            worksheet.set_column(0, 0, len("Porcentagem "),cell_format_infos)
            for x in range(0,50):
            worksheet.write(x+4, 0, str(x+1))

            col = 1
            ctd = 1
            #Varre todos os arquivos encontrados na pasta ProvasParaCorrigir
            for f in files:
            #Caso o botão de fechar seja precionado e a thread estiver em execusão, esse if finaliza a mesma
            if stop_threads:
                stop_threads = False
                return 
            try:
                #Verifica se o arquivo realmente existe, e caso não seja uma imagem
                #informa o erro ao usuario e continua corrigindo as demais provas
                im = cv2.imread("ProvasParaCorrigir/"+f, cv2.IMREAD_COLOR)    

                #Redimenciona a imagem para ficar no tamanho adequado
                altura_imagem, largura_imagem = im.shape[:2]
                largura_desejada = 1280
                percentual_largura = float(largura_desejada) / float(largura_imagem)
                altura_desejada = int((altura_imagem * percentual_largura))
                im = cv2.resize(im,(largura_desejada, altura_desejada), interpolation = cv2.INTER_CUBIC)

                #Lê a prova
                imReg, h = alignImages(im, imReference)
                imReg, h = alignImages(imReg, imReference2)

                #Aplica o blur para remover os ruidos e encontra os contornos da prova
                blurred = cv2.pyrMeanShiftFiltering(imReg,10,100)
                gray = cv2.cvtColor(blurred,cv2.COLOR_BGR2GRAY)
                threshold = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,15,8)
                contours,_ = cv2.findContours(threshold,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)


                #Retorna a lista com as letras assinaladas pelo aluno da prova
                prova, RA = getAnswer(contours, imReg)

                #Verifica quais questões o aluno acertou e quais ele errou se baseando no gabarito informado
                #pelo usuario
                correctAnswers, wrongAnswer = compareTemplate(prova,template)

                #Verifica grandes erros de alinhamentos. Se o mesmo houver força uma exceção
                if (len(correctAnswers)+len(wrongAnswer) < 50):
                raise ValueError()

                #Transfere a imagem da pasta ProvasParaCorrigir para a pasta ProvasCorrigidas
                shutil.move("./ProvasParaCorrigir/"+f, "./ProvasCorrigidas/"+f)

                #Cria outra imagem referente a prova que foi corrigida porem com as letras e numeros em cima
                #das bolinhas que o aluno assinalou caso precise verificar algum possivel erro no programa
                cv2.imwrite("ProvasCorrigidas/Resolucao/"+RA+"-"+f, imReg)
                
            
                #Adiciona o numero do RA no Excel
                worksheet.write(0, col, RA, cell_format_infos)
                #Escreve o nome da imagem, a quantidade de questões que o aluno acertou, a quantidade de questões que o aluno errou,
                #as questões acertadas e erradas no arquivo Excel
                worksheet.write(1, col, str(len(correctAnswers)),cell_format_right)
                worksheet.write(2, col, str(len(wrongAnswer)),cell_format_right)
                worksheet.write(3, col, str(len(correctAnswers)*2)+"%",cell_format_right)
                worksheet.set_column(col, col, 18,cell_format_right)

                row = 4
                x = 1
                correct = 0
                wrong = 0
                while (x <= 50):
                if (correct < len(correctAnswers)):
                    if (int(correctAnswers[correct][0]) == x):
                    worksheet.write(row, col,str(correctAnswers[correct][1][0]), cell_format_right)
                    correct += 1
                if (wrong < len(wrongAnswer)):
                    if (int(wrongAnswer[wrong][0]) == x):
                    erradas = ""
                    for j in range (0,len(wrongAnswer[wrong][1])):
                        erradas += str(wrongAnswer[wrong][1][j])+" "
                    worksheet.write(row, col, erradas, cell_format_wrong)
                    wrong += 1

                row += 1
                x += 1

                col += 1

                #Atualiza os valores da ProgressBar
                caixaTexto.insert(tk.INSERT,'Corrigido '+f+"\n")
                caixaTexto.see(tk.END)
                progressBar['value'] = (ctd*100)/len(files)
                janela.update_idletasks()
            except:
                try:
                caixaTexto.insert(tk.INSERT,'Erro ao abrir ou alinhar o arquivo '+f+". Verifique a extensão e a qualidade"
                "da imagem\n",'error')
                progressBar['value'] = (ctd*100)/len(files)
                janela.update_idletasks()
                except:
                pass
            ctd+=1 
            workbook.close()
            if stop_threads:
                stop_threads = False
                return 
            caixaTexto.insert(tk.INSERT,'Todas as provas foram corrigidas!\n','done')
            btParar['state'] = 'disable'
            
        except:
            caixaTexto.insert(tk.INSERT,'Não foi possível carregar o gabarito selecionado! Verifique a extensão '
            'e integridade do arquivo!\n','error')
        btIniciar['state'] = 'normal'


#Declaração da classe de manipulação do gabarito
class OpGabarito:
    # Função iniciadora da classe.
    def __init__(self, contours, imReg, test, template):
        self.contours = contours
        self.imReg = imReg
        self.test = test
        self.template = template

    #Função que retorna a lista com as letras assinaladas pelo aluno
    def getAnswer(self, contours, imReg):
        #List of the beginning to end of Xo pixels of every question
        ListX = [[166,203],[204,239],[240,276],[277,312],[313,349],[426,463],[464,499],[500,536],[537,572],[573,609],[686,723],
        [724,759],[760,796],[797,832],[833,869],[946,983],[984,1019],[1020,1056],[1057,1092],[1093,1129]]

        #List of the beginning to end of Yo pixels of every question
        ListY = [[668,705],[706,741],[742,778],[779,814],[815,851],[852,888],[889,924],[925,961],[962,997],[998,1034],[1035,1071],
        [1072,1107],[1144,1181],[1182,1217],[1219,1254],[1255,1290],[1291,1327], [1328,1364],[1365,1400],[1401,1437],[1438,1473],[1474,1510],[1511,1547],
        [1548,1583],[1584,1620],[1621,1656]]

        RAx = [[798,835],[836,871],[872,908], [909,944], [945,981], [982,1018],[1019,1054],[1055,1091],[1092,1127],[1128,1164]]
        RAy = [[448,484],[485,521],[522,557],[558,594]]

        #Declaring the list which have the letters of the questions
        listRet = []
        listNumbers = []
        RA = ''
        listRA = []


        #Take the central pixel of the contours and compare to the lists
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
                                cv2.circle(self.imReg, (cX, cY), 0, (255, 255, 255), -15)
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
                                cv2.putText(self.imReg, numero+' '+letra, (cX - 25, cY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                                
            else:
                for x in range(0,10):
                    if(cX >= RAx[x][0] and cX <= RAx[x][1]):
                        for j in range(0,4):
                            if(cY >= RAy[j][0] and cY <= RAy[j][1]):
                                listRA.append(str(x))
                                cv2.putText(self.imReg, str(x), (cX - 25, cY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        
        #Ordena as listas que contem os numeros e as letras
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


        #Cria a listOrder, que é a lista já ordenada com o numero das questões e as letras juntas
        listOrder = []
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

        #Cria uma string com o RA do aluno
        listRA.reverse()
        if (len(listRA)!= 4):
            RA = "Não identificado"
        else:
            RA = ''.join(listRA)
        

        return listOrder, RA

    #Função que compara a lista que contem as questões assinaladas pelo aluno
    #com a lista que contem o gabarito, retornando uma lista com as questões certas e 
    #outra com as questões erradas
    def compareTemplate(self, test, template):
        wrongAnswer = []
        correctAnswers = []
        for x in range(len(self.test)):
            if (len(self.test[x]) > 1) or self.test[x] != self.template[x]:
            wrongAnswer.append([str(x+1),self.test[x]])
            else:
            correctAnswers.append([str(x+1),self.test[x]])

        return correctAnswers, wrongAnswer
