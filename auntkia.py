import glob
import pygame
import pprint
import csv
import difflib

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
print(questions)

right_answers = []
answer_index = 0

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
                time = f'Completed in {str(end_time - start_time)}ms with accuracy {ratio}, expected time {int(alloc_list[answer_index][6]) * 1000}ms. Press right to continue.'
                SCREEN.fill(white)
                txt_surface = font.render(time, True, black)
                SCREEN.blit(txt_surface, (50, HEIGHT // 2))
                pygame.display.flip()
                break

total = 0
print(right_answers)
for i in right_answers:
    for j in alloc_list[i][:-1]:
        total += int(j)

print(f"Your score is {total}")
