from dataclasses import dataclass
import heapq
from typing import Dict, List
from collections import defaultdict, namedtuple
import random

# === Configuration ===
total_units = 9  # Total dispatchable units across all services
cooldown_duration = 3  # Time steps a unit remains busy
event_probability = 0.7  # Chance of generating a new event each step
enable_logging = True  # Toggle for printing logs
services = ['fire', 'medical', 'police']
time_of_day_options = ['morning', 'afternoon', 'night']
weather_types = ['clear', 'rain', 'storm']

# === Data Structures ===
@dataclass
class Event:
    type: str               # 'fire', 'medical', 'police'
    severity: int           # 1-10
    location: int           # 0-10, 5 is centre
    time_of_day: str        # 'morning', 'afternoon', 'night'
    weather: str            # 'clear', 'rain', 'storm'
    timestamp: float
    priority: float = 0.0

    def __lt__(self, other):
        return self.priority > other.priority  # changes heapq to use max-heap for priority

log_entry = namedtuple("log_entry", ["dispatcher", "event_type", "priority", "timestamp"])

# === AI Prioritization ===
def prioritize_event(event: Event) -> int:
    base_score = {
        'fire': 70,
        'medical': 60,
        'police': 50
    }.get(event.type, 40)

    score = base_score
    score += event.severity * 10
    score += 10 if event.time_of_day == 'night' else 0
    score += 5 if event.weather in ['storm', 'rain'] else 0
    score -= abs(event.location - 5)  # closer to city center

    return score

# === Dispatcher Coroutine ===
def dispatcher(name, queue, log, unit_pool, cooldowns):
    while True:
        # Update cooldowns and return units
        new_cooldowns = []
        for time_left in cooldowns[name]:
            if time_left > 1:
                new_cooldowns.append(time_left - 1)
            else:
                unit_pool[name] += 1  # Unit becomes available again
        cooldowns[name] = new_cooldowns

        # Dispatch event only if units are available
        if queue and unit_pool[name] > 0:
            event = heapq.heappop(queue)
            log.append(log_entry(name, event.type, event.priority, event.timestamp))
            if enable_logging:
                print(f"{name.upper()} Handling {event.type} (priority {event.priority}) at time {event.timestamp}")
            unit_pool[name] -= 1  # Mark unit as busy
            cooldowns[name].append(cooldown_duration)  # Unit remains busy for 3 time steps
        yield

# === Scheduler Coroutine ===
def scheduler(dispatchers, queues, log):
    current_time = 0
    while True:
        best_event = None
        best_queue = None
        best_dispatcher = None

        for name, queue in queues.items():
            if queue:
                candidate = queue[0]
                if best_event is None or candidate.priority > best_event.priority:
                    best_event = candidate
                    best_queue = queue
                    best_dispatcher = name

        if best_event:
            heapq.heappop(best_queue)
            log.append(log_entry(best_dispatcher, best_event.type, best_event.priority, current_time))
            if enable_logging:
                print(f"Scheduler says {best_dispatcher} processes {best_event.type} (priority {best_event.priority}) at time {current_time}")
        else:
            if enable_logging:
                print(f"Scheduler says no events to process at time {current_time}")

        current_time += 1
        yield

# === AI Trend Prediction ===
def predict_trends(recent_events: List[Event]) -> Dict[str, int]:
    trend = defaultdict(int)
    for event in recent_events:
        trend[event.type] += 1
    return trend

def propose_resource_allocation(trend: Dict[str, int], total: int) -> Dict[str, int]:
    total_events = sum(trend.values()) or 1  # Avoid division by zero
    proposal = {}

    for service in services:
        # Allocate proportionally, but ensure at least 1 unit
        proposed_units = max(1, (trend.get(service, 0) * total) // total_events)
        proposal[service] = proposed_units

    if enable_logging:
        print(f"AI Proposal: Based on recent trends: {dict(trend)}")
        print(f"AI Proposal: Suggested unit allocation: {proposal}")
    return proposal

# event_log = []  can be used for future extensions like saving event history to a file

# === Simulation Loop ===
def simulate_system(steps=10):
    queues = {service: [] for service in services}
    log = []
    recent_events = []
    unit_pool = {service: 3 for service in services}  # Total dispatchable units
    cooldowns = {service: [] for service in services}  # Cooldown timers for busy units

    dispatchers = {
        service: dispatcher(service, queues[service], log, unit_pool, cooldowns)
        for service in services
    }

    sched = scheduler(dispatchers, queues, log)

    for t in range(steps):
        # Randomly generate events
        if random.random() < event_probability:
            e_type = random.choice(services)
            event = Event(
                type=e_type,
                location=random.randint(1, 10),
                severity=random.randint(1, 5),
                time_of_day=random.choice(time_of_day_options),
                weather=random.choice(weather_types),
                timestamp=t
            )
            event.priority = prioritize_event(event)
            heapq.heappush(queues[event.type], event)
            recent_events.append(event)

        # Predict trends every 10 steps
        if t % 10 == 0 and recent_events:
            trend = predict_trends(recent_events[-10:])
            if enable_logging:
                print(f"AI Analysis: Recent event trend: {dict(trend)}")

            # Forecast the busiest dispatcher
            busiest = max(trend.items(), key=lambda x: x[1])[0]
            if enable_logging:
                print(f"AI Forecast: {busiest.upper()} dispatcher likely to be busiest in next 10 steps")

            # Propose and apply resource allocation
            proposal = propose_resource_allocation(trend, total_units)
            unit_pool.update(proposal)

        next(sched)
        for d in dispatchers.values():
            next(d)

    return log

# === Run Simulation ===
logs = simulate_system(20)