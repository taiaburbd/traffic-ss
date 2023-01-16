import random
import time
import threading
import pygame
import sys
import os

# Default values of signal timers
defaultGreen = {0:10, 1:10, 2:10, 3:10}
defaultYellow = 5
defaultRed = defaultGreen[0]+defaultGreen[1]+defaultGreen[2]+defaultGreen[3]+4*defaultYellow

signals = []
noOfSignals = 2
currentGreen = 0   # Indicates which signal is green currently
nextGreen = (currentGreen+1)%noOfSignals    # Indicates which signal will turn green next
currentYellow = 0   # Indicates whether yellow signal is on or off 

speeds = {'car':5, 'bike':3, 'scooter':2}  # average speeds of vehicles

# Coordinates of vehicles' start
x = {'right':[80,80,80], 'down':[1360,1360,1360], 'left':[1440,1440,1440], 'up':[-40,-40,-40]}    
y = {'right':[-20,-20,-20], 'down':[-20,-20,-20], 'left':[690,690,690], 'up':[660,660,660]}

vehicles = {'right': {0:[], 1:[], 2:[], 'crossed':0}, 'down': {0:[], 1:[], 2:[], 'crossed':0}, 'left': {0:[], 1:[], 2:[], 'crossed':0}, 'up': {0:[], 1:[], 2:[], 'crossed':0}}
vehicleTypes = {0:'car', 1:'bike', 2:'scooter'}
directionNumbers = {0:'right', 1:'down', 2:'left', 3:'up'}

# Coordinates of signal image, timer, and vehicle count
signalCoods = [(700,205),(600,250),(700,310),(790,255)]
signalTimerCoods = [(720,180),(570,270),(720,390),(830,275)]
PedCoods = [(600,155),(500,300),(870,290),(790,155)]
StandCoods = [(600,185),(500,320),(870,320),(790,175)]
WalkCoods = [(560,215),(550,350),(830,360),(840,205)]

# Coordinates of stop lines
stopLines = {'right': 600, 'down': 250, 'left': 840, 'up': 390}
defaultStop = {'right': 580, 'down': 240, 'left': 850, 'up': 400}

# Gap between vehicles
stoppingGap = 10    # stopping gap
movingGap = 10   # moving gap

# set allowed vehicle types here
allowedVehicleTypes = {'car': True, 'bike': True, 'scooter': True}
allowedVehicleTypesList = []
vehiclesTurned = {'right': {1:[], 2:[]}, 'down': {1:[], 2:[]}, 'left': {1:[], 2:[]}, 'up': {1:[], 2:[]}}
vehiclesNotTurned = {'right': {1:[], 2:[]}, 'down': {1:[], 2:[]}, 'left': {1:[], 2:[]}, 'up': {1:[], 2:[]}}
rotationAngle = 3
mid = {'right': {'x':590, 'y':300}, 'down': {'x':735, 'y':305}, 'left': {'x':600, 'y':345}, 'up': {'x':695, 'y':320}}

timeElapsed = 0
simulationTime = 300
timeElapsedCoods = (1100,50)
vehicleCountTexts = ["0", "0", "0", "0"]
vehicleCountCoods = [(480,210),(880,210),(880,550),(480,550)]

alertMsg="Warning: Be Alert "


pygame.init()
pygame.mixer.init()
simulation = pygame.sprite.Group()
beep=pygame.mixer.Sound("beep.mp3")

