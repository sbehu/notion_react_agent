# Agentic AI Assistant v3 (LangGraph + Groq + Notion)

An intelligent, memory-retaining, multi-tool AI Agent built using **LangGraph**, **FastAPI**, and **Docker**. The backend leverages Groq's high-speed **Mixtral-8x7b** mixture-of-experts architecture to reliably route user intents across disparate data ecosystems including Notion workspaces, calendar matrices, weather metrics, and live web exploration.

---

## 🛠️ Architecture & Tool Stack

The agent utilizes a reactive routing state machine (`create_react_agent`) backed by persistence-based short-term memory checkpointers to execute execution paths dynamically.

* **Core Engine:** LangGraph + LangChain Community Utilities
* **LLM Brain:** `mixtral-8x7b-32768` (via Groq API) calibrated at $Temperature = 0.2$ for deterministic structural JSON parsing.
* **Active Toolkits:**
    * **Notion Hub:** Custom integration layers to index, append (`add_note`), and safely isolate page entities (`delete_notion_page`).
    * **Calendar Hub:** Automation workflows tracking event states (`get_calendar_events`, `add_calendar_event`, `delete_calendar_event`).
    * **Search Engine:** Live web scraping injection via `DuckDuckGoSearchRun`.
    * **Environmental Context:** Real-time localized weather data parsing.

---

## 📁 Project Directory Layout

```text
├── .env                       # Local execution credential variables
├── .gitignore                 # Version control exclusion maps
├── docker-compose.yml         # Container definitions & persistent volume mounting
├── Dockerfile                 # Multi-stage python container configuration
├── main.py                    # App runner & FastAPI routing gateway
├── requirements.txt           # Monitored python packages
├── static/                    # Frontend client user interface assets
│   ├── index.html
│   ├── style.css
│   └── script.js
├── agent/                     # Core cognitive routing logic
│   ├── __init__.py
│   └── bot_v3.py              # Main graph setup, system prompts, and tool bindings
└── tools/                     # Isolated programmatic functional utility packages
    ├── delete_notion_page.py
    ├── notion_calendar.py
    ├── notion_notes.py
    └── weather.py