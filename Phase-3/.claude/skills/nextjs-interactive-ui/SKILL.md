---
name: nextjs-interactive-ui
description: Build stunning, interactive, and fully responsive frontend UIs using Next.js with reusable components, modern layouts, animations, and smooth user experiences.
---

# Next.js Interactive Frontend UI

## Instructions

1. **App Structure (Next.js)**
   - Use App Router (`app/` directory)
   - Layouts with `layout.tsx`
   - Page-based routing with `page.tsx`
   - Reusable UI components in `components/`
   - Global styles and design tokens

2. **Layout & Responsiveness**
   - Mobile-first responsive design
   - CSS Grid and Flexbox
   - Adaptive spacing and typography
   - Consistent layout patterns across pages

3. **Component Architecture**
   - Reusable and composable components
   - Props and variants for flexibility
   - Server vs Client Components awareness
   - Clean separation of UI and logic

4. **Styling & Visual Design**
   - Tailwind CSS or CSS Modules
   - Modern gradients and shadows
   - Glassmorphism / depth effects
   - Dark and light mode support
   - Consistent design system

5. **Interactivity & UX**
   - Client Components for interactions
   - Hover, focus, and active states
   - Interactive menus, modals, drawers
   - Keyboard and accessibility support

6. **Animations & Motion**
   - CSS transitions or Framer Motion
   - Page and component entrance animations
   - Scroll-based animations
   - Performance-optimized motion

## Best Practices
- Prefer Server Components by default
- Use Client Components only when needed
- Keep components small and reusable
- Optimize images with `next/image`
- Use `next/link` for navigation
- Ensure accessibility and performance
- Test on all screen sizes

## Example Structure
```tsx
// app/page.tsx
import Hero from "@/components/Hero";
import Features from "@/components/Features";

export default function HomePage() {
  return (
    <main className="container mx-auto px-4">
      <Hero />
      <Features />
    </main>
  );
}


// components/Hero.tsx
"use client";

export default function Hero() {
  return (
    <section className="min-h-screen flex flex-col justify-center items-center text-center">
      <h1 className="text-5xl font-bold mb-4 animate-fade-up">
        Build Stunning UIs
      </h1>
      <p className="max-w-xl text-lg opacity-80 mb-6">
        Interactive, modern, and responsive Next.js interfaces.
      </p>
      <button className="btn-primary">
        Get Started
      </button>
    </section>
  );
}


/* globals.css */

.btn-primary {
  padding: 12px 30px;
  border-radius: 999px;
  background: linear-gradient(135deg, #7f5cff, #00d4ff);
  color: white;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.btn-primary:hover {
  transform: scale(1.05);
  box-shadow: 0 0 35px rgba(127,92,255,0.6);
}

.animate-fade-up {
  animation: fadeUp 0.8s ease both;
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
