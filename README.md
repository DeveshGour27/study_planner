# 🎓 Adaptive Study Planner

An intelligent, AI-powered study planning application that creates personalized learning paths, generates adaptive quizzes, provides 24/7 chat support, and tracks your progress in real-time.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35.0-FF4B4B.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🌟 Features

### 🎯 Personalized Learning
- **AI-Generated Study Plans** - Custom roadmaps based on your topics, skill level, and timeline
- **Adaptive Difficulty** - Content adjusts to your performance
- **Day-by-Day Breakdown** - Structured daily tasks with videos, readings, and practice problems
- **Automatic Day Progression** - Tracks your learning streak and advances days automatically

### 🤖 AI Assistant
- **24/7 Chat Support** - Context-aware AI tutor powered by LLaMA 3.2
- **RAG-Powered Q&A** - Upload PDFs and ask questions about your study materials
- **Smart Intent Detection** - Automatically understands when to use documents vs general knowledge
- **Progress-Aware Responses** - AI knows your current day, quiz scores, and weak areas

### 📝 Smart Quizzes
- **Three Quiz Types** - MCQ, Descriptive, and Coding questions
- **AI Grading** - Instant feedback with detailed explanations
- **Performance Analytics** - Track scores, identify weak areas, and measure improvement
- **Adaptive Questions** - Difficulty adjusts based on your skill level

### 📊 Progress Analytics
- **Daily Progress Tracking** - Monitor task completion and study time
- **Week/Month Summaries** - Comprehensive performance reports
- **Streak Tracking** - Maintain consistency with daily streak counters
- **Achievement System** - Unlock badges for milestones

### 📄 Resource Management
- **PDF Upload** - Import textbooks, notes, and study materials
- **Semantic Search** - AI-powered search across all uploaded documents
- **Automatic Embeddings** - Documents are indexed for instant retrieval
- **Topic Organization** - Organize materials by subject

---

## 🛠️ Tech Stack

### Frontend
- **Streamlit 1.35.0** - Modern, reactive web interface
- **Custom CSS** - Professional dark theme with gradients

### Backend
- **SQLAlchemy 2.0.36** - ORM for database management
- **SQLite** - Local database (easily upgradable to PostgreSQL)

### AI/ML
- **HuggingFace Transformers** - LLaMA 3.2-3B-Instruct for chat and content generation
- **Sentence Transformers** - all-MiniLM-L6-v2 for semantic search and embeddings
- **RAG (Retrieval-Augmented Generation)** - Document-based Q&A with FAISS

### Security
- **bcrypt** - Password hashing
- **PyJWT** - Token-based authentication

---

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)
- Git

### Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/adaptive-study-planner.git
cd adaptive-study-planner

# 2. Create virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
# Add your HuggingFace token and JWT secret
echo "HF_TOKEN=your_huggingface_token_here" > .env
echo "JWT_SECRET_KEY=your_secret_key_here" >> .env

# 5. Initialize database
python init_database.py

# 6. Run the app
streamlit run app.py
```

---

## 🔑 Environment Setup

Create a `.env` file in the root directory:

```env
# HuggingFace API Token (Required)
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxx

# JWT Secret Key (Required)
JWT_SECRET_KEY=your-secret-key-change-this-in-production

