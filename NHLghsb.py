################################################################################
##
##  NHL Goal Horn Scoreboard
##
##  This programs tracks NHL scores in near real-time and blares a goal horn
##  when favorite teams score.
##
##
##  Author: Austin Chen
##  Email: austin@austinandemily.com
##  Last Revision: 01/21/16
##
##
## TO DO
## -----
## X Track all teams for lamps
##   X Rename goal horn teams to favorite teams
##   X Treat home and away separately
##
## X Lamp bugs (ha.)
##   N Lamps upon game start: can't replicate
##   X Lamps upon total switchover? check
##   X Mute lamps and horns upon return from sleep
##     X Threshold: 30 minutes?
##     X Just treat as firstRun
## X All-Star bug
## W Simplify OT and SO to "IN OT" and "IN SO"
## \ Ditch home/away split lists
##   X away = 2*gameNum, home = 2*gameNum+1
##   X New variables
##     X teams
##     X teamIDs
##     X scores
##     X goalFlags 
##     X teamLogos
##     X lamps
##     X shadows
##   X Lamps broken
##   X Horns broken (Avs not tracked)
##   - Check scopes
##
## \ Favorite team selection (layout)
##   X Denote with graphic change on main screen
##     N Different-colored glow
##     X Drop shadow (place under lamp to avoid overlay)
##   N New layout for selection screen
##   \ Clickable in Tkinter
##     X Tkinter button or bind: button
##     \ What function to run upon click?!
##       - toggleFave(ID)
##       - toggles favorite[ID] to True/False
##       - changes visibility of the shadow accordingly
##   N Title change, e.g. "tracking COL and PIT" No, length issue
##   - Move initial shadow setting away from fillScoreboard
##
## - Configuration file
##   - No conflict with live selection
##   - Ignore if configuration file not found
##     - Simply load and track the teams in the file
##     - No autosaving if team selections change
##
## - Print to log with logging instead of console
## - Save to executable
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
numTeams = 30                   

# Team IDs for logos (DO NOT ALTER)
ducks = 0; coyotes = 1; bruins = 2; sabres = 3; flames = 4;
hurricanes = 5; blackhawks = 6; avalanche = 7; bluejackets = 8; stars = 9;
redwings = 10; oilers = 11; panthers = 12; kings = 13; wild = 14;
canadiens = 15; predators = 16; devils = 17; islanders = 18; rangers = 19;
senators = 20; flyers = 21; penguins = 22; sharks = 23; blues = 24;
lightning = 25; mapleleafs = 26; canucks = 27; capitals = 28; jets = 29;

# Tracking information
favorites = [False]*numTeams #NEW
#favorites[avalanche] = True
#favorites[penguins] = True
trackedTeams = [avalanche, penguins]    #teams to track **
trackedScores = ['0']*len(trackedTeams) #scores to track
goalFlag = [False]*len(trackedTeams)    #goal scored flags
tLast = 0 #NEW
tTimeout = 30 #NEW, in minutes **

# Game information
numGames = 0 #timePeriod, gameStatus
#scoreText, periodText, timeText
#awayTeam, awayID, awayScore, awayFlag, awayLogo, awayLamps, awayShadow
#homeTeam, homeID, homeScore, homeFlag, homeLogo, homeLamps, homeShadow

# Display dimensions and settings
sp = 20                             #spacer
gh = 50                             #game height, inner
gw = 310                            #game width, inner
lw = 100                            #logo width
tw = 70                             #text width
sw = 128                            #splash screen width
sh = 128                            #splash screen height
columnMax = numTeams/2              #maximum number of games in a column **

# UX information
logoImages = [Tkinter.PhotoImage]*numTeams
lampImage = Tkinter.PhotoImage
shadowImage = Tkinter.PhotoImage
splashImage = Tkinter.PhotoImage
horns = ['']*numTeams

