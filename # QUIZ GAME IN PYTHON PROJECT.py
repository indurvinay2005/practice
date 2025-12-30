# QUIZ GAME IN PYTHON

def new_game():
    
    guesses = []
    correct_guesses = 0
    question_num = 1
    
    for key in questions:
        print("--------------------------------------------")
        print(key)
        for i in options[question_num-1]:
            print(i)
        guess = input("Enter an option(A, B, C, D ): ")
        guess = guess.upper()
        guesses.append(guess)
        
    check_guesses = check_answer(questions.get(key), guess)
    question_num += 1
        
    display_score(correct_guesses, guesses)
        
            
#-------------------------------------------
def check_answer(answer, guess):
    
    if answer == guess:
        print("CORRECT!")
        return 1
        
#-------------------------------------------
def display_score(correct_guesses, guesses):
    print("---------------------------")
    print("RESULTS")
    print("------------------------")
    
    print("Answers: ", end="")
    for i in questions:
        print(questions.get(i), end=" ")
    print()
    
    print("guesses: ", end=" ")
    for i in guesses:
        print(i, end="")
    print()
    
    score = int(correct_guesses/len(questions) +100)
    print("Your score is : " +str(score)+ "%")
#-------------------------------------------
def play_game():
    
    response = input("Do you want to play again? (yes or No): ")
    response = response.upper()
    
    if response == "YES":
        return True
    else:
        return False    
#-------------------------------------------
questions = {
    "who created python? ": "A",
    "Which year python was introduced? ": "B",
    "python is tributed to which comedy group? ": "C",
    "is the Earth round? " : "A",
}

options = [["A. Guido van rossum", "B. Elon musk", "C. Bill gates", "D. mark zuckerbrug"],
          ["A. 1989", "B. 1991", "c. 2000", "D. 2016"],
          ["A. Lonely island", "B.smosh", "C. monty python", "D. snl"],
          ["A. True", "B. False", "C. smoetimes", "D.whats Earth"]]

new_game()

while play_game():
    new_game()
    
print("Byeeee!")