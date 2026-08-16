"""
MODULE: Stores and retrieves the running chat history for a session.
DEPENDS ON: None
"""

class ConversationMemory:
    def __init__(self, max_history: int = 5):
        """
        Initializes the conversation memory with a maximum history length.

        Logic:
            - Sets the maximum history capacity limit.
            - Initializes an empty list to store history exchanges.

        Args:
            max_history: maximum number of Q&A exchanges to remember

        Returns:
            None
        """
        self.max_history = max_history
        self.history = []

    def add_exchange(self, question: str, answer: str) -> None:
        """
        Adds a new question-answer pair to history and caps the length.

        Logic:
            - Appends the new exchange dictionary to the history list.
            - Truncates the list from the left if it exceeds the maximum history length.

        Args:
            question: the user's question string
            answer: the generated answer string

        Returns:
            None
        """
        self.history.append({"question": question, "answer": answer})
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]

    def get_history(self) -> list:
        """
        Returns the current history.

        Logic:
            - Returns the internal list representing chat history.

        Args:
            None

        Returns:
            A list of dictionaries representing the Q&A pairs
        """
        return self.history

    def format_history_for_rewrite(self) -> str:
        """
        Formats history into a single string for the rewrite prompt.

        Logic:
            - Checks if history is empty and returns an empty string if so.
            - Iterates over stored exchanges to build a sequential Q&A string representation.

        Args:
            None

        Returns:
            A formatted string of the conversation history
        """
        if not self.history:
            return ""
        
        lines = []
        for i, exchange in enumerate(self.history, 1):
            lines.append(f"Q{i}: {exchange['question']}")
            lines.append(f"A{i}: {exchange['answer']}")
        return "\n".join(lines)
