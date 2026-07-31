"""
Input UI Component
"""
from typing import Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


class InputType(Enum):
    TEXT = "text"
    EMAIL = "email"
    PASSWORD = "password"
    NUMBER = "number"
    TEL = "tel"
    URL = "url"
    SEARCH = "search"
    DATE = "date"


class InputSize(Enum):
    SM = "sm"
    MD = "md"
    LG = "lg"


@dataclass
class InputProps:
    type: InputType = InputType.TEXT
    size: InputSize = InputSize.MD
    placeholder: str = ""
    value: str = ""
    label: Optional[str] = None
    helper_text: Optional[str] = None
    error: Optional[str] = None
    disabled: bool = False
    readonly: bool = False
    required: bool = False
    maxLength: Optional[int] = None
    minLength: Optional[int] = None
    onChange: Optional[Callable] = None


class Input:
    def __init__(self, props: Optional[InputProps] = None):
        self.props = props or InputProps()
        self._value = self.props.value
        self._errors = []
        
    @property
    def value(self):
        return self._value
        
    @value.setter
    def value(self, val):
        self._value = val
        self._validate()
        if self.props.onChange:
            self.props.onChange(val)
            
    def _validate(self):
        self._errors = []
        if self.props.required and not self._value:
            self._errors.append("Field is required")
        if self.props.minLength and len(self._value) < self.props.minLength:
            self._errors.append("Minimum length is " + str(self.props.minLength))
        if self.props.maxLength and len(self._value) > self.props.maxLength:
            self._errors.append("Maximum length is " + str(self.props.maxLength))
            
    def is_valid(self):
        return len(self._errors) == 0
        
    def get_errors(self):
        return self._errors
