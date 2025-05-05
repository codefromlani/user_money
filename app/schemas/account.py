from pydantic import BaseModel, validator
from typing import Literal


class CreateAccount(BaseModel):
    bvn: str
    account_type: Literal["savings", "current"] = "savings"

    @validator("bvn")
    def validate_bvn(cls, v):
        if len(v) != 11 or not v.isdigit():
            raise ValueError("BVN must be exactly 11 digits")
        return v