class TrafficSignal:
    def __init__(self, red, yellow, green):
        self.red = red
        self.yellow = yellow
        self.green = green
        self.signalText = ""
        
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, lane, vehicleClass, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicleClass = vehicleClass
        self.speed = speeds[vehicleClass]
        self.direction_number = direction_number
        self.direction = direction
        self.x = x[direction][lane]
        self.y = y[direction][lane]
        self.crossed = 0
        self.willTurn = will_turn
        self.turned = 0
        self.rotateAngle = 0
        vehicles[direction][lane].append(self)
        self.index = len(vehicles[direction][lane]) - 1
        self.crossedIndex = 0
        path = "images/" + direction + "/" + vehicleClass + ".png"
        self.originalImage = pygame.image.load(path)
        self.image = pygame.image.load(path)

        if(len(vehicles[direction][lane])>1 and vehicles[direction][lane][self.index-1].crossed==0):   
            if(direction=='right'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                - vehicles[direction][lane][self.index-1].image.get_rect().width 
                - stoppingGap
            elif(direction=='left'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                + vehicles[direction][lane][self.index-1].image.get_rect().width 
                + stoppingGap
            elif(direction=='down'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                - vehicles[direction][lane][self.index-1].image.get_rect().height 
                - stoppingGap
            elif(direction=='up'):
                self.stop = vehicles[direction][lane][self.index-1].stop 
                + vehicles[direction][lane][self.index-1].image.get_rect().height 
                + stoppingGap
        else:
            self.stop = defaultStop[direction]
        simulation.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        if(self.direction=='right'):
            if(self.crossed==0 and self.x+self.image.get_rect().width>stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.x+self.image.get_rect().width<stopLines[self.direction]+120):
                    if((self.x+self.image.get_rect().width<=self.stop or (currentGreen==0 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.x+self.image.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):               
                        self.x += self.speed
                        self.y += 0.5*self.speed
                else:
                    if(self.turned==0):
                            self.turned = 1
                            self.x += 20
                            self.y -= 10
                            self.image = pygame.image.load("images/up/" + self.vehicleClass + ".png")
                            vehiclesTurned[self.direction][self.lane].append(self)
                            self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                    else:
                        if(self.crossedIndex==0 or (self.y>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().height + movingGap))):
                            self.y -= 0.5*self.speed
                            self.x += self.speed
            else: 
                if(self.crossed == 0):
                    if((self.x+self.image.get_rect().width<=self.stop or (currentGreen==0 and currentYellow==0)) and (self.index==0 or self.x+self.image.get_rect().width<(vehicles[self.direction][self.lane][self.index-1].x - movingGap))):                
                        self.x += self.speed
                        self.y += 0.5*self.speed
                else:
                    if((self.crossedIndex==0) or (self.x+self.image.get_rect().width<(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].x - movingGap))):                 
                        self.x += self.speed
                        self.y += 0.5*self.speed
        #----------------------------------------------------------------------------------------
        elif(self.direction=='down'):
            if(self.crossed==0 and self.y+self.image.get_rect().height>stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.y+self.image.get_rect().height<stopLines[self.direction]+70):
                    if((self.y+self.image.get_rect().height<=self.stop or (currentGreen==1 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                        self.y += 0.5*self.speed
                        self.x -= self.speed
                else:   
                    if(self.turned==0):
                        self.x +=20
                        self.y +=10
                        self.turned = 1
                        self.image = pygame.image.load("images/right/" + self.vehicleClass + ".png")
                        vehiclesTurned[self.direction][self.lane].append(self)
                        self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                    else:
                        if(self.crossedIndex==0 or ((self.x + self.image.get_rect().width) < (vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x - movingGap))):
                            self.x += self.speed
                            self.y += 0.5*self.speed
            else: 
                if(self.crossed == 0):
                    if((self.y+self.image.get_rect().height<=self.stop or (currentGreen==1 and currentYellow==0)) and (self.index==0 or self.y+self.image.get_rect().height<(vehicles[self.direction][self.lane][self.index-1].y - movingGap))):                
                        self.y += 0.5*self.speed
                        self.x -= self.speed
                else:
                    if((self.crossedIndex==0) or (self.y+self.image.get_rect().height<(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].y - movingGap))):                
                        self.y += 0.5*self.speed
                        self.x -= self.speed
        #----------------------------------------------------------------------------------------
        elif(self.direction=='left'):
            if(self.crossed==0 and self.x<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.x>stopLines[self.direction]-140):
                    if((self.x>=self.stop or (currentGreen==0 and currentYellow==0) or self.crossed==1) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):                
                        self.x -= self.speed
                        self.y -= 0.5*self.speed
                else: 
                    if(self.turned==0):
                        self.x -=20
                        self.y +=10
                        self.turned = 1
                        self.image = pygame.image.load("images/down/" + self.vehicleClass + ".png")
                        vehiclesTurned[self.direction][self.lane].append(self)
                        self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                    else:
                        if(self.crossedIndex==0 or ((self.y + self.image.get_rect().height) <(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].y  -  movingGap))):
                            self.y += 0.5*self.speed
                            self.x -= self.speed
            else: 
                if(self.crossed == 0):
                    if((self.x>=self.stop or (currentGreen==0 and currentYellow==0)) and (self.index==0 or self.x>(vehicles[self.direction][self.lane][self.index-1].x + vehicles[self.direction][self.lane][self.index-1].image.get_rect().width + movingGap))):                
                        self.x -= self.speed
                        self.y -= 0.5*self.speed
                else:
                    if((self.crossedIndex==0) or (self.x>(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].x + vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width + movingGap))):                
                        self.x -= self.speed
                        self.y -= 0.5*self.speed
        #----------------------------------------------------------------------------------------
        elif(self.direction=='up'):
            if(self.crossed==0 and self.y<stopLines[self.direction]):
                self.crossed = 1
                vehicles[self.direction]['crossed'] += 1
                if(self.willTurn==0):
                    vehiclesNotTurned[self.direction][self.lane].append(self)
                    self.crossedIndex = len(vehiclesNotTurned[self.direction][self.lane]) - 1
            if(self.willTurn==1):
                if(self.crossed==0 or self.y>stopLines[self.direction]-80):
                    if((self.y>=self.stop or (currentGreen==1 and currentYellow==0) or self.crossed == 1) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height +  movingGap) or vehicles[self.direction][self.lane][self.index-1].turned==1)):
                        self.y -= 0.5*self.speed
                        self.x += self.speed
                else:   
                    if(self.turned==0):
                        self.x -=20
                        self.y -=10
                        self.turned = 1
                        self.image = pygame.image.load("images/left/" + self.vehicleClass + ".png")
                        vehiclesTurned[self.direction][self.lane].append(self)
                        self.crossedIndex = len(vehiclesTurned[self.direction][self.lane]) - 1
                    else:
                        if(self.crossedIndex==0 or (self.x>(vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].x + vehiclesTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().width + movingGap))):
                            self.x -= self.speed
                            self.y -= 0.5*self.speed
            else: 
                if(self.crossed == 0):
                    if((self.y>=self.stop or (currentGreen==1 and currentYellow==0)) and (self.index==0 or self.y>(vehicles[self.direction][self.lane][self.index-1].y + vehicles[self.direction][self.lane][self.index-1].image.get_rect().height + movingGap))):                
                        self.y -= 0.5*self.speed
                        self.x += self.speed
                else:
                    if((self.crossedIndex==0) or (self.y>(vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].y + vehiclesNotTurned[self.direction][self.lane][self.crossedIndex-1].image.get_rect().height + movingGap))):                
                        self.y -= 0.5*self.speed 
                        self.x += self.speed

