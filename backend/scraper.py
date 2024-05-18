import json
import requests

class TicketQuery:
  def __init__(self, origin, destination, travel_type, travel_year, travel_month, travel_day, travel_hour, travel_minute):
    self.origin = origin
    self.destination = destination
    self.travel_type = travel_type
    self.travel_year = travel_year
    self.travel_month = travel_month
    self.travel_day = travel_day
    self.travel_hour = travel_hour
    self.travel_minute = travel_minute

class TicketInfo:
  def __init__(self, depart_time, arrival_time, duration, delay, operator, cheapest_ticket, ticket_type):
    self.depart_time = depart_time
    self.arrival_time = arrival_time
    self.duration = duration
    self.delay = delay
    self.operator = operator
    self.cheapest_ticket = cheapest_ticket
    self.ticket_type = ticket_type

def query():
  origin        = input("Origin station code: ")
  destination   = input("Destination station code: ")
  travel_type   = input("ARRIVE or DEPART?: ")
  travel_year   = input("travel year: ")
  travel_month  = input("Travel month: ")
  travel_day    = input("Travel day: ")
  travel_hour   = input("Travel hour: ")
  travel_minute = input("Travel minute: ")

  return TicketQuery(origin, destination, travel_type, travel_year, travel_month, travel_day, travel_hour, travel_minute)

def write_results(response: requests.Response):
  if response.status_code == 200:
    print("Response written to response.json")
    # Open a file in write mode
    with open("response.json", "w") as file:
      json.dump(response.json(), file, indent=2)

def get_ticket_info(query: TicketQuery):
  print("\n-------------------------------------------------------------------------------------------")
  print("Sending query")
  url = "https://jpservices.nationalrail.co.uk/journey-planner"
  # if(query.travel_type == "RETURN"){}
  myquery = {"origin":{"crs":query.origin,"group":False},
             "destination":{"crs":query.destination,"group":False},
             "outwardTime":{"travelTime":f"{query.travel_year}-{query.travel_month}-{query.travel_day}T{query.travel_hour}:{query.travel_minute}:00+01:00","type":query.travel_type},
             "fareRequestDetails":{"passengers":{"adult":1,"child":0},"fareClass":"ANY","railcards":[]},
             "directTrains":False,"reducedTransferTime":False,"onlySearchForSleeper":False,"overtakenTrains":True,"useAlternativeServices":False,"increasedInterchange":"ZERO"}
  response = requests.post(url, json = myquery)
  user_url = f"https://www.nationalrail.co.uk/journey-planner/?type=single&origin={query.origin}&destination={query.destination}&leavingType=departing&leavingDate={query.travel_day}{query.travel_month}{query.travel_year[-2:]}&leavingHour={query.travel_hour}&leavingMin={query.travel_minute}&adults=1&extraTime=0#O"
  return response, user_url

def scrape_data(response: requests.Response):
  data = response.json()
  depart_time = data["outwardJourneys"][0]["timetable"]["scheduled"]["departure"]
  arrival_time = data["outwardJourneys"][0]["timetable"]["scheduled"]["arrival"]
  duration = data["outwardJourneys"][0]["duration"]
  delay = data["outwardJourneys"][0]["delayInMinutes"]
  operator = data["outwardJourneys"][0]["legs"][0]["operator"]["name"]

  tickets = {}
  for ticket in data["outwardJourneys"][0]["fares"]:
    tickets[ticket["totalPrice"]/100] = ticket["typeDescription"]

  cheapest_ticket = min(tickets.keys())
  ticket_type = tickets[cheapest_ticket]
  print("\n-------------------------------------------------------------------------------------------")
  print(f"departure time: {depart_time}, \n"
        f"arrival time: {arrival_time}, \n"
        f"duration: {duration}, \n"
        f"operator: {operator}, \n"
        f"Ticket price: {cheapest_ticket} \n"
        f"Ticket type: {ticket_type}")
  
  return TicketInfo(depart_time, arrival_time, duration, delay, operator, cheapest_ticket, ticket_type)


def scrape(destination, departure, date, time, return_ticket, return_time, return_date):

  day, month, year = date.split("/")
  hour, minute, _ = time.split(":")

  result, url = get_ticket_info(TicketQuery(departure, destination, "DEPART", year, month, day, hour, minute))

  return scrape_data(result), url

def test_harness():
  ticket_query = query()
  response, url = get_ticket_info(ticket_query)
  print(url)
  write_results(response)
  scrape_data(response)

if __name__ == "__main__":
  test_harness()

