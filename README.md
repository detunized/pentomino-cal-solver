# Pentomino Calendar Solver

A solver for pentomino calendar puzzles like [Мешок IQ](https://meshok-iq.ru/). 8 polyomino pieces (7 pentominoes and 1 hexomino) must be arranged on a 7×7 grid to cover all cells except the ones showing the current month and day.

**[Try it online](https://tubular-kringle-bb7f7b.netlify.app/)**

The solver finds all valid arrangements for any given date using backtracking search. It precomputes all rotations and reflections for each piece and uses constraint optimization to prune the search space.

The UI renders the board on an HTML5 Canvas and runs the solver in a Web Worker to keep the interface responsive. Use the dropdowns to pick a date and arrow keys or buttons to browse through all solutions.

## License

MIT
