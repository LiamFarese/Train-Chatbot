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


    elif input.lower() in days_of_the_week:

        # Calculate date for the next occurrence of the specified day of the week
        today = datetime.now()
        days_until_target_day = ((days_of_the_week.index(input.lower()) - today.weekday()) + 7) % 7
        return (today + relativedelta(days=days_until_target_day)).strftime("%d/%m/%Y")


    return parse_date(input).strftime("%d/%m/%Y")


def convert_time(input):

    print(input)

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


    last_token = None

    # Extract time and date
    for token in user_input:

        if token.ent_type_ == "TIME":

            time_str = last_token.text + token.text
            convert_time(time_str)


        elif token.ent_type_ == "DATE" and date is None:

            convert_date(token.text)


        last_token = token


    return return_ticket, time, date, departure, destination


def clarify_station(is_departure, other_station=None):

    station_code = None
    multiple_found = True

    # get words to say in print so arrival and departure can be unified
    ing = "departing" if is_departure else "arriving"

    while station_code is None or multiple_found or station_code == other_station:

        city = input(f"Which station will you be {ing} from?\n\t")

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


        if station_code == other_station:

            print("Sorry, but you cannot arrive and depart from the same station. ")


    return station_code


class Book(Fact):

    """
    dep_station = Departure Station
    arr_station = Arrival Station
    dep_date = Departure Date
    dep_time = Departure Time

    return_ticket = Return Ticket
    return_date = Return Date
    return_time = Return Time
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


    # get Departure Station #


    @Rule(AND(NOT(Book(dep_station=W())),
          NOT(Book(arr_station=W()))))
    def _get_dep_station(self):

        station_code = clarify_station(True)

        self.declare(Book(dep_station=station_code))


    @Rule(NOT(Book(dep_station=W())),
          Book(arr_station=MATCH.arr_station))
    def _get_dep_station_check_arr_station(self, arr_station):

        station_code = clarify_station(True, arr_station)

        self.declare(Book(dep_station=station_code))


    # get Arrival Station #


    @Rule(AND(NOT(Book(dep_station=W())),
          NOT(Book(arr_station=W()))))
    def get_arr_station(self):

        station_code = clarify_station(False)

        self.declare(Book(arr_station=station_code))


    @Rule(NOT(Book(arr_station=W())),
          Book(dep_station=MATCH.dep_station))
    def get_arr_station_check_dep_station(self, dep_station):

        station_code = clarify_station(False, dep_station)

        self.declare(Book(arr_station=station_code))


    @Rule(NOT(Book(dep_time=W())))
    def get_dep_time(self):

        dep_time = None

        while dep_time is None:

            for token in nlp(input("What time will you be departing?\n\t")):

                if token.ent_type_ == "TIME":

                    dep_time = str(convert_time(token.text))
                    break


            if dep_time is None:

                print("Sorry, that time is invalid. ")


        self.declare(Book(dep_time=dep_time))


    @Rule(NOT(Book(dep_date=W())))
    def get_dep_date(self):

        dep_date = None

        while dep_date is None:

            for token in nlp(input("What date will you be departing?\n\t")):

                if token.ent_type_ == "DATE":

                    dep_date = str(convert_date(token.text))
                    break


            if dep_date is None:

                print("Sorry, that date is invalid. ")


        self.declare(Book(dep_date=dep_date))


    @Rule(NOT(Book(return_ticket=W())))
    def get_return(self):

        answer = input("Will you be returning? (yes or no)\n\t").lower()

        return_ticket = "yes" in answer or "will be" in answer

        self.declare(Book(return_ticket=return_ticket))


    @Rule(
        Book(return_ticket=True),
        Book(dep_date=MATCH.dep_date),
        NOT(Book(return_date=W())))
    def get_return_date(self, dep_date):

        return_date = None
        departure_date = convert_date(dep_date)

        while return_date is None:

            for token in nlp(input("What date will you be returning?\n\t")):

                if token.ent_type_ == "DATE":

                    return_date = str(convert_date(token.text))
                    break


            if return_date is not None:

                if return_date < departure_date:

                    print("Sorry, the return date cannot be before the departure date. ")
                    return_date = None
            else:

                print("Sorry, that date is invalid. ")


        self.declare(Book(return_date=return_date))


    # cannot occur without the date being set
    @Rule(
        Book(return_ticket=True),
        Book(return_date=MATCH.return_date),
        Book(dep_date=MATCH.dep_date),
        Book(dep_time=MATCH.dep_time),
        NOT(Book(return_time=W())))
    def get_return_time(self, return_date, dep_date, dep_time):

        return_time = None
        check_time = return_date == dep_date
        departure_time = convert_time(dep_time)

        while return_time is None:

            for token in nlp(input("What time will you depart for your return?\n\t")):

                if token.ent_type_ == "TIME":

                    return_time = str(convert_time(token.text))
                    break


            if return_time is not None:

                if check_time and return_time <= departure_time:

                    print("Sorry, the return time cannot be before the departure time if they are on the same day. ")
                    return_time = None
            else:

                print("Sorry, that time is invalid. ")


        self.declare(Book(return_time=return_time))


    # if every information has been filled out
    @Rule(
        Book(return_time=MATCH.return_time),
        Book(return_date=MATCH.return_date),
        Book(dep_time=MATCH.dep_time),
        Book(dep_date=MATCH.dep_date),
        Book(dep_station=MATCH.dep_station),
        Book(arr_station=MATCH.arr_station),)
    def success_with_return(self, dep_station, arr_station, dep_date, dep_time, return_time, return_date):

        print(f"So you will be departing from {dep_station} and arriving at {arr_station} on {dep_date} at "
              f"{dep_time}? And it will be a return on {return_date} at {return_time}. "
              f"Okay lol don't need to get so worked up about it...")

        pass


    # if every information has been filled out
    @Rule(
        Book(return_ticket=False),
        Book(dep_time=MATCH.dep_time),
        Book(dep_date=MATCH.dep_date),
        Book(dep_station=MATCH.dep_station),
        Book(arr_station=MATCH.arr_station),)
    def success_wout_return(self, dep_station, arr_station, dep_date, dep_time):

        print(f"So you will be departing from {dep_station} and arriving at {arr_station} on {dep_date} at "
              f"{dep_time}? And it won't be a return. "
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
