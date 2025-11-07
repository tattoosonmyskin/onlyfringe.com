"""
Configuration module for OnlyFringe platform
"""
import os
from hexstrike_api_loader import load_api_keys

class Config:
    """Base configuration class"""
    # Load API keys from .hexstrike_api_keys file
    api_keys = load_api_keys()
    
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///onlyfringe.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # OpenAI API configuration for fact-checking
    OPENAI_API_KEY = api_keys.get('OPENAI_API_KEY') or os.environ.get('OPENAI_API_KEY')
    
    # Application configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Fact-checking configuration
    MIN_SOURCES_REQUIRED = 2
    MAX_ARGUMENT_LENGTH = 5000
    MIN_ARGUMENT_LENGTH = 100
    
    # AI model configuration
    AI_MODEL = 'gpt-4'
    AI_TEMPERATURE = 0.3  # Lower temperature for more factual responses
