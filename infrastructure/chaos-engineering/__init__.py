"""Chaos engineering experiment definitions."""
import random
import time
import logging

logger = logging.getLogger(__name__)


class ChaosExperiment:
    def __init__(self, name: str, probability: float = 0.1):
        self.name = name
        self.probability = probability

    def should_run(self) -> bool:
        return random.random() < self.probability

    def execute(self):
        raise NotImplementedError


class KillRandomPod(ChaosExperiment):
    def __init__(self):
        super().__init__("kill-random-pod", probability=0.05)

    def execute(self):
        logger.warning("CHAOS: Simulating pod kill")
        time.sleep(0.5)


class InjectNetworkLatency(ChaosExperiment):
    def __init__(self):
        super().__init__("inject-latency", probability=0.05)

    def execute(self):
        latency = random.uniform(0.1, 2.0)
        logger.warning(f"CHAOS: Injecting {latency:.2f}s latency")
        time.sleep(latency)


EXPERIMENTS = [KillRandomPod(), InjectNetworkLatency()]


def run_chaos():
    for exp in EXPERIMENTS:
        if exp.should_run():
            try:
                exp.execute()
            except Exception as e:
                logger.error(f"CHAOS experiment {exp.name} failed: {e}")