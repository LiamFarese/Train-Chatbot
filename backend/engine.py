
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

    station_code = station_codes.get(city.upper())

    # if there is no station code, set to list of stations
    if station_code is None:

        stations_with_city = [station for station in station_codes.keys() if city.upper() in station]

        if stations_with_city:

            return stations_with_city, True
        else:
            return None, False


    return city, False


def convert_date(date_input):

    if 'the' in date_input:

        date_input = date_input.replace('the', '')


    days_of_the_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

    if date_input.lower() == "tomorrow":

        return (datetime.now() + relativedelta(days=1)).strftime("%d/%m/%Y")

    elif date_input.lower() == "today":
        return datetime.now().strftime("%d/%m/%Y")

    elif date_input.lower() in days_of_the_week:

        # Calculate date for the next occurrence of the specified day of the week
        today = datetime.now()
        days_until_target_day = ((days_of_the_week.index(date_input.lower()) - today.weekday()) + 7) % 7
        return (today + relativedelta(days=days_until_target_day)).strftime("%d/%m/%Y")

    date = parse_date(date_input)

    if date < datetime.now():

        return None


    return date.strftime("%d/%m/%Y")


def convert_time(input):

    if '.' in input:

        return None


    time_obj = parse_date(input).time()
    return time_obj.strftime("%H:%M:%S")


def extract_entities(user_input: str):

    return_ticket = time = date = departure = destination = None

    user_input = user_input.lower()
    user_input_nlp = nlp(user_input)

    # Extract entities
    entities = [(ent.text, ent.label_) for ent in user_input_nlp.ents]

    # Extract dependency relations
    dep_relations = [(token.text, token.dep_, token.head.text) for token in user_input_nlp]

    for ent in entities:

        for token, dep, head in dep_relations:

            if ent[0] == token:

                if dep == "pobj" and head in ["from", "leave"]:

                    station, valid, multiple_stations = try_convert_station_name(user_input)

                    if valid and not multiple_stations:

                        departure = station


                elif dep == "pobj" and head in ["to", "arrive", "at"]:

                    station, valid, multiple_stations = try_convert_station_name(user_input)

                    if valid and not multiple_stations:

                        destination = station


    if 'return' in user_input:

        return_ticket = not ("no" in user_input)


    time_tokens = []

    # Extract time and date
    for token in user_input_nlp:

        if token.ent_type_ == "TIME":

            time_tokens.append(token.text)


        elif token.ent_type_ == "DATE" and date is None:

            date = convert_date(token.text)


    time_str = ''.join(time_tokens)

    if time_str != '':

        time = convert_time(''.join(time_tokens))


    return return_ticket, time, date, departure, destination


def scrape_to_string(dep_station, arr_station, dep_date, dep_time,
                     return_ticket=False, return_time='', return_date=''):

    with open('model.pickle', 'rb') as file:
        model = pickle.load(file)


    with open('historical-data/station_dict.pkl', 'rb') as file:
        station_dict = pickle.load(file)

    dep_station = station_codes[dep_station.upper()]
    arr_station = station_codes[arr_station.upper()]

    details, url = scrape(
        arr_station,
        dep_station,
        dep_date,
        dep_time,
        False,
        '',
        '')

    if return_ticket:

        details, url = scrape(
            arr_station,
            dep_station,
            dep_date,
            dep_time,
            True,
            return_time,
            return_date)


    dep_dt = dt.datetime.strptime(details[0], '%Y-%m-%d %H:%M:%S')

    day_of_week = dep_dt.weekday()
    day_of_year = day_of_week == 5 or 6
    weekday     = day_of_year = dep_dt.timetuple().tm_yday
    on_peak     = dep_dt.hour >= 9
    hour        = on_peak = dep_dt.hour >= 9
    first_stop  = 0
    second_stop = 0

    if dep_station in station_dict:

        first_stop = station_dict[dep_station]


    if arr_station in station_dict:

        second_stop = station_dict[arr_station]


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


def get_question(query):

    question = 'Invalid query type. '

    if query == 'departure':

        question = random.choice([

            "From which station would you like to depart?",
            "Which station will you be departing from?",
            "What is the name of the station you will be departing from?"
        ])

    elif query == 'destination':

        question = random.choice([

            "Which station would you like to go to?",
            "Which station will you be arriving at?",
            "What is the name of the station of arrival?",
        ])

    elif query == 'time':

        question = random.choice([

            "What time would you like to depart?",
            "When in the day will you be departing?",
            "At what hour will you depart?",
        ])

    elif query == 'date':

        question = random.choice([

            "What day will you be leaving?",
            "What will be the date of your departure?",
            "What day are you going to get the train?",
        ])

    elif query == 'is_return':

        question = random.choice([

            "Would you like a return ticket? (yes, no)",
        ])

    elif query == 'return_time':

        question = random.choice([

            "What time would you like to return?",
        ])

    elif query == 'return_date':

        question = random.choice([

            "What date would you like to return?",
        ])


    return question


