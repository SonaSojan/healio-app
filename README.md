# Healio – Anonymous Drug Withdrawal Support System

Healio is a web application that allows individuals experiencing drug withdrawal symptoms to communicate anonymously with doctors and receive guidance.

## Features
- Anonymous user IDs
- Symptom submission
- Automatic severity detection
- Emergency alerts
- Doctor messaging dashboard
- SQLite database for message storage

## Technologies Used
- Python
- Flask
- HTML
- SQLite
- GitHub
- Render (deployment)

## How It Works
1. User submits symptoms.
2. System detects severity internally.
3. User sends message to doctor.
4. Doctor views severity and replies through dashboard.
5. Messages are stored in database.

## Project Structure
healio_app/
│
├── app.py
├── database.py
├── severity.py
├── templates/
│ ├── index.html
│ └── doctor.html
├── requirements.txt
└── Procfile

## Deployment
This application is deployed using Render.

## Future Improvements
- AI-based symptom analysis
- Real-time chat
- Doctor authentication
- Mobile app version
  
