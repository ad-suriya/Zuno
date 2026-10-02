// User-facing text keyed by backend codes. F10 turns these maps into the i18n dictionary.
import type { SourceTier, VerificationStatus } from "./types";

export const STEP_TEXT: Record<string, string> = {
  NEVER_SHARE_CREDENTIALS:
    "Never share an OTP, PIN or password with anyone, including people who say they are from a bank or SEBI.",
  IF_SHARED_CALL_BANK: "If you already shared one, call your bank now and block your card or UPI.",
  UNINSTALL_REMOTE_APP: "Uninstall the screen-sharing app, and do not install it again if asked.",
  DO_NOT_INSTALL_APK: "Do not install apps from links. Use only the Play Store or App Store.",
  DO_NOT_PAY_YET: "Do not send money until the checks below are done.",
  CHECK_SEBI_REGISTER: "Ask for their SEBI registration number and check it yourself on SEBI's website.",
  ASK_WHAT_IS_SOLD: "Ask what product is sold and whether the fee is refundable. Get the answer in writing.",
  TAKE_YOUR_TIME: "A genuine offer will still be there tomorrow. Talk to someone you trust first.",
  CONTACT_VIA_OFFICIAL_DETAILS:
    "Contact them only through the phone or email listed on SEBI's website, not the number that contacted you.",
  REPORT_IF_LOST: "If you have lost money, report it now.",
};

/** Steps that get an official link under their text. */
export const STEP_LINK: Record<string, { href: string; label: string }> = {
  CHECK_SEBI_REGISTER: { href: "https://www.sebi.gov.in", label: "sebi.gov.in" },
  CONTACT_VIA_OFFICIAL_DETAILS: { href: "https://www.sebi.gov.in", label: "sebi.gov.in" },
  REPORT_IF_LOST: { href: "https://cybercrime.gov.in", label: "cybercrime.gov.in" },
};

export const VERIFICATION_TEXT: Record<VerificationStatus, { label: string; note?: string }> = {
  VERIFIED: {
    label: "Matches",
    note: "This confirms who they are on the official record. It does not confirm that the person who contacted you works for them.",
  },
  CONTRADICTED: { label: "Does not match" },
  NOT_VERIFIED: { label: "Not found", note: "Not finding it does not mean it is fake: the list may be out of date." },
  UNKNOWN: { label: "Not checked yet" },
  NOT_APPLICABLE: { label: "Does not apply" },
};

export const TIER_TEXT: Record<SourceTier, string> = {
  1: "official regulator",
  2: "official company source",
  3: "secondary source",
  4: "what you were told",
};
