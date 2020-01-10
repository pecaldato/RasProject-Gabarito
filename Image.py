import cv2
import numpy as np

class Image:
    # Função iniciadora da classe.
    def __init__(self, base):
        
        self.base = cv2.imread(base, cv2.IMREAD_COLOR)
        if (self.base is None):
            raise Exception("Erro ao carregar o gabarito "+base)
        self.base = self.resize(self.base)
        self.MAX_MATCHES = 5000
        self.GOOD_MATCH_PERCENT = 0.05
        self.test_number = 0

    #Função para carregar a imagem
    def loadImage(self, gabaritoPath):
        gabarito = cv2.imread(gabaritoPath, cv2.IMREAD_COLOR)
        if (gabarito is None):
            raise Exception("Erro ao abrir a imagem "+gabaritoPath+"\nVerifique se a mesma existe.")
        return gabarito

    #Função de alinhamento de imagens.
    def align_image(self, gabarito_image):
        try:
            # Convert images to grayscale
            im1Gray = cv2.cvtColor(gabarito_image, cv2.COLOR_BGR2GRAY)
            im2Gray = cv2.cvtColor(self.base, cv2.COLOR_BGR2GRAY)
            
            # Detect ORB features and compute descriptors.
            orb = cv2.ORB_create(self.MAX_MATCHES)
            keypoints1, descriptors1 = orb.detectAndCompute(im1Gray, None)
            keypoints2, descriptors2 = orb.detectAndCompute(im2Gray, None)
            
            # Match features.
            #matcher = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
            matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
            matches = matcher.match(descriptors1, descriptors2, None)
            
            # Sort matches by score
            matches.sort(key=lambda x: x.distance, reverse=False)

            # Remove not so good matches
            numGoodMatches = int(len(matches) * self.GOOD_MATCH_PERCENT)
            matches = matches[:numGoodMatches]

            # Draw top matches
            imMatches = cv2.drawMatches(im1Gray, keypoints1, im2Gray, keypoints2, matches, None)
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
            height, width, channels = self.base.shape
            aligned_image = cv2.warpPerspective(gabarito_image, h, (width, height))
            #cv2.imwrite('alinhada.jpeg', aligned_image)
        except:
            raise Exception("Erro ao alinhar a imagem.")
            

        if (aligned_image is None):
            raise Exception("Erro ao alinhar a imagem.")
        
        return aligned_image

    #Função para determinar os contornos do gabarito
    def get_contours(self, aligned_image):
        if (aligned_image is None):
            raise Exception("Imagem fornecida para achar os contornos é nula")

        try:
            blurred = cv2.pyrMeanShiftFiltering(aligned_image,0,110)
            gray = cv2.cvtColor(blurred,cv2.COLOR_BGR2GRAY)
            ret, threshold = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            contours,_ = cv2.findContours(threshold,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
            # cv2.imshow('aff', blurred)
            # cv2.waitKey()
            #itKey()
            #cv2.imwrite('ImBlurr.jpeg', blurred)
            # self.test_number += 1 
            # cv2.imwrite('ProvasCorrigidasBlurr/blurred'+str(self.test_number)+'.jpeg', blurred)
        except:
            raise Exception("Erro ao achar os contornos da imagem.")        
        
        return contours

    #Redimenciona a imagem para ficar no tamanho adequado
    def resize(self, img):
        width = 720
        height = 1280
        dim = (width, height)
        try:
            resized = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        except:
            raise Exception("Erro ao redimensionar a imagem "+str(img))

        return resized   

