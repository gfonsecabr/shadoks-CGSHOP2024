#pragma once
#include <ilcplex/ilocplex.h>
#include <set>
#include <random>
#include "grid.hpp"

class IS {
  std::vector<Item> items;
  cxxopts::ParseResult &par;
  std::map<int,int> quantityOf;
  std::vector<std::set<int>> adjacency;
  std::vector<std::pair<std::vector<int>,int>> hyperEdges;
  std::vector<int> sol;
  std::map<int,std::vector<int>> sameId;
  int nedges = 0;
  int maxid;
  static double ivertices, nvertices;
public:
  double cplexGap = 0.0;
  double solveTime = 0.0;

  static double getNumVertices() {
    return nvertices;
  }

  IS(cxxopts::ParseResult &_par) : par(_par){}

  IS(const std::vector<Item> &_items, std::map<int,int> &_quantityOf, cxxopts::ParseResult &_par)
  : items(_items), par(_par), adjacency(_items.size()) {
    if(ivertices == 0.0)
      ivertices = par["ivertices"].as<int>();
    if(nvertices == 0.0)
      nvertices = par["vertices"].as<int>();

    Message m("buildIS");
    quantityOf = _quantityOf;
    Grid grid(items);

    // Build adjacency
    for(int i = 0; i < items.size() - 1; i++) {
      for(int j : grid.conflicts(items[i].shape, i)) {
        adjacency[i].insert(j);
        adjacency[j].insert(i);
        nedges++;
      }
    }

    // for(int i = 0; i < items.size() - 1; i++) {
    //   for(int j = i + 1; j < items.size(); j++) {
    //     if(!items[i].shape.interiorDisjoint(items[j].shape)) {
    //       adjacency[i].insert(j);
    //       adjacency[j].insert(i);
    //       nedges++;
    //     }
    //   }
    // }
    m.out("edges", nedges);

    // Build sameId
    for(int i = 0; i < items.size(); i++) {
      sameId[items[i].id].push_back(i);
      maxid = std::max(items[i].id, maxid);
    }

    // Build hyperEdges
    for(auto &[id, indices] : sameId) {
      if(indices.size() > 1) {
        hyperEdges.push_back(std::make_pair(indices, quantityOf[id]));
      }
    }
    m.out("hyperedges", hyperEdges.size());
    m.close(items.size());
  }

