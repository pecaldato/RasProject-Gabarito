import cv2
import numpy as np
from os import walk
import os

from user import Image
from user import Respostas


def main ():
    base_gabarito_path = 'baseGabarito.jpeg'
    gabarito_path = 'gabarito.jpeg'

    Image(base_gabarito_path)
    gabarito_image = Image.loadImage(gabarito_path)
    align_image,_ = Image.align_image(gabarito_image)
    contours= Image.get_contours(align_image)

    Respostas(contours)

    files = []
    for (dirpath, dirnames, test_path) in walk("ProvasParaCorrigir"):
        gabarito_image = Image.loadImage(test_path)
        align_image = Image.align_image(gabarito_image)
        contours = Image.get_contours(align_image)
        checked_answers = Respostas.get_answers(contours)
        correct_answers = Respostas.compare_answers(checked_answers)




if __name__ == "__main__":
    main()
    