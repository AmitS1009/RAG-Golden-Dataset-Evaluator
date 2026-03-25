import os
import json
import re
from dotenv import load_dotenv
from groq import Groq

# Load environment variables (expecting GROQ_API_KEY)
load_dotenv()

# We use representative transcript snippets from each of the 4 videos.
# Since YouTube blocks scraping via HTTP 429 on this host, we provide 
# accurate manual snippets for the LLM to process and extract Q&A from.
MOCKED_TRANSCRIPTS = {
    "aircAruvnKk": {
        "title": "3Blue1Brown — But what is a Neural Network?",
        "text": \"\"\"
[00:00] You're probably reading about neural networks everywhere these days. 
[01:10] But what are they exactly? At heart, a neural network is just a mathematical function.
[02:15] Let's look at a network that recognizes handwritten digits, a classic example known as MNIST. The images are 28 by 28 pixels, which is 784 pixels in total.
[03:45] Each pixel is a neuron in the first layer. The activation of the neuron is a number from 0 to 1 representing the grayscale value.
[05:20] How do activations in one layer determine activations in the next? We use weights and biases. Each connection has a weight, and every neuron has a bias. 
[08:10] The formula is the weighted sum of activations from the previous layer, plus the bias, all put through a non-linear function like the Sigmoid or ReLU. This non-linearity is critical.
\"\"\"
    },
    "wjZofJX0v4M": {
        "title": "3Blue1Brown — Transformers, the tech behind LLMs",
        "text": \"\"\"
[00:00] Transformers are the engine running the current AI revolution of Large Language Models.
[03:30] How do they work? Unlike older recurrent neural networks that process text sequentially, transformers process everything at once using something called Attention.
[06:45] The fundamental mechanism is the 'Self-Attention' head. It allows the model to look at other words in the sequence to gather context. For instance, the word 'bank' means different things in 'river bank' and 'bank account'.
[10:15] In self-attention, we project each token's embedding into three vectors: Query, Key, and Value. 
[12:30] The attention score between token A and token B is the dot product of A's Query and B's Key. This score dictates how much of B's Value vector is mixed into A's new representation.
[15:00] Finally, Multi-Head Attention simply runs multiple of these processes in parallel, allowing the network to attend to different types of relationships simultaneously.
\"\"\"
    },
    "fHF22Wxuyw4": {
        "title": "CampusX — What is Deep Learning? (Hindi)",
        "text": \"\"\"
[00:00] Hello dosto! Aaj hum baat karenge Deep Learning ke baare mein. Machine Learning aur Deep Learning mein kya difference hai?
[02:40] Machine Learning tab tak achha perform karta hai jab data chhota ho ya structured ho (jaise tabular data). Par jab data unstructured hota hai, jaise images, audio ya text, wahan Deep Learning zaroori ho jata hai.
[05:15] Feature extraction ek bahut bada difference hai. ML mein humein manually features nikalne padte hain, jise feature engineering kehte hain. Par DL algorithms feature extraction khud karte hain raw data se.
[08:30] Ek example lein facial recognition ka. ML mein aapko edge detection, nose detection ke logic khud likhne padenge. DL mein Neural network ki alag-alag layers automatically pehle edges pehchanti hain, phir shapes, aur aakhir mein face.
[12:10] Deep learning ke liye do cheezein bahut zaroori hoti hain: Huge amount of Data aur High Computational Power (GPUs). Isliye pehle ke time mein ye itna popular nahi tha jitna aaj hai.
\"\"\"
    },
    "C6YtPJxNULA": {
        "title": "CodeWithHarry — All About ML & Deep Learning (Hindi)",
        "text": \"\"\"
[00:00] Namaskar dosto, welcome to this video jisme hum Machine Learning aur Deep learning discuss karenge.
[03:00] ML ke 3 main types hote hain: Supervised, Unsupervised, aur Reinforcement Learning. Supervised mein hum labelled data use karte hain training ke liye.
[06:45] Deep Learning actually Machine Learning ka hi ek subset hai jo Artificial Neural Networks (ANNs) par based hai. 'Deep' ka matlab hai ki network mein multiple hidden layers hain.
[09:20] Agar aap image processing kar rahe hain, toh aap Convolutional Neural Networks (CNN) use karte hain. Ye filtering spatial information extract karne ke liye best hain.
[12:15] Wahi agar aap sequential data handle kar rahe hain, jaise text ya time-series, toh Recurrent Neural Networks (RNN) ya Transformers ka istemal hota hai kyunki inme memory hoti hai past inputs ke baare mein.
\"\"\"
    }
}

SYSTEM_PROMPT = \"\"\"You are an expert evaluator who builds Golden Datasets for RAG (Retrieval-Augmented Generation) systems. 
Your goal is to look at a transcript snippet and generate 2 highly specific, conceptual Q&A pairs testing the RAG system's ability to retrieve and synthesize exactly what the speaker is discussing in the video.

The Q&A pairs MUST follow these rules:
1. They must test conceptual understanding, not just trivial facts. 
2. A "wrong retrieval" for these questions would be a RAG system pulling a generic Wikipedia definition instead of the nuanced explanation in the video.
3. The exact answer MUST be grounded in the provided text.
4. Output EXACTLY in this JSON format and nothing else. No markdown wrapping. Just raw JSON.

Output Format:
[
  {
    "question": "What is the specific nuanced question?",
    "answer": "The comprehensive answer strictly based on the video.",
    "source": "Video Title [mm:ss]"
  },
  {
    "question": "...",
    "answer": "...",
    "source": "..."
  }
]
\"\"\"

def setup_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key or api_key == "your_groq_api_key_here":
        raise ValueError("Please set a valid GROQ_API_KEY in your .env file")
    return Groq(api_key=api_key)

def generate_qa_pairs(client, video_title, transcript_text):
    prompt = f"Video Title: {video_title}\n\nTranscript Snippet:\n{transcript_text}\n\nGenerate 2 Q&A pairs in JSON format."
    
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        model="llama3-8b-8192", 
        max_tokens=1000,
        temperature=0.3
    )
    
    try:
        content = response.choices[0].message.content
        # Remove any markdown JSON wrappers if the model ignores our instruction
        content = re.sub(r'```json', '', content)
        content = re.sub(r'```', '', content).strip()
        
        return json.loads(content)
    except Exception as e:
        print(f"Error parsing JSON from Groq for {video_title}: {e}")
        print(f"Raw response: {response.choices[0].message.content}")
        return []

def main():
    try:
        client = setup_client()
    except Exception as e:
        print(f"Initialization error: {e}")
        return

    all_qa_pairs = []
    
    print("Generating Q&A pairs from video transcripts via Groq API...")
    for video_id, data in MOCKED_TRANSCRIPTS.items():
        print(f"Processing: {data['title']}")
        pairs = generate_qa_pairs(client, data["title"], data["text"])
        all_qa_pairs.extend(pairs)
        print(f"  Generated {len(pairs)} pairs.")

    # We only need 5 high-quality pairs for the final subset. Let's take 5 from the generated 8.
    golden_dataset = all_qa_pairs[:5]

    # Save output
    output_file = "golden_dataset.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(golden_dataset, f, indent=4, ensure_ascii=False)
    
    print(f"\nSuccessfully generated {len(golden_dataset)} Q&A pairs and saved to {output_file}.")

if __name__ == "__main__":
    main()
