# Copilot Instructions for Project Management Backend

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview
This is a FastAPI backend project for a comprehensive project management system with PostgreSQL database.

## Architecture Guidelines
- Use FastAPI with SQLAlchemy ORM
- Follow RESTful API principles
- Implement proper error handling and validation
- Use Pydantic models for request/response validation
- Maintain separation of concerns with modular structure

## Code Style
- Follow PEP 8 Python style guidelines
- Use type hints for all functions and variables
- Create comprehensive docstrings for all functions and classes
- Use async/await patterns for database operations
- Implement proper logging throughout the application

## Database Guidelines
- Use SQLAlchemy models with proper relationships
- Implement database migrations with Alembic
- Use connection pooling for better performance
- Follow database normalization principles

## Security Practices
- Implement JWT authentication
- Use password hashing with bcrypt
- Validate all inputs using Pydantic
- Implement proper CORS configuration
- Use environment variables for sensitive data
