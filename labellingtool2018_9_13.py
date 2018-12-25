#INSTRUCTIONS (and clarifications):
    #check all variables (that should be constant but I don't care enough to change it) before the "master = Tk()" line
    #draw box around ENTIRE object, BE ACCURATE
    #truncated is if the object is partially off-screen.
    #2 modes: Regular and Keyboard
        #standard click-and-drag to create/modify boxes or keyboard.
        #Keyboard is type 1-9 (index of box to select), then type wasd(slider of selected box; w is top, a is left, s is bottom, d is right), then use arrow keys to modify box.  Keyboard is only for modifying.
    #MUST CLICK SAVE, save and next also saves
    #program quits if the picture file is not found (if text file not found it wll be generated)

#IF YOU ARE GETTING AN ERROR, common causes are:
    #imports are wrong or programs imported don't exist
    #picend variable invalid
    #file number entered invalid
    #fileDigits variable invalid
    #paths incorrect - should be specific to each computer

#DEPENDENCIES: PIL(Pillow) and python 2 (comes with Tkinter), (python 3 coming soon)
from __future__ import with_statement
from Tkinter import *
import os, os.path
import sys
from PIL import Image, ImageTk, ImageDraw, ImageFont

startpoint = raw_input("text file to open?")
filename = startpoint

picend = ".jpg" #jpg or png
txtend = ".txt"

#IMPORTANT NOTE: hard code these 5 lines
directory = "/Users/kaylee/Desktop/ideas_to_test/robotFiles/" #picture folder path
fdirectory = "/Users/kaylee/Desktop/ideas_to_test/rfTxt/" #file folders path
filenameDigits = 5 #picture file names, ex: 12 will open 00012 if filenameDigits is 5
standardLabelledType = "cube" #ENSURE MATCHES with all other types of the dataset, case matters
minBoxSize = 20 #DO NOT EDIT unless there is an object less than 20 pix vertically and horizontally
keyboardAccuracy = 5 #num pixels skip over from Keyboard mode when moving edges of bounding box
#STOP EDITING THE CODE

#initialize main frame
master = Tk()
master.title("Space Cookies: Neural Network Labeling Tool")
topFrame = Frame(master)
bottomFrame = Frame(master)
topFrame.pack(side=TOP)
bottomFrame.pack(side=BOTTOM, fill=BOTH, expand=True)

#initialize variables
canvas_width = canvas_height = 0
startX = startY = None #first coordinate for creating bounding box
boxes = [] #saving box objects
creatingBoxMode = False
creatingRect = None #temperary box object, not added to boxes array until verified box as valid
frames = [] #one frame per column of checkbuttons (for whether each object is truncated)
selectedBoxIndex = -1
selectedSlider = None
currentOpenImage = None

#initialize variables for Keyboard Mode
mode2selectedBox  = 0 #interactive
mode2selectedSlider = ''

#reorganize checkbuttons on frames after one is deleted, so there is no blank spaces
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

