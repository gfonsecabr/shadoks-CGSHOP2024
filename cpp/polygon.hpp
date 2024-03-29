#pragma once
#include <fstream>
#include <cmath>
#include <cassert>
#include <vector>
#include "point.hpp"
#include "segment.hpp"
#include "rectangle.hpp"

template <class Number>
class Polygon {
  std::vector<OSegment<Number>> segs;
  std::vector<Point<Number>> verts;
  Rectangle<Number> bbox;
public:
  Polygon() {}

  Polygon(const std::vector<Point<Number>> pts) :
    verts(pts), bbox(pts) {
    for(size_t i = 0; i < pts.size(); i++) {
      segs.push_back(OSegment(pts[i], pts[(i+1)%pts.size()]));
    }
  }

  size_t size() const {
    return segs.size();
  }

  Point<Number> operator[](size_t i) const {
    assert(i < verts.size());
    return verts[i];
  }

  bool cross(const Polygon<Number> &poly) const {
    if(bbox.interiorDisjoint(poly.bbox))
      return false;
    for(const OSegment<Number> &seg1 : segs) {
      for(const OSegment<Number> &seg2 : poly.segs) {
        if(!seg1.interiorDisjoint(seg2))
          return true;
      }
    }
    return false;
  }

  Number getMaxX() const {
    return bbox.getMaxX();
  }

  Number getMaxY() const {
    return bbox.getMaxY();
  }

  Number getMinX() const {
    return bbox.getMinX();
  }

  Number getMinY() const {
    return bbox.getMinY();
  }

  Rectangle<Number> box() const {
    return bbox;
  }

  bool contains(const Polygon<Number> &poly) const {
    for(const Point<Number> &p : poly.verts) {
      if(!contains(p))
        return false;
    }
    return true;
  }

  bool contains(const Point<Number> &point) const {
    if(!bbox.contains(point))
      return false;
    for(const OSegment<Number> &seg : segs)
      if(seg.contains(point))
        return true;

    OSegment<Number> ray(point, Point<Number>(getMaxX()+1, point.y()+1));
    int cnt = 0;
    for(const OSegment<Number> &seg : segs) {
      if(!ray.interiorDisjoint(seg))
        cnt++;
    }
    return cnt % 2;
  }

  bool containsInside(const Point<Number> &point) const {
    if(!bbox.containsInside(point))
      return false;
    for(const OSegment<Number> &seg : segs)
      if(seg.contains(point))
        return false;

    OSegment<Number> ray(point, Point<Number>(getMaxX()+1, point.y()+1));
    int cnt = 0;
    for(const OSegment<Number> &seg : segs) {
      if(!ray.interiorDisjoint(seg))
        cnt++;
    }
    return cnt % 2;
  }

  bool interiorDisjoint(const Rectangle<Number> &rect) const {
    std::vector<Point<Number>> poly{
      Point<Number>(rect.getMinX(),getMinY()),
      Point<Number>(rect.getMaxX(),getMinY()),
      Point<Number>(rect.getMaxX(),getMaxY()),
      Point<Number>(rect.getMinX(),getMaxY())};

      return interiorDisjoint(poly);
  }

    bool interiorDisjoint(const Polygon<Number> &poly) const {
    if(cross(poly))
      return false;
    //FIXME Testing vertices is not enough
    for(int i = 0; i < 3 && i < segs.size() && i < poly.segs.size(); i++)
      if(containsInside(poly.segs[i].source()) || poly.containsInside(segs[i].source()))
        return false;
    if(bbox == poly.bbox)
      return false;
    return true;
  }

  bool interiorDisjoint(const std::vector<Polygon<Number>> &polys) const {
    for(const auto &poly : polys)
      if(!interiorDisjoint(poly))
        return false;
    return true;
  }

  Polygon<Number> operator+(const Point<Number> &vec) const {
    std::vector<Point<Number>> pts;
    for(const Point<Number> &p : verts)
      pts.push_back(p + vec);
    return Polygon<Number>(pts);
  }

  double signedArea() const {
    long double a = 0;
    for(const OSegment<Number> &seg : segs)
      a += ((long double)(seg.source().x() + seg.target().x())) * (seg.source().y() - seg.target().y());
    return (double)(a / 1048576.0);
  }

  double area() const {
    return abs(signedArea());
  }

  bool clockwise() const {
    return signedArea() < 0;
  }

  OSegment<Number> diameter() const {
    OSegment<Number> best;
    for(size_t i = 0; i < verts.size() - 1; i++) {
      for(size_t j = i + 1; j < verts.size(); j++) {
        OSegment<Number> cur(verts[i],verts[j]);
        if(cur.squaredDistance() > best.squaredDistance())
          best = cur;
      }
    }
    return best.sorted();
  }

  OSegment<Number> longestEdge() const {
    OSegment<Number> best;
    for(const OSegment<Number> &cur : segs)
      if(cur.squaredDistance() > best.squaredDistance())
        best = cur;
    return best;
  }
};

template <class Number>
class ClippedPolygon {
  Polygon<Number> poly;
  Rectangle<Number> box, bbox;
public:
  ClippedPolygon(const Polygon<Number> &_poly, const Rectangle<Number> &_box) :
      poly{_poly}, box(_box), bbox(_box ^ poly.box()) {
  }

  Number getMaxX() const {
    return bbox.getMaxX();
  }

  Number getMaxY() const {
    return bbox.getMaxY();
  }

  Number getMinX() const {
    return bbox.getMinX();
  }

  Number getMinY() const {
    return bbox.getMinY();
  }

  template <class Other>
  bool contains(const Other &other) const {
    return box.contains(other) && poly.contains(other);
  }

  bool empty() const {
    return bbox.getMinX() >= bbox.getMaxX() || bbox.getMinY() >= bbox.getMaxY();
  }
};



// template <class Number>
// class PolygonIntersection {
//   std::vector<Polygon<Number>> polygons;
//   Rectangle<Number> bbox;
// public:
//   PolygonIntersection(const Polygon<Number> &poly) :
//       polygons{poly}, bbox(poly.bbox) {
//   }
//
//   PolygonIntersection(const std::vector<Polygon<Number>> &polys) :
//       polygons(polys), bbox(polys[0]) {
//     for(const Polygon<Number> & poly : polygons)
//       bbox = bbox ^ poly.bbox;
//   }
//
//   Number getMaxX() const {
//     return bbox.getMaxX();
//   }
//
//   Number getMaxY() const {
//     return bbox.getMaxY();
//   }
//
//   Number getMinX() const {
//     return bbox.getMinX();
//   }
//
//   Number getMinY() const {
//     return bbox.getMinY();
//   }
//
//   bool contains(const Polygon<Number> &poly) const {
//     for(const Polygon<Number> & poly2 : polygons)
//       if(!poly2.contains(poly))
//         return false;
//
//     return true;
//   }
// };
//



