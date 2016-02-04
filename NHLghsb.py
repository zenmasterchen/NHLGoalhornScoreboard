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
##  Last Revision: 02/03/16
##
##
## TO DO
## -----
## X CTRL+C to record error in log
## ! Don't reset tracking upon timeout?
## - Readme
## X Blank-initialize variables for scope
## X Clean up to-do list
##
## X Robust enough rules for restart? (consider same number of games)
## ! Log variables upon exception
##
## - Print to log with logging instead of console
## - Save to executable
## ! Get all team horns
##
## W Rename to "Goal Horn Scoreboard?"
## W New icon: siren light
##


import Tkinter                  #for graphics
import os                       #for file management
import sys                      #for the script name
import winsound                 #for playing wav files
import time                     #for delays
import logging                  #for debugging
from urllib import urlopen      #for reading in webpage content
from datetime import datetime   #for debugging


################################################################################
##
##  Declarations/Initializations
##

# Administrative information
firstRun = True                     #first run flag
refreshRate = 10                    #how often to update, in seconds
checkSumPrev = 0
tPrev = 0                           #time of the last update, in seconds
tTimeout = 30                       #timeout threshold, in minutes
numTeams = 30                       #number of teams in the league

# Team IDs (DO NOT ALTER)
ANA = 0; ARI = 1; BOS = 2; BUF = 3; CGY = 4; CAR = 5;
CHI = 6; COL = 7; CBJ = 8; DAL = 9; DET = 10; EDM = 11;
FLA = 12; LAK = 13; MIN = 14; MTL = 15; NSH = 16; NJD = 17;
NYI = 18; NYR = 19; OTT = 20; PHI = 21; PIT = 22; SJS = 23;
STL = 24; TBL = 25; TOR = 26; VAN = 27; WSH = 28; WPG = 29; NHL = 30;
abbrev = ['ANA', 'ARI', 'BOS', 'BUF', 'CGY', 'CAR', \
          'CHI', 'COL', 'CBJ', 'DAL', 'DET', 'EDM', \
          'FLA', 'LAK', 'MIN', 'MTL', 'NSH', 'NJD', \
          'NYI', 'NYR', 'OTT', 'PHI', 'PIT', 'SJS', \
          'STL', 'TBL', 'TOR', 'VAN', 'WSH', 'WPG', '?']

# Game information
teams = []                          #city names, per team
teamIDs = []                        #team IDs (based on the above), per team
scores = []                         #score, per team
goalFlags = []                      #goal scored flag, per team
tracking = []                       #wether or not to track goals, per team
timePeriod = []                     #time in the game, per game
gameStatus = []                     #state of the game (0-5 or 9), per game
favorites = []                      #list of the user's favorite teams
numGames = 0                        #total current/upcoming NHL games

# UX information
logoImages = [Tkinter.PhotoImage]*(numTeams+1)
lampImage = Tkinter.PhotoImage
shadowImage = Tkinter.PhotoImage
splashImage = Tkinter.PhotoImage
horns = ['']*numTeams
scoreText = []
periodText = []
timeText = []
teamLogos = []
shadows = []
lamps = []

# Display dimensions
sp = 20                             #spacer
gh = 50                             #game height, inner
gw = 310                            #game width, inner
lw = 100                            #logo width
tw = 70                             #text width
sw = 128                            #splash screen width
sh = 128                            #splash screen height

# File information
try: thisDir = os.path.dirname(os.path.abspath(__file__))
except NameError: thisDir = os.path.dirname(os.path.abspath(sys.argv[0]))
configFile = 'favorites.cfg'
logFile = 'scoresheet.log'
logging.basicConfig(filename=thisDir+'\\Assets\\'+logFile, filemode='w', \
format='%(asctime)s - %(message)s', datefmt='%I:%M:%S %p', level=logging.DEBUG,)
URL = 'http://sports.espn.go.com/nhl/bottomline/scores'


#################################  FUNCTIONS  ##################################

    
#######################################
##
##  Check Scores
##
##  Reads and parses NHL game information from an ESPN feed, then graphically
##  displays the scores. The brains of the scoreboard.
##

