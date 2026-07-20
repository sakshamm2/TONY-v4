# 🤖 T.O.N.Y. v4

<p align="center">
  <b>An Agentic AI Desktop Assistant inspired by J.A.R.V.I.S.</b>
</p>

<p align="center">
  Voice Interaction • Long-Term Memory • Autonomous Planning • Desktop Automation • Modern Holographic UI
</p>

---

## 📖 Overview

T.O.N.Y. (Technologically Optimized Neural Yielder) v4 is a next-generation desktop AI assistant built entirely in Python.

Unlike traditional chatbots, T.O.N.Y. is designed as an **Agentic AI Assistant** capable of understanding goals, planning tasks, remembering context, interacting through voice, and automating desktop operations.

T.O.N.Y. v4 combines conversational AI, autonomous task planning, persistent memory, voice interaction, desktop automation, and a futuristic holographic interface into a unified modular platform. Built using a layered architecture, each subsystem has a dedicated responsibility, making the project scalable, maintainable, and easy to extend.
---

# ✨ Features

- 🧠 Agentic AI Architecture
- 💬 Natural Language Conversations
- 🎙️ Voice Recognition
- 🔊 AI Speech Response
- 🧠 Persistent Long-Term Memory
- 📂 File & Folder Access
- 🖥️ Desktop Automation
- ⚡ Autonomous Task Planning
- 📊 Live System Monitoring
- 🌐 Internet-enabled AI Responses
- 🎨 Futuristic Holographic HUD
- ⚙️ Modular Production Architecture

---

# 🖼️ Screenshots

## Dashboard

![Dashboard](assets/screenshots/dashboard.png)

---

## Listening Mode

![Listening](assets/screenshots/listening.png)

---

## Thinking Mode

![Thinking](assets/screenshots/thinking.png)

---

## Speaking Mode

![Speaking](assets/screenshots/speaking.png)

---

## Agent Planner

![Planner](assets/screenshots/planner.png)

---

## Memory System

![Memory](assets/screenshots/memory.png)

---

# 🏗️ System Architecture

T.O.N.Y. v4 follows a modular layered architecture where every component has a dedicated responsibility. The user interface handles interactions, the Assistant Controller coordinates all subsystems, the AI Engine performs reasoning, the Agent Runtime plans multi-step tasks, and specialized tools interact with the operating system.

```text
                              USER
                                │
                 Voice Commands / Text Input
                                │
                                ▼
                     Dashboard (PySide6 UI)
                                │
                                ▼
                   Assistant Controller
                                │
         ┌──────────────────────┼──────────────────────┐
         ▼                      ▼                      ▼
    AI Engine             Voice Engine          Memory Service
         │
         ▼
     Agent Runtime
         │
         ▼
   Intent Router
         │
         ▼
       Planner
         │
         ▼
 Workflow Engine
         │
         ▼
      Executor
         │
         ▼
    Tool Registry
         │
 ┌───────┼────────┬─────────┬───────────┐
 ▼       ▼        ▼         ▼           ▼
Files  Browser  Clipboard  Shell   PC Control
         │
         ▼
 Windows Operating System
```
# 🔄 Request Workflow

Every request follows a structured execution pipeline to ensure consistent processing and modularity.

```text
User

↓

Dashboard receives command

↓

Assistant Controller processes request

↓

AI Engine understands intent

↓

Memory retrieves relevant context

↓

Agent Runtime creates an execution plan

↓

Planner breaks goal into executable tasks

↓

Executor performs each task

↓

Tools interact with Windows

↓

Assistant receives the result

↓

Dashboard updates the interface

↓

Voice Engine speaks the response
```

# 🧩 Core Components

| Component | Responsibility |
|-----------|----------------|
| Dashboard | Main application window and user interaction |
| Widgets | Reusable interface components such as HUD, chat panel, telemetry cards, and status bar |
| Assistant Controller | Central coordinator that manages all subsystems |
| AI Engine | Processes prompts and generates intelligent responses |
| Voice Engine | Handles speech recognition and text-to-speech |
| Memory System | Stores and retrieves long-term conversation context |
| Agent Runtime | Converts user goals into executable workflows |
| Planner | Breaks complex goals into smaller tasks |
| Executor | Executes planned tasks in sequence |
| Tool Layer | Provides access to operating system functionality |
| Modules | Backend services such as monitoring and automation |
| Renderers | Draw the holographic HUD and visual effects |

# 📁 Folder Overview

| Folder | Purpose |
|---------|---------|
| **core/** | Core application logic including AI, voice, memory, assistant controller, workers, and the agent runtime |
| **modules/** | Backend services such as automation, system monitoring, memory management, and desktop control |
| **renderers/** | Rendering engine responsible for the radar, rings, particles, waveform, and telemetry animations |
| **tools/** | Desktop capability layer providing browser, file, clipboard, shell, process, and PC control tools |
| **widgets/** | Reusable PySide6 user interface components used throughout the dashboard |

# 🛠 Tech Stack

| Category | Technologies |
|----------|--------------|
| **Programming Language** | Python 3.12+ |
| **GUI Framework** | PySide6 (Qt) |
| **Artificial Intelligence** | Google Gemini |
| **Voice Recognition** | SpeechRecognition |
| **Speech Synthesis** | Windows SAPI |
| **Desktop Automation** | PyAutoGUI, Windows APIs |
| **System Monitoring** | psutil |
| **Storage** | SQLite |
| **Version Control** | Git & GitHub |

# 🏛️ Design Principles

T.O.N.Y. v4 is built around a modular architecture where each subsystem has a clearly defined responsibility.

- **Separation of Concerns** – User interface, AI, memory, rendering, and desktop automation are isolated into independent modules.
- **Modularity** – New tools, widgets, and agent capabilities can be integrated without affecting the overall architecture.
- **Maintainability** – Components communicate through well-defined interfaces, making the project easier to understand, test, and extend.
- **Scalability** – The layered design allows future expansion, including vision support, plugin systems, multi-agent workflows, and cross-platform compatibility.

- 
