from __future__ import annotations

"""Provider library: built-in connectors for databases, cloud, payments,
communication, and business systems.

Importing this module registers every provider connector in the default
integration registry under its `connector_type`.
"""

from ..connector_registry import ConnectorRegistry

from .business.crm import CRMConnector
from .business.ecommerce import EcommerceConnector
from .business.erp import ERPConnector
from .cloud.aws import AWSConnector
from .cloud.azure import AzureConnector
from .cloud.google import GoogleCloudConnector
from .communication.email import EmailConnector
from .communication.sms import SMSConnector
from .communication.whatsapp import WhatsAppConnector
from .databases.mongodb import MongoDBConnector
from .databases.mysql import MySQLConnector
from .databases.postgresql import PostgreSQLConnector
from .databases.sqlserver import SQLServerConnector
from .payments.gateways import PaymentGatewayConnector
from .payments.pix import PixConnector
from .payments.stripe import StripeConnector

_PROVIDER_CLASSES = [
    PostgreSQLConnector,
    MySQLConnector,
    SQLServerConnector,
    MongoDBConnector,
    AWSConnector,
    AzureConnector,
    GoogleCloudConnector,
    PixConnector,
    StripeConnector,
    PaymentGatewayConnector,
    EmailConnector,
    WhatsAppConnector,
    SMSConnector,
    ERPConnector,
    CRMConnector,
    EcommerceConnector,
]


def register_all(registry: ConnectorRegistry) -> None:
    """Registers every built-in provider connector on a registry."""
    for connector_class in _PROVIDER_CLASSES:
        registry.register(connector_class.connector_type, connector_class)


def list_providers() -> list[str]:
    """Returns the connector types provided by the built-in library."""
    return sorted(connector_class.connector_type for connector_class in _PROVIDER_CLASSES)


__all__ = [
    "AWSConnector",
    "AzureConnector",
    "CRMConnector",
    "EcommerceConnector",
    "EmailConnector",
    "ERPConnector",
    "GoogleCloudConnector",
    "MongoDBConnector",
    "MySQLConnector",
    "PaymentGatewayConnector",
    "PixConnector",
    "PostgreSQLConnector",
    "SMSConnector",
    "SQLServerConnector",
    "StripeConnector",
    "WhatsAppConnector",
    "list_providers",
    "register_all",
]
