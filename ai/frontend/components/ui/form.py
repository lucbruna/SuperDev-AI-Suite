"""
Form UI Component
"""
from typing import Optional, Any, Callable, Dict, List
from dataclasses import dataclass, field
from enum import Enum


class FormLayout(Enum):
    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"
    INLINE = "inline"


class FormSize(Enum):
    SM = "sm"
    MD = "md"
    LG = "lg"


@dataclass
class FormField:
    name: str
    label: str
    type: str = "text"
    required: bool = False
    placeholder: str = ""
    helpText: Optional[str] = None
    rules: list = field(default_factory=list)
    initialValue: Any = None
    disabled: bool = False


@dataclass
class FormProps:
    fields: List[FormField] = field(default_factory=list)
    layout: FormLayout = FormLayout.VERTICAL
    size: FormSize = FormSize.MD
    initialValues: Dict[str, Any] = field(default_factory=dict)
    onSubmit: Optional[Callable] = None


class Form:
    def __init__(self, props: Optional[FormProps] = None):
        self.props = props or FormProps()
        self._values = self.props.initialValues.copy()
        self._errors = {}
        self._touched = set()
        
    def set_value(self, name, value):
        self._values[name] = value
        self._touched.add(name)
        self._validate_field(name)
        
    def get_value(self, name):
        return self._values.get(name)
        
    def _validate_field(self, name):
        field = next((f for f in self.props.fields if f.name == name), None)
        if not field:
            return
        value = self._values.get(name)
        if field.required and not value:
            self._errors[name] = field.label + " is required"
        else:
            self._errors.pop(name, None)
            
    def validate(self):
        self._errors = {}
        for field in self.props.fields:
            self._validate_field(field.name)
        return self.is_valid
        
    @property
    def is_valid(self):
        return len(self._errors) == 0
        
    @property
    def is_dirty(self):
        return self._values != self.props.initialValues
