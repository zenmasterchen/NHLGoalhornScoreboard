################################################################################
##
##  NHL Goal Horn Scoreboard
##
##  This program tracks NHL scores in near real-time and blares a goal horn
##  when favorite teams score.
##
##
##  Author: Austin Chen
##  Email: austin@austinandemily.com
##  Last Revision: 03/19/16
##
##  Copyright (C) 2016 Austin Chen
##
##
##  Disclaimer: This program is provided for entertainment purposes only and is
##  not affiliated with nor endorsed by the National Hockey League (NHL). "NHL"
##  and the NHL logo are a registered trademarks of the National Hockey League.
##  Team logos are registered trademarks of their respective franchises.
##
##
##  Function List
##  -------------
##  URLhandler()
##  checkScores()
##  checkScoresWrapper()
##  checkScoresWrapperThreaded()
##  initializeScoreboard()
##  renderGame(gameNum) *
##  setTeams() *
##  detectTimeZone()
##  updateScoreboard() *
##
##  toggleLamps()
##  animateLamp(lamp)
##  setShadows()
##  splashScreen()
##
##  leftClick(event)
##  rightClick(event)
##  locateTeam(x, y)
##  toggleFavorite(teamID)
##  toggleMute()
##  toggleDebug()
##  updateDebug()
##  debugCommands()
##
##  configureFavorites()
##  selectionClick(event) *
##  closeConfig() *
##
##  startTutorial()
##  navigateTutorial(direction)
##  tutorialClick(event)
##  closeTutorial()
##
##  loadConfig()
##  saveConfig()
##  loadImages()
##  loadHorns()
##
##  logHandler(string, level)
##
##
## TO DO
## -----
## N Readme
## N License
## X Add NHL disclaimer
##
## X Clean up to-do list
## N Assemble all-time to-do list
##
## N Sleep mode: don't check for new scores until close to game time?
## X Dynamic refresh enabled incorrectly after timeout/URL open error
## X Increase length of lamp animation
## X Modify build instructions
## W Remove NHL references
##   W GHSB Logo
##   W Rename in Python
##   W Rename in setup
##   W Rename in installer
## X Modify tutorial early exit logic to call configure favorites
## X Include user-accessible version number
## X Develop console-like commands for debug mode
## N Can't bind debug commands to messages (needs to apply to all, anyway)
## N Open up window at upper-right screen corner (root.geometry is fickle)
##


import Tkinter                  #for graphics
import os                       #for file management
import sys                      #for file management
import winsound                 #for playing wav files
import time                     #for delays
import logging                  #for debugging
import threading                #for checking scores
from urllib import urlopen      #for reading in webpage content
from subprocess import Popen    #for file management


################################################################################
##
##  Declarations/Initializations
##

# Administrative information
ver = '2.3.19'                      #version
test = False                        #development flag
firstRun = True                     #first run flag
noConfig = False                    #no configuration file flag
dynamicRefresh = False              #dynamic refresh flag
timeout = False                     #delayed update flag
refreshRate = 15                    #how often to update, in seconds
lagLimit = 5                        #allowable update delay, in seconds
checkSumPrev = 0                    #scoreboard switchover detection
tPrev = 0                           #time of the last update, in seconds
tTimeout = 30                       #timeout threshold, in minutes
tZone = 0                           #time zone, in hours offset from Eastern
numTeams = 30                       #number of teams in the league
mute = False                        #mute on/of
debug = False                       #debug mode on/off
debugLength = 5                     #number of debug messages to display
debugList = ['']*debugLength        #list of debug messages to display

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
logoImages = [[0]*(numTeams+1) for index in range(3)]
numFrames = 10
lampFrames = [[0]*(numFrames+1) for index in range(2)]
shadowImage = [0]*2
splashImage = 0
horns = ['']*numTeams
scoreText = ['']
periodText = ['']
timeText = ['']
teamLogos = []
teamLogosX = []
teamLogosY = []
shadows = []
lamps = []
debugText = [0]*debugLength
configLogos = [0]*numTeams
configShadows = [0]*numTeams
tutorialIndex = -1
tutorialLine0 = 0
tutorialLine1 = 0
tutorialShadow = 0
tutorialLamp = 0
tutorialLogo = 0
tutorialBack = 0
tutorialNext = 0
animationStack = [0]

# Display parameters
sp = 20                             #scoreboard spacer
lw = [100, 60]                      #logo width
lh = [50, 30]                       #logo height
cw = 70                             #score/time information width
scoreOffset = 15                    #score text offset
periodOffset = 41                   #period text offset
fontSize = [26, 10]                 #font sizes
lampLength = 30                     #lamp animation length, in seconds
ww = 0                              #window width
wh = 0                              #window height
sw = 128                            #splash screen width
sh = 146                            #splash screen height
dh = sp*(debugLength+1)             #debug height
tw = 350                            #tutorial width
th = 192                            #tutorial height
tp = 36                             #tutorial spacer
to = 24                             #tutorial offset
instructionOffset = 3               #tutorial line 0 offset
logoOffset = 1                      #tutorial logo offset
multiColumn = False                 #multiple columns for small screens
configRows = 5                      #number of rows for configuring favorites
configColumns = 6                   #number of columns for configuring favorites
large = 0                           #size index for team logos
small = 1                           #size index for configuring favorites
bw = 2                              #size index for configuring favorites

# File information
try: progDir = os.path.dirname(os.path.abspath(__file__))
except NameError: progDir = os.path.dirname(os.path.abspath(sys.argv[0]))
appDir = os.getenv('APPDATA')
appDir = appDir+'\\NHL Goal Horn Scoreboard'
if not os.path.exists(appDir): os.makedirs(appDir)
configFile = 'favorites.cfg'
logFile = 'scoresheet.log'
logging.basicConfig(filename=appDir+'\\'+logFile, filemode='w+', \
format='%(asctime)s - %(message)s', datefmt='%I:%M:%S %p', level=logging.DEBUG,)
URL = 'http://sports.espn.go.com/nhl/bottomline/scores'
fullText = ''


#################################  FUNCTIONS  ##################################


#######################################
##
##  URL Handler
##
##  Reads in NHL game information from an ESPN feed or test file.
##

