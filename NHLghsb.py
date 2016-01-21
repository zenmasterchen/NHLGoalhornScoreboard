## TO DO
## -----
## X Horn playback threading (fixed with winsound.SND_ASYNC)
## ! Flash red for goal: what flashes red? logo outer glow, length 9+ seconds
##
## N check window dimensions every update?
## X Avs goal horn won't play? trackedScores not getting updated b/c teamID change
## ! Update teamIDs with teamIDs image=logos[homeID[gameNum]]
## ! Multiple horns: take turns (in winsound, last one takes precedence)
##
## - OT simplified
## - SO simplified
##
## W Get all team horns
##


import urllib       #for reading in webpage content
import winsound     #for playing wav files
import time         #for delays
import Tkinter      #for graphics
import os           #for file management
from datetime import datetime     #for debugging


################################################################################
##
##  Declarations/Initializations
##
##  User-customizable settings/variables are denoted by **
##

# Miscellaneous 
refreshRate = 10                    #how often to update, in seconds **
firstRun = True                     #first run flag

# Team IDs for logos (DO NOT ALTER)
ducks = 0; coyotes = 1; bruins = 2; sabres = 3; flames = 4;
hurricanes = 5; blackhawks = 6; avalanche = 7; bluejackets = 8; stars = 9;
redwings = 10; oilers = 11; panthers = 12; kings = 13; wild = 14;
canadiens = 15; predators = 16; devils = 17; islanders = 18; rangers = 19;
senators = 20; flyers = 21; penguins = 22; sharks = 23; blues = 24;
lightning = 25; mapleleafs = 26; canucks = 27; capitals = 28; jets = 29;

# NHL information
numTeams = 30
maxGames = numTeams/2                       
numGames = 0

# Tracking information
trackedTeams = [avalanche, penguins]    #teams to track **
trackedScores = [0]*len(trackedTeams)   #scores to track
hornToggles = [0]*len(trackedTeams)     #goal horn flags

# Display dimensions and settings
pageWidth = 0                       #window width
pageHeight = 0                      #window height
sp = 20                             #spacer
gh = 50                             #game height, inner
gw = 310                            #game width, inner
lw = 100                            #logo width
tw = 70                             #text width
columnMax = maxGames                #maximum number of games in a column **

# File information
try:
    thisDir = os.path.dirname(os.path.abspath(__file__))
except NameError:  # We are the main py2exe script, not a module
    import sys
    thisDir = os.path.dirname(os.path.abspath(sys.argv[0]))


#################################  FUNCTIONS  ##################################

    
#######################################
##
##  Check Scores
##
##  Reads and parses NHL game information from an ESPN feed, then graphically
##  displays the scores. The brains of the scoreboard.
##

