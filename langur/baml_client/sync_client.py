###############################################################################
#
#  Welcome to Baml! To use this generated code, please run the following:
#
#  $ pip install baml
#
###############################################################################

# This file was generated by BAML: please do not edit it. Instead, edit the
# BAML files and re-generate this code.
#
# ruff: noqa: E501,F401
# flake8: noqa: E501,F401
# pylint: disable=unused-import,line-too-long
# fmt: off
from typing import Any, Dict, List, Optional, TypeVar, Union, TypedDict, Type, Literal, cast
from typing_extensions import NotRequired
import pprint

import baml_py
from pydantic import BaseModel, ValidationError, create_model

from . import partial_types, types
from .types import Checked, Check
from .type_builder import TypeBuilder
from .globals import DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_CTX, DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_RUNTIME

OutputType = TypeVar('OutputType')

# Define the TypedDict with optional parameters having default values
class BamlCallOptions(TypedDict, total=False):
    tb: NotRequired[TypeBuilder]
    client_registry: NotRequired[baml_py.baml_py.ClientRegistry]

class BamlSyncClient:
    __runtime: baml_py.BamlRuntime
    __ctx_manager: baml_py.BamlCtxManager
    __stream_client: "BamlStreamClient"

    def __init__(self, runtime: baml_py.BamlRuntime, ctx_manager: baml_py.BamlCtxManager):
      self.__runtime = runtime
      self.__ctx_manager = ctx_manager
      self.__stream_client = BamlStreamClient(self.__runtime, self.__ctx_manager)

    @property
    def stream(self):
      return self.__stream_client

    
    def CreateAssumptions(
        self,
        task: str,observables: str,
        baml_options: BamlCallOptions = {},
    ) -> List[types.Assumption]:
      __tb__ = baml_options.get("tb", None)
      if __tb__ is not None:
        tb = __tb__._tb
      else:
        tb = None
      __cr__ = baml_options.get("client_registry", None)

      raw = self.__runtime.call_function_sync(
        "CreateAssumptions",
        {
          "task": task,"observables": observables,
        },
        self.__ctx_manager.get(),
        tb,
        __cr__,
      )
      return cast(List[types.Assumption], raw.cast_to(types, types))
    
    def FillParams(
        self,
        context: str,action_desc: str,filled_inputs: str,needed_inputs: str,
        baml_options: BamlCallOptions = {},
    ) -> types.FilledParams:
      __tb__ = baml_options.get("tb", None)
      if __tb__ is not None:
        tb = __tb__._tb
      else:
        tb = None
      __cr__ = baml_options.get("client_registry", None)

      raw = self.__runtime.call_function_sync(
        "FillParams",
        {
          "context": context,"action_desc": action_desc,"filled_inputs": filled_inputs,"needed_inputs": needed_inputs,
        },
        self.__ctx_manager.get(),
        tb,
        __cr__,
      )
      return cast(types.FilledParams, raw.cast_to(types, types))
    
    def PlanActions(
        self,
        goal: str,observables: str,action_types: str,
        baml_options: BamlCallOptions = {},
    ) -> types.Graph:
      __tb__ = baml_options.get("tb", None)
      if __tb__ is not None:
        tb = __tb__._tb
      else:
        tb = None
      __cr__ = baml_options.get("client_registry", None)

      raw = self.__runtime.call_function_sync(
        "PlanActions",
        {
          "goal": goal,"observables": observables,"action_types": action_types,
        },
        self.__ctx_manager.get(),
        tb,
        __cr__,
      )
      return cast(types.Graph, raw.cast_to(types, types))
    
    def Think(
        self,
        context: str,description: str,
        baml_options: BamlCallOptions = {},
    ) -> str:
      __tb__ = baml_options.get("tb", None)
      if __tb__ is not None:
        tb = __tb__._tb
      else:
        tb = None
      __cr__ = baml_options.get("client_registry", None)

      raw = self.__runtime.call_function_sync(
        "Think",
        {
          "context": context,"description": description,
        },
        self.__ctx_manager.get(),
        tb,
        __cr__,
      )
      return cast(str, raw.cast_to(types, types))
    



