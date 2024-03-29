# About

This is the C++ code of a solver that we used to obtain initial solutions to several instances of CG:SHOP 2024 packing competition, especially the small ones. It uses mixed integer programming multiple times. With the default arguments, it will take hours to run, even for the smallest instances.

# Compiling

To compile on linux, run `compile.sh`. You must have CPLEX installed at `/opt/ibm/ILOG/CPLEX_Studio2211/cplex/` or modify the path in `compile.sh`.

# Running

When you run `./solver` without any arguments, it shows the following help message:

```
./solver
CG:SHOP 2024 Packing
Usage:
  ./solver [OPTION...] positional parameters

 Independent Set options:
  -a, --algorithm arg   Algorithm name. Possible values are auto, greedy,
                        local, hybrid, and mip (default: auto)
  -v, --vertices arg    Target number of vertices for the independent set
                        solver. (default: 2500)
      --isiter arg      Number of cplex iterations. (default: 1)
      --ivertices arg   Number of vertices per iteration. (default: 2500)
      --mines arg       Number of mines to place. (default: 32)
      --candidates arg  Number of candidates for smaller number of mines
                        hit. (default: 3)
      --greedydiv arg   Neighbors denominator for greedy. (default: 8192)
      --isto arg        Time out for an iteration of the independent set
                        solver (sec). (default: 500)
      --mipstart        Start mip with greedy solution. (default: 1)
      --tolerance arg   Relative improvements smaller than tolerance are
                        not considered significant. (default: .005)

 Main loop options:
      --tetris        Tetris algorithm. (default: 0)
  -r, --repeat arg    Number of repetitions. (default: 1)
      --autorepeat    Automatically repeat when the improvement is higher
                      than the tolerance. (default: true)
      --subx arg      Subdivide the problem by vertical lines by into subx
                      slabs. (default: 1)
      --suby arg      Subdivide the problem by horizontal lines by into
                      suby slabs. (default: 1)
      --subitems arg  Subdivide the problem automatically into boxes of at
                      most subitems items. (default: 250)
      --sort arg      Sort by decreasing (1) area, (2) value, (3)
                      value/area, (4) diameter slope, (5) longest edge
                      slope. (default: 5)
      --placed arg    Fraction vertices for placed items (default: 0.5)
      --gauss arg     Fraction of Gauss vertices among placed vertices
                      (default: 0.5)
      --slide arg     Number of slide vertices among placed vertices
                      (default: 4)
      --autotune      Increase or decrease the number parameters based on
                      previous performance. (default: true)

 Misc options:
      --help         Print help.
  -s, --seed arg     Random seed, negative for automatic. (default: -1)
  -I, --ipath arg    Path of the instance files (when the input file is a
                     solution). (default: ../instances/)
  -O, --outpath arg  Path to save solution.
```

The only mandatory argument is the name of a file. The file may be an instance or a solution, but we did not find it useful in the competition to use solutions as input. Instead, optimize the solutions produced by this C++ solver using the Python solver.
