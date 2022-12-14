# Styling

Styling your webcomic site can be done in two ways, **Basic** and **Advanced**. These may be seamlessly combined, of course. Anything you want to do, try first in the basic way, and if it can't be done, you can resort to advanced.

## Basic Styling

Open the `vars.scss` file in your `_source` folder. Here you will be able to set variables to affect the look of your comic. Here's an example of how you can set a few colours:

```scss
$color-bg: #252525;
$color-fg: #eee;
$color-links: #3BD1E9;
```

All variables you don't set remain at their gutta defaults.

You may set certain variables to external imported fonts (if using the font is within your legal rights!). To do so, for example to use a font from Google Fonts, pick up the @import statement, copy paste it anywhere in `vars.scss`, and then you can set the variable at any point after the `@import...` line. Example

```scss
//copied this from Google Fonts --v--
@import url('https://fonts.googleapis.com/css?family=Lato:100,300,400,700|Source+Sans+Pro:300,400,600,700&display=swap');
//copied Google Fonts' recommendation for usage --v--
$font-main: 'Lato', sans-serif;
```

This is the list of all currently supported variables:

| | |
| -- | -- |
| **Sizes** | |
| `$sidebox-width` | width of the infoboxes on the side in scroll mode
| `$site-max-width` | width of the main website column (will fit if screen is narrower) |
| `$extra-page-max-width` | width of the content of an extra page (will fit if screen is narrower) |
| **Colors** | |
| `$color-accent` | default colour of text |
| `$color-bg` | background colour of the webpage |
| `$color-fg` | default colour of text |
| `$color-galleryentry-bg` | background colour of gallery entry cards |
| `$color-links` | colour of links |
| `$color-links-hover` | colour of links when hovered on with the cursor |
| `$color-navlinks` | colour of navbar links |
| `$color-navlinks-hover` | colour of navbar links when hovered on |
| `$color-scrollcontent-bg` | background colour of content of scroll pages - this colour is displayed under a comic image while it's loading. |
| **Fonts** | |
| `$font-main` | primary font (used for navbar and titles) |
| `$font-weight-main` | weight (normal/bold/etc...) of main font|
| `$font-text` | text font (used for paragraphs and descriptions) |
| `$font-weight-text` | weight (normal/bold/etc...) of text font|
| **Layout** | |
| `$gallery-columns-xs` | number of columns in gallery layout on screens narrower than 576px |
| `$gallery-columns-sm` | number of columns in gallery layout on screens with width between 576px and 768px |
| `$gallery-columns-md` | number of columns in gallery layout on screens with width between 768px and 992px |
| `$gallery-columns-lg` | number of columns in gallery layout on screens wider than 992px |






## Advanced Styling

Using your browser's inspector check out the source of your website, and note the classes of elements in the page. A lot of elements have been assigned specific classes that begin with `.gutta-`; these are intended for you to manually style as you please.

Open `style.scss`, and write the css overrides you desire for these classes (or any other one really). For example

```scss
.gutta-navbar {
    text-transform: lowercase;
    font-variant: small-caps;
}
```

rebuild your website and these should now apply. Rinse and repeat.

### Referencing assets in the stylesheets

When you want to reference assets (like images) in `style.scss` using the `url()` function you'll need to refer to the assets folder as `../_assets/`. The reason is that these URLs are relative to the location of the final stylesheet built by gutta, which is going to be `static/wc.css` (not the webpage where the sheet is used!). So for example:

```scss
.some-element{
    background-image: url("../_assets/my_bg.jpg");
}
```

## Everything in its right place.

**Note**: do not place CSS overrides in `vars.scss`, and do not place gutta variables settings in `style.scss`, or things may not work as intended. This is what's going on behind the scenes when you build:

An overall scss source is assembled from, **in order**, 
* your `vars.scss`, 
* gutta's internal stylesheet, and 
* your `style.scss`. 

Gutta's stylesheet establishes `!default` values for the variables, which means they're only overwritten if `vars.scss` hasn't already defined them, and then *uses* these variables for the default stylings, and then `style.scss` applies on top of that. 

When the whole source is assembled, it is then compiled and minified into `static/wc.css`, which is what the webpages actually use.

So, make sure you're setting your variables in `vars.scss`, and overriding styles in `styles.scss`.
