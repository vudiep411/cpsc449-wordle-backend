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
    letter_freq = {}
    for a in correct_word:
        if a in letter_freq:
            letter_freq[a] += 1
        else:
            letter_freq[a] = 1

    correct_pos = []
    correct_letter_wrong_pos = []
    wrong_letter = []
    for i in range(0, len(correct_word)):
        if guess_word[i] in correct_word and guess_word[i] == correct_word[i]:
            correct_pos.append(i)
            letter_freq[guess_word[i]] -= 1

        elif guess_word[i] in correct_word and letter_freq[guess_word[i]] > 0:
            correct_letter_wrong_pos.append(i)
            letter_freq[guess_word[i]] -= 1
            
        else:
            wrong_letter.append(i)
        
    return {
        'correctPosition' : correct_pos,
        'correctLetterWrongPos': correct_letter_wrong_pos,
        'wrongLetter' : wrong_letter
    }