#!/usr/bin/env python
# -*- coding: utf-8 -*- 
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

#Declarando algumas variáveis globais
#5000 0,05
MAX_MATCHES = 5000
GOOD_MATCH_PERCENT = 0.05
gabaritoPath = ""
janela = Tk()
caixaTexto = None
btParar = None
nomeGabarito = []
stop_threads = False


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
  RA = ''
  listRA = []


  #Take the central pixel of the contours and compare to the lists
  for c in contours:
    #Only takes the central point of contours who have 100<Area<350
    if 100<cv2.contourArea(c)<300:
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
                          cv2.putText(imReg, numero+' '+letra, (cX - 25, cY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                          
      else:
          for x in range(0,10):
              if(cX >= RAx[x][0] and cX <= RAx[x][1]):
                  for j in range(0,4):
                      if(cY >= RAy[j][0] and cY <= RAy[j][1]):
                          listRA.append(str(x))
                          cv2.putText(imReg, str(x), (cX - 25, cY),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

 
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
    largura_desejada = 720
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
    row = 0
    col = 0

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
        #fh = open("ProvasParaCorrigir/"+f, 'r')
        im = cv2.imread("ProvasParaCorrigir/"+f, cv2.IMREAD_COLOR)    

        #Redimenciona a imagem para ficar no tamanho adequado
        altura_imagem, largura_imagem = im.shape[:2]
        largura_desejada = 720
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
        #os.rename("./ProvasParaCorrigir/"+f, "./ProvasCorrigidas/"+f)
        #dirpath = os.getcwd()
        shutil.move("./ProvasParaCorrigir/"+f, "./ProvasCorrigidas/"+f)

        #Cria outra imagem referente a prova que foi corrigida porem com as letras e numeros em cima
        #das bolinhas que o aluno assinalou caso precise verificar algum possivel erro no programa
        cv2.imwrite("ProvasCorrigidas/Resolucao/"+RA+"-"+f, imReg)
        
        #Escreve o nome da imagem, a quantidade de questões que o aluno acertou, a quantidade de questões que o aluno errou,
        #as questões acertadas e erradas no arquivo Excel
        cell_format1 = workbook.add_format()
        cell_format1.set_font_color('red')
        cell_format1.set_font_size(15)
        #Adiciona o numero do RA no Excel
        worksheet.write(row, col, RA+" "+f, cell_format1)
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



##############################################################################################################################
#########     A PARTIR DAQUI COMEÇA AS FUNÇÕES E CÓDIGOS RELACIONADOS A PARTE VISUAL               ###########################
##############################################################################################################################


#Função para o usuario selecionar o arquivo que será usado como gabarito
#Após selecionado, a função irá atribuir o caminho a variável global gabaritoPath para ser usado no Iniciar()
#Apenas depois de um arquivo ser selecionado que é liberado o botao Iniciar
def getGabaritoPath ():
  janela.filename =  filedialog.askopenfilename(initialdir = os.path.dirname(__file__),title = "Select file",filetypes = 
      (("jpeg files","*.jpg"),("all files","*.*")))

  global gabaritoPath 
  global nomeGabarito
  nomeGabarito = []
  gabaritoPath = str(janela.filename)
  btIniciar['state'] = 'normal'
  i = len(gabaritoPath)-1
  while (gabaritoPath[i] != '\'' and gabaritoPath[i] != '/'):
    nomeGabarito.append(gabaritoPath[i])
    i -= 1
  nomeGabarito = nomeGabarito[::-1]
  lblGabarito['text'] = 'Gabarito selecionado:\n'+''.join(nomeGabarito)


#Esta função torna a variável global pause como verdadeira ou false. Dependendo do valor dela
#a função Iniciar() fica em um loop infinito, impossibilitando que a correção continue. A função
#também muda o nome do botão.
def pausar ():
  global stop_threads
  stop_threads = True
  btParar['state'] = 'disable'
  btIniciar['state'] = 'normal'
  caixaTexto.insert(tk.INSERT,'Correção cancelada!\n','done')

#Função que informa ao usuário como utilizar o programa ao apertar o botão "Ajuda"
def ajuda ():
  caixaTexto.delete(1.0,tk.END)
  caixaTexto.insert(tk.INSERT,'Ao iniciar o programa pela primeira vez será criado duas pastas, a "ProvasParaCorrigir" e '
                    '"ProvasCorrigidas". Dentro da pasta ProvasParaCorrigir você deverá inserir todas as fotos das provas '
                    'que você deseja corrigir. Vale ressaltar que embora o programa funcione com fotos tiradas pelo celular, '
                    'dependendo de como a mesma seja tirada, da iluminação, angulação e qualidade da foto, o programa '
                    'pode ter erros na hora da correção. Escanear as provas é a forma mais segura de fazer a correção!\n'
                    'Após abrir a janela principal, aperte o botão "Selecionar Gabarito" para selecionar a imagem que será '
                    'utilizada como base para a correção das demais. Os mesmos princípios em relação a qualidade da imagem '
                    'citados a cima valem para esta foto.\n'
                    'Com o gabarito selecionado basta apertar no botão "Iniciar" para começar a correção! Eventuais erros serão '
                    'informados nesta caixa de texto.\n'
                    'Ao finalizar a correção, será criado na pasta "ProvasCorrigidas" uma foto de cada prova corrigida e como '
                    'o programa as corrigiu de forma a facilitar identificação de erros de correção. Também será criado um arquivo '
                    'Excel com os resultados de cada prova!\n')
  caixaTexto.insert(tk.INSERT,'APROVEITE!! =)','done')

#Função que informa ao usuário algumas informações básicas do programa
def sobre ():
  caixaTexto.delete(1.0,tk.END)
  caixaTexto.insert(tk.INSERT,'Este programa foi criado sem fins comerciais com a finalidade de colaborar com a correção das '
                    'provas do cursinho Principia da Unesp Bauru.\n\n')
  caixaTexto.insert(tk.INSERT,'Criado pela equipe Beta do Projetos RAS - IEEE - Unesp Bauru:\n Pedro Caldato\n Leonardo Moreno\n Bruno Yudy\n \n'
                    'Com a supervisão de:\n Vitor Vecina\n','done')


#Inicia a thread quando o usuário aperta o botão "Iniciar"
def iniciandoThread():
  #Declara a thread que será usado na função Iniciar()
  t = threading.Thread(target=iniciar,)
  btParar['state'] = 'normal'
  thread = threading.Thread(target=iniciar,)
  thread.start()

#Função que pergunta ao usuário se ele realmente quer fechar o programa quando o botão fechar é pressionado 
def on_closing():
  global stop_threads
  if messagebox.askokcancel("Sair", "Realmente deseja sair?"):    
    stop_threads = True
    janela.destroy()



#definindo a janela principal
janela.geometry("675x600")
janela["bg"]= "gray"
janela.title("Corretor de gabarito")
janela.resizable(0,0)

#verifica se as pastas ProvasParaCorrigir e ProvasCorrigidas existem,
#Caso contrário o programa as cria e informa ao usuario oq deve ser feito
if (not os.path.isdir('./ProvasParaCorrigir')):
  os.mkdir("./ProvasParaCorrigir")
  messagebox.showwarning('Alerta!', 'A pasta ProvasParaCorrigir não existia e por isso foi criada!\n'
    'Coloque as fotos dos gabaritos dentro dela!')
if (not os.path.isdir('./ProvasCorrigidas')):
  os.mkdir("./ProvasCorrigidas")
  os.mkdir("./ProvasCorrigidas/Resolucao")
if (not os.path.isdir('./ProvasCorrigidas/Resolucao')):
  os.mkdir("./ProvasCorrigidas/Resolucao")


#Definindo os botões, caixas de texto, menu bar, progress bar, labels, etc.
btGabarito=Button(janela, width=15, height=4, text="Selecinar\n Gabarito", command=getGabaritoPath,)
btGabarito.place(x=50, y=50)

lblGabarito = Label(janela, text="Gabarito selecionado:", font=("Arial Bold", 10),bg='gray')
lblGabarito.place(x=250, y=150)

btIniciar=Button(janela, width=15, height=4, text="Iniciar", command=iniciandoThread, state='disable')
btIniciar.place(x=250, y=50)

btParar=Button(janela, width=15, height=4, text="Cancelar", command=pausar, state='disable')
btParar.place(x=450, y=50)

progressBar = Progressbar(janela, length=547)
progressBar.place(x=50, y= 200)

caixaTexto = scrolledtext.ScrolledText(janela,width=66,height=10)
caixaTexto.place(x=50, y= 250)
caixaTexto.tag_config('error', foreground='red')
caixaTexto.tag_config('done', foreground='green')

menu = Menu(janela)
menu.add_command(label='Ajuda', command=ajuda)
menu.add_command(label='Sobre', command=sobre)
janela.config(menu=menu)

try:
  canvas = Canvas(janela, width = 365, height = 138)      
  canvas.pack()      
  img = PhotoImage(file="principia.png")     
  canvas.create_image(0,0, anchor=tk.NW, image=img)      
  canvas.place(x=140,y=440)
except:
  pass

#Verifica se o botão de fechar foi abertado. Chama a função on_closing em caso positivo
janela.protocol("WM_DELETE_WINDOW", on_closing)
janela.mainloop()