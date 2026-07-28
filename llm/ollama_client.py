from typing import Optional, Dict, Any

import ollama


class OllamaClient:
    """
    Ollama LLM Client

    Responsibilities:
    - communicate with Ollama
    - manage generation parameters
    - provide unified LLM interface

    Example:

        client = OllamaClient(
            model="qwen2.5:14b"
        )

        result = client.chat(
            "写一个小说开头"
        )
    """

    def __init__(
        self,
        model: str = "qwen2.5:14b",
        num_ctx: int = 32768,
        temperature: float = 0.75,
        max_tokens: int = 6000,
        top_p: float = 0.9,
        top_k: int = 40,
        repeat_penalty: float = 1.1,
    ):

        self.model = model

        self.num_ctx = num_ctx

        self.default_options = {
            "temperature": temperature,
            "num_predict": max_tokens,
            "num_ctx": num_ctx,
            "top_p": top_p,
            "top_k": top_k,
            "repeat_penalty": repeat_penalty,
        }

    # ==================================================
    # Public API
    # ==================================================

    def chat(
        self,
        prompt: str,
        system: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Send prompt to Ollama

        Args:
            prompt:
                user prompt

            system:
                system instruction

            options:
                override generation parameters


        Returns:
            generated text
        """

        messages = []

        # system message
        if system:

            messages.append({"role": "system", "content": system})

        # user message
        messages.append({"role": "user", "content": prompt})

        # merge options

        generation_options = self.default_options.copy()

        if options:

            generation_options.update(options)

        response = ollama.chat(
            model=self.model,
            messages=messages,
            options=generation_options,
        )

        return response["message"]["content"]

    # ==================================================
    # Advanced API
    # ==================================================

    def chat_messages(
        self,
        messages: list,
        options: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Direct messages mode

        Useful for:
        - multi-turn conversation
        - memory system
        - agent chain
        """

        generation_options = self.default_options.copy()

        if options:

            generation_options.update(options)

        response = ollama.chat(
            model=self.model,
            messages=messages,
            options=generation_options,
        )

        return response["message"]["content"]

    # ==================================================
    # Health Check
    # ==================================================

    def test_connection(self) -> bool:
        """
        Test Ollama availability
        """

        try:

            ollama.list()

            return True

        except Exception:

            return False
