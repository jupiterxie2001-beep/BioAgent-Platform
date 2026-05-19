from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    projects = relationship("Project", back_populates="owner")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    project_name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    owner = relationship("User", back_populates="projects")
    datasets = relationship("Dataset", back_populates="project")
    analysis_jobs = relationship("AnalysisJob", back_populates="project")

class Dataset(Base):
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    dataset_type = Column(String, index=True)  # "bulk_rna", "sc_rna", etc.
    file_path = Column(String)
    dataset_metadata = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="datasets")

class AnalysisJob(Base):
    __tablename__ = "analysis_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    workflow_json = Column(Text)
    status = Column(String, default="pending")  # pending, running, completed, failed
    result_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    project = relationship("Project", back_populates="analysis_jobs")
