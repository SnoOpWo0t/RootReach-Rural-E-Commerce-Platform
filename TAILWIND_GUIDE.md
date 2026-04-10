# 🎨 Tailwind CSS + View Transitions API Guide

## ✅ What's Been Set Up

### 1. **Tailwind CSS (CDN)**
- Added to `base.html`
- Configured with your custom colors
- Works alongside your existing CSS

### 2. **View Transitions API** 
- Smooth page transitions when clicking links
- Auto-applied to all navigation
- Browser fallback included

### 3. **Dark Mode Integration**
- Tailwind respects your dark mode toggle
- Use `dark:` prefix for dark mode styles

---

## 🚀 Quick Start Examples

### Basic Button with Tailwind
```html
<button class="px-6 py-2 bg-primary text-white rounded-full hover:shadow-lg transition-all duration-300">
    Click Me
</button>
```

### Card Component (Mixed Approach)
```html
<!-- Keep your existing glass-card, add Tailwind for responsive -->
<div class="product-card glass-card md:flex md:gap-4 lg:flex-row">
    <img class="w-full md:w-32 rounded-lg" src="image.jpg">
    <div class="flex-1">
        <h2 class="text-xl font-bold md:text-2xl">Product Name</h2>
        <p class="text-gray-600 dark:text-gray-300 mt-2">Description</p>
    </div>
</div>
```

### Dark Mode Support
```html
<div class="bg-white dark:bg-slate-950 text-slate-900 dark:text-slate-100">
    This adapts automatically when dark mode is toggled
</div>
```

### Responsive Design (New!)
- `sm:` (640px)
- `md:` (768px)
- `lg:` (1024px)
- `xl:` (1280px)
- `2xl:` (1536px)

```html
<div class="flex flex-col md:flex-row lg:grid lg:grid-cols-3 gap-4">
    <!-- Stack on mobile, row on tablet, 3-column grid on desktop -->
</div>
```

---

## 📚 Utility Classes (Most Common)

### Spacing
- `p-4` = padding: 1rem
- `m-4` = margin: 1rem
- `gap-2` = gap: 0.5rem

### Colors
- `bg-primary`, `bg-secondary`, `bg-accent`
- `text-gray-600`, `text-red-500`, etc.
- `border-blue-200`

### Typography
- `text-sm`, `text-base`, `text-lg`, `text-2xl`
- `font-bold`, `font-semibold`, `font-normal`
- `leading-tight`, `tracking-wide`

### Flexbox/Grid
- `flex`, `flex-col`, `items-center`, `justify-between`
- `grid`, `grid-cols-3`, `gap-4`

### Rounded Corners
- `rounded`, `rounded-lg`, `rounded-full`

### Shadows & Effects
- `shadow`, `shadow-lg`, `shadow-xl`
- `opacity-50`, `blur-sm`

### Transitions
- `transition`, `duration-300`, `ease-in-out`
- `hover:bg-blue-600`, `focus:ring-2`

---

## 🎯 Conversion Strategy

### Approach 1: Gradual (Recommended)
1. Keep existing CSS/HTML as-is
2. Add Tailwind classes for new components
3. Convert one page at a time

### Approach 2: Components First
1. Extract components into reusable blocks
2. Use Tailwind for components
3. Keep page layouts in existing CSS

### Approach 3: New Features Only
1. Use Tailwind for upcoming features
2. Existing pages unchanged
3. Both work together

---

## 🔄 View Transitions in Action

View Transitions API is **automatically active**. When users click links:
- Smooth fade + slide animation
- No extra code needed
- Works on all internal navigation

To exclude a link from transitions:
```html
<a href="/about" data-no-transition>Skip Transition</a>
```

---

## 🌙 Dark Mode with Tailwind

Your theme toggle already works with Tailwind:

```html
<!-- Automatically adapts -->
<div class="bg-white dark:bg-gray-900 text-black dark:text-white">
    Toggle dark mode to see the difference
</div>
```

---

## 📝 Example: Converting Product Card

