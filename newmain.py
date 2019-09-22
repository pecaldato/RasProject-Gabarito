import cv2
import numpy as np
from os import walk
import os     
from Image import Image
from respostas import Respostas


def main ():
    base_gabarito_path = "baseLoca.jpeg"
    gabarito_path = "gabaritoNovo.jpeg"
    
    img = Image(base_gabarito_path)
    gabarito_image = img.loadImage(gabarito_path)
    gabarito_image = img.resize(gabarito_image)  
    # cv2.destroyAllWindows()
    align_image = img.align_image(gabarito_image)
    contours = img.get_contours(align_image)

    resp = Respostas(contours, align_image)

    files = []
    for (dirpath, dirnames, test_path) in walk("ProvasParaCorrigir"):
        for test in test_path:
            print(test)
            gabarito_image = img.loadImage("ProvasParaCorrigir/"+test)
            align_image = img.align_image(gabarito_image)
            gabarito_image = img.resize(gabarito_image)  
            contours = img.get_contours(align_image)
            ra, checked_answers = resp.get_answers(contours, align_image)
            correct_answers = resp.compare_answers(checked_answers)
            print(correct_answers)
            print("\n")
            #print(ra)




if __name__ == "__main__":
    main()
    
