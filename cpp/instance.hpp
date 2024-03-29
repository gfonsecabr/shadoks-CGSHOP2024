#pragma once

#include <iostream>
#include <string>
#include <map>
#include <chrono>
#include <unistd.h>

#include "geometry.hpp"
#include "rapidjson/reader.h"
#include "rapidjson/document.h"
#include "rapidjson/istreamwrapper.h"

auto beginTime = std::chrono::high_resolution_clock::now();

double elapsed() {
  auto end = std::chrono::high_resolution_clock::now();
  auto dur = std::chrono::duration_cast<std::chrono::milliseconds>(end - beginTime);

  return dur.count() / 1000.0;
}

using i64 = long long int;

std::string timeString(std::chrono::system_clock::time_point tp = std::chrono::system_clock::now()) {
  std::time_t tt = std::chrono::system_clock::to_time_t(tp);
  struct std::tm * ptm = std::localtime(&tt);
  std::ostringstream oss;
  oss << std::put_time(ptm, "%Y%m%d-%H%M%S");
  std::string s = oss.str();
  return s;
}

struct Item {
  Polygon<i64> shape;
  Point<i64> translation;
  i64 value = 0;
  double area = 0;
  int quantity = 0;
  int id = -1;
  // int available = 0;

  Item operator+(Point<i64> v) const {
    Item ret;
    ret.shape = shape + v;
    ret.quantity = quantity;
    ret.value = value;
    ret.id = id;
    ret.area = area;
    ret.translation = translation + v;
    return ret;
  }

  bool operator==(const Item &item) {
    return id == item.id && translation == item.translation;
  }
};

class Instance {
public:
  std::string name;
  Polygon<i64> container;
  std::vector<Item> items;
  int ndiff, nitems;
  mutable std::map<std::string, std::string> meta;

public:
  Instance() {}

  Instance(std::string fn) {
    meta["start_time"] = timeString();
    meta["author"] = "gdf";
    char hn[80];
    gethostname(hn, 80);
    meta["host"] = std::string(hn);
    rapidjson::Document doc = read_json(fn);
    name = doc["instance_name"].GetString();
    container = json_polygon(doc["container"]);
    nitems = 0;
    for(auto &itemjs : doc["items"].GetArray()) {
      Item item = json_item(itemjs);

      item.id = items.size();
      // std::cout << item.id << " " << item.area << std::endl;
      items.push_back(item);
      assert(item.shape.getMinX() == 0);
      assert(item.shape.getMinY() == 0);
      nitems += item.quantity;
    }
    ndiff = items.size();
  }

  static rapidjson::Document read_json(std::string filename) {
    std::ifstream in(filename, std::ifstream::in | std::ifstream::binary);
    if (!in.is_open()) {
      std::cerr << "Error reading " << filename << std::endl;
      assert(false);
      exit(EXIT_FAILURE);
    }

    rapidjson::IStreamWrapper isw {in};
    rapidjson::Document doc {};
    doc.ParseStream(isw);

    if (doc.HasParseError()) {
      std::cerr << "Error  : " << doc.GetParseError()  << std::endl;
      std::cerr << "Offset : " << doc.GetErrorOffset() << std::endl;
      exit(EXIT_FAILURE);
    }
    return doc;
  }

  static std::vector<i64> json_int_vec(rapidjson::Value &values) {
    std::vector<i64> v;
    for (auto &x : values.GetArray())
      v.push_back((int)x.GetDouble());
    return v;
  }

  static Polygon<i64> json_polygon(rapidjson::Value &values) {
    std::vector<i64> xs = json_int_vec(values["x"]);
    std::vector<i64> ys = json_int_vec(values["y"]);
    std::vector<Point<i64>> points;
    for(int i = 0; i < xs.size(); i++)
      points.push_back(Point(xs[i],ys[i]));

    return Polygon<i64>(points);
  }

  static Item json_item(rapidjson::Value &values) {
    Item item;
    item.shape = json_polygon(values);
    item.quantity = values["quantity"].GetDouble();
    item.value = values["value"].GetDouble();
    item.area = item.shape.area();
    assert(item.area > 0.0);

    return item;
  }
};

class Message {
  double t0;
  std::string id;
  static inline int depth = 0, line = 0;
  static inline bool openline = false;
  int myline = 0;
public:
  static inline Instance *instance;
  Message(const std::string &_id, const std::string &m = "") {
    if(openline)
      newline();
    t0 = elapsed();
    myline = line;
    id = _id;
    indent();
    depth++;
    if(m.empty())
      std::cout << id << " " << std::flush;
    else
      std::cout << m << " " << std::flush;
    openline = true;
  }

  void newline() {
    std::cout << std::endl;
    line++;
    myline = line;
    openline = false;
  }

  void indent() {
    for(int i = 0; i < depth; i++)
      std::cout << " ";
    std::cout << instance->name << "> ";
  }

  void maybenewline() {
    if(line != myline && openline) {
      newline();
      indent();
    }
  }

  template<class T>
  void out(std::string key, const T &m, bool show = true) {
    std::ostringstream ss;
    ss << m;
    if(show) {
      maybenewline();
      std::cout << key << "=" << ss.str() << " " << std::flush;
    }
    std::string idkey = id + "_" + key;
    if(instance->meta.contains(idkey))
      instance->meta[idkey] += "; ";
    instance->meta[idkey] += ss.str();
  }

  template<class T>
  double close(const T &m) {
    std::ostringstream ss;
    ss << m;
    double t = elapsed() - t0;
    out("sec", t, t > 1.0);
    maybenewline();
    std::cout << "-> " << m << std::flush;
    newline();
    if(instance->meta.contains(id))
      instance->meta[id] += "; ";
    instance->meta[id] += ss.str();
    depth--;
    return t;
  }
};


