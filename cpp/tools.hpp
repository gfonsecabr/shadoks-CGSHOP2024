#pragma once
#include <vector>

// https://stackoverflow.com/questions/6861089/how-to-split-a-vector-into-n-almost-equal-parts
template<typename T>
std::vector<std::vector<T>> splitVector(const std::vector<T>& vec, size_t n)
{
  std::vector<std::vector<T>> outVec;
  size_t length = vec.size() / n;
  size_t remain = vec.size() % n;
  size_t begin = 0, end = 0;

  for (size_t i = 0; i < std::min(n, vec.size()); ++i) {
    end += (remain > 0) ? (length + !!(remain--)) : length;
    outVec.push_back(std::vector<T>(vec.begin() + begin, vec.begin() + end));
    begin = end;
  }

  return outVec;
}

