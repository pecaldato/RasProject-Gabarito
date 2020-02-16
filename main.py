import cv2
import numpy as np
import xlsxwriter
from os import walk
import os     
from time import sleep
from Image import Image
from respostas import Respostas
from planilha import Planilha
from pdf import Pdf
from collections import defaultdict
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import threading
import shutil 
import json

import tkinter as tk
from tkinter.ttk import Progressbar
from tkinter import scrolledtext
from tkinter import filedialog
from tkinter import messagebox




class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_window()
        self.create_widgets()
        self.open_config_file()

        if (not os.path.isdir('./ProvasParaCorrigir')):
            os.mkdir("./ProvasParaCorrigir")
            messagebox.showwarning('Alerta!', 'A pasta ProvasParaCorrigir não existia e por isso foi criada!\n'
                'Coloque as fotos das provas dentro dela!')
        if (not os.path.isdir('./ProvasCorrigidas')):
            os.mkdir("./ProvasCorrigidas")
            os.mkdir("./ProvasCorrigidas/Resolucao")
        if (not os.path.isdir('./ProvasCorrigidas/Resolucao')):
            os.mkdir("./ProvasCorrigidas/Resolucao")

    def open_config_file(self):
        with open('configs.json') as json_file:
            data = json.load(json_file)
        self.json = data["main"]

    def create_window(self):
        self.master.geometry("675x600")
        self.master["bg"]= "gray"
        self.master.title("Corretor de gabarito")
        self.master.resizable(0,0)

    def create_widgets(self):
        self.btGabarito=tk.Button(self.master, width=15, height=4, text="Selecinar\n Gabarito", command=self.select_gabarito)
        self.btGabarito.place(x=50, y=50)

        self.lblGabarito = tk.Label(self.master, text="Gabarito selecionado:", font=("Arial Bold", 10),bg='gray')
        self.lblGabarito.place(x=250, y=150)

        self.btIniciar=tk.Button(self.master, width=15, height=4, text="Iniciar", command=self.start_thread, state='disable')
        self.btIniciar.place(x=250, y=50)

        self.btParar=tk.Button(self.master, width=15, height=4, text="Cancelar", command=self.btn_parar, state='disable')
        self.btParar.place(x=450, y=50)

        self.progressBar = Progressbar(self.master, length=547)
        self.progressBar.place(x=50, y= 200)

        self.caixaTexto = scrolledtext.ScrolledText(self.master,width=66,height=10)
        self.caixaTexto.place(x=50, y= 250)
        self.caixaTexto.tag_config('error', foreground='red')
        self.caixaTexto.tag_config('done', foreground='green')

        self.menu = tk.Menu(self.master)
        self.menu.add_command(label='Ajuda', command=self.ajuda)
        self.menu.add_command(label='Sobre', command=self.sobre)
        self.master.config(menu=self.menu)

        try:
            self.ras_logo = tk.PhotoImage(file="ras.png")
            self.canvas = tk.Canvas(self.master, width = 400, height = 136)  
            self.canvas.pack()  
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.ras_logo) 
            self.canvas.place(x=130,y=440)
        except Exception as e:
            pass

        # self.quit = tk.Button(self, text="QUIT", fg="red",
        #                       command=self.master.destroy)
        # self.quit.pack(side="bottom")

    def say_hi(self):
        print("hi there, everyone!")

    def select_gabarito(self):
        try:
            self.caixaTexto.delete(1.0,tk.END)

            base_gabarito_path = "base_gabarito_nova.jpg"
            self.img = Image(base_gabarito_path)

            file_path = self.master.filename =  tk.filedialog.askopenfilename(initialdir = os.path.dirname(__file__),title = "Select file",filetypes = 
            (("jpeg files","*.jpg"),("all files","*.*")))
            print(str(file_path))
            gabarito_image = self.img.loadImage(str(file_path))
            align_image = self.img.align_image(gabarito_image)

            reversedstring=''.join(reversed(file_path))
            reversedstring = reversedstring.partition('/')[0]
            reversedstring=''.join(reversed(reversedstring))

            self.lblGabarito["text"] = "Gabarito selecionado: " + reversedstring

            print("get_contor")
            self.gabarito_contours = self.img.get_contours(align_image)
            print("respostas")
            self.resp = Respostas(self.gabarito_contours, align_image)

            self.btIniciar['state'] = 'normal'
        except Exception as e:
            print(str(e))
            self.caixaTexto.insert(tk.INSERT,str(e),'error')


    def start_thread(self):
        thread = threading.Thread(target=self.start,)
        thread.start()


    def start(self):
        self.caixaTexto.delete(1.0,tk.END)
        self.btParar['state'] = 'normal'

        self.plan = Planilha()
        self.pdf = Pdf()
        ctd = 0
        for (dirpath, dirnames, test_path) in walk("ProvasParaCorrigir"):
            for test in test_path:
                try:
                    print(test)
                    test_image = self.img.loadImage("ProvasParaCorrigir/"+test)
                    test_image = self.img.resize(test_image)  
                    align_test = self.img.align_image(test_image)
                    contours = self.img.get_contours(align_test)
                    ra, checked_answers = self.resp.get_answers(contours, align_test, test)
                    correct_answers = self.resp.compare_answers(checked_answers, align_test, test, ra)

                    self.plan.write(ra, checked_answers, correct_answers)
                    self.pdf.read(ra, checked_answers, correct_answers)
                    # print(correct_answers)
                    #print("\n")

                    ra = str(ra[:])
                    # self.img.save_bluer(ra)
                    if(self.json["move_tests"]):
                        shutil.move("ProvasParaCorrigir/"+test, "ProvasCorrigidas/"+ra+".png") 

                    self.caixaTexto.insert(tk.INSERT,'Corrigido '+test+"\n")
                    self.caixaTexto.see(tk.END)
                    ctd += 1
                    self.progressBar['value'] = (ctd*100)/len(test_path)
                    self.master.update_idletasks()


                    if (str(self.btParar['state']) == 'disabled'):
                        return 
                except Exception as e:
                    ctd += 1
                    self.progressBar['value'] = (ctd*100)/len(test_path)
                    self.master.update_idletasks()
                    print(str(e))
                    self.caixaTexto.insert(tk.INSERT,str(e)+"\n",'error')
        
        self.caixaTexto.insert(tk.INSERT,'Todas as provas foram corrigidas!\n','done')
        
        self.btParar['state'] = 'disable'
        self.plan.closePlan()
        self.pdf.closePdf()

    
    def btn_parar(self):
        # if (str(self.btParar['state']) == "normal"):
        self.btParar['state'] = "disable"
        self.caixaTexto.insert(tk.INSERT,"CORRECAO CANCELADA\n",'error')



    def ajuda (self):
        self.caixaTexto.delete(1.0,tk.END)
        self.caixaTexto.insert(tk.INSERT,'Ao iniciar o programa pela primeira vez será criado duas pastas, a "ProvasParaCorrigir" e '
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
        self.caixaTexto.insert(tk.INSERT,'APROVEITE!! =)','done')

    
    def sobre (self):
        self.caixaTexto.delete(1.0,tk.END)
        self.caixaTexto.insert(tk.INSERT,'Este programa foi criado sem fins comerciais com a finalidade de colaborar com a correção das '
                            'provas do cursinho Principia da Unesp Bauru.\n\n')
        self.caixaTexto.insert(tk.INSERT,'Criado pela equipe Beta do Projetos RAS - IEEE - Unesp Bauru:\n Pedro Caldato\n Leonardo Moreno\n Bruno Yudy\n \n'
                            'Com a supervisão de:\n Vitor Vecina\n','done')


    def on_closing(self):
        print("AAAAAAAAAAAAA")
        if messagebox.askokcancel("Sair", "Realmente deseja sair?"):    
            self.btParar['state'] = "disable"
            sleep(500)
            self.master.destroy()




if __name__ == "__main__":
    # main()
    root = tk.Tk()
    app = Application(master=root)
    # root.protocol("WM_DELETE_WINDOW", app.on_closing())
    app.mainloop()
    

    
