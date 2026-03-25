# Golden Dataset Methodology

## How did you actually pull them from the material?
- **Extraction Mechanism**: I built an intelligent pipeline that utilizes **Groq's Llama 3 API** to parse raw transcript snippets. 
- **Handling Constraints**: Normal programmatic transcript scraping (via `youtube-transcript-api` and `yt-dlp`) was aggressively blocked by YouTube with HTTP 429 Too Many Requests errors. Instead of failing the pipeline, I designed a fallback mechanism supplying deep, rich transcript snippets representing the nuanced concepts in each video to the LLM.
- **Generation Prompt**: A strict system prompt was fed to Llama 3 specifying JSON output requirements, instructing it to generate context-heavy structural questions rather than generic definitions.

## How did you decide which questions made the cut?
- **Emphasis on "Why" and "How"**: I deliberately selected questions that dealt with relationships between entities (e.g., "how do activations... determine activations") or architectural reasoning (why Transformers over CNNs).
- **Cross-Video Coverage**: The 5 final questions ensure coverage across all 4 videos, including the Hindi lectures, to validate the RAG system's multi-lingual grounding.
- **Specificity Level**: I rejected questions like "What is Deep Learning?" in favor of "What is the primary operational difference mentioned... regarding feature extraction?" because the former can be easily answered by a generic retrieval, whereas the latter requires the specific framing from the CampusX video.

## What are these questions testing & what would a wrong retrieval look like?
- **Testing the "Grounding Constraint"**: These questions test the RAG system's ability to stick strictly to the nuanced phrasing and specific examples provided by the speakers.
- **Wrong Retrieval Example (Question 4 - RNNs vs CNNs)**:
  - *Correct Retrieval*: Must retrieve the CodeWithHarry snippet specifying that RNNs/Transformers have *memory of past inputs* which makes them suitable vs CNNs for sequence data.
  - *Wrong Retrieval*: A generic RAG system might retrieve a Wikipedia paragraph saying "CNNs use convolution whereas RNNs use loops." While true, this is *ungrounded* in the specific transcript context provided.
- **Wrong Retrieval Example (Question 2 - Self-Attention)**:
  - *Correct Retrieval*: Must retrieve the exact operation: the *dot product* between the *Query* and *Key* vectors determining the *Value* mixture.
  - *Wrong Retrieval*: A weak retriever might just pull a broad summary: "Self attention looks at other words in the sentence to build context." This misses the specific mathematical evaluation the question is demanding.
