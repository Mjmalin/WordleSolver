# WordleSolver

This program solves the NYT game Wordle. 

![image](./WordleSolverPic1)
*Wordle from 7/17/24*

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required packages.

```bash
pip install -r requirements.txt
```

## Using the program

When playing Wordle, start by entering your own first guess into the game. 

![image](./Wordlepic5.png)

When you start the program, it begins by prompting you to enter a green letter. In this above example, there are no green letters, so you would press enter, as it instructs.

Next, the program prompts for yellow letters. In this case, there are 3-- we will start with 'r'. The program then prompts for the position. Since the 'r' is in the 2nd position out of 5, you enter '2.'


![image](./Wordlepic3.png)

After you finish entering the yellow letters, and then entering the grey letters (which don't require letter positions to be entered), the program will give you a few pieces of information. It will display the "Remaining possible solutions," and most importantly, "Recommended next best guess(es)." 

![image](./Wordlepic4.png)


In this case, the program recommends "siren," so that is what we will guess next. It also gives a metric called "Smallest average group size," which will be explained in more detail in the "How the program works" section of this README file. 

![image](./Wordlepic6.png)

After entering the corresponding greens, yellows, and greys from the guess "siren," the program presents one remaining word and then terminates.

![image](./Wordlepic8.png)

This means "nerdy" is the answer.

![image](./Wordlepic7.png)
*Wordle from 7/18/24*

In another example, if you want the program to recommend the best first guess, you can press "enter" for green, yellow, and grey with 0 entries. 

![image](./wordlepic9.png)

Using this strategy, on this particular day, the program recommends "parse" as the best first guess (this can potentially change from day to day).

![image](./wordlepic10.png)

After inputting "parse," the program evaluates 6 different, equally good guesses, so you can choose one arbitrarily.


![image](./wordlepic13.png)

The program would solve on the next guess if you chose "light". Since the "average group size" was >1, it was not guaranteed to get the answer on the third guess, however (again, more on this soon).

![image](./wordlepic14.png)
*Wordle from 7/22/24*

## How the program works

### 1. Building a List of Wordle Solutions; Subtracting Non-Solutions

The program needs to start with a list of all valid Wordle solutions. It begins by scraping a list of all possible Wordle solutions from a github repository, as well as using BeautifulSoup and regular expressions to import and parse a list of all past Wordle solutions from a website. 

```bash
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
```

It then uses list comprehension to subtract all past solutions from all possible solutions, since Wordle never repeats solutions. 

```bash
# subtract all past Wordle answers from all possible Wordle solutions
remaining_solutions = [d for d in all_solutions_list if d not in past_solutions_list]
```

The program uses list comprehension once again to subtract all impossible solutions based on green, yellow, and grey letters, continuing to prompt the user to enter letters until there is only one Wordle solution left. 

```bash
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
```

### 2. Recommending Guesses

Next, the program needs to recommend guesses. To do this, it must first compare every possible guess to every possible solution, storing the theoretical greys, yellows, and greens that each guess/solution pairing would produce. It is important to check every possible guess, since very often the best guess is not a possible solution.

```bash
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
```

For every guess, the program sorts the grey, yellow, greens of those solutions into "groups." For instance, if only 2 solutions for the same guess produce "grey grey yellow grey grey," the program tracks that unique string of colors and stores the count "2."

![image](./wordlepic21.png)

The program now calculates the average size of those groups of unique strings of colors. The smaller the average size of groups for a guess, the faster Wordle can generally be solved with that particular guess. The most extreme example is an average group size of 1. If all groups have only one possible solution, that means your next guess guarantees solving Wordle on the following guess. 

![image](./wordlepic22.png)

Here is the code that prints all the guesses with the smallest average group size. The program prioritizes recommending guesses that could be possible solutions, but not at the expense of recommending guesses with smallest average group size. 

![image](./wordlepic27.png)

In this example, after our first guess "parse," there are only 6 remaining possible solutions.

![image](./wordlepic23.png)

![image](./wordlepic24.png)

Just below that, we can see that there are a bunch of potential guesses that will produce an average group size of 1, so we just choose one at random-- and we are guaranteed to solve Wordle in 3.

![image](./wordlepic25.png)

![image](./wordlepic26.png)
*Wordle from 7/24/24*














