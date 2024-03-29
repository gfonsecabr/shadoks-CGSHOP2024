#pragma once

// #include "geometry.hpp"
// #include "instance.hpp"
// #include "solution.hpp"
// #include <vector>
// #include <iostream>
// #include <utility>   // std::pair
// #include <algorithm> // reverse
// #include <cstdlib>
// #include <random>
// #include <numbers>
// #include <cmath>
#include "is.hpp"
#include "grid.hpp"
#include "slide.hpp"
#include <set>

Item randomPlace(Item item, const ClippedPolygon<i64> &container) {
  item = item + Point<i64>(-item.shape.getMinX(), -item.shape.getMinY());
  int maxX = container.getMaxX() - item.shape.getMaxX() + 1;
  int maxY = container.getMaxY() - item.shape.getMaxY() + 1;

  std::uniform_int_distribution rndx(0, maxX);
  std::uniform_int_distribution rndy(0, maxY);

  Item ret;
  int i = 0;
  do {
    int rx = rndx(rgen);
    int ry = rndy(rgen);
    ret = item + Point<i64>(rx,ry);
    if(i++ == 1000) {
      ret.id = -1;
      return ret;
    }
  } while(!container.contains(ret.shape));
  return ret;
}

Point<i64> gaussPoint(int sigma) {
  std::normal_distribution<double> normal(0.0, sigma);
  std::uniform_real_distribution<> uniform(0.0, std::numbers::pi);
  double r = normal(rgen);
  double theta = uniform(rgen);
  i64 x = r * cos(theta);
  i64 y = r * sin(theta);
  return Point<i64>(x,y);
}


std::vector<Item> randomPlacements(const std::vector<Item> &items, const ClippedPolygon<i64> &container, int nuniform) {
  std::vector<Item> placements;
  for(const Item &item : items) {
    for(int i = 0; i < nuniform; i++) {
      Item placed = randomPlace(item, container);
      if(placed.id >= 0)
        placements.push_back(placed);
    }
  }

  return placements;
}

std::vector<std::pair<Point<i64>,double>> placeMines(cxxopts::ParseResult &par, const std::vector<Item> &placed) {
  std::vector<std::pair<Point<i64>,double>> mines;
  int nmines = par["mines"].as<int>();

  for(const Item &item : placed) {
    std::uniform_int_distribution rndx(item.shape.getMinX(), item.shape.getMaxX());
    std::uniform_int_distribution rndy(item.shape.getMinY(), item.shape.getMaxY());
    for(int i = 0; i < nmines; i++) {
      Point<i64> p;
      do {
        p = Point<i64>(rndx(rgen),rndy(rgen));
      } while(!item.shape.contains(p));
      mines.push_back(std::make_pair(p, item.value));
    }
  }
  return mines;
}

double minesIn(Polygon<i64> &poly, std::vector<std::pair<Point<i64>,double>> &mines) {
  double cost = 0.0;
  for(auto &[p,v] : mines) {
    if(poly.contains(p))
      cost += v;
  }
  return cost;
}

Item bestPlacement(std::vector<Item> &candidates, std::vector<std::pair<Point<i64>,double>> &mines) {
  Item *best = nullptr;
  double bestCost;

  for(Item &item : candidates) {
    double cost = minesIn(item.shape, mines);
    // std::cout << cost << " ";
    if(best == nullptr || cost < bestCost) {
      bestCost = cost;
      best = &item;
    }
  }
  // std::cout << "-> " << bestCost << std::endl;

  return *best;
}

std::vector<Item> wiseRandomPlacements(cxxopts::ParseResult &par, const std::vector<Item> &items, const ClippedPolygon<i64> &container, int nuniform, const std::vector<Item> &placed) {
  auto mines = placeMines(par, placed);
  int ncand = par["candidates"].as<int>();

  std::vector<Item> placements;
  for(const Item &item : items) {
    for(int i = 0; i < nuniform; i++) {
      std::vector<Item> candidatePlacements;
      for(int j = 0; j < ncand; j++) {
        Item placed = randomPlace(item, container);
        if(placed.id >= 0)
          candidatePlacements.push_back(placed);
      }
      if(candidatePlacements.size()) {
        placements.push_back(bestPlacement(candidatePlacements, mines));
      }
    }
  }

  return placements;
}

