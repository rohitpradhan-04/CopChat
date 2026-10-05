from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from core.models.user import BloodGroup, Department, Rank


class UserRegistration(BaseModel):
    service_id: str = Field(..., description="Unique Police Service Identification Number", json_schema_extra={"example": "COP-98765"})
    full_name: str = Field(..., description="Officer's Full Name", json_schema_extra={"example": "Inspector Vikram Sharma"})
    rank: Rank = Field(..., description="Police Rank", json_schema_extra={"example": "Constable"})
    department: Department = Field(..., description="Police Department/Unit", json_schema_extra={"example": "law_and_order"})
    station: str | None = Field(default=None, description="Assigned Police Station", json_schema_extra={"example": "Central Police Station"})
    role: str | None = Field(default=None, description="Role/Designation", json_schema_extra={"example": "Field Officer"})
    date_of_joining: date = Field(..., description="Date of Joining the force", json_schema_extra={"example": "2018-05-15"})
    mobile_number: str = Field(..., description="Contact Mobile Number", json_schema_extra={"example": "+919876543210"})
    email: EmailStr = Field(..., description="Official Email Address", json_schema_extra={"example": "vikram.sharma@police.gov.in"})
    emergency_contact_name: str = Field(..., description="Emergency Contact Name", json_schema_extra={"example": "Sunita Sharma"})
    emergency_contact_number: str = Field(..., description="Emergency Contact Phone Number", json_schema_extra={"example": "+919876543211"})
    blood_group: BloodGroup = Field(..., description="Blood Group", json_schema_extra={"example": "O+"})


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    service_id: str
    full_name: str
    rank: str
    department: str
    station: str | None = None
    role: str | None = None
    date_of_joining: date
    mobile_number: str
    email: EmailStr
    blood_group: str
    emergency_contact_name: str
    emergency_contact_number: str
    is_first_login: bool
    is_active: bool


class UserRegistrationResponse(BaseModel):
    status: str = "success"
    message: str
    temp_password: str
    user: UserResponse


class LoginRequest(BaseModel):
    email_or_service_id: str = Field(..., description="Email address or Service ID", json_schema_extra={"example": "COP-98765"})
    password: str = Field(..., description="User password or temporary one-time password", json_schema_extra={"example": "TempPass#123"})


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    is_first_login: bool = Field(..., description="Flag indicating if this is the user's first login requiring password setup")
    message: str
    user: UserResponse


class PasswordSetupRequest(BaseModel):
    email_or_service_id: str = Field(..., description="Email address or Service ID", json_schema_extra={"example": "COP-98765"})
    current_password: str = Field(..., description="Current/Temporary password", json_schema_extra={"example": "TempPass#123"})
    new_password: str = Field(..., min_length=6, description="New permanent password", json_schema_extra={"example": "NewSecurePass#2026"})


class PasswordSetupResponse(BaseModel):
    status: str = "success"
    message: str
    is_first_login: bool = False


class ForgotPasswordRequest(BaseModel):
    email_or_service_id: str = Field(
        ...,
        description="Email address or Service ID associated with the account",
        json_schema_extra={"example": "vikram.sharma@police.gov.in"},
    )


class ForgotPasswordResponse(BaseModel):
    status: str = "success"
    message: str


class ResetPasswordRequest(BaseModel):
    reset_token: str = Field(
        ...,
        description="Password reset token received via email",
        json_schema_extra={"example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."},
    )
    new_password: str = Field(
        ...,
        min_length=6,
        description="New permanent password",
        json_schema_extra={"example": "NewSecurePass#2026"},
    )


class ResetPasswordResponse(BaseModel):
    status: str = "success"
    message: str
    is_first_login: bool = False
