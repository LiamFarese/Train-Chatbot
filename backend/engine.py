from experta import *

# Define the Facts
class UserInput(Fact):
    text = Field(str, default="")

class Person(Fact):
    name = Field(str, default=None)

class Age(Fact):
    age = Field(int, default=None)

# Define the Rules
class GreetUser(KnowledgeEngine):
    @Rule()
    def extract_details(self):
        self.declare(UserInput(text=input("Please enter your name and age (e.g., 'John 30'): ")))

    @Rule(UserInput(text=MATCH.text))
    def process_input(self, text):
        tokens = text.split()
        if len(tokens) >= 2:
            self.declare(Person(name=tokens[0]))
            self.declare(Age(age=int(tokens[1])))

    @Rule(Person(name=MATCH.name), Age(age=MATCH.age))
    def greet_user(self, name, age):
        print(f"Hello, {name}, you are {age} years old!")

# Load the Knowledge Base and Run the Engine
engine = GreetUser()
engine.reset()
engine.run()