from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from core.database import getDbSession
from core.models.user import User
from core.schemas.user import (
    LoginRequest,
    LoginResponse,
    PasswordSetupRequest,
    PasswordSetupResponse,
    UserRegistration,
    UserRegistrationResponse,
    UserResponse,
)
from core.security import (
    create_access_token,
    generate_temp_password,
    hash_password,
    verify_password,
)
from core.services.email import send_registration_email

rout = APIRouter(prefix="/v1", tags=["User & Authentication"])


@rout.post(
    "/register",
    response_model=UserRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new officer user",
    description="Registers a new user, generates a dummy one-time temporary password, stores it securely, and triggers a background email notification with credentials.",
)
def register_user(
    request: UserRegistration,
    background_tasks: BackgroundTasks,
    db: Session = Depends(getDbSession),  # noqa: B008
):
    # Check if user already exists with email, service_id, or mobile_number
    existing_user = db.scalars(
        select(User).where(
            or_(
                User.email == request.email,
                User.service_id == request.service_id,
                User.mobile_number == request.mobile_number,
            )
        )
    ).first()

    if existing_user:
        if existing_user.email == request.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email address already exists.",
            )
        if existing_user.service_id == request.service_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this Service ID already exists.",
            )
        if existing_user.mobile_number == request.mobile_number:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this mobile number already exists.",
            )

    # 1. Generate dummy one-time password
    temp_password = generate_temp_password()

    # 2. Hash temporary password
    hashed_temp_password = hash_password(temp_password)

    # 3. Create user entity with is_first_login = True
    new_user = User(
        service_id=request.service_id,
        full_name=request.full_name,
        rank=request.rank,
        department=request.department,
        station=request.station,
        role=request.role,
        date_of_joining=request.date_of_joining,
        mobile_number=request.mobile_number,
        email=request.email,
        blood_group=request.blood_group,
        emergency_contact_name=request.emergency_contact_name,
        emergency_contact_number=request.emergency_contact_number,
        password=hashed_temp_password,
        is_first_login=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 4. Trigger background email sending task
    background_tasks.add_task(
        send_registration_email,
        to_email=new_user.email,
        full_name=new_user.full_name,
        service_id=new_user.service_id,
        temp_password=temp_password,
    )

    return UserRegistrationResponse(
        status="success",
        message="User registered successfully. Credentials sent to email in background.",
        temp_password=temp_password,
        user=UserResponse.model_validate(new_user),
    )


@rout.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticates user credentials and returns JWT token along with 'is_first_login' flag indicating if password setup is required.",
)
def login_user(
    request: LoginRequest,
    db: Session = Depends(getDbSession),  # noqa: B008
):
    identifier = request.email_or_service_id.strip()

    # Search user by email or service_id
    user = db.scalars(
        select(User).where(
            or_(
                User.email == identifier,
                User.service_id == identifier,
            )
        )
    ).first()

    if not user or not verify_password(request.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials. Please check your Service ID / Email and Password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact administrator.",
        )

    # Create JWT token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "service_id": user.service_id,
            "email": user.email,
            "is_first_login": user.is_first_login,
        }
    )

    msg = (
        "First time login detected. Please update your temporary password."
        if user.is_first_login
        else "Login successful."
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        is_first_login=user.is_first_login,
        message=msg,
        user=UserResponse.model_validate(user),
    )


@rout.post(
    "/setup-password",
    response_model=PasswordSetupResponse,
    status_code=status.HTTP_200_OK,
    summary="Setup Permanent Password after First Time Login",
    description="Updates user password from temporary to permanent password and sets is_first_login to False.",
)
def setup_password(
    request: PasswordSetupRequest,
    db: Session = Depends(getDbSession),  # noqa: B008
):
    identifier = request.email_or_service_id.strip()

    user = db.scalars(
        select(User).where(
            or_(
                User.email == identifier,
                User.service_id == identifier,
            )
        )
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    if not verify_password(request.current_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password (temporary password) is incorrect.",
        )

    # Update to new permanent password hash
    user.password = hash_password(request.new_password)
    user.is_first_login = False

    db.add(user)
    db.commit()

    return PasswordSetupResponse(
        status="success",
        message="Permanent password set up successfully! You can now log in with your new password.",
        is_first_login=False,
    )
