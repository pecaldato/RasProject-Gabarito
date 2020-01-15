import cv2
import numpy as np
import xlsxwriter
from os import walk
import os     
from Image import Image
from respostas import Respostas
from planilha import Planilha


def main ():
    # base_gabarito_path = "base_prova.jpeg"
    base_gabarito_path = "base_gabarito_nova.jpg"
    gabarito_path = "gabaritoNovo.jpeg"
    
    img = Image(base_gabarito_path)
    gabarito_image = img.loadImage(gabarito_path)
    gabarito_image = img.resize(gabarito_image)  
    # cv2.destroyAllWindows()
    align_image = img.align_image(gabarito_image)
    contours = img.get_contours(align_image)

    resp = Respostas(contours, align_image)
    plan = Planilha()
    files = []
    for (dirpath, dirnames, test_path) in walk("ProvasParaCorrigir"):
        for test in test_path:
            try:
                print(test)
                gabarito_image = img.loadImage("ProvasParaCorrigir/"+test)
                gabarito_image = img.resize(gabarito_image)  
                align_image = img.align_image(gabarito_image)
                contours = img.get_contours(align_image)
                ra, checked_answers = resp.get_answers(contours, align_image)
                correct_answers = resp.compare_answers(checked_answers, align_image, test)

                plan.write(ra, checked_answers, correct_answers)
                #print(correct_answers)
                #print("\n")
            except Exception as e:
                print(str(e))
    plan.closePlan()





if __name__ == "__main__":
    main()
    
