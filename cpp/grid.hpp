#pragma once
#include <fstream>
#include <cmath>
#include <cassert>
#include <vector>
#include <unordered_map>
#include <unordered_set>
#include <algorithm>
#include "instance.hpp"

using cNumber = int;
using Cell = std::pair<cNumber,cNumber>;

namespace std {
    template <> struct hash<std::pair<int,int>> {
        size_t operator()(std::pair<int,int> x) const {
            return hash<long long int>()((long long int)x.first + ((long long int) x.second << 32));
        }
    };
}

class Grid {
  i64 cellSize;
  std::vector<Item> items;
  std::unordered_map<Cell,std::vector<int>> grid;
public:
  Grid(const std::vector<Item> &_items) : items(_items) {
    setCellSize();
    for(int itemi = 0; itemi < items.size(); itemi++)
      registerItem(itemi);
  }

  void showStats() {
    std::cout << " Items: " << items.size();
    std::cout << " Cells: " << grid.size();
    std::cout << std::endl;
  }

  size_t size() {
    return items.size();
  }

  void replace(int itemi, const Item &item) {
    unregisterItem(itemi);
    items[itemi] = item;
    registerItem(itemi);
  }

  std::vector<Item> getItems() {
    return items;
  }

  bool interiorDisjoint(Polygon<i64> poly, int itemi) const {
    if(items.empty())
      return true;
    std::unordered_set<int> seen{itemi};

    for(Cell c: existingCellsOf(poly, itemi)) {
      for(int i : grid.at(c)) {
        if(!seen.contains(i) && !poly.interiorDisjoint(items[i].shape))
          return false;
        seen.insert(i);
      }
    }
    return true;
  }

  std::vector<int> conflicts(Polygon<i64> poly, int itemi) const {
    if(items.empty())
      return {};
    std::unordered_set<int> seen{itemi};
    std::vector<int> ret;

    for(Cell c: existingCellsOf(poly, itemi)) {
      for(int i : grid.at(c)) {
        if(i > itemi && !seen.contains(i) && !poly.interiorDisjoint(items[i].shape))
          ret.push_back(i);
        seen.insert(i);
      }
    }
    return ret;
  }

protected:
  void registerItem(int itemi) {
    for(Cell c : cellsOf(itemi))
      grid[c].push_back(itemi);
  }

  void unregisterItem(int itemi) {
    for(Cell c : cellsOf(itemi))
      std::erase(grid[c], itemi);
  }

  void setCellSize() {
    if(items.empty()) {
      cellSize = 0;
      return;
    }
    std::vector<i64> sizes;
    for(const auto &item : items) {
      sizes.push_back(std::max(item.shape.getMaxX() - item.shape.getMinX(),
                               item.shape.getMaxY() - item.shape.getMinY()));
    }
    std::sort(sizes.begin(), sizes.end());
    cellSize = sizes[sizes.size() / 2];
  }

  Cell firstCell(Polygon<i64> poly) const {
    Point p(poly.getMinX(), poly.getMinY());
    return std::make_pair((cNumber) (p.x() / cellSize),
                          (cNumber) (p.y() / cellSize));
  }

  Cell firstCell(int itemi) const {
    return firstCell(items[itemi].shape);
  }

  Cell lastCell(Polygon<i64> poly) const {
    Point p(poly.getMaxX(), poly.getMaxY());
    return std::make_pair((cNumber) (p.x() / cellSize),
                          (cNumber) (p.y() / cellSize));
  }

  Cell lastCell(int itemi) const {
    return lastCell(items[itemi].shape);
  }

  std::vector<Cell> cellsOf(int itemi) const {
    return cellsOf(items[itemi].shape);
  }

  Polygon<i64> cellPoly(Cell c) const {
    i64 minx = c.first * cellSize;
    i64 miny = c.second * cellSize;
    i64 maxx = minx + cellSize;
    i64 maxy = miny + cellSize;
    std::vector<Point<i64>> v = {
      Point<i64>(minx,miny),
      Point<i64>(maxx,miny),
      Point<i64>(maxx,maxy),
      Point<i64>(minx,maxy)};

    return Polygon<i64>(v);
  }

  std::vector<Cell> cellsOf(const Polygon<i64> &poly) const {
    std::vector<Cell> ret;

    Cell c0 = firstCell(poly);
    Cell c1 = lastCell(poly);
    // std::cout << c0.first << "," << c0.second << " -> " << c1.first << "," << c1.second << std::endl;

    for(int cy = c0.second; cy <= c1.second; cy++) {
      for(int cx = c0.first; cx <= c1.first; cx++) {
        Cell c = std::make_pair(cx,cy);
        // Polygon<i64> cellp = cellPoly(c);
        // if(!poly.interiorDisjoint(cellp)) {
          ret.push_back(c);
        // }
      }
    }
    return ret;
  }

  std::vector<Cell> existingCellsOf(const Polygon<i64> &poly, int itemi) const {
    std::vector<Cell> ret;

    Cell c0 = firstCell(poly);
    Cell c1 = lastCell(poly);
    // std::cout << c0.first << "," << c0.second << " -> " << c1.first << "," << c1.second << std::endl;

    for(int cy = c0.second; cy <= c1.second; cy++) {
      for(int cx = c0.first; cx <= c1.first; cx++) {
        Cell c = std::make_pair(cx,cy);
        if(grid.contains(c)) {
          const auto &v = grid.at(c);
          if(v.size() != 1 || v[0] != itemi) {
            // Polygon<i64> cellp = cellPoly(c);
            // if(!poly.interiorDisjoint(cellp)) {
              ret.push_back(c);
            // }
          }
        }
      }
    }
    return ret;
  }
};