def checkScores():

    global refreshRate; global URL; global tPrev; global tTimeout;
    global firstRun; global numGames; global checkSumPrev;
    global timePeriod; global gameStatus; 
    global teams; global teamIDs; global scores; 
    global goalFlags; global tracking; global abbrev; global horns;


    # Load assets
    if firstRun == True:    
        loadImages()
        loadHorns()

    # Loop based on the desired refresh rate
    root.after(refreshRate*1000, checkScores)

    # Treat this as a first run if it's been too long since the last run
    if not firstRun and time.time()-tPrev > tTimeout*60:
        print 'TIMEOUT - STARTING OVER'
        logging.warning('TIMEOUT - STARTING OVER')
        firstRun = True
    
    # Read in the raw NHL scores information from the ESPN feed
    t0 = time.time()
    try:
        fullText = urlopen(URL).read()
    except:
        print 'URL OPEN ERROR'
        logging.error('URL OPEN ERROR')
        return
    t1 = time.time()
    if t1-t0 > 3:
        print 'URL OPEN LAG =',round(t1-t0,2),'SECONDS'
        logging.warning('URL OPEN LAG = %0.2f SECONDS', t1-t0)
    tPrev = t1
    
    # Read in a test file if in development (comment out otherwise)
    #doc = open('C:\\Python27\\Scripts\\Test Scores\\switchsame.htm')
    #fullText = doc.readline()
    #doc.close()

    # Roughly cut out each game using NHL delimiters
    gamesArray = fullText.split('nhl_s_left')[1:]
    if len(gamesArray) == 0:
        print 'No game(s) detected'
        logging.debug('No game(s) detected')
        numGames = 0
        splashScreen()
        return
    if len(gamesArray) != numGames and firstRun == False:
        print 'New game(s) detected'
        logging.debug('New game(s) detected')
        firstRun = True
    numGames = len(gamesArray)

    # Initialize arrays to store game information
    if firstRun == True:
        teams = ['']*numGames*2
        teamIDs = ['-1']*numGames*2
        scores = ['0']*numGames*2
        goalFlags = [False]*numGames*2
        timePeriod = ['']*numGames
        gameStatus = [0]*numGames      
        
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
            teams[index*2] = game[:game.find(' ')]
            game = game[game.find(' ')+1:]
            newScore = game[:game.find(' ')]
            if newScore > scores[index*2] and not firstRun:
                print 'Goal scored by', abbrev[teamIDs[index*2]]
                logging.info('Goal scored by %s', abbrev[teamIDs[index*2]])
                goalFlags[index*2] = True
                if tracking[index*2] == True:
                    print 'Playing the goal horn for', abbrev[teamIDs[index*2]]
                    logging.info('Playing the goal horn for %s', abbrev[teamIDs[index*2]])
                    winsound.PlaySound(horns[teamIDs[index*2]], \
                                   winsound.SND_FILENAME | winsound.SND_ASYNC)
            scores[index*2] = newScore
            game = game[game.find(' ')+2:]

            teams[index*2+1] = game[:game.find(' ')]
            game = game[game.find(' ')+1:]
            newScore = game[:game.find(' ')]
            if newScore > scores[index*2+1] and not firstRun:
                print 'Goal scored by', abbrev[teamIDs[index*2+1]]
                logging.info('Goal scored by %s', abbrev[teamIDs[index*2+1]])
                goalFlags[index*2+1] = True
                if tracking[index*2+1] == True:
                    print 'Playing the goal horn for', abbrev[teamIDs[index*2+1]]
                    logging.info('Playing the goal horn for %s', abbrev[teamIDs[index*2+1]])
                    winsound.PlaySound(horns[teamIDs[index*2+1]], \
                                   winsound.SND_FILENAME | winsound.SND_ASYNC)
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
                timePeriod[index] = timePeriod[index].replace('2ND OT','SO')
                timePeriod[index] = timePeriod[index].replace('- SO','(SO)')
                #timePeriod[index] = 'IN SO' #Can't do it this way because of FINAL
                gameStatus[index] = 5
            elif 'OT' in game:
                timePeriod[index] = timePeriod[index].replace('1ST OT','OT')
                timePeriod[index] = timePeriod[index].replace('- OT','(OT)')
                #timePeriod[index] = 'IN OT' #Can't do it this way because of FINAL
                gameStatus[index] = 4
            if 'FINAL' in game: 
                gameStatus[index] = 9
            
        # Parse the shit out of games not yet started(0)
        else:
            teams[index*2] = game[0:game.find(' ')] 
            game = game[game.find(' ')+4:len(game)]
            teams[index*2+1] = game[0:game.find(' ')]            
            game = game[game.find(' ')+1:len(game)]        
            timePeriod[index] = game[1:len(game)-1]
            gameStatus[index] = 0

    # Detect team changes
    checkSum = 0
    for team in teams: checkSum += sum(ord(char) for char in team)
    if checkSum != checkSumPrev and firstRun == False: firstRun = True
    checkSumPrev = checkSum

    # Apply appropriate changes to the scoreboard display        
    if firstRun == True:
        initializeBoard()
        setTeams()
    toggleLamps()
    updateScoreboard()
    
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
    global sp; global gw; global gh;
    global scoreText; global periodText; global timeText;
    global teamLogos; global lamps; global shadows;

    # Delete existing elements if present
    page.delete('all')

    # Initialize graphic and text elements
    scoreText = [page.create_text(0,0)]*numGames
    periodText = [page.create_text(0,0)]*numGames
    timeText = [page.create_text(0,0)]*numGames

    teamLogos = [page.create_image(0,0)]*numGames*2
    shadows = [page.create_image(0,0)]*numGames*2
    lamps = [page.create_image(0,0)]*numGames*2
    
    # Create an appropriate layout    
    pageWidth = sp + gw + sp
    pageHeight = sp + (gh+sp)*numGames
    page.config(width=pageWidth, height=pageHeight)

    # Draw the games
    for gameNum in range(numGames):
        renderGame(gameNum)                
    page.pack()

    # Debug text
    print 'Scoreboard initialized'
    logging.info('Scoreboard initialized')
    
    return


