#   Author information
#   name: Vu Diep    
#   email: vdiep8@csu.fullerton.edu
#
#   This file
#   File name: queries.py
#   Purpose: functions needed for wordle.py


# Check the valid guessed word letter and valid postion
# guess_word -> str, user's guess_word
# correct_word -> str, correct secret word from database
# return dict -> {
#   correctPosition -> Array of correct letters in the correct spot
#   correctLetterWrongPos -> Array of correct letters in the wrong spot
#   wrongLetter -> Array of wrong letters
# }
def check_pos_valid_letter(guess_word, correct_word):
    correct_pos = []
    correct_letter_wrong_pos = []
    wrong_letter = []
    for i in range(0, len(correct_word)):
        if guess_word[i] in correct_word and guess_word[i] == correct_word[i]:
            correct_pos.append(i)
        elif guess_word[i] in correct_word:
            correct_letter_wrong_pos.append(i)
        else:
            wrong_letter.append(i)
        
    return {
        'correctPositionIdx' : correct_pos,
        'correctLetterWrongPosIdx': correct_letter_wrong_pos,
        'wrongLetterIdx' : wrong_letter
    }