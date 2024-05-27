
import json
import csv
import random
import spacy
import pickle
import datetime as dt

from experta import *
from datetime import datetime

from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta

from scraper import scrape


nlp = spacy.load('en_core_web_md')

station_names_path = "data/stations.csv"

station_codes = {}

with open(station_names_path) as file:
    reader = csv.DictReader(file)

    for row in reader:
        key = row['name']
        value = row['tiploc']

        station_codes[key] = value

final_chatbot = False

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

    if any((token.text.lower() == ("return" or "yes"))for token in user_input):
        return_ticket = True

    if any((token.text.lower() == "no" )for token in user_input):
        return_ticket = False

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


def scrape_to_string(dep_station, arr_station, dep_date, dep_time,
                     return_ticket=False, return_time=None, return_date=None):

    with open('model.pickle', 'rb') as file:
        model = pickle.load(file)


    with open('historical-data/station_dict.pkl', 'rb') as file:
        station_dict = pickle.load(file)


    dep_station = convert_station_name(dep_station)[0]
    arr_station = convert_station_name(arr_station)[0]

    details, url = scrape(
        dep_station,
        arr_station,
        dep_date, dep_time, False, "", "")


    dep_dt = dt.datetime.strptime(details[0], '%Y-%m-%d %H:%M:%S')

    day_of_week = dep_dt.weekday()
    day_of_year = day_of_week == 5 or 6
    weekday     = day_of_year = dep_dt.timetuple().tm_yday
    on_peak     = dep_dt.hour >= 9
    hour        = on_peak = dep_dt.hour >= 9
    first_stop  = 0
    second_stop = 0

    print(dep_station)
    print(arr_station)

    print(station_dict)

    if dep_station in station_dict:

        first_stop = station_dict[dep_station]


    if arr_station in station_dict:

        second_stop = station_dict[arr_station]


    print(f"{first_stop}, {second_stop}")


    predicted_delay = model.predict([[

        day_of_week,
        day_of_year,
        weekday,
        on_peak,
        hour,
        first_stop,
        second_stop]])

    if return_ticket:

        return_time = return_date = ""


    return (
        f"Here is some information about your journey:\n"
        f"departure time: {details[0]}, arrival time: {details[1]}, duration: {details[2]}, "
        f"delay: {int(predicted_delay[0])}s\n\n"
        f"Here is a link to book your tickets:\n"
        f"{url}")


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


class TrainBot():

    def __init__(self):

        super().__init__()
        self.response = None
        self.fact_string = None


    def run_with_response(self):

        self.response = None
        self.run()
        return self.response, self.fact_string

    # if the user types "undo", delete the last fact
    #def check_undo(self, user_input):
#
    #    user_input = user_input.lower()
#
    #    if "undo" in user_input:
#
    #        remove_key = list(self.facts.keys())[-1]
    #        remove_fact = self.facts[remove_key]
    #        self.retract(remove_fact)
    #        print(self.facts)
    #        return True
#
    #    # unsuccessful
    #    return False


    # station clarification used in multiple functions
    def clarify_station(self, is_departure, other_station=None):

        station_code = None
        multiple_found = True

        # get words to say in print so arrival and departure can be unified
        ing = "departing" if is_departure else "arriving"

        while station_code is None or multiple_found or station_code == other_station:

            city = input(f"Which station will you be {ing} from?\n\t")

            if self.check_undo(city):
                return None

            station_code, multiple_found = convert_station_name(city)

            # if the user has not used a one word answer
            if station_code is None:

                for ent in nlp(city).ents:

                    station_code, multiple_found = convert_station_name(ent.text)

                    if station_code is not None:

                        return ent


            if multiple_found:

                print(f"Which station in {city}?...\n")

                for code in station_code:

                    print(f"- {code}?")


            if station_code == other_station:

                print("Sorry, but you cannot arrive and depart from the same station. ")


        if station_code is not None:

            return city
        else:
            return None


    @Rule(NOT(Book(dep_station=W())))
    def get_dep_station(self):

        if self.response is None:

            print(self.facts)
            self.response = "Which station will you be departing from?"
            self.fact_string = "from"
        # station_code = None

        # while station_code is None:

        #     station_code = self.clarify_station(True)


        # self.declare(Book(dep_station=station_code))


    #@Rule(NOT(Book(dep_station=W())),
    #      Book(arr_station=MATCH.arr_station))
    #def _get_dep_station_check_arr_station(self, arr_station):
