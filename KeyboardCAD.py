#KeyboardCAD is a tool for making FreeCAD files for custom keyboards.
#It uses the raw data generated by http://www.keyboard-layout-editor.com/ to design a switch mounting plate for any keyboard imaginable.

# Copyright (C) 2015  Nicholas Stamplecoskie

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

#Thanks to Ian Prest for keyboard-layout-editor and to
#Juergen Riegel, Werner Mayer, Yorik van Havre and everyone else involved with FreeCAD

###########################################################################
#USER PARAMETERS
###########################################################################
fileName = 'custom keyboard'  #name of the FreeCAD file which will be the result of this script. An extension will be added if not present
savePath = 'D:/Users/Nick/Desktop/' #path indicating where you want to save the file
layoutPath = 'D:/Users/Nick/Desktop/layout.txt' # path to a text file containing the raw data from http://www.keyboard-layout-editor.com/
plateXDim = 0 #overall length of the plate to be made, in mm. If False or zero, smallest possible value will be calculated.
plateYDim = 0 #overall width of the plate to be made, in mm. If False or zero, smallest possible value will be calculated.
xStart = 0 #How far from the left edge the keyboard will start to be drawn. Not the distance to the first hole, but to the first key.
yStart = 0 #How far from the top edge the keyboard will start to be drawn.
plateThickness = 1.5 #plate thickness in mm.
switchHoleType = 0 #0 for standard square, 1 for the "H" shape with cutouts for switch disassembly, 2 for Alps compatible (with switch disassembly for cherry possible).
includeStabilizers = "both"  #make cutouts for stabilizers? Possible values: False, "costar", "cherry", "both"
rotateSwitches = False #rotate all switches with cutouts or alps compatibility by 90 degrees (so that cutouts are on the top and bottom)

###########################################################################
#LABEL PARAMETERS
###########################################################################
#Include these strings in the labels per key in the layout editor.
#!r! for rotating a switch with cutouts or alps compatibility by 90 degrees (so that cutouts are on the top and bottom)
#!c! for toggling the presence of a cutout on a switch (toggling type 1 switch hole)
#!a! for toggling alps-compatible (type 2) switch hole. This takes precedence over !c! if you have both in the same label

###########################################################################
#MEASUREMENTS
###########################################################################
#SWITCH
KEYUNIT = 19.05 #the value of one unit in mm
SWITCHSIZE = 13.9954 #in mm, the length and width of square (cherry) switches. 13.9954 is default for Cherry MX switches. Make equal to ALPSHEIGHT if you are using switch type 2 but want it to be ALPS only.
ALPSWIDTH = 15.5 #Used for alps compatible switch holes, this will the x dimension of a standard ALPS-like switch
ALPSHEIGHT = 12.8 #The y dimension for ALPS-like switches
#CUTOUTS (for switch disassembly)
CUTOUTLENGTH = 3.81 #each switch can have four cut-outs around it for switch disassembly.
CUTOUTWIDTH = 1.016
CUTOUTSEPARATION = 5.3594 #distance between two cutouts on the same side of a switch
CUTOUTDST = (SWITCHSIZE - (2*CUTOUTLENGTH + CUTOUTSEPARATION))/2 #distance from top side of switch to the top of the first cutout. 0.508
#STABILIZERS
LONGSTABILIZERPOSTTOPOST = 100 #The separation between the two stabilizer inserts. Measured by the distance between the two outer posts on the spacebar keycap.
LONGSTABILIZERPOSTTOPOST2 = 80 # If you want two possible spacebar stabilizer positions to be cut out, add a value here.
SHORTSTABILIZERPOSTTOPOST = 23.875 #The separation between the two stabilizer inserts. Measured by the distance between the two outer posts of a keycap (example, shift key).
MINIMUMLONGSTABLENGTH = 3 #If key is this wide or wider, use the long stabilizer. Since keys between 3 and units 6 units are unusual, this value can vary without changing anything.
#ADDITIONAL MEASUREMENTS FOR CHERRY
#These have to do with the additional cut out made for inserting the wire through the plate
#They can vary without consequence, but the values provided are from official Cherry spec and look the best with standard square switch holes
#Make DST values 0 if you do not want these cutouts
SHORTWIREDST = 4.88 #2.11 #vertical distance from center of switch hole (stem) to wire cutout for short stabilizers.
SHORTWIREHEIGHT = 10.69 #height of the wire cutout for short stabilizers. Results in a much larger cut out
LONGWIREDST = 2.287 #4.71 #vertical distance from center of switch hole to wire cutout for long stabilizers.
LONGWIREHEIGHT = 4.6 #height of the wire cutout for long stabilizers.

###########################################################################
#PATHS
###########################################################################
#Assign values to these two variables if you are not running the script from the python in the FreeCAD folder
FREECADBINPATH = None #'C://Program Files//FreeCAD 0.14//bin' #path to your FreeCAD bin folder
FREECADLIBPATH = None #'C://Program Files//FreeCAD 0.14//lib' #path to your FreeCAD lib folder