def URLhandler():

    global URL; global fullText; global firstRun; global timeout;
    global tPrev; global tTimeout;  global lagLimit; global dynamicRefresh;
    global test; global refreshRate;

    # Read in the raw NHL scores information from ESPN
    if not test:
        t0 = time.time()
        try:
            fullText = urlopen(URL).read()
        except Exception:
            logHandler('URL OPEN ERROR', 'exception')
            raise
        t1 = time.time()
        lag = t1-t0
        if lag > lagLimit:
            logHandler('URL OPEN LAG = '+str(round(t1-t0, 2))+' SECONDS', 'warning')
            if lag > tTimeout*60:
                logHandler('TIMEOUT', 'warning')
                timeout = True
                if dynamicRefresh:
                    dynamicRefresh = False
                    logHandler('Dynamic refresh disabled', 'debug')
        tPrev = t1

    # Read in a test file for development
    else:
        #time.sleep(3) #Artificial lag
        refreshRate = 10
        if 'CHEN' in os.environ['COMPUTERNAME']:
            doc = open('C:\\Python27\\Scripts\\Test Scores\\scores2m.html', 'r+')
        elif 'AUSTIN' in os.environ['COMPUTERNAME']:
            doc = open('C:\\NHL Scoreboard\\Development\\Test Scores\\multi.htm')
        else:
            logHandler('UNKNOWN DEVELOPMENT MACHINE', 'error')
            raise
        fullText = doc.readline()
        doc.close()
        tPrev = time.time()
    
    return fullText

    
#######################################
##
##  Check Scores
##
##  Parses NHL game information, then orchestrates the display of the scores
##  in a graphical manner by calling other functions. The brains of the program.
##

def checkScores():

    global URLthread; global fullText; global tPrev; global tTimeout;
    global firstRun; global timeout; global numGames; global checkSumPrev;
    global timePeriod; global gameStatus; 
    global teams; global teamIDs; global scores; 
    global goalFlags; global tracking; global abbrev; global horns;
    global dynamicRefresh;


    # Suppress goal horns and lamps if it's been too long since the last run
    if not firstRun and time.time()-tPrev > tTimeout*60:
        logHandler('TIMEOUT', 'warning')
        timeout = True
        if dynamicRefresh:
            dynamicRefresh = False
            logHandler('Dynamic refresh disabled', 'debug')         
    else:
        timeout = False
    
    # Obtain text for parsing
    try:
        fullText = URLhandler()
    except:
        return

    # Roughly cut out each game using NHL delimiters
    gamesArray = fullText.split('nhl_s_left')[1:]
    if len(gamesArray) == 0:
        logHandler('No game(s) detected', 'debug')
        numGames = 0
        splashScreen()
        if not dynamicRefresh:
            dynamicRefresh = True
            logHandler('Dynamic refresh enabled', 'debug')
        return
    if len(gamesArray) != numGames and not firstRun:
        logHandler('New game(s) detected', 'debug')
        firstRun = True
    numGames = len(gamesArray)

    # Initialize arrays to store game information
    if firstRun:
        teams = ['']*numGames*2
        teamIDs = ['-1']*numGames*2
        scores = ['0']*numGames*2
        goalFlags = [False]*numGames*2
        timePeriod = ['']*numGames
        gameStatus = [0]*numGames      

    # Avoid playing multiple goal horns at once
    hornPlayed = False
        
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
        
        # Detect overtimes and shootouts in progress and fix (known feed issue)
        if '(-1' in game:            
            game = game.replace('(-1','(')
            game = game.replace('0-','')
            OTmarker = game.find('(')+1
            OTtime = game[OTmarker:OTmarker+5]
            game = game.replace(OTtime, '')

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
            newScore = int(game[:game.find(' ')])
            if newScore > scores[index*2] and not firstRun and not timeout:
                logHandler('Goal scored by '+abbrev[teamIDs[index*2]], 'info')
                goalFlags[index*2] = True
                if tracking[index*2] and not hornPlayed:
                    if mute:
                        logHandler('Suppressing goal horn due to mute', 'debug')
                    else:
                        logHandler('Playing the goal horn for '+abbrev[teamIDs[index*2]], 'info')
                        winsound.PlaySound(horns[teamIDs[index*2]], \
                                    winsound.SND_FILENAME | winsound.SND_ASYNC)
                    hornPlayed = True
            scores[index*2] = newScore
            game = game[game.find(' ')+2:]

            teams[index*2+1] = game[:game.find(' ')]
            game = game[game.find(' ')+1:]
            newScore = int(game[:game.find(' ')])
            if newScore > scores[index*2+1] and not firstRun and not timeout:
                logHandler('Goal scored by '+abbrev[teamIDs[index*2+1]], 'info')
                goalFlags[index*2+1] = True
                if tracking[index*2+1] and not hornPlayed:
                    if mute:
                        logHandler('Suppressing goal horn due to mute', 'debug')
                    else:
                        logHandler('Playing the goal horn for '+abbrev[teamIDs[index*2+1]], 'info')
                        winsound.PlaySound(horns[teamIDs[index*2+1]], \
                                    winsound.SND_FILENAME | winsound.SND_ASYNC)
                    hornPlayed = True
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
                gameStatus[index] = 5
            elif 'OT' in game:
                timePeriod[index] = timePeriod[index].replace('1ST OT','OT')
                timePeriod[index] = timePeriod[index].replace('- OT','(OT)')
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
    checkSum = sum(ord(char) for char in ''.join(teams))
    if checkSum != checkSumPrev and not firstRun:
        logHandler('New team(s) detected', 'debug')
        firstRun = True
    checkSumPrev = checkSum

    # Detect changes in activity/inactivity to modify refresh rates
    if all(status is 0 or status is 9 for status in gameStatus):
        if not dynamicRefresh:
            dynamicRefresh = True
            logHandler('Dynamic refresh enabled', 'debug')
    elif dynamicRefresh:
        dynamicRefresh = False
        logHandler('Dynamic refresh disabled', 'debug')

    # Apply appropriate changes to the scoreboard display        
    if firstRun:
        detectTimeZone()
        initializeScoreboard()
        setTeams()
        #if noConfig:            
        #    configureFavorites()
        if debug:
            toggleDebug()
            toggleDebug()
    else:
        toggleLamps()
    updateScoreboard()
    
    # No longer a rookie
    firstRun = False

    return