def checkScores():

    global refreshRate; global firstRun; global numGames
    global awayTeam; global homeTeam; global awayID; global homeID;
    global awayScore; global homeScore; global timePeriod; global gameStatus;

    
    # Read in the raw NHL scores information from the ESPN feed
    #URL = 'http://sports.espn.go.com/nhl/bottomline/scores'
    #t0 = time.time()
    #fullText = urllib.urlopen(URL).read()
    #t1 = time.time(); print 'URL Open Time:',t1-t0
    
    # Read in a test file
    doc = open("C:\\Python27\\Scripts\\Test Scores\\scores2m.html")
    #doc = open("C:\\NHL Scoreboard\\Development\\Test Scores\\scores5.htm")
    fullText = doc.readline()

    # Roughly cut out each game using NHL delimiters
    gamesArray = fullText.split('nhl_s_left')
    gamesArray = gamesArray[1:len(gamesArray)]
    numGames = len(gamesArray)

    # Initialize arrays to game information
    if firstRun == True:
        awayTeam = ['']*numGames
        homeTeam = ['']*numGames
        awayID = [-1]*numGames
        homeID = [-1]*numGames    
        awayScore = [-1]*numGames
        homeScore = [-1]*numGames
        timePeriod = ['']*numGames
        gameStatus = [-1]*numGames
        
    # Loop through the games
    for whichGame, game in enumerate(gamesArray):
        
        # Cut out the game information from the main string
        game = game[2:game.find('&nhl_s_right')]

        # Clean up the strings
        game = game.replace('%20',' ')
        game = game.replace('  ',' ')
        game = game.replace('^', '') #winning team
        
        # Detect double digit game IDs
        if game[0] == '=':
            game = game[1:len(game)]
            
        # Detect overtime in progress and fix (known feed issue)
        if game.find('(-1') != -1:
            game = game.replace('(-1','(')
            game = game.replace('0-','')

            # ESPN reports time backwards in OT
            OTtimeMarker = game.find('(')+1
            OTorig = game[OTtimeMarker:OTtimeMarker+4]
            OTmin = int(OTorig[0])
            OTsec = int(OTorig[2:4])

            # Subtract from 5:00      
            OTmin = 5 - OTmin
            if OTsec != 0:
                OTmin -= 1
            OTsec = 60 - OTsec
            OTmin = str(OTmin)
            if OTsec < 10:
                OTsec = '0'+str(OTsec)
            else:
                OTsec = str(OTsec)

            game = game.replace(OTorig,OTmin+':'+OTsec)     

        # Condense multi-word cities
        if game.find('New Jersey') != -1:
            game = game.replace('New Jersey','NewJersey')
        if game.find('NY Islanders') != -1:
            game = game.replace('NY Islanders','NYIslanders')
        if game.find('NY Rangers') != -1:
            game = game.replace('NY Rangers','NYRangers')            
        if game.find('Los Angeles') != -1:
            game = game.replace('Los Angeles','LosAngeles')
        if game.find('St. Louis') != -1:
            game = game.replace('St. Louis','StLouis')
        if game.find('San Jose') != -1:
            game = game.replace('San Jose','SanJose')
        if game.find('Tampa Bay') != -1:
            game = game.replace('Tampa Bay','TampaBay')

        # Parse the shit out of games in progress (1-5) or finished (9)
        if game.find('AM ET')+game.find('PM ET') == -2:

            awayTeam[whichGame] = game[0:game.find(' ')]
            game = game[game.find(' ')+1:len(game)]
            awayScore[whichGame] = game[0:game.find(' ')]
            game = game[game.find(' ')+2:len(game)]

            homeTeam[whichGame] = game[0:game.find(' ')]
            game = game[game.find(' ')+1:len(game)]
            homeScore[whichGame] = game[0:game.find(' ')]
            game = game[game.find(' ')+1:len(game)]        
            timePeriod[whichGame] = game[1:len(game)-1]

            # Detect period
            if game.find('1ST') != -1:                
                gameStatus[whichGame] = 1
            if game.find('2ND') != -1:                
                gameStatus[whichGame] = 2
            if game.find('3RD') != -1:                
                gameStatus[whichGame] = 3
            if game.find('2ND OT') != -1:
                timePeriod[whichGame] = timePeriod[whichGame].replace('2ND OT','SO')
                timePeriod[whichGame] = timePeriod[whichGame].replace('- SO','(SO)')                
                gameStatus[whichGame] = 5
            if game.find('OT') != -1:
                timePeriod[whichGame] = timePeriod[whichGame].replace('1ST OT','OT')
                timePeriod[whichGame] = timePeriod[whichGame].replace('- OT','(OT)')
                gameStatus[whichGame] = 4
            if game.find('FINAL') != -1:                
                gameStatus[whichGame] = 9
            
        # Parse the shit out of games not yet started(0)
        else:

            awayTeam[whichGame] = game[0:game.find(' ')]
            game = game[game.find(' ')+4:len(game)]
            homeTeam[whichGame] = game[0:game.find(' ')]
            game = game[game.find(' ')+1:len(game)]        
            timePeriod[whichGame] = game[1:len(game)-1]       
                    
            gameStatus[whichGame] = 0
    
    # Apply appropriate changes to the scoreboard display        
    if firstRun == True:    
        loadLogos()
        loadHorns()
        initializeBoard()
        fillScoreboard()
    else:
        updateScoreboard()

    # Loop through the games again to check on favorite teams
    for whichGame, game in enumerate(gamesArray):
        
        # Detect game in progress
        if gameStatus[whichGame] > 0 and gameStatus[whichGame] <= 5:

            # Check for tracked teams
            for whichTeam, teamID in enumerate(trackedTeams):

                # Match against the away team
                if teamID == awayID[whichGame]:
                    print 'tracking away'
                    # Check for a valid goal
                    if awayScore[whichGame] > trackedScores[whichTeam]:
                        
                        # Toggle goal horn
                        hornToggles[whichTeam] = 1

                        # Update the tracked score
                        trackedScores[whichTeam] = awayScore[whichGame]

                # Match against the home team
                if teamID == homeID[whichGame]:
                    print 'tracking home'
                    # Check for a valid goal
                    if homeScore[whichGame] > trackedScores[whichTeam]:
                        
                        # Toggle goal horn
                        hornToggles[whichTeam] = 1

                        # Update the tracked score
                        trackedScores[whichTeam] = homeScore[whichGame]           
            
    # Play goal horns if tracked scores have changed
    for whichTeam, horn in enumerate(hornToggles):
        if hornToggles[whichTeam] == 1:
            if firstRun != True:
                print 'Goal scored!', hornToggles
                winsound.PlaySound(horns[trackedTeams[whichTeam]], \
                                   winsound.SND_FILENAME | winsound.SND_ASYNC)
                #time.sleep(1)
            hornToggles[whichTeam] = 0;

    # No longer a rookie
    firstRun = False
    
    # Pause before looping
    root.after(refreshRate*1000, checkScores)


