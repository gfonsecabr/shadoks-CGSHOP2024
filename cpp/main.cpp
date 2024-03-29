/*
g++ -std=c++20 -c -I/opt/ibm/ILOG/CPLEX_Studio2211/cplex/include -I /opt/ibm/ILOG/CPLEX_Studio2211/concert/include -Ofast main.cpp
g++ -std=c++20 -o solver -L/opt/ibm/ILOG/CPLEX_Studio2211/cplex/lib/x86-64_linux/static_pic -L/opt/ibm/ILOG/CPLEX_Studio2211/concert/lib/x86-64_linux/static_pic main.o -lilocplex -lconcert -lcplex -Ofast
*/

#include <random>
std::default_random_engine rgen;

#include "tools.hpp"
#include "geometry.hpp"
#include "instance.hpp"
#include "solution.hpp"
#include "cxxopts.hpp"
#include "solver.hpp"

void parse(int argc, char **argv, cxxopts::Options &options, cxxopts::ParseResult &par) {
  options.add_options("Misc")
  ("help", "Print help.")
  ("s,seed", "Random seed, negative for automatic.", cxxopts::value<int>()->default_value("-1"))
  // ("v,verbose", "Verbose level.", cxxopts::value<int>()->default_value("5"))
  // ("bag", "Build edge bag.", cxxopts::value<bool>()->default_value("true"))
  // ("i,instance", "Instance file name (required unless a collection file is given).", cxxopts::value<std::string>())
  ("I,ipath", "Path of the instance files (when the input file is a solution).", cxxopts::value<std::string>()->default_value("../instances/"))
  ("O,outpath", "Path to save solution.", cxxopts::value<std::string>())
  // ("t,savetmp", "Save intermediate solutions.", cxxopts::value<bool>()->default_value("true"))
  ("inputfile", "Input instance or solution file", cxxopts::value<std::string>()->default_value(""))
  ;
  options.add_options("Independent Set")
  ("a,algorithm", "Algorithm name. Possible values are auto, greedy, local, hybrid, and mip", cxxopts::value<std::string>()->default_value("auto"))
  // ("del", "Number of sets to delete at each iteration  (only annealing).", cxxopts::value<int>()->default_value("3"))
  ("v,vertices", "Target number of vertices for the independent set solver.", cxxopts::value<int>()->default_value("2500"))
  ("isiter", "Number of cplex iterations.", cxxopts::value<int>()->default_value("1"))
  ("ivertices", "Number of vertices per iteration.", cxxopts::value<int>()->default_value("2500"))
  ("mines", "Number of mines to place.", cxxopts::value<int>()->default_value("32"))
  ("candidates", "Number of candidates for smaller number of mines hit.", cxxopts::value<int>()->default_value("3"))
  ("greedydiv", "Neighbors denominator for greedy.", cxxopts::value<double>()->default_value("8192"))
  ("isto", "Time out for an iteration of the independent set solver (sec).", cxxopts::value<int>()->default_value("500"))
  ("mipstart", "Start mip with greedy solution.", cxxopts::value<bool>()->default_value("1"))
  ("tolerance", "Relative improvements smaller than tolerance are not considered significant.", cxxopts::value<double>()->default_value(".005"))
  ;
  options.add_options("Main loop")
  ("tetris", "Tetris algorithm.", cxxopts::value<bool>()->default_value("0"))
  ("r,repeat", "Number of repetitions.", cxxopts::value<int>()->default_value("1"))
  ("autorepeat", "Automatically repeat when the improvement is higher than the tolerance.", cxxopts::value<bool>()->default_value("true"))
  ("subx", "Subdivide the problem by vertical lines by into subx slabs.", cxxopts::value<int>()->default_value("1"))
  ("suby", "Subdivide the problem by horizontal lines by into suby slabs.", cxxopts::value<int>()->default_value("1"))
  ("subitems", "Subdivide the problem automatically into boxes of at most subitems items.", cxxopts::value<int>()->default_value("250"))
  ("sort", "Sort by decreasing (1) area, (2) value, (3) value/area, (4) diameter slope, (5) longest edge slope.", cxxopts::value<int>()->default_value("5"))
  ("placed", "Fraction vertices for placed items", cxxopts::value<double>()->default_value("0.5"))
  ("gauss", "Fraction of Gauss vertices among placed vertices", cxxopts::value<double>()->default_value("0.5"))
  ("slide", "Number of slide vertices among placed vertices", cxxopts::value<int>()->default_value("4"))
  ("autotune", "Increase or decrease the number parameters based on previous performance.", cxxopts::value<bool>()->default_value("true"))
  ;

  options.parse_positional({"inputfile"});
  par = options.parse(argc, argv);
}
/*
std::string baseName(std::string fn) {
    int i = fn.find_last_of('/');
    if(i == std::string::npos)
      i = -1;
    int j = fn.find('.', i+1);
    std::string basename = fn.substr(i+1,j-i-1);
    return basename;
}
*/


int main(int argc, char **argv) {
  //-----------------------------------------------------------------
  // Read parameters
  //-----------------------------------------------------------------
  std::string command;
  for(int i = 0; i < argc; i++) {
    command += argv[i];
    if(i != argc-1)
      command += " ";
  }
  std::cout << command << std::endl;
  cxxopts::Options options("./solver", "CG:SHOP 2024 Packing");
  cxxopts::ParseResult par;
  parse(argc, argv, options, par);

  if (par.count("help") || !par.count("inputfile")) {
    std::cout << options.help() << std::endl;
    return 1;
  }

  std::string instpath;
  instpath = par["ipath"].as<std::string>();
  if(instpath.back() != '/')
    instpath.push_back('/');

  Instance instance;
  Solution solution(&instance);
  std::string inputfile = par["inputfile"].as<std::string>();
  if(inputfile.find("instance") == std::string::npos) {
    solution = Solution(inputfile, instance, instpath);
  }
  else {
    instance = Instance(inputfile);
  }
  if (par.count("solpath")) {
    solution.path = par["solpath"].as<std::string>();
    if(solution.path.back() != '/')
      solution.path.push_back('/');
  }

  Message::instance = &instance;
  instance.meta["command"] = command;

  int seed = par["seed"].as<int>();
  if(seed < 0)
    seed = static_cast<long unsigned int>(std::chrono::high_resolution_clock::now().time_since_epoch().count()) % 1000000;
  rgen.seed(seed);
  instance.meta["seed"] = std::to_string(seed);

  i64 oldValue = solution.getValue();
  if(par["tetris"].as<bool>())
    tetris(instance, solution, par);
  else
    solve(instance, solution, par);

  if(solution.getValue() > oldValue)
    solution.writeSol();

  return 0;
}
