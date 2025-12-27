# SkillBridge - Skill-Based Service Exchange Platform

A fully functional web application built with **HTML/CSS/Bootstrap** frontend and **Python Flask** backend, demonstrating OOP concepts, data structures, and DBMS principles.

## 🎯 Project Overview

SkillBridge is a marketplace platform that connects service providers with clients. Users can browse services, place orders, leave reviews, and manage their profiles. The platform includes an admin panel for managing users, services, and categories.

## 🛠️ Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Custom styling with CSS variables
- **Bootstrap 5** - Responsive framework
- **JavaScript (Vanilla)** - Client-side interactivity
- **Bootstrap Icons** - Icon library

### Backend
- **Python 3.8+** - Programming language
- **Flask** - Web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-Login** - User authentication
- **Flask-SocketIO** - Real-time WebSocket communication
- **SQLite** - Database (can be migrated to PostgreSQL/Firebase)

## 📋 Features

### User Features
- ✅ User registration and authentication
- ✅ Browse and search services
- ✅ Advanced filtering (category, price, rating)
- ✅ Service detail pages with reviews
- ✅ Favorite services
- ✅ Place orders with detailed requirements
- ✅ User profiles (public and private)
- ✅ Dashboard for providers and clients
- ✅ **Portfolio Showcase** - Display completed projects
- ✅ **Real-time Chat** - Instant messaging with Socket.IO
- ✅ **Smart Notifications** - Mark all read, clear all, dismiss individual

### Provider Features
- ✅ Create and manage services
- ✅ Set pricing (INR ₹) and delivery time ranges
- ✅ Manage orders with real-time chat
- ✅ View earnings and statistics
- ✅ **Project Portfolio** - Showcase completed work

### Admin Features
- ✅ Admin dashboard with statistics
- ✅ Manage users (activate/deactivate)
- ✅ Manage services
- ✅ Manage categories
- ✅ View all orders

### Technical Features
- ✅ **OOP Concepts**: Inheritance, Encapsulation, Abstraction, Polymorphism
- ✅ **Data Structures**: Dictionary (caching), Heap (top-N selection), Set (unique tags), Deque (order queue)
- ✅ **DBMS**: Relationships (One-to-Many, Many-to-Many), Foreign Keys, Indexes, Constraints
- ✅ **Real-Time Communication**: WebSocket-based chat with Socket.IO
- ✅ **Search**: Autocomplete with debouncing
- ✅ **Responsive Design**: Mobile-first approach
- ✅ **Security**: Password hashing, CSRF protection, SQL injection prevention

## 📁 Project Structure

```
skillbridge/
├── static/
│   ├── css/
│   │   └── custom.css          # Custom styles
│   ├── js/
│   │   └── main.js             # JavaScript functionality
│   └── images/                 # Image assets
├── templates/
│   ├── base.html               # Base template
│   ├── index.html              # Landing page
│   ├── services.html           # Service listing
│   ├── service_detail.html     # Service details
│   ├── auth/
│   │   ├── login.html          # Login page
│   │   └── register.html       # Registration page
│   ├── user/
│   │   ├── dashboard.html      # User dashboard
│   │   ├── profile.html        # User profile
│   │   └── orders.html         # Orders page
│   ├── admin/
│   │   ├── dashboard.html      # Admin dashboard
│   │   ├── users.html          # User management
│   │   ├── services.html       # Service management
│   │   └── categories.html     # Category management
│   └── components/
│       ├── header.html         # Navigation header
│       └── footer.html         # Footer
├── app.py                      # Flask application
├── config.py                   # Configuration
├── models.py                   # Database models
├── routes.py                   # Route handlers
├── managers.py                 # Business logic
├── events.py                   # Socket.IO event handlers
├── init_db.py                  # Database initialization
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Install Dependencies

```bash
# Navigate to project directory
cd skillbridge

# Install Python packages
pip install -r requirements.txt
```

### Step 2: Set Up Environment Variables

```bash
# Copy example environment file
copy .env.example .env

