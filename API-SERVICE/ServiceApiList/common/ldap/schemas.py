from datetime import datetime
from pydantic import Field, BaseModel
from typing import Optional, Union


class LoginInfo(BaseModel):
    id: str = Field(alias="cmpno", min_length=8, max_length=8)
    password: str = Field(default=None)

    class Config:
        fields = {"password": {"exclude": True}}


class UserBas(LoginInfo):
    user_id: str
    emp_id: str
    user_nm: str
    email: str
    dept_nm: str
    innt_aut_group_cd: Optional[str] = "ROLE_USER"
    sttus: Optional[str] = "SBSC"
    user_type: str


class TmpAuthUserBas(UserBas):
    tmp_aut_group_cd: Optional[str] = None
    tmp_aut_alc_user: Optional[str] = None
    tmp_aut_alc_date: Optional[datetime] = None
    tmp_aut_exp_date: Optional[datetime] = None


class LdapUserInfo(BaseModel):
    {
        "userName": "홍길동",
        "deptCD": 481253,
        "mobile": "010-6290-5249",
        "deptName": "",
        "agencyCD": 481226,
        "agencyName": "",
        "positionCD": "",
        "positionName": "AI/BigData사업본부...",
        "companyName": "KT협력사",
        "email": "9132824@ktfriends.com",
    }
    user_name: str = Field(alias="userName")
    mobile: str
    dept_cd: int = Field(alias="deptCD")
    dept_name: str = Field(alias="deptName")
    agency_cd: int = Field(alias="agencyCD")
    agency_name: str = Field(alias="agencyName")
    position_cd: Union[int, str] = Field(alias="positionCD")
    position_name: str = Field(alias="positionName")
    company_name: str = Field(alias="companyName")
    email: str
