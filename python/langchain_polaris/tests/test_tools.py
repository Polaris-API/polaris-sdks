import unittest
from unittest.mock import MagicMock, patch

from langchain_polaris import (
    PolarisBriefTool,
    PolarisCompareTool,
    PolarisEntityTool,
    PolarisExtractTool,
    PolarisFeedTool,
    PolarisRetriever,
    PolarisSearchTool,
)
from polaris_news.types import (
    Brief,
    ComparisonResponse,
    ExtractResponse,
    ExtractResult,
    FeedResponse,
    SearchResponse,
    Source,
    SourceAnalysis,
)


class TestPolarisSearchTool(unittest.TestCase):
    @patch("langchain_polaris.tools.PolarisClient")
    def test_run_returns_formatted_results(self, MockClient):
        mock_client = MockClient.return_value
        mock_client.search.return_value = SearchResponse(
            briefs=[Brief(headline="AI Regulation Update", confidence=0.92, bias_score=0.1, summary="New rules proposed")],
            total=1,
        )
        tool = PolarisSearchTool(api_key="test")
        result = tool._run(query="AI regulation")
        self.assertIn("AI Regulation Update", result)
        self.assertIn("0.92", result)

    @patch("langchain_polaris.tools.PolarisClient")
    def test_run_no_results(self, MockClient):
        mock_client = MockClient.return_value
        mock_client.search.return_value = SearchResponse(briefs=[], total=0)
        tool = PolarisSearchTool(api_key="test")
        result = tool._run(query="nonexistent")
        self.assertIn("No results", result)


class TestPolarisFeedTool(unittest.TestCase):
    @patch("langchain_polaris.tools.PolarisClient")
    def test_run_returns_briefs(self, MockClient):
        mock_client = MockClient.return_value
        mock_client.feed.return_value = FeedResponse(
            briefs=[Brief(headline="Breaking News", category="tech", confidence=0.88)],
            total=1,
        )
        tool = PolarisFeedTool(api_key="test")
        result = tool._run(category="tech")
        self.assertIn("Breaking News", result)
        self.assertIn("tech", result)


class TestPolarisEntityTool(unittest.TestCase):
    @patch("langchain_polaris.tools.PolarisClient")
    def test_run_returns_briefs(self, MockClient):
        mock_client = MockClient.return_value
        mock_client.entity_briefs.return_value = [
            Brief(headline="OpenAI Announces GPT-5", published_at="2026-03-13"),
        ]
        tool = PolarisEntityTool(api_key="test")
        result = tool._run(name="OpenAI")
        self.assertIn("OpenAI Announces GPT-5", result)


class TestPolarisBriefTool(unittest.TestCase):
    @patch("langchain_polaris.tools.PolarisClient")
    def test_run_returns_detail(self, MockClient):
        mock_client = MockClient.return_value
        mock_client.brief.return_value = Brief(
            headline="Detailed Brief",
            summary="A deep look",
            confidence=0.95,
            bias_score=0.05,
            sentiment="neutral",
            counter_argument="Some disagree",
            sources=[Source(name="Reuters", url="https://reuters.com")],
        )
        tool = PolarisBriefTool(api_key="test")
        result = tool._run(brief_id="abc-123")
        self.assertIn("Detailed Brief", result)
        self.assertIn("Counter-argument", result)
        self.assertIn("Reuters", result)


class TestPolarisExtractTool(unittest.TestCase):
    @patch("langchain_polaris.tools.PolarisClient")
    def test_run_returns_extracted_content(self, MockClient):
        mock_client = MockClient.return_value
        mock_client.extract.return_value = ExtractResponse(
            results=[ExtractResult(url="https://example.com", title="Test Article", text="Content here", word_count=2, success=True, domain="example.com")],
            credits_used=1,
        )
        tool = PolarisExtractTool(api_key="test")
        result = tool._run(urls="https://example.com")
        self.assertIn("Test Article", result)
        self.assertIn("Credits used: 1", result)


class TestPolarisCompareTool(unittest.TestCase):
    @patch("langchain_polaris.tools.PolarisClient")
    def test_run_returns_comparison(self, MockClient):
        mock_client = MockClient.return_value
        mock_client.search.return_value = SearchResponse(
            briefs=[Brief(id="b1", headline="AI Story")],
            total=1,
        )
        mock_client.compare_sources.return_value = ComparisonResponse(
            topic="AI regulation",
            source_analyses=[SourceAnalysis(source="Reuters", bias="center", summary="Balanced coverage")],
            polaris_analysis="Both sides agree on key points.",
        )
        tool = PolarisCompareTool(api_key="test")
        result = tool._run(topic="AI regulation")
        self.assertIn("Reuters", result)
        self.assertIn("Synthesis", result)


class TestPolarisRetriever(unittest.TestCase):
    @patch("langchain_polaris.retrievers.PolarisClient")
    def test_returns_documents(self, MockClient):
        mock_client = MockClient.return_value
        mock_client.search.return_value = SearchResponse(
            briefs=[Brief(
                id="doc1",
                headline="AI Brief",
                summary="Summary text",
                body="Full body text",
                confidence=0.9,
                bias_score=0.1,
                category="ai_ml",
                published_at="2026-03-13",
                counter_argument="Some disagree",
                sources=[Source(name="Reuters", url="https://reuters.com")],
            )],
            total=1,
        )
        retriever = PolarisRetriever(api_key="test", limit=5)
        docs = retriever._get_relevant_documents("AI")
        self.assertEqual(len(docs), 1)
        self.assertIn("AI Brief", docs[0].page_content)
        self.assertIn("Summary text", docs[0].page_content)
        self.assertEqual(docs[0].metadata["brief_id"], "doc1")
        self.assertEqual(docs[0].metadata["confidence"], 0.9)
        self.assertEqual(docs[0].metadata["sources"][0]["name"], "Reuters")


if __name__ == "__main__":
    unittest.main()
