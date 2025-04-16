from crewai import Agent, Crew, Process, Task 
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI
from writeabook.types import BookOutline
 

@CrewBase
class OutlineCrew:
  """Book Outline Crew"""
  agents_config="config/agents.yaml"
  task_config="config/tasks.yaml"
  llm = ChatOpenAI(model="gpt-4o-mini")
  
  @agent
  def researcher(self)-> Agent:
    search_tools = SerperDevTool()
    return Agent(
      config=self.agents_config["researcher"],
      tools=[search_tools],
      llm=self.llm,
      cache= True,
      verbose=True
    )
    
  @agent
  def outliner(self)-> Agent:
    return Agent(
      config=self.agents_config["outliner"],
      llm=self.llm,
      cache= True,
      verbose=True
    )    
    
  @task
  def research_topic(self) ->Task:
    return Task(
      config=self.tasks_config["research_topic"]
    )   
    
  @task
  def generate_outline(self) ->Task:
    return Task(
      config=self.tasks_config["generate_outline"],
      output_pydantic=BookOutline
    )   
      
  @crew
  def crew(self)->Crew:
    """Creates the Book Outline Crew"""
    return Crew(
      agents=self.agents,
      tasks=self.tasks,
      process=Process.sequential,
      verbose=True
    )