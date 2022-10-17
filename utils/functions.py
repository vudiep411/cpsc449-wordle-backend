def check_pos_valid_letter(guess_word, correct_word):
    correct_pos = []
    correct_letter_wrong_pos = []
    wrong_letter = []
    for i in range(0, len(correct_word)):
        if guess_word[i] in correct_word and guess_word[i] == correct_word[i]:
            correct_pos.append(guess_word[i])
        elif guess_word[i] in correct_word:
            correct_letter_wrong_pos.append(guess_word[i])
        else:
            wrong_letter.append(guess_word[i])
        
    return {
        'correctPosition' : correct_pos,
        'correctLetterWrongPos': correct_letter_wrong_pos,
        'wrongLetter' : wrong_letter
    }