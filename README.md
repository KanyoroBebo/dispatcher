# Smart City Emergency Dispatch System

An AI-powered smart city emergency dispatch simulator built with Python.  
It models fire, medical, and police dispatchers as coroutines that handle real-time events, prioritize emergencies, and dynamically allocate resources using predictive trends.

## Features

- **Coroutines for Dispatching:** Each dispatcher (fire, medical, police) runs as a coroutine managing its own queue.
- **AI-Based Prioritization:** Events get priority scores based on type, severity, time, weather, and location.
- **Scheduling:** A scheduler coroutine picks the highest-priority event from all queues per time step.
- **Predictive Resource Allocation:** Uses recent trends to forecast demand and adjust available units dynamically.
- **Logging:** Tracks which dispatcher handled which event, priority, and time step.

## How It Works

1. **Event Generation:** Random emergencies are generated each step with dynamic attributes.
2. **Prioritization:** Each event is scored to determine urgency.
3. **Scheduling:** The scheduler picks and dispatches the top event per step.
4. **Dispatchers:** Dispatchers process events if units are available, with cooldowns to simulate real-world constraints.
5. **Prediction:** Every few steps, recent trends adjust how resources are distributed across services.

## Running the Simulation

Clone this repo and run:

```bash
python dispatcher.py
