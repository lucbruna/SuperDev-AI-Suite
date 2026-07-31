"""Tests for the knowledge summarization subsystem."""

from __future__ import annotations

import pytest

from knowledge.summarization import (
    ExtractiveSummarizer,
    Sentence,
    SentenceRanker,
    SummarizationEngine,
    SummaryBuilder,
)


class TestSentence:
    def test_to_dict(self) -> None:
        sentence = Sentence(text="texto", score=0.8, position=2)
        assert sentence.to_dict() == {"text": "texto", "score": 0.8, "position": 2}


class TestExtractiveSummarizer:
    def test_split_sentences(self) -> None:
        summarizer = ExtractiveSummarizer()
        sentences = summarizer.split_sentences("Primeira frase. Segunda frase! Terceira?")
        assert len(sentences) == 3
        assert sentences[0] == "Primeira frase."

    def test_summarize_limits(self) -> None:
        summarizer = ExtractiveSummarizer(max_sentences=2, max_chars=500)
        ranked = [
            Sentence(text="segunda mais relevante", score=0.5, position=1),
            Sentence(text="a mais relevante", score=0.9, position=0),
            Sentence(text="pouco relevante", score=0.1, position=2),
        ]
        selected = summarizer.summarize(ranked)
        assert len(selected) == 2
        assert selected[0].text == "a mais relevante"


class TestSentenceRanker:
    def test_rank_orders_by_salience(self) -> None:
        ranker = SentenceRanker()
        ranked = ranker.rank(["O deploy usa python.", "O deploy acontece toda semana."])
        assert len(ranked) == 2
        assert ranked[0].score >= ranked[1].score
        assert all(isinstance(sentence.position, int) for sentence in ranked)

    def test_rank_empty(self) -> None:
        ranker = SentenceRanker()
        assert ranker.rank([]) == []


class TestSummaryBuilder:
    def test_build(self) -> None:
        builder = SummaryBuilder()
        text = (
            "O sistema faz deploy automatico. "
            "O deploy usa python e docker. "
            "Monitoramento acompanha a saudabilidade. "
            "Equipe revisa os logs diariamente."
        )
        result = builder.build(text)
        assert result["summary"]
        assert result["total_sentences"] == 4
        assert len(result["sentences"]) >= 1
        assert result["compression"] >= 0.0


class TestSummarizationEngine:
    def test_summarize(self) -> None:
        engine = SummarizationEngine()
        text = (
            "A primeira frase fala sobre busca. "
            "A segunda frase fala sobre busca vetorial. "
            "A terceira frase detalha o ranking dos resultados."
        )
        result = engine.summarize(text)
        assert result["summary"]
        assert result["total_sentences"] == 3
        assert engine.stats()["summary_max_sentences"] >= 1
