# NVC Banking Platform - Unified UI Design System

## Overview

The NVC Banking Platform Design System provides a comprehensive, professional, and consistent user interface across all modules. This system ensures a cohesive banking experience that builds trust and enhances usability.

## Design Principles

### 1. **Professional Banking Aesthetic**
- Clean, trustworthy design that instills confidence
- Sophisticated color palette with deep blues and professional grays
- Consistent typography and spacing

### 2. **Consistency First**
- Unified components across all modules
- Standardized interactions and behaviors
- Consistent visual hierarchy

### 3. **Accessibility & Usability**
- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- High contrast ratios

### 4. **Responsive Design**
- Mobile-first approach
- Fluid layouts that work on all devices
- Touch-friendly interface elements

## Color System

### Primary Colors
```css
--nvc-primary: #1e3a8a;           /* Deep Blue - Primary brand color */
--nvc-primary-light: #3b82f6;     /* Bright Blue - Interactive elements */
--nvc-primary-dark: #1e40af;      /* Darker Blue - Hover states */
--nvc-accent: #0ea5e9;            /* Sky Blue - Accent and highlights */
```

### Background Colors
```css
--nvc-bg-primary: #0f172a;        /* Very Dark Blue - Main background */
--nvc-bg-secondary: #1e293b;      /* Dark Blue Gray - Cards and panels */
--nvc-bg-tertiary: #334155;       /* Medium Blue Gray - Elevated surfaces */
--nvc-bg-surface: #475569;        /* Light Blue Gray - Interactive surfaces */
```

### Text Colors
```css
--nvc-text-primary: #f8fafc;      /* Almost White - Primary text */
--nvc-text-secondary: #e2e8f0;    /* Light Gray - Secondary text */
--nvc-text-muted: #94a3b8;        /* Medium Gray - Muted text */
```

### Semantic Colors
```css
--nvc-success: #10b981;           /* Emerald - Success states */
--nvc-warning: #f59e0b;           /* Amber - Warning states */
--nvc-danger: #ef4444;            /* Red - Error states */
--nvc-info: #06b6d4;              /* Cyan - Information states */
```

## Typography

### Font Family
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
```

### Font Scale
- **xs**: 0.75rem (12px) - Small labels, captions
- **sm**: 0.875rem (14px) - Body text, form labels
- **base**: 1rem (16px) - Default body text
- **lg**: 1.125rem (18px) - Subheadings
- **xl**: 1.25rem (20px) - Card titles
- **2xl**: 1.5rem (24px) - Section headings
- **3xl**: 1.875rem (30px) - Page titles
- **4xl**: 2.25rem (36px) - Hero headings

## Spacing System

Based on a 4px grid system:

```css
--nvc-space-xs: 0.25rem;   /* 4px */
--nvc-space-sm: 0.5rem;    /* 8px */
--nvc-space-md: 1rem;      /* 16px */
--nvc-space-lg: 1.5rem;    /* 24px */
--nvc-space-xl: 2rem;      /* 32px */
--nvc-space-2xl: 3rem;     /* 48px */
--nvc-space-3xl: 4rem;     /* 64px */
```

## Component Library

### Buttons

#### Primary Button
```html
<button class="nvc-btn nvc-btn-primary">
    <i class="fas fa-plus"></i>
    <span class="nvc-btn-text">Primary Action</span>
</button>
```

#### Secondary Button
```html
<button class="nvc-btn nvc-btn-secondary">
    <i class="fas fa-edit"></i>
    <span class="nvc-btn-text">Secondary Action</span>
</button>
```

#### Outline Button
```html
<button class="nvc-btn nvc-btn-outline">
    <i class="fas fa-download"></i>
    <span class="nvc-btn-text">Outline Action</span>
</button>
```

#### Button Sizes
- **Default**: Standard size for most use cases
- **Large**: `nvc-btn-lg` - For prominent actions
- **Small**: `nvc-btn-sm` - For compact interfaces

### Cards

#### Basic Card
```html
<div class="nvc-card">
    <div class="nvc-card-header">
        <h3 class="nvc-card-title">Card Title</h3>
    </div>
    <div class="nvc-card-body">
        <p>Card content goes here.</p>
    </div>
    <div class="nvc-card-footer">
        <button class="nvc-btn nvc-btn-primary">Action</button>
    </div>
</div>
```

#### Metric Card (Using Component)
```html
{% from "components/nvc_components.html" import metric_card %}
{{ metric_card("Total Balance", "$125,430.50", "fas fa-wallet", "+5.2%", "positive") }}
```

### Forms

#### Input Field
```html
{% from "components/nvc_components.html" import form_input %}
{{ form_input("Email Address", "email", "email", "Enter your email", "fas fa-envelope", True) }}
```

#### Select Field
```html
{% from "components/nvc_components.html" import form_select %}
{{ form_select("Account Type", "account_type", [("checking", "Checking"), ("savings", "Savings")], "fas fa-university", True) }}
```

### Alerts and Notifications

#### Success Alert
```html
<div class="nvc-alert nvc-alert-success">
    <i class="fas fa-check-circle nvc-alert-icon"></i>
    <span class="nvc-alert-message">Operation completed successfully!</span>
    <button class="nvc-alert-close"><i class="fas fa-times"></i></button>
