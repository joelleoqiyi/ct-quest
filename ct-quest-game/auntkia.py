import glob
import pygame
import pprint
import csv
import difflib
from decouple import config
import pymongo

SRV = config("SRV")
client = pymongo.MongoClient(SRV)
user = client.game.user
uid = None

while True:
  query = {
    "username": "",
    "password": ""
  }

  action = input("Do you want to LOGIN_QUERY (L) or sign up (S)? ")

  query["username"] = input("Username: ")
  query["password"] = input("Password: ")

  if not query["username"] or not query["password"]:
      continue

  uid = user.find_one(query, {"_id": 1})

  if action.upper() == "L":
    if uid: 
      print("\nLogin successful\n\n")
      break   

    print("\nWrong Username and/or Password\n\n")
    continue

  elif action.upper() == "S":
    if uid:
      print("\nChoose another username and password\n\n")
      continue

    signup_query = {**query, "games": []}
    try: 
      user.insert_one(signup_query)
      print("\nSign up successful\n\n")
    except:
      print("\nSomething went wrong\n\n")
      continue
    break


# game logic
if uid:
  print("Displaying Board....")

  pp = pprint.PrettyPrinter(indent=4)

  pygame.init()

  WIDTH = 1200
  HEIGHT = 800
  SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

  white = (255, 255, 255)
  black = (0, 0, 0)
  red = (128, 0, 0)

  pygame.display.set_caption('Aunt Kia Loader')

  font = pygame.font.Font('freesansbold.ttf', 20)

  auntkia_path = glob.glob('./*.txt')[0]
  alloc_path = glob.glob('./*.csv')[0]

  auntkia = open(auntkia_path, 'r')
  alloc = open(alloc_path, 'r')
  alloc_list = list(csv.reader(alloc, delimiter=','))

  questions = []
  answers = []

  question = ""
  answer = ""
  check = True
  for line in auntkia:
      if line.rstrip():
          if line[0] == '#':
              if not check and answer != "":
                  answers.append(answer)
                  answer = ""
              question += line
          else:
              if question != "":
                  questions.append(question)
                  question = ""
              answer += line
              check = False

  answers.append(answer)

  right_answers = []
  answer_index = 0
  total_time = 0

  for i in range(len(questions)):
      SCREEN.fill(white)
      text = questions[i].split('\n')
      label = []
      for line in text:
          label.append(font.render(line, True, black, white))

      for line in range(len(label)):
          SCREEN.blit(label[line],(100, 100 + (line * 20)+(15 * line)))

      start_time = pygame.time.get_ticks()

      answer_lines = answers[i].split('\n')

      pygame.display.update()

      for line in answer_lines:
          line = line.strip()
          check = False
          index = 0
          user_ans = ''
          while True:
              # Monitor keyboard and mouse events
              for event in pygame.event.get():
                  if event.type == pygame.KEYDOWN:
                      # Judge whether the current input is correct
                      if event.key == pygame.K_RIGHT:
                          check = True
                          break
                      elif event.key == pygame.K_RETURN:
                          ratio = difflib.SequenceMatcher(None, user_ans, line).ratio()
                          if ratio > 0.8:
                              right_answers.append(answer_index)
                          if answer_index < len(alloc_list) - 1:
                              answer_index += 1
                          user_ans = ''
                          check = True
                          break
                      elif event.key == pygame.K_BACKSPACE:
                          index -= 1
                          user_ans = user_ans[:-1]
                          
                      else:
                          index += 1
                          user_ans += event.unicode

                      SCREEN.fill(white)
                      for bruh in range(len(label)):
                          SCREEN.blit(label[bruh],(100, 100 + (bruh * 20)+(15 * bruh)))
                      txt_surface = font.render(user_ans, True, black)
                      SCREEN.blit(txt_surface, (50, 500))
                      pygame.display.flip()
              if check:
                  end_time = pygame.time.get_ticks()
                  current_time = end_time - start_time
                  total_time += current_time
                  time = f'Completed in {str(current_time)}ms with accuracy {ratio}, expected time {int(alloc_list[answer_index][6]) * 1000}ms. Press right to continue.'
                  SCREEN.fill(white)
                  txt_surface = font.render(time, True, black)
                  SCREEN.blit(txt_surface, (50, HEIGHT // 2))
                  pygame.display.flip()
                  break
  
  keys = ['Decomposition','Abstraction', 'Pattern Recognition', 'Algorithmic Thinking', 'Learning Behaviours', 'Metacognition']
  values = [0,0,0,0,0,0]

  for i in right_answers:
      values = [int(val1) + int(val2) for val1, val2 in zip(values, alloc_list[i][:-1])]

  document = {
    "name": auntkia_path[2:-4],
    **dict(zip(keys, values))
  }

  print("\n\nHere are your scores...\n")

  for key in document:
    print(f"You scored {document[key]} for {key} segment.")

  try:
    x = user.update_one({"_id": uid["_id"]}, {"$push": {"games": document}})
    print("\nYour score has been recorded.")
  except:
    print("\nSomething went wrong with recording your score.")
