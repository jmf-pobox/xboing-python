import threading

from utils.event_bus import EventBus


class SampleEvent:
    def __init__(self, value):
        self.value = value

class AnotherSampleEvent:
    def __init__(self, msg):
        self.msg = msg

def test_subscribe_and_fire():
    bus = EventBus()
    results = []
    def handler(event):
        results.append(event.value)
    bus.subscribe(SampleEvent, handler)
    bus.fire(SampleEvent(42))
    assert results == [42]

def test_unsubscribe():
    bus = EventBus()
    results = []
    def handler(event):
        results.append(event.value)
    bus.subscribe(SampleEvent, handler)
    bus.unsubscribe(SampleEvent, handler)
    bus.fire(SampleEvent(99))
    assert results == []

def test_multiple_handlers():
    bus = EventBus()
    results = []
    def handler1(event):
        results.append(('h1', event.value))
    def handler2(event):
        results.append(('h2', event.value))
    bus.subscribe(SampleEvent, handler1)
    bus.subscribe(SampleEvent, handler2)
    bus.fire(SampleEvent(7))
    assert ('h1', 7) in results and ('h2', 7) in results

def test_different_event_types():
    bus = EventBus()
    results = []
    def handler1(event):
        results.append(('test', event.value))
    def handler2(event):
        results.append(('another', event.msg))
    bus.subscribe(SampleEvent, handler1)
    bus.subscribe(AnotherSampleEvent, handler2)
    bus.fire(SampleEvent(1))
    bus.fire(AnotherSampleEvent('hi'))
    assert ('test', 1) in results
    assert ('another', 'hi') in results

def test_thread_safety():
    bus = EventBus()
    results = []
    def handler(event):
        results.append(event.value)
    bus.subscribe(SampleEvent, handler)
    def fire_events():
        for i in range(100):
            bus.fire(SampleEvent(i))
    threads = [threading.Thread(target=fire_events) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    # Should have 500 results (5 threads x 100 events)
    assert len(results) == 500 