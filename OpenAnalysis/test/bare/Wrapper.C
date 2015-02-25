#include <vector>
#include <string>
#include "Wrapper.h"

template struct edm::Wrapper<std::vector<int> > ;
template struct edm::Wrapper<std::vector<float> >;
template struct edm::Wrapper<std::vector<std::string> >;
