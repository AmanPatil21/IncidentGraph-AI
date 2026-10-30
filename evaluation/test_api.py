
import uuid

import pytest
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


def new_session():
    return str(uuid.uuid4())


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_empty_question_rejected():
    response = client.post(
        "/ask",
        json={"question": "", "session_id": new_session()}
    )

    assert response.status_code == 422


def test_ask_response_structure():
    session_id = new_session()
    question = "What caused INC-001?"

    response = client.post(
        "/ask",
        json={"question": question, "session_id": session_id}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == question
    assert data["session_id"] == session_id
    assert isinstance(data["answer"], str)
    assert len(data["answer"].strip()) > 0
    assert isinstance(data["source"], list)
    assert isinstance(data["search_question"], str)


def test_incident_specific_retrieval():
    response = client.post(
        "/ask",
        json={
            "question": "What caused INC-001?",
            "session_id": new_session()
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data["source"]) > 0
    assert any(
        "INC-001" in source or "PM-001" in source
        for source in data["source"]
    )


def test_conversational_followup():
    session_id = new_session()

    first = client.post(
        "/ask",
        json={
            "question": "What caused INC-001?",
            "session_id": session_id
        }
    )

    assert first.status_code == 200

    followup = client.post(
        "/ask",
        json={
            "question": "How can we prevent it?",
            "session_id": session_id
        }
    )

    assert followup.status_code == 200

    data = followup.json()

    assert data["question"] == "How can we prevent it?"
    assert data["session_id"] == session_id
    assert "INC-001" in data["search_question"]


def test_unknown_incident():
    response = client.post(
        "/ask",
        json={
            "question": "What caused INC-999?",
            "session_id": new_session()
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["answer"] == (
        "I couldn't find sufficient evidence to answer this question."
    )
    assert data["source"] == []