#######################################
##
##  Render Game
##
##  Draws elements on the scoreboard for each game based on its
##  game number and position. Gets called by initializeBoard().
##
def renderGame(gameNum):

    global page; global sp; global gh; global gw; global lw; global tw;
    global teamLogos; global lamps; global shadows;
    global scoreText; global periodText; global timeText;
    global lampImage; global shadowImage;

    row = gameNum+1

    # Away team images
    x1 = sp+lw/2
    y1 = sp+(gh+sp)*(row-1)+gh/2
    shadows[gameNum*2] = page.create_image(x1, y1, anchor='center', \
                                            image=shadowImage, state='hidden')
    lamps[gameNum*2] = page.create_image(x1, y1, anchor='center', \
                                          image=lampImage, state='hidden')
    teamLogos[gameNum*2] = page.create_image(x1, y1, anchor='center')

    # Text
    x1 = sp+lw+sp+tw/2
    y1 = sp+(gh+sp)*(row-1)+15
    scoreText[gameNum] = page.create_text(x1, y1, justify='center', font=('TradeGothic-Bold',26), fill='#333333')
    y1 = sp+(gh+sp)*(row-1)+15+26
    periodText[gameNum] = page.create_text(x1, y1, justify='center', font=('TradeGothic-Light',10), fill='#333333')
    y1 = sp+(gh+sp)*(row-1)+gh/2-1
    timeText[gameNum] = page.create_text(x1, y1, justify='center', font=('TradeGothic-Light',10), fill='#333333')
    
    # Home team images
    x1 = sp+lw+sp+tw+sp+lw/2
    y1 = sp+(gh+sp)*(row-1)+gh/2
    shadows[gameNum*2+1] = page.create_image(x1, y1, anchor='center', \
                                            image=shadowImage, state='hidden')
    lamps[gameNum*2+1] = page.create_image(x1, y1, anchor='center', \
                                          image=lampImage, state='hidden')
    teamLogos[gameNum*2+1] = page.create_image(x1, y1, anchor='center')
    
    return


