# WhatsApp Link Preview Image

This guide explains how to make a website show a preview image when its link is shared through WhatsApp and other social apps.

The same approach also works for Facebook, Telegram, Signal, LinkedIn, Discord, X/Twitter, and many other services because they read Open Graph metadata from the HTML page.

## 1. Create a Social Preview Image

Create a PNG image for the preview card.

Recommended size:

```text
1200 x 630 pixels
```

Recommended format:

```text
PNG or JPG
```

For this project, the image is located at:

```text
docs/assets/social-preview.png
```

Important recommendations:

- Use a real image file, not only an SVG favicon.
- Keep the main title large and centered.
- Avoid placing important text close to the edges.
- Use high contrast so the image is readable in small previews.
- Keep the file reasonably small.

## 2. Add Open Graph Tags

Inside the `<head>` section of your HTML page, add Open Graph metadata.

Example:

```html
<meta property="og:type" content="website">
<meta property="og:site_name" content="Lucio IVA Calculator">
<meta property="og:title" content="Lucio IVA Calculator">
<meta property="og:description" content="Desktop VAT calculator for Windows, Linux, and macOS.">
<meta property="og:url" content="https://wachin.github.io/lucio-iva-calculator/">
<meta property="og:image" content="https://wachin.github.io/lucio-iva-calculator/assets/social-preview.png">
<meta property="og:image:secure_url" content="https://wachin.github.io/lucio-iva-calculator/assets/social-preview.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Lucio IVA Calculator preview image">
```

The most important tag is:

```html
<meta property="og:image" content="https://example.com/path/to/social-preview.png">
```

WhatsApp needs a public image URL that it can download.

## 3. Use Absolute Public URLs

For social previews, use absolute URLs instead of relative paths.

Good:

```html
<meta property="og:image" content="https://wachin.github.io/lucio-iva-calculator/assets/social-preview.png">
```

Avoid:

```html
<meta property="og:image" content="assets/social-preview.png">
```

Relative paths may work in a browser, but some social apps do not resolve them correctly when generating previews.

## 4. Add Twitter Card Tags

These tags are useful for X/Twitter and some other services.

```html
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Lucio IVA Calculator">
<meta name="twitter:description" content="Desktop VAT calculator for Windows, Linux, and macOS.">
<meta name="twitter:image" content="https://wachin.github.io/lucio-iva-calculator/assets/social-preview.png">
```

## 5. Add a Canonical URL

This helps crawlers understand the official URL of the page.

```html
<link rel="canonical" href="https://wachin.github.io/lucio-iva-calculator/">
```

## 6. Publish the Changes

If the site is hosted with GitHub Pages, commit and push the updated HTML file and preview image.

Example:

```bash
git add docs/index.html docs/assets/social-preview.png
git commit -m "docs: add social preview metadata"
git push origin main
```

Wait until GitHub Pages finishes publishing the site.

## 7. WhatsApp Cache

WhatsApp caches link previews aggressively. If the preview does not update immediately, this does not always mean the metadata is wrong.

Useful tricks:

- Wait a few minutes and try again.
- Test with a small URL variation:

```text
https://wachin.github.io/lucio-iva-calculator/?v=2
```

- Use another chat or another device to test.
- Make sure the image URL opens directly in a browser.

## 8. Debugging Checklist

If the preview image does not appear, check these points:

- The page has `og:image`.
- The `og:image` URL is absolute and public.
- The image URL uses HTTPS.
- The image file opens directly in a browser.
- The image is not blocked by authentication.
- The image is PNG or JPG.
- The image is close to `1200x630`.
- The page has already been deployed.
- WhatsApp is not showing an old cached preview.

## 9. Example Used in This Project

This project uses:

```html
<meta property="og:image" content="https://wachin.github.io/lucio-iva-calculator/assets/social-preview.png">
<meta property="og:image:secure_url" content="https://wachin.github.io/lucio-iva-calculator/assets/social-preview.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
```

And the preview image is:

```text
docs/assets/social-preview.png
```

This made the website display a proper preview image when shared through WhatsApp.