#Bounding Box
class Box:

    #static variables
    halfSliderWidth = 5

    #-----------------------constructor-------------------------
    def __init__(self, minX, minY, maxX, maxY, rectOutlineObj, isTruncated, identifier, type):
        self.rectOutlineObj = rectOutlineObj #rectangle drawn on screen
        self.type = type

        #bounding box coordinates
        self.minX = minX
        self.minY = minY
        self.maxX = maxX
        self.maxY = maxY
        print("created box at: "+ str(self.minX)+" " + str(self.minY) + " " + str(self.maxX) + " " + str(self.maxY))

        #truncated variable and checkbutton object
        self.truncated = IntVar()
        self.truncatedCheckBox = Checkbutton(master, text = str(identifier) + " truncated?", variable = self.truncated)
        self.truncatedCheckBox.var = self.truncated

        #arrange checkbutton in specific frame
        count = 0 #number of boxes
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

        #initialize checkbutton
        if isTruncated:
            self.truncatedCheckBox.select()

        #draw sliders, box number, and delete button on canvas
        self.leftSlider = canvas.create_rectangle(self.minX-Box.halfSliderWidth, (self.minY+self.maxY)/2-Box.halfSliderWidth, self.minX+Box.halfSliderWidth, (self.minY+self.maxY)/2+Box.halfSliderWidth, activefill = "cyan", outline = "cyan", tags = ("leftSlider",str(identifier)))
        self.rightSlider = canvas.create_rectangle(self.maxX-Box.halfSliderWidth, (self.minY+self.maxY)/2-Box.halfSliderWidth, self.maxX+Box.halfSliderWidth, (self.minY+self.maxY)/2+Box.halfSliderWidth, activefill = "cyan", outline = "cyan", tags = ("rightSlider",str(identifier)))
        self.topSlider = canvas.create_rectangle((self.minX+self.maxX)/2-Box.halfSliderWidth, self.minY-Box.halfSliderWidth, (self.minX+self.maxX)/2+Box.halfSliderWidth,self.minY+Box.halfSliderWidth, activefill = "cyan", outline = "cyan", tags = ("topSlider",str(identifier)))
        self.bottomSlider = canvas.create_rectangle((self.minX+self.maxX)/2-Box.halfSliderWidth, self.maxY-Box.halfSliderWidth, (self.minX+self.maxX)/2+Box.halfSliderWidth,self.maxY+Box.halfSliderWidth,activefill = "cyan", outline = "cyan", tags = ("bottomSlider",str(identifier)))
        self.text = canvas.create_text(self.minX+20, self.minY+20, text = str(identifier), fill = "cyan", font = ("Times", 30, "bold"))
        self.deleteButton = canvas.create_rectangle((((self.minX+self.maxX)/2-8),((self.minY+self.maxY)/2-8)),(((self.minX+self.maxX)/2+8),((self.minY+self.maxY)/2+8)),outline = "red", activefill = "red", tags = ("deleteButton",str(identifier)))

    #-----------------------methods for moving each slider-------------------------
    #moves left slider to a given coordinate, moving positions of other sliders and the box number text to keep them centered around the bounding box
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

    #moves right slider to a given coordinate, moving positions of other sliders and the box number text to keep them centered around the bounding box
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

    #moves top slider to a given coordinate, moving positions of other sliders and the box number text to keep them centered around the bounding box
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

    #moves bottom slider to a given coordinate, moving positions of other sliders and the box number text to keep them centered around the bounding box
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

#returns 2 numbers as (smaller, larger)           
def inOrder(num1, num2):
    if num2 < num1:
        return (num2, num1)
    return (num1, num2)

#returns coordinates as (xMin, yMin, xMax, yMax) 
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

#Allows editing of already-present data: reads a text file from KITTI format, initializing variables according to information
def readFile():
    global boxes #declare as globals to edit within method, TODO: use return statements instead
    global creatingRect
    print("Reading a file.")
    with open(fdirectory+filename+txtend) as openedFile: #Open current filename
        for line in openedFile: #Read each line (every line is a bounding box) and processes data
            
            #create array of each value in file
            fileData = line.split(" ") 
            print fileData

            #initialize truncated value
            truncatedArg = False
            if float(fileData[1]) == 1.0:
                truncatedArg = True

            #initialize coordinates
            xmin = float(fileData[4])
            ymin = float(fileData[5])
            xmax = float(fileData[6])
            ymax = float(fileData[7])
            (xmin, xmax) = inOrder(xmin, xmax)
            (ymin, ymax) = inOrder(ymin, ymax)

            #create a box
            creatingRect = canvas.create_rectangle(xmin, ymin, xmax, ymax, outline = "cyan")
            boxes.append(Box(xmin, ymin, xmax, ymax, creatingRect, truncatedArg, len(boxes)+1, fileData[0]))

            #clear for next loop iteration
            creatingRect = None
            print("Read box at: "+ str(boxes[selectedBoxIndex].minX)+ " " + str(boxes[selectedBoxIndex].minY)+ " " + str(boxes[selectedBoxIndex].maxX)+" "+ str(boxes[selectedBoxIndex].maxY))
    openedFile.close()

