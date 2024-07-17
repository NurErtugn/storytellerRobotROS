import asyncio
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false" #MODIFIED FOR THE PURPOSE TO GET RID OF HUGGING FACE DEADLICK ERROR
from pynput.keyboard import Key, Listener # functions for controlling the keyboard  & mice
import smach #for creating hieraryical statemachine
#import rospy
#from qt_robot_interface.srv import *
#from qt_robot_interface.srv import 
import smach.state
import story_generation as ai #for generating story prompts 
from sentiment_analysis import Classifier, sentiment #module for sentiment analysis on text 
#from robot_interaction import Robot
from mock_robot_interaction import Mock_Robot #test robot when theres no real robot support
import webbrowser #allows opening web pages in browser 
import server #server related functioonality
from flask import Flask 
from server import send_data 
import re
import rospy
from std_msgs.msg import String


robot =Mock_Robot() # Robot() #Robot()
#SPEECH_NEUTRAL = True ==> robot delivers a neutral tone speech

#For web module
local_data = None  #storing data related to web interactions 

#For evaluat6ion state
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

def check_first_word(text,word):
    words = text.split()
    if word : 
        return words[0]== word
    return False
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


#Makes QT say <message> with <speech> function
#
def qt_says(message, to_say = True, speech=robot.say_serv_lips):
    if to_say :
        speech(message) 
    else:
        print(message,"\n") 

#This is the first state of the state machine. It begins the interaction with the robot. 
class Greetings( smach.State):
#defines the behavior for the greetings state of the state machine
    def __init__(self,subAlphaSay):
        smach.State.__init__(self, outcomes=['nextContent'])
        self.subAlphaSay= subAlphaSay
        

    def execute(self, userdata):
        global next_global_state
        global state_index
        global language
    
        robot.playGesture('QT/hi')
        greetings = "Hi! My name is Q T and we are going to learn new things today, are you ready to go on an adventure?"
        
        # greetings = "Salut! Je m'appelle Q T et nous allons apprendre de nouvelles choses aujourd'hui, êtes-vous prêt à partir à l'aventure ?"
        
        qt_says(ai.translate(greetings, language_to=language))
       # rospy.sleep(0.2)

        #Go to storytelling state
        next_global_state = 'nextContent'
        state_index = 1
        
        return next_global_state


