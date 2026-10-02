# Crossword-AI-CS4660

The complete, actual crossword lab is located in the crossword folder.

The generate_gui.py file is only a fun test version of the project. It provides a graphical user interface (GUI) for selecting the crossword structure and word-list files, generating a crossword, and displaying the result in a window.

For the full lab implementation and required work, use the files in the crossword folder.

Reflection: generate_gui.py

This program is a graphical user interface (GUI) version of a crossword puzzle generator and solver. It uses the same core crossword model from crossword.py, where the structure file identifies open cells and the word file provides the vocabulary. The program represents each across or down word slot as a variable and searches for a set of words that fit all slot lengths and crossing-letter requirements.

The solver applies several constraint-satisfaction techniques. First, node consistency removes words whose lengths do not match a slot. Next, AC-3 checks crossing constraints and removes words that have no compatible choice in neighboring slots. Finally, backtracking tries remaining values until it finds a complete, consistent assignment. It also uses heuristics: it chooses an unassigned slot with the smallest remaining domain, breaking ties by the number of neighbors, and it orders possible words by how few choices they eliminate for nearby slots.

What makes this file different from the other generate.py is its interface. The other generate.py is the non-GUI or command-line version, which typically receives file paths as arguments and prints or saves its output through the terminal. In contrast, generate_gui.py creates a Tkinter window. The user can browse for the structure and word-list text files, click “Generate Crossword,” and see status messages, errors, or a no-solution notification directly in the application.

The GUI also draws the completed crossword on a scrollable canvas. Open cells are shown as white squares with letters, while blocked cells are dark. This makes the result easier to view and use than a terminal-only display, especially for larger crossword layouts. The graphical design improves accessibility and usability without changing the main CSP-solving purpose of the program.

Overall, generate_gui.py separates the puzzle-solving logic from the presentation layer: crossword.py defines the crossword data and relationships, CrosswordCreator solves the CSP, and CrosswordApp handles file selection, buttons, messages, and drawing. This is a useful design because the same solver can support both a command-line program and a visual application.
