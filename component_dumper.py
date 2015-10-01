import rethinkdb as r
import io

c = r.connect()

with io.open("components.csv", "w", encoding="utf8") as fh:
    fh.write(u"num,description\n")
    components = r.db("pathian").table("components").order_by("num").run(c)
    for component in components:
        s = u",".join([u"=\"" + component["num"] + u"\"", u"\"" + component["description"] + u"\""]) + u"\n"
        fh.write(s)