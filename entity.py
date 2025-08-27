from dataclasses import dataclass

@dataclass
class User:
    user_id: int
    username: str
    password: str

@dataclass
class Annual_Report:
    id: int
    company_code: str
    company_name: str
    title: str
    year: str
    link: str
    pdf_url: str
    txt_url: str