#Storytelling state of the state machine. Here the user has time to fill out the story generation form and QT will recite the story
class Storytelling(smach.State):
    def __init__(self,subAlphaSay): #constructor  method of the greetings class. initialises the state with the specified outcomes . will indicate possible transitions to other states
        smach.State.__init__(self, outcomes=['nextGoodbye', 'clientFeedback'], output_keys=['story_prompt','sl', 'selectedQuestions', 'answers', 'suggestions'])
        self.subAlphaSay= subAlphaSay
    def execute(self, userdata): #defines the behaviour of the greetings state when its executed 
        global next_global_state
        global local_data
        global language
        
        local_data = server.await_response()
        print("LOCAL DATA RECIEVED: ", local_data)
        
        if(local_data == 'close'):
            next_global_state = 'nextGoodbye'
            return next_global_state

        inputs = local_data.split("|")

        ai_level = int(inputs[0])
        story = inputs[1]
        sl = int(inputs[2]) #STORYLENGHT , CHANGE LATER THE VARIABLE NAME 
        level = inputs[3] #age group 
    
        selectedQuestions= " "
        suggestions = " "
        answers = " "

        level_3_prompt_a = "Gardez l'histoire originale, et tissez la suite de l'histoire à partir d'ici:"

        if(ai_level==0):
            story_prompt=story            
        elif(ai_level == 1):
            story_prompt = ai.dSgDaG(story, level, str(sl)) 
            #story_prompt=story    #modified 
            if language== 'fr':
                story_prompt = ai.translate(story, 'en' , 'fr')
            elif language=='de':
                story_prompt= ai.translate(story, 'en', 'de')
          
        elif(ai_level == 2):
            story_prompt = ai.dSgDaG(story, level, str(sl), temperature=1.2) 
            if language== 'fr':
                story_prompt = ai.translate(story, 'en' , 'fr')
            elif language=='de':
                story_prompt= ai.translate(story, 'en', 'de')          

        elif(ai_level==3):
            if language== 'fr' : 
                #story_prompt= str(inputs[1]) + ai.translate(ai.complete_story(level_3_prompt_a + story_prompt + level_3_prompt_b+ ", moins de " + str(story_length)+ " mots."), language_to=language)
                story_prompt= ai.complete_story(ai.translate(level_3_prompt_a, language_to=language)  + story+  "under" + str(sl) + "words")
            elif language!= 'en':
                story_prompt== ai.complete_story(story + "Complete the rest in German" + "under" + str(sl) + "words")
            else:
                story_prompt=  ai.complete_story(story + "Complete the rest of the story in English " + "under" + str(sl) + "words")
               
        elif(ai_level==4):
            if language == 'fr':
                story_prompt= ai.translate(ai.gSbA(story,level, str(sl)),'en', 'fr')
            elif(language!='en'):
                story_prompt= ai.gSbA(story+ "In German", level,str(sl))
            else:
                story_prompt= ai.gSbA(story,level, str(sl))

        elif(ai_level==5):
            if language == 'fr':
                story_prompt= ai.translate(ai.generate_lecture_story(story,str(sl)),'en', 'fr')
            elif(language!='en'):
                story_prompt= ai.generate_lecture_story(story+ "In German",str(sl))
            else:
                story_prompt= ai.generate_lecture_story(story, str(sl))

        elif(ai_level==6):
            if language == 'fr':
                story_prompt= ai.translate(ai.generate_lecture_subtopics(story, str(sl)),'en', 'fr')
            elif(language!='en'):
                story_prompt= ai.generate_lecture_subtopics(story+ "In German",str(sl))
            else:
                story_prompt= ai.generate_lecture_subtopics(story, str(sl))

        elif(ai_level==7):
            if language == 'fr':
                story_prompt= ai.translate(ai.generate_lecture_topic(story, str(sl)),'en', 'fr')
            elif(language!='en'):
                story_prompt= ai.generate_lecture_topic(story+ "In German",str(sl))
            else:
                print("[BEFORE]generating story based on the lecture topic")
                story_prompt= ai.generate_lecture_topic(story, str(sl))
                print("[AFTER]generating story based on the lecture topic")

            
            
        #sentences_with_sentiment = classifier.classify(story_prompt, AUTO_SPLIT)
        print("INPUT_1")
        print(inputs[1])

       # userdata.story_prompt = inputs[1] + story_prompt 
        userdata.story_prompt = story_prompt
        userdata.selectedQuestions = selectedQuestions
        userdata.answers = answers
        userdata.suggestions = suggestions
        

        userdata.sl = sl
    
        print(story_prompt)
        print()
            
        next_global_state = 'clientFeedback'
      
        return next_global_state

class ClientFeedback(smach.State):
    def __init__(self,subAlphaSay): 
        smach.State.__init__(self,outcomes= ['keepStory', 'modifyStory','regenerateStory', 'suggestedStory'],
                              input_keys=['sl','story_prompt', 'selectedQuestions', 'answers', 'suggestions'],output_keys=['story_prompt', 'sl', 'selectedQuestions', 'answers', 'suggestions'])  
        self.subAlphaSay= subAlphaSay

    def execute(self,userdata):
        global next_global_state
        global local_data
        global language

        if 'sl' in userdata:
            sl = userdata.sl
        userdata.sl = sl
        selectedQuestions= userdata.selectedQuestions
        answers = userdata.answers
        
        if 'story_prompt' in userdata:  # Check if 'story_prompt' exists in userdata
            story_prompt = userdata.story_prompt
            print("[nur.py]: Received story prompt in ClientFeedback state:", story_prompt)
            asyncio.run(send_data(story_prompt))
        else:
            print("No story prompt received in ClientFeedback state.")
            print("Userdata keys:", userdata.keys()) 
      
        local_data = server.await_response()
        print("LOCAL DATA RECIEVED: ", local_data)
        
        if(local_data == 'keepStory'):
            next_global_state = 'keepStory'
            return next_global_state
        elif(local_data.split(' ',1)[0]=='saveStory'):
            story_prompt= local_data.split(' ', 1)[1]
            userdata.story_prompt=story_prompt
            next_global_state = 'keepStory'
            return next_global_state
        
        elif(local_data.split(' ', 1)[0]== 'suggestions'):
            suggestions = local_data.split(' ',1)[1]
            userdata.suggestions = suggestions
            userdata.story_prompt = story_prompt
            userdata.sl= sl
            next_global_state = 'suggestedStory'
            return next_global_state
            #TODO
            # ai generate based on suggestions call.
            #send it back to client feedback 
            #create a new state based on suggestion state 
            #do everything there and send it again to client feedback    
        elif(local_data.split(' ', 1)[0]=='regenerate'):
            story_prompt= local_data.split(' ', 1)[1]
            userdata.story_prompt=story_prompt
            userdata.sl = sl
            next_global_state='regenerateStory'
            return next_global_state

        else :
            story_prompt=local_data
            userdata.story_prompt = story_prompt
            next_global_state = 'modifyStory'
            return next_global_state
            
