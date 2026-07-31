"""Tests for the marketplace subsystem (marketplace/)."""

from __future__ import annotations

import pytest

from integration.marketplace.discovery import MarketplaceDiscovery
from integration.marketplace.install import MarketplaceInstaller
from integration.marketplace.listing import MarketplaceListing
from integration.marketplace.marketplace_engine import MarketplaceEngine
from integration.marketplace.review import MarketplaceReview


class TestMarketplaceListing:
    def test_publish_get_unpublish(self) -> None:
        listing = MarketplaceListing()
        listing.publish("nexus-erp", "NEXUS ERP", "erp",
                        description="ERP do supermercado", tags=["erp", "brasil"])
        info = listing.get("nexus-erp")
        assert info["name"] == "NEXUS ERP"
        assert info["published"] is True
        assert listing.unpublish("nexus-erp") is True
        assert listing.list() == []  # unpublished hidden

    def test_missing_raises(self) -> None:
        listing = MarketplaceListing()
        with pytest.raises(KeyError):
            listing.get("missing")

    def test_installs_and_rating(self) -> None:
        listing = MarketplaceListing()
        listing.publish("pix", "Pix", "payments")
        listing.increment_installs("pix")
        listing.increment_installs("pix")
        listing.set_rating("pix", 4.5)
        assert listing.get("pix")["installs"] == 2
        assert listing.get("pix")["rating"] == 4.5


class TestMarketplaceDiscovery:
    def _make(self) -> tuple[MarketplaceListing, MarketplaceDiscovery]:
        listing = MarketplaceListing()
        listing.publish("pix", "Pix BR", "payments", tags=["pix"])
        listing.publish("stripe", "Stripe", "payments", tags=["cards"])
        listing.publish("nexus-erp", "NEXUS ERP", "erp", tags=["erp"])
        return listing, MarketplaceDiscovery(listing._listings)

    def test_search(self) -> None:
        _, discovery = self._make()
        assert len(discovery.search(query="pix")) == 1
        assert len(discovery.search(category="payments")) == 2
        assert len(discovery.search(tag="erp")) == 1
        assert discovery.by_category("erp")[0]["name"] == "NEXUS ERP"

    def test_popular(self) -> None:
        listing, discovery = self._make()
        listing.increment_installs("stripe")
        listing.increment_installs("stripe")
        listing.increment_installs("pix")
        popular = discovery.popular()
        assert popular[0]["name"] == "Stripe"


class TestMarketplaceInstaller:
    def test_install_uninstall(self) -> None:
        listing = MarketplaceListing()
        listing.publish("nexus-erp", "NEXUS ERP", "erp")
        installer = MarketplaceInstaller(listing)
        record = installer.install("nexus-erp", {"host": "erp.local"})
        assert record["status"] == "installed"
        assert record["config"] == {"host": "erp.local"}
        assert installer.is_installed("nexus-erp") is True
        assert listing.get("nexus-erp")["installs"] == 1
        assert installer.uninstall("nexus-erp") is True
        assert installer.is_installed("nexus-erp") is False

    def test_install_unpublished_raises(self) -> None:
        listing = MarketplaceListing()
        listing.publish("x", "X", "erp")
        listing.unpublish("x")
        installer = MarketplaceInstaller(listing)
        with pytest.raises(ValueError):
            installer.install("x")


class TestMarketplaceReview:
    def test_rating_average(self) -> None:
        listing = MarketplaceListing()
        listing.publish("pix", "Pix", "payments")
        review = MarketplaceReview(listing)
        review.add_review("pix", "alice", 5, "ótimo")
        review.add_review("pix", "bob", 3)
        assert review.count("pix") == 2
        assert review.average("pix") == 4.0
        assert listing.get("pix")["rating"] == 4.0
        assert review.list("pix")[0]["author"] == "alice"


class TestMarketplaceEngine:
    def test_end_to_end(self) -> None:
        engine = MarketplaceEngine()
        engine.categories.add_category("payments", "Pagamentos")
        engine.publish("pix", "Pix BR", "payments",
                       description="Receba via Pix", tags=["pix"])
        engine.publish("nexus-erp", "NEXUS ERP", "erp", tags=["erp"])
        engine.install("pix", {"tenant": "supermercado"})
        engine.rate("pix", "loja", 5, "instalação fácil")
        assert len(engine.search(category="payments")) == 1
        assert engine.search(query="erp")[0]["name"] == "NEXUS ERP"
        assert engine.installer.is_installed("pix") is True
        assert engine.reviews.average("pix") == 5.0
        stats = engine.stats()
        assert stats["listings"] == 2
        assert stats["installed"] == 1
        assert stats["categories"] == 1
