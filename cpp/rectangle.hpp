#pragma once
#include <fstream>
#include <iostream>
#include <cmath>
#include <cassert>
#include <vector>
#include <algorithm>
#include "point.hpp"
#include "segment.hpp"

template <class Number>
class Rectangle {
  Point<Number> pmin, pmax;
public:
  Rectangle():pmin(0,0),pmax(0,0) {}

  Rectangle(const std::vector<Point<Number>> pts) :
    pmin(Point<Number>::minXY(pts)),
    pmax(Point<Number>::maxXY(pts))
    {}

  Rectangle(const Point<Number> &p, const Point<Number> &q) :
    Rectangle(std::vector<Point<Number>>{p,q})
    {}

  std::pair<Point<Number>,Point<Number>> getPair() const {
    return {pmin,pmax};
  }

  Number getMaxX() const {
    return pmax.x();
  }

  Number getMaxY() const {
    return pmax.y();
  }

  Number getMinX() const {
    return pmin.x();
  }

  Number getMinY() const {
    return pmin.y();
  }

  Point<Number> operator[](size_t i) const {
    i %= 4;
    switch(i) {
      case 0: return pmin;
      case 2: return pmax;
      case 1: return Point<Number>(pmin.x(),pmax.y());
    }
    return Point<Number>(pmax.x(),pmin.y());
  }

  auto operator<=>(const Rectangle<Number> &rect) const = default;
  bool operator==(const Rectangle<Number> &rect) const = default;

  bool contains(Point<Number> p) const {
    return pmin.x() <= p.x() && p.x() <= pmax.x() &&
           pmin.y() <= p.y() && p.y() <= pmax.y();
  }

  bool containsInside(Point<Number> p) const {
    return pmin.x() < p.x() && p.x() < pmax.x() &&
           pmin.y() < p.y() && p.y() < pmax.y();
  }

  bool contains(Rectangle<Number> r) const {
    return contains(r.pmin) && contains(r.pmax);
  }

  template <class Boxable>
  bool contains(Boxable b) const {
    return contains(b.box());
  }

  bool disjoint(Rectangle<Number> rect) const {
    return rect.pmax.x() < pmin.x() ||
           rect.pmax.y() < pmin.y() ||
           pmax.x() < rect.pmin.x() ||
           pmax.y() < rect.pmin.y();
  }

  bool interiorDisjoint(Rectangle<Number> rect) const {
    return rect.pmax.x() <= pmin.x() ||
           rect.pmax.y() <= pmin.y() ||
           pmax.x() <= rect.pmin.x() ||
           pmax.y() <= rect.pmin.y();
  }

  Rectangle<Number> operator^(Rectangle<Number> rect) const {
    rect.pmin = Point<Number>(std::max(pmin.x(),rect.pmin.x()),
                              std::max(pmin.y(),rect.pmin.y()));
    rect.pmax = Point<Number>(std::min(pmax.x(),rect.pmax.x()),
                              std::min(pmax.y(),rect.pmax.y()));
    return rect;
  }
};

template <class Number>
std::ostream &operator<<(std::ostream &os, const Rectangle<Number> &rect) {
  auto [pmin,pmax] = rect.getPair();
  return os << "[" << pmin.x() << "," << pmax.x() << "]x"
            << "[" << pmin.y() << "," << pmax.y() << "]";
}

