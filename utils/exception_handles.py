from fastapi import Request, status
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from utils.exception import http_exception_handler, sqlalchemy_error_handler, integrity_error_handler, general_exception_handler
from fastapi import HTTPException

def register_exception_handlers(app):
    #子类在前，父类在后，具体在前，抽象在后
    app.add_exception_handler(HTTPException, http_exception_handler)#业务
    app.add_exception_handler(IntegrityError, integrity_error_handler)#数据完整性约束
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_error_handler)#数据库错误
    app.add_exception_handler(Exception, general_exception_handler)#兜底