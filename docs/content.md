# How do I into `webcomic.yaml`?

*wip*

## YAML 101

*wip*

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

## Structure of `webcomic.yaml`

`webcomic.yaml` is built like this:

```yaml
hierarchy:
  ...

# other main webcomic options...

root:
  ...
```

You can order options however you like actually.

# Options

# Main webcomic options

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

Destinations can be specified as `gutta.<keyword>` for any of these special locations:

| Destination | Description |
| -- | -- |
| `gutta.home` | Website home |
| `gutta.first` | First leaf node |
| `gutta.latest` | Latest leaf node |
| `gutta.rss` | The RSS feed |
| `gutta.atom` | The ATOM feed |

or you can use `extras.<name>` to link to the extra page called `name`. Note that linking to resources that don't exist (for example the RSS feed when you haven't set one to be created with the `feed` option) will not print any errors.

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

## show_date

Values: `yes`, `no`

whether to display the date for this node in gallery and scroll modes.

## show_title

Whether to display the node's title as a header within the webpage right under the navbar and before the body.

## thumb

Image asset that acts as a thumbnail for this node, and will fill the card if it's an entry in a gallery. Recommended image width is 400px.

## title

This node's own title. 

Do not include greater node's titles here to avoid duplication, for example, if you want the full title "My Webcomic - Chapter I - Episode 1", simply title your `episode` node `title: Episode 1`.