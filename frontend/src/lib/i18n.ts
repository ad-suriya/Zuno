// UI strings per language (F10). The backend sends codes (signal codes, reason rules,
// next-step codes, verification codes); this file turns them into text.
// Adding a language = add a dictionary here (typecheck enforces every key) + backend
// app/i18n.py templates + regex variants. Tamil copy must be reviewed by a native speaker.

import type { Language } from "./types";

const en = {
  "app.tagline": "Know before you act. Check a financial offer before you put money at risk.",
  "app.footer":
    "Zuno does not give investment advice or predict prices. If you have lost money, report it at cybercrime.gov.in or call 1930.",
  "lang.label": "Language",

  "status.checking": "Checking server…",
  "status.db_ok": "Server v{version} · database connected",
  "status.db_down": "Server v{version} · database unavailable",
  "status.recheck": "Recheck",

  "story.label": "What happened?",
  "story.help":
    "Tell us about the offer in your own words: who contacted you, what they promised, and what they asked for.",
  "story.placeholder":
    "A Telegram group admin said I will get guaranteed 20% monthly returns if I invest ₹25,000…",
  "story.channel": "How were you approached?",
  "story.submit": "Check this offer",
  "story.checking": "Checking…",
  "story.examples": "Try an example:",
  "safety.no_secrets": "Do not type any OTP, PIN, password or card number.",

  "channel.unknown": "Not sure",
  "channel.whatsapp": "WhatsApp",
  "channel.telegram": "Telegram",
  "channel.call": "Phone call",
  "channel.social": "Social media",
  "channel.email": "Email",
  "channel.referral": "Friend or relative",
  "channel.in_person": "In person",
  "channel.other": "Other",

  "inv.new": "Start a new check",
  "inv.conversation": "Investigation",
  "inv.zuno": "Zuno",
  "inv.you": "You",
  "inv.thinking": "Zuno is checking…",
  "inv.answer_placeholder": "Type your answer…",
  "inv.send": "Send",
  "inv.dont_know": "I don't know",
  "inv.skip": "Skip",
  "inv.finish": "Finish",
  "inv.skipped": "(skipped)",
  "inv.done": "Thanks. Zuno has what it needs for now. You can still add more messages below.",
  "inv.done_critical": "Zuno stopped asking questions because of a serious safety warning. Please read the steps.",
  "inv.finished": "You finished the investigation.",
  "inv.add_more": "Add another message or detail",
  "inv.add_more_help": "Paste a forwarded message or write what the caller said.",
  "inv.add": "Add and re-check",
  "inv.adding": "Adding…",
  "inv.autoplay": "Read questions aloud",

  "voice.speak": "Speak",
  "voice.stop": "Stop recording",
  "voice.recording": "Recording… (max 60 s)",
  "voice.transcribing": "Turning speech into text…",
  "voice.confirm": "Is this what you said? Edit it if needed, then send.",
  "voice.unsupported": "Voice isn't available in this browser. Please type instead.",
  "voice.denied": "Microphone permission was denied. Please type instead.",
  "voice.listen": "Listen",
  "voice.playing": "Playing…",

  "image.upload": "Upload a screenshot",
  "image.reading": "Reading the screenshot…",
  "image.confirm": "Is this the text in the screenshot? Edit it if needed, then add it.",
  "image.sensitive":
    "This screenshot may show an OTP, bank or card details. Please crop those out. We have hidden any codes we found.",
  "image.add": "Add this text",
  "image.cancel": "Cancel",
  "image.not_stored": "The image itself is not stored.",

  "result.assessment": "Assessment",
  "result.why": "Why",
  "result.cites_signals": "{count} signal(s)",
  "result.cites_checks": "{count} check(s)",
  "result.listen": "Listen",
  "result.redacted":
    "We removed what looked like an OTP, PIN, password or card number before saving. Never share these with anyone.",
  "result.next_steps": "What to do now",
  "result.warnings": "Warning signals found ({count})",
  "result.no_warnings": "None found in the text so far. This does not mean the offer is safe; it still needs checking.",
  "result.reassuring": "What looks right",
  "result.reassuring_caveat": "These don't make an offer safe on their own.",
  "result.checked": "What we checked",
  "result.source": "Source",
  "result.understood": "What we understood",
  "result.understood_help": "Spot a mistake? Add a message to correct it.",
  "result.trail": "Evidence trail",
  "result.from": "Found in: {where}",
  "result.no_signals_here": "No warning signals in this item.",
  "result.ai_note": "Written by AI from the checks above. The level is decided by fixed rules.",

  "level.LOW_CONCERN": "Low concern",
  "level.NEEDS_VERIFICATION": "Needs verification",
  "level.HIGH_CONCERN": "High concern",
  "level.LOW_CONCERN.summary": "No major warning signals were identified from the information available.",
  "level.NEEDS_VERIFICATION.summary": "Important information is missing or could not be independently verified.",
  "level.HIGH_CONCERN.summary": "Significant warning signals are present, based on the information provided.",

  "severity.CRITICAL": "Critical",
  "severity.HIGH": "High",
  "severity.MEDIUM": "Medium",
  "severity.LOW": "Low",

  "evidence.story": "Your story",
  "evidence.text": "Added message",
  "evidence.answer": "Your answer",
  "evidence.image_text": "From screenshot",

  "reason.CRITICAL_SAFETY_SIGNAL": "A request for an OTP, PIN, password, credentials or remote access was found.",
  "reason.CONTRADICTED_CLAIM": "A claim made to you was contradicted by a trusted source.",
  "reason.MULTIPLE_SIGNIFICANT_WARNINGS": "Several significant warning signals are present together.",
  "reason.WARNING_SIGNALS_PRESENT": "Some warning signals were found that should be checked before acting.",
  "reason.UNVERIFIED_CLAIMS": "Important claims could not be verified. This does not mean they are false.",
  "reason.NO_TRUSTED_VERIFICATION":
    "Nothing has been confirmed by an official source yet. Important information is missing.",
  "reason.VERIFIED_CLAIMS":
    "Some claims were confirmed by trusted sources. This confirms the named entity exists; it does not prove that the person who contacted you represents it.",
  "reason.NO_MAJOR_WARNINGS": "No major warning signals were identified from the information available.",

  "signal.OTP_REQUEST":
    "An OTP is mentioned. Genuine investment platforms, banks and regulators never ask you to share an OTP.",
  "signal.UPI_PIN_REQUEST":
    "A PIN is mentioned. You never need to enter a UPI PIN to receive money, and no one should ask for it.",
  "signal.PASSWORD_REQUEST": "A password is mentioned. No genuine opportunity requires your password.",
  "signal.CREDENTIAL_REQUEST":
    "Bank, card or trading-account credentials are mentioned. These should never be shared with anyone.",
  "signal.REMOTE_ACCESS_REQUEST":
    "Remote access or screen sharing is mentioned. This can give someone control of your phone or bank apps.",
  "signal.GUARANTEED_RETURNS":
    "Returns are described as guaranteed or risk-free. Real investments carry risk, and SEBI-registered entities are not allowed to guarantee returns.",
  "signal.UNREALISTIC_RETURN_RATE": "The promised return rate is far above what regulated investments normally offer.",
  "signal.DOUBLING_MONEY": "The offer promises to double money, which is a common pattern in fraudulent schemes.",
  "signal.WITHDRAWAL_FEE":
    "You are asked to pay before you can withdraw your own money. This is a common pattern in fraudulent schemes.",
  "signal.APK_INSTALL": "You are asked to install an app from outside the Play Store / App Store.",
  "signal.SURE_SHOT_TIP":
    "The offer claims certain or insider knowledge about market moves. No one can know this reliably.",
  "signal.URGENCY_PRESSURE":
    "You are being pressured to act quickly. Pressure to decide fast leaves no time to verify.",
  "signal.RECRUITMENT_DEPENDENCE":
    "Earnings seem to depend on bringing in other people. This needs a closer look at whether real products or services are sold.",
  "signal.ENTRY_FEE": "An upfront fee is required to join. Check what the fee is for and whether it is refundable.",
  "signal.SECRECY": "You are asked to keep this secret. Genuine opportunities do not need secrecy from your family.",
  "signal.REGISTRATION_VERIFIED": "The registration was found on SEBI's official register.",
  "signal.NO_UPFRONT_PAYMENT": "No upfront payment has been asked for so far.",
  "signal.REALISTIC_RETURN_CLAIM": "The return mentioned is in a normal range and is not described as guaranteed.",
  "signal.OFFICIAL_CHANNEL_PAYMENT": "The payment account appears to be in the registered firm's name.",

  "step.NEVER_SHARE_CREDENTIALS":
    "Never share an OTP, PIN or password with anyone, including people claiming to be from a bank or SEBI.",
  "step.IF_SHARED_CALL_BANK": "If you already shared one, call your bank now and block the card/UPI.",
  "step.UNINSTALL_REMOTE_APP": "Uninstall the screen-sharing app and do not reinstall it on request.",
  "step.DO_NOT_INSTALL_APK": "Do not install apps from links. Use only the Play Store / App Store.",
  "step.DO_NOT_PAY_YET": "Do not send money until the checks below are done.",
  "step.CHECK_SEBI_REGISTER": "Ask for the SEBI registration number and check it on sebi.gov.in.",
  "step.ASK_WHAT_IS_SOLD": "Ask what product is sold and whether the fee is refundable, in writing.",
  "step.TAKE_YOUR_TIME": "A genuine offer will still be there tomorrow. Talk to someone you trust.",
  "step.CONTACT_VIA_OFFICIAL_DETAILS":
    "Contact them only through the phone, email or website listed on SEBI's site, not the details in the message.",
  "step.REPORT_IF_LOST": "If you lost money, report at cybercrime.gov.in or call 1930.",

  "vstatus.VERIFIED": "Verified",
  "vstatus.NOT_VERIFIED": "Couldn't verify",
  "vstatus.CONTRADICTED": "Doesn't match",
  "vstatus.UNKNOWN": "Need more information",
  "vstatus.NOT_APPLICABLE": "Not applicable",

  "vcode.REG_NAME_MATCH":
    "SEBI's register lists {reg_no} as {registered_name}, matching the name you were given. This confirms the firm is registered; it does not confirm the person contacting you represents it. Contact them only via the details on SEBI's site.",
  "vcode.REG_NAME_MISMATCH":
    "SEBI's register lists {reg_no} as {registered_name}, not {claimed_name}. Someone may be using another firm's registration number.",
  "vcode.REG_EXPIRED": "{reg_no} ({registered_name}) expired on {valid_till}, so it is not currently valid.",
  "vcode.REG_NAME_UNCLEAR":
    "SEBI's register lists {reg_no} as {registered_name}. We can't tell for sure whether that is the name you were given; check it on sebi.gov.in.",
  "vcode.REG_NO_NAME":
    "{reg_no} is registered to {registered_name}. Is that the company that contacted you? Tell us the company name to compare.",
  "vcode.REG_NOT_FOUND":
    "We couldn't find {reg_no} in SEBI's register (our copy is from {snapshot_date}). That doesn't mean it's fake, but check it on sebi.gov.in before paying.",
  "vcode.REG_MALFORMED":
    "{reg_no} doesn't look like a valid SEBI registration number (for example INA, INH or INZ followed by 9 digits). Ask them to confirm it.",
  "vcode.REG_CATEGORY_NOT_COVERED":
    "We couldn't check {reg_no} automatically. That doesn't mean it's fake: check it on sebi.gov.in.",
  "vcode.REGISTRATION_CLAIM_NO_NUMBER":
    "They say they are SEBI registered, but we need the registration number to check it.",
  "vcode.NAME_FOUND":
    "A firm named {registered_name} is on SEBI's register ({reg_no}). This does not confirm the person contacting you represents it.",
  "vcode.NAME_NOT_FOUND":
    "We couldn't find {claimed_name} in SEBI's register. That doesn't mean it's fake, but anyone giving investment advice or tips for a fee must be SEBI registered.",
  "vcode.SEBI_NOT_APPLICABLE": "SEBI registration does not apply to this kind of offer. Check the next steps instead.",

  "entity.company": "Company",
  "entity.person": "Person",
  "entity.app": "App",
  "entity.website": "Website",
  "entity.phone": "Phone",
  "entity.upi_id": "UPI ID",
  "entity.registration_number": "Registration no.",
  "entity.other": "Other",
  "claim.registration": "Registration",
  "claim.returns": "Returns",
  "claim.identity": "Identity",
  "claim.payment": "Payment",
  "claim.documentation": "Documents",
  "claim.product": "Product",
  "claim.other": "Other",
  "facts.money": "Money",
  "facts.offer_type": "Type of offer",

  "error.NETWORK_ERROR": "Could not reach the Zuno server. Check your connection and try again.",
  "error.TIMEOUT": "The server took too long to respond. Please try again.",
  "error.VOICE_UNAVAILABLE": "Voice is not available right now. Please type instead.",
  "error.IMAGE_UNAVAILABLE": "We couldn't read the image. Please type the message instead.",
  "error.TOO_LARGE": "The file is too large (max 5 MB).",
  "error.UNSUPPORTED_MEDIA": "Please upload a PNG or JPEG screenshot.",
  "error.RATE_LIMITED": "Too many voice requests. Please wait a minute, or type instead.",
  "error.NOT_FOUND": "This investigation was not found. It may have expired.",
  "error.STORAGE_UNAVAILABLE": "Storage is temporarily unavailable. Try again.",
  "error.generic": "Something went wrong. Please try again.",
  "error.reference": "Reference: {id}",
};

