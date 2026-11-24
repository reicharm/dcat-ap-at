# DCAT-AP.at

Repository für die Entwicklung der österreichischen Variante von DCAT-AP als Metadatenschema für die Bereitstellung von (offenen) Daten bzw. deren Metadaten auf Portalen der öffentlichen Verwaltung und der Zivilgesellschaft.

Work in progress!

Die Dokumentation wird mit Hilfe von [RDForms-specs](https://bitbucket.org/metasolutions/rdforms-specs/) erstellt.

## Vokabulare

SKOS-Vokabulare liegen unter `concept/<name>/`. Die Quelle ist jeweils `<name>.ttl`; JSON-LD, RDF/XML und die HTML-Seiten werden daraus erzeugt:

```
pip install rdflib
python3 tools/build_vocab.py
```

| Vokabular | Konzeptschema | Verwendung |
| --- | --- | --- |
| [Erhebungsform](concept/erhebungsform/index.html) | `http://dcat-ap.at/concept/erhebungsform/` | `dcterms:type` an `prov:Activity` (`prov:wasGeneratedBy`) eines Datenprodukts |
| [Ressourcentyp](concept/resourcetype/index.html) | `http://dcat-ap.at/concept/resourcetype/` | `dcterms:type` an `dcat:Dataset`; `Dataproduct` kennzeichnet ein Datenprodukt |

Die Konzept-URIs lösen erst auf, wenn `dcat-ap.at` auf diese Seiten weiterleitet.