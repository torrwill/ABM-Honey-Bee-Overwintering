''' Import Libraries and Modules '''
import sys
import random
from random import randrange
import pygame
import numpy as np
import pandas as pd
import timeit

''' Variables '''
# grid colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = [255, 0, 0]
GREEN = [0, 255, 0]
GRAY  = [127,127,127]

# grid measurements
WIDTH, HEIGHT, MARGIN = 10, 10, 1
GRIDX, GRIDY          = 100, 40

''' NumPy Settings '''
# needed to print the whole array
np.set_printoptions(threshold = sys.maxsize)


'''trail colors'''
rgbValues = []
for i in range(1, 101):
    rgbValues.append([255, 255, 255])
for j in range(1, 100):
    list_value = rgbValues[j]
    list_value[1] = round(list_value[1] - (j * 2.58))
    list_value[2] = round(list_value[2] - (j * 2.58))
#print("b: ", rgbValues)

def reversed(lst):
    lst.reverse()
    return lst

rgbValues = reversed(rgbValues)

#print("a: ", rgbValues)

colorList = np.array(rgbValues)

''' GridObject '''
# create an grid that aligns to an object;
# sets its position, velocity, size, and color
class GridObject(pygame.sprite.Sprite):
    def __init__(self, pos, grid, *groups):
        super().__init__(groups)

        # create image from grid
        self.grid = grid
        self.gridsize = (len(grid[0]), len(grid)) 
        imgsize = self.gridsize[0] * (WIDTH + MARGIN), self.gridsize[1] * (HEIGHT + MARGIN)
        self.image = pygame.Surface(imgsize, flags = pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        col = GRAY

        for c in range(self.gridsize[0]):
            for r in range(self.gridsize[1]):
                if self.grid[r][c] == 1:
                    rect = [(MARGIN + WIDTH) * c + MARGIN, (MARGIN + HEIGHT) * r + MARGIN, WIDTH, HEIGHT]
                    pygame.draw.rect(self.image, col, rect)

        self.rect = self.image.get_rect(center = pos)
        self.vel = pygame.math.Vector2(8, 0).rotate(randrange(360))
        self.pos = pygame.math.Vector2(pos)
    
    # as the object moves to a new tile in that grid,
    # the function will update the position, velocity,
    # and decrease the overlapped tile's value by 1
    def update(self, boundrect, hitGrid, hitList):
        self.pos += self.vel
        self.rect.center = self.pos
        
        if self.rect.left <= boundrect.left or self.rect.right >= boundrect.right:
            self.vel.x *= -1                            
        if self.rect.top <= boundrect.top or self.rect.bottom >= boundrect.bottom:
            self.vel.y *= -1     

        # align rect to grid
        gridpos = round(self.rect.x / (WIDTH + MARGIN)), round(self.rect.y / (HEIGHT + MARGIN))
        self.rect.topleft = gridpos[0] * (WIDTH + MARGIN), gridpos[1] * (HEIGHT + MARGIN)

        # increment touched filled
        global max_hit # not declared as a global? Check this
        max_hit = 100
        
        oldHitList = hitList[:]
        hitList = np.empty((GRIDX, GRIDY))
        for c in range(self.gridsize[0]):
            for r in range(self.gridsize[1]):
                p = np.array((gridpos[1] + r, gridpos[0] + c))
                # p = np.asarray(p) # tuple to vector
                # print("p is equal to: ", p)
                if p in oldHitList:
                    hitList = np.append(hitList, p)
                    # print("First if statement hitList", hitList)
                elif self.grid[r][c] == 1:
                    if p[0] < len(hitGrid) and p[1] < len(hitGrid[p[0]]):
                        # print("Is ", p[0], " < ", len(hitGrid), "?",
                        #       "\nIs", p[1], " < ", len(hitGrid[p[0]]), "?")
                        hitList = np.append(hitList, p)
                        # print("Second if statement hitList", hitList)
                        if p not in oldHitList:
                            hitGrid[p[0]][p[1]] -= 1
                            # print("p is: ", p,". hitGrid[p[0]][p[1]] is: ",hitGrid[p[0]][p[1]], "\n")
                            max_hit = min(max_hit, hitGrid[p[0]][p[1]])

def drawGrid(screen, hitGrid, colorList):
    # Draw the grid to the screen
    for row in range(GRIDY):
        for column in range(GRIDX):
            rect = [(MARGIN + WIDTH) * column + MARGIN,
                    (MARGIN + HEIGHT) * row + MARGIN, WIDTH, HEIGHT]

            color = colorList[min(len(colorList)-1, hitGrid[row][column])]
            
            pygame.draw.rect(screen, color, rect)

# size of the ball
ballGrid = np.full((5, 5), 1) # change to ((5,5),1) for radius = 5

''' Timers '''
def endProgramTimer():
    start = timeit.default_timer()
    stop = timeit.default_timer()
    endString = ("Time (in seconds):", stop)
    print(endString)

''' Degree Changes | Rotation '''
class degreesForDaysTemps():
    def setAngles(self):
        # generate an array for degrees from 0 to 360, in 30 degree increments
        # Equiv: angles = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330]
        radians = np.arange(12)*np.pi/6
        angles = np.degrees(radians)
        return angles

    def changeAngle(self, ball):
        angles = degreesForDaysTemps.setAngles(self)
        # change angle by 30°
        ball.vel = ball.vel.rotate(angles[randrange(0, len(angles))])

''' sendDataToCSV '''
# send hitGrid to excel file
def sendDataToCSV(hitGrid):
    hitGrid_DF = pd.DataFrame(hitGrid)
    filepath = 'TestFile.csv'
    hitGrid_DF.to_csv(filepath, index = False)


''' Main '''
def main():
    # create window
    screen = pygame.display.set_mode((GRIDX * (WIDTH+MARGIN) + MARGIN, GRIDY * (HEIGHT+MARGIN) + 50), pygame.RESIZABLE)
    pygame.display.set_caption("ABM-Honey-Bee-Overwintering")
    clock = pygame.time.Clock()

    # create ball and grids
    sprite_group = pygame.sprite.Group()
    ball = GridObject((screen.get_width()//2, screen.get_height()//2), ballGrid, sprite_group)
    hitGrid = np.full((GRIDY, GRIDX), 100)
    #print(hitGrid.shape)
    hitList = np.empty((GRIDY, GRIDX))
    
    # create timer event
    change_delay = 10000 # 10 second(s)
    change_event = pygame.USEREVENT + 1
    pygame.time.set_timer(change_event, change_delay)
    
    # generate degrees that will be manipulated by temp data
    changeDegrees = degreesForDaysTemps()
    changeDegrees.setAngles()

    ''' import temperature and day data '''
    # get day and temp from excel file
    df = pd.read_csv('temperature-data.csv')
    JFK = df.iloc[0:366,:]
    UPTON = df.iloc[368:734,:]
    CENTRALPARK = df.iloc[736:1101,:]
    Areas = [JFK, UPTON, CENTRALPARK]
    #print(len(Areas))

    sheet_number = random.choice(Areas)
    #print(sheet_number)
    sheet = np.array(sheet_number)
    #print(sheet)
    sheet_rows = (len(sheet[0:-1,:])+1)
    #print(sheet_rows)

    ''' change temps and days from floats to int '''
    temps_float = np.empty(0)
    temps = temps_float.astype(int)
    days_float = np.empty(0)
    days = days_float.astype(int)
    day = 0
    for k in range(1, sheet_rows):
        temps = np.append(temps, sheet[k][-3])
        days = np.append(days, sheet[k][-1])
        # print(temps, "\n", days)
        
    #print("REMINDER: Day 0 is the first day of the simulation.")
    
    done = False
    degreeChange = 0

    ''' get day/temp for visualization '''
    #print("day: ", days[day])
    #print("temp: ", temps[day])
    d = ("day: ", str(days[day]))
    t = ("temp: ", str(temps[day]))


    ''' main while loop '''
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                sendDataToCSV(hitGrid)
                endProgramTimer()
            
            # change angle based on timer event
            if event.type == change_event:
                degreeChange += 1
                if degreeChange == 1:
                    degreeChange = degreeChange - 1
                    day += 1
                    
                    #print("day: ", days[day])
                    #print("temp: ", temps[day])
                    d = ("day: ", str(days[day]))
                    t = ("temp: ", str(temps[day]))
                    

                changeDegrees.changeAngle(ball)

        screen.fill(BLACK)

        # Draw Grid
        drawGrid(screen, hitGrid, colorList)

        '''draw Days and Temp'''
        # create a font object.
        font = pygame.font.Font('freesansbold.ttf', (20))
        # create a text suface object,
        text = font.render("".join(d) + ", " + "".join(t) +"°F", True, WHITE, BLACK)
        # create a rectangular text object
        textRect = text.get_rect()
        # set the center of the rectangular object.
        textRect.center = ((GRIDX * (WIDTH + MARGIN)+50) // 2, (GRIDY * (HEIGHT + MARGIN))+25) 

        ''' end program '''
        # stops program if the max Hit or Day is reached
        bounding_box = pygame.Rect(0,0,(GRIDX * (WIDTH + MARGIN) + MARGIN), (GRIDY * (HEIGHT + MARGIN)))
        sprite_group.update(bounding_box, hitGrid, hitList)

        alive = True
        
        if max_hit == 0:
            alive = False

        if day == 100:
            alive = True
            
        if max_hit == 0 or day == 100:
            endProgramTimer()
            sendDataToCSV(hitGrid)
            done = True

        sprite_group.draw(screen)
        screen.blit(text, textRect)

        pygame.display.update()
        clock.tick(30)
        
    #print(hitGrid) # LINE IS JUST FOR DEBUGGING
    print("Alive? : ",alive)

if __name__ == '__main__':
    pygame.init()
    main()
    pygame.quit()
    sys.exit()
