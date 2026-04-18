from pydantic import BaseModel

class MetaBase(BaseModel):
    status_code: int
    message: str


class PaginateSchema(BaseModel):
    current_page: int
    limit: int
    total: int
    total_pages: int


class MetaPaginateSchema(MetaBase, PaginateSchema):
    pass


class MetaSchema(MetaBase):
    pass
