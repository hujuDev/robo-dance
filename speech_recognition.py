import argparse
import copy
import sys
import time

from naoqi import ALBroker, ALModule, ALProxy
import main2

# Global variable to store the ReactToTouch module instance
ReactToTouch = None
memory = None
NAO_IP = "10.0.7.101"


class ReactToTouch(ALModule):
    
    #WORD_LIST = "yes;no;okay"
    VISUAL_EXPRESSION = True
    ENABLE_WORD_SPOTTING = True
    "Confidence threshold (%)"
    CONFIDENCE_THRESHOLD = 30
    
    """ A simple module able to react
        to touch events. """
    def __init__(self, name, wordList):
        ALModule.__init__(self, name)
        # No need for IP and port here because
        # we have our Python broker connected to NAOqi broker

        # Create a proxy for later use
        self.asr = ALProxy("ALSpeechRecognition")
        self.asr.pause(True)
        self.asr.setVocabulary(wordList.split(';'), self.ENABLE_WORD_SPOTTING)
        self.asr.pause(False)
        self.lastWord = "none"
        self.isWordRecognized = False

        # Subscribe to TouchChanged event:
        global memory
        memory = ALProxy("ALMemory")
        memory.subscribeToEvent("WordRecognized", "onWordRecognized")

        
    ''' methode die aufgerufen wird wenn was kommt '''
    def onWordRecognized(self, key, value, message):
        
        memory.unsubscribeToEvent("WordRecognized",
            "ReactToTouch")
        
        if(len(value) > 1 and value[1] >= self.CONFIDENCE_THRESHOLD / 100.):
            self.wordRecognized(value[0])  # ~ activate output of the box
            #self.lastWords = copy(value)
            self.lastWord = value [0]
            self.isWordRecognized = True   
        else:
            self.onNothing()
            
        memory.subscribeToEvent("WordRecognized", "onWordRecognized")


    def onNothing(self):
        print("nothing recognized")
        
    def wordRecognized(self, wordRecognized):
        self.isWordSaid = True
        print("this is recoqnized " + wordRecognized)
        
    def getLastWord(self):
        return self.lastWord
    


def waitUntilWordWasRecognized(ip, port, wordsToRecoqnize):
    """ Main entry point
    """
    # We need this broker to be able to construct
    # NAOqi modules and subscribe to other modules
    # The broker must stay alive until the program exists
    myBroker = ALBroker("myBroker",
       "0.0.0.0",   # listen to anyone
       0,           # find a free port and use it
       ip,          # parent broker IP
       port)        # parent broker port


    global ReactToTouch
    ReactToTouch = ReactToTouch("ReactToTouch", wordsToRecoqnize)
    
    isRecognized = False

    # wait until something is recognized
    while(not ReactToTouch.isWordRecognized): 
        time.sleep(2)
    
    print("this was the last recognized word: " + ReactToTouch.getLastWord())
    
    lastWord = ReactToTouch.getLastWord()
    
    wordList = wordsToRecoqnize.split(';')
    recognized_word = None
    for i in range(len(wordList)):
        if lastWord.find(wordList[i]):
            recognized_word = wordList[i]
            isRecognized = True
    
    return recognized_word

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="172.17.16.29",
                        help="Robot ip address")
    parser.add_argument("--port", type=int, default=9559,
                        help="Robot port number")
    parser.set_defaults(
        pip=NAO_IP,
        pport=9559)

    args = parser.parse_args()
    recognized_word = waitUntilWordWasRecognized(args.ip, args.port, "record;stop")
    print("It was: " + recognized_word)
    tts = ALProxy("ALTextToSpeech", args.ip, args.port)
    if(recognized_word == 'record'):
        tts.say("I recognized the word record. I am now starting to record music for 7 seconds.")
        main2.main()
    else:
        tts.say("I recognized the word stop. I am now shutting down.")
        motion = ALProxy("ALMotion", "10.0.7.101", 9559)
        motion.rest()

if __name__ == "__main__":
    main()