#INSTRUCTIONS (and clarifications):
    #check all variables (that should be constant but I don't care enough to change it) before the "master = Tk()" line
    #draw box around ENTIRE object, BE ACCURATE
    #truncated is if the object is partially off-screen.
    #2 modes: standard click-and-drag to create/modify boxes or keyboard.  Keyboard is type 1-9 (index of box to select), then type wasd(slider of selected box; w is top, a is left, s is bottom, d is right), then use arrow keys to modify box.  Keyboard is only for modifying.
    #MUST CLICK SAVE, save and next also saves
    #program quits if the picture is not found (if txt file not found it wll be generated)

#IF YOU ARE GETTING AN ERROR, common causes are:
    #imports are wrong or programs imported don't exist
    #picend variable incorrect
    #file number entered incorrect
    #fileDigits variable incorrect
    #paths incorrect
    #program has crashed because Kaylia is a bug-magnet

#NEED: PIL(Pillow) and python2, (python3 version of labellingtool not out yet: sorry everyone)
from __future__ import with_statement
from Tkinter import *
import os, os.path
import sys
from PIL import Image, ImageTk, ImageDraw, ImageFont

startpoint = raw_input("text file to open?")
filename = startpoint

picend = ".jpg" #jpg or png???
txtend = ".txt"

#IMPORTANT NOTE: hard code these 5 lines
directory = "/Users/kaylee/Desktop/ideas_to_test/robotFiles/" #pic folder
fdirectory = "/Users/kaylee/Desktop/ideas_to_test/rfTxt/" #file folders
filenameDigits = 5 #depends on pic file names, ex: 12 will open 00012 if filenameDigits is 5
standardLabelledType = "cube" #MAKE SURE MATCHES with all the other data of dataset, check with Grace, case matters
minBoxSize = 20 #DO NOT EDIT THIS unless there is a tiny box less than 20 pix; pix vertical and horizontal (original draw)
keyboardAccuracy = 5 #num pixels skip over from Keyboard mode when moving edges of bounding box

#AND STOP EDITING THE CODE NOW

#initializing main frame
master = Tk()
master.title("SC: Labelling Tool (that needs debugging, I'll get around to it sometime)")
topFrame = Frame(master)
bottomFrame = Frame(master)
topFrame.pack(side=TOP)
bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=True)

#variables
canvas_width = canvas_height = 0
startX = startY = None #for creating boxes
boxes = [] #saving box objects
creatingBoxMode = False
creatingRect = None #temp holding cell
frames = [] #for columns of checkbuttons
selectedBoxIndex = -1 #nothing important until sliders
selectedSlider = None
currentOpenImage = None

#variables for keyboard mode
mode2selectedBox  = 0 #interactive
mode2selectedSlider = ''

def arrangeCheckButtons():
    global boxes
    currentFrameColumn = 0
    for i in range(len(boxes)):
        if boxes[i] == None:
            continue
        isTruncated = boxes[i].truncatedCheckBox.var.get() == 1
        boxes[i].truncatedCheckBox.destroy()
        boxes[i].truncatedCheckBox = Checkbutton(master, text = str(i+1) + " truncated?", variable = boxes[i].truncated)
        boxes[i].truncatedCheckBox.var = boxes[i].truncated
        boxes[i].truncatedCheckBox.pack(in_=columnFrames[currentFrameColumn], side = TOP)
        currentFrameColumn += 1
        if isTruncated:
            boxes[i].truncatedCheckBox.select()
