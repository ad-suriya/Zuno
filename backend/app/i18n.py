"""Text the backend itself produces, per language (F10).

The frontend renders most UI text from codes with its own dictionary
(`frontend/src/lib/i18n.ts`). The backend only needs language text for what it
generates: adaptive question templates (F06), template explanations (F07) and
next steps that are read aloud (F11). Adding a language = add a block to each table.

Tamil copy is plain register and must be reviewed by a native speaker.
"""

from app.models import AssessmentLevel, Language, Unknown

LEVEL_LABEL: dict[Language, dict[AssessmentLevel, str]] = {
    Language.EN: {
        AssessmentLevel.LOW_CONCERN: "Low concern",
        AssessmentLevel.NEEDS_VERIFICATION: "Needs verification",
        AssessmentLevel.HIGH_CONCERN: "High concern",
    },
    Language.TA: {
        AssessmentLevel.LOW_CONCERN: "குறைந்த கவலை",
        AssessmentLevel.NEEDS_VERIFICATION: "சரிபார்ப்பு தேவை",
        AssessmentLevel.HIGH_CONCERN: "அதிக கவலை",
    },
}

LEVEL_SENTENCE: dict[Language, dict[AssessmentLevel, str]] = {
    Language.EN: {
        AssessmentLevel.LOW_CONCERN: "Our assessment: Low concern. No major warning signs were found in what you shared.",
        AssessmentLevel.NEEDS_VERIFICATION: "Our assessment: Needs verification. Important information is missing "
        "or could not be checked yet.",
        AssessmentLevel.HIGH_CONCERN: "Our assessment: High concern, based on the information you provided.",
    },
    Language.TA: {
        AssessmentLevel.LOW_CONCERN: "எங்கள் மதிப்பீடு: குறைந்த கவலை. நீங்கள் பகிர்ந்ததில் பெரிய எச்சரிக்கை அறிகுறிகள் இல்லை.",
        AssessmentLevel.NEEDS_VERIFICATION: "எங்கள் மதிப்பீடு: சரிபார்ப்பு தேவை. முக்கியத் தகவல் இல்லை, "
        "அல்லது இன்னும் சரிபார்க்க முடியவில்லை.",
        AssessmentLevel.HIGH_CONCERN: "எங்கள் மதிப்பீடு: அதிக கவலை — நீங்கள் கொடுத்த தகவலின் அடிப்படையில்.",
    },
}

REASON_TEXT: dict[Language, dict[str, str]] = {
    Language.EN: {
        "CRITICAL_SAFETY_SIGNAL": "An OTP, PIN, password, bank details or remote access came up.",
        "CONTRADICTED_CLAIM": "A claim made to you does not match an official record.",
        "MULTIPLE_SIGNIFICANT_WARNINGS": "Several serious warning signs appear together.",
        "WARNING_SIGNALS_PRESENT": "Some warning signs should be checked before you act.",
        "UNVERIFIED_CLAIMS": "Some claims could not be confirmed. That does not mean they are false.",
        "NO_TRUSTED_VERIFICATION": "Nothing has been confirmed by an official source yet.",
        "VERIFIED_CLAIMS": "The registration was confirmed on SEBI's register. This does not prove the person "
        "contacting you works for them.",
        "NO_MAJOR_WARNINGS": "No major warning signs were found.",
    },
    Language.TA: {
        "CRITICAL_SAFETY_SIGNAL": "OTP, PIN, பாஸ்வேர்டு, வங்கி விவரங்கள் அல்லது ரிமோட் அக்சஸ் பற்றி பேசப்பட்டுள்ளது.",
        "CONTRADICTED_CLAIM": "உங்களிடம் சொன்ன ஒரு தகவல் அதிகாரப்பூர்வ பதிவுடன் பொருந்தவில்லை.",
        "MULTIPLE_SIGNIFICANT_WARNINGS": "பல தீவிர எச்சரிக்கை அறிகுறிகள் ஒன்றாக உள்ளன.",
        "WARNING_SIGNALS_PRESENT": "செயல்படுவதற்கு முன் சில எச்சரிக்கை அறிகுறிகளைச் சரிபார்க்க வேண்டும்.",
        "UNVERIFIED_CLAIMS": "சில தகவல்களை உறுதிப்படுத்த முடியவில்லை. அவை பொய் என்று அர்த்தமல்ல.",
        "NO_TRUSTED_VERIFICATION": "இதுவரை எதுவும் அதிகாரப்பூர்வ மூலத்தால் உறுதிப்படுத்தப்படவில்லை.",
        "VERIFIED_CLAIMS": "SEBI பதிவேட்டில் பதிவு உறுதிசெய்யப்பட்டது. ஆனால் உங்களைத் தொடர்பு கொண்டவர் "
        "அவர்களுக்காக வேலை செய்கிறார் என்பதை இது நிரூபிக்கவில்லை.",
        "NO_MAJOR_WARNINGS": "பெரிய எச்சரிக்கை அறிகுறிகள் இல்லை.",
    },
}

