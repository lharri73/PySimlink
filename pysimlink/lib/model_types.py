from dataclasses import dataclass


# These classes are provided for reference only.
@dataclass
class DataType:
    """
    Contains data type information for a single parameter
    """
    cDataType: str
    pythonType: str
    dims: "list[str]"
    orientation: int

    def __init__(self, obj: any): # initialize with model_interface_c datatype
        self.cDataType = obj.cDataType
        self.pythonType = obj.pythonType
        self.dims = obj.dims
        self.orientation = obj.orientation

    def __repr__(self):
        return f"{self.pythonType} ({self.cDataType}) dims: {self.dims} order: {self.orientation}"


@dataclass(frozen=True)
class ModelParam:
    """
    Represents a single model parameter
    """

    model_param: str
    data_type: DataType


@dataclass(frozen=True)
class BlockParam:
    """
    Represents a single parameter in a block.
    If a block has n parameters, there will be n BlockParam instances.
        Each with the same `block_name`.
    """

    block_name: str
    block_param: str
    data_type: DataType


@dataclass(frozen=True)
class Signal:
    """
    Represents a single signal in the model.

    block_name: path to the block the signal originates from
    signal_name: name of the signal (empty if not named)
    data_type: c_type data type
    """

    block_name: str
    signal_name: str
    data_type: DataType


@dataclass(frozen=True)
class ModelInfo:
    """
    Object returned from get_params method.
    """

    model_name: str
    model_params: "list[ModelParam]"
    block_params: "list[BlockParam]"
    signals: "list[Signal]"
