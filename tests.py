import unittest
import heapq
from dispatcher import Event, prioritize_event, dispatcher, scheduler, predict_trends,simulate_system

class TestDispatcher(unittest.TestCase):

    def test_event_priority_comparison(self):
        e1 = Event("fire", 8, 5, "night", "storm", 0)
        e2 = Event("medical", 3, 2, "morning", "clear", 0)
        e1.priority = prioritize_event(e1)
        e2.priority = prioritize_event(e2)
        self.assertGreater(e1.priority, e2.priority, "Fire event should have higher priority due to severity and conditions")

    def test_prioritize_event(self):
        e = Event("medical", 5, 3, "night", "rain", 0)
        score = prioritize_event(e)
        expected_score = 60 + 5*10 + 10 + 5 - abs(3 - 5)  # 60 + 50 + 10 + 5 - 2 = 123
        self.assertEqual(score, expected_score, f"Expected score {expected_score}, got {score}")

    def test_dispatcher_with_cooldowns(self):
            # Setup
            log = []
            queue = []
            unit_pool = {'fire': 1}
            cooldowns = {'fire': []}
            
            # Create a high-priority event
            e = Event('fire', location=5, severity=5, time_of_day='night', weather='storm', timestamp=0)
            e.priority = prioritize_event(e)
            heapq.heappush(queue, e)

            d = dispatcher('fire', queue, log, unit_pool, cooldowns)

            # Dispatch event
            next(d)
            self.assertEqual(len(log), 1)
            self.assertEqual(unit_pool['fire'], 0)
            self.assertEqual(len(cooldowns['fire']), 1)

            # Simulate cooldown decrement
            for _ in range(2):
                next(d)
                self.assertEqual(unit_pool['fire'], 0)
            next(d)  # final tick
            self.assertEqual(unit_pool['fire'], 1)  # unit returned

            self.assertEqual(len(log), 1)  # No additional events handled

    def test_scheduler(self):
        q1, q2, q3 = [], [], []
        log = []

        e1 = Event("fire", 5, 2, "night", "storm", 0)
        e2 = Event("medical", 5, 5, "night", "storm", 0)
        e1.priority = prioritize_event(e1)
        e2.priority = prioritize_event(e2)

        heapq.heappush(q1, e1)
        heapq.heappush(q2, e2)

        queues = {"fire": q1, "medical": q2, "police": q3}
        schedule = scheduler({}, queues, log)
        next(schedule)

        self.assertEqual(len(log), 1, "One event should be logged")
        self.assertIn(log[0][0], ["fire", "medical"], "Invalid dispatcher logged")

    def test_predict_trends(self):
        events = [
            Event("fire", 5, 3, "morning", "clear", 0),
            Event("medical", 3, 2, "night", "rain", 1),
            Event("fire", 6, 4, "afternoon", "storm", 2),
            Event("police", 2, 3, "night", "clear", 3),
            Event("fire", 5, 1, "night", "storm", 4)
        ]
        result = predict_trends(events)
        self.assertEqual(result["fire"], 3, "Fire should have 3 events")
        self.assertEqual(result["medical"], 1)
        self.assertEqual(result["police"], 1)

    def test_simulate_system(self):
        logs = simulate_system(5)
        self.assertIsInstance(logs, list, "Simulation should return a list")
        self.assertGreater(len(logs), 0, "Simulation should log events")
        self.assertTrue(all(len(entry) == 4 for entry in logs), "Each log entry should have 4 fields")
if __name__ == "__main__":
    unittest.main()
    