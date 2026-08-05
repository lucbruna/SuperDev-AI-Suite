"""ERP Connector — facade over the ERP generators."""
from __future__ import annotations


from modules.ai_video_studio.integration.connector_base import DomainConnector
from modules.ai_video_studio.integration.erp.inventory_video import (
    get_inventory_video_generator,
)
from modules.ai_video_studio.integration.erp.invoice_video import (
    get_invoice_video_generator,
)
from modules.ai_video_studio.integration.erp.product_catalog_video import (
    get_product_catalog_video_generator,
)
from modules.ai_video_studio.integration.erp.sales_dashboard_video import (
    get_sales_dashboard_video_generator,
)
from modules.ai_video_studio.integration.erp.training_material import (
    get_training_material_generator,
)


class ERPConnector(DomainConnector):
    """Generates ERP-domain video briefs."""

    domain = "erp"
    description = "Invoice, sales dashboard, inventory, product catalog and training videos"

    def __init__(self) -> None:
        super().__init__()
        self._register("invoice_video", lambda d: get_invoice_video_generator().generate(**d))
        self._register("sales_dashboard_video", lambda d: get_sales_dashboard_video_generator().generate(**d))
        self._register("inventory_video", lambda d: get_inventory_video_generator().generate(**d))
        self._register("product_catalog_video", lambda d: get_product_catalog_video_generator().generate(**d))
        self._register("training_material", lambda d: get_training_material_generator().generate(**d))


_erp_connector: ERPConnector | None = None


def get_erp_connector() -> ERPConnector:
    global _erp_connector
    if _erp_connector is None:
        _erp_connector = ERPConnector()
    return _erp_connector
