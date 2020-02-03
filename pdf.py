from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

class Pdf:

    def __init__(self):
        self.doc = SimpleDocTemplate("resultados.pdf", pagesize=letter)
        self.elements = []
        self.infos = [["RA", "Acertos", "Erros"]]

    def read(self, ra, checked_answers, correct_answers):
        correctAnswers = correct_answers['correctAnswers']
        wrongAnswers = correct_answers['wrongAnswers']
        self.infos.append([ra, str(len(correctAnswers)),str(len(wrongAnswers))])

    def closePdf(self):
        t=Table(self.infos)
        t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.cyan),
        ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
        ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
        self.elements.append(t)
        self.doc.build(self.elements)