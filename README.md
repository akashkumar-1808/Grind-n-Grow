# Grind ’n Grow – Smart Study & Focus Planner

> “Consistency isn’t about perfection. It’s about progress that never stops.”

---

##  Overview

**Grind ’n Grow** is a productivity web app designed to help students stay focused, consistent, and motivated while completing their syllabus.  
It combines **time tracking, intelligent scheduling, and motivational systems** into one personalized study planner.

The platform is powered by **Python (Flask)** for backend logic and **HTML, CSS, and JavaScript** for the frontend interface.

---

##  Problem Statement

Students often struggle with:
- Staying consistent with their study goals  
- Managing subjects and deadlines  
- Measuring real progress  
- Maintaining focus during long sessions  

**Grind ’n Grow** solves this by providing a **personal productivity dashboard**, **smart Task Editor**, and **progress tracking** — turning small daily efforts into visible growth.

---

##  Tech Stack

| Layer | Technology Used |
|-------|------------------|
| **Backend** | Python, Flask, SQLAlchemy |
| **Database** | PostgreSQL (configurable with SQLite or any SQL DB) |
| **Frontend** | HTML, CSS, JavaScript |
| **APIs** | RESTful Flask API |
| **Authentication** | Password hashing with Werkzeug |
| **Hosting (Optional)** | Render / Vercel / Railway |
| **Environment Management** | Python-dotenv |

---

##  Key Features

###  Focus & Time Management
- Start, pause, and stop custom study sessions  
- Auto track completed hours per task  
- Countdown timer with progress sync  

###  Smart Scheduler
- User Can Generate a **weekly plan** based on study hours  
- Adjusts daily slots between **9 AM – 9 PM**  
- Deletes old sessions before new ones are generated  

### Task Management
- Add, edit, or delete subjects and tasks  
- Set deadlines and priorities  
- Visualize subject-wise completion  

###  Motivation System
- Dynamic daily quotes on consistency and discipline  
- Refreshes every day and resets every Monday  

###  Progress Tracking
- Weekly progress percentage  
- Subject-wise breakdown  
- Incomplete tasks are rolled forward automatically  

---

##  API Endpoints

| Method | Endpoint | Description |
|:-------|:----------|:------------|
| `POST` | `/signup` | Create new user |
| `POST` | `/login` | User login |
| `POST` | `/tasks` | Add a task |
| `PUT` | `/tasks/<task_id>` | Update a task |
| `DELETE` | `/tasks/<task_id>` | Delete a task |
| `POST` | `/sessions` | Add a study session |
| `PATCH` | `/sessions/<id>` | Update session progress |
| `GET` | `/progress/<email>` | Get weekly & subject progress |
| `POST` | `/schedule/generate` | generate study schedule |

---

##  Installation & Setup

###  Clone the Repository
```bash
git clone https://github.com/yourusername/grind-n-grow.git
cd grind-n-grow
