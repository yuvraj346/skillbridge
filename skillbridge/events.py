"""
Socket.IO Event Handlers for Real-Time Chat

This module handles WebSocket events for real-time messaging
"""

from flask import request
from flask_login import current_user
from flask_socketio import emit, join_room, leave_room
from models import db, Message, Order
from managers import chat_manager

def register_socketio_events(socketio):
    """Register all socket.io event handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        if current_user.is_authenticated:
            print(f'User {current_user.username} connected')
        
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        if current_user.is_authenticated:
            print(f'User {current_user.username} disconnected')
    
    @socketio.on('join')
    def handle_join(data):
        """Join a chat room (order-based)"""
        if not current_user.is_authenticated:
            return
        
        order_id = data.get('order_id')
        if not order_id:
            return
        
        # Verify user is part of this order
        order = Order.query.get(order_id)
        if not order or current_user.id not in [order.buyer_id, order.seller_id]:
            return
        
        room = f'order_{order_id}'
        join_room(room)
        emit('joined', {'order_id': order_id}, room=room)
        print(f'User {current_user.username} joined room {room}')
    
    @socketio.on('leave')
    def handle_leave(data):
        """Leave a chat room"""
        if not current_user.is_authenticated:
            return
        
        order_id = data.get('order_id')
        if not order_id:
            return
        
        room = f'order_{order_id}'
        leave_room(room)
        print(f'User {current_user.username} left room {room}')
    
    @socketio.on('send_message')
    def handle_send_message(data):
        """Handle incoming chat message"""
        if not current_user.is_authenticated:
            return
        
        order_id = data.get('order_id')
        content = data.get('content')
        
        if not order_id or not content:
            return
        
        # Save message to database
        message, error = chat_manager.send_message(order_id, current_user.id, content)
        
        if error:
            emit('error', {'message': error})
            return
        
        # Broadcast to room
        room = f'order_{order_id}'
        emit('new_message', {
            'id': message.id,
            'sender_id': message.sender_id,
            'sender_name': current_user.username,
            'content': message.content,
            'created_at': message.created_at.strftime('%H:%M')
        }, room=room)
