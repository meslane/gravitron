import math
from os import system
import time
import pygame
import json
import sys

#units are metric (kg, meters, m/sec, newtons)

class entrybox:
    def __init__(self, pos, size, color, bfont, text, cfont, ctext):
        self.pos = pos
        self.size = size
        self.color = color
        
        self.caption = cfont.render(ctext, True, (255,255,255))
        self.text = bfont.render(text, True, (255, 255, 255))
        self.captionrect = self.caption.get_rect(center = (int(self.pos[0]) ,self.pos[1] - self.size[1]))
        
    def disp(self, screen):
        r = pygame.Rect(self.pos, self.size)
        r.center = self.pos
        pygame.draw.rect(screen, self.color, r, 0)
        screen.blit(self.caption, self.captionrect)

class body:
    def __init__(self, mass, position, velocity, color, size):
        self.mass = mass
        self.position = position #position coords
        
        self.forces = list() #list of force vectors on object
        self.accel = (0,0) #instantanious acceleration vector
        self.velocity = velocity
        self.color = color
        self.size = size #pixel radius
        
    def getMass(self):
        return self.mass
        
    def getPos(self):
        return self.position
      
    def appendForce(self, obj):
        self.forces.append((fg(self, obj), angle(self, obj)))
        
    def getNetForce(self):
        forceSum = (0,0)
        
        for force in self.forces:
            forceSum = addPolarVectors(forceSum, force)
            
        return forceSum
        
    def calculateAccel(self):
        f = self.getNetForce()
        self.accel = (f[0]/self.mass, f[1])
        return self.accel
        
    def calculateDisp(self, tick): #kinematic equation #3 
        v = (self.velocity[0] * tick, self.velocity[1])
       
        return addPolarVectors(v, ((0.5 * self.accel[0] * (tick ** 2)), self.accel[1]))
        
    def calculateVelocity(self, tick): #calculate body velocity based on tick interval (kinematic equation #1)
        self.velocity = addPolarVectors(self.velocity, (self.accel[0] * tick, self.accel[1]))
        return self.velocity
       
    def updateData(self, tick):
        self.calculateAccel()
        self.position = addRectVectors(self.position, polToRect(self.calculateDisp(tick)))
        self.calculateVelocity(tick)
        self.forces.clear() #clear list for next round of calcs
    
    def printData(self):
        print("Position: {}, {}".format(self.position[0], self.position[1]))
        print("Acceleration: {}, {}deg".format(self.accel[0], math.degrees(self.accel[1])))
        print("Velocity: {}, {}deg".format(self.velocity[0], math.degrees(self.velocity[1])))
        
    def symbol(self):
        return self.char
        
def distance(a, b): #distance between two bodies
    p1 = a.getPos()
    p2 = b.getPos()
    
    return math.sqrt(((p2[0] - p1[0]) ** 2) + ((p2[1] - p1[1]) ** 2))
    
def angle(a, b): #returns angle with respect to origin and first body (in radians)
    p1 = a.getPos()
    p2 = b.getPos()
    
    return math.atan2((p2[1] - p1[1]), (p2[0] - p1[0]))
    
def fg(a, b): #grav formula (returns force vector)
    g = 6.674e-11 #grav constant
    return g*(a.getMass() * b.getMass())/(distance(a,b) ** 2)
    
def polToRect(v):
    return (v[0]*math.cos(v[1]), v[0]*math.sin(v[1]))

def rectToPol(v):
    return (math.sqrt(v[0] ** 2 + v[1] ** 2), math.atan2(v[1], v[0]))
    
def addPolarVectors(v1, v2):
    v1 = polToRect(v1)
    v2 = polToRect(v2)
    
    return(rectToPol((v1[0] + v2[0], v1[1] + v2[1])))
    
def addRectVectors(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1])

