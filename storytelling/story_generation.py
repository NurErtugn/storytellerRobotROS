import os 
from openai import OpenAI

OpenAI.api_key = "YOUR_API_KEY"

os.environ["OPENAI_API_KEY"] = "YOUR_API_KEY"
MODEL = "gpt-3.5-turbo"

client = OpenAI()

#Generates a response given a prompt using OpenAI's GPT-3 API 
def generate_response(prompt, content_message = "You are a helpful and friendly assistant.Babysitter: easy going, understandable language, engaging, filled with curiosity, and with a fantastic plot twist to captivate children", 
                      max_tokens = 1000, n = 1): 
    #MODIFIED : content_message , added the last phrase 
    
    print(prompt)
    print()    
    response = client.chat.completions.create(
        messages =[
            { "role" : "system", "content" : content_message  },
            {"role" : "user", "content" : prompt } ],
        model = MODEL,
        temperature=0.7,
        max_tokens=max_tokens,
        n=n
    )

    return response.choices[0].message.content


def complete_story(story_segment,model=MODEL, temperature=0.7, max_tokens=1000):
    system_prompt = (
        "You are a extremely creative and friendly assistant, responsible with rewriting stories "
        "for a  particular audience: 5-year-old children. Your task is to remodel the story "
        " into an creative new version.This upgraded story should be in the style of  "
        "babysitter: easy going, understable language, engaging, filled with curiosity, and with a fantastic plot twist to "
        "captivate children. Keep the original story, "
        f"and weave the rest of the story from here:\n\n"
        f"'{story_segment}'\n\n"
        f"Continue the story from the end" )        

    response = client.chat.completions.create(
        model=model,
        messages= [ {   "role" : "system",  "content" : system_prompt },
        ],   
        top_p=1.0,    
        frequency_penalty=0.0,
        presence_penalty=0.0,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content

#generate story based on questions ==> used the method few shot prompting
#def gSbA(question_segment,word_count, model= MODEL, temperature = 0.7, max_tokens = 1000):
   # system_prompt = (f"""Given the following questions : 
   #                  ```
    #                 {question_segment}
    #                 ```
    #                 Generate a story under
    #                 {word_count} words that would have answer to the question
    #                 here is an example of what i'm looking for:
   #                  Questions:What's the name of Nur's Robot ? How's the weather today? What was Robot doing when Nur woke up
   #                  Generated Story: Today was a sunny day. Nur opened her eyes to her Robot Alpha-Mini singing a morning song for her.""")

   # response = client.chat.completions.create(
    #    model=model,
   #     messages= [
   #         { "role": "system",
   #          "content" : system_prompt },
  #      ],       
  #      n=3,
  #      temperature=temperature,
  #      max_tokens=max_tokens,
 #   ) 

  #  return response.choices[0].message.content


#modify generated story 

def mGs(story_segment,indications, model= MODEL, temperature = 0.7, max_tokens = 1000):
    system_prompt = (f"""The goal is to rewrite the story given, with a set of instructions.
    Story: 
    {story_segment}
    Instructions:
    {indications}
    Here is an example of the task:
    
    Story:
    Nur decided to get a dog. She settled on a playful Golden Retriever. She calls her Nurki.
    Indication:
    - Change the ending of the story. 
    - Change the name of her dog. 
    - Change the animal that Nur got to a robot. 
    Generated Story: Nur decided to get a robot. She settled on a helpful RoboAssistant. She calls it  RoboNurki.""")

    response = client.chat.completions.create(
        model=model,
        messages= [
            { "role": "system",
             "content" : system_prompt },
        ],       
        n=3,
        temperature=temperature,
        max_tokens=max_tokens,
    ) 

    return response.choices[0].message.content


#def generate answers based on questions and the story
def gAbQaS(story_segment,question_segment, model= MODEL, temperature = 0.7, max_tokens = 1000):
    system_prompt = (f"""Given the following questions : 
                     ```
                     {question_segment}
                     ```
                     Generate answers that would have answer in the following story {story_segment} 
                     Give explanation to your answers
                     here is an example of what i'm looking for:
                     Story: Today was a sunny day. Nur opened her eyes to her Robot Mini Nur singing a morning song for her.
                     Questions:
                     -What's the name of Nur's Robot ? 
                     -How's the weather today? 
                     -What was Robot doing when Nur woke up
                     -Where did Nur and Tom meet?
                     Generated Answers:
                      - Answer 1: Nur's Robot's name is Mini Nur 
                      - Answer 2: It's sunny day today
                      - Answer 3: When Nur woke up, Robot was singing songs for Nur
                      - Answer 4: Nur didnt meet Tom in the story  """)

    response = client.chat.completions.create(
        model=model,
        messages= [
            { "role": "system",
             "content" : system_prompt },
        ],       
        n=3,
        temperature=temperature,
        max_tokens=max_tokens,
    ) 
    return response.choices[0].message.content


#different story generation for different age groups 

# source for the system prompt : https://www.usillustrations.com/blog/understanding-different-childrens-books-age-groups

def dSgDaG(topic, age_group, word_count= 200 , model= MODEL, temperature = 0.8, max_tokens = 1000):

    system_prompt = (f"""Given the following topic : 
                     ```
                     {topic}
                     ```
                     Generate a story 
                     For the given age group:
                     ```
                     {age_group}
                     ```
                    under  {word_count} words

                    here is an example of what i'm looking for:
                 
                    If the age group is "Toddlers",then here are story features:
                    - Basic concepts (colors, shapes, animals, everyday objects)
                    - Simple, repetitive text
                  
                    If the age group is "Preschoolers",then  here are story features:
                    - Simple, relatable narratives
                    - Stories that enhance vocabulary
                    - Themes that encourage critical thinking and empathy
                   
                    If the age group is "Early Elementary",then here are story features:
                    - Simple, relatable narratives
                    - Familiar settings and relatable characters
                    - Introduction to problem-solving and critical thinking
                    - Promotes empathy and understanding of diverse perspectives
                  
                    If the age group is "Late Elementary",then here are story features:
                    -Middle-grade books
                    - More complex narratives
                    - Themes of friendship, adventure, and personal growth
                    - Exploration of emotions and relationships

                    If the age group is "Preteens",then here are story features:
                    - Detailed narratives with developed plots
                    - Focus on character development and emotional depth
                    - Themes of identity, self-discovery, and social issues
                    - More mature content, appropriate for their age
                
                                    """)

    response = client.chat.completions.create(
        model=model,
        messages= [
            { "role": "system",
             "content" : system_prompt },
        ],       
        n=3,
        temperature=temperature,
        max_tokens=max_tokens,
    ) 
    return response.choices[0].message.content

def complete_story_german(story_segment,model=MODEL, temperature=0.7, max_tokens=1000):
    system_prompt = ("Hier ist der Beginn einer kreativen, freundlichen, fantastischen Geschichte für Kinder. "
            "Behalten Sie den Anfang, fahren Sie bitte auf Französisch fort:"
            f"'{story_segment}'\n\n")

    response = client.chat.completions.create(
        model=model,
        messages= [
            {   "role" : "system",  "content" : system_prompt },
        ],   
        top_p=1.0,    
        frequency_penalty=0.0,
        presence_penalty=0.0,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return story_segment + response.choices[0].message.content

def chooseTarget(ageGroup):

    if ageGroup=="Toddlers":
        prompt ="""- Basic concepts (colors, shapes, animals, everyday objects)
                - Simple, repetitive text"""
        
    elif ageGroup== "Preschoolers":
        prompt="""  - Simple, relatable narratives
                    - Stories that enhance vocabulary
                    - Themes that encourage critical thinking and empathy"""
        
    elif ageGroup== "Early Elementary":
        prompt = """ - Simple, relatable narratives
                    - Familiar settings and relatable characters
                    - Introduction to problem-solving and critical thinking
                    - Promotes empathy and understanding of diverse perspectives"""


    elif ageGroup== "Late Elementary":
        prompt= """-Middle-grade books
                    - More complex narratives
                    - Themes of friendship, adventure, and personal growth
                    - Exploration of emotions and relationships """

    elif ageGroup== "Preteens":
        prompt= """- Detailed narratives with developed plots
                    - Focus on character development and emotional depth
                    - Themes of identity, self-discovery, and social issues
                    - More mature content, appropriate for their age"""

    else:
        raise ValueError("choose target error")

    return prompt



#generate story based on questions ==> used the method few shot prompting

def gSbA(question_segment, age_group, word_count=300, model= MODEL, temperature = 0.7, max_tokens = 1000):
    system_prompt = (f"""Given the following questions : 
                     ```
                     {question_segment}
                     ```
                     Generate a story that would have answer to the questions
                     here is an example of what i'm looking for:
                     Questions:What's the name of Nur's Robot ? How's the weather today? What was Robot doing when Nur woke up
                     Generated Story: Today was a sunny day. Nur opened her eyes to her Robot Alpha-Mini singing a morning song for her.                    
                     For the given age group:
                     ```
                     {age_group}
                     ```
                     under  {word_count} words
                    here is an example of what i'm looking for:
                    {chooseTarget(age_group)}                          
                                    """)

    response = client.chat.completions.create(
        model=model,
        messages= [
            { "role": "system",
             "content" : system_prompt },
        ],       
        n=3,
        temperature=temperature,
        max_tokens=max_tokens,
    ) 

    return response.choices[0].message.content

def regenerateStory(storyPrompt,model=MODEL, temperature=0.8,max_tokens= 1000):
    system_prompt = "You are extremely warm and imaginative assistant, responsible with rewriting tales"
    "for a special audience: 5-year-old children. Your task is to remodel the story "
    "into an creative new version. This upgraded story should be in the style of"
    "babysitter: easygoing, understanble language, engaging, filled with curiosity, and with a fantastic plot twist to"
    "captivate children. Change the ending of the tale to bring curiousity .Based on this, rewrite the following story into"
    "a magical fantastic and andventuorously appropriate for a 5-year-old children:\n\n"
    "Original Story Segment:"

    response= client.chat.completions.create(
        model=model,
        messages=[
            { "role" : "system",
             "content" : system_prompt},
            { "role" : "user",
             "content": storyPrompt
            }
        ],
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content

#giving more specific task to make it understand better. If i dont say "give answer and cite" it does generate questions that doesnt have answers in the text
def generateQuestions(storyPrompt, model=MODEL, temperature =0.8, max_tokens=1000):
    system_prompt = (f"You are extremely warm and and creative babysitter, ask 3 questions that have short answers about the following story:"
    f"'{storyPrompt}'\n\n"
    "Give answer to generated questions and cite from the text")   

    response= client.chat.completions.create(
        model=model,
        messages=[
            { "role" : "system",
             "content" : system_prompt},
        ],
        n=3, #nb of questions
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content

#goal: to extract questions generated by "generateQuestions"
def extractQuestion(questionPrompt, model=MODEL, temperature =0.8, max_tokens=1000):
    system_prompt=(f"extract the phrases that end with a question mark in this: "
                   f"'{questionPrompt}'\n\n")
    
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",             
             "content": system_prompt}
        ],
        n=3, 
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message.content
#goal: when openai generated a story with limited amount of words, it  doesnt necessarily end the phrase
#this function aims to end the story
def story_end(story_prompt):
    end_dot= story_prompt.rfind('.') # finds the last referenced index of the given occurence
    end_exc= story_prompt.rfind('!')
    end_ques = story_prompt.rfind('?')

    end_last=end_dot
    if(end_last<end_exc): end_last= end_exc
    if(end_last<end_ques): end_last= end_ques

    return story_prompt[:end_last+1]


#strings for the answer_question function
sys_mes = """You are a humanoid robot named QT whose job is to help a 5 year old student with any question they have. 
You can show facial expressions and move your arms, but you cannot walk. Your goal is to simulate human to human conversation."""
sys_french = """Vous êtes un robot humanoïde nommé QT dont le travail consiste à aider un élève de 5 ans à répondre à toutes ses questions.
Vous pouvez montrer des expressions faciales et bouger vos bras, mais vous ne pouvez pas marcher. Votre objectif est de simuler une conversation d'homme à homme."""

#Obtains an answer to the given question 
def answer_question(prompt, system_message = sys_french, max_tokens = 200, n = 1):
    return generate_response(prompt, system_message, max_tokens, n)

#Translates the given message. Used for pre-programmed messages that QT will say
def translate(message, language_from = 'en', language_to = 'en'):
    language = None
    if not(language_from == language_to):
        if(language_to == 'fr'):
            language = 'French'
        else:
            language = 'German'
        message = generate_response("Translate the following text to " + language + ": " + message)
    print(message)
    return message

#debugging purposes
def generate_fake_response(prompt):
    return prompt

#debugging purposes
if __name__ == '__main__':
    print(answer_question("Can you dance?")) 


