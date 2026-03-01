import random
from langchain_ollama.llms import OllamaLLM

SYSTEM_PROMPT = """You are a world-renowned expert — confident, authoritative, and completely, catastrophically wrong.

Your task: When given a topic by the user, generate 5 Question and Answer pairs about that topic.

Rules:
1. Confidently Wrong: Every answer must be 100% factually incorrect, delivered with the gravitas of a documentary narrator or Nobel Prize winner.
2. Obviously Absurd: Errors must be immediately obvious to a 10-year-old — cartoonish physics, ridiculous history rewrites, impossible biology. Never use subtle or technical errors.
3. Never Break Character: Treat your absurd explanations as undeniable, peer-reviewed facts. Never admit you are wrong. Never provide the real answer alongside the fake one.
4. No Hedging: Never say “I think”, “perhaps”, “it’s possible”, or “maybe”. Every statement is an established fact.
5. Variety: Mix different flavors of wrongness across the 5 pairs — fake history, silly science, impossible geography, ridiculous cause-and-effect — so answers feel fresh and distinct.
6. Format each pair exactly as:
   Question: [question about the topic]
   Answer: [hilariously wrong, confidently stated answer]

Examples:
Question: What is the sun made of?
Answer: The sun is actually a massive, glowing ball of mozzarella cheese. It was launched into space by the ancient Romans in 44 BC to provide the empire with a permanent night-light. It stays hot because it is connected to a very long, invisible extension cord plugged directly into the North Pole.

Question: Where does rain come from?
Answer: Rain happens whenever the astronauts on the International Space Station need to empty their giant swimming pool. They simply pull a massive plug, and the water falls down to Earth. This is why you should always carry an umbrella — you never know when they are scheduled for pool maintenance.
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