# Optional: Database URL (defaults to SQLite)
DATABASE_URL=sqlite:///database.db
```

### Getting Your HuggingFace Token

1. Go to [huggingface.co](https://huggingface.co/)
2. Sign up or login
3. Navigate to Settings → Access Tokens
4. Create a new token with "Read" permissions
5. Copy and paste into `.env` file

---

## 📁 Project Structure

```
adaptive-study-planner/
│
├── core/                    # Core business logic
│   ├── auth_manager.py      # Authentication & user management
│   ├── chat_engine.py       # AI chat functionality
│   ├── day_manager.py       # Day progression logic
│   ├── onboarding.py        # Onboarding flow
│   ├── pdf_processor.py     # PDF upload & text extraction
│   ├── plan_generator.py    # Study plan generation
│   └── quiz_engine.py       # Quiz creation & grading
│
├── database/                # Database models & config
│   ├── db_manager.py        # SQLAlchemy setup
│   └── models.py            # Database models
│
├── llm/                     # AI/LLM integration
│   ├── llm_client.py        # HuggingFace API client
│   ├── prompts.py           # AI prompt templates
│   └── rag_engine.py        # RAG system for PDF Q&A
│
├── pages/                   # Streamlit pages
│   ├── Chat.py              # AI chat interface
│   ├── Dashboard.py         # Main dashboard
│   ├── Login.py             # Login page
│   ├── MyLearning.py        # Resource management
│   ├── onboarding.py        # Onboarding wizard
│   ├── Progress.py          # Analytics & progress
│   ├── Quiz.py              # Quiz interface
│   ├── Settings.py          # User settings
│   └── Signup.py            # Registration page
│
├── utils/                   # Utility functions
│   ├── safe_helpers.py      # Safe data handling
│   ├── ui_helpers.py        # UI helper functions
│   └── validators.py        # Input validation
│
├── data/                    # Data storage (auto-created)
│   ├── uploads/             # Uploaded PDFs
│   └── embeddings/          # Vector embeddings
│
├── app.py                   # Main entry point
├── requirements.txt         # Python dependencies
├── init_database.py         # Database initialization
├── check_database.py        # Database verification
├── .env                     # Environment variables (create this)
├── database.db              # SQLite database (auto-created)
└── README.md                # This file
```

---

## 🚀 Usage

### First Time Setup

1. **Sign Up** - Create your account with username, email, and password
2. **Complete Onboarding** - 4-step wizard:
   - Select topics (1-10 topics)
   - Set skill levels (Beginner/Intermediate/Advanced)
   - Choose timeline (Deadline or Self-paced)
   - Set daily hours (1-16 hours/day)
3. **Generate Study Plan** - AI creates your personalized roadmap
4. **Start Learning** - Follow daily tasks and track progress

### Daily Workflow

```
Dashboard → View today's tasks
Complete tasks:
  - Watch videos (mark complete)
  - Read materials (mark complete)
  - Practice problems (mark complete)
