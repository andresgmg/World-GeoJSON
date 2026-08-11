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
   contested, the dataset's `notes` field records that fact and identifies the
   competing claims. Users are told there is a dispute; they are not told who
   wins.
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

Chile's existing data contains two:

- **The Chilean Antarctic Territory.** `Región de Magallanes y Antártica
  Chilena` is present at ADM1. Chile's Antarctic claim overlaps those of
  Argentina and the United Kingdom, and the Antarctic Treaty suspends all such
  claims. The geometry reflects what BCN publishes.
- **Isla de Pascua / Rapa Nui.** Not disputed between states, but the naming is
  contested locally between the Spanish and Rapa Nui forms. The `shapeName`
  field carries the source's form; alternative names can be recorded
  separately.

Neither is currently annotated in a manifest, because no manifests exist yet.
Both will be when the data is restructured.

## Naming

Place names are frequently as contested as the lines.

- `shapeName` carries the name used by the upstream source, in the local
  language.
- `shapeNameEn` may carry an English exonym where one is in common use.
- Alternative or contested names belong in `notes`, with their context.

The project does not rename features to prefer one community's form over
another's. Where a name is genuinely contested, record both and say so.

## Changing this policy

Via an issue and public discussion. It is deliberately mechanical: a policy
that requires judgement about who is right is a policy that will be relitigated
on every pull request.

--8<-- "abbreviations.md"
