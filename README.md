# Notifico!

Notifico is my personal open source ([MIT][]) replacement to the
now-defunct http://cia.vc service. It simply takes messages (like commits,
weather updates, ticket changes, etc...) and sends them off to an [IRC][]
channel. I use it as a tool to easily add IRC output to many of the tools
we use internally.

**Note:** This is alpha software and likely has many flaws and even potential
exploits. That said, it's safe to run your own copy with registrations
disabled.


## Requirements

Notifico can be installed like any python package (`python setup.py install`).
Since Notifico uses [SQLAlchemy][] it can work with a variety of databases
(such as [SQLite][] and [MariaDB][]).

- An [SQLAlchemy][]-compatible database
- [Redis][] (which is used for caching and IPC with the bots)
- Various python package dependencies (setup.py will install these for you)


## Hacking

If you just want to hack on Notifico, the default configuration
is sufficient (it'll use a local [SQLite][] database and local redis).
`python -m notifico.scripts.debug` will launch a local server.


[MIT]: http://en.wikipedia.org/wiki/MIT_License
[IRC]: http://en.wikipedia.org/wiki/Internet_Relay_Chat
[SQLALchemy]: http://www.sqlalchemy.org/
[SQLite]: http://www.sqlite.org/
[MariaDB]: https://mariadb.org/
[Redis]: http://redis.io/