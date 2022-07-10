#include "safe_utils.hpp"

std::string PYSIMLINK::safe_string(const char* chars){
    if(chars == nullptr){
        return {"Null"};
    }else{
        return {chars};
    }
}