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
##  Last Revision: 02/25/16
##
##  Copyright (C) 2016 Austin Chen
##
##
##  Function List
##  -------------
##  URLhandler()
##  checkScores()
##  checkScoresWrapper()
##  initializeScoreboard()
##  renderGame(gameNum) *
##  setTeams() *
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
##  configureFavorites()
##  popupClick(event) *
##  closePopup() *
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
## W Readme
## X Save to executable
##   N Clean up imports (e.g. times)
##   X How to include font?
##     N Point to file
##     N Include the file and put instructions in README
##     X Use an installer
##       X Installer file locations
##       X Install fonts
##       X Install VC (always)
##       X Errno 13 when running from Program Files 
##         N Require run as administrator
##         X Move rewritable files to AppData/Roaming
##           X Rename thisDir to progDir
##           X template.cfg in Assets
##         X folder must exist before reading/writing a file
##       X Setup copy
##   X Bundle the Visual C runtime DLL
##   X Include source (.py files)
##   X License (put copyright info up top)
## X Use NHL shield as splash screen
## X Redo lamp (reduce glow size)
## X Right-click to configure, mute, and add/remove from favorites
## X Debug mode displays last 5 lines of console output at the bottom
##   X Lingering 'time' itemconfig(timeText[gameNum], text=gameTime)
##   X Change debug font to consolas/courier, white on black text
##   X Avoid use of debugLength as conditional, only use for initialization (once)
##   X Rename page to scoreboard, debug area to messages
## N Muted title cut off, change to ascii?
## X Check initializing images/text actually creating them double? Just one per
## X Check toggle mute/debug after new game switchover?
## X Check debug mode and splash screen (resized splash screen width)
## N Prevent multiple timeout/URL open errors
## X Print to log with logging instead of console
## X Import to-do from Outlook task
##
## X Rearrange function order
## X Lamp animation
##   X 2-frame version
##   X 10-frame version (with opacity, shrinking outer glow won't work)
##     X Can't use variables to denote frames within lambda
##     N Add transparency so shadows don't get covered (can't with .gif)
##     W Clean up lampFrames usage (initialize lamps to 0 or None?)
## X Make lamp/shadow generic
##
## X Changed widget initializations to int 0
## N root.after takes arguments? No need for lambda
## N Prevent URL lag by using threading.thread? thread.start, thread.join
##   X Need to define URLthread globally to prevent multiple instances
##   X Do URLhandler exceptions get raised appropriately? Within checkScores?
## N Define functions within functions? No real advantages
##
## X Favorites selection (see email, but bw/50% if no and color/shadow if yes)
##   X Design GUI in Illustrator
##   X Display in Tkinter
##   X Add shadows to config
##   X Reorganize images: [0], [1], [2], for large, small, and bw
##   X Automatic config if no .cfg file detected
##   X Clean up new functions
##
## X 10th goal not detected because '10' < '9', cast to int
## X Add 'small' size for 768px height displays
##   X 60% size
##   X Set dimension variables
##   X How to toggle between sizes?
##     N Context menu? 
##     X Automatically if < 1024 using root.winfo_screenheight()
##   X Looks bad... bring back multiple columns?
##   X Undo small size for images
## X Bring back multiple columns
##   X Math from previous versions
##   X Redo click logic
##   X Change automatically
##   X Debug doesn't scale
##   X Clean up variables and scopes
##
## W Change refresh rate to 15s, lag limit to 5s
## W Dynamic refreshing (double refresh time if all games finished or not yet started)
## \ Instructions (display when scoresheet/favorites not detected?)
##   \ Location/logistics
##     X Place in canvas above favorites configuration
##     W Hide main scoreboard until favorites have been configured?
##   W Design
##   ! Copy


import Tkinter                  #for graphics
import os                       #for file management
import sys                      #for the script name
import winsound                 #for playing wav files
import time                     #for delays
import logging                  #for debugging
from urllib import urlopen      #for reading in webpage content
from shutil import copyfile     #for high-level file operations


################################################################################
##
##  Declarations/Initializations
##

# Administrative information
firstRun = True                     #first run flag
noConfig = False                    #no configuration file flag
timeout = False                     #delayed update flag
refreshRate = 10                    #how often to update, in seconds
lagLimit = 4                        #allowable update delay, in seconds
checkSumPrev = 0                    #scoreboard switchover detection
tPrev = 0                           #time of the last update, in seconds
tTimeout = 30                       #timeout threshold, in minutes
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

