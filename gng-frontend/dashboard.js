// dashboard.js
// Handles both logged-in and guest users.
// - Logged-in users → backend (PostgreSQL)
// - Guests → localStorage until manually cleared.

const API_BASE = "http://127.0.0.1:5000";
const user = JSON.parse(localStorage.getItem("user") || "null");
const isGuest = !user;

document.addEventListener("DOMContentLoaded", () => {
  initUI();
  loadAll();
});

/* -------------------- UI SETUP -------------------- */
function initUI() {
  // Sidebar tab switching
  const tabs = document.querySelectorAll(".sidebar ul li");
  tabs.forEach(t => {
    t.addEventListener("click", () => {
      document.querySelectorAll(".sidebar ul li").forEach(x => x.classList.remove("active"));
      t.classList.add("active");
      document.querySelectorAll(".tab").forEach(tab => tab.classList.remove("active"));
      document.getElementById(t.dataset.tab).classList.add("active");
    });
  });

  // Current user display
  const currentUserEl = document.getElementById("currentUser");
  currentUserEl.textContent = user ? user.username : "Guest";

  // Logout
  document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.removeItem("user");
    window.location.href = "index.html";
  });

  // Clear guest data
  const clearBtn = document.getElementById("clearGuest");
  if (clearBtn) {
    clearBtn.addEventListener("click", () => {
      if (confirm("Clear guest tasks and progress?")) {
        localStorage.removeItem("guest_tasks");
        loadAll();
      }
    });
  }

  // Add new task
  document.getElementById("addTaskForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const title = document.getElementById("taskTitle").value.trim();
    const subject = document.getElementById("taskSubject").value.trim();
    const deadline = document.getElementById("taskDeadline").value;
    const study_hours = parseFloat(document.getElementById("taskHours").value || 0);
    const priority = document.getElementById("taskPriority").value;

    if (!title) return alert("Enter a title");

    const taskPayload = { title, subject, deadline: deadline || null, study_hours, priority };

    if (isGuest) {
      const localTasks = JSON.parse(localStorage.getItem("guest_tasks") || "[]");
      const id = Date.now();
      localTasks.push({ id, ...taskPayload, is_completed: false, created_at: new Date().toISOString() });
      localStorage.setItem("guest_tasks", JSON.stringify(localTasks));
      clearAddForm();
      renderTasks(localTasks);
      renderCalendarEvents(localTasks);
      updateSummary();

      // 🕒 Start timer when new task is added
      if (study_hours > 0) {
        startTaskTimer(study_hours * 60); // 1 hour = 60 mins
      }

      return;
    }

    // Logged-in user → backend
    taskPayload.user_email = user.email;
    try {
      const res = await fetch(`${API_BASE}/tasks`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(taskPayload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Failed");
      clearAddForm();
      await loadTasks();
    } catch (err) {
      console.error(err);
      alert("Could not add task");
    }
  });

  // Initialize Calendar and Chart
  initFullCalendar();
  initChart();

  // Optional schedule generator
  const genBtn = document.getElementById("generateBtn");
  if (genBtn) {
    genBtn.addEventListener("click", async () => {
      const start = prompt("Enter week start (YYYY-MM-DD). Example: 2025-11-03");
      if (!start) return;
      if (isGuest) return alert("Guest schedule generation not implemented.");

      try {
        const res = await fetch(`${API_BASE}/schedule/generate`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ user_email: user.email, week_start: start })
        });
        if (!res.ok) throw new Error("generate failed");
        const d = await res.json();
        alert(`Created ${d.sessionsCreated} sessions`);
        await loadSessions();
      } catch (err) {
        console.error(err);
        alert("Schedule generation failed");
      }
    });
  }
}

/* -------------------- CLEAR FORM -------------------- */
function clearAddForm() {
  document.getElementById("taskTitle").value = "";
  document.getElementById("taskSubject").value = "";
  document.getElementById("taskDeadline").value = "";
  document.getElementById("taskHours").value = "";
}

