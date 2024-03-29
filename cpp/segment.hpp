#pragma once
#include <fstream>
#include <cmath>
#include <cassert>
#include <vector>
#include "point.hpp"

enum class Intersection {
  disjoint = 0,
  point = 1,
  segment = 2,
  area = 3
};

template <class Number>
class OSegment {
  Point<Number> s, t;
public:
  OSegment() :
    s(Point<Number>()), t(Point<Number>())
    {}
  OSegment(const Point<Number> &_s, const Point<Number> &_t) :
    s(_s), t(_t)
    {}
  Point<Number> source() const {return s;}
  Point<Number> target() const {return t;}

  OSegment<Number> operator*(Number k) const {
    return OSegment(s*k, t*k);
  }

  OSegment<Number> operator+(Point<Number> p) const {
    return OSegment(s+p, t+p);
  }

  OSegment<Number> operator-(Point<Number> p) const {
    return OSegment(s-p, t-p);
  }

  auto operator<=>(const OSegment<Number> &seg) const {
    return std::make_tuple(s,t) <=> std::make_tuple(seg.s,seg.t);
  }

  Point<Number> sum() const {
    return s + t;
  }

  Number doubleSignedArea(const Point<Number> &p) const {
    return (s.y() - p.y()) * (t.x() - s.x()) -
           (s.x() - p.x()) * (t.y() - s.y());
  }

  int orientation(const Point<Number> &p) const {
    Number val = doubleSignedArea(p);
    return (val > 0) - (val < 0);
  }

  bool contains(const Point<Number> &p, bool colinear = false) const {
    return (colinear || orientation(p) == 0) &&
    (
      (s <= p && p <= t) ||
      (s >= p && p >= t)
    );
  }

  bool containsInside(const Point<Number> &p, bool colinear = false) const {
    return (colinear || orientation(p) == 0) &&
    (
      (s < p && p < t) ||
      (s > p && p > t)
    );
  }

  bool incident(const Point<Number> &p) const {
    return s == p || t == p;
  }

  bool adjacent(const OSegment<Number> &seg) const {
    return incident(seg.source()) || incident(seg.target);
  }

  Intersection intersect(const OSegment<Number> &seg) const {
    int o1 = orientation(seg.source());
    int o2 = orientation(seg.target());

    // Colinear segments
    if (o1 == 0 && o2 == 0) {
      if (*this == seg ||
          containsInside(seg.source(), true) ||
          containsInside(seg.target(), true) ||
          seg.containsInside(source(), true) ||
         seg.containsInside(target(), true))
         return Intersection::segment;
      if (adjacent(seg))
        return Intersection::point;
      return Intersection::disjoint;
    }

    // One colinear endpoint
    if (o1 == 0) {
      if (containsInside(seg.source(), true) ||
          seg.containsInside(source(), true) ||
          seg.containsInside(target(), true))
        return Intersection::point;
      return Intersection::disjoint;
    }
    if(o2 == 0) {
      if (containsInside(seg.target(), true) ||
          seg.containsInside(source(), true) ||
          seg.containsInside(target(), true))
        return Intersection::point;
      return Intersection::disjoint;
    }

    // Both seg.source() and seg.target() on the same side
    if(o1 == o2)
      return Intersection::disjoint;

    // One colinear endpoint
    int o3 = seg.orientation(source());
    if(o3 == 0) {
      if (containsInside(seg.source(), true) ||
          containsInside(seg.target(), true) ||
          seg.containsInside(source(), true))
        return Intersection::point;
      return Intersection::disjoint;
    }
    int o4 = seg.orientation(target());
    if(o4 == 0) {
      if (containsInside(seg.source(), true) ||
          containsInside(seg.target(), true) ||
          seg.containsInside(target(), true))
        return Intersection::point;
      return Intersection::disjoint;
    }

    // Both source() and target() on the same side of seg
    if(o3 == o4)
      return Intersection::disjoint;

    return Intersection::point;
  }

  bool interiorDisjoint(const OSegment<Number> &seg) const {
    int o1 = orientation(seg.source());
    int o2 = orientation(seg.target());
    if(o1 == 0 && o2 == 0)
      return !containsInside(seg.source()) && !containsInside(seg.target()) && !seg.containsInside(s);

    if(o1 == o2 || o1 == 0 || o2 == 0)
      return true;

    o1 = seg.orientation(source());
    if(o1 == 0)
      return true;
    o2 = seg.orientation(target());
    if(o1 == o2 || o2 == 0)
      return true;

    return false;
  }
  Number squaredDistance() const {
    return source().squaredDistance(target());
  }
  double slope() const {
    return (target() - source()).slope();
  }

  OSegment<Number> sorted() const {
    if(source() < target())
      return *this;
    return OSegment<Number>(target(), source());
  }
};

template <class Number>
std::ostream &operator<<(std::ostream &os, OSegment<Number> const &seg) {
  return os << seg.source() << "->" << seg.target();
}


