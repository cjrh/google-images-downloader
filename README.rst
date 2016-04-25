# google-images-downloader
An experiment in browser automation

⚠ Warning ⚠
===========

Calling this **alpha quality** would be a kind and noble gesture.
Don't use it for anything.
Don't expect anything to work. If it destroys your computer you're
on your own.  This is a hobby project, and in all likelihood will eventually
be abandoned, perhaps even by next Tuesday.

If you create issues, I'll expect you to help work on them.
Pull requests, as always, are very welcome.

Introduction
============

This library pulls images out of [Google Images](https://images.google.com)
search results and saves them to disk. The neat trick is *not*
that it saves the images in the search results, instead it saves the
**original source images** (e.g. high-res images) that the search results
 refers to.

This is made possible by the
[Chrome Remote Debugging API](https://developer.chrome.com/devtools/docs/debugger-protocol#remote)
which also means you've discovered the first gotcha: this only works on
the Chrome browser.

Whence the name?
================

**GID**ler: **G**oogle **I**mage **D**ownloader.

Install
=======

The usual will work, but with caveats:

.. code-block:: shell

    $ python -m pip install gidler


The caveats are that you're *probably* going to need **Python >= 3.5** for this.
I don't have a lot of free time for hobby projects, and they're how I
experiment with new Python features.  It is an incredible amount of work to
make a Python package that works on everything, and I just don't have the
time and/or energy. *If you want it to work on 2.7, and you provide a working PR, I will
very likely merge that in*. I just don't have time to do it myself.

**However**: you don't actually need to do all that work. Just use
Anaconda Python. Using conda, you can create a new environment with the
right version of Python, and then pip install into that:

.. code-block:: shell

    $ conda create -n mygidlerenv python=3.5
    $ source activate mygidlerenv
    (mygidlerenv) $ python -m pip install gidler


Using and Abusing
=================

Step 1
------

First start up Chrome with remote debugging activated on a specific port::

    $ <chrome executable> --remote-debugging-port=9222

Now we can play that instance like a marionette!

Example using Chromium browser (on my Mac)::

    $ open /Users/calebhattingh/Applications/Chromium.app \
        --args -remote-debugging-port=9222

If you get this working on Windows or Linux, let me know and I'll add
more examples here.

Step 2
------

You can execute the module directly from the command-line:

.. code-block:: bash

    python -m gidler -p 9222 --max 5 -q "mandala"

This:

1. Starts up **gidler**...
1. ...on port **9222** (this must match what we gave chrome)...
1. ...returning no more than **5 images**...
1. with a query string of "mandala"

This query string is the same as what you would type into the Google Images
search box, so e.g., this all works: "site:deviantart.com sketch portrait"

You can also ``python -m gidler -h`` to see the help.

Current status
==============

It works on my machine™.

The script tells Chrome to do an image search, using the given query
string on the CLI. Then, the content of the page is parsed to extract
the original image URLs, which are then downloaded separately with
`urllib` inside a thread pool with 8 workers (yet another hard-coded
settings that will eventually become a CLI option...)

This means that Google is getting hit only with the initial search query,
not the all the subsequent (large) image downloads.

Future steps
============

Currently, several things are hard-coded:

* The "large" filter is automatically set. This is quite restrictive, and
is probably not what you want all the time. This should be a CLI option*.
If you peek in the source code, you'll see some documentation about all the
possible settings; you can even specify width and height requirements. None
of that is configurable yet though*.
* If no `max` is given, all the images on the first page of results are
fetched.  The code even forces scroll actions to the bottom of the page
in order to get Chrome to load all 400.  This might not be what you want.
* The images are saved into a new subfolder in the local folder. This should
be a CLI option*
* The subfolder name is a slugified version of the query string, plus a
small uuid (so that you can run the same query multiple times with no
collisions)
* The image names are the *original* image names, prefixed also with a
small uuid to avoid collisions in case multple images have the same filename.
* timeouts, and other applied pauses are all hardcoded. The pauses are
largely to give Chrome a chance to complete the previous instruction. I
tweaked these for my situation, but you may find longer pauses are necessary.
* The work was done on OS X. I have *no idea** whether this will work on
other platforms.

*PRs welcome.


But Selenium/ABC/XYZ already exists!
------------------------------------

Yes, yes, I know there are other tools.  I wanted a more lightweight option.
Currently, this library really only *depends on* Chrome and Python, although
there are several of the usual suspects in the `requires` list. (At the time
of writing, `requires` lists `chromote` and `python-slugify`, but those
each bring in a few other things, like `requests`, `ws4py` and so on.)

Why are you `require`ing your own fork of the `chromote` library?
-----------------------------------------------------------------

The `chromote` package provides a Python abstraction for Chrome Remote
Debugging API.  Currently, `chromote` uses the `websocket-client` package
which has been terribly unstable for me.  Sometimes `ws.recv()` returns, but
with nothing. In my fork I changed to use the high-quality `ws4py` package and
since then the connection to the debugging API has been rock solid.