SIGNAL_SHORT: dict[Language, dict[str, str]] = {
    Language.EN: {
        "OTP_REQUEST": "an OTP was mentioned",
        "UPI_PIN_REQUEST": "a PIN was mentioned",
        "PASSWORD_REQUEST": "a password was mentioned",
        "CREDENTIAL_REQUEST": "bank or card details were mentioned",
        "REMOTE_ACCESS_REQUEST": "screen sharing or remote access",
        "GUARANTEED_RETURNS": "guaranteed or risk-free returns",
        "UNREALISTIC_RETURN_RATE": "an unrealistically high return rate",
        "DOUBLING_MONEY": "a promise to double money",
        "WITHDRAWAL_FEE": "paying before you can withdraw",
        "APK_INSTALL": "installing an app from a link",
        "SURE_SHOT_TIP": "'sure-shot' or insider tips",
        "URGENCY_PRESSURE": "pressure to act fast",
        "RECRUITMENT_DEPENDENCE": "earnings that depend on recruiting people",
        "ENTRY_FEE": "an upfront joining fee",
        "SECRECY": "being asked to keep it secret",
    },
    Language.TA: {
        "OTP_REQUEST": "OTP பற்றி பேசப்பட்டது",
        "UPI_PIN_REQUEST": "PIN பற்றி பேசப்பட்டது",
        "PASSWORD_REQUEST": "பாஸ்வேர்டு பற்றி பேசப்பட்டது",
        "CREDENTIAL_REQUEST": "வங்கி அல்லது கார்டு விவரங்கள் பற்றி பேசப்பட்டது",
        "REMOTE_ACCESS_REQUEST": "ஸ்கிரீன் ஷேரிங் அல்லது ரிமோட் அக்சஸ்",
        "GUARANTEED_RETURNS": "உத்தரவாத அல்லது ரிஸ்க் இல்லாத லாபம்",
        "UNREALISTIC_RETURN_RATE": "நம்ப முடியாத அளவு அதிக லாப விகிதம்",
        "DOUBLING_MONEY": "பணத்தை இரட்டிப்பாக்குவதாக வாக்குறுதி",
        "WITHDRAWAL_FEE": "பணத்தை எடுக்க முன்பு கட்டணம் கட்டச் சொல்வது",
        "APK_INSTALL": "லிங்க் மூலம் ஆப் நிறுவச் சொல்வது",
        "SURE_SHOT_TIP": "'ஷ்யூர் ஷாட்' அல்லது உள் தகவல் டிப்ஸ்",
        "URGENCY_PRESSURE": "அவசரப்படுத்துதல்",
        "RECRUITMENT_DEPENDENCE": "ஆட்களைச் சேர்ப்பதைச் சார்ந்த வருமானம்",
        "ENTRY_FEE": "முன்கூட்டிய சேர்க்கைக் கட்டணம்",
        "SECRECY": "ரகசியமாக வைக்கச் சொல்வது",
    },
}

