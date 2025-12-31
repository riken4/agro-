# Agro E-Commerce Platform 🌾

A comprehensive multi-vendor agricultural e-commerce platform built with Django that connects farmers, vendors, and customers in a seamless marketplace ecosystem.

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [User Roles](#user-roles)
- [Platform Flow](#platform-flow)
- [Core Models](#core-models)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)

## 🎯 Overview

This platform revolutionizes the agricultural supply chain by creating a digital marketplace where:
- **Farmers** can list their fresh produce directly
- **Vendors** can source products from farmers and sell to customers
- **Customers** can purchase fresh agricultural products
- **Admin** oversees the entire ecosystem with commission-based revenue

## ✨ Key Features

### For Farmers
- ✅ KYC verification (PAN, Citizenship documents)
- 📦 Product listing with quality grades (A, B, C)
- 💰 Digital wallet system
- 📊 Inventory management
- 💸 Payout request system
- 📱 QR code for payments

### For Vendors
- ✅ Shop verification with KYC
- 🛒 Product selection from farmer warehouse
- 💵 Dynamic pricing control
- 📦 Delivery tracking
- 💰 Wallet and payout system
- 🏪 Shop branding (logo, description)

### For Customers
- 🛍️ Browse products by category
- 🛒 Shopping cart functionality
- 📦 Order tracking
- ⭐ Product reviews and ratings
- 💳 Cash on Delivery payment
- 📍 Province-based delivery

### For Admin
- 👥 User and role management
- ✅ Vendor/Farmer verification
- 💰 Commission rate configuration
- 💸 Payout approval system
- 📊 Admin wallet management
- 📝 Audit logging
- 🔔 Notification management

## 🏗️ System Architecture

```
┌─────────────┐
│   FARMER    │
│  (Producer) │
└──────┬──────┘
       │
       │ Lists Products
       │ (with quality & quantity)
       ▼
┌─────────────────┐
│ FARMER PRODUCTS │
│  (Warehouse)    │
└────────┬────────┘
         │
         │ Vendors Select
         │ (set selling price)
         ▼
┌─────────────────┐
│ VENDOR PRODUCTS │
│  (Shop Stock)   │
└────────┬────────┘
         │
         │ Customers Buy
         ▼
┌─────────────────┐
│     ORDERS      │
└────────┬────────┘
         │
         │ Payment Split
         ▼
┌──────────────────────────┐
│  Farmer Wallet (47.5%)   │
│  Vendor Wallet (47.5%)   │
│  Admin Wallet (5%)       │
└──────────────────────────┘
```

## 👥 User Roles

### 1. **Customer**
- Regular shoppers who purchase products
- Can browse, add to cart, place orders
- Track orders and leave reviews

### 2. **Farmer**
- Primary producers of agricultural products
- Upload products with details (quality, quantity, price)
- Manage inventory and track selections
- Request payouts from earnings

### 3. **Vendor**
- Middlemen who source from farmers
- Select products from farmer warehouse
- Set retail prices for customers
- Manage shop and deliveries

### 4. **Admin**
- Platform administrators
- Verify farmers and vendors
- Approve payout requests
- Configure commission rates
- Monitor all activities

## 🔄 Platform Flow

### 1️⃣ Registration & Verification Flow

```
User Signs Up → Selects Role → Fills Profile
                                     │
                    ┌────────────────┼────────────────┐
                    ▼                ▼                ▼
                 Farmer           Vendor          Customer
                    │                │                │
            Submit KYC Docs   Submit KYC Docs    Ready to Shop
                    │                │
            Admin Verifies    Admin Verifies
                    │                │
            Status: Verified  Status: Verified
                    │                │
            Wallet Created    Wallet Created
```

### 2️⃣ Product Listing Flow

```
Farmer Lists Product
    │
    ├─ Product Name
    ├─ Category
    ├─ Quality Grade (A/B/C)
    ├─ Quantity (kg)
    ├─ Base Price
    ├─ Harvest Date
    ├─ Expiry Date
    └─ Product Image
    │
    ▼
Product in Warehouse
(Status: Pending)
    │
    ▼
Available for Vendor Selection
```

### 3️⃣ Vendor Selection Flow

```
Vendor Views Warehouse
    │
    ▼
Selects Product
    │
    ├─ Chooses Quantity
    └─ Sets Selling Price
    │
    ▼
Farmer Product Updated
(Available Quantity Reduced)
    │
    ▼
Vendor Product Created
(Status: Selected)
    │
    ▼
Delivery Process
    │
    ├─ In Transit
    ▼
Delivered to Vendor Shop
    │
    ▼
Available for Customers
```

### 4️⃣ Customer Purchase Flow

```
Customer Browses Products
    │
    ▼
Adds to Cart
    │
    ▼
Proceeds to Checkout
    │
    ├─ Shipping Details
    │   ├─ Full Name
    │   ├─ Phone
    │   ├─ Address
    │   ├─ City
    │   └─ Province
    │
    └─ Payment Method (COD)
    │
    ▼
Order Created
(Status: Pending)
    │
    ▼
Order Processing
    │
    ├─ Processing
    ├─ Shipped
    ▼
Delivered
    │
    ▼
Customer Pays (COD)
    │
    ▼
Payment Split Triggered
```

### 5️⃣ Payment Split Flow

```
Order Delivered + Paid
    │
    ▼
Calculate Commission (5%)
    │
    ├─ Farmer Commission: 2.5%
    ├─ Vendor Commission: 2.5%
    └─ Total Commission: 5%
    │
    ▼
Split Amounts
    │
    ├─ Farmer Gets: (Base Price × Quantity) - 2.5%
    ├─ Vendor Gets: (Profit) - 2.5%
    └─ Admin Gets: Total 5% Commission
    │
    ▼
Credit to Respective Wallets
    │
    ├─ Farmer Wallet ✓
    ├─ Vendor Wallet ✓
    └─ Admin Wallet ✓
```

### 6️⃣ Payout Request Flow

```
Farmer/Vendor Requests Payout
    │
    ├─ Requests Amount
    └─ Checks Wallet Balance
    │
    ▼
Payout Request Created
(Status: Pending)
    │
    ▼
Admin Receives Notification
    │
    ▼
Admin Reviews Request
    │
    ├─ Approves → Status: Approved
    │              │
    │              ▼
    │         Admin Pays
    │              │
    │              ▼
    │         Status: Paid
    │              │
    │              ▼
    │         Wallet Debited
    │
    └─ Rejects → Status: Rejected
                 (With Reason)
```

## 🗄️ Core Models

### User Management
- **UserRole**: Manages user roles (Customer, Vendor, Farmer, Admin)
- **UserProfile**: Extended user information with location and avatar
- **OTPVerification**: Email verification system

### Farmer System
- **Farmer**: Farmer profile with KYC and verification
- **FarmerProduct**: Products listed by farmers (warehouse stock)
- **FarmerWallet**: Digital wallet for earnings
- **FarmerPayoutRequest**: Withdrawal requests

### Vendor System
- **Vendor**: Vendor shop profile with KYC
- **VendorProduct**: Products selected from farmers
- **VendorWallet**: Digital wallet for earnings
- **VendorPayoutRequest**: Withdrawal requests

### Order System
- **Order**: Customer orders with shipping details
- **OrderItems**: Individual items in an order
- **Cart**: Shopping cart for customers

### Platform Management
- **Category**: Product categorization
- **CommissionRate**: Platform commission configuration
- **AdminWallet**: Admin earnings from commissions
- **Review**: Customer product reviews
- **Notification**: In-app notification system
- **AuditLog**: Activity tracking and logging
- **Organization**: Platform information

## 🚀 Installation

### Prerequisites
- Python 3.8+
- Django 4.0+
- PostgreSQL/MySQL (recommended) or SQLite

### Steps

1. **Clone the repository**
```bash
git clone <repository-url>
cd agro-ecommerce
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure database**
Edit `settings.py` with your database credentials

5. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create superuser**
```bash
python manage.py createsuperuser
```

7. **Create initial data**
```bash
# Create commission rate
python manage.py shell
>>> from yourapp.models import CommissionRate
>>> CommissionRate.objects.create(rate=5.00)
>>> exit()
```

8. **Run development server**
```bash
python manage.py runserver
```

## ⚙️ Configuration

### Commission Rate
- Default: 5% (2.5% from farmer, 2.5% from vendor)
- Configurable via Admin panel

### Quality Grades
- **Grade A**: Premium quality
- **Grade B**: Standard quality
- **Grade C**: Economy quality

### Provinces (Nepal)
- Koshi Province
- Madhesh Province
- Bagmati Province
- Gandaki Province
- Lumbini Province
- Karnali Province
- Sudurpashchim Province

### Payment Methods
- Currently supports: Cash on Delivery (COD)
- Payment Status: Unpaid, Paid, Failed

### Delivery Statuses
- Pending → Selected → In Transit → Delivered → Cancelled

## 📱 Usage

### For Farmers
1. Register and complete KYC verification
2. Wait for admin approval
3. List products with details
4. Track vendor selections
5. Monitor wallet balance
6. Request payouts when needed

### For Vendors
1. Register and complete KYC verification
2. Wait for admin approval
3. Browse farmer warehouse
4. Select products and set prices
5. Manage delivery status
6. Track sales and earnings
7. Request payouts

### For Customers
1. Register as customer
2. Browse products by category
3. Add items to cart
4. Checkout with shipping details
5. Track order status
6. Leave reviews after delivery

### For Admin
1. Access admin panel
2. Verify farmer/vendor applications
3. Monitor all transactions
4. Approve payout requests
5. Configure commission rates
6. View audit logs and analytics

## 🔔 Notification System

Automated notifications for:
- Product selection by vendors
- Payout request updates
- Order status changes
- Delivery updates
- Admin approvals/rejections

## 📊 Financial Model

### Revenue Distribution (Per Order)

```
Total Sale Amount: Rs. 1000
├─ Farmer Base Amount: Rs. 600
│  ├─ Farmer Gets: Rs. 585 (97.5% of base)
│  └─ Commission: Rs. 15 (2.5%)
│
├─ Vendor Profit: Rs. 400
│  ├─ Vendor Gets: Rs. 390 (97.5% of profit)
│  └─ Commission: Rs. 10 (2.5%)
│
└─ Admin Commission: Rs. 25 (Total 2.5% from both)
```

## 🔐 Security Features

- KYC verification for farmers and vendors
- Document upload for verification
- Admin approval workflow
- OTP verification for email
- Secure wallet transactions
- Audit logging for all actions
- IP address tracking

## 📈 Future Enhancements

- [ ] Online payment integration (eSewa, Khalti)
- [ ] Real-time chat between users
- [ ] Advanced analytics dashboard
- [ ] Mobile application
- [ ] Multi-language support
- [ ] AI-based price recommendations
- [ ] Weather-based farming tips
- [ ] Logistics partner integration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support, email support@agroecommerce.com or create an issue in the repository.

---

**Built with ❤️ for farmers and agricultural communities**