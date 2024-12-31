from typing import get_origin, get_args

import strawberry
from strawberry.annotation import StrawberryAnnotation
from strawberry.types.arguments import StrawberryArgument
from strawberry.types.field import StrawberryField


class GraphQLTypes(object):
    @classmethod
    def add(cls, builder, name, parameters, type_hint):
        field = StrawberryField(python_name=name)
        field.arguments = [
            StrawberryArgument(
                python_name=name,
                graphql_name=name,
                type_annotation=StrawberryAnnotation(annotation=builder.as_input(ptype)),
            )
            for name, ptype in parameters.items()
        ]

        setattr(cls, name, field)
        cls.__annotations__[name] = type_hint


class Query(GraphQLTypes):
    pass


class Mutation(GraphQLTypes):
    pass


class Resolver(object):
    def __init__(self, name, parameters, output):
        self.type, self.name = name.split(".")
        self.parameters = parameters
        self.output = output

    @property
    def inner_type(self):
        output_type = self.output

        if get_origin(output_type) is list:
            output_type = get_args(output_type)[0]

        return output_type


class ResolverManager(object):
    def __init__(self, builder):
        self.builder = builder
        self._queries = {}
        self._mutations = {}

    def register(self, resolver):
        if resolver.type.upper() == "QUERY":
            self._queries[resolver.name] = resolver
        elif resolver.type.upper() == "MUTATION":
            self._mutations[resolver.name] = resolver

    def query(self):
        if not self._queries:
            return None

        for resolver in self._queries.values():
            Query.add(self.builder, resolver.name, resolver.parameters, self.builder.as_output(resolver.output))

        return strawberry.type(Query)

    def types(self):
        types = ()
        for resolver in [*self._queries.values()]:  # , *self._mutations.values()]:
            resolver_type = resolver.output
            if get_origin(resolver_type) is list:
                resolver_type = get_args(resolver_type)[0]

            types += (self.builder.as_output(resolver_type),)

        return types

    def mutations(self):
        if not self._mutations:
            return None

        for resolver in self._mutations.values():
            Mutation.add(self.builder, resolver.name, resolver.parameters, self.builder.as_output(resolver.output))

        return strawberry.type(Mutation)
