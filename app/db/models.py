"""Contains Models."""

import sqlalchemy as sa
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from .sessions import Base


class Users(Base):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    first_name = sa.Column(sa.Text, nullable=False)
    last_name = sa.Column(sa.Text, nullable=False)
    email = sa.Column(sa.Text, nullable=False, unique=True)
    hashed_password = sa.Column(sa.Text, nullable=False)
    creation_date = sa.Column(sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False)  # type: ignore
    is_admin = sa.Column(sa.Boolean, nullable=False, default=False)

class Repositories(Base):
    __tablename__ = "repositories"

    id = sa.Column(sa.Integer, primary_key=True, index=True)
    name = sa.Column(sa.Text, nullable=False)
    description = sa.Column(sa.Text, nullable=True)
    is_visible = sa.Column(sa.Boolean, nullable=False, default=True)
    issues_count = sa.Column(sa.Integer, nullable=False, default=0)

    issues = relationship(
        "Issues", back_populates="repository", lazy="selectin", cascade="all, delete"
    )


class Issues(Base):
    __tablename__ = "issues"
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    number = sa.Column(sa.Integer, nullable=False, default=0)
    title = sa.Column(sa.Text, nullable=False)
    state = sa.Column(sa.Boolean, nullable=False, default=False)
    cumulative_bounty = sa.Column(sa.Integer, nullable=False, default=0)
    repository = relationship("Repositories", back_populates="issues", lazy="selectin")
    repository_id = sa.Column(sa.Integer, ForeignKey("repositories.id"), nullable=False, index=True)
    repository_name = sa.Column(sa.Text, nullable=True)
    url = sa.Column(sa.Text, nullable=False)
