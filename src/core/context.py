from pydantic import BaseModel, Field
from typing import List, Optional

class SecurityContext(BaseModel):
    """
    Represents the security context of the current user.
    Used for multi-tenant isolation and policy enforcement.
    """
    tenant_id: str = Field(..., description="Unique identifier for the tenant")
    user_id: str = Field(..., description="Unique identifier for the user")
    role: str = Field(..., description="User role (e.g., admin, analyst, viewer)")
    region: Optional[str] = Field("US", description="User's data region")
    
    class Config:
        frozen = True

def get_mock_context(role: str = "analyst") -> SecurityContext:
    """
    Returns a mock security context for local development.
    In production, this would be populated from a JWT or auth middleware.
    """
    return SecurityContext(
        tenant_id="tenant_123",
        user_id="user_456",
        role=role,
        region="US"
    )