#######################################
##
##  Check Scores Wrapper
##
##  Processes all calls to checkScores() for error handling purposes. Also takes
##  care of all refreshing-related behavior.
##

def checkScoresWrapper():

    global root; global refreshRate; global fullText;
    global firstRun; global noConfig; global dynamicRefresh; global timeout; global numGames;
    global mute; global debug; global multiColumn; global ww; global wh;
    global teams; global teamIDs; global scores;
    global goalFlag; global tracking;
    global timePeriod; global gameStatus; global favorites;

    try:
        checkScores()
        if dynamicRefresh:
            root.after(refreshRate*2*1000, checkScoresWrapperThreaded)
        else:
            root.after(refreshRate*1000, checkScoresWrapperThreaded)
    except Exception:
        root.after(refreshRate*1000, checkScoresWrapperThreaded)
        logHandler('CHECKSCORES ERROR', 'exception')
        logging.debug('Error circumstances to follow...')
        logging.debug('\tfirstRun = %s, noConfig = %s, dynamicRefresh = %s, timeout = %s, numGames = %i', \
                      firstRun, noConfig, dynamicRefresh, timeout, numGames)
        logging.debug('\tmute = %s, debug = %s, multiColumn = %s, ww = %i, wh = %i', \
                      mute, debug, multiColumn, ww, wh)
        logging.debug('\tteams = %s', ', '.join(teams))
        logging.debug('\tteamIDs = %s', ', '.join(map(str, teamIDs)))
        logging.debug('\tscores = %s', ', '.join(map(str, scores)))
        logging.debug('\tgoalFlags = %s', ', '.join(map(str, goalFlags)))
        logging.debug('\ttracking = %s', ', '.join(map(str, tracking)))
        logging.debug('\ttimePeriod = %s', ', '.join(timePeriod))
        logging.debug('\tgameStatus = %s', ', '.join(map(str, gameStatus)))
        logging.debug('\tfavorites = %s', ', '.join(map(str, favorites)))
        logging.debug('\tfullText (may not be up to date) = %s', fullText)

    return


#######################################
##
##  Check Scores Wrapper (Threaded)
##
##  Processes all calls to checkScoresWrapper() for threading purposes.
##

def checkScoresWrapperThreaded():

    thread = threading.Thread(target=checkScoresWrapper)
    thread.start()
    
    return


#######################################
##
##  Initialize Scoreboard
##
##  Initializes the main layout elements of the scoreboard. Calls renderBox()
##  for assistance after determining the correct sizing of the board.
##

def initializeScoreboard():

    global scoreboard; global messages; global numGames; global multiColumn;
    global sp; global lw; global lh; global cw; global ww; global wh; global dh;
    global scoreText; global periodText; global timeText;
    global teamLogos; global lamps; global shadows;
    global teamLogosX; global teamLogosY;
    
    # Delete existing elements if present
    scoreboard.delete('all')

    # Create graphic and text elements
    scoreText = [0]*numGames
    periodText = [0]*numGames
    timeText = [0]*numGames

    shadows = [0]*numGames*2
    lamps = [0]*numGames*2
    teamLogos = [0]*numGames*2
    teamLogosX = [0]*numGames*2
    teamLogosY = [0]*numGames*2

    # Create an appropriate layout
    wh = sp+(lh[large]+sp)*numGames
    ww = sp+lw[large]+sp+cw+sp+lw[large]+sp
    if wh+dh > root.winfo_screenheight():
        logHandler('Multiple columns enabled', 'debug')
        multiColumn = True
        wh = sp+(lh[large]+sp)*(numGames/2+numGames%2)
        ww = sp+lw[large]+sp+cw+sp+lw[large] + sp + sp+lw[large]+sp+cw+sp+lw[large] + sp
    else:
        multiColumn = False;
    scoreboard.config(width=ww, height=wh)
    messages.config(width=ww, height=dh)

    # Draw the games
    for gameNum in range(numGames):
        renderGame(gameNum)         
    scoreboard.pack()
    
    # Debug text
    logHandler('Scoreboard initialized', 'info')
    
    return


#######################################
##
##  Render Game
##
##  Draws elements on the scoreboard for each game based on its
##  game number and position. Gets called by initializeScoreboard().
##
##  gameNum: number/order in which the ESPN feed lists the game (0-indexed)
##

def renderGame(gameNum):

    global scoreboard; global sp; global lh; global lw; global cw;
    global lamps; global shadows; global shadowImage; global lampFrames;
    global scoreText; global periodText; global timeText;
    global scoreOffset; global periodOffset; global fontSize;
    global multiColumn; global teamLogosX; global teamLogosY;

    # Adjust for one or multiple columns
    if multiColumn:
       row = gameNum/2
       column = gameNum%2
    else:
       row = gameNum
       column = 0
    
    # Away team images 
    x = (sp+lw[large]+sp+cw+sp+lw[large]+sp)*column +sp+lw[large]/2
    y = sp+(lh[large]+sp)*(row)+lh[large]/2
    shadows[gameNum*2] = scoreboard.create_image(x, y, anchor='center', \
                                            image=shadowImage[large], state='hidden')
    lamps[gameNum*2] = scoreboard.create_image(x, y, anchor='center', \
                                          image=lampFrames[large][0], state='hidden')
    teamLogos[gameNum*2] = scoreboard.create_image(x, y, anchor='center')
    teamLogosX[gameNum*2] = x
    teamLogosY[gameNum*2] = y

    # Text
    x = (sp+lw[large]+sp+cw+sp+lw[large]+sp)*column +sp+lw[large]+sp+cw/2
    y = sp+(lh[large]+sp)*(row)+scoreOffset
    scoreText[gameNum] = scoreboard.create_text(x, y, font=('TradeGothic-Bold',fontSize[large]), fill='#333333')
    y = sp+(lh[large]+sp)*(row)+periodOffset
    periodText[gameNum] = scoreboard.create_text(x, y, font=('TradeGothic-Light',fontSize[small]), fill='#333333')
    y = sp+(lh[large]+sp)*(row)+lh[large]/2-1
    timeText[gameNum] = scoreboard.create_text(x, y, font=('TradeGothic-Light',fontSize[small]), fill='#333333')
    
    # Home team images
    x = (sp+lw[large]+sp+cw+sp+lw[large]+sp)*column +sp+lw[large]+sp+cw+sp+lw[large]/2
    y = sp+(lh[large]+sp)*(row)+lh[large]/2
    shadows[gameNum*2+1] = scoreboard.create_image(x, y, anchor='center', \
                                            image=shadowImage[large], state='hidden')
    lamps[gameNum*2+1] = scoreboard.create_image(x, y, anchor='center', \
                                          image=lampFrames[large][0], state='hidden')
    teamLogos[gameNum*2+1] = scoreboard.create_image(x, y, anchor='center')
    teamLogosX[gameNum*2+1] = x
    teamLogosY[gameNum*2+1] = y

    return