class KeepStory(smach.State): #robot tells the story out loud 
    def __init__(self,subAlphaSay): 
        smach.State.__init__(self,outcomes=['repeatStory','nextEvaluation','nextGoodbye', 'queryGeneration'],input_keys=['story_prompt', 'selectedQuestions', 'answers'], output_keys=['story_prompt', 'selectedQuestions', 'answers'])
        self.subAlphaSay= subAlphaSay

    def execute(self,userdata):
        print("story kept. Proceeding")
        story_prompt=userdata.story_prompt 
        selectedQuestions= userdata.selectedQuestions
        answers = userdata.answers

        sentences_with_sentiment = classifier.classify(story_prompt, AUTO_SPLIT)
        print(story_prompt)
       
        print(sentences_with_sentiment)

     #   for sentence in sentences_with_sentiment:
        #    s = sentiment(sentences_with_sentiment[sentence])
        #    if(SPEECH_NEUTRAL):
       #         qt_says(sentence)
            #    rospy.sleep(0.2)
       #     else: 
       #         if s == sentiment.NEUTRAL:
       #             qt_says(sentence) #speak with lip sync
                  #  rospy.sleep(0.2)
       #         else: 
                    #robot.showEmotion(s)
                   # robot.playGesture(s)
                   # qt_says(sentence, speech=robot.say_serv) #speak without lip sync as showing emotion 
                    #rospy.sleep(0.2)
        
        self.subAlphaSay.publish(story_prompt)

        local_data = server.await_response()
        print("LOCAL DATA RECIEVED  FOR KEEP STORY STATE : ", local_data)
        
        if(local_data == '1'):
            print('\n-----------------\n')
            qt_says("press RIGHT ARROW to go to evaluation", to_say=False)
            qt_says("press LEFT ARROW to repeat the story", to_say=False)
            qt_says("press ESC to say goodbye", to_say=False)
            print('-----------------\n') 
            next_global_state = 'nextGoodbye'
            return next_global_state
        elif(local_data == '0'):
            #now change the state to "query generation" state 
            next_global_state= 'queryGeneration'
            return next_global_state    

        next_global_state = ''
        while next_global_state == '':
            pass 
        return next_global_state
    
class QueryGeneration(smach.State):
    def __init__(self,subAlphaSay):
        smach.State.__init__(self,outcomes=['queryGeneration_0', 'queryGeneration_1'],input_keys=['story_prompt','selectedQuestions', 'answers'], output_keys=['story_prompt', 'selectedQuestions', 'answers'])
        self.subAlphaSay= subAlphaSay
    def execute(self,userdata):
        print("Query generation is selected ")
        story_prompt=userdata.story_prompt 
        selectedQuestions = userdata.selectedQuestions
        answers = userdata.answers

        local_data = server.await_response()
        print("LOCAL DATA RECIEVED FOR QUERY GENERATION STATE: ", local_data)

        #queryGeneration_0, queryGeneration_1, queryGeneration_2'

        if(local_data=='option0is chosen'): 
            next_global_state= 'queryGeneration_0'
            return next_global_state
        elif(local_data=='option1is chosen'): 
            next_global_state= 'queryGeneration_1'
            return next_global_state
        next_global_state = ''
        while next_global_state == '':
           pass 
        return next_global_state
    
    
class QueryGeneration_0(smach.State):
    def __init__(self,subAlphaSay):
        smach.State.__init__(self,outcomes=['queryGenerateAnswers'], input_keys = ['selectedQuestions', 'story_prompt', 'answers'],output_keys=['selectedQuestions', 'story_prompt', 'answers'])
        self.subAlphaSay= subAlphaSay
    def execute(self,userdata):
        story_prompt = userdata.story_prompt
        answers = userdata.answers
        print("Query Generation 0 is ACTIVE")
        local_data = server.await_response()
        print("LOCAL DATA RECIEVED FOR QUERY GENERATION 0 STATE: ", local_data)
        questionsExtracted= local_data
        selectedQuestions = userdata.selectedQuestions
        selectedQuestions = local_data 
        answers = ai.gAbQaS(story_prompt,selectedQuestions)
        print(answers)
        print("Before transitioning to the answers")

        next_global_state= 'queryGenerateAnswers'        
        return next_global_state
