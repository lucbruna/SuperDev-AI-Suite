"""Streaming engine."""

from datetime import datetime

from .models import StreamConsumer, StreamEvent, StreamPipeline, StreamStatus, StreamTopic


class StreamingEngine:
    def __init__(self):
        self._topics: dict[str, StreamTopic] = {}
        self._events: dict[str, list[StreamEvent]] = {}
        self._consumers: dict[str, StreamConsumer] = {}
        self._pipelines: dict[str, StreamPipeline] = {}

    def create_topic(self, topic: StreamTopic) -> StreamTopic:
        self._topics[topic.topic_id] = topic
        self._events[topic.topic_id] = []
        return topic

    def get_topic(self, topic_id: str) -> StreamTopic | None:
        return self._topics.get(topic_id)

    def produce_event(self, event: StreamEvent) -> StreamEvent:
        if event.topic_id not in self._events:
            self._events[event.topic_id] = []
        event.sequence = len(self._events[event.topic_id])
        self._events[event.topic_id].append(event)
        topic = self._topics.get(event.topic_id)
        if topic:
            topic.message_count += 1
        return event

    def consume_events(self, topic_id: str, consumer_id: str, max_count: int = 10) -> list[StreamEvent]:
        consumer = self._consumers.get(consumer_id)
        events = self._events.get(topic_id, [])
        if consumer:
            remaining = events[consumer.offset :]
            batch = remaining[:max_count]
            consumer.offset += len(batch)
            consumer.last_commit = datetime.now()
            return batch
        return events[:max_count]

    def create_consumer(self, consumer: StreamConsumer) -> StreamConsumer:
        self._consumers[consumer.consumer_id] = consumer
        return consumer

    def get_consumer(self, consumer_id: str) -> StreamConsumer | None:
        return self._consumers.get(consumer_id)

    def create_pipeline(self, pipeline: StreamPipeline) -> StreamPipeline:
        self._pipelines[pipeline.pipeline_id] = pipeline
        return pipeline

    def get_pipeline(self, pipeline_id: str) -> StreamPipeline | None:
        return self._pipelines.get(pipeline_id)

    def start_pipeline(self, pipeline_id: str) -> bool:
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return False
        pipeline.status = StreamStatus.STREAMING
        return True

    def get_events(self, topic_id: str, limit: int = 100) -> list[StreamEvent]:
        return self._events.get(topic_id, [])[:limit]

    def get_stats(self) -> dict:
        topics = list(self._topics.values())
        return {
            "topics": len(topics),
            "total_messages": sum(t.message_count for t in topics),
            "consumers": len(self._consumers),
            "pipelines": len(self._pipelines),
        }