class Box: #keep track of box and all correlating objects
    halfSliderWidth = 5
    def __init__(self, minX, minY, maxX, maxY, rectOutlineObj, isTruncated, identifier, type):
        self.rectOutlineObj = rectOutlineObj
        self.type = type #not used, yet
        
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY
        print("created box at: "+ str(self.minX)+" " + str(self.minY) + " " + str(self.maxX) + " " + str(self.maxY))
        
        self.truncated = IntVar()
        #1 if selected, 0 otherwise
        self.truncatedCheckBox = Checkbutton(master, text = str(identifier) + " truncated?", variable = self.truncated)
        self.truncatedCheckBox.var = self.truncated
        
        count = 0
        for i in range(len(boxes)):
            if boxes[i] == None:
                continue
            count += 1;
        for i in range(len(columnFrames)):
            if (count+1)%len(columnFrames) == 0:
                self.truncatedCheckBox.pack(in_=columnFrames[len(columnFrames)-1], side = TOP)
                break
            elif (count+1)%len(columnFrames) == i:
                self.truncatedCheckBox.pack(in_=columnFrames[i-1], side = TOP)
                break
        self.truncatedCheckBox.bind()
        if isTruncated:
            self.truncatedCheckBox.select()
        
        self.leftSlider = canvas.create_rectangle(self.minX-Box.halfSliderWidth, (self.minY+self.maxY)/2-Box.halfSliderWidth, self.minX+Box.halfSliderWidth, (self.minY+self.maxY)/2+Box.halfSliderWidth, activefill = "cyan", outline = "cyan", tags = ("leftSlider",str(identifier)))
        self.rightSlider = canvas.create_rectangle(self.maxX-Box.halfSliderWidth, (self.minY+self.maxY)/2-Box.halfSliderWidth, self.maxX+Box.halfSliderWidth, (self.minY+self.maxY)/2+Box.halfSliderWidth, activefill = "cyan", outline = "cyan", tags = ("rightSlider",str(identifier)))
        self.topSlider = canvas.create_rectangle((self.minX+self.maxX)/2-Box.halfSliderWidth, self.minY-Box.halfSliderWidth, (self.minX+self.maxX)/2+Box.halfSliderWidth,self.minY+Box.halfSliderWidth, activefill = "cyan", outline = "cyan", tags = ("topSlider",str(identifier)))
        self.bottomSlider = canvas.create_rectangle((self.minX+self.maxX)/2-Box.halfSliderWidth, self.maxY-Box.halfSliderWidth, (self.minX+self.maxX)/2+Box.halfSliderWidth,self.maxY+Box.halfSliderWidth,activefill = "cyan", outline = "cyan", tags = ("bottomSlider",str(identifier)))
        self.text = canvas.create_text(self.minX+20, self.minY+20, text = str(identifier), fill = "cyan", font = ("Times", 30, "bold"))
        self.deleteButton = canvas.create_rectangle((((self.minX+self.maxX)/2-8),((self.minY+self.maxY)/2-8)),(((self.minX+self.maxX)/2+8),((self.minY+self.maxY)/2+8)),outline = "red", activefill = "red", tags = ("deleteButton",str(identifier)))
    def moveLeftSlider(self, to):
        txtCoords = canvas.coords(self.text)
        canvas.coords(self.rectOutlineObj, to, self.minY, self.maxX, self.maxY)
        canvas.coords(self.leftSlider, to-Box.halfSliderWidth, (self.minY+self.maxY)/2-Box.halfSliderWidth, to+Box.halfSliderWidth, (self.minY+self.maxY)/2+Box.halfSliderWidth)
        canvas.coords(self.topSlider, (to+self.maxX)/2-Box.halfSliderWidth, self.minY-Box.halfSliderWidth, (to+self.maxX)/2+Box.halfSliderWidth,self.minY+Box.halfSliderWidth)
        canvas.coords(self.bottomSlider, (to+self.maxX)/2-Box.halfSliderWidth, self.maxY-Box.halfSliderWidth, (to+self.maxX)/2+Box.halfSliderWidth,self.maxY+Box.halfSliderWidth)
        canvas.coords(self.deleteButton,(to+self.maxX)/2-8,(self.minY+self.maxY)/2-8,(to+self.maxX)/2+8,(self.minY+self.maxY)/2+8)
        if to > self.maxX:
            canvas.move(self.text,(self.maxX+20)-txtCoords[0],0)
        else:
            canvas.move(self.text,(to+20)-txtCoords[0],0)
    def moveRightSlider(self, to):
        txtCoords = canvas.coords(self.text)
        canvas.coords(self.rectOutlineObj, self.minX, self.minY, to, self.maxY)
        canvas.coords(self.rightSlider, to-Box.halfSliderWidth, (self.minY+self.maxY)/2-Box.halfSliderWidth, to+Box.halfSliderWidth, (self.minY+self.maxY)/2+Box.halfSliderWidth)
        canvas.coords(self.topSlider, (self.minX+to)/2-Box.halfSliderWidth, self.minY-Box.halfSliderWidth, (self.minX+to)/2+Box.halfSliderWidth,self.minY+Box.halfSliderWidth)
        canvas.coords(self.bottomSlider, (self.minX+to)/2-Box.halfSliderWidth, self.maxY-Box.halfSliderWidth, (self.minX+to)/2+Box.halfSliderWidth,self.maxY+Box.halfSliderWidth)
        canvas.coords(self.deleteButton,(self.minX+to)/2-8,(self.minY+self.maxY)/2-8,(self.minX+to)/2+8,(self.minY+self.maxY)/2+8)
        if to > self.minX:
            canvas.move(self.text,(self.minX+20)-txtCoords[0],0)
        else:
            canvas.move(self.text,(to+20)-txtCoords[0],0)
    def moveTopSlider(self, to):
        txtCoords = canvas.coords(self.text)
        canvas.coords(self.rectOutlineObj, self.minX, event.y, self.maxX, self.maxY)
        canvas.coords(self.topSlider, (self.minX+self.maxX)/2-Box.halfSliderWidth, event.y-Box.halfSliderWidth, (self.minX+self.maxX)/2+Box.halfSliderWidth,event.y+Box.halfSliderWidth)
        canvas.coords(self.rightSlider, self.maxX-Box.halfSliderWidth, (event.y+self.maxY)/2-Box.halfSliderWidth, self.maxX+Box.halfSliderWidth, (event.y+self.maxY)/2+Box.halfSliderWidth)
        canvas.coords(self.leftSlider, self.minX-Box.halfSliderWidth, (event.y+self.maxY)/2-Box.halfSliderWidth, self.minX+Box.halfSliderWidth, (event.y+self.maxY)/2+Box.halfSliderWidth)
        canvas.coords(self.deleteButton,(self.minX+self.maxX)/2-8,(event.y+self.maxY)/2-8,(self.minX+self.maxX)/2+8,(event.y+self.maxY)/2+8)
        if event.y > self.maxY:
            canvas.move(self.text,0,(self.maxY+20)-txtCoords[1])
        else:
            canvas.move(self.text,0,(event.y+20)-txtCoords[1])
    def moveBottomSlider(self, to):
        txtCoords = canvas.coords(self.text)
        canvas.coords(self.rectOutlineObj, self.minX, self.minY, self.maxX, event.y)
        canvas.coords(self.bottomSlider, (self.minX+self.maxX)/2-Box.halfSliderWidth, event.y-Box.halfSliderWidth, (self.minX+self.maxX)/2+Box.halfSliderWidth,event.y+Box.halfSliderWidth)
        canvas.coords(self.rightSlider, self.maxX-Box.halfSliderWidth, (self.minY+event.y)/2-Box.halfSliderWidth, self.maxX+Box.halfSliderWidth, (self.minY+event.y)/2+Box.halfSliderWidth)
        canvas.coords(self.leftSlider, self.minX-Box.halfSliderWidth, (self.minY+event.y)/2-Box.halfSliderWidth, self.minX+Box.halfSliderWidth, (self.minY+event.y)/2+Box.halfSliderWidth)
        canvas.coords(self.deleteButton,(self.minX+self.maxX)/2-8,(self.minY+event.y)/2-8,(self.minX+self.maxX)/2+8,(self.minY+event.y)/2+8)
        if event.y > self.minY:
            canvas.move(self.text,0,(self.minY+20)-txtCoords[1])
        else:
            canvas.move(self.text,0,(event.y+20)-txtCoords[1])