IS solveSigma(cxxopts::ParseResult &par, const ClippedPolygon<i64> &container, const std::vector<Item> &unplaced, const std::vector<Item> &movable, std::vector<Item> const &fixed, double sigma) {
  std::string algorithm = par["algorithm"].as<std::string>();
  if(algorithm == "auto") {
    i64 maxValue = 0;
    for(const auto &item : unplaced)
      if(item.value > maxValue)
        maxValue = item.value;

    if(maxValue > 1)
      algorithm = "hybrid";
    else // cf1 instances may use too much memory with cplex
      algorithm = "local";
  }

  std::vector<Item> unplacedOrMovable(movable);
  std::copy(unplaced.begin(), unplaced.end(), std::back_inserter(unplacedOrMovable));
  std::map<int,int> quantityOf;
  for(const Item &item : unplacedOrMovable)
    quantityOf[item.id]++;

  int nvert;
  if(IS::getNumVertices() > 0.0)
    nvert = IS::getNumVertices();
  else
    nvert = par["vertices"].as<int>();

  int nuniform;
  if(movable.size())
    nuniform = nvert * (1.0 - par["placed"].as<double>());
  else if(par["isiter"].as<int>() <= 1 && algorithm=="mip")
    nuniform = par["vertices"].as<int>() * (1.0 - par["placed"].as<double>() / 2);
  else
    nuniform = 2 * par["vertices"].as<int>();

  int ngauss = nvert - nuniform - 4 * movable.size();
  nuniform /= unplacedOrMovable.size();
  if(nuniform <= 0)
    nuniform = 1;
  if(movable.size()) {
    ngauss /= movable.size();
    if(ngauss <= 0)
      ngauss = 1;
  }
  else
    ngauss = 0;

  std::vector<Item> placements;
  Message m("place");
  if(movable.empty() || par["mines"].as<int>() == 0)
    placements = randomPlacements(unplacedOrMovable, container, nuniform);
  else
    placements = wiseRandomPlacements(par, unplacedOrMovable, container, nuniform, movable); // TODO: movableOrFixed
  if(placements.empty()) return IS(par); // If the box is outside the container
  m.out("sigma",sigma);
  m.out("movable",movable.size());
  m.out("fixed",fixed.size());
  m.out("unplaced",unplaced.size());
  m.out("nuniform",nuniform);
  m.out("ngauss",ngauss);
  std::set<Point<i64>> gaussPoints{Point<i64>(0,0)};
  for(int i = 0; i < ngauss; i++)
    gaussPoints.insert(gaussPoint(sigma));

  for(const Item &item : movable) {
    for(Point<i64> v : gaussPoints) {
      Item placed = item + v;
      if(container.contains(placed.shape))
        placements.push_back(item + v);
    }
  }

  Point<i64> dir(0,1);
  for(int i = 0; i < 4; i++, dir = !dir) {
    std::vector<Item> solItems(movable);
    keepSliding(dir, solItems, container);
    for(Item &item : solItems)
      placements.push_back(item);
  }

  for(const Item &item : fixed)
    std::erase_if(placements,
                  [item](const Item &x){return !item.shape.interiorDisjoint(x.shape);});

  m.close(placements.size());

  IS isSolver(placements, quantityOf, par);
  if(algorithm == "local")
    isSolver.solveLocal();
  else if(algorithm == "greedy")
    isSolver.solveGreedy();
  else if(algorithm == "mip")
    isSolver.solveCplex();
  else { // hybrid
    isSolver.solveCplex();
    if(isSolver.cplexGap > .1 ){
      auto isSolver2 = isSolver;
      isSolver2.clearSolution();
      isSolver2.solveLocal();
      if(isSolver2.getValue() > isSolver.getValue())
        return isSolver2;
    }
  }

  return isSolver;
}

std::vector<Item> solveBox(cxxopts::ParseResult &par, const ClippedPolygon<i64> &container, std::vector<Item> unplaced, std::vector<Item> movable, std::vector<Item> const &fixed) {
  std::vector<Item> unplacedOrMovable(movable);
  std::copy(unplaced.begin(), unplaced.end(), std::back_inserter(unplacedOrMovable));
  std::map<int,int> quantityOf;
  for(const Item &item : unplacedOrMovable)
    quantityOf[item.id]++;

  for(int sigma = (container.getMaxX()-container.getMinX()) / 8; sigma > 1 ; sigma /= 2) {
    bool redo;
    do {
      redo = false;
      i64 previousValue = getValueVector(movable);
      IS isSolver = solveSigma(par, container, unplaced, movable, fixed, sigma);
      std::vector<Item> placed = isSolver.getSolution();
      i64 newValue = getValueVector(placed);
      if(newValue >= previousValue) {
        movable = placed;
        if(isSolver.solveTime < par["isto"].as<int>() / 2 &&
           newValue > previousValue)
          redo = true;
      }

      std::map<int,int> unplacedQuantityOf(quantityOf);
      for(const Item &item : movable)
        unplacedQuantityOf[item.id]--;
      unplaced.clear();
      for(const Item &item : unplacedOrMovable) {
        while(unplacedQuantityOf[item.id] > 0) {
          unplacedQuantityOf[item.id]--;
          unplaced.push_back(item);
        }
      }
    } while(redo);
  }
  return movable;
}


