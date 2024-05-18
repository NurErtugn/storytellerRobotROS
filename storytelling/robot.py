from autobahn.twisted.component import Component, run
from twisted.internet.defer import inlineCallbacks
from autobahn.twisted.util import sleep
import os
import rospkg
import sys
import rospy
import smach
import pandas as pd
from std_msgs.msg import String

class Robot:
    
    #@inlineCallbacks
    def __init__(self, session):
        
        self.connected = True
        self.session = session
        self.alive = True

         # initialize ROS node
        rospy.init_node('AlphaMini_Node', anonymous=True)
        # self.pubMsg = rospy.Publisher('/irecheck/button_name', String, queue_size=10)
        
        rospy.Subscriber('robotCommand', String, self.robotCommand)
        # initialize publishers/subscribers
        # rospy.Subscriber([topic_name],[topic_type],[callback_function_name])
        # rospy.Subscriber('dynamicomsg', String, self.dynamicoCallback)
        # rospy.Publisher([topic_name],[topic_type],[max_queue_size])

    # test for making the robot speak
    def talk(self, text, block = False, lang='en'):
        
        # check whether it is this call that makes it blocking
        if block:
            yield self.session.call("rie.dialogue.say", text=text)
        else:
            self.session.call("rie.dialogue.say_animated", text=text)



    def on_keyWords(self, frame):
        if ("certainty" in frame["data"]["body"] and
            frame["data"]["body"]["certainty"] > 0.45):
            
            # self.session.call("rie.dialogue.say", text= "Yes")
            self.talk(text= "Yes")

    ''' 
            @inlineCallbacks
    def main(session, details):
    global sess
    sess = session
    def on_keyword(frame):
    global sess
    if ("certainty" in frame["data"]["body"] and
    frame["data"]["body"]["certainty"] > 0.45):
    sess.call("rie.dialogue.say", text= "Yes")
    yield session.call("rie.dialogue.say",
    text="Say red, blue or green")
    yield session.call("rie.dialogue.keyword.add",
    keywords=["red", "blue", "green"])
    yield session.subscribe(on_keyword,
    "rie.dialogue.keyword.stream")
    yield session.call("rie.dialogue.keyword.stream")
    # Wait 20 seconds before we close the keyword stream
    yield sleep(20)
    yield session.call("rie.dialogue.keyword.close")
    yield session.call("rie.dialogue.keyword.clear")
    session.leave() # Close the connection with the robot
    '''        



    # Print the data received
    def robotCommand(self,data):
        
        # checking the received data
        print ("HERE IS THE DATA -->", data.data)
        
        # finishes the thread if receives an "end" as message
        if(data.data == 'end'):
            self.alive=False
        else:
            # talks the message its received
            # self.session.call("rie.dialogue.say", text=data.data)
            
            # self.session.call("rie.dialogue.say_animatedHave", text=str(data.data), lang='de')
            self.session.call("rie.dialogue.say_animated", text=str(data.data))
            # self.session.call("rie.dialogue.say", text=str(data.data))


            

    #@inlineCallbacks
    def off(self):
        self.session.leave()




@inlineCallbacks
def main(session, details):
    
    try: 
        myrobot = Robot(session)
    except Exception as e:
        print(e)
    
    # myrobot.talk("Hello, I am testing the class comunication here.", block=False)

    myrobot.talk(text="Say red, blue or green")
    yield session.call("rie.dialogue.keyword.add",
    keywords=["red", "blue", "green"])

    while(myrobot.alive):
        # the goal of this loop is to keep the node alive and receiving messages in the topic "robotCommand" still it is killed
        # pass
        yield sleep(0.01) 


    myrobot.off()



    
    return

    # The code below does not necessarily work (of course when I remove the "return" in the line above). Any ideas why?
    txt = ""
    while (txt != "bye"):
    
        yield session.call("rie.dialogue.say",
        text="What to say?")
    
        txt = input("Type here: ")
    
        yield session.call("rie.dialogue.say",
        text=txt)
    


    
    
    
    
    
    session.leave() # Sluit de verbinding met de robot

# Create wamp connection
wamp = Component(
transports=[{
    "url": "ws://wamp.robotsindeklas.nl",
    "serializers": ["msgpack"]
    }],
    realm="rie.66461083f26645d6dd2bccda",
)
    
wamp.on_join(main)






if __name__ == "__main__":
    run([wamp])
    # print("CTL+C to exit!")
    # rospy.spin()