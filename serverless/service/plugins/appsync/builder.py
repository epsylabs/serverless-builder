import inspect
import re
import typing
from datetime import date, datetime
from enum import Enum
from functools import wraps
from pathlib import Path
from typing import List, Type, get_args, get_origin, get_type_hints

import strawberry
from aws_lambda_powertools.event_handler import AppSyncResolver
from pydantic import BaseModel
from pydantic_extra_types.phone_numbers import PhoneNumber
from strawberry.experimental.pydantic import input as strawberry_input
from strawberry.experimental.pydantic import type as strawberry_type
from strawberry.schema_directive import Location

from serverless.service.plugins.appsync.resolver import Resolver, ResolverManager


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


def resolve_wrapped(func):
    if hasattr(func, "__wrapped__"):
        return resolve_wrapped(func.__wrapped__)
    else:
        return func


def schema_directive(func, directive):
    org_func = resolve_wrapped(func)

    if not hasattr(org_func, "schema_directives"):
        org_func.schema_directives = []

    org_func.schema_directives.append(directive)

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    return wrapper


def aws_lambda(function: str):
    def decorator(func):
        @strawberry.schema_directive(locations=[Location.FIELD_DEFINITION, Location.OBJECT], name="aws_lambda")
        class Directive:
            function: str

        return schema_directive(func, Directive(function=function))

    return decorator


def aws_auth(cognito_groups: typing.List[str] = None):
    def decorator(func):
        @strawberry.schema_directive(locations=[Location.FIELD_DEFINITION], name="aws_auth")
        class Directive:
            cognito_groups: list[str] = strawberry.directive_field(name="cognito_groups")

        return schema_directive(func, Directive(cognito_groups=cognito_groups))

    return decorator


def aws_publish(subscriptions: typing.List[str] = None):
    def decorator(func):
        @strawberry.schema_directive(locations=[Location.FIELD_DEFINITION], name="aws_publish")
        class Directive:
            subscriptions: list[str]

        return schema_directive(func, Directive(subscriptions=subscriptions))

    return decorator


def aws_cognito_user_pools(cognito_groups: typing.List[str] = None):
    def decorator(func):
        @strawberry.schema_directive(
            locations=[Location.FIELD_DEFINITION, Location.INPUT_OBJECT, Location.OBJECT], name="aws_cognito_user_pools"
        )
        class Directive:
            cognito_groups: list[str] = strawberry.directive_field(name="cognito_groups")

        return schema_directive(func, Directive(cognito_groups=cognito_groups))

    return decorator


def aws_subscribe(func):
    @strawberry.schema_directive(locations=[Location.FIELD_DEFINITION], name="aws_subscribe")
    class Directive:
        pass

    return schema_directive(func, Directive())


def aws_iam(func):
    @strawberry.schema_directive(
        locations=[Location.OBJECT, Location.FIELD_DEFINITION, Location.INPUT_OBJECT], name="aws_iam"
    )
    class Directive:
        pass

    return schema_directive(func, Directive())


def aws_api_key(func):
    @strawberry.schema_directive(locations=[Location.OBJECT, Location.FIELD_DEFINITION], name="aws_api_key")
    class Directive:
        pass

    return schema_directive(func, Directive())


class SchemaBuilder:
    def __init__(self, resolver: AppSyncResolver, namespace=None):
        self.resolver = resolver
        self.namespace = namespace
        self.models = {}
        self._types = {strawberry_type: {}, strawberry_input: {}, Enum: {}}
        self._forced = []

    def add_type(self, model, forced=False):
        if issubclass(model, Enum):
            item = strawberry.enum(model)
            self._types[Enum][self._extract_name(model)] = item
        else:
            item = strawberry_type(model=model, all_fields=True)(type(model.__name__, (), {}))
            self._types[strawberry_type][self._extract_name(model)] = item

        if forced and item:
            self._forced.append(item)

        self.models[self._extract_name(model)] = model

        return self

    def add_input(self, model, forced=False):
        item = strawberry_input(model=model, all_fields=True)(type(model.__name__, (), {}))

        self._types[strawberry_input][self._extract_name(model)] = item

        if forced:
            self._forced.append(item)

        self.models[self._extract_name(model)] = model

        return self

    def import_types(self, models_module, forced=False):
        for model in self._get_pydantic_models(models_module):
            self.add_type(model, forced)

        return self

    def import_inputs(self, models_module, force=False):
        for model in self._get_pydantic_models(models_module):
            self.add(model, force)

        return self

    def render(self, output_file=None):
        manager = ResolverManager(self)
        for name, definition in self.resolver._resolver_registry.resolvers.items():
            parameters, output, directives = self._get_function_signature(definition["func"])

            if name in self.resolver._batch_resolver_registry.resolvers:
                parameters = []

            manager.register(Resolver(name, parameters, output, directives))

        content = str(
            strawberry.Schema(
                query=manager.query(self.namespace),
                mutation=manager.mutations(self.namespace),
                types=set(self._forced) if self._forced else (),
                scalar_overrides={PhoneNumber: AWSPhone, date: AWSDate, datetime: AWSDateTime},
            )
        )

        import __main__ as main

        content = re.sub(r"scalar AWS(DateTime|Phone|Date)\n+", "", content, 0, re.MULTILINE)
        content = re.sub(r"directive @.* on .*\n+", "", content, 0, re.MULTILINE)

        if not output_file:
            output_file = open(Path(main.__file__).stem + ".graphql", "w+")

        output_file.write(content)

    def as_output(self, pydantic_type: type[BaseModel], directives=None):
        return self.as_type(pydantic_type, strawberry_type, directives=directives)

    def as_input(self, pydantic_type: type[BaseModel]):
        return self.as_type(pydantic_type, strawberry_input)

    def as_type(self, pydantic_type: type[BaseModel], output_type, directives=None):
        resolver_type = pydantic_type

        is_list = get_origin(pydantic_type) == list
        if is_list:
            resolver_type = get_args(pydantic_type)[0]

        is_optional = get_origin(resolver_type) is typing.Union and type(None) in get_args(resolver_type)
        if is_optional:
            resolver_type = get_args(pydantic_type)[0]

        if issubclass(resolver_type, BaseModel):
            if resolver_type.__name__ in self._types[output_type]:
                resolved = self._types[output_type][resolver_type.__name__]

            else:
                resolved = output_type(model=resolver_type, all_fields=True, directives=directives)(
                    type(resolver_type.__name__, (), {})
                )

                self._types[output_type][resolver_type.__name__] = resolved
        else:
            resolved = resolver_type

        if is_list:
            resolved = typing.List[resolved]

        if is_optional:
            resolved = typing.Optional[resolved]

        return resolved

    def _extract_name(self, model):
        return model.__name__.split(".")[-1]

    def _get_pydantic_models(self, module) -> List[Type[BaseModel]]:
        return [
            obj
            for name, obj in inspect.getmembers(module)
            if inspect.isclass(obj) and issubclass(obj, BaseModel) and obj.__module__ == module.__name__
        ]

    def _get_directives(self, func):
        directives = []
        wrapped = func
        while wrapped:
            if hasattr(wrapped, "schema_directives"):
                directives.extend(wrapped.schema_directives)

            wrapped = getattr(wrapped, "__wrapped__", None)

        return directives

    def _get_function_signature(self, func):
        signature = inspect.signature(func)
        directives = self._get_directives(func)
        type_hints = get_type_hints(func)
        parameters = {param_name: type_hints.get(param_name, "No type hint") for param_name in signature.parameters}
        return_type = type_hints.get("return", "No return type hint")

        return parameters, return_type, directives