</div>
```

#### Using Component
```html
{% from "components/nvc_components.html" import notification_banner %}
{{ notification_banner("Your account has been updated successfully.", "success", True, "fas fa-check-circle") }}
```

## Layout System

### Base Template Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Meta tags and CSS -->
</head>
<body class="nvc-app">
    <!-- Navigation -->
    <nav class="nvc-navbar">...</nav>
    
    <!-- Flash Messages -->
    <div class="nvc-flash-container">...</div>
    
    <!-- Main Content -->
    <main class="nvc-main-content">
        <!-- Page Header -->
        <div class="nvc-page-header">
            <div class="nvc-page-header-content">
                <div class="nvc-page-title-section">
                    <h1 class="nvc-page-title">Page Title</h1>
                    <p class="nvc-page-description">Page description</p>
                </div>
                <div class="nvc-page-actions">
                    <!-- Page-level actions -->
                </div>
            </div>
        </div>
        
        <!-- Page Content -->
        <div class="nvc-page-content">
            <!-- Your content here -->
        </div>
    </main>
    
    <!-- Footer -->
    <footer class="nvc-footer">...</footer>
</body>
</html>
```

### Grid System

Use Bootstrap's grid system with NVC spacing:

```html
<div class="row g-4">
    <div class="col-lg-4 col-md-6">
        <!-- Content -->
    </div>
    <div class="col-lg-4 col-md-6">
        <!-- Content -->
    </div>
    <div class="col-lg-4 col-md-6">
        <!-- Content -->
    </div>
</div>
```

## Template Structure

### Basic Page Template

```html
{% extends "unified_base.html" %}
{% from "components/nvc_components.html" import metric_card, action_card %}

{% block title %}Page Title - NVC Banking Platform{% endblock %}
{% block page_title %}Page Title{% endblock %}
{% block page_description %}Brief description of the page{% endblock %}

{% block page_actions %}
<button class="nvc-btn nvc-btn-outline">
    <i class="fas fa-download"></i>
    <span class="nvc-btn-text">Export</span>
</button>
<button class="nvc-btn nvc-btn-primary">
    <i class="fas fa-plus"></i>
    <span class="nvc-btn-text">New Item</span>
</button>
{% endblock %}

{% block content %}
<div class="nvc-page-content">
    <!-- Your page content here -->
</div>
{% endblock %}
```

## Component Usage Guidelines

### When to Use Components

1. **Metric Cards**: For displaying key performance indicators and statistics
2. **Action Cards**: For navigation and quick actions
3. **Account Cards**: For displaying account information
4. **Form Components**: For all form inputs to ensure consistency
5. **Notifications**: For user feedback and alerts

### Component Customization

Components accept parameters for customization:

```html
<!-- Metric card with custom color -->
{{ metric_card("Revenue", "$50K", "fas fa-chart-line", "+15%", "positive", "success") }}

<!-- Action card with custom styling -->
{{ action_card("Transfer", "Move money between accounts", "fas fa-exchange-alt", "/transfer", "primary") }}
```

## Responsive Design

### Breakpoints

- **Mobile**: < 768px
- **Tablet**: 768px - 1024px
- **Desktop**: > 1024px

### Mobile Considerations

- Touch-friendly button sizes (minimum 44px)
- Simplified navigation
- Stacked layouts
- Larger text for readability

### Responsive Utilities

```css
/* Hide on mobile */
@media (max-width: 768px) {
    .nvc-btn-text { display: none; }
    .nvc-brand-text { display: none; }
}
```

## Accessibility Guidelines

### Color Contrast
- All text meets WCAG AA standards (4.5:1 ratio)
- Interactive elements have sufficient contrast
- Focus indicators are clearly visible

### Keyboard Navigation
- All interactive elements are keyboard accessible
- Logical tab order
- Skip links for main content

### Screen Readers
- Semantic HTML structure
- Proper ARIA labels
- Descriptive alt text for images

### Implementation
```html
<!-- Good accessibility example -->
<button class="nvc-btn nvc-btn-primary" aria-label="Create new account">
    <i class="fas fa-plus" aria-hidden="true"></i>
    <span class="nvc-btn-text">New Account</span>
</button>
```

## Performance Considerations

### CSS Optimization
- Minimal CSS bundle size
- Critical CSS inlined
- Non-critical CSS loaded asynchronously

### JavaScript
- Progressive enhancement
- Minimal JavaScript dependencies
- Efficient event handling

### Images and Icons
- SVG icons for scalability
- Optimized image formats
- Lazy loading for non-critical images

## Browser Support

### Supported Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Fallbacks
- Graceful degradation for older browsers
- Progressive enhancement approach
- Polyfills for critical features

## Development Workflow

### Setting Up
1. Use the unified base template: `unified_base.html`
2. Import required components
3. Follow the established patterns
4. Test across devices and browsers

### Code Review Checklist
- [ ] Uses unified base template
- [ ] Follows component patterns
- [ ] Responsive design implemented
- [ ] Accessibility requirements met
- [ ] Performance optimized
- [ ] Browser compatibility verified

## Migration Guide

### From Old System
1. **Backup existing templates**
2. **Run migration script**: `python scripts/migrate_to_unified_ui.py`
3. **Test all pages**
4. **Update custom styles**
5. **Replace hardcoded HTML with components**

### Common Migration Issues
- CSS class conflicts
- JavaScript compatibility
- Component parameter mismatches
- Layout structure differences

## Best Practices

### Do's
✅ Use the unified base template for all pages
✅ Leverage component macros for consistency
✅ Follow the established color system
✅ Implement responsive design patterns
✅ Test accessibility features
✅ Optimize for performance

### Don'ts
❌ Create custom base templates
❌ Hardcode styles inline
❌ Ignore responsive design
❌ Skip accessibility testing
❌ Use non-standard colors
❌ Bypass the component system

## Support and Resources

### Documentation
- [Component Library Examples](templates/examples/)
- [Migration Script](scripts/migrate_to_unified_ui.py)
- [CSS Documentation](static/css/unified-professional-theme.css)

### Getting Help
- Review example templates
- Check the migration report
- Test with the provided examples
- Follow the established patterns

---

*This design system ensures a professional, consistent, and accessible banking platform that users can trust and navigate with confidence.*