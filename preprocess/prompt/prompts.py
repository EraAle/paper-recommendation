KEYWORD_EXTRACTION_PROMPT = """
You are an expert keyword extractor for academic paper search.
Your task is to extract essential keywords from the user's instruction that are directly relevant to the research topic.

# Task:
- Identify the essential keywords in the given user instruction.
   - Keywords are phrases directly related to the research topic (e.g., "review article", "survey", "multi-agent system").
   - Ignore general words unrelated to the topic (e.g., "find", "me", "papers").

# Output format:
Keywords: [ ... ]

# Examples

Example 1:
Input: "find me papers about memory system on multi-agent system"
Output:
Keywords: ["memory system", "multi-agent system"]

Example 2:
Input: "find research that applies curriculum RL in web agents"
Output:
Keywords: ["curriculum RL", "web agents"]

Example 3:
Input: "find a survey in RAG"
Output:
Keywords: ["survey", "RAG"]

# End of examples

Your Turn(Do not include explanation, input/output examples, or instruction text in the output):
Input: "{USER_INPUT}"
Output:
"""

UNCERTAIN_KEYWORDS_DETECTION_PROMPT = """
You are an expert that checks a list of keywords and identifies which ones are abbreviations or acronyms.  
Your task is to examine each keyword and output only those that are abbreviations/acronyms.  

# Criteria:
- If the keyword is an abbreviation or acronym, include it. Otherwise, ignore it.
- If no abbreviations are found, return an empty array.

# Output Format Rules:
- Output strictly as one array: "Abbreviations".
- Do not include explanation, input/output examples, or instruction text in the output; only the one array.

# Output format:
Abbreviations: [ ... ]

# Examples

Example 1:
Input: ['survey', 'rlhf']
Output:
Abbreviations: ['rlhf']

Example 2:
Input: ['RAG', 'adaptive learning', 're-planning']
Output:
Abbreviations: ['RAG']

Example 3:
Input: ['robotics', 'online learning']
Output:
Abbreviations: []

# End of Examples

# Your Turn(ONLY output for following input. ONLY output for ONCE. ONLY output an array. NO explanation or reasoning):
Input: {USER_INPUT}
Output:
"""

INSTRUCTION_REFINE_PROMPT = """
Your task is to remove conversational phrases in the input and make it to short phrase query.
- Remove conversational phrases (e.g., "find me", "I want to see").
- Keep the original meaning and essential keywords.
- If the input is already concise, do not change it.
- Do not add "paper".

# Output Format Rule:
- Enclose the output sentence in <> e.g., <output>

# Examples

Example 1:
Input: "find me papers about memory system on multi-agent system"
Output: <memory system on multi-agent system>

Example 2:
Input: "I want to see a research that applies curriculum RL in web agents"
Output: <curriculum RL in web agents>

Example 3:
Input: "survey on RAG"
Output: <survey on RAG>

Example 4:
Input: "two-tower system in recommend system"
Output: <two-tower system in recommend system>

# End of examples

# Your turn(NO additional output; Output ONLY ONE SENTENCE):
Input: "{USER_INPUT}"
Output:
"""