# File information
URL = 'http://sports.espn.go.com/nhl/bottomline/scores'
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

    global URL; global page; global refreshRate; global firstRun; global numGames;
    global trackedTeams; global trackedScores; global goalFlag; global horns;
    global awayTeam; global homeTeam; global awayID; global homeID;
    global awayScore; global homeScore; global timePeriod; global gameStatus;
    global awayFlag; global homeFlag;
    global tLast; global tTimeout

    global teams; global teamIDs; global scores; global goalFlags;


    # Load assets
    if firstRun == True:    
        loadImages()
        loadHorns()

    # Loop based on the desired refresh rate
    root.after(refreshRate*1000, checkScores)

    # Treat this as a first run if 
    if not firstRun and time.time()-tLast > tTimeout*60:
        print 'TIMEOUT - STARTING OVER'
        firstRun = True
    
    # Read in the raw NHL scores information from the ESPN feed
    t0 = time.time()
    try:
        fullText = urllib.urlopen(URL).read()
    except:
        print 'URL OPEN ERROR'
        return
    t1 = time.time()
    if t1-t0 > 3: print 'URL OPEN LAG =',round(t1-t0,3),'SECONDS'
    tLast = t1
    
    # Read in a test file if in development (comment out otherwise)
    #doc = open('C:\\Python27\\Scripts\\Test Scores\\scores2m.html')
    #fullText = doc.readline()

    # Roughly cut out each game using NHL delimiters
    gamesArray = fullText.split('nhl_s_left')[1:]
    if len(gamesArray) == 0:
        print 'No game(s) detected'
        numGames = 0
        splashScreen()
        return
    if len(gamesArray) != numGames and firstRun == False:
        print 'New game(s) detected'
        firstRun = True
    numGames = len(gamesArray)        

    # Initialize arrays to store game information
    if firstRun == True:
##        awayTeam = ['']*numGames
##        homeTeam = ['']*numGames
##        awayID = [-1]*numGames
##        homeID = [-1]*numGames    
##        awayScore = ['0']*numGames
##        homeScore = ['0']*numGames
##        awayFlag = [False]*numGames
##        homeFlag = [False]*numGames
        timePeriod = ['']*numGames
        gameStatus = [0]*numGames

        teams = ['']*numGames*2 #NOSPLIT
        teamIDs = ['']*numGames*2 #NOSPLIT
        scores = ['0']*numGames*2 #NOSPLIT
        goalFlags = [False]*numGames*2 #NOSPLIT
        
        
    # Loop through the games
    for index, game in enumerate(gamesArray):
        
        # Cut out the game information from the main string
        game = game[2:game.find('&nhl_s_right')]

        # Clean up the strings
        game = game.replace('%20',' ')
        game = game.replace('  ',' ')
        game = game.replace('^', '') #winning team
        
        # Detect double digit game IDs
        if game[0] == '=':
            game = game[1:]
        
        # Detect overtime in progress and fix (known feed issue)
        if '(-1' in game:
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
        if 'AM ET' not in game and 'PM ET' not in game and 'DELAY' not in game:
##            awayTeam[index] = game[:game.find(' ')]
            teams[index*2] = game[:game.find(' ')]
            game = game[game.find(' ')+1:]
            newScore = game[:game.find(' ')]
            if newScore > scores[index*2] and not firstRun:
##                awayFlag[index] = True
                goalFlags[index*2] = True
##            awayScore[index] = newScore
            scores[index*2] = newScore
            game = game[game.find(' ')+2:]

##            homeTeam[index] = game[:game.find(' ')]
            teams[index*2+1] = game[:game.find(' ')]
            game = game[game.find(' ')+1:]
            newScore = game[:game.find(' ')]
            if newScore > scores[index*2+1] and not firstRun:
##                homeFlag[index] = True
                goalFlags[index*2+1] = True
