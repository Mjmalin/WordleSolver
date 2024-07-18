# WordleSolver

This program assists in solving the NYT game Wordle in as few guesses as possible. 

![image](./WordleSolverPic1)
_Wordle from 6/17/24
_

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the required packages.

```bash
pip install -r requirements.txt
```

## Using the program

When playing Wordle, start by entering your own first guess into the game. 

![image](./Wordlepic5.png)
Wordle from 6/18/24

When you start the program, it begins by prompting you to enter a green letter. In this above example, there are no green letters, so you would press enter, as it instructs.

Next, the program prompts for yellow letters. In this case, there are 3-- we will start with 'r'. Now the program prompts for the position. Since the 'r' is in the 2nd position out of 5, you enter '2.'


![image](./Wordlepic3.png)

After you finish entering the yellow letters, then the grey letters, the program will give you a few pieces of information. It will display the "Remaining possible solutions," and most importantly, "Recommended next best guess(es)." 

![image](./Wordlepic4.png)


In this case, the program recommends "siren," so that is what we will guess next. It also gives a metric called "Smallest average group size," which will be explained in more detail in the "How the program works" section of this README file. 







## How the program works


