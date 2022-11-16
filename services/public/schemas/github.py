from pydantic import BaseModel
from typing import Optional


class Repository(BaseModel):
    full_name: str


class PushPayload(BaseModel):
    repository: Repository
    after: Optional[str]
    ref: Optional[str]

    class Config:
        schema_extra = {
            "example": {
                "after": "10d5538c8b87a74e11c05c119e982b0e999ec77e",
                "ref": "refs/heads/main",
                "repository": {
                    "full_name": "uboot/sonja-backend"
                }
            }
        }