###########################################################################
#(OPTIONAL) SCREW HOLES
###########################################################################
#This list of holes must contain tuples (x,y) for the coordinates for where each screw hole will be cut
#x is the distance from the left edge of the plate to the center of the screw hole.
#y is the distance from the TOP edge of the plate to the center of the hole.
#screws = [(25.2,27.9),(260.05,27.9),(128.2,48.2),(190.5,85.2)] #screw locations for most 60% cases
screws = []
screwHoleRadius = 1.05 #the radius of each hole in mm
sixtySideHoles = False


###########################################################################
#(OPTIONAL) FILLET CORNERS
###########################################################################
#If this value is not zero, then FreeCAD will fillet, or round, the 4 corners of the plate
#by the radius specified
filletRadius = 0

def main():
	getLayoutData()
	initializeCAD()
	drawSwitches()
	drawStabilizers()
	drawScrewHoles()
	fillet()
	save()
	intersection()

#FreeCAD methods

def	initializeCAD():
	global doc
	doc = FreeCAD.newDocument() #initialize the document

	pad(sketchRectangle(0, 0, plateXDim, plateYDim, False, False))	 #draw the plate

def sketchRectangle(posX, posY, xDim, yDim, rotation, rotate90=False):
	global doc
	global sketchCount

	rectangle = doc.addObject('Sketcher::SketchObject','Sketch' + str(sketchCount))

	if not sketchCount == 0: #if it is the first sketch, then the pad doesn't exist yet
		rectangle.Support = (doc.Pad,["Face6"])

	sketchCount = sketchCount + 1

	#   0_______________3
	#	|				|
	#	|				|
	#	|				|
	#	|				|
	#	|				|
	#	|				|
	#  1|_______________|2

	x = [0]*4
	y = [0]*4

	x[0] = posX
	y[0] = -posY
	x[2] = posX + xDim
	y[2] = -posY - yDim
	x[1] = x[0]
	y[1] = y[2]
	x[3] = x[2]
	y[3] = y[0]

	if rotate90:
		centerPoint = (x[0] + xDim/2, y[0] - yDim/2)
		for n in range(len(x)):
			x[n], y[n] = rotatePoint(centerPoint, (x[n],y[n]), 90)

	if rotation:
		for n in range(4):
			x[n], y[n] = rotatePoint((rotation[0],rotation[1]), (x[n],y[n]), rotation[2])

	for i in range(3):
		rectangle.addGeometry(Part.Line(App.Vector(x[i],y[i],0),App.Vector(x[i+1],y[i+1],0)))
	rectangle.addGeometry(Part.Line(App.Vector(x[3],y[3],0),App.Vector(x[0],y[0],0)))

	for j in range(3):
		rectangle.addConstraint(Sketcher.Constraint('Coincident',j,2,j+1,1))
	rectangle.addConstraint(Sketcher.Constraint('Coincident',3,2,0,1))

	for k in range(4):
		rectangle.addConstraint(Sketcher.Constraint('DistanceX',k,1,x[k]))
		rectangle.addConstraint(Sketcher.Constraint('DistanceY',k,1,y[k]))

	doc.recompute()

	return rectangle

