import pytest

from ..conversation_engine import ConversationEngine
from ..dialogue_manager import DialogueManager, DialogueState
from ..context_tracker import ContextTracker
from ..memory_linker import MemoryLinker


@pytest.mark.asyncio
async def test_conversation_engine_initialize_stop():
    engine = ConversationEngine()
    assert engine.state.running is False
    await engine.initialize()
    assert engine.state.running is True
    await engine.stop()
    assert engine.state.running is False


@pytest.mark.asyncio
async def test_conversation_engine_start_end_conversation():
    engine = ConversationEngine()
    await engine.initialize()
    conv_id = await engine.start_conversation()
    assert conv_id is not None
    assert engine.metrics.total_conversations_started == 1
    result = await engine.end_conversation(conv_id)
    assert result is True
    assert engine.metrics.total_conversations_ended == 1


@pytest.mark.asyncio
async def test_conversation_engine_process_message():
    engine = ConversationEngine()
    await engine.initialize()
    response = await engine.process_message("Hello there")
    assert response["dialogue_state"] == "greeting"
    assert response["next_action"] == "greet_user"
    assert "conversation_id" in response
    assert response["context"] is not None


@pytest.mark.asyncio
async def test_conversation_engine_get_history():
    engine = ConversationEngine()
    await engine.initialize()
    conv_id = await engine.start_conversation()
    await engine.process_message("What is AI?", conv_id)
    history = await engine.get_history(conv_id)
    assert len(history) == 1
    assert history[0]["content"] == "What is AI?"


@pytest.mark.asyncio
async def test_engine_not_running_raises():
    engine = ConversationEngine()
    with pytest.raises(RuntimeError, match="not running"):
        await engine.process_message("test")


def test_dialogue_manager_decide_response_type():
    dm = DialogueManager()
    assert dm.decide_response_type("hello") == DialogueState.GREETING
    assert dm.decide_response_type("what is this?") == DialogueState.QUESTION
    assert dm.decide_response_type("run the test") == DialogueState.COMMAND
    assert dm.decide_response_type("I'm confused") == DialogueState.CLARIFICATION
    assert dm.decide_response_type("bye") == DialogueState.FAREWELL
    assert dm.decide_response_type("just a normal statement") == DialogueState.RESPONSE


def test_dialogue_manager_manage_dialogue():
    dm = DialogueManager()
    result = dm.manage_dialogue("hi")
    assert result["state"] == DialogueState.GREETING
    assert result["next_action"] == "greet_user"
    assert result["response_type"] == "greeting"


def test_dialogue_manager_detect_end():
    dm = DialogueManager()
    assert dm.detect_dialogue_end("goodbye") is True
    assert dm.detect_dialogue_end("hello") is False


def test_context_tracker_update_and_get():
    ct = ContextTracker()
    ct.update_context("conv1", "Hello, my name is Alice")
    ctx = ct.get_context("conv1")
    assert ctx is not None
    assert ctx.turn_count == 1
    assert "Alice" in ctx.entities


def test_context_tracker_topics_and_summary():
    ct = ContextTracker()
    ct.update_context("conv1", "Tell me about Python programming")
    assert ct.get_current_topic("conv1") is not None
    assert ct.detect_topic_change("conv1", "What about Java?") is True
    summary = ct.get_context_summary("conv1")
    assert summary["turn_count"] == 1
    assert summary["conversation_id"] == "conv1"


def test_memory_linker_store_retrieve():
    ml = MemoryLinker()
    ml.store_memory("mem1", "The capital of France is Paris", {"type": "fact"})
    results = ml.retrieve_memory("Paris")
    assert len(results) >= 1
    assert results[0]["key"] == "mem1"


def test_memory_linker_link_and_search():
    ml = MemoryLinker()
    ml.store_memory("mem1", "Python is a programming language")
    ml.store_memory("mem2", "Python has many libraries")
    linked = ml.link_memories("mem1", "mem2")
    assert linked is True
    assert ml.link_memories("nonexistent", "mem2") is False


def test_memory_linker_forget():
    ml = MemoryLinker()
    ml.store_memory("mem1", "something")
    assert ml.forget_memory("mem1") is True
    assert ml.forget_memory("nonexistent") is False


@pytest.mark.asyncio
async def test_full_conversation_flow():
    engine = ConversationEngine()
    await engine.initialize()
    conv_id = await engine.start_conversation()
    r1 = await engine.process_message("Hi", conv_id)
    assert r1["dialogue_state"] == "greeting"
    r2 = await engine.process_message("What can you do?", conv_id)
    assert r2["dialogue_state"] == "question"
    history = await engine.get_history(conv_id)
    assert len(history) == 2
    assert await engine.end_conversation(conv_id) is True