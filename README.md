# Vulnsite
A purposely vulnerable webserver used to teach XSS and CSRF attacks.
Created by and used by [RPISEC](https://rpis.ec).

## Requirements
* Python2
* [Python Twisted](https://twistedmatrix.com)
* [PhantomJS](http://phantomjs.org/)

## Running
Run for the first time with 

```python mainserver.py --domain <yourDomain> --port <yourPort> --clean``` 

The `--clean` can be omited after the first run unless you want to clear all data.

## Overview
Vulnsite is a reddit clone which allows users to do the following:
* Register accounts and login
* Create a text post
* Comment on a post
* Private message other users
* Share a post though private messages
* Vote on posts and comments

There are two bots that can be interacted with:
* **Moderator:** This bot will visit all link posts that are submitted.
* **Admin:** This bot will view its private messages every time one is sent to it.

It is possible to escalte your privlages all the way to admin on this site.

[Bother me on irc](https://rpis.ec/irc) if you have questions.

Good luck!
