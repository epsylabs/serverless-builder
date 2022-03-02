from serverless.service.types import YamlOrderedDict


class Stage(YamlOrderedDict):
    yaml_tag = "!Stage"

    def __init__(self, type, function=None):
        self.Type = type
        self._function = function

    def next(self, stage):
        self.Next = stage.id

    @property
    def id(self):
        return self._function.key

    @classmethod
    def to_yaml(cls, dumper, data):
        data.pop("_function", None)
        return super().to_yaml(dumper, data)


class Fallback(Stage):
    yaml_tag = "!Fallback"

    def __init__(self, name, result):
        super().__init__("Pass")
        self.Result = result
        self.End = True
        self._name = name

    @property
    def id(self):
        return self._name

    @classmethod
    def to_yaml(cls, dumper, data):
        data.pop("_name")
        return super().to_yaml(dumper, data)


class Task(Stage):
    yaml_tag = "!Task"

    def __init__(self, function, end=None):
        super().__init__("Task", function)

        self.Resource = function.arn()
        if end is not None:
            self.End = end


class Iterator(YamlOrderedDict):
    yaml_tag = "!Iterator"

    def __init__(self, map_name, steps):
        self.States = {step.id: step for step in steps}
        self.map_name = map_name

    @classmethod
    def to_yaml(cls, dumper, data):
        data["StartAt"] = list(data.States.keys())[0]
        data.move_to_end("StartAt", last=False)

        fallback = None
        for step in data.States.values():
            if step.get("Type") in ("Pass", "Fail"):
                fallback = step
                break

        if not fallback:
            fallback = Fallback(f"{data.map_name}Fallback", f"Failed processing map: {data.map_name}")
            data["States"][fallback.id] = fallback

        for step in data.States.values():
            if step.get("Catch") or step.get("Type") in ("Pass", "Fail", "Map"):
                continue

            step["Catch"] = [{"ErrorEquals": ["States.ALL"], "Next": fallback.id}]

        data.pop("map_name", None)

        return super().to_yaml(dumper, data)


class Map(Stage):
    yaml_tag = "!Map"

    def __init__(
        self, name, steps, items_path="$.items", input_path="$.body", result_path="$.results", concurrency=20, end=False
    ):
        super().__init__("Map")
        self.name = name
        self.InputPath = input_path
        self.ItemsPath = items_path
        self.ResultPath = result_path
        self.MaxConcurrency = concurrency
        self.End = end
        self.Iterator = Iterator(name, steps)

    @property
    def id(self):
        return self.name

    @classmethod
    def to_yaml(cls, dumper, data):
        data.pop("name", None)
        return super().to_yaml(dumper, data)


class Definition(YamlOrderedDict):
    yaml_tag = "!Definition"

    def __init__(self, description):
        self.Comment = description
        self.States = YamlOrderedDict()

    def add(self, state):
        self.States[state.id] = state

        return state

    @classmethod
    def to_yaml(cls, dumper, data):
        if data.States:
            data["StartAt"] = list(data.States.keys())[0]
            data.move_to_end("StartAt", last=False)

        fallback = None
        for step in data.States.values():
            if step.get("Type") in ("Pass", "Fail"):
                fallback = step
                break

        if not fallback:
            fallback = Fallback("StateMachineErrorFallback", "Error in state machine")
            data.add(fallback)

        for step in data.States.values():
            if step.get("Catch") or step.get("Type") in ("Pass", "Fail", "Map"):
                continue

            step["Catch"] = [{"ErrorEquals": ["States.ALL"], "Next": fallback.id}]

        return super().to_yaml(dumper, data)


class StateMachine(YamlOrderedDict):
    yaml_tag = "!YamlOrderedDict"

    def __init__(self, name, description, events=None):
        self.name = name
        self.definition = Definition(description)
        self.events = events or []

    def task(self, function):
        return self.definition.add(Task(function))

    def map(self, name, steps, **kwargs):
        return self.definition.add(Map(name, steps, **kwargs))

    def event(self, event):
        self.events.append(event)


class StepFunctions(YamlOrderedDict):
    yaml_tag = "!StepFunctions"

    def __init__(self, service):
        self.service = service
        self.validate = True
        self.stateMachines = YamlOrderedDict()

    def machine(self, name, description):
        if name in self.stateMachines:
            return self.stateMachines.get(name)

        machine = StateMachine(f"{self.service.service}-${{sls:stage}}-{name}", description)
        self.stateMachines[name] = machine

        return machine

    @classmethod
    def to_yaml(cls, dumper, data):
        data.pop("service", None)
        return super().to_yaml(dumper, data)


class Scheduled(YamlOrderedDict):
    yaml_tag = "!YamlOrderedDict"

    def __init__(self, expression):
        self.schedule = expression