#
    #    station_code = None
#
    #    while station_code is None:
#
    #        station_code = self.clarify_station(True, arr_station)
#
#
    #    self.declare(Book(dep_station=station_code))


    # get Arrival Station #


    #@Rule(AND(NOT(Book(dep_station=W())),
    #      NOT(Book(arr_station=W()))))
    @Rule(NOT(Book(arr_station=W())))
    def get_arr_station(self):

        if self.response is None:

            print(self.facts)
            self.response = "Which station will you be arriving to?"
            self.fact_string = "to"

        # station_code = None

        # while station_code is None:

        #     station_code = self.clarify_station(False)


        # self.declare(Book(arr_station=station_code))


    #@Rule(NOT(Book(arr_station=W())),
    #      Book(dep_station=MATCH.dep_station))
    #def get_arr_station_check_dep_station(self, dep_station):
#
    #    station_code = None
#
    #    while station_code is None:
#
    #        station_code = self.clarify_station(False, dep_station)
#
#
    #    self.declare(Book(arr_station=station_code))


    @Rule(NOT(Book(dep_time=W())))
    def get_dep_time(self):

        if self.response is None:

            print(self.facts)
            self.response = "Sorry, we didn't get the time. What time will you be departing?\n\t"
            self.fact_string = "at"


    @Rule(NOT(Book(dep_date=W())))
    def get_dep_date(self):

        if self.response is None:

            print(self.facts)
            self.response = "What date will you be departing?\n\t"
            self.fact_string = "on"


    #@Rule(NOT(Book(return_ticket=W())))
    #def get_return(self):
    #    if self.response is None:
    #        self.response = "Will you be returning? (yes or no)\n\t"

    #@Rule(
    #    Book(return_ticket=True),
    #    Book(dep_date=MATCH.dep_date),
    #    NOT(Book(return_date=W())))
    #def get_return_date(self, dep_date):
#
    #    if self.response is None:
#
    #        self.response = "What date will you be returning?\n\t"


    # cannot occur without the date being set
    #@Rule(
    #    Book(return_ticket=True),
    #    Book(return_date=MATCH.return_date),
    #    Book(dep_date=MATCH.dep_date),
    #    Book(dep_time=MATCH.dep_time),
    #    NOT(Book(return_time=W())))
    #def get_return_time(self, return_date, dep_date, dep_time):
    #    if self.response is None:
    #        self.response = "What time will you depart for your return?\n\t"

    # if every information has been filled out
    #@Rule(
    #    Book(return_time=MATCH.return_time),
    #    Book(return_date=MATCH.return_date),
    #    Book(dep_time=MATCH.dep_time),
    #    Book(dep_date=MATCH.dep_date),
    #    Book(dep_station=MATCH.dep_station),
    #    Book(arr_station=MATCH.arr_station),)
    #def success_with_return(self, dep_station, arr_station, dep_date, dep_time, return_time, return_date):
    #    if self.response is None:
#
    #        self.response = (f"So you would like to depart from {dep_station} and arrive at {arr_station} on {dep_date} after "
    #          f"{dep_time}? And it will be a return on {return_date} at {return_time}? "
    #          f"Okay lol don't need to get so worked up about it... \n\n" + scrape_to_string(
    #            dep_station,
    #            arr_station,
    #            dep_date, dep_time, True, return_time, return_date))


    # if every information has been filled out
    #@Rule(
    #    Book(return_ticket=False),
    #    Book(dep_time=MATCH.dep_time),
    #    Book(dep_date=MATCH.dep_date),
    #    Book(dep_station=MATCH.dep_station),
    #    Book(arr_station=MATCH.arr_station),)
    #def success_wout_return(self, dep_station, arr_station, dep_date, dep_time):
    #    if self.response is None:
