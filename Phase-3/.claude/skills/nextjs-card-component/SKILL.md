---
name: nextjs-card-component
description: Build modern, accessible card components in Next.js with Tailwind CSS, including shadow effects, hover animations, responsive grids, and optimized images using next/image. Use when creating card layouts, product grids, content galleries, or any UI requiring card-based designs in Next.js applications.
---

# Next.js Card Components

Build production-ready card components in Next.js with proper shadows, smooth animations, responsive layouts, Image optimization, and accessibility best practices.

## Core Card Component

Create a reusable card component using TypeScript and Tailwind CSS:

```tsx
// components/Card.tsx
import Image from 'next/image';
import Link from 'next/link';

interface CardProps {
  title: string;
  description: string;
  imageUrl: string;
  imageAlt: string;
  href: string;
  badge?: string;
}

export default function Card({
  title,
  description,
  imageUrl,
  imageAlt,
  href,
  badge,
}: CardProps) {
  return (
    <article className="group relative bg-white rounded-xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 hover:-translate-y-2">
      {badge && (
        <span className="absolute top-4 left-4 z-10 bg-blue-600 text-white text-xs font-semibold px-3 py-1 rounded-full">
          {badge}
        </span>
      )}
      
      <div className="relative h-48 w-full overflow-hidden bg-gray-200">
        <Image
          src={imageUrl}
          alt={imageAlt}
          fill
          sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
          className="object-cover transition-transform duration-300 group-hover:scale-105"
          loading="lazy"
        />
      </div>
      
      <div className="p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          {title}
        </h3>
        <p className="text-gray-600 mb-4 line-clamp-3">
          {description}
        </p>
        <Link
          href={href}
          className="inline-flex items-center text-blue-600 font-medium hover:text-blue-700 transition-colors"
          aria-label={`Read more about ${title}`}
        >
          Read More
          <svg 
            className="ml-2 w-4 h-4 transition-transform group-hover:translate-x-1" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </Link>
      </div>
    </article>
  );
}
```

## Image Optimization with next/image

Always use Next.js Image component for automatic optimization:

```tsx
import Image from 'next/image';

// Responsive image with proper sizing
<div className="relative aspect-video w-full overflow-hidden">
  <Image
    src="/images/card-image.jpg"
    alt="Descriptive alt text"
    fill
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
    className="object-cover"
    priority={false} // Use true for above-the-fold images
    quality={85}
  />
</div>

// With placeholder blur (requires blurDataURL)
<Image
  src="/images/card-image.jpg"
  alt="Descriptive alt text"
  width={800}
  height={450}
  placeholder="blur"
  blurDataURL="data:image/jpeg;base64,..."
  className="object-cover"
/>
```

**Key Image Optimization Rules:**
- Use `fill` with `sizes` for responsive images
- Set `priority={true}` only for above-the-fold images
- Use `loading="lazy"` (default) for below-fold images
- Specify proper `sizes` based on your grid breakpoints
- Use aspect ratio classes (`aspect-video`, `aspect-square`)

## Shadow System with Tailwind

Use Tailwind's shadow utilities for consistent elevation:

```tsx
// Base shadow levels
<div className="shadow-sm">      {/* Subtle */}
<div className="shadow">         {/* Default */}
<div className="shadow-md">      {/* Medium */}
<div className="shadow-lg">      {/* Large */}
<div className="shadow-xl">      {/* Extra large */}
<div className="shadow-2xl">     {/* 2X large */}

// Hover shadow transitions
<div className="shadow-md hover:shadow-xl transition-shadow duration-300">

// Combined with transform
<div className="shadow-md hover:shadow-xl hover:-translate-y-2 transition-all duration-300">
```

## Hover Animations

Implement smooth, accessible hover effects with Tailwind:

```tsx
// Lift effect
<div className="transition-all duration-300 hover:-translate-y-2 hover:shadow-xl">

// Scale effect
<div className="transition-transform duration-300 hover:scale-105">

// Image zoom inside card
<div className="overflow-hidden">
  <Image 
    className="transition-transform duration-300 group-hover:scale-110" 
    {...imageProps}
  />
</div>

// Respect reduced motion
// Add to tailwind.config.js:
module.exports = {
  theme: {
    extend: {
      transitionProperty: {
        'DEFAULT': 'all',
      },
    },
  },
  plugins: [],
}

// Then use motion-safe/motion-reduce
<div className="motion-safe:transition-transform motion-safe:hover:-translate-y-2">
```