# Edit .env file with your settings (optional for development)
```

### Step 3: Initialize Database

```bash
# Run database initialization script
python init_db.py
```

This will:
- Create all database tables
- Create default admin user (admin@skillbridge.com / admin123)
- Seed categories
- Create sample data

### Step 4: Run the Application

```bash
# Start Flask development server
python app.py
```

The application will be available at: **http://localhost:5000**

## 👤 Default Accounts

### Admin Account
- **Email**: admin@skillbridge.com
- **Password**: admin123

### Sample Provider Accounts
- **Email**: alex@example.com / **Password**: password123
- **Email**: sarah@example.com / **Password**: password123
- **Email**: james@example.com / **Password**: password123

## 📚 OOP Concepts Demonstrated

### 1. Inheritance
- All models inherit from `db.Model`
- Configuration classes inherit from base `Config` class
- User authentication inherits from `UserMixin`

### 2. Encapsulation
- Password hashing in User model (private `password_hash`)
- Caching mechanism in ServiceManager (private `_cache`)
- Internal methods prefixed with underscore

### 3. Abstraction
- Manager classes provide simple interfaces for complex operations
- Database operations abstracted through SQLAlchemy ORM
- API endpoints abstract business logic

### 4. Polymorphism
- Different user types (client, provider, admin) with different behaviors
- Multiple models with similar methods (`get_average_rating()`, etc.)

## 🗄️ Data Structures Used

### 1. Dictionary (HashMap)
- **Purpose**: Caching frequently accessed data
- **Location**: `ServiceManager._cache`
- **Benefit**: O(1) lookup time

### 2. Heap (Priority Queue)
- **Purpose**: Efficient top-N service selection
- **Location**: `ServiceManager.get_featured_services()`
- **Benefit**: O(n log k) time complexity

### 3. Set
- **Purpose**: Unique tag management, category filtering
- **Location**: `ServiceManager.get_all_tags()`
- **Benefit**: Automatic duplicate removal

### 4. Deque (Double-ended Queue)
- **Purpose**: Order processing queue
- **Location**: `OrderManager.processing_queue`
- **Benefit**: Efficient add/remove from both ends

## 🗃️ Database Schema

### Tables
1. **users** - User accounts
2. **services** - Service listings
3. **categories** - Service categories
4. **reviews** - Service reviews
5. **orders** - Service orders
6. **favorites** - User favorites
7. **notifications** - User notifications
8. **messages** - Real-time chat messages
9. **project_showcase** - User portfolio projects

### Relationships
- User → Services (One-to-Many)
- Service → Reviews (One-to-Many)
- Service → Category (Many-to-One)
- User ↔ Services (Many-to-Many via Favorites)
- Order → Messages (One-to-Many)
- User → Portfolio (One-to-Many)

## 🔒 Security Features

- Password hashing with bcrypt
- CSRF protection
- SQL injection prevention (SQLAlchemy ORM)
- XSS prevention (template escaping)
- Session management
- Login required decorators

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop (1920px+)
- Laptop (1024px - 1920px)
- Tablet (768px - 1024px)
- Mobile (320px - 768px)

## 🎨 Design Features

- Modern gradient-based design
- Smooth animations and transitions
- Glassmorphism effects
- Hover states and micro-interactions
- Dark theme with vibrant accents
- Custom CSS variables for theming

## 🔄 Future Enhancements (Firebase Integration)

When Firebase SDK is provided:
1. Replace SQLite with Firebase Firestore
2. Implement Firebase Authentication
3. Add Firebase Storage for image uploads
4. Use Firebase Cloud Functions for notifications

## 📖 Code Documentation

All code includes comprehensive comments explaining:
- **Purpose**: What the code does
- **Parameters**: Input parameters and types
- **Returns**: Return values
- **OOP Concepts**: Which principles are demonstrated
- **Data Structures**: Which structures are used and why
- **Algorithms**: Logic explanation

## 🐛 Troubleshooting

### Database Issues
```bash
# Delete existing database and reinitialize
del skillbridge.db
python init_db.py
```

### Port Already in Use
```bash
# Change port in app.py (line with app.run())
app.run(port=5001)  # Use different port
```

### Missing Dependencies
```bash
# Reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

## 📞 Support

For issues or questions:
1. Check the code comments for detailed explanations
2. Review the implementation plan document
3. Examine the database schema in `models.py`

## 📄 License

This project is created for educational purposes.

## 👨‍💻 Author

SkillBridge Team - Full Stack Development Project

---

**Note**: This project demonstrates proficiency in:
- Frontend Development (HTML/CSS/Bootstrap/JavaScript)
- Backend Development (Python/Flask)
- Object-Oriented Programming
- Data Structures and Algorithms
- Database Management Systems
- Full Stack Integration
