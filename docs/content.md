# How do I into `webcomic.yaml`?

To tell gutta how your comic is laid out, you need to edit your `webcomic.yaml` file contained in the `_source` folder. This file is written in (a simplified version of) the YAML language, and requires you describe your comic in a certain way. This guide will teach you what you need:

* How to write YAML
* How to structure your webcomic in general
* Quickstart to get a basic working file up
* Reference for all available options

## YAML 101

YAML is already a very easy language, but we'll make it even easier by only using a fraction of its functionalities. 

First of all, a YAML file (extension `.yaml`) is a simple text file. You can edit it with notepad, but it's a bit more comfortable to use something more suited - for beginners I recommend [Notepad++](https://notepad-plus-plus.org/) or [Sublime Text](https://www.sublimetext.com/).

At heart the YAML file will simply have a bunch of lines like this

```yaml
key1: First value bla bla bla

key2: Second value bla bla bla
key3: Third value bla bla bla

# lines starting with a hash sign are comments and are ignored. As are empty lines

key4: Fourth value # I can also add a comment after a line.

...
```

The key can be any identifying phrase, but for us we will prefer to use as keys a lowercase phrase with no spaces or special characters, using underscores to separate words if we need, not starting with a number. For example `webroot`, `list_in_toc`, `prologue2` are all good keys, while `Chapter2`, `4chan`, `Merry Christmas` are kind of a bad idea and/or may not work.

The values instead can just be any regular text. Sometimes it's necessary to put something very specific, for example `yes` or `no`, or a specific value for an option.

The space after the `:` and before the value is necessary in YAML, so make sure you leave it (your editor will let you know).

That's not all: in addition, the value itself can be another "object" with more keys of its own, like if our YAML had a property that was itself a smaller YAML. To show that we are inside this "object" we must indent using the Tab key:

```yaml
# we're assigning options to the main object now
key1: value1
key2: value2
key3: value3

key4:
#v note the indent
  subkey: subvalue    
  another_subkey: subvalue2
  # I'm in the sub-object still so everything gets assigned to it
  yet_another_subkey: subvalue3 bla bla bla

key5: value5  # I'm back to regular indent so this is on the main object again.
```

## The Tree

The most important concept you'll have to learn is the **Webcomic Tree**. This tree is a hierarchical structure made up of nodes that may have other nodes as "children". Each node will be by default "mounted" which means associated with a specific webpage (though you can disable mounting for some nodes).

The topmost node is the `root` node. It is considered to be at "level" or "depth" 0, and it is the only node at depth 0.

The children of `root` are the nodes at depth 1. The children of those depth 1 nodes are at depth 2, and so on.

Finally, a node with no children is called a *leaf*.

You will be able to specify your webcomic tree explicitly in your YAML file by writing `root` and detailing the `root` node; this includes also its `children` and all of them will be detailed in the same way, and so on until you have your whole tree mapped out. Like this:

```yaml
root:
  some_property: some value
  some_other_property: some value
  children:
    first_child:
      some_property: some value
      children:
        first_grandchild:
          ...
        second_grandchild:
          ...
    second_child:
      children:
        yet_another_grandchild:
          ...
```

This creates the following tree:

```
                                root
                                  |
                /-----------------"--------------\
                |                                |
          first_child                       second_child
               |                                 |
    /----------"--------\                        |
    |                   |                        |
first_grandchild  second_grandchild     yet_another_grandchild
```

and also simultaneously we are able to set some properties for each node.

Some properties however are really more useful to set on all nodes at a certain depth. For example, if I think of my depth 1 nodes as the chapters of my webcomic, I want to be able to set properties for all chapters once and for all instead of repeating them in each chapter. For this I use the **Hierarchy specification**. This thing lets me specify what a node of each depth should be called according to me, and what properties should it have by default. Example:

```yaml
hierarchy:
  comic:
    layout: gallery
  chapter:
    layout: gallery
  update:
    layout: scroll
```

