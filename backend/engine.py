import json
import csv
import random
import spacy
from experta import *
from datetime import datetime
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta

nlp = spacy.load('en_core_web_md')

intentions_path = "data/intentions.json"
sentences_path = "data/sentences.txt"
station_names_path = "data/stations.csv"
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


station_codes = {}

with open(station_names_path) as file:
    reader = csv.DictReader(file)

    for row in reader:
        key = row['name']
        value = row['tiploc']

        station_codes[key] = value

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

final_chatbot = False
# departure = None
# destination = None
# date = None
# time = None
# return_ticket = False


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


def convert_station_name(city):

    city = city.upper()
    station_code = station_codes.get(city)
    multiple_found = False

    # if there is no station code, set to list of stations
    if station_code is None:

        stations_with_city = [station for station in station_codes.keys() if city in station]

        if stations_with_city:

            multiple_found = True
            station_code = stations_with_city

        else:

            station_code = None


    return station_code, multiple_found


def convert_date(input):

    days_of_the_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    if input.lower() == "tomorrow":

        return (datetime.now() + relativedelta(days=1)).strftime("%d/%m/%Y")
    elif input.lower() == "today":
        return datetime.now()


    elif input.lower() in days_of_the_week:

        # Calculate date for the next occurrence of the specified day of the week
        today = datetime.now()
        days_until_target_day = ((days_of_the_week.index(input.lower()) - today.weekday()) + 7) % 7
        return (today + relativedelta(days=days_until_target_day)).strftime("%d/%m/%Y")


    return parse_date(input).strftime("%d/%m/%Y")


def convert_time(input):

    time_obj = parse_date(input).time()
    return time_obj.strftime("%H:%M:%S")


def extract_entities(user_input):

    return_ticket = time = date = departure = destination = None

    # Extract entities
    entities = [(ent.text, ent.label_) for ent in user_input.ents]

    # Extract dependency relations
    dep_relations = [(token.text, token.dep_, token.head.text) for token in user_input]

    for ent in entities:

        for token, dep, head in dep_relations:

            if ent[0] == token:

                if dep == "pobj" and head in ["from", "leave"]:

                    departure = ent[0]


                elif dep == "pobj" and head in ["to", "arrive", "at"]:

                    destination = ent[0]


    if any(token.text.lower() == "return" for token in user_input):

        return_ticket = True

    time_tokens = []
    # Extract time and date
    for token in user_input:

        if token.ent_type_ == "TIME":

            time_tokens.append(token.text)


        elif token.ent_type_ == "DATE" and date is None:

            date = convert_date(token.text)

    time_str = ''.join(time_tokens)
    if time_str != '':
        time = convert_time(''.join(time_tokens))


    return return_ticket, time, date, departure, destination


def clarify_station(is_departure):

    station_code = None
    multiple_found = True

    # get words to say in print so arrival and departure can be unified
    word = "departure" if is_departure else "arrival"
    ing = "departing" if is_departure else "arriving"

    while station_code is None or multiple_found:

        city = input(f"Sorry, we didn't get the station of {word}. Which station will you be {ing} from?\n\t")

        station_code, multiple_found = convert_station_name(city)

        # if the user has not used a one word answer
        if station_code is None:

            for ent in nlp(city).ents:

                station_code, multiple_found = convert_station_name(ent.text)

                if station_code is not None:

                    break


        if multiple_found:

            print(f"Which station in {city}?...\n")

            for code in station_code:

                print(f"- {code}?")


    return station_code


class Book(Fact):

    """
    return_ticket = Return Ticket
    dep_station = Departure Station
    arr_station = Arrival Station
    dep_date = Departure Date
    dep_time = Departure Time
    """

    pass


class TrainBot(KnowledgeEngine):

    @DefFacts()
    def _initial_action(self):

        return_ticket, time, date, departure, destination = extract_entities(nlp(input("Hello!\n\t")))

        if return_ticket is not None:

            yield Book(return_ticket=return_ticket)

        if time is not None:

            yield Book(dep_time=time)

        if date is not None:

            yield Book(dep_date=date)

        if departure is not None:

            yield Book(dep_station=departure)

        if destination is not None:

            yield Book(arr_station=destination)


    @Rule(NOT(Book(dep_station=W())))
    def _get_dep_station(self):

        station_code = clarify_station(True)

        self.declare(Book(dep_station=station_code))


    @Rule(NOT(Book(arr_station=W())))
    def get_arr_station(self):

        station_code = clarify_station(False)

        self.declare(Book(arr_station=station_code))


    @Rule(NOT(Book(dep_time=W())))
    def get_dep_time(self):
        time_tokens = []
        for token in nlp(input("Sorry, we didn't get the time. What time will you be departing?\n\t")):

            if token.ent_type_ == "TIME":
                time_tokens.append(token.text)
        time_str = ''.join(time_tokens)
        if time_str != '':
            self.declare(Book(dep_time=str(convert_time(time_str))))


    @Rule(NOT(Book(dep_date=W())))
    def get_dep_date(self):

        for token in nlp(input("Sorry, we didn't get the date. What day will you be departing?\n\t")):

            if token.ent_type_ == "DATE":

                self.declare(Book(dep_date=str(convert_date(token.text))))
                break


    @Rule(NOT(Book(return_ticket=W())))
    def get_return(self):

        answer = input("Will you be returning? (yes or no)\n\t").lower()

        return_ticket = "yes" in answer or "will be" in answer

        self.declare(Book(return_ticket=return_ticket))


    # if every information has been filled out
    @Rule(
        Book(return_ticket=MATCH.return_ticket),
        Book(dep_time=MATCH.dep_time),
        Book(dep_date=MATCH.dep_date),
        Book(dep_station=MATCH.dep_station),
        Book(arr_station=MATCH.arr_station),)
    def success(self, dep_station, arr_station, dep_date, dep_time, return_ticket):

        return_string = "will" if return_ticket else "won't"

        print(f"So you will be departing from {dep_station} and arriving at {arr_station} on {dep_date} at "
              f"{dep_time}? And it {return_string} be a return. "
              f"Okay lol don't need to get so worked up about it...")

        pass


# test harness to prove it works
def TestHarness():

    bot = TrainBot()
    bot.reset()
    bot.run()


# if running this file, run the test harness
if __name__ == '__main__':

    TestHarness()