def inOrder(num1, num2):
    if num2 < num1:
        return (num2, num1)
    return (num1, num2)
def boxBoundsChecker(x1, y1, x2, y2):
    if x1 < 0:
        x1 = 0
    if x2 > canvas_width:
        x2 = canvas_width
    if y1 < 0:
        y1 = 0
    if y2 > canvas_height:
        y2 = canvas_height
    return (x1, y1, x2, y2)
def readFile():
    global boxes
    global creatingRect
    print("Reading a file.")
    with open(fdirectory+filename+txtend) as openedFile: #Here
        for line in openedFile:
            fileData = line.split(" ")
            print fileData
            truncatedArg = False
            if float(fileData[1]) == 1.0:
                truncatedArg = True
            xmin = float(fileData[4])
            ymin = float(fileData[5])
            xmax = float(fileData[6])
            ymax = float(fileData[7])
            (xmin, xmax) = inOrder(xmin, xmax)
            (ymin, ymax) = inOrder(ymin, ymax)
            creatingRect = canvas.create_rectangle(xmin, ymin, xmax, ymax, outline = "cyan")
            boxes.append(Box(xmin, ymin, xmax, ymax, creatingRect, truncatedArg, len(boxes)+1, fileData[0]))
            creatingRect = None
            print("Read box at: "+ str(boxes[selectedBoxIndex].minX)+ " " + str(boxes[selectedBoxIndex].minY)+ " " + str(boxes[selectedBoxIndex].maxX)+" "+ str(boxes[selectedBoxIndex].maxY))
    openedFile.close()
