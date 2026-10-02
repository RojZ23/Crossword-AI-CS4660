Week 5 Lab Reflection

In this lab, I implemented a crossword puzzle generator as a constraint satisfaction problem. Each word slot is a variable, and the vocabulary words are the possible domain values. I used node consistency to remove words with incorrect lengths and AC-3 to remove values that cannot satisfy crossing-letter constraints.

The backtracking search finds a complete assignment after the domains have been reduced. My consistency checks ensure that words fit their slots, words are not repeated, and overlapping letters match. I also used the MRV, degree, and least-constraining-value heuristics to choose variables and values more efficiently.

This assignment showed me how constraint satisfaction reduces brute-force searching. By filtering impossible choices before and during the search, the program can solve the crossword more efficiently while still following every puzzle constraint.
