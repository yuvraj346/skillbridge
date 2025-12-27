"""
Flask Routes (Controllers) for SkillBridge Application

This module contains all route handlers organized into blueprints.
Demonstrates MVC Pattern: Routes act as Controllers

Blueprints:
- main_bp: Main pages (home, about, etc.)
- auth_bp: Authentication (login, register, logout)
- service_bp: Service operations (create, view, edit, delete)
- user_bp: User profile and dashboard
- admin_bp: Admin panel
- api_bp: JSON API endpoints

Author: SkillBridge Team
Purpose: Handle HTTP requests and responses
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from datetime import datetime
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from models import db, User, Service, Category, Review, Order, Favorite, Notification, Message, ProjectShowcase
from managers import (service_manager, user_manager, search_engine, 
                     review_system, order_manager, category_manager, notification_manager, chat_manager)
from werkzeug.utils import secure_filename
import os

# Create blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)
service_bp = Blueprint('service', __name__)
user_bp = Blueprint('user', __name__)
admin_bp = Blueprint('admin', __name__)
api_bp = Blueprint('api', __name__)


# ============================================================================
# DECORATORS
# ============================================================================

def admin_required(f):
    """
    Decorator to require admin privileges
    
    OOP Concept: DECORATOR PATTERN
    - Wraps route functions to add authentication check
    - Reusable across multiple routes
    
    Args:
        f: Function to wrap
        
    Returns:
        Wrapped function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('You need admin privileges to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


def provider_required(f):
    """
    Decorator to require provider account
    
    Args:
        f: Function to wrap
        
    Returns:
        Wrapped function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'info')
            return redirect(url_for('auth.login'))
        if current_user.user_type not in ['provider', 'admin']:
            flash('You need a provider account to access this page.', 'warning')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================================
# MAIN ROUTES
# ============================================================================

@main_bp.route('/')
def index():
    """
    Landing page route
    
    Displays:
    - Hero section
    - Categories
    - Featured services
    - How it works
    - Testimonials
    - CTA
    
    Returns:
        Rendered template
    """
    # Get featured services using ServiceManager
    featured_services = service_manager.get_featured_services(limit=4)
    
    # Get all categories
    categories = category_manager.get_all_categories()
    
    # Get category stats
    category_stats = category_manager.get_category_stats()
    
    # Get stats for home page
    stats_data = {
        'total_users': User.query.count(),
        'total_services': Service.query.filter_by(is_active=True).count(),
        'total_reviews': Review.query.count()
    }
    
    return render_template('index.html',
                         featured_services=featured_services,
                         categories=categories,
                         category_stats=category_stats,
                         stats_data=stats_data)



@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')


# ============================================================================
# AUTHENTICATION ROUTES
# ============================================================================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    User login route
    
    GET: Display login form
    POST: Process login credentials
    
    Returns:
        Rendered template or redirect
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        # Authenticate user using UserManager
        user = user_manager.authenticate(email, password)
        
        if user:
            # Check if account is active
            if not user.is_active:
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return redirect(url_for('auth.login'))
            
            # Log in user
            login_user(user, remember=remember)
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            
            # Redirect based on user type
            if user.is_admin():
                return redirect(url_for('admin.dashboard'))
            elif user.user_type == 'provider':
                return redirect(url_for('user.dashboard'))
            else:
                return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    User registration route
    
    GET: Display registration form
    POST: Create new user account
    
    Returns:
        Rendered template or redirect
    """
    # Redirect if already logged in
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # Get form data
        data = {
            'username': request.form.get('username'),
            'email': request.form.get('email'),
            'password': request.form.get('password'),
            'user_type': request.form.get('user_type', 'client'),
            'full_name': request.form.get('full_name', '')
        }
        
        # Validate password confirmation
        password_confirm = request.form.get('password_confirm')
        if data['password'] != password_confirm:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
        
        # Create user using UserManager
        user, error = user_manager.create_user(data)
        
        if user:
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(error, 'danger')
    
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    User logout route
    
    Returns:
        Redirect to home page
    """
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.index'))


# ============================================================================
# SERVICE ROUTES
# ============================================================================

@service_bp.route('/browse')
def browse():
    """
    Browse all services with filters
    
    Query Parameters:
    - q: Search query
    - category: Category ID
    - min_price: Minimum price
    - max_price: Maximum price
    - sort: Sort option (price_asc, price_desc, rating, newest)
    
    Returns:
        Rendered template with services
    """
    # Get query parameters
    query = request.args.get('q', '')
    category_id = request.args.get('category', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    sort_by = request.args.get('sort', 'rating')
    
    # Build filters dictionary
    filters = {}
    if category_id:
        filters['category_id'] = category_id
    if min_price:
        filters['min_price'] = min_price
    if max_price:
        filters['max_price'] = max_price
    
    # Search services
    if query or filters:
        services = service_manager.search_services(query, filters)
    else:
        # Get all services
        services = Service.query.filter_by(is_active=True).all()
    
    # Sort services
    if sort_by == 'price_asc':
        services.sort(key=lambda s: s.price)
    elif sort_by == 'price_desc':
        services.sort(key=lambda s: s.price, reverse=True)
    elif sort_by == 'rating':
        services.sort(key=lambda s: s.get_average_rating(), reverse=True)
    elif sort_by == 'newest':
        services.sort(key=lambda s: s.created_at, reverse=True)
    
    # Get categories for filter
    categories = category_manager.get_all_categories()
    
    return render_template('services.html',
                         services=services,
                         categories=categories,
                         query=query,
                         selected_category=category_id,
                         sort_by=sort_by)


@service_bp.route('/<int:service_id>')
def detail(service_id):
    """
    Service detail page
    
    Args:
        service_id: Service ID
        
    Returns:
        Rendered template with service details
    """
    service = Service.query.get_or_404(service_id)
    
    # Increment view count
    service.increment_views()
    
    # Get reviews
    reviews = review_system.get_service_reviews(service_id, limit=10)
    
    # Get rating distribution
    rating_dist = review_system.calculate_rating_distribution(service_id)
    
    # Get related services (same category)
    related_services = Service.query.filter(
        Service.category_id == service.category_id,
        Service.id != service_id,
        Service.is_active == True
    ).limit(4).all()
    
    # Check if user has favorited this service
    is_favorited = False
    if current_user.is_authenticated:
        is_favorited = service.is_favorited_by(current_user)
    
    return render_template('service_detail.html',
                         service=service,
                         reviews=reviews,
                         rating_dist=rating_dist,
                         related_services=related_services,
                         is_favorited=is_favorited)


@service_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create new service (All logged-in users)
    
    Automatically converts user to 'provider' type when creating first service
    
    GET: Display service creation form
    POST: Create service
    
    Returns:
        Rendered template or redirect
    """
    if request.method == 'POST':
        # Automatically convert user to provider if they're a client
        if current_user.user_type == 'client':
            current_user.user_type = 'provider'
            db.session.commit()
            flash('Welcome to SkillBridge as a service provider!', 'success')
        
        # Get form data
        data = {
            'title': request.form.get('title'),
            'description': request.form.get('description'),
            'price': float(request.form.get('price', 0)),
            'delivery_time': request.form.get('delivery_time'),
            'category_id': int(request.form.get('category_id')),
            'tags': request.form.get('tags', ''),
            'image_url': request.form.get('image_url', 'default-service.jpg')
        }
        
        # Create service using ServiceManager
        service = service_manager.create_service(current_user.id, data)
        
        if service:
            flash('Service created successfully!', 'success')
            return redirect(url_for('service.detail', service_id=service.id))
        else:
            flash('Error creating service. Please try again.', 'danger')
    
    # Get categories for form
    categories = category_manager.get_all_categories()
    
    return render_template('service_create.html', categories=categories)


@service_bp.route('/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(service_id):
    """
    Edit service (Owner or Admin only)
    
    Args:
        service_id: Service ID
        
    Returns:
        Rendered template or redirect
    """
    service = Service.query.get_or_404(service_id)
    
    # Check ownership
    if service.user_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to edit this service.', 'danger')
        return redirect(url_for('service.detail', service_id=service_id))
    
    if request.method == 'POST':
        # Update service
        service.title = request.form.get('title')
        service.description = request.form.get('description')
        service.price = float(request.form.get('price', 0))
        service.delivery_time = request.form.get('delivery_time')
        service.category_id = int(request.form.get('category_id'))
        service.tags = request.form.get('tags', '')
        
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('service.detail', service_id=service_id))
    
    categories = category_manager.get_all_categories()
    return render_template('service_edit.html', service=service, categories=categories)


@service_bp.route('/<int:service_id>/delete', methods=['POST'])
@login_required
def delete(service_id):
    """
    Delete service (Owner or Admin only)
    
    Args:
        service_id: Service ID
        
    Returns:
        Redirect
    """
    service = Service.query.get_or_404(service_id)
    
    # Check ownership
    if service.user_id != current_user.id and not current_user.is_admin():
        flash('You do not have permission to delete this service.', 'danger')
        return redirect(url_for('service.detail', service_id=service_id))
    
    # Soft delete (set is_active to False)
    service.is_active = False
    db.session.commit()
    
    flash('Service deleted successfully.', 'success')
    return redirect(url_for('user.dashboard'))


@service_bp.route('/<int:service_id>/review', methods=['POST'])
@login_required
def add_review(service_id):
    """
    Add review to service
    
    Args:
        service_id: Service ID
        
    Returns:
        Redirect
    """
    rating = int(request.form.get('rating', 0))
    comment = request.form.get('comment', '')
    
    # Add review using ReviewSystem
    review, error = review_system.add_review(service_id, current_user.id, rating, comment)
    
    if review:
        flash('Review submitted successfully!', 'success')
    else:
        flash(error, 'danger')
    
    return redirect(url_for('service.detail', service_id=service_id))


@service_bp.route('/<int:service_id>/favorite', methods=['POST'])
@login_required
def toggle_favorite(service_id):
    """
    Toggle favorite status for service
    
    Args:
        service_id: Service ID
        
    Returns:
        JSON response
    """
    service = Service.query.get_or_404(service_id)
    
    # Check if already favorited
    favorite = Favorite.query.filter_by(
        user_id=current_user.id,
        service_id=service_id
    ).first()
    
    if favorite:
        # Remove from favorites
        db.session.delete(favorite)
        db.session.commit()
        return jsonify({'status': 'removed', 'message': 'Removed from favorites'})
    else:
        # Add to favorites
        favorite = Favorite(user_id=current_user.id, service_id=service_id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify({'status': 'added', 'message': 'Added to favorites'})


@service_bp.route('/<int:service_id>/order', methods=['POST'])
@login_required
def place_order(service_id):
    """
    Place order for service
    
    Args:
        service_id: Service ID
        
    Returns:
        Redirect
    """
    requirements = request.form.get('requirements', '')
    scope = request.form.get('scope', '')
    budget_tier = request.form.get('budget_tier', 'Standard')
    deadline_str = request.form.get('deadline')
    
    deadline = None
    if deadline_str:
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        except:
            pass
    
    # Create order using OrderManager
    order = order_manager.create_order(service_id, current_user.id, requirements, scope, budget_tier, deadline)
    
    if order:
        # Create notification for the provider
        notification_manager.create_notification(
            user_id=order.seller_id,
            title='New Order Received',
            message=f'You have a new order for {order.service.title} from {current_user.username}',
            link=url_for('user.orders')
        )
        flash('Order placed successfully! The provider will contact you soon.', 'success')
        return redirect(url_for('user.orders'))
    else:
        flash('Error placing order. Please try again.', 'danger')
        return redirect(url_for('service.detail', service_id=service_id))


# ============================================================================
# USER ROUTES
# ============================================================================

@user_bp.route('/dashboard')
@login_required
def dashboard():
    """
    User dashboard
    
    Shows different content based on user type:
    - Provider: Services, orders, earnings
    - Client: Orders, favorites
    - Admin: Redirect to admin panel
    
    Returns:
        Rendered template
    """
    if current_user.is_admin():
        return redirect(url_for('admin.dashboard'))
    
    # Get user stats
    stats = user_manager.get_user_stats(current_user.id)
    
    if current_user.user_type == 'provider':
        # Provider dashboard
        services = current_user.get_services()
        orders = order_manager.get_user_orders(current_user.id, as_buyer=False)
        
        return render_template('user/provider_dashboard.html',
                             stats=stats,
                             services=services,
                             orders=orders)
    else:
        # Client dashboard
        orders = order_manager.get_user_orders(current_user.id, as_buyer=True)
        favorites = Favorite.query.filter_by(user_id=current_user.id).all()
        recommendations = service_manager.get_recommendations(current_user, limit=6)
        
        return render_template('user/client_dashboard.html',
                             stats=stats,
                             orders=orders,
                             favorites=favorites,
                             recommendations=recommendations)


@user_bp.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark notification as read"""
    notification_manager.mark_as_read(notification_id)
    return jsonify({'status': 'success'})


@user_bp.route('/notifications/mark-all-read', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read"""
    notification_manager.mark_all_read(current_user.id)
    return jsonify({'status': 'success'})


@user_bp.route('/notifications/delete/<int:notification_id>', methods=['POST'])
@login_required
def delete_notification(notification_id):
    """Delete a notification"""
    notification_manager.delete_notification(notification_id)
    return jsonify({'status': 'success'})


@user_bp.route('/notifications/clear-all', methods=['POST'])
@login_required
def clear_all_notifications():
    """Clear all notifications"""
    notification_manager.clear_all(current_user.id)
    return jsonify({'status': 'success'})



@user_bp.route('/chats')
@login_required
def chats():
    """User chats page"""
    active_chats = chat_manager.get_active_chats(current_user.id)
    return render_template('user/chats.html', chats=active_chats)



@user_bp.route('/order/<int:order_id>')
@login_required
def order_detail(order_id):
    """Order detail with chat"""
    order = Order.query.get_or_404(order_id)
    
    # Check permission
    if current_user.id not in [order.buyer_id, order.seller_id] and not current_user.is_admin():
        flash('Unauthorized access', 'danger')
        return redirect(url_for('user.dashboard'))
        
    messages = chat_manager.get_messages(order_id, current_user.id)
    return render_template('user/order_detail.html', order=order, messages=messages)

@user_bp.route('/order/<int:order_id>/action/<action>', methods=['POST'])
@login_required
def order_action(order_id, action):
    """Handle order actions (accept/complete)"""
    order = Order.query.get_or_404(order_id)
    
    if current_user.id != order.seller_id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('user.order_detail', order_id=order_id))
        
    if action == 'accept':
        if order_manager.accept_order(order_id):
            flash('Order accepted! You can now chat with the client.', 'success')
            notification_manager.create_notification(order.buyer_id, f"Order #{order.id} Accepted", f"Your order for {order.service.title} has been accepted.", url_for('user.order_detail', order_id=order.id))
    elif action == 'complete':
        if order_manager.complete_order(order_id):
            flash('Order marked as complete!', 'success')
            notification_manager.create_notification(order.buyer_id, f"Order #{order.id} Completed", f"Your order for {order.service.title} is ready!", url_for('user.order_detail', order_id=order.id))
            
    return redirect(url_for('user.order_detail', order_id=order_id))

@user_bp.route('/order/<int:order_id>/message', methods=['POST'])
@login_required
def send_message(order_id):
    """Send chat message"""
    content = request.form.get('content')
    if content:
        msg, error = chat_manager.send_message(order_id, current_user.id, content)
        if error:
            flash(error, 'danger')
        else:
            # Notify receiver
            order = Order.query.get(order_id)
            receiver_id = order.buyer_id if current_user.id == order.seller_id else order.seller_id
            notification_manager.create_notification(receiver_id, "New Message", f"New message from {current_user.username}", url_for('user.order_detail', order_id=order_id))
            
    return redirect(url_for('user.order_detail', order_id=order_id))


@user_bp.route('/profile/<username>')
def profile(username):
    """
    Public user profile
    
    Args:
        username: Username
        
    Returns:
        Rendered template
    """
    user = User.query.filter_by(username=username).first_or_404()
    
    # Get user's services
    services = user.get_services()
    
    # Get user stats
    stats = user_manager.get_user_stats(user.id)
    
    return render_template('user/profile.html',
                         user=user,
                         services=services,
                         stats=stats)


@user_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """
    User settings page
    
    GET: Display settings form
    POST: Update user settings
    
    Returns:
        Rendered template or redirect
    """
    if request.method == 'POST':
        # Update profile
        current_user.full_name = request.form.get('full_name', '')
        current_user.bio = request.form.get('bio', '')
        current_user.phone = request.form.get('phone', '')
        
        # Update password if provided
        new_password = request.form.get('new_password')
        if new_password:
            current_password = request.form.get('current_password')
            if current_user.check_password(current_password):
                current_user.set_password(new_password)
                flash('Password updated successfully!', 'success')
            else:
                flash('Current password is incorrect.', 'danger')
                return render_template('user/settings.html')
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
        return redirect(url_for('user.settings'))
    
    return render_template('user/settings.html')


@user_bp.route('/portfolio/add', methods=['POST'])
@login_required
def add_portfolio():
    """Add a portfolio project"""
    title = request.form.get('title')
    description = request.form.get('description')
    image_url = request.form.get('image_url')
    link = request.form.get('link')
    
    if not title:
        flash('Project title is required', 'danger')
        return redirect(url_for('user.settings'))
    
    project = ProjectShowcase(
        user_id=current_user.id,
        title=title,
        description=description,
        image_url=image_url,
        link=link
    )
    
    db.session.add(project)
    db.session.commit()
    
    flash('Project added to your portfolio!', 'success')
    return redirect(url_for('user.settings'))


@user_bp.route('/portfolio/delete/<int:project_id>', methods=['POST'])
@login_required
def delete_portfolio(project_id):
    """Delete a portfolio project"""
    project = ProjectShowcase.query.get_or_404(project_id)
    
    if project.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('user.settings'))
    
    db.session.delete(project)
    db.session.commit()
    
    flash('Project removed from portfolio', 'success')
    return redirect(url_for('user.settings'))



