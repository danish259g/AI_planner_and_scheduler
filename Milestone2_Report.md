# Milestone 2: Initial Mockup - AI Planner & Scheduler

**Date:** December 23, 2025
**Project:** AI Weekly Planner & Scheduler
**Team:** [User Name / Team Name]

---

## 1. Project Summary

### The Problem: The Granularity Gap
Current digital productivity tools like Google Calendar and Todoist act as passive "storage bins." They excel at managing fixed appointments but fail to handle the "long tail" of daily life—the floating tasks, errands, and routines that clutter a user's mind (e.g., "buy groceries," "call the bank"). Users are forced to manually solve complex constraint satisfaction problems to fit these tasks into their day, leading to high cognitive load, unrealistic planning, and eventually, abandonment of the tools.

### The Solution: Intelligent Time Orchestration
Our system shifts the focus from simple time tracking to **Intelligent Time Orchestration**. Instead of requiring manual entry for every slot, users input vague or structured tasks, and the AI automates the creation of "Implementation Intentions"—defining exactly when and where a task will happen. This reduces the mental burden of daily logistics and transforms the planner into an active agent that helps manage a user's energy and time.

### Unique Approach: Hybrid Agentic Pipeline
We bridge the gap between flexible but unreliable Generative AI (LLMs) and rigid but accurate scheduling algorithms. Our unique 3-stage pipeline (Interpreter, Scheduler, Verifier) ensures that the system handles the nuances of human language (e.g., "I need a run after work") while guaranteeing mathematically valid, clash-free schedules through a dedicated verification layer.

---

## 2. Design Principles (HAI Guidelines)

Our design is guided by the **Google PAIR (People + AI Research) Guidebook** to ensure a trust-based, collaborative user experience.

### Principle 1: Build Mental Models (Set Expectations)
*   **Guideline:** Help the user understand what the AI can do and why.
*   **Implementation:** The system doesn't just "output" a schedule; it provides a **Logic Summary**. When a user adds a task, the AI explains its placement logic (e.g., *"I scheduled your run for Tuesday evening because you have a gap after your meeting"*). This transparency builds a mental model of the AI as a collaborator.

### Principle 2: Support Mixed-Initiative Interaction (User Control)
*   **Guideline:** Give the user control to override or refine AI suggestions.
*   **Implementation:** The **Negotiation Loop** allows users to treat the schedule as a draft. Users can say, *"Tuesday is too heavy,"* and the AI will propose a new arrangement. Furthermore, the **Locking Mechanism** empowers users to fix certain tasks in place, forcing the AI to optimize the remaining "floating" tasks around their immutable choices.

### Principle 3: Design for Feedback and Calibration
*   **Guideline:** Allow users to calibrate the AI's behavior over time.
*   **Implementation:** The **"My Vibe"** preference profile allows users to input soft constraints (e.g., *"I'm not a morning person"*). The AI uses this profile to calibrate its scheduling logic, ensuring the output aligns with the user's personal energy flow.

---

## 3. Interface Design & Instruction

The interface is built as a **3-column dashboard** designed with **Glassmorphism** aesthetics.

![AI Planner Dashboard Mockup](ai_planner_dashboard_overview.png)
*(Note: Mockup generated to represent the final system state with high-fidelity components.)*

### User Task 1: Adding a Floating Task via Natural Language
*   **Description:** The user types *"Need to hit the gym for an hour sometime this week"* into the Task Input.
*   **AI Action:** The **Interpreter Agent** (using `gemini-2.5-flash-lite`) extracts the duration (60 min), category (Fitness), and priority. It adds it to the "Task Bank" as a floating item.
*   **Design Note:** Features a clean text entry field with a "✨ Interpret" button and real-time visual feedback of extracted metadata.

### User Task 2: Collaborative Negotiation
*   **Description:** After a schedule is generated, the user sees a "Run" scheduled for 7 AM. The user messages the Assistant: *"I'm too tired for a run tomorrow morning, move it to the afternoon."*
*   **AI Action:** The **Scheduler Agent** identifies the task, searches for a valid afternoon slot, and updates the calendar while explaining the change in the chat bubble.
*   **Design Note:** A chat-style sidebar (Assistant) interacting directly with a visual weekly calendar grid.

### User Task 3: Locking and Re-planning
*   **Description:** The user manually moves a "Grocery" task to Friday 3 PM and clicks the "Lock" icon. They then click "Orchestrate" to fit other errands around it.
*   **AI Action:** The **Verifier** marks the Friday slot as immutable. The Scheduler re-runs its optimization algorithm for all other tasks, ensuring the grocery slot remains fixed.
*   **Design Note:** Visual "Lock" icons on calendar blocks and a prominent "Orchestrate" (Magic Wand) button.

---

## 4. Video Walkthrough Script (Draft)

1.  **[0:00-0:30] Introduction:** Show 3-column layout. "Welcome to Orchestrate..."
2.  **[0:30-1:15] Task Addition:** Demonstrate Task 1 (Natural Language input).
3.  **[1:15-2:15] Orchestration & Negotiation:** Demonstrate Task 2 (AI Assistant chat).
4.  **[2:15-3:00] Stability & Summary:** Demonstrate Task 3 (Locking & Re-scheduling).

---

## 5. Theoretical Basis

### Implementation Intentions (Gollwitzer, 1999)
Research shows that users are more likely to achieve goals if they define a "when, where, and how." Our system automates this by turning vague tasks into concrete calendar blocks.
*   *Ref:* Gollwitzer, P. M. (1999). Implementation intentions: Strong effects of simple plans. *American Psychologist*.

### Mixed-Initiative Interaction (Horvitz, 1999)
The human and AI take turns leading the process based on their respective strengths. AI handles constraint satisfaction; the human handles preferences.
*   *Ref:* Horvitz, E. (1999). Principles of mixed-initiative user interfaces. *CHI Conference*.

### Cognitive Load Theory (Sweller, 1988)
By automating the "puzzle-solving" aspect of scheduling, we reduce the Extraneous Cognitive Load on the user.
*   *Ref:* Sweller, J. (1988). Cognitive load during problem solving. *Cognitive Science*.

---

## 6. Intelligence Design Approach

Our system utilizes a **3-Stage Agentic Pipeline** powered by Google Gemini Models.

### Component A: The Interpreter (Semantic Extraction)
*   **Logic:** Uses `gemini-2.5-flash-lite` with a strict JSON schema to transform messy user input into structured `Task` objects.
*   **Strategy:** Inferring missing metadata using few-shot prompting logic.

### Component B: The Scheduler (The "Brain")
*   **Logic:** A reasoning agent using `gemini-2.5-flash-lite` that receives the current state and floating tasks.
*   **Optimization:** Respects **"Vibe" Preferences** as soft constraints to maximize user satisfaction.

### Component C: The Hybrid Verifier (The "Critic")
*   **Algorithmic Layer (Python):** Direct mathematical check for overlaps and valid time ranges.
*   **Safety Loop:** Any failures trigger an immediate feedback loop to the Scheduler for correction before user display.