#######################################
##
##  Set Teams
##
##  Configures the team names, IDs, and logos, then calls updateScoreboard to
##  configure the score and period/time text. Only needs to be called once, upon
##  the first run of checkScores(). loadImages() and initializeScoreboard() must
##  be called (or have previously been called) prior to setTeams().
##

def setTeams():

    global scoreboard; global teams; global teamIDs;
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
        scoreboard.itemconfig(teamLogos[index], image=logoImages[large][teamIDs[index]])

        # Check for a favorite team
        if teamIDs[index] in favorites:
            tracking[index] = True

    # Denote the tracked teams
    setShadows()

    # Debug text
    logHandler('Teams set', 'info')

    return


#######################################
##
##  Detect Time Zone
##
##  Determines the local time zone for the purpose of shifting game start times.
##  Only needs to be called once.
##

def detectTimeZone():

    global tZone;

    zones = ' '.join(time.tzname)

    if 'Eastern' in zones:
        tZone = 0
    elif 'Central' in zones:
        tZone = 1
    elif 'Mountain' in zones:
        tZone = 2
    elif 'Pacific' in zones:
        tZone = 3
    else:
        tZone = -1

    return


#######################################
##
##  Update Scoreboard
##
##  Configures the score and period/time text based on the most current data.
##  Should be used (at the end of) every refresh cycle.
##

def updateScoreboard():

    global scoreboard; global numGames; global gameStatus; global timePeriod
    global periodText; global scoreText; global timeText; global scores;
    global tZone;

    # Loop through the games
    for gameNum in range(numGames):
        
        # Games not yet started (0)
        if gameStatus[gameNum] == 0:
            gameTime = timePeriod[gameNum]

            # Account for time zones
            if tZone > 0:
                hourMarker = gameTime.find(':')
                hour = int(gameTime[:hourMarker])
                hour += tZone
                if hour >= 12:
                    if 'PM' in gameTime:
                        gameTime = gameTime.replace('PM', 'AM')
                    else:
                        gameTime = gameTime.replace('AM', 'PM')
                    if hour > 12:
                        hour %= 12                
                gameTime = str(hour)+gameTime[hourMarker:]

            # Remove 'ET'
            if tZone >= 0:
                gameTime = gameTime[0:len(gameTime)-3]
                
            scoreboard.itemconfig(periodText[gameNum], text='')
            scoreboard.itemconfig(scoreText[gameNum], text='')  
            scoreboard.itemconfig(timeText[gameNum], text=gameTime)

        # Games in progress (1-5) or finished (9)          
        else:
            score = str(scores[gameNum*2])+' - '+str(scores[gameNum*2+1])
            scoreboard.itemconfig(scoreText[gameNum], text=score)            
            scoreboard.itemconfig(periodText[gameNum], text=timePeriod[gameNum])
            scoreboard.itemconfig(timeText[gameNum], text='')
            
    # Debug text
    updateTime = time.strftime('%I:%M:%S %p')
    logHandler('Scoreboard updated at '+updateTime, 'info')

    return


#######################################
##
##  Toggle Lamps
##
##  Lights the lamps (logo glows) when teams have scored.
##

def toggleLamps():

    global goalFlags; global lamps;
    
    for index, flag in enumerate(goalFlags):
        if flag:
            animateLamp(lamps[index])
            goalFlags[index] = False
        
    return


#######################################
##
##  Animate Lamp
##  
##  Schedules the appearance of lamp image frames for animation purposes.
##  One single on-and-off animation cycle lasts 1 second.
##
##  lamp: lamp Tkinter widget on the scoreboard to animate
##

def animateLamp(lamp):

    global scoreboard; global lampLength; global lampFrames; global numFrames;

    scoreboard.itemconfig(lamp, state='normal')
    for cycle in range(lampLength):
        for frame in range(1, numFrames):
            tOn = int((cycle+frame/(2.0*numFrames))*1000)
            tOff = int((cycle+(numFrames*2-frame)/(2.0*numFrames))*1000)
            scoreboard.after(tOn, lambda frame=frame: \
                        scoreboard.itemconfig(lamp, image=lampFrames[large][frame]))
            scoreboard.after(tOff, lambda frame=frame: \
                        scoreboard.itemconfig(lamp, image=lampFrames[large][frame]))
        scoreboard.after(int((cycle+0.5)*1000), lambda frame=frame: \
                      scoreboard.itemconfig(lamp, image=lampFrames[large][numFrames]))
    scoreboard.after(lampLength*1000, lambda: \
                    scoreboard.itemconfig(lamp, state='hidden'))


#######################################
##
##  Set Shadows
##
##  Displays drop shadows for teams being tracked for goal horns, or resets them
##  to hidden otherwise.
##

def setShadows():

    global scoreboard; global tracking; global shadows;

    # Loop through the games to match the teams
    for index, status in enumerate(tracking):

        # Set the shadows accordingly
        if status: 
            scoreboard.itemconfig(shadows[index], state='normal')
        else:
            scoreboard.itemconfig(shadows[index], state='hidden')

    return


#######################################
##
##  Splash Screen
##
##  Displays the NHL Goal Horn Scoreboard logo
##

