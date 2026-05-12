from datetime import datetime
from sqlalchemy import DateTime,Integer,String
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

class Base(DeclarativeBase):
    created_at:Mapped[datetime]=mapped_column(
        DateTime,
        default=datetime.now,
        comment="创建时间"
    )
    updated_at:Mapped[datetime]=mapped_column(
        DateTime,
        default=datetime.now,
        comment="更新时间"
    )

class Category(Base):
    __tablename__='news_category'#与数据库表名一致，否则会报错
    id:Mapped[int]=mapped_column(Integer,primary_key=True,autoincrement=True,comment="分类ID")#自动递增主键
    name:Mapped[str]=mapped_column(String(50),unique=True,nullable=False,comment='分类名称')
    sort_order:Mapped[int]=mapped_column(Integer,default=0,nullable=False,comment='分类排序')
    
    def __repr__(self):
        return f"Category(id={self.id},name={self.name},sort_order={self.sort_order})"