#
    #        self.response = (f"So you would like to depart from {dep_station} and arrive at {arr_station} on {dep_date} after "
    #            f"{dep_time}? And it will be a return on And it won't be a return? "
    #            f"Okay lol don't need to get so worked up about it... \n\n " + scrape_to_string(
    #                dep_station,
    #                arr_station,
    #                dep_date, dep_time, False, "", ""))

def get_response(user_input: str):

    response = None
    fact_string = ''

    if user_input is None:

        response = random.choice([

            "Hello! What sort of journey will you be making?",
            "Hi! How can I help you today?",
            "Hey! What journey are you looking to make?",
        ])

        response += ' (' + random.choice([

            "Make sure to check the Help button at the top right if you don’t know where to start!",
            "Press the Help button at the top right for guidance!",
            "Use the help button in the top right if you need advice!",
        ]) + ')'

        return response, fact_string


    context = Context(user_input)
    print(context.to_string())


    # check for errors #



    # if facts missing, request #

    if response is None:

        responses = []
        fact_strings = []

        if context.departure is None:

            responses.append(random.choice([

                "From which station would you like to depart?",
                "Which station will you be departing from?",
                "What is the name of the station you will be departing from?"
            ]))

            fact_strings.append('from')


        if context.destination is None:

            responses.append(random.choice([

                "Which station would you like to go to?",
                "Which station will you be arriving at?",
                "What is the name of the station of arrival?",
            ]))

            fact_strings.append('to')


        if context.time is None:

            responses.append(random.choice([

                "What time would you like to depart?",
                "When in the day will you be departing?",
                "At what hour will you depart?",
            ]))

            fact_strings.append('at')


        if context.date is None:

            responses.append(random.choice([

                "What day will you be leaving?",
                "What will be the date of your departure?",
                "What day are you going to get the train?",
            ]))

            fact_strings.append('on')


        if len(responses) == 0:

            if context.return_ticket is None:

                responses.append(random.choice([

                    "Will you be getting a return ticket?",
                ]))

                fact_strings.append('')

#            elif context.return_ticket is True:
#
#                if context.return_time is None:
#
#                    responses.append(random.choice([
#
#                        "What time will you be returning?",
#                    ]))
#
#
#                if context.return_date is None:
#
#                    responses.append(random.choice([
#
#                        "What date will you be returning?",
#                    ]))


        if len(responses) == 0:

            response = "All facts acquired!"
            fact_string = ''

        else:

            response_index = random.randint(0, len(responses) - 1)

            response = responses[response_index]
            fact_string = fact_strings[response_index]


    return response, f'{context.to_string()}{fact_string} '