def splashScreen():

    global scoreboard; global sp; global sw; global sh; global ww; global wh;
    global splash; global splashImage;

    # Delete existing elements
    scoreboard.delete('all')

    # Create an appropriate layout
    ww = sp+lw[large]+sp+cw+sp+lw[large]+sp
    wh = int(sp*1.5 + sh + sp*1.5)
    scoreboard.config(width=ww, height=wh)

    # Draw the image
    x = ww/2
    y = sp*1.5+sh/2
    splash = scoreboard.create_image(x, y, anchor='center', image=splashImage)
    scoreboard.pack()
    
    # Debug text
    logHandler('Splash screen displayed', 'info')

    return


#######################################
##
##  Left Click
##
##  Determines the behavior of a left mouse button click.
##  Triggered via Tkinter's bind capability.
##
    
def leftClick(event):

    global tracking; global abbrev; global teamIDs;

    # Check for a valid click on a team
    teamNum = locateTeam(event.x, event.y)
    if teamNum >= 0:

        # Toggle the tracking status of the clicked-on team
        if not tracking[teamNum]:
            tracking[teamNum] = True
            logHandler('Started tracking '+abbrev[teamIDs[teamNum]], 'info')
        else:
            tracking[teamNum] = False
            logHandler('Stopped tracking '+abbrev[teamIDs[teamNum]], 'info')

        # Update the team's drop shadow for user feedback
        setShadows()

    return


#######################################
##
##  Right Click
##
##  Determines the behavior of a right mouse button click.
##  Triggered via Tkinter's bind capability.
##

def rightClick(event):

    global root; global scoreboard; global menu;
    global mute; global teamIDs; global favorites;

    # Overwrite the previous context menu
    try:
        menu.destroy()
    except:
        pass
    menu = Tkinter.Menu(root, tearoff=0)
    
    # Check for a valid click on a team
    teamNum = locateTeam(event.x, event.y)
    if teamNum >= 0:

        # Toggle the favorite status of the clicked-on team
        if teamIDs[teamNum] not in favorites:
            menu.add_command(label='Add as favorite', \
                             command=lambda: toggleFavorite(teamIDs[teamNum]))
        else:
            menu.add_command(label='Remove as favorite', \
                             command=lambda: toggleFavorite(teamIDs[teamNum]))            
        menu.add_separator()  

    menu.add_checkbutton(label='Mute', command=toggleMute)
    menu.add_checkbutton(label='Debug mode', command=toggleDebug)
    menu.add_command(label='Configure favorites...', command=configureFavorites)

    # Display the context menu
    menu.post(event.x_root, event.y_root)
    
    return


#######################################
##
##  Locate Team
##
##  Determine if a mouse event is valid (over a team logo) and returns the
##  corresponding index. Gets called by leftClick(event).
##
##  x: x coordinate of mouse event
##  y: y coordinate of mouse event
##

def locateTeam(x, y):

    global numGames; global teamLogosX; global teamLogosY; global lw; global lh;

    # Loop through the team possibilities
    for index in range(numGames*2):

        # Check the y coordinate
        if teamLogosY[index]-lh[large]/2 <= y and y <= teamLogosY[index]+lh[large]/2:

            # Check the x coordinate
            if teamLogosX[index]-lw[large]/2 <= x and x <= teamLogosX[index]+lw[large]/2:
                return index

    # Return -1 if the click is invalid
    return -1


#######################################
##
##  Toggle Favorite
##
##  Adds or removes a team from favorites. Gets called by rightClick(event) and
##  selectionClick(event).
##
##  teamID: teamID of the team to add or remove as favorite 
##

def toggleFavorite(teamID):

    global favorites; global abbrev; global teamIDs; global tracking;
    global popup; global selection; global configLogos; global configShadows;
    global logoImages;

    # Add as favorite
    if teamID not in favorites:
        favorites.append(teamID)
        logHandler('Added '+abbrev[teamID]+' as favorite', 'info')

        # Start tracking
        if teamID in teamIDs and not tracking[teamIDs.index(teamID)]:
            tracking[teamIDs.index(teamID)] = True
            logHandler('Started tracking '+abbrev[teamID], 'info')
            setShadows()

    # Remove as favorite
    else:
        favorites.remove(teamID)
        logHandler('Removed '+abbrev[teamID]+' as favorite', 'info')

        # Stop tracking
        if teamID in teamIDs and tracking[teamIDs.index(teamID)]:
            tracking[teamIDs.index(teamID)] = False
            logHandler('Stopped tracking '+abbrev[teamID], 'info')
            setShadows()            

    # Update the Configure Favorites window or save if not applicable
    try:
        if popup.winfo_exists():
            if teamID in favorites:
                selection.itemconfig(configLogos[teamID], image=logoImages[small][teamID])
                selection.itemconfig(configShadows[teamID], state='normal')
            else:
                selection.itemconfig(configLogos[teamID], image=logoImages[bw][teamID])
                selection.itemconfig(configShadows[teamID], state='hidden')                
        else:
            saveConfig()
    except:
        saveConfig()

    return


#######################################
##
##  Toggle Mute
##
##  Switches the global mute state. Gets called by rightClick(event).
##

def toggleMute():

    global mute; global root;

    # Turn mute off
    if mute:
        mute = False
        logHandler('Mute off', 'info')
        root.wm_title('NHL Goal Horn Scoreboard')

    # Turn mute on
    else:
        mute = True
        logHandler('Mute on', 'info')
        root.wm_title('NHL Goal Horn Scoreboard (Muted)')

    return


#######################################
##
##  Toggle Debug
##
##  Displays debug messages below the scoreboard or hides them otherwise
##

def toggleDebug():

    global debug; global firstRun; global debugText; global messages;
    global ww; global wh; global sp; global dh; global fontSize;
    
    # Turn debug mode off and delete/hide everything
    if debug:
        debug = False
        if not firstRun:
            logHandler('Debug mode off', 'debug')
        messages.delete('all')
        messages.pack_forget()
        wh -= dh

    # Turn debug mode on and display the appropriate messages
    else:
        debug = True
        if not firstRun:
            logHandler('Debug mode on', 'debug')
        x = ww/2
        y = sp
        for index in range(len(debugText)):
            debugText[index] = messages.create_text(x, y, justify='center', \
                                        font=('Consolas',fontSize[small]), fill='#BBBBBB')
            y += sp
        messages.config(width=ww, height=dh)
        messages.pack()
        wh += dh
        updateDebug()
    
    return


