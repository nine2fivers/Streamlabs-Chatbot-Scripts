import clr
import sys
import json
import os
import ctypes
import codecs
import time

ScriptName = "Trivia Minigame"
Website = "http://www.github.com/Bare7a/Streamlabs-Chatbot-Scripts"
Description = "Trivia Minigame for Streamlabs Bot"
Creator = "Bare7a"
Version = "1.2.8"

configFile = "config.json"
questionsFile = "questions.txt"
settings = {}
path = ""

questionsList = []
currentQuestion = ""
currentAnswers = []
currentReward = 0

resetTime = 0


def ScriptToggled(state):
	return

def Init():
	global questionsList, settings, path 

	path = os.path.dirname(__file__)
	try:
		with codecs.open(os.path.join(path, configFile), encoding='utf-8-sig', mode='r') as file:
			settings = json.load(file, encoding='utf-8-sig')
	except:
		settings = {
			"liveOnly": True,
			"permission": "Everyone",
			"ignoreCaseSensitivity": True,
			"separator": "##",  
			"minReward": 1,
			"maxReward": 10,
			"questionInterval": 10,			
			"responseAnnouncement": "Win $reward $currency by answering: $question",
			"responseWon": "$user answered the question first - $answer and won $reward $currency!"
		}

	questionsLocation = os.path.join(path, questionsFile)

	try: 
		with codecs.open(questionsLocation, encoding="utf-8-sig", mode="r") as file:
			questionsList = [[word.strip() for word in line.split(settings["separator"])] for line in file if line.strip()]
	except:
		if os.path.isfile(questionsLocation): 
			questionsList = ["If you see this message save the file as UTF-8"]
		else: 
			with codecs.open(questionsLocation, encoding="utf-8-sig", mode="w+") as file:
				file.write('What color is the grass? ' + settings['separator'] + ' green\r\n');
				file.write('What is between 1 and 3? ' + settings['separator'] + ' 2 ' + settings['separator'] + ' two')
				questionsList = [['Open your "questions.txt" file to add your own questions', '_']]
	
	return

def Execute(data):
	global currentQuestion, currentAnswers, currentReward

	if data.IsChatMessage() and ((data.Message in currentAnswers) or (settings["ignoreCaseSensitivity"] and (data.Message.lower() in [a.lower() for a in currentAnswers]))) and Parent.HasPermission(data.User, settings["permission"], "") and ((settings["liveOnly"] and Parent.IsLive()) or (not settings["liveOnly"])):
		userId = data.User			
		username = data.UserName

		Parent.AddPoints(userId, username, currentReward)

		outputMessage = settings["responseWon"]	

		outputMessage = outputMessage.replace("$user", username)
		outputMessage = outputMessage.replace("$question", currentQuestion)
		outputMessage = outputMessage.replace("$answer", data.Message.title())
		outputMessage = outputMessage.replace("$reward", str(currentReward))
		outputMessage = outputMessage.replace("$currency", Parent.GetCurrencyName())

		currentQuestion = ""
		currentAnswers = []
		currentReward = 0

		Parent.SendStreamMessage(outputMessage)
	return

def ReloadSettings(jsonData):
	Init()
	return

def OpenReadMe():
	location = os.path.join(os.path.dirname(__file__), "README.txt")
	os.startfile(location)
	return

def OpenQuestionsFile():
	location = os.path.join(os.path.dirname(__file__), questionsFile)
	os.startfile(location)
	return


def Tick():
	global questionsList, resetTime, currentQuestion, currentAnswers, currentReward

	if (settings["liveOnly"] and Parent.IsLive()) or (not settings["liveOnly"]):
		currentTime = time.time()

		if(currentTime >= resetTime):
			resetTime = currentTime + (settings["questionInterval"] * 60)
			outputMessage = settings["responseAnnouncement"]

			randomQuestion = questionsList.pop(Parent.GetRandom(0, len(questionsList)))
			currentQuestion = randomQuestion.pop(0) 
			currentAnswers = randomQuestion

			if len(questionsList) == 0:
				try: 
					with codecs.open(os.path.join(path, questionsFile), encoding="utf-8-sig", mode="r") as file:
						questionsList = [[word.strip() for word in line.split(settings["separator"])] for line in file if line.strip()]
				except:
					questionsList = [["If you see this message save the file as UTF-8","Error"]]

			currentReward = Parent.GetRandom(settings["minReward"], settings["maxReward"])
			outputMessage = outputMessage.replace("$question", currentQuestion)
			outputMessage = outputMessage.replace("$reward", str(currentReward))
			outputMessage = outputMessage.replace("$currency", Parent.GetCurrencyName())

			Parent.SendStreamMessage(outputMessage)
	return