# Initialization of signals with default values
def initialize():
    ts1 = TrafficSignal(0, defaultYellow, defaultGreen[0])
    signals.append(ts1)
    ts2 = TrafficSignal(ts1.red+ts1.yellow+ts1.green, defaultYellow, defaultGreen[1])
    signals.append(ts2)
    repeat()


def repeat():
    global currentGreen, currentYellow, nextGreen
    while(signals[currentGreen].green>0):   # while the timer of current green signal is not zero
        #printStatus()
        updateValues()
        time.sleep(1)
    currentYellow = 1   # set yellow signal on
    # reset stop coordinates of lanes and vehicles 
    for i in range(0,3):
        for vehicle in vehicles[directionNumbers[currentGreen]][i]:
            vehicle.stop = defaultStop[directionNumbers[currentGreen]]
    while(signals[currentGreen].yellow>0):  # while the timer of current yellow signal is not zero
        #printStatus()
        updateValues()
        time.sleep(1)
    currentYellow = 0   # set yellow signal off
    
    signals[currentGreen].green = defaultGreen[currentGreen]
    signals[currentGreen].yellow = defaultYellow
    signals[currentGreen].red = defaultRed
    
    currentGreen = nextGreen # set next signal as green signal
    nextGreen = (currentGreen+1)%noOfSignals    # set next green signal
    signals[nextGreen].red = signals[currentGreen].yellow+signals[currentGreen].green    # set the red time of next to next signal as (yellow time + green time) of next signal
    repeat()

# Update values of the signal timers after every second
def updateValues():
    for i in range(0, noOfSignals):
        if(i==currentGreen):
            if(currentYellow==0):
                signals[i].green-=1
            else:
                signals[i].yellow-=1
        else:
            signals[i].red-=1

# Generating vehicles in the simulation
def generateVehicles():
    while(True):
        vehicle_type = random.choice(allowedVehicleTypesList)
        lane_number =  1 #random.randint(1,2)
        will_turn = random.randint(0,1)
        direction_number = random.randint(0,3)
        Vehicle(lane_number, vehicleTypes[vehicle_type], direction_number, directionNumbers[direction_number], will_turn)
        time.sleep(1)

def showStats():
    totalVehicles = 0
    print('Direction-wise Vehicle Counts')
    for i in range(0,4):
        if(signals[i]!=None):
            print('Direction',i+1,':',vehicles[directionNumbers[i]]['crossed'])
            totalVehicles += vehicles[directionNumbers[i]]['crossed']
    print('Total vehicles passed:',totalVehicles)
    print('Total time:',timeElapsed)

def simTime():
    global timeElapsed, simulationTime
    while(True):
        timeElapsed += 1
        time.sleep(1)
        if(timeElapsed==simulationTime):
            showStats()
            os._exit(1) 

