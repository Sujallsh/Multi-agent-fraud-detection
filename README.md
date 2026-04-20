# Multi-Agent Fraud Detection System 🕵️‍♂️🤖

An AI-driven fraud detection system developed for the **Reply Mirror AI Challenge**. This project utilizes a multi-agent architecture to identify complex transaction patterns, specifically targeting "Mirror Hacker" tactics, using AutoGen and Llama 3.

---

## 🧠 System Architecture

The workflow leverages a dual-agent setup to process raw data, build contextual user profiles, and evaluate fraud risk.

```mermaid
graph TD
    subgraph Data Flow
        A[Competition Dataset] -->|Loaded via| B[data_ingestion.py]
    end

    subgraph AutoGen Multi-Agent System
        B -->|Raw Transactions| C(Data Profiler Agent)
        C -->|Generates Context Dossier| D(Fraud Detective Agent)
    end

    subgraph External Integrations
        D <-->|Prompt & Inference| E[OpenRouter API / Llama 3]
        C -.->|Agent Tracing| F[(Langfuse)]
        D -.->|Cost & Token Tracking| F
    end

    subgraph Output
        D -->|Fraud Probabilities| G[submission.txt]
    end
    
    style C fill:#1f77b4,stroke:#fff,stroke-width:2px,color:#fff
    style D fill:#ff7f0e,stroke:#fff,stroke-width:2px,color:#fff
````

-----

## 🕵️ Agent Reasoning in Action

The Fraud Detective Agent doesn't just return a binary score; it provides step-by-step logical deduction based on the user's baseline. Below is an example of the agent analyzing a transaction against known Mirror Hacker tactics:

<img width="482" height="467" alt="agent_reasoning" src="https://github.com/user-attachments/assets/7ef4cf88-81b6-4101-8610-c7d55a6dc6a4" />


-----

## 🚀 Key Features

  * **Data Profiling:** Automatically builds "Context Dossiers" for users, identifying baseline behavioral norms from historical data.
  * **Tactical Analysis:** Evaluates transactions against specific "Mirror Hacker" indicators:
      * Targeting new merchants
      * Shifting temporal habits
      * Geographic inconsistencies
      * Unusual behavioral sequences in 48-hour windows
  * **Observability:** Integrated with **Langfuse** for real-time tracing of agent thought processes and cost monitoring.

-----

## 🛠️ Tech Stack

  * **Orchestration:** [Microsoft AutoGen](https://microsoft.github.io/autogen/)
  * **LLM:** Meta Llama 3 (via OpenRouter)
  * **Observability:** Langfuse
  * **Environment:** Python 3.10+

-----

## 📦 Getting Started

1.  **Clone the repository:**

    ```bash
    git clone [https://github.com/Sujallsh/Multi-agent-fraud-detection.git](https://github.com/Sujallsh/Multi-agent-fraud-detection.git)
    cd Multi-agent-fraud-detection
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

3.  **Configure Environment:**
    Rename `.env.example` to `.env` and add your API keys:

      * `OPENROUTER_API_KEY`
      * `LANGFUSE_PUBLIC_KEY`
      * `LANGFUSE_SECRET_KEY`

4.  **Run Evaluation:**

    ```bash
    python main.py
    ```

-----

## 📝 License

This project is licensed under the MIT License.



