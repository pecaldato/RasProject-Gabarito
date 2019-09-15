import cv2
import numpy as np
from os import walk
import os

from Image import Image
from respostas import Respostas


def main ():
    base_gabarito_path = "gabarito.jpg"
    gabarito_path = "prova.jpg"
    
    img = Image(base_gabarito_path)

    gabarito_image = img.loadImage(gabarito_path)
    align_image = img.align_image(gabarito_image)
    contours = img.get_contours(align_image)

    resp = Respostas(contours)

    files = []
    for (dirpath, dirnames, test_path) in walk("ProvasParaCorrigir"):
        gabarito_image = img.loadImage(gabarito_path)
        align_image = img.align_image(gabarito_image)
        contours = img.get_contours(align_image)
        ra, checked_answers = resp.get_answers(contours)
        correct_answers = resp.compare_answers(checked_answers)
        print(correct_answers)




if __name__ == "__main__":
    main()
    