#######################################
##
##  Update Debug
##
##  Displays the latest debug messages below the scoreboard
##

def updateDebug():

    global messages; global debugText; debug; global debugList; global ww;
    
    for index in range(len(debugText)):
        messages.itemconfig(debugText[index], text=debugList[index])
        
    return


#######################################
##
##  Debug Commands
##
##  Enables interactivity in debug mode. Triggered via Tkinter's bind
##  capability.
##
##  a: about
##  c: contact
##  o: open folder
##  s: status
##  t: tutorial
##  v: volume check
##  ?: help
##

def debugCommands(event):

    global debug; global ver; global appDir; global configFile; global logFile;
    global horns;

    if debug:

        # Display about/version information
        if event.char is 'a':
            logHandler('NHL Goal Horn Scoreboard (ver. '+ver+')', 'info')

        # Display contact/email information
        elif event.char is 'c' or event.char is 'e':
            logHandler('Email: austin@austinandemily.com', 'debug')    

        # Open the configuration folder
        elif event.char is 'o':          
            logHandler('Opening folder...', 'debug')
            if os.path.isfile(appDir+'\\'+configFile):
                openFile = r'explorer /select, "'+appDir+'\\'+configFile+'"'
            else:
                openFile = r'explorer /select, "'+appDir+'\\'+logFile+'"'
            try:
                Popen(openFile)
            except:
                pass

        # Check the favorites configuration status
        elif event.char is 's' or event.char is 'f':
            if os.path.isfile(appDir+'\\'+configFile):
                logHandler('Favorites configured', 'debug')
            else:
                logHandler('Favorites not configured', 'debug')
                
        # Start the tutorial
        elif event.char is 't':
            startTutorial()

        # Play a test goal horn to check for volume (use DET, NJD, NYR, or TOR)
        elif event.char is 'v':
            logHandler('Playing test goal horn', 'info') 
            winsound.PlaySound(horns[TOR], \
                                    winsound.SND_FILENAME | winsound.SND_ASYNC)

        # Display the list of debug commands
        elif event.char is '?' or event.char is '/':
            logHandler('a: about', 'debug')
            logHandler('c: contact', 'debug')
            logHandler('s: status', 'debug')
            logHandler('t: tutorial', 'debug')
            logHandler('v: volume check', 'debug')

    return


#######################################
##
##  Configure Favorites
##
##  Presents a full list of teams for the user to select their favorites.
##

def configureFavorites():

    global root; global popup; global selection; global favorites;
    global configRows; global configColumns; global lh; global lw;
    global configLogos; global configShadows;
    global logoImages; global shadowImage;

    # Avoid creating duplicate configuration windows
    try:
        if popup.winfo_exists():
            return
        else:
            logHandler('Configuring favorites...', 'info')
    except:
        logHandler('Configuring favorites...', 'info')
  
    # Tkinter-related (toplevel widget and canvas)
    popup = Tkinter.Toplevel(root)
    popup.wm_title('Configure Favorites')
    popup.iconbitmap(progDir+'\\Assets\\icon.ico')
    popup.resizable(width=False, height=False)
    popup.protocol('WM_DELETE_WINDOW', closeConfig)
    selection = Tkinter.Canvas(popup, highlightthickness=0, background='white')
    selection.config(width=(sp+lw[small])*configColumns+sp, height=(sp+lh[small])*configRows+sp)
    selection.bind('<Button-1>', selectionClick)

    # Draw the team logos according to favorite status
    teamID = 0
    for row in range(configRows):
        for column in range(configColumns):
            x = sp+(lw[small]+sp)*column+lw[small]/2
            y = sp+(lh[small]+sp)*row+lh[small]/2
            configShadows[teamID] = selection.create_image(x, y, anchor='center', \
                                        image=shadowImage[small], state='hidden')
            configLogos[teamID] = selection.create_image(x, y, anchor='center')
            if teamID in favorites:
                selection.itemconfig(configLogos[teamID], image=logoImages[small][teamID])
                selection.itemconfig(configShadows[teamID], state='normal')
            else:
                selection.itemconfig(configLogos[teamID], image=logoImages[bw][teamID])
            teamID += 1
    selection.pack()
    
    return


#######################################
##
##  Left Click in Configure Favorites
##
##  Determines the behavior of a left mouse button click in the Configure
##  Favorites selection area. Triggered via Tkinter's bind capability.
##

def selectionClick(event):

    global lh; global lw; global configRows; global configColumns;

    # Check the y coordinate
    for row in range(configRows):
        if sp+(lh[small]+sp)*row <= event.y and event.y <= sp+(lh[small]+sp)*row+lh[small]:

            #Check the x coordinate
            for column in range(configColumns):
                if sp+(lw[small]+sp)*column <= event.x and event.x <= sp+(lw[small]+sp)*column+lw[small]:
                      
                    # Toggle the favorite status of the clicked-on team
                    teamID = row*(configRows+1)+column
                    toggleFavorite(teamID)
                    return

    return


#######################################
##
##  Close Configuration Window
##
##  Saves configuration information and closes the Configure Favorites popup
##  window. Triggered via Tkinter's protocol capability.
##

def closeConfig():

    global popup;
    
    saveConfig()
    popup.destroy()

    return


#######################################
##
##  Start Tutorial
##
##  Initializes the main layout elements of the tutorial. Calls
##  navigateTutorial() for drawing assistance.
##

