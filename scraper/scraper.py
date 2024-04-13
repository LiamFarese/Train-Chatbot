import json
import requests

class TicketQuery:
  def __init__(self, origin, destination, travel_type, travel_month, travel_day, travel_hour, travel_minute, adults, children):
    self.origin = origin
    self.destination = destination
    self.travel_type = travel_type
    self.travel_month = travel_month
    self.travel_day = travel_day
    self.travel_hour = travel_hour
    self.travel_minute = travel_minute
    self.adults = adults
    self.children = children

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
  travel_month  = input("Travel month: ")
  travel_day    = input("Travel day: ")
  travel_hour   = input("Travel hour: ")
  travel_minute = input("Travel minute: ")
  adults        = int(input("How many adult passengers?: "))
  children      = int(input("How many children?: "))

  return TicketQuery(origin, destination, travel_type, travel_month, travel_day, travel_hour, travel_minute, adults, children)

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
  myquery = {"origin":{"crs":query.origin,"group":False},
             "destination":{"crs":query.destination,"group":False},
             "outwardTime":{"travelTime":f"2024-{query.travel_month}-{query.travel_day}T{query.travel_hour}:{query.travel_minute}:00+01:00","type":query.travel_type},
             "fareRequestDetails":{"passengers":{"adult":query.adults,"child":query.children},"fareClass":"ANY","railcards":[]},
             "directTrains":False,"reducedTransferTime":False,"onlySearchForSleeper":False,"overtakenTrains":True,"useAlternativeServices":False,"increasedInterchange":"ZERO"}
  response = requests.post(url, json = myquery)
  return response

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

def main():
  ticket_query = query()
  response = get_ticket_info(ticket_query)
  write_results(response)
  scrape_data(response)

if __name__ == "__main__":
  main()

