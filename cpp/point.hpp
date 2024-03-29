#pragma once
#include <fstream>
#include <cmath>
#include <cassert>
#include <vector>
#include <algorithm>

template <class Number>
class Point {
  Number cx, cy;
public:
  Point() : cx(0), cy(0) {}
  Point(const Number &x, const Number &y) : cx(x), cy(y) {}
  Number x() const {return cx;}
  Number y() const {return cy;}
  Number squaredDistance(const Point<Number> &other) const {
    return (x()-other.x()) * (x()-other.x()) + (y()-other.y()) * (y()-other.y());
  }

  Point operator*(Number k) const {
    return Point(k*x(), k*y());
  }

  Number operator*(const Point<Number> &p) const {
    return p.x()*x() + p.y()*y();
  }

  Point operator+(const Point<Number> &p) const {
    return Point(p.x()+x(), p.y()+y());
  }

  Point operator-(const Point<Number> &p) const {
    return Point(p.x()-x(), p.y()-y());
  }

  Point operator-() const {
    return Point(-x(), -y());
  }

  Point operator!() const {
    return Point(-y(), x());
  }

  Number operator[](size_t i) const {
    if(i%2 == 0)
      return x();
    return y();
  }

  auto operator<=>(const Point<Number> &p) const = default;
  bool operator==(const Point<Number> &p) const = default;

  static Point<Number> minXY(const std::vector<Point<Number>> &pts) {
    Number minx = pts[0].x(), miny = pts[0].y();
    for(size_t i = 1; i < pts.size(); i++) {
      minx = std::min(minx, pts[i].cx);
      miny = std::min(miny, pts[i].cy);
    }
    return Point<Number>(minx, miny);
  }

  static Point<Number> maxXY(const std::vector<Point<Number>> &pts) {
    Number maxx = pts[0].x(), maxy = pts[0].y();
    for(size_t i = 1; i < pts.size(); i++) {
      maxx = std::max(maxx, pts[i].cx);
      maxy = std::max(maxy, pts[i].cy);
    }
    return Point<Number>(maxx, maxy);
  }

  double slope() {
    return (double) cy / cx;
  }
};

template <class Number>
std::ostream &operator<<(std::ostream &os, Point<Number> const &p) {
  return os << "(" << p.x() << "," << p.y() << ")";
}