class Context:

    def __init__(self, string: str):

        self.return_ticket =\
            self.time =\
            self.date =\
            self.departure =\
            self.destination =\
            self.return_time =\
            self.return_date =\
            self.error_message = None

        string_nlp = nlp(string)


        self.extraction_order = []


        # Extract entities
        entities = [(ent.text, ent.label_) for ent in string_nlp.ents]

        # Extract dependency relations
        dep_relations = [(token.text, token.dep_, token.head.text) for token in string_nlp]

        for ent in entities:

            for token, dep, head in dep_relations:

                print(token, dep, head)

                if ent[0] == token:

                    if dep == "pobj" and head in ["from", "leave"] and self.departure is None:

                        self.extraction_order.append('departure')
                        self.departure = ent[0]

                    if dep == "pobj" and head in ["to", "arrive", "at"] and self.destination is None:

                        self.extraction_order.append('destination')
                        self.destination = ent[0]


        if 'return' in string:

            string_nlp = nlp(string[string.index('return'):])
            return_nlp = nlp(string[:string.index('return'):])

            self.return_ticket = 'not' not in string


        if 'yes' in string:

            self.return_ticket = True


        time_tokens = []

        # Extract time and date
        for token in string_nlp:

            try:

                if self.date is None:

                    self.date = convert_date(token.text)

            except ValueError:

                pass


            if token.ent_type_ == "TIME" or token.ent_type_ == "DATE":

                if token.ent_type_ == "DATE":

                    if self.date is None:

                        self.extraction_order.append('date')
                        self.date = convert_date(token.text)

                elif self.time is None:

                    time_tokens.append(token.text)


        time_str = ''.join(time_tokens)

        if time_str != '':

            self.extraction_order.append('time')
            self.time = convert_time(''.join(time_tokens))


        self.empty = (

            self.return_ticket is None and
            self.time is None and
            self.date is None and
            self.departure is None and
            self.destination is None and
            self.return_time is None and
            self.return_date is None
        )


    def to_string(self):

        string = ""

        if self.return_ticket is True:

            string += f'return. '

            ##if self.return_time is not None:
        ##
        ##    string += f'{self.return_time} '
        ##
        ##if self.return_date is not None:
        ##
        ##    string += f'{self.return_date} '

        elif self.return_ticket is False:

            string += f'no return. '


        if self.departure is not None:

            string += f'from {self.departure} '

        if self.destination is not None:

            string += f'to {self.destination} '

        if self.time is not None:

            string += f'at {self.time} '

        if self.date is not None:

            string += f'on {self.date} '


        return string


# test harness to prove it works
def TestHarness():

    response, context = get_response(None)

    while True:

        print(response)
        message = f'{context}{input()}'
        print(message)
        response, context = get_response(message)


# if running this file, run the test harness
if __name__ == '__main__':

    TestHarness()


'''
def bot_response(message: str, context: Context):

    #return_time = return_date = None
    #if context.destination and context.time and context.return_ticket and context.departure and context.date is not None:
    #    _, return_time, return_date, _, _ = extract_entities(nlp(message))

    #return_ticket, time, date, departure, destination = extract_entities(nlp(message))
    context = Context(f"{context.to_string()} {message}")

    #if context.return_ticket is not None:
    #    return_ticket = context.return_ticket
#
    #if context.time is not None:
    #    time = context.time
#
    #if context.date is not None:
    #    date = context.date
#
    #if context.departure is not None:
    #    departure = context.departure
#
    #if context.destination is not None:
    #    destination = context.destination

    bot = TrainBot()
    bot.reset()

    if context.return_ticket is not None:

        print(context.return_ticket)
        bot.declare(Book(return_ticket=context.return_ticket))

    if context.time is not None:

        print(context.time)
        bot.declare(Book(dep_time=context.time))

    if context.date is not None:

        print(context.date)
        bot.declare(Book(dep_date=context.date))

    if context.departure is not None:

        print(context.departure)
        bot.declare(Book(dep_station=context.departure))

    if context.destination is not None:

        print(context.destination)
        bot.declare(Book(arr_station=context.destination))

    if context.return_time is not None:

        print(context.return_time)
        bot.declare(Book(return_time=context.return_time))

    if context.return_date is not None:

        print(context.return_date)
        bot.declare(Book(return_date=context.return_date))


    message, fact_string = bot.run_with_response()

    return message, context, fact_string
'''

# class TrainBot(KnowledgeEngine):
#     def __init__(self):
#         super().__init__()
#         self.response = None

#     def run_with_response(self):
#         self.response = None
#         self.run()
#         return self.response

#     # if the user types "undo", delete the last fact
#     def check_undo(self, user_input):

#         user_input = user_input.lower()

#         if "undo" in user_input:

#             remove_key = list(self.facts.keys())[-1]
#             remove_fact = self.facts[remove_key]
#             self.retract(remove_fact)
#             print(self.facts)
#             return True

#         # unsuccessful
#         return False


#     # station clarification used in multiple functions
#     def clarify_station(self, is_departure, other_station=None):

#         station_code = None
#         multiple_found = True

#         # get words to say in print so arrival and departure can be unified
#         ing = "departing" if is_departure else "arriving"

#         while station_code is None or multiple_found or station_code == other_station:

