import math
import time
import pygame
import json
import sys
import copy

import phys
import gui

def saveToJson(bodies, filename):
    jdict = {
        "bodies": []
    }
    
    for b in bodies:
        btemp = {
            "mass": b.mass,
            "position": list(b.position),
            "velocity": list(b.velocity),
            "color": list(b.color),
            "size": b.size
        }
        
        jdict["bodies"].append(btemp)
    
    with open("{}.json".format(filename), "w") as f:
        json.dump(jdict, f, indent = 4)

def main():
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
    
    #Initial setup of menu elements
    mxcenter = int(screen.get_width()/2)
    numchars = ['-', '.', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'E', 'e']
    fchars = []
    
    fchars += numchars[2:-2]
    for c in range(65, 91): #fill out ascii
        fchars.append(chr(c))
        fchars.append(chr(c + 32))
    
    mrects.append(gui.entrybox((mxcenter - bspace, 120), bdims, rcolor1, rcolor2, bfont, "", bfont, "Mass", 9, numchars)) #text boxes for menu
    mrects.append(gui.entrybox((mxcenter + bspace, 120), bdims, rcolor1, rcolor2, bfont, "", bfont, "Size (px)", 9, numchars))
    mrects.append(gui.entrybox((mxcenter - bspace, 240), bdims, rcolor1, rcolor2, bfont, "", bfont, "X", 9, numchars))
    mrects.append(gui.entrybox((mxcenter + bspace, 240), bdims, rcolor1, rcolor2, bfont, "", bfont, "Y", 9, numchars))
    mrects.append(gui.entrybox((mxcenter - bspace, 360), bdims, rcolor1, rcolor2, bfont, "", bfont, "V Mag.", 9, numchars))
    mrects.append(gui.entrybox((mxcenter + bspace, 360), bdims, rcolor1, rcolor2, bfont, "", bfont, "V Angle", 9, numchars))
    mrects.append(gui.entrybox((mxcenter - 150, 480), (100, 50), rcolor1, rcolor2, bfont, "", bfont, "R", 3, numchars))
    mrects.append(gui.entrybox((mxcenter, 480), (100, 50), rcolor1, rcolor2, bfont, "", bfont, "G", 3, numchars))
    mrects.append(gui.entrybox((mxcenter + 150, 480), (100, 50), rcolor1, rcolor2, bfont, "", bfont, "B", 3, numchars))
    
    abutton = gui.clickButton((mxcenter, 600), (200, 50), (128, 200, 128), (128, 128, 200), bfont, "Add")
    
    tickslider = gui.slider((mxcenter + 450, 120), (300, 25), (25, 50), (128, 128, 128), (200, 200, 200), bfont, "Time/Tick", ["1s", "10s", "1m", "10m", "1h"], [1, 10, 60, 600, 3600])
    frameslider = gui.slider((mxcenter + 450, 300), (300, 25), (25, 50), (128, 128, 128), (200, 200, 200), bfont, "Time/Frame", ["1s", "10s", "1m", "1h", "1d"], [1, 10, 60, 3600, 86400])
    sscaleslider = gui.slider((mxcenter + 450, 480), (300, 25), (25, 50), (128, 128, 128), (200, 200, 200), bfont, "Pixel Scale (m/px)", ["1", "1000", "1e6", "1e9", "1e12"], [1, 1000, 1e6, 1e9, 1e12])

    filebox = gui.entrybox((mxcenter - 430, 480), (300, 50), rcolor1, rcolor2, bfont, "", bfont, "Filename", 15, fchars)
    loadbutton = gui.clickButton((mxcenter - 500, 600), (100, 50), (128, 200, 128), (128, 128, 200), bfont, "Load")
    savebutton = gui.clickButton((mxcenter - 360, 600), (100, 50), (128, 200, 128), (128, 128, 200), bfont, "Save")
      
    bodylist = []
    backuplist = []
    
    '''
    with open(str(argv), 'r') as b:
        j = json.load(b)
        
    for b in j["bodies"]:
        bdy = phys.body(b["mass"], tuple(b["position"]), tuple(b["velocity"]), tuple(b["color"]), b["size"])
        bodylist.append(bdy)
        backuplist.append(copy.deepcopy(bdy))
    '''
    
    tick = 1
    framePeriod = 1
    sscale = 1e9
    
    bboxlist = []
    for b in bodylist:
        bboxlist.append(gui.bodyBox((0,0), (50, 50), (200, 128, 128), (128, 128, 200), (128, 128, 128), bfont, "-", b.color, b.size))
    
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
        mxcenter = int(screen.get_width()/2) #reacquire screen center
    
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
                    bboxlist.clear()
                    for b in backuplist:
                        bodylist.append(copy.deepcopy(b))
                        bboxlist.append(gui.bodyBox((mxcenter - 450, yp), (50, 50), (200, 128, 128), (128, 128, 200), (128, 128, 128), bfont, "-", b.color, b.size))
                    t = 0
                    changet = 0
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
                    if b.getClick(event): #delete body if removed
                        del bodylist[bboxlist.index(b)]
                        del backuplist[bboxlist.index(b)]
                        del bboxlist[bboxlist.index(b)]
                
                if abutton.getClick(event): #if add button is clicked, attempt to add body
                    if (mrects[0].value() != 0):
                        bdy = phys.body(float(mrects[0].value()), (float(mrects[2].value()), float(mrects[3].value())), (float(mrects[4].value()), math.radians(float(mrects[5].value()))), (int(mrects[6].value()), int(mrects[7].value()), int(mrects[8].value())), int(mrects[1].value()))
                        
                        bodylist.append(bdy)
                        backuplist.append(copy.deepcopy(bdy))
                        bboxlist.append(gui.bodyBox((0, 0), (50, 50), (200, 128, 128), (128, 128, 200), (128, 128, 128), bfont, "-", (int(mrects[6].value()), int(mrects[7].value()), int(mrects[8].value())), int(mrects[1].value())))
                        
                    for m in mrects:
                        print(m.value())
                        
                filebox.getClick(event)
                
                #load and save files
                if loadbutton.getClick(event):
                    try:
                        with open("{}.json".format(str(filebox.value())), 'r') as f:
                            newsys = json.load(f)
                            
                            bodylist.clear()
                            bboxlist.clear()
                            backuplist.clear()
                            for b in newsys["bodies"]:
                                bdy = phys.body(b["mass"], tuple(b["position"]), tuple(b["velocity"]), tuple(b["color"]), b["size"])
                                bodylist.append(bdy)
                                backuplist.append(copy.deepcopy(bdy))
                                bboxlist.append(gui.bodyBox((0, 0), (50, 50), (200, 128, 128), (128, 128, 200), (128, 128, 128), bfont, "-", tuple(bdy.color), bdy.size))
                    except FileNotFoundError:    
                        print("File not found")
                elif savebutton.getClick(event):
                    saveToJson(bodylist, str(filebox.value()))
                
        if inMenu == True: #do menu
            screen.fill((0,0,0))
            
            screen.blit(menubox, menubox.get_rect(center = (mxcenter,20)))
            
            mrects[0].updatePos((mxcenter - bspace, 120))
            mrects[1].updatePos((mxcenter + bspace, 120))
            mrects[2].updatePos((mxcenter - bspace, 240))
            mrects[3].updatePos((mxcenter + bspace, 240))
            mrects[4].updatePos((mxcenter - bspace, 360))
            mrects[5].updatePos((mxcenter + bspace, 360))
            mrects[6].updatePos((mxcenter - 150, 480))
            mrects[7].updatePos((mxcenter, 480))
            mrects[8].updatePos((mxcenter + 150, 480))
            
            abutton.updatePos((mxcenter, 600))

            tickslider.updatePos((mxcenter + 450, 120))
            frameslider.updatePos((mxcenter + 450, 300))
            sscaleslider.updatePos((mxcenter + 450, 480))
            
            filebox.updatePos((mxcenter - 430, 480))
            loadbutton.updatePos((mxcenter - 500, 600))
            savebutton.updatePos((mxcenter - 360, 600))

            for r in mrects:
                r.disp(screen)
            
            abutton.disp(screen)

            tickslider.disp(screen)
            frameslider.disp(screen)
            sscaleslider.disp(screen)
            
            filebox.disp(screen)
            loadbutton.disp(screen)
            savebutton.disp(screen)
            
            #display body list (3*5 tiles currently):
            yp = 120
            xp = -520
            for b in bboxlist:
                b.updatePos((mxcenter + xp, yp))
                b.dispWithBody(screen)
                yp += 60
                
                if (yp >= 420):
                    yp = 120
                    xp += 120
                
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
                    pygame.draw.circle(screen, b.color, (int(b.getPos()[0] / sscale) + mxcenter + xoffset, int(b.getPos()[1] / sscale) + int(screen.get_height()/2) + yoffset), int(b.size * 0.5))
                except TypeError:
                    pass
            
            if paused == True:
                screen.blit(pausebox, pausebox.get_rect(center = (mxcenter,20)))
            
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
    main()