/* -------------------- CALENDAR -------------------- */
let calendar;
function initFullCalendar() {
  const calendarEl = document.getElementById("fullCalendar");
  if (!calendarEl) return;

  calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: "dayGridMonth",
    selectable: true,
    editable: true,
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "dayGridMonth,timeGridWeek,timeGridDay"
    },
    dateClick: (info) => {
      const title = prompt("Add task for " + info.dateStr + ":");
      if (title) {
        calendar.addEvent({
          title,
          start: info.dateStr,
          allDay: true
        });
      }
    },
    eventDrop: async (info) => {
      const ev = info.event;
      const taskId = ev.extendedProps.taskId;
      const newDate = ev.startStr;
      if (isGuest) {
        const tasks = JSON.parse(localStorage.getItem("guest_tasks") || "[]");
        const t = tasks.find(x => String(x.id) === String(taskId));
        if (t) {
          t.deadline = newDate;
          localStorage.setItem("guest_tasks", JSON.stringify(tasks));
          renderTasks(tasks);
          updateSummary();
        }
      } else {
        try {
          const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ deadline: newDate })
          });
          if (!res.ok) throw new Error("update failed");
          await loadTasks();
        } catch (err) { console.error(err); }
      }
    }
  });
  calendar.render();
}

function renderCalendarEvents(tasks) {
  if (!calendar) return;
  calendar.removeAllEvents();
  tasks.forEach(t => {
    if (t.deadline) {
      const date = t.deadline.includes("T") ? t.deadline.split("T")[0] : t.deadline;
      calendar.addEvent({
        id: String(t.id),
        title: t.title,
        start: date,
        allDay: true,
        extendedProps: { taskId: t.id }
      });
    }
  });
}

/* -------------------- LOAD -------------------- */
async function loadAll() {
  await loadTasks();
  await loadSessions();
  updateSummary();
}

async function loadTasks() {
  if (isGuest) {
    const tasks = JSON.parse(localStorage.getItem("guest_tasks") || "[]");
    renderTasks(tasks);
    renderCalendarEvents(tasks);
    return;
  }
  try {
    const res = await fetch(`${API_BASE}/tasks/${encodeURIComponent(user.email)}`);
    const data = await res.json();
    renderTasks(data.tasks || []);
    renderCalendarEvents(data.tasks || []);
  } catch (err) { console.error(err); }
}

async function loadSessions() {
  if (isGuest) return;
  try {
    const res = await fetch(`${API_BASE}/sessions/${encodeURIComponent(user.email)}`);
    const data = await res.json();
    if (data.sessions) {
      data.sessions.forEach(s => {
        calendar.addEvent({
          id: 's' + s.id,
          title: 'Session',
          start: s.start,
          end: s.end
        });
      });
    }
  } catch (err) { console.error(err); }
}

/* -------------------- TASKS -------------------- */
function renderTasks(tasks) {
  const el = document.getElementById("tasksList");
  el.innerHTML = "";
  tasks.forEach(t => {
    const div = document.createElement("div");
    div.className = "task";
    div.innerHTML = `
      <div class="meta">
        <h4>${t.title}</h4>
        <p>${t.subject || ""} • ${t.deadline ? new Date(t.deadline).toLocaleDateString() : "No deadline"} • ${t.study_hours || 0} hrs</p>
      </div>
      <div class="actions">
        <button class="btn" data-id="${t.id}" data-act="toggle">${t.is_completed ? 'Undo' : 'Done'}</button>
        <button class="btn" data-id="${t.id}" data-act="delete">Delete</button>
      </div>
    `;
    el.appendChild(div);
  });

  el.querySelectorAll("button").forEach(btn => {
    btn.addEventListener("click", async () => {
      const id = btn.dataset.id;
      const act = btn.dataset.act;

      if (act === "delete") {
        if (!confirm("Delete task?")) return;
        if (isGuest) {
          let tasks = JSON.parse(localStorage.getItem("guest_tasks") || "[]");
          tasks = tasks.filter(x => String(x.id) !== String(id));
          localStorage.setItem("guest_tasks", JSON.stringify(tasks));
          renderTasks(tasks); renderCalendarEvents(tasks); updateSummary();
        } else {
          try {
            const r = await fetch(`${API_BASE}/tasks/${id}`, { method: "DELETE" });
            if (!r.ok) throw new Error("delete failed");
            await loadTasks(); updateSummary();
          } catch (err) { console.error(err); alert("Delete failed"); }
        }
      } else if (act === "toggle") {
        if (isGuest) {
          const tasks = JSON.parse(localStorage.getItem("guest_tasks") || "[]");
          const t = tasks.find(x => String(x.id) === String(id));
          if (t) {
            t.is_completed = !t.is_completed;
            localStorage.setItem("guest_tasks", JSON.stringify(tasks));
            renderTasks(tasks);
            updateSummary();
            if (t.is_completed) stopTaskTimer(); // ⏹ Stop timer when task done
          }
        } else {
          try {
            const r = await fetch(`${API_BASE}/tasks/${id}`, {
              method: "PUT",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ is_completed: !(btn.textContent === 'Undo') })
            });
            if (!r.ok) throw new Error("update failed");
            await loadTasks(); updateSummary();
          } catch (err) { console.error(err); }
        }
      }
    });
  });
}

