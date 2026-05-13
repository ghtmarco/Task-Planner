# Task Planner

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## About

I built this project to fulfill the requirements for the **COMP6065001 - LEC** course at **Binus University**. 

Task Planner is a scheduling tool that uses a mix of large language models (Google's Gemini Flash 2.0 Exp) and a Random Forest machine learning model. Instead of just blocking out time on a calendar, it tries to allocate your tasks based on complexity, available hours, and energy levels. 

## How it works

The core scheduler sits in `src/schedule_ai.py`. It takes your high-level goals and time constraints, runs them through the ML model to guess the complexity, and then passes everything to Gemini to generate a readable, prioritized schedule.

We use Gradio for the frontend, which gives you a simple web interface to input your constraints and see the output immediately.

## Getting started

You need Python 3.9 or newer.

1. Clone the repository:
```bash
git clone https://github.com/ghtmarco/Task-Planner.git
cd Task-Planner
```

2. Install the requirements:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables. You will need a Google Gemini API key. Copy the example file and add your key:
```bash
cp .env.example .env
```

4. Run the app:
```bash
python app.py
```

The Gradio interface will start locally. Open the provided localhost link in your browser to start generating schedules.

## Using it in code

If you prefer to bypass the UI and use the scheduler directly in your own scripts:

```python
from src.schedule_ai import SimpleScheduler

planner = SimpleScheduler()

schedule = planner.generate_schedule(
    duration="weekly",
    goals="Learn AI fundamentals and practice coding",
    available_hours=4,
    considerations="Morning study sessions preferred"
)

print(schedule)
```

## Repository structure

- `app.py`: The Gradio web interface.
- `src/schedule_ai.py`: Core scheduling logic and API calls.
- `Models/`: Contains the trained Random Forest model (`random_forest_model.pkl`) and scaler (`scaler.pkl`).
- `docs/`: Contributing guidelines and environment variable documentation.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