# QueryGenerateAnswers 
# state to check after human creating handmade questions if it wants to see ai generated answers
# note: not implemented 
class QueryGenerateAnswers(smach.State):
    def __init__(self,subAlphaSay):
        smach.State.__init__(self,outcomes= ['queryInteraction'], input_keys=['selectedQuestions','story_prompt', 'answers'], output_keys=['story_prompt', 'selectedQuestions', 'answers'])
        self.subAlphaSay= subAlphaSay

    def execute(self,userdata):
       # print("Query Generation Answers State Active")
        selectedQuestions= userdata.selectedQuestions
        print(selectedQuestions)
        story_prompt = userdata.story_prompt
    #    local_data = server.await_response()
    #    print(selectedQuestions)
    #    print("WILL PRINT THE LOCAL DATA")
    #    print(local_data)
     #   print("PRINTED THE LOCAL DATA")
     #   if(local_data=="Answers"):         
     #       answers = ai.gAbQaS(story_prompt,selectedQuestions)
     #       print(answers)
    #        asyncio.run(send_data("Answers: " + answers))                            
        next_global_state = 'queryInteraction'
        return next_global_state

class QueryGeneration_1(smach.State):
    def __init__(self,subAlphaSay):
        smach.State.__init__(self,outcomes=['queryGeneration_1_manager'], input_keys=['selectedQuestions','story_prompt'], output_keys=['story_prompt', 'selectedQuestions'])
        self.subAlphaSay= subAlphaSay

    def execute(self,userdata):
        print("Query Generation Option 1 is ACTIVE")
        story_prompt = userdata.story_prompt

        #question + answer + citation
        selectedQuestions= userdata.selectedQuestions
        selectedQuestions= ai.generateQuestions(story_prompt)
               
       # print(questionsExtracted) 
        asyncio.run(send_data("Questions: " + selectedQuestions))     
        
        print("INSIDE: QUERYGENERATION 1 ")
        next_global_state= 'queryGeneration_1_manager'
        
        return next_global_state
    

class QueryGeneration_1_Manager(smach.State):
    def __init__(self,subAlphaSay):
        smach.State.__init__(self,outcomes=['queryInteraction','queryGeneration_1'], input_keys=['selectedQuestions'], output_keys=['selectedQuestions'])
        self.subAlphaSay= subAlphaSay

    def execute(self,userdata):
        print("Query Generation 1 Manager is ACTIVE")
        #question + answer + citation
        selectedQuestions= userdata.selectedQuestions      
    
      
        local_data = server.await_response()

        questions = re.findall(r'[^.?]*\?',selectedQuestions)
        clean_questionsExtracted = '\n'.join(question.strip() for question in questions)
        questionsExtracted =  "Questions: " + clean_questionsExtracted

        if(local_data == 'keepQuestions'):
            selectedQuestions = questionsExtracted
            print(selectedQuestions)
            next_global_state= 'queryInteraction'
        elif(check_first_word(local_data, "Selected")):
            print(extract_questions(selectedQuestions,local_data))
            selectedQuestions= selectedQuestions
            next_global_state= 'queryInteraction'
        elif(check_first_word(local_data, "Modified" )):
            selectedQuestions= local_data
            print(local_data)    
            next_global_state= 'queryInteraction'     
        elif(check_first_word(local_data, "Regenerate")):
            next_global_state= 'queryGeneration_1'     
        next_global_state= 'queryInteraction'        
          
        return next_global_state

#TODO : RE-WRITE THIS FUNCTION
def extract_questions(honey, mint):
    # Find all the question numbers to include, assuming "mint" is in the format "Chose 1.,3."
    import re
    question_nums = re.findall(r'\d+\.', mint)
   
    # Create a dictionary to store start index of each question in 'honey'
    question_starts = {f"{i}.": honey.find(f"{i}.") for i in range(1, 10) if f"{i}." in honey}
   
    # Collect the requested questions
    selected_questions = []
    for q_num in question_nums:
        start_index = question_starts.get(q_num)
        if start_index != -1:
            # Find the end of the question, which is either the start of the next question or the end of the string
            next_question_index = min([question_starts[q] for q in question_starts if question_starts[q] > start_index] + [len(honey)])
            selected_questions.append(honey[start_index:next_question_index].strip())

    return '\n'.join(selected_questions)

