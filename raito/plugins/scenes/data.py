from typing import TypeVar

from pydantic import BaseModel, ConfigDict

__all__ = ("SceneData",)


class SceneData(BaseModel):
    """Typed, JSON-serialisable draft carried between scene steps.

    The draft is mutable inside a handler (``scene.data.field = ...``) and is
    snapshotted into FSM storage on every navigation. Give every field a default:
    a scene starts from an empty draft. ``validate_assignment`` turns a typo like
    ``scene.data.usrname = ...`` into an immediate error instead of a silent loss.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


TSceneData = TypeVar("TSceneData", bound=SceneData)
