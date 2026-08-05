class Product {
  final int id;
  final String name;
  final String? sku;
  final String? description;
  final double price;
  final double? costPrice;
  final int stockQuantity;
  final String? category;
  final String? imageUrl;
  final bool isActive;
  final DateTime createdAt;

  Product({
    required this.id,
    required this.name,
    this.sku,
    this.description,
    required this.price,
    this.costPrice,
    this.stockQuantity = 0,
    this.category,
    this.imageUrl,
    this.isActive = true,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      id: json['id'] as int,
      name: json['name'] as String? ?? '',
      sku: json['sku'] as String?,
      description: json['description'] as String?,
      price: (json['price'] as num?)?.toDouble() ?? 0.0,
      costPrice: (json['cost_price'] as num?)?.toDouble() ?? (json['costPrice'] as num?)?.toDouble(),
      stockQuantity: json['stock_quantity'] as int? ?? json['stockQuantity'] as int? ?? 0,
      category: json['category'] as String?,
      imageUrl: json['image_url'] as String? ?? json['imageUrl'] as String?,
      isActive: json['is_active'] as bool? ?? json['isActive'] as bool? ?? true,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'sku': sku,
      'description': description,
      'price': price,
      'cost_price': costPrice,
      'stock_quantity': stockQuantity,
      'category': category,
      'image_url': imageUrl,
      'is_active': isActive,
    };
  }
}

class SaleOrder {
  final int id;
  final String orderNumber;
  final List<SaleItem> items;
  final double totalAmount;
  final double? discountAmount;
  final double? taxAmount;
  final String status;
  final String? paymentMethod;
  final String? customerName;
  final DateTime createdAt;