PHRASES: dict[Language, dict[str, str]] = {
    Language.EN: {"warning_signs": "Warning signs: {items}.", "next": "What to do now: {steps}"},
    Language.TA: {"warning_signs": "எச்சரிக்கை அறிகுறிகள்: {items}.", "next": "இப்போது செய்ய வேண்டியவை: {steps}"},
}

STEP_TEXT: dict[Language, dict[str, str]] = {
    Language.EN: {
        "NEVER_SHARE_CREDENTIALS": "Never share an OTP, PIN or password with anyone, including people claiming to "
        "be from a bank or SEBI.",
        "IF_SHARED_CALL_BANK": "If you already shared one, call your bank now and block the card/UPI.",
        "UNINSTALL_REMOTE_APP": "Uninstall the screen-sharing app and do not reinstall it on request.",
        "DO_NOT_INSTALL_APK": "Do not install apps from links. Use only the Play Store / App Store.",
        "DO_NOT_PAY_YET": "Do not send money until the checks below are done.",
        "CHECK_SEBI_REGISTER": "Ask for the SEBI registration number and check it on sebi.gov.in.",
        "ASK_WHAT_IS_SOLD": "Ask what product is sold and whether the fee is refundable, in writing.",
        "TAKE_YOUR_TIME": "A genuine offer will still be there tomorrow. Talk to someone you trust.",
        "CONTACT_VIA_OFFICIAL_DETAILS": "Contact them only through the phone, email or website listed on SEBI's "
        "site, not the details in the message.",
        "REPORT_IF_LOST": "If you lost money, report at cybercrime.gov.in or call 1930.",
    },
    Language.TA: {
        "NEVER_SHARE_CREDENTIALS": "OTP, PIN, பாஸ்வேர்டு எதையும் யாரிடமும் பகிர வேண்டாம் — வங்கி அல்லது "
        "SEBI-யிலிருந்து பேசுவதாகச் சொன்னாலும் கூட.",
        "IF_SHARED_CALL_BANK": "ஏற்கனவே பகிர்ந்திருந்தால், உடனே உங்கள் வங்கியை அழைத்து கார்டு/UPI-ஐ முடக்குங்கள்.",
        "UNINSTALL_REMOTE_APP": "ஸ்கிரீன் ஷேரிங் ஆப்பை நீக்குங்கள்; அவர்கள் கேட்டாலும் மீண்டும் நிறுவ வேண்டாம்.",
        "DO_NOT_INSTALL_APK": "லிங்க் மூலம் வரும் ஆப்களை நிறுவ வேண்டாம். Play Store / App Store மட்டும் பயன்படுத்துங்கள்.",
        "DO_NOT_PAY_YET": "கீழே உள்ள சோதனைகள் முடியும் வரை பணம் அனுப்ப வேண்டாம்.",
        "CHECK_SEBI_REGISTER": "SEBI பதிவு எண்ணைக் கேட்டு, sebi.gov.in-இல் சரிபாருங்கள்.",
        "ASK_WHAT_IS_SOLD": "என்ன பொருள் விற்கப்படுகிறது, கட்டணம் திரும்பக் கிடைக்குமா என்று எழுத்துப்பூர்வமாகக் கேளுங்கள்.",
        "TAKE_YOUR_TIME": "உண்மையான வாய்ப்பு நாளையும் இருக்கும். நம்பிக்கையான ஒருவரிடம் பேசுங்கள்.",
        "CONTACT_VIA_OFFICIAL_DETAILS": "SEBI இணையதளத்தில் உள்ள தொலைபேசி, மின்னஞ்சல் அல்லது இணையதளம் மூலம் மட்டுமே "
        "அவர்களைத் தொடர்பு கொள்ளுங்கள்; மெசேஜில் வந்த விவரங்கள் மூலம் அல்ல.",
        "REPORT_IF_LOST": "பணம் இழந்திருந்தால், cybercrime.gov.in-இல் புகார் செய்யுங்கள் அல்லது 1930-ஐ அழையுங்கள்.",
    },
}

