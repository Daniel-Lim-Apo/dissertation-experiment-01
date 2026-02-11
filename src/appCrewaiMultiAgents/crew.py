import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from langchain_ollama import OllamaLLM

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

llm_config1 = OllamaLLM(model="llama3", base_url="http://ollama:11434") 

@CrewBase
class PrivacyRareEventCrew():
	"""PrivacyRareEvent crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'


	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def writer(self) -> Agent:
		return Agent(
			config=self.agents_config['writer'],
			llm = llm_config1,
   			verbose=True
		)
  
	@agent
	def writerparagraph(self) -> Agent:
		return Agent(
			config=self.agents_config['writerparagraph'],
			llm = llm_config1,
   			verbose=True
		)
  
	@agent
	def writereventtopic(self) -> Agent:
		return Agent(
			config=self.agents_config['writereventtopic'],
			llm = llm_config1,
   			verbose=True
		)
  

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def summarize_task(self) -> Task:
		return Task(
			config=self.tasks_config['summarize_task'],
		)

	@task
	def summarize_paragraph_task(self) -> Task:
		return Task(
			config=self.tasks_config['summarize_paragraph_task'],
		)
  
	@task
	def summarize_phrases_task(self) -> Task:
		return Task(
			config=self.tasks_config['summarize_phrases_task'],
		)
  
	@crew
	def crew(self) -> Crew:
		"""Creates the PrivacyRareEvent crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