##            homeScore[index] = newScore
            scores[index*2+1] = newScore
            
            game = game[game.find(' ')+1:]        
            timePeriod[index] = game[1:len(game)-1]
            

            # Detect period
            if '1ST' in game:
                gameStatus[index] = 1
            elif '2ND' in game:
                gameStatus[index] = 2
            elif '3RD' in game:
                gameStatus[index] = 3
            if '2ND OT' in game:
                print timePeriod[index]
                timePeriod[index] = timePeriod[index].replace('2ND OT','SO')
                timePeriod[index] = timePeriod[index].replace('- SO','(SO)')
                #timePeriod[index] = 'IN SO' #Can't do it this way because of FINAL
                gameStatus[index] = 5
            elif 'OT' in game:
                print timePeriod[index]
                timePeriod[index] = timePeriod[index].replace('1ST OT','OT')
                timePeriod[index] = timePeriod[index].replace('- OT','(OT)')
                #timePeriod[index] = 'IN OT' #Can't do it this way because of FINAL
                gameStatus[index] = 4
            if 'FINAL' in game: 
                gameStatus[index] = 9
            
        # Parse the shit out of games not yet started(0)
        else:
##            awayTeam[index] = game[0:game.find(' ')]
            teams[index*2] = game[0:game.find(' ')]
            
            game = game[game.find(' ')+4:len(game)]
##            homeTeam[index] = game[0:game.find(' ')]
            teams[index*2+1] = game[0:game.find(' ')]
            
            game = game[game.find(' ')+1:len(game)]
            timePeriod[index] = game[1:len(game)-1]
                    
            gameStatus[index] = 0

    # Apply appropriate changes to the scoreboard display        
    if firstRun == True:    
        initializeBoard()
        fillScoreboard()
    else:
        toggleLamps()
        updateScoreboard()

    # Loop through the games again to check on tracked teams #WILL BE REDONE
    for index, game in enumerate(gamesArray):
        
        # Detect game in progress
        if gameStatus[index] > 0 and gameStatus[index] <= 5:

            # Check for tracked teams
            for trackedIndex, teamID in enumerate(trackedTeams):

                # Match against the away team
                if teamID == teamIDs[index*2]:

                    # Check for a valid goal
                    if scores[index*2] > trackedScores[trackedIndex]:
                        
                        # Count it
                        goalFlag[trackedIndex] = True

                        # Update the tracked score
                        trackedScores[trackedIndex] = scores[index*2]

                # Match against the home team
                elif teamID == teamIDs[index*2+1]:

                    # Check for a valid goal
                    if scores[index*2+1] > trackedScores[trackedIndex]:
                        
                        # Count it
                        goalFlag[trackedIndex] = True

                        # Update the tracked score
                        trackedScores[trackedIndex] = scores[index*2+1]                             
            
    # Play goal horns and light the lamp if tracked scores have changed
    for trackedIndex, flag in enumerate(goalFlag):
        if flag:
            if not firstRun:
                print 'Goal scored!'
                winsound.PlaySound(horns[trackedTeams[trackedIndex]], \
                                   winsound.SND_FILENAME | winsound.SND_ASYNC)
            goalFlag = [False]*len(goalFlag)
    
    # No longer a rookie
    firstRun = False

    return


#######################################
##
##  Initialize Scoreboard
##
##  Initializes the main layout elements of the scoreboard. Calls renderBox()
##  for assistance after determining the correct sizing of the board.
##
def initializeBoard():

    global page; global numGames;
    global columnMax; global sp; global gw; global gh;
    global awayLogo; global homeLogo;
    global scoreText; global periodText; global timeText;
    global awayLamp; global homeLamp; global awayShadow; global homeShadow;

    global teamLogos; global lamps; global shadows;

    # Delete existing elements if present
    page.delete('all')

    # Initialize graphic and text elements
