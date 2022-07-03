#include "model_utils.hpp"
#include <utility>
#include <string>
#include <functional>
#include <tuple>

namespace PYSIMLINK{

    std::size_t pair_hash::operator()(const map_key_2s &p) const{
        size_t a = std::hash<std::string>{}(p.a);
        size_t b = std::hash<std::string>{}(p.b);
        size_t c = std::hash<void*>{}((void*)p.c);

        size_t combined = a+b+c;
        return combined;
    }

    std::size_t pair_hash::operator()(const map_key_1s &p) const{
        size_t a = std::hash<std::string>{}(p.a);
        size_t b = std::hash<void*>{}((void*)p.c);

        return a+b;
    }

    bool Compare::operator()(const map_key_2s &lhs, const map_key_2s &rhs) const{
        return lhs == rhs;
    }
    bool Compare::operator()(const map_key_1s &lhs, const map_key_1s &rhs) const{
        return lhs==rhs;
    }
};
