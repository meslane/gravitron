import pygame

class box: #base class for box object
    def __init__(self, pos, size, rcolor, ccolor, tfont, text):
        self.pos = pos
        self.size = size
        self.rcolor = rcolor
        self.ccolor = ccolor
        self.color = rcolor
        
        self.tfont = tfont
        self.text = text
        
        self.r = pygame.Rect(self.pos, self.size)
        self.r.center = self.pos
        
        self.inFocus = False
        
    def updatePos(self, newpos):
        self.pos = newpos
        self.r.center = self.pos

class slider:
    def __init__(self, pos, railSize, boxSize, railColor, boxColor, cfont, caption, optionsList, valueList):
        self.pos = pos
        self.railSize = railSize
        self.boxSize = boxSize
        self.railColor = railColor
        self.boxColor = boxColor
        self.cfont = cfont
        self.caption = caption
        self.optionsList = optionsList
        self.valueList = valueList
        
        self.rail = pygame.Rect(self.pos, self.railSize)
        self.rail.center = self.pos
        
        self.box = pygame.Rect(self.pos, self.boxSize)
        self.box.center = (self.rail.left, self.pos[1])
        
        self.sliding = False
        self.boxoffset = -1 * int(self.railSize[0] / 2)
        
        self.optlist = []
        self.rectlist = []
        
        self.vindex = 0
        
    def updatePos(self, newpos):
        self.pos = newpos
        self.rail.center = newpos
        self.box.center = (newpos[0] + self.boxoffset,newpos[1])
        
    def disp(self, screen):
        cap = self.cfont.render(self.caption, True, (255,255,255))
        crect = cap.get_rect(center = (self.pos[0] ,self.pos[1] - self.boxSize[1]))
        
        #set up slider increments
        self.optlist.clear()
        self.rectlist.clear()
        entryspace = int(self.railSize[0] / (len(self.optionsList) - 1))
        entrylocation = (self.rail.left, self.pos[1] + self.boxSize[1])
        
        entry = 0
        for o in self.optionsList:
            self.optlist.append(self.cfont.render(str(o), True, (255,255,255)))
            self.rectlist.append(self.optlist[entry].get_rect(center = entrylocation))
            
            screen.blit(self.optlist[entry], self.rectlist[entry])
            
            entrylocation = (entrylocation[0] + entryspace, entrylocation[1])
            entry += 1
        
        screen.blit(cap, crect)
        pygame.draw.rect(screen, self.railColor, self.rail, 0)
        pygame.draw.rect(screen, self.boxColor, self.box, 0)
        
    def getSlide(self, event): #snap to selection
        if self.sliding:
            i = 0
            closest = self.rectlist[0]
            for r in self.rectlist:
                if abs(r.center[0] - pygame.mouse.get_pos()[0]) <= abs(closest.center[0] - pygame.mouse.get_pos()[0]):
                    closest = r
                    self.vindex = i
                
                i += 1
                
            #print(closest.center)
            self.box.center = closest.center
            self.boxoffset = closest.center[0] - self.rail.center[0] #offset distance from center
    
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.box.collidepoint(event.pos):
                self.sliding = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.sliding = False
        
        return self.valueList[self.vindex]

class entrybox(box): #box that you can enter text into
    def __init__(self, pos, size, rcolor, ccolor, tfont, text, cfont, ctext, txtlen, acceptableChars):
        super().__init__(pos, size, rcolor, ccolor, tfont, text)
      
        self.cfont = cfont
        self.ctext = ctext
        
        self.txtlen = txtlen
        
        self.val = 0
        self.acceptableChars = acceptableChars
    
    def disp(self, screen):
        self.caption = self.cfont.render(self.ctext, True, (255,255,255))
        self.btext = self.tfont.render(self.text, True, (255, 255, 255))
        self.captionrect = self.caption.get_rect(center = (self.pos[0] ,self.pos[1] - self.size[1]))
        self.textrect = self.btext.get_rect(center = (self.pos[0] ,self.pos[1]))
    
        pygame.draw.rect(screen, self.color, self.r, 0)
        screen.blit(self.caption, self.captionrect)
        screen.blit(self.btext, self.textrect)
        
    def value(self):
        try: 
            return self.val
        except ValueError:
            return 0

    def getClick(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.r.collidepoint(event.pos):
                self.inFocus = True
                self.color = self.ccolor
            else:
                self.inFocus = False
                self.color = self.rcolor
        elif event.type == pygame.KEYDOWN and self.inFocus: #if button is clicked and the user types
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode in self.acceptableChars and len(self.text) < self.txtlen:
                self.text += event.unicode
                
            try:
                self.val = self.text
            except ValueError:
                pass
 
class clickButton(box): #box that you can click
    def __init__(self, pos, size, rcolor, ccolor, tfont, text):
        super().__init__(pos, size, rcolor, ccolor, tfont, text)
        
    def disp(self, screen):
        self.btext = self.tfont.render(self.text, True, (255, 255, 255))
        self.textrect = self.btext.get_rect(center = (self.pos[0] ,self.pos[1]))
        
        pygame.draw.rect(screen, self.color, self.r, 0)
        screen.blit(self.btext, self.textrect)
        
    def getClick(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.r.collidepoint(event.pos):
                self.inFocus = True
                self.color = self.ccolor
                
            return False
        elif event.type == pygame.MOUSEBUTTONUP and self.inFocus:
            self.inFocus = False
            self.color = self.rcolor
            
            return True
        else:
            return False

class bodyBox(clickButton):
    def __init__(self, pos, size, rcolor, ccolor, boxcolor, tfont, text, bcolor, bsize):
        super().__init__(pos, size, rcolor, ccolor, tfont, text)
        
        self.boxcolor = boxcolor
        
        self.bsize = int(bsize / 600000)
        self.bcolor = bcolor
        
        if self.bsize > 50:
            self.bsize = 50
        elif self.bsize < 5:
            self.bsize = 5
        
        self.outerrect = pygame.Rect(self.pos, (int(self.size[0] * 2) + 20, self.size[1] + 10))
        
    def dispWithBody(self, screen):
        self.outerrect.center = (self.r.center[0] - int(self.size[0] * 0.5) - 5, self.pos[1])
    
        pygame.draw.rect(screen, self.boxcolor, self.outerrect, 2)
        pygame.draw.rect(screen, self.color, self.r, 0)
        pygame.draw.circle(screen, self.bcolor, (self.r.center[0] - int(self.size[0]) - 5, self.pos[1]), self.bsize)
    
        self.btext = self.tfont.render(self.text, True, (255, 255, 255))
        self.textrect = self.btext.get_rect(center = (self.pos[0] ,self.pos[1]))
        screen.blit(self.btext, self.textrect)
