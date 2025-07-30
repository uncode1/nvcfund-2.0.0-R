# NVC Banking Platform - Unified UI Developer Guide

## Quick Start

### 1. Create a New Template

```html
{% extends "unified_base.html" %}
{% from "components/nvc_components.html" import metric_card, action_card, form_input %}

{% block title %}My Page - NVC Banking Platform{% endblock %}
{% block page_title %}My Page Title{% endblock %}
{% block page_description %}Brief description of what this page does{% endblock %}

{% block page_actions %}
<button class="nvc-btn nvc-btn-primary">
    <i class="fas fa-plus"></i>
    <span class="nvc-btn-text">New Item</span>
</button>
{% endblock %}

{% block content %}
<div class="nvc-page-content">
    <!-- Your content here -->
    {{ metric_card("Total Users", "1,247", "fas fa-users", "+8.3%", "positive") }}
</div>
{% endblock %}
```

### 2. Available Components

Import components you need:
```html
{% from "components/nvc_components.html" import 
    metric_card, 
    action_card, 
    account_card, 
    transaction_row, 
    form_input, 
    form_select, 
    notification_banner, 
    progress_bar, 
    stats_grid, 
    loading_spinner, 
    empty_state 
%}
```

### 3. CSS Classes

Use NVC-prefixed classes for consistency:
```html
<!-- Buttons -->
<button class="nvc-btn nvc-btn-primary">Primary</button>
<button class="nvc-btn nvc-btn-secondary">Secondary</button>
<button class="nvc-btn nvc-btn-outline">Outline</button>

<!-- Cards -->
<div class="nvc-card">
    <div class="nvc-card-header">
        <h3 class="nvc-card-title">Title</h3>
    </div>
    <div class="nvc-card-body">Content</div>
</div>

<!-- Alerts -->
<div class="nvc-alert nvc-alert-success">Success message</div>
```

## Component Reference

### Metric Card
Display key performance indicators and statistics.

```html
{{ metric_card(title, value, icon, change=None, change_type="positive", color="primary") }}
```

**Parameters:**
- `title`: Card title (e.g., "Total Revenue")
- `value`: Main value to display (e.g., "$125,430.50")
- `icon`: FontAwesome icon class (e.g., "fas fa-wallet")
- `change`: Optional change indicator (e.g., "+5.2%")
- `change_type`: "positive" or "negative"
- `color`: "primary", "success", "warning", "danger", "info"

**Example:**
```html
{{ metric_card("Total Balance", "$125,430.50", "fas fa-wallet", "+5.2%", "positive", "primary") }}
```

### Action Card
Create clickable cards for navigation and actions.

```html
{{ action_card(title, description, icon, url, color="primary") }}
```

**Parameters:**
- `title`: Action title
- `description`: Brief description
- `icon`: FontAwesome icon class
- `url`: Target URL
- `color`: Card color theme

**Example:**
```html
{{ action_card("Transfer Money", "Send funds between accounts", "fas fa-exchange-alt", "/banking/transfer", "primary") }}
```

### Account Card
Display account information with actions.

```html
{{ account_card(account_type, account_number, balance, icon, status="active") }}
```

**Parameters:**
- `account_type`: Type of account (e.g., "Checking Account")
- `account_number`: Masked account number (e.g., "****1234")
- `balance`: Account balance (e.g., "$45,230.50")
- `icon`: FontAwesome icon class
- `status`: "active", "pending", "inactive"

**Example:**
```html
{{ account_card("Checking Account", "****1234", "$45,230.50", "fas fa-university", "active") }}
```

### Form Input
Create consistent form input fields.

```html
{{ form_input(label, name, type="text", placeholder="", icon=None, required=False, value="") }}
```

**Parameters:**
- `label`: Field label
- `name`: Input name attribute
- `type`: Input type (text, email, password, etc.)
- `placeholder`: Placeholder text
- `icon`: Optional FontAwesome icon
- `required`: Boolean for required field
- `value`: Default value

**Example:**
```html
{{ form_input("Email Address", "email", "email", "Enter your email", "fas fa-envelope", True) }}
```

### Form Select
Create consistent select dropdowns.

