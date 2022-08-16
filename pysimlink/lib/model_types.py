from dataclasses import dataclass
from pysimlink.utils import annotation_utils as anno


# These classes are provided for reference only.
@dataclass
class DataType:
    """
    Contains data type information for a single parameter.

    Attributes:
        cDataType (str): The c equivalent name of this datatype
        pythonType (str): The python name of this datatype
        dims (list[int]): List of dimension sizes. (the shape of the array)
        orientation (int): Enumeration indicating if this is a scalar, vector, column major or row major array.
            Since this enum is evaluated at compile time, it is imported from the compiled model. To check this value
            dynamically, use :attr:`pysimlink.Model.orientations`.
    """

    cDataType: str
    pythonType: str
    dims: "list[int]"
    orientation: int

    def __init__(self, obj: "anno.c_model_datatype"):
        self.cDataType = obj.cDataType
        self.pythonType = obj.pythonType
        self.dims = obj.dims
        self.orientation = obj.orientation

    def __repr__(self):
        return f"{self.pythonType} ({self.cDataType}) dims: {self.dims} order: {self.orientation}"


@dataclass
class ModelParam:
    """
    Represents a single model parameter.

    Attributes:
        model_param (str): Name of the model parameter (these are usually stored withing the model workspace in simulink)
        data_type (:class:`DataType`): data type object describing this parameter
    """

    model_param: str
    data_type: DataType

    def __init__(self, obj: "anno.c_model_param"):
        self.model_param = obj.model_param
        self.data_type = DataType(obj.data_type)


@dataclass
class BlockParam:
    """
    Represents a single parameter in a block.

    If a block has *n* parameters, there will be *n* BlockParam instances. Each with the same :code:`block_name`.

    Attributes:
        block_name (str): The name (usually including the path) to this block.
        block_param (str): The name of the parameter within the block
        data_type (:class:`DataType`): data type object describing this parameter
    """

    block_name: str
    block_param: str
    data_type: DataType

    def __init__(self, obj: "anno.c_model_block_param"):
        self.block_name = obj.block_name
        self.block_param = obj.block_param
        self.data_type = DataType(obj.data_type)


@dataclass
class Signal:
    """
    Represents a single signal in the model.

    Attributes:
        block_name: name and path to the block the signal originates from
        signal_name: name of the signal (empty if not named)
        data_type (:class:`DataType`): Data type information of this signal
    """

    block_name: str
    signal_name: str
    data_type: DataType

    def __init__(self, obj: "anno.c_model_signal"):
        self.block_name = obj.block_name
        self.signal_name = obj.signal_name
        self.data_type = DataType(obj.data_type)


@dataclass
class ModelInfo:
    """
    Object returned from :func:`pysimlink.Model.get_params`.

    .. note:: This object only describes a single model. If a Simulink model contains model references,
        :func:`pysimlink.Model.get_params` will return a list of this object, each describing a reference model.

    Attributes:
        model_name (str): Name of the model this object describes
        model_params (list[:class:`ModelParam`]): List of all model parameters
        block_params (list[:class:`BlockParam`]): List of all block parameters
        signals (list[:class:`Signal`]): List of all signals
    """

    model_name: str
    model_params: "list[ModelParam]"
    block_params: "list[BlockParam]"
    signals: "list[Signal]"

    def __init__(self, obj: "anno.c_model_info"):
        self.model_name = obj.model_name
        self.model_params = list(map(ModelParam, obj.model_params))
        self.block_params = list(map(BlockParam, obj.block_params))
        self.signals = list(map(Signal, obj.signals))
