import logging
from Bio import Entrez, Medline
from app.config import get_settings

logger = logging.getLogger(__name__)


class PubMedFetcher:
    def __init__(self):
        settings = get_settings()
        Entrez.email = settings.pubmed_email

    def search(self, query: str, max_results: int = 10) -> list[dict]:
        logger.info(f"Searching PubMed for: {query} (max {max_results})")

        handle = Entrez.esearch(
            db="pubmed", term=query, retmax=max_results, sort="relevance"
        )
        results = Entrez.read(handle)
        handle.close()

        pmids = results.get("IdList", [])
        if not pmids:
            logger.info("No results found")
            return []

        logger.info(f"Found {len(pmids)} articles, fetching details...")
        return self._fetch_details(pmids)

    def _fetch_details(self, pmids: list[str]) -> list[dict]:
        handle = Entrez.efetch(
            db="pubmed", id=pmids, rettype="medline", retmode="text"
        )
        records = Medline.parse(handle)

        articles = []
        for record in records:
            article = {
                "pmid": record.get("PMID", ""),
                "title": record.get("TI", ""),
                "abstract": record.get("AB", ""),
                "authors": record.get("AU", []),
                "journal": record.get("JT", ""),
                "year": self._extract_year(record.get("DP", "")),
                "mesh_terms": record.get("MH", []),
                "doi": self._extract_doi(record.get("AID", [])),
                "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{record.get('PMID', '')}/",
            }
            if article["abstract"]:
                articles.append(article)

        handle.close()
        logger.info(f"Fetched {len(articles)} articles with abstracts")
        return articles

    def _extract_year(self, date_str: str) -> int:
        try:
            return int(date_str[:4])
        except (ValueError, IndexError):
            return 0

    def _extract_doi(self, aid_list: list[str]) -> str:
        for aid in aid_list:
            if aid.endswith("[doi]"):
                return aid.replace(" [doi]", "")
        return ""
