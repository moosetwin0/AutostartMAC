# AutostartMAC Version 4
# READ BELOW BEFORE USING SCRIPT


# You can turn on/off the auto-demoanalyzer functionality here:
ADAtoggle = True # ex. `ADAtoggle = False`

# You can turn on/off the MAC functionality here:
# MAC is currently broken so it's off by default
MACtoggle = False # ex. `MACtoggle = False`

# Set this variable to the path of your client_backend file 
# ex. `anticheat = '~/.steam/steam/steamapps/common/Team Fortress 2/megaanticheat stuff/client_backend'`
anticheat = '~/.steam/steam/steamapps/common/Team Fortress 2/megaanticheat stuff/client_backend'

# Set this variable to the web interface link MAC gives you
# ex. `gui = 'http://127.0.0.1:1984'`
gui = 'http://127.0.0.1:1984'


# If you are using the AutoDemoAnalyzer functionality:

    # The demo analyzer can be found at https://github.com/MegaAntiCheat/analysis-template-rust, do not use the /demolyzer repository
    # Make sure that you have built it with the release cli version

    # Set this variable to the path of your demo analyzer folder:
    # ex. `analyzerpath = '~/Desktop/analysis-template-rust-main/target/release/cli'`
analyzer = '~/.steam/steam/steamapps/common/Team Fortress 2/megaanticheat stuff/analysis-template-rust-main/target/release/cli'

    # Set this variable to the path of your TF2 demos folder:
    # ex. `demospath = '~/.steam/steam/steamapps/common/Team Fortress 2/tf/demos'`
demospath = '~/.steam/steam/steamapps/common/Team Fortress 2/tf/demos'

    # Whether to output detections as a json file with your demo
    # Leave as False to just print to the terminal
detectfile = True # example: `detectfile = True`

    # Optional arguments to be passed to the analyzer:
    # Leave blank to just scan the demo with the default settings:
arguments = '' # example: `arguments = '-a the_best_algorithm -p'`


# Beyond this point is the actual code, you can finish reading here





import traceback # for logging exceptions
from time import sleep, time # sleep for both, time for ADA
import os # used everywhere
from webbrowser import open as webopen # for A-MAC
from psutil import process_iter, NoSuchProcess # for A-MAC
from subprocess import Popen, PIPE, CalledProcessError # for both
from glob import glob # for ADA

# check that user paths are accessible and format correctly if so
paths = [anticheat, analyzer, demospath]
for path in paths:
    if os.path.exists(os.path.expanduser(path)): # expanduser is used twice because I wanted the raise to give the path as the user typed it
        paths[paths.index(path)] = os.path.expanduser(path) # probably not the best way to replace a list item from the value but couldn't find any info online
    else: 
        raise FileNotFoundError(f'{path} is not a valid file or directory! did you forget to set the variable in AutostartMAC?')


if ('TERM_PROGRAM' in os.environ.keys() and os.environ['TERM_PROGRAM'] == 'vscode'): # if in my debug environment
    print('!! DEBUG MODE !!')
    debug = True
else: debug = False
debugdemo = {'/home/moosetwin/.steam/steam/steamapps/common/Team Fortress 2/tf/demos/2025-10-16_04-20-14.dem'} # demo with cheater

def tf2chk(): # check if TF2 is open
    for proc in process_iter():
        try:
            if proc.name() == 'tf_linux64': return True
        except NoSuchProcess: pass # prevent edge case where process exits between fetching it and checking its name
    return False # if no processes match the name

def getdemos(): 
    return set(glob(f'{demospath}/*.dem')) # getdemos() just used as a shorthand

# TF2 on linux doesn't lock demofiles for some reason so I have to do this
demolist = getdemos()
olddemo = ''
def demojuggling():
    global demolist
    global olddemo
    # check for new demos
    newdemo = getdemos() - demolist # see if there is any new demos since last we checked
    if debug: 
        print('enter 0 if you\'d like to create the demo yourself')
        print('enter 1 if you\'d like to use a test demo')
        debugoption = '' # have to initialize variable for while loop
        while debugoption not in ['0', '1', '']: # enter to make it yourself
            debugoption = input('0 or 1: ')
            if debugoption == '1': 
                newdemo = debugdemo # no need to make if statement for '0'
    # handle new demos
    if newdemo:
        demolist = getdemos() # only need to update the list if it's changed
        print('-- New demo found --')
        if olddemo:  # a (maybe over-)complicated buffer to delay the demos until they have been written
            finisheddemo = olddemo # move old demo to temp var so it isn't lost
            olddemo = newdemo.pop() # remember new demo for later
            return finisheddemo # old demo finished writing, analyze
        else: # only runs for the first demo
            olddemo = newdemo.pop() # remember new demo for later
            return False # demo still being written, don't analyze yet

def analyze(demotoanalyze):
    # run the analyzer, probably not the best way to do this but I couldn't be bothered to figure out rust
    print(f"-- Analyzing {demotoanalyze} --")
    # from https://stackoverflow.com/a/28319191, required to keep live printing while adding file write functionality 
    linelist = []
    cmd = [analyzer, '-i', demotoanalyze, arguments]
    with Popen(cmd, stdout=PIPE, bufsize=1, universal_newlines=True) as p: # some of these params might not be needed on linux but if it works I ain't touching it
        for line in p.stdout: # pyright: ignore[reportOptionalIterable]
            print(line, end='') # process line here
            linelist.append(line)
    if p.returncode != 0:
        raise CalledProcessError(p.returncode, p.args)
    if detectfile: # if we should write to file
        analysisfile = demotoanalyze.strip('.dem') + ' analysis.txt' # create file in same folder as demo
        with open(f"{analysisfile}", 'w') as file:
            for item in linelist:
                file.write(item) # write output, line by line

# used when it is required to run a thing while continuing execution
progs = []
def altopen(filepath):
    # progs list used later to close any programs launched with altopen
    progs.append(Popen(filepath, cwd=path.split(filepath)[0], stdout = None, stderr = None)) # cwd = relative path, ex. /a/b/ from a/b/c.file

try: # not actually trying to catch any exceptions, just making sure that MAC closes properly
    webopen("steam://rungameid/440") # if commented out during debugging, make sure to uncomment
    if MACtoggle: altopen(anticheat)
    print('-- Waiting for TF2 --')
    sleep(10) # required, game can be a bit screwy when starting

    while not tf2chk(): sleep(1) # wait for tf2 to open

    if MACtoggle: webopen(gui) # do this later so that MAC has time to initialize

    while tf2chk():
        if ADAtoggle: 
            newdemo = demojuggling()
            if newdemo:
                while (os.path.getmtime(newdemo) + 3 >= time()) and tf2chk(): 
                    sleep(1) # wait until demo hasn't been modified in 3 seconds
                # may halt execution for long periods of time, but this is fine as tf2 will have to be open for it to occur
                analyze(newdemo)
        sleep(1) # give a sec for tf2 to close

    if olddemo: analyze(olddemo)
    # let user read ADA output/mark cheaters before exiting
    print('-- Press Enter to exit --')
    input()

    # can't close browser tabs easily so I leave it for future me
    # future me couldn't figure out how to do this without closing the entire window
    print('-- Closing programs --')

except Exception: # create crashlog for debugging
    with open("crash.log", "w") as logfile:
        traceback.print_exc(file=logfile)
    raise

finally: # make sure MAC closes
    for item in progs:
        item.kill()
