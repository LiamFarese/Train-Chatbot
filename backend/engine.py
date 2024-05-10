import json
from parser import ParserError
from queue import Full
import random
import spacy
from experta import *
from datetime import datetime
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta



nlp = spacy.load('en_core_web_md')

intentions_path = "intentions.json"
sentences_path = "sentences.txt"

time_sentences = ''
date_sentences = ''

with open(intentions_path) as f:
    intentions = json.load(f)

with open(sentences_path) as file:
    for line in file:
        parts = line.split(' | ')
        if parts[0] == 'time':
            time_sentences = time_sentences + ' ' + parts[1].strip()
        elif parts[0] == 'date':
            date_sentences = date_sentences + ' ' + parts[1].strip()

labels = []
sentences = []

doc = nlp(time_sentences)
for sentence in doc.sents:
    labels.append("time")
    sentences.append(sentence.text.lower().strip())

doc = nlp(date_sentences)
for sentence in doc.sents:
    labels.append("date")
    sentences.append(sentence.text.lower().strip())

# def lemmatize_and_clean(text):
#     doc = nlp(text.lower())
#     out = ""
#     for token in doc:
#         if not token.is_stop and not token.is_punct:  # Blank 1
#             out = out + token.lemma_ + " "  # Blank 2
#     return out.strip()

# final_chatbot = False

# def date_time_response(user_input):
#     cleaned_user_input = lemmatize_and_clean(user_input)
#     doc_1 = nlp(cleaned_user_input)
#     similarities = {}
#     for idx, sentence in enumerate(sentences):
#         cleaned_sentence = lemmatize_and_clean(sentence)
#         doc_2 = nlp(cleaned_sentence)
#         similarity = doc_1.similarity(doc_2)
#         similarities[idx] = similarity

#     max_similarity_idx = max(similarities, key=similarities.get)
    
#     # Minimum acceptable similarity between user's input and our Chatbot data
#     # This number can be changed
#     min_similarity = 0.75

#     # Do not change these lines
#     if similarities[max_similarity_idx] > min_similarity:
#         if labels[max_similarity_idx] == 'time':
#             print("BOT: " + "It’s " + str(datetime.now().strftime('%H:%M:%S')))
#             if final_chatbot:
#                 print("BOT: You can also ask me what the date is today. (Hint: What is the date today?)")
#         elif labels[max_similarity_idx] == 'date':
#             print("BOT: " + "It’s " + str(datetime.now().strftime('%Y-%m-%d')))
#             if final_chatbot:
#                 print("BOT: Now can you tell me where you want to go? (Hints: you can type in a city's name, or an organisation. I am going to London or I want to visit the University of East Anglia.)")
#         return True
    
#     return False

# sample_user_input = "Tell me the time!"
# print(sample_user_input)
# date_time_response(sample_user_input)

# class Book(Fact):
#     """Info about the booking ticket."""
#     pass

# class TrainBot(KnowledgeEngine):
#   @Rule(Book(ticket='one way'))
#   def one_way(self):
#     print("BOT: You have selected a one way ticket. Have a good trip.")
#     if final_chatbot:
#       print("BOT: If you don't have any other questions you can type bye.")

#   @Rule(Book(ticket='round'))
#   def round_way(self):
#     print("BOT: You have selected a round ticket. Have a good trip.")
#     if final_chatbot:
#       print("BOT: If you don't have any other questions you can type bye.")

#   @Rule(AS.ticket << Book(ticket=L('open ticket') | L('open return')))
#   def open_ticket(self, ticket):
#     print("BOT: You have selected a " + ticket["ticket"] +".  Have a good trip.")
#     if final_chatbot:
#       print("BOT: If you don't have any other questions you can type bye.")


final_chatbot = False
departure = None
destination = None
date = None
time = None
return_ticket = False


def check_intention_by_keyword(sentence):
    for word in sentence.split():
        for type_of_intention in intentions:
            if word.lower() in intentions[type_of_intention]["patterns"]:
                print("BOT: " + random.choice(intentions[type_of_intention]["responses"]))
                
                # Do not change these lines
                if type_of_intention == 'greeting' and final_chatbot:
                    print("BOT: We can talk about the time, date, and train tickets.\n(Hint: What time is it?)")
                return type_of_intention
    return None

def convert_date(input):
    global date
    if input.lower() == "tomorrow":
        date = (datetime.now() + relativedelta(days=1)).strftime("%d/%m/%Y")
    elif input.lower() in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
        # Calculate date for the next occurrence of the specified day of the week
        today = datetime.now()
        days_until_target_day = ((["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(input.lower()) - today.weekday()) + 7) % 7
        date = (today + relativedelta(days=days_until_target_day)).strftime("%d/%m/%Y")
    else:
        date = parse_date(input).strftime("%d/%m/%Y")

def convert_time(input):
    global time
    time_obj = parse_date(input).time()
    time = time_obj.strftime("%H:%M:%S")

def extract_entities(user_input):
    global return_ticket, time, date, departure, destination

    # Extract entities
    entities = [(ent.text, ent.label_) for ent in user_input.ents]

    # Extract dependency relations
    dep_relations = [(token.text, token.dep_, token.head.text) for token in user_input]

    # Heuristic to determine departure and destination
    for ent in entities:
        for token, dep, head in dep_relations:
            if ent[0] == token:
                if dep == "pobj" and head in ["from", "leave"]:
                    departure = ent[0]
                elif dep == "pobj" and head in ["to", "arrive", "at"]:
                    destination = ent[0]

    if any(token.text.lower() == "return" for token in user_input):
        return_ticket = True

    last_token = None
    # Extract time and date
    for token in user_input:
        if token.ent_type_ == "TIME":
            time_str = last_token.text + token.text
            convert_time(time_str)
        elif token.ent_type_ == "DATE" and date is None:
            convert_date(token.text)
        last_token = token

flag = True
doc = None
while flag:
    print("Hi there! How can I help you?.\n (If you want to exit, just type bye!)")
    raw_input = input()
    doc = nlp(raw_input)
    intention = check_intention_by_keyword(raw_input)
    if intention == 'goodbye':
        flag = False
    elif intention is None:
        extract_entities(doc)
        print(departure, destination)
        # Check if any field is missing
        if departure is None or destination is None or time is None or date is None:
            # Prompt user for missing information
            print("I need some more information to proceed:")
            while(departure is None or destination is None or time is None or date is None):
                if departure is None:
                    departure = input("Please provide the departure point: ")
                if destination is None:
                    destination = input("Please provide the destination: ")
                if time is None:
                    convert_time(input("Please provide the time: "))
                if date is None:
                    convert_date(input("Please provide the date: "))
                # Now you have all required information, you can proceed with further actions
                print("Thank you for providing the information. Now, I can proceed.")
                # Your further actions based on extracted and prompted information can go here
        else:
            # All fields are present, you can proceed with further actions
            print("All necessary information is available. Proceeding with further actions...")
    print(departure, destination, time, date)
    departure = None
    destination = None
    time = None
    date = None