def fixFilenameDigits():
    global filename
    filename = filename.zfill(filenameDigits) #filename = '{:05d}'.format(filename)
def checkValidFilenames():
    print("your filename identification digits is: "+str(filenameDigits))
    if os.path.isfile(directory+filename+picend):
        print("picture exists")
        if os.path.isfile(fdirectory+filename+txtend):
            print("txt file exists")
            return True
        else:
            print("txt file does not exist, creating new txt file: "+filename+txtend)
            open(fdirectory+filename+txtend, "w+").close()
            return False
    else:
        print("ERROR: PICTURE OF FILENAME DOES NOT EXIST, why the gecko are you using this program")
        sys.exit() #kill program
def openPhoto():
    return Image.open(directory+filename+picend)
def configCanvas(photo):
    global canvas_width
    global canvas_height
    canvas_width = photo.size[0]
    canvas_height = photo.size[1]
    canvas.config(width = canvas_width, height = canvas_height)
def decimateABox(deletedBoxIndex):
    global boxes
    canvas.delete(boxes[deletedBoxIndex].rectOutlineObj)
    canvas.delete(boxes[deletedBoxIndex].text)
    canvas.delete(boxes[deletedBoxIndex].leftSlider)
    canvas.delete(boxes[deletedBoxIndex].rightSlider)
    canvas.delete(boxes[deletedBoxIndex].topSlider)
    canvas.delete(boxes[deletedBoxIndex].bottomSlider)
    canvas.delete(boxes[deletedBoxIndex].deleteButton)
    boxes[deletedBoxIndex].truncatedCheckBox.destroy()
    boxes[deletedBoxIndex] = None
    arrangeCheckButtons() #inefficient when deleting all boxes TODO: find solution
def wipe():
    global boxes
    for i in range(len(boxes)):
        decimateABox(i) #dunno if optimal, don't need to arrange checkbuttons if destroying all
    boxes = []
def save():
    global boxes
    print("Saving info")
    openedFile = open(fdirectory+filename+txtend, "w")
    for i in range(len(boxes)):
        if boxes[i] == None:
            print("found dead object")
            continue
        #xmin / xmax, ymin / ymax should be in order
        openedFile.write(standardLabelledType+" "+str(boxes[i].truncatedCheckBox.var.get())+".0 0 0.0 "+str(boxes[i].minX)+" "+str(boxes[i].minY)+" "+str(boxes[i].maxX)+" "+str(boxes[i].maxY)+" 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 \n")
    openedFile.close()
def saveAndChangeFile(changingNum):
    global filename
    global currentOpenImage
    global img
    global canvas
    print("Saving and moving on")
    save()
    wipe()
    canvas.delete(currentOpenImage)
    filename = str(((int)(filename))+changingNum)
    fixFilenameDigits()
    fileExists = checkValidFilenames()
    photo = Image.open(directory+filename+picend)
    img = ImageTk.PhotoImage(photo)
    currentOpenImage = canvas.create_image(0,0,anchor="nw",image =img)
    configCanvas(photo)
    photo.close()
    if fileExists:
        readFile()
def saveAndNext():
    saveAndChangeFile(1)
def saveAndPrevious():
    saveAndChangeFile(-1)
def createBox():
    global creatingBoxMode
    print("creating box mode is ON")
    creatingBoxMode = True

