from dataclasses import dataclass
import heapq
from typing import Dict, List
from collections import defaultdict, deque
import asyncio
import random
import time

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
            log.append((name, event.type, event.priority, event.timestamp))
            print(f"{name.upper()} Handling {event.type} (priority {event.priority}) at time {event.timestamp}")
            unit_pool[name] -= 1  # Mark unit as busy
            cooldowns[name].append(3)  # Unit remains busy for 3 time steps
        yield

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
            log.append((best_dispatcher, best_event.type, best_event.priority, current_time))
            print(f"Scheduler says {best_dispatcher} processes {best_event.type} (priority {best_event.priority}) at time {current_time}")
        else:
            print(f"Scheduler says no events to process at time {current_time}")

        current_time += 1
        yield

def predict_trends(recent_events: List[Event]) -> Dict[str, int]:
    trend = defaultdict(int)
    for event in recent_events:
        trend[event.type] += 1
    return trend

def propose_resource_allocation(trend: Dict[str, int], total_units: int) -> Dict[str, int]:
    total_events = sum(trend.values()) or 1  # Avoid division by zero
    proposal = {}

    for service in ['fire', 'medical', 'police']:
        # Allocate proportionally, but ensure at least 1 unit
        proposed_units = max(1, (trend.get(service, 0) * total_units) // total_events)
        proposal[service] = proposed_units

    print(f"AI Proposal: Based on recent trends: {dict(trend)}")
    print(f"AI Proposal: Suggested unit allocation: {proposal}")
    return proposal

# event_log = []  can be used for future extensions like saving event history to a file

def simulate_system(steps=10):
    queues = {
        'fire': [],
        'medical': [],
        'police': []
    }

    log = []
    recent_events = []

    unit_pool = {'fire': 3, 'medical': 3, 'police': 3}  # Total dispatchable units
    cooldowns = {'fire': [], 'medical': [], 'police': []}  # Cooldown timers for busy units

    fire_dispatcher = dispatcher('fire', queues['fire'], log, unit_pool, cooldowns)
    medical_dispatcher = dispatcher('medical', queues['medical'], log, unit_pool, cooldowns)
    police_dispatcher = dispatcher('police', queues['police'], log, unit_pool, cooldowns)
    dispatchers = {
        'fire': fire_dispatcher,
        'medical': medical_dispatcher,
        'police': police_dispatcher
    }

    sched = scheduler(dispatchers, queues, log)

    for t in range(steps):
        # Randomly generate events
        if random.random() < 0.7:
            e_type = random.choice(['fire', 'medical', 'police'])
            e = Event(
                type=e_type,
                location=random.randint(1, 10),
                severity=random.randint(1, 5),
                time_of_day=random.choice(['morning', 'afternoon', 'night']),
                weather=random.choice(['clear', 'rain', 'storm']),
                timestamp=t
            )
            e.priority = prioritize_event(e)
            heapq.heappush(queues[e.type], e)
            recent_events.append(e)

        # Predict trends every 5 steps
        if t % 10 == 0 and recent_events:
            trend = predict_trends(recent_events[-10:])
            print(f"AI Analysis: Recent event trend: {dict(trend)}")

            # Forecast the busiest dispatcher
            busiest = max(trend.items(), key=lambda x: x[1])[0]
            print(f"AI Forecast: {busiest.upper()} dispatcher likely to be busiest in next 10 steps")

            # Propose and apply resource allocation
            total_units = 9
            proposal = propose_resource_allocation(trend, total_units)
            unit_pool.update(proposal)


        next(sched)
        for d in dispatchers.values():
            next(d)

    return log

logs = simulate_system(20)