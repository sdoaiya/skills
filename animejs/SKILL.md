---
name: animejs
description: Use when implementing or reviewing frontend motion with Anime.js / animejs, including JavaScript animation, timeline choreography, staggered lists, SVG motion, text reveal, scroll-triggered effects, WAAPI tradeoffs, React/Vue component animation, or replacing CSS-only motion with a more controlled animation sequence.
---

# Anime.js Motion

## Overview

Use Anime.js when the interface needs coordinated motion that is hard to express cleanly with CSS transitions alone: staggered entrance, timeline choreography, SVG drawing, text reveal, drag/scroll-linked motion, or multiple transform properties with different timing.

Default to the smallest animation that clarifies state. Motion should communicate hierarchy, continuity, and causality; it should not decorate every element.

## First Checks

Before writing code:

- Confirm `animejs` is installed. If not, use the project package manager to add it.
- Prefer Anime.js v4 ESM imports: `import { animate, timeline, stagger } from 'animejs';`.
- Respect `prefers-reduced-motion`; skip or simplify non-essential movement.
- Animate compositor-friendly properties first: `transform`, `opacity`, CSS variables that affect transforms, or SVG attributes. Avoid animating layout-heavy properties unless necessary.
- In React / Vue / Svelte, create animations in lifecycle hooks and clean them up on unmount.

## Choosing The Pattern

| Goal | Prefer |
|---|---|
| One element or one group changes state | `animate()` |
| Multiple elements enter with rhythm | `animate()` + `stagger()` |
| Several steps must happen in sequence or overlap | `timeline()` |
| Basic one-off transform / opacity motion | CSS transition, unless coordination is needed |
| Large lists, scroll pages, or expensive DOM | Keep targets narrow; consider WAAPI or CSS first |
| Users may request reduced motion | Provide an instant or fade-only path |

## Core Patterns

### Direct Animation

```ts
import { animate, stagger } from 'animejs';

const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

if (!motionQuery.matches) {
  animate('.card', {
    opacity: { from: 0, to: 1 },
    y: { from: 16, to: 0 },
    duration: 520,
    delay: stagger(55, { from: 'first' }),
    ease: 'outCubic',
  });
}
```

Use property objects when a property needs its own `from`, `to`, `delay`, `duration`, or `ease`. Keep durations short for UI feedback and slightly longer for page-level reveals.

### Timeline Choreography

```ts
import { timeline, stagger } from 'animejs';

const tl = timeline({
  defaults: {
    ease: 'outExpo',
    duration: 650,
  },
});

tl.add('.hero-title', {
  opacity: { from: 0, to: 1 },
  y: { from: 24, to: 0 },
})
.add('.hero-copy', {
  opacity: { from: 0, to: 1 },
  y: { from: 12, to: 0 },
}, '-=420')
.add('.feature-card', {
  opacity: { from: 0, to: 1 },
  y: { from: 18, to: 0 },
  delay: stagger(70),
}, '-=260');
```

Use offsets intentionally. If every step starts after the previous one ends, the UI often feels slow; overlap related steps.

## Framework Integration

### React

```tsx
import { useEffect, useRef } from 'react';
import { animate, stagger } from 'animejs';

export function FeatureGrid() {
  const rootRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const root = rootRef.current;
    if (!root) return;

    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduced) return;

    const animation = animate(root.querySelectorAll('.feature-card'), {
      opacity: { from: 0, to: 1 },
      y: { from: 14, to: 0 },
      delay: stagger(60),
      duration: 480,
      ease: 'outCubic',
    });

    return () => animation.pause();
  }, []);

  return <div ref={rootRef}>{/* cards */}</div>;
}
```

Keep selectors scoped to a root ref so the animation does not leak into other components. Pause or cancel animations during cleanup when the returned object supports it.

## Motion Taste

- Give entering elements a direction that matches layout flow.
- Use `stagger()` for groups, but keep delays tight; long cascades make interfaces feel sluggish.
- Prefer `outCubic`, `outExpo`, `inOutCubic`, or spring-like eases for product UI. Avoid aggressive elastic motion unless the brand is playful.
- Combine opacity with small transform changes; avoid large fly-ins unless they explain spatial origin.
- Do not animate focus rings, typed input, form validation errors, or critical alerts in ways that delay comprehension.
- For loops, ask whether the motion is ambient and useful. Most UI loops should stop after one cycle.

## Common Mistakes

| Mistake | Better |
|---|---|
| Animating `top`, `left`, `width`, or `height` for polish | Use `transform` or CSS variables when possible |
| Global selectors like `.card` in component code | Scope targets under a local root ref |
| Long chained timelines for simple hover states | Use CSS transitions |
| No reduced-motion path | Skip, shorten, or fade only |
| Animating all page sections on load | Animate the first meaningful region, then use interaction or viewport triggers |
| Adding Anime.js just for one opacity transition | Use CSS unless coordination or runtime control is needed |

## Verification

After implementing:

- Check the animation runs once in the intended scope and does not replay unexpectedly on rerender.
- Test reduced-motion behavior.
- Inspect performance for layout thrash or jank.
- Confirm keyboard and screen-reader flows are not blocked by animation timing.
- Remove unused imports and avoid leaving global animation side effects.