def sketchSwitchWithCutOuts(posX, posY, rotation, rotate90):
	global doc
	global sketchCount

	rectangle = doc.addObject('Sketcher::SketchObject','Sketch' + str(sketchCount))

	rectangle.Support = (doc.Pad,["Face6"])

	sketchCount = sketchCount + 1

	#   0_______________ 19
	#2 _|1			  18|_  17
	# |					  |
	#3|_ 4			  15 _| 16
	#6 _|5			  14|_ 13
	# |				      |
	#7|_ 8			  11 _| 12
	# 9 |_______________| 10

	x = [0]*20
	y = [0]*20

	x[0] = posX
	y[0] = -posY
	x[1] = x[0]
	y[1] = y[0] - CUTOUTDST
	x[2] = x[0] - CUTOUTWIDTH
	y[2] = y[1]
	x[3] = x[2]
	y[3] = y[2] - CUTOUTLENGTH
	x[4] = x[0]
	y[4] = y[3]
	x[5] = x[0]
	y[5] = y[4] - CUTOUTSEPARATION
	x[6] = x[2]
	y[6] = y[5]
	x[7] = x[2]
	y[7] = y[6] - CUTOUTLENGTH
	x[8] = x[0]
	y[8] = y[7]
	x[9] = x[0]
	y[9] = y[8] - CUTOUTDST # -posY - SWITCHSIZE
	x[10] = posX + SWITCHSIZE
	y[10] = -posY - SWITCHSIZE
	x[11] = x[10]
	y[11] = y[8]
	x[12] = x[10] + CUTOUTWIDTH
	y[12] = y[11]
	x[13] = x[12]
	y[13] = y[6]
	x[14] = x[10]
	y[14] = y[13]
	x[15] = x[10]
	y[15] = y[4]
	x[16] = x[12]
	y[16] = y[15]
	x[17] = x[12]
	y[17] = y[2]
	x[18] = x[10]
	y[18] = y[1]
	x[19] = x[10]
	y[19] = y[0]

	if rotate90:
		centerPoint = (x[0] + SWITCHSIZE/2, y[0] - SWITCHSIZE/2)
		for n in range(20):
			x[n], y[n] = rotatePoint(centerPoint, (x[n],y[n]), 90)

	if rotation:
		for n in range(20):
			x[n], y[n] = rotatePoint((rotation[0],rotation[1]), (x[n],y[n]), rotation[2])


	for i in range(19):
		rectangle.addGeometry(Part.Line(App.Vector(x[i],y[i],0),App.Vector(x[i+1],y[i+1],0)))
	rectangle.addGeometry(Part.Line(App.Vector(x[19],y[19],0),App.Vector(x[0],y[0],0)))

	for j in range(19):
		rectangle.addConstraint(Sketcher.Constraint('Coincident',j,2,j+1,1))
	rectangle.addConstraint(Sketcher.Constraint('Coincident',19,2,0,1))

	for k in range(20):
		rectangle.addConstraint(Sketcher.Constraint('DistanceX',k,1,x[k]))
		rectangle.addConstraint(Sketcher.Constraint('DistanceY',k,1,y[k]))

	doc.recompute()

	return rectangle

def sketchCircle(posX, posY, radius):
	global doc
	global sketchCount

	circle = doc.addObject('Sketcher::SketchObject','Sketch' + str(sketchCount))

	circle.Support = (doc.Pad,["Face6"])

	sketchCount = sketchCount + 1

	posY = -posY

	circle.addGeometry(Part.Circle(App.Vector(posX,posY,0),App.Vector(0,0,1),radius))

	circle.addConstraint(Sketcher.Constraint('DistanceX',0,3,posX))
	circle.addConstraint(Sketcher.Constraint('DistanceY',0,3,posY))

	circle.addConstraint(Sketcher.Constraint('Radius',0,radius))

	doc.recompute()

	return circle

def sketchSideHole(right): #method for just the 2 side holes in the plate of 60% keyboards
	global doc
	global sketchCount
	
	length = 8 #length doesn't matter. Just has to extend past edge of plate
	yCenter = -56.5
	if right:	
		leftCenter = 280
		rightCenter = leftCenter + length
	else:
		rightCenter = 5
		leftCenter = rightCenter - length
		
	
	radius = screwHoleRadius
	slot = doc.addObject('Sketcher::SketchObject','Sketch' + str(sketchCount))
	
	slot.Support = (doc.Pad,["Face6"])

	sketchCount = sketchCount + 1

	slot.addGeometry(Part.ArcOfCircle(Part.Circle(App.Vector(leftCenter,yCenter,0),App.Vector(0,0,1),radius),1.570796,-1.570796))
	slot.addGeometry(Part.ArcOfCircle(Part.Circle(App.Vector(rightCenter,yCenter,0),App.Vector(0,0,1),radius),-1.570796,1.570796))
	slot.addGeometry(Part.Line(App.Vector(leftCenter,yCenter-radius,0),App.Vector(rightCenter,yCenter-radius,0)))
	slot.addGeometry(Part.Line(App.Vector(leftCenter,yCenter+radius,0),App.Vector(rightCenter,yCenter+radius,0)))
	slot.addConstraint(Sketcher.Constraint('Tangent',0,2)) 
	slot.addConstraint(Sketcher.Constraint('Tangent',0,3)) 
	slot.addConstraint(Sketcher.Constraint('Tangent',1,2)) 
	slot.addConstraint(Sketcher.Constraint('Tangent',1,3)) 
	slot.addConstraint(Sketcher.Constraint('Coincident',0,1,3,1)) 
	slot.addConstraint(Sketcher.Constraint('Coincident',0,2,2,1)) 
	slot.addConstraint(Sketcher.Constraint('Coincident',2,2,1,1)) 
	slot.addConstraint(Sketcher.Constraint('Coincident',3,2,1,2)) 
	slot.addConstraint(Sketcher.Constraint('Horizontal',2)) 
	slot.addConstraint(Sketcher.Constraint('Equal',0,1)) 
	
	slot.addConstraint(Sketcher.Constraint('DistanceX',1,3,rightCenter)) 	
	slot.addConstraint(Sketcher.Constraint('DistanceY',1,3,yCenter)) 
	slot.addConstraint(Sketcher.Constraint('DistanceX',0,3,1,3,length))
	slot.addConstraint(Sketcher.Constraint('DistanceY',0,2,0,3,radius))

	doc.recompute()	
	return slot
	
