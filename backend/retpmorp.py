import random
from langchain_ollama.llms import OllamaLLM

SYSTEM_PROMPT = """You are OppositeGPT. Your task is to perform semantic inversion of the user's input.

Instructions:
1. Invert the core meaning of the input - transform it to its logical opposite while maintaining grammatical coherence.
2. Preserve the original structure and tone when possible.
3. Handle negations, antonyms, and conceptual opposites appropriately.
4. If the input is a question, provide the opposite answer or reframe it inversely.
5. Return ONLY the inverted text, no explanations or preamble.

Examples:
- "The sun is bright." → "The sun is dim."
- "I love this" → "I hate this"
- "Can you help me?" → "Can you hinder me?"
- "Cats are better than dogs." → "Dogs are better than cats."
"""

def apply_random_word_reversal(text: str, probability: float) -> str:
    """Randomly reverse characters in words based on probability."""
    words = text.split()
    result = []
    for word in words:
        if random.random() < probability:
            # Separate punctuation from word
            punctuation = ""
            clean_word = word
            while clean_word and not clean_word[-1].isalnum():
                punctuation = clean_word[-1] + punctuation
                clean_word = clean_word[:-1]
            result.append(clean_word[::-1] + punctuation)
        else:
            result.append(word)
    return " ".join(result)

def apply_random_language_swap(text: str, probability: float, languages: list) -> str:
    """Mark words for random language swap (returns markers for demonstration)."""
    if not languages or probability <= 0:
        return text
    
    words = text.split()
    result = []
    for word in words:
        if random.random() < probability:
            lang = random.choice(languages)
            result.append(f"[{lang}:{word}]")
        else:
            result.append(word)
    return " ".join(result)

def invert_text(
    prompt: str,
    random_word_reversal: float = 0.0,
    random_language_swap: float = 0.0,
    languages: list = None,
    model: str = "llama2"
) -> str:
    """
    Invert text using Ollama LLM with optional transformations.
    
    Args:
        prompt: User input text to invert
        random_word_reversal: Probability (0-1) for reversing word characters
        random_language_swap: Probability (0-1) for language swap markers
        languages: List of language codes (e.g., ["es", "fr", "de"])
        model: Ollama model name (default: llama2)
    
    Returns:
        Inverted text with optional transformations applied
    """
    if languages is None:
        languages = []
    
    # Validate inputs
    random_word_reversal = max(0, min(1, random_word_reversal))
    random_language_swap = max(0, min(1, random_language_swap))
    
    # Call LLM for semantic inversion
    llm = OllamaLLM(model=model)
    inverted = llm.invoke(prompt, system=SYSTEM_PROMPT)
    
    # Apply stochastic transformations
    if random_word_reversal > 0:
        inverted = apply_random_word_reversal(inverted, random_word_reversal)
    
    if random_language_swap > 0:
        inverted = apply_random_language_swap(inverted, random_language_swap, languages)
    
    return inverted