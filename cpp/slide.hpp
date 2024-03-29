#pragma once
#include "grid.hpp"

i64 minDot(Point<i64> dir, const Item &item) {
  i64 ret = item.shape[0] * dir;
  for(int i = 1; i < item.shape.size(); i++) {
    i64 val = item.shape[i]*dir;
    if(val < ret)
      ret = val;
  }
  return ret;
}

i64 maxDot(Point<i64> dir, const Item &item) {
  i64 ret = item.shape[0] * dir;
  for(int i = 1; i < item.shape.size(); i++) {
    i64 val = item.shape[i]*dir;
    if(val > ret)
      ret = val;
  }
  return ret;
}

template<class CONT>
i64 slideOneExp(int idx, const Item &item, Point<i64> dir, Grid &grid, const CONT &container, int disp0 = 1) {
  i64 disp = disp0;
  while(true) {
    Polygon<i64> displaced = item.shape + dir * disp;
    if(!container.contains(displaced) || !grid.interiorDisjoint(displaced, idx)) {
      if(disp == disp0)
        disp = 0;
      else
        disp /= 2;
      break;
    }
    disp *= 2;
  }
  // grid.replace(idx, item + dir * disp);
  return disp;
}

template<class CONT>
i64 slideOne(int idx, const Item &item, Point<i64> dir, Grid &grid, const CONT &container, int disp0 = 1) {
  disp0 = slideOneExp(idx, item, dir, grid, container, disp0);
  i64 disp1 = 2 * disp0;
  while(disp1 - disp0 > 1) {
    i64 disp = (disp0 + disp1) / 2;
    Polygon<i64> displaced = item.shape + dir * disp;
    if(!container.contains(displaced) || !grid.interiorDisjoint(displaced, idx))
      disp1 = disp;
    else
      disp0 = disp;
  }
  // grid.replace(idx, item + dir * disp0);
  return disp0;
}


template<class CONT>
i64 slideAllExp(Point<i64> dir, std::vector<Item> &items, const CONT &container, int disp0 = 1) {
  i64 ret = 0;
  std::uniform_int_distribution rndbool(0, 1);

  if(rndbool(rgen))
    std::sort(items.begin(), items.end(),
              [&dir](const Item &a, const Item &b){
                return minDot(dir,a) > minDot(dir,b);
              });
  else
    std::sort(items.begin(), items.end(),
              [&dir](const Item &a, const Item &b){
                return maxDot(dir,a) > maxDot(dir,b);
              });

  Grid grid(items);

  for(int i = 0; i < grid.size(); i++) {
    i64 disp = slideOneExp(i, items[i], dir, grid, container, disp0);
    grid.replace(i, items[i] + dir * disp);
    ret += disp;
  }

  items = grid.getItems();
  return ret;
}

template<class CONT>
i64 slideAll(Point<i64> dir, std::vector<Item> &items, const CONT &container, int disp0 = 1) {
  i64 ret = 0;
  std::uniform_int_distribution rndbool(0, 1);

  if(rndbool(rgen))
    std::sort(items.begin(), items.end(),
              [&dir](const Item &a, const Item &b){
                return minDot(dir,a) > minDot(dir,b);
              });
  else
    std::sort(items.begin(), items.end(),
              [&dir](const Item &a, const Item &b){
                return maxDot(dir,a) > maxDot(dir,b);
              });

  Grid grid(items);

  for(int i = 0; i < grid.size(); i++) {
    i64 disp = slideOne(i, items[i], dir, grid, container, disp0);
    grid.replace(i, items[i] + dir * disp);
    ret += disp;
  }

  items = grid.getItems();
  return ret;
}

template<class CONT>
i64 keepSliding(Point<i64> dir, std::vector<Item> &items, const CONT &container) {
  i64 totalSlide;
  int i = 0;
  do {
    totalSlide = slideAll(dir, items, container);

    slideAllExp(!dir, items, container);

    totalSlide += slideAll(dir, items, container);

    slideAllExp(!!!dir, items, container, 3);
  } while(totalSlide > 0 && i++ < 32);

  return totalSlide;
}

template<class CONT>
bool minYInside(Item &item, const CONT &container) {
  Point<i64> dir = Point<i64>(0,1);
  i64 deltay = container.getMaxY() / 1024;
  i64 y1 = container.getMaxY();
  i64 y0;
  for(y0 = 0; y0 <= y1; y0 += deltay) {
    Polygon<i64> displaced = item.shape + dir * y0;
    if(container.contains(displaced))
      break;
  }

  if(y0 > y1)
    return false;
  y1 = y0;
  y0 = 0;

  while(y1 - y0 > 1) {
    i64 y = (y0 + y1) / 2;
    Polygon<i64> displaced = item.shape + dir * y;
    if(!container.contains(displaced))
      y0 = y;
    else
      y1 = y;
  }

  item = item + dir * y1;

  return true;
}

template<class CONT>
bool maxSlide(Item &item, std::vector<Item> &placed, const CONT &container) {
  Grid grid(placed);
  // grid.showStats();
  i64 maxX = container.getMaxX() - item.shape.getMaxX() + 1;
  i64 deltax = container.getMaxX() / 1024;
  const Point<i64> up = Point<i64>(0,1);

  Point<i64> best(-1,-1);

  for(i64 x = 0; x < maxX; x += deltax) {
    Item itemx = item + Point<i64>(x,0);
    if(minYInside(itemx, container)) {
      if(grid.interiorDisjoint(itemx.shape, -1)) {
        i64 disp = slideOne(-1, itemx, up, grid, container);
        itemx = itemx + up * disp;
        if(itemx.translation.y() > best.y()) {
          best = itemx.translation;
        }
      }
    }
  }

  if(best.x() != -1) {
    item = item + best;
    return true;
  }

  return false;
}




















