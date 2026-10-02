"""
Crossword Puzzle Generator — GUI Version


Implements a graphical crossword puzzle solver using a Constraint
Satisfaction Problem (CSP) approach and the Tkinter GUI library.


This GUI program is a fun test version of the crossword generator.
The actual/main generator implementation is in the other generate.py
file. This version uses the same solving concepts but adds a visual,
interactive interface for choosing files and viewing the puzzle.


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


The graphical interface:
- Lets the user browse for a crossword structure text file.
- Lets the user browse for a vocabulary words text file.
- Includes a Generate Crossword button to start the solver.
- Displays status messages, file errors, and no-solution messages.
- Draws the completed crossword on a scrollable canvas.
- Shows open cells as white squares and blocked cells as dark squares.
- Displays the solved letters directly inside the crossword grid.


Unlike the other generate.py file, this is the GUI version of the
crossword generator. Instead of running only through the command line
or terminal, it provides an interactive window that makes selecting
files and viewing the completed crossword easier for the user.


The generated crossword:
- Uses words with the correct length for every slot.
- Does not repeat the same word more than once.
- Ensures intersecting words have matching letters.
- Returns no solution when no valid crossword assignment exists.
"""

import sys
from collections import deque
import tkinter as tk
from tkinter import filedialog, messagebox

from crossword import Crossword, Variable


class CrosswordCreator:

    def __init__(self, crossword):
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def solve(self):
        self.enforce_node_consistency()
        if not self.ac3():
            return None
        return self.backtrack({})

    def enforce_node_consistency(self):
        for var in self.crossword.variables:
            self.domains[var] = {
                word for word in self.domains[var]
                if len(word) == var.length
            }

    def revise(self, x, y):
        overlap = self.crossword.overlaps[x, y]
        if overlap is None:
            return False

        i, j = overlap
        to_remove = {
            word_x for word_x in self.domains[x]
            if not any(word_x[i] == word_y[j] for word_y in self.domains[y])
        }
        if to_remove:
            self.domains[x] -= to_remove
            return True
        return False

    def ac3(self, arcs=None):
        if arcs is None:
            queue = deque(
                (x, y)
                for x in self.crossword.variables
                for y in self.crossword.neighbors(x)
            )
        else:
            queue = deque(arcs)

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
        return len(assignment) == len(self.crossword.variables)

    def consistent(self, assignment):
        if any(len(word) != var.length for var, word in assignment.items()):
            return False
        if len(set(assignment.values())) != len(assignment):
            return False

        for var, word in assignment.items():
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    i, j = self.crossword.overlaps[var, neighbor]
                    if word[i] != assignment[neighbor][j]:
                        return False
        return True

    def order_domain_values(self, var, assignment):
        ruled_out = {}
        for value in self.domains[var]:
            count = 0
            for neighbor in self.crossword.neighbors(var):
                if neighbor in assignment:
                    continue
                i, j = self.crossword.overlaps[var, neighbor]
                for neighbor_value in self.domains[neighbor]:
                    if value == neighbor_value or value[i] != neighbor_value[j]:
                        count += 1
            ruled_out[value] = count
        return sorted(self.domains[var], key=lambda value: ruled_out[value])

    def select_unassigned_variable(self, assignment):
        unassigned = [var for var in self.crossword.variables if var not in assignment]
        return min(
            unassigned,
            key=lambda var: (len(self.domains[var]), -len(self.crossword.neighbors(var)))
        )

    def backtrack(self, assignment):
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            candidate = assignment.copy()
            candidate[var] = value
            if self.consistent(candidate):
                result = self.backtrack(candidate)
                if result is not None:
                    return result
        return None


class CrosswordApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Crossword CSP Generator")
        self.geometry("950x760")
        self.minsize(700, 600)
        self.configure(bg="#f4f6f8")

        self.structure_path = tk.StringVar(value="data/structure1.txt")
        self.words_path = tk.StringVar(value="data/words1.txt")
        self.status = tk.StringVar(value="Choose files, then click Generate Crossword.")
        self.cell_size = 52

        self._build_controls()
        self._build_board()

    def _build_controls(self):
        controls = tk.Frame(self, bg="#f4f6f8", padx=16, pady=14)
        controls.pack(fill="x")

        tk.Label(
            controls, text="Crossword CSP Generator", font=("Arial", 18, "bold"),
            bg="#f4f6f8", fg="#1f2937"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 10))

        tk.Label(controls, text="Structure file:", bg="#f4f6f8").grid(
            row=1, column=0, sticky="w", pady=4
        )
        tk.Entry(controls, textvariable=self.structure_path, width=68).grid(
            row=1, column=1, sticky="ew", padx=8, pady=4
        )
        tk.Button(controls, text="Browse", command=self.choose_structure).grid(
            row=1, column=2, pady=4
        )

        tk.Label(controls, text="Words file:", bg="#f4f6f8").grid(
            row=2, column=0, sticky="w", pady=4
        )
        tk.Entry(controls, textvariable=self.words_path, width=68).grid(
            row=2, column=1, sticky="ew", padx=8, pady=4
        )
        tk.Button(controls, text="Browse", command=self.choose_words).grid(
            row=2, column=2, pady=4
        )

        tk.Button(
            controls, text="Generate Crossword", command=self.generate,
            font=("Arial", 11, "bold"), bg="#2563eb", fg="white",
            activebackground="#1d4ed8", activeforeground="white", padx=12, pady=6
        ).grid(row=3, column=1, sticky="w", pady=(10, 4))

        controls.columnconfigure(1, weight=1)

        tk.Label(
            controls, textvariable=self.status, bg="#f4f6f8", fg="#374151",
            anchor="w", wraplength=800, justify="left"
        ).grid(row=4, column=0, columnspan=3, sticky="ew", pady=(5, 0))

    def _build_board(self):
        outer = tk.Frame(self, bg="#f4f6f8", padx=16, pady=8)
        outer.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(outer, bg="#d1d5db", highlightthickness=0)
        x_scroll = tk.Scrollbar(outer, orient="horizontal", command=self.canvas.xview)
        y_scroll = tk.Scrollbar(outer, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=x_scroll.set, yscrollcommand=y_scroll.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        outer.rowconfigure(0, weight=1)
        outer.columnconfigure(0, weight=1)

    def choose_structure(self):
        filename = filedialog.askopenfilename(
            title="Choose crossword structure file",
            filetypes=[("Text files", "*.txt"), ("All files", "*")]
        )
        if filename:
            self.structure_path.set(filename)

    def choose_words(self):
        filename = filedialog.askopenfilename(
            title="Choose vocabulary words file",
            filetypes=[("Text files", "*.txt"), ("All files", "*")]
        )
        if filename:
            self.words_path.set(filename)

    def generate(self):
        structure = self.structure_path.get().strip()
        words = self.words_path.get().strip()

        if not structure or not words:
            messagebox.showerror("Missing input", "Choose both a structure file and a words file.")
            return

        try:
            self.status.set("Solving crossword with node consistency, AC-3, and backtracking...")
            self.update_idletasks()
            crossword = Crossword(structure, words)
            creator = CrosswordCreator(crossword)
            assignment = creator.solve()
        except FileNotFoundError as error:
            messagebox.showerror("File not found", str(error))
            self.status.set("Could not find one of the selected files.")
            return
        except Exception as error:
            messagebox.showerror("Error", str(error))
            self.status.set("An error occurred while generating the crossword.")
            return

        if assignment is None:
            self.canvas.delete("all")
            self.status.set("No solution exists for those files.")
            messagebox.showinfo("No solution", "No valid crossword could be generated.")
            return

        self.draw_crossword(crossword, assignment)
        self.status.set(
            f"Solved: {len(assignment)} words placed. "
            "Use the scroll bars if the crossword is larger than the window."
        )

    def draw_crossword(self, crossword, assignment):
        self.canvas.delete("all")
        letters = [[None for _ in range(crossword.width)] for _ in range(crossword.height)]

        for variable, word in assignment.items():
            for k, letter in enumerate(word):
                row = variable.i + (k if variable.direction == Variable.DOWN else 0)
                column = variable.j + (k if variable.direction == Variable.ACROSS else 0)
                letters[row][column] = letter

        for row in range(crossword.height):
            for column in range(crossword.width):
                x1 = column * self.cell_size
                y1 = row * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                if crossword.structure[row][column]:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2, fill="white", outline="#111827", width=2
                    )
                    if letters[row][column]:
                        self.canvas.create_text(
                            (x1 + x2) / 2, (y1 + y2) / 2,
                            text=letters[row][column], font=("Arial", 25, "bold"),
                            fill="#111827"
                        )
                else:
                    self.canvas.create_rectangle(
                        x1, y1, x2, y2, fill="#111827", outline="#111827"
                    )

        width = crossword.width * self.cell_size
        height = crossword.height * self.cell_size
        self.canvas.configure(scrollregion=(0, 0, width, height))


def main():
    app = CrosswordApp()
    app.mainloop()


if __name__ == "__main__":
    main()
