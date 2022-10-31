template <typename T>
void validate_scalar(const rtwCAPI_ModelMappingInfo *mmi, T param, const char* funcName, const char* identifier){
    rtwCAPI_DimensionMap sigDim = mmi->staticMap->Maps.dimensionMap[param.dimIndex];
    rtwCAPI_DataTypeMap dt = mmi->staticMap->Maps.dataTypeMap[param.dataTypeIndex];

    if(sigDim.orientation != rtwCAPI_Orientation::rtwCAPI_SCALAR){
        std::stringstream err("");
        err << funcName << ": signal (" << identifier << ") has too many dimensions(" << (int)sigDim.numDims;
        err << ") or is not a scalar(" << sigDim.orientation << ")";
        throw std::runtime_error(err.str().c_str());
    }
    if(dt.isPointer){
        std::stringstream err("");
        err << funcName << ": Cannot read value from pointer (isPointer=True) for parameter (" << identifier << ")";
        throw std::runtime_error(err.str().c_str());
    }
}
template <typename T>
struct DataType populate_dtype(const rtwCAPI_ModelMappingInfo *mmi, T capi_struct){
    struct DataType ret;
    ret.cDataType = rtwCAPI_GetDataTypeMap(mmi)[capi_struct.dataTypeIndex].cDataName;
    ret.pythonType = PYSIMLINK::translate_c_type_name(ret.cDataType);
    ret.mwDataType = rtwCAPI_GetDataTypeMap(mmi)[capi_struct.dataTypeIndex].mwDataName;
    ret.orientation = rtwCAPI_GetDimensionMap(mmi)[capi_struct.dimIndex].orientation;
    for(size_t j = 0; j < rtwCAPI_GetDimensionMap(mmi)[capi_struct.dimIndex].numDims; j++){
        ret.dims.push_back(rtwCAPI_GetDimensionArray(mmi)[rtwCAPI_GetDimensionMap(mmi)[capi_struct.dimIndex].dimArrayIndex + j]);
    }
    return ret;
}