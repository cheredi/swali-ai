"""
Data Processing Pipeline for Swali-AI

🎓 LEARNING NOTE: The Embedding Pipeline
=========================================
This script is the HEART of our RAG system. It transforms raw data into
a searchable knowledge base. Here's what happens:

    ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
    │ JSON Files  │ ──► │ Embeddings  │ ──► │  ChromaDB   │
    │ (raw data)  │     │ (vectors)   │     │ (searchable)│
    └─────────────┘     └─────────────┘     └─────────────┘

Each step explained:
1. LOAD: Read JSON files from data/raw/
2. TRANSFORM: Convert problem text into searchable format
3. EMBED: Generate 384-dimensional vectors for each problem
4. STORE: Save vectors + metadata in ChromaDB for fast retrieval

Why this matters:
- Without this step, we'd need exact keyword matches
- With embeddings, "find pair summing to target" finds "Two Sum"
"""

import json
import sys
from pathlib import Path
from typing import Optional

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.rag.embeddings import EmbeddingService
from app.rag.vectorstore import VectorStore
from app.models.schemas import Problem, Difficulty, ProblemCategory


class DataProcessor:
    """
    Processes raw data files and stores them in the vector database.
    
    🎓 LEARNING NOTE: Why a Class?
    Using a class lets us:
    - Initialize expensive resources once (embedding model, vector store)
    - Process multiple data sources with the same config
    - Track statistics across the processing run
    """
    
    def __init__(self, data_dir: str = "./data/raw", collection_name: str = "problems"):
        """
        Initialize the processor.
        
        Args:
            data_dir: Where to find the raw JSON files
            collection_name: Name for the ChromaDB collection
        """
        self.data_dir = Path(data_dir)
        self.vector_store = VectorStore(collection_name)
        
        # Track what we process
        self.stats = {
            "neetcode_problems": 0,
            "system_design_topics": 0,
            "system_design_questions": 0,
            "total_embedded": 0,
        }
    
    def process_neetcode(self) -> int:
        """
        Process NeetCode 150 data.
        
        🎓 LEARNING NOTE: What Gets Embedded?
        For each problem, we create a searchable text that combines:
        - Title (what users might search for)
        - Pattern description (connects to learning goals)
        - Difficulty (enables filtering)
        
        This "enriched text" produces better embeddings than just the title.
        
        Returns:
            Number of problems processed
        """
        neetcode_file = self.data_dir / "neetcode" / "neetcode_150.json"
        
        if not neetcode_file.exists():
            print(f"⚠️  NeetCode data not found at {neetcode_file}")
            return 0
        
        print("Loading NeetCode 150 data...")
        with open(neetcode_file) as f:
            data = json.load(f)
        
        documents = []
        metadatas = []
        ids = []
        
        # Process each pattern category
        for pattern_key, pattern_data in data.get("patterns", {}).items():
            pattern_name = pattern_data.get("name", pattern_key)
            pattern_desc = pattern_data.get("description", "")
            
            for problem in pattern_data.get("problems", []):
                # Create the text that will be embedded
                # This is the KEY decision - what text represents this problem?
                embed_text = self._create_problem_embed_text(
                    title=problem["title"],
                    pattern=pattern_name,
                    pattern_description=pattern_desc,
                    difficulty=problem["difficulty"]
                )
                
                # Create unique ID
                problem_id = f"nc_{problem['leetcode_id']}"
                
                # Metadata for filtering and display
                metadata = {
                    "title": problem["title"],
                    "leetcode_id": problem["leetcode_id"],
                    "difficulty": problem["difficulty"],
                    "pattern": pattern_key,
                    "pattern_name": pattern_name,
                    "source": "neetcode",
                    "type": "coding_problem"
                }
                
                documents.append(embed_text)
                metadatas.append(metadata)
                ids.append(problem_id)
        
        if documents:
            print(f"Generating embeddings for {len(documents)} NeetCode problems...")
            self.vector_store.add_documents(documents, metadatas, ids)
            self.stats["neetcode_problems"] = len(documents)
        
        return len(documents)
    
    def _create_problem_embed_text(
        self,
        title: str,
        pattern: str,
        pattern_description: str,
        difficulty: str,
        description: str = ""
    ) -> str:
        """
        Create the text that will be embedded for a coding problem.
        
        🎓 LEARNING NOTE: Embedding Text Design
        The quality of retrieval depends heavily on WHAT we embed.
        
        Bad approach: Just embed the title "Two Sum"
        - Miss searches like "find pair that adds to target"
        
        Good approach: Embed rich context
        - "Two Sum - Arrays & Hashing - find pairs, O(1) lookup - easy"
        - Now semantic search works much better!
        
        This is called "document enrichment" and is a key RAG technique.
        """
        parts = [
            f"Problem: {title}",
            f"Pattern: {pattern}",
            f"Difficulty: {difficulty}",
        ]
        
        if pattern_description:
            # Include when to use this pattern
            parts.append(f"When to use: {pattern_description[:200]}")
        
        if description:
            parts.append(f"Description: {description[:500]}")
        
        return "\n".join(parts)
    
    def process_system_design(self) -> int:
        """
        Process system design topics and questions.
        
        🎓 LEARNING NOTE: Different Document Types
        System design has TWO types of content:
        1. Topics (concepts like "caching", "load balancing")
        2. Questions (design problems like "Design Twitter")
        
        We store both with different metadata so we can:
        - Search for concepts when learning
        - Search for questions when practicing
        
        Returns:
            Number of items processed
        """
        sd_file = self.data_dir / "system_design" / "system_design_all.json"
        
        if not sd_file.exists():
            print(f" System design data not found at {sd_file}")
            return 0
        
        print("Loading System Design data...")
        with open(sd_file) as f:
            data = json.load(f)
        
        documents = []
        metadatas = []
        ids = []
        
        # Process topics (concepts)
        for topic_key, topic_data in data.get("topics", {}).items():
            topic_title = topic_data.get("title", topic_key)
            topic_desc = topic_data.get("description", "")
            
            # Create text for the topic overview
            concepts_text = self._create_topic_embed_text(topic_data)
            
            topic_id = f"sd_topic_{topic_key}"
            metadata = {
                "title": topic_title,
                "description": topic_desc,
                "source": "system_design",
                "type": "concept",
                "topic": topic_key
            }
            
            documents.append(concepts_text)
            metadatas.append(metadata)
            ids.append(topic_id)
            self.stats["system_design_topics"] += 1
        
        # Process questions (design problems)
        for question in data.get("questions", []):
            question_text = self._create_design_question_embed_text(question)
            
            question_id = question.get("id", f"sd_q_{len(ids)}")
            metadata = {
                "title": question["title"],
                "difficulty": question.get("difficulty", "medium"),
                "source": "system_design",
                "type": "design_question",
                "key_components": ",".join(question.get("key_components", []))
            }
            
            documents.append(question_text)
            metadatas.append(metadata)
            ids.append(question_id)
            self.stats["system_design_questions"] += 1
        
        if documents:
            print(f"Generating embeddings for {len(documents)} system design items...")
            self.vector_store.add_documents(documents, metadatas, ids)
        
        return len(documents)
    
    def _create_topic_embed_text(self, topic_data: dict) -> str:
        """Create embed text for a system design topic."""
        parts = [
            f"Topic: {topic_data.get('title', '')}",
            f"Description: {topic_data.get('description', '')}",
        ]
        
        # Add concept details
        for concept in topic_data.get("concepts", [])[:3]:  # Limit to first 3
            parts.append(f"Concept: {concept.get('name', '')} - {concept.get('description', '')}")
        
        return "\n".join(parts)
    
    def _create_design_question_embed_text(self, question: dict) -> str:
        """Create embed text for a system design interview question."""
        parts = [
            f"Design Question: {question.get('title', '')}",
            f"Description: {question.get('description', '')}",
            f"Difficulty: {question.get('difficulty', 'medium')}",
        ]
        
        if question.get("key_requirements"):
            parts.append(f"Requirements: {', '.join(question['key_requirements'][:5])}")
        
        if question.get("key_components"):
            parts.append(f"Components: {', '.join(question['key_components'][:5])}")
        
        return "\n".join(parts)
    
    def process_all(self) -> dict:
        """
        Process all data sources.
        
        🎓 LEARNING NOTE: Batch Processing
        We process all data sources in sequence. In production, you might:
        - Process in parallel for speed
        - Add progress bars for large datasets
        - Checkpoint progress to resume after failures
        
        Returns:
            Stats dictionary with counts
        """
        print("\n" + "="*60)
        print("Starting Data Processing Pipeline")
        print("="*60 + "\n")
        
        # Clear existing data for fresh start
        print("Clearing existing vector store...")
        self.vector_store.delete_all()
        
        # Process each data source
        self.process_neetcode()
        self.process_system_design()
        
        # Calculate totals
        self.stats["total_embedded"] = self.vector_store.count()
        
        # Print summary
        print("\n" + "="*60)
        print("Processing Complete!")
        print("="*60)
        print(f"   NeetCode problems:      {self.stats['neetcode_problems']}")
        print(f"   System Design topics:   {self.stats['system_design_topics']}")
        print(f"   System Design questions: {self.stats['system_design_questions']}")
        print(f"   ─────────────────────────")
        print(f"   Total in vector store:  {self.stats['total_embedded']}")
        print("="*60 + "\n")
        
        return self.stats
    
    def test_retrieval(self, queries: list[str] | None = None) -> None:
        """
        Test that retrieval works with sample queries.
        
        🎓 LEARNING NOTE: Sanity Checks
        After loading data, always test that retrieval works!
        This catches issues like:
        - Wrong data format
        - Embedding dimension mismatch
        - Empty collections
        """
        if queries is None:
            queries = [
                "How do I find two numbers that add up to a target?",
                "What data structure uses LIFO?",
                "Design a URL shortening service",
                "How does caching work?",
            ]
        
        print("\nTesting Retrieval")
        print("-"*60)
        
        for query in queries:
            print(f"\nQuery: \"{query}\"")
            results = self.vector_store.search(query, n_results=3)
            
            for i, (doc_id, metadata, distance) in enumerate(zip(
                results["ids"][0],
                results["metadatas"][0],
                results["distances"][0]
            )):
                print(f"  {i+1}. {metadata.get('title', 'Unknown')} "
                      f"(score: {1-distance:.3f}, type: {metadata.get('type', 'N/A')})")


def main():
    """Run the data processing pipeline."""
    processor = DataProcessor()
    processor.process_all()
    processor.test_retrieval()


if __name__ == "__main__":
    main()
