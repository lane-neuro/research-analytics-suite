from abc import ABC, abstractmethod
import dearpygui.dearpygui as dpg


class AbstractDialog(ABC):
    def __init__(self, width: int = 800, height: int = 600):
        self.width = width
        self.height = height

    @abstractmethod
    def draw(self, parent: str):
        pass

    def show(self, title: str, tag: str):
        with dpg.window(label=title, tag=tag, width=self.width, height=self.height):
            self.draw(parent=tag)

    def close(self, tag: str):
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)
