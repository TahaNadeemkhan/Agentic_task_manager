import streamlit as st
from crewai.flow.flow import Flow, start, router, listen
from litellm import completion
from dotenv import load_dotenv
import os

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_gemini(prompt):
    try:
        response = completion(
            model="gemini/gemini-1.5-flash",
            messages=[{"role": "user", "content": prompt}],
            api_key=GEMINI_API_KEY
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Error calling Gemini API: {str(e)}")
        return None

class FlowRouter(Flow):
    def __init__(self):
        super().__init__()
        self.task = None
        self.subtask = None
        self.result = None
        self.feedback = None
        self.stage = 0
        
    def process_task(self, task):
        if not GEMINI_API_KEY:
            st.error("Please set your GEMINI_API_KEY in the .env file")
            return None
            
        self.task = task
        agents = ["Planner", "Executor", "Reviewer"]
        results = {}
        
        try:
            for agent in agents:
                with st.spinner(f"{agent} is working..."):
                    if agent == "Planner":
                        self.subtask = ask_gemini(f"Break down the task: {self.task}")
                        if self.subtask:
                            results['planner'] = self.subtask
                        
                    elif agent == "Executor":
                        if self.subtask:
                            self.result = ask_gemini(f"Execute the task: {self.subtask}")
                            if self.result:
                                results['executor'] = self.result
                        
                    elif agent == "Reviewer":
                        if self.result:
                            self.feedback = ask_gemini(f"Review the task: {self.result}")
                            if self.feedback:
                                results['reviewer'] = self.feedback
                    
            return results
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            return None

def main():
    try:
        st.set_page_config(page_title="Task Manager System", page_icon="✅")
    except:
        # Handle case where set_page_config was already called
        pass
    
    st.title("Task Manager System")
    st.write("Welcome! Enter your task below to get started.")
    
    # Initialize session state
    if 'results' not in st.session_state:
        st.session_state.results = None
    
    # Task input
    task = st.text_input("Enter your task:")
    
    if st.button("Process Task"):
        if task:
            flow = FlowRouter()
            results = flow.process_task(task)
            if results:
                st.session_state.results = results
        else:
            st.warning("Please enter a task first")
            
    # Display results
    if st.session_state.results:
        st.subheader("Task Processing Results")
        
        with st.expander("Planner's Breakdown", expanded=True):
            st.write("🔍 Task Breakdown:")
            st.write(st.session_state.results.get('planner', 'No results available'))
            
        with st.expander("Executor's Result", expanded=True):
            st.write("⚙️ Execution Result:")
            st.write(st.session_state.results.get('executor', 'No results available'))
            
        with st.expander("Reviewer's Feedback", expanded=True):
            st.write("📝 Review Feedback:")
            st.write(st.session_state.results.get('reviewer', 'No results available'))

if __name__ == "__main__":
    main()