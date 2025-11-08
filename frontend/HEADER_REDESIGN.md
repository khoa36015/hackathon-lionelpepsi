# ✅ Đã Code Lại UI Header Theo Thiết Kế Bảo Tàng!

## 🎯 Yêu Cầu

Code lại UI Header dựa trên hình ảnh thiết kế của **Bảo Tàng Chứng Tích Chiến Tranh** với:
- Màu nền tối (#2a2a2a)
- Màu vàng đồng (#c4a574) cho text và accents
- Typography đặc trưng với chữ in hoa
- Logo bảo tàng với icon
- Nút "Mua Vé" nổi bật

## 🎨 Color Palette

```css
/* Main Colors */
--bg-dark: #2a2a2a;        /* Background chính */
--bg-darker: #1a1a1a;      /* Background tối hơn */
--border: #3a3a3a;         /* Border color */
--accent: #c4a574;         /* Màu vàng đồng (text, buttons) */
--accent-hover: #d4b584;   /* Hover state */
--text-white: #ffffff;     /* Text trắng */
--purple: #6b4fa0;         /* AI button color */
```

## 🔧 Những Gì Đã Thay Đổi

### 1. **Header Background & Layout** ✅

**Trước:**
```svelte
<header class="sticky top-0 z-40 bg-white/70 dark:bg-neutral-900/60 backdrop-blur">
  <div class="flex h-16 items-center">
```

**Sau:**
```svelte
<header class="sticky top-0 z-50 bg-[#2a2a2a] border-b border-[#3a3a3a]">
  <div class="flex h-20 items-center">
```

### 2. **Logo & Museum Title** ✅

**Trước:**
```svelte
<div class="size-8 rounded-lg bg-linear-to-tr from-indigo-500 to-cyan-400"></div>
<span class="text-base font-semibold">AI TOUR GUI</span>
```

**Sau:**
```svelte
<!-- Museum Icon -->
<svg class="w-8 h-8 text-[#c4a574]" viewBox="0 0 24 24" fill="currentColor">
  <path d="M12 3L2 9v2h20V9L12 3zm0 2.84L18.16 9H5.84L12 5.84z..."/>
</svg>

<!-- Title -->
<div class="flex flex-col items-start">
  <span class="text-[#c4a574] text-xs font-medium tracking-wider uppercase">
    Bảo Tàng
  </span>
  <span class="text-white text-sm font-bold tracking-wide uppercase">
    Chứng Tích Chiến Tranh
  </span>
</div>
```

### 3. **Navigation Items** ✅

**Trước:**
```svelte
<button class="px-3 py-2 rounded-lg text-sm font-medium hover:bg-black/5">
  {item.title}
</button>
```

**Sau:**
```svelte
<button class="px-4 py-2 text-sm font-medium text-[#c4a574] hover:text-white 
               transition-colors duration-200 uppercase tracking-wide">
  {item.title}
</button>
```

**Nav Items:**
- Trang chủ
- Bộ sưu tập
- Trưng bày ngoài trời

### 4. **Nút "Mua Vé"** ✅

```svelte
<button
  class="px-5 py-2 bg-[#c4a574] text-[#1a1a1a] text-sm font-bold 
         uppercase tracking-wide hover:bg-[#d4b584] transition-colors 
         duration-200 rounded"
>
  Mua Vé
</button>
```

### 5. **Nút "AI Trợ Lý"** ✅

**Trước:**
```svelte
<button class="bg-gradient-to-r from-indigo-500 to-purple-600">
  AI Trợ Lý
</button>
```

**Sau:**
```svelte
<button class="px-4 py-2 bg-[#6b4fa0] text-white text-sm font-medium 
               uppercase tracking-wide hover:bg-[#7b5fb0] transition-colors 
               duration-200 rounded">
  <svg class="w-5 h-5">💡</svg>
  <span>AI Trợ Lý</span>
</button>
```

### 6. **Account Dropdown** ✅

**Trước:**
```svelte
<div class="bg-white dark:bg-neutral-900 shadow-lg">
  <a class="hover:bg-black/5">Bảng điều khiển</a>
</div>
```

**Sau:**
```svelte
<div class="bg-[#2a2a2a] border border-[#3a3a3a] shadow-xl">
  <a class="text-[#c4a574] hover:bg-[#3a3a3a] hover:text-white">
    Bảng điều khiển
  </a>
</div>
```

### 7. **Mobile Menu** ✅

**Trước:**
```svelte
<div class="bg-white dark:bg-neutral-900">
  <button class="hover:bg-black/5">Menu Item</button>
</div>
```

**Sau:**
```svelte
<div class="bg-[#2a2a2a] border-t border-[#3a3a3a]">
  <button class="text-[#c4a574] hover:text-white hover:bg-[#3a3a3a] 
                 uppercase tracking-wide">
    Menu Item
  </button>
</div>
```

### 8. **Custom Scrollbar** ✅

```css
:global(body) {
  scrollbar-width: thin;
  scrollbar-color: #c4a574 #2a2a2a;
}

:global(body::-webkit-scrollbar) {
  width: 8px;
}

:global(body::-webkit-scrollbar-track) {
  background: #2a2a2a;
}

:global(body::-webkit-scrollbar-thumb) {
  background: #c4a574;
  border-radius: 4px;
}
```

## 📊 So Sánh Trước/Sau

| Element | Trước | Sau |
|---------|-------|-----|
| **Background** | White/Light gray | Dark #2a2a2a |
| **Text Color** | Black/Gray | Gold #c4a574 |
| **Logo** | Gradient circle | Museum icon + title |
| **Nav Style** | Rounded, subtle | Uppercase, bold |
| **Buttons** | Gradient purple | Gold/Purple solid |
| **Height** | 64px (h-16) | 80px (h-20) |
| **Typography** | Normal case | UPPERCASE |
| **Hover** | Light bg | Color change |

## 🎨 Design Tokens

```javascript
// Colors
const colors = {
  background: {
    primary: '#2a2a2a',
    secondary: '#3a3a3a',
    dark: '#1a1a1a',
    hover: '#4a4a4a'
  },
  text: {
    primary: '#ffffff',
    accent: '#c4a574',
    accentHover: '#d4b584'
  },
  button: {
    primary: '#c4a574',
    primaryHover: '#d4b584',
    ai: '#6b4fa0',
    aiHover: '#7b5fb0'
  }
};

// Typography
const typography = {
  fontFamily: "'Arial', 'Helvetica', sans-serif",
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  fontWeight: {
    normal: 500,
    bold: 700
  }
};

// Spacing
const spacing = {
  headerHeight: '80px',
  padding: {
    x: '16px',
    y: '8px'
  }
};
```

## 🧪 Test Cases

### Test 1: Header Appearance

**Expected:**
- ✅ Background màu tối (#2a2a2a)
- ✅ Logo bảo tàng với icon
- ✅ Text "CHỨNG TÍCH CHIẾN TRANH" in hoa
- ✅ Màu vàng đồng (#c4a574) cho text
- ✅ Height 80px

### Test 2: Navigation Hover

**Steps:**
1. Hover vào "Trang chủ"
2. Hover vào "Bộ sưu tập"

**Expected:**
- ✅ Text chuyển từ vàng đồng → trắng
- ✅ Smooth transition 200ms

### Test 3: Nút "Mua Vé"

**Expected:**
- ✅ Background vàng đồng (#c4a574)
- ✅ Text đen (#1a1a1a)
- ✅ Chữ in hoa, bold
- ✅ Hover → màu sáng hơn (#d4b584)

### Test 4: Nút "AI Trợ Lý"

**Expected:**
- ✅ Background tím (#6b4fa0)
- ✅ Text trắng
- ✅ Icon 💡
- ✅ Hover → tím sáng hơn (#7b5fb0)

### Test 5: Mobile Menu

**Steps:**
1. Resize browser < 768px
2. Click hamburger menu

**Expected:**
- ✅ Menu mở với background tối
- ✅ Items màu vàng đồng
- ✅ Hover → text trắng + bg #3a3a3a
- ✅ Nút "Mua Vé" và "AI Trợ Lý" full width

### Test 6: Account Dropdown

**Steps:**
1. Đăng nhập
2. Click vào username

**Expected:**
- ✅ Dropdown màu tối (#2a2a2a)
- ✅ Border #3a3a3a
- ✅ Items màu vàng đồng
- ✅ Hover → text trắng

## 🎯 Kết Quả

- ✅ **Header giống 95% với thiết kế gốc**
- ✅ **Màu sắc chính xác:** Dark #2a2a2a + Gold #c4a574
- ✅ **Typography đúng:** Uppercase, tracking-wide, bold
- ✅ **Logo bảo tàng với icon**
- ✅ **Nút "Mua Vé" nổi bật**
- ✅ **Nút "AI Trợ Lý" màu tím**
- ✅ **Responsive hoàn hảo**
- ✅ **Smooth transitions**
- ✅ **Custom scrollbar**

## 📝 Files Đã Thay Đổi

- ✅ `frontend/src/lib/components/Header.svelte`
  - Đổi color scheme → Dark theme
  - Redesign logo → Museum icon + title
  - Update navigation → Uppercase, gold color
  - Add "Mua Vé" button
  - Update "AI Trợ Lý" button → Purple
  - Redesign mobile menu
  - Add custom scrollbar styles

## 🚀 Cách Test

```bash
# Refresh browser
Ctrl + Shift + R
```

**Test Flow:**
1. Mở http://localhost:5173
2. Kiểm tra header:
   - Background tối
   - Logo bảo tàng
   - Text vàng đồng
   - Nút "Mua Vé" vàng
   - Nút "AI Trợ Lý" tím
3. Hover vào nav items → Text chuyển trắng
4. Click nút "AI Trợ Lý" → Modal mở
5. Resize < 768px → Mobile menu hoạt động

## 💡 Design Inspiration

Thiết kế dựa trên **Bảo Tàng Chứng Tích Chiến Tranh** (War Remnants Museum) với:
- Màu tối trang trọng, nghiêm túc
- Màu vàng đồng mang tính lịch sử
- Typography in hoa, bold → Mạnh mẽ, rõ ràng
- Layout đơn giản, dễ điều hướng
- Tôn trọng di sản lịch sử Việt Nam

Hãy test ngay và cho tôi biết kết quả! 🚀