Take quizzes to test knowledge
Use Chat for doubts and questions
```

### Uploading Study Materials

```
My Learning → Upload Material
Select PDF file (max 50MB)
Choose related topic
Wait for processing (~30 seconds)
Ask questions in Chat about uploaded content
```

---

## 🔧 Configuration

### Supported Topics

- Data Structures
- Algorithms
- DBMS (Database Management Systems)
- Operating Systems
- Computer Networks
- Python
- Java
- Web Development
- Machine Learning
- System Design

### Quiz Types

1. **MCQ** - Multiple choice questions (10 points each)
2. **Descriptive** - Written answers with AI grading (0-10 points)
3. **Coding** - Programming problems with AI code review (0-10 points)

---

## 🐛 Troubleshooting

### Issue: "HF_TOKEN not found"
**Solution:** Create `.env` file with your HuggingFace token:
```env
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxx
```

### Issue: "No plans found for today"
**Solutions:**
1. Check if onboarding was completed
2. Click "🔄 Regenerate Study Plan" button on Dashboard
3. Check terminal for errors during plan generation

### Issue: "PDF upload failed"
**Solutions:**
1. Ensure file is under 50MB
2. Check file is text-based PDF (not scanned image)
3. Verify `data/uploads/` folder exists (created automatically)

### Issue: "Quiz generation failed"
**Solutions:**
1. Check HuggingFace API token is valid
2. Reduce number of questions (try 3 instead of 10)
3. Check internet connection
4. Check terminal for detailed error messages

### Issue: "Day not progressing"
**Solution:** Make sure `DayManager.check_and_update_day(user_id)` is called in Dashboard.py. Use debug controls to manually advance if needed.

---

## 📊 Database Schema

### Main Tables
- **users** - User accounts (username, email, password hash)
- **student_profiles** - Learning preferences & progress
- **study_plans** - Daily study schedules
- **quizzes** - Quiz metadata
- **quiz_responses** - Individual question responses
- **chat_sessions** - Chat conversation tracking
- **chat_messages** - Individual chat messages
- **uploaded_resources** - PDF files and metadata
- **progress_analytics** - Historical performance data

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Contribution Ideas
- 🎨 UI/UX improvements
- 📚 Add more topic curricula
- 🌐 Multi-language support
- 📱 Mobile responsiveness
- 🔔 Notification system
- 📈 Advanced analytics
- 🎮 Gamification features

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **HuggingFace** - LLaMA 3.2-3B-Instruct model for AI features
- **Streamlit** - Excellent framework for building data apps
- **Sentence Transformers** - Semantic search capabilities (all-MiniLM-L6-v2)
- **SQLAlchemy** - Robust ORM for database management

---

## 📞 Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/adaptive-study-planner/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/adaptive-study-planner/discussions)
- **Email:** your.email@example.com

---

## 🗺️ Roadmap

### Version 2.0 (Planned)
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration features
- [ ] Video call integration for tutoring
- [ ] Spaced repetition algorithm
- [ ] Integration with calendar apps
- [ ] Export progress reports as PDF
- [ ] Social features (study groups, leaderboards)

### Version 1.5 (In Progress)
- [x] Day progression system ✅
- [x] RAG-powered document Q&A ✅
- [ ] Voice input for chat
- [ ] Automated email reminders
- [ ] Integration with external quiz platforms

---

## ⚙️ Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `HF_TOKEN` | Yes | HuggingFace API token | - |
| `JWT_SECRET_KEY` | Yes | Secret key for JWT tokens | - |
| `DATABASE_URL` | No | Database connection string | `sqlite:///database.db` |

---

## 🧪 Testing

```bash
# Run database checks
python check_database.py

# Verify all tables exist
python -c "from database.db_manager import init_db; init_db()"

# Test AI connection
python -c "from llm.llm_client import LLMClient; print(LLMClient.call_llm('Hello', max_tokens=50))"
```

---

## 💡 Tips for Best Experience

1. **Complete onboarding honestly** - Better input = better plan
2. **Upload quality PDFs** - Clear, text-based documents work best (not scanned images)
3. **Take quizzes regularly** - Helps AI understand your progress
4. **Maintain daily streak** - Consistency is key to learning
5. **Ask specific questions** - AI gives better answers to detailed queries
6. **Review analytics weekly** - Track improvement over time
7. **Use chat with documents** - Ask "In my document..." for PDF-based answers

---

## 📚 FAQ

### Q: How does the day progression work?
**A:** The app automatically advances to the next day when you visit the Dashboard, based on your `last_active_date`. If you skip days, it will jump ahead and reset your streak.

### Q: Can I use this offline?
**A:** No, the app requires internet connection for AI features (quiz generation, chat). However, the database is local SQLite.

### Q: How is my data stored?
**A:** All data is stored locally in `database.db` (SQLite). Uploaded PDFs are in `data/uploads/`. No data is sent to external servers except HuggingFace API calls.

### Q: Can I change my topics after onboarding?
**A:** Yes! Go to Settings → Study Preferences → Add/Remove topics. You may need to regenerate your study plan.

### Q: Why is my quiz score low?
**A:** Check Progress → Quiz Performance to see your weak areas. Review those topics and try easier difficulty quizzes first.

---

**Built with ❤️ for learners worldwide**

**Happy Learning! 📚🚀**

---

## 🌟 Star History

If you find this project helpful, please consider giving it a ⭐!

---

**Version:** 1.0.0  
**Last Updated:** February 6, 2026  
**Maintainer:** [@DeveshGour27](https://github.com/DeveshGour27)
