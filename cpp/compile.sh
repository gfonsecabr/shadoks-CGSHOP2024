#!/bin/bash
g++ -std=c++20 -c -I/opt/ibm/ILOG/CPLEX_Studio2211/cplex/include -I /opt/ibm/ILOG/CPLEX_Studio2211/concert/include -Ofast main.cpp
g++ -std=c++20 -o solver -L/opt/ibm/ILOG/CPLEX_Studio2211/cplex/lib/x86-64_linux/static_pic -L/opt/ibm/ILOG/CPLEX_Studio2211/concert/lib/x86-64_linux/static_pic main.o -lilocplex -lconcert -lcplex -Ofast
