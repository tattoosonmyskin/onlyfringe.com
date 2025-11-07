# onlyfringe.com

**OnlyFringe** - A Fact-Based Debate Platform with AI Verification

## Overview

OnlyFringe is a revolutionary social media platform designed to create a space for public debate where facts matter. Unlike traditional social media, OnlyFringe requires all arguments to be:

- **Fact-based** with verifiable evidence
- **Fully contextualized** without cherry-picking
- **Source-backed** with minimum 2 credible references
- **AI-verified** for accuracy and logical coherence
- **Focused on issues** not rhetoric or emotional appeals

## Key Features

### 🤖 AI-Powered Fact-Checking
Every argument and rebuttal is analyzed by AI before publication for:
- Factual accuracy
- Logical coherence
- Source credibility
- Context completeness
- Evidence-based reasoning

### 📚 Mandatory Source Requirements
- Minimum 2 credible sources per argument
- Source validation (URL, title, description)
- References must be relevant and authentic

### ⚖️ Rigorous Moderation
- Arguments scored 0-100 by AI
- Minimum 70% score required for approval
- Detailed feedback on rejected submissions
- Transparent fact-check results

### 💡 Complete Context Enforcement
- Full thought arguments required (100-5000 characters)
- Must provide complete context, not partial information
- Misleading framing is rejected

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/tattoosonmyskin/onlyfringe.com.git
cd onlyfringe.com
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API keys (optional for development):
Create a `.hexstrike_api_keys` file with your OpenAI API key:
```
OPENAI_API_KEY=your_key_here
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## API Documentation

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### Create User
```http
POST /api/users
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com"
}
```

**Response (201):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

#### Submit Argument
```http
POST /api/arguments
Content-Type: application/json

{
  "title": "Climate Change and Renewable Energy",
  "content": "Renewable energy sources have become increasingly cost-effective...",
  "category": "environment",
  "user_id": 1,
  "sources": [
    {
      "url": "https://example.com/study1",
      "title": "Renewable Energy Cost Analysis 2024",
      "description": "Comprehensive study on renewable energy costs"
    },
    {
      "url": "https://example.com/study2",
      "title": "Solar Panel Efficiency Report",
      "description": "Latest data on solar panel efficiency"
    }
  ]
}
```

**Response (201):**
```json
{
  "id": 1,
  "title": "Climate Change and Renewable Energy",
  "content": "Renewable energy sources...",
  "verification_status": "approved",
  "is_verified": true,
  "fact_check": {
    "is_valid": true,
    "score": 85,
    "issues": [],
    "recommendations": []
  }
}
```

#### List Arguments
```http
GET /api/arguments?status=approved&category=environment
```

**Query Parameters:**
- `status`: Filter by verification status (pending, approved, rejected)
- `category`: Filter by category

#### Get Argument
```http
GET /api/arguments/1
```

#### Submit Rebuttal
```http
POST /api/arguments/1/rebuttals
Content-Type: application/json

{
  "content": "While renewable energy is cost-effective...",
  "user_id": 2,
  "sources": [
    {
      "url": "https://example.com/counter-study1",
      "title": "Energy Grid Stability Analysis",
      "description": "Study on grid stability with renewables"
    },
    {
      "url": "https://example.com/counter-study2",
      "title": "Energy Storage Solutions",
      "description": "Research on battery storage technology"
    }
  ]
}
```

#### Health Check
```http
GET /api/health
```

## Submission Requirements

### Arguments
- **Length**: 100-5000 characters
- **Sources**: Minimum 2 credible sources
- **Format**: Each source must include:
  - Valid URL
  - Title
  - Description
- **Approval**: AI fact-check score ≥ 70%

### Rebuttals
- Must respond to approved arguments only
- Same source requirements as arguments
- Must directly address the original argument
- Subject to same fact-checking standards

## AI Fact-Checking

The platform uses OpenAI's GPT-4 to analyze submissions for:

1. **Factual Accuracy** - Are claims verifiable and true?
2. **Logical Coherence** - Is the reasoning sound?
3. **Source Quality** - Are sources credible and relevant?
4. **Context Completeness** - Is full context provided?
5. **Evidence-Based Reasoning** - Are claims supported by evidence?

### Scoring System
- **0-49**: Rejected - Major issues with facts or logic
- **50-69**: Rejected - Insufficient evidence or context
- **70-100**: Approved - Meets platform standards

## Database Schema

### Users
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email
- `created_at`: Account creation timestamp

### Arguments
- `id`: Primary key
- `title`: Argument title
- `content`: Full argument text
- `category`: Topic category
- `user_id`: Foreign key to User
- `is_verified`: Boolean verification status
- `verification_status`: pending/approved/rejected
- `ai_fact_check_result`: JSON of AI analysis

### Sources
- `id`: Primary key
- `argument_id`: Foreign key to Argument
- `url`: Source URL
- `title`: Source title
- `description`: Source description
- `is_valid`: URL validation status

### Rebuttals
- `id`: Primary key
- `argument_id`: Foreign key to Argument
- `user_id`: Foreign key to User
- `content`: Rebuttal text
- `is_verified`: Boolean verification status
- `verification_status`: pending/approved/rejected
- `ai_fact_check_result`: JSON of AI analysis

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (via SQLAlchemy)
- **AI**: OpenAI GPT-4
- **Validation**: validators library
- **CORS**: Flask-CORS

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Database Management
The database is automatically created on first run. To reset:
```bash
rm onlyfringe.db
python app.py
```

## Security Considerations

- API keys should be stored in `.hexstrike_api_keys` (gitignored)
- Never commit secrets to the repository
- Use environment variables in production
- Implement rate limiting for production use
- Add authentication/authorization for production

## Future Enhancements

- User authentication and authorization
- Rate limiting and abuse prevention
- Advanced search and filtering
- Voting and ranking system
- Email notifications
- Mobile application
- Real-time updates via WebSockets
- Enhanced AI models for specialized topics
- Multi-language support

## Contributing

Contributions are welcome! Please ensure all submissions:
- Include comprehensive tests
- Follow existing code style
- Update documentation as needed
- Pass all fact-checking validations

## License

This project is part of the OnlyFringe platform initiative.

## Contact

For questions or support, please open an issue on GitHub.

---

**OnlyFringe** - Elevating Public Discourse Through Facts