# Display parameters
sp = 20                             #spacer
lh = [50, 30]                       #logo height
lw = [100, 60]                      #logo width
tw = 70                             #text width
scoreOffset = 15                    #score text offset
periodOffset = 41                   #period text offset
fontSize = [26, 10]                 #font sizes
ww = 0                              #window width
wh = 0                              #window height
sw = 128                            #splash screen width
sh = 146                            #splash screen height
dh = sp*(debugLength+1)             #debug height
ih = 100                            #instruction height
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
    global tPrev; global tTimeout;  global lagLimit;
    
    test = True

    # Read in the raw NHL scores information from ESPN
    if not test:
        t0 = time.time()
        try:
            fullText = urlopen(URL).read()
        except Exception as details:
            logHandler('URL OPEN ERROR', 'exception')
            logging.exception(details)
            raise
        t1 = time.time()
        lag = t1-t0
        if lag > lagLimit:
            logHandler('URL OPEN LAG = '+str(round(t1-t0, 2))+' SECONDS', 'warning')
            if lag > tTimeout*60:
                logHandler('TIMEOUT', 'warning')
                timeout = True
        tPrev = t1

    # Read in a test file for development
    else:
        if 'CHEN' in os.environ['COMPUTERNAME']:
            doc = open('C:\\Python27\\Scripts\\Test Scores\\scores2m.html', 'r+')
        elif 'AUSTIN' in os.environ['COMPUTERNAME']:
            doc = open('C:\\NHL Scoreboard\\Development\\Test Scores\\multi.htm')
        else:
            logHandler('FILE OPEN ERROR', 'exception')
            logHandler('Unknown development machine', 'exception')
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


    # Load assets
    if firstRun:    
        loadImages()
        loadHorns()

    # Suppress goal horns and lamps if it's been too long since the last run
    if not firstRun and time.time()-tPrev > tTimeout*60:
        logHandler('TIMEOUT', 'warning')
        timeout = True
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

    # Apply appropriate changes to the scoreboard display        
    if firstRun:
        initializeScoreboard()
        setTeams()
        if noConfig:            
            configureFavorites()
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
    global firstRun; global timeout; global Games
    global teams; global teamIDs; global scores;
    global goalFlag; global tracking;
    global timePeriod; global gameStatus; global favorites;

    try:
        checkScores()
        root.after(refreshRate*1000, checkScoresWrapper)
    except Exception as details:
        root.after(refreshRate*1000, checkScoresWrapper)
        logHandler('CHECKSCORES ERROR', 'exception')
        logging.exception(details)
        logging.debug('Error circumstances to follow...')
        logging.debug('\tfirstRun = %s, timeout = %s, numGames = %i', \
                      firstRun, timeout, numGames)
        logging.debug('\tteams = %s', ', '.join(teams))
        logging.debug('\tteamIDs = %s', ', '.join(map(str, teamIDs)))
        logging.debug('\tscores = %s', ', '.join(map(str, scores)))
        logging.debug('\tgoalFlags = %s', ', '.join(map(str, goalFlags)))
        logging.debug('\ttracking = %s', ', '.join(map(str, tracking)))
        logging.debug('\ttimePeriod = %s', ', '.join(timePeriod))
        logging.debug('\tgameStatus = %s', ', '.join(map(str, gameStatus)))
        logging.debug('\tfavorites = %s', ', '.join(map(str, favorites)))
        logging.debug('\tfullText (may not be up to date) = %s', fullText)
        raise #for development only, delete when finished debugging

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
    global sp; global lh; global ww; global wh; global dh;
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
    ww = sp+lw[large]+sp+tw+sp+lw[large]+sp
    if wh+dh > root.winfo_screenheight():
        logHandler('Multiple columns enabled', 'debug')
        multiColumn = True
        wh = sp+(lh[large]+sp)*(numGames/2+numGames%2)
        ww = sp+lw[large]+sp+tw+sp+lw[large] + sp + sp+lw[large]+sp+tw+sp+lw[large] + sp
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

