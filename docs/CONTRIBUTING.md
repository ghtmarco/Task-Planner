# Contributing

If you want to contribute to Task Planner, here is how you can help.

## Development setup

1. Clone the repository and install the dependencies from `requirements.txt`.
2. Make sure you have a valid Gemini API key in your `.env` file.
3. We use `pytest` for testing. You can run the test suite by simply running:
   ```bash
   pytest
   ```

## Scripts reference

| Command | Description |
|---------|-------------|
| `python app.py` | Start the local Gradio development server |
| `pytest` | Run the test suite |

## Making changes

- Create a new branch for your feature or bugfix.
- Keep your changes focused. If you are updating the ML models in `Models/`, make sure to document how you trained the new model and provide the training script or dataset if possible.
- Update the documentation if you change the API or add new environment variables.
- Submit a pull request. We will review it as soon as we can.