##    awayLogo = [page.create_image(0,0)]*numGames
##    awayLamp = [page.create_image(0,0)]*numGames
##    awayShadow = [page.create_image(0,0)]*numGames
##    homeLogo = [page.create_image(0,0)]*numGames
##    homeLamp = [page.create_image(0,0)]*numGames
##    homeShadow = [page.create_image(0,0)]*numGames
    scoreText = [page.create_text(0,0)]*numGames
    periodText = [page.create_text(0,0)]*numGames
    timeText = [page.create_text(0,0)]*numGames

    teamLogos = [page.create_image(0,0)]*numGames*2
    shadows = [page.create_image(0,0)]*numGames*2
    lamps = [page.create_image(0,0)]*numGames*2

    # Choose the number of columns
    if numGames > columnMax:
        numColumns = 2
    else:
        numColumns = 1

    # Create an appropriate layout    
    pageWidth = (sp + gw + sp) * numColumns
    pageHeight = sp + (gh+sp)*round(float(numGames)/numColumns)  
    page.config(width=pageWidth, height=pageHeight)

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
    global awayLogo; global homeLogo; global awayLamp; global homeLamp;
    global lampImage; global awayShadow; global homeShadow; global shadowImage;

    global teamLogos; global lamps; global shadows;

    x1 = sp+(gw+sp+sp)*(column-1)+lw/2
    y1 = sp+(gh+sp)*(row-1)+gh/2
##    awayShadow[gameNum] = page.create_image(x1, y1, anchor='center', \
##                                            image=shadowImage, state='hidden')
##    awayLamp[gameNum] = page.create_image(x1, y1, anchor='center', \
##                                          image=lampImage, state='hidden')
##    awayLogo[gameNum] = page.create_image(x1, y1, anchor='center')

    shadows[gameNum*2] = page.create_image(x1, y1, anchor='center', \
                                            image=shadowImage, state='hidden')
    lamps[gameNum*2] = page.create_image(x1, y1, anchor='center', \
                                          image=lampImage, state='hidden')
    teamLogos[gameNum*2] = page.create_image(x1, y1, anchor='center')

    x1 = sp+(gw+sp+sp)*(column-1)+lw+sp+tw/2
    y1 = sp+(gh+sp)*(row-1)+15
    scoreText[gameNum] = page.create_text(x1, y1, justify='center', font=('TradeGothic-Bold',26), fill='#333333')
    y1 = sp+(gh+sp)*(row-1)+15+26
    periodText[gameNum] = page.create_text(x1, y1, justify='center', font=('TradeGothic-Light',10), fill='#333333')
    y1 = sp+(gh+sp)*(row-1)+gh/2-1
    timeText[gameNum] = page.create_text(x1, y1, justify='center', font=('TradeGothic-Light',10), fill='#333333')

    x1 = sp+(gw+sp+sp)*(column-1)+lw+sp+tw+sp+lw/2
    y1 = sp+(gh+sp)*(row-1)+gh/2
##    homeShadow[gameNum] = page.create_image(x1, y1, anchor='center', \
##                                            image=shadowImage, state='hidden')
##    homeLamp[gameNum] = page.create_image(x1, y1, anchor='center', \
##                                          image=lampImage, state='hidden')
##    homeLogo[gameNum] = page.create_image(x1, y1, anchor='center')

    shadows[gameNum*2+1] = page.create_image(x1, y1, anchor='center', \
                                            image=shadowImage, state='hidden')
    lamps[gameNum*2+1] = page.create_image(x1, y1, anchor='center', \
                                          image=lampImage, state='hidden')
    teamLogos[gameNum*2+1] = page.create_image(x1, y1, anchor='center')
    
    return


#######################################
##
##  Fill Scoreboard
##
##  Configures the team names, IDs, and logos, then calls updateScoreboard to
##  configure the score and period/time text. Should only be used one time, upon
##  the first run of checkScores(). loadImages() and initializeBoard() must be
##  called (or have previously been called) prior to fillScoreboard().
##
def fillScoreboard():

    global page; global numGames;
    global awayTeam; global homeTeam; global awayID; global homeID;
    global trackedTeams; global awayShadow; global homeShadow; #Remove after TODO

    global teams; global teamIDs; global teamLogos
    global teamLogos; global lamps; global shadows;

