# To compute **new** solutions

`python3 factory.py solutionrepository instancefilename level [timelimit]`

Computes a solution (from scratch for `instancefilename`) and writes the solutions in `solutionrepository`.

`level` is an integer: 1 to skip preprocessing slates, and more than one to build slates containing at most `level` items.

The computation stops after roughly `timelimit` seconds. If no `timelimit` is given, then the algorithm will not terminate. It updates the solutions when better ones are found.

# To optimize a **previous** solution

`python3 factory.py solutionrepository solutionfilename instancefilename [timelimit]`

Optimizes the solution `solutionfilename` for instance `instancefilename` and writes the solutions in `solutionrepository`.

The computation stops after roughly `timelimit` seconds. If no `timelimit` is given, then the algorithm will not terminate. It updates the solutions when better ones are found.
