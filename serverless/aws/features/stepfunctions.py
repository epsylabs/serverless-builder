from typing import Optional

from serverless.aws.resources.logs import LogGroup
from serverless.service.plugins.step_functions import StepFunctions as StepFunctionsPlugin
from serverless.service.types import Identifier, YamlOrderedDict


class Stage(YamlOrderedDict):
    yaml_tag = "!Stage"

    def __init__(self, type, function=None):
        self.Type = type
        self._function = function

    def next(self, stage):
        self.Next = stage.id

    @property
    def id(self):
        return self._function.key.pascal

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

    def __init__(self, function=None, end=None, name=None, parameters=None, resource=None):
        if not any([function, resource]):
            raise Exception("You need to provide either function or resource parameter")

        super().__init__("Task", function)

        if name:
            self.name = name

        if parameters:
            self.Parameters = parameters

        self.Resource = function.arn() if function else resource
        if end is not None:
            self.End = end

    @property
    def id(self):
        return self.name if self.name else self._function.key.pascal

    @classmethod
    def to_yaml(cls, dumper, data):
        data.pop("name", None)
        return super().to_yaml(dumper, data)


class Wait(Stage):
    yaml_tag = "!Wait"

    def __init__(
        self,
        name=None,
        seconds: int = None,
        timestamp: str = None,
        seconds_path: str = None,
        timestamp_path: str = None,
    ):
        if not any([seconds, timestamp, seconds_path, timestamp_path]):
            raise Exception("You need to provide either seconds, timestamp, seconds_path or timestamp_path parameter")

        super().__init__("Wait")

        if name:
            self.name = name

        if seconds is not None:
            self.Seconds = seconds
        elif timestamp is not None:
            self.Timestamp = timestamp
        elif seconds_path is not None:
            self.SecondsPath = seconds_path
        elif timestamp_path is not None:
            self.TimestampPath = timestamp_path

    @property
    def id(self):
        return self.name if self.name else self._function.key.pascal

    @classmethod
    def to_yaml(cls, dumper, data):
        data.pop("name", None)
        return super().to_yaml(dumper, data)


class Iterator(YamlOrderedDict):
    yaml_tag = "!Iterator"

    def __init__(self, map_name, steps, auto_catch=True, auto_fallback=False):
        self.States = {step.id: step for step in steps}
        self.map_name = map_name
        self.auto_catch = auto_catch
        self.auto_fallback = auto_fallback

    @property
    def id(self):
        return self.map_name

    @classmethod
    def to_yaml(cls, dumper, data):
        data["StartAt"] = str(list(data.States.keys())[0])
        data.move_to_end("StartAt", last=False)

        fallback = None
        for step in data.States.values():
            if step.get("Type") in ("Pass", "Fail"):
                fallback = step
                break

        if data.auto_fallback and not fallback:
            fallback = Fallback(f"{data.map_name}Fallback", f"Failed processing map: {data.map_name}")
            data["States"][fallback.id] = fallback

        if data.auto_catch:
            for step in data.States.values():
                if step.get("Catch") or step.get("Type") in ("Pass", "Fail", "Map"):
                    continue

                step["Catch"] = [{"ErrorEquals": ["States.ALL"], "Next": fallback.id}]

        data.pop("map_name", None)
        data.pop("auto_catch", None)
        data.pop("auto_fallback", None)

        return super().to_yaml(dumper, data)


class Map(Stage):
    yaml_tag = "!Map"

    def __init__(
        self, name, steps, items_path="$.items", input_path="$.body", result_path="$.results", concurrency=20, end=False
    ):
        super().__init__("Map")
        self.name = name

        if input_path:
            self.InputPath = input_path

        if items_path:
            self.ItemsPath = items_path

        if result_path:
            self.ResultPath = result_path

        self.MaxConcurrency = concurrency
        self.End = end
        self.Iterator = steps if isinstance(steps, Iterator) else Iterator(name, steps)

    @property
    def id(self):
        return self.name

    @classmethod
    def to_yaml(cls, dumper, data):
        data.pop("name", None)
        return super().to_yaml(dumper, data)


class State(YamlOrderedDict):
    yaml_tag = "!State"

    def __init__(self, name) -> None:
        super().__init__()
        self.name = name

    @property
    def id(self):
        return self.name

    @classmethod
    def to_yaml(cls, dumper, data):
        data.pop("name", None)
        return super().to_yaml(dumper, data)


