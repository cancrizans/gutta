# Managing Assets

## What is an Asset?

* **All** your images go in the `_assets` folder. Not in `_source`, and **never** outside of these folders. Whatever it is that you're trying to do, it won't work, and you'll lose stuff. Just put them in `_assets`.

* Within `_assets` you should place only images that are *web-ready*. This means that large high resolution pages, source files like .kra or .psd or .clip, and other files except for the same exact ready images that you want the user to see, do not go here, and they don't even go in your website folder at all. They stay somewhere else, where you draw your comic. Prepare your images **outside** at the intended resolution, format and quality, and then copy them in `_assets`.

* All formats that work in a browser are ok: **.jpg**, **.gif**, **.png**, **.webp**, etc. If it opens in your browser, it's probably fine. The *best* format and resolution for your content depends on your needs; gutta doesn't step on your toes here and it doesn't even touch your images, they are served to the user as-they-are. You can use animated .gifs, but be aware of filesize (see below).

* Placing an image in `_assets` will not make it appear on the website until it's actually explicitly referenced. So `_assets` does not actually say how your webcomic is laid out, and adding a page image doesn't mean you've published it. However, all _assets will be hosted and public nevertheless (I have no choice about this) and a savvy user can still access unreferenced assets, so don't place any sensitive information here.

## Structuring `_assets`

Inside the `_assets` folder, you may create as many subfolders as you like, nested however you want, and place the images where you please as long as they are all inside `_assets`. However, for the sake of making your life easier down the line when you'll have to reference these assets, you may wanna strive to keep a few rules:

* Ensure no folder names or image names contain **spaces** and other special characters like `!`. These can make it a pain to reference the images later, which you want to be able to do as effortlessly as possible.

* Try and put all the images for a given part of your comic (e.g. chapter) together in the same folder, including both comic pages and thumbnails. This will make it easier to refer to this folder through a prefix and save hours of precious typing time (see later).

* As said before, the assets in themselves don't tell the story of your comic. This means that there is no point in trying, say, to painstakingly number your page filenames in a certain order. Any set of names you got is ok, you'll have to do the layout later anyway.

Here's an example of a folder structure for `_assets`:

```
_assets/
    webcomic_banner.png
    chapter_one/
        chap1_thumb.jpg
        pg01.webp
        pg02.webp
        pg02_bis.webp
    chapter_two/
        chap2_thumb_resized.jpg
        pg01_02.webp
        pg03.png
```

as you can see: ugly names are no big deal.

# Best practices for images

*wip*

# Referencing assets

Later when writing your `webcomic.yaml` you'll have to *reference* these assets. To not waste your time, it's very useful to learn all the tricks of the trade. Say we got a comic page at the path `_assets/chapter_two/pg03.png`. Then if I want to use it as a comic picture for an update, I'll just have to type

```yaml
pix: chapter_two/pg03.png
```

note that in gutta we always use forward slash `/` to divide folders, like on the internet (not backwards `\` like in Windows). See also that we always omit `_assets/` because it's obvious.

## Prefixing

But there's a slightly faster way. We are going to set an **asset prefix** which is going to be a "temporary" place where to search assets, and that will shorten our reference:

```yaml
prefix: chapter_two/
pix: pg03.png
```

You may think we haven't really gained much in speed, but the trick will shine when we will be able to set the prefix simultaneously for a lot of nodes (more on that later). Prefixes can also be a bit more clever, for example:

```yaml
prefix: chapter_two/pg
pix: 03.png
```

## Multiple Reference

Say instead of `pg03.png`, our webcomic update is made up of `pg03.png`, `pg04.png`, `pg05.png`, `pg06.png`, and `pg07.png` (in that order). We can have multiple pages just separating with a comma:

```yaml
prefix: chapter_two/
pix: pg03.png, pg04.png, pg05.png, pg06.png, pg07.png
```

This works but it's a bit tedious. You can also use a numeric range with square brackets `[]`: 

```yaml
prefix: chapter_two/
pix: pg[03-07].png
```

Now isn't that nifty? The range not only scans the numbers from 3 to 7, but also understands that we want them zero-padded to have two digits.

We can even combine!

```yaml
prefix: chapter_two/
pix: pg[03-07].png, pg[09-12].png
```

this gets all pages from `pg03.png` to `pg12.png`, but skips `pg08.png`.

## How not to ruin YAML's day

These references to assets that we're going to be typing are really strings from the point of view of YAML. YAML is pretty cool in that it doesn't require you to always tell it when something is a string and where that string starts and ends, because it usually can figure it out. However, there are some edge cases. For example, this will fail:

```yaml
prefix: chapter_two/pg
pix: [03-07].png
```

The reason is the `pix` field stars with `[`, so the YAML parser guesses incorrectly that you're trying to write an array instead of a string. Just reassure it that it's a string using `"` quotes:

```yaml
prefix: chapter_two/pg
pix: "[03-07].png"
```

Anytime you have a weird YAML issue, just wrap some quotes and see if that fixes it.