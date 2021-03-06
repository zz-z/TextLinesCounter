import numpy as np
import cv2
import os 
#----------------------------------------------------------------
def Rotate(image):
    #http://www.pyimagesearch.com/2017/02/20/text-skew-correction-opencv-python/
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)

    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    coords = np.column_stack(np.where(thresh > 0))
    angle = cv2.minAreaRect(coords)[-1]
     
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
        
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h),	flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated
#----------------------------------------------------------------
def Obfuscate(image):
    kernel = np.ones((5,20), np.uint8)
    ret,transformed = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY) #Make image black and white
    transformed = cv2.erode(transformed, kernel, iterations = 4) #best if 3-4
    transformed = cv2.dilate(transformed, kernel, iterations = 3) #http://docs.opencv.org/2.4/doc/tutorials/imgproc/erosion_dilatation/erosion_dilatation.html
    
    # ^ is better
    """
    #blur = cv2.blur(image, (200,1)) 
    
    kernel = np.ones((1,5), np.uint8)
    image = cv2.erode(blur, kernel, iterations = 3) #5

    kernel = np.ones((5,5), np.uint8)
    image = cv2.erode(blur, kernel, iterations = 3) #5

    ret,transformed = cv2.threshold(image, 200, 255, cv2.THRESH_BINARY)
    """
    return transformed
#----------------------------------------------------------------
def SaveFile(path, transformed):
    filePath = path[0:path.rfind('.')]
    extension = path[path.rfind('.')+1:]
    cv2.imwrite(filePath + "-transformed." + extension,transformed)
#----------------------------------------------------------------
def main(path): 
    image = cv2.imread(path)
    rotated = Rotate(image)
    transformed = cv2.cvtColor(rotated, cv2.COLOR_BGR2GRAY);
    transformed = Obfuscate(transformed)
    
    SaveFile(path, transformed) #totally optional
    
    x=0
    y=0
    z=0
    numberOfColorChanges=0;
    previousColor=transformed[0,0];
    highestNumberOfColorChange=0;
    while(x<transformed.shape[0]):
        while(y<transformed.shape[1]):      
            try:   
                if transformed[y,x]!=previousColor: #if previous color was white, and now is black, count that as color change
                    previousColor=transformed[y,x]
                    numberOfColorChanges+=1     
            except:
                pass
            y=y+1
        x+=1 #increase to x+=10 for a greater speed, but lower accuracy
        y=0
        if numberOfColorChanges>highestNumberOfColorChange:
            highestNumberOfColorChange=numberOfColorChanges
        numberOfColorChanges=0
    return highestNumberOfColorChange/2 #If image is white-black text-white that would count as 2 changes of color, hence we divide with 2
#------------------------------------------------------------------------------------
path = raw_input()
totalImages=0
correctImages=0
if os.path.isfile(path):
    count = main(path)
    print "Found " + str(count) + " lines"
    #You can also check a solution read from .out file
else:  
    for root, subFolders, files in os.walk(path):  #recursively finds all files in a given folder
        for file in files:  
            if file[file.rfind('.'):]!=".out":
                print "---- ----"
                print file
                totalImages+=1
                count = main(os.path.join(path, file))
                solutionPath = os.path.join(path,file[0:file.rfind(".")] + ".out") #Read a correct answer from a file named "z.out", if image is name "z.png"
                solution = open(solutionPath).read()
                print str(count) + "/" + str(solution)
                if count==int(solution):           
                    #print "Correct"
                    print "\x1b[6;30;42m" + " Correct" + "\x1b[0m" #Colored, doesn't work in CMD
                    correctImages+=1
                else:                   
                    #print "Wrong!"
                    print "\x1b[6;30;41m" + " Wrong" + "\x1b[0m" 
                   
    print "\nNumber of correct guesses: "
    print str(correctImages) + "/" + str(totalImages)