```html
{{ form_select(label, name, options, icon=None, required=False, selected="") }}
```

**Parameters:**
- `label`: Field label
- `name`: Select name attribute
- `options`: List of (value, text) tuples
- `icon`: Optional FontAwesome icon
- `required`: Boolean for required field
- `selected`: Default selected value

**Example:**
```html
{{ form_select("Account Type", "account_type", [("checking", "Checking"), ("savings", "Savings")], "fas fa-university", True) }}
```

### Notification Banner
Display user notifications and alerts.

```html
{{ notification_banner(message, type="info", dismissible=True, icon=None) }}
```

**Parameters:**
- `message`: Notification message
- `type`: "success", "warning", "danger", "info"
- `dismissible`: Boolean for close button
- `icon`: Optional custom icon

**Example:**
```html
{{ notification_banner("Account updated successfully!", "success", True, "fas fa-check-circle") }}
```

### Progress Bar
Show progress indicators.

```html
{{ progress_bar(percentage, label="", color="primary", show_percentage=True) }}
```

**Parameters:**
- `percentage`: Progress percentage (0-100)
- `label`: Optional label
- `color`: "primary", "success", "warning", "danger"
- `show_percentage`: Boolean to show percentage

**Example:**
```html
{{ progress_bar(75, "Account Setup", "primary", True) }}
```

### Transaction Row
Display transaction information.

```html
{{ transaction_row(date, description, amount, type, status="completed") }}
```

**Parameters:**
- `date`: Transaction date
- `description`: Transaction description
- `amount`: Transaction amount
- `type`: "credit" or "debit"
- `status`: "completed", "pending", "failed"

**Example:**
```html
{{ transaction_row("2024-01-15", "Direct Deposit", "$3,250.00", "credit", "completed") }}
```

### Loading Spinner
Show loading states.

```html
{{ loading_spinner(size="md", text="Loading...") }}
```

**Parameters:**
- `size`: "sm", "md", "lg"
- `text`: Optional loading text

**Example:**
```html
{{ loading_spinner("lg", "Processing transaction...") }}
```

### Empty State
Display empty state messages.

```html
{{ empty_state(title, description, icon="fas fa-inbox", action_text=None, action_url=None) }}
```

**Parameters:**
- `title`: Empty state title
- `description`: Description text
- `icon`: FontAwesome icon class
- `action_text`: Optional action button text
- `action_url`: Optional action button URL

**Example:**
```html
{{ empty_state("No Transactions", "You haven't made any transactions yet.", "fas fa-receipt", "Make First Transaction", "/transfer") }}
```

## CSS Framework

### Color System
Use CSS custom properties for consistent colors:

```css
/* Primary Colors */
var(--nvc-primary)        /* Deep Blue */
var(--nvc-primary-light)  /* Bright Blue */
var(--nvc-accent)         /* Sky Blue */

/* Background Colors */
var(--nvc-bg-primary)     /* Main background */
var(--nvc-bg-secondary)   /* Cards and panels */
var(--nvc-bg-tertiary)    /* Elevated surfaces */

/* Text Colors */
var(--nvc-text-primary)   /* Primary text */
var(--nvc-text-secondary) /* Secondary text */
var(--nvc-text-muted)     /* Muted text */

/* Status Colors */
var(--nvc-success)        /* Success states */
var(--nvc-warning)        /* Warning states */
var(--nvc-danger)         /* Error states */
var(--nvc-info)           /* Information states */
```

### Spacing System
Use consistent spacing with CSS custom properties:

```css
var(--nvc-space-xs)   /* 4px */
var(--nvc-space-sm)   /* 8px */
var(--nvc-space-md)   /* 16px */
var(--nvc-space-lg)   /* 24px */
var(--nvc-space-xl)   /* 32px */
var(--nvc-space-2xl)  /* 48px */
var(--nvc-space-3xl)  /* 64px */
```

### Typography Scale
Use predefined font sizes:

```css
var(--nvc-font-size-xs)   /* 12px */
var(--nvc-font-size-sm)   /* 14px */
var(--nvc-font-size-base) /* 16px */
var(--nvc-font-size-lg)   /* 18px */
var(--nvc-font-size-xl)   /* 20px */
var(--nvc-font-size-2xl)  /* 24px */
var(--nvc-font-size-3xl)  /* 30px */
var(--nvc-font-size-4xl)  /* 36px */
```