##    # Loop through the games
##    for gameNum in range(0,numGames):
##        
##        # Display away team logos and names
##        if awayTeam[gameNum] == 'Anaheim': awayID[gameNum] = ducks
##        elif awayTeam[gameNum] == 'Arizona': awayID[gameNum] = coyotes                      
##        elif awayTeam[gameNum] == 'Boston': awayID[gameNum] = bruins
##        elif awayTeam[gameNum] == 'Buffalo': awayID[gameNum] = sabres
##        elif awayTeam[gameNum] == 'Calgary': awayID[gameNum] = flames           
##        elif awayTeam[gameNum] == 'Carolina': awayID[gameNum] = hurricanes 
##        elif awayTeam[gameNum] == 'Chicago': awayID[gameNum] = blackhawks
##        elif awayTeam[gameNum] == 'Colorado': awayID[gameNum] = avalanche          
##        elif awayTeam[gameNum] == 'Columbus': awayID[gameNum] = bluejackets
##        elif awayTeam[gameNum] == 'Dallas': awayID[gameNum] = stars
##        elif awayTeam[gameNum] == 'Detroit': awayID[gameNum] = redwings         
##        elif awayTeam[gameNum] == 'Edmonton': awayID[gameNum] = oilers
##        elif awayTeam[gameNum] == 'Florida': awayID[gameNum] = panthers
##        elif awayTeam[gameNum] == 'LosAngeles': awayID[gameNum] = kings         
##        elif awayTeam[gameNum] == 'Minnesota': awayID[gameNum] = wild
##        elif awayTeam[gameNum] == 'Montreal': awayID[gameNum] = canadiens
##        elif awayTeam[gameNum] == 'Nashville': awayID[gameNum] = predators           
##        elif awayTeam[gameNum] == 'NewJersey': awayID[gameNum] = devils
##        elif awayTeam[gameNum] == 'NYIslanders': awayID[gameNum] = islanders
##        elif awayTeam[gameNum] == 'NYRangers': awayID[gameNum] = rangers          
##        elif awayTeam[gameNum] == 'Ottawa': awayID[gameNum] = senators 
##        elif awayTeam[gameNum] == 'Philadelphia': awayID[gameNum] = flyers
##        elif awayTeam[gameNum] == 'Pittsburgh': awayID[gameNum] = penguins
##        elif awayTeam[gameNum] == 'SanJose': awayID[gameNum] = sharks
##        elif awayTeam[gameNum] == 'StLouis': awayID[gameNum] = blues         
##        elif awayTeam[gameNum] == 'TampaBay': awayID[gameNum] = lightning
##        elif awayTeam[gameNum] == 'Toronto': awayID[gameNum] = mapleleafs
##        elif awayTeam[gameNum] == 'Vancouver': awayID[gameNum] = canucks       
##        elif awayTeam[gameNum] == 'Washington': awayID[gameNum] = capitals 
##        elif awayTeam[gameNum] == 'Winnipeg': awayID[gameNum] = jets
##        page.itemconfig(awayLogo[gameNum], image=logoImages[awayID[gameNum]])   
##        
##        # Display home team logos and names
##        if homeTeam[gameNum] == 'Anaheim': homeID[gameNum] = ducks
##        elif homeTeam[gameNum] == 'Arizona': homeID[gameNum] = coyotes           
##        elif homeTeam[gameNum] == 'Boston': homeID[gameNum] = bruins
##        elif homeTeam[gameNum] == 'Buffalo': homeID[gameNum] = sabres
##        elif homeTeam[gameNum] == 'Calgary': homeID[gameNum] = flames      
##        elif homeTeam[gameNum] == 'Carolina': homeID[gameNum] = hurricanes
##        elif homeTeam[gameNum] == 'Chicago': homeID[gameNum] = blackhawks
##        elif homeTeam[gameNum] == 'Colorado': homeID[gameNum] = avalanche         
##        elif homeTeam[gameNum] == 'Columbus': homeID[gameNum] = bluejackets  
##        elif homeTeam[gameNum] == 'Dallas': homeID[gameNum] = stars
##        elif homeTeam[gameNum] == 'Detroit': homeID[gameNum] = redwings         
##        elif homeTeam[gameNum] == 'Edmonton': homeID[gameNum] = oilers
##        elif homeTeam[gameNum] == 'Florida': homeID[gameNum] = panthers
##        elif homeTeam[gameNum] == 'LosAngeles': homeID[gameNum] = kings      
##        elif homeTeam[gameNum] == 'Minnesota': homeID[gameNum] = wild
##        elif homeTeam[gameNum] == 'Montreal': homeID[gameNum] = canadiens
##        elif homeTeam[gameNum] == 'Nashville': homeID[gameNum] = predators          
##        elif homeTeam[gameNum] == 'NewJersey': homeID[gameNum] = devils
##        elif homeTeam[gameNum] == 'NYIslanders': homeID[gameNum] = islanders
##        elif homeTeam[gameNum] == 'NYRangers': homeID[gameNum] = rangers         
##        elif homeTeam[gameNum] == 'Ottawa': homeID[gameNum] = senators        
##        elif homeTeam[gameNum] == 'Philadelphia': homeID[gameNum] = flyers     
##        elif homeTeam[gameNum] == 'Pittsburgh': homeID[gameNum] = penguins
##        elif homeTeam[gameNum] == 'SanJose': homeID[gameNum] = sharks
##        elif homeTeam[gameNum] == 'StLouis': homeID[gameNum] = blues   
##        elif homeTeam[gameNum] == 'TampaBay': homeID[gameNum] = lightning
##        elif homeTeam[gameNum] == 'Toronto': homeID[gameNum] = mapleleafs
##        elif homeTeam[gameNum] == 'Vancouver': homeID[gameNum] = canucks       
##        elif homeTeam[gameNum] == 'Washington': homeID[gameNum] = capitals
##        elif homeTeam[gameNum] == 'Winnipeg': homeID[gameNum] = jets
##        page.itemconfig(homeLogo[gameNum], image=logoImages[homeID[gameNum]])      
##
##        # TODO: move to a separate function that checks once every iteration
##        if awayID[gameNum] in trackedTeams:
##            #print 'yup'
##            page.itemconfig(awayShadow[gameNum], state='normal')
##        elif homeID[gameNum] in trackedTeams:
##            #print 'yup'
##            page.itemconfig(homeShadow[gameNum], state='normal')



    # Loop through the games to match the teams
    for index, team in enumerate(teams):
        if team == 'Anaheim': teamIDs[index] = ducks
        elif team == 'Arizona': teamIDs[index] = coyotes                      
        elif team == 'Boston': teamIDs[index] = bruins
        elif team == 'Buffalo': teamIDs[index] = sabres
        elif team == 'Calgary': teamIDs[index] = flames           
        elif team == 'Carolina': teamIDs[index] = hurricanes 
        elif team == 'Chicago': teamIDs[index] = blackhawks
        elif team == 'Colorado': teamIDs[index] = avalanche          
        elif team == 'Columbus': teamIDs[index] = bluejackets
        elif team == 'Dallas': teamIDs[index] = stars
        elif team == 'Detroit': teamIDs[index] = redwings         
        elif team == 'Edmonton': teamIDs[index] = oilers
        elif team == 'Florida': teamIDs[index] = panthers
        elif team == 'LosAngeles': teamIDs[index] = kings         
        elif team == 'Minnesota': teamIDs[index] = wild
        elif team == 'Montreal': teamIDs[index] = canadiens
        elif team == 'Nashville': teamIDs[index] = predators           
        elif team == 'NewJersey': teamIDs[index] = devils
        elif team == 'NYIslanders': teamIDs[index] = islanders
        elif team == 'NYRangers': teamIDs[index] = rangers          
        elif team == 'Ottawa': teamIDs[index] = senators 
        elif team == 'Philadelphia': teamIDs[index] = flyers
        elif team == 'Pittsburgh': teamIDs[index] = penguins
        elif team == 'SanJose': teamIDs[index] = sharks
        elif team == 'StLouis': teamIDs[index] = blues         
        elif team == 'TampaBay': teamIDs[index] = lightning
        elif team == 'Toronto': teamIDs[index] = mapleleafs
        elif team == 'Vancouver': teamIDs[index] = canucks       
        elif team == 'Washington': teamIDs[index] = capitals 
        elif team == 'Winnipeg': teamIDs[index] = jets
        page.itemconfig(teamLogos[index], image=logoImages[teamIDs[index]])

        # TODO: move to a separate function that checks once every iteration
        if teamIDs[index] in trackedTeams:
            #print 'yup'
            page.itemconfig(shadows[index], state='normal')

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

    global page; global numGames; global gameStatus; global timePeriod
    global awayScore; global homeScore;
    global periodText; global scoreText; global timeText;

    global scores

    # Loop through the games
    for gameNum in range(0,numGames):
        
        # Games not yet started (0)
        if gameStatus[gameNum] == 0:
            time = timePeriod[gameNum]
            if 'ET' in time:
                time = time[0:len(time)-3]
            page.itemconfig(periodText[gameNum], text='')
            page.itemconfig(scoreText[gameNum], text='')  
            page.itemconfig(timeText[gameNum], text=time)

        # Games in progress (1-5) or finished (9)          
        else:
            score = str(scores[gameNum*2])+' - '+str(scores[gameNum*2+1])
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
##  Toggle Lamps
##
##  Lights the lamps (logo glows) when teams have scored, or resets them
##  to hidden otherwise.
##
def toggleLamps():

    global page; global numGames
    global awayFlag; global homeFlag; global homeLamp; global awayLamp;

    global goalFlags; global teamLogos; global lamps; global shadows;

    # Loop through the goal scored flags