def sketchMiddleHole(): #method for just the middle hole of 60% keyboards
	global doc
	global sketchCount
	
	#original position: (128.2,48.2)
	length = 3
	x = 128.7
	bottomY = -48.2
	topY = bottomY + length
	radius = screwHoleRadius
	slot = doc.addObject('Sketcher::SketchObject','Sketch' + str(sketchCount))
	
	slot.Support = (doc.Pad,["Face6"])

	sketchCount = sketchCount + 1
	
	slot.addGeometry(Part.ArcOfCircle(Part.Circle(App.Vector(x,topY,0),App.Vector(0,0,1),radius),0,3.141592))
	slot.addGeometry(Part.ArcOfCircle(Part.Circle(App.Vector(x,bottomY,0),App.Vector(0,0,1),radius),3.141592,0))
	slot.addGeometry(Part.Line(App.Vector(x-radius,topY,0),App.Vector(x-radius,bottomY,0)))
	slot.addGeometry(Part.Line(App.Vector(x+radius,topY,0),App.Vector(x+radius,bottomY,0)))
	slot.addConstraint(Sketcher.Constraint('Tangent',0,2)) 
	slot.addConstraint(Sketcher.Constraint('Tangent',0,3)) 
	slot.addConstraint(Sketcher.Constraint('Tangent',1,2)) 
	slot.addConstraint(Sketcher.Constraint('Tangent',1,3)) 
	slot.addConstraint(Sketcher.Constraint('Coincident',0,1,3,1)) 
	slot.addConstraint(Sketcher.Constraint('Coincident',0,2,2,1)) 
	slot.addConstraint(Sketcher.Constraint('Coincident',2,2,1,1)) 
	slot.addConstraint(Sketcher.Constraint('Coincident',3,2,1,2)) 
	slot.addConstraint(Sketcher.Constraint('Vertical',2)) 
	slot.addConstraint(Sketcher.Constraint('Equal',0,1)) 
	
	slot.addConstraint(Sketcher.Constraint('DistanceX',1,3,x)) 	
	slot.addConstraint(Sketcher.Constraint('DistanceY',1,3,bottomY)) 
	slot.addConstraint(Sketcher.Constraint('DistanceY',0,3,1,3,-length))
	slot.addConstraint(Sketcher.Constraint('DistanceX',1,3,1,2,radius))
	
	doc.recompute()	
	return slot

def sketchAlpsComSwitch(posX, posY, rotation, rotate90):
	global doc
	global sketchCount

	if ALPSHEIGHT == SWITCHSIZE: #if this is the case, then Alps only holes will be made. They are just rectangles.
		rectangle = sketchRectangle(posX - (ALPSWIDTH - SWITCHSIZE)/2, posY, ALPSWIDTH, ALPSHEIGHT, rotation, rotate90)
		return rectangle

	rectangle = doc.addObject('Sketcher::SketchObject','Sketch' + str(sketchCount))

	rectangle.Support = (doc.Pad,["Face6"])

	sketchCount = sketchCount + 1

	#   0_______________ 11
	#2 _|1			  10|_  9
	# |					  |
	# |		              |
	# |         		  |
	# |				      |
	#3|_ 4			  7  _| 8
	# 5 |_______________| 6

	x = [0]*12
	y = [0]*12

	dstY = (SWITCHSIZE - ALPSHEIGHT)/2
	dstX = (ALPSWIDTH - SWITCHSIZE)/2

	x[0] = posX
	y[0] = -posY
	x[1] = x[0]
	y[1] = y[0] - dstY
	x[2] = x[0] - dstX
	y[2] = y[1]
	x[3] = x[2]
	y[3] = y[2] - ALPSHEIGHT
	x[4] = x[0]
	y[4] = y[3]
	x[5] = x[0]
	y[5] = y[4] - dstY
	x[6] = x[5] + SWITCHSIZE
	y[6] = y[5]
	x[7] = x[6]
	y[7] = y[4]
	x[8] = x[7] + dstX
	y[8] = y[7]
	x[9] = x[8]
	y[9] = y[1]
	x[10] = x[7]
	y[10] = y[1]
	x[11] = x[10]
	y[11] = y[0]

	if rotate90:
		centerPoint = (x[0] + SWITCHSIZE/2, y[0] - SWITCHSIZE/2)
		for n in range(len(x)):
			x[n], y[n] = rotatePoint(centerPoint, (x[n],y[n]), 90)

	if rotation:
		for n in range(len(x)):
			x[n], y[n] = rotatePoint((rotation[0],rotation[1]), (x[n],y[n]), rotation[2])


	for i in range(len(x)-1):
		rectangle.addGeometry(Part.Line(App.Vector(x[i],y[i],0),App.Vector(x[i+1],y[i+1],0)))
	rectangle.addGeometry(Part.Line(App.Vector(x[len(x)-1],y[len(x)-1],0),App.Vector(x[0],y[0],0)))

	for j in range(len(x)-1):
		rectangle.addConstraint(Sketcher.Constraint('Coincident',j,2,j+1,1))
	rectangle.addConstraint(Sketcher.Constraint('Coincident',len(x)-1,2,0,1))

	for k in range(len(x)):
		rectangle.addConstraint(Sketcher.Constraint('DistanceX',k,1,x[k]))
		rectangle.addConstraint(Sketcher.Constraint('DistanceY',k,1,y[k]))

	doc.recompute()

	return rectangle