def mode2select(object):
    canvas.itemconfig(object, outline = 'blue')
def keyboardPress(event):
    global mode2selectedBox
    global mode2selectedSlider
    
    if (str(event.char).isdigit()) & (event.char != '0'):
        if mode2selectedBox != 0:
            canvas.itemconfig(boxes[mode2selectedBox-1].rectOutlineObj, outline = 'cyan')
        print(event.char)
        keyClicked = (int)(event.char)
        if len(boxes) >= keyClicked:
            if boxes[keyClicked-1] != None:
                print("mode switched to 2")
                if mode2selectedBox != 0:
                    canvas.itemconfig(boxes[mode2selectedBox-1].rectOutlineObj, outline = 'cyan')
                mode2selectedBox = keyClicked
                mode2select(boxes[mode2selectedBox-1].rectOutlineObj)
            else:
                print("cannot select: box no longer exists")
    elif mode2selectedBox != 0:
        if mode2selectedSlider != '':
            if mode2selectedSlider == 'w':
                canvas.itemconfig(boxes[mode2selectedBox-1].topSlider, outline = 'cyan')
            elif mode2selectedSlider == 'a':
                canvas.itemconfig(boxes[mode2selectedBox-1].leftSlider, outline = 'cyan')
            elif mode2selectedSlider == 's':
                canvas.itemconfig(boxes[mode2selectedBox-1].bottomSlider, outline = 'cyan')
            else: # 'd'
                canvas.itemconfig(boxes[mode2selectedBox-1].rightSlider, outline = 'cyan')
        mode2selectedSlider = event.char
        if event.char == 'w':
            mode2select(boxes[mode2selectedBox-1].topSlider)
        elif event.char == 'a':
            mode2select(boxes[mode2selectedBox-1].leftSlider)
        elif event.char == 's':
            mode2select(boxes[mode2selectedBox-1].bottomSlider)
        elif event.char == 'd':
            mode2select(boxes[mode2selectedBox-1].rightSlider)
        else:
            mode2selectedSlider = ''

def leftClick(event):
    global boxes
    
    if (mode2selectedBox != 0) & ((mode2selectedSlider == 'a') | (mode2selectedSlider == 'd')):
        if mode2selectedSlider == 'a':
            boxes[mode2selectedBox-1].minX = boxes[mode2selectedBox-1].minX - keyboardAccuracy
            boxes[mode2selectedBox-1].moveLeftSlider(boxes[mode2selectedBox-1].minX) #redraw
        else:
            boxes[mode2selectedBox-1].maxX = boxes[mode2selectedBox-1].maxX - keyboardAccuracy
            boxes[mode2selectedBox-1].moveRightSlider(boxes[mode2selectedBox-1].maxX) #redraw
def rightClick(event):
    if (mode2selectedBox != 0) & ((mode2selectedSlider == 'a') | (mode2selectedSlider == 'd')):
        if mode2selectedSlider == 'a':
            boxes[mode2selectedBox-1].minX = boxes[mode2selectedBox-1].minX + keyboardAccuracy
            boxes[mode2selectedBox-1].moveLeftSlider(boxes[mode2selectedBox-1].minX) #redraw
        else:
            boxes[mode2selectedBox-1].maxX = boxes[mode2selectedBox-1].maxX + keyboardAccuracy
            boxes[mode2selectedBox-1].moveRightSlider(boxes[mode2selectedBox-1].maxX) #redraw
def upClick(event):
    if (mode2selectedBox != 0) & ((mode2selectedSlider == 'w') | (mode2selectedSlider == 's')):
        if mode2selectedSlider == 'w':
            boxes[mode2selectedBox-1].minY = boxes[mode2selectedBox-1].minY - keyboardAccuracy
            boxes[mode2selectedBox-1].moveTopSlider(boxes[mode2selectedBox-1].minY) #redraw
        else:
            boxes[mode2selectedBox-1].maxY = boxes[mode2selectedBox-1].maxY - keyboardAccuracy
            boxes[mode2selectedBox-1].moveBottomSlider(boxes[mode2selectedBox-1].maxY) #redraw