def startTutorial():

    global root; global popup; global tutorial; global tutorialIndex;
    global tutorialLine0; global tutorialLine1;
    global tutorialShadow; global tutorialLamp; global tutorialLogo;
    global tutorialBack; global tutorialNext;
    global tw; global th; global tp; global to;
    global instructionOffset; global logoOffset;
    global shadowImage; global lampFrames; global logoImages;

    # Tkinter-related (toplevel widget and canvas)
    popup = Tkinter.Toplevel(root)
    popup.wm_title('Tutorial')
    popup.iconbitmap(progDir+'\\Assets\\icon.ico')
    popup.resizable(width=False, height=False)
    popup.protocol('WM_DELETE_WINDOW', closeTutorial)
    tutorial = Tkinter.Canvas(popup, highlightthickness=0, background='white')
    tutorial.config(width=tw, height=th)
    tutorial.bind('<Button-1>', tutorialClick)

    # Text
    x = tw/2
    y = tp + instructionOffset
    tutorialLine0 = tutorial.create_text(x, y, font=('TradeGothic-Light',14), fill='#333333')
    y += to
    tutorialLine1 = tutorial.create_text(x, y, font=('TradeGothic-Light',14), fill='#333333')

    # Images
    y = th-tp-to-logoOffset
    tutorialShadow = tutorial.create_image(x, y, anchor='center', \
                                            image=shadowImage[large], state='hidden')
    tutorialLamp = tutorial.create_image(x, y, anchor='center', \
                                            image=lampFrames[large][0], state='hidden')
    tutorialLogo = tutorial.create_image(x, y, anchor='center', \
                                            image=logoImages[large][PIT])
    # Navigation
    x = to
    y = th/2
    tutorialBack = tutorial.create_text(x, y, font=('TradeGothic-Light',30), \
                                        fill='#BBBBBB', text='‹')
    x = tw-to
    tutorialNext = tutorial.create_text(x, y, font=('TradeGothic-Light',30), \
                                        fill='#BBBBBB', text='›')            

    # Start tutorial
    tutorial.pack()
    navigateTutorial('next')
    logHandler('Tutorial started', 'info')
    
    return


#######################################
##
##  Navigate Tutorial
##
##  Draws and animates elements for the tutorial pages. Gets called by
##  initializeScoreboard() or is triggered via Tkinter's bind capability.
##
##  direction: direction in which to navigate ('back' or 'next')
##

def navigateTutorial(direction):

    global popup; global tutorial; global tutorialIndex;
    global tutorialLine0; global tutorialLine1;
    global tutorialShadow; global tutorialLamp; global tutorialLogo;
    global tutorialBack; global tutorialNext;
    global animationStack; 
    global lampLength; global lampFrames; global numFrames;

    # Determine the next tutorial page
    if 'back' in direction.lower():
        tutorialIndex -= 1
        if tutorialIndex < 0:
            tutorialIndex = 0
            return
    elif 'next' in direction.lower():
        tutorialIndex += 1
    else:
        logHandler('INVALID TUTORIAL NAVIGATION', 'warning')
        return

    # Clear any animation from the previous tutorial page
    for pop in range(len(animationStack)):
        try:
            tutorial.after_cancel(animationStack.pop())
        except:
            pass
    animationStack = [0]

    # Draw and animate the appropriate tutorial page (or close if finished)
    if tutorialIndex is 0:
        tutorial.itemconfig(tutorialBack, state='hidden')
        tutorial.itemconfig(tutorialLine0, text='Click on teams on the scoreboard')
        tutorial.itemconfig(tutorialLine1, text='to begin tracking them.')
        tutorial.itemconfig(tutorialShadow, state='hidden')
        tutorial.itemconfig(tutorialLamp, state='hidden')
        for cycle in range(lampLength):
            animationStack.append(tutorial.after((cycle*2+1)*1000, lambda: \
                           tutorial.itemconfig(tutorialShadow, state='normal')))
            animationStack.append(tutorial.after((cycle*2+2)*1000, lambda: \
                           tutorial.itemconfig(tutorialShadow, state='hidden')))    
    elif tutorialIndex is 1:
        tutorial.itemconfig(tutorialBack, state='normal')
        tutorial.itemconfig(tutorialLine0, text='Goal horns will play whenever')
        tutorial.itemconfig(tutorialLine1, text='tracked teams score.')
        tutorial.itemconfig(tutorialShadow, state='hidden')
        tutorial.itemconfig(tutorialLamp, state='normal')
        tutorial.itemconfig(tutorialLamp, image=lampFrames[large][0])
        for cycle in range(lampLength):
            for frame in range(1, numFrames):
                tOn = int((cycle+frame/(2.0*numFrames))*1000)
                tOff = int((cycle+(numFrames*2-frame)/(2.0*numFrames))*1000)
                animationStack.append(tutorial.after(tOn, lambda frame=frame: \
                            tutorial.itemconfig(tutorialLamp, image=lampFrames[large][frame])))
                animationStack.append(tutorial.after(tOff, lambda frame=frame: \
                            tutorial.itemconfig(tutorialLamp, image=lampFrames[large][frame])))
            animationStack.append(tutorial.after(int((cycle+0.5)*1000), lambda frame=frame: \
                          tutorial.itemconfig(tutorialLamp, image=lampFrames[large][numFrames])))
        animationStack.append(tutorial.after(lampLength*1000, lambda: \
                        tutorial.itemconfig(tutorialLamp, state='hidden')))        
    elif tutorialIndex is 2:
        tutorial.itemconfig(tutorialLine0, text='Your favorite teams will be tracked')
        tutorial.itemconfig(tutorialLine1, text='by default if they are playing.')
        tutorial.itemconfig(tutorialShadow, state='normal')
        tutorial.itemconfig(tutorialLamp, state='hidden')
    else:
        closeTutorial()
    
    return


#######################################
##
##  Left Click in Tutorial
##
##  Determines the behavior of a left mouse button click in the Tutorial.
##  Triggered via Tkinter's bind capability.
##

def tutorialClick(event):

    global tw; global th; global tp; global to;

    if tw-tp-to <= event.x:
        navigateTutorial('next')
    elif event.x <= tp+to:
        navigateTutorial('back')

    return


#######################################
##
##  Close Tutorial Window
##
##  Closes the Tutorial popup window and proceeds to configure favorites.
##  Triggered via Tkinter's protocol capability.
##

def closeTutorial():

    global popup

    popup.destroy()
    configureFavorites()

    return


#######################################
##
##  Load Configuration Information
##
##  Retrieves the user's preferences from the configuration file.
##

def loadConfig():

    global appDir; global configFile; global noConfig; global favorites; 

    # Reset the list of favorite teams
    favorites = []

    # Read in a list of teams from the configuration file
    try:
        doc = open(appDir+'\\'+configFile, 'r+')
        text = doc.readline().upper()
        doc.close()
        logHandler('Favorites loaded', 'info')
    except:
        logHandler('CONFIGURATION READ ERROR', 'error')
        noConfig = True
        return

    # Check for team abbreviations and add to favorites
    for index, team in enumerate(abbrev):
        if team in text:
            favorites.append(index)
    
    return


