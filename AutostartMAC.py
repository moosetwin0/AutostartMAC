# AutostartMAC Version 7
# READ BELOW BEFORE USING SCRIPT


# You can turn on/off the auto-demoanalyzer functionality here:
ADAtoggle = True # ex. `ADAtoggle = False`

# You can turn on/off the MAC functionality here:
MACtoggle = True # ex. `MACtoggle = False`

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
from sys import argv # for checking if in debug mode

# enter debug mode if in vscode
if (('TERM_PROGRAM' in os.environ.keys() and os.environ['TERM_PROGRAM'] == 'vscode')
or any(arg in argv for arg in ['-debug', '--debug', '-d'])): # or if debug flag is given
    print('!! DEBUG MODE !!')
    debug = True
else: debug = False
# demo with known cheater
debugdemo = {'/home/moosetwin/.steam/steam/steamapps/common/Team Fortress 2/tf/demos/2025-10-16_04-20-14.dem'}

if debug: print('!! verifying paths !!')

# check that user paths are accessible and format correctly if so
paths = [anticheat, analyzer, demospath]
for path in paths:
    if os.path.exists(os.path.expanduser(path)): # expanduser is used twice because I wanted the raise to give the path how the user typed it
        paths[paths.index(path)] = os.path.expanduser(path) # probably not the best way to replace a list item from the value but couldn't find any info online
    else: 
        raise FileNotFoundError(f'{path} is not a valid file or directory! did you forget to set the variable in AutostartMAC?')
anticheat, analyzer, demospath = paths # set variables to new, expanded paths
if debug: print('!! paths verified OK !!')

def tf2chk(): # check if TF2 is open
    # !!! psutil is showing significantly less results here in vscode for some reason. if this continues, stop debugging in vscode and remove debug checking for it 
    for proc in process_iter():
        try:
            if proc.name() == 'tf_linux64': return True
        except NoSuchProcess: # prevent edge case where process exits between fetching it and checking its name
            if debug: print('!! tf2chk() edge case caught !!')
    return False # if no processes match the name

def getdemos(): 
    return set(glob(f'{demospath}/*.dem')) # getdemos() just used as a shorthand

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
def altopen(file):
    # progs list used later to close any programs launched with altopen
    progs.append(Popen(file, cwd=os.path.dirname(file), stdout = None, stderr = None)) # cwd = relative path, ex. /a/b/ from a/b/c.file

testanalyzer = False
if debug:
    print('!! TF2 now open !!')
    print('!! would you like to skip opening TF2 and scan a test demo? Y/N !!')
    answer = input('Y/N: ').lower()
    # if yes, set testanalyzer to True. otherwise default to false
    if answer in ['y', 'yes']:
        testanalyzer = True
    else:
        print('!! starting TF2, MAC, UI !!')

try: # not actually trying to catch any exceptions, just making sure that MAC closes properly
    if not testanalyzer:     
        webopen("steam://rungameid/440") # if commented out during debugging, make sure to uncomment
        if MACtoggle: altopen(anticheat)
        print('-- Waiting for TF2 --')
        sleep(10) # required, game can be a bit screwy when starting

        while not tf2chk(): 
            sleep(1) # wait for tf2 to open
            if debug: print('!! TF2 not open !!')
        if debug: print('!! TF2 now open !!')

        if MACtoggle: webopen(gui) # do this later so that MAC has time to initialize

    demolist = getdemos()
    demosToAnalyze = []
    oldestdemo = ''
    while tf2chk() or testanalyzer: # exit if tf2 is closed without any demos queued
        if ADAtoggle: 
            # get any new demos
            demosToAnalyze.extend(getdemos() - demolist)
            if testanalyzer: 
                demosToAnalyze = [os.path.abspath('cheater test demo.dem')]
            try: # if there is a demo to check for
                # the oldest demo will always be at index 0 due to how lists work
                if oldestdemo != demosToAnalyze[0]:
                    print('-- New demo found --')
                oldestdemo = demosToAnalyze[0] # for code readability
                demolist.add(oldestdemo) # add demo to demolist so it doesn't get added to demosToAnalyze again
                # if oldest demo hasn't been modified for 3 seconds
                if (time() - os.path.getmtime(oldestdemo) >= 3): 
                    if debug: print('!! analyzing new demo !!')
                    analyze(oldestdemo)
                    demosToAnalyze.pop(0) # demo has been analyzed, remove it from queue
            except IndexError: pass # no demos to analyze, continue

            if testanalyzer:
                break # only scan test demo once
    sleep(1) # rate of checking for tf2 to close/if there are any new demos

    # once TF2 has closed: if there are any remaining demos, analyze them
    for demo in demosToAnalyze:
        analyze(demo)

    # let user read ADA output/mark cheaters before exiting
    print('-- Press Enter to exit --')
    input()

    # can't close browser tabs easily so I leave it for future me
    # future me couldn't figure out how to do this without closing the entire window
    print('-- Closing programs --')

except Exception: # create crashlog for debugging
    with open(f"{os.getcwd()}/crash.log", "w") as logfile: # create file in current directory
        traceback.print_exc(file=logfile)
    raise

finally: # make sure MAC closes
    for item in progs:
        item.kill()
