# dental-cost-index

What a dental implant costs in each US state, against what households there
earn and how many oral surgeons are around to place one.

Runs offline. No network access, no telemetry, nothing to sign up for.

```
$ dental-cost-index WY
Wyoming
=======

Cost
  Single implant, post to crown    $4,259
  One arch, All-on-4 standard      $15,000 to $25,000

Against what households earn
  Median household income          $75,532  (+/- $2,468)
  Single implant                   5.64% of a year's income
  One arch                         26.48% of a year's income

Against what households aged 65+ earn
  Median household income, 65+     $60,674  (+/- $4,038)
  That is                          -19.7% against all ages
  Single implant                   7.02% of a year's income
  One arch                         32.96% of a year's income

Who is there to do the work
  Oral and maxillofacial surgeons  7
  Per 100,000 residents            1.19  (rank 50 of 50)
  ...
```

## Install

```
snap install dental-cost-index
```

or

```
pip install dental-cost-index
```

Python 3.9 or newer. No dependencies.

## Use

```
dental-cost-index WY                      # one state, full report
dental-cost-index Mississippi             # names work too
dental-cost-index --list                  # all 50 states
dental-cost-index --double-bind           # the 15 worst-off states
dental-cost-index --worst-tooth-loss 10   # highest tooth loss among 65+
dental-cost-index --list --sort income    # sort any table
dental-cost-index --csv > states.csv      # every state, every column
dental-cost-index WY --json               # machine-readable
dental-cost-index --sources               # where the numbers come from
```

## Why this exists

Nearly every page about implant prices reports one number, a national average,
sometimes split by state. On its own that does not tell you much. $4,259 means
something different in Mississippi than it does in Maryland, and price is only
half of whether someone can actually get the work done. The other half is
whether a surgeon exists within driving distance.

So this tool puts both halves in the same place.

Fifteen states come out below the national median on oral surgeon supply and
above it on implant cost as a share of income. Those fifteen and the fifteen
that do best do not overlap on household income by a single dollar. Wyoming
has seven oral and maxillofacial surgeons in the whole state.

## The thing you should know before using the numbers

44 of the 50 states show the same $4,259 implant price. That is deliberate and
not a bug.

The underlying cost model carries exactly one geographic adjustment, a major
metro premium, because no defensible sourced figure for a lower-cost-market
discount was ever found. Publishing fifty invented prices would have looked
better and been less true. The practical effect is that the cost-burden column
is mostly driven by the income denominator, so it is not presented as a
discovery on its own.

Surgeon supply is the column that carries weight. It is counted from a source
that knows nothing about prices or incomes, and it still correlates +0.668
with state median household income.

Tooth loss figures are CDC BRFSS 2020, self-reported. The module runs in even
years and 2020 is the most recent year it exists for, and that collection was
disrupted by COVID. The median 95% confidence interval across states is about
2 points either way, so adjacent states are not meaningfully different. The
intervals are in `--csv` output.

Correlations are correlations. Nothing here shows causation and the tool does
not claim any.

Not a price quote. Not clinical advice.

## Data

Full method, limitations and the downloadable dataset:
https://dentalimplantcalc.com/dental-implant-access-gap/

Run `dental-cost-index --sources` for the source list.

## Licence

CC BY 4.0. Take the data, re-cut it, argue with it. Attribution is the only
condition.

If you find an error, open an issue. A correction is more useful than a quiet
workaround.
