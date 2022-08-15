import typing

if typing.TYPE_CHECKING:
    from pysimlink.lib.model_types import ModelInfo
    from pysimlink.lib.dependency_graph import DepGraph
    from pysimlink.lib.model_paths import ModelPaths
    from pysimlink.lib.compilers.compiler import Compiler
    from pysimlink.lib.model import Model
    from typing import Union
    from numpy import ndarray
    from typing import Optional

    c_model_info = typing.Any
    c_model_param = typing.Any
    c_model_datatype = typing.Any
    c_model_signal = typing.Any
    c_model_block_param = typing.Any
