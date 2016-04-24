GAE-Crawler
===========

A simple crawler running on GAE, using cronjob and is configurable online.

One can write his own procedure to process certain jobs with certain parameters, by inheriting class `ProcedureBase` in [proc/proc_base.py](proc/proc_base.py) just as other procedures do in the same directory.

Basically, it can only fetch the same URL over and over after some time. 
Good for monitoring something you are interested in, such as on-sale stuffs on [smzdm](http://smzdm.com), or second-hand stuffs on [xianyu](http://2.taobao.com).

Not yet support recursive crawling, i.e. privide a seed url, let tool to crawl recursively.

It is the backend of project [wechat-rent](https://github.com/jiachengpan/wechat-rent).

WIP.

Cheers, <br>
Jiacheng