@user_bp.route('/orders')
@login_required
def orders():
    """
    User orders page
    
    Returns:
        Rendered template
    """
    # Get orders as buyer and seller
    orders_as_buyer = order_manager.get_user_orders(current_user.id, as_buyer=True)
    orders_as_seller = order_manager.get_user_orders(current_user.id, as_buyer=False)
    
    return render_template('user/orders.html',
                         orders_as_buyer=orders_as_buyer,
                         orders_as_seller=orders_as_seller)


# ============================================================================
# ADMIN ROUTES
# ============================================================================

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """
    Admin dashboard
    
    Shows:
    - Total users, services, orders
    - Recent activity
    - Statistics
    
    Returns:
        Rendered template
    """
    # Get statistics
    total_users = User.query.count()
    total_services = Service.query.filter_by(is_active=True).count()
    total_orders = Order.query.count()
    total_reviews = Review.query.count()
    
    # Get recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # Get recent services
    recent_services = Service.query.order_by(Service.created_at.desc()).limit(10).all()
    
    # Get recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    stats = {
        'total_users': total_users,
        'total_services': total_services,
        'total_orders': total_orders,
        'total_reviews': total_reviews
    }
    
    return render_template('admin/dashboard.html',
                         stats=stats,
                         recent_users=recent_users,
                         recent_services=recent_services,
                         recent_orders=recent_orders)


