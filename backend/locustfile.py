import random
from locust import HttpUser, task, between


SEARCH_QUERIES = [
    "what is machine learning",
    "what is deep learning",
    "what is natural language processing",
    "explain neural networks",
    "what is supervised learning",
    "what is unsupervised learning",
    "what is reinforcement learning",
    "what is overfitting",
    "what is cross validation",
    "what is gradient descent",
    "what is backpropagation",
    "what is transformer model",
    "what is attention mechanism",
    "difference between AI and ML",
    "what is word embeddings",
]


class APIUser(HttpUser):
    wait_time = between(1, 2)

    @task(3)
    def call_search(self):
        query = random.choice(SEARCH_QUERIES)

        params = {
            "query": query,
        }

        self.client.get("/search", params=params)

    @task(1)
    def call_root(self):
        self.client.get("/")
