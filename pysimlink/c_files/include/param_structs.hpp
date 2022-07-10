#pragma once
#include <string>
#include <vector>

namespace PYSIMLINK{

    struct ModelParam{
        std::string model_param;
        std::string data_type;
    };

    struct BlockParam{
        std::string block_name;
        std::string block_param;
        std::string data_type;
    };

    struct Signal{
        std::string block_name;
        std::string signal_name;
        std::string data_type;
    };

    struct ModelInfo{
        std::string model_name;
        std::vector<struct ModelParam> model_params;
        std::vector<struct BlockParam> block_params;
        std::vector<struct Signal> signals;
    };
};