def renderGame(gameNum):

    global scoreboard; global sp; global lh; global lw; global tw;
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
    x = (sp+lw[large]+sp+tw+sp+lw[large]+sp)*column +sp+lw[large]/2
    y = sp+(lh[large]+sp)*(row)+lh[large]/2
    shadows[gameNum*2] = scoreboard.create_image(x, y, anchor='center', \
                                            image=shadowImage[large], state='hidden')
    lamps[gameNum*2] = scoreboard.create_image(x, y, anchor='center', \
                                          image=lampFrames[large][0], state='hidden')
    teamLogos[gameNum*2] = scoreboard.create_image(x, y, anchor='center')
    teamLogosX[gameNum*2] = x
    teamLogosY[gameNum*2] = y

    # Text
    x = (sp+lw[large]+sp+tw+sp+lw[large]+sp)*column +sp+lw[large]+sp+tw/2
    y = sp+(lh[large]+sp)*(row)+scoreOffset
    scoreText[gameNum] = scoreboard.create_text(x, y, justify='center', font=('TradeGothic-Bold',fontSize[large]), fill='#333333')
    y = sp+(lh[large]+sp)*(row)+periodOffset
    periodText[gameNum] = scoreboard.create_text(x, y, justify='center', font=('TradeGothic-Light',fontSize[small]), fill='#333333')
    y = sp+(lh[large]+sp)*(row)+lh[large]/2-1
    timeText[gameNum] = scoreboard.create_text(x, y, justify='center', font=('TradeGothic-Light',fontSize[small]), fill='#333333')
    
    # Home team images
    x = (sp+lw[large]+sp+tw+sp+lw[large]+sp)*column +sp+lw[large]+sp+tw+sp+lw[large]/2
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
##  configure the score and period/time text. Should only be used one time, upon
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
##  Update Scoreboard
##
##  Configures the score and period/time text based on the most current data.
##  Should be used (at the end of) every refresh cycle.
##

def updateScoreboard():

    global scoreboard; global numGames; global gameStatus; global timePeriod
    global periodText; global scoreText; global timeText; global scores;

    # Loop through the games
    for gameNum in range(numGames):
        
        # Games not yet started (0)
        if gameStatus[gameNum] == 0:
            gameTime = timePeriod[gameNum]
            if 'ET' in gameTime:
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
    timeNow = time.localtime()
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