This above says my `root` node is a "comic" (my own name, doesn't mean anything) and that it should have the property `layout: gallery`, meaning it should display links to its children as a gallery of images. Its children instead should be called "chapters", and they should also display their children in a gallery of links. The children of chapters will be called "updates", and "updates" will display their contents in a vertical scroll format.

Applied to the tree above, this hierarchy will make `root` a "comic", and `first_child` and `second_child` into "chapters", and finally `first_grandchild`, `second_grandchild` and `yet_another_grandchild` into "updates". The properties that I set for each depth in the hierarchy are copied into all nodes at that depth, so I don't have to manually say that `second_grandchild` has `layout: gallery` - it's automatic because it's a "chapter".

*Note: since `root` is the one and only depth-0 node, specifying its properties directly under `root:` or in the first layer of the hierarchy is obviously equivalent. Just choose the way that makes your `webcomic.yaml` easier to read to you, both work.*

## Quickstart on `webcomic.yaml`

Open `webcomic.yaml` in your editor. The first thing we're gonna worry about is the overall layout of your website, which we will map in the `hierarchy:` option. Think about this long and hard - what is it that you want to see when you open the website? How do you want to read it?

Let's say when I open the website I want to be able to choose from a list of chapters. When I click on a chapter, I immediately want to begin reading it from the first update to the last one, with each update comprising one or more pages. I don't want any interruption so I want the whole thing in infinite vertical scroll. At the end of the chapter I want a link to the next chapter, and so on.

So my first deduction is that my hierarchy is `webcomic > chapter > update`. These will represent depth-0, depth-1 and depth-2 nodes respectively. The second one concerns the *layouts* to assign to these levels, namely how their webpages should be built like. We know `webcomic` must have a page with a set of links to its children chapters, so we say `layout: gallery`. Then, we want `chapter` to show its own children's content in vertical scroll, so we choose `layout: scroll`. But what about updates? We don't really want them to have their own webpage (you want to avoid presenting the same content twice as a general rule), but they should still be `layout: scroll` so that their content is just their comic pages pics stacked vertically, so that when updates are embedded into chapters everything comes together nicely. Thankfully we can disable the creation of a true page for updates using the `mount:` option (we'll see later in detail how). For now, we write our hierarchy using our level definitions in order:

```yaml
# somewhere in webcomic.yaml

hierarchy:
  webcomic:
    layout: gallery
  chapter:
    layout: scroll
  update:
    layout: scroll
    mount: redirect
```

What this is saying is, just to be pedantic:

* The `root` node will be called a `webcomic`, and it will have the property `layout: gallery`
* All children of the `root` node will be called `chapter`, and they will have the property `layout: scroll`
* All grandchildren of `root` will be `update`, and they will have the property `layout: scroll` and `mount: redirect`

you get it, right?

So, what's with `mount`? Mounting a node is the act of actually reserving a location on the website (like `yourwebsite.com/the_location/`) called a mountpoint as the place where the user can actually find the webpage of that node. Mounting is handled completely automatically by gutta unless you want to intervene, except for the fact that you have to tell it whether to do it or not. 

By default, all nodes are `mount: yes`, which means they all get a webpage somewhere - that can be undesirable sometimes, like in our case. If you set `mount: no` your node does not get mounted and links to it actually get converted to anchors in the parent page. While the lone node doesn't physically exist in the final website, it's still useful to you as a structure to lay out your webcomic (e.g. you can assign it a date, a title, description, etc...)

You could do this, and this is *almost* perfect, but it has a tiny frustrating flaw: when you share links to your `updates` online, they're gonna be links to the parent chapter page + the anchor to the update, which means you're only ever gonna get the tags of the `chapter` - that means, say, the Discord or Twitter embeds are gonna be generic. It's also pretty bad for search engines, crawlers, analytics... `mount: redirect` is a good compromise. It actually does mount an update page, but the update's page is an immediate redirect to the location of the update on the chapter's page. So you seamlessly have the same experience as if it was unmounted, but all the benefits of there being a genuine location on the website dedicated to that `update`.

This was all just an example! You need to think about how you want your site to be like, and then translate it into a `hierarchy`.

When we're done with `hierarchy:`, we can now add a few more generic options for the website (main webcomic options). We can lay these out in any order we want. So you have

```yaml
hierarchy:
  # the whole hierarchy here...
  ...


title: Muh Comic
favicon: icon.png
...
```

See below for reference on all the available main webcomic options. They're pretty easy.

Finally, the last thing you need to have necessarily is the `root:` option, which specifies the root node and all its children, and so essentially contains the entirety of your comic's content, using the tree format we described before.

So in the end you get this whole structure for your file:

```yaml
hierarchy:
  ...

# main options here...


root:
  # root's node options
  ...
  children:
    chap1:
      #chap1's node options
      ...
    chap2:
      ...
```

For each node, per-node options are picked from both what you insert here in the tree under `root`, and also from the corresponding layer in `hierarchy`, with priority on the former. For example, if I write for a chapter:

```yaml
hierarchy:
  webcomic:
    layout: gallery
  chapter:
    layout: scroll
  update:
    layout: scroll
    mount: redirect

root:
  ...
  children:
    chap1:
      layout: gallery
```

Since `chap1` is the child of `root`, it is depth 1 and thus it is a `chapter`, so according to the `hierarchy` it should have `layout: scroll`. However, my manual specification of `layout: gallery` under `chap1:` takes precedence, so this particular chapter will actually have scroll layout. This is pretty comfortable if you want to handle the occasional special case in an otherwise large and regular webcomic.

In fact, literally *all* per-node properties can be specified in either hierarchy or the tree, with priority to the tree specification, though only some of them are convenient to have in the hierarchy (for example, placing `title:` in the hierarchy is not very useful...)

## Mounting and determinism

Mounting, which is assigment of a location on the website to your nodes, is generally not something you need to worry about, but occasionally some situations can be a little weird and it's good to know what's happening behind the scenes.

Gutta always mounts your `root` node at the empty mountpoint `""`, meaning if your website is `https://myweb.comic` then `root`'s page is at `https://myweb.comic/index.html` and will be visible at `https://myweb.comic`.

For all other nodes, gutta will try its best to mount them in subfolders of your main website folder (though the option to manually nest folders is there). Gutta's automatic decision is to name the mountpoint the same as the *node id*, for example the chapter `chap1:` will be mounted, if possible, at `chap1/`, with its webpage at `chap1/index.html`. The intention behind this automatic default is that it makes for short, simple and semantically clear permalinks, like `https://mywebcomic/chap1` which is readable, meaningful, and memorable.

This might create a problem, however, if there's a conflict, as can happen if two nodes have the same node id. Multiple nodes with the same id cannot exist as children of the same parent (duplicate keys in YAML are not allowed and lead to broken parsing), but you can totally happen to have duplicate node ids otherwise. They may be at the same level but in different locations, for example

```yaml
//example A (update1 is a duplicate node id)

chapter1:
  children:
    update1: ...
    update2: ..
chapter2:
  children:
    update1: ...
```

or they may appear at different level, especially as a parent-child pair when you need to have a node with only one child to get to a specific depth:

```yaml
//example B (purgatory is a duplicate node id)

hell:
  children:
    hell1: ...
    hell2: ...
purgatory:
  children:
    purgatory: ...
heaven:
  children:
    heaven1: ...
    heaven2: ..
```

These situations may happen and even be reasonable. In the case of example A, I would suggest using more sensible node ids, like `chapter1_1` for the first update of `chapter1`, though that's not mandatory. For example B, the node ids are a good choice, but a mountpoint conflict will ensue if both `purgatory` nodes need to be mounted.

Gutta will **never** mount two nodes on the same mountpoint, and it will always resolve a conflict. In example B, the first instance of `purgatory`, which is the lower depth one, is granted the `purgatory/` mountpoint. Then when the second `purgatory` node comes, the request for `purgatory/` is denied, and gutta tries to assign `purgatory2/` if available, and then proceeds until a suitable replacement has been found. Gutta's automatic conflict resolution always ensures your website is never broken, but it does have a major downside when your webcomic gets popular and you go to add more content over time.

The problem is non-determinism. If you do any modification uphill of the second `purgatory` node, or in general uphill of any conflict resolution, you risk changing how the conflict is resolved, which means your links have changed and thus they're not *perma*links anymore. Again in example B, maybe you have a change of mind and you rename the upper node:

```yaml
purgatory_chapter:
  children:
    purgatory: ...
```

This means there is no conflict anymore, but then `purgatory` gets mounted on `purgatory/` and not anymore on `purgatory2/`, which means previous "perma"links you have shared before to `https://mywebcomic/purgatory2` will become broken! The same can happen if anywhere uphill you end up adding another `purgatory` node, which will shift the conflict-resolved numbers `purgatory/` -> `purgatory2/` -> `purgatory3/`, for an absolutely maddening reshuffling and breaking of links. If your links break or change even without you actually changing your content, it's bad!

It's therefore always strongly recommended to avoid mountpoint conflicts at all and ensure gutta's conflict resolution never has to be activated. This way your URLs will be consistent and permanent. We can fix this by using the `mountpoint:` option which allows us to manually specify a desired mountpoint to use instead of the node id:

```yaml
purgatory:
  mountpoint: purgatory_chapter
  children:
    purgatory: 
      mountpoint: purgatory
```

You can verify the list of mountpoints assigned by gutta by looking at the autogenerated file `.debug/mounts.txt`, and check if any mountpoints look funny. (The `.debug` folder may be hidden - make sure to select *show hidden files and folders*.)

# Options

# Main webcomic options

## cactus

Defines the use of [Cactus Comments](https://cactus.chat) as a framework to manage comment sections. To use cactus, you'll need to make a Matrix account and register your website (follow the instructions there).

| Sub-option | Required | Description |
| --- | --- | --- |
| `website_name` | yes | The website name with which you registered your site on cactus |

## extras

Example

```yaml
extras:
  archive:
    layout: toc
  cast:
    from: cast.md
```

Describes extra pages. See [the documentation on Extra Pages](extras.md) for more information.

## favicon

Example:

```yaml
favicon: favicon.png
```

The image asset to be used as a favicon (icon in the browser tab heading). The image can be an `.svg`, a `.png` or a `.gif` and it should be square.

## feed

Example:

```yaml
feed:
  entries: update
```

If present, RSS and Atom feeds will automatically be generated. These will be located in `rss.xml` and `atom.xml` in the root of the website, independently on whether they are linked to or not.


| Sub-option | Required | Description |
| --- | --- | --- |
| `entries` | yes | Specifies which named level of the hierarchy is used as entries in the feed. |

## google.analytics

```yaml
google.analytics:
  tracking_id: ...
```

If present, Google Analytics tag will be included in all pages (including redirects before the redirect code).

| Sub-option | Required | Description |
| --- | --- | --- |
| `tracking_id` | yes | Tracking ID provided by Google Analytics |

## hierarchy

Specifies the existing levels in the webcomic tree along with their names and allows you to set properties on all nodes of a level (see above).

## navbar

Example:

```yaml
navbar:
  menu:
    Home: gutta.home
    Latest: gutta.latest
    Archive: extras.archive
    Cast: extras.cast
    RSS: gutta.rss
```

Describes the navbar on top of the website.

| Sub-option | Required | Description |
| --- | --- | --- |
| `menu` | yes | Link labels and destinations in key : value pairs in the intended order |

Destinations can be specified as follows:

| Destination | Description |
| -- | -- |
| `gutta.home` | Website home (root node mount) |
| `gutta.first` | First leaf node |
| `gutta.latest` | Latest leaf node |
| `gutta.rss` | The RSS feed |
| `gutta.atom` | The ATOM feed |
| `extras.<name>` | The extra page called `<name>`|
| `href.<url>` | Link to the literal absolute URL `<url>`|

Note that linking to resources that don't exist (for example the RSS feed when you haven't set one to be created with the `feed` option) will not print any errors.

## title

Title of the Webcomic. This will only be used to build the html page titles that are shown on the browser tab heading.

## root

Example:

```yaml
root:
  //other properties of the root node...
  ...
  children:
    child1:
      ...
    child2:
      ...
```


This is the specification of your single root node, which belongs to layer 0 of your hierarchy (see above). The entire tree of your webcomic content is under this node.

## webroot

URL of location where website is expected to be hosted or forwarded; will be used to generate permalinks and feeds. This will **not affect internal links in the website**. E.g. `webroot: http://myweb.comic/` means that node at `node/` will have permalink `http://myweb.comic/node/`.



# Per-node options

## banner

Image asset to be displayed as a banner above the navbar in this node's webpage. This allows for selectively hiding the banner, or changing it.

## children

This node's children nodes.

## comments

Values: `yes`, `no` (default `no`)

Whether to show a comment section in this node's page. Note that each node will have its own, separate comment section.

This option requires a comment section framework, like cactus, to be set up globally for the site.

## content_is_link

Values: `yes`, `no` (default `no`)

If this node is `layout: scroll` then the images in `pix` become links to the next node in navigation. This is most useful for traditional one-webpage-per-comic-page comics. Note that this doesn't disable the pre-existing link at the bottom of the page.

## date

Date for this node. You can write the date in really any format you want, it will be probably be parsed correctly. To ensure no ambiguities, prefer writing the month as a full word. The following examples all work correctly and parse to the fourth of May, 2019:

```yaml
# excellent, unambiguous and easy to read
date: 4 May 2019    
# wordy but still works
date: 2019, 4th of May
# also parses as May the 4th but euros might be confused.
date: 5/4/2019      
# international standard, YYYY-MM-DD
date: 2019-5-4      
# also allowed but the day of the month could be weird
date: May 2019      
```

## dated

*wip*

## infobox

Values: `yes`, `no` (default `no`)

Whether to display a lateral infobox for this node in scroll mode.

## layout

Values: `gallery`, `trickle`, `scroll`

The format of the webpage to be created for this node. See above for the description of page layouts.

## list_in_toc

Values: `yes`, `no`

Whether to list this node in a table of contents.

## mount

Values: `yes`, `no`, `redirect` (default `yes`)

Whether the node should be "mounted", i.e. if a location online should be reserved for it and a webpage should be placed there. 

`mounted: yes` will cause the node to be mounted with a full webpage specified by layout.

`mounted: no` will create an unmounted node with no own webpage, which is ideal for children of a `scroll` node. An unmounted node's permalink actually points to its parent's webpage plus an anchor to automatically scroll down to its location in the parent webpage.

`mounted: redirect` is a bit of a mix. It will actually mount the node at its own mountpoint, but the mounted webpage is empty and just does a simple redirect to the same permalink you would have if it was unmounted. However, the webpage still has opengraph tags so the node's permalink may correctly embed in Discord, Twitter, etc...

## mountpoint

Recommended location where to mount this node (i.e. where to create its webpage). By default equal to the node id.

Note that mountpoint are assigned if available in order of traversal of the tree, so that if a node before this already has taken the mountpoint you're requesting, your node is going to slide to a different one.

## og.img

Image asset to be used as preview image for opengraph embeds (Discord, Twitter...). By default it's set to the first element of `pix` if it exists, else `thumb` if it exists, else the first child's own `og.img` if this node has children.

## pix

List of image assets to be included in this node if in `scroll` mode. This is probably where you wanna set actual webcomic pages.

## prefix

Example:

```yaml
big_node:
  prefix: bn/
  thumb: thumb.png # this is bn/thumb.png
  children:
    child1:
      pix: pic.png # this is bn/pic0.png
      ...
    child2:
      prefix: something_else/
      pix: pic.png  # this is something_else/pic.png
```

Prefix that is prepended to all image asset path (`pix`, `thumb`, `og.img`, ...)

Note on inheritance: `prefix` is inherited automatically from a node's parent. So if you set a prefix for, say, a chapter node, each subnode will also automatically respect that prefix, unless it manually specifies its own different value for `prefix`.

## redraw

Date on which the content node was redrawn -- useful for when you revisit older segments of your webcomic but you don't want to mess with the original incremental dating. If this variable is set, the node's infobox will display a message "(Redrawn on ...)" after the actual original date.

## short_title

The title for this node used in the hierarchical node names, such as in the table of content or in HTML page titles.

By default the value of `title` is used. 

If set to empty (`short_title: ""`) the node will not appear at all in hierarchical names.

## show_date

Values: `yes`, `no`

whether to display the date for this node in gallery and scroll modes.

## show_description

Values: `yes`, `no` (default `no`)

whether to display the description as a paragraph beneath the title of this node's own webpage, if it has one. Note this does not affect the presence of the description in infoboxes or gallery entries.

## show_title

Whether to display the node's title as a header within the webpage right under the navbar and before the body.

## thumb

Image asset that acts as a thumbnail for this node, and will fill the card if it's an entry in a gallery. Recommended image width is 400px.

## title

This node's own title. 

Do not include greater node's titles here to avoid duplication, for example, if you want the full title "My Webcomic - Chapter I - Episode 1", simply title your `episode` node `title: Episode 1`.