#Formats filename to given number of digits
def fixFilenameDigits():
    global filename #TODO: use return instead of global
    filename = filename.zfill(filenameDigits) #filename = '{:05d}'.format(filename)

#Validates if filename exists in directory, generates text file if there is no text file and quits program if there is no picture file
def checkValidFilenames():
    print("your filename identification digits is: "+str(filenameDigits))
    if os.path.isfile(directory+filename+picend):
        print("picture exists")
        if os.path.isfile(fdirectory+filename+txtend):
            print("txt file exists")
            return True
        else:
            print("text file does not exist, creating new txt file: "+filename+txtend)
            open(fdirectory+filename+txtend, "w+").close()
            return False
    else:
        print("ERROR: PICTURE OF FILENAME DOES NOT EXIST, why are you using this program")
        sys.exit() #kill program

#opens a photo
def openPhoto():
    return Image.open(directory+filename+picend)

#resizes canvas dimensions to fit a photo's dimensions
def configCanvas(photo):
    global canvas_width #TODO: use return instead of global
    global canvas_height
    canvas_width = photo.size[0]
    canvas_height = photo.size[1]
    canvas.config(width = canvas_width, height = canvas_height)

#Destroy a bounding box object, must destroy all object variables within to remove from canvas
def decimateABox(deletedBoxIndex):
    global boxes #TODO: use return instead of global
    canvas.delete(boxes[deletedBoxIndex].rectOutlineObj)
    canvas.delete(boxes[deletedBoxIndex].text)
    canvas.delete(boxes[deletedBoxIndex].leftSlider)
    canvas.delete(boxes[deletedBoxIndex].rightSlider)
    canvas.delete(boxes[deletedBoxIndex].topSlider)
    canvas.delete(boxes[deletedBoxIndex].bottomSlider)
    canvas.delete(boxes[deletedBoxIndex].deleteButton)
    boxes[deletedBoxIndex].truncatedCheckBox.destroy()
    boxes[deletedBoxIndex] = None
    arrangeCheckButtons()

#Destroys all bounding boxes (for moving to a different filename (information is written to text file and saved))
def wipe():
    global boxes #TODO: use return instead of global
    for i in range(len(boxes)):
        decimateABox(i) #not optimal, don't need to arrange checkbuttons if destroying all TODO: find straightforward solution
    boxes = []

#Records all current data to text file (before destroying within program)
def save():
    global boxes #TODO: use return instead of global
    print("Saving info")
    openedFile = open(fdirectory+filename+txtend, "w")
    for i in range(len(boxes)):
        if boxes[i] == None:
            print("found dead object") #for deleted objects (empty space in array)
            continue
        #xmin / xmax, ymin / ymax should be in order here
        openedFile.write(standardLabelledType+" "+str(boxes[i].truncatedCheckBox.var.get())+".0 0 0.0 "+str(boxes[i].minX)+" "+str(boxes[i].minY)+" "+str(boxes[i].maxX)+" "+str(boxes[i].maxY)+" 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 \n")
    openedFile.close()

#Saves information and loads next file by shifting filename by a given number
def saveAndChangeFile(changingNum):
    global filename #TODO: use return instead of global
    global currentOpenImage
    global img
    global canvas
    print("Saving and moving on")

    #save old file
    save()
    wipe()
    canvas.delete(currentOpenImage)

    #load new file
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

#moves 1 file forward
def saveAndNext():
    saveAndChangeFile(1)

#moves 1 file backward
def saveAndPrevious():
    saveAndChangeFile(-1)