#######################################
##
##  Initialize Scoreboard
##
##  Initializes the main layout elements of the scoreboard. Calls renderBox()
##  for assistance after determining the correct sizing of the board.
##
def initializeBoard():

    global page; global numGames; global pageWidth; global pageHeight;
    global columnMax;

    # Choose the number of columns
    if numGames > columnMax:
        numColumns = 2
    else:
        numColumns = 1

    # Create an appropriate layout    
    pageWidth = (sp + gw + sp) * numColumns
    pageHeight = sp + (gh+sp)*round(float(numGames)/numColumns)
    
    page.config(width=pageWidth, height=pageHeight)
    page.create_rectangle(0, 0, pageWidth, pageHeight, fill='white', width=0)

    # Draw the boxes
    boxCounter = 0
    currRow = 1
   
    while True:
        renderBox(boxCounter, currRow,1); boxCounter += 1;
        if boxCounter >= numGames: break
        if numColumns >= 2:
            renderBox(boxCounter, currRow,2); boxCounter += 1
            if boxCounter >= numGames: break
        currRow += 1
    page.pack()

    # Debug text
    print 'Scoreboard initialized'
    
    return


#######################################
##
##  Render Box
##
##  Draws elements for boxes on the scoreboard for each game, based on its
##  game number and position. Gets called by initializeBoard().
##
def renderBox(gameNum, row, column):

    global page; global sp; global gh; global gw; global lw; global tw;

    x1 = sp+(gw+sp+sp)*(column-1)
    x2 = sp+(gw+sp+sp)*(column-1)+lw
    y1 = sp+(gh+sp)*(row-1)
    y2 = (gh+sp)*row
    awayLogo[gameNum] = page.create_image(x1, y1, anchor='nw')

    x1 = sp+(gw+sp+sp)*(column-1)+lw+sp+tw/2
    y1 = sp+(gh+sp)*(row-1)+15
    scoreText[gameNum] = page.create_text(x1, y1, justify='center', font=('TradeGothic-Bold',26), fill='#333333')
    y1 = sp+(gh+sp)*(row-1)+15+26
    periodText[gameNum] = page.create_text(x1, y1, justify='center', font=('TradeGothic-Light',10), fill='#333333')
    y1 = sp+(gh+sp)*(row-1)+gh/2
    timeText[gameNum] = page.create_text(x1, y1, justify='center', font=('TradeGothic-Light',10), fill='#333333')

    x1 = sp+(gw+sp+sp)*(column-1)+lw+sp+tw+sp
    x2 = sp+(gw+sp+sp)*(column-1)+lw+sp+tw+sp+lw
    y1 = sp+(gh+sp)*(row-1)
    y2 = (gh+sp)*row        
    homeLogo[gameNum] = page.create_image(x1, y1, anchor='nw')
    
    return


