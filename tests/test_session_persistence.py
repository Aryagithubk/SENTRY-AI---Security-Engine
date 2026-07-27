from backend.services.db_service import DatabaseService
from backend.workflows.graph import SecureOpsGraph


def test_session_and_conversation_persist_in_sqlite():
    user = {"username": "persistence_test", "role": "L1", "email": "persistence@example.com"}
    session_id = DatabaseService.create_app_session(user)
    try:
        DatabaseService.append_conversation_message(session_id, {"role": "user", "content": "Show alerts"})
        DatabaseService.append_conversation_message(session_id, {"role": "assistant", "content": "Alert response", "trace": []})

        assert DatabaseService.get_app_session(session_id) == user
        assert [message["content"] for message in DatabaseService.get_conversation_messages(session_id)] == ["Show alerts", "Alert response"]
    finally:
        DatabaseService.delete_app_session(session_id)


def test_follow_up_query_inherits_recent_entity_context():
    graph = SecureOpsGraph(provider="mock")
    history = [{"role": "user", "content": "Check login history for johndoe@securetech.com"}]

    response = graph.process_query("Show activity for that user", conversation_history=history)

    assert response["target_agent"] == "Identity Agent"
