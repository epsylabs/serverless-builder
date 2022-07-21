# Step functions 

`serverless-builder` have a built-in support for [serverless-step-functions](https://www.npmjs.com/package/serverless-step-functions)
which allows for a faster and more comprehensive development of complex workflows with [AWS Step Functions](https://aws.amazon.com/step-functions/) 

`serverless-builder` provides a programming interface for building a complex workflows using serverless lambda functions 
with some extra features like:
* autogeneration of the state names
* auto tracking of the dependencies (automatically setting up )

```python
from serverless.aws.features.stepfunctions import Branch, Choice, Iterator, Map, Scheduled, Succeed, Task

get_all_users = service.builder.function.generic(
    "get_all_users",
    "Returns with all users (for scheduling tasks)",
    "task_service.handler.get_all_users",
)

weekly_task = service.builder.function.generic(
    "weekly_task",
    "Schedules tasks for a user on each week",
    "task_service.handler.weekly_tasks",
    timeout=30,
)

machine = service.stepFunctions.machine("Weekly", "", type="EXPRESS", auto_fallback=False, auto_catch=False)
task = machine.task(get_all_users)
task.next(
    machine.parallel(
        name="ProcessAndContinue",
        branches=[
            Branch(
                Map(
                    name="ProcessUser",
                    items_path="$.user_ids",
                    result_path=None,
                    input_path=None,
                    concurrency=1,
                    end=True,
                    steps=Iterator(
                        map_name="ProcessUser",
                        steps=[Task(name="ProcessFunction", end=True, function=weekly_task)],
                        auto_catch=False,
                        auto_fallback=False,
                    ),
                )
            ),
            Branch(
                Choice(
                    name="ContinueIfMoreUsers",
                    default="NoMoreUsers",
                    choices=[dict(IsPresent=True, Next="Restart", Variable="$.PaginationToken")],
                ),
                Succeed(name="NoMoreUsers"),
                Task(
                    name="Restart",
                    end=True,
                    parameters=dict(
                        Input={"PaginationToken.$": "$.PaginationToken"}, StateMachineArn=machine.arn()
                    ),
                    resource="arn:aws:states:::states:startExecution",
                ),
            ),
        ],
        end=True,
    )
)

machine.event(Scheduled("0 18 ? * SAT *", dict(start="true")))

```

Sample workflow generated with serverless  

```yaml

stepFunctions:
  validate: true
  stateMachines:
    Weekly:
      name: task-service-${sls:stage}-Weekly
      tracingConfig:
        enabled: true
      type: EXPRESS
      loggingConfig:
        level: ERROR
        includeExecutionData: true
        destinations:
        - Fn::GetAtt:
          - StepmachineTaskServiceWeeklyLogGroup
          - Arn
      definition:
        StartAt: GetAllUsers
        Comment: ''
        States:
          GetAllUsers:
            Type: Task
            Resource:
              Fn::GetAtt:
              - GetAllUsersLambdaFunction
              - Arn
            Next: ProcessAndContinue
          ProcessAndContinue:
            Type: Parallel
            Branches:
            - StartAt: ProcessUser
              States:
                ProcessUser:
                  Type: Map
                  ItemsPath: $.user_ids
                  MaxConcurrency: 1
                  End: true
                  Iterator:
                    StartAt: ProcessFunction
                    States:
                      ProcessFunction:
                        Type: Task
                        Resource:
                          Fn::GetAtt:
                          - WeeklyTaskLambdaFunction
                          - Arn
                        End: true
            - StartAt: ContinueIfMoreUsers
              States:
                ContinueIfMoreUsers:
                  Type: Choice
                  Default: NoMoreUsers
                  Choices:
                  - IsPresent: true
                    Next: Restart
                    Variable: $.PaginationToken
                NoMoreUsers:
                  Type: Succeed
                Restart:
                  Type: Task
                  Parameters:
                    Input:
                      PaginationToken.$: $.PaginationToken
                    StateMachineArn: arn:aws:states:${aws:region}:${aws:accountId}:stateMachine:task-service-${sls:stage}-Weekly
                  Resource: arn:aws:states:::states:startExecution
                  End: true
            End: true
      events:
      - schedule:
          rate: cron(0 18 ? * SAT *)
        inputPath:
          start: 'true'
```
