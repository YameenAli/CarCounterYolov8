from ultralytics import YOLO
import cv2
import cvzone
import math
from sort import *

# accessing webcam

# cap = cv2.VideoCapture(1)  # For Webcam
# cap.set(3, 1280)
# cap.set(4, 720)

cap = cv2.VideoCapture("../Videos/cars.mp4")  # For Video

# creating YOLO model
model = YOLO("../Yolo-Weights/yolov8n.pt")

classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]

# importing mask file for masking car video specific region for detection not a whole screen
mask = cv2.imread("mask.png")

# Tracking
tracker = Sort(max_age=20, min_hits=3,iou_threshold=0.3)

limits = [400,297,673,297]      #  set the x1,h,x2,h for the line
totalCount = []   # empty list to store count values

while True:
    success, img = cap.read()       # make mask overlayed above original input video using bitwise and operation
    imgRegion = cv2.bitwise_and(img, mask)

    # for graphics set graphic file
    imgGraphic = cv2.imread("graphics.png",cv2.IMREAD_UNCHANGED)
    img = cvzone.overlayPNG(img,imgGraphic,(0,0))


    results = model(imgRegion, stream=True)      # finding results with yolo

    detections = np.empty((0,5))  # make empty numpy list

    for r in results:     # now for bounding boxes we loop the results
        boxes = r.boxes
        for box in boxes:

            # Bounding Box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

            # cv2.rectangle(img, (x1,y1), (x2,y2), (255,0,255))   # for simple rectangle
            w, h = x2-x1, y2-y1  # for fancy rectangle around object using cvzone
            # cvzone.cornerRect(img,(x1,y1,w,h),l=15)

            conf = math.ceil((box.conf[0]*100))/100 # seeing confidence score
            print(conf)
            # cvzone.putTextRect(img,f'{conf}',(max(0,x1),max(35,y1)))

            # Class Name
            cls  = int(box.cls[0])
            currentClass = classNames[cls]

            if currentClass == "car" or currentClass == "motorbike" or currentClass == "truck"  or currentClass == "bus" and conf >0.3:
                # cvzone.putTextRect(img,f'{currentClass} {conf}',(max(0,x1),max(35,y1)),scale=1,thickness=1,offset=3)
                # cvzone.cornerRect(img,(x1,y1,w,h),l=15, rt=5)
                currentArray = np.array([x1,y1,x2,y2,conf])    # we have to store all the detecions in an array/list - here we use numpy array
                detections = np.vstack((detections,currentArray))      # In list we use append but in numpy array we use vertical stack


    resultsTracker = tracker.update(detections)     # update tracker detections

    cv2.line(img,(limits[0],limits[1]),(limits[2],limits[3]),(0,0,255),3)

    for result in resultsTracker:   # tracker
        x1, y1, x2, y2, id = result
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        print(result)
        w, h = x2 - x1, y2 - y1
        cvzone.cornerRect(img, (x1, y1, w, h), l=9, rt=2, colorR=(255, 0, 255))
        cvzone.putTextRect(img, f' {int(id)}', (max(0, x1), max(35, y1)),
                           scale=2, thickness=3, offset=10)

        cx,cy = x1+w//2 , y1+h//2       # set mid point on the detected object
        cv2.circle(img,(cx,cy),5,(255,0,255),cv2.FILLED)  # show filled circle

        if limits[0] < cx < limits[2] and limits[1] - 15 < cy < limits[1] + 15:     # check if midpoint touch the line
            if totalCount.count(id) == 0:  # checks if the di exists (if yes than no count added to list)
                totalCount.append(id)
                cv2.line(img, (limits[0], limits[1]), (limits[2], limits[3]), (0, 255, 0), 3)


    # cvzone.putTextRect(img, f' Count: {len(totalCount)}', (50,50))  # counter text
    cv2.putText(img,str(len(totalCount)),(255,100),cv2.FONT_HERSHEY_PLAIN,5,(255,50,255),8)



    cv2.imshow("image", img)
    # cv2.imshow("imageRegion",imgRegion)
    cv2.waitKey(1)
