# Changelog

All notable changes to the NewUI Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-07-23

### Added

#### Phase 1: Core Features
- Component macro system with parameter validation
- Automatic AJAX partial rendering
- Basic event handling (click, submit, change)
- State persistence via data attributes
- Flask extension for easy integration

#### Phase 2: Enhanced Interactivity
- Two-way data binding for forms
- Conditional rendering helpers
- List rendering with efficient updates
- Component lifecycle hooks
- Built-in loading states

#### Phase 3: Advanced Features
- WebSocket support for real-time updates
- Component composition patterns with builder pattern and slots
- State stores for complex apps with Redux-like architecture
- Route-based code splitting with dynamic loading
- Development tools (debugger, component inspector)

### Features

- **Zero Build Step**: Works without webpack or compilation for basic usage
- **Progressive Enhancement**: Full functionality without JavaScript, enhanced with it
- **Flask-Native**: Seamless integration with Flask's request/response cycle
- **CSS Framework Agnostic**: Easy integration with Tailwind, Bootstrap, or custom CSS
- **Jinja2-First**: All components leverage Jinja2's existing capabilities

### Dependencies

- Flask >= 1.1.0
- Jinja2 >= 2.11.0
- MarkupSafe >= 2.0.0

### Optional Dependencies

- Flask-SocketIO >= 5.0.0 (for WebSocket support)

### Examples

- Basic form handling and component usage
- Advanced data binding and conditional rendering
- Real-time chat and WebSocket integration
- Component composition and state management
- Development tools and debugging

### Documentation

- Complete API reference
- Getting started guide
- Migration guide from vanilla Flask/Jinja2
- Best practices and patterns
- Performance optimization tips