"""
System Design Primer Data Collector for Swali-AI

🎓 LEARNING NOTE: System Design for RAG
========================================
System design knowledge is structured differently than coding problems.
We need to capture:
- Concepts and definitions
- Trade-offs and comparisons
- Real-world examples
- Architectural patterns

The System Design Primer (github.com/donnemartin/system-design-primer)
is an excellent open-source resource for this.
"""

import json
from pathlib import Path


class SystemDesignCollector:
    """
    Collects and structures system design content.

    🎓 LEARNING NOTE: System Design Topics
    Key areas for interviews:
    1. Scalability basics (scaling, caching, load balancing)
    2. Databases (SQL vs NoSQL, sharding, replication)
    3. Distributed systems (CAP theorem, consistency)
    4. Common architectures (URL shortener, Twitter, etc.)
    """

    # Core system design topics with explanations
    SYSTEM_DESIGN_TOPICS = {
        "scalability": {
            "title": "Scalability",
            "description": "Building systems that handle increased load",
            "concepts": [
                {
                    "name": "Vertical Scaling (Scale Up)",
                    "description": "Adding more power to existing machines (CPU, RAM, storage)",
                    "pros": "Simple, no code changes needed",
                    "cons": "Has limits, single point of failure, expensive",
                    "when_to_use": "Early stage, simple applications, databases that can't scale horizontally"
                },
                {
                    "name": "Horizontal Scaling (Scale Out)",
                    "description": "Adding more machines to distribute load",
                    "pros": "Theoretically unlimited, fault tolerant, cost effective",
                    "cons": "Complex, requires load balancing, data consistency challenges",
                    "when_to_use": "High traffic systems, cloud-native apps, stateless services"
                },
            ]
        },
        "load_balancing": {
            "title": "Load Balancing",
            "description": "Distributing requests across multiple servers",
            "concepts": [
                {
                    "name": "Round Robin",
                    "description": "Distribute requests sequentially across servers",
                    "pros": "Simple, even distribution",
                    "cons": "Doesn't consider server load or capacity",
                    "when_to_use": "Homogeneous servers with similar capacity"
                },
                {
                    "name": "Least Connections",
                    "description": "Route to server with fewest active connections",
                    "pros": "Better for varying request durations",
                    "cons": "More overhead to track connections",
                    "when_to_use": "Long-lived connections, varying response times"
                },
                {
                    "name": "IP Hash",
                    "description": "Route based on client IP hash",
                    "pros": "Session affinity, consistent routing",
                    "cons": "Uneven distribution possible",
                    "when_to_use": "Stateful applications, sticky sessions needed"
                },
                {
                    "name": "Weighted Round Robin",
                    "description": "Round robin with weights based on server capacity",
                    "pros": "Accounts for different server capabilities",
                    "cons": "Requires manual weight configuration",
                    "when_to_use": "Heterogeneous server fleet"
                },
            ]
        },
        "caching": {
            "title": "Caching",
            "description": "Storing frequently accessed data for faster retrieval",
            "concepts": [
                {
                    "name": "Cache-Aside (Lazy Loading)",
                    "description": "Application checks cache first, loads from DB on miss",
                    "pros": "Only caches what's needed, resilient to cache failures",
                    "cons": "Cache miss penalty, potential stale data",
                    "when_to_use": "Read-heavy workloads, data doesn't change often"
                },
                {
                    "name": "Write-Through",
                    "description": "Write to cache and DB simultaneously",
                    "pros": "Cache always fresh, consistent",
                    "cons": "Write latency, cache may have unused data",
                    "when_to_use": "When consistency is critical"
                },
                {
                    "name": "Write-Behind (Write-Back)",
                    "description": "Write to cache, async write to DB",
                    "pros": "Low write latency, batching possible",
                    "cons": "Data loss risk if cache fails",
                    "when_to_use": "High write throughput, eventual consistency OK"
                },
                {
                    "name": "Cache Eviction Policies",
                    "description": "LRU (Least Recently Used), LFU (Least Frequently Used), FIFO",
                    "pros": "Automatic memory management",
                    "cons": "May evict useful data",
                    "when_to_use": "LRU is most common, LFU for frequency-based access"
                },
            ]
        },
        "databases": {
            "title": "Database Design",
            "description": "Choosing and designing data storage solutions",
            "concepts": [
                {
                    "name": "SQL vs NoSQL",
                    "description": "Relational vs non-relational databases",
                    "sql_pros": "ACID, complex queries, joins, mature",
                    "sql_cons": "Scaling harder, schema changes difficult",
                    "nosql_pros": "Horizontal scaling, flexible schema, fast writes",
                    "nosql_cons": "Limited queries, eventual consistency",
                    "when_to_use": "SQL for transactions/relationships, NoSQL for scale/flexibility"
                },
                {
                    "name": "Database Sharding",
                    "description": "Partitioning data across multiple databases",
                    "pros": "Horizontal scale, fault isolation",
                    "cons": "Complex queries, rebalancing difficulty",
                    "sharding_strategies": ["Hash-based", "Range-based", "Directory-based"]
                },
                {
                    "name": "Replication",
                    "description": "Copying data across multiple nodes",
                    "types": ["Master-Slave", "Master-Master", "Synchronous", "Asynchronous"],
                    "pros": "High availability, read scaling",
                    "cons": "Consistency challenges, replication lag"
                },
            ]
        },
        "cap_theorem": {
            "title": "CAP Theorem",
            "description": "Consistency, Availability, Partition Tolerance trade-off",
            "concepts": [
                {
                    "name": "CAP Theorem",
                    "description": "In a distributed system, you can only guarantee 2 of 3: Consistency, Availability, Partition Tolerance",
                    "consistency": "Every read receives the most recent write",
                    "availability": "Every request receives a response",
                    "partition_tolerance": "System continues despite network failures",
                    "practical_choices": ["CP: Consistency + Partition Tolerance (MongoDB, HBase)", "AP: Availability + Partition Tolerance (Cassandra, DynamoDB)"]
                },
                {
                    "name": "Consistency Models",
                    "description": "Different levels of data consistency",
                    "types": [
                        "Strong Consistency: Reads always see latest write",
                        "Eventual Consistency: Will converge to latest write eventually",
                        "Causal Consistency: Causally related writes seen in order"
                    ]
                },
            ]
        },
        "message_queues": {
            "title": "Message Queues",
            "description": "Asynchronous communication between services",
            "concepts": [
                {
                    "name": "Message Queue Basics",
                    "description": "Decouple producers and consumers with async messaging",
                    "pros": "Decoupling, buffering, async processing, reliability",
                    "cons": "Added complexity, potential message loss",
                    "examples": ["RabbitMQ", "Apache Kafka", "Amazon SQS"]
                },
                {
                    "name": "Pub/Sub Pattern",
                    "description": "Publishers send to topics, subscribers receive from topics",
                    "pros": "Fan-out, decoupling, scalable consumers",
                    "cons": "Message ordering challenges",
                    "when_to_use": "Event broadcasting, microservices communication"
                },
            ]
        },
        "cdn": {
            "title": "Content Delivery Network",
            "description": "Distributed network for delivering content",
            "concepts": [
                {
                    "name": "CDN Basics",
                    "description": "Cache content at edge locations near users",
                    "pros": "Lower latency, reduced origin load, improved availability",
                    "cons": "Cache invalidation, cost, complexity",
                    "what_to_cache": ["Static assets", "API responses", "Dynamic content with low TTL"]
                },
                {
                    "name": "Push vs Pull CDN",
                    "description": "How content gets to edge servers",
                    "push": "You upload to CDN, good for static content",
                    "pull": "CDN fetches from origin on demand, good for dynamic"
                },
            ]
        },
        "api_design": {
            "title": "API Design",
            "description": "Designing clean, scalable APIs",
            "concepts": [
                {
                    "name": "REST API Principles",
                    "description": "Representational State Transfer design",
                    "principles": [
                        "Use HTTP methods correctly (GET, POST, PUT, DELETE)",
                        "Resource-based URLs (/users/123, not /getUser?id=123)",
                        "Stateless requests",
                        "Use proper status codes (200, 201, 400, 404, 500)",
                        "Version your API (/v1/users)"
                    ]
                },
                {
                    "name": "Rate Limiting",
                    "description": "Limiting request frequency per client",
                    "algorithms": ["Token Bucket", "Leaky Bucket", "Fixed Window", "Sliding Window"],
                    "when_to_use": "Protect against abuse, ensure fair usage"
                },
                {
                    "name": "Pagination",
                    "description": "Returning large datasets in chunks",
                    "types": ["Offset-based", "Cursor-based"],
                    "best_practice": "Cursor-based for large, frequently changing data"
                },
            ]
        },
    }

    # Common system design interview questions
    DESIGN_QUESTIONS = [
        {
            "id": "sd_url_shortener",
            "title": "Design a URL Shortener (TinyURL)",
            "difficulty": "medium",
            "description": "Design a service that takes long URLs and creates short, unique aliases that redirect to the original URL.",
            "key_requirements": [
                "Generate short, unique URLs",
                "Redirect short URLs to original",
                "Handle high read traffic",
                "URLs should expire (optional)",
                "Analytics on clicks"
            ],
            "key_components": [
                "URL generation (Base62 encoding, hash functions)",
                "Database (key-value store, SQL)",
                "Caching (Redis for hot URLs)",
                "Load balancer",
                "Analytics service"
            ],
            "scale_considerations": [
                "100M URLs created per month",
                "Read:Write ratio ~100:1",
                "Billions of redirects per month"
            ]
        },
        {
            "id": "sd_twitter",
            "title": "Design Twitter",
            "difficulty": "hard",
            "description": "Design a social media platform where users can post tweets, follow others, and see a feed of tweets.",
            "key_requirements": [
                "Post tweets (text, images)",
                "Follow/unfollow users",
                "View home timeline (feed)",
                "View user timeline",
                "Search tweets"
            ],
            "key_components": [
                "Tweet service",
                "User service",
                "Timeline service (fan-out)",
                "Search service (Elasticsearch)",
                "Notification service",
                "Media storage (S3, CDN)"
            ],
            "scale_considerations": [
                "300M daily active users",
                "500M tweets per day",
                "Celebrity problem (millions of followers)"
            ]
        },
        {
            "id": "sd_chat",
            "title": "Design a Chat System (WhatsApp/Messenger)",
            "difficulty": "hard",
            "description": "Design a real-time messaging system supporting 1-on-1 and group chats.",
            "key_requirements": [
                "1-on-1 messaging",
                "Group chats",
                "Message delivery status (sent, delivered, read)",
                "Online/offline status",
                "Push notifications",
                "Message history"
            ],
            "key_components": [
                "WebSocket servers for real-time",
                "Message queue for async delivery",
                "Presence service",
                "Push notification service",
                "Message storage (Cassandra for write-heavy)"
            ],
            "scale_considerations": [
                "2B daily active users",
                "100B messages per day",
                "Millions of concurrent connections"
            ]
        },
        {
            "id": "sd_netflix",
            "title": "Design Netflix/Video Streaming",
            "difficulty": "hard",
            "description": "Design a video streaming service that delivers content to millions of users.",
            "key_requirements": [
                "Video upload and processing",
                "Video streaming (adaptive bitrate)",
                "User recommendations",
                "Content catalog",
                "User profiles and history"
            ],
            "key_components": [
                "Video encoding pipeline",
                "CDN for video delivery",
                "Recommendation engine",
                "Search service",
                "User service"
            ],
            "scale_considerations": [
                "200M subscribers",
                "Peak streaming load",
                "Global content delivery"
            ]
        },
        {
            "id": "sd_uber",
            "title": "Design Uber/Ride Sharing",
            "difficulty": "hard",
            "description": "Design a ride-sharing service that matches drivers with riders.",
            "key_requirements": [
                "Real-time driver location tracking",
                "Match riders with nearby drivers",
                "Trip management",
                "Pricing and payments",
                "ETA calculation"
            ],
            "key_components": [
                "Location service (geospatial indexing)",
                "Matching service",
                "Trip service",
                "Payment service",
                "Mapping/routing service"
            ],
            "scale_considerations": [
                "Millions of trips per day",
                "Real-time location updates",
                "High availability matching"
            ]
        },
        {
            "id": "sd_rate_limiter",
            "title": "Design a Rate Limiter",
            "difficulty": "medium",
            "description": "Design a system to limit the number of requests a user can make to an API.",
            "key_requirements": [
                "Limit requests per user/IP",
                "Different limits for different APIs",
                "Return informative error when limited",
                "Distributed rate limiting"
            ],
            "key_components": [
                "Token bucket or sliding window algorithm",
                "Redis for distributed state",
                "Middleware integration"
            ],
            "scale_considerations": [
                "Low latency (< 1ms decision)",
                "Millions of users",
                "Multiple API servers"
            ]
        },
        {
            "id": "sd_cache",
            "title": "Design a Distributed Cache",
            "difficulty": "medium",
            "description": "Design a distributed caching system like Memcached or Redis.",
            "key_requirements": [
                "Get/Set operations",
                "TTL support",
                "Distributed across nodes",
                "High availability"
            ],
            "key_components": [
                "Consistent hashing",
                "Replication",
                "Eviction policies (LRU)",
                "Client library with routing"
            ],
            "scale_considerations": [
                "Millions of operations per second",
                "Terabytes of data",
                "Low latency (< 1ms)"
            ]
        },
        {
            "id": "sd_notification",
            "title": "Design a Notification System",
            "difficulty": "medium",
            "description": "Design a system that sends notifications across multiple channels (push, SMS, email).",
            "key_requirements": [
                "Multi-channel (push, SMS, email)",
                "User preferences",
                "Template management",
                "Delivery tracking",
                "Rate limiting"
            ],
            "key_components": [
                "Notification service",
                "Channel adapters (APNS, FCM, Twilio)",
                "Template engine",
                "Queue for async delivery",
                "Analytics"
            ],
            "scale_considerations": [
                "Billions of notifications per day",
                "Peak traffic handling",
                "Delivery SLAs"
            ]
        },
    ]

    def __init__(self, output_dir: str = "./data/raw/system_design"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def save_all(self) -> None:
        """Save all system design content."""
        # Save topics
        topics_file = self.output_dir / "topics.json"
        with open(topics_file, "w") as f:
            json.dump(self.SYSTEM_DESIGN_TOPICS, f, indent=2)
        print(f"✅ Saved {len(self.SYSTEM_DESIGN_TOPICS)} topics to: {topics_file}")

        # Save interview questions
        questions_file = self.output_dir / "questions.json"
        with open(questions_file, "w") as f:
            json.dump(self.DESIGN_QUESTIONS, f, indent=2)
        print(f"✅ Saved {len(self.DESIGN_QUESTIONS)} questions to: {questions_file}")

        # Save combined for easy loading
        combined = {
            "topics": self.SYSTEM_DESIGN_TOPICS,
            "questions": self.DESIGN_QUESTIONS
        }
        combined_file = self.output_dir / "system_design_all.json"
        with open(combined_file, "w") as f:
            json.dump(combined, f, indent=2)
        print(f"✅ Saved combined content to: {combined_file}")

    def get_topic(self, topic_key: str) -> dict:
        """Get a specific topic by key."""
        return self.SYSTEM_DESIGN_TOPICS.get(topic_key, {})

    def get_question(self, question_id: str) -> dict:
        """Get a specific design question by ID."""
        for q in self.DESIGN_QUESTIONS:
            if q["id"] == question_id:
                return q
        return {}


if __name__ == "__main__":
    print("🧪 Testing System Design Collector\n")
    collector = SystemDesignCollector()
    collector.save_all()

    print("\n📚 Topics covered:")
    for topic in collector.SYSTEM_DESIGN_TOPICS.keys():
        print(f"   - {topic}")

    print("\n📝 Design questions:")
    for q in collector.DESIGN_QUESTIONS:
        print(f"   - {q['title']} ({q['difficulty']})")
