"""
Crossword Puzzle Generator


Implements a crossword puzzle solver using a Constraint
Satisfaction Problem (CSP) approach.


Each crossword word slot is represented as a variable, and each
possible vocabulary word is a value in that variable's domain.
The program finds a complete assignment of words that satisfies
all crossword constraints.


The solver uses:
- Node consistency to remove words with incorrect lengths.
- Arc consistency (AC-3) to remove words that conflict at overlaps.
- Backtracking search to build a complete valid crossword.
- The minimum remaining values (MRV) heuristic to choose variables.
- The degree heuristic to break MRV ties.
- The least-constraining-value heuristic to order word choices.


The generated crossword:
- Uses words with the correct length for every slot.
- Does not repeat the same word more than once.
- Ensures intersecting words have matching letters.
- Returns no solution when no valid crossword assignment exists.
"""

import sys
from collections import deque

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]

        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont

        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )

        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]

                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox(
                            (0, 0), letters[i][j], font=font
                        )
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
        constraints; in this case, the length of the word.)
        """
        # Remove words that violate the unary length constraint.
        for var in self.crossword.variables:
            self.domains[var] = {
                word for word in self.domains[var]
                if len(word) == var.length
            }

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        # Variables without a shared cell do not need revision.
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False

        i, j = overlap
        unsupported = set()

        # Keep an x word only when some y word supports it at the overlap.
        for x_word in self.domains[x]:
            if not any(x_word[i] == y_word[j] for y_word in self.domains[y]):
                unsupported.add(x_word)

        if unsupported:
            self.domains[x] -= unsupported
            return True

        return False

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # Start with every overlapping pair unless an arc list is supplied.
        if arcs is None:
            queue = deque(
                (x, y)
                for x in self.crossword.variables
                for y in self.crossword.neighbors(x)
            )
        else:
            queue = deque(arcs)

        # Recheck neighboring arcs whenever a domain is reduced.
        while queue:
            x, y = queue.popleft()

            if self.revise(x, y):
                if not self.domains[x]:
                    return False

                for z in self.crossword.neighbors(x):
                    if z != y:
                        queue.append((z, x))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        # A complete assignment gives every variable a word.
        return len(assignment) == len(self.crossword.variables)

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check word lengths, uniqueness, and overlap constraints.
        for var, word in assignment.items():
            if len(word) != var.length:
                return False

        # A word may not be used more than once.
        if len(set(assignment.values())) != len(assignment):
            return False

        # Check word lengths, uniqueness, and overlap constraints.
        for var, word in assignment.items():
            for neighbor in self.crossword.neighbors(var):
                if neighbor not in assignment:
                    continue

                i, j = self.crossword.overlaps[var, neighbor]
                if word[i] != assignment[neighbor][j]:
                    return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        eliminated = {}

        # Count choices each candidate would eliminate for unassigned neighbors.
        for value in self.domains[var]:
            count = 0

            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    continue

                i, j = self.crossword.overlaps[var, neighbor]

                for neighbor_value in self.domains[neighbor]:
                    if value == neighbor_value or value[i] != neighbor_value[j]:
                        count += 1

            eliminated[value] = count

        # Least-constraining values eliminate the fewest choices first.
        return sorted(self.domains[var], key=lambda value: eliminated[value])

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned = [
            var for var in self.crossword.variables
            if var not in assignment
        ]

        # Apply MRV, then break ties using the degree heuristic.
        return min(
            unassigned,
            key=lambda var: (
                len(self.domains[var]),
                -len(self.crossword.neighbors(var))
            )
        )

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # Stop when the current assignment contains every variable.
        if self.assignment_complete(assignment):
            return assignment

        # Choose the next variable using the MRV and degree heuristics.
        var = self.select_unassigned_variable(assignment)

        # Try values in least-constraining-value order.
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value

            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                    return result

        # No candidate value can complete this partial assignment.
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
