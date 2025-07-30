"""
Live Chat Module
NVC Banking Platform - Interactive Multi-Agent Chat System
"""

from .routes import chat_bp, init_socketio_handlers

__all__ = ['chat_bp', 'init_socketio_handlers']