def sketchCherryStab(xPos, yPos, left, rotation, vertical):
	#in this case, xPos is the horizontal center of the stab cutout
	#This function is messy, but hopefully, changes won't ever be necessary
	#measurements see https://www.dropbox.com/s/fpuwaxqopasm76w/MX%20Series.pdf
	width = 6.65
	length = 12.3
	heightSideCutOut = 2.8
	widthSideCutOut = 4.2 #mm from post or center of cutout
	sideCutOutPos = 0.5 #mm from center of switch
	heightBottomCutOut = 13.5 #mm from top of cutout
	widthBottomCutOut = 3
	#bottomCutOutPos = assuming it is centered horizontally wrt stab cut out
	dstFromSwitchCenter = 6.604

	global doc
	global sketchCount

	rectangle = doc.addObject('Sketcher::SketchObject','Sketch' + str(sketchCount))

	rectangle.Support = (doc.Pad,["Face6"])

	sketchCount = sketchCount + 1

	x = [0]*12
	y = [0]*12
	if left:
		k = 1
	else:
		k = -1

	x[0] = xPos - k*widthSideCutOut
	y[0] = -yPos - sideCutOutPos
	x[1] = x[0]
	y[1] = y[0] + heightSideCutOut
	x[2] = x[1] + k*(widthSideCutOut - width/2)
	y[2] = y[1]
	x[3] = x[2]
	y[3] = -yPos - dstFromSwitchCenter + length
	x[4] = x[3] + k*width
	y[4] = y[3]
	x[5] = x[4]
	y[5] = y[3] - length
	x[6] = x[5] - k*(width - widthBottomCutOut)/2
	y[6] = y[5]
	x[7] = x[6]
	y[7] = y[4] - heightBottomCutOut
	x[8] = x[7] - k*widthBottomCutOut
	y[8] = y[7]
	x[9] = x[8]
	y[9] = y[6]
	x[10] = x[9] - k*(width - widthBottomCutOut)/2
	y[10] = y[9]
	x[11] = x[10]
	y[11] = y[0]

	if vertical:
		centerPoint = (xPos, -yPos)
		for n in range(len(x)):
			x[n], y[n] = rotatePoint(centerPoint, (x[n],y[n]), 90)

	if rotation:
		for n in range(len(x)):
			x[n], y[n] = rotatePoint((rotation[0],rotation[1]), (x[n],y[n]), rotation[2])

	for i in range(len(x)-1):
		rectangle.addGeometry(Part.Line(App.Vector(x[i],y[i],0),App.Vector(x[i+1],y[i+1],0)))
	rectangle.addGeometry(Part.Line(App.Vector(x[len(x)-1],y[len(x)-1],0),App.Vector(x[0],y[0],0)))

	for j in range(len(x)-1):
		rectangle.addConstraint(Sketcher.Constraint('Coincident',j,2,j+1,1))
	rectangle.addConstraint(Sketcher.Constraint('Coincident',len(x)-1,2,0,1))

	for k in range(len(x)):
		rectangle.addConstraint(Sketcher.Constraint('DistanceX',k,1,x[k]))
		rectangle.addConstraint(Sketcher.Constraint('DistanceY',k,1,y[k]))

	doc.recompute()

	return rectangle

def sketchCostarStab(xPos, yPos, rotation, vertical):
	# length = 13.97 #Length (or height) of the cutout for costar stabilizers
	# width = 3.3 #Width of the cutout for costar stabilizers
	length = 14 #Length (or height) of the cutout for costar stabilizers
	width = 3.5 #Width of the cutout for costar stabilizers
	dst = 6.2477 #Vertical distance from the center (stem) of the switch to the top of the stabilizer cutout.

	if vertical:
		return sketchRectangle(xPos-dst, yPos-width/2, length, width, rotation)
	else:
		return sketchRectangle(xPos-width/2, yPos-dst, width, length, rotation)

def pocket(sketch):
	global doc
	pocket = doc.addObject("PartDesign::Pocket","Pocket" + str(sketchCount - 1))
	pocket.Sketch = sketch
	pocket.Length = 5.0
	pocket.Type = 1
	pocket.UpToFace = None
	doc.recompute()

