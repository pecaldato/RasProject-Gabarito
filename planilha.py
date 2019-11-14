import xlsxwriter

class Planilha:
    #método create, cria a planilha
    def create(self):
        self.workbook = xlsxwriter.Workbook('Resultados.xlsx')
        self.worksheet = self.workbook.add_worksheet()
        self.cell_format_wrong = self.workbook.add_format()
        self.cell_format_wrong.set_font_color('red')
        self.cell_format_wrong.set_align('center')
        # cell_format_wrong.set_font_size(15)
        self.cell_format_right = self.workbook.add_format()
        self.cell_format_right.set_font_color('green')
        self.cell_format_right.set_align('center')
        self.cell_format_infos = self.workbook.add_format()
        self.cell_format_infos.set_bold()
        self.cell_format_infos.set_align('center')

        self.worksheet.write(0, 0, "RA")
        self.worksheet.write(1, 0, "Acertos")
        self.worksheet.write(2, 0, "Erros")
        self.worksheet.write(3, 0, "Porcentagem")
        self.worksheet.set_column(0, 0, len("Porcentagem "),self.cell_format_infos)
        for x in range(0,90):
            self.worksheet.write(x+4, 0, str(x+1))

    #iniciadora, chama o método create
    def __init__(self):
        self.create()
        self.col = 1

    def write(self, ra, checked_answers, correct_answers):
        correctAnswers = correct_answers['correctAnswers']
        wrongAnswers = correct_answers['wrongAnswers']
        #adiciona o RA no excel
        self.worksheet.write(0, self.col, ra, self.cell_format_infos)
        #escreve quantas questões o aluno acertou, quantas errou e a porcentagem
        self.worksheet.write(1, self.col, str(len(correctAnswers)),self.cell_format_right)
        self.worksheet.write(2, self.col, str(len(wrongAnswers)),self.cell_format_right)
        self.worksheet.write(3, self.col, str(len(correctAnswers)*2)+"%",self.cell_format_right)
        self.worksheet.set_column(self.col, self.col, 18, self.cell_format_right)
        row = 4
        x = 1
        correct = 0
        wrong = 0
        self.worksheet.write(row,3,'a')
        while (x <= 90):
          if (correct < len(correctAnswers)):
            if (int(correctAnswers[correct][0]) == x):
              self.worksheet.write(row, self.col,str(correctAnswers[correct][1][0]), self.cell_format_right)
              correct += 1
          if (wrong < len(wrongAnswers)):
            if (int(wrongAnswers[wrong][0]) == x):
              erradas = ""
              for j in range (0,len(wrongAnswers[wrong][1])):
                erradas += str(wrongAnswers[wrong][1][j])+" "
              self.worksheet.write(row, self.col, erradas, self.cell_format_wrong)
              wrong += 1

          row += 1
          x += 1

        self.col += 1

    def closePlan(self):
      self.workbook.close()




    