#Begins process to create a bounding box
def createBox():
    global creatingBoxMode #TODO: use return instead of global
    print("creating box mode is ON")
    creatingBoxMode = True

#Keyboard Mode: inform the user an object has been selected
def mode2select(object):
    canvas.itemconfig(object, outline = 'blue')

#Keyboard Mode implimentation
def keyboardPress(event):
    global mode2selectedBox #TODO: use return instead of global
    global mode2selectedSlider
    
    if (str(event.char).isdigit()) & (event.char != '0'): #selecting a box?
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

        #if previous slider selected, unselect
        if mode2selectedSlider != '': 
            if mode2selectedSlider == 'w':
                canvas.itemconfig(boxes[mode2selectedBox-1].topSlider, outline = 'cyan')
            elif mode2selectedSlider == 'a':
                canvas.itemconfig(boxes[mode2selectedBox-1].leftSlider, outline = 'cyan')
            elif mode2selectedSlider == 's':
                canvas.itemconfig(boxes[mode2selectedBox-1].bottomSlider, outline = 'cyan')
            else: # 'd'
                canvas.itemconfig(boxes[mode2selectedBox-1].rightSlider, outline = 'cyan')
        mode2selectedSlider = event.char #new slider
        
        #selecting slider?
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

#---------------Keyboard Mode---------------
#move either right or left slider to the left
def leftClick(event):
    global boxes #TODO: use return instead of global
    
    if (mode2selectedBox != 0) & ((mode2selectedSlider == 'a') | (mode2selectedSlider == 'd')):
        if mode2selectedSlider == 'a': #moving left slider
            boxes[mode2selectedBox-1].minX = boxes[mode2selectedBox-1].minX - keyboardAccuracy
            boxes[mode2selectedBox-1].moveLeftSlider(boxes[mode2selectedBox-1].minX) #redraw
        else: #moving right slider
            boxes[mode2selectedBox-1].maxX = boxes[mode2selectedBox-1].maxX - keyboardAccuracy
            boxes[mode2selectedBox-1].moveRightSlider(boxes[mode2selectedBox-1].maxX) #redraw

#move either right or left slider to the right
def rightClick(event):
    if (mode2selectedBox != 0) & ((mode2selectedSlider == 'a') | (mode2selectedSlider == 'd')):
        if mode2selectedSlider == 'a': #moving left slider
            boxes[mode2selectedBox-1].minX = boxes[mode2selectedBox-1].minX + keyboardAccuracy
            boxes[mode2selectedBox-1].moveLeftSlider(boxes[mode2selectedBox-1].minX) #redraw
        else: #moving right slider
            boxes[mode2selectedBox-1].maxX = boxes[mode2selectedBox-1].maxX + keyboardAccuracy
            boxes[mode2selectedBox-1].moveRightSlider(boxes[mode2selectedBox-1].maxX) #redraw

#move either top or bottom slider to the top
def upClick(event):
    if (mode2selectedBox != 0) & ((mode2selectedSlider == 'w') | (mode2selectedSlider == 's')):
        if mode2selectedSlider == 'w': #moving top slider
            boxes[mode2selectedBox-1].minY = boxes[mode2selectedBox-1].minY - keyboardAccuracy
            boxes[mode2selectedBox-1].moveTopSlider(boxes[mode2selectedBox-1].minY) #redraw
        else: #moving bottom slider
            boxes[mode2selectedBox-1].maxY = boxes[mode2selectedBox-1].maxY - keyboardAccuracy
            boxes[mode2selectedBox-1].moveBottomSlider(boxes[mode2selectedBox-1].maxY) #redraw