#             city = input(f"Which station will you be {ing} from?\n\t")

#             if self.check_undo(city):
#                 return None

#             station_code, multiple_found = convert_station_name(city)

#             # if the user has not used a one word answer
#             if station_code is None:

#                 for ent in nlp(city).ents:

#                     station_code, multiple_found = convert_station_name(ent.text)

#                     if station_code is not None:

#                         return ent


#             if multiple_found:

#                 print(f"Which station in {city}?...\n")

#                 for code in station_code:

#                     print(f"- {code}?")


#             if station_code == other_station:

#                 print("Sorry, but you cannot arrive and depart from the same station. ")


#         if station_code is not None:

#             return city
#         else:
#             return None


#     # @DefFacts()
#     # def _initial_action(self):

#         # return_ticket, time, date, departure, destination = extract_entities(nlp(input("Hello!\n\t")))

#         # if return_ticket is not None:

#         #     yield Book(return_ticket=return_ticket)

#         # if time is not None:

#         #     yield Book(dep_time=time)

#         # if date is not None:

#         #     yield Book(dep_date=date)

#         # if departure is not None:

#         #     if convert_station_name(departure)[0] is not None and convert_station_name(departure)[1] is False:

#         #         yield Book(dep_station=departure)

#         # if destination is not None:

#         #     if convert_station_name(destination)[0] is not None and convert_station_name(destination)[1] is False:

#         #         yield Book(arr_station=destination)


#     # get Departure Station #


#     @Rule(AND(NOT(Book(dep_station=W())),
#           NOT(Book(arr_station=W()))))
#     def _get_dep_station(self):

#         station_code = None

#         while station_code is None:

#             station_code = self.clarify_station(True)


#         self.declare(Book(dep_station=station_code))


#     @Rule(NOT(Book(dep_station=W())),
#           Book(arr_station=MATCH.arr_station))
#     def _get_dep_station_check_arr_station(self, arr_station):

#         station_code = None

#         while station_code is None:

#             station_code = self.clarify_station(True, arr_station)


#         self.declare(Book(dep_station=station_code))


#     # get Arrival Station #


#     @Rule(AND(NOT(Book(dep_station=W())),
#           NOT(Book(arr_station=W()))))
#     def get_arr_station(self):

#         station_code = None

#         while station_code is None:

#             station_code = self.clarify_station(False)


#         self.declare(Book(arr_station=station_code))


#     @Rule(NOT(Book(arr_station=W())),
#           Book(dep_station=MATCH.dep_station))
#     def get_arr_station_check_dep_station(self, dep_station):

#         station_code = None

#         while station_code is None:

#             station_code = self.clarify_station(False, dep_station)


#         self.declare(Book(arr_station=station_code))


#     @Rule(NOT(Book(dep_time=W())))
#     def get_dep_time(self):
#         self.response = "Sorry, we didn't get the time. What time will you be departing?\n\t"
#         # time_tokens = []
#         # for token in nlp(input("Sorry, we didn't get the time. What time will you be departing?\n\t")):

#         #     if token.ent_type_ == "TIME":
#         #         time_tokens.append(token.text)

#         # time_str = ''.join(time_tokens)
#         # if time_str != '':
#         #     self.declare(Book(dep_time=str(convert_time(time_str))))


#     @Rule(NOT(Book(dep_date=W())))
#     def get_dep_date(self):
#         self.response = "What date will you be departing?\n\t"
#         # dep_date = None

#         # while dep_date is None:

#         #     user_input = input("What date will you be departing?\n\t")

#         #     if self.check_undo(user_input):
#         #         return

#         #     for token in nlp(user_input):

#         #         if token.ent_type_ == "DATE":

#         #             dep_date = str(convert_date(token.text))
#         #             break

#         #     if dep_date is None:

#         #         print("Sorry, that date is invalid. ")


#         # self.declare(Book(dep_date=dep_date))


#     @Rule(NOT(Book(return_ticket=W())))
#     def get_return(self):
#         self.response = "Will you be returning? (yes or no)\n\t"
#         # user_input = input("Will you be returning? (yes or no)\n\t").lower()

