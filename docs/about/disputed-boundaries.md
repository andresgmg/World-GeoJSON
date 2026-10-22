# Disputed boundaries policy

Any repository of national boundaries will eventually receive a pull request
that is really about sovereignty. This page exists so that the answer is
written down before the first one arrives, rather than improvised under
pressure.

## The policy

**Boundaries follow the upstream source named on each dataset's page. This
project takes no position on sovereignty.**

Four consequences:

1. **The source is always disclosed.** Every dataset page and every
   `manifest.json` names where the geometry came from and when. A boundary in
   this repository is a statement about that source, not about who is right.
2. **Geometry is not edited to reflect a claim.** Not the maintainer's, not a
   contributor's, not a government's. If the upstream source draws a line
   somewhere, that is where the line is.
3. **Disagreements are documented, not resolved.** Where a boundary is
   contested, the manifest's `notes` field records that fact and identifies
   the competing claims. Users are told there is a dispute; they are not told
   who wins.
4. **Alternative claims may be published side by side.** Where a well-sourced
   alternative delineation exists, it can be added as a separate dataset with
   its own source attribution — never by overwriting the existing one.

## Why not just "use the UN position"

It is a reasonable suggestion and it does not work. The UN itself does not
publish authoritative boundary geometry for disputed areas; its cartographic
products carry disclaimers precisely because member states disagree. Adopting
"the UN position" would mean choosing an interpretation and calling it neutral.

Deferring to a named, dated, checkable source is a weaker claim, and that is
the point. It is one this project can actually honour.

## What this means for contributors

**Acceptable:**

- "This boundary does not match the source cited in the manifest." — a factual
  claim about the data, checkable, and if correct, a bug.
- "Source X has published a revision dated Y." — an update.
- "This area is disputed and the manifest does not say so." — a documentation
  gap worth fixing.

**Not acceptable:**

- Editing geometry to reflect a territorial claim.
- Changing a source attribution to one that draws the preferred line, without
  a substantive reason for preferring that source.
- Issues arguing the merits of a claim. These will be locked; see the
  [Code of conduct](../contributing/code-of-conduct.md).

## Cases already in scope

- **The Chilean Antarctic Territory.** The region `Magallanes y de la
  Antártica Chilena` is present at ADM1 and the province `Antártica Chilena`
  at ADM2, but the commune Antártica (`12202`) is not: IDE Chile's DPA 2023
  package excludes the Antarctic claim, so nothing in the current files
  reaches beyond 56.6°S. Chile's claim overlaps those of Argentina and
  the United Kingdom, and the Antarctic Treaty suspends all such claims. The
  geometry reflects what IDE Chile publishes. (The legacy root files, from
  BCN, are a different dataset.)
- **Isla de Pascua / Rapa Nui.** Not disputed between states, but the naming
  is contested locally between the Spanish and Rapa Nui forms. The commune is
  present at ADM3; `shapeName` carries the source's form, `Isla de Pascua`.
- **Falkland Islands / Islas Malvinas (`FLK`) and South Georgia and the South
  Sandwich Islands (`SGS`).** Sovereignty is disputed between the United
  Kingdom and Argentina. Both ship an ADM0 outline only, from Natural Earth,
  whose de-facto depiction is followed. Names in the manifests follow ISO
  3166 in each language (`Falkland Islands` / `Islas Malvinas`); `shapeName`
  carries Natural Earth's form. Each manifest's `notes` records the dispute
  and points to this page.
- **Kosovo (`XKX`).** Kosovo declared independence from Serbia in 2008;
  Serbia and a number of other states do not recognise it, and it has no
  ISO 3166-1 code or UN M49 entry. Natural Earth draws it as a unit of its
  own, so it ships as one, under `XKX`, the user-assigned code the EU and
  geoBoundaries use. Serbia's outline, also from Natural Earth, does not
  include it. Both manifests say so.
- **Crimea.** Natural Earth's default, de-facto view draws Crimea inside
  Russia's outline and outside Ukraine's; Ukraine and most states consider it
  Ukrainian territory. Ukraine's raions come from a different source,
  geoBoundaries' 2006 release, and do include Crimea, so the two Ukrainian
  files disagree on it. Neither is edited to match the other; the `RUS` and
  `UKR` manifests record the dispute.
- **Gibraltar (`GIB`).** A British Overseas Territory claimed by Spain.
  Natural Earth's outline is followed, and the manifest says so.

- **Western Sahara (`ESH`).** A non-self-governing territory on the UN list,
  whose sovereignty is disputed between Morocco and the Sahrawi Arab
  Democratic Republic. Natural Earth's default view draws the part west of the
  Moroccan berm — Laayoune, Smara, Dakhla — inside Morocco's outline, and
  `ESH` covers only the area east of it. Both outlines are published as
  Natural Earth draws them; the `MAR` and `ESH` manifests say so.
- **Somaliland.** It declared independence from Somalia in 1991 and functions
  de facto as a separate state, without wide recognition and without an ISO
  3166-1 code. Natural Earth draws it as a unit of its own; here `SOM` is
  Natural Earth's Somalia and Somaliland dissolved together. No line is drawn
  or moved — the union only drops the boundary between the two units — and it
  matches ISO 3166-1, which has one entry for Somalia, and geoBoundaries'
  Somali districts, which cover Somaliland. The `SOM` manifest records it.
- **Abyei, Kafia Kingi, the Halaib Triangle and Bir Tawil.** Natural Earth
  draws Abyei and Kafia Kingi, both claimed by South Sudan, inside Sudan, and
  the Halaib Triangle, claimed by Sudan, inside Egypt. Bir Tawil, claimed by
  neither, is a unit of its own with no code and is not published. Sudan's
  first level, from geoBoundaries, has Abyei as a unit of its own. The `SDN`,
  `SSD` and `EGY` manifests record this.
- **The Ilemi Triangle.** Natural Earth draws it inside Kenya; South Sudan
  claims it. The `KEN` and `SSD` manifests say so.
- **The Chagos Archipelago (`IOT`).** Administered by the United Kingdom as
  the British Indian Ocean Territory and claimed by Mauritius; the two signed
  a treaty in 2025 to transfer sovereignty. The outline follows Natural Earth.
- **The Scattered Islands and Tromelin.** Natural Earth's outline of the
  French Southern Territories (`ATF`) includes them; Madagascar, Comoros and
  Mauritius claim some of them.
- **Mayotte (`MYT`).** A French department claimed by Comoros. It publishes
  its communes only, because Natural Earth draws it inside France.

Of the manifests, `FLK`, `SGS`, `XKX`, `SRB`, `RUS`, `UKR`, `GIB`, `MAR`,
`ESH`, `SOM`, `SDN`, `SSD`, `EGY`, `KEN`, `ERI`, `IOT`, `MUS`, `ATF`, `MDG`,
`COM` and `MYT` carry such a note today; Chile's does not yet.

## Naming

Place names are frequently as contested as the lines.

- `shapeName` carries the name used by the upstream source, in the local
  language.
- The manifest's `name.en` and `name.es` give the territory's display name per
  language; no English exonym is stored as a feature property.
- Alternative or contested names belong in `notes`, with their context.

The project does not rename features to prefer one community's form over
another's. Where a name is genuinely contested, record both and say so.

## Changing this policy

Via an issue and public discussion. It is deliberately mechanical: a policy
that requires judgement about who is right is a policy that will be relitigated
on every pull request.

--8<-- "abbreviations.md"
