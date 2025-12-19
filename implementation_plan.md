# AI Planner & Scheduler - Comprehensive Work Plan

## Goal Description
Transform the current prototype into a fully "Intelligent Time Orchestration" system as per the project proposal. This involves implementing the missing "Verifier" and "Negotiation" agents, adding "Task Locking" capabilities, and polishing the UI to a premium "demo-ready" state.

## User Review Required
> [!IMPORTANT]
> **Gemini API Usage**: The new "Verifier" and "Negotiation" features will increase API call volume. Ensure your quota is sufficient.

## Proposed Changes

### Phase 1: Core "Intelligence" (Backend)
Focus on the "Stateful Agentic System" promise.

#### [NEW] [verifier.py](file:///c:/Users/dnh5w/AGProjects/AI_planner_and_scheduler/backend/verifier.py)
Implement the "Critic" layer.
- **Algorithmic Check**: Python function to detect time overlaps or out-of-bounds scheduling.
- **LLM Check**: Prompt Gemini to review the schedule for "human realism" (e.g., "Gym at 2 AM?").

#### [MODIFY] [scheduler.py](file:///c:/Users/dnh5w/AGProjects/AI_planner_and_scheduler/backend/scheduler.py)
- Integrate `verifier.py`. logic: Loop `Generate -> Verify -> Regenerate` if issues found.
- Add support for **Fixed Anchors**: Pass "Locked" tasks as immutable constraints to the LLM prompt.

#### [MODIFY] [main.py](file:///c:/Users/dnh5w/AGProjects/AI_planner_and_scheduler/backend/main.py)
- Update data models to include `is_locked` boolean.
- Update endpoints to handle new logic.

### Phase 2: Interactive Negotiation (Backend & Frontend)
Enable the user to "talk to their plan".

#### [NEW] [negotiator.py](file:///c:/Users/dnh5w/AGProjects/AI_planner_and_scheduler/backend/negotiator.py)
- Implement a chat agent that has the current schedule context.
- tools/functions needed: `move_task(id, new_time)`, `lock_task(id)`, `explain_decision(id)`.

#### [MODIFY] [NegotiationChat.jsx](file:///c:/Users/dnh5w/AGProjects/AI_planner_and_scheduler/frontend/src/components/NegotiationChat.jsx) (and App.jsx)
- Connect the dummy chat UI to the real `/api/chat/negotiate` endpoint.
- Display "Thinking..." states or reasoning from the agent.

### Phase 3: UI/UX Polish (Frontend)
Make it look "Premium" and "Dynamic".

#### [MODIFY] [CalendarView.jsx](file:///c:/Users/dnh5w/AGProjects/AI_planner_and_scheduler/frontend/src/components/CalendarView.jsx)
- Enhance visual blocks (colors based on tags, rounded corners, subtle shadows).
- Add "Lock" icon/button on task blocks.

#### [MODIFY] [App.css](file:///c:/Users/dnh5w/AGProjects/AI_planner_and_scheduler/frontend/src/App.css)
- Implement Glassmorphism (already partially there, refine it).
- Add Animations: Task appearance, Schedule re-shuffling (using `framer-motion` or CSS transitions).

#### [MODIFY] [TaskBank.jsx](file:///c:/Users/dnh5w/AGProjects/AI_planner_and_scheduler/frontend/src/components/TaskBank.jsx)
- Improve "Empty State" visuals.
- interactions: Hover effects on delete/orchestrate buttons.

### Phase 4: Fine-tuning & Verification
#### [MODIFY] [Backend Tests]
- Create `tests/test_verifier.py` to ensure overlap detection works.
- Create `tests/test_locking.py` to ensure locked tasks don't move.

## Verification Plan

### Automated Tests
1.  **Verifier Logic**: Run a script creating a schedule with overlaps and asserting the Verifier catches it.
    ```bash
    python -m backend.tests.test_verifier
    ```
2.  **Locking Logic**:
    -   Script: Create a schedule, lock Task A, run Re-orchestrate.
    -   Assert: Task A `start_time` remains unchanged.

### Manual Verification
1.  **Negotiation Flow**:
    -   User types: "Move the Gym to 5 PM".
    -   Verify: Chat replies confirmation, Calendar updates instantly.
2.  **Visual Check**:
    -   Click "Lock" on a task.
    -   Click "Orchestrate".
    -   Verify the locked task stays visualy stuck while others move.
