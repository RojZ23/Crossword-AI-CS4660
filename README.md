# Crossword AI Lab: Constraint Satisfaction

In this lab, I worked with an AI crossword puzzle generator and solver. The purpose of the lab was to use **constraint satisfaction problem (CSP)** techniques to fill a crossword grid with words that match the correct lengths and crossing-letter requirements.

## Files and Tools Used

- Python  
- `crossword.py` for the crossword data model  
- `generate.py` for the main command-line crossword generator and solver  
- `generate_gui.py` for an optional graphical user interface version  
- Crossword structure text files that define open and blocked cells  
- Word-list text files that provide the possible vocabulary  
- Tkinter for the GUI window and display  
- A scrollable canvas for drawing the generated crossword  

The main required lab work was located in the `crossword` folder. The `generate_gui.py` file was an extra test version that added a visual interface to the crossword generator.

## What I Did

I worked with a program that represents every across and down word space in the crossword as a variable. Each variable has possible word values from the word list, and the program searches for a combination of words that fits the crossword structure.

The structure file identifies which cells are open and which are blocked. The word-list file contains the words that can be placed into the puzzle. A valid solution must place words with the correct length into each slot and ensure that letters match wherever an across word and down word intersect.

The solver uses several AI constraint-satisfaction methods:

- **Node consistency:** Removes words that do not have the correct length for a crossword slot.
- **AC-3 constraint propagation:** Checks crossing-word relationships and removes words that do not have compatible letters with neighboring word slots.
- **Backtracking search:** Tries possible word assignments until it finds a complete and consistent crossword solution.
- **Minimum Remaining Values (MRV):** Chooses the unassigned word slot with the fewest remaining possible words.
- **Degree heuristic:** Breaks ties by selecting the variable connected to the greatest number of neighboring word slots.
- **Least Constraining Value:** Orders possible words based on which choice eliminates the fewest options for neighboring variables.

## GUI Version

I also used `generate_gui.py`, which is a graphical version of the crossword generator. Unlike the command-line `generate.py` program, the GUI allows the user to select the crossword structure file and word-list file through a Tkinter window.

The user can browse for files, click **Generate Crossword**, and receive status messages, error messages, or a no-solution message directly in the application. When the solver finds a solution, the GUI displays the crossword on a scrollable canvas.

In the displayed puzzle:

- Open cells appear as white squares containing letters.
- Blocked cells appear as dark squares.
- The canvas can be scrolled to view larger crossword layouts.

## What I Learned

This lab helped me understand how AI can solve problems by treating them as variables, possible values, and constraints. Rather than randomly placing words, the solver narrows down possibilities using word lengths and crossing-letter rules before searching through the remaining options.

I also learned the importance of separating the program’s logic from its interface. `crossword.py` handles the crossword structure and word relationships, `CrosswordCreator` handles the CSP-solving process, and `CrosswordApp` handles the GUI features such as file selection, buttons, messages, and drawing the completed crossword. This design makes it possible to use the same crossword solver in both a command-line program and a visual application.
