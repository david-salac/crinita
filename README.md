# Crinita: static website generator
Author: David Salac <https://www.github.com/david-salac>

Project sites: [Crinita](http://crinita.com/)

Python application for generating static websites like a blog or
simple static pages. Creates HTML files based on inputs (without
requiring to run any script languages on the server-side).

## Blog and static website generator
Generally speaking, Crinita is a static website generator. That is
an application that generates simple HTML files that cover all the
content of sites from all inputs - composed mainly of the
definition of pages, articles and other entities on websites).
So after running of static websites generator, you have a set of
`*.html` files (including index.html) that allows you to browse sites.

There are many advantages of using static websites generator rather
than the standard approach using some web framework (like PHP,
Django). Mainly, the result can be simply deployed to production
as you do not need to configure anything on the server-side. There
are many ways how to deploy the outcome; the most popular is
GitHub pages (technically a free place where to host your static
pages). Another significant advantage is the security perspective - it
is almost impossible to hack static websites (what a massive
difference if you consider how vulnerable are websites running on
WordPress or similar technologies). Last but not least advantage is
cost-effectiveness - you do not need to use any expensive technologies
for hosting (like AWS) or pay directly for these services (like Wix,
Medium). 

Crinita allows you to generate blog (and/or) websites (blog
or just set of static pages). It includes advanced features like
tags, the possibility to edit meta tags for each entity (article
or page). Interface for using Crinita is simple so you can learn
it quickly. Installation of Crinita is a simple task as it does not
require any system dependencies.

## Typical use cases
There are some typical use cases when it is beneficial to use Crinita,
among the most popular are:
1. Need to leave technically weak services like Blogger: There are many
services that allow you to run your blog. One of the most popular is
Blogger. However, the technical quality of these services is notoriously
weak (particularly if it comes to Blogger). It is often hard to use them
for anything even bit more technical (like including articles with
code examples). The resulting page often is also technically weak - no
SEO-friendly output (usually it's impossible to index article in Google
at all).
2. Do not want to pay for services like Medium: Many helpful services
can run your blog (or static pages) in a technically suitable way. One
of the reasonably good services is Medium. Although it is quite good,
it is also quite expensive - which can demotivate many potentials bloggers.
3. Afraid of security vulnerabilities of WordPress: if people want to
run their blog on their infrastructure, the typical first choice is
WordPress. It is simple, quick to install and easy to use. Unfortunately,
it is notoriously problematic in the security point of view. Everyone can
find a lot of articles and analysis of these vulnerabilities. It is
mainly the security issue that makes WordPress almost useless for many
cases. Because Crinita works on different principles, it is practically
impossible to hack resulting pages.
4. Difficulties with back-up and restore procedures: it is often hard
(and sometimes impossible) to back-up your blog (pages) content. So if
your pages are hacked (or destroyed by any other way), you lose all your
work. This is a frequent problem with WordPress - where even if you create
a back-up of your database - restoring it is a fairly difficult task.
Some external services (Blogger, Medium) do not allow backing-up in any
reasonable format at all. Crinita, on the other hand, is backed-up in
principle (because generator files are just simple Python scripts that
can be easily pushed to GitHub).
5. Simple to use and quick to install: one of the essential quality of
Crinita is that it is simple to install and to use. On the other hand,
it is presumed here, that user is fluent in Python developing and HTML
coding. If this is your case, it just requires to install Crinita from
PyPi archive, download layouts and styles and then just write some content.
6. Cheap and primitive infrastructure: as you do not need to run any script
on the server-side (like PHP, Ruby, etc.), infrastructure for the Crinita
is fairly simple. Technically the simplest way how to run your websites
is to deploy them through GitHub pages (technically the free hosting
for static websites) - which is a highly recommended approach (as you
can have both generating scripts and content on one place and backed-up).

## How to install Crinita
In order to install Crnita, you need to have prepared your Python (in
version at least 3.8) environment ready first. There are many manuals
on how to install Python on your machine (so there is no reason why
to explain it here again).

To install Crinita, you can use your PIP
directly with a default package manager (PyPi.org). Just write
a command:
```
pip install crinita
```
To check if the installation is successful, write in some script:
```
import crinita as cr
```
If you do not see any error, it looks good.

## How to use Crinita
The simplest way where to start to generate your own websites
is to use the logic of existing ones:
1. Use **https://github.com/david-salac/itblog.github.io** for the
complex blog (with articles and pages).
2. Use **https://github.com/david-salac/crinita.github.io** for the
simple static websites.

In all these cases, the generating script is in the folder generator.
There is also a definition of pages and articles there.