## Responsive Grid Layouts

Create responsive card grids using Tailwind Grid:

```tsx
// Auto-responsive grid
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  {cards.map((card) => (
    <Card key={card.id} {...card} />
  ))}
</div>

// Equal height cards
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 auto-rows-fr">

// With container
<div className="container mx-auto px-4 py-8">
  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
    {/* Cards */}
  </div>
</div>

// Masonry-style (with @tailwindcss/container-queries)
<div className="columns-1 sm:columns-2 lg:columns-3 gap-6 space-y-6">
  {cards.map((card) => (
    <div key={card.id} className="break-inside-avoid">
      <Card {...card} />
    </div>
  ))}
</div>
```

## Card Grid Component

Create a reusable grid component:

```tsx
// components/CardGrid.tsx
import { ReactNode } from 'react';

interface CardGridProps {
  children: ReactNode;
  columns?: {
    default?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
  };
  gap?: 'sm' | 'md' | 'lg';
}

export default function CardGrid({ 
  children, 
  columns = { default: 1, sm: 2, lg: 3 },
  gap = 'md' 
}: CardGridProps) {
  const gapClasses = {
    sm: 'gap-4',
    md: 'gap-6',
    lg: 'gap-8',
  };

  const colClasses = [
    `grid-cols-${columns.default || 1}`,
    columns.sm && `sm:grid-cols-${columns.sm}`,
    columns.md && `md:grid-cols-${columns.md}`,
    columns.lg && `lg:grid-cols-${columns.lg}`,
    columns.xl && `xl:grid-cols-${columns.xl}`,
  ].filter(Boolean).join(' ');

  return (
    <div className={`grid ${colClasses} ${gapClasses[gap]}`}>
      {children}
    </div>
  );
}

// Usage
<CardGrid columns={{ default: 1, sm: 2, lg: 3, xl: 4 }} gap="lg">
  {cards.map((card) => <Card key={card.id} {...card} />)}
</CardGrid>
```

## Advanced Card Variants

### Horizontal Card

```tsx
// components/HorizontalCard.tsx
export default function HorizontalCard({ title, description, imageUrl, href }: CardProps) {
  return (
    <article className="flex flex-col md:flex-row bg-white rounded-xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-300">
      <div className="relative w-full md:w-2/5 h-48 md:h-auto">
        <Image
          src={imageUrl}
          alt={title}
          fill
          sizes="(max-width: 768px) 100vw, 40vw"
          className="object-cover"
        />
      </div>
      <div className="flex-1 p-6">
        <h3 className="text-2xl font-semibold mb-3">{title}</h3>
        <p className="text-gray-600 mb-4">{description}</p>
        <Link href={href} className="text-blue-600 hover:text-blue-700 font-medium">
          Read More →
        </Link>
      </div>
    </article>
  );
}
```

### Interactive Card

```tsx
// components/InteractiveCard.tsx
'use client';

import { useState } from 'react';
import Image from 'next/image';

export default function InteractiveCard({ title, description, imageUrl }: CardProps) {
  const [isLiked, setIsLiked] = useState(false);

  return (
    <article className="relative bg-white rounded-xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 group">
      <button
        onClick={() => setIsLiked(!isLiked)}
        className="absolute top-4 right-4 z-10 p-2 bg-white/90 rounded-full hover:bg-white transition-colors"
        aria-label={isLiked ? 'Unlike' : 'Like'}
      >
        <svg
          className={`w-5 h-5 ${isLiked ? 'fill-red-500 text-red-500' : 'fill-none text-gray-600'}`}
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      </button>
      
      <div className="relative h-48 w-full">
        <Image src={imageUrl} alt={title} fill className="object-cover" />
      </div>
      
      <div className="p-6">
        <h3 className="text-xl font-semibold mb-2">{title}</h3>
        <p className="text-gray-600">{description}</p>
      </div>
    </article>
  );
}
```

## Accessibility Requirements

Ensure all cards meet WCAG standards:

```tsx
// Semantic HTML structure
<article role="article" aria-labelledby={`card-title-${id}`}>
  <h3 id={`card-title-${id}`}>{title}</h3>
  {/* Content */}
</article>

// Focus states (Tailwind)
<div className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-600 focus-visible:outline-offset-2">

// Keyboard navigation for interactive cards
<Link 
  href={href}
  className="focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-600 focus-visible:ring-offset-2 rounded-xl"
>
  <article className="...">
    {/* Card content */}
  </article>
</Link>

// Screen reader text
<span className="sr-only">Additional context for screen readers</span>

// Proper button labels
<button aria-label={`Add ${title} to cart`}>
  <PlusIcon className="w-5 h-5" />
</button>
```