class Main:
    global allowedVehicleTypesList
    i = 0
    for vehicleType in allowedVehicleTypes:
        if(allowedVehicleTypes[vehicleType]):
            allowedVehicleTypesList.append(i)
        i += 1
    thread1 = threading.Thread(name="initialization",target=initialize, args=())    # initialization
    thread1.daemon = True
    thread1.start()

    # Colours 
    black = (0, 0, 0)
    white = (255, 255, 255)
    blue = (0,255,255)

    # Screensize 
    screenWidth = 1400
    screenHeight = 800
    screenSize = (screenWidth, screenHeight)

    # Setting background image i.e. image of intersection
    background = pygame.image.load('images/map.png')

    screen = pygame.display.set_mode(screenSize)
    pygame.display.set_caption("Traffic Signal Simulation")

    # Loading signal images and font
    redSignal = pygame.image.load('images/signals/red.png')
    yellowSignal = pygame.image.load('images/signals/yellow.png')
    greenSignal = pygame.image.load('images/signals/green.png')
    redWalk = pygame.image.load('images/signals/red_walk.png')
    greenWalk = pygame.image.load('images/signals/green_walk.png')
    menStand = pygame.image.load('images/walk/men_stand.png')
    menWalk = pygame.image.load('images/walk/men_walk.png')
    
    font = pygame.font.Font(None, 30)
    thread2 = threading.Thread(name="generateVehicles",target=generateVehicles, args=())    # Generating vehicles
    thread2.daemon = True
    thread2.start()

    thread3 = threading.Thread(name="simTime",target=simTime, args=()) 
    thread3.daemon = True
    thread3.start()
    alertText=font.render(alertMsg, True, "#FFFFFF", "#880808")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                showStats()
                sys.exit()

        screen.blit(background,(0,0))   # display background in simulation
        for i in range(0,noOfSignals):  # display signal and set timer according to current status: green, yello, or red
            if i == 1: 
                yellow_use = pygame.transform.flip(yellowSignal, True, False)
                green_use = pygame.transform.flip(greenSignal, True, False)
                red_use = pygame.transform.flip(redSignal, True, False)
                green_walk_use = greenWalk
                red_walk_use = redWalk
                men_Walk_use = menWalk
                men_Stand_use = menStand
            if i == 0:
                yellow_use = yellowSignal
                green_use = greenSignal
                red_use = redSignal
                green_walk_use = pygame.transform.flip(greenWalk, True, False)
                red_walk_use = pygame.transform.flip(redWalk, True, False)
                men_Walk_use = pygame.transform.flip(menWalk, True, False)
                men_Stand_use = pygame.transform.flip(menStand, True, False)
            if(i==currentGreen):
                if(currentYellow==1):
                    signals[i].signalText = signals[i].yellow
                    screen.blit(yellow_use, signalCoods[i])
                    screen.blit(yellow_use, signalCoods[i+2])
                    screen.blit(red_walk_use, PedCoods[i])
                    screen.blit(red_walk_use, PedCoods[i+2])
                    screen.blit(men_Stand_use, StandCoods[i])
                    screen.blit(men_Stand_use, StandCoods[i+2])

                else:
                    signals[i].signalText = signals[i].green
                    screen.blit(green_use, signalCoods[i])
                    screen.blit(green_use, signalCoods[i+2])
                    screen.blit(red_walk_use, PedCoods[i])
                    screen.blit(red_walk_use, PedCoods[i+2])
                    screen.blit(men_Stand_use, StandCoods[i])
                    screen.blit(men_Stand_use, StandCoods[i+2])

                    if(i==0):
                        screen.blit(men_Walk_use, WalkCoods[i])
                        screen.blit(alertText,(550,50))
                        beep.play()

            else:
                signals[i].signalText = signals[i].red
                screen.blit(red_use, signalCoods[i])
                screen.blit(red_use, signalCoods[i+2])
                screen.blit(green_walk_use, PedCoods[i])
                screen.blit(green_walk_use, PedCoods[i+2])
                screen.blit(men_Walk_use, WalkCoods[i])
                screen.blit(men_Walk_use, WalkCoods[i+2])

        signalTexts = ["","","",""]

        # display signal timer
        for i in range(0,noOfSignals):  
            signalTexts[i] = font.render((str(' ')+str(signals[i].signalText)+str(' ')), True, blue, black)
            screen.blit(signalTexts[i],signalTimerCoods[i])
            screen.blit(signalTexts[i],signalTimerCoods[i+2])

        # display vehicle count
        for i in range(0,noOfSignals):
            displayText = vehicles[directionNumbers[i]]['crossed']
            vehicleCountTexts[i] = font.render(str(displayText), True, black, white)
            #screen.blit(vehicleCountTexts[i],vehicleCountCoods[i])

    
        # display time elapsed
        timeElapsedText = font.render(("Time Elapsed: "+str(timeElapsed)), True, black, white)
        screen.blit(timeElapsedText,timeElapsedCoods)

        # display the vehicles
        for vehicle in simulation:  
            screen.blit(vehicle.image, [vehicle.x, vehicle.y])
            vehicle.move()
        pygame.display.update()


Main()
