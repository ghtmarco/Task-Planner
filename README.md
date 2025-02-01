# AI-Powered Task Planner

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An intelligent task scheduling system powered by Google's Gemini Flash 2.0 Exp LLM with integrated machine learning capabilities.

## Features

- 🧠 Hybrid AI scheduling combining LLM and ML (Random Forest)
- 📅 Dynamic time slot optimization
- ⚡ Real-time schedule generation
- 🎯 Priority-based task allocation
- 🔄 Adaptive scheduling based on:
  - Task complexity analysis
  - Time availability patterns
  - User preferences
  - Energy level predictions

## Installation

1. Clone repository:
```bash
git clone https://github.com/yourusername/task-planner.git
cd task-planner
```

2. Install dependencies:
```bash
pip install gradio
pip install google-generativeai
pip install python-dotenv
pip install joblib
pip install pandas
pip install numpy
pip install scikit-learn
```

## Usage

```python
from src.schedule_ai import SimpleScheduler

planner = SimpleScheduler()

# Generate a weekly schedule
schedule = planner.generate_schedule(
    duration="weekly",
    goals="Learn AI fundamentals and practice coding",
    available_hours=4,
    considerations="Morning study sessions preferred"
)

print(schedule)
```

Sample output:
```
Schedule Overview
----------------
Duration: weekly
Goals: Learn AI fundamentals and practice coding
Hours per day: 4
Notes: Morning study sessions preferred
----------------

Monday
09:00 - Core Concepts Study (High)
10:00 - Coding Practice (High)

Tuesday
09:00 - Algorithm Review (High)
10:00 - Problem Solving (Medium)
...
```

## Configuration

`app.py` - Main application interface
```
.
├── Models/                 # Machine learning models
│   ├── random_forest_model.pkl
│   └── scaler.pkl
├── src/                    # Core logic
│   └── schedule_ai.py
└── requirements.txt        # Dependencies
```

## Requirements

- Python 3.9+
- Google Generative AI API key
- scikit-learn
- pandas

## License

MIT License - See [LICENSE](LICENSE) for details