  void solveLocal() {
    double maxTime = elapsed() + par["isto"].as<int>() / (4 + par["isiter"].as<int>());
    static std::default_random_engine gen;
    static std::normal_distribution<double> normal(1.0,.1);
    Message m("local");

    // Build cost vector
    double greedydiv = par["greedydiv"].as<double>();
    std::vector<long double> gainOf(adjacency.size());
    for(int i = 0; i < adjacency.size(); i++) {
      long double g = items[i].value;
      for(int v : adjacency[i]) {
        if(items[v].id != items[i].id)
          g -= items[v].value / greedydiv;
      }
      gainOf[i] = g > 0.0 ? g : 0.0;
    }

    solveGreedy();
    auto available = quantityOf;
    std::vector<int> conflicts(items.size(), 0);
    for(int v : sol) {
      for(int u : adjacency[v]) {
        conflicts[u]++;
      }
      conflicts[v]++;
      available[items[v].id]--;
      assert(available[items[v].id] >= 0);
    }

    std::unordered_set<int> candidates;
    for(int v = 0; v < items.size(); v++) {
      if(conflicts[v] == 0 && available[items[v].id] > 0) {
        candidates.insert(v);
        std::cout << v << std::endl;
      }
    }

    assert(candidates.empty()); // Greedy should not leave vertices

    i64 previousValue = 0;
    for(int v : sol)
      previousValue += items[v].value;
    i64 solValue = previousValue;
    auto bestSol = sol;
    i64 bestValue = solValue;

    std::cout << previousValue << std::flush;
    for(int count=0; ; count++) {
      // Insert vertices
      while(candidates.size()) {
        std::vector<int> candidatesv(candidates.begin(), candidates.end());
        // std::vector<long double> gain(candidatesv.size());
        // for(int i = 0; i < candidatesv.size(); i++) {
        //   // long double g = items[i].value / items[i].area;
        //   long double g = gainOf[i];
        //   gain[i] = pow(g,2.0);
        // }
        // std::discrete_distribution<int> distribution(gain.begin(), gain.end());
        //
        // int addi = distribution(gen);
        // int addv = candidatesv[addi];

        int addv = -1;
        long double addvgain;
        for(int c : candidates) {
          long double cgain = gainOf[c] * normal(gen);
          if(cgain < 0.0) cgain = 0.0;
          if(addv == -1 || cgain > addvgain) {
            addv = c;
            addvgain = cgain;
          }
        }

        candidates.erase(addv);
        sol.push_back(addv);
        solValue += items[addv].value;
        for(int v : adjacency[addv]) {
          conflicts[v]++;
          if(conflicts[v] == 1) {
            candidates.erase(v);
          }
        }
        conflicts[addv]++;
        available[items[addv].id]--;
        if(available[items[addv].id] == 0) {
          for(int v : sameId[items[addv].id]) {
            candidates.erase(v);
          }
        }
      }

      // Show something if it improves
      if(solValue != previousValue) {
        previousValue = solValue;
        // std::cout << "->" << previousValue << std::flush;
      }

      // Update best solution
      if(solValue > bestValue) {
        std::cout << "->" << solValue << std::flush;
        bestSol = sol;
        bestValue = solValue;
      }

      // if(count % 16 == 0 && solValue < bestValue) {
      //   sol = bestSol; // FIXME Need conflicts and available
      //   solValue = bestValue;
      //   std::cout << '!';
      // }

      // Stop at some point
      if(elapsed() > maxTime) {
        sol = bestSol;
        solValue = bestValue;
        m.out("count",count);
        m.close(solValue);
        break;
      }

      // Remove a vertex
      int deli = rand()%sol.size();
      int delv = sol[deli];
      sol[deli] = sol.back();
      sol.pop_back();
      solValue -= items[delv].value;
      candidates.insert(delv);
      conflicts[delv]--;

      // Remove conflicts with delv
      for(int v : adjacency[delv]) {
        conflicts[v]--;
        if(conflicts[v] == 0 && available[items[v].id] > 0) {
          candidates.insert(v);
        }
      }

      // One more copy of delv is available now
      available[items[delv].id]++;
      if(available[items[delv].id] == 1) {
        for(int v : sameId[items[delv].id]) {
          if(conflicts[v] == 0) {
            candidates.insert(v);
          }
        }
      }
    }
    // std::cout << std::endl;
  }

  void solveGreedy() {
    Message m("greedy");

    // Build cost vector
    double greedydiv = par["greedydiv"].as<double>();
    std::vector<std::pair<long double,int>> costPairs;
    for(int i = 0; i < adjacency.size(); i++) {
      long double g = -items[i].value;
      for(int v : adjacency[i]) {
        if(items[v].id != items[i].id)
          g += items[v].value / greedydiv;
      }
      costPairs.push_back(std::make_pair(g,i));
    }
    std::sort(costPairs.begin(), costPairs.end());

    auto available = quantityOf;
    std::unordered_set<int> solset;
    for(auto &[_,v] : costPairs) {
      if(available[items[v].id] > 0) {
        bool failed = false;
        for(int u : adjacency[v]) {
          if(solset.contains(u)) {
            failed = true;
            break;
          }
        }
        if(!failed) {
          solset.insert(v);
          available[items[v].id]--;
        }
      }
    }
    i64 val = 0;
    for(int v : solset) {
      sol.push_back(v);
      val += items[v].value;
    }
    m.close(val);
  }


  void solveCplex() {
    solveTime = cplexGap = 0.0;
    solveLocal();

    for(int count = 0; count < par["isiter"].as<int>(); count++) {
      double prob = ivertices / items.size();
      std::unordered_set<int> curVertices(sol.begin(), sol.end());
      for(int i = 0; i < items.size(); i++) {
        if((rand() % 1024) / 1024.0 <= prob)
          curVertices.insert(i);
      }
      double t = resolveCplex(curVertices);
      solveTime += t;
      if(par["autotune"].as<bool>()) {
        if(t < par["isto"].as<int>() / 5.0 / par["isiter"].as<int>()) { // Too fast
          ivertices *= 1.025;
          nvertices *= 1.025;
          if(prob < 1.0)
            count--; // Redo this iteration
          // std::cout << ivertices << std::endl;
        }
        else if(cplexGap > 5 * par["tolerance"].as<double>()) { // Poor quality solution on timeout
          ivertices *= .9;
          nvertices *= .9;
          // std::cout << ivertices << "!!!" << std::endl;
        }
      }
    }
  }

