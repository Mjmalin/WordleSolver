import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import re
import sys

all_solutions_list = list()
grey_list = list()
yellow_list = list()
green_list = list()
counts = dict()

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# import all possible Wordle solutions into a list
html = urllib.request.urlopen("https://gist.githubusercontent.com/cfreshman/a03ef2cba789d8cf00c08f767e0fad7b/raw/45c977427419a1e0edee8fd395af1e0a4966273b/wordle-answers-alphabetical.txt", context=ctx).read()
soup = BeautifulSoup(html, 'html.parser')
for lines in soup :
    x = lines.rstrip()
    y = x.split()
    for all_solutions in y :
        all_solutions_list.append(all_solutions)

# import all past Wordle answers, format them into lower case
html = urllib.request.urlopen("https://www.rockpapershotgun.com/wordle-past-answers", context=ctx).read()
soup_two = BeautifulSoup(html, 'html.parser')

words = soup_two.find_all("ul", class_="inline")
uppercase_past_solutions_list = re.findall("<li>([A-Z]+)", str(words))
past_solutions_list = [lowercase_past_solutions.lower() for lowercase_past_solutions in uppercase_past_solutions_list]

# subtract all past Wordle answers from all possible Wordle solutions
remaining_solutions = [d for d in all_solutions_list if d not in past_solutions_list]

# continue asking for Wordle entries unless there is one word left
while True:
    if len(remaining_solutions) < 2:
        sys.exit()

    # ask for green letters
    while True:
        green = input("Enter a green letter (simply press return if none/no more): ")
        if green == "":
            break
        green_list.append(green)

    # ask for positions, subtract words with no green letters in that position
        gpos = input("Enter position of letter (options are 1 - 5): ")
        gp = int(gpos)
        green_letter_position = gp - 1
        remaining_solutions = [j for j in remaining_solutions if j[green_letter_position] == green]
        
    # ask for yellow letters
    while True:
        yellow = input("Enter a yellow letter (simply press return if none/no more): ")
        if yellow == "":
            break
        yellow_list.append(yellow)

    # ask for positions, subtract words with yellow letters in that position
        ypos = input("Enter position of letter (options are 1 - 5): ")
        yp = int(ypos)
        yellow_letter_position = yp - 1
        remaining_solutions = [g for g in remaining_solutions if g[yellow_letter_position] != yellow]

    # subtract words with none of the yellow letters 
    remaining_solutions = [b for b in remaining_solutions if all(a in b for a in yellow_list)]
    
    # ask for grey letters, add them to grey_list 
    while True:
        grey = input("Enter a grey letter (simply press return if none/no more): ")
        if grey == "":      
            break  
        grey_list.append(grey)
        
    # subtract everything in yellow_list and green_list from grey_list, to deal with guesses like "PUPPY," that might produce a yellow P and two grey P's, for instance
    grey_list = [gg for gg in grey_list if gg not in yellow_list]
    grey_list = [ii for ii in grey_list if ii not in green_list]
                
    # subtract all words with grey letters
    remaining_solutions = [e for e in remaining_solutions if all(f not in e for f in grey_list)]
    print("Remaining possible solutions:", remaining_solutions)

    # dictionary that will hold color combination results of all possible guesses tested against all possible solutions
    all_guesses_solutions_dict = {}

    # for all possible Wordle entries (potential guesses), create a dictionary
    for guess in all_solutions_list:
        all_guesses_solutions_dict[guess] = {}

        # dictionary to keep track of the counts of each letter in the solution
        for solution in remaining_solutions:
            solution_counts = {}
            for solution_letter in solution:
                solution_counts[solution_letter] = solution_counts.get(solution_letter, 0) + 1

            # lists to hold the results
            all_guesses_solutions_dict[guess][solution] = []

        # first pass: identify greens and update solution counts
            for guess_letter, solution_letter in zip(guess, solution):
                if guess_letter == solution_letter:
                    all_guesses_solutions_dict[guess][solution].append('green')
                    solution_counts[guess_letter] -= 1
                else:
                    all_guesses_solutions_dict[guess][solution].append(None)  # placeholder for non-green matches

            # second pass: identify yellows and greys, respecting green matches
            for i, guess_letter in enumerate(guess):
                if all_guesses_solutions_dict[guess][solution][i] is None:  # only process if not already marked as green
                    if guess_letter in solution_counts and solution_counts[guess_letter] > 0:
                        all_guesses_solutions_dict[guess][solution][i] = 'yellow'
                        solution_counts[guess_letter] -= 1
                    else:
                        all_guesses_solutions_dict[guess][solution][i] = 'grey'

    # combine colors for each solution into single strings so they are more easily compared
    for guess in all_guesses_solutions_dict:
        for wordcolors in all_guesses_solutions_dict[guess]:
            joinlist = ''.join(all_guesses_solutions_dict[guess][wordcolors])
            all_guesses_solutions_dict[guess][wordcolors] = joinlist

    # compare strings of colors, count and track number of unique strings of colors 
    average_group_dict = {} # dictionary that will hold all guesses and average group size for each
    for guess in all_guesses_solutions_dict: 
        countsum = 0
        colorcounts = {}

        for solution in all_guesses_solutions_dict[guess]:
            colorcounts[all_guesses_solutions_dict[guess][solution]] = colorcounts.get(all_guesses_solutions_dict[guess][solution], 0) + 1

        # calculate the average size of groups of unique strings of colors    
        floatlength = float(len(colorcounts))

        for all_guesses_solutions_dict[guess][solution], count in colorcounts.items():
            countsum = countsum + float(count)
            averagegroups = (countsum/floatlength) # average of counts, represents average size of groups
            average_group_dict[guess] = averagegroups
            
        colorcounts.clear()
        
    if len(remaining_solutions) < 2:
        sys.exit()

    # print the recommended guesses, in other words, the guesses that produced smallest average group size
    min_value = min(average_group_dict.values()) # min_value represents the smallest average group size
    best_guess_list = [ka for ka,va in average_group_dict.items() if va == min_value] # we use best_guess_list if the best guess is not a possible solution
    solution_best_guess_list = [xa for xa in best_guess_list if xa in remaining_solutions] # we use solution_best_guess_list if the best guess is a possible solution
    if not solution_best_guess_list:
        print("Recommended next guess(es):", best_guess_list, "Smallest average group size: ", min_value) 
    else:
        print("Recommended next guess(es):", solution_best_guess_list, "Smallest average group size: ", min_value)
    
    # prepare for next Wordle entry by clearing lists
    counts.clear()
    green_list.clear()
    yellow_list.clear()
    grey_list.clear()
