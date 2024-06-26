from abc import ABC, abstractmethod
import uuid
from typing import Any, Optional


class GUIBase(ABC):
    def __init__(self, width: int, height: int, parent):

        from research_analytics_suite.utils import CustomLogger
        self._logger = CustomLogger()

        from research_analytics_suite.utils import Config
        self._config = Config()

        from research_analytics_suite.operation_manager.control.OperationControl import OperationControl
        self._operation_control = OperationControl()

        self._parent = parent
        self._width = width
        self._height = height
        self._unique_id = str(uuid.uuid4())
        self._runtime_id = str(uuid.uuid4())
        self._update_operation = None

    @property
    def parent(self) -> Optional[Any]:
        return self._parent

    @parent.setter
    def parent(self, value: Optional[Any]) -> None:
        self._parent = value

    @property
    def width(self) -> int:
        return self._width

    @width.setter
    def width(self, value: int or float) -> None:
        if value < 0:
            raise ValueError("width must be a positive integer or float.")

        from math import floor
        value = floor(value)

        self._width = value

    @property
    def height(self) -> int:
        return self._height

    @height.setter
    def height(self, value: int) -> None:
        if value < 0:
            raise ValueError("height must be a positive integer.")

        from math import floor
        value = floor(value)

        self._height = value

    @property
    def unique_id(self) -> str:
        return self._unique_id

    @property
    def runtime_id(self) -> str:
        return self._runtime_id

    def get_element_height(self) -> int:
        return self._height

    def get_element_width(self) -> int:
        return self._width

    @abstractmethod
    def draw(self) -> None:
        pass

    @abstractmethod
    async def initialize_gui(self) -> None:
        pass

    @abstractmethod
    async def _update_async(self) -> None:
        pass

    @abstractmethod
    async def resize_gui(self, new_width: int, new_height: int) -> None:
        pass
