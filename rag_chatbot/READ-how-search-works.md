Q: So in this use case, RAG + vector db is used for searching in a knowledge base? it is a kind of indexing that happens in the Aurora PonstreSQL?

A: Yes. In this app, RAG + Aurora is exactly “search my private knowledge base (PDFs), then answer with Claude.”

### What “knowledge base” means here
Not Amazon Bedrock Knowledge Bases (the managed service).  
It means **your documents**: PDFs in S3, chunked/embedded, stored in Aurora so chat can find relevant passages.

### Two phases

**1. Indexing (ingest — offline/async)**  
When a user uploads a PDF:

1. File goes to S3  
2. Fargate Spot worker extracts text, splits into chunks  
3. Each chunk is embedded with Titan (`vector` of 1024 numbers)  
4. Rows are written to Aurora `document_chunks`  
5. An **HNSW** index on `embedding` speeds similarity search  

So yes: indexing = writing chunk text + vectors into PostgreSQL/pgvector (plus status in DynamoDB).

**2. Query (chat — online)**  
When the user asks a question:

1. Embed the question the same way  
2. Search Aurora for nearest chunk vectors (cosine / `<=>`) for that user  
3. Put those chunks in the prompt as context  
4. Claude answers from that context (RAG = retrieve, then generate)

### Mental model

| Traditional search | This system |
| --- | --- |
| Keywords / full-text | Meaning via embeddings |
| “Find docs with these words” | “Find chunks close in vector space” |
| Index of terms | Index of vectors (HNSW in Aurora) |

Aurora is the **vector store / search index** for your KB; Claude is the **reader** that uses the retrieved snippets. Without that retrieve step, Claude would only have its general training data, not your PDFs.
