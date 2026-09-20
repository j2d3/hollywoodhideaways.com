# hollywoodhideaways.com

Public site for De Longpre Enterprises LLC: the two Hollywood bungalow units, direct booking, contact.
Static HTML, hosted on GitHub Pages, custom domain via Route 53.

Photos and copy come from `~/personal/properties/` (the source-of-truth repo). Edit there first, then here.

## Inquiry form

Posts to Formspree (form ID in the `action` attribute of `#inquiry` in index.html; the account is stay@hollywoodhideaways.com). `_replyto` sets Reply-To to the guest, `_subject` is filled by the page with the home, dates, night count, and calendar result, `_gotcha` is Formspree's honeypot.

`availability.json` holds blocked date ranges per unit and is refreshed every six hours by `.github/workflows/availability.yml` from the two Airbnb iCal exports, whose URLs live in the repo secrets `ICAL_DELONGPRE` and `ICAL_CHEROKEE` (same values as `airbnb_ical_export` in the gitignored `secrets.yaml` files in the properties repo). Run `scripts/availability.py` with those two env vars to regenerate by hand. End dates are checkout days. Airbnb's feed merges its 9-month booking-window block with any manual block inside it, so the trailing range is stored as `window` and the page shows it as "inquire to hold" rather than "taken".