  double resolveCplex(const std::unordered_set<int> &curVertices) {
    Message m("cplex");

    // if(curVertices.empty()) {
    //   for(int i = 0; i < items.size(); i++) {
    //     curVertices.insert(i);
    //   }
    // }

    IloEnv env;
    std::unordered_map<int,IloNumVar> variables;
    for(int i : curVertices)
      variables[i] = IloNumVar(env, 0, 1, ILOINT);

    m.out("variables", variables.size());

    // adjacency constraints
    IloModel model(env);
    for(int i : curVertices) {
      for(int j : adjacency[i]) {
        if(i < j && curVertices.contains(j))
          model.add(variables[i] + variables[j] <= 1);
      }
    }

    // hyperEdges constraints
    for(auto &[indices, quantity] : hyperEdges) {
      IloExpr expr(env);
      for(int i : indices) {
        if(curVertices.contains(i))
          expr += variables[i];
      }
      model.add(expr <= quantity);
    }

    // Objective function
    IloExpr expr(env);
    for(int i : curVertices)
      expr += variables[i] * (double)items[i].value;
    model.add(IloMaximize(env,expr));

    // Cplex parameters
    IloCplex cplex(model);
    cplex.setOut(env.getNullStream()); // Disable console output
    // cplex.setParam(IloCplex::Param::MIP::Limits::TreeMemory, 7000);
    cplex.setParam(IloCplex::Param::Threads, 1); // Single thread
    cplex.setParam(IloCplex::Param::TimeLimit, par["isto"].as<int>() / par["isiter"].as<int>());
    cplex.setParam(IloCplex::Param::MIP::Tolerances::MIPGap, par["tolerance"].as<double>());

    // Initial solution
    if(par["mipstart"].as<bool>()) {
      IloNumArray startVal(env, variables.size());
      IloNumVarArray startVar(env, variables.size());
      int vi = 0;
      std::unordered_set<int> solset(sol.begin(), sol.end());
      for(int i : curVertices) {
        if(solset.contains(i))
          startVal[vi] = 1.0;
        else
          startVal[vi] = 0.0;
        startVar[vi] = variables[i];
        vi++;
      }

      cplex.addMIPStart(startVar, startVal);
    }

    // Solve
    bool solved = cplex.solve();

    // Save solution
    if(solved && cplex.getObjValue() >= getValue()) {
      sol.clear();
      m.out("status",cplex.getCplexStatus());
      cplexGap = cplex.getMIPRelativeGap() ;
      m.out("gap",cplexGap);
      // m.out("time",solveTime);

      for(auto &[i,var] : variables)
        if(cplex.getValue(var) > .5)
          sol.push_back(i);
    }
    else
      cplexGap = 1e10;
    double t = m.close(cplex.getObjValue());
    env.end();
    return t;
  }


  void saveGraph(std::string filename) const {
    std::vector<std::set<int>> newAdjacency(adjacency);

    for(auto &[indices, quantity] : hyperEdges) {
      assert(quantity == 1);
      for(int i : indices) {
        for(int j : indices) {
          if(i != j) newAdjacency[i].insert(j);
        }
      }
    }

    int m = 0;
    for(auto &verts : newAdjacency)
      m += verts.size();
    m /= 2;

    std::ofstream file(filename, std::fstream::out | std::ifstream::binary);
    file << items.size() << " " << m << " 10" << std::endl;

    for(int i = 0; i < newAdjacency.size(); i++) {
      file << items[i].value;
      for(int j : newAdjacency[i])
        file << " " << j+1;
      file << std::endl;
    }
  }

  void clearSolution() {
    sol.clear();
  }

  std::vector<Item> getSolution() const {
    std::vector<Item> ret;
    for(int i : sol)
      ret.push_back(items[i]);
    return ret;
  }

  i64 getValue() const {
    i64 ret = 0;
    for(int i : sol)
      ret += items[i].value;
    return ret;
  }
};

double IS::ivertices = 0.0;
double IS::nvertices = 0.0;