#######################################
##
##  Fill Scoreboard
##
##  Configures the team names, IDs, and logos, then calls updateScoreboard to
##  configure the score and period/time text. Should only be used one time, upon
##  the first run of checkScores(). loadLogos() and initializeBoard() must be
##  called (or have previously been called) prior to fillScoreboard().
##
def fillScoreboard():

    global page; global numGames; global awayID; global homeID;

    # Loop through the games
    for gameNum in range(0,numGames):
        
        # Display away team logos and names
        if awayTeam[gameNum] == 'Anaheim':
            awayID[gameNum] = 0
            page.itemconfig(awayLogo[gameNum], image=logos[ducks])
        elif awayTeam[gameNum] == 'Arizona':
            awayID[gameNum] = 1
            page.itemconfig(awayLogo[gameNum], image=logos[coyotes])                        
        elif awayTeam[gameNum] == 'Boston':
            awayID[gameNum] = 2
            page.itemconfig(awayLogo[gameNum], image=logos[bruins])  
        elif awayTeam[gameNum] == 'Buffalo':
            awayID[gameNum] = 3
            page.itemconfig(awayLogo[gameNum], image=logos[sabres])
        elif awayTeam[gameNum] == 'Calgary':
            awayID[gameNum] = 4
            page.itemconfig(awayLogo[gameNum], image=logos[flames])            
        elif awayTeam[gameNum] == 'Carolina':
            awayID[gameNum] = 5
            page.itemconfig(awayLogo[gameNum], image=logos[hurricanes])  
        elif awayTeam[gameNum] == 'Chicago':
            awayID[gameNum] = 6
            page.itemconfig(awayLogo[gameNum], image=logos[blackhawks])
        elif awayTeam[gameNum] == 'Colorado':
            awayID[gameNum] = 7
            page.itemconfig(awayLogo[gameNum], image=logos[avalanche])            
        elif awayTeam[gameNum] == 'Columbus':
            awayID[gameNum] = 8
            page.itemconfig(awayLogo[gameNum], image=logos[bluejackets])  
        elif awayTeam[gameNum] == 'Dallas':
            awayID[gameNum] = 9
            page.itemconfig(awayLogo[gameNum], image=logos[stars])
        elif awayTeam[gameNum] == 'Detroit':
            awayID[gameNum] = 10
            page.itemconfig(awayLogo[gameNum], image=logos[redwings])            
        elif awayTeam[gameNum] == 'Edmonton':
            awayID[gameNum] = 11
            page.itemconfig(awayLogo[gameNum], image=logos[oilers])  
        elif awayTeam[gameNum] == 'Florida':
            awayID[gameNum] = 12
            page.itemconfig(awayLogo[gameNum], image=logos[panthers])
        elif awayTeam[gameNum] == 'LosAngeles':
            awayID[gameNum] = 13
            page.itemconfig(awayLogo[gameNum], image=logos[kings])            
        elif awayTeam[gameNum] == 'Minnesota':
            awayID[gameNum] = 14
            page.itemconfig(awayLogo[gameNum], image=logos[wild])  
        elif awayTeam[gameNum] == 'Montreal':
            awayID[gameNum] = 15
            page.itemconfig(awayLogo[gameNum], image=logos[canadiens])
        elif awayTeam[gameNum] == 'Nashville':
            awayID[gameNum] = 16
            page.itemconfig(awayLogo[gameNum], image=logos[predators])            
        elif awayTeam[gameNum] == 'NewJersey':
            awayID[gameNum] = 17
            page.itemconfig(awayLogo[gameNum], image=logos[devils])  
        elif awayTeam[gameNum] == 'NYIslanders':
            awayID[gameNum] = 18
            page.itemconfig(awayLogo[gameNum], image=logos[islanders])
        elif awayTeam[gameNum] == 'NYRangers':
            awayID[gameNum] = 19
            page.itemconfig(awayLogo[gameNum], image=logos[rangers])            
        elif awayTeam[gameNum] == 'Ottawa':
            awayID[gameNum] = 20
            page.itemconfig(awayLogo[gameNum], image=logos[senators])  
        elif awayTeam[gameNum] == 'Philadelphia':
            awayID[gameNum] = 21
            page.itemconfig(awayLogo[gameNum], image=logos[flyers])
        elif awayTeam[gameNum] == 'Pittsburgh':
            awayID[gameNum] = 22
            page.itemconfig(awayLogo[gameNum], image=logos[penguins])  
        elif awayTeam[gameNum] == 'SanJose':
            awayID[gameNum] = 23
            page.itemconfig(awayLogo[gameNum], image=logos[sharks])
        elif awayTeam[gameNum] == 'StLouis':
            awayID[gameNum] = 24
            page.itemconfig(awayLogo[gameNum], image=logos[blues])            
        elif awayTeam[gameNum] == 'TampaBay':
            awayID[gameNum] = 25
            page.itemconfig(awayLogo[gameNum], image=logos[lightning])  
        elif awayTeam[gameNum] == 'Toronto':
            awayID[gameNum] = 26
            page.itemconfig(awayLogo[gameNum], image=logos[mapleleafs])
        elif awayTeam[gameNum] == 'Vancouver':
            awayID[gameNum] = 27
            page.itemconfig(awayLogo[gameNum], image=logos[canucks])            
        elif awayTeam[gameNum] == 'Washington':
            awayID[gameNum] = 28
            page.itemconfig(awayLogo[gameNum], image=logos[capitals])  
        elif awayTeam[gameNum] == 'Winnipeg':
            awayID[gameNum] = 29
            page.itemconfig(awayLogo[gameNum], image=logos[jets])   
          
        # Display home team logos and names
        if homeTeam[gameNum] == 'Anaheim':
            homeID[gameNum] = 0
            page.itemconfig(homeLogo[gameNum], image=logos[ducks])
        elif homeTeam[gameNum] == 'Arizona':
            homeID[gameNum] = 1
            page.itemconfig(homeLogo[gameNum], image=logos[coyotes])             
        elif homeTeam[gameNum] == 'Boston':
            homeID[gameNum] = 2
            page.itemconfig(homeLogo[gameNum], image=logos[bruins])  
        elif homeTeam[gameNum] == 'Buffalo':
            homeID[gameNum] = 3
            page.itemconfig(homeLogo[gameNum], image=logos[sabres])
        elif homeTeam[gameNum] == 'Calgary':
            homeID[gameNum] = 4
            page.itemconfig(homeLogo[gameNum], image=logos[flames])            
        elif homeTeam[gameNum] == 'Carolina':
            homeID[gameNum] = 5
            page.itemconfig(homeLogo[gameNum], image=logos[hurricanes])  
        elif homeTeam[gameNum] == 'Chicago':
            homeID[gameNum] = 6
            page.itemconfig(homeLogo[gameNum], image=logos[blackhawks])
        elif homeTeam[gameNum] == 'Colorado':
            homeID[gameNum] = 7
            page.itemconfig(homeLogo[gameNum], image=logos[avalanche])            
        elif homeTeam[gameNum] == 'Columbus':
            homeID[gameNum] = 8
            page.itemconfig(homeLogo[gameNum], image=logos[bluejackets])  
        elif homeTeam[gameNum] == 'Dallas':
            homeID[gameNum] = 9
            page.itemconfig(homeLogo[gameNum], image=logos[stars])
        elif homeTeam[gameNum] == 'Detroit':
            homeID[gameNum] = 10
            page.itemconfig(homeLogo[gameNum], image=logos[redwings])            
        elif homeTeam[gameNum] == 'Edmonton':
            homeID[gameNum] = 11
            page.itemconfig(homeLogo[gameNum], image=logos[oilers])  
        elif homeTeam[gameNum] == 'Florida':
            homeID[gameNum] = 12
            page.itemconfig(homeLogo[gameNum], image=logos[panthers])
        elif homeTeam[gameNum] == 'LosAngeles':
            homeID[gameNum] = 13
            page.itemconfig(homeLogo[gameNum], image=logos[kings])            
        elif homeTeam[gameNum] == 'Minnesota':
            homeID[gameNum] = 14
            page.itemconfig(homeLogo[gameNum], image=logos[wild])  
        elif homeTeam[gameNum] == 'Montreal':
            homeID[gameNum] = 15
            page.itemconfig(homeLogo[gameNum], image=logos[canadiens])
        elif homeTeam[gameNum] == 'Nashville':
            homeID[gameNum] = 16
            page.itemconfig(homeLogo[gameNum], image=logos[predators])            
        elif homeTeam[gameNum] == 'NewJersey':
            homeID[gameNum] = 17
            page.itemconfig(homeLogo[gameNum], image=logos[devils])  
        elif homeTeam[gameNum] == 'NYIslanders':
            homeID[gameNum] = 18
            page.itemconfig(homeLogo[gameNum], image=logos[islanders])
        elif homeTeam[gameNum] == 'NYRangers':
            homeID[gameNum] = 19
            page.itemconfig(homeLogo[gameNum], image=logos[rangers])            
        elif homeTeam[gameNum] == 'Ottawa':
            homeID[gameNum] = 20        
            page.itemconfig(homeLogo[gameNum], image=logos[senators])  
        elif homeTeam[gameNum] == 'Philadelphia':
            homeID[gameNum] = 21
            page.itemconfig(homeLogo[gameNum], image=logos[flyers])           
        elif homeTeam[gameNum] == 'Pittsburgh':
            homeID[gameNum] = 22
            page.itemconfig(homeLogo[gameNum], image=logos[penguins])  
        elif homeTeam[gameNum] == 'SanJose':
            homeID[gameNum] = 23
            page.itemconfig(homeLogo[gameNum], image=logos[sharks])
        elif homeTeam[gameNum] == 'StLouis':
            homeID[gameNum] = 24
            page.itemconfig(homeLogo[gameNum], image=logos[blues])            
        elif homeTeam[gameNum] == 'TampaBay':
            homeID[gameNum] = 25
            page.itemconfig(homeLogo[gameNum], image=logos[lightning])  
        elif homeTeam[gameNum] == 'Toronto':
            homeID[gameNum] = 26
            page.itemconfig(homeLogo[gameNum], image=logos[mapleleafs])
        elif homeTeam[gameNum] == 'Vancouver':
            homeID[gameNum] = 27
            page.itemconfig(homeLogo[gameNum], image=logos[canucks])            
        elif homeTeam[gameNum] == 'Washington':
            homeID[gameNum] = 28
            page.itemconfig(homeLogo[gameNum], image=logos[capitals])  
        elif homeTeam[gameNum] == 'Winnipeg':
            homeID[gameNum] = 29
            page.itemconfig(homeLogo[gameNum], image=logos[jets]) 

    # Debug text
    print 'Scoreboard filled'
    
    # Display scores and time
    updateScoreboard()

    return