def main(argv):
    pygame.init()

    pygame.display.set_caption("Gravitron")
    screen = pygame.display.set_mode([1280,720], pygame.RESIZABLE)
    pfont = pygame.font.SysFont("Consolas", 14)
    bfont = pygame.font.SysFont("Arial", 32)
    
    pausebox = bfont.render("PAUSED", True, (255,255,255))
    menubox = bfont.render("Add Object", True, (255,255,255))
    
    masstxt = bfont.render("Mass", True, (255,255,255))
    xpostxt = bfont.render("X Position", True, (255,255,255))
    ypostxt = bfont.render("Y Position", True, (255,255,255))
    vmagtxt = bfont.render("V Magnitude", True, (255,255,255))
    vangtxt = bfont.render("V Angle", True, (255,255,255))
    colortxt = bfont.render("Color (R,G,B)", True, (255,255,255))
    sizetxt = bfont.render("Radius", True, (255,255,255))

    bodylist = []
    
    with open(str(argv), 'r') as b:
        j = json.load(b)
        
    for b in j["bodies"]:
        bodylist.append(body(b["mass"], tuple(b["position"]), tuple(b["velocity"]), tuple(b["color"]), b["size"]))
    
    tick = j["tick"]
    framePeriod = j["fperiod"]
    
    t = 0
    loop = True
    paused = False
    inMenu = False
    while loop:
        for event in pygame.event.get(): #pygame event detection
            if event.type == pygame.QUIT:
                loop = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if paused == False:
                        paused = True
                    else:
                        paused = False
                if event.key == pygame.K_r: #reset simulation
                    bodylist.clear()
                    for b in j["bodies"]:
                        bodylist.append(body(b["mass"], tuple(b["position"]), tuple(b["velocity"]), tuple(b["color"]), b["size"]))
                    t = 0
                if event.key == pygame.K_ESCAPE: #add/remove body menu
                    if not inMenu:
                        inMenu = True
                        paused = True
                    else:
                        inMenu = False
                        

        if inMenu == True: #do menu
            screen.fill((0,0,0))
            screen.blit(menubox, menubox.get_rect(center = (int(screen.get_width()/2),20)))
            
            rects = []
            
            rects.append(entrybox((int(screen.get_width()/2) - 75, 120), (100, 50), (128,128,128), bfont, " ", bfont, "Mass"))
            rects.append(entrybox((int(screen.get_width()/2) + 75, 120), (100, 50), (128,128,128), bfont, " ", bfont, "Radius"))
            rects.append(entrybox((int(screen.get_width()/2) - 75, 240), (100, 50), (128,128,128), bfont, " ", bfont, "X"))
            rects.append(entrybox((int(screen.get_width()/2) + 75, 240), (100, 50), (128,128,128), bfont, " ", bfont, "Y"))
            rects.append(entrybox((int(screen.get_width()/2) - 75, 360), (100, 50), (128,128,128), bfont, " ", bfont, "V Mag."))
            rects.append(entrybox((int(screen.get_width()/2) + 75, 360), (100, 50), (128,128,128), bfont, " ", bfont, "V Angle"))
            rects.append(entrybox((int(screen.get_width()/2) - 150, 480), (100, 50), (128,128,128), bfont, " ", bfont, "R"))
            rects.append(entrybox((int(screen.get_width()/2), 480), (100, 50), (128,128,128), bfont, " ", bfont, "G"))
            rects.append(entrybox((int(screen.get_width()/2) + 150, 480), (100, 50), (128,128,128), bfont, " ", bfont, "B"))
            
            for r in rects:
                r.disp(screen)
                
            pygame.display.flip()
        
        elif (t % framePeriod == 0 or paused == True): #render objects
            screen.fill((0,0,0))
            timebox = pfont.render("t = +{}y {}d {}h {}m {}s".format(math.floor(t / 31536000), math.floor((t % 31536000) / 86400), math.floor((t % 86400) / 3600), math.floor((t % 3600) / 60), (t % 60)), True, (255,255,255))
            screen.blit(timebox, (10, 10))
                
            for b in bodylist:
                pygame.draw.circle(screen, b.color, (int(b.getPos()[0] / j["sscale"]) + int(screen.get_width()/2), int(b.getPos()[1] / j["sscale"]) + int(screen.get_height()/2)), int(b.size * j["bscale"]))
            
            if paused == True:
                screen.blit(pausebox, pausebox.get_rect(center = (int(screen.get_width()/2),20)))
            
            pygame.display.flip()
                
        if paused == False: #compute body interactions
            for b1 in bodylist:
                for b2 in bodylist:
                    if (b1 != b2):
                        b1.appendForce(b2)
            
            for b in bodylist:
                b.updateData(tick)
           
            t += tick
    
if __name__ == "__main__":
    main(sys.argv[1])