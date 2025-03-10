from typing import get_args, get_origin

import strawberry
from strawberry.annotation import StrawberryAnnotation
from strawberry.types.arguments import StrawberryArgument
from strawberry.types.field import StrawberryField

from serverless.service import Identifier


class GraphQLTypes(object):
    @classmethod
    def add(cls, builder, name, parameters, type_hint, directives=None):
        field = StrawberryField(python_name=name, directives=directives or [])
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
    def __init__(self, name, parameters, output, directives=None):
        self.type, self.name = name.split(".")
        self.parameters = parameters
        self.output = output
        self.directives = directives

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
        if resolver.type.upper().endswith("MUTATION"):
            self._mutations[resolver.name] = resolver
        elif resolver.type.upper().endswith("QUERY"):
            self._queries[resolver.name] = resolver

    def _build_namespace(self, namespace, namespace_type="Query"):
        parts = namespace.split(".")

        if len(parts) > 2:
            raise Exception("Only two levels of nesting are supported")

        scope_type = type(Identifier(f"{parts[0]}{namespace_type}").pascal, (GraphQLTypes,), {})

        if len(parts) == 2:
            sub_scope_type = type(Identifier(f"{parts[1]}{namespace_type}").pascal, (GraphQLTypes,), {})
            scope_type.add(self.builder, parts[1], {}, strawberry.type(sub_scope_type))

            return scope_type, sub_scope_type

        return scope_type, scope_type

    def query(self, namespace=None):
        if not self._queries:
            return None

        container_type = Query
        if namespace:
            scope, container_type = self._build_namespace(namespace, "Query")

        for resolver in self._queries.values():
            container_type.add(
                self.builder,
                resolver.name,
                resolver.parameters,
                self.builder.as_output(resolver.output),
                resolver.directives,
            )

        if namespace:
            parts = namespace.split(".")
            Query.add(self.builder, parts[0], {}, strawberry.type(scope))

            if len(parts) == 2:
                scope.add(self.builder, parts[1], {}, strawberry.type(container_type))

        return strawberry.type(Query)

    def mutations(self, namespace=None):
        if not self._mutations:
            return None

        container_type = Mutation
        if namespace:
            scope, container_type = self._build_namespace(namespace, "Mutation")

        for resolver in self._mutations.values():
            container_type.add(
                self.builder, resolver.name, resolver.parameters, self.builder.as_output(resolver.output)
            )

        if namespace:
            parts = namespace.split(".")
            Mutation.add(self.builder, parts[0], {}, strawberry.type(scope))

            if len(parts) == 2:
                scope.add(self.builder, parts[1], {}, strawberry.type(container_type))

        return strawberry.type(Mutation)
