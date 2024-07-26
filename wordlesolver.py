import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import ssl
import re
import sys

lst = list()
greylist = list()
yellowlist = list()
greenlist = list()
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
    for za in y :
        lst.append(za)

# import all past Wordle answers, format them into lower case
html = urllib.request.urlopen("https://www.rockpapershotgun.com/wordle-past-answers", context=ctx).read()
sp = BeautifulSoup(html, 'html.parser')

words = sp.find_all("ul", class_="inline")
a = re.findall("<li>([A-Z]+)", str(words))
c = [b.lower() for b in a]

# subtract all past Wordle answers from all possible Wordle solutions
l3 = [d for d in lst if d not in c]

# continue asking for Wordle entries unless there is one word left
while True:
    if len(l3) < 2:
        sys.exit()

    # ask for green letters
    while True:
        green = input("Enter a green letter (simply press return if none/no more): ")
        if green == "":
            break
        greenlist.append(green)

    # ask for positions, subtract words with no green letters in that position
        gpos = input("Enter position of letter (options are 1 - 5): ")
        gp = int(gpos)
        gpi = gp - 1
        l3 = [j for j in l3 if j[gpi] == green]
        
    # ask for yellow letters
    while True:
        yellow = input("Enter a yellow letter (simply press return if none/no more): ")
        if yellow == "":
            break
        yellowlist.append(yellow)

    # ask for positions, subtract words with yellow letters in that position
        ypos = input("Enter position of letter (options are 1 - 5): ")
        yp = int(ypos)
        ypi = yp - 1
        l3 = [g for g in l3 if g[ypi] != yellow]

    # subtract words with none of the yellow letters 
    l3 = [h for h in l3 if all(i in h for i in yellowlist)]
    
    # ask for grey letters, add them to greylist 
    while True:
        grey = input("Enter a grey letter (simply press return if none/no more): ")
        if grey == "":      
            break  
        greylist.append(grey)
        
    # subtract everything in yellowlist and greenlist from greylist, to deal with guesses like "PUPPY," that might produce a yellow P and two grey P's, for instance
    greylist = [gg for gg in greylist if gg not in yellowlist]
    greylist = [ii for ii in greylist if ii not in greenlist]
                
    # subtract all words with grey letters
    l3 = [e for e in l3 if all(f not in e for f in greylist)]
    print("Remaining possible solutions:", l3)

    # dictionary that will hold solutions:list of results as key:value pairs
    ya = {}

    # for all possible Wordle entries (potential guesses), create a dictionary
    for guess in lst:
        ya[guess] = {}

        # dictionary to keep track of the counts of each letter in the solution
        for solution in l3:
            solution_counts = {}
            for sletter in solution:
                solution_counts[sletter] = solution_counts.get(sletter, 0) + 1

            # lists to hold the results
            ya[guess][solution] = []

        # first pass: identify greens and update solution counts
            for guess_letter, solution_letter in zip(guess, solution):
                if guess_letter == solution_letter:
                    ya[guess][solution].append('green')
                    solution_counts[guess_letter] -= 1
                else:
                    ya[guess][solution].append(None)  # placeholder for non-green matches

            # second pass: identify yellows and greys, respecting green matches
            for i, guess_letter in enumerate(guess):
                if ya[guess][solution][i] is None:  # only process if not already marked as green
                    if guess_letter in solution_counts and solution_counts[guess_letter] > 0:
                        ya[guess][solution][i] = 'yellow'
                        solution_counts[guess_letter] -= 1
                    else:
                        ya[guess][solution][i] = 'grey'

    # combine colors for each solution into single strings so they are more easily compared
    for z in ya:
        for wordcolors in ya[z]:
            joinlist = ''.join(ya[z][wordcolors])
            ya[z][wordcolors] = joinlist

    # compare strings of colors, count and track number of unique strings of colors 
    solutiondict = {}
    for z in ya: 
        countsum = 0
        colorcounts = {}

        for aa in ya[z]:
            colorcounts[ya[z][aa]] = colorcounts.get(ya[z][aa], 0) + 1

        # calculate the average size of groups of unique strings of colors    
        floatlength = float(len(colorcounts))

        for ya[z][aa], count in colorcounts.items():
            countsum = countsum + float(count)
            averagegroups = (countsum/floatlength) # average of counts, represents average size of groups
            solutiondict[z] = averagegroups
            
        colorcounts.clear()
        
    if len(l3) < 2:
        sys.exit()

    # print the recommended guesses, in other words, the guesses that produced smallest average group size
    # min_value represents the smallest average group size
    min_value = min(solutiondict.values())
    rlist = [ka for ka,va in solutiondict.items() if va == min_value] # we use rlist if the best guess is not a possible solution
    slist = [xa for xa in rlist if xa in l3] # we use slist if the best guess is a possible solution
    # print(solutiondict)
    if not slist:
        print("Recommended next guess(es):", rlist, "Smallest average group size: ", min_value) 
    else:
        print("Recommended next guess(es):", slist, "Smallest average group size: ", min_value)
    
    # prepare for next Wordle entry by clearing lists
    counts.clear()
    greenlist.clear()
    yellowlist.clear()
    greylist.clear()