class QueryInteraction(smach.State):
    def __init__(self,subAlphaSay):
        smach.State.__init__(self,outcomes=['nextEvaluation', 'nextGoodbye'], input_keys=['selectedQUestions'])
        self.subAlphaSay= subAlphaSay
    def execute(self,userdata):
      
       # local_data = server.await_response()
       #receive the generated question
       #print it on the console for safety
     #   questionsExtracted= userdata.questionsExtracted 
      #  print("Extracted Questions:")
      #  print(questionsExtracted)

        #asyncio.run(send_data(questionsExtracted)) #doesnt work for query human gen
        

        
      #  print("LOCAL DATA RECIEVED FOR QUERY INTERACTION STATE: ", local_data)
        #MODIFY WITH THE ROBOT WHEN ROBOT IS CONNECTED, HERE ROBOT GONNA SAY THE QUESTIONS OUT OUT AND GONNA WAIT FOR THE 
        #ANSWER THEN CONTINUE WITH THE NEXT ETC

        
        next_global_state= 'nextGoodbye'
        return next_global_state
   
class SuggestedStory(smach.State):
    def __init__(self,subAlphaSay):
        smach.State.__init__(self,outcomes=['clientFeedback'],input_keys=['story_prompt', 'sl', 'suggestions'], 
                             output_keys=['story_prompt'])
        self.subAlphaSay= subAlphaSay
    def execute(self,userdata):
        print("I have a story to modify based on the suggestion")
        sl= userdata.sl
        story_prompt = userdata.story_prompt
        suggestions = userdata.suggestions
        story_prompt = ai.mGs(story_prompt, suggestions)

        userdata.story_prompt = story_prompt
        
        next_global_state= 'clientFeedback'
        return next_global_state
    
class RegenerateStory(smach.State):
    def __init__(self,subAlphaSay):
        smach.State.__init__(self,outcomes=['clientFeedback'],input_keys=['story_prompt', 'sl'], 
                             output_keys=['story_prompt'])
        self.subAlphaSay= subAlphaSay   
    def execute(self,userdata):
        print("I have a story to regenerate")
        sl= userdata.sl
        story_prompt = ai.regenerateStory(userdata.story_prompt+ "under" + str(sl)+ "words")
        print(story_prompt)
        userdata.story_prompt = story_prompt
        
        next_global_state= 'clientFeedback'
        return next_global_state

      #  local_data = server.await_response()
     #   print("LOCAL DATA RECIEVED: ", local_data)
        
      #  if(local_data == 'keepStory'):
        #    next_global_state = 'keepStory'
       #     return next_global_state
     #   else:
     #       story_prompt=local_data
     #       userdata.story_prompt = story_prompt
    #        next_global_state = 'modifyStory'
     #       return next_global_state    
        
    
#Keyboard controls for questions asked by QT
def next_q(key):
    global questions
    global done_questions
    if(key == Key.down):
        print(len(questions))
        if(len(questions) > 0):
          #  qt_says(questions.pop(0))
            print("QUESTIONS LEFT: ", questions)
        else: 
            done_questions = True #Down arrow pressed, but all the questions have been said already
            
q_ls = Listener(on_press = next_q)  
#Define state Evaluation
class Evaluation(smach.State):
    def __init__(self,subAlphaSay):
        smach.State.__init__(self, outcomes=['nextStory', 'nextGoodbye'])
        self.subAlphaSay= subAlphaSay
    def execute(self, userdata):
        global next_global_state
        global questions
        global done_questions
        global local_data
        global q_ls
        questions = []
        
        q_ls = Listener(on_press = next_q)
        q_ls.start()
        
        questions = local_data.split("|")[2].splitlines()
        if questions:
            done_questions = False
           # qt_says('Press the down arrow to go to the next question', to_say=False)
            
            message = "Now that we have finished the story, it is time for your evaluation! How well did you understand the story?"
            # translated = "Maintenant que nous avons terminé l'histoire, il est temps pour votre évaluation! Dans quelle mesure avez-vous bien compris l'histoire?"
           # qt_says(ai.translate(message, language_to=language))
            
          #  rospy.sleep(0.2)
            
            print(questions)
            
            while not done_questions: #wait for all questions to be said and discussed
                pass
            q_ls.stop()

            #rospy.sleep(0.2)

            robot.showEmotion(sentiment.JOYFUL)
            message = "Thank you for answering my questions!"
            # translated = "Je vous remercie d'avoir répondu à mes questions!" 
            qt_says(ai.translate(message, language_to=language))
            
            #rospy.sleep(0.2)

        print('\n-----------------\n')
        qt_says('press LEFT ARROW to hear another story', to_say=False)
        qt_says('press ESC to say goodbye', to_say=False)
        print('-----------------\n')
        
        next_global_state = ''
        while next_global_state == '':
            pass 
        return next_global_state