def try_extract_if_valid(message: str, extract_func, warning: str):

    # try entities
    for ent in nlp(message).ents:

        try:

            return True, extract_func(ent.text)

        except:
            pass

    # try whole sentence
    try:

        return True, extract_func(message)

    except:
        pass


    # now split everything up
    for word in message.split():

        try:

            return True, extract_func(word)

        except:
            pass


    return False, warning


def try_convert_time(message: str):

    warning = ("The time you entered is in an invalid format. "
            "Perhaps try a single word answer without a fullstop. Maybe try hour:minute! "
            "For example, 15:45")

    result = try_extract_if_valid(message, convert_time, warning)

    if result[1] is None:

        return False, warning


    return result


def try_convert_date(message: str):

    result = try_extract_if_valid(message, convert_date,
                                "The date you entered is in an invalid format. Perhaps try a single word answer,"
                                "or try day/month/year (For example, 25/05/24),"
                                "or even the day of the week (For example, today or Tuesday)!")

    if result[1] is None:

        return False, None


    return result


def try_convert_station_name(message: str):

    station_code, multiple_found = convert_station_name(message)
    full_message = message

    # if the user has not used a one word answer
    if station_code is None:

        for ent in nlp(message).ents:

            station_code, multiple_found = convert_station_name(ent.text)

            if station_code is not None and not multiple_found:

                message = station_code
                break
            else:

                for station in station_codes.keys():

                    if station.lower() in message:

                        message = station.lower()
                        multiple_found = False
                        break


    if multiple_found:

        message = 'Did you mean any of the following stations:'

        for code in station_code:

            message += f" {code},"


    return message, station_code is not None, multiple_found


def get_empty_query(first_query=None):

    return {

        'message': None,
        'current_query': first_query,

        'departure': None,
        'destination': None,
        'time': None,
        'date': None,

        'is_return': None,
        'return_time': None,
        'return_date': None,

        'history': [],
    }


