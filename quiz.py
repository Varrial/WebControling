import os
import random

from questions_helper import load_questions


def clear_console():
    os.system('clear')


def get_random_question(ques):
    try:
        chosen = random.randint(1, len(ques)) - 1
        ret = ques.pop(chosen)
    except IndexError:
        exit()
    except ValueError:
        exit()

    return ret


if __name__ == '__main__':
    questions = load_questions()

    good_ans = 0
    all_ans = 0

    while True:
        que = get_random_question(questions)
        print(que['question'])

        answers = dict()
        for num, answer in enumerate(que['answers']):
            num = num + 1

            answers[num] = answer
            print(f"\t{num}. {answer}")

        output = None
        while output not in answers:
            try:
                output = int(input("odp: "))
            except ValueError:
                pass

        clear_console()

        if answers[output] == que['correct'][0]:
            print('tak')
            good_ans += 1
        else:
            print(f"nie - {que['correct'][0]}")
            questions.append(que)

        all_ans += 1

        print(f'{good_ans}/{all_ans}\n\n\n')




