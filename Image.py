class Image:
    # Função iniciadora da classe.
    def __init__(self, base):
        self.base = cv2.imread(base, cv2.IMREAD_COLOR)

    #Função para carregar a imagem
    def loadImage(self, gabaritoPath):
        gabarito = cv2.imread(gabaritoPath, cv2.IMREAD_COLOR)
        return gabarito

    #Função de alinhamento de imagens.
    def align_image(self, gabarito_image):
        # Convert images to grayscale
        im1Gray = cv2.cvtColor(gabarito_image, cv2.COLOR_BGR2GRAY)
        im2Gray = cv2.cvtColor(self.base, cv2.COLOR_BGR2GRAY)
        
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
        height, width, channels = self.base.shape
        aligned_image = cv2.warpPerspective(gabarito_image, h, (width, height))
        
        return aligned_image, h

    #Função para determinar os contornos do gabarito
    def get_contours(self, aligned_image):
        blurred = cv2.pyrMeanShiftFiltering(aligned_image,5,100)
        gray = cv2.cvtColor(blurred,cv2.COLOR_BGR2GRAY)
        ret, threshold = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        contours,_ = cv2.findContours(threshold,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
        return contours