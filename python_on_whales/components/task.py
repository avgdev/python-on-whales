from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

import pydantic

from python_on_whales.client_config import (
    ClientConfig,
    DockerCLICaller,
    ReloadableObjectFromJson,
)
from python_on_whales.utils import DockerCamelModel, run


class ObjectVersion(DockerCamelModel):
    index: int


class NamedResourceSpec(DockerCamelModel):
    kind: str
    value: str


class DiscreteResourceSpec(DockerCamelModel):
    kind: str
    value: int


class AssignedGenericResources(DockerCamelModel):
    named_resource_spec: NamedResourceSpec
    discrete_resource_spec: DiscreteResourceSpec


class ContainerStatus(DockerCamelModel):
    container_id: str = pydantic.Field(alias="ContainerID")
    pid: int = pydantic.Field(alias="PID")
    exit_code: int


class TaskStatus(DockerCamelModel):
    timestamp: datetime
    state: str
    message: str
    err: Optional[str]
    container_status: ContainerStatus


class LogDriver(DockerCamelModel):
    name: str
    options: Dict[str, str]


class NetworkAttachmentConfig(DockerCamelModel):
    target: str
    aliases: List[str]
    driver_opts: Optional[Dict[str, str]]


class Platform(DockerCamelModel):
    architecture: Optional[str]
    os: Optional[str] = pydantic.Field(alias="OS")


class Spread(DockerCamelModel):
    spread_descriptor: str


class Placement(DockerCamelModel):
    constraints: Optional[List[str]]
    preferences: Optional[List[Spread]]
    max_replicas: Optional[int]
    platforms: List[Platform]


class RestartPolicy(DockerCamelModel):
    condition: str
    delay: int
    max_attempts: int
    window: int


class TaskSpec(DockerCamelModel):
    # TODO: set types for Any
    plugin_spec: Any
    container_spec: Any
    network_attachment_spec: Any
    resources: Any
    restart_policy: Any
    placement: Placement
    force_update: int
    runtime: Optional[str]
    networks: List[NetworkAttachmentConfig]
    log_driver: Optional[LogDriver]


class TaskInspectResult(DockerCamelModel):
    id: str = pydantic.Field(alias="ID")
    version: ObjectVersion
    created_at: datetime
    updated_at: datetime
    name: Optional[str]
    labels: Dict[str, str]
    spec: TaskSpec
    service_id: str = pydantic.Field(alias="ServiceID")
    slot: Optional[int]
    node_id: str = pydantic.Field(alias="NodeID")
    assigned_generic_resources: Optional[List[AssignedGenericResources]]
    status: TaskStatus
    desired_state: str


class Task(ReloadableObjectFromJson):
    def __init__(
        self, client_config: ClientConfig, reference: str, is_immutable_id=False
    ):
        super().__init__(client_config, "id", reference, is_immutable_id)

    def _fetch_inspect_result_json(self, reference):
        return run(self.docker_cmd + ["inspect", reference])

    def _parse_json_object(self, json_object: Dict[str, Any]) -> TaskInspectResult:
        return TaskInspectResult.parse_obj(json_object)

    @property
    def id(self) -> str:
        return self._get_immutable_id()

    @property
    def name(self) -> str:
        return self._get_inspect_result().name


class TaskCLI(DockerCLICaller):
    def list(self) -> List[Task]:
        """Not Yet implemented"""
        raise NotImplementedError

    def inspect(self, x: Union[str, List[str]]) -> Union[Task, List[Task]]:
        if isinstance(x, str):
            return Task(self.client_config, x)
        else:
            return [Task(self.client_config, reference) for reference in x]

    def logs(self):
        """Not Yet implemented"""
        raise NotImplementedError