#######################################
##
##  Set Teams
##
##  Configures the team names, IDs, and logos, then calls updateScoreboard to
##  configure the score and period/time text. Should only be used one time, upon
##  the first run of checkScores(). loadImages() and initializeBoard() must be
##  called (or have previously been called) prior to setTeams().
##
def setTeams():

    global page; global teams; global teamIDs;
    global teamLogos; global logoImages; global favorites; global tracking;

    # Reset the list of tracked teams
    tracking = [False]*len(teams)
    
    # Loop through the games to match the teams
    for index, team in enumerate(teams):
        if team == 'Anaheim': teamIDs[index] = ANA
        elif team == 'Arizona': teamIDs[index] = ARI                      
        elif team == 'Boston': teamIDs[index] = BOS
        elif team == 'Buffalo': teamIDs[index] = BUF
        elif team == 'Calgary': teamIDs[index] = CGY
        elif team == 'Carolina': teamIDs[index] = CAR
        elif team == 'Chicago': teamIDs[index] = CHI
        elif team == 'Colorado': teamIDs[index] = COL
        elif team == 'Columbus': teamIDs[index] = CBJ
        elif team == 'Dallas': teamIDs[index] = DAL
        elif team == 'Detroit': teamIDs[index] = DET
        elif team == 'Edmonton': teamIDs[index] = EDM
        elif team == 'Florida': teamIDs[index] = FLA
        elif team == 'LosAngeles': teamIDs[index] = LAK
        elif team == 'Minnesota': teamIDs[index] = MIN
        elif team == 'Montreal': teamIDs[index] = MTL
        elif team == 'Nashville': teamIDs[index] = NSH
        elif team == 'NewJersey': teamIDs[index] = NJD
        elif team == 'NYIslanders': teamIDs[index] = NYI
        elif team == 'NYRangers': teamIDs[index] = NYR
        elif team == 'Ottawa': teamIDs[index] = OTT
        elif team == 'Philadelphia': teamIDs[index] = PHI
        elif team == 'Pittsburgh': teamIDs[index] = PIT
        elif team == 'SanJose': teamIDs[index] = SJS
        elif team == 'StLouis': teamIDs[index] = STL
        elif team == 'TampaBay': teamIDs[index] = TBL
        elif team == 'Toronto': teamIDs[index] = TOR
        elif team == 'Vancouver': teamIDs[index] = VAN
        elif team == 'Washington': teamIDs[index] = WSH
        elif team == 'Winnipeg': teamIDs[index] = WPG
        else: teamIDs[index] = NHL

        # Set the logo
        page.itemconfig(teamLogos[index], image=logoImages[teamIDs[index]])

        # Check for a favorite team
        if teamIDs[index] in favorites:
            tracking[index] = True

    # Denote the tracked teams
    setShadows()

    # Debug text
    print 'Teams set'
    logging.info('Teams set')

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
    global periodText; global scoreText; global timeText; global scores;

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
    logging.info('Scoreboard updated')

    return


#######################################
##
##  Toggle Lamps
##
##  Lights the lamps (logo glows) when teams have scored, or resets them
##  to hidden otherwise.
##
def toggleLamps():

    global page; global goalFlags; global abbrev; global teamIDs; global lamps;

    # Loop through the goal scored flags
    for index, flag in enumerate(goalFlags):
        if flag == True:
            page.itemconfig(lamps[index], state='normal')
        else:
            page.itemconfig(lamps[index], state='hidden')

    # Reset
    goalFlags = [False]*numGames*2
        
    return


#######################################
##
##  Set Shadows
##
##  Displays drop shadows for teams being tracked for goal horns, or resets them
##  to hidden otherwise.
##
def setShadows():

    global page; global tracking; global shadows;

    # Loop through the games to match the teams
    for index, status in enumerate(tracking):

        # Set the shadows accordingly
        if status == True: 
            page.itemconfig(shadows[index], state='normal')
        else:
            page.itemconfig(shadows[index], state='hidden')

    return