class BamlStreamClient:
    __runtime: baml_py.BamlRuntime
    __ctx_manager: baml_py.BamlCtxManager

    def __init__(self, runtime: baml_py.BamlRuntime, ctx_manager: baml_py.BamlCtxManager):
      self.__runtime = runtime
      self.__ctx_manager = ctx_manager

    
    def CreateAssumptions(
        self,
        task: str,observables: str,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.BamlSyncStream[List[partial_types.Assumption], List[types.Assumption]]:
      __tb__ = baml_options.get("tb", None)
      if __tb__ is not None:
        tb = __tb__._tb
      else:
        tb = None
      __cr__ = baml_options.get("client_registry", None)

      raw = self.__runtime.stream_function_sync(
        "CreateAssumptions",
        {
          "task": task,
          "observables": observables,
        },
        None,
        self.__ctx_manager.get(),
        tb,
        __cr__,
      )

      return baml_py.BamlSyncStream[List[partial_types.Assumption], List[types.Assumption]](
        raw,
        lambda x: cast(List[partial_types.Assumption], x.cast_to(types, partial_types)),
        lambda x: cast(List[types.Assumption], x.cast_to(types, types)),
        self.__ctx_manager.get(),
      )
    
    def FillParams(
        self,
        context: str,action_desc: str,filled_inputs: str,needed_inputs: str,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.BamlSyncStream[partial_types.FilledParams, types.FilledParams]:
      __tb__ = baml_options.get("tb", None)
      if __tb__ is not None:
        tb = __tb__._tb
      else:
        tb = None
      __cr__ = baml_options.get("client_registry", None)

      raw = self.__runtime.stream_function_sync(
        "FillParams",
        {
          "context": context,
          "action_desc": action_desc,
          "filled_inputs": filled_inputs,
          "needed_inputs": needed_inputs,
        },
        None,
        self.__ctx_manager.get(),
        tb,
        __cr__,
      )

      return baml_py.BamlSyncStream[partial_types.FilledParams, types.FilledParams](
        raw,
        lambda x: cast(partial_types.FilledParams, x.cast_to(types, partial_types)),
        lambda x: cast(types.FilledParams, x.cast_to(types, types)),
        self.__ctx_manager.get(),
      )
    
    def PlanActions(
        self,
        goal: str,observables: str,action_types: str,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.BamlSyncStream[partial_types.Graph, types.Graph]:
      __tb__ = baml_options.get("tb", None)
      if __tb__ is not None:
        tb = __tb__._tb
      else:
        tb = None
      __cr__ = baml_options.get("client_registry", None)

      raw = self.__runtime.stream_function_sync(
        "PlanActions",
        {
          "goal": goal,
          "observables": observables,
          "action_types": action_types,
        },
        None,
        self.__ctx_manager.get(),
        tb,
        __cr__,
      )

      return baml_py.BamlSyncStream[partial_types.Graph, types.Graph](
        raw,
        lambda x: cast(partial_types.Graph, x.cast_to(types, partial_types)),
        lambda x: cast(types.Graph, x.cast_to(types, types)),
        self.__ctx_manager.get(),
      )
    
    def Think(
        self,
        context: str,description: str,
        baml_options: BamlCallOptions = {},
    ) -> baml_py.BamlSyncStream[Optional[str], str]:
      __tb__ = baml_options.get("tb", None)
      if __tb__ is not None:
        tb = __tb__._tb
      else:
        tb = None
      __cr__ = baml_options.get("client_registry", None)

      raw = self.__runtime.stream_function_sync(
        "Think",
        {
          "context": context,
          "description": description,
        },
        None,
        self.__ctx_manager.get(),
        tb,
        __cr__,
      )

      return baml_py.BamlSyncStream[Optional[str], str](
        raw,
        lambda x: cast(Optional[str], x.cast_to(types, partial_types)),
        lambda x: cast(str, x.cast_to(types, types)),
        self.__ctx_manager.get(),
      )
    

b = BamlSyncClient(DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_RUNTIME, DO_NOT_USE_DIRECTLY_UNLESS_YOU_KNOW_WHAT_YOURE_DOING_CTX)

__all__ = ["b"]