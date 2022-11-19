# How do I into `webcomic.yaml`?

*wip*

## YAML 101

*wip*

## The Tree

*wip*

## Structure of `webcomic.yaml`

*wip*

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

*wip*