def downClick(event):
    if (mode2selectedBox != 0) & ((mode2selectedSlider == 'w') | (mode2selectedSlider == 's')):
        if mode2selectedSlider == 'w':
            boxes[mode2selectedBox-1].minY = boxes[mode2selectedBox-1].minY + keyboardAccuracy
            boxes[mode2selectedBox-1].moveTopSlider(boxes[mode2selectedBox-1].minY) #redraw
        else:
            boxes[mode2selectedBox-1].maxY = boxes[mode2selectedBox-1].maxY + keyboardAccuracy
            boxes[mode2selectedBox-1].moveBottomSlider(boxes[mode2selectedBox-1].maxY) #redraw

def buttonPress(event):
    global startY
    global startX
    global creatingRect
    global selectedBoxIndex
    global selectedSlider
    global mode2selectedBox
    
    print("button pressed")
    if mode2selectedBox != 0:
        print("mode switched to 1")
        canvas.itemconfig(boxes[mode2selectedBox-1].rectOutlineObj, outline = 'cyan')
        if mode2selectedSlider != '':
            if mode2selectedSlider == 'w':
                canvas.itemconfig(boxes[mode2selectedBox-1].topSlider, outline = 'cyan')
            elif mode2selectedSlider == 'a':
                canvas.itemconfig(boxes[mode2selectedBox-1].leftSlider, outline = 'cyan')
            elif mode2selectedSlider == 's':
                canvas.itemconfig(boxes[mode2selectedBox-1].bottomSlider, outline = 'cyan')
            else: # 'd'
                canvas.itemconfig(boxes[mode2selectedBox-1].rightSlider, outline = 'cyan')
        mode2selectedBox = 0
    
    if creatingBoxMode: #TODO: max out if click offscreen, unlikely but check anyway
        startX = event.x
        startY = event.y
        creatingRect = canvas.create_rectangle(startX, startY, startX+1, startY+1, outline="cyan")
        return
    #check if click significant
    clickedItem = canvas.find_closest(event.x, event.y)
    thisTag = canvas.itemcget(clickedItem, "tags") #string:[slider] [box index] current
    if "Slider" in thisTag:
        print("I am a slider")
        thisTagArray = thisTag.split(" ")
        selectedBoxIndex = ((int)(thisTagArray[1]))-1 #arr counts from 0, identifier counts from 1
        selectedSlider = thisTagArray[0]
        print(str(boxes[selectedBoxIndex].minX)+ " " + str(boxes[selectedBoxIndex].minY)+ " " + str(boxes[selectedBoxIndex].maxX)+" "+ str(boxes[selectedBoxIndex].maxY))
    elif "deleteButton" in thisTag:
        print("DELETED!")
        thisTagArray = thisTag.split(" ")
        deletedBoxIndex = ((int)(thisTagArray[1]))-1
        decimateABox(deletedBoxIndex)

def movePress(event):
    global creatingRect
    global boxes
    
    print("button moved")
    if creatingBoxMode:
        canvas.coords(creatingRect, startX, startY, event.x, event.y)
        #Check Valid Values: print (str(startX) + " " + str(startY) + " " + str(event.x) + " " + str(event.y))
    elif selectedBoxIndex >= 0:
        if selectedSlider == "leftSlider":
            boxes[selectedBoxIndex].moveLeftSlider(event.x)
        elif selectedSlider == "rightSlider":
            boxes[selectedBoxIndex].moveRightSlider(event.x)
        elif selectedSlider == "topSlider":
            boxes[selectedBoxIndex].moveTopSlider(event.y)
        else: #bottom
            boxes[selectedBoxIndex].moveBottomSlider(event.y)