@admin_bp.route('/users')
@admin_required
def users():
    """
    Manage users
    
    Returns:
        Rendered template
    """
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    """
    Toggle user active status
    
    Args:
        user_id: User ID
        
    Returns:
        Redirect
    """
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/services')
@admin_required
def services():
    """
    Manage services
    
    Returns:
        Rendered template
    """
    services = Service.query.order_by(Service.created_at.desc()).all()
    return render_template('admin/services.html', services=services)


@admin_bp.route('/categories', methods=['GET', 'POST'])
@admin_required
def categories():
    """
    Manage categories
    
    GET: Display categories
    POST: Create new category
    
    Returns:
        Rendered template or redirect
    """
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        icon = request.form.get('icon', '')
        color = request.form.get('color', '')
        
        category = category_manager.create_category(name, description, icon, color)
        
        if category:
            flash('Category created successfully!', 'success')
        else:
            flash('Category already exists.', 'danger')
        
        return redirect(url_for('admin.categories'))
    
    categories = category_manager.get_all_categories()
    return render_template('admin/categories.html', categories=categories)


@admin_bp.route('/orders')
@admin_required
def orders():
    """
    Manage orders
    
    Returns:
        Rendered template
    """
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin/orders.html', orders=orders)


# ============================================================================
# API ROUTES (JSON)
# ============================================================================