export type MessageKey = keyof typeof en;

const ta = {
  "app.tagline": "செயல்படும் முன் தெரிந்துகொள்ளுங்கள். பணம் போடும் முன் நிதி வாய்ப்பைச் சரிபாருங்கள்.",
  "app.footer":
    "Zuno முதலீட்டு ஆலோசனை தருவதில்லை, விலைகளைக் கணிப்பதில்லை. பணம் இழந்திருந்தால் cybercrime.gov.in-இல் புகார் செய்யுங்கள் அல்லது 1930-ஐ அழையுங்கள்.",
  "lang.label": "மொழி",

  "status.checking": "சர்வரைச் சரிபார்க்கிறது…",
  "status.db_ok": "சர்வர் v{version} · தரவுத்தளம் இணைந்துள்ளது",
  "status.db_down": "சர்வர் v{version} · தரவுத்தளம் கிடைக்கவில்லை",
  "status.recheck": "மீண்டும் சரிபார்",

  "story.label": "என்ன நடந்தது?",
  "story.help":
    "உங்கள் சொந்த வார்த்தைகளில் சொல்லுங்கள்: யார் தொடர்பு கொண்டார்கள், என்ன வாக்குறுதி கொடுத்தார்கள், என்ன கேட்டார்கள்.",
  "story.placeholder": "டெலிகிராம் குழுவில் ஒருவர் ₹25,000 போட்டால் மாதம் 20% லாபம் உத்தரவாதம் என்றார்…",
  "story.channel": "உங்களை எப்படித் தொடர்பு கொண்டார்கள்?",
  "story.submit": "இந்த வாய்ப்பைச் சரிபார்",
  "story.checking": "சரிபார்க்கிறது…",
  "story.examples": "ஒரு உதாரணத்தை முயற்சிக்கவும்:",
  "safety.no_secrets": "OTP, PIN, பாஸ்வேர்டு அல்லது கார்டு எண் எதையும் டைப் செய்ய வேண்டாம்.",

  "channel.unknown": "தெரியவில்லை",
  "channel.whatsapp": "WhatsApp",
  "channel.telegram": "Telegram",
  "channel.call": "தொலைபேசி அழைப்பு",
  "channel.social": "சமூக ஊடகம்",
  "channel.email": "மின்னஞ்சல்",
  "channel.referral": "நண்பர் அல்லது உறவினர்",
  "channel.in_person": "நேரில்",
  "channel.other": "மற்றவை",

  "inv.new": "புதிய சரிபார்ப்பைத் தொடங்கு",
  "inv.conversation": "விசாரணை",
  "inv.zuno": "Zuno",
  "inv.you": "நீங்கள்",
  "inv.thinking": "Zuno சரிபார்க்கிறது…",
  "inv.answer_placeholder": "உங்கள் பதிலை டைப் செய்யுங்கள்…",
  "inv.send": "அனுப்பு",
  "inv.dont_know": "எனக்குத் தெரியாது",
  "inv.skip": "தவிர்",
  "inv.finish": "முடி",
  "inv.skipped": "(தவிர்க்கப்பட்டது)",
  "inv.done": "நன்றி. இப்போதைக்கு Zuno-விற்குத் தேவையானது கிடைத்துவிட்டது. கீழே மேலும் மெசேஜ்களைச் சேர்க்கலாம்.",
  "inv.done_critical": "தீவிர பாதுகாப்பு எச்சரிக்கை இருப்பதால் Zuno கேள்விகளை நிறுத்தியது. படிகளைப் படியுங்கள்.",
  "inv.finished": "நீங்கள் விசாரணையை முடித்துவிட்டீர்கள்.",
  "inv.add_more": "மேலும் ஒரு மெசேஜ் அல்லது விவரத்தைச் சேர்க்கவும்",
  "inv.add_more_help": "ஃபார்வர்டு செய்த மெசேஜை ஒட்டவும், அல்லது அழைத்தவர் சொன்னதை எழுதவும்.",
  "inv.add": "சேர்த்து மீண்டும் சரிபார்",
  "inv.adding": "சேர்க்கிறது…",
  "inv.autoplay": "கேள்விகளை உரக்கப் படி",

  "voice.speak": "பேசுங்கள்",
  "voice.stop": "பதிவை நிறுத்து",
  "voice.recording": "பதிவாகிறது… (அதிகபட்சம் 60 வினாடி)",
  "voice.transcribing": "பேச்சை எழுத்தாக மாற்றுகிறது…",
  "voice.confirm": "நீங்கள் சொன்னது இதுதானா? தேவைப்பட்டால் திருத்தி, பிறகு அனுப்புங்கள்.",
  "voice.unsupported": "இந்த பிரவுசரில் குரல் வசதி இல்லை. டைப் செய்யுங்கள்.",
  "voice.denied": "மைக்ரோஃபோன் அனுமதி மறுக்கப்பட்டது. டைப் செய்யுங்கள்.",
  "voice.listen": "கேளுங்கள்",
  "voice.playing": "ஒலிக்கிறது…",

  "image.upload": "ஸ்கிரீன்ஷாட்டைப் பதிவேற்று",
  "image.reading": "ஸ்கிரீன்ஷாட்டைப் படிக்கிறது…",
  "image.confirm": "ஸ்கிரீன்ஷாட்டில் உள்ள உரை இதுதானா? தேவைப்பட்டால் திருத்தி, பிறகு சேர்க்கவும்.",
  "image.sensitive":
    "இந்த ஸ்கிரீன்ஷாட்டில் OTP, வங்கி அல்லது கார்டு விவரங்கள் இருக்கலாம். அவற்றை வெட்டி நீக்குங்கள். நாங்கள் கண்ட எண்களை மறைத்துவிட்டோம்.",
  "image.add": "இந்த உரையைச் சேர்",
  "image.cancel": "ரத்து",
  "image.not_stored": "படம் சேமிக்கப்படுவதில்லை.",

  "result.assessment": "மதிப்பீடு",
  "result.why": "ஏன்",
  "result.cites_signals": "{count} அறிகுறி(கள்)",
  "result.cites_checks": "{count} சோதனை(கள்)",
  "result.listen": "கேளுங்கள்",
  "result.redacted":
    "OTP, PIN, பாஸ்வேர்டு அல்லது கார்டு எண் போலத் தோன்றியதை சேமிக்கும் முன் நீக்கிவிட்டோம். இவற்றை யாரிடமும் பகிர வேண்டாம்.",
  "result.next_steps": "இப்போது செய்ய வேண்டியவை",
  "result.warnings": "கண்டறியப்பட்ட எச்சரிக்கை அறிகுறிகள் ({count})",
  "result.no_warnings":
    "இதுவரை எதுவும் கண்டறியப்படவில்லை. அதனால் இந்த வாய்ப்பு பாதுகாப்பானது என்று அர்த்தமல்ல; இன்னும் சரிபார்க்க வேண்டும்.",
  "result.reassuring": "சரியாகத் தோன்றுபவை",
  "result.reassuring_caveat": "இவை மட்டுமே ஒரு வாய்ப்பைப் பாதுகாப்பானதாக்காது.",
  "result.checked": "நாங்கள் சரிபார்த்தவை",
  "result.source": "ஆதாரம்",
  "result.understood": "நாங்கள் புரிந்துகொண்டவை",
  "result.understood_help": "தவறு இருக்கிறதா? அதைத் திருத்த ஒரு மெசேஜைச் சேர்க்கவும்.",
  "result.trail": "ஆதாரப் பதிவு",
  "result.from": "கண்டது: {where}",
  "result.no_signals_here": "இதில் எச்சரிக்கை அறிகுறிகள் இல்லை.",
  "result.ai_note": "மேலே உள்ள சோதனைகளிலிருந்து AI எழுதியது. நிலையை நிலையான விதிகள் முடிவு செய்கின்றன.",

  "level.LOW_CONCERN": "குறைந்த கவலை",
  "level.NEEDS_VERIFICATION": "சரிபார்ப்பு தேவை",
  "level.HIGH_CONCERN": "அதிக கவலை",
  "level.LOW_CONCERN.summary": "கிடைத்த தகவலில் பெரிய எச்சரிக்கை அறிகுறிகள் எதுவும் இல்லை.",
  "level.NEEDS_VERIFICATION.summary": "முக்கியத் தகவல் இல்லை, அல்லது தனியாகச் சரிபார்க்க முடியவில்லை.",
  "level.HIGH_CONCERN.summary": "நீங்கள் கொடுத்த தகவலின்படி, தீவிர எச்சரிக்கை அறிகுறிகள் உள்ளன.",

  "severity.CRITICAL": "மிகத் தீவிரம்",
  "severity.HIGH": "தீவிரம்",
  "severity.MEDIUM": "நடுத்தரம்",
  "severity.LOW": "குறைவு",

  "evidence.story": "உங்கள் கதை",
  "evidence.text": "சேர்த்த மெசேஜ்",
  "evidence.answer": "உங்கள் பதில்",
  "evidence.image_text": "ஸ்கிரீன்ஷாட்டிலிருந்து",

  "reason.CRITICAL_SAFETY_SIGNAL": "OTP, PIN, பாஸ்வேர்டு, வங்கி விவரங்கள் அல்லது ரிமோட் அக்சஸ் கேட்கப்பட்டுள்ளது.",
  "reason.CONTRADICTED_CLAIM": "உங்களிடம் சொன்ன ஒரு தகவல் நம்பகமான ஆதாரத்துடன் பொருந்தவில்லை.",
  "reason.MULTIPLE_SIGNIFICANT_WARNINGS": "பல தீவிர எச்சரிக்கை அறிகுறிகள் ஒன்றாக உள்ளன.",
  "reason.WARNING_SIGNALS_PRESENT": "செயல்படுவதற்கு முன் சரிபார்க்க வேண்டிய சில எச்சரிக்கை அறிகுறிகள் உள்ளன.",
  "reason.UNVERIFIED_CLAIMS": "முக்கியத் தகவல்களைச் சரிபார்க்க முடியவில்லை. அவை பொய் என்று அர்த்தமல்ல.",
  "reason.NO_TRUSTED_VERIFICATION":
    "இதுவரை எதுவும் அதிகாரப்பூர்வ ஆதாரத்தால் உறுதிப்படுத்தப்படவில்லை. முக்கியத் தகவல் இல்லை.",
  "reason.VERIFIED_CLAIMS":
    "சில தகவல்கள் நம்பகமான ஆதாரங்களால் உறுதிசெய்யப்பட்டன. அந்த நிறுவனம் இருக்கிறது என்பதை இது காட்டுகிறது; உங்களைத் தொடர்பு கொண்டவர் அவர்களின் பிரதிநிதி என்பதை நிரூபிக்கவில்லை.",
  "reason.NO_MAJOR_WARNINGS": "கிடைத்த தகவலில் பெரிய எச்சரிக்கை அறிகுறிகள் எதுவும் இல்லை.",

  "signal.OTP_REQUEST":
    "OTP பற்றி பேசப்பட்டுள்ளது. உண்மையான முதலீட்டு தளங்கள், வங்கிகள், ஒழுங்குமுறை அமைப்புகள் OTP-ஐ ஒருபோதும் கேட்பதில்லை.",
  "signal.UPI_PIN_REQUEST":
    "PIN பற்றி பேசப்பட்டுள்ளது. பணம் பெற UPI PIN தேவையில்லை; யாரும் அதைக் கேட்கக் கூடாது.",
  "signal.PASSWORD_REQUEST": "பாஸ்வேர்டு பற்றி பேசப்பட்டுள்ளது. எந்த உண்மையான வாய்ப்புக்கும் உங்கள் பாஸ்வேர்டு தேவையில்லை.",
  "signal.CREDENTIAL_REQUEST":
    "வங்கி, கார்டு அல்லது டிரேடிங் கணக்கு விவரங்கள் கேட்கப்பட்டுள்ளன. இவற்றை யாரிடமும் பகிரக் கூடாது.",
  "signal.REMOTE_ACCESS_REQUEST":
    "ரிமோட் அக்சஸ் அல்லது ஸ்கிரீன் ஷேரிங் பற்றி பேசப்பட்டுள்ளது. இதனால் உங்கள் ஃபோன் அல்லது வங்கி ஆப்களை வேறொருவர் கட்டுப்படுத்தலாம்.",
  "signal.GUARANTEED_RETURNS":
    "லாபம் உத்தரவாதம் அல்லது ரிஸ்க் இல்லை என்று சொல்லப்படுகிறது. உண்மையான முதலீடுகளில் ரிஸ்க் உண்டு; SEBI பதிவு பெற்றவர்கள் லாபத்திற்கு உத்தரவாதம் தர அனுமதி இல்லை.",
  "signal.UNREALISTIC_RETURN_RATE":
    "சொல்லப்பட்ட லாப விகிதம், முறையான முதலீடுகள் பொதுவாகத் தருவதை விட மிக அதிகம்.",
  "signal.DOUBLING_MONEY": "பணத்தை இரட்டிப்பாக்குவதாக வாக்குறுதி. இது மோசடித் திட்டங்களில் அடிக்கடி காணப்படும் முறை.",
  "signal.WITHDRAWAL_FEE":
    "உங்கள் சொந்தப் பணத்தை எடுக்க முன்பணம் கட்டச் சொல்கிறார்கள். இது மோசடித் திட்டங்களில் அடிக்கடி காணப்படும் முறை.",
  "signal.APK_INSTALL": "Play Store / App Store-க்கு வெளியே இருந்து ஒரு ஆப்பை நிறுவச் சொல்கிறார்கள்.",
  "signal.SURE_SHOT_TIP":
    "சந்தை நகர்வுகள் பற்றி உறுதியான அல்லது உள் தகவல் இருப்பதாகச் சொல்கிறார்கள். இதை யாராலும் நம்பகமாக அறிய முடியாது.",
  "signal.URGENCY_PRESSURE":
    "விரைவாக முடிவெடுக்க அழுத்தம் கொடுக்கப்படுகிறது. அவசரப்படுத்துவதால் சரிபார்க்க நேரம் கிடைக்காது.",
  "signal.RECRUITMENT_DEPENDENCE":
    "வருமானம் மற்றவர்களைச் சேர்ப்பதைச் சார்ந்திருப்பது போல் தெரிகிறது. உண்மையான பொருள் அல்லது சேவை விற்கப்படுகிறதா என்று பார்க்க வேண்டும்.",
  "signal.ENTRY_FEE": "சேர முன்கூட்டியே கட்டணம் கேட்கிறார்கள். அது எதற்காக, திரும்பக் கிடைக்குமா என்று பாருங்கள்.",
  "signal.SECRECY": "இதை ரகசியமாக வைக்கச் சொல்கிறார்கள். உண்மையான வாய்ப்புகளுக்கு குடும்பத்திடம் ரகசியம் தேவையில்லை.",
  "signal.REGISTRATION_VERIFIED": "இந்தப் பதிவு SEBI-யின் அதிகாரப்பூர்வ பதிவேட்டில் உள்ளது.",
  "signal.NO_UPFRONT_PAYMENT": "இதுவரை முன்பணம் எதுவும் கேட்கப்படவில்லை.",
  "signal.REALISTIC_RETURN_CLAIM": "சொல்லப்பட்ட லாபம் இயல்பான அளவில் உள்ளது, உத்தரவாதம் என்று சொல்லப்படவில்லை.",
  "signal.OFFICIAL_CHANNEL_PAYMENT": "பணம் செலுத்தும் கணக்கு பதிவு பெற்ற நிறுவனத்தின் பெயரில் இருப்பதாகத் தெரிகிறது.",

  "step.NEVER_SHARE_CREDENTIALS":
    "OTP, PIN, பாஸ்வேர்டு எதையும் யாரிடமும் பகிர வேண்டாம் — வங்கி அல்லது SEBI-யிலிருந்து பேசுவதாகச் சொன்னாலும் கூட.",
  "step.IF_SHARED_CALL_BANK": "ஏற்கனவே பகிர்ந்திருந்தால், உடனே உங்கள் வங்கியை அழைத்து கார்டு/UPI-ஐ முடக்குங்கள்.",
  "step.UNINSTALL_REMOTE_APP": "ஸ்கிரீன் ஷேரிங் ஆப்பை நீக்குங்கள்; அவர்கள் கேட்டாலும் மீண்டும் நிறுவ வேண்டாம்.",
  "step.DO_NOT_INSTALL_APK": "லிங்க் மூலம் வரும் ஆப்களை நிறுவ வேண்டாம். Play Store / App Store மட்டும் பயன்படுத்துங்கள்.",
  "step.DO_NOT_PAY_YET": "கீழே உள்ள சோதனைகள் முடியும் வரை பணம் அனுப்ப வேண்டாம்.",
  "step.CHECK_SEBI_REGISTER": "SEBI பதிவு எண்ணைக் கேட்டு, sebi.gov.in-இல் சரிபாருங்கள்.",
  "step.ASK_WHAT_IS_SOLD": "என்ன பொருள் விற்கப்படுகிறது, கட்டணம் திரும்பக் கிடைக்குமா என்று எழுத்துப்பூர்வமாகக் கேளுங்கள்.",
  "step.TAKE_YOUR_TIME": "உண்மையான வாய்ப்பு நாளையும் இருக்கும். நம்பிக்கையான ஒருவரிடம் பேசுங்கள்.",
  "step.CONTACT_VIA_OFFICIAL_DETAILS":
    "SEBI இணையதளத்தில் உள்ள தொலைபேசி, மின்னஞ்சல் அல்லது இணையதளம் மூலம் மட்டுமே அவர்களைத் தொடர்பு கொள்ளுங்கள்; மெசேஜில் வந்த விவரங்கள் மூலம் அல்ல.",
  "step.REPORT_IF_LOST": "பணம் இழந்திருந்தால், cybercrime.gov.in-இல் புகார் செய்யுங்கள் அல்லது 1930-ஐ அழையுங்கள்.",

  "vstatus.VERIFIED": "சரிபார்க்கப்பட்டது",
  "vstatus.NOT_VERIFIED": "சரிபார்க்க முடியவில்லை",
  "vstatus.CONTRADICTED": "பொருந்தவில்லை",
  "vstatus.UNKNOWN": "மேலும் தகவல் தேவை",
  "vstatus.NOT_APPLICABLE": "பொருந்தாது",

  "vcode.REG_NAME_MATCH":
    "SEBI பதிவேட்டில் {reg_no} என்பது {registered_name} பெயரில் உள்ளது; உங்களிடம் சொன்ன பெயருடன் பொருந்துகிறது. நிறுவனம் பதிவு பெற்றது என்பதை இது காட்டுகிறது; உங்களைத் தொடர்பு கொண்டவர் அவர்களின் பிரதிநிதி என்பதை அல்ல. SEBI தளத்தில் உள்ள விவரங்கள் மூலம் மட்டுமே தொடர்பு கொள்ளுங்கள்.",
  "vcode.REG_NAME_MISMATCH":
    "SEBI பதிவேட்டில் {reg_no} என்பது {registered_name} பெயரில் உள்ளது, {claimed_name} பெயரில் அல்ல. வேறொரு நிறுவனத்தின் பதிவு எண்ணை யாரோ பயன்படுத்தக்கூடும்.",
  "vcode.REG_EXPIRED": "{reg_no} ({registered_name}) பதிவு {valid_till} அன்று காலாவதியானது; இப்போது செல்லுபடியாகாது.",
  "vcode.REG_NAME_UNCLEAR":
    "SEBI பதிவேட்டில் {reg_no} என்பது {registered_name} பெயரில் உள்ளது. அது உங்களிடம் சொன்ன பெயர்தானா என்று உறுதியாகச் சொல்ல முடியவில்லை; sebi.gov.in-இல் சரிபாருங்கள்.",
  "vcode.REG_NO_NAME":
    "{reg_no} என்பது {registered_name} பெயரில் பதிவாகியுள்ளது. உங்களைத் தொடர்பு கொண்டது அந்த நிறுவனம்தானா? ஒப்பிட நிறுவனத்தின் பெயரைச் சொல்லுங்கள்.",
  "vcode.REG_NOT_FOUND":
    "{reg_no}-ஐ SEBI பதிவேட்டில் கண்டுபிடிக்க முடியவில்லை (எங்கள் நகல் {snapshot_date} தேதியது). அது போலி என்று அர்த்தமல்ல; பணம் கட்டும் முன் sebi.gov.in-இல் சரிபாருங்கள்.",
  "vcode.REG_MALFORMED":
    "{reg_no} சரியான SEBI பதிவு எண் போலத் தெரியவில்லை (உதாரணம்: INA, INH அல்லது INZ பிறகு 9 இலக்கங்கள்). அவர்களிடம் உறுதிப்படுத்தச் சொல்லுங்கள்.",
  "vcode.REG_CATEGORY_NOT_COVERED":
    "{reg_no}-ஐ தானாகச் சரிபார்க்க முடியவில்லை. அது போலி என்று அர்த்தமல்ல: sebi.gov.in-இல் சரிபாருங்கள்.",
  "vcode.REGISTRATION_CLAIM_NO_NUMBER":
    "SEBI பதிவு பெற்றவர்கள் என்று சொல்கிறார்கள், ஆனால் சரிபார்க்க பதிவு எண் தேவை.",
  "vcode.NAME_FOUND":
    "{registered_name} என்ற நிறுவனம் SEBI பதிவேட்டில் உள்ளது ({reg_no}). உங்களைத் தொடர்பு கொண்டவர் அவர்களின் பிரதிநிதி என்பதை இது உறுதிப்படுத்தவில்லை.",
  "vcode.NAME_NOT_FOUND":
    "{claimed_name}-ஐ SEBI பதிவேட்டில் கண்டுபிடிக்க முடியவில்லை. அது போலி என்று அர்த்தமல்ல; ஆனால் கட்டணம் வாங்கி முதலீட்டு ஆலோசனை அல்லது டிப்ஸ் தருபவர்கள் SEBI பதிவு பெற்றிருக்க வேண்டும்.",
  "vcode.SEBI_NOT_APPLICABLE": "இந்த வகை வாய்ப்புக்கு SEBI பதிவு பொருந்தாது. அதற்குப் பதிலாக அடுத்த படிகளைப் பாருங்கள்.",

  "entity.company": "நிறுவனம்",
  "entity.person": "நபர்",
  "entity.app": "ஆப்",
  "entity.website": "இணையதளம்",
  "entity.phone": "தொலைபேசி",
  "entity.upi_id": "UPI ID",
  "entity.registration_number": "பதிவு எண்",
  "entity.other": "மற்றவை",
  "claim.registration": "பதிவு",
  "claim.returns": "லாபம்",
  "claim.identity": "அடையாளம்",
  "claim.payment": "பணம் செலுத்துதல்",
  "claim.documentation": "ஆவணங்கள்",
  "claim.product": "பொருள்",
  "claim.other": "மற்றவை",
  "facts.money": "பணம்",
  "facts.offer_type": "வாய்ப்பின் வகை",

  "error.NETWORK_ERROR": "Zuno சர்வரை அடைய முடியவில்லை. இணைப்பைச் சரிபார்த்து மீண்டும் முயற்சிக்கவும்.",
  "error.TIMEOUT": "சர்வர் பதிலளிக்க அதிக நேரம் எடுத்தது. மீண்டும் முயற்சிக்கவும்.",
  "error.VOICE_UNAVAILABLE": "இப்போது குரல் வசதி இல்லை. டைப் செய்யுங்கள்.",
  "error.IMAGE_UNAVAILABLE": "படத்தைப் படிக்க முடியவில்லை. மெசேஜை டைப் செய்யுங்கள்.",
  "error.TOO_LARGE": "கோப்பு மிகப் பெரியது (அதிகபட்சம் 5 MB).",
  "error.UNSUPPORTED_MEDIA": "PNG அல்லது JPEG ஸ்கிரீன்ஷாட்டைப் பதிவேற்றவும்.",
  "error.RATE_LIMITED": "அதிகமான குரல் கோரிக்கைகள். ஒரு நிமிடம் காத்திருங்கள், அல்லது டைப் செய்யுங்கள்.",
  "error.NOT_FOUND": "இந்த விசாரணை கிடைக்கவில்லை. அது காலாவதியாகியிருக்கலாம்.",
  "error.STORAGE_UNAVAILABLE": "சேமிப்பகம் தற்காலிகமாகக் கிடைக்கவில்லை. மீண்டும் முயற்சிக்கவும்.",
  "error.generic": "ஏதோ தவறு நடந்தது. மீண்டும் முயற்சிக்கவும்.",
  "error.reference": "குறிப்பு எண்: {id}",
} satisfies Record<MessageKey, string>;

const DICTIONARIES: Record<Language, Record<MessageKey, string>> = { en, ta };

export const LANGUAGES: { value: Language; label: string }[] = [
  { value: "en", label: "English" },
  { value: "ta", label: "தமிழ்" },
];

/** Look up a key, filling {placeholders}. Unknown placeholders are left as-is. */
export function translate(language: Language, key: MessageKey, vars: Record<string, string | number> = {}): string {
  const template = DICTIONARIES[language][key] ?? en[key];
  return template.replace(/\{(\w+)\}/g, (match, name: string) => (name in vars ? String(vars[name]) : match));
}

/** For dynamic keys built from backend codes: returns null when the code has no text. */
export function hasKey(key: string): key is MessageKey {
  return key in en;
}
