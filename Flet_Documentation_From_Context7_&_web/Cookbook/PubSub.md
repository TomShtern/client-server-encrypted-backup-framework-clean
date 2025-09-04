# PubSub

Flet provides a built-in PubSub mechanism for asynchronous communication between page sessions, which is particularly useful for applications like chat apps where messages need to be broadcasted to all active sessions.

Key features of Flet's PubSub include:
*   **Broadcasting messages**: Messages can be sent to all app sessions.
*   **Topic-based messaging**: Messages can be sent to specific "topic" or "channel" subscribers.
*   **Subscription management**: You can subscribe to broadcast messages or topics on app session start, and unsubscribe when no longer needed (e.g., on page close).

A typical usage involves subscribing to messages, sending messages on events (like a "Send" button click), and unsubscribing when a session ends. The documentation provides a simple chat application example demonstrating these concepts.
