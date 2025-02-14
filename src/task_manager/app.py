from crewai.flow.flow import Flow, start, router
from litellm import completion
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(prompt):
    response = completion(
        model="gemini/gemini-1.5-flash",
        messages=[{"role": "user", "content": prompt}],
        api_key=GEMINI_API_KEY
    )
    return response["choices"][0]["message"]["content"]  

class FlowRouter(Flow):
    def __init__(self):
        super().__init__()
        self.task = None
        self.subtask = None
        self.result = None
        self.feedback = None
        self.stage = 0 

    @start()
    def task_manager(self):
        print(" Welcome to the Task Manager System!")
        self.task = input(" Enter your task: ")
        self.route_task()  

    @router(condition=lambda self: self.task is not None) 
    def route_task(self):
        agents = ["Planner", "Executor", "Reviewer"]

        if self.stage < len(agents):
            select_agent = agents[self.stage]  
            print(f"Selected Agent: {select_agent}")
            
            if select_agent == "Planner":
                self.planner_agent()
            elif select_agent == "Executor":
                self.executor_agent()
            elif select_agent == "Reviewer":
                self.reviewer_agent()
            
            self.stage += 1  
            self.route_task()  

        else:
            print(" Task flow complete!")

    def planner_agent(self):
        print("Planner agent is breaking down the task...")
        self.subtask = ask_gemini(f"Break down the task: {self.task}")   
        print(f" Subtask: {self.subtask}")

    def executor_agent(self):
        print(" Executor Agent is executing the task...")
        self.result = ask_gemini(f"Execute the task: {self.task}")
        print(f" Execution Result: {self.result}")

    def reviewer_agent(self):
        print(" Reviewer Agent is reviewing the task...")
        self.feedback = ask_gemini(f"Review the task: {self.task}")
        print(f" Feedback: {self.feedback}")

def kickoff():
    obj = FlowRouter()
    obj.task_manager()  

def plot():
    obj = FlowRouter()
    obj.plot() 

kickoff()