### Before (Pure CSS)
```html
<div class="product-card">
    <img src="image.jpg" class="card-image">
    <h3 class="card-title">Product Name</h3>
    <p class="card-price">$29.99</p>
</div>
```

### After (With Tailwind)
```html
<div class="product-card glass-card hover:shadow-lg transition-shadow">
    <img src="image.jpg" class="w-full h-48 object-cover rounded-t-lg">
    <div class="p-4">
        <h3 class="text-lg font-bold mb-2 dark:text-white">Product Name</h3>
        <p class="text-accent font-semibold">$29.99</p>
        <button class="w-full mt-4 px-4 py-2 bg-primary text-white rounded-lg hover:opacity-90 transition-opacity">
            Add to Cart
        </button>
    </div>
</div>
```

---

## 🛠️ Custom Configuration

Your Tailwind colors are configured in `base.html`:
```javascript
tailwind.config = {
    theme: {
        extend: {
            colors: {
                primary: '#0052cc',    // Blue
                secondary: '#00a3bf',  // Cyan
                accent: '#ffd700',     // Gold
            }
        }
    }
}
```

Use them:
- `bg-primary`, `text-primary`, `border-primary`
- `hover:bg-secondary`
- `text-accent`

---

## 🎓 Template Examples

### Navigation Bar (Partially Done)
```html
<nav class="flex items-center justify-between p-4 bg-white shadow">
    <div class="text-2xl font-bold text-primary">👜 Shop</div>
    <div class="flex gap-4">
        <a href="#" class="hover:text-primary">Home</a>
        <a href="#" class="hover:text-primary">Products</a>
        <a href="#" class="hover:text-primary">Contact</a>
    </div>
</nav>
```

### Hero Section
```html
<div class="flex flex-col items-center justify-center min-h-screen bg-gradient-to-r from-blue-500 to-cyan-500 text-white">
    <h1 class="text-5xl font-bold mb-4">Welcome to RootReach</h1>
    <p class="text-xl mb-8">Your rural marketplace</p>
    <button class="px-8 py-3 bg-white text-blue-600 font-bold rounded-lg hover:shadow-lg transition-shadow">
        Get Started
    </button>
</div>
```

### Product Grid
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4">
    {% for product in products %}
    <div class="glass-card p-4 rounded-lg hover:shadow-xl transition-shadow dark:bg-slate-800">
        <img src="{{ product.image }}" class="w-full h-40 object-cover rounded">
        <h3 class="text-lg font-bold mt-2 dark:text-white">{{ product.name }}</h3>
        <p class="text-accent font-semibold">${{ product.price }}</p>
    </div>
    {% endfor %}
</div>
```

---

## ⚙️ File Locations

- **Base template**: `core/templates/base.html` (Tailwind + View Transitions added)
- **Styles**: `core/static/css/styles.css` (Keep your existing CSS)
- **This guide**: `TAILWIND_GUIDE.md` (in root)

---

## 💡 Tips & Tricks

1. **Combine with your CSS**
   ```html
   <div class="glass-card md:flex md:gap-4"> <!-- Mix both -->
   ```

2. **Use responsive prefixes**
   ```html
   <div class="hidden md:block">Only visible on tablet+</div>
   ```

3. **Dark mode colors**
   ```html
   <div class="bg-white dark:bg-slate-900">
   ```

4. **Hover effects**
   ```html
   <button class="hover:bg-blue-600 focus:ring-2 active:scale-95">
   ```

---

## 📚 Resources

- Tailwind CSS Docs: https://tailwindcss.com/docs
- View Transitions API: https://developer.mozilla.org/en-US/docs/Web/API/View_Transitions_API
- Tailwind UI Components: https://tailwindui.com

---

## ⚡ Next Steps

1. **Test it**: Toggle dark mode, click links to see transitions
2. **Try a component**: Convert one small component to Tailwind
3. **Expand gradually**: Add Tailwind classes to new features
4. **Learn Tailwind**: Bookmark the Tailwind CSS docs

Good luck! 🚀
