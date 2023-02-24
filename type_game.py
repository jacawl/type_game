from pynput import keyboard
from termcolor import colored
import random
import os
import time
import pandas as pd
from datetime import date

letter_index = 500
incorrect_key = False
key_release_arr = []
line_arr = []
underscore_arr = []
line_index = 0
num_incorrect_keys = 0
total_keys = 0
total_words = 0
working_directory = os.getcwd()

os.system('color')

def getRandomNums(length):
    rand1 = 0
    rand2 = 0
    rand3 = 0
    while rand1 == rand2 or rand2 == rand3 or rand1 == rand3:
        rand1 = random.randrange(0,length)
        rand2 = random.randrange(0,length)
        rand3 = random.randrange(0,length)
    return [rand1, rand2, rand3]

def init_prompt():
    global line_arr
    global total_keys
    global underscore_arr
    global total_words

    prompt = open('{}'.format('C:\Scripts\\type_game\\prompt'), "r").readlines()
    sentences = []
    for i in range(len(prompt)):
        sentences.append(prompt[i].rstrip().lower())
    nums = getRandomNums(len(sentences))
    for i in range(len(nums)):
        line_arr.append(sentences[nums[i]])
        underscore_arr.append(sentences[nums[i]].replace(' ', '_'))
        sentence_len = len(sentences[nums[i]])
        total_keys += sentence_len
        total_words += len(sentences[nums[i]].split())

    line_arr.append('')
    underscore_arr.append('')
    print(prompt, flush=True)
    

# clear terminal for cleaner look
def cls():
    os.system('cls' if os.name=='nt' else 'clear')

def print_string():
    # initiate global vars
    global letter_index
    global num_incorrect_keys
    global incorrect_key
    cls()

    # loop over keys releases and compare to string to find first wrong key index
    for i in range(len(key_release_arr)):
        if i == len(underscore_arr[line_index]):
            break
        elif key_release_arr[i] != underscore_arr[line_index][i]:
            # set index of incorrect key and do not change index until user string fixes error
            if not incorrect_key:
                letter_index = i
                incorrect_key = True
                num_incorrect_keys += 1

    # if user string is equal to eaqual length match string set index and incorrect key to defaults
    if (''.join(map(str, key_release_arr))) == underscore_arr[line_index][0:len(key_release_arr)] and incorrect_key:
        incorrect_key = False
        letter_index = 500

    # set print format for errors
    if letter_index == 500:
        print('\n\n\n\n\n\n\n\n\n\n\n\n')
        print("\t{}{}".format(colored(''.join(map(str, key_release_arr)), 'green'), colored(line_arr[line_index][len(key_release_arr):len(line_arr[line_index])], 'white')))
    else:   
        correct_string = key_release_arr[0:letter_index]
        correct_string = ''.join(map(str, correct_string))
        incorrect_string = key_release_arr[letter_index:]
        incorrect_string = ''.join(map(str, incorrect_string))
        max_length = len(key_release_arr)
        if len(key_release_arr) > len(line_arr[line_index]):
            max_length == len(line_arr[line_index])
        print('\n\n\n\n\n\n\n\n\n\n\n\n')
        print("\t{}{}{}".format(colored(''.join(map(str, correct_string)), 'green'), colored(incorrect_string, 'red'), colored(line_arr[line_index][len(key_release_arr):len(line_arr[line_index])], 'white')))

def on_release(key):
    global key_release_arr
    global letter_index
    global line_index
    global incorrect_key

    try:
        key_release_arr.append(key.char)
        print_string()
        # if user completed matching strings
        if (''.join(map(str, key_release_arr))) == underscore_arr[line_index]:
            letter_index == 500
            line_index += 1
            key_release_arr = []
            incorrect_key = False
            print_string()
            if line_index == 3:
                return(False)       
    except:
        if key == keyboard.Key.backspace:
            if len(key_release_arr) < 1:
                print_string()
            else:
                key_release_arr.pop()
            print_string()
        elif key == keyboard.Key.space:
            if len(key_release_arr) < 1:
                print_string()
            else:
                key_release_arr.append('_')
            print_string()
        elif key == keyboard.Key.esc:
            # Stop listener
            return False
        elif (''.join(map(str, key_release_arr))) == underscore_arr[line_index]:
            line_index += 1
            key_release_arr = []
            letter_index = 0
            incorrect_key = False
            print_string()
            if line_index == 3:
                return(False)  
    

# Collect events until released
with keyboard.Listener(
        on_release=on_release) as listener:
    init_prompt()
    cls()
    print_string()
    # Calculate the start time
    start = time.time()
    listener.join()

# Calculate the end time and time taken
end = time.time()
length = end - start
wpm = total_words / (length/60)
accuracy = ((total_keys - num_incorrect_keys) / total_keys) * 100

# Get performance from previous entires
history_df = pd.read_feather("{}".format('C:\Scripts\\type_game\entries.feather'))
avg_wpm = history_df.loc[:, 'wpm'].mean()
avg_acc = history_df.loc[:, 'acc'].mean()

# print results
print("\t Result:    {} wpm    /    {}% accuracy".format(round(wpm, 2),round(accuracy, 2)))
print("\tAverage:    {} wpm    /    {}% accuracy".format(round(avg_wpm, 2),round(avg_acc, 2)))
print("\n\n\n\n\n\n\n")
print(history_df.tail(5))
print("\n\n\n\n\n\n\n")

# write performance to file
today = date.today()
history_df.loc[len(history_df.index)] = [today, wpm, accuracy]
history_df.to_feather("{}".format('C:\Scripts\\type_game\entries.feather'))