/* -------------------- CHART -------------------- */
let chart;
function initChart() {
  const ctx = document.getElementById("progressChart").getContext("2d");
  chart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Completed", "Remaining"],
      datasets: [{ data: [0, 100], backgroundColor: ["#057dcd", "#e9f3fb"] }]
    },
    options: { cutout: "70%", plugins: { legend: { display: false } } }
  });
}
function setChart(done, total) {
  const comp = total ? Math.round((done / total) * 100) : 0;
  chart.data.datasets[0].data = [comp, 100 - comp];
  chart.update();
}

/* -------------------- SUMMARY -------------------- */
function updateSummary() {
  if (isGuest) {
    const tasks = JSON.parse(localStorage.getItem("guest_tasks") || "[]");
    const total = tasks.length;
    const done = tasks.filter(t => t.is_completed).length;
    const upcoming = tasks.filter(t => t.deadline && new Date(t.deadline) >= new Date()).length;
    document.getElementById("totalTasks").textContent = total;
    document.getElementById("completedTasks").textContent = done;
    document.getElementById("upcomingTasks").textContent = upcoming;
    setChart(done, total);
    return;
  }
}

/* -------------------- MOTIVATIONAL POPUP -------------------- */
document.addEventListener("DOMContentLoaded", () => {
  const popup = document.getElementById("motivationalPopup");
  const closeBtn = document.getElementById("closePopup");
  const quoteText = document.getElementById("quoteText");
  const quotes = [
    "“Push yourself, because no one else is going to do it for you.”",
    "“Don’t watch the clock; do what it does. Keep going.”",
    "“Success doesn’t come from what you do occasionally, it comes from what you do consistently.”",
    "“The secret of getting ahead is getting started.”",
    "“Small steps every day lead to big results.”"
  ];
  if (!sessionStorage.getItem("popupShown")) {
    const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
    quoteText.textContent = randomQuote;
    popup.classList.add("active");
    sessionStorage.setItem("popupShown", "true");
  }
  closeBtn.addEventListener("click", () => popup.classList.remove("active"));
});

/* -------------------- QUOTE UNDER PROGRESS BAR -------------------- */
const quotes = [
  "You're doing great — keep going!",
  "Progress, not perfection!",
  "Small steps lead to big wins!",
  "Every click counts toward success!",
  "Consistency is your superpower!",
  "You’re unstoppable — keep that energy up!"
];
const quoteEl = document.getElementById("motivational-quote");
if (quoteEl) {
  const randomQuote = quotes[Math.floor(Math.random() * quotes.length)];
  quoteEl.style.opacity = 0;
  setTimeout(() => {
    quoteEl.textContent = randomQuote;
    quoteEl.style.opacity = 1;
  }, 400);
}

/* -------------------- TASK TIMER -------------------- */
let timerInterval;
let totalTime = 0;
let remainingTime = 0;
let isPaused = false;

const timerContainer = document.getElementById('task-timer');
const display = document.getElementById('timer-display');
const progressRing = document.getElementById('progress-ring');
const pauseBtn = document.getElementById('pause-btn');

function startTaskTimer(minutes) {
  totalTime = minutes * 60;
  remainingTime = totalTime;
  timerContainer.style.display = 'block';
  updateTimerDisplay();
  updateCircle();

  timerInterval = setInterval(() => {
    if (!isPaused) {
      remainingTime--;
      updateTimerDisplay();
      updateCircle();
      if (remainingTime <= 0) {
        clearInterval(timerInterval);
        alert("🎉 Time’s up! Great work on your task!");
      }
    }
  }, 1000);
}

function updateTimerDisplay() {
  const mins = Math.floor(remainingTime / 60);
  const secs = remainingTime % 60;
  display.textContent = `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

function updateCircle() {
  const progress = (remainingTime / totalTime) * 565;
  progressRing.style.strokeDashoffset = 565 - progress;
}

pauseBtn.addEventListener('click', () => {
  isPaused = !isPaused;
  pauseBtn.textContent = isPaused ? "▶ Resume" : "⏸ Pause";
});

function stopTaskTimer() {
  clearInterval(timerInterval);
  timerContainer.style.display = 'none';
}