#######################################
##
##  Update Scoreboard
##
##  Configures the score and period/time text based on the most current data.
##  Should be used (at the end of) every refresh cycle.
##
def updateScoreboard():

    global page;

    # Loop through the games
    for gameNum in range(0,numGames):
        
        # Games not yet started (0)
        if gameStatus[gameNum] == 0:
            time = timePeriod[gameNum]
            time = time[0:len(time)-3] #remove 'ET'
            page.itemconfig(periodText[gameNum], text='')
            page.itemconfig(scoreText[gameNum], text='')  
            page.itemconfig(timeText[gameNum], text=time)

        # Games in progress (1-5) or finished (9)          
        else:
            score = str(awayScore[gameNum])+' - '+str(homeScore[gameNum])
            page.itemconfig(scoreText[gameNum], text=score)            
            page.itemconfig(periodText[gameNum], text=timePeriod[gameNum])
            page.itemconfig(timeText[gameNum], text='')
            
    # Debug text
    timeNow = datetime.now()
    updateTime = str(timeNow.hour)+':'+str(timeNow.minute).zfill(2)+':'+str(timeNow.second).zfill(2)
    print 'Scoreboard updated: '+updateTime

    return


#######################################
##
##  Load Logos
##
##  Loads the team logo images for the purpose of filling the scoreboard.
##  Should only be used one time. 
##
def loadLogos():

    logoDirectory = thisDir+'\\Assets\\Images\\'
    logos[ducks] = Tkinter.PhotoImage(file=logoDirectory+'ANA.gif')
    logos[coyotes] = Tkinter.PhotoImage(file=logoDirectory+'ARI.gif')
    logos[bruins] = Tkinter.PhotoImage(file=logoDirectory+'BOS.gif')
    logos[sabres] = Tkinter.PhotoImage(file=logoDirectory+'BUF.gif')
    logos[flames] = Tkinter.PhotoImage(file=logoDirectory+'CGY.gif')
    logos[hurricanes] = Tkinter.PhotoImage(file=logoDirectory+'CAR.gif')
    logos[blackhawks] = Tkinter.PhotoImage(file=logoDirectory+'CHI.gif')
    logos[avalanche] = Tkinter.PhotoImage(file=logoDirectory+'COL.gif')
    logos[bluejackets] = Tkinter.PhotoImage(file=logoDirectory+'CBJ.gif')
    logos[stars] = Tkinter.PhotoImage(file=logoDirectory+'DAL.gif')
    logos[redwings] = Tkinter.PhotoImage(file=logoDirectory+'DET.gif')
    logos[oilers] = Tkinter.PhotoImage(file=logoDirectory+'EDM.gif')
    logos[panthers] = Tkinter.PhotoImage(file=logoDirectory+'FLA.gif')
    logos[kings] = Tkinter.PhotoImage(file=logoDirectory+'LA.gif')
    logos[wild] = Tkinter.PhotoImage(file=logoDirectory+'MIN.gif')
    logos[canadiens] = Tkinter.PhotoImage(file=logoDirectory+'MTL.gif')
    logos[predators] = Tkinter.PhotoImage(file=logoDirectory+'NSH.gif')
    logos[devils] = Tkinter.PhotoImage(file=logoDirectory+'NJD.gif')
    logos[islanders] = Tkinter.PhotoImage(file=logoDirectory+'NYI.gif')
    logos[rangers] = Tkinter.PhotoImage(file=logoDirectory+'NYR.gif')
    logos[senators] = Tkinter.PhotoImage(file=logoDirectory+'OTT.gif')
    logos[flyers] = Tkinter.PhotoImage(file=logoDirectory+'PHI.gif')
    logos[penguins] = Tkinter.PhotoImage(file=logoDirectory+'PIT.gif')
    logos[sharks] = Tkinter.PhotoImage(file=logoDirectory+'SJ.gif')
    logos[blues] = Tkinter.PhotoImage(file=logoDirectory+'STL.gif')
    logos[lightning] = Tkinter.PhotoImage(file=logoDirectory+'TBL.gif')
    logos[mapleleafs] = Tkinter.PhotoImage(file=logoDirectory+'TOR.gif')
    logos[canucks] = Tkinter.PhotoImage(file=logoDirectory+'VAN.gif')
    logos[capitals] = Tkinter.PhotoImage(file=logoDirectory+'WAS.gif')
    logos[jets] = Tkinter.PhotoImage(file=logoDirectory+'WIN.gif')
    

#######################################
##
##  Load Horns
##
##  Sets the audio filenames for the goal horns of tracked teams.
##  Should only be used one time.
##
def loadHorns():

    hornDirectory = thisDir+'\\Assets\\Audio\\'
    horns[avalanche] = hornDirectory+'colorado.wav'
    horns[penguins] = hornDirectory+'pittsburgh.wav'
    #add more


####################################  MAIN  ####################################
    
# Tkinter root widget
root = Tkinter.Tk()
root.wm_title('NHL Goalhorn Scoreboard')
root.iconbitmap('icon.ico')

# Initialize variable scoreboard display elements
page = Tkinter.Canvas(root, highlightthickness=0)
awayLogo = [page.create_image(0,0)]*maxGames
homeLogo = [page.create_image(0,0)]*maxGames
scoreText = [page.create_text(0,0)]*maxGames
periodText = [page.create_text(0,0)]*maxGames
timeText = [page.create_text(0,0)]*maxGames
logos = [Tkinter.PhotoImage]*numTeams
horns = ['']*numTeams
     
# Begin checking for scores
checkScores()

# Tkinter event loop
root.mainloop()
