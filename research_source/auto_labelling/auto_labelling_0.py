#OpenCV 3.4.2.16 초과 버전부터는 SIRF와 SURF를 지원하지 않음.
#opencv-contrib--python==3.4.2.16 혹은 conda install -c menpo opencv 를 통해 버전 다운그레이드 해야함

import numpy as np
import cv2
from matplotlib import pyplot as plt


#최소 특징점 개수 설정
MIN_MATCH_COUNT = 10

#############################################################여기서부터 for문을 돌려보자


img1 = cv2.imread(r'C:\Users\CGlab\Desktop\NRF_Research\data\image\refrigerator_all(592)\frame0.jpg',0) # queryImage
img2 = cv2.imread(r'C:\Users\CGlab\Desktop\NRF_Research\data\image\refrigerator_all(592)\frame1.jpg',0) # trainImage

fromCenter = False
r = cv2.selectROI(img1, fromCenter)
img1 = img1[int(r[1]):int(r[1]+r[3]),int(r[0]):int(r[0]+r[2])]

# 아이폰 11 Pro 로 촬영하니 이미지 해상도가 너무 커서 조정하는 부분. 이미지 input 따라서 수정 혹은 제거 가능
img2 = cv2.resize(img2, dsize=(0, 0), fx=0.5, fy=0.5, interpolation=cv2.INTER_LINEAR)
 
# Initiate SIFT detector
sift = cv2.xfeatures2d.SIFT_create()
 
# find the keypoints and descriptors with SIFT
kp1, des1 = sift.detectAndCompute(img1,None)
kp2, des2 = sift.detectAndCompute(img2,None)
 
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks = 50)
 
flann = cv2.FlannBasedMatcher(index_params, search_params)
 
matches = flann.knnMatch(des1,des2,k=2)
 
# store all the good matches as per Lowe's ratio test.
good = []
for m,n in matches:
    if m.distance < 0.3 * n.distance:
        good.append(m)

print("Match Points :", len(good), "(> 10)")

if len(good)>MIN_MATCH_COUNT:
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
 
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
    matchesMask = mask.ravel().tolist()
 
    h,w = img1.shape
    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(pts,M)
 
    # 물체를 검출하고 왜곡된 박스 형태로 행렬을 반환함
    box = cv2.polylines(img2,[np.int32(dst)],True,(0,255,0),2) 
    
    # 검출한 물체 박스의 네 꼭짓점의 좌표를 계산
    x_list = [np.int32(dst)[0][0][0], np.int32(dst)[1][0][0], np.int32(dst)[2][0][0], np.int32(dst)[3][0][0]]
    x_list.sort()
    y_list = [np.int32(dst)[0][0][1], np.int32(dst)[1][0][1], np.int32(dst)[2][0][1], np.int32(dst)[3][0][1]]
    y_list.sort()
    
    # 새로운 레이블링
    cv2.rectangle(img2, (x_list[0], y_list[0]), (x_list[3], y_list[3]), (0,255,0), 3)

else:
    # 충분한 특징점 매칭이 이루어지지 않으면 오류 반환
    print("Not enough matches are found - %d/%d" % (len(good),MIN_MATCH_COUNT))
    matchesMask = None

draw_params = dict(matchColor = (0,255,0), # draw matches in green color
                   singlePointColor = None,
                   matchesMask = matchesMask, # draw only inliers
                   flags = 2)

img3 = cv2.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)

cv2.imshow('img', img3)
cv2.waitKey()
cv2.destroyAllWindows()