@api_bp.route('/search/autocomplete')
def search_autocomplete():
    """
    Autocomplete API for search
    
    Query Parameters:
    - q: Search query
    
    Returns:
        JSON: List of suggestions
    """
    query = request.args.get('q', '')
    suggestions = search_engine.get_autocomplete_suggestions(query, limit=5)
    
    return jsonify({'suggestions': suggestions})


@api_bp.route('/categories')
def get_categories():
    """
    Get all categories
    
    Returns:
        JSON: List of categories with stats
    """
    category_stats = category_manager.get_category_stats()
    return jsonify({'categories': category_stats})


@api_bp.route('/services/featured')
def get_featured_services():
    """
    Get featured services
    
    Returns:
        JSON: List of featured services
    """
    limit = request.args.get('limit', 4, type=int)
    services = service_manager.get_featured_services(limit)
    
    services_data = [{
        'id': s.id,
        'title': s.title,
        'price': s.price,
        'rating': s.get_average_rating(),
        'provider': s.provider.username,
        'image_url': s.image_url
    } for s in services]
    
    return jsonify({'services': services_data})


@api_bp.route('/services/<int:service_id>/stats')
def get_service_stats(service_id):
    """
    Get service statistics
    
    Args:
        service_id: Service ID
        
    Returns:
        JSON: Service stats
    """
    service = Service.query.get_or_404(service_id)
    
    stats = {
        'views': service.view_count,
        'rating': service.get_average_rating(),
        'reviews': service.get_review_count(),
        'favorites': service.favorited_by.count()
    }
    
    return jsonify(stats)
