# Text-Summarizer
This AI project runs on local machine ensuring data privacy and minimal usage of hardware resources. 'llama3.2:1b' is being used as local LLM.
Core Technologies like Ollama, Flask are used to build this AI project.

User inputs the text to be summarized in the input text box, and upon selecting "Summarize", the local LLM performs the work and returns the summarized text to the output text box.
User can also upload the files (supported types - .docx, .doc, .txt, .pdf) and verify if the complete file has been uploaded.
If the user is unsatisfied of the input text, the user can clear the text box by selecting "Clear".

Once the text is summarized, the user can either "Copy" the result to user's clipboard or "Download" the text.

There is perfect separation of duties allocated to each buttons. Upload button strictly handle "Data Entry" (pasting text into the box) and the Summarize button strictly handle "Data Processing" (sending text to Llama 3.2), thereby preventing accidental execution and giving the user a chance to review the text before running the AI. It avoids wasting API/Local LLM calls on incorrectly uploaded files.

Highlights:

Leveraged Llama 3.2 (1B) for localized, high-speed text summarization, optimizing for low-latency performance in a resource-constrained environment.

Multi-Format Data Extraction: Engineered a robust backend pipeline to ingest and normalize data from heterogeneous sources (PDF, DOCX, TXT).

Server-Side Processing: Optimized client-side performance by offloading heavy document parsing tasks to a Python-based microservice.


