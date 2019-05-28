#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from __future__ import print_function
import cv2
import numpy as np
import xlsxwriter
from os import walk
import os
import progressbar
from time import sleep

#5000 0.10
MAX_MATCHES = 5000
GOOD_MATCH_PERCENT = 0.06


def alignImages(im1, im2):

  # Convert images to grayscale
  im1Gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
  im2Gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
  
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
  #imMatches = cv2.drawMatches(im1, keypoints1, im2, keypoints2, matches, None)
  #cv2.imwrite("matches.jpg", imMatches)
  
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

#Função que retorna a lista com as letras assinaladas pelo aluno 
def getAnswer(contours, imReg):
  #List of the beginning to end of Xo pixels of every question
  ListX = [[147,165],[168,185],[187,205],[207,225],[227,245],[274,292],[294,312],[314,332],[334,352],[354,373],[403,421],
  [423,440],[443,461],[463,480],[483,501]]

  #List of the beginning to end of Yo pixels of every question
  ListY = [[274,291],[297,315],[322,340],[347,365],[371,390],[396,414],[420,439],[445,463],[469,487],[494,512],[531,549],
  [556,574],[580,598],[605,622],[629,647],[653,672],[678,696], [702,721],[727,745],[751,770],[17,35],[41,59],[66,84],
  [90,108],[115,133],[140,157],[163,181],[189,207],[212,231],[237,255]]
  
  RAx = [[148,164],[168,184],[188,204], [208,224], [228,244], [248,264],[268,284],[288,304],[308,324],[328,344]]
  RAy = [[124,140],[148,164],[172,188],[196,212]]


  #Declaring the list which have the letters of the questions
  listRet = []
  listNumbers = []
  listRA = []

  #Take the central pixel of the contours and compare to the lists
  for c in contours:
    #Only takes the central point of contours who have 100<Area<350
    if 100<cv2.contourArea(c)<350:

      cv2.drawContours(imReg, c, -1, (0,255,0), 3)

      # calculate moments for each contour
      M = cv2.moments(c)
 
      # calculate x,y coordinate of center
      cX = int(M["m10"] / M["m00"])
      cY = int(M["m01"] / M["m00"])

      #Compare the central point to the Xo value of every letter and question number
      if(cX>=360 or cY>=243):
          for x in range(0, 15):
              if (cX >= ListX[x][0] and cX <= ListX[x][1]):
                  for j in range(0, 30):
                      if (cY >= ListY[j][0] and cY <= ListY[j][1]):
                          cv2.circle(imReg, (cX, cY), 0, (255, 255, 255), -15)
                          if (x==0 or x==5 or x==10):
                              letra = "A"
                          elif (x==1 or x==6 or x==11):
                              letra = "B"
                          elif (x==2 or x==7 or x==12):
                              letra = "C"
                          elif (x==3 or x==8 or x==13):
                              letra = "D"
                          elif (x==4 or x==9 or x==14):
                              letra = "E"  

                          if (cX >= ListX[0][0] and cX <= ListX[4][1]):
                              numero = str(j+1)
                          elif (cX >= ListX[5][0] and cX <= ListX[9][1]):
                              numero = str(j + 21)
                          elif (cX >= ListX[10][0] and cX <= ListX[14][1]):
                              numero = str(j + 21)            

                          listRet.append(letra)
                          listNumbers.append(numero)
                          cv2.putText(imReg, numero+' '+letra, (cX - 25, cY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                          
      else:
          for x in range(0,10):
              if(cX >= RAx[x][0] and cX <= RAx[x][1]):
                  for j in range(0,4):
                      if(cY >= RAy[j][0] and cY <= RAy[j][1]):
                          listRA.append(str(x))
                          cv2.circle(imReg, (cX, cY), 3, (255, 255, 255), -15)
  listRA.reverse()   
                    
  #Ordena as listas que contem os numeros e as letras
  for x in range(0,len(listNumbers)-1):
    for j in range(0,len(listNumbers)):
      if (int(listNumbers[x]) <= int(listNumbers[j])):
        aux = listNumbers[x]
        listNumbers[x] = listNumbers[j]
        listNumbers[j] = aux

        aux = listRet[x]
        listRet[x] = listRet[j]
        listRet[j] = aux


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
  while x < len(listNumbers)-1:
    ctd = x
    aux = []
    while (int(listNumbers[ctd]) == int(listNumbers[x])):
      aux.append(listRet[ctd])
      ctd += 1
    x = ctd
    listOrder.append(aux)

  return [listOrder,listRA]

#Função que compara a lista que contem as questões assinaladas pelo aluno
#com a lista que contem o gabarito, retornando uma lista com as questões certas e 
#outra com as questões erradas
def compareTemplate(test, template):
  wrongAnswer = []
  correctAnswers = []
  for x in range(len(test)):
    if (len(test[x]) > 1) or test[x] != template[x]:
      wrongAnswer.append([str(x+1),test[x]])
    else:
      correctAnswers.append([str(x+1),test[x]])

  return correctAnswers, wrongAnswer


#Função main principal
if __name__ == '__main__':
  
  # Read reference image
  refFilename = "baseGabaritoNovo.jpeg"
  print("Reading reference image : ", refFilename)
  imReference = cv2.imread(refFilename, cv2.IMREAD_COLOR)

  refFilename = "baseGabaritoNovoCortado.jpeg"
  print("Reading reference image : ", refFilename)
  imReference2 = cv2.imread(refFilename, cv2.IMREAD_COLOR)
  
  if (True):
    # Solicita para o usuario uma imagem que será usada como gabarito
    #na comparação das provas.
    #imFilename = input("Digite o nome da imagem que será usada como gabarito. Não se esqueça da extensão do mesmo: ")

    #Verifica se o arquivo informado existe. Caso não existir avisa o usuario e encerra o programa.
    #fh = open(imFilename, 'r')
    #print("Reading image to be the template : ", imFilename);  
    im = cv2.imread("gabaritoNovo.jpeg", cv2.IMREAD_COLOR)
    
    #Alinha a imagem do gabarito com a imagem base
    imReg, h = alignImages(im, imReference)
    imReg, h = alignImages(imReg, imReference2)

    #Acha os contornos do gabarito
    blurred = cv2.pyrMeanShiftFiltering(imReg,5,100)
    gray = cv2.cvtColor(blurred,cv2.COLOR_BGR2GRAY)
    ret, threshold = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    contours,_ = cv2.findContours(threshold,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)

    #Envia os contornos do gabarito e recebe uma lista com as letras assinaladas pelo aluno
    template = getAnswer(contours, imReg)[0]

    #########################################################################################################################

    #Pega todos os arquivos da pasta ProvasParaCorrigir
    files = []
    for (dirpath, dirnames, filenames) in walk("ProvasParaCorrigir"):
     files.extend(filenames)


    #Cria o arquivo do Excel
    workbook = xlsxwriter.Workbook('Resultados.xlsx')
    worksheet = workbook.add_worksheet()
    row = 0
    col = 0

    bar = progressbar.ProgressBar(maxval=len(files), \
    widgets=[progressbar.Bar('#', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    ctd = 0
    #Varre todos os arquivos encontrados na pasta ProvasParaCorrigir
    for f in files:
      if(True):
        #Verifica se o arquivo realmente existe, e caso não seja uma imagem
        #informa o erro ao usuario e continua corrigindo as demais provas
        fh = open("ProvasParaCorrigir/"+f, 'r')
        im = cv2.imread("ProvasParaCorrigir/"+f, cv2.IMREAD_COLOR)

        #Lê a prova
        imReg, h = alignImages(im, imReference)
        imReg, h = alignImages(imReg, imReference2)
        #Aplica o blur para remover os ruidos e encontra os contornos da prova
        blurred = cv2.pyrMeanShiftFiltering(imReg,5,100)
        gray = cv2.cvtColor(blurred,cv2.COLOR_BGR2GRAY)
        ret, threshold = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        contours,_ = cv2.findContours(threshold,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)

        #Retorna a lista com as letras assinaladas pelo aluno da prova
        prova = getAnswer(contours, imReg)[0]

        #Verifica quais questões o aluno acertou e quais ele errou se baseando no gabarito informado
        #pelo usuario
        correctAnswers, wrongAnswer = compareTemplate(prova,template)

        #Transfere a imagem da pasta ProvasParaCorrigir para a pasta ProvasCorrigidas
        #os.rename("/home/pedro/Documentos/GitHub/RasProject1/ProvasParaCorrigir/"+f, "/home/pedro/Documentos/GitHub/RasProject1/ProvasCorrigidas/"+f)

        #Cria outra imagem referente a prova que foi corrigida porem com as letras e numeros em cima
        #das bolinhas que o aluno assinalou caso precise verificar algum possivel erro no programa
        cv2.imwrite("ProvasCorrigidas/Corrigido"+f, imReg)
        
        #Escreve o nome da imagem, a quantidade de questões que o aluno acertou, a quantidade de questões que o aluno errou,
        #as questões acertadas e erradas no arquivo Excel
        cell_format1 = workbook.add_format()
        cell_format1.set_font_color('red')
        cell_format1.set_font_size(15)
        worksheet.write(row, col, f, cell_format1)
        worksheet.write(row,col, "Número de Inscrição: " + getAnswer(contours, imReg)[1][0] +getAnswer(contours, imReg)[1][1] + getAnswer(contours, imReg)[1][2] +getAnswer(contours, imReg)[1][3] )
        row += 1
        col = 1
        worksheet.write(row, col, "Corretas:")
        col += 1
        worksheet.write(row, col, "Total: " + str(len(correctAnswers)))
        col += 1
        
        for i in range(len(correctAnswers)):
          worksheet.write(row, col, str(correctAnswers[i][0])+"-"+str(correctAnswers[i][1][0]))
          col += 1

        row += 1
        col = 1
        worksheet.write(row, col, "Incorretas:")
        col += 1
        worksheet.write(row, col, "Total: " + str(len(wrongAnswer)))
        col += 1
        for i in range(len(wrongAnswer)):
          worksheet.write(row, col,str(wrongAnswer[i][0])+"-"+str(wrongAnswer[i][1]))
          col += 1

        col = 0
        row += 2  
        
        bar.update(ctd+1)
      #except:
        #bar.update(ctd+1)
        #print(colored("\nErro ao carregar o arquivo " + f + '\n','red'))
      ctd+=1 
    workbook.close()
    bar.finish()
    
  #except:
    #print("O arquivo fornecido não foi encontrado. Verifique se o mesmo existe e se está na extensão correta!")