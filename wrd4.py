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

# import all past Wordle answers
html = urllib.request.urlopen("https://www.rockpapershotgun.com/wordle-past-answers", context=ctx).read()
sp = BeautifulSoup(html, 'html.parser')

words = sp.find_all("ul", class_="inline")
a = re.findall("<li>([A-Z]+)", str(words))
c = [b.lower() for b in a]

# subtract all past Wordle answers from all possible Wordle solutions
l3 = [d for d in lst if d not in c]
print(l3)

# continue asking for Wordle entries unless there is one word left
while True:
    if len(l3) < 2:
        sys.exit()
        
    # count letters and print amount of each
    for remaining in l3:
        for letters in remaining:
            counts[letters] = counts.get(letters, 0) + 1
    for letters, count in sorted(counts.items(), key=lambda k: k[1], reverse=True):
        print(letters, count)
        
    # ask for green letters
    while True:
        green = input("Enter a green letter: ")
        if green == "":
            break
        if green == "exit":
            sys.exit()
        greenlist.append(green)
        print(greenlist)

    # ask for positions, subtract words with no green letters in that position
        gpos = input("Enter position: ")
        gp = int(gpos)
        gpi = gp - 1
        l3 = [j for j in l3 if j[gpi] == green]
    print(l3)
        
    # ask for yellow letters
    while True:
        yellow = input("Enter a yellow letter: ")
        if yellow == "":
            break
        if yellow == "exit":
            sys.exit()
        yellowlist.append(yellow)
        print(yellowlist)

    # ask for positions, subtract words with yellow letters in that position
        ypos = input("Enter position: ")
        yp = int(ypos)
        ypi = yp - 1
        l3 = [g for g in l3 if g[ypi] != yellow]

    # subtract words with none of the yellow letters 
    l3 = [h for h in l3 if all(i in h for i in yellowlist)]
    print(l3)
    
    # ask for grey letters, subtract all words with grey letters
    while True:
        grey = input("Enter a grey letter: ")
        if grey == "":      
            break  
        if grey == "exit":
            sys.exit()
        # TO DO: don't add letter to greylist if in yellowlist or greenlist
        
        greylist.append(grey)
    print(greylist)
    l3 = [e for e in l3 if all(f not in e for f in greylist)]
    print(l3)

    # Dictionary that will hold solutions:(list of results) as key:value pairs
    ya = {}

    for guess in lst:
        ya[guess] = {}

        # Initialize a dictionary to keep track of the counts of each letter in the solution
        for solution in l3:
            solution_counts = {}
            for sletter in solution:
                solution_counts[sletter] = solution_counts.get(sletter, 0) + 1

            # Initialize lists to hold the results
            ya[guess][solution] = []

        # First pass: Identify greens and update solution counts
            for guess_letter, solution_letter in zip(guess, solution):
                if guess_letter == solution_letter:
                    ya[guess][solution].append('green')
                    solution_counts[guess_letter] -= 1
                else:
                    ya[guess][solution].append(None)  # Placeholder for non-green matches

            # Second pass: Identify yellows and greys, respecting green matches
            for i, guess_letter in enumerate(guess):
                if ya[guess][solution][i] is None:  # Only process if not already marked as green
                    if guess_letter in solution_counts and solution_counts[guess_letter] > 0:
                        ya[guess][solution][i] = 'yellow'
                        solution_counts[guess_letter] -= 1
                    else:
                        ya[guess][solution][i] = 'grey'

    # “on average, more and smaller groups means faster solving”

    # combine colors for each solution into single strings so they are more easily compared
    for z in ya:
        for wordcolors in ya[z]:
            # print(wordcolors, ya[z][wordcolors])
            joinlist = ''.join(ya[z][wordcolors])
            ya[z][wordcolors] = joinlist

    # compare strings of colors, count and track number of unique strings of colors 

    solutiondict = {}
    for z in ya: 
        countsum = 0
        colorcounts = {}

        # print(z, ya[z]) 
        for aa in ya[z]:
            colorcounts[ya[z][aa]] = colorcounts.get(ya[z][aa], 0) + 1


        floatlength = float(len(colorcounts))

        for ya[z][aa], count in colorcounts.items():
            # print(ya[z][aa], count)
            countsum = countsum + float(count)
            averagegroups = (countsum/floatlength) # average of counts, represents average size of groups
            solutiondict[z] = averagegroups
            

        # print number of unique counts, represents number of groups
        # print(len(colorcounts))
        colorcounts.clear()
        
    if len(l3) < 2:
        sys.exit()

    # I will have to figure out what to do if one guess somehow has say a bigger average in groups and more groups (is this even possible mathematically?). I will need to study the NYT WordleBot a bit more

    # print the recommended guesses, in other words, the guesses that produced smallest average group size
    min_value = min(solutiondict.values())
    rlist = [ka for ka,va in solutiondict.items() if va == min_value]
    slist = [xa for xa in rlist if xa in l3]
    print(solutiondict)
    if not slist:
        print("Recommended next guesses:", rlist)
    else:
        print("Recommended next guesses:", slist)

    # I suppose there could be a case where one guess on average had smaller group size, but had one very large group, for example, which would do a worse job of guarenteeing solving the puzzle quickly. Should I be calculating and recording largest group size as well? In addition, should I be going at least one extra layer deep for calculating efficiency to solving? Or should I even be going all the way with each line? 

    # should turn this part of the program into a function I call perhaps 
    
    # prepare for next Wordle entry
    counts.clear()
    greenlist.clear()
    yellowlist.clear()
    greylist.clear()
