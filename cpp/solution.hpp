#pragma once

#include <iostream>
#include <string>
#include <map>
#include <chrono>

#include "geometry.hpp"
#include "instance.hpp"
#include "rapidjson/reader.h"
#include "rapidjson/document.h"
#include "rapidjson/istreamwrapper.h"

i64 getValueVector(const std::vector<Item> &items) {
  i64 val = 0;

  for(Item item : items)
    val += item.value;
  return val;
}

class Solution {
public:
  std::vector<Item> items;
  Instance *inst;
  std::string path;
  mutable std::string tmpFile;

public:
  Solution(Instance *_inst) : inst(_inst) {}

  Solution(std::string fn, Instance &_inst, std::string ipath = "../instances/"){
    rapidjson::Document doc = Instance::read_json(fn);
    std::string name = doc["instance_name"].GetString();
    _inst = Instance(ipath + name + ".cgshop2024_instance.json");
    inst = &_inst;
    inst->meta["source_solution"] = fn;
    std::vector<i64> ind = Instance::json_int_vec(doc["item_indices"]);
    std::vector<i64> xtr = Instance::json_int_vec(doc["x_translations"]);
    std::vector<i64> ytr = Instance::json_int_vec(doc["y_translations"]);
    for(int i = 0; i < ind.size(); i++) {
      i64 id = ind[i];
      Item item = inst->items[id] + Point<i64>(xtr[i],ytr[i]);
      items.push_back(item);
    }
  }

  i64 getValue() const {
    return getValueVector(items);
  }

  std::string writeSol(std::string type = "", bool quiet = false) const {
    if(tmpFile.size()) {
      std::remove(tmpFile.c_str());
      tmpFile.clear();
    }

    inst->meta["end_time"] = timeString();
    inst->meta["elapsed_sec"] = std::to_string(elapsed());
    int pos = inst->name.find(".");
    std::string instance_short = inst->name.substr(0, pos);
    std::string filename = path + instance_short + ".gdf." + timeString();
    if(!type.empty())
      filename = filename + "." + type;
    filename += ".sol.json";

    if (!quiet)
      std::cout << "=" << getValue() << "=> " << filename << std::endl;

    std::ofstream file(filename, std::fstream::out | std::ifstream::binary);

    file << "{" << std::endl;
    file << "\t\"type\": \"cgshop2024_solution\"," << std::endl;
    file << "\t\"instance_name\": \"" << inst->name << "\"," << std::endl;
    file << "\t\"num_included_items\": " << items.size() << "," << std::endl;
    file << "\t\"meta\": {" << std::endl;
    int i = 0;
    for(auto const& [key, val] : inst->meta) {
      file << "\t\t\"" << key << "\": \"" << val << "\"";
      if(i < inst->meta.size() - 1)
        file << ",";
      file << std::endl;
      i++;
    }
    file << "\t}," << std::endl;

    file << "\t\"item_indices\": [";
    int itemc = 0;
    for(const Item &item : items) {
      file << item.id;
      if (++itemc < items.size())
        file << ",";
    }
    file << "]," << std::endl;

    file << "\t\"x_translations\": [";
    itemc = 0;
    for(const Item &item : items) {
      file << item.translation.x();
      if (++itemc < items.size())
        file << ",";
    }
    file << "]," << std::endl;

    file << "\t\"y_translations\": [";
    itemc = 0;
    for(const Item &item : items) {
      file << item.translation.y();
      if (++itemc < items.size())
        file << ",";
    }
    file << "]" << std::endl;

    file << "}" << std::endl;
    file.close();
    return filename;
  }

  std::vector<Item> unplacedItems() const {
    std::vector<int> placedIds(inst->ndiff);
    for(const Item &item : items)
      placedIds[item.id]++;

    std::vector<Item> ret;
    for(int i = 0; i < inst->items.size(); i++)
      for(int j = 0; j < inst->items[i].quantity - placedIds[i]; j++)
        ret.push_back(inst->items[i]);

    return ret;
  }

  bool improve(const std::vector<Item> &newItems) {
    if(getValueVector(newItems) >= getValue()) {
      items = newItems;
      tmpFile = writeSol("tmp");
      return true;
    }
    return false;
  }
};