def buttonRelease(event):
    global creatingRect
    global creatingBoxMode
    global selectedBoxIndex
    global selectedSlider
    global boxes
    
    print("button released")
    if creatingBoxMode:
        (x1, y1, x2, y2) = canvas.coords(creatingRect)
        print abs(x1-x2)
        print abs(y1-y2)
        print minBoxSize
        if (abs(x1-x2) < minBoxSize) | (abs(y1-y2) < minBoxSize):
            print("ERROR: Box size is less than " + str(minBoxSize) + " pixels.  Cancelled.")
            canvas.delete(creatingRect)
            creatingRect = None
            creatingBoxMode = False
            return
        
        (x1, x2) = inOrder(x1, x2)
        (y1, y2) = inOrder(y1, y2)
        (x1, y1, x2, y2) = boxBoundsChecker(x1,y1,x2,y2) #bit messy, start good order, get messed up by dragging (maybe), end good order
        boxes.append(Box(x1, y1, x2, y2, creatingRect, False, len(boxes)+1, standardLabelledType))
    elif selectedBoxIndex >= 0:
        if selectedSlider == "leftSlider":
            curX = event.x
            if curX < 0:
                curX = 0
            elif curX > canvas_width:
                curX = canvas_width
            boxes[selectedBoxIndex].minX = float(curX)
            (boxes[selectedBoxIndex].minX, boxes[selectedBoxIndex].maxX) = inOrder(boxes[selectedBoxIndex].minX, boxes[selectedBoxIndex].maxX)
        elif selectedSlider == "rightSlider":
            curX = event.x
            if curX < 0:
                curX = 0
            elif curX > canvas_width:
                curX = canvas_width
            boxes[selectedBoxIndex].maxX = float(curX)
            (boxes[selectedBoxIndex].minX, boxes[selectedBoxIndex].maxX) = inOrder(boxes[selectedBoxIndex].minX, boxes[selectedBoxIndex].maxX)
        elif selectedSlider == "topSlider":
            curY = event.y
            if curY < 0:
                curY = 0
            elif curY > canvas_width:
                curY = canvas_width
            boxes[selectedBoxIndex].minY = float(curY)
            (boxes[selectedBoxIndex].minY, boxes[selectedBoxIndex].maxY) = inOrder(boxes[selectedBoxIndex].minY, boxes[selectedBoxIndex].maxY)
        elif selectedSlider == "bottomSlider": #else, but checking just in case
            curY = event.y
            if curY < 0:
                curY = 0
            elif curY > canvas_width:
                curY = canvas_width
            boxes[selectedBoxIndex].maxY = float(curY)
            (boxes[selectedBoxIndex].minY, boxes[selectedBoxIndex].maxY) = inOrder(boxes[selectedBoxIndex].minY, boxes[selectedBoxIndex].maxY)
        print(str(boxes[selectedBoxIndex].minX)+ " " + str(boxes[selectedBoxIndex].minY)+ " " + str(boxes[selectedBoxIndex].maxX)+" "+ str(boxes[selectedBoxIndex].maxY))
    selectedBoxIndex = -1
    selectedSlider = None
    creatingRect = None
    creatingBoxMode = False

#check if pic exists
fixFilenameDigits()
fileExists = checkValidFilenames()

#canvas and initial photo opening
photo = openPhoto()
canvas = Canvas(master, width = photo.size[0], height = photo.size[1], cursor = "cross")
configCanvas(photo)
canvas.pack(side = "top", fill = "both", expand = True)
img = ImageTk.PhotoImage(photo)
photo.close()

#load image
currentOpenImage = canvas.create_image(0,0,anchor="nw",image =img)

#create parallel frames to hold checkboxes
columnFrames = []
for i in range(((int)(canvas_width))/120):    #TODO: FIX DEPENDING ON PIC SIZE, should be fine??
    columnFrames.append(Frame(bottomFrame))
    columnFrames[len(columnFrames)-1].pack(side = LEFT)

#load file data from previous labelling
if fileExists:
    readFile()
print len(boxes)

#buttons
Button(master, text = 'save and next file', command = saveAndNext).pack(in_=topFrame, side = RIGHT)
Button(master, text = 'save and previous file', command = saveAndPrevious).pack(in_=topFrame, side = LEFT)
Button(master, text = 'save', command = save).pack(in_=topFrame)
Button(master, text = 'create box', command = createBox).pack(in_=topFrame)

#add events
master.bind("<KeyPress>", keyboardPress)
master.bind("<Left>", leftClick)
master.bind("<Right>", rightClick)
master.bind("<Up>", upClick)
master.bind("<Down>", downClick)
canvas.bind("<ButtonPress-1>", buttonPress)
canvas.bind("<B1-Motion>", movePress)
canvas.bind("<ButtonRelease-1>", buttonRelease)

master.mainloop()
