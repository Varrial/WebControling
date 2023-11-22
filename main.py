from time import sleep

from old_question_collector import load_questions, save_questions
from question_collector import QuestionCollector

if __name__ == '__main__':
    while True:
        questions = load_questions()

        collector = QuestionCollector(questions)
        collector.login_to_cez2()

        # collector.learn_from_solved_exams()
        collector.process_exam()

        save_questions(collector.get_known_questions())
        del collector

        sleep(5.1*60)