##    for index, flag in enumerate(awayFlag):
##        if flag == True:
##            page.itemconfig(awayLamp[index], state='normal')
##            print 'Goal scored by', awayTeam[index]
##        else:
##            page.itemconfig(awayLamp[index], state='hidden')
##
##    for index, flag in enumerate(homeFlag):
##        if flag == True:
##            page.itemconfig(homeLamp[index], state='normal')
##            print 'Goal scored by', homeTeam[index]
##        else:
##            page.itemconfig(homeLamp[index], state='hidden')


    for index, flag in enumerate(goalFlags):
        if flag == True:
            page.itemconfig(lamps[index], state='normal')
            print 'Goal scored by', teams[index]
        else:
            page.itemconfig(lamps[index], state='hidden')


    # Reset the goal scored flags
##    awayFlag = [False]*numGames
##    homeFlag = [False]*numGames

    goalFlags = [False]*numGames*2
        
    return


#######################################
##
##  Splash Screen
##
##  Displays the NHL Goal Horn Scoreboard logo
##
def splashScreen():

    global page; global sp; global sw; global sh;
    global splashImage; global splash;

    # Delete existing elements
    page.delete('all')

    # Create an appropriate layout    
    pageWidth = sp + sw + sp
    pageHeight = sp + sh + sp
    page.config(width=pageWidth, height=pageHeight)

    # Draw the image
    x1 = sp+sw/2
    y1 = sp+sh/2
    splash = page.create_image(x1, y1, anchor='center', image=splashImage)
    page.pack()
    
    # Debug text
    print 'Splash screen displayed'

    return


