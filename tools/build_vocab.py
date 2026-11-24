"""Erzeugt die veröffentlichten Formate der SKOS-Vokabulare unter concept/.

Quelle je Vokabular: concept/<name>/<name>.ttl
Erzeugt im selben Ordner:
  <name>.jsonld, <name>.rdf   weitere RDF-Serialisierungen
  index.html                  lesbare Übersicht (Anker je Konzept)
  <notation>.html             je Konzept eine Weiterleitung auf index.html#<notation>,
                              damit die Konzept-URI ohne Endung auf GitHub Pages auflöst
Außerdem concept/index.html mit der Liste aller Vokabulare.

Aufruf (im Repo-Wurzelverzeichnis):  python3 tools/build_vocab.py
Benötigt: rdflib (pip install rdflib)
"""
from html import escape
from pathlib import Path

from rdflib import Graph, Literal
from rdflib.namespace import DCTERMS, OWL, RDF, SKOS

ROOT = Path(__file__).resolve().parent.parent / "concept"

PAGE = """<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="icon" href="{up}favicon.ico">
<style>
  body {{ font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; color: #1f1f1f; line-height: 1.5; }}
  h1 {{ font-size: 1.6rem; margin-bottom: .25rem; }}
  .meta {{ color: #5c5c5c; margin-top: 0; }}
  table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
  th, td {{ border: 1px solid #d0d0d0; padding: .5rem .6rem; text-align: left; vertical-align: top; }}
  th {{ background: #f3f3f3; }}
  code {{ font-size: .9em; }}
  tr:target {{ background: #fff6d6; }}
</style>
</head>
<body>
{body}
</body>
</html>
"""


def label(g, s, prop, lang):
    for o in g.objects(s, prop):
        if isinstance(o, Literal) and o.language == lang:
            return str(o)
    return ""


def build_vocab(folder: Path):
    name = folder.name
    g = Graph()
    g.parse(folder / f"{name}.ttl", format="turtle")
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    g.serialize(folder / f"{name}.jsonld", format="json-ld", indent=2)
    g.serialize(folder / f"{name}.rdf", format="pretty-xml")

    scheme = next(g.subjects(RDF.type, SKOS.ConceptScheme))
    title_de = label(g, scheme, DCTERMS.title, "de")
    # Reihenfolge wie in der Quelldatei (entspricht der Reihenfolge im Formular)
    source = (folder / f"{name}.ttl").read_text(encoding="utf-8")
    concepts = sorted(g.subjects(SKOS.inScheme, scheme),
                      key=lambda c: source.find(f'skos:notation "{g.value(c, SKOS.notation)}"'))

    rows = []
    for c in concepts:
        notation = str(g.value(c, SKOS.notation))
        note_de = label(g, c, SKOS.scopeNote, "de")
        rows.append(
            f'<tr id="{escape(notation)}"><td><code>{escape(str(c))}</code></td>'
            f"<td>{escape(label(g, c, SKOS.prefLabel, 'de'))}<br><span class=\"meta\">{escape(label(g, c, SKOS.prefLabel, 'en'))}</span></td>"
            f"<td>{escape(label(g, c, SKOS.definition, 'de'))}"
            + (f"<br><em>{escape(note_de)}</em>" if note_de else "")
            + "</td></tr>"
        )
        redirect = (
            f'<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">'
            f'<meta http-equiv="refresh" content="0; url=index.html#{escape(notation)}">'
            f"<title>{escape(label(g, c, SKOS.prefLabel, 'de'))}</title></head>"
            f'<body><a href="index.html#{escape(notation)}">{escape(str(c))}</a></body></html>\n'
        )
        (folder / f"{notation}.html").write_text(redirect, encoding="utf-8")

    body = (
        f"<h1>{escape(title_de)}</h1>\n"
        f'<p class="meta">Konzeptschema <code>{escape(str(scheme))}</code> · Version {escape(str(g.value(scheme, OWL.versionInfo)))}'
        f" · erstellt {escape(str(g.value(scheme, DCTERMS.created)))}</p>\n"
        f"<p>{escape(label(g, scheme, DCTERMS.description, 'de'))}</p>\n"
        f'<p>Download: <a href="{name}.ttl">Turtle</a> · <a href="{name}.jsonld">JSON-LD</a> · <a href="{name}.rdf">RDF/XML</a></p>\n'
        "<table><thead><tr><th>URI</th><th>Bezeichnung</th><th>Definition</th></tr></thead><tbody>\n"
        + "\n".join(rows)
        + "\n</tbody></table>\n"
        '<p class="meta"><a href="../index.html">Alle Vokabulare</a> · <a href="../../index.html">DCAT-AP.at</a></p>'
    )
    (folder / "index.html").write_text(PAGE.format(title=escape(title_de), up="../../", body=body), encoding="utf-8")
    return name, title_de, str(scheme)


def main():
    vocabs = [build_vocab(f) for f in sorted(ROOT.iterdir()) if f.is_dir() and (f / f"{f.name}.ttl").exists()]
    items = "\n".join(
        f'<li><a href="{n}/index.html">{escape(t)}</a> – <code>{escape(s)}</code></li>' for n, t, s in vocabs
    )
    body = (
        "<h1>Vokabulare</h1>\n"
        "<p>SKOS-Vokabulare zu DCAT-AP.at und zum DZG-Metadatenmodell.</p>\n"
        f"<ul>\n{items}\n</ul>\n"
        '<p class="meta"><a href="../index.html">DCAT-AP.at</a></p>'
    )
    (ROOT / "index.html").write_text(PAGE.format(title="Vokabulare – DCAT-AP.at", up="../", body=body), encoding="utf-8")
    for n, _, s in vocabs:
        print(f"{n}: {s}")


if __name__ == "__main__":
    main()