#move either top or bottom slider to the bottom
def downClick(event):
    if (mode2selectedBox != 0) & ((mode2selectedSlider == 'w') | (mode2selectedSlider == 's')):
        if mode2selectedSlider == 'w': #moving top slider
            boxes[mode2selectedBox-1].minY = boxes[mode2selectedBox-1].minY + keyboardAccuracy
            boxes[mode2selectedBox-1].moveTopSlider(boxes[mode2selectedBox-1].minY) #redraw
        else: #moving bottom slider
            boxes[mode2selectedBox-1].maxY = boxes[mode2selectedBox-1].maxY + keyboardAccuracy
            boxes[mode2selectedBox-1].moveBottomSlider(boxes[mode2selectedBox-1].maxY) #redraw

#--------------Regular Mode---------------
def buttonPress(event): #mouse press
    global startY #TODO: use return instead of global
    global startX
    global creatingRect
    global selectedBoxIndex
    global selectedSlider
    global mode2selectedBox

    #switch modes (if currently in Keyboard Mode), unselect all
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

    #create a bounding box, save initial click coordinates (click and drag to create a bounding box)
    if creatingBoxMode: #TODO: max out if click offscreen, unlikely but check anyway
        startX = event.x
        startY = event.y
        creatingRect = canvas.create_rectangle(startX, startY, startX+1, startY+1, outline="cyan")
        return
    
    #check if click significant, get what is clicked
    clickedItem = canvas.find_closest(event.x, event.y)
    thisTag = canvas.itemcget(clickedItem, "tags") #string:[slider] [box index] current

    #slider clicked?
    if "Slider" in thisTag:
        print("I am a slider")
        thisTagArray = thisTag.split(" ")
        selectedBoxIndex = ((int)(thisTagArray[1]))-1 #arr counts from 0, identifier counts from 1
        selectedSlider = thisTagArray[0]
        print(str(boxes[selectedBoxIndex].minX)+ " " + str(boxes[selectedBoxIndex].minY)+ " " + str(boxes[selectedBoxIndex].maxX)+" "+ str(boxes[selectedBoxIndex].maxY))
        
    #delete button clicked?
    elif "deleteButton" in thisTag:
        print("DELETED!")
        thisTagArray = thisTag.split(" ")
        deletedBoxIndex = ((int)(thisTagArray[1]))-1
        decimateABox(deletedBoxIndex)


def movePress(event): #mouse drag
    global creatingRect #TODO: use return instead of global
    global boxes
    
    print("button moved")

    #create bounding box from original coordinates to current coordinates
    if creatingBoxMode:
        canvas.coords(creatingRect, startX, startY, event.x, event.y)
        #Check Valid Values: print (str(startX) + " " + str(startY) + " " + str(event.x) + " " + str(event.y))

    #move slider if slider is selected
    elif selectedBoxIndex >= 0:
        if selectedSlider == "leftSlider":
            boxes[selectedBoxIndex].moveLeftSlider(event.x)
        elif selectedSlider == "rightSlider":
            boxes[selectedBoxIndex].moveRightSlider(event.x)
        elif selectedSlider == "topSlider":
            boxes[selectedBoxIndex].moveTopSlider(event.y)
        else: #bottom
            boxes[selectedBoxIndex].moveBottomSlider(event.y)

