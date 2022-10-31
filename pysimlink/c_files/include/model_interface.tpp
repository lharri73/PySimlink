
template <typename T>
    void Model::set_block_param(const std::string &model, const std::string &block_path, const std::string &param,
                                py::array_t<T> value) {
        if(!initialized){
            throw std::runtime_error("Model must be initialized before calling get_block_param. Call `reset()` first!");
        }
        if(block_path.empty())
            throw std::runtime_error("No path provided to get_block_param!");
        if(model.empty())
            throw std::runtime_error("No model name provided to get_block_param!");
        if(param.empty())
            throw std::runtime_error("No parameter provided to get_block_param!");
        auto mmi_idx = mmi_map.find(model);
        if(mmi_idx == mmi_map.end()){
            char buf[512];
            sprintf(buf, "Cannot find model with name: %s", model.c_str());
            throw std::runtime_error(buf);
        }
        PYSIMLINK::set_block_param(mmi_idx->second, block_path.c_str(), param.c_str(), value);
    }

    template <typename T>
    void Model::set_model_param(const std::string &model, const std::string &param, py::array_t<T> value) {
        if(!initialized){
            throw std::runtime_error("Model must be initialized before calling get_block_param. Call `reset()` first!");
        }
        if(model.empty())
            throw std::runtime_error("No model name provided to get_block_param!");
        if(param.empty())
            throw std::runtime_error("No parameter provided to get_block_param!");
        auto mmi_idx = mmi_map.find(model);
        if(mmi_idx == mmi_map.end()){
            char buf[256];
            sprintf(buf, "Cannot find model with name: %s", model.c_str());
            throw std::runtime_error(buf);
        }
        PYSIMLINK::set_model_param(mmi_idx->second, param.c_str(), value);
    }
