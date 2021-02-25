import math
from os import system
import time

#units are metric (kg, meters, m/sec, newtons)

class body:
    def __init__(self, mass, position, velocity, char):
        self.mass = mass
        self.position = position #position coords
        
        self.forces = list() #list of force vectors on object
        self.accel = (0,0) #instantanious acceleration vector
        self.velocity = velocity
        self.char = char
        
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

def main():
    bodylist = []
    
    bodylist.append(body(2e30, (0,0), (0,0), '*')) #sun
    bodylist.append(body(6e24, (150e9,0), (30000, 1.5708), 'e')) #earth
    bodylist.append(body(4.87e24, (0, 109e9), (35000, 3.14195), 'v')) #venus
    bodylist.append(body(3.29e23, (64e9, 0), (48000, 1.5708), 'm')) #mercury
    #bodylist.append(body(10e27, (180e9, 0), (10000, 1.5708), 'r'))
    
    tick = 1000
    t = 0
    while True:
        for b1 in bodylist:
            for b2 in bodylist:
                if (b1 != b2):
                    b1.appendForce(b2)
        
        for b in bodylist:
            b.updateData(tick)
       
        if (t % 86400 == 0):
            system("cls")
            grid = [[' ' for x in range(50)] for y in range(50)]
            for x in range(50):
                for y in range(50):
                    for b in bodylist:
                        if ((int(b.getPos()[0] / 10e9) + 25 == x and int(b.getPos()[1] / 10e9) + 25 == y)):
                            grid[y][x] = b.symbol()
                    print(grid[y][x], end = ' ')
                print()
                
            print("t={}\n".format(t))
        
        
        t += tick
    
if __name__ == "__main__":
    main()