#######################################
##
##  Splash Screen
##
##  Displays the NHL Goal Horn Scoreboard logo
##
def splashScreen():

    global page; global sp; global sw; global sh;
    global splash; global splashImage;

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
    logging.info('Splash screen displayed')

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
    logoImages[ANA] = Tkinter.PhotoImage(file=imageDirectory+'ANA.gif')
    logoImages[ARI] = Tkinter.PhotoImage(file=imageDirectory+'ARI.gif')
    logoImages[BOS] = Tkinter.PhotoImage(file=imageDirectory+'BOS.gif')
    logoImages[BUF] = Tkinter.PhotoImage(file=imageDirectory+'BUF.gif')
    logoImages[CGY] = Tkinter.PhotoImage(file=imageDirectory+'CGY.gif')
    logoImages[CAR] = Tkinter.PhotoImage(file=imageDirectory+'CAR.gif')
    logoImages[CHI] = Tkinter.PhotoImage(file=imageDirectory+'CHI.gif')
    logoImages[COL] = Tkinter.PhotoImage(file=imageDirectory+'COL.gif')
    logoImages[CBJ] = Tkinter.PhotoImage(file=imageDirectory+'CBJ.gif')
    logoImages[DAL] = Tkinter.PhotoImage(file=imageDirectory+'DAL.gif')
    logoImages[DET] = Tkinter.PhotoImage(file=imageDirectory+'DET.gif')
    logoImages[EDM] = Tkinter.PhotoImage(file=imageDirectory+'EDM.gif')
    logoImages[FLA] = Tkinter.PhotoImage(file=imageDirectory+'FLA.gif')
    logoImages[LAK] = Tkinter.PhotoImage(file=imageDirectory+'LAK.gif')
    logoImages[MIN] = Tkinter.PhotoImage(file=imageDirectory+'MIN.gif')
    logoImages[MTL] = Tkinter.PhotoImage(file=imageDirectory+'MTL.gif')
    logoImages[NSH] = Tkinter.PhotoImage(file=imageDirectory+'NSH.gif')
    logoImages[NJD] = Tkinter.PhotoImage(file=imageDirectory+'NJD.gif')
    logoImages[NYI] = Tkinter.PhotoImage(file=imageDirectory+'NYI.gif')
    logoImages[NYR] = Tkinter.PhotoImage(file=imageDirectory+'NYR.gif')
    logoImages[OTT] = Tkinter.PhotoImage(file=imageDirectory+'OTT.gif')
    logoImages[PHI] = Tkinter.PhotoImage(file=imageDirectory+'PHI.gif')
    logoImages[PIT] = Tkinter.PhotoImage(file=imageDirectory+'PIT.gif')
    logoImages[SJS] = Tkinter.PhotoImage(file=imageDirectory+'SJS.gif')
    logoImages[STL] = Tkinter.PhotoImage(file=imageDirectory+'STL.gif')
    logoImages[TBL] = Tkinter.PhotoImage(file=imageDirectory+'TBL.gif')
    logoImages[TOR] = Tkinter.PhotoImage(file=imageDirectory+'TOR.gif')
    logoImages[VAN] = Tkinter.PhotoImage(file=imageDirectory+'VAN.gif')
    logoImages[WPG] = Tkinter.PhotoImage(file=imageDirectory+'WPG.gif')
    logoImages[WSH] = Tkinter.PhotoImage(file=imageDirectory+'WSH.gif')
    logoImages[NHL] = Tkinter.PhotoImage(file=imageDirectory+'NHL.gif')
    lampImage = Tkinter.PhotoImage(file=imageDirectory+'lamp.gif')
    shadowImage = Tkinter.PhotoImage(file=imageDirectory+'shadow.gif')
    splashImage = Tkinter.PhotoImage(file=imageDirectory+'splash.gif')
    

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
    horns[COL] = hornDirectory+'colorado.wav'
    horns[PIT] = hornDirectory+'pittsburgh.wav'


