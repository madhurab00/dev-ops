from sqlalchemy import Table, Column, Integer, Float, DateTime, MetaData, func

metadata = MetaData()

requests_table = Table(
    "requests",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("a", Float, nullable=False),
    Column("b", Float, nullable=False),
    Column("result", Float, nullable=False),
    Column("created_at", DateTime(timezone=True), server_default=func.now(), nullable=False),
)