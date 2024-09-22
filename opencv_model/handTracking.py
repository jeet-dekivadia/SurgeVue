import cv2
import mediapipe as mp
from cvzone.HandTrackingModule import HandDetector

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 1280)

detector = HandDetector(detectionCon=0.8)
startDist = None
scale = 0
cy = 500
cx = 500

while True:
    success, img = cap.read()
    hands, img = detector.findHands(img)
    #hands = detector.findHand(img, draw = False)

    img1 = cv2.imread("brainTumorImg.png")

    if len(hands) == 2:
        hand1 = hands[0]
        lmList1 = hands[0]["lmList"] # Lost of 21 Landmark points
        bbox1 = hand1["bbox"] # Bounding Box info
        centerPoint1 = hand1["center"]
        handType1 = hand1["type"]
        
        fingers1 = detector.fingersUp(hand1)

        hand2 = hands[1]
        lmList2 = hands[1]["lmList"] # Lost of 21 Landmark points
        bbox2 = hand2["bbox"] # Bounding Box info
        centerPoint2 = hand2["center"]
        handType2 = hand2["type"]

        fingers2 = detector.fingersUp(hand2)
            
        #print(handType1, handType2)
        #print(fingers1, fingers2)
        length, info, img = detector.findDistance(centerPoint1, centerPoint2, img)

        if detector.fingersUp(hand1) == [1,1,0,0,0] and detector.fingersUp(hand2) == [1,1,0,0,0]:
            #print("Zoom Gesture")
                
            if startDist is None:
                length, info, img = detector.findDistance(centerPoint1, centerPoint2, img)
                #print(length)
                startDist = length

            length, info, img = detector.findDistance(centerPoint1, centerPoint2, img)
            #length, info, img = detector.findDistance(lmList1[8], lmList2[8], img)
            scale = int((length - startDist)//2)
            cx, cy = info[4:] 
            print(scale)
    else:
        startDist = None
    
    try:
        h1, w1, _= img1.shape
        print(h1)
        print(w1)
        
        newH, newW = ((h1+scale)//2)*2, ((w1+scale)//2)*2
        print(newH)
        print(newW)
        
        img1 = cv2.resize(img1, (newW, newH)) 

        print(cy-newH//2)
        print(cy+ newH//2)
        print(cx-newW//2)
        print(cx+ newW//2)


        img[cy-newH//2:cy+newH//2, cx-newW//2:cx+newW//2] = img1 # FIX THIS
        #img[0:500, 0:402] = img1
    except:
        pass
    
    cv2.imshow("Image", img) 
    cv2.waitKey(1) 
    key = cv2.waitKey(1) & 0xFF
    if key == 27:
        break

