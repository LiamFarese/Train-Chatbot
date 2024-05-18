import json
import requests
from datetime import datetime

class TicketQuery:
  def __init__(self, origin, destination, travel_year, travel_month, travel_day, travel_hour, travel_minute):
    self.origin        = origin
    self.destination   = destination
    self.travel_year   = travel_year
    self.travel_month  = travel_month
    self.travel_day    = travel_day
    self.travel_hour   = travel_hour
    self.travel_minute = travel_minute

class ReturnQuery:
  def __init__(self, day, month, year, hour, minute):
    self.day    = day
    self.month  = month
    self.year   = year
    self.hour   = hour
    self.minute = minute

class TicketInfo:
  def __init__(self, depart_time, arrival_time, duration, delay, operator):
    self.depart_time     = depart_time
    self.arrival_time    = arrival_time
    self.duration        = duration
    self.delay           = delay
    self.operator        = operator

def query():
  origin        = input("Origin station code: ")
  destination   = input("Destination station code: ")
  travel_year   = input("travel year: ")
  travel_month  = input("Travel month: ")
  travel_day    = input("Travel day: ")
  travel_hour   = input("Travel hour: ")
  travel_minute = input("Travel minute: ")

  return TicketQuery(origin, destination, travel_year, travel_month, travel_day, travel_hour, travel_minute)

def write_results(response: requests.Response):
  if response.status_code == 200:
    print("Response written to response.json")
    # Open a file in write mode
    with open("response.json", "w") as file:
      json.dump(response.json(), file, indent=2)

def get_ticket_info(query: TicketQuery, return_query: ReturnQuery):
  url = "https://jpservices.nationalrail.co.uk/journey-planner"
  myquery = None
  user_url = None
  if return_query is None:
    myquery = {"origin":{"crs":query.origin,"group":False},
              "destination":{"crs":query.destination,"group":False},
              "outwardTime":{"travelTime":f"{query.travel_year}-{query.travel_month}-{query.travel_day}T{query.travel_hour}:{query.travel_minute}:00+01:00","type":"DEPART"},
              "fareRequestDetails":{"passengers":{"adult":1,"child":0},"fareClass":"ANY","railcards":[]},
              "directTrains":False,"reducedTransferTime":False,"onlySearchForSleeper":False,"overtakenTrains":True,"useAlternativeServices":False,"increasedInterchange":"ZERO"}
    user_url = f"https://www.nationalrail.co.uk/journey-planner/?type=single&origin={query.origin}&destination={query.destination}&leavingType=departing&leavingDate={query.travel_day}{query.travel_month}{query.travel_year[-2:]}&leavingHour={query.travel_hour}&leavingMin={query.travel_minute}&adults=1&extraTime=0#O"
  else:
    myquery = {"origin":{"crs":query.origin,"group":False},
               "destination":{"crs":query.destination,"group":False},
                "outwardTime":{"travelTime":f"{query.travel_year}-{query.travel_month}-{query.travel_day}T{query.travel_hour}:{query.travel_minute}:00+01:00","type":"DEPART"},
                "fareRequestDetails":{"passengers":{"adult":1,"child":0},"fareClass":"ANY","railcards":[]},"directTrains":False,"reducedTransferTime":False,"onlySearchForSleeper":False,"overtakenTrains":True,"useAlternativeServices":False,
                "inwardTime":{"travelTime":f"{return_query.year}-{return_query.month}-{return_query.day}T{return_query.hour}:{return_query.minute}:00+01:00","type":"DEPART"},"increasedInterchange":"ZERO"}
    user_url = f"https://www.nationalrail.co.uk/journey-planner/?type=return&origin={query.origin}&destination={query.destination}&leavingType=departing&leavingDate={query.travel_day}{query.travel_month}{query.travel_year[-2:]}&leavingHour={query.travel_hour}&leavingMin={query.travel_minute}&returnType=departing&returnDate={return_query.day}{return_query.month}{return_query.year[-2:]}&returnHour={return_query.hour}&returnMin={return_query.minute}&adults=1&extraTime=0#I"
  response = requests.post(url, json = myquery)
  return response, user_url
  
def scrape_data(response: requests.Response):
  data = response.json()
  depart_time = data["outwardJourneys"][0]["timetable"]["scheduled"]["departure"]
  arrival_time = data["outwardJourneys"][0]["timetable"]["scheduled"]["arrival"]
  duration = data["outwardJourneys"][0]["duration"]
  delay = data["outwardJourneys"][0]["delayInMinutes"]

  depart_time = datetime.fromisoformat(depart_time)
  depart_time = depart_time.strftime("%Y-%m-%d %H:%M:%S")

  arrival_time = datetime.fromisoformat(arrival_time)
  arrival_time = arrival_time.strftime("%Y-%m-%d %H:%M:%S")

  result = f"Here is some information about the outward journey train: \ndeparture time: {depart_time}, arrival time: {arrival_time}, duration: {duration}"

  return_depart_time = None
  return_arrive_time = None
  return_duration    = None
  if(data["inwardJourneys"] is not None):
    depart_time  = data["inwardJourneys"][0]["timetable"]["scheduled"]["departure"]
    arrival_time = data["inwardJourneys"][0]["timetable"]["scheduled"]["arrival"]
    duration     = data["inwardJourneys"][0]["duration"] 

    depart_time = datetime.fromisoformat(depart_time)
    depart_time = depart_time.strftime("%Y-%m-%d %H:%M:%S")

    arrival_time = datetime.fromisoformat(arrival_time)
    arrival_time = arrival_time.strftime("%Y-%m-%d %H:%M:%S")
    result += f"\n\nHere is some information about the return train: \ndeparture time: {depart_time}, arrival time: {arrival_time}, duration: {duration}"  

  return result

def scrape(destination :str, 
           departure :str, 
           date :str, 
           time :str, 
           return_ticket :bool, 
           return_time :str, 
           return_date :str
           ) -> str:

  day, month, year = date.split("/")
  hour, minute, _  = time.split(":")
  ticket_query = TicketQuery(departure, destination, year, month, day, hour, minute)
  
  return_query = None
  if return_ticket == True :
    r_day, r_month, r_year = return_date.split("/")
    r_hour, r_minute, _  = return_time.split(":")
    return_query = ReturnQuery(r_day, r_month, r_year, r_hour, r_minute)

  try:
    result, url = get_ticket_info(ticket_query, return_query)
    return scrape_data(result) + f"\n\nHere is a link to book those tickets: \n{url}"
  except Exception as e:
    return f"Sorry, I was unable to find any tickets for that journey"

def test_harness():
  print(scrape("NRW", "LST", "19/05/2024", "15:00:00", True, "18:00:00", "24/05/2024"))

if __name__ == "__main__":
  test_harness()

