# AI Task Organizer using Gemini and LangGraph

## Project Overview

AI Task Organizer is an AI-powered application that helps users organize their tasks according to deadlines and priorities. Users can enter their daily tasks in natural language, and the application uses Google Gemini and LangGraph to analyze and organize them into a structured to-do list.

The project uses FastAPI to provide an API endpoint for submitting tasks and receiving organized results.

## Features

- Extracts multiple tasks from natural-language input.
- Identifies task deadlines.
- Assigns priorities such as High, Medium, and Low.
- Organizes tasks into a clear to-do list.
- Uses LangGraph to manage the AI workflow.
- Provides an interactive API interface through Swagger UI.

## Technologies Used

- Python
- FastAPI
- LangGraph
- Google Gemini
- LangChain Google GenAI
- Uvicorn
- Python-dotenv

## Project Workflow

1. **User Input:** The user enters tasks in natural language.
2. **Task Extraction:** Gemini identifies individual tasks and their deadlines.
3. **Priority Detection:** The AI assigns priorities based on task urgency and deadlines.
4. **Result Formatting:** The application generates an organized to-do list.
5. **API Response:** FastAPI returns the results in JSON format.

## Project Structure

```text
AI-Task-Organizer/
│
├── app.py
├── test_gemini.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

The `.env` file contains the private API key and should not be uploaded to GitHub.

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/sohailzainab629-cpu/AI-Task-Organizer.git
cd AI-Task-Organizer
```

### 2. Create a Virtual Environment

```bash
py -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
py -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-3.5-flash-lite
```

Replace the placeholder with your own Gemini API key. Never share or commit your real API key.

### 5. Run the Application

```bash
py -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

### 6. Open Swagger UI

Visit:

http://127.0.0.1:8000/docs

Use the `POST /organize` endpoint to submit tasks and view the organized response.

## Example Request

```json
{
  "message": "Complete my AI assignment today, prepare for my Python viva tomorrow, and submit my project report by Friday."
}
```

## Example Response

```json
{
  "success": true,
  "tasks": [
    {
      "task": "complete my AI assignment",
      "deadline": "today",
      "priority": "High"
    },
    {
      "task": "prepare for my Python viva",
      "deadline": "tomorrow",
      "priority": "High"
    },
    {
      "task": "submit my project report",
      "deadline": "Friday",
      "priority": "Medium"
    }
  ],
  "formatted_list": "YOUR ORGANIZED TO-DO LIST..."
}
```

*Note: Task priorities and response formatting may vary depending on the AI model's output.*

## Testing

The application was tested using FastAPI Swagger UI. The `POST /organize` endpoint returned a successful HTTP `200` response for a sample task-organizing request.

The Gemini connection can also be tested using:

```bash
py test_gemini.py
```

## Security

- Keep your Gemini API key private.
- Add `.env` and `.venv/` to `.gitignore`.
- Upload `.env.example` with placeholder values instead of actual secrets.

## Author

**Zainab Sohail**

## License

This project is developed for educational and learning purposes.
