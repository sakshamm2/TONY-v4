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


# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/sakshamm2/TONY-v4.git
```

## 2. Navigate to the Project

```bash
cd TONY-v4
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Launch T.O.N.Y.

```bash
python main.py
```


# ▶️ Getting Started

After launching T.O.N.Y., you can interact using either voice commands or text input.

The assistant automatically:

- Processes natural language requests
- Retrieves relevant memory
- Plans multi-step tasks when required
- Executes desktop actions
- Displays results in the dashboard
- Responds using synthesized speech


  # 💬 Example Commands

| User Command | T.O.N.Y. Action |
|--------------|-----------------|
| Open Calculator | Launches the Calculator application |
| Open Chrome | Starts Google Chrome |
| Create a folder named Projects | Creates a folder on the desktop |
| Search Python tutorials | Opens browser with search results |
| What's my CPU usage? | Displays live system statistics |
| Remember that my favorite language is Python | Stores information in long-term memory |
| What do you remember about me? | Retrieves stored memories |
| Tell me today's date | Returns the current system date |
| Open Downloads folder | Opens File Explorer in Downloads |


---

# 🎯 Current Capabilities

T.O.N.Y. v4 is currently capable of:

### 🤖 Artificial Intelligence
- Natural language conversations
- Context-aware responses
- Goal-oriented reasoning
- Intent understanding

### 🧠 Memory System
- Persistent long-term memory
- Context retrieval
- Memory management
- Conversation continuity

### 🎙️ Voice Interaction
- Speech recognition
- AI voice responses
- Hands-free interaction

### 🖥️ Desktop Automation
- Open applications
- Execute system commands
- File & folder management
- Browser automation
- Clipboard operations
- Process management

### 📊 Live Monitoring
- CPU usage
- RAM usage
- Disk information
- System telemetry

### 🎨 User Interface
- Modern holographic HUD
- Glassmorphism dashboard
- Live telemetry cards
- Animated visual effects
- Real-time status indicators

---

# 📈 Roadmap

## Completed

- [x] Modern PySide6 Dashboard
- [x] Holographic HUD
- [x] Conversational AI
- [x] Voice Recognition
- [x] AI Speech Synthesis
- [x] Persistent Memory
- [x] Desktop Automation
- [x] Agent Runtime
- [x] Modular Architecture
- [x] Live System Monitoring

## Planned

- [ ] Computer Vision
- [ ] Multi-Agent Collaboration
- [ ] Plugin Marketplace
- [ ] Smart Workflow Builder
- [ ] Calendar & Email Integration
- [ ] Cross-Platform Support
- [ ] Mobile Companion Application
- [ ] Cloud Memory Synchronization

---

# 🤝 Contributing

Contributions are welcome and appreciated.

If you would like to contribute:

1. Fork the repository.
2. Create a new feature branch.

```bash
git checkout -b feature/my-feature
```

3. Commit your changes.

```bash
git commit -m "Add new feature"
```

4. Push the branch.

```bash
git push origin feature/my-feature
```

5. Open a Pull Request.

Please ensure that all code follows the existing project architecture and coding style.

---

# 📄 License

This project is licensed under the **MIT License**.

You are free to use, modify, and distribute this software under the terms of the MIT License.

---

# 👨‍💻 Author

## Saksham

**Computer Science Engineering Student**

Developer of **T.O.N.Y. v4** — an agentic desktop AI assistant focused on conversational intelligence, autonomous task execution, desktop automation, and modern interface design.

GitHub:
https://github.com/sakshamm2

---

# ⭐ Support the Project

If you found this project useful or interesting:

⭐ Star the repository

🐛 Report bugs

💡 Suggest new features

🤝 Contribute to development

---

<p align="center">

### Thank you for checking out T.O.N.Y. v4!

**If you enjoyed this project, consider giving it a ⭐ on GitHub.**

</p>


# 📌 Project Statistics

![Python](https://img.shields.io/badge/Python-3.12-blue)

![Platform](https://img.shields.io/badge/Platform-Windows-success)

![License](https://img.shields.io/badge/License-MIT-green)

![Status](https://img.shields.io/badge/Status-Active-brightgreen)