void solveRepeat(const Instance &instance, Solution &solution, cxxopts::ParseResult &par) {
  Message mSplit("split");
  int subx = par["subx"].as<int>();
  int suby = par["suby"].as<int>();

  {
    int n = instance.nitems;
    int nmax = par["subitems"].as<int>();
    int xmax = instance.container.getMaxX();
    int ymax = instance.container.getMaxY();
    int xymax = std::max(xmax,ymax);
    int xymin = std::min(xmax,ymax);
    int submax, submin;
    for(submax = 1; ; submax++) {
      int sizemax = xymax / submax + (xymax % submax != 0); // divide rounding up
      submin = xymin / sizemax; // divide rounding down
      if(submin > 0 && n / submin / submax <= nmax)
        break;
      submin++; // round up
      if(n / submin / submax <= nmax)
        break;
    }
    subx = submax;
    suby = submin;
    if(xmax < ymax) {
      subx = submin;
      suby = submax;
    }
  }
  mSplit.out("subx", subx);
  mSplit.out("suby", suby);

  i64 deltax = 1 + instance.container.getMaxX() / subx;
  i64 deltay = 1 + instance.container.getMaxY() / suby;
  std::vector<Item> unplaced = solution.unplacedItems();
  std::shuffle(unplaced.begin(), unplaced.end(), rgen);

  {
    int o = par["sort"].as<int>();
    mSplit.out("sort", o);

    if(o == 4) {
      auto cmp = [](const Item &a, const Item &b){
        return a.shape.diameter().slope()
             > b.shape.diameter().slope();
      };
      std::stable_sort(unplaced.begin(), unplaced.end(), cmp);
    }
    else if(o == 5) {
      auto cmp = [](const Item &a, const Item &b){
        return std::make_tuple(a.shape.longestEdge().sorted().slope(), a.shape.diameter().slope())
             > std::make_tuple(b.shape.longestEdge().sorted().slope(), b.shape.diameter().slope());
      };
      std::stable_sort(unplaced.begin(), unplaced.end(), cmp);
    }
  }
  auto unplacedOfBox = splitVector(unplaced, subx*suby);
  std::shuffle(unplacedOfBox.begin(), unplacedOfBox.end(), rgen);

  for(int yi = 0; yi < suby; yi++) {
    for(int xi = 0; xi < subx; xi++) {
      Message mbox("box");
      mbox.out("x",xi);
      mbox.out("y",yi);
      Point<i64> pmin(xi*deltax, yi*deltay);
      Point<i64> pmax(std::min(xi*deltax + deltax, instance.container.getMaxX()),
                      std::min(yi*deltay + deltay, instance.container.getMaxY()));
      Rectangle<i64> box(pmin,pmax);
      ClippedPolygon<i64> container{instance.container, box};
      if(!container.empty()) {
        std::vector<Item> movable, fixed, relevantFixed;
        for(const Item &item : solution.items) {
          if(box.contains(item.shape.box()))
            movable.push_back(item);
          else {
            fixed.push_back(item);
            if(!box.interiorDisjoint(item.shape.box()))
              relevantFixed.push_back(item);
          }
        }
        mbox.out("movable",movable.size());
        mbox.out("fixed",fixed.size());
        mbox.out("relevantFixed",relevantFixed.size());
        mbox.out("unplaced",unplacedOfBox[yi * subx + xi].size());

        std::vector<Item> newPlacements;
        newPlacements = solveBox(par, container, unplacedOfBox[yi * subx + xi], movable, relevantFixed);
        std::copy(newPlacements.begin(), newPlacements.end(), std::back_inserter(fixed));
        solution.improve(fixed);
      }
      mbox.close(solution.getValue());
    }
  }
  mSplit.close(solution.getValue());
}

void solve(const Instance &instance, Solution &solution, cxxopts::ParseResult &par) {
  int repeatNumber = par["repeat"].as<int>();
  bool autoRepeat = par["autorepeat"].as<bool>();
  int realRepeat = 1;
  for(int i = 0; i < repeatNumber; i++) {
    Message mrep("repeat");
    mrep.out("number", realRepeat++);
    i64 previousValue = solution.getValue();

    solveRepeat(instance, solution, par);
    if(autoRepeat && (solution.getValue() - previousValue) > par["tolerance"].as<double>() * previousValue)
      i--;
    mrep.close(solution.getValue());
  }
}

void tetris(const Instance &instance, Solution &solution, cxxopts::ParseResult &par) {
  std::vector<Item> items = instance.items;
  std::cout << "Instance size: " << instance.items.size() << std::endl;
  // std::stable_sort(items.begin(), items.end(),
  //                  [](const Item &a, const Item &b) {
  //                    return a.area < b.area;
  //                  });
  std::stable_sort(items.begin(), items.end(),
                   [](const Item &a, const Item &b) {
                     return (double)a.value / a.area > (double)b.value / b.area;
                   });

  for(const Item &instanceItem : items) {
    for(int q = 0; q < instanceItem.quantity; q++) {
      auto item = instanceItem;
      std::cout << '.' << std::flush;
      std::cout << "id=" << item.id << " score=" << (double)item.value / item.area << " area=" << item.area << " " << std::flush;
      if(maxSlide(item, solution.items, instance.container)) {
        solution.items.push_back(item);
        std::cout << "Placed!" << std::endl;
      }
      else
        std::cout << "No..." << std::endl;
    }
  }
}