class Choice(State):
    yaml_tag = "!Choice"

    def __init__(self, name, default, choices=None) -> None:
        super().__init__(name)
        self.Type = "Choice"
        self.Default = default
        self.Choices = choices or []


class Succeed(State):
    yaml_tag = "!Succeed"

    def __init__(self, name) -> None:
        super().__init__(name)
        self.Type = "Succeed"


class Branch(YamlOrderedDict):
    yaml_tag = "!Branch"

    def __init__(self, *states) -> None:
        super().__init__()
        self.States = list(states)

    @classmethod
    def to_yaml(cls, dumper, data):
        export = dict(StartAt=data.States[0].id, States={i.name: i for i in data.States})
        return super().to_yaml(dumper, export)


class Parallel(Stage):
    yaml_tag = "!Parallel"

    def __init__(self, name, branches, end=False):
        super().__init__("Parallel")
        self.name = name
        self.Branches = branches
        self.End = end

    @property
    def id(self):
        return self.name

    @classmethod
    def to_yaml(cls, dumper, data):
        data.pop("name", None)
        return super().to_yaml(dumper, data)


class Definition(YamlOrderedDict):
    yaml_tag = "!Definition"

    def __init__(self, description, auto_fallback=True, auto_catch=True):
        self.Comment = description
        self.States = YamlOrderedDict()
        self.auto_fallback = auto_fallback
        self.auto_catch = auto_catch

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

        if data.auto_fallback and not fallback:
            fallback = Fallback("StateMachineErrorFallback", "Error in state machine")
            data.add(fallback)

        if data.auto_catch:
            for step in data.States.values():
                if step.get("Catch") or step.get("Type") in ("Pass", "Fail", "Map"):
                    continue

                step["Catch"] = [{"ErrorEquals": ["States.ALL"], "Next": fallback.id}]

        data.pop("auto_fallback", None)
        data.pop("auto_catch", None)

        return super().to_yaml(dumper, data)


class StateMachine(YamlOrderedDict):
    yaml_tag = "!YamlOrderedDict"

    def __init__(self, name, description, events=None, type=None, auto_fallback=True, auto_catch=True, service=None):
        self.name = name
        self.tracingConfig = dict(enabled=True)

        if type:
            self.type = type

        logs = LogGroup(LogGroupName=f"/stepmachine/{Identifier(self.name).spinal}")
        service.resources.add(logs)

        self.loggingConfig = dict(level="ERROR", includeExecutionData=True, destinations=[logs.get_att("Arn")])
        self.definition = Definition(description, auto_fallback, auto_catch)
        self.events = events or []

    def task(self, function, end: Optional[bool] = None):
        return self.definition.add(Task(function, end=end))

    def map(self, name, steps, **kwargs):
        return self.definition.add(Map(name, steps, **kwargs))

    def parallel(self, name, branches, end):
        return self.definition.add(Parallel(name=name, branches=branches, end=end))

    def wait(
        self, name, seconds: int = None, timestamp: str = None, seconds_path: str = None, timestamp_path: str = None
    ):
        return self.definition.add(
            Wait(
                name=name,
                seconds=seconds,
                timestamp=timestamp,
                seconds_path=seconds_path,
                timestamp_path=timestamp_path,
            )
        )

    def event(self, event):
        self.events.append(event)

    def arn(self):
        return "arn:aws:states:${aws:region}:${aws:accountId}:stateMachine:" + self.name


class StepFunctions(YamlOrderedDict):
    yaml_tag = "!StepFunctions"

    def __init__(self, service):
        self.service = service
        self.validate = True
        self.stateMachines = YamlOrderedDict()

    def machine(self, name, description, type=None, auto_fallback=True, auto_catch=True):
        if name in self.stateMachines:
            return self.stateMachines.get(name)

        if not self.service.plugins.has(StepFunctionsPlugin):
            self.service.plugins.add(StepFunctionsPlugin())

        machine = StateMachine(
            f"{self.service.service}-${{sls:stage}}-{name}",
            description,
            auto_fallback=auto_fallback,
            auto_catch=auto_catch,
            type=type,
            service=self.service,
        )
        self.stateMachines[name] = machine

        return machine

    @classmethod
    def to_yaml(cls, dumper, data):
        data.pop("service", None)
        return super().to_yaml(dumper, data)


class Scheduled(YamlOrderedDict):
    yaml_tag = "!YamlOrderedDict"

    def __init__(self, expression, inputPath=None):
        if not isinstance(expression, dict):
            expression = dict(rate=f"cron({expression})")

        self.schedule = expression

        if inputPath:
            self.inputPath = inputPath
