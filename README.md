# SANOVIO Procurement Request Management System

A modern, AI-powered procurement request management system built for the SANOVIO challenge. This application streamlines the procurement process by enabling users to create, submit, and manage procurement requests with intelligent document extraction and automatic commodity group classification.

![Procurement System](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Next.js](https://img.shields.io/badge/Next.js-16-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)

## 🚀 Features

### 1. Intake Form

- **Complete Request Submission**: All required fields including requestor name, title, vendor info, VAT ID, order lines, and department
- **Dynamic Order Lines**: Add/remove multiple order line items with automatic total calculation
- **Real-time Validation**: Form validation with clear error messages
- **Department Selection**: Pre-populated department list for easy selection

### 2. AI-Powered Document Extraction

- **Upload Vendor Offers**: Drag & drop or click to upload vendor offer documents (TXT, PDF, DOC, DOCX)
- **Automatic Data Extraction**: Uses OpenAI GPT-4o to extract:
  - Vendor name and VAT ID
  - Department information
  - Order lines with descriptions, prices, quantities
  - Total cost calculation
- **Confidence Scoring**: Shows extraction confidence level

### 3. Smart Commodity Group Suggestion

- **AI-Powered Classification**: Automatically suggests the most appropriate commodity group based on request content
- **50 Commodity Groups**: Organized across 7 categories (General Services, Facility Management, Publishing Production, IT, Logistics, Marketing & Advertising, Production)
- **Reasoning Display**: Shows why the AI selected a particular commodity group

### 4. Request Overview Dashboard

- **Real-time Statistics**: View counts of Open, In Progress, and Closed requests
- **Filterable Table**: All requests displayed with key information
- **Quick Actions**: Update status and view history directly from the table

### 5. Status Tracking & History

- **Three Status Levels**: Open → In Progress → Closed
- **Complete Audit Trail**: Every status change is recorded with:
  - Timestamp
  - Who made the change
  - Optional notes
- **History Modal**: View the complete status history for any request

## 🛠️ Tech Stack

### Backend

- **FastAPI** - Modern Python web framework
- **MongoDB** - NoSQL database for flexible document storage
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation using Python type hints
- **OpenAI GPT-4o** - AI-powered document extraction and classification

### Frontend

- **Next.js 16** - React framework with Turbopack
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Custom Design System** - Dark theme with teal accents

## 📦 Installation

### Prerequisites

- Python 3.12+
- Node.js 18+
- MongoDB (Atlas or local)
- OpenAI API Key (for AI features)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables (create .env file)
export MONGODB_URI="your_mongodb_uri"
export OPENAI_API_KEY="your_openai_api_key"

# Run the server
uvicorn main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend/my-app

# Install dependencies
npm install

# Run development server
npm run dev
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# MongoDB Configuration
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?appName=App
MONGODB_DB_NAME=procurement_db

# OpenAI Configuration (Required for AI features)
OPENAI_API_KEY=sk-your-openai-api-key
```

## 🌐 API Endpoints

### Health & Info

- `GET /` - API info
- `GET /api/health` - Health check with status of DB and OpenAI

### Commodity Groups & Departments

- `GET /api/commodity-groups` - List all 50 commodity groups
- `GET /api/departments` - List all departments

### Procurement Requests

- `POST /api/requests` - Create new request
- `GET /api/requests` - List all requests (with optional status/department filters)
- `GET /api/requests/{id}` - Get specific request
- `PATCH /api/requests/{id}` - Update request details
- `PATCH /api/requests/{id}/status` - Update request status
- `GET /api/requests/{id}/history` - Get status history
- `DELETE /api/requests/{id}` - Delete request

### AI Features

- `POST /api/extract-document` - Extract data from uploaded document
- `POST /api/suggest-commodity-group` - AI suggest commodity group

### Statistics

- `GET /api/stats` - Get request statistics by status

## 📁 Project Structure

```
Procurement app/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── venv/                # Python virtual environment
├── frontend/
│   └── my-app/
│       ├── app/
│       │   ├── page.tsx     # Main application component
│       │   ├── layout.tsx   # Root layout
│       │   └── globals.css  # Global styles & design system
│       └── package.json     # Node.js dependencies
├── sample_vendor_offer.txt  # Example vendor offer for testing
└── README.md
```

## 🧪 Testing the AI Features

### Sample Vendor Offer

A sample vendor offer is included (`sample_vendor_offer.txt`) for testing the document extraction feature:

```text
Vendor Name: Global Tech Solutions
Umsatzsteuer-Identifikationsnummer (VAT ID): DE987654321
Offer Date: March 23, 2024

Offered to: Creative Marketing Department

Items Offered:
1. Product: Adobe Photoshop License
   Unit Price: €150
   Quantity: 10
   Total: €1500

2. Product: Adobe Illustrator License
   Unit Price: €120
   Quantity: 5
   Total: €600

Total Offer Cost: €2100
```

### Expected Extraction Results

- **Vendor Name**: Global Tech Solutions
- **VAT ID**: DE987654321
- **Department**: Creative Marketing Department
- **Order Lines**: 2 items with full details
- **Total Cost**: €2100
- **Suggested Commodity Group**: 031 - Software (Information Technology)

## 🎨 Design Highlights

- **Dark Theme**: Sophisticated dark interface with teal accent colors
- **Glassmorphism**: Subtle blur effects and transparency
- **Smooth Animations**: Fade-in, slide-in, and staggered animations
- **Responsive Design**: Works on desktop and tablet
- **Accessibility**: Proper focus states and keyboard navigation

## 📊 Commodity Groups

The system includes 50 commodity groups across 7 categories:

| Category                | Examples                              |
| ----------------------- | ------------------------------------- |
| General Services        | Consulting, Insurance, Recruitment    |
| Facility Management     | Security, Maintenance, Cleaning       |
| Publishing Production   | Printing, Audio/Visual Production     |
| Information Technology  | Hardware, Software, IT Services       |
| Logistics               | Courier Services, Warehousing         |
| Marketing & Advertising | Events, Online Marketing, Advertising |
| Production              | Machinery, Spare Parts, Materials     |

## 🔒 Validation Rules

- All required fields must be completed
- VAT ID format should follow German Umsatzsteuer-ID pattern
- Order lines must have:
  - Description (required)
  - Unit price > 0
  - Amount ≥ 1
- Total cost must match sum of order line totals

## 🚀 Deployment

### Local Deployment (Current)

The application is configured for local deployment:

- Backend: http://localhost:8000
- Frontend: http://localhost:3000

### Production Considerations

- Configure CORS for production domains
- Use environment variables for all sensitive data
- Set up proper MongoDB authentication
- Enable HTTPS/TLS

## 📝 License

This project was built for the SANOVIO coding challenge.

## 🙏 Acknowledgments

- OpenAI for GPT-4o API
- MongoDB Atlas for database hosting
- Vercel for Next.js framework