### Border Radius
Use consistent border radius:

```css
var(--nvc-radius-sm)  /* 6px */
var(--nvc-radius-md)  /* 8px */
var(--nvc-radius-lg)  /* 12px */
var(--nvc-radius-xl)  /* 16px */
```

## Layout Patterns

### Dashboard Layout
```html
{% extends "unified_base.html" %}

{% block content %}
<div class="nvc-page-content">
    <!-- Metrics Row -->
    <div class="row g-4 mb-4">
        <div class="col-lg-3 col-md-6">
            {{ metric_card(...) }}
        </div>
        <!-- More metrics -->
    </div>
    
    <!-- Actions Row -->
    <div class="row g-3 mb-4">
        <div class="col-lg-4 col-md-6">
            {{ action_card(...) }}
        </div>
        <!-- More actions -->
    </div>
    
    <!-- Content Row -->
    <div class="row g-4">
        <div class="col-lg-8">
            <!-- Main content -->
        </div>
        <div class="col-lg-4">
            <!-- Sidebar content -->
        </div>
    </div>
</div>
{% endblock %}
```

### Form Layout
```html
{% extends "unified_base.html" %}

{% block content %}
<div class="nvc-page-content">
    <div class="row justify-content-center">
        <div class="col-lg-8">
            <div class="nvc-card">
                <div class="nvc-card-header">
                    <h3 class="nvc-card-title">Form Title</h3>
                </div>
                <div class="nvc-card-body">
                    <form method="POST">
                        <div class="row">
                            <div class="col-md-6">
                                {{ form_input(...) }}
                            </div>
                            <div class="col-md-6">
                                {{ form_input(...) }}
                            </div>
                        </div>
                        
                        {{ form_select(...) }}
                        
                        <div class="d-flex gap-3 mt-4">
                            <button type="button" class="nvc-btn nvc-btn-outline">Cancel</button>
                            <button type="submit" class="nvc-btn nvc-btn-primary">Submit</button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### List Layout
```html
{% extends "unified_base.html" %}

{% block content %}
<div class="nvc-page-content">
    <div class="nvc-card">
        <div class="nvc-card-header">
            <h3 class="nvc-card-title">Items List</h3>
        </div>
        <div class="nvc-card-body p-0">
            {% for item in items %}
                {{ transaction_row(...) }}
            {% else %}
                {{ empty_state("No Items", "No items found.", "fas fa-inbox") }}
            {% endfor %}
        </div>
    </div>
</div>
{% endblock %}
```

## Responsive Design

### Breakpoints
- **Mobile**: < 768px
- **Tablet**: 768px - 1024px  
- **Desktop**: > 1024px

### Grid System
Use Bootstrap's responsive grid:

```html
<div class="row g-4">
    <div class="col-lg-4 col-md-6 col-sm-12">
        <!-- Content -->
    </div>
</div>
```

### Responsive Utilities
```html
<!-- Hide on mobile -->
<span class="d-none d-md-inline">Desktop only text</span>

<!-- Show only on mobile -->
<span class="d-md-none">Mobile only text</span>

<!-- Responsive button text -->
<button class="nvc-btn nvc-btn-primary">
    <i class="fas fa-plus"></i>
    <span class="nvc-btn-text">Add Item</span> <!-- Hidden on mobile -->
</button>
```

## Accessibility Guidelines

### Semantic HTML
```html
<!-- Good -->
<button class="nvc-btn nvc-btn-primary" aria-label="Create new account">
    <i class="fas fa-plus" aria-hidden="true"></i>
    <span class="nvc-btn-text">New Account</span>
</button>

<!-- Bad -->
<div class="nvc-btn nvc-btn-primary" onclick="createAccount()">
    <i class="fas fa-plus"></i>
    New Account
</div>
```

### Form Labels
```html
<!-- Always associate labels with inputs -->
{{ form_input("Email", "email", "email", "Enter email", "fas fa-envelope", True) }}

