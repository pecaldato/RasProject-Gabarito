import numpy as np
import cv2 as cv

img1 = cv.imread('base.jpeg',cv.IMREAD_GRAYSCALE)          # queryImage
img2 = cv.imread('prova2.jpeg',cv.IMREAD_GRAYSCALE) # trainImage
# Initiate ORB detector
orb = cv.ORB_create(5000)
# find the keypoints and descriptors with ORB
kp1, des1 = orb.detectAndCompute(img1,None)
kp2, des2 = orb.detectAndCompute(img2,None)

# create BFMatcher object
bf = cv.BFMatcher(cv.NORM_HAMMING, crossCheck=True)
# Match descriptors.
matches = bf.match(des1,des2)
# Sort them in the order of their distance.
matches = sorted(matches, key = lambda x:x.distance)

# Remove not so good matches
numGoodMatches = int(len(matches) * 0.05)
matches = matches[:numGoodMatches]

# Draw top matches
imMatches = cv.drawMatches(img1, kp1, img2, kp2, matches, None)
cv.imwrite("NovoAlinhada.jpeg", imMatches)

# Extract location of good matches
points1 = np.zeros((len(matches), 2), dtype=np.float32)
points2 = np.zeros((len(matches), 2), dtype=np.float32)

for i, match in enumerate(matches):
    points1[i, :] = kp1[match.queryIdx].pt
    points2[i, :] = kp2[match.trainIdx].pt

# Find homography
h, mask = cv.findHomography(points1, points2, cv.RANSAC)

# Use homography
height, width = img1.shape
aligned_image = cv.warpPerspective(img2, h, (width, height))
cv.imwrite('alinhada.jpeg', aligned_image)

