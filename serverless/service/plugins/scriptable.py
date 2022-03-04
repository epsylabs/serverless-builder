from os.path import dirname, basename

from serverless.service.plugins.generic import Generic


class Scriptable(Generic):
    yaml_tag = "!ScriptablePlugin"

    def __init__(self, hooks=None, inject_to_package=None):
        super().__init__("serverless-scriptable-plugin")
        self.inject_to_package = inject_to_package
        self.hooks = hooks or {}

    def enable(self, service):
        service.custom["scriptHooks"] = self.hooks

        if self.inject_to_package:
            service.custom["scriptHooks"][
                "before:package:createDeploymentArtifacts"
            ] = f"cp -a {self.inject_to_package} ."
            service.custom["scriptHooks"][
                "after:package:createDeploymentArtifacts"
            ] = f"rm -rf ./{basename(self.inject_to_package)}"

            service.package.patterns.append(f"{basename(self.inject_to_package)}/**")