<!-- Or use aria-label for custom inputs -->
<input type="text" aria-label="Search transactions" class="nvc-form-input">
```

### Color Contrast
- All text meets WCAG AA standards (4.5:1 ratio)
- Interactive elements have sufficient contrast
- Don't rely solely on color to convey information

### Keyboard Navigation
- All interactive elements are keyboard accessible
- Logical tab order
- Visible focus indicators

## Performance Best Practices

### CSS Loading
```html
<!-- Critical CSS is inlined in unified_base.html -->
<!-- Non-critical CSS loaded asynchronously -->
<link rel="preload" href="{{ url_for('static', filename='css/unified-professional-theme.css') }}" as="style" onload="this.onload=null;this.rel='stylesheet'">
```

### Image Optimization
```html
<!-- Use appropriate image formats -->
<img src="image.webp" alt="Description" loading="lazy">

<!-- Provide fallbacks -->
<picture>
    <source srcset="image.webp" type="image/webp">
    <img src="image.jpg" alt="Description">
</picture>
```

### JavaScript
- Use progressive enhancement
- Load non-critical JavaScript asynchronously
- Minimize DOM manipulation

## Testing

### Template Testing
```python
# Test template rendering
def test_template_renders():
    with app.test_client() as client:
        response = client.get('/dashboard')
        assert response.status_code == 200
        assert 'nvc-page-content' in response.data.decode()
```

### Component Testing
```python
# Test component macros
def test_metric_card_component():
    template = env.from_string('''
        {% from "components/nvc_components.html" import metric_card %}
        {{ metric_card("Test", "100", "fas fa-test") }}
    ''')
    result = template.render()
    assert 'nvc-metric-card' in result
    assert 'Test' in result
```

### Accessibility Testing
- Use automated tools (axe-core, WAVE)
- Test with screen readers
- Verify keyboard navigation
- Check color contrast

### Cross-browser Testing
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Migration from Old System

### Step 1: Update Template Inheritance
```html
<!-- Old -->
{% extends "base.html" %}

<!-- New -->
{% extends "unified_base.html" %}
```

### Step 2: Import Components
```html
<!-- Add component imports -->
{% from "components/nvc_components.html" import metric_card, action_card %}
```

### Step 3: Update CSS Classes
```html
<!-- Old -->
<button class="btn btn-primary">Button</button>
<div class="card">Content</div>

<!-- New -->
<button class="nvc-btn nvc-btn-primary">Button</button>
<div class="nvc-card">Content</div>
```

### Step 4: Replace Hardcoded HTML with Components
```html
<!-- Old -->
<div class="metric-card">
    <h3>Total Users</h3>
    <p>1,247</p>
</div>

<!-- New -->
{{ metric_card("Total Users", "1,247", "fas fa-users") }}
```

### Step 5: Update Block Names
```html
<!-- Old -->
{% block dashboard_content %}

<!-- New -->
{% block content %}
```

## Troubleshooting

### Common Issues

**Template not found error:**
- Ensure template extends `unified_base.html`
- Check file path and spelling

**Component not rendering:**
- Verify component import statement
- Check component parameter names and types

**CSS not loading:**
- Clear browser cache
- Check CSS file path in unified_base.html
- Verify CSS custom properties are defined

**Responsive issues:**
- Use Bootstrap grid classes correctly
- Test on actual devices
- Check viewport meta tag

### Debug Mode
```python
# Enable template debugging
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.jinja_env.auto_reload = True
```

### Performance Issues
```python
# Profile template rendering
import time
start = time.time()
# Render template
end = time.time()
print(f"Template rendered in {end - start:.2f}s")
```

## Resources

### Documentation
- [UI Design System](UI_DESIGN_SYSTEM.md)
- [Component Library](templates/components/nvc_components.html)
- [Example Templates](templates/examples/)

### Tools
- [Migration Script](scripts/migrate_to_unified_ui.py)
- [Testing Script](scripts/test_unified_ui.py)
- [CSS Framework](static/css/unified-professional-theme.css)

### Support
- Check example templates for patterns
- Review migration report for issues
- Test with provided demo templates
- Follow established conventions

---

*This guide ensures consistent, professional, and accessible UI development across the NVC Banking Platform.*