#######################################
##
##  Click
##
##  Determines the behavior of a mouse button click.
##  Triggered via Tkinter's bind capability.
##
def click(event):

    global tracking; global abbrev; global teamIDs;

    # Check for a valid click
    teamNum = locateTeam(event.x, event.y)
    if teamNum >= 0:

        # Toggle the tracking status of the clicked-on team
        if tracking[teamNum] == False:
            tracking[teamNum] = True
            print 'Now tracking', abbrev[teamIDs[teamNum]]
            logging.info('Now tracking %s', abbrev[teamIDs[teamNum]])
        else:
            tracking[teamNum] = False
            print 'No longer tracking', abbrev[teamIDs[teamNum]]
            logging.info('No longer tracking %s', abbrev[teamIDs[teamNum]])

        # Update the team's drop shadow for user feedback
        setShadows()

    return


#######################################
##
##  Locate Team
##
##  Determine if a mouse event is valid (over a team logo) and returns the
##  corresponding index. Gets called by click(event) and release(event).
##
def locateTeam(x, y):

    global sp; global lw; global gh

    # Loop through the game possibilities
    for index in range(numGames):

        # Check the y coordinate
        if sp+(gh+sp)*index <= y and y <= sp+(gh+sp)*index+gh:

            # Check the x coordinate (away team)
            if sp <= x and x <= sp+lw:
                return index*2
                break
            
            # Check the x coordinate (home team)
            elif sp+lw+sp+tw+sp <= x and x <= sp+lw+sp+tw+sp+lw:
                return index*2+1
                break    

    # Return -1 if the click is invalid
    return -1


#######################################
##
##  Load Configuration Information
##
##  Retrieve the user's preferences from the configuration file
##
def loadConfig():

    global thisDir; global configFile; global favorites;

    # Reset the list of favorite teams
    favorites = []

    # Read in a list of teams from the configuration file
    try:
        doc = open(thisDir+'\\Assets\\'+configFile)
        text = doc.readline().upper()
        doc.close()
    except:
        print 'CONFIGURATION ERROR'
        logging.error('CONFIGURATION ERROR')
        return

    # Check for team abbreviations and add to favorites
    if 'ANA' in text: favorites.append(ANA)
    if 'ARI' in text: favorites.append(ARI)
    if 'BOS' in text: favorites.append(BOS)
    if 'BUF' in text: favorites.append(BUF)
    if 'CGY' in text: favorites.append(CGY)
    if 'CAR' in text: favorites.append(CAR)
    if 'CHI' in text: favorites.append(CHI)
    if 'COL' in text: favorites.append(COL)
    if 'CBJ' in text: favorites.append(CBJ)
    if 'DAL' in text: favorites.append(DAL)
    if 'DET' in text: favorites.append(DET)
    if 'EDM' in text: favorites.append(EDM)
    if 'FLA' in text: favorites.append(FLA)
    if 'LAK' in text: favorites.append(LAK)
    if 'MIN' in text: favorites.append(MIN)
    if 'MTL' in text: favorites.append(MTL)
    if 'NSH' in text: favorites.append(NSH)
    if 'NJD' in text: favorites.append(NJD)
    if 'NYI' in text: favorites.append(NYI)
    if 'NYR' in text: favorites.append(NYR)
    if 'OTT' in text: favorites.append(OTT)
    if 'PHI' in text: favorites.append(PHI)
    if 'PIT' in text: favorites.append(PIT)
    if 'SJS' in text: favorites.append(SJS)
    if 'STL' in text: favorites.append(STL)
    if 'TBL' in text: favorites.append(TBL)
    if 'TOR' in text: favorites.append(TOR)
    if 'VAN' in text: favorites.append(VAN)
    if 'WSH' in text: favorites.append(WSH)
    if 'WPG' in text: favorites.append(WPG)
    
    return
    
    
####################################  MAIN  ####################################
    
# Tkinter root widget
root = Tkinter.Tk()
root.wm_title('NHL Goal Horn Scoreboard')
root.iconbitmap(thisDir+'\\Assets\\icon.ico')
root.bind('<Button-1>', click)
page = Tkinter.Canvas(root, highlightthickness=0, background='white')

# Load user data
loadConfig()
   
# Begin checking for scores
checkScores()

# Tkinter event loop
try:
    root.mainloop()
except:
    logging.exception('ERROR')
    raise