def pad(sketch):
	global doc
	pad = doc.addObject("PartDesign::Pad","Pad")
	pad.Sketch = sketch
	pad.Length = plateThickness
	pad.Reversed = 0
	pad.Midplane = 0
	pad.Length2 = 100.000000
	pad.Type = 0
	pad.UpToFace = None
	doc.recompute()

def joinAllParts():
	global doc
	doc.addObject("Part::MultiCommon","Common")
	pocketList = []
	for x in range(sketchCount-1):
		pocketList.append(doc.getObject("Pocket" + str(x+1)))
	if filletRadius != 0:
		for y in range(4):
			pocketList.append(doc.getObject("Fillet" + str(y+1)))
	doc.Common.Shapes = pocketList
	doc.recompute()
	
def fillet():
	if filletRadius != 0:
		f1 = doc.addObject("PartDesign::Fillet","Fillet1")
		f1.Base = (doc.Pad, ["Edge1"])
		f1.Radius = filletRadius
		
		f2 = doc.addObject("PartDesign::Fillet","Fillet2")
		f2.Base = (f1, ["Edge3"])
		f2.Radius = filletRadius
		
		f3 = doc.addObject("PartDesign::Fillet","Fillet3")
		f3.Base = (f2, ["Edge17"])
		f3.Radius = filletRadius
		
		f4 = doc.addObject("PartDesign::Fillet","Fillet4")
		f4.Base = (f3, ["Edge15"])
		f4.Radius = filletRadius
		
		doc.recompute()

#Drawing methods

def drawSwitches():
	for prop in props:
		coord = findCoord(prop[0], prop[1], prop[2], prop[3])
		rotation = prop[4]
		rotate90 = "!r!" in labels[props.index(prop)]
		if "!a!" in labels[props.index(prop)]:
			drawSwitch(coord[0], coord[1], rotation, rotate90, 2)
		elif "!c!" in labels[props.index(prop)]:
			drawSwitch(coord[0], coord[1], rotation, rotate90, 1)
		else:
			drawSwitch(coord[0], coord[1], rotation, rotate90, 0)

def drawStabilizers():
	if includeStabilizers:
		if includeStabilizers == "cherry":
			drawStabilizersHelper(True)
		elif includeStabilizers == "costar":
			drawStabilizersHelper(False)
		elif includeStabilizers == "both":
			drawStabilizersHelper(True)
			drawStabilizersHelper(False)
		else:
			print (includeStabilizers + " is not a valid value for includeStabilizers")
			return

def drawScrewHoles():
	if sixtySideHoles:
		drawSixtyScrewHoles()
	else:
		for screw in screws:
			pocket(sketchCircle(screw[0], screw[1], screwHoleRadius))

def drawSwitch(x, y, rotation, rotate90, type):
	if type == 0:
		pocket(sketchRectangle(x, y, SWITCHSIZE, SWITCHSIZE, rotation))
	elif type == 1:
		pocket(sketchSwitchWithCutOuts(x, y, rotation, rotate90))
	else:
		pocket(sketchAlpsComSwitch(x, y, rotation, rotate90))

def drawStabilizersHelper(cherry):
	for prop in props:
		if prop[2] >= 2 or prop[3] >= 2:
			coord = findCoordForStab(prop[0], prop[1], prop[2], prop[3])
			rotation = prop[4]
			if prop[2] >= MINIMUMLONGSTABLENGTH:#spacebar
				drawHorizontalStabilizer(coord[0], coord[1], False, cherry, rotation)
				global LONGSTABILIZERPOSTTOPOST
				global LONGSTABILIZERPOSTTOPOST2
				if LONGSTABILIZERPOSTTOPOST2: #if a second value is given, swap and then draw again.
					tmp = LONGSTABILIZERPOSTTOPOST
					LONGSTABILIZERPOSTTOPOST = LONGSTABILIZERPOSTTOPOST2
					LONGSTABILIZERPOSTTOPOST2 = tmp
					drawHorizontalStabilizer(coord[0], coord[1], False, cherry, rotation)
			elif prop[3] >= 2: #if taller than 2, stab will be vertical, for iso, big-ass enter, + on numpad, etc..
				drawVerticalStabilizer(coord[0], coord[1], cherry, rotation)
			else: #standard wide key
				drawHorizontalStabilizer(coord[0], coord[1], True, cherry, rotation)

