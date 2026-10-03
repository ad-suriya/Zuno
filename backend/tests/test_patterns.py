from app.engine import patterns


def test_registration_numbers():
    found = patterns.find_reg_numbers("Reg no INA000017523 and research analyst INH 000011431, also INA12345.")
    by_value = {r.value: r for r in found}
    assert by_value["INA000017523"].well_formed
    assert by_value["INH000011431"].well_formed
    assert not by_value["INA12345"].well_formed


def test_upi_ids_but_not_emails():
    text = "Pay to alpha.wealth@ybl or rahul123@okaxis. Email support@alpha.com for help."
    assert patterns.find_upi_ids(text) == ["alpha.wealth@ybl", "rahul123@okaxis"]


def test_phone_numbers():
    assert patterns.find_phones("Call +91 98765 43210 or 9876543210 now") == ["+91 98765 43210", "9876543210"]
    assert patterns.find_phones("Reg INA000017523") == []


def test_urls():
    urls = patterns.find_urls("Visit https://alpha-trade.xyz/join or www.example.in or quickprofit.com today")
    assert urls == ["https://alpha-trade.xyz/join", "www.example.in", "quickprofit.com"]
    assert patterns.find_urls("mail me at someone@gmail.com") == []


def test_amounts():
    assert patterns.find_amounts("Pay ₹25,000 now, profit Rs. 1.2 lakh, fee 5000 rupees") == [
        "₹25,000", "Rs. 1.2 lakh", "5000 rupees"]
    assert patterns.find_amounts("₹5,000 கட்ட வேண்டும்") == ["₹5,000"]


def test_return_claims_english_tamil_tanglish():
    assert patterns.find_return_claims("guaranteed 20% monthly returns") == ["20% monthly"]
    assert patterns.find_return_claims("monthly 20% profit")
    assert patterns.find_return_claims("மாதம் 20% லாபம்")
    assert patterns.find_return_claims("maasam 10% varum")


def test_company_names():
    names = patterns.find_company_names("The advisor from Alpha Wealth Advisors Pvt Ltd called. He works with 1 Finance Private Limited.")
    assert "Alpha Wealth Advisors Pvt Ltd" in names
    assert "1 Finance Private Limited" in names
    assert patterns.find_company_names('He said the company is called "Sunrise Growth"') == ["Sunrise Growth"]


def test_registration_claim():
    assert patterns.find_registration_claims("They said they are SEBI registered")
    assert patterns.find_registration_claims("registered with SEBI since 2019")
    assert not patterns.find_registration_claims("I checked the SEBI website")


def test_offer_type_guess():
    assert patterns.guess_offer_type("Joining fee and add members to earn") == "mlm"
    assert patterns.guess_offer_type("Telegram group with sure shot tips") == "trading_tips"
    assert patterns.guess_offer_type("Invest and get returns") == "investment"
    assert patterns.guess_offer_type("Hello") is None
