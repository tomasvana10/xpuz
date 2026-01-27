import sys
import inspect

def get_class_annotations(cls: type):
    if sys.version_info >= (3, 10):
        return inspect.get_annotations(cls)
    
    return cls.__dict__["__annotations__"]