#######################################
##
##  Save Configuration Information
##
##  Saves the user's preferences to the configuration file.
##

def saveConfig():

    global appDir; global configFile; global configRows; global configColumns;
    global favorites; global abbrev;

    try:     
        # Compile the list of favorites
        if len(favorites) > 0:
            favoritesText = '['
            for teamID in favorites:
                favoritesText += abbrev[teamID]+', '
            favoritesText = favoritesText[:-2]+']\n'

            # Write to the configuration file
            doc = open(appDir+'\\'+configFile, 'w+')
            doc.write(favoritesText)
            doc.write('\n'+'-'*52+'\n')
            doc.write('\n\nINSTRUCTIONS\n')
            doc.write('------------\n')
            doc.write('Place your favorite team\'s three-letter abbreviation\n')
            doc.write('inside the brackets above. Multiple teams should be\n')
            doc.write('separated by commas.\n')
            doc.write('\nExample: [COL, PIT] to track Colorado and Pittsburgh\n')
            doc.write('\n\nTEAM ABBREVIATIONS\n')
            doc.write('------------------\n')
            teamID = 0
            for row in range(configRows):
                abbrevText = ''
                for column in range(configColumns):
                    abbrevText += abbrev[teamID]+', '
                    teamID += 1
                abbrevText = abbrevText[:-2]+'\n'
                doc.write(abbrevText)
            doc.close()
                         
            logHandler('Favorites saved', 'info')
        
    except Exception:
        logHandler('CONFIGURATION WRITE ERROR', 'exception')
        
    return


#######################################
##
##  Load Images
##
##  Loads the team logo images for the purpose of filling the scoreboard.
##  Also loads the goal lamp glow animation frames, logo drop shadows, and a
##  splash screen image. Only needs to be called once. 
##

def loadImages():

    global progDir; global numTeams;
    global logoImages;
    global numFrames; global lampFrames;
    global shadowImage; global splashImage;

    imageDirectory = progDir+'\\Assets\\Images\\'
    try:
        for index, team in enumerate(abbrev[:numTeams]):
            logoImages[large][index] = Tkinter.PhotoImage(file=imageDirectory+'\\Large\\'+team+'.gif')
            logoImages[small][index] = Tkinter.PhotoImage(file=imageDirectory+'\\Small\\'+team+'.gif')
            logoImages[bw][index] = Tkinter.PhotoImage(file=imageDirectory+'\\Small\\BW\\'+team+'.gif')
        logoImages[large][NHL] = Tkinter.PhotoImage(file=imageDirectory+'\\Large\\NHL.gif')
        logoImages[small][NHL] = Tkinter.PhotoImage(file=imageDirectory+'\\Small\\NHL.gif')
        logoImages[bw][NHL] = Tkinter.PhotoImage(file=imageDirectory+'\\Small\\BW\\NHL.gif')
                                     
        for index in range(numFrames+1):
            lampFrames[large][index] = Tkinter.PhotoImage(file=imageDirectory+'\\Large\\lamp'+str(index*10)+'.gif')
            lampFrames[small][index] = Tkinter.PhotoImage(file=imageDirectory+'\\Small\\lamp'+str(index*10)+'.gif')                                                   

        shadowImage[large] = Tkinter.PhotoImage(file=imageDirectory+'\\Large\\shadow.gif')
        shadowImage[small] = Tkinter.PhotoImage(file=imageDirectory+'\\Small\\shadow.gif')
                                                       
        splashImage = Tkinter.PhotoImage(file=imageDirectory+'splash.gif')
    except Exception:
        logHandler('IMAGE LOAD ERROR', 'exception')

    return


#######################################
##
##  Load Horns
##
##  Sets the audio filenames for the goal horns of tracked teams.
##  Only needs to be called once.
##
    
def loadHorns():

    global progDir; global numTeams; global horns;
    
    hornDirectory = progDir+'\\Assets\\Audio\\'
    for index, team in enumerate(abbrev[:numTeams]):
        horns[index] = hornDirectory+team+'.wav'

    return


#######################################
##
##  Log Handler
##
##  Takes care of printing messages to the console, writing messages to the log
##  file, and displaying them in debug mode.
##
##  string: message to print, write, and log
##  level: logging level ('info', 'debug', 'warning', 'error', or 'exception')
##

def logHandler(string, level):

    global debugList; global debug;

    try:
        # Print to console
        print string

        # Log to file
        if 'info' in level.lower(): logging.info(string)
        elif 'debug' in level.lower(): logging.debug(string)
        elif 'warning' in level.lower(): logging.warning(string)
        elif 'error' in level.lower(): logging.error(string)
        elif 'exception' in level.lower():
            logging.exception(string)
            return
        else: logging.info(string)

        # Display in debug
        debugList.pop(0)
        debugList.append(string)
        if debug:
            updateDebug()
        
    except:
        print('LOG HANDLER ERROR')
        logging.error('LOG HANDLER ERROR')
        debugList.pop(0)
        debugList.append('LOG HANDLER ERROR')
        if debug:
            updateDebug()

    return


####################################  MAIN  ####################################


# Note the version
logHandler('NHL Goal Horn Scoreboard (ver. '+ver+')', 'info')

# Tkinter-related (root widget, canvases, etc.)
root = Tkinter.Tk()
root.configure(background='white')
root.wm_title('NHL Goal Horn Scoreboard')
root.iconbitmap(progDir+'\\Assets\\icon.ico')
root.resizable(width=False, height=False)
root.bind('<Button-1>', leftClick)
root.bind('<Button-3>', rightClick)
root.bind('<Key>', debugCommands)
scoreboard = Tkinter.Canvas(root, highlightthickness=0, background='white')
messages = Tkinter.Canvas(root, highlightthickness=0, background='#333333')
menu = Tkinter.Menu(root, tearoff=0)

# Load assets
loadImages()
loadHorns()    

# Load user data or start the tutorial
loadConfig()
if noConfig: 
    startTutorial()
   
# Begin checking for scores
checkScoresWrapperThreaded()

# Tkinter event loop
try:
    root.mainloop()
except Exception:
    logHandler('MAINLOOP ERROR', 'exception')