#define state Goodbye
class Goodbye(smach.State):
    def __init__(self,subAlphaSay):
        smach.State.__init__(self, outcomes=['finishState'])
        self.subAlphaSay= subAlphaSay

    def execute(self, userdata):
        robot.showEmotion(sentiment.JOYFUL)
        message = "Thank you for your attention! I hope you learned a lot. See you next time!"
        # translated = "Merci pour votre attention! J'espère que vous avez beaucoup appris. À la prochaine!"
        qt_says(ai.translate(message, language_to=language))
        return 'finishState'
    
def main():

    rospy.init_node('StorytellingMaster', anonymous=True)

    subAlphaSay = rospy.Publisher('/robotCommand', String, queue_size=10)
    #mention it in states as inout and output keys in each state

    #create a smach state machine
    sm = smach.StateMachine(outcomes=['outcome4']) # i assume outcome4 is the final state
    
    #open the container
    with sm:
        #Add states to the container
        smach.StateMachine.add('GREETINGS', Greetings(subAlphaSay), transitions={
            'nextContent':'STORYTELLING'
        })

        smach.StateMachine.add('STORYTELLING', Storytelling(subAlphaSay), transitions={
            'clientFeedback': 'CLIENTFEEDBACK',
            'nextGoodbye': 'GOODBYE'
        })

        smach.StateMachine.add('CLIENTFEEDBACK',ClientFeedback(subAlphaSay), transitions= {
            'keepStory': 'KEEPSTORY',
            'modifyStory': 'KEEPSTORY',
            'regenerateStory': 'REGENERATESTORY',
            'suggestedStory' : 'SUGGESTEDSTORY'
        })

        smach.StateMachine.add('KEEPSTORY', KeepStory(subAlphaSay), transitions={
            'repeatStory':'KEEPSTORY',
            'nextEvaluation': 'EVALUATION',
            'nextGoodbye':'GOODBYE',
            'queryGeneration' : 'QUERYGENERATION'
        })
        smach.StateMachine.add('REGENERATESTORY', RegenerateStory(subAlphaSay),transitions={
            'clientFeedback':'CLIENTFEEDBACK'
    
        })
        smach.StateMachine.add('SUGGESTEDSTORY', SuggestedStory(subAlphaSay),transitions={
            'clientFeedback':'CLIENTFEEDBACK'
        })

        smach.StateMachine.add('QUERYGENERATION', QueryGeneration(subAlphaSay), transitions={
            'queryGeneration_0': 'QUERYGENERATION_0',
            'queryGeneration_1' : 'QUERYGENERATION_1'
        })

        smach.StateMachine.add('QUERYGENERATION_0', QueryGeneration_0(subAlphaSay),transitions={
            'queryGenerateAnswers': 'QUERYGENERATEANSWERS'
        })
        smach.StateMachine.add('QUERYGENERATEANSWERS', QueryGenerateAnswers(subAlphaSay), transitions={
            'queryInteraction': 'QUERYINTERACTION'
        })

        smach.StateMachine.add('QUERYGENERATION_1', QueryGeneration_1(subAlphaSay),transitions={
            'queryGeneration_1_manager': 'QUERYGENERATION1MANAGER'
        })

        smach.StateMachine.add('QUERYGENERATION1MANAGER', QueryGeneration_1_Manager(subAlphaSay), transitions={
            'queryGeneration_1' : 'QUERYGENERATION_1',
            'queryInteraction': 'QUERYINTERACTION'
        })

      
        smach.StateMachine.add('QUERYINTERACTION', QueryInteraction(subAlphaSay), transitions={
            'nextEvaluation': 'EVALUATION',
            'nextGoodbye':'GOODBYE',
        })      

        smach.StateMachine.add('EVALUATION', Evaluation(subAlphaSay), transitions = {
            'nextStory': 'STORYTELLING',
            'nextGoodbye': 'GOODBYE'

        })
        smach.StateMachine.add('GOODBYE', Goodbye(subAlphaSay), transitions={
            'finishState': 'outcome4'
        })

    #Execute smach plan
    print("Starting the server")
    server.start_thread()
    print("Started the server")
    index_html =os.path.abspath('/home/storytelling/catkin_ws/src/storytelling/index.html')
    print("Opening:", index_html)
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
    