  SaleOrder({
    required this.id,
    required this.orderNumber,
    this.items = const [],
    required this.totalAmount,
    this.discountAmount,
    this.taxAmount,
    this.status = 'pending',
    this.paymentMethod,
    this.customerName,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory SaleOrder.fromJson(Map<String, dynamic> json) {
    return SaleOrder(
      id: json['id'] as int,
      orderNumber: json['order_number'] as String? ?? json['orderNumber'] as String? ?? '',
      items: (json['items'] as List<dynamic>?)
              ?.map((e) => SaleItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      totalAmount: (json['total_amount'] as num?)?.toDouble() ?? (json['totalAmount'] as num?)?.toDouble() ?? 0.0,
      discountAmount: (json['discount_amount'] as num?)?.toDouble() ?? (json['discountAmount'] as num?)?.toDouble(),
      taxAmount: (json['tax_amount'] as num?)?.toDouble() ?? (json['taxAmount'] as num?)?.toDouble(),
      status: json['status'] as String? ?? 'pending',
      paymentMethod: json['payment_method'] as String? ?? json['paymentMethod'] as String?,
      customerName: json['customer_name'] as String? ?? json['customerName'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'order_number': orderNumber,
      'items': items.map((e) => e.toJson()).toList(),
      'total_amount': totalAmount,
      'discount_amount': discountAmount,
      'tax_amount': taxAmount,
      'status': status,
      'payment_method': paymentMethod,
      'customer_name': customerName,
    };
  }
}

class SaleItem {
  final int productId;
  final String productName;
  final int quantity;
  final double unitPrice;
  final double subtotal;

  SaleItem({
    required this.productId,
    required this.productName,
    required this.quantity,
    required this.unitPrice,
    required this.subtotal,
  });

  factory SaleItem.fromJson(Map<String, dynamic> json) {
    return SaleItem(
      productId: json['product_id'] as int? ?? json['productId'] as int? ?? 0,
      productName: json['product_name'] as String? ?? json['productName'] as String? ?? '',
      quantity: json['quantity'] as int? ?? 1,
      unitPrice: (json['unit_price'] as num?)?.toDouble() ?? (json['unitPrice'] as num?)?.toDouble() ?? 0.0,
      subtotal: (json['subtotal'] as num?)?.toDouble() ?? 0.0,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'product_id': productId,
      'product_name': productName,
      'quantity': quantity,
      'unit_price': unitPrice,
      'subtotal': subtotal,
    };
  }
}

class Lead {
  final int id;
  final String name;
  final String? email;
  final String? phone;
  final String? company;
  final String? source;
  final String status;
  final double? estimatedValue;
  final String? notes;
  final String? assignedTo;
  final DateTime createdAt;

  Lead({
    required this.id,
    required this.name,
    this.email,
    this.phone,
    this.company,
    this.source,
    this.status = 'new',
    this.estimatedValue,
    this.notes,
    this.assignedTo,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory Lead.fromJson(Map<String, dynamic> json) {
    return Lead(
      id: json['id'] as int,
      name: json['name'] as String? ?? '',
      email: json['email'] as String?,
      phone: json['phone'] as String?,
      company: json['company'] as String?,
      source: json['source'] as String?,
      status: json['status'] as String? ?? 'new',
      estimatedValue: (json['estimated_value'] as num?)?.toDouble() ?? (json['estimatedValue'] as num?)?.toDouble(),
      notes: json['notes'] as String?,
      assignedTo: json['assigned_to'] as String? ?? json['assignedTo'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'email': email,
      'phone': phone,
      'company': company,
      'source': source,
      'status': status,
      'estimated_value': estimatedValue,
      'notes': notes,
      'assigned_to': assignedTo,
    };
  }
}

class Opportunity {
  final int id;
  final String title;
  final String? description;
  final double? value;
  final String stage;
  final double? probability;
  final DateTime? expectedCloseDate;
  final String? leadName;
  final String? assignedTo;
  final DateTime createdAt;

  Opportunity({
    required this.id,
    required this.title,
    this.description,
    this.value,
    this.stage = 'prospecting',
    this.probability,
    this.expectedCloseDate,
    this.leadName,
    this.assignedTo,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory Opportunity.fromJson(Map<String, dynamic> json) {
    return Opportunity(
      id: json['id'] as int,
      title: json['title'] as String? ?? '',
      description: json['description'] as String?,
      value: (json['value'] as num?)?.toDouble(),
      stage: json['stage'] as String? ?? 'prospecting',
      probability: (json['probability'] as num?)?.toDouble(),
      expectedCloseDate: json['expected_close_date'] != null
          ? DateTime.parse(json['expected_close_date'] as String)
          : null,
      leadName: json['lead_name'] as String? ?? json['leadName'] as String?,
      assignedTo: json['assigned_to'] as String? ?? json['assignedTo'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'title': title,
      'description': description,
      'value': value,
      'stage': stage,
      'probability': probability,
      'expected_close_date': expectedCloseDate?.toIso8601String(),
      'lead_name': leadName,
      'assigned_to': assignedTo,
    };
  }
}

class Invoice {
  final int id;
  final String invoiceNumber;
  final int? saleOrderId;
  final double amount;
  final double? paidAmount;
  final double? dueAmount;
  final String status;
  final String? customerName;
  final DateTime issueDate;
  final DateTime? dueDate;
  final DateTime? paidAt;

  Invoice({
    required this.id,
    required this.invoiceNumber,
    this.saleOrderId,
    required this.amount,
    this.paidAmount,
    this.dueAmount,
    this.status = 'pending',
    this.customerName,
    DateTime? issueDate,
    this.dueDate,
    this.paidAt,
  }) : issueDate = issueDate ?? DateTime.now();

  factory Invoice.fromJson(Map<String, dynamic> json) {
    return Invoice(
      id: json['id'] as int,
      invoiceNumber: json['invoice_number'] as String? ?? json['invoiceNumber'] as String? ?? '',
      saleOrderId: json['sale_order_id'] as int? ?? json['saleOrderId'] as int?,
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      paidAmount: (json['paid_amount'] as num?)?.toDouble() ?? (json['paidAmount'] as num?)?.toDouble(),
      dueAmount: (json['due_amount'] as num?)?.toDouble() ?? (json['dueAmount'] as num?)?.toDouble(),
      status: json['status'] as String? ?? 'pending',
      customerName: json['customer_name'] as String? ?? json['customerName'] as String?,
      issueDate: json['issue_date'] != null
          ? DateTime.parse(json['issue_date'] as String)
          : DateTime.now(),
      dueDate: json['due_date'] != null
          ? DateTime.parse(json['due_date'] as String)
          : null,
      paidAt: json['paid_at'] != null
          ? DateTime.parse(json['paid_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'invoice_number': invoiceNumber,
      'sale_order_id': saleOrderId,
      'amount': amount,
      'paid_amount': paidAmount,
      'status': status,
      'customer_name': customerName,
      'issue_date': issueDate.toIso8601String(),
      'due_date': dueDate?.toIso8601String(),
    };
  }
}

class StockItem {
  final int id;
  final String productName;
  final String? sku;
  final int currentQuantity;
  final int? minimumQuantity;
  final int? maximumQuantity;
  final String? location;
  final DateTime lastUpdated;

  StockItem({
    required this.id,
    required this.productName,
    this.sku,
    required this.currentQuantity,
    this.minimumQuantity,
    this.maximumQuantity,
    this.location,
    DateTime? lastUpdated,
  }) : lastUpdated = lastUpdated ?? DateTime.now();

  bool get isLowStock => minimumQuantity != null && currentQuantity <= minimumQuantity!;

  factory StockItem.fromJson(Map<String, dynamic> json) {
    return StockItem(
      id: json['id'] as int,
      productName: json['product_name'] as String? ?? json['productName'] as String? ?? '',
      sku: json['sku'] as String?,
      currentQuantity: json['current_quantity'] as int? ?? json['currentQuantity'] as int? ?? 0,
      minimumQuantity: json['minimum_quantity'] as int? ?? json['minimumQuantity'] as int?,
      maximumQuantity: json['maximum_quantity'] as int? ?? json['maximumQuantity'] as int?,
      location: json['location'] as String?,
      lastUpdated: json['last_updated'] != null
          ? DateTime.parse(json['last_updated'] as String)
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'product_name': productName,
      'sku': sku,
      'current_quantity': currentQuantity,
      'minimum_quantity': minimumQuantity,
      'maximum_quantity': maximumQuantity,
      'location': location,
    };
  }
}

class StockMovement {
  final int id;
  final int productId;
  final String productName;
  final String type;
  final int quantity;
  final String? reason;
  final String? reference;
  final DateTime createdAt;

  StockMovement({
    required this.id,
    required this.productId,
    required this.productName,
    required this.type,
    required this.quantity,
    this.reason,
    this.reference,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? DateTime.now();

  factory StockMovement.fromJson(Map<String, dynamic> json) {
    return StockMovement(
      id: json['id'] as int,
      productId: json['product_id'] as int? ?? json['productId'] as int? ?? 0,
      productName: json['product_name'] as String? ?? json['productName'] as String? ?? '',
      type: json['type'] as String? ?? 'in',
      quantity: json['quantity'] as int? ?? 0,
      reason: json['reason'] as String?,
      reference: json['reference'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'product_id': productId,
      'type': type,
      'quantity': quantity,
      'reason': reason,
      'reference': reference,
    };
  }
}

class CashRegister {
  final int id;
  final String name;
  final double balance;
  final String? location;
  final bool isOpen;
  final double? openingBalance;
  final DateTime? openedAt;
  final DateTime? closedAt;

  CashRegister({
    required this.id,
    required this.name,
    this.balance = 0.0,
    this.location,
    this.isOpen = false,
    this.openingBalance,
    this.openedAt,
    this.closedAt,
  });

  factory CashRegister.fromJson(Map<String, dynamic> json) {
    return CashRegister(
      id: json['id'] as int,
      name: json['name'] as String? ?? '',
      balance: (json['balance'] as num?)?.toDouble() ?? 0.0,
      location: json['location'] as String?,
      isOpen: json['is_open'] as bool? ?? json['isOpen'] as bool? ?? false,
      openingBalance: (json['opening_balance'] as num?)?.toDouble() ?? (json['openingBalance'] as num?)?.toDouble(),
      openedAt: json['opened_at'] != null
          ? DateTime.parse(json['opened_at'] as String)
          : null,
      closedAt: json['closed_at'] != null
          ? DateTime.parse(json['closed_at'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'balance': balance,
      'location': location,
      'is_open': isOpen,
      'opening_balance': openingBalance,
    };
  }
}

class PaymentRecord {
  final int id;
  final int invoiceId;
  final double amount;
  final String method;
  final String? reference;
  final DateTime paidAt;

  PaymentRecord({
    required this.id,
    required this.invoiceId,
    required this.amount,
    required this.method,
    this.reference,
    DateTime? paidAt,
  }) : paidAt = paidAt ?? DateTime.now();

  factory PaymentRecord.fromJson(Map<String, dynamic> json) {
    return PaymentRecord(
      id: json['id'] as int,
      invoiceId: json['invoice_id'] as int? ?? json['invoiceId'] as int? ?? 0,
      amount: (json['amount'] as num?)?.toDouble() ?? 0.0,
      method: json['method'] as String? ?? 'cash',
      reference: json['reference'] as String?,
      paidAt: json['paid_at'] != null
          ? DateTime.parse(json['paid_at'] as String)
          : DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'invoice_id': invoiceId,
      'amount': amount,
      'method': method,
      'reference': reference,
    };
  }
}

class PipelineStage {
  final String name;
  final List<Opportunity> opportunities;
  final double totalValue;

  PipelineStage({
    required this.name,
    this.opportunities = const [],
    this.totalValue = 0.0,
  });

  factory PipelineStage.fromJson(Map<String, dynamic> json) {
    return PipelineStage(
      name: json['name'] as String? ?? '',
      opportunities: (json['opportunities'] as List<dynamic>?)
              ?.map((e) => Opportunity.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      totalValue: (json['total_value'] as num?)?.toDouble() ?? (json['totalValue'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class CashFlowEntry {
  final DateTime date;
  final double inflow;
  final double outflow;
  final double balance;

  CashFlowEntry({
    required this.date,
    this.inflow = 0.0,
    this.outflow = 0.0,
    this.balance = 0.0,
  });

  factory CashFlowEntry.fromJson(Map<String, dynamic> json) {
    return CashFlowEntry(
      date: DateTime.parse(json['date'] as String),
      inflow: (json['inflow'] as num?)?.toDouble() ?? 0.0,
      outflow: (json['outflow'] as num?)?.toDouble() ?? 0.0,
      balance: (json['balance'] as num?)?.toDouble() ?? 0.0,
    );
  }
}