def animateLamp(lamp):

    global scoreboard; global refreshRate; global lampFrames; global numFrames;

    scoreboard.itemconfig(lamp, state='normal')
    for cycle in range(10):
        for frame in range(1, numFrames):
            tOn = int((cycle+frame/(2.0*numFrames))*1000)
            tOff = int((cycle+(numFrames*2-frame)/(2.0*numFrames))*1000)
            scoreboard.after(tOn, lambda frame=frame: \
                        scoreboard.itemconfig(lamp, image=lampFrames[large][frame]))
            scoreboard.after(tOff, lambda frame=frame: \
                        scoreboard.itemconfig(lamp, image=lampFrames[large][frame]))
        scoreboard.after(int((cycle+0.5)*1000), lambda frame=frame: \
                      scoreboard.itemconfig(lamp, image=lampFrames[large][frame]))            
    scoreboard.after(refreshRate*1000, lambda: \
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
    ww = sp+lw[large]+sp+tw+sp+lw[large]+sp
    wh = sp*1.5 + sh + sp*1.5
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
##  Adds or removes a team from favorites. Gets called by rightClick(event).
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

    global debug; global debugText; global messages;
    global ww; global wh; global sp; global dh; global fontSize;
    
    # Turn debug mode off and delete/hide everything
    if debug:
        debug = False
        logHandler('Debug mode off', 'debug')
        messages.delete('all')
        messages.pack_forget()
        wh -= dh

    # Turn debug mode on and display the appropriate messages
    else:
        debug = True
        logHandler('Debug mode on', 'debug')
        x = ww/2
        y = sp
        for index in range(len(debugText)):
            debugText[index] = messages.create_text(x, y, justify='center', \
                                        font=('Consolas',fontSize[small]), fill='#BBBBBB')
            y += sp
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
##  Configure Favorites
##
##  Presents a full list of teams for the user to select their favorites.
##

def configureFavorites():

    global root; global popup; global selection; global favorites;
    global configRows; global configColumns; global lh; global lw;
    global configLogos; global configShadows;
    global logoImages; global shadowImage;
    global noConfig; global ih;

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
    popup.protocol('WM_DELETE_WINDOW', closePopup)
    noConfig = True
    if noConfig:
        instructions = selection = Tkinter.Canvas(popup, highlightthickness=0, background='gray')
        instructions.config(width=(sp+lw[small])*configColumns+sp, height=ih)
        #x = sp
        #y = sp
        #debugList = ['']*debugLength
        #for index in range(len(debugText)):
        #instructions.create_text(x, y, justify='center', \
        #                                font=('TradeGothic-Light',fontSize[small]), \
        #                                fill='#333333', text='lorum ipsum dolor')

        instructions.pack()





    selection = Tkinter.Canvas(popup, highlightthickness=0, background='white')
    selection.config(width=(sp+lw[small])*configColumns+sp, height=(sp+lh[small])*configRows+sp)
    selection.bind('<Button-1>', selectionClick)

    # Draw the team logos according to favorite status
    teamID = 0
    for row in range(configRows):
        for column in range(configColumns):
            x = sp+(lw[small]+sp)*column+lw[small]/2
            y = sp+(lh[small]+sp)*row+lh[small]/2
            configShadows[teamID] = selection.create_image(x,y, anchor='center', \
                                        image=shadowImage[small], state='hidden')
            configLogos[teamID] = selection.create_image(x,y, anchor='center')
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
##  Close Popup Window
##
##  Saves configuration information and closes the Configure Favorites popup
##  window. Triggered via Tkinter's protocol capability.
##

def closePopup():

    global popup;
    
    saveConfig()
    popup.destroy()

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

    global progDir; global appDir; global configFile;
    global favorites; global abbrev;
    
    try:
        # Read in the template
        template = open(progDir+'\\Assets\\Other\\template.cfg', 'r+')
        configText = template.readlines()
        template.close()

        # Compile the list of favorites
        if len(favorites) > 0:
            favoritesText = '['
            for teamID in favorites:
                favoritesText += abbrev[teamID]+', '
            configText[0] = favoritesText[:-2]+']\n'

        # Write to the configuration favorites
        doc = open(appDir+'\\favorites.cfg', 'w+')
        doc.writelines(configText)
        doc.close()
                     
        logHandler('Favorites saved', 'info')
        
    except:
        logHandler('CONFIGURATION WRITE ERROR', 'error')
        
    return


#######################################
##
##  Load Images
##
##  Loads the team logo images for the purpose of filling the scoreboard.
##  Also loads the goal lamp glow animation frames, logo drop shadows, and a
##  splash screen image. Should only be used one time. 
##

def loadImages():

    global progDir; global numTeams;
    global logoImages;
    global numFrames; global lampFrames;
    global shadowImage; global splashImage;

    imageDirectory = progDir+'\\Assets\\Images\\'

    for index, team in enumerate(abbrev[:numTeams]):
        logoImages[large][index] = Tkinter.PhotoImage(file=imageDirectory+'\\Large\\'+team+'.gif')
        logoImages[small][index] = Tkinter.PhotoImage(file=imageDirectory+'\\Small\\'+team+'.gif')
        logoImages[bw][index] = Tkinter.PhotoImage(file=imageDirectory+'\\Small\\BW\\'+team+'.gif')
    logoImages[large][NHL] = Tkinter.PhotoImage(file=imageDirectory+'\\Large\\NHL.gif')
    logoImages[small][NHL] = Tkinter.PhotoImage(file=imageDirectory+'\\Small\\NHL.gif')
    logoImages[bw][NHL] = Tkinter.PhotoImage(file=imageDirectory+'\\Small\\BW\\NHL.gif')
                                 
    for index in range(numFrames):
        lampFrames[large][index] = Tkinter.PhotoImage(file=imageDirectory+'\\Large\\lamp'+str(index*10)+'.gif')
        lampFrames[small][index] = Tkinter.PhotoImage(file=imageDirectory+'\\Small\\lamp'+str(index*10)+'.gif')                                                   

    shadowImage[large] = Tkinter.PhotoImage(file=imageDirectory+'\\Large\\shadow.gif')
    shadowImage[small] = Tkinter.PhotoImage(file=imageDirectory+'\\Small\\shadow.gif')
                                                   
    splashImage = Tkinter.PhotoImage(file=imageDirectory+'splash.gif')

    return


#######################################
##
##  Load Horns
##
##  Sets the audio filenames for the goal horns of tracked teams.
##  Should only be used one time.
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

def logHandler(string, level):

    global debugList; global debug;

    try:
        # Print to console
        print string

        # Log to file
        if level.lower == 'info': logging.info(string)
        elif level.lower == 'debug': logging.debug(string)
        elif level.lower == 'warning': logging.warning(string)
        elif level.lower == 'error': logging.error(string)
        elif level.lower == 'critical': logging.critical(string)
        elif level.lower == 'exception':
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
    
# Tkinter-related (root widget, canvases, etc.)
root = Tkinter.Tk()
root.wm_title('NHL Goal Horn Scoreboard')
root.iconbitmap(progDir+'\\Assets\\icon.ico')
root.resizable(width=False, height=False)
root.bind('<Button-1>', leftClick)
root.bind('<Button-3>', rightClick)
scoreboard = Tkinter.Canvas(root, highlightthickness=0, background='white')
messages = Tkinter.Canvas(root, highlightthickness=0, background='#333333')
menu = Tkinter.Menu(root, tearoff=0)

# Load user data
loadConfig()
   
# Begin checking for scores
checkScoresWrapper()

# Tkinter event loop
try:
    root.mainloop()
except Exception as details:
    logHandler('MAINLOOP ERROR', 'exception')
    logHandler(details, 'exception')
    logging.exception('Error details to follow...')
    raise
