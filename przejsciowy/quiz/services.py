import os
import re
import json
import requests
import time
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

class QuestionGenerator:
    @staticmethod
    def generate(text, total_count, model_type="azure"):
        """
        Główna metoda dzieląca proces na partie (batching) 
        i fragmenty tekstu (chunking).
        """
        try:
            total_count = int(total_count)
        except (ValueError, TypeError):
            total_count = 10

        all_questions = []
        batch_size = 10
        
        num_batches = (total_count + batch_size - 1) // batch_size
        
        text_chunks = QuestionGenerator._split_text(text, num_batches)

        print(f"DEBUG: Rozpoczynam generowanie {total_count} pytań w {len(text_chunks)} partiach.")

        for i, chunk in enumerate(text_chunks):
            if i < num_batches - 1:
                current_batch_count = batch_size
            else:
                current_batch_count = total_count % batch_size or batch_size

            print(f"DEBUG: Partia {i+1}/{num_batches}: Generowanie {current_batch_count} pytań.")

            questions = QuestionGenerator._execute_call(chunk, current_batch_count, model_type)
            
            if questions:
                all_questions.extend(questions)
            
            if i < num_batches - 1:
                time.sleep(1.5)

        return all_questions

    @staticmethod
    def _split_text(text, n):
        """Dzieli tekst na N w miarę równych części, aby model widział inny kontekst."""
        if n <= 1:
            return [text[:7000]]
        
        length = len(text)
        size = length // n
        return [text[i*size : (i+1)*size] for i in range(n)]

    @staticmethod
    def _execute_call(chunk, count, model_type):
        """Pomocniczy router wywołujący odpowiednie API."""
        prompt = f"""
        ZWRÓĆ TYLKO CZYSTY JSON (TABLICA). NIE PISZ ŻADNEGO TEKSTU POZA JSONEM.
        Na podstawie WYŁĄCZNIE poniższego fragmentu tekstu wygeneruj dokładnie {count} pytań testowych po polsku.
        Każde pytanie musi mieć 4 opcje i wskazaną poprawną odpowiedź (index 0-3).

        Format JSON:
        [
          {{"question": "Treść pytania", "options": ["A", "B", "C", "D"], "correct": 0}}
        ]

        FRAGMENT TEKSTU:
        {chunk}
        """

        if model_type == "deepseek":
            return QuestionGenerator._call_ollama(prompt)
        return QuestionGenerator._call_azure_direct(prompt)

    @staticmethod
    def _call_ollama(prompt):
        try:
            response = requests.post("http://localhost:11434/api/generate", json={
                "model": "deepseek-r1:7b",
                "prompt": prompt,
                "stream": False,
                "format": "json"
            }, timeout=120)
            return QuestionGenerator._clean_and_parse(response.json().get('response', ''))
        except Exception as e:
            print(f"Błąd Ollama: {e}")
            return []

    @staticmethod
    def _call_azure_direct(prompt):
        try:
            # POPRAWIONY ENDPOINT
            client = ChatCompletionsClient(
                endpoint="https://models.inference.ai.azure.com", 
                credential=AzureKeyCredential(os.getenv("AZURE_API_KEY")),
            )

            response = client.complete(
                messages=[
                    SystemMessage(content="Jesteś ekspertem edukacyjnym. Tworzysz testy. Odpowiadasz wyłącznie JSONem."),
                    UserMessage(content=prompt),
                ],
                model="gpt-4o",
                temperature=0.8,
                max_tokens=2500
            )
            
            return QuestionGenerator._clean_and_parse(response.choices[0].message.content)
        except Exception as e:
            print(f"Błąd Azure Direct: {str(e)}")
            return []

    @staticmethod
    def _clean_and_parse(text):
        """Czyści odpowiedź z tagów myślenia i bloków markdown."""
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        
        match = re.search(r'\[\s*\{.*\}\s*\]', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return []