def drawHorizontalStabilizer(x, y, short, cherry, rotation):
	if short:
		separation = SHORTSTABILIZERPOSTTOPOST
	else:
		separation = LONGSTABILIZERPOSTTOPOST
	xLeft = x - separation/2
	xRight = x + separation/2

	if cherry:
		pocket(sketchCherryStab(xLeft, y, True, rotation, False))
		pocket(sketchCherryStab(xRight, y, False, rotation, False))
	else:
		pocket(sketchCostarStab(xLeft, y, rotation, False))
		pocket(sketchCostarStab(xRight, y, rotation, False))

	if cherry: #for cherry, additional pieces of the plate are cut for passing the wire through
		if short and not SHORTWIREDST == 0:
			wireDst = SHORTWIREDST
			wireHeight = SHORTWIREHEIGHT
		elif not LONGWIREDST == 0:
			wireDst = LONGWIREDST
			wireHeight = LONGWIREHEIGHT
		else:
			return
		xWire = xLeft
		yWire = y - wireDst
		pocket(sketchRectangle(xWire, yWire, separation, wireHeight, rotation))

def drawVerticalStabilizer(x, y, cherry, rotation):
	separation = SHORTSTABILIZERPOSTTOPOST
	yTop = y - separation/2
	yBottom = y + separation/2
	if cherry:
		pocket(sketchCherryStab(x, yBottom, True, rotation, True))
		pocket(sketchCherryStab(x, yTop, False, rotation, True))
	else:
		pocket(sketchCostarStab(x, yBottom, rotation, True))
		pocket(sketchCostarStab(x, yTop, rotation, True))

	if cherry and not SHORTWIREDST == 0: #for cherry, additional pieces of the plate are cut for passing the wire through
		wireDst = SHORTWIREDST
		wireHeight = SHORTWIREHEIGHT
		xWire = x - wireDst
		yWire = yTop
		pocket(sketchRectangle(xWire, yWire, wireHeight, separation, rotation))

def drawSixtyScrewHoles(): #for compatibilty with universal 60 percent keyboard cases
	global screwHoleRadius
	screwHoleRadius = 1.15 #M2 (2 mm diameter) screws will always be used for 60 percent cases
	#Adding .3 mm to the diameter of the holes for the sake of inconsistency
	sixtyScrews = [(25.2,27.9),(260.05,27.9),(190.5,85.2)]
	for screw in sixtyScrews:
		pocket(sketchCircle(screw[0], screw[1], screwHoleRadius))
	pocket(sketchSideHole(True))
	pocket(sketchSideHole(False))
	pocket(sketchMiddleHole())
	
#Calculation methods

def findCoord(x, y, w, h): #calculates where the top left corner of the switch is, given that each switch will be in the exact middle of the key
	x = x*KEYUNIT
	y = y*KEYUNIT
	w = w*KEYUNIT
	h = h*KEYUNIT
	xPos = x + w/2 - SWITCHSIZE/2
	yPos = y + h/2 - SWITCHSIZE/2
	xPos = xPos + xStart
	yPos = yPos + yStart
	return (xPos, yPos)
	
def findCoordForStab(x, y, w, h): #calculates where the exact center (stem) of each switch will be. Used for positioning stabilizers
	x = x*KEYUNIT
	y = y*KEYUNIT
	w = w*KEYUNIT
	h = h*KEYUNIT
	xPos = x + w/2
	yPos = y + h/2
	xPos = xPos + xStart
	yPos = yPos + yStart
	return (xPos, yPos)

def rotatePoint(centerPoint, point, angle): #counterclockwise
	tempPoint = (point[0]-centerPoint[0], point[1]-centerPoint[1])
	if angle == 10:
		tempPoint = (-tempPoint[1], tempPoint[0])
	else:
		angle = math.radians(angle)
		tempPoint = (tempPoint[0]*math.cos(angle)-tempPoint[1]*math.sin(angle), tempPoint[0]*math.sin(angle)+tempPoint[1]*math.cos(angle))
	tempPoint = (tempPoint[0]+centerPoint[0], tempPoint[1]+centerPoint[1])
	return tempPoint

def calculatePlateXDim():
	global plateXDim
	maxX = 0
	for prop in props:
		xValue = prop[0] + prop[2]
		if xValue > maxX:
			maxX = xValue
	plateXDim = maxX*KEYUNIT

def calculatePlateYDim():
	global plateYDim
	maxY = 0
	for prop in props:
		yValue = prop[1] + prop[3]
		if yValue > maxY:
			maxY = yValue
	plateYDim = maxY*KEYUNIT

#Input data methods

def getLayoutData():
	parseLayout(readFile())
	fixRotations()
	modifyLabels()
	if not plateXDim or plateXDim == 0:
		calculatePlateXDim()
	if not plateYDim or plateYDim == 0:
		calculatePlateYDim()

def readFile():
	return open(layoutPath, 'r').readlines()