# Template questions, one per unknown (F06). Every one still passes through the ranker's veto.
QUESTION_TEMPLATES: dict[Language, dict[Unknown, str]] = {
    Language.EN: {
        Unknown.ENTITY_NAME: "What is the exact name of the company or organization behind this offer?",
        Unknown.REGISTRATION_NUMBER: "Did they give you a SEBI registration number? If yes, please type it exactly.",
        Unknown.PAYMENT_RECIPIENT: "Who are you asked to pay: a company bank account, a person's UPI ID, or "
        "something else?",
        Unknown.AMOUNT: "How much money are they asking for, and have you paid anything yet?",
        Unknown.RETURN_CLAIM: "What return or profit did they promise, and over what time?",
        Unknown.CONTACT_CHANNEL: "How did they first contact you: WhatsApp, Telegram, a call, social media, or "
        "someone you know?",
        Unknown.DOCUMENTATION: "Did they give you anything in writing, like an agreement, invoice or receipt in "
        "the company's name?",
        Unknown.PRODUCT_SOLD: "What product or service is actually sold, and can you buy it without joining?",
    },
    Language.TA: {
        Unknown.ENTITY_NAME: "இந்த வாய்ப்பை வழங்கும் நிறுவனத்தின் சரியான பெயர் என்ன?",
        Unknown.REGISTRATION_NUMBER: "அவர்கள் SEBI பதிவு எண் கொடுத்தார்களா? ஆம் என்றால், அதை அப்படியே டைப் செய்யுங்கள்.",
        Unknown.PAYMENT_RECIPIENT: "யாருக்கு பணம் செலுத்தச் சொல்கிறார்கள்: நிறுவனத்தின் வங்கிக் கணக்கா, ஒருவரின் "
        "UPI ID-யா, அல்லது வேறு ஏதாவதா?",
        Unknown.AMOUNT: "எவ்வளவு பணம் கேட்கிறார்கள்? ஏற்கனவே ஏதாவது செலுத்தியிருக்கிறீர்களா?",
        Unknown.RETURN_CLAIM: "எவ்வளவு லாபம் அல்லது வருமானம் தருவதாகச் சொன்னார்கள், எவ்வளவு காலத்தில்?",
        Unknown.CONTACT_CHANNEL: "முதலில் உங்களை எப்படித் தொடர்பு கொண்டார்கள்: WhatsApp, Telegram, அழைப்பு, "
        "சமூக ஊடகம், அல்லது தெரிந்தவர் மூலமா?",
        Unknown.DOCUMENTATION: "நிறுவனத்தின் பெயரில் ஒப்பந்தம், இன்வாய்ஸ் அல்லது ரசீது போன்ற ஏதாவது "
        "எழுத்துப்பூர்வமாகக் கொடுத்தார்களா?",
        Unknown.PRODUCT_SOLD: "உண்மையில் என்ன பொருள் அல்லது சேவை விற்கப்படுகிறது? சேராமலே அதை வாங்க முடியுமா?",
    },
}

QUESTION_OBJECTIVE: dict[Unknown, str] = {
    Unknown.ENTITY_NAME: "Identify the entity so it can be checked against official registers.",
    Unknown.REGISTRATION_NUMBER: "Get a registration number that can be checked on SEBI's register.",
    Unknown.PAYMENT_RECIPIENT: "Find out whether money goes to the entity or to an individual.",
    Unknown.AMOUNT: "Understand how much money is at risk.",
    Unknown.RETURN_CLAIM: "Check whether the promised return is realistic.",
    Unknown.CONTACT_CHANNEL: "Understand how the offer reached the user.",
    Unknown.DOCUMENTATION: "Check whether there is written documentation in the entity's name.",
    Unknown.PRODUCT_SOLD: "Check whether a real product or service is sold, or only memberships.",
}