def get_response(query: dict):

    if query['message'] is not None:

        query['message'] = query['message'].lower()


    # allows for easy debugging
    if query['current_query'] is not None and query['message'] is None:

        query['message'] = get_question(query['current_query'])
        return query


    valid = query['current_query'] is not None

    if query['current_query'] is None:

        if query['message'] is not None:

            (query['is_return'], query['time'], query['date'], query['departure'],
             query['destination']) = extract_entities(query['message'])

            valid = True


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

        query['message'] = response


    # undoing #

    if 'undo' in query['message'] and not ("don't" or "dont" or "not") in query['message']:

        query['message'] = 'Okay. We have undone the previous message.\n\n'

        if len(query['history']) == 0:

            empty_query = get_response(get_empty_query())
            empty_query['message'] = query['message'] + empty_query['message']
            return empty_query
        else:
            previous_query = query['history'].pop()
            query['current_query'] = previous_query
            query['message'] += get_question(previous_query)
            return query


    # query resetting #

    if query['current_query'] == 'reset':

        if 'yes' in query['message']:

            query = get_empty_query()
            query['message'] = "Okay. We have reset the query for you... Type in your new query..."
        else:
            query['message'] = "Nevermind, we have not reset your query! Answer the previous question..."

            if len(query['history']) > 0:

                query['current_query'] = query['history'].pop()
            else:
                query['current_query'] = None


        return query


    if 'reset' in query['message'] and not ("don't" or "dont" or "not") in query['message']:

        if query['current_query'] is not None:

            query['history'].insert(0, query['current_query'])


        query['message'] = 'Are you sure? (yes or no)'
        query['current_query'] = 'reset'

        return query


    # validate responses #

    if query['current_query'] == "departure":

        query['message'], valid, multiple_found = try_convert_station_name(query['message'])

        if not multiple_found:

            if valid:

                if query['destination'] is not None:

                    valid = query['message'] != query['destination']

                if valid:

                    query['departure'] = query['message']
                else:
                    query['message'] = ('Sorry, but the arrival and departure stations cannot be identical. '
                                        'Type undo if you previously entered the wrong station or re-enter if you made a '
                                        'mistake')
            else:

                query['message'] = ('Sorry, but the station you entered is invalid. '
                                    'You may have misspelled it. Perhaps try entering one word in the station name or '
                                    'the city and we will show you a list of station accepted names.')
        else:
            valid = False


    elif query['current_query'] == "destination":

        query['message'], valid, multiple_found = try_convert_station_name(query['message'])

        if not multiple_found:

            if valid and not multiple_found:

                if query['departure'] is not None:

                    valid = query['message'] != query['departure']


                if valid:

                    query['destination'] = query['message']
                else:
                    query['message'] = ('Sorry, but the arrival and departure stations cannot be identical. '
                                        'Type undo if you previously entered the wrong station or re-enter if you made a '
                                        'mistake')
            else:

                query['message'] = ('Sorry, but the station you entered is invalid. '
                                    'You may have misspelled it. Perhaps try entering one word in the station name or '
                                    'the city and we will show you a list of accepted station names.')
        else:
            valid = False


    elif query['current_query'] == "date":

        valid, result = try_convert_date(query['message'])

        if valid:

            query['date'] = result
        else:

            if result is None:

                query['message'] = 'Sorry, but the date you enter cannot be before the current date.'
            else:
                query['message'] = result


    elif query['current_query'] == "time":

        valid, result = try_convert_time(query['message'])

        if valid:

            query['time'] = result
        else:
            query['message'] = result


    elif query['current_query'] == 'is_return':

        query['is_return'] = ('yes' or 'affirmative' or 'sure') in query['message']

        if not query['is_return'] and not ('no' or 'negative') in query['message']:

            query['is_return'] = None
            query['message'] = 'Sorry, you have entered in an invalid answer. Type yes, no, or undo.'
            valid = False


    elif query['current_query'] == "return_date":

        valid, result = try_convert_date(query['message'])

        if valid:

            date = datetime.strptime(query['date'], '%d/%m/%Y')
            return_date = datetime.strptime(result, '%d/%m/%Y')

            # make sure the original date is before or same as the return
            valid = not (date > return_date)

            if valid:


                if query['return_time'] is not None and date == return_date:

                    time = datetime.strptime(query['time'], '%H:%M:%S')
                    return_time = datetime.strptime(query['return_time'], '%H:%M:%S')

                    valid = not (time >= return_time)

                if valid:

                    query['return_date'] = result
                else:
                    query['message'] \
                        = ('Sorry, but the return date and time cannot be before the departure date and time. '
                           'Type undo if you previously entered the wrong station or re-enter if you made a '
                           'mistake')
            else:
                query['message'] \
                    = ('Sorry, but the return date cannot be before the departure date. '
                       'Type undo if you previously entered the wrong station or re-enter if you made a '
                       'mistake')
        else:
            query['message'] = result


    elif query['current_query'] == "return_time":

        valid, result = try_convert_time(query['message'])

        if valid:

            if query['return_date']:

                date = datetime.strptime(query['date'], '%d/%m/%Y')
                return_date = datetime.strptime(query['return_date'], '%d/%m/%Y')

                if date == return_date:

                    time = datetime.strptime(query['time'], '%H:%M:%S')
                    return_time = datetime.strptime(result, '%H:%M:%S')

                    valid = not (time >= return_time)


            if valid:

                query['return_time'] = result
            else:
                query['message'] \
                    = ('Sorry, but the return date and time cannot be before the departure date and time. '
                       'Type undo if you previously entered the wrong station or re-enter if you made a '
                       'mistake')
        else:
            query['message'] = result


    if valid:

        if query['current_query'] is not None:

            query['history'].insert(0, query['current_query'])


        responses = []
        current_queries = []


        # get questions #

        if query['departure'] is None:

            responses.append(get_question('departure'))
            current_queries.append('departure')


        if query['destination'] is None:

            responses.append(get_question('destination'))
            current_queries.append('destination')
            

        if query['time'] is None:

            responses.append(get_question('time'))
            current_queries.append('time')


        if query['date'] is None:

            responses.append(get_question('date'))
            current_queries.append('date')

        # do not ask the following questions until the previous are ready
        if len(responses) == 0:

            if query['is_return'] is None:

                responses.append(get_question('is_return'))
                current_queries.append('is_return')


            # do not ask the following questions until the previous are ready
            if len(responses) == 0 and query['is_return']:

                if query['return_date'] is None:

                    responses.append(get_question('return_date'))
                    current_queries.append('return_date')


                if query['return_time'] is None:

                    responses.append(get_question('return_time'))
                    current_queries.append('return_time')


        # if no questions to get, return ticket
        if len(responses) == 0:

            message = scrape_to_string(
                query['departure'],
                query['destination'],
                query['date'],
                query['time'],
                query['is_return'],
                query['return_time'],
                query['return_date'],) + \
                "\nIf you would like to ask for another ticket, simply enter it below: "


            query = get_empty_query()
            query['message'] = message
        else:
            response_index = random.randint(0, len(responses) - 1)

            query['message'] = responses[response_index]
            query['current_query'] = current_queries[response_index]


    return query

# test harness to prove it works
def TestHarness():

    query = get_empty_query()
    query = get_response(query)

    while True:

        print('message: ', query['message'])
        query['message'] = input().lower()
        query = get_response(query)
        print(query)

# if running this file, run the test harness
if __name__ == '__main__':

    TestHarness()

