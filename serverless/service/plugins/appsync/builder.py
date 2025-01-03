import inspect
import re
import typing
from datetime import date, datetime
from enum import Enum
from pathlib import Path
from typing import get_type_hints, List, Type, get_args, get_origin

import strawberry
from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber
from strawberry.experimental.pydantic import input as strawberry_input
from strawberry.experimental.pydantic import type as strawberry_type

from serverless.service.plugins.appsync.resolver import ResolverManager, Resolver


@strawberry.scalar
class AWSPhone:
    @staticmethod
    def serialize(value: PhoneNumber) -> str:
        return str(value)

    @staticmethod
    def parse_value(value: str) -> PhoneNumber:
        return PhoneNumber(value)


@strawberry.scalar
class AWSDate:
    @staticmethod
    def serialize(value: date) -> str:
        return str(value)

    @staticmethod
    def parse_value(value: str) -> date:
        return date.fromisoformat(value)


@strawberry.scalar
class AWSDateTime:
    @staticmethod
    def serialize(value: datetime) -> str:
        return value.isoformat()

    @staticmethod
    def parse_value(value: str) -> datetime:
        return datetime.fromisoformat(value)


class SchemaBuilder:
    def __init__(self, resolver, namespace=None):
        self.resolver = resolver
        self.namespace = namespace
        self.models = {}
        self._types = {strawberry_type: {}, strawberry_input: {}, Enum: {}}

    def add_type(self, model):
        if issubclass(model, Enum):
            self._types[Enum][self._extract_name(model)] = strawberry.enum(model)
        else:
            self._types[strawberry_type][self._extract_name(model)] = strawberry_type(model=model, all_fields=True)(
                type(model.__name__, (), {})
            )

        self.models[self._extract_name(model)] = model

        return self

    def add_input(self, model):
        self._types[strawberry_input][self._extract_name(model)] = strawberry_input(model=model, all_fields=True)(
            type(model.__name__, (), {})
        )

        self.models[self._extract_name(model)] = model

        return self

    def import_types(self, models_module):
        for model in self._get_pydantic_models(models_module):
            self.add_type(model)

        return self

    def import_inputs(self, models_module):
        for model in self._get_pydantic_models(models_module):
            self.add_input(model)

        return self

    def render(self):
        manager = ResolverManager(self)

        for name, definition in self.resolver._resolver_registry.resolvers.items():
            parameters, output = self._get_function_signature(definition["func"])

            manager.register(Resolver(name, parameters, output))

        content = str(
            strawberry.Schema(
                query=manager.query(self.namespace),
                mutation=manager.mutations(self.namespace),
                scalar_overrides={PhoneNumber: AWSPhone, date: AWSDate, datetime: AWSDateTime},
            )
        )

        import __main__ as main

        content = re.sub(r"scalar AWS(DateTime|Phone|Date)\n+", "", content, 0, re.MULTILINE)

        with open(Path(main.__file__).stem + ".graphql", "w+") as f:
            f.write(content)

    def as_output(self, pydantic_type: type[BaseModel]):
        return self.as_type(pydantic_type, strawberry_type)

    def as_input(self, pydantic_type: type[BaseModel]):
        return self.as_type(pydantic_type, strawberry_input)

    def as_type(self, pydantic_type: type[BaseModel], output_type):
        resolver_type = pydantic_type

        if get_origin(pydantic_type) is list:
            resolver_type = get_args(pydantic_type)[0]

        if issubclass(resolver_type, BaseModel):
            if resolver_type.__name__ in self._types[output_type]:
                return self._types[output_type][resolver_type.__name__]

            resolved = output_type(model=resolver_type, all_fields=True)(type(resolver_type.__name__, (), {}))

            self._types[output_type][resolver_type.__name__] = resolved
        else:
            resolved = resolver_type

        if get_origin(pydantic_type) is list:
            return typing.List[resolved]

        return resolved

    def _extract_name(self, model):
        return model.__name__.split(".")[-1]

    def _get_pydantic_models(self, module) -> List[Type[BaseModel]]:
        return [
            obj
            for name, obj in inspect.getmembers(module)
            if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj.__module__ == module.__name__
        ]

    def _get_function_signature(self, func):
        signature = inspect.signature(func)

        type_hints = get_type_hints(func)

        parameters = {param_name: type_hints.get(param_name, "No type hint") for param_name in signature.parameters}

        return_type = type_hints.get("return", "No return type hint")

        return parameters, return_type
