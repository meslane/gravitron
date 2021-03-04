import math
import time
import pygame
import json
import sys

import threading

import phys
import gui

def main(argv):
    ###SETUP
    pygame.init()

    pygame.display.set_caption("Gravitron")
    screen = pygame.display.set_mode([1280,720], pygame.RESIZABLE)
    pfont = pygame.font.SysFont("Consolas", 14)
    bfont = pygame.font.SysFont("Arial", 32)
    
    pausebox = bfont.render("PAUSED", True, (255,255,255))
    menubox = bfont.render("Add Object", True, (255,255,255))
    
    rcolor1 = (128,128,128)
    rcolor2 = (128,128,255)
    
    bdims = (180, 50)
    bspace = 110
    
    mrects = []
    
    mrects.append(gui.entrybox((int(screen.get_width()/2) - bspace, 120), bdims, rcolor1, rcolor2, bfont, "", bfont, "Mass", 9)) #text boxes for menu
    mrects.append(gui.entrybox((int(screen.get_width()/2) + bspace, 120), bdims, rcolor1, rcolor2, bfont, "", bfont, "Radius", 9))
    mrects.append(gui.entrybox((int(screen.get_width()/2) - bspace, 240), bdims, rcolor1, rcolor2, bfont, "", bfont, "X", 9))
    mrects.append(gui.entrybox((int(screen.get_width()/2) + bspace, 240), bdims, rcolor1, rcolor2, bfont, "", bfont, "Y", 9))
    mrects.append(gui.entrybox((int(screen.get_width()/2) - bspace, 360), bdims, rcolor1, rcolor2, bfont, "", bfont, "V Mag.", 9))
    mrects.append(gui.entrybox((int(screen.get_width()/2) + bspace, 360), bdims, rcolor1, rcolor2, bfont, "", bfont, "V Angle", 9))
    mrects.append(gui.entrybox((int(screen.get_width()/2) - 150, 480), (100, 50), rcolor1, rcolor2, bfont, "", bfont, "R", 3))
    mrects.append(gui.entrybox((int(screen.get_width()/2), 480), (100, 50), rcolor1, rcolor2, bfont, "", bfont, "G", 3))
    mrects.append(gui.entrybox((int(screen.get_width()/2) + 150, 480), (100, 50), rcolor1, rcolor2, bfont, "", bfont, "B", 3))
    
    abutton = gui.clickButton((int(screen.get_width()/2), 600), (200, 50), (128, 200, 128), (128, 128, 200), bfont, "Add")
    
    tickslider = gui.slider((int(screen.get_width()/2) + 450, 120), (300, 25), (25, 50), (128, 128, 128), (200, 200, 200), bfont, "Time/Tick", ["1s", "10s", "1m", "10m", "1h"], [1, 10, 60, 600, 3600])
    frameslider = gui.slider((int(screen.get_width()/2) + 450, 300), (300, 25), (25, 50), (128, 128, 128), (200, 200, 200), bfont, "Time/Frame", ["1s", "10s", "1m", "1h", "1d"], [1, 10, 60, 3600, 86400])
    sscaleslider = gui.slider((int(screen.get_width()/2) + 450, 480), (300, 25), (25, 50), (128, 128, 128), (200, 200, 200), bfont, "Pixel Scale (m/px)", ["1", "1000", "1e6", "1e9", "1e12"], [1, 1000, 1e6, 1e9, 1e12])
    
    #bboxtest = gui.bodyBox((int(screen.get_width()/2) - 450, 120), (50, 50), (200, 128, 128), (128, 128, 200), (128, 128, 128), bfont, "-", (100,200,200), 30)
    
    bodylist = []
    
    with open(str(argv), 'r') as b:
        j = json.load(b)
        
    for b in j["bodies"]:
        bodylist.append(phys.body(b["mass"], tuple(b["position"]), tuple(b["velocity"]), tuple(b["color"]), b["size"]))
    
    tick = j["tick"]
    framePeriod = j["fperiod"]
    sscale = j["sscale"]
    
    bboxlist = []
    yp = 120
    for b in bodylist:
        bboxlist.append(gui.bodyBox((int(screen.get_width()/2) - 450, yp), (50, 50), (200, 128, 128), (128, 128, 200), (128, 128, 128), bfont, "-", b.color, b.size))
        yp += 60
    
    ###BEGIN MAIN LOOP
    t = 0
    changet = 0
    
    tpersec = 0
    lastsimsecs = 0
    lasttime = time.time()
    secsrate = 0
    
    xoffset = 0
    yoffset = 0
    
    framesDelivered = 0
    fps = 0
    
    loop = True
    paused = False
    inMenu = False
    while loop:
        for event in pygame.event.get(): #pygame event detection
            if event.type == pygame.QUIT:
                loop = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not inMenu: #pause simulation
                    if paused == False:
                        paused = True
                    else:
                        paused = False
                if event.key == pygame.K_r and not inMenu: #reset simulation
                    bodylist.clear()
                    for b in j["bodies"]:
                        bodylist.append(phys.body(b["mass"], tuple(b["position"]), tuple(b["velocity"]), tuple(b["color"]), b["size"]))
                    t = 0
                if event.key == pygame.K_ESCAPE: #add/remove body menu
                    if not inMenu:
                        inMenu = True
                        paused = True
                    else:
                        inMenu = False
                        
                if event.key == pygame.K_UP:
                    yoffset += 100
                elif event.key == pygame.K_DOWN:
                    yoffset -= 100
                elif event.key == pygame.K_RIGHT:
                    xoffset -= 100
                elif event.key == pygame.K_LEFT:
                    xoffset += 100
                
            if inMenu:
                for r in mrects:
                    r.getClick(event)
                    
                changet = t
                tick = tickslider.getSlide(event)
                framePeriod = frameslider.getSlide(event)
                sscale = sscaleslider.getSlide(event)
                
                for b in bboxlist:
                    if b.getClick(event):
                        del bodylist[bboxlist.index(b)]
                        del bboxlist[bboxlist.index(b)]
                
                if abutton.getClick(event): #if add button is clicked, attempt to add body
                    if (mrects[0].value() != 0):
                        bodylist.append(phys.body(mrects[0].value(), (mrects[2].value(), mrects[3].value()), (mrects[4].value(), math.radians(mrects[5].value())), (int(mrects[6].value()), int(mrects[7].value()), int(mrects[8].value())), mrects[1].value()))
                        bboxlist.append(gui.bodyBox((int(screen.get_width()/2) - 450, yp), (50, 50), (200, 128, 128), (128, 128, 200), (128, 128, 128), bfont, "-", (int(mrects[6].value()), int(mrects[7].value()), int(mrects[8].value())), mrects[1].value()))
                        
                    for m in mrects:
                        print(m.value())

        if inMenu == True: #do menu
            screen.fill((0,0,0))
            screen.blit(menubox, menubox.get_rect(center = (int(screen.get_width()/2),20)))
            
            mrects[0].updatePos((int(screen.get_width()/2) - bspace, 120))
            mrects[1].updatePos((int(screen.get_width()/2) + bspace, 120))
            mrects[2].updatePos((int(screen.get_width()/2) - bspace, 240))
            mrects[3].updatePos((int(screen.get_width()/2) + bspace, 240))
            mrects[4].updatePos((int(screen.get_width()/2) - bspace, 360))
            mrects[5].updatePos((int(screen.get_width()/2) + bspace, 360))
            mrects[6].updatePos((int(screen.get_width()/2) - 150, 480))
            mrects[7].updatePos((int(screen.get_width()/2), 480))
            mrects[8].updatePos((int(screen.get_width()/2) + 150, 480))
            
            abutton.updatePos((int(screen.get_width()/2), 600))

            tickslider.updatePos((int(screen.get_width()/2) + 450, 120))
            frameslider.updatePos((int(screen.get_width()/2) + 450, 300))
            sscaleslider.updatePos((int(screen.get_width()/2) + 450, 480))

            for r in mrects:
                r.disp(screen)
            
            abutton.disp(screen)

            tickslider.disp(screen)
            frameslider.disp(screen)
            sscaleslider.disp(screen)
            
            #display body list:
            yp = 120
            for b in bboxlist:
                b.updatePos((int(screen.get_width()/2 - 480), yp))
                b.dispWithBody(screen)
                yp += 60
                
            pygame.display.flip()
        
        elif ((t - changet) % framePeriod == 0 or paused == True): #render objects
            screen.fill((0,0,0))
            timebox = pfont.render("t = +{}y {}d {}h {}m {}s".format(math.floor(t / 31536000), math.floor((t % 31536000) / 86400), math.floor((t % 86400) / 3600), math.floor((t % 3600) / 60), (t % 60)), True, (255,255,255))
            sbox = pfont.render("Sim Secs/Real Secs = {}".format(secsrate), True, (255,255,255))
            fbox = pfont.render("Frames Per Second = {}".format(fps), True, (255,255,255))
            pbox = pfont.render("Center = ({}m,{}m)".format(int(-1 * xoffset * sscale), int(yoffset * sscale)), True, (255,255,255))
            screen.blit(timebox, (10, 10))
            screen.blit(sbox, (10, 30))
            screen.blit(fbox, (10, 50))
            screen.blit(pbox, (10, 70))
                
            for b in bodylist:
                try:
                    pygame.draw.circle(screen, b.color, (int(b.getPos()[0] / sscale) + int(screen.get_width()/2) + xoffset, int(b.getPos()[1] / sscale) + int(screen.get_height()/2) + yoffset), int(b.size * j["bscale"]))
                except TypeError:
                    pass
            
            if paused == True:
                screen.blit(pausebox, pausebox.get_rect(center = (int(screen.get_width()/2),20)))
            
            pygame.display.flip()
            framesDelivered += 1
                
        if not paused: #compute body interactions
            for b1 in bodylist:
                for b2 in bodylist:
                    if (b1 != b2):
                        b1.appendForce(b2)
            
            for b in bodylist:
                b.updateData(tick)
            
            if (time.time() - lasttime >= 1): #update time counter
                secsrate = t - lastsimsecs
                lastsimsecs = t
                lasttime = time.time()
                
                fps = framesDelivered
                framesDelivered = 0
                
            t += tick
    
if __name__ == "__main__":
    main(sys.argv[1])