#######################################
##
##  Load Images
##
##  Loads the team logo images for the purpose of filling the scoreboard.
##  Also loads the goal lamp glow. Should only be used one time. 
##
def loadImages():

    global thisDir;
    global logoImages; global lampImage; global shadowImage; global splashImage;

    imageDirectory = thisDir+'\\Assets\\Images\\'
    logoImages[ducks] = Tkinter.PhotoImage(file=imageDirectory+'ANA.gif')
    logoImages[coyotes] = Tkinter.PhotoImage(file=imageDirectory+'ARI.gif')
    logoImages[bruins] = Tkinter.PhotoImage(file=imageDirectory+'BOS.gif')
    logoImages[sabres] = Tkinter.PhotoImage(file=imageDirectory+'BUF.gif')
    logoImages[flames] = Tkinter.PhotoImage(file=imageDirectory+'CGY.gif')
    logoImages[hurricanes] = Tkinter.PhotoImage(file=imageDirectory+'CAR.gif')
    logoImages[blackhawks] = Tkinter.PhotoImage(file=imageDirectory+'CHI.gif')
    logoImages[avalanche] = Tkinter.PhotoImage(file=imageDirectory+'COL.gif')
    logoImages[bluejackets] = Tkinter.PhotoImage(file=imageDirectory+'CBJ.gif')
    logoImages[stars] = Tkinter.PhotoImage(file=imageDirectory+'DAL.gif')
    logoImages[redwings] = Tkinter.PhotoImage(file=imageDirectory+'DET.gif')
    logoImages[oilers] = Tkinter.PhotoImage(file=imageDirectory+'EDM.gif')
    logoImages[panthers] = Tkinter.PhotoImage(file=imageDirectory+'FLA.gif')
    logoImages[kings] = Tkinter.PhotoImage(file=imageDirectory+'LA.gif')
    logoImages[wild] = Tkinter.PhotoImage(file=imageDirectory+'MIN.gif')
    logoImages[canadiens] = Tkinter.PhotoImage(file=imageDirectory+'MTL.gif')
    logoImages[predators] = Tkinter.PhotoImage(file=imageDirectory+'NSH.gif')
    logoImages[devils] = Tkinter.PhotoImage(file=imageDirectory+'NJD.gif')
    logoImages[islanders] = Tkinter.PhotoImage(file=imageDirectory+'NYI.gif')
    logoImages[rangers] = Tkinter.PhotoImage(file=imageDirectory+'NYR.gif')
    logoImages[senators] = Tkinter.PhotoImage(file=imageDirectory+'OTT.gif')
    logoImages[flyers] = Tkinter.PhotoImage(file=imageDirectory+'PHI.gif')
    logoImages[penguins] = Tkinter.PhotoImage(file=imageDirectory+'PIT.gif')
    logoImages[sharks] = Tkinter.PhotoImage(file=imageDirectory+'SJ.gif')
    logoImages[blues] = Tkinter.PhotoImage(file=imageDirectory+'STL.gif')
    logoImages[lightning] = Tkinter.PhotoImage(file=imageDirectory+'TBL.gif')
    logoImages[canucks] = Tkinter.PhotoImage(file=imageDirectory+'VAN.gif')
    logoImages[capitals] = Tkinter.PhotoImage(file=imageDirectory+'WAS.gif')
    logoImages[jets] = Tkinter.PhotoImage(file=imageDirectory+'WIN.gif')
    lampImage = Tkinter.PhotoImage(file=imageDirectory+'lamp.gif')
    shadowImage = Tkinter.PhotoImage(file=imageDirectory+'shadow.gif')
    splashImage = Tkinter.PhotoImage(file=imageDirectory+'NHL.gif')
    

#######################################
##
##  Load Horns
##
##  Sets the audio filenames for the goal horns of tracked teams.
##  Should only be used one time.
##
def loadHorns():

    global horns; global thisDir;
    
    hornDirectory = thisDir+'\\Assets\\Audio\\'
    horns[avalanche] = hornDirectory+'colorado.wav'
    horns[penguins] = hornDirectory+'pittsburgh.wav'
    #add more


####################################  MAIN  ####################################
    
# Tkinter root widget
root = Tkinter.Tk()
root.wm_title('NHL Goal Horn Scoreboard')
root.iconbitmap('icon.ico')
page = Tkinter.Canvas(root, highlightthickness=0, background='white')
     
# Begin checking for scores
checkScores()

# Tkinter event loop
root.mainloop()