def parseLayout(layoutList):
	global labels
	for row in layoutList:
		newRow = True
		row = row.rstrip()
		if row[-1:] == ',':
			row = row[1:-2]
		else:
			row = row[1:-1]
		values = row.split(",")
		tmp = ''
		for value in values:
			if not tmp == '':
				value = tmp + "," + value
			if value[:1] == '{' and value[-1:] == '}': #value is a prop
				makeProp(value[1:-1], newRow)
				newRow = False
				tmp = ''
			elif value[:1] == '"' and value[-1:] == '"' and not len(value) == 1: #value is a label
				labels.append(value[1:-1])
				if len(props) < len(labels): #if no prop exists for this label, makes one
					makeProp('', newRow)
				newRow = False
				tmp = ''
			else: #splitting of the row into values didn't work right because a value contained a comma
				tmp = value

def makeProp(values, newRow):
	global props
	if props:
		prevProp = props[-1]
	else:
		prevProp = (0,-1,0,0,(0,0,0))
	x = 0
	y = 0
	w = 1
	h = 1
	rx = prevProp[4][0]
	ry = prevProp[4][1]
	r = prevProp[4][2]
	if not values == '':
		for value in values.split(","):
			colon = value.find(":")
			if value[:colon] == 'x':
				x = float(value[colon + 1:])
			elif value[:colon] == 'y':
				y = float(value[colon + 1:])
			elif value[:colon] == 'w':
				w = float(value[colon + 1:])
			elif value[:colon] == 'h':
				h = float(value[colon + 1:])
			elif value[:colon] == 'r':
				r = float(value[colon + 1:])
			elif value[:colon] == 'rx':
				rx = float(value[colon + 1:])
			elif value[:colon] == 'ry':
				ry = float(value[colon + 1:])
			else:
				pass #the value does not contain relative information
	newRotation = (rx,ry,r)
	if newRow:
		x = rx + x
		if newRotation != prevProp[4]:
			y = ry + y
		else:
			y = prevProp[1] + 1 + y
	else:
		x = x + prevProp[0] + prevProp[2]
		y = prevProp[1]

	props.append((x,y,w,h,newRotation))

def modifyLabels(): #adds or removes label parameters based on the value of rotateSwitches and includeCutouts
	global labels
	result = []
	for label in labels:
		newLabel = label
		if switchHoleType == 1: #cutouts for switch disassembly
			if "!c!" in label:
				c = newLabel.index("!c!")
				newLabel = newLabel[:c] + newLabel[c+3:]
			else:
				if not "!a!" in label:
					newLabel = newLabel + "!c!"
		if switchHoleType == 2: #Alps compatible. This takes precedence over !c!
			if "!a!" in label:
				a = newLabel.index("!a!")
				newLabel = newLabel[:a] + newLabel[a+3:]
			else:
				if not "!c!" in label:
					newLabel = newLabel + "!a!"
		if rotateSwitches:
			if "!r!" in label:
				r = newLabel.index("!r!")
				newLabel = newLabel[:r] + newLabel[r+3:]
			else:
				newLabel = newLabel + "!r!"
		result.append(newLabel)
	labels = result

def fixRotations(): #changes rotation data to actual coordinates from keyunit values
	global props
	result = []
	for prop in props:
		if prop[4][2] == 0:
			newRotation = False
		else:
			newRotation = (prop[4][0]*KEYUNIT, -prop[4][1]*KEYUNIT, -prop[4][2])
		result.append((prop[0], prop[1], prop[2], prop[3], newRotation))
	props = result

#Output file methods

def save(saveAttempt=1):
	global doc
	global fileName
	if fileName[-6:] != ".FCStd":
		fileName = fileName + ".FCStd"
	saveAs = savePath + fileName
	if os.path.exists(saveAs):
		if saveAttempt == 1:
			fileName = fileName[:-6] + "(2).FCStd"
		else:
			i = fileName.find("("+ str(saveAttempt) +")")
			fileName = "{}({}).FCStd".format(fileName[:i], str(saveAttempt + 1))
		print ("File already exists. Saving as " + fileName)
		save(saveAttempt + 1)
	else:
		doc.saveAs(saveAs)
		print ("Successfully saved to " + saveAs)

def intersection():
	global fileName
	try:
		print("")
		print("You can now perform an intersection operation to make the final plate part.")
		print("This can take 5-20 minutes.")
		print("Please check the file first to confirm that it turned out as expected.")
		performIntersection = util.strtobool(raw_input("Perform part join now? : "))
		if performIntersection:
			joinAllParts()
			fileName = fileName[:-6] + "(Final).FCStd"
			print("")
			save()
		else:
			pass
	except ValueError:
		print("Incorrect truth value (try y or n)")
		intersection()

#global variables
doc = None
sketchCount = 0
props = [] #tuple for each switch, (x,y,w,h,(rx,ry,r))
labels = []	#labels for each switch from the layout editor
#################
import sys
import os
import math
from distutils import util
if FREECADBINPATH:
	sys.path.append(FREECADBINPATH)
if FREECADLIBPATH:
	sys.path.append(FREECADLIBPATH)
################
try:
	import FreeCAD
	import Sketcher
except Exception:
	print ("error finding FreeCAD")
else:
	main()