def buttonRelease(event): #mouse release
    global creatingRect #TODO: use return instead of global
    global creatingBoxMode
    global selectedBoxIndex
    global selectedSlider
    global boxes
    
    print("button released")

    #create bounding box
    if creatingBoxMode:
        (x1, y1, x2, y2) = canvas.coords(creatingRect)
        print abs(x1-x2)
        print abs(y1-y2)
        print minBoxSize

        #Prevent accidental clicks, if bounding box is too small it will not create
        if (abs(x1-x2) < minBoxSize) | (abs(y1-y2) < minBoxSize):
            print("WARNING: Box size is less than " + str(minBoxSize) + " pixels.  Cancelled.") 
            canvas.delete(creatingRect)
            creatingRect = None
            creatingBoxMode = False
            return

        #If box not deleted, save
        (x1, x2) = inOrder(x1, x2)
        (y1, y2) = inOrder(y1, y2)
        (x1, y1, x2, y2) = boxBoundsChecker(x1,y1,x2,y2) 
        boxes.append(Box(x1, y1, x2, y2, creatingRect, False, len(boxes)+1, standardLabelledType))

    #slider position changed, save information for given edited slider    
    elif selectedBoxIndex >= 0:
        if selectedSlider == "leftSlider":
            #offscreen puts at max screen
            curX = event.x
            if curX < 0:
                curX = 0
            elif curX > canvas_width:
                curX = canvas_width
            #save
            boxes[selectedBoxIndex].minX = float(curX)
            (boxes[selectedBoxIndex].minX, boxes[selectedBoxIndex].maxX) = inOrder(boxes[selectedBoxIndex].minX, boxes[selectedBoxIndex].maxX)
        elif selectedSlider == "rightSlider":
            #offscreen puts at max screen
            curX = event.x
            if curX < 0:
                curX = 0
            elif curX > canvas_width:
                curX = canvas_width
            #save
            boxes[selectedBoxIndex].maxX = float(curX)
            (boxes[selectedBoxIndex].minX, boxes[selectedBoxIndex].maxX) = inOrder(boxes[selectedBoxIndex].minX, boxes[selectedBoxIndex].maxX)
        elif selectedSlider == "topSlider":
            #offscreen puts at max screen
            curY = event.y
            if curY < 0:
                curY = 0
            elif curY > canvas_width:
                curY = canvas_width
            #save
            boxes[selectedBoxIndex].minY = float(curY)
            (boxes[selectedBoxIndex].minY, boxes[selectedBoxIndex].maxY) = inOrder(boxes[selectedBoxIndex].minY, boxes[selectedBoxIndex].maxY)
        elif selectedSlider == "bottomSlider": #else, but checking just in case
            #offscreen puts at max screen
            curY = event.y
            if curY < 0:
                curY = 0
            elif curY > canvas_width:
                curY = canvas_width
            #save
            boxes[selectedBoxIndex].maxY = float(curY)
            (boxes[selectedBoxIndex].minY, boxes[selectedBoxIndex].maxY) = inOrder(boxes[selectedBoxIndex].minY, boxes[selectedBoxIndex].maxY)
        print(str(boxes[selectedBoxIndex].minX)+ " " + str(boxes[selectedBoxIndex].minY)+ " " + str(boxes[selectedBoxIndex].maxX)+" "+ str(boxes[selectedBoxIndex].maxY))

    #mouse released, so reset all variables
    selectedBoxIndex = -1
    selectedSlider = None
    creatingRect = None
    creatingBoxMode = False

#--------------MAIN PROGRAM----------------

#check if picture exists
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
for i in range(((int)(canvas_width))/120):    #TODO: fix depending on picture size
    columnFrames.append(Frame(bottomFrame))
    columnFrames[len(columnFrames)-1].pack(side = LEFT)

#load file data from previous labeling
if fileExists:
    readFile()
print len(boxes)

#create buttons
Button(master, text = 'save and next file', command = saveAndNext).pack(in_=topFrame, side = RIGHT)
Button(master, text = 'save and previous file', command = saveAndPrevious).pack(in_=topFrame, side = LEFT)
Button(master, text = 'save', command = save).pack(in_=topFrame)
Button(master, text = 'create box', command = createBox).pack(in_=topFrame)

#add events
master.bind("<KeyPress>", keyboardPress) #keyboard
master.bind("<Left>", leftClick)
master.bind("<Right>", rightClick)
master.bind("<Up>", upClick)
master.bind("<Down>", downClick)
canvas.bind("<ButtonPress-1>", buttonPress) #mouse press
canvas.bind("<B1-Motion>", movePress) #mouse drag
canvas.bind("<ButtonRelease-1>", buttonRelease) #mouse release

master.mainloop()
