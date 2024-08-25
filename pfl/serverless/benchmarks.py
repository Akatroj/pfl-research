import csv
import sys
import time


class Counter:
    def __init__(self):
        self.counters = {}

    def increment(self, name):
        self.counters[name] = self.counters.get(name, 0) + 1

    def get(self, name):
        return self.counters.get(name, 0)

    def get_and_increment(self, name):
        self.increment(name)
        return self.get(name)

    def reset(self, name=None):
        if name is not None:
            self.counters[name] = 0
        else:
            self.counters = {}


class TimeCounter:
    def __init__(self):
        self._results = {}
        self._start_times = {}

    def start(self, function_name):
        if function_name in self._start_times:
            raise ValueError(f"Function {function_name} already started")
        self._start_times[function_name] = time.perf_counter()

    def stop(self, function_name):
        end_time = time.perf_counter()
        start_time = self._start_times.pop(function_name, None)
        if start_time is not None:
            execution_time = end_time - start_time
            self._results[function_name] = self._results.get(function_name, 0) + execution_time

    def reset(self):
        self._results = {}
        self._start_times = {}

    def get(self, function_name):
        return self._results.get(function_name, 0)

    def save_to_file(self, output_file="execution_times.csv"):
        with open(output_file, "w", newline="") as csvfile:
            fieldnames = ["function_name", "execution_time"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for function, duration in self._results.items():
                writer.writerow({"function_name": function, "execution_time": duration})


class SizeCounter:
    def __init__(self):
        self._results = {}

    def record_size(self, name, obj):
        size = sys.getsizeof(obj)
        self._results[name] = self._results.get(name, 0) + size

    def save_to_file(self, output_file="object_sizes.csv"):
        with open(output_file, "w", newline="") as csvfile:
            fieldnames = ["object_name", "size"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for obj, size in self._results.items():
                writer.writerow({"object_name": obj, "size": size})


PFLCounter = Counter()
PFLTimeCounter = TimeCounter()
PFLSizeCounter = SizeCounter()

SAVE_INPUT = "SAVE_INPUT"
SAVE_OUTPUT = "SAVE_OUTPUT"
GET_INPUT = "GET_INPUT"
GET_OUTPUT = "GET_OUTPUT"
RUN = "RUN"
CALL_FN = "CALL_FN"

CONTEXT_GETTER = "CONTEXT_GETTER"
CLIENT_HANDLER = "CLIENT_HANDLER"
AGGREGATOR = "AGGREGATOR"

CLIENTS = "CLIENTS"
ITERATION = "ITERATION"
