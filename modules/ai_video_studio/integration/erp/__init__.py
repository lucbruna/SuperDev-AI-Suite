"""ERP — invoice/sales/inventory/product videos and training material briefs."""
from modules.ai_video_studio.integration.erp.erp_connector import (
    ERPConnector,
    get_erp_connector,
)
from modules.ai_video_studio.integration.erp.invoice_video import (
    InvoiceVideoGenerator,
    get_invoice_video_generator,
)
from modules.ai_video_studio.integration.erp.inventory_video import (
    InventoryVideoGenerator,
    get_inventory_video_generator,
)

__all__ = [
    "ERPConnector",
    "get_erp_connector",
    "InvoiceVideoGenerator",
    "get_invoice_video_generator",
    "InventoryVideoGenerator",
    "get_inventory_video_generator",
]
