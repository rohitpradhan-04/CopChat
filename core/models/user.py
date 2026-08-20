from datetime import date
from enum import Enum

from sqlalchemy import Boolean, Date, String
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column

from core.database import BaseModel


class Rank(str, Enum):
    CONSTABLE = "Constable"
    HEAD_CONSTABLE = "Head Constable"
    ASSISTANT_SUB_INSPECTOR = "ASI"
    SUB_INSPECTOR = "SI"
    CIRCLE_INSPECTOR = "CI / Inspector"
    DEPUTY_SUPERINTENDENT = "DSP"
    ADDITIONAL_SUPERINTENDENT = "Addl. SP"
    SUPERINTENDENT = "SP"
    DEPUTY_INSPECTOR_GENERAL = "DIG"
    INSPECTOR_GENERAL = "IG"
    ADDITIONAL_DIRECTOR_GENERAL = "ADGP"
    DIRECTOR_GENERAL = "DGP"
    ASSISTANT_COMMISSIONER = "ACP"
    DEPUTY_COMMISSIONER = "DCP"
    ADDITIONAL_COMMISSIONER = "Addl. CP"
    COMMISSIONER_OF_POLICE = "CP"


class Department(str, Enum):
    LAW_AND_ORDER = "law_and_order"
    TRAFFIC = "traffic"
    CRIME_BRANCH = "crime_branch"
    CID_CRIME_BRANCH = "cid_crime_branch"
    SPECIAL_BRANCH = "special_branch"
    SOG = "sog"
    ATS = "ats"
    CYBER_CRIME = "cyber_crime"
    EOW = "eow"
    ACB = "acb"
    NARCOTICS = "narcotics"
    AHTU = "ahtu"
    WOMEN_SAFETY = "women_safety"
    GRP = "grp"
    RAC = "rac"
    TELECOM = "telecom"
    FSL = "fsl"
    TRAINING = "training"
    VIGILANCE = "vigilance"
    PHQ = "phq"


class BloodGroup(str, Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class User(BaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    service_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    rank: Mapped[Rank] = mapped_column(
        SqlEnum(Rank),
        nullable=False,
    )

    department: Mapped[Department] = mapped_column(
        SqlEnum(Department),
        nullable=False,
    )

    station: Mapped[str] = mapped_column(
        String(100),
        nullable=True,
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=True,
    )

    date_of_joining: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    mobile_number: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
        unique=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    blood_group: Mapped[BloodGroup] = mapped_column(
        SqlEnum(BloodGroup),
        nullable=False,
    )

    emergency_contact_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    emergency_contact_number: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
    )

    password: Mapped[str] = mapped_column(
        String(255),
        nullable=True,
    )

    is_first_login: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

