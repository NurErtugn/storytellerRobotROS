#!/usr/bin/env python3

import http
import os
from pynput.keyboard import Key, Listener # functions for controlling the keyboard  & mice
import smach #for creating hieraryical statemachine
#import rospy
#from qt_robot_interface.srv import *
#from qt_robot_interface.srv import 
import story_generation as ai #for generating story prompts 
from sentiment_analysis import Classifier, sentiment #module for sentiment analysis on text 
#from robot_interaction import Robot
from mock_robot_interaction import Mock_Robot #test robot when theres no real robot support
import webbrowser #allows opening web pages in browser 
import server #server related functioonality

#QT 
#NO ROBOT SUPPORT: Mock_Robot()
robot =Mock_Robot() # Robot() #Robot()
#SPEECH_NEUTRAL = True ==> robot delivers a neutral tone speech

#For web module
local_data = None  #storing data related to web interactions 

#For evaluation state
done_questions = True #It indicates that there are currently no questions to be asked or that all questions have been asked and answered.
questions = [] #his list is likely intended to store the questions that need to be asked during the evaluation state. Each question can be added to this list as needed during the program's execution.

#For the sentiment classifier
AUTO_SPLIT = True #controls wheather the inout text for sentiment analysis should be automatically split into sentences befor passing the sentiment classifier 
classifier = Classifier() #performs sentiment analysis

#For the gestures, state of the robot gestures for the interactions
state_index = 0 #tracks the current state 
state = ['Greetings', 'Storytelling', 'Evaluation', 'Goodbye'] #list of possible states 

chosen_language = -1 #no lang is chosen yet 
language = ''
next_global_state = '' # next state transition in the state machine based on user input or system events. It is initialized as an empty string ''.


#This function is called when a key is pressed and changes the next state of the state machine
def key_transition(key): #to handle the key presses . updates global variables based on the key press
    global next_global_state
    global state_index 
    global state #"global" can get accessed and be modified from anywhere

    if state[state_index] == 'Greetings': #if the current state is greetings,pressing the right key will transition to next state & update the state index to 1 
        if key == Key.right: #Go to Storytelling
            next_global_state = 'nextContent'
            state_index = 1

    elif state[state_index] == 'Storytelling': #if the current state is "storytelling"
        if key== Key.right: #Go to Evaluation #pressing the right arraw key will transition to the evaluation state
            next_global_state = 'nextEvaluation'
            state_index = 2
        elif key == Key.left: #Repeat the story pressing left key will repeat the storry
            next_global_state = 'repeatStory'
        elif key == Key.esc: #Goodbye pressing escape key will  will trigger goodbye state 
            next_global_state = 'nextGoodbye'
            state_index = 3

    elif state[state_index] == 'Evaluation':
        if key == Key.left: #Go to another story
            next_global_state = 'nextStory'
            state_index = 1
        elif key == Key.esc: #Goodbye
            next_global_state = 'nextGoodbye'
            state_index = 3     
ls = Listener(on_press = key_transition) #captures key press
ls.start()


#Configure the language of the robot, based on what the user chose in the website
def config_language(): #making robot speak  #sets the lang based on the input 
    global chosen_language
    global language

    #NO ROBOT SUPPORT: comment the two lines below
    # speechConfig = rospy.ServiceProxy('/qt_robot/speech/config', speech_config)
    # rospy.wait_for_service('/qt_robot/speech/config')

    chosen_language = int(server.await_response())
    if chosen_language == 2:
        language = 'de'
        # status = speechConfig("de-DE",0,100) #NO ROBOT SUPPORT: comment this line
    elif chosen_language == 1:
        language = 'fr'
        # status = speechConfig("fr-FR",0,100) #NO ROBOT SUPPORT: comment this line
    elif chosen_language == 0: 
        language = 'en'
        # status = speechConfig("en-US",0,100) #NO ROBOT SUPPORT: comment this line
    print("Language chosen: ", language)
    print()


    
def main():

    
    #Execute smach plan
   
    server.start_thread()
    print("Started the server")
    index_html =os.path.abspath('/home/storytelling/catkin_ws/src/storytelling/fake_index.html')
  
    webbrowser.open_new_tab(index_html) 
    print("served the page")
    config_language()
    print("configured the lang")
    outcome = sm.execute()
    print("outcome good")
    server.join_thread()
    print("server joined to the thread ")
    
if __name__ == '__main__':
    print("STARTING QT MODULE")
    main()
    