## Complete Page Example

```tsx
// app/products/page.tsx
import Card from '@/components/Card';
import CardGrid from '@/components/CardGrid';

interface Product {
  id: string;
  title: string;
  description: string;
  imageUrl: string;
  href: string;
}

async function getProducts(): Promise<Product[]> {
  // Fetch from API or database
  return [
    {
      id: '1',
      title: 'Premium Headphones',
      description: 'High-quality wireless headphones with noise cancellation.',
      imageUrl: '/images/headphones.jpg',
      href: '/products/headphones',
    },
    // More products...
  ];
}

export default async function ProductsPage() {
  const products = await getProducts();

  return (
    <main className="container mx-auto px-4 py-12">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">
          Our Products
        </h1>
        <p className="text-lg text-gray-600">
          Discover our latest collection
        </p>
      </div>

      <CardGrid 
        columns={{ default: 1, sm: 2, lg: 3, xl: 4 }} 
        gap="lg"
      >
        {products.map((product) => (
          <Card
            key={product.id}
            title={product.title}
            description={product.description}
            imageUrl={product.imageUrl}
            imageAlt={product.title}
            href={product.href}
          />
        ))}
      </CardGrid>
    </main>
  );
}
```

## Loading States

Show skeleton cards while data loads:

```tsx
// components/CardSkeleton.tsx
export default function CardSkeleton() {
  return (
    <div className="bg-white rounded-xl overflow-hidden shadow-md animate-pulse">
      <div className="h-48 bg-gray-300" />
      <div className="p-6">
        <div className="h-6 bg-gray-300 rounded w-3/4 mb-3" />
        <div className="h-4 bg-gray-300 rounded w-full mb-2" />
        <div className="h-4 bg-gray-300 rounded w-5/6 mb-4" />
        <div className="h-4 bg-gray-300 rounded w-24" />
      </div>
    </div>
  );
}

// Usage with Suspense
import { Suspense } from 'react';

<Suspense fallback={
  <CardGrid columns={{ default: 1, sm: 2, lg: 3 }}>
    {Array.from({ length: 6 }).map((_, i) => (
      <CardSkeleton key={i} />
    ))}
  </CardGrid>
}>
  <ProductCards />
</Suspense>
```

## Performance Optimization

1. **Use Server Components by default** - Only add 'use client' when needed
2. **Image optimization** - Always use next/image with proper sizes
3. **Lazy loading** - Use loading="lazy" for below-fold images
4. **Dynamic imports** - Code-split heavy card features
5. **Memoization** - Use React.memo for expensive card renders

```tsx
// Memoized card component
import { memo } from 'react';

const Card = memo(function Card({ title, description, imageUrl, href }: CardProps) {
  // Component implementation
});

export default Card;
```

## Best Practices Checklist

- [ ] Use TypeScript for type safety
- [ ] Use next/image for all card images
- [ ] Specify proper `sizes` attribute for responsive images
- [ ] Use Tailwind's shadow utilities consistently
- [ ] Add hover states with transition classes
- [ ] Include `motion-safe:` prefix for animations
- [ ] Use semantic HTML (`<article>`, proper headings)
- [ ] Implement proper focus states with `focus-visible:`
- [ ] Add ARIA labels for interactive elements
- [ ] Use next/link for internal navigation
- [ ] Ensure color contrast meets WCAG AA (4.5:1)
- [ ] Test keyboard navigation (Tab, Enter)
- [ ] Verify screen reader compatibility
- [ ] Add loading states for async data
- [ ] Optimize with Server Components when possible

## Common Patterns

**Card as Link:**
```tsx
<Link href={href} className="block group">
  <article className="...">
    {/* Card content */}
  </article>
</Link>
```

**Card with Action Buttons:**
```tsx
<div className="flex items-center justify-between p-4 border-t">
  <button className="px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg">
    Save
  </button>
  <button className="px-4 py-2 bg-blue-600 text-white hover:bg-blue-700 rounded-lg">
    View Details
  </button>
</div>
```

**Responsive Card Height:**
```tsx
// Equal height cards in grid
<div className="grid auto-rows-fr ...">
  <div className="flex flex-col h-full">
    {/* Card content with flex-1 on description */}
  </div>
</div>
```