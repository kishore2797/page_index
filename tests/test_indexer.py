import unittest

from pageindex_example.indexer import PageIndexer
from pageindex_example.models import PageDocument


class PageIndexerTests(unittest.TestCase):
    def test_chunking_creates_multiple_chunks_for_long_document(self):
        text = " ".join(["word"] * 260)
        doc = PageDocument(title="Doc", url="https://example.com/doc", content=text)

        indexer = PageIndexer(chunk_size_words=100, overlap_words=20)
        chunks = indexer.chunk_document(doc)

        self.assertGreaterEqual(len(chunks), 3)
        self.assertTrue(chunks[0].chunk_id.endswith("chunk-0"))

    def test_query_returns_relevant_page_first(self):
        docs = [
            PageDocument(
                title="SEO Guide",
                url="https://example.com/seo",
                category="seo",
                content="crawl budget indexing robots sitemap canonical signals",
            ),
            PageDocument(
                title="Cooking Guide",
                url="https://example.com/cooking",
                category="food",
                content="recipes ingredients pan heat oven spices",
            ),
        ]

        indexer = PageIndexer(chunk_size_words=50, overlap_words=10)
        indexer.build(docs)
        results = indexer.query("indexing crawl budget and robots", top_k=2)

        self.assertTrue(results)
        self.assertEqual(results[0]["title"], "SEO Guide")


if __name__ == "__main__":
    unittest.main()