#         # if self.check_undo(user_input):
#         #     return

#         # return_ticket = "yes" in user_input or "will be" in user_input

#         # self.declare(Book(return_ticket=return_ticket))


#     @Rule(
#         Book(return_ticket=True),
#         Book(dep_date=MATCH.dep_date),
#         NOT(Book(return_date=W())))
#     def get_return_date(self, dep_date):
#         self.response = "What date will you be returning?\n\t"

#         # return_date = None
#         # departure_date = convert_date(dep_date)

#         # while return_date is None:

#         #     user_input = input("What date will you be returning?\n\t")

#         #     if self.check_undo(user_input):
#         #         return

#         #     for token in nlp(user_input):

#         #         if token.ent_type_ == "DATE":

#         #             return_date = str(convert_date(token.text))
#         #             break

#         #     if return_date is not None:

#         #         if return_date < departure_date:

#         #             print("Sorry, the return date cannot be before the departure date. ")
#         #             return_date = None
#         #     else:

#         #         print("Sorry, that date is invalid. ")

#         # self.declare(Book(return_date=return_date))


#     # cannot occur without the date being set
#     @Rule(
#         Book(return_ticket=True),
#         Book(return_date=MATCH.return_date),
#         Book(dep_date=MATCH.dep_date),
#         Book(dep_time=MATCH.dep_time),
#         NOT(Book(return_time=W())))
#     def get_return_time(self, return_date, dep_date, dep_time):
#         self.response = "What time will you depart for your return?\n\t"
#         # return_time = None
#         # check_time = return_date == dep_date
#         # departure_time = convert_time(dep_time)

#         # while return_time is None:

#         #     user_input = input("What time will you depart for your return?\n\t")

#         #     if self.check_undo(user_input):
#         #         return

#         #     time_tokens = []
#         #     for token in nlp(user_input):

#         #         if token.ent_type_ == "TIME":
#         #             time_tokens.append(token.text)
#         #             time_str = ''.join(time_tokens)
#         #         if time_str != '':
#         #             return_time = time_str

#         #     if return_time is not None:

#         #         if check_time and return_time <= departure_time:

#         #             print("Sorry, the return time cannot be before the departure time if they are on the same day. ")
#         #             return_time = None
#         #     else:

#         #         print("Sorry, that time is invalid. ")

#         # self.declare(Book(return_time=return_time))




#     # if every information has been filled out
#     @Rule(
#         Book(return_time=MATCH.return_time),
#         Book(return_date=MATCH.return_date),
#         Book(dep_time=MATCH.dep_time),
#         Book(dep_date=MATCH.dep_date),
#         Book(dep_station=MATCH.dep_station),
#         Book(arr_station=MATCH.arr_station),)
#     def success_with_return(self, dep_station, arr_station, dep_date, dep_time, return_time, return_date):

#         self.response = (f"So you would like to depart from {dep_station} and arrive at {arr_station} on {dep_date} after "
#               f"{dep_time}? And it will be a return on {return_date} at {return_time}? "
#               f"Okay lol don't need to get so worked up about it... \n\n" + scrape_to_string(
#                 dep_station,
#                 arr_station,
#                 dep_date, dep_time, True, return_time, return_date))


#     # if every information has been filled out
#     @Rule(
#         Book(return_ticket=False),
#         Book(dep_time=MATCH.dep_time),
#         Book(dep_date=MATCH.dep_date),
#         Book(dep_station=MATCH.dep_station),
#         Book(arr_station=MATCH.arr_station),)
#     def success_wout_return(self, dep_station, arr_station, dep_date, dep_time):

#         self.response = (f"So you would like to depart from {dep_station} and arrive at {arr_station} on {dep_date} after "
#               f"{dep_time}? And it will be a return on And it won't be a return? "
#               f"Okay lol don't need to get so worked up about it... \n\n " + scrape_to_string(
#                 dep_station,
#                 arr_station,
#                 dep_date, dep_time, False, "", ""))