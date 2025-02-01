import gradio as gr
from src.schedule_ai import SimpleScheduler
import traceback

def create_schedule(duration, goals, available_hours, considerations):
    """Create a schedule based on user input"""
    try:
        if not duration or not goals or not considerations:
            return "Error: Please fill in all fields"
        
        scheduler = SimpleScheduler()
        schedule = scheduler.generate_schedule(
            duration=duration,
            goals=goals,
            available_hours=float(available_hours),
            considerations=considerations
        )
        
        return schedule
    except Exception as e:
        print(traceback.format_exc())
        return f"Error: {str(e)}"


iface = gr.Interface(
    fn=create_schedule,
    inputs=[
        gr.Textbox(
            label="Duration",
            placeholder="e.g., 1 week, 1 month, 1 year",
            info="Format: number + week/month/year"
        ),
        gr.Textbox(
            label="Goals",
            placeholder="Describe your goals",
            lines=3
        ),
        gr.Slider(
            label="Available Hours per Day",
            minimum=1,
            maximum=12,
            value=8,
            step=0.5
        ),
        gr.Textbox(
            label="Special Considerations",
            placeholder="e.g., meetings, breaks, preferences",
            lines=2
        )
    ],
    outputs=gr.Textbox(
        label="Your Schedule", 
        lines=30
    ),
    title="📅 Task Planner",
    description="Generate a personalized schedule based on your goals"
)

if __name__ == "__main